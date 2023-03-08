from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from smx.compat import StrEnum
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import native, SourceModNativesMixin, WritableString

if TYPE_CHECKING:
    from smx.plugin import SourcePawnPlugin


class PluginStatus(enum.IntEnum):
    Running = 0     # Plugin is running
    Paused = 1      # Plugin is loaded but paused
    Error = 2       # Plugin is loaded but errored/locked
    Loaded = 3      # Plugin has passed loading and can be finalized
    Failed = 4      # Plugin has a fatal failure
    Created = 5     # Plugin is created but not initialized
    Uncompiled = 6  # Plugin is not yet compiled by the JIT
    BadLoad = 7     # Plugin failed to load
    Evicted = 8     # Plugin was unloaded due to an error


class PlInfo(enum.IntEnum):
    Name = 0
    Author = 1
    Description = 2
    Version = 3
    URL = 4


class SourceModIncNatives(SourceModNativesMixin):
    @native
    def GetMyHandle(self) -> SourceModHandle[SourcePawnPlugin]:
        return self.sys.handles.new_handle(self.runtime.plugin)

    # TODO(zk)
    # @native
    # def GetPluginStatus(self, handle: SourceModHandle[SourcePawnPlugin] | None) -> PluginStatus:
    #     if handle is None:
    #         plugin = self.runtime.plugin
    #     else:
    #         plugin = handle.obj
    #
    #     return plugin.status

    @native
    def GetPluginFilename(self, handle: SourceModHandle[SourcePawnPlugin] | None, buffer: WritableString) -> None:
        if handle is None:
            plugin = self.runtime.plugin
        else:
            plugin = handle.obj

        buffer.write(plugin.filename)

    # TODO(zk)
    # @native
    # def IsPluginDebugging(self, handle: SourceModHandle[SourcePawnPlugin] | None) -> bool:
    #     if handle is None:
    #         plugin = self.runtime.plugin
    #     else:
    #         plugin = handle.obj
    #
    #     return plugin.is_debugging

    @native
    def GetPluginInfo(
        self,
        handle: SourceModHandle[SourcePawnPlugin] | None,
        info: PlInfo,
        buf: WritableString
    ) -> bool:
        if handle is None:
            plugin = self.runtime.plugin
        else:
            plugin = handle.obj

        value = plugin.myinfo.get(info.name.lower())
        if value is None:
            return False

        buf.write(value)
        return True
