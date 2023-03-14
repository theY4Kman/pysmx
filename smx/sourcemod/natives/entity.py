from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import (
    Array,
    SourceModNativesMixin,
    WritableString,
    native,
)
from smx.sourcemod.natives.sourcemod import Address


class PropType(IntEnum):
    Prop_Send = 0
    Prop_Data = 1


class PropFieldType(IntEnum):
    PropField_Unsupported = 0
    PropField_Integer = 1
    PropField_Float = 2
    PropField_Entity = 3
    PropField_Vector = 4
    PropField_String = 5
    PropField_String_T = 6
    PropField_Variant = 7


class EntityNatives(SourceModNativesMixin):
    @native
    def GetMaxEntities(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntityCount(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsValidEntity(self, entity: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsValidEdict(self, edict: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsEntNetworkable(self, entity: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CreateEdict(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveEdict(self, edict: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveEntity(self, entity: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEdictFlags(self, edict: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEdictFlags(self, edict: int, flags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEdictClassname(self, edict: int, clsname: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntityNetClass(self, edict: int, clsname: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ChangeEdictState(self, edict: int, offset: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntData(self, entity: int, offset: int, size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntData(self, entity: int, offset: int, value: int, size: int, change_state: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntDataFloat(self, entity: int, offset: int) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntDataFloat(self, entity: int, offset: int, value: float, change_state: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntDataEnt(self, entity: int, offset: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntDataEnt(self, entity: int, offset: int, other: int, change_state: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntDataEnt2(self, entity: int, offset: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntDataEnt2(self, entity: int, offset: int, other: int, change_state: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntDataVector(self, entity: int, offset: int, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntDataVector(self, entity: int, offset: int, vec: Array[float], change_state: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntDataString(self, entity: int, offset: int, buffer: str, maxlen: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntDataString(self, entity: int, offset: int, buffer: str, maxlen: int, change_state: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FindSendPropOffs(self, cls: str, prop: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntProp(self, entity: int, type_: PropType, prop: str, size: int, element: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntProp(self, entity: int, type_: PropType, prop: str, value: int, size: int, element: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntPropFloat(self, entity: int, type_: PropType, prop: str, element: int) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntPropFloat(self, entity: int, type_: PropType, prop: str, value: float, element: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntPropEnt(self, entity: int, type_: PropType, prop: str, element: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntPropEnt(self, entity: int, type_: PropType, prop: str, other: int, element: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntPropVector(self, entity: int, type_: PropType, prop: str, vec: Array[float], element: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntPropVector(self, entity: int, type_: PropType, prop: str, vec: Array[float], element: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntPropString(self, entity: int, type_: PropType, prop: str, buffer: str, maxlen: int, element: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntPropString(self, entity: int, type_: PropType, prop: str, buffer: str, element: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntPropArraySize(self, entity: int, type_: PropType, prop: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntityAddress(self, entity: int) -> Address:
        raise SourcePawnUnboundNativeError
