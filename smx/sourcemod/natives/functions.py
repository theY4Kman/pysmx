from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.runtime import PluginFunction
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    MethodMap,
    Pointer,
    SourceModNativesMixin,
    WritableString,
    native,
)


NativeCall = Callable
RequestFrameCallback = Callable


class ParamType(IntEnum):
    Param_Any = 0
    Param_Cell = 2
    Param_Float = 4
    Param_String = 7
    Param_Array = 9
    Param_VarArgs = 10
    Param_CellByRef = 3
    Param_FloatByRef = 5


class ExecType(IntEnum):
    ET_Ignore = 0
    ET_Single = 1
    ET_Event = 2
    ET_Hook = 3


class GlobalForward:
    pass


class PrivateForward(GlobalForward):
    pass


class GlobalForwardMethodMap(MethodMap):
    pass


class PrivateForwardMethodMap(GlobalForwardMethodMap):
    @native
    def AddFunction(self, this: SourceModHandle[PrivateForward], plugin: SourceModHandle, func: PluginFunction) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveFunction(self, this: SourceModHandle[PrivateForward], plugin: SourceModHandle, func: PluginFunction) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveAllFunctions(self, this: SourceModHandle[PrivateForward], plugin: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError


class FunctionsNatives(SourceModNativesMixin):
    GlobalForward = GlobalForwardMethodMap()
    PrivateForward = PrivateForwardMethodMap()

    @native
    def GetFunctionByName(self, plugin: SourceModHandle, name: str) -> PluginFunction:
        raise SourcePawnUnboundNativeError

    @native
    def CreateGlobalForward(self, name: str, type_: ExecType, *args) -> SourceModHandle[GlobalForward]:
        raise SourcePawnUnboundNativeError

    @native
    def CreateForward(self, type_: ExecType, *args) -> SourceModHandle[PrivateForward]:
        raise SourcePawnUnboundNativeError

    @native
    def GetForwardFunctionCount(self, fwd: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def AddToForward(self, fwd: SourceModHandle, plugin: SourceModHandle, func: PluginFunction) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveFromForward(self, fwd: SourceModHandle, plugin: SourceModHandle, func: PluginFunction) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveAllFromForward(self, fwd: SourceModHandle, plugin: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def Call_StartForward(self, fwd: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_StartFunction(self, plugin: SourceModHandle, func: PluginFunction) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_PushCell(self, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_PushCellRef(self, value: Pointer[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_PushFloat(self, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_PushFloatRef(self, value: Pointer[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_PushArray(self, value: Array[int], size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_PushArrayEx(self, value: Array[int], size: int, cpflags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_PushNullVector(self) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_PushString(self, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_PushStringEx(self, value: str, length: int, szflags: int, cpflags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_PushNullString(self) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Call_Finish(self, result: Pointer[int]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def Call_Cancel(self) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CreateNative(self, name: str, func: NativeCall) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ThrowNativeError(self, error: int, fmt: str, *args) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetNativeStringLength(self, param: int, length: Pointer[int]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetNativeString(self, param: int, buffer: WritableString, bytes_: Pointer[int]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetNativeString(self, param: int, source: WritableString, utf8: bool, bytes_: Pointer[int]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetNativeCell(self, param: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetNativeFunction(self, param: int) -> PluginFunction:
        raise SourcePawnUnboundNativeError

    @native
    def GetNativeCellRef(self, param: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetNativeCellRef(self, param: int, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetNativeArray(self, param: int, local: Array[int], size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetNativeArray(self, param: int, local: Array[int], size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsNativeParamNullVector(self, param: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsNativeParamNullString(self, param: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FormatNativeString(self, out_param: int, fmt_param: int, vararg_param: int, out_len: int, written: Pointer[int], out_string: str, fmt_string: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def RequestFrame(self, function: RequestFrameCallback, data: int) -> None:
        raise SourcePawnUnboundNativeError
