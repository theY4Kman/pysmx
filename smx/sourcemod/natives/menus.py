from __future__ import annotations

from enum import IntEnum
from typing import Callable

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


VoteHandler = Callable
MenuHandler = Callable


class MenuStyle(IntEnum):
    MenuStyle_Default = 0
    MenuStyle_Valve = 1
    MenuStyle_Radio = 2


class MenuAction(IntEnum):
    MenuAction_Start = 1
    MenuAction_Display = 2
    MenuAction_Select = 4
    MenuAction_Cancel = 8
    MenuAction_End = 16
    MenuAction_VoteEnd = 32
    MenuAction_VoteStart = 64
    MenuAction_VoteCancel = 128
    MenuAction_DrawItem = 256
    MenuAction_DisplayItem = 512


class MenuSource(IntEnum):
    MenuSource_None = 0
    MenuSource_External = 1
    MenuSource_Normal = 2
    MenuSource_RawPanel = 3


class Panel:
    pass


class Menu:
    pass


class PanelMethodMap(MethodMap):
    @native
    def SetTitle(self, this: SourceModHandle[Panel], text: str, only_if_empty: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DrawText(self, this: SourceModHandle[Panel], text: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CanDrawFlags(self, this: SourceModHandle[Panel], style: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetKeys(self, this: SourceModHandle[Panel], keys: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Send(self, this: SourceModHandle[Panel], client: int, handler: MenuHandler, time: int) -> bool:
        raise SourcePawnUnboundNativeError


class MenuMethodMap(MethodMap):
    @native
    def Display(self, this: SourceModHandle[Menu], client: int, time: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DisplayAt(self, this: SourceModHandle[Menu], client: int, first_item: int, time: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveItem(self, this: SourceModHandle[Menu], position: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveAllItems(self, this: SourceModHandle[Menu]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetItem(self, this: SourceModHandle[Menu], position: int, info_buf: str, info_buf_len: int, style: Pointer[int], disp_buf: str, disp_buf_len: int, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ShufflePerClient(self, this: SourceModHandle[Menu], start: int, stop: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetClientMapping(self, this: SourceModHandle[Menu], client: int, array: Array[int], length: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetTitle(self, this: SourceModHandle[Menu], fmt: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetTitle(self, this: SourceModHandle[Menu], buffer: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ToPanel(self, this: SourceModHandle[Menu]) -> SourceModHandle[Panel]:
        raise SourcePawnUnboundNativeError

    @native
    def Cancel(self, this: SourceModHandle[Menu]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DisplayVote(self, this: SourceModHandle[Menu], clients: Array[int], num_clients: int, time: int, flags: int) -> bool:
        raise SourcePawnUnboundNativeError


class MenusNatives(SourceModNativesMixin):
    Panel = PanelMethodMap()
    Menu = MenuMethodMap()

    @native
    def CreateMenu(self, handler: MenuHandler, actions: MenuAction) -> SourceModHandle[Menu]:
        raise SourcePawnUnboundNativeError

    @native
    def DisplayMenu(self, menu: SourceModHandle, client: int, time: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DisplayMenuAtItem(self, menu: SourceModHandle, client: int, first_item: int, time: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveMenuItem(self, menu: SourceModHandle, position: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveAllMenuItems(self, menu: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetMenuItem(self, menu: SourceModHandle, position: int, info_buf: str, info_buf_len: int, style: Pointer[int], disp_buf: str, disp_buf_len: int, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def MenuShufflePerClient(self, menu: SourceModHandle, start: int, stop: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def MenuSetClientMapping(self, menu: SourceModHandle, client: int, array: Array[int], length: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetMenuSelectionPosition(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetMenuItemCount(self, menu: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetMenuPagination(self, menu: SourceModHandle, items_per_page: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetMenuPagination(self, menu: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetMenuStyle(self, menu: SourceModHandle) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def SetMenuTitle(self, menu: SourceModHandle, fmt: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetMenuTitle(self, menu: SourceModHandle, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CreatePanelFromMenu(self, menu: SourceModHandle) -> SourceModHandle[Panel]:
        raise SourcePawnUnboundNativeError

    @native
    def GetMenuExitButton(self, menu: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetMenuExitButton(self, menu: SourceModHandle, button: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetMenuExitBackButton(self, menu: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetMenuExitBackButton(self, menu: SourceModHandle, button: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetMenuNoVoteButton(self, menu: SourceModHandle, button: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CancelMenu(self, menu: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetMenuOptionFlags(self, menu: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetMenuOptionFlags(self, menu: SourceModHandle, flags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def IsVoteInProgress(self, menu: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CancelVote(self) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def VoteMenu(self, menu: SourceModHandle, clients: Array[int], num_clients: int, time: int, flags: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetVoteResultCallback(self, menu: SourceModHandle, callback: VoteHandler) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CheckVoteDelay(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsClientInVotePool(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RedrawClientVoteMenu(self, client: int, revotes: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetMenuStyleHandle(self, style: MenuStyle) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def CreatePanel(self, h_style: SourceModHandle) -> SourceModHandle[Panel]:
        raise SourcePawnUnboundNativeError

    @native
    def CreateMenuEx(self, h_style: SourceModHandle, handler: MenuHandler, actions: MenuAction) -> SourceModHandle[Menu]:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientMenu(self, client: int, h_style: SourceModHandle) -> MenuSource:
        raise SourcePawnUnboundNativeError

    @native
    def CancelClientMenu(self, client: int, auto_ignore: bool, h_style: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetMaxPageItems(self, h_style: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetPanelStyle(self, panel: SourceModHandle) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def SetPanelTitle(self, panel: SourceModHandle, text: str, only_if_empty: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DrawPanelText(self, panel: SourceModHandle, text: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CanPanelDrawFlags(self, panel: SourceModHandle, style: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetPanelKeys(self, panel: SourceModHandle, keys: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SendPanelToClient(self, panel: SourceModHandle, client: int, handler: MenuHandler, time: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetPanelTextRemaining(self, panel: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetPanelCurrentKey(self, panel: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetPanelCurrentKey(self, panel: SourceModHandle, key: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RedrawMenuItem(self, text: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def InternalShowMenu(self, client: int, str_: str, time: int, keys: int, handler: MenuHandler) -> bool:
        raise SourcePawnUnboundNativeError
