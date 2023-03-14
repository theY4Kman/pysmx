from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import (
    SourceModNativesMixin,
    WritableString,
    native,
)


class SdktoolsStringtablesNatives(SourceModNativesMixin):
    @native
    def FindStringTable(self, name: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetNumStringTables(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetStringTableNumStrings(self, tableidx: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetStringTableMaxStrings(self, tableidx: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetStringTableName(self, tableidx: int, name: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FindStringIndex(self, tableidx: int, str_: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ReadStringTable(self, tableidx: int, stringidx: int, str: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetStringTableDataLength(self, tableidx: int, stringidx: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetStringTableData(self, tableidx: int, stringidx: int, userdata: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetStringTableData(self, tableidx: int, stringidx: int, userdata: str, length: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddToStringTable(self, tableidx: int, str_: str, userdata: str, length: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LockStringTables(self, lock: bool) -> bool:
        raise SourcePawnUnboundNativeError
