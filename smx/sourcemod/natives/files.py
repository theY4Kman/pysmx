from __future__ import annotations

import ctypes
import io
import os
from enum import IntEnum

from smx.sourcemod.natives.base import MethodMap, native, SourceModNativesMixin, WritableString
from smx.sourcemod.printf import atcprintf


class File:
    def __init__(self, fp: io.FileIO):
        self.fp = fp
        # XXX(zk): surely this will bite me in the ass
        self.size = os.fstat(fp.fileno()).st_size

    def is_eof(self) -> bool:
        return self.fp.tell() == self.size


class FileMethodMap(MethodMap):
    @native('handle', 'writable_string')
    def ReadLine(self, file: File, buf: WritableString):
        line = file.fp.readline()
        return buf.write(line, null_terminate=True)

    @native('handle', 'cell', 'cell', 'cell')
    def Read(self, file: File, items_addr: int, num_items: int, item_size: int):
        if item_size not in (1, 2, 4):
            # TODO(zk): native error
            raise ValueError('Unsupported item size %s' % item_size)

        data = file.fp.read(num_items * item_size)
        items_read = len(data) // item_size
        data = data[:items_read * item_size]

        self.amx._writeheap(items_addr, ctypes.create_string_buffer(data))
        return items_read

    @native('handle')
    def EndOfFile(self, file: File):
        return file.is_eof()


class PathType(IntEnum):
    PATH_SM = 0


class FilesNatives(SourceModNativesMixin):
    File = FileMethodMap()

    @native('cell', 'writable_string', 'string', '...')
    def BuildPath(self, path_type: PathType, buffer: WritableString, fmt: str, *args):
        if path_type != PathType.PATH_SM:
            raise ValueError('Unsupported path type %s' % path_type)

        suffix = atcprintf(self.amx, fmt, args)
        path = str(self.runtime.root_path / suffix)
        return buffer.write(path, null_terminate=True)

    @native('string', 'string', 'bool', 'string')
    def OpenFile(self, file: str, mode: str, use_valve_fs: bool = False, valve_path_id: str = 'GAME'):
        if use_valve_fs:
            # TODO(zk)
            raise NotImplementedError('Valve FS not implemented')

        fp = open(file, mode)
        return self.sys.handles.new_handle(File(fp), on_close=fp.close)
