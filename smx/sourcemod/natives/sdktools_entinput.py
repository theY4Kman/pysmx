from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class SdktoolsEntinputNatives(SourceModNativesMixin):
    @native
    def AcceptEntityInput(self, dest: int, input: str, activator: int, caller: int, outputid: int) -> bool:
        raise SourcePawnUnboundNativeError
