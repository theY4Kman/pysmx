from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    MethodMap,
    Pointer,
    SourceModNativesMixin,
    WritableString,
    native,
)


class StringMap:
    pass


class StringMapSnapshot:
    pass


class StringMapMethodMap(MethodMap):
    @native
    def Clone(self, this: SourceModHandle[StringMap]) -> SourceModHandle[StringMap]:
        raise SourcePawnUnboundNativeError

    @native
    def SetValue(self, this: SourceModHandle[StringMap], key: str, value: int, replace: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetArray(self, this: SourceModHandle[StringMap], key: str, array: Array[int], num_items: int, replace: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetString(self, this: SourceModHandle[StringMap], key: str, value: str, replace: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetValue(self, this: SourceModHandle[StringMap], key: str, value: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetArray(self, this: SourceModHandle[StringMap], key: str, array: Array[int], max_size: int, size: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetString(self, this: SourceModHandle[StringMap], key: str, value: str, max_size: int, size: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ContainsKey(self, this: SourceModHandle[StringMap], key: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Remove(self, this: SourceModHandle[StringMap], key: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Clear(self, this: SourceModHandle[StringMap]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Snapshot(self, this: SourceModHandle[StringMap]) -> SourceModHandle[StringMapSnapshot]:
        raise SourcePawnUnboundNativeError


class StringMapSnapshotMethodMap(MethodMap):
    @native
    def KeyBufferSize(self, this: SourceModHandle[StringMapSnapshot], index: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetKey(self, this: SourceModHandle[StringMapSnapshot], index: int, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError


class AdtTrieNatives(SourceModNativesMixin):
    StringMap = StringMapMethodMap()
    StringMapSnapshot = StringMapSnapshotMethodMap()

    @native
    def CreateTrie(self) -> SourceModHandle[StringMap]:
        raise SourcePawnUnboundNativeError

    @native
    def SetTrieValue(self, map_: SourceModHandle, key: str, value: int, replace: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetTrieArray(self, map_: SourceModHandle, key: str, array: Array[int], num_items: int, replace: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetTrieString(self, map_: SourceModHandle, key: str, value: str, replace: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetTrieValue(self, map_: SourceModHandle, key: str, value: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetTrieArray(self, map_: SourceModHandle, key: str, array: Array[int], max_size: int, size: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetTrieString(self, map_: SourceModHandle, key: str, value: str, max_size: int, size: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveFromTrie(self, map_: SourceModHandle, key: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ClearTrie(self, map_: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetTrieSize(self, map_: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CreateTrieSnapshot(self, map_: SourceModHandle) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def TrieSnapshotLength(self, snapshot: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TrieSnapshotKeyBufferSize(self, snapshot: SourceModHandle, index: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetTrieSnapshotKey(self, snapshot: SourceModHandle, index: int, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError
