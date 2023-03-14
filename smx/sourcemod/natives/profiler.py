from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import MethodMap, SourceModNativesMixin, native


class Profiler:
    pass


class ProfilerMethodMap(MethodMap):
    @native
    def Start(self, this: SourceModHandle[Profiler]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Stop(self, this: SourceModHandle[Profiler]) -> None:
        raise SourcePawnUnboundNativeError


class ProfilerNatives(SourceModNativesMixin):
    Profiler = ProfilerMethodMap()

    @native
    def CreateProfiler(self) -> SourceModHandle[Profiler]:
        raise SourcePawnUnboundNativeError

    @native
    def StartProfiling(self, prof: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def StopProfiling(self, prof: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetProfilerTime(self, prof: SourceModHandle) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def EnterProfilingEvent(self, group: str, name: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LeaveProfilingEvent(self) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def IsProfilingActive(self) -> bool:
        raise SourcePawnUnboundNativeError
