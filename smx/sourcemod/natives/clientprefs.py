from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    MethodMap,
    Pointer,
    SourceModNativesMixin,
    native,
)


CookieMenuHandler = Callable


class CookieAccess(IntEnum):
    CookieAccess_Public = 0
    CookieAccess_Protected = 1
    CookieAccess_Private = 2


class CookieMenu(IntEnum):
    CookieMenu_YesNo = 0
    CookieMenu_YesNo_Int = 1
    CookieMenu_OnOff = 2
    CookieMenu_OnOff_Int = 3


class CookieMenuAction(IntEnum):
    CookieMenuAction_DisplayOption = 0
    CookieMenuAction_SelectOption = 1


class Cookie:
    pass


class CookieMethodMap(MethodMap):
    @native
    def Find(self, name: str) -> SourceModHandle[Cookie]:
        raise SourcePawnUnboundNativeError

    @native
    def Set(self, this: SourceModHandle[Cookie], client: int, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Get(self, this: SourceModHandle[Cookie], client: int, buffer: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetByAuthId(self, this: SourceModHandle[Cookie], auth_id: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetPrefabMenu(self, this: SourceModHandle[Cookie], type_: CookieMenu, display: str, handler: CookieMenuHandler, info: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientTime(self, this: SourceModHandle[Cookie], client: int) -> int:
        raise SourcePawnUnboundNativeError


class ClientprefsNatives(SourceModNativesMixin):
    Cookie = CookieMethodMap()

    @native
    def RegClientCookie(self, name: str, description: str, access: CookieAccess) -> SourceModHandle[Cookie]:
        raise SourcePawnUnboundNativeError

    @native
    def FindClientCookie(self, name: str) -> SourceModHandle[Cookie]:
        raise SourcePawnUnboundNativeError

    @native
    def SetClientCookie(self, client: int, cookie: SourceModHandle, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientCookie(self, client: int, cookie: SourceModHandle, buffer: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetAuthIdCookie(self, auth_id: str, cookie: SourceModHandle, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AreClientCookiesCached(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetCookiePrefabMenu(self, cookie: SourceModHandle, type_: CookieMenu, display: str, handler: CookieMenuHandler, info: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetCookieMenuItem(self, handler: CookieMenuHandler, info: int, display: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ShowCookieMenu(self, client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetCookieIterator(self) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def ReadCookieIterator(self, iter_: SourceModHandle, name: str, name_len: int, access: Pointer[CookieAccess], desc: str, desc_len: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetCookieAccess(self, cookie: SourceModHandle) -> CookieAccess:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientCookieTime(self, client: int, cookie: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError
