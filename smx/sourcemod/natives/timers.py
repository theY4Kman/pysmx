from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import native, Pointer, SourceModNativesMixin

if TYPE_CHECKING:
    from smx.runtime import PluginFunction

logger = logging.getLogger(__name__)


class TimerNatives(SourceModNativesMixin):
    @native
    def CreateTimer(self, interval: float, func: PluginFunction, data: int, flags: int):
        """
        native Handle:CreateTimer(Float:interval, Timer:func, any:data=INVALID_HANDLE, flags=0)

        Creates a basic timer.  Calling CloseHandle() on a timer will end the timer.

        @param interval    Interval from the current game time to execute the given function.
        @param func        Function to execute once the given interval has elapsed.
        @param data        Handle or value to pass through to the timer callback function.
        @param flags       Flags to set (such as repeatability or auto-Handle closing).
        @return            Handle to the timer object.  You do not need to call CloseHandle().
                               If the timer could not be created, INVALID_HANDLE will be returned.
        """
        logger.info('Interval: %f, func: %d, data: %d, flags: %d' % (interval, func, data, flags))
        return self.sys.timers.create_timer(interval, func, data, flags)

    @native
    def KillTimer(self, timer: SourceModHandle, auto_close: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TriggerTimer(self, timer: SourceModHandle, reset: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetTickedTime(self) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetMapTimeLeft(self, timeleft: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetMapTimeLimit(self, time: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ExtendMapTimeLimit(self, time: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetTickInterval(self) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def IsServerProcessing(self) -> bool:
        raise SourcePawnUnboundNativeError
