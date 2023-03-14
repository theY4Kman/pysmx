from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import Array, SourceModNativesMixin, native


class SdktoolsVariantTNatives(SourceModNativesMixin):
    @native
    def SetVariantBool(self, val: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVariantString(self, str_: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVariantInt(self, val: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVariantFloat(self, val: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVariantVector3D(self, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVariantPosVector3D(self, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVariantColor(self, color: Array[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVariantEntity(self, entity: int) -> None:
        raise SourcePawnUnboundNativeError
