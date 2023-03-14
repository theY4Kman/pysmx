from __future__ import annotations

from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import Array, SourceModNativesMixin, native


TEHook = Callable


class SdktoolsTempentsNatives(SourceModNativesMixin):
    @native
    def AddTempEntHook(self, te_name: str, hook: TEHook) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveTempEntHook(self, te_name: str, hook: TEHook) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TE_Start(self, te_name: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TE_IsValidProp(self, prop: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def TE_WriteNum(self, prop: str, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TE_ReadNum(self, prop: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TE_WriteFloat(self, prop: str, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TE_ReadFloat(self, prop: str) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def TE_WriteVector(self, prop: str, vector: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TE_ReadVector(self, prop: str, vector: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TE_WriteAngles(self, prop: str, angles: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TE_WriteFloatArray(self, prop: str, array: Array[float], array_size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TE_Send(self, clients: Array[int], num_clients: int, delay: float) -> None:
        raise SourcePawnUnboundNativeError
