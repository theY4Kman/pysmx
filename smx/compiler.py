from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from tempfile import mkdtemp
from typing import Iterable

from smx.plugin import SourcePawnPlugin

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


def compile_to_string(
    code,
    *,
    filename: str | None = None,
    include_dir: str | Path | Iterable[str | Path] | None = INCLUDE_DIR,
    extra_args: Iterable[str] = ()
):
    if isinstance(code, str):
        # NOTE: all source code is assumed to be UTF-8
        code = code.encode('utf-8')

    if include_dir is None:
        include_dir = []
    elif isinstance(include_dir, (str, Path)):
        include_dir = [include_dir]

    if not filename:
        filename = 'tmp_plugin.sp'

    base_name = os.path.splitext(filename)[0]
    out_filename = base_name + '.smx'

    tmp_dir = mkdtemp(prefix=base_name)
    try:
        tmp_path = Path(tmp_dir)
        in_file = tmp_path / filename
        out_file = tmp_path / out_filename

        in_file.write_bytes(code)
        out_file.touch(exist_ok=True)

        compiler = _get_compiler_path()

        include_dir_args = [
            arg
            for path in include_dir
            for arg in ('-i', str(path))
        ]
        args = [
            compiler,
            *include_dir_args,
            '-o', str(out_file),
            *extra_args,
            str(in_file),
        ]

        try:
            subprocess.check_output(args, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'spcomp failed with code {e.returncode}: {e.stdout}')

        return out_file.read_bytes()
    finally:
        shutil.rmtree(tmp_dir)


def compile_plugin(
    code,
    *,
    filename: str | None = None,
    include_dir: str | Path | Iterable[str | Path] | None = INCLUDE_DIR,
    extra_args: Iterable[str] = (),
    **plugin_options
):
    """Compile SourcePawn code to a pysmx plugin"""
    smx = compile_to_string(code, filename=filename, include_dir=include_dir, extra_args=extra_args)
    fp = BytesIO(smx)
    return SourcePawnPlugin(fp, **plugin_options)
