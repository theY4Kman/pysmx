from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    MethodMap,
    SourceModNativesMixin,
    WritableString,
    native,
)
from smx.sourcemod.natives.sorting import SortFuncADTArray, SortOrder, SortType


class ArrayList:
    pass


class ArrayListMethodMap(MethodMap):
    @native
    def Clear(self, this: SourceModHandle[ArrayList]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Clone(self, this: SourceModHandle[ArrayList]) -> SourceModHandle[ArrayList]:
        raise SourcePawnUnboundNativeError

    @native
    def Resize(self, this: SourceModHandle[ArrayList], newsize: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Push(self, this: SourceModHandle[ArrayList], value: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PushString(self, this: SourceModHandle[ArrayList], value: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PushArray(self, this: SourceModHandle[ArrayList], values: Array[int], size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def Get(self, this: SourceModHandle[ArrayList], index: int, block: int, as_char: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetString(self, this: SourceModHandle[ArrayList], index: int, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetArray(self, this: SourceModHandle[ArrayList], index: int, buffer: Array[int], size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def Set(self, this: SourceModHandle[ArrayList], index: int, value: int, block: int, as_char: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetString(self, this: SourceModHandle[ArrayList], index: int, value: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetArray(self, this: SourceModHandle[ArrayList], index: int, values: Array[int], size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ShiftUp(self, this: SourceModHandle[ArrayList], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Erase(self, this: SourceModHandle[ArrayList], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SwapAt(self, this: SourceModHandle[ArrayList], index1: int, index2: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FindString(self, this: SourceModHandle[ArrayList], item: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FindValue(self, this: SourceModHandle[ArrayList], item: int, block: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def Sort(self, this: SourceModHandle[ArrayList], order: SortOrder, type_: SortType) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SortCustom(self, this: SourceModHandle[ArrayList], sortfunc: SortFuncADTArray, hndl: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError


class AdtArrayNatives(SourceModNativesMixin):
    ArrayList = ArrayListMethodMap()

    @native
    def CreateArray(self, blocksize: int, startsize: int) -> SourceModHandle[ArrayList]:
        raise SourcePawnUnboundNativeError

    @native
    def ClearArray(self, array: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CloneArray(self, array: SourceModHandle) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def ResizeArray(self, array: SourceModHandle, newsize: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetArraySize(self, array: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PushArrayCell(self, array: SourceModHandle, value: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PushArrayString(self, array: SourceModHandle, value: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PushArrayArray(self, array: SourceModHandle, values: Array[int], size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetArrayCell(self, array: SourceModHandle, index: int, block: int, as_char: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetArrayString(self, array: SourceModHandle, index: int, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetArrayArray(self, array: SourceModHandle, index: int, buffer: Array[int], size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetArrayCell(self, array: SourceModHandle, index: int, value: int, block: int, as_char: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetArrayString(self, array: SourceModHandle, index: int, value: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetArrayArray(self, array: SourceModHandle, index: int, values: Array[int], size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ShiftArrayUp(self, array: SourceModHandle, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveFromArray(self, array: SourceModHandle, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SwapArrayItems(self, array: SourceModHandle, index1: int, index2: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FindStringInArray(self, array: SourceModHandle, item: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FindValueInArray(self, array: SourceModHandle, item: int, block: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetArrayBlockSize(self, array: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError
