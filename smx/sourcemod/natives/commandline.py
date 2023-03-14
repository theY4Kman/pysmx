from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class CommandlineNatives(SourceModNativesMixin):
    @native
    def GetCommandLine(self, command_line: str, maxlen: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetCommandLineParam(self, param: str, value: str, maxlen: int, def_value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetCommandLineParamInt(self, param: str, def_value: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetCommandLineParamFloat(self, param: str, def_value: float) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def FindCommandLineParam(self, param: str) -> bool:
        raise SourcePawnUnboundNativeError
