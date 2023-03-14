from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    MethodMap,
    SourceModNativesMixin,
    WritableString,
    native,
)


class BfWrite:
    pass


class BfRead:
    pass


class BfWriteMethodMap(MethodMap):
    @native
    def WriteBool(self, this: SourceModHandle[BfWrite], bit: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteByte(self, this: SourceModHandle[BfWrite], byte: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteChar(self, this: SourceModHandle[BfWrite], chr_: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteShort(self, this: SourceModHandle[BfWrite], num: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteWord(self, this: SourceModHandle[BfWrite], num: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteNum(self, this: SourceModHandle[BfWrite], num: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteFloat(self, this: SourceModHandle[BfWrite], num: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteString(self, this: SourceModHandle[BfWrite], string: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteEntity(self, this: SourceModHandle[BfWrite], ent: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteAngle(self, this: SourceModHandle[BfWrite], angle: float, num_bits: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteCoord(self, this: SourceModHandle[BfWrite], coord: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteVecCoord(self, this: SourceModHandle[BfWrite], coord: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteVecNormal(self, this: SourceModHandle[BfWrite], vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def WriteAngles(self, this: SourceModHandle[BfWrite], angles: Array[float]) -> None:
        raise SourcePawnUnboundNativeError


class BfReadMethodMap(MethodMap):
    @native
    def ReadBool(self, this: SourceModHandle[BfRead]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadByte(self, this: SourceModHandle[BfRead]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadChar(self, this: SourceModHandle[BfRead]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadShort(self, this: SourceModHandle[BfRead]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadWord(self, this: SourceModHandle[BfRead]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadNum(self, this: SourceModHandle[BfRead]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadFloat(self, this: SourceModHandle[BfRead]) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def ReadString(self, this: SourceModHandle[BfRead], buffer: WritableString, line: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadEntity(self, this: SourceModHandle[BfRead]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadAngle(self, this: SourceModHandle[BfRead], num_bits: int) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def ReadCoord(self, this: SourceModHandle[BfRead]) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def ReadVecCoord(self, this: SourceModHandle[BfRead], coord: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadVecNormal(self, this: SourceModHandle[BfRead], vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadAngles(self, this: SourceModHandle[BfRead], angles: Array[float]) -> None:
        raise SourcePawnUnboundNativeError


class BitbufferNatives(SourceModNativesMixin):
    BfWrite = BfWriteMethodMap()
    BfRead = BfReadMethodMap()

    @native
    def BfWriteBool(self, bf: SourceModHandle, bit: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteByte(self, bf: SourceModHandle, byte: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteChar(self, bf: SourceModHandle, chr_: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteShort(self, bf: SourceModHandle, num: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteWord(self, bf: SourceModHandle, num: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteNum(self, bf: SourceModHandle, num: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteFloat(self, bf: SourceModHandle, num: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteString(self, bf: SourceModHandle, string: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteEntity(self, bf: SourceModHandle, ent: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteAngle(self, bf: SourceModHandle, angle: float, num_bits: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteCoord(self, bf: SourceModHandle, coord: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteVecCoord(self, bf: SourceModHandle, coord: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteVecNormal(self, bf: SourceModHandle, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfWriteAngles(self, bf: SourceModHandle, angles: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadBool(self, bf: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadByte(self, bf: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadChar(self, bf: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadShort(self, bf: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadWord(self, bf: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadNum(self, bf: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadFloat(self, bf: SourceModHandle) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadString(self, bf: SourceModHandle, buffer: WritableString, line: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadEntity(self, bf: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadAngle(self, bf: SourceModHandle, num_bits: int) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadCoord(self, bf: SourceModHandle) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadVecCoord(self, bf: SourceModHandle, coord: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadVecNormal(self, bf: SourceModHandle, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfReadAngles(self, bf: SourceModHandle, angles: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BfGetNumBytesLeft(self, bf: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError
