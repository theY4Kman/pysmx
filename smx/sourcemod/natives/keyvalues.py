from __future__ import annotations

from enum import IntEnum

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


class KvDataTypes(IntEnum):
    KvData_None = 0
    KvData_String = 1
    KvData_Int = 2
    KvData_Float = 3
    KvData_Ptr = 4
    KvData_WString = 5
    KvData_Color = 6
    KvData_UInt64 = 7
    KvData_NUMTYPES = 8


class KeyValues:
    pass


class KeyValuesMethodMap(MethodMap):
    @native
    def ExportToFile(self, this: SourceModHandle[KeyValues], file: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ExportToString(self, this: SourceModHandle[KeyValues], buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ImportFromFile(self, this: SourceModHandle[KeyValues], file: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ImportFromString(self, this: SourceModHandle[KeyValues], buffer: str, resource_name: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Import(self, this: SourceModHandle[KeyValues], other: SourceModHandle[KeyValues]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetString(self, this: SourceModHandle[KeyValues], key: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetNum(self, this: SourceModHandle[KeyValues], key: str, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetUInt64(self, this: SourceModHandle[KeyValues], key: str, value: Array[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetFloat(self, this: SourceModHandle[KeyValues], key: str, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetColor(self, this: SourceModHandle[KeyValues], key: str, r: int, g: int, b: int, a: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVector(self, this: SourceModHandle[KeyValues], key: str, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetString(self, this: SourceModHandle[KeyValues], key: str, value: WritableString, defvalue: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetNum(self, this: SourceModHandle[KeyValues], key: str, defvalue: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetFloat(self, this: SourceModHandle[KeyValues], key: str, defvalue: float) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetColor(self, this: SourceModHandle[KeyValues], key: str, r: Pointer[int], g: Pointer[int], b: Pointer[int], a: Pointer[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetUInt64(self, this: SourceModHandle[KeyValues], key: str, value: Array[int], defvalue: Array[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetVector(self, this: SourceModHandle[KeyValues], key: str, vec: Array[float], defvalue: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def JumpToKey(self, this: SourceModHandle[KeyValues], key: str, create: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def JumpToKeySymbol(self, this: SourceModHandle[KeyValues], id: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GotoFirstSubKey(self, this: SourceModHandle[KeyValues], key_only: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GotoNextKey(self, this: SourceModHandle[KeyValues], key_only: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SavePosition(self, this: SourceModHandle[KeyValues]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GoBack(self, this: SourceModHandle[KeyValues]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DeleteKey(self, this: SourceModHandle[KeyValues], key: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DeleteThis(self, this: SourceModHandle[KeyValues]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def Rewind(self, this: SourceModHandle[KeyValues]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetSectionName(self, this: SourceModHandle[KeyValues], section: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetSectionName(self, this: SourceModHandle[KeyValues], section: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetDataType(self, this: SourceModHandle[KeyValues], key: str) -> KvDataTypes:
        raise SourcePawnUnboundNativeError

    @native
    def SetEscapeSequences(self, this: SourceModHandle[KeyValues], use_escapes: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def NodesInStack(self, this: SourceModHandle[KeyValues]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FindKeyById(self, this: SourceModHandle[KeyValues], id: int, name: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetNameSymbol(self, this: SourceModHandle[KeyValues], key: str, id: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetSectionSymbol(self, this: SourceModHandle[KeyValues], id: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError


class KeyvaluesNatives(SourceModNativesMixin):
    KeyValues = KeyValuesMethodMap()

    @native
    def CreateKeyValues(self, name: str, first_key: str, first_value: str) -> SourceModHandle[KeyValues]:
        raise SourcePawnUnboundNativeError

    @native
    def KvSetString(self, kv: SourceModHandle, key: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvSetNum(self, kv: SourceModHandle, key: str, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvSetUInt64(self, kv: SourceModHandle, key: str, value: Array[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvSetFloat(self, kv: SourceModHandle, key: str, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvSetColor(self, kv: SourceModHandle, key: str, r: int, g: int, b: int, a: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvSetVector(self, kv: SourceModHandle, key: str, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvGetString(self, kv: SourceModHandle, key: str, value: WritableString, defvalue: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvGetNum(self, kv: SourceModHandle, key: str, defvalue: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def KvGetFloat(self, kv: SourceModHandle, key: str, defvalue: float) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def KvGetColor(self, kv: SourceModHandle, key: str, r: Pointer[int], g: Pointer[int], b: Pointer[int], a: Pointer[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvGetUInt64(self, kv: SourceModHandle, key: str, value: Array[int], defvalue: Array[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvGetVector(self, kv: SourceModHandle, key: str, vec: Array[float], defvalue: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvJumpToKey(self, kv: SourceModHandle, key: str, create: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def KvJumpToKeySymbol(self, kv: SourceModHandle, id: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def KvGotoFirstSubKey(self, kv: SourceModHandle, key_only: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def KvGotoNextKey(self, kv: SourceModHandle, key_only: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def KvSavePosition(self, kv: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvDeleteKey(self, kv: SourceModHandle, key: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def KvDeleteThis(self, kv: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def KvGoBack(self, kv: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def KvRewind(self, kv: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvGetSectionName(self, kv: SourceModHandle, section: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def KvSetSectionName(self, kv: SourceModHandle, section: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvGetDataType(self, kv: SourceModHandle, key: str) -> KvDataTypes:
        raise SourcePawnUnboundNativeError

    @native
    def KeyValuesToFile(self, kv: SourceModHandle, file: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FileToKeyValues(self, kv: SourceModHandle, file: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def StringToKeyValues(self, kv: SourceModHandle, buffer: str, resource_name: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def KvSetEscapeSequences(self, kv: SourceModHandle, use_escapes: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvNodesInStack(self, kv: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def KvCopySubkeys(self, origin: SourceModHandle, dest: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KvFindKeyById(self, kv: SourceModHandle, id: int, name: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def KvGetNameSymbol(self, kv: SourceModHandle, key: str, id: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def KvGetSectionSymbol(self, kv: SourceModHandle, id: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError
