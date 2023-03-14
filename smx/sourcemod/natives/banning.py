from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class BanningNatives(SourceModNativesMixin):
    @native
    def BanClient(self, client: int, time: int, flags: int, reason: str, kick_message: str, command: str, source: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def BanIdentity(self, identity: str, time: int, flags: int, reason: str, command: str, source: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveBan(self, identity: str, flags: int, command: str, source: int) -> bool:
        raise SourcePawnUnboundNativeError
