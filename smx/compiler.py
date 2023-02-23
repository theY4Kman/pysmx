from __future__ import annotations

import os
import platform
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable

from smx.reader import SourcePawnPlugin

PKG_DIR = os.path.abspath(os.path.dirname(__file__))
SPCOMP_DIR = os.path.join(PKG_DIR, 'spcomp')
INCLUDE_DIR = os.path.join(PKG_DIR, 'include')

PLATFORMS = {
    ('win32',   32): 'spcomp.exe',
    ('win32',   64): 'spcomp.exe64',
    ('linux',   32): 'spcomp.elf',
    ('linux2',  32): 'spcomp.elf',
    ('linux',   64): 'spcomp.elf64',
    ('linux2',  64): 'spcomp.elf64',
    ('darwin',  32): 'spcomp.macho'
}


def _get_compiler_name():
    plat = sys.platform
    # ref: https://stackoverflow.com/a/12578715/148585
    word_size = 64 if platform.machine().endswith('64') else 32
    return PLATFORMS.get((plat, word_size))


def _abs_compiler_path(*parts):
    return os.path.join(SPCOMP_DIR, *parts)


def _get_compiler_path():
    return _abs_compiler_path(_get_compiler_name())


def compile_to_string(code, *, include_dir: str | Path | None = INCLUDE_DIR, extra_args: Iterable[str] = ()):
    if isinstance(code, str):
        # NOTE: all source code is assumed to be UTF-8
        code = code.encode('utf-8')

    fp = NamedTemporaryFile(prefix='tmp_plugin', suffix='.sp', delete=False)
    fp.write(code)
    fp.flush()

    out = NamedTemporaryFile(prefix='tmp_plugin', suffix='.smx', delete=False)
    try:
        # Files must be closed first, so spcomp can open it on Windows
        fp.close()
        out.close()

        compiler = _get_compiler_path()
        args = [compiler]
        if include_dir:
            args += ['-i', str(include_dir)]
        args += ['-o', out.name]
        if extra_args:
            args.extend(extra_args)
        args.append(fp.name)

        try:
            subprocess.check_output(args)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'spcomp failed with code {e.returncode}: {e.stdout}')

        with open(out.name, 'rb') as compiled:
            return compiled.read()
    finally:
        os.unlink(fp.name)
        os.unlink(out.name)


def compile_plugin(
    code,
    *,
    include_dir: str | Path | None = INCLUDE_DIR,
    extra_args: Iterable[str] = (),
    **plugin_options
):
    """Compile SourcePawn code to a pysmx plugin"""
    smx = compile_to_string(code, include_dir=include_dir, extra_args=extra_args)
    fp = BytesIO(smx)
    return SourcePawnPlugin(fp, **plugin_options)
