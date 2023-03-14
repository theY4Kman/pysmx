from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    MethodMap,
    SourceModNativesMixin,
    WritableString,
    native,
)


EventHook = Callable


class EventHookMode(IntEnum):
    EventHookMode_Pre = 0
    EventHookMode_Post = 1
    EventHookMode_PostNoCopy = 2


class Event:
    pass


class EventMethodMap(MethodMap):
    @native
    def Fire(self, this: SourceModHandle[Event], dont_broadcast: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FireToClient(self, this: SourceModHandle[Event], client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Cancel(self, this: SourceModHandle[Event]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetBool(self, this: SourceModHandle[Event], key: str, def_value: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetBool(self, this: SourceModHandle[Event], key: str, value: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetInt(self, this: SourceModHandle[Event], key: str, def_value: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetInt(self, this: SourceModHandle[Event], key: str, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetFloat(self, this: SourceModHandle[Event], key: str, def_value: float) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def SetFloat(self, this: SourceModHandle[Event], key: str, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetString(self, this: SourceModHandle[Event], key: str, value: WritableString, defvalue: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetString(self, this: SourceModHandle[Event], key: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetName(self, this: SourceModHandle[Event], name: WritableString) -> None:
        raise SourcePawnUnboundNativeError


class EventsNatives(SourceModNativesMixin):
    Event = EventMethodMap()

    @native
    def HookEvent(self, name: str, callback: EventHook, mode: EventHookMode) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def HookEventEx(self, name: str, callback: EventHook, mode: EventHookMode) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def UnhookEvent(self, name: str, callback: EventHook, mode: EventHookMode) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CreateEvent(self, name: str, force: bool) -> SourceModHandle[Event]:
        raise SourcePawnUnboundNativeError

    @native
    def FireEvent(self, event: SourceModHandle, dont_broadcast: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CancelCreatedEvent(self, event: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEventBool(self, event: SourceModHandle, key: str, def_value: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetEventBool(self, event: SourceModHandle, key: str, value: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEventInt(self, event: SourceModHandle, key: str, def_value: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEventInt(self, event: SourceModHandle, key: str, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEventFloat(self, event: SourceModHandle, key: str, def_value: float) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def SetEventFloat(self, event: SourceModHandle, key: str, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEventString(self, event: SourceModHandle, key: str, value: WritableString, defvalue: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetEventString(self, event: SourceModHandle, key: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetEventName(self, event: SourceModHandle, name: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetEventBroadcast(self, event: SourceModHandle, dont_broadcast: bool) -> None:
        raise SourcePawnUnboundNativeError
