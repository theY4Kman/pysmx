from __future__ import annotations

import re

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import Array, native, Pointer, SourceModNativesMixin, WritableString

RGX_BREAK_STRING = re.compile(
    r'^\s*(?:"(?P<quoted>[^"]*)(?:"|$)|(?P<unquoted>\S+))(?P<end_ws>\s*)',
    # ASCII mode ensures \s only matches "\n\v\r\t\f ", like SM does
    flags=re.ASCII,
)


class StringNatives(SourceModNativesMixin):
    @native
    def strlen(self, string: str) -> int:
        return len(string)

    @native
    def StrContains(self, string: str, substr: str, case_sensitive: bool = True) -> int:
        if not case_sensitive:
            string = string.lower()
            substr = substr.lower()

        return string.find(substr)

    def _strcmp(self, str1: str, str2: str, case_sensitive: bool = True) -> int:
        if not case_sensitive:
            str1 = str1.lower()
            str2 = str2.lower()

        return (str1 > str2) - (str1 < str2)

    @native
    def strcmp(self, str1: str, str2: str, case_sensitive: bool = True) -> int:
        return self._strcmp(str1, str2, case_sensitive)

    @native
    def strncmp(self, str1: str, str2: str, num: int, case_sensitive: bool = True) -> int:
        return self._strcmp(str1[:num], str2[:num], case_sensitive)

    @native
    def strcopy(self, dest: WritableString, src: str) -> int:
        return dest.write(src, null_terminate=True)

    @native
    def Format(self, buffer: WritableString, format_: str, *args) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FormatEx(self, buffer: WritableString, format_: str, *args) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def VFormat(self, buffer: WritableString, format_: str, varpos: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def StringToInt(self, str_: str, n_base: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def StringToIntEx(self, str_: str, result: Pointer[int], n_base: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def StringToInt64(self, str_: str, result: Array[int], n_base: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IntToString(self, num: int, str: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def Int64ToString(self, num: Array[int], str: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def StringToFloat(self, str_: str) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def StringToFloatEx(self, str_: str, result: Pointer[float]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FloatToString(self, num: float, str: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def BreakString(self, source: str, arg: WritableString) -> int:
        if not source:
            arg.write(b'', null_terminate=True)
            return -1

        match = RGX_BREAK_STRING.match(source)
        if match is None:
            arg.write(b'', null_terminate=True)
            return -1

        arg.write(match.group('quoted') or match.group('unquoted'), null_terminate=True)

        if not match.group('end_ws'):
            return -1

        return match.endpos

    @native
    def TrimString(self, string_offs: int) -> int:
        buf = WritableString(self.amx, string_offs, -1)
        string = buf.read()
        if len(string) == 0:
            return 0

        buf.max_length = len(string)
        return buf.write(string.strip(), null_terminate=True)

    @native
    def SplitString(self, source: str, split: str, part: str, part_len: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReplaceString(self, text: WritableString, search: str, replace: str, case_sensitive: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReplaceStringEx(self, text: WritableString, search: str, replace: str, search_len: int, replace_len: int, case_sensitive: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetCharBytes(self, source: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsCharAlpha(self, chr_: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsCharNumeric(self, chr_: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsCharSpace(self, chr_: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsCharMB(self, chr_: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsCharUpper(self, chr_: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsCharLower(self, chr_: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def StripQuotes(self, text: str) -> bool:
        raise SourcePawnUnboundNativeError
