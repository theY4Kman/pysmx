from __future__ import annotations

from typing import TYPE_CHECKING

from smx.sourcemod.natives.base import native, SourceModNativesMixin, WritableString

if TYPE_CHECKING:
    from smx.plugin import SourcePawnPlugin


class SourceModIncNatives(SourceModNativesMixin):
    @native('handle', 'writable_string')
    def GetPluginFilename(self, plugin: SourcePawnPlugin | None, buffer: WritableString) -> None:
        if plugin is None:
            plugin = self.runtime.plugin

        buffer.write(plugin.filename)
