from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import Pointer, SourceModNativesMixin, native


class NextmapNatives(SourceModNativesMixin):
    @native
    def SetNextMap(self, map_: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetNextMap(self, map_: str, maxlen: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ForceChangeLevel(self, map_: str, reason: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetMapHistorySize(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetMapHistory(self, item: int, map_: str, map_len: int, reason: str, reason_len: int, start_time: Pointer[int]) -> None:
        raise SourcePawnUnboundNativeError
