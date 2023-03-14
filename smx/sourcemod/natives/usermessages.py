from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    SourceModNativesMixin,
    WritableString,
    native,
)


MsgHook = Callable
MsgPostHook = Callable


class UserMsg(IntEnum):
    INVALID_MESSAGE_ID = -1


class UserMessageType(IntEnum):
    UM_BitBuf = 0
    UM_Protobuf = 1


class UsermessagesNatives(SourceModNativesMixin):
    @native
    def GetUserMessageType(self) -> UserMessageType:
        raise SourcePawnUnboundNativeError

    @native
    def GetUserMessageId(self, msg: str) -> UserMsg:
        raise SourcePawnUnboundNativeError

    @native
    def GetUserMessageName(self, msg_id: UserMsg, msg: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def StartMessage(self, msgname: str, clients: Array[int], num_clients: int, flags: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def StartMessageEx(self, msg: UserMsg, clients: Array[int], num_clients: int, flags: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def EndMessage(self) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def HookUserMessage(self, msg_id: UserMsg, hook: MsgHook, intercept: bool, post: MsgPostHook) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def UnhookUserMessage(self, msg_id: UserMsg, hook: MsgHook, intercept: bool) -> None:
        raise SourcePawnUnboundNativeError
