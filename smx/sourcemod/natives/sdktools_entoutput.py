from __future__ import annotations

from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


EntityOutput = Callable


class SdktoolsEntoutputNatives(SourceModNativesMixin):
    @native
    def HookEntityOutput(self, classname: str, output: str, callback: EntityOutput) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def UnhookEntityOutput(self, classname: str, output: str, callback: EntityOutput) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def HookSingleEntityOutput(self, entity: int, output: str, callback: EntityOutput, once: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def UnhookSingleEntityOutput(self, entity: int, output: str, callback: EntityOutput) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FireEntityOutput(self, caller: int, output: str, activator: int, delay: float) -> None:
        raise SourcePawnUnboundNativeError
