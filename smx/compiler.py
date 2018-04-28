from __future__ import division

import os
import subprocess
import sys
from subprocess import check_call
from tempfile import NamedTemporaryFile

import six

from smx import SourcePawnPlugin


PKG_DIR = os.path.abspath(os.path.dirname(__file__))
SPCOMP_DIR = os.path.join(PKG_DIR, 'spcomp')
INCLUDE_DIR = os.path.join(PKG_DIR, 'include')


def _get_compiler_name():
    return {
        'win32': 'spcomp.exe',
        'linux2': 'spcomp.elf',
        'darwin': 'spcomp.macho',
    }.get(sys.platform)


def _abs_compiler_path(*parts):
    return os.path.join(SPCOMP_DIR, *parts)


def _get_compiler_path():
    return _abs_compiler_path(_get_compiler_name())


def compile_to_string(code, assemble=False, include_dir=INCLUDE_DIR,
                      extra_args=''):
    if isinstance(code, six.text_type):
        # NOTE: all source code is assumed to be UTF-8
        code = six.binary_type(code, 'utf-8')

    fp = NamedTemporaryFile(prefix='tmp_plugin', suffix='.sp', delete=False)
    fp.write(code)
    fp.flush()

    out_suffix = '.asm' if assemble else '.smx'
    out = NamedTemporaryFile(prefix='tmp_plugin', suffix=out_suffix, delete=False)
    try:
        # Files must be closed first, so spcomp can open it on Windows
        fp.close()
        out.close()

        compiler = _get_compiler_path()
        args = [compiler]
        if include_dir:
            args += ['-i', include_dir]
        if assemble:
            args.append('-a')
        args += ['-o', out.name]
        if extra_args:
            args.append(extra_args)
        args.append(fp.name)

        check_call(args, stdout=subprocess.PIPE)

        with open(out.name, 'r' if assemble else 'rb') as compiled:
            return compiled.read()
    finally:
        os.unlink(fp.name)
        os.unlink(out.name)


def compile(code, **options):
    """Compile SourcePawn code to a pysmx plugin"""
    smx = compile_to_string(code, **options)
    fp = six.BytesIO(smx)
    plugin = SourcePawnPlugin(fp)

    asm = compile_to_string(code, assemble=True, **options)
    plugin.runtime.amx._verify_asm(asm)

    return plugin
