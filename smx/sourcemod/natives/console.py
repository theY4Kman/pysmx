from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.admin import AdminId
from smx.sourcemod.natives.base import (MethodMap, native, Pointer, SourceModNativesMixin, WritableString)
from smx.sourcemod.natives.keyvalues import KeyValues
from smx.sourcemod.printf import atcprintf

SrvCmd = Callable
ConCmd = Callable
CommandListener = Callable


class QueryCookie(IntEnum):
    QUERYCOOKIE_FAILED = 0


class ReplySource(IntEnum):
    SM_REPLY_TO_CONSOLE = 0
    SM_REPLY_TO_CHAT = 1


class CommandIterator:
    pass


class CommandIteratorMethodMap(MethodMap):
    @native
    def Next(self, this: SourceModHandle[CommandIterator]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetDescription(self, this: SourceModHandle[CommandIterator], buffer: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetName(self, this: SourceModHandle[CommandIterator], buffer: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError


class ConsoleNatives(SourceModNativesMixin):
    CommandIterator = CommandIteratorMethodMap()

    @native
    def ServerCommand(self, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ServerCommandEx(self, buffer: str, maxlen: int, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def InsertServerCommand(self, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ServerExecute(self) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ClientCommand(self, client: int, fmt: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FakeClientCommand(self, client: int, fmt: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FakeClientCommandEx(self, client: int, fmt: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FakeClientCommandKeyValues(self, client: int, kv: SourceModHandle[SourceModHandle[KeyValues]]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PrintToServer(self, fmt: str, *args):
        out = atcprintf(self.amx, fmt, args)
        self.runtime.printf(out)

    @native
    def PrintToConsole(self, client: int, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReplyToCommand(self, client: int, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetCmdReplySource(self) -> ReplySource:
        raise SourcePawnUnboundNativeError

    @native
    def SetCmdReplySource(self, source: ReplySource) -> ReplySource:
        raise SourcePawnUnboundNativeError

    @native
    def IsChatTrigger(self) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ShowActivity2(self, client: int, tag: str, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ShowActivity(self, client: int, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ShowActivityEx(self, client: int, tag: str, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FormatActivitySource(self, client: int, target: int, namebuf: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RegServerCmd(self, cmd: str, callback: SrvCmd, description: str, flags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RegConsoleCmd(self, cmd: str, callback: ConCmd, description: str, flags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RegAdminCmd(self, cmd: str, callback: ConCmd, adminflags: int, description: str, group: str, flags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetCmdArgs(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetCmdArg(self, argnum: int, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetCmdArgString(self, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetCommandIterator(self) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def ReadCommandIterator(self, iter_: SourceModHandle, name: str, name_len: int, eflags: Pointer[int], desc: str, desc_len: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CheckCommandAccess(self, client: int, command: str, flags: int, override_only: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CheckAccess(self, id: AdminId, command: str, flags: int, override_only: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetCommandFlags(self, name: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetCommandFlags(self, name: str, flags: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FindFirstConCommand(self, buffer: str, max_size: int, is_command: Pointer[bool], flags: Pointer[int], description: str, descrmax_size: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def FindNextConCommand(self, search: SourceModHandle, buffer: str, max_size: int, is_command: Pointer[bool], flags: Pointer[int], description: str, descrmax_size: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def AddServerTag(self, tag: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveServerTag(self, tag: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddCommandListener(self, callback: CommandListener, command: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveCommandListener(self, callback: CommandListener, command: str) -> None:
        raise SourcePawnUnboundNativeError
