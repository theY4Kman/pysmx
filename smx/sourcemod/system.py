from __future__ import annotations

from smx.engine import engine_time
from smx.sourcemod.handles import SourceModHandles
from smx.sourcemod.natives import SourceModNatives
from smx.sourcemod.timers import SourceModTimers

__all__ = ['SourceModSystem']


class SourceModSystem:
    """Emulates all SourcePawn -> SourceMod interactions"""

    def __init__(self, amx):
        """
        @type   amx: smx.vm.SourcePawnAbstractMachine
        @param  amx: The abstract machine owning these natives
        """
        self.amx = amx
        self.plugin = self.amx.plugin
        self.runtime = self.plugin.runtime

        self.natives = SourceModNatives(self)
        self.timers = SourceModTimers(self)
        self.handles = SourceModHandles(self)

        self.tickrate = 66
        self.interval_per_tick = 1.0 / self.tickrate
        self.last_tick = None

        self.convars = {}

    def tick(self):
        self.last_tick = engine_time()
