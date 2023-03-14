from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class BasecommNatives(SourceModNativesMixin):
    @native
    def BaseComm_IsClientGagged(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def BaseComm_IsClientMuted(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def BaseComm_SetClientGag(self, client: int, gag_state: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def BaseComm_SetClientMute(self, client: int, mute_state: bool) -> bool:
        raise SourcePawnUnboundNativeError
