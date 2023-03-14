from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import Array, SourceModNativesMixin, native


SortFunc2D = Callable
SortFunc1D = Callable
SortFuncADTArray = Callable


class SortOrder(IntEnum):
    Sort_Ascending = 0
    Sort_Descending = 1
    Sort_Random = 2


class SortType(IntEnum):
    Sort_Integer = 0
    Sort_Float = 1
    Sort_String = 2


class SortingNatives(SourceModNativesMixin):
    @native
    def SortIntegers(self, array: Array[int], array_size: int, order: SortOrder) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SortFloats(self, array: Array[float], array_size: int, order: SortOrder) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SortStrings(self, array: str, array_size: int, order: SortOrder) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SortCustom1D(self, array: Array[int], array_size: int, sortfunc: SortFunc1D, hndl: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SortCustom2D(self, array: Array[Array[int]], array_size: int, sortfunc: SortFunc2D, hndl: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SortADTArray(self, array: SourceModHandle, order: SortOrder, type_: SortType) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SortADTArrayCustom(self, array: SourceModHandle, sortfunc: SortFuncADTArray, hndl: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError
