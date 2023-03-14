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


class Protobuf:
    pass


class ProtobufMethodMap(MethodMap):
    @native
    def ReadInt(self, this: SourceModHandle[Protobuf], field: str, index: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadInt64(self, this: SourceModHandle[Protobuf], field: str, value: Array[int], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadFloat(self, this: SourceModHandle[Protobuf], field: str, index: int) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def ReadBool(self, this: SourceModHandle[Protobuf], field: str, index: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadString(self, this: SourceModHandle[Protobuf], field: str, buffer: WritableString, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadColor(self, this: SourceModHandle[Protobuf], field: str, buffer: Array[int], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadAngle(self, this: SourceModHandle[Protobuf], field: str, buffer: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadVector(self, this: SourceModHandle[Protobuf], field: str, buffer: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadVector2D(self, this: SourceModHandle[Protobuf], field: str, buffer: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetRepeatedFieldCount(self, this: SourceModHandle[Protobuf], field: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def HasField(self, this: SourceModHandle[Protobuf], field: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetInt(self, this: SourceModHandle[Protobuf], field: str, value: int, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetInt64(self, this: SourceModHandle[Protobuf], field: str, value: Array[int], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetFloat(self, this: SourceModHandle[Protobuf], field: str, value: float, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetBool(self, this: SourceModHandle[Protobuf], field: str, value: bool, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetString(self, this: SourceModHandle[Protobuf], field: str, value: str, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetColor(self, this: SourceModHandle[Protobuf], field: str, color: Array[int], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetAngle(self, this: SourceModHandle[Protobuf], field: str, angle: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVector(self, this: SourceModHandle[Protobuf], field: str, vec: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVector2D(self, this: SourceModHandle[Protobuf], field: str, vec: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddInt(self, this: SourceModHandle[Protobuf], field: str, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddInt64(self, this: SourceModHandle[Protobuf], field: str, value: Array[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddFloat(self, this: SourceModHandle[Protobuf], field: str, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddBool(self, this: SourceModHandle[Protobuf], field: str, value: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddString(self, this: SourceModHandle[Protobuf], field: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddColor(self, this: SourceModHandle[Protobuf], field: str, color: Array[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddAngle(self, this: SourceModHandle[Protobuf], field: str, angle: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddVector(self, this: SourceModHandle[Protobuf], field: str, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddVector2D(self, this: SourceModHandle[Protobuf], field: str, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveRepeatedFieldValue(self, this: SourceModHandle[Protobuf], field: str, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ReadMessage(self, this: SourceModHandle[Protobuf], field: str) -> SourceModHandle[Protobuf]:
        raise SourcePawnUnboundNativeError

    @native
    def ReadRepeatedMessage(self, this: SourceModHandle[Protobuf], field: str, index: int) -> SourceModHandle[Protobuf]:
        raise SourcePawnUnboundNativeError

    @native
    def AddMessage(self, this: SourceModHandle[Protobuf], field: str) -> SourceModHandle[Protobuf]:
        raise SourcePawnUnboundNativeError


class ProtobufNatives(SourceModNativesMixin):
    Protobuf = ProtobufMethodMap()

    @native
    def PbReadInt(self, pb: SourceModHandle, field: str, index: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PbReadFloat(self, pb: SourceModHandle, field: str, index: int) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def PbReadBool(self, pb: SourceModHandle, field: str, index: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def PbReadString(self, pb: SourceModHandle, field: str, buffer: WritableString, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbReadColor(self, pb: SourceModHandle, field: str, buffer: Array[int], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbReadAngle(self, pb: SourceModHandle, field: str, buffer: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbReadVector(self, pb: SourceModHandle, field: str, buffer: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbReadVector2D(self, pb: SourceModHandle, field: str, buffer: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbGetRepeatedFieldCount(self, pb: SourceModHandle, field: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PbSetInt(self, pb: SourceModHandle, field: str, value: int, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbSetFloat(self, pb: SourceModHandle, field: str, value: float, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbSetBool(self, pb: SourceModHandle, field: str, value: bool, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbSetString(self, pb: SourceModHandle, field: str, value: str, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbSetColor(self, pb: SourceModHandle, field: str, color: Array[int], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbSetAngle(self, pb: SourceModHandle, field: str, angle: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbSetVector(self, pb: SourceModHandle, field: str, vec: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbSetVector2D(self, pb: SourceModHandle, field: str, vec: Array[float], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbAddInt(self, pb: SourceModHandle, field: str, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbAddFloat(self, pb: SourceModHandle, field: str, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbAddBool(self, pb: SourceModHandle, field: str, value: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbAddString(self, pb: SourceModHandle, field: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbAddColor(self, pb: SourceModHandle, field: str, color: Array[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbAddAngle(self, pb: SourceModHandle, field: str, angle: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbAddVector(self, pb: SourceModHandle, field: str, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbAddVector2D(self, pb: SourceModHandle, field: str, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbRemoveRepeatedFieldValue(self, pb: SourceModHandle, field: str, index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PbReadMessage(self, pb: SourceModHandle, field: str) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def PbReadRepeatedMessage(self, pb: SourceModHandle, field: str, index: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def PbAddMessage(self, pb: SourceModHandle, field: str) -> SourceModHandle:
        raise SourcePawnUnboundNativeError
