from __future__ import annotations

import io
import os
from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    MethodMap,
    native,
    Pointer,
    SourceModNativesMixin,
    WritableString,
)
from smx.sourcemod.printf import atcprintf


class FileType(IntEnum):
    FileType_Unknown = 0
    FileType_Directory = 1
    FileType_File = 2


class FileTimeMode(IntEnum):
    FileTime_LastAccess = 0
    FileTime_Created = 1
    FileTime_LastChange = 2


class PathType(IntEnum):
    Path_SM = 0


class DirectoryListing:
    pass


class File:
    def __init__(self, fp: io.FileIO):
        self.fp = fp
        # XXX(zk): surely this will bite me in the ass
        self.size = os.fstat(fp.fileno()).st_size

    def is_eof(self) -> bool:
        return self.fp.tell() == self.size


class DirectoryListingMethodMap(MethodMap):
    @native
    def GetNext(self, this: SourceModHandle[DirectoryListing], buffer: WritableString, type_: Pointer[FileType]) -> bool:
        raise SourcePawnUnboundNativeError


class FileMethodMap(MethodMap):
    @native
    def ReadLine(self, handle: SourceModHandle[File], buf: WritableString):
        line = handle.obj.fp.readline()
        return buf.write(line, null_terminate=True)

    @native
    def Read(self, handle: SourceModHandle[File], items: Array[bytes], num_items: int, item_size: int):
        if item_size not in (1, 2, 4):
            # TODO(zk): native error
            raise ValueError('Unsupported item size %s' % item_size)

        data = handle.obj.fp.read(num_items * item_size)
        items_read = len(data) // item_size
        data = data[:items_read * item_size]

        items[:len(data)] = data
        return items_read

    @native
    def ReadString(self, this: SourceModHandle[File], buffer: str, max_size: int, read_count: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def Write(self, this: SourceModHandle[File], items: Array[int], num_items: int, size: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def WriteString(self, this: SourceModHandle[File], buffer: str, term: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def WriteLine(self, this: SourceModHandle[File], format_: str, *args) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadInt8(self, this: SourceModHandle[File], data: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadUint8(self, this: SourceModHandle[File], data: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadInt16(self, this: SourceModHandle[File], data: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadUint16(self, this: SourceModHandle[File], data: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadInt32(self, this: SourceModHandle[File], data: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def WriteInt8(self, this: SourceModHandle[File], data: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def WriteInt16(self, this: SourceModHandle[File], data: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def WriteInt32(self, this: SourceModHandle[File], data: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def EndOfFile(self, handle: SourceModHandle[File]):
        return handle.obj.is_eof()

    @native
    def Seek(self, this: SourceModHandle[File], position: int, where: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Flush(self, this: SourceModHandle[File]) -> bool:
        raise SourcePawnUnboundNativeError


class FilesNatives(SourceModNativesMixin):
    DirectoryListing = DirectoryListingMethodMap()
    File = FileMethodMap()

    @native
    def BuildPath(self, path_type: PathType, buffer: WritableString, fmt: str, *args):
        if path_type != PathType.Path_SM:
            raise ValueError('Unsupported path type %s' % path_type)

        suffix = atcprintf(self.amx, fmt, args)
        path = str(self.runtime.root_path / suffix)
        return buffer.write(path, null_terminate=True)

    @native
    def OpenDirectory(self, path: str, use_valve_fs: bool, valve_path_id: str) -> SourceModHandle[DirectoryListing]:
        raise SourcePawnUnboundNativeError

    @native
    def ReadDirEntry(self, dir_: SourceModHandle, buffer: WritableString, type_: Pointer[FileType]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def OpenFile(self, file: str, mode: str, use_valve_fs: bool = False, valve_path_id: str = 'GAME'):
        if use_valve_fs:
            # TODO(zk)
            raise NotImplementedError('Valve FS not implemented')

        fp = open(file, mode)
        return self.sys.handles.new_handle(File(fp), on_close=fp.close)

    @native
    def DeleteFile(self, path: str, use_valve_fs: bool, valve_path_id: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadFileLine(self, hndl: SourceModHandle, buffer: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadFile(self, hndl: SourceModHandle, items: Array[int], num_items: int, size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadFileString(self, hndl: SourceModHandle, buffer: str, max_size: int, read_count: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def WriteFile(self, hndl: SourceModHandle, items: Array[int], num_items: int, size: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def WriteFileString(self, hndl: SourceModHandle, buffer: str, term: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def WriteFileLine(self, hndl: SourceModHandle, format_: str, *args) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsEndOfFile(self, file: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FileSeek(self, file: SourceModHandle, position: int, where: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FilePosition(self, file: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FileExists(self, path: str, use_valve_fs: bool, valve_path_id: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RenameFile(self, newpath: str, oldpath: str, use_valve_fs: bool, valve_path_id: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DirExists(self, path: str, use_valve_fs: bool, valve_path_id: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FileSize(self, path: str, use_valve_fs: bool, valve_path_id: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FlushFile(self, file: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveDir(self, path: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CreateDirectory(self, path: str, mode: int, use_valve_fs: bool, valve_path_id: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetFilePermissions(self, path: str, mode: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetFileTime(self, file: str, tmode: FileTimeMode) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def LogToOpenFile(self, hndl: SourceModHandle, message: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LogToOpenFileEx(self, hndl: SourceModHandle, message: str, *args) -> None:
        raise SourcePawnUnboundNativeError

