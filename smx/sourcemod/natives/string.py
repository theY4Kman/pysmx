from __future__ import annotations

import re

from smx.sourcemod.natives.base import native, SourceModNativesMixin, WritableString


RGX_BREAK_STRING = re.compile(
    r'^\s*(?:"(?P<quoted>[^"]*)(?:"|$)|(?P<unquoted>\S+))(?P<end_ws>\s*)',
    # ASCII mode ensures \s only matches "\n\v\r\t\f ", like SM does
    flags=re.ASCII,
)


class StringNatives(SourceModNativesMixin):
    @native('string')
    def strlen(self, string: str) -> int:
        return len(string)

    @native('string', 'string', 'bool')
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

    @native('string', 'string', 'bool')
    def strcmp(self, str1: str, str2: str, case_sensitive: bool = True) -> int:
        return self._strcmp(str1, str2, case_sensitive)

    @native('string', 'string', 'cell', 'bool')
    def strncmp(self, str1: str, str2: str, num: int, case_sensitive: bool = True) -> int:
        return self._strcmp(str1[:num], str2[:num], case_sensitive)

    @native('writable_string', 'string')
    def strcopy(self, dest: WritableString, src: str) -> int:
        return dest.write(src, null_terminate=True)

    @native('cell')
    def TrimString(self, string_offs: int) -> int:
        buf = WritableString(self.amx, string_offs, -1)
        string = buf.read()
        if len(string) == 0:
            return 0

        buf.max_length = len(string)
        return buf.write(string.strip(), null_terminate=True)

    @native('string', 'writable_string')
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
