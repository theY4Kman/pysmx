from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.runtime import PluginFunction
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    MethodMap,
    SourceModNativesMixin,
    native,
)


class DataPackPos(IntEnum):
    pass


class DataPack:
    pass


class DataPackMethodMap(MethodMap):
    @native
    def WriteCell(self, this: SourceModHandle[DataPack], cell: int, insert: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteFloat(self, this: SourceModHandle[DataPack], val: float, insert: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteString(self, this: SourceModHandle[DataPack], str_: str, insert: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteFunction(self, this: SourceModHandle[DataPack], fktptr: PluginFunction, insert: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteCellArray(self, this: SourceModHandle[DataPack], array: Array[int], count: int, insert: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteFloatArray(self, this: SourceModHandle[DataPack], array: Array[float], count: int, insert: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadCell(self, this: SourceModHandle[DataPack]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadFloat(self, this: SourceModHandle[DataPack]) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def ReadString(self, this: SourceModHandle[DataPack], buffer: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadFunction(self, this: SourceModHandle[DataPack]) -> PluginFunction:
        raise SourcePawnUnboundNativeError

    @native
    def ReadCellArray(self, this: SourceModHandle[DataPack], buffer: Array[int], count: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadFloatArray(self, this: SourceModHandle[DataPack], buffer: Array[float], count: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Reset(self, this: SourceModHandle[DataPack], clear: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def IsReadable(self, this: SourceModHandle[DataPack], unused: int) -> bool:
        raise SourcePawnUnboundNativeError


class DatapackNatives(SourceModNativesMixin):
    DataPack = DataPackMethodMap()

    @native
    def CreateDataPack(self) -> SourceModHandle[DataPack]:
        raise SourcePawnUnboundNativeError

    @native
    def WritePackCell(self, pack: SourceModHandle, cell: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WritePackFloat(self, pack: SourceModHandle, val: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WritePackString(self, pack: SourceModHandle, str_: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WritePackFunction(self, pack: SourceModHandle, fktptr: PluginFunction) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadPackCell(self, pack: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadPackFloat(self, pack: SourceModHandle) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def ReadPackString(self, pack: SourceModHandle, buffer: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadPackFunction(self, pack: SourceModHandle) -> PluginFunction:
        raise SourcePawnUnboundNativeError

    @native
    def ResetPack(self, pack: SourceModHandle, clear: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetPackPosition(self, pack: SourceModHandle) -> DataPackPos:
        raise SourcePawnUnboundNativeError

    @native
    def SetPackPosition(self, pack: SourceModHandle, position: DataPackPos) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def IsPackReadable(self, pack: SourceModHandle, bytes_: int) -> bool:
        raise SourcePawnUnboundNativeError
