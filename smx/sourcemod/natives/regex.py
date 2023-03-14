from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    MethodMap,
    Pointer,
    SourceModNativesMixin,
    native,
)


class RegexError(IntEnum):
    REGEX_ERROR_NONE = 0
    REGEX_ERROR_ASSERT = 1
    REGEX_ERROR_BADBR = 2
    REGEX_ERROR_BADPAT = 3
    REGEX_ERROR_BADRPT = 4
    REGEX_ERROR_EBRACE = 5
    REGEX_ERROR_EBRACK = 6
    REGEX_ERROR_ECOLLATE = 7
    REGEX_ERROR_ECTYPE = 8
    REGEX_ERROR_EESCAPE = 9
    REGEX_ERROR_EMPTY = 10
    REGEX_ERROR_EPAREN = 11
    REGEX_ERROR_ERANGE = 12
    REGEX_ERROR_ESIZE = 13
    REGEX_ERROR_ESPACE = 14
    REGEX_ERROR_ESUBREG = 15
    REGEX_ERROR_INVARG = 16
    REGEX_ERROR_NOMATCH = -1
    REGEX_ERROR_NULL = -2
    REGEX_ERROR_BADOPTION = -3
    REGEX_ERROR_BADMAGIC = -4
    REGEX_ERROR_UNKNOWN_OPCODE = -5
    REGEX_ERROR_NOMEMORY = -6
    REGEX_ERROR_NOSUBSTRING = -7
    REGEX_ERROR_MATCHLIMIT = -8
    REGEX_ERROR_CALLOUT = -9
    REGEX_ERROR_BADUTF8 = -10
    REGEX_ERROR_BADUTF8_OFFSET = -11
    REGEX_ERROR_PARTIAL = -12
    REGEX_ERROR_BADPARTIAL = -13
    REGEX_ERROR_INTERNAL = -14
    REGEX_ERROR_BADCOUNT = -15
    REGEX_ERROR_DFA_UITEM = -16
    REGEX_ERROR_DFA_UCOND = -17
    REGEX_ERROR_DFA_UMLIMIT = -18
    REGEX_ERROR_DFA_WSSIZE = -19
    REGEX_ERROR_DFA_RECURSE = -20
    REGEX_ERROR_RECURSIONLIMIT = -21
    REGEX_ERROR_NULLWSLIMIT = -22
    REGEX_ERROR_BADNEWLINE = -23
    REGEX_ERROR_BADOFFSET = -24
    REGEX_ERROR_SHORTUTF8 = -25
    REGEX_ERROR_RECURSELOOP = -26
    REGEX_ERROR_JIT_STACKLIMIT = -27
    REGEX_ERROR_BADMODE = -28
    REGEX_ERROR_BADENDIANNESS = -29
    REGEX_ERROR_DFA_BADRESTART = -30
    REGEX_ERROR_JIT_BADOPTION = -31
    REGEX_ERROR_BADLENGTH = -32


class Regex:
    pass


class RegexMethodMap(MethodMap):
    @native
    def Match(self, this: SourceModHandle[Regex], str_: str, ret: Pointer[RegexError], offset: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def MatchAll(self, this: SourceModHandle[Regex], str_: str, ret: Pointer[RegexError]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetSubString(self, this: SourceModHandle[Regex], str_id: int, buffer: str, maxlen: int, match: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def MatchCount(self, this: SourceModHandle[Regex]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CaptureCount(self, this: SourceModHandle[Regex], match: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def MatchOffset(self, this: SourceModHandle[Regex], match: int) -> int:
        raise SourcePawnUnboundNativeError


class RegexNatives(SourceModNativesMixin):
    Regex = RegexMethodMap()

    @native
    def CompileRegex(self, pattern: str, flags: int, error: str, max_len: int, errcode: Pointer[RegexError]) -> SourceModHandle[Regex]:
        raise SourcePawnUnboundNativeError

    @native
    def MatchRegex(self, regex: SourceModHandle, str_: str, ret: Pointer[RegexError], offset: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetRegexSubString(self, regex: SourceModHandle, str_id: int, buffer: str, maxlen: int) -> bool:
        raise SourcePawnUnboundNativeError
