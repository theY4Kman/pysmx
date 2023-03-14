from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class MoveType(IntEnum):
    MOVETYPE_NONE = 0
    MOVETYPE_ISOMETRIC = 1
    MOVETYPE_WALK = 2
    MOVETYPE_STEP = 3
    MOVETYPE_FLY = 4
    MOVETYPE_FLYGRAVITY = 5
    MOVETYPE_VPHYSICS = 6
    MOVETYPE_PUSH = 7
    MOVETYPE_NOCLIP = 8
    MOVETYPE_LADDER = 9
    MOVETYPE_OBSERVER = 10
    MOVETYPE_CUSTOM = 11


class RenderMode(IntEnum):
    RENDER_NORMAL = 0
    RENDER_TRANSCOLOR = 1
    RENDER_TRANSTEXTURE = 2
    RENDER_GLOW = 3
    RENDER_TRANSALPHA = 4
    RENDER_TRANSADD = 5
    RENDER_ENVIRONMENTAL = 6
    RENDER_TRANSADDFRAMEBLEND = 7
    RENDER_TRANSALPHAADD = 8
    RENDER_WORLDGLOW = 9
    RENDER_NONE = 10


class RenderFx(IntEnum):
    RENDERFX_NONE = 0
    RENDERFX_PULSE_SLOW = 1
    RENDERFX_PULSE_FAST = 2
    RENDERFX_PULSE_SLOW_WIDE = 3
    RENDERFX_PULSE_FAST_WIDE = 4
    RENDERFX_FADE_SLOW = 5
    RENDERFX_FADE_FAST = 6
    RENDERFX_SOLID_SLOW = 7
    RENDERFX_SOLID_FAST = 8
    RENDERFX_STROBE_SLOW = 9
    RENDERFX_STROBE_FAST = 10
    RENDERFX_STROBE_FASTER = 11
    RENDERFX_FLICKER_SLOW = 12
    RENDERFX_FLICKER_FAST = 13
    RENDERFX_NO_DISSIPATION = 14
    RENDERFX_DISTORT = 15
    RENDERFX_HOLOGRAM = 16
    RENDERFX_EXPLODE = 17
    RENDERFX_GLOWSHELL = 18
    RENDERFX_CLAMP_MIN_SCALE = 19
    RENDERFX_ENV_RAIN = 20
    RENDERFX_ENV_SNOW = 21
    RENDERFX_SPOTLIGHT = 22
    RENDERFX_RAGDOLL = 23
    RENDERFX_PULSE_FAST_WIDER = 24
    RENDERFX_MAX = 25


class EntityPropStocksNatives(SourceModNativesMixin):
    @native
    def GetEntityFlags(self, entity: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntityFlags(self, entity: int, flags: int) -> None:
        raise SourcePawnUnboundNativeError
