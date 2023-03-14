from __future__ import annotations

from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


GameLogHook = Callable


class LoggingNatives(SourceModNativesMixin):
    @native
    def LogMessage(self, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LogToFile(self, file: str, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LogToFileEx(self, file: str, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LogAction(self, client: int, target: int, message: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LogError(self, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddGameLogHook(self, hook: GameLogHook) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveGameLogHook(self, hook: GameLogHook) -> None:
        raise SourcePawnUnboundNativeError
