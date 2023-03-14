from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import Array, SourceModNativesMixin, native


class SdktoolsEngineNatives(SourceModNativesMixin):
    @native
    def SetClientViewEntity(self, client: int, entity: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetLightStyle(self, style: int, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientEyePosition(self, client: int, pos: Array[float]) -> None:
        raise SourcePawnUnboundNativeError
