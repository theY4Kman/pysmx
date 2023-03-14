from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    MethodMap,
    Pointer,
    SourceModNativesMixin,
    WritableString,
    native,
)
from smx.sourcemod.natives.console import QueryCookie


ConVarQueryFinished = Callable
ConVarChanged = Callable


class ConVarBounds(IntEnum):
    ConVarBound_Upper = 0
    ConVarBound_Lower = 1


class ConVarQueryResult(IntEnum):
    ConVarQuery_Cancelled = -1
    ConVarQuery_Okay = 0
    ConVarQuery_NotFound = 1
    ConVarQuery_NotValid = 2
    ConVarQuery_Protected = 3


class ConVar:
    def __init__(
        self,
        name: str,
        default_value: str,
        description: str = '',
        flags: int = 0,
        min: float | None = None,
        max: float | None = None
    ):
        self.name = name
        self.value = self.default_value = default_value
        self.description = description
        self.flags = flags
        self.min = min
        self.max = max

    def __str__(self):
        return self.value

    def __repr__(self):
        return '<ConVar %s %r>' % (self.name, self.value)


class ConVarMethodMap(MethodMap):
    @native
    def SetBool(self, this: SourceModHandle[ConVar], value: bool, replicate: bool, notify: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetInt(self, this: SourceModHandle[ConVar], value: int, replicate: bool, notify: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetFloat(self, this: SourceModHandle[ConVar], value: float, replicate: bool, notify: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetString(self, this: SourceModHandle[ConVar], value: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetString(self, this: SourceModHandle[ConVar], value: str, replicate: bool, notify: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RestoreDefault(self, this: SourceModHandle[ConVar], replicate: bool, notify: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetDefault(self, this: SourceModHandle[ConVar], value: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetBounds(self, this: SourceModHandle[ConVar], type_: ConVarBounds, value: Pointer[float]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetBounds(self, this: SourceModHandle[ConVar], type_: ConVarBounds, set_: bool, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetName(self, this: SourceModHandle[ConVar], name: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetDescription(self, this: SourceModHandle[ConVar], buffer: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReplicateToClient(self, this: SourceModHandle[ConVar], client: int, value: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def AddChangeHook(self, this: SourceModHandle[ConVar], callback: ConVarChanged) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveChangeHook(self, this: SourceModHandle[ConVar], callback: ConVarChanged) -> None:
        raise SourcePawnUnboundNativeError


class ConvarsNatives(SourceModNativesMixin):
    ConVar = ConVarMethodMap()

    @native
    def CreateConVar(
        self,
        name: str,
        default_value: str,
        description: str,
        flags: int,
        has_min: bool,
        min: float,
        has_max: bool,
        max: float
    ):
        cvar = ConVar(
            name,
            default_value,
            description,
            flags,
            min if has_min else None,
            max if has_max else None,
        )
        self.sys.convars[name] = cvar
        return self.sys.handles.new_handle(cvar)

    @native
    def FindConVar(self, name: str) -> SourceModHandle[ConVar]:
        raise SourcePawnUnboundNativeError

    @native
    def HookConVarChange(self, convar: SourceModHandle, callback: ConVarChanged) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def UnhookConVarChange(self, convar: SourceModHandle, callback: ConVarChanged) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetConVarBool(self, convar: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetConVarBool(self, convar: SourceModHandle, value: bool, replicate: bool, notify: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetConVarInt(self, handle: SourceModHandle[ConVar]) -> int:
        return int(handle.obj.value)

    @native
    def SetConVarInt(self, convar: SourceModHandle, value: int, replicate: bool, notify: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetConVarFloat(self, handle: SourceModHandle[ConVar]) -> float:
        return float(handle.obj.value)

    @native
    def SetConVarFloat(self, convar: SourceModHandle, value: float, replicate: bool, notify: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetConVarString(self, handle: SourceModHandle[ConVar], buf: WritableString):
        return buf.write(handle.obj.value, null_terminate=True)

    @native
    def SetConVarString(self, convar: SourceModHandle, value: str, replicate: bool, notify: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ResetConVar(self, convar: SourceModHandle, replicate: bool, notify: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetConVarDefault(self, convar: SourceModHandle, value: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetConVarFlags(self, convar: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetConVarFlags(self, convar: SourceModHandle, flags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetConVarBounds(self, convar: SourceModHandle, type_: ConVarBounds, value: Pointer[float]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetConVarBounds(self, convar: SourceModHandle, type_: ConVarBounds, set_: bool, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetConVarName(self, convar: SourceModHandle, name: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SendConVarValue(self, client: int, convar: SourceModHandle, value: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def QueryClientConVar(self, client: int, cvar_name: str, callback: ConVarQueryFinished, value: int) -> QueryCookie:
        raise SourcePawnUnboundNativeError
