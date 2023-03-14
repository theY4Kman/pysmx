from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import Array, SourceModNativesMixin, native


class Action(IntEnum):
    Plugin_Continue = 0
    Plugin_Changed = 1
    Plugin_Handled = 3
    Plugin_Stop = 4


class Identity(IntEnum):
    Identity_Core = 0
    Identity_Extension = 1
    Identity_Plugin = 2


class PluginStatus(IntEnum):
    Plugin_Running = 0
    Plugin_Paused = 1
    Plugin_Error = 2
    Plugin_Loaded = 3
    Plugin_Failed = 4
    Plugin_Created = 5
    Plugin_Uncompiled = 6
    Plugin_BadLoad = 7
    Plugin_Evicted = 8


class PluginInfo(IntEnum):
    PlInfo_Name = 0
    PlInfo_Author = 1
    PlInfo_Description = 2
    PlInfo_Version = 3
    PlInfo_URL = 4


class CoreNatives(SourceModNativesMixin):
    @native
    def IsNullVector(self, vec: Array[float]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsNullString(self, str_: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def VerifyCoreVersion(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def MarkNativeAsOptional(self, name: str) -> None:
        raise SourcePawnUnboundNativeError
