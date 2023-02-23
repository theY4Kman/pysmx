from __future__ import annotations

from smx.sourcemod.natives.base import native, SourceModNativesMixin, sp_ftoc, WritableString


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
    @native('string', 'string', 'string', 'cell', 'bool', 'float', 'bool', 'float')
    def CreateConVar(self, name, default_value, description, flags, has_min, min, has_max, max):
        cvar = ConVar(name, default_value, description, flags, min if has_min else None, max if has_max else None)
        self.sys.convars[name] = cvar
        return self.sys.handles.new_handle(cvar)

    @native('handle')
    def GetConVarInt(self, cvar: ConVar) -> int:
        return int(cvar.value)

    @native('handle')
    def GetConVarFloat(self, cvar: ConVar) -> float:
        return float(cvar.value)

    @native('handle', 'writable_string')
    def GetConVarString(self, cvar: ConVar, buf: WritableString):
        return buf.write(cvar.value, null_terminate=True)
