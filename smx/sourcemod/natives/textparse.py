from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    MethodMap,
    Pointer,
    SourceModNativesMixin,
    native,
)


SMC_ParseStart = Callable
SMC_NewSection = Callable
SMC_KeyValue = Callable
SMC_EndSection = Callable
SMC_ParseEnd = Callable
SMC_RawLine = Callable


class SMCResult(IntEnum):
    SMCParse_Continue = 0
    SMCParse_Halt = 1
    SMCParse_HaltFail = 2


class SMCError(IntEnum):
    SMCError_Okay = 0
    SMCError_StreamOpen = 1
    SMCError_StreamError = 2
    SMCError_Custom = 3
    SMCError_InvalidSection1 = 4
    SMCError_InvalidSection2 = 5
    SMCError_InvalidSection3 = 6
    SMCError_InvalidSection4 = 7
    SMCError_InvalidSection5 = 8
    SMCError_InvalidTokens = 9
    SMCError_TokenOverflow = 10
    SMCError_InvalidProperty1 = 11


class SMCParser:
    pass


class SMCParserMethodMap(MethodMap):
    @native
    def ParseFile(self, this: SourceModHandle[SMCParser], file: str, line: Pointer[int], col: Pointer[int]) -> SMCError:
        raise SourcePawnUnboundNativeError

    @native
    def GetErrorString(self, this: SourceModHandle[SMCParser], error: SMCError, buffer: str, buf_max: int) -> None:
        raise SourcePawnUnboundNativeError


class TextparseNatives(SourceModNativesMixin):
    SMCParser = SMCParserMethodMap()

    @native
    def SMC_CreateParser(self) -> SourceModHandle[SMCParser]:
        raise SourcePawnUnboundNativeError

    @native
    def SMC_ParseFile(self, smc: SourceModHandle, file: str, line: Pointer[int], col: Pointer[int]) -> SMCError:
        raise SourcePawnUnboundNativeError

    @native
    def SMC_GetErrorString(self, error: SMCError, buffer: str, buf_max: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SMC_SetParseStart(self, smc: SourceModHandle, func: SMC_ParseStart) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SMC_SetParseEnd(self, smc: SourceModHandle, func: SMC_ParseEnd) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SMC_SetReaders(self, smc: SourceModHandle, ns: SMC_NewSection, kv: SMC_KeyValue, es: SMC_EndSection) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SMC_SetRawLine(self, smc: SourceModHandle, func: SMC_RawLine) -> None:
        raise SourcePawnUnboundNativeError
