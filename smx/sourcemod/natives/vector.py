from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import Array, SourceModNativesMixin, native


class VectorNatives(SourceModNativesMixin):
    @native
    def GetVectorLength(self, vec: Array[float], squared: bool) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetVectorDistance(self, vec1: Array[float], vec2: Array[float], squared: bool) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetVectorDotProduct(self, vec1: Array[float], vec2: Array[float]) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetVectorCrossProduct(self, vec1: Array[float], vec2: Array[float], result: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def NormalizeVector(self, vec: Array[float], result: Array[float]) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetAngleVectors(self, angle: Array[float], fwd: Array[float], right: Array[float], up: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetVectorAngles(self, vec: Array[float], angle: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetVectorVectors(self, vec: Array[float], right: Array[float], up: Array[float]) -> None:
        raise SourcePawnUnboundNativeError
