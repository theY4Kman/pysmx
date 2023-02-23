from __future__ import annotations

import logging

from smx.sourcemod.natives.base import native, SourceModNativesMixin

logger = logging.getLogger(__name__)


class TimerNatives(SourceModNativesMixin):
    @native('float', 'cell', 'cell', 'cell')
    def CreateTimer(self, interval, func, data, flags):
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
