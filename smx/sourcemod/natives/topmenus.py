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


TopMenuHandler = Callable


class TopMenuAction(IntEnum):
    TopMenuAction_DisplayOption = 0
    TopMenuAction_DisplayTitle = 1
    TopMenuAction_SelectOption = 2
    TopMenuAction_DrawOption = 3
    TopMenuAction_RemoveObject = 4


class TopMenuObjectType(IntEnum):
    TopMenuObject_Category = 0
    TopMenuObject_Item = 1


class TopMenuPosition(IntEnum):
    TopMenuPosition_Start = 0
    TopMenuPosition_LastRoot = 1
    TopMenuPosition_LastCategory = 3


class TopMenuObject(IntEnum):
    INVALID_TOPMENUOBJECT = 0


class TopMenu:
    pass


class TopMenuMethodMap(MethodMap):
    @native
    def FromHandle(self, handle: SourceModHandle) -> SourceModHandle[TopMenu]:
        raise SourcePawnUnboundNativeError

    @native
    def LoadConfig(self, this: SourceModHandle[TopMenu], file: str, error: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def AddCategory(self, this: SourceModHandle[TopMenu], name: str, handler: TopMenuHandler, cmdname: str, flags: int, info_string: str) -> TopMenuObject:
        raise SourcePawnUnboundNativeError

    @native
    def AddItem(self, this: SourceModHandle[TopMenu], name: str, handler: TopMenuHandler, parent: TopMenuObject, cmdname: str, flags: int, info_string: str) -> TopMenuObject:
        raise SourcePawnUnboundNativeError

    @native
    def GetInfoString(self, this: SourceModHandle[TopMenu], parent: TopMenuObject, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetObjName(self, this: SourceModHandle[TopMenu], topobj: TopMenuObject, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def Remove(self, this: SourceModHandle[TopMenu], topobj: TopMenuObject) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Display(self, this: SourceModHandle[TopMenu], client: int, position: TopMenuPosition) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DisplayCategory(self, this: SourceModHandle[TopMenu], category: TopMenuObject, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FindCategory(self, this: SourceModHandle[TopMenu], name: str) -> TopMenuObject:
        raise SourcePawnUnboundNativeError


class TopmenusNatives(SourceModNativesMixin):
    TopMenu = TopMenuMethodMap()

    @native
    def CreateTopMenu(self, handler: TopMenuHandler) -> SourceModHandle[TopMenu]:
        raise SourcePawnUnboundNativeError

    @native
    def LoadTopMenuConfig(self, topmenu: SourceModHandle, file: str, error: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def AddToTopMenu(self, topmenu: SourceModHandle, name: str, type_: TopMenuObjectType, handler: TopMenuHandler, parent: TopMenuObject, cmdname: str, flags: int, info_string: str) -> TopMenuObject:
        raise SourcePawnUnboundNativeError

    @native
    def GetTopMenuInfoString(self, topmenu: SourceModHandle, parent: TopMenuObject, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetTopMenuObjName(self, topmenu: SourceModHandle, topobj: TopMenuObject, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveFromTopMenu(self, topmenu: SourceModHandle, topobj: TopMenuObject) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DisplayTopMenu(self, topmenu: SourceModHandle, client: int, position: TopMenuPosition) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DisplayTopMenuCategory(self, topmenu: SourceModHandle, category: TopMenuObject, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FindTopMenuCategory(self, topmenu: SourceModHandle, name: str) -> TopMenuObject:
        raise SourcePawnUnboundNativeError

    @native
    def SetTopMenuTitleCaching(self, topmenu: SourceModHandle, cache_titles: bool) -> None:
        raise SourcePawnUnboundNativeError
