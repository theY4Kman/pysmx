from __future__ import annotations

from smx.sourcemod.natives.base import native, SourceModNativesMixin
from smx.sourcemod.printf import atcprintf


class ConsoleNatives(SourceModNativesMixin):
    @native('string', '...')
    def PrintToServer(self, fmt, *args):
        out = atcprintf(self.amx, fmt, args)
        self.runtime.printf(out)
