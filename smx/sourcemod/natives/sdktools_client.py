from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class SdktoolsClientNatives(SourceModNativesMixin):
    @native
    def InactivateClient(self, client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReconnectClient(self, client: int) -> None:
        raise SourcePawnUnboundNativeError
