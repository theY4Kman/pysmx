from __future__ import annotations

from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import (
    Array,
    Pointer,
    SourceModNativesMixin,
    native,
)


MultiTargetFilter = Callable


class CommandfiltersNatives(SourceModNativesMixin):
    @native
    def ProcessTargetString(self, pattern: str, admin: int, targets: Array[int], max_targets: int, filter_flags: int, target_name: str, tn_maxlength: int, tn_is_ml: Pointer[bool]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def AddMultiTargetFilter(self, pattern: str, filter_: MultiTargetFilter, phrase: str, phrase_is_ml: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveMultiTargetFilter(self, pattern: str, filter_: MultiTargetFilter) -> None:
        raise SourcePawnUnboundNativeError
