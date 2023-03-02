from __future__ import annotations

from typing import Type, TYPE_CHECKING

from smx.engine import engine_time
from smx.sourcemod.handles import SourceModHandles
from smx.sourcemod.natives import SourceModNatives
from smx.sourcemod.timers import SourceModTimers

if TYPE_CHECKING:
    from smx.vm import SourcePawnAbstractMachine
    from smx.runtime import SourcePawnPluginRuntime
    from smx.plugin import SourcePawnPlugin

__all__ = ['SourceModSystem']


class SourceModSystem:
    """Emulates all SourcePawn -> SourceMod interactions"""

    def __init__(
        self,
        amx: SourcePawnAbstractMachine,
        *,
        natives_cls: Type[SourceModNatives] = SourceModNatives,
    ):
        """
        :param amx:
            The abstract machine calling out to SourceMod
        """
        self.amx: SourcePawnAbstractMachine = amx
        self.plugin: SourcePawnPlugin = self.amx.plugin
        self.runtime: SourcePawnPluginRuntime = self.plugin.runtime

        self.natives: SourceModNatives = natives_cls(self)
        self.timers = SourceModTimers(self)
        self.handles = SourceModHandles(self)

        self.tickrate: int = 66
        self.interval_per_tick: float = 1.0 / self.tickrate
        self.last_tick: int | None = None

        self.convars = {}

    def tick(self):
        self.last_tick = engine_time()
