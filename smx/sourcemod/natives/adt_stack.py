from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    MethodMap,
    Pointer,
    SourceModNativesMixin,
    WritableString,
    native,
)


class ArrayStack:
    pass


class ArrayStackMethodMap(MethodMap):
    @native
    def Clear(self, this: SourceModHandle[ArrayStack]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Clone(self, this: SourceModHandle[ArrayStack]) -> SourceModHandle[ArrayStack]:
        raise SourcePawnUnboundNativeError

    @native
    def Push(self, this: SourceModHandle[ArrayStack], value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PushString(self, this: SourceModHandle[ArrayStack], value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PushArray(self, this: SourceModHandle[ArrayStack], values: Array[int], size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Pop(self, this: SourceModHandle[ArrayStack], block: int, as_char: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PopString(self, this: SourceModHandle[ArrayStack], buffer: WritableString, written: Pointer[int]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PopArray(self, this: SourceModHandle[ArrayStack], buffer: Array[int], size: int) -> None:
        raise SourcePawnUnboundNativeError


class AdtStackNatives(SourceModNativesMixin):
    ArrayStack = ArrayStackMethodMap()

    @native
    def CreateStack(self, blocksize: int) -> SourceModHandle[ArrayStack]:
        raise SourcePawnUnboundNativeError

    @native
    def PushStackCell(self, stack: SourceModHandle, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PushStackString(self, stack: SourceModHandle, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PushStackArray(self, stack: SourceModHandle, values: Array[int], size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PopStackCell(self, stack: SourceModHandle, value: Pointer[int], block: int, as_char: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def PopStackString(self, stack: SourceModHandle, buffer: WritableString, written: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def PopStackArray(self, stack: SourceModHandle, buffer: Array[int], size: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsStackEmpty(self, stack: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetStackBlockSize(self, stack: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError
