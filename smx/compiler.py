import os
import sys
from subprocess import check_call
from tempfile import NamedTemporaryFile

from smx import SourcePawnPlugin

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


PKG_DIR = os.path.abspath(os.path.dirname(__file__))
SPCOMP_DIR = os.path.join(PKG_DIR, 'spcomp')
INCLUDE_DIR = os.path.join(PKG_DIR, 'include')


def _get_compiler_name():
    return {
        'win32': 'spcomp.exe',
        # TODO: OSX and Linux
    }.get(sys.platform)


def _abs_compiler_path(*parts):
    return os.path.join(SPCOMP_DIR, *parts)


def _get_compiler_path():
    return _abs_compiler_path(_get_compiler_name())


def compile_to_string(code, **options):
    compiler = _get_compiler_path()
    fp = NamedTemporaryFile(prefix='tmp_plugin', suffix='.sp', delete=False)
    fp.write(code)
    fp.flush()

    out = NamedTemporaryFile(prefix='tmp_plugin', suffix='.smx', delete=False)
    try:
        # Files must be closed first, so spcomp can open it on Windows
        fp.close()
        out.close()

        check_call([
            compiler,
            '-i', INCLUDE_DIR,
            '-o', out.name,
            fp.name,
        ])

        with open(out.name, 'rb') as compiled:
            return compiled.read()
    finally:
        os.unlink(fp.name)
        os.unlink(out.name)


def compile(code, **options):
    """Compile SourcePawn code to a pysmx plugin"""
    smx = compile_to_string(code, **options)
    fp = StringIO(smx)
    return SourcePawnPlugin(fp)
