from __future__ import annotations

from typing import TYPE_CHECKING

from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import native, SourceModNativesMixin, WritableString

if TYPE_CHECKING:
    from smx.plugin import SourcePawnPlugin


class SourceModIncNatives(SourceModNativesMixin):
    @native
    def GetPluginFilename(self, handle: SourceModHandle[SourcePawnPlugin] | None, buffer: WritableString) -> None:
        if handle is None:
            plugin = self.runtime.plugin
        else:
            plugin = handle.obj

        buffer.write(plugin.filename)
