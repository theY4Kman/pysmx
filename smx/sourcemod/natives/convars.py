from __future__ import annotations

from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import native, SourceModNativesMixin, WritableString


class ConVar:
    def __init__(
        self,
        name: str,
        default_value: str,
        description: str = '',
        flags: int = 0,
        min: float | None = None,
        max: float | None = None
    ):
        self.name = name
        self.value = self.default_value = default_value
        self.description = description
        self.flags = flags
        self.min = min
        self.max = max

    def __str__(self):
        return self.value

    def __repr__(self):
        return '<ConVar %s %r>' % (self.name, self.value)


class ConVarNatives(SourceModNativesMixin):
    @native
    def CreateConVar(
        self,
        name: str,
        default_value: str,
        description: str,
        flags: int,
        has_min: bool,
        min: float,
        has_max: bool,
        max: float
    ):
        cvar = ConVar(
            name,
            default_value,
            description,
            flags,
            min if has_min else None,
            max if has_max else None,
        )
        self.sys.convars[name] = cvar
        return self.sys.handles.new_handle(cvar)

    @native
    def GetConVarInt(self, handle: SourceModHandle[ConVar]) -> int:
        return int(handle.obj.value)

    @native
    def GetConVarFloat(self, handle: SourceModHandle[ConVar]) -> float:
        return float(handle.obj.value)

    @native
    def GetConVarString(self, handle: SourceModHandle[ConVar], buf: WritableString):
        return buf.write(handle.obj.value, null_terminate=True)
