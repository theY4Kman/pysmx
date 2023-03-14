from __future__ import annotations

from enum import IntEnum


class TFResourceType(IntEnum):
    TFResource_Ping = 0
    TFResource_Score = 1
    TFResource_Deaths = 2
    TFResource_TotalScore = 3
    TFResource_Captures = 4
    TFResource_Defenses = 5
    TFResource_Dominations = 6
    TFResource_Revenge = 7
    TFResource_BuildingsDestroyed = 8
    TFResource_Headshots = 9
    TFResource_Backstabs = 10
    TFResource_HealPoints = 11
    TFResource_Invulns = 12
    TFResource_Teleports = 13
    TFResource_ResupplyPoints = 14
    TFResource_KillAssists = 15
    TFResource_MaxHealth = 16
    TFResource_PlayerClass = 17
