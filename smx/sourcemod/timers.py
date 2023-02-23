from __future__ import annotations

import time

from smx.engine import engine_time


class SourceModTimers:
    """Handles SourceMod timers"""

    TIMER_REPEAT = (1 << 0)             # Timer will repeat until it returns Plugin_Stop
    TIMER_FLAG_NO_MAPCHANGE = (1 << 1)  # Timer will not carry over mapchanges
    TIMER_HNDL_CLOSE = (1 << 9)         # Deprecated define, replaced by below
    TIMER_DATA_HNDL_CLOSE = (1 << 9)    # Timer will automatically call CloseHandle() on its data when finished

    def __init__(self, sys):
        """
        @type   sys: smx.system.SourceModSystem
        @param  sys: The SourceMod system emulator owning these natives
        """
        self.sys = sys
        self._timers = []

    def create_timer(self, interval, callback, data, flags):
        handle_id = self.sys.handles.new_handle(None)  # TODO: uhh, actual timer objects

        def timer_callback():
            # XXX: call this enter_frame instead?
            # self.sys.runtime.amx._dummy_frame()
            return self.sys.runtime.call_function(callback, handle_id, data)

        # TODO: repeating timers
        self._timers.append((engine_time() + interval, timer_callback))
        return handle_id

    def has_timers(self):
        return bool(self._timers)

    def poll_for_timers(self):
        while self.has_timers():
            time.sleep(self.sys.interval_per_tick)
            self.sys.tick()

            to_call = [f for call_after, f in self._timers
                       if self.sys.last_tick > call_after]
            self._timers = [(call_after, f) for call_after, f in self._timers
                            if self.sys.last_tick <= call_after]

            for callback in to_call:
                callback()
