from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import SourceModNativesMixin, native
from smx.sourcemod.natives.sourcemod import Address


class SDKCallType(IntEnum):
    SDKCall_Static = 0
    SDKCall_Entity = 1
    SDKCall_Player = 2
    SDKCall_GameRules = 3
    SDKCall_EntityList = 4
    SDKCall_Raw = 5
    SDKCall_Server = 6


class SDKLibrary(IntEnum):
    SDKLibrary_Server = 0
    SDKLibrary_Engine = 1


class SDKFuncConfSource(IntEnum):
    SDKConf_Virtual = 0
    SDKConf_Signature = 1
    SDKConf_Address = 2


class SDKType(IntEnum):
    SDKType_CBaseEntity = 0
    SDKType_CBasePlayer = 1
    SDKType_Vector = 2
    SDKType_QAngle = 3
    SDKType_PlainOldData = 4
    SDKType_Float = 5
    SDKType_Edict = 6
    SDKType_String = 7
    SDKType_Bool = 8


class SDKPassMethod(IntEnum):
    SDKPass_Pointer = 0
    SDKPass_Plain = 1
    SDKPass_ByValue = 2
    SDKPass_ByRef = 3


class SdktoolsNatives(SourceModNativesMixin):
    @native
    def StartPrepSDKCall(self, type_: SDKCallType) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PrepSDKCall_SetVirtual(self, vtblidx: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PrepSDKCall_SetSignature(self, lib: SDKLibrary, signature: str, bytes_: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def PrepSDKCall_SetAddress(self, addr: Address) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def PrepSDKCall_SetFromConf(self, gameconf: SourceModHandle, source: SDKFuncConfSource, name: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def PrepSDKCall_SetReturnInfo(self, type_: SDKType, pass_: SDKPassMethod, decflags: int, encflags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PrepSDKCall_AddParameter(self, type_: SDKType, pass_: SDKPassMethod, decflags: int, encflags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def EndPrepSDKCall(self) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def SDKCall(self, call: SourceModHandle, *args) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetPlayerResourceEntity(self) -> int:
        raise SourcePawnUnboundNativeError
