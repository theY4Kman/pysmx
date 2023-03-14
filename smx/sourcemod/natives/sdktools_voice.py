from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class ListenOverride(IntEnum):
    Listen_Default = 0
    Listen_No = 1
    Listen_Yes = 2


class SdktoolsVoiceNatives(SourceModNativesMixin):
    @native
    def SetClientListeningFlags(self, client: int, flags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientListeningFlags(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetClientListening(self, i_receiver: int, i_sender: int, b_listen: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientListening(self, i_receiver: int, i_sender: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetListenOverride(self, i_receiver: int, i_sender: int, override: ListenOverride) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetListenOverride(self, i_receiver: int, i_sender: int) -> ListenOverride:
        raise SourcePawnUnboundNativeError

    @native
    def IsClientMuted(self, i_muter: int, i_mutee: int) -> bool:
        raise SourcePawnUnboundNativeError
