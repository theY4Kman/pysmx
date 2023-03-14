from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class CSRoundEndReason(IntEnum):
    CSRoundEnd_TargetBombed = 0
    CSRoundEnd_VIPEscaped = 1
    CSRoundEnd_VIPKilled = 2
    CSRoundEnd_TerroristsEscaped = 3
    CSRoundEnd_CTStoppedEscape = 4
    CSRoundEnd_TerroristsStopped = 5
    CSRoundEnd_BombDefused = 6
    CSRoundEnd_CTWin = 7
    CSRoundEnd_TerroristWin = 8
    CSRoundEnd_Draw = 9
    CSRoundEnd_HostagesRescued = 10
    CSRoundEnd_TargetSaved = 11
    CSRoundEnd_HostagesNotRescued = 12
    CSRoundEnd_TerroristsNotEscaped = 13
    CSRoundEnd_VIPNotEscaped = 14
    CSRoundEnd_GameStart = 15
    CSRoundEnd_TerroristsSurrender = 16
    CSRoundEnd_CTSurrender = 17
    CSRoundEnd_TerroristsPlanted = 18
    CSRoundEnd_CTsReachedHostage = 19


class CSWeaponID(IntEnum):
    CSWeapon_NONE = 0
    CSWeapon_P228 = 1
    CSWeapon_GLOCK = 2
    CSWeapon_SCOUT = 3
    CSWeapon_HEGRENADE = 4
    CSWeapon_XM1014 = 5
    CSWeapon_C4 = 6
    CSWeapon_MAC10 = 7
    CSWeapon_AUG = 8
    CSWeapon_SMOKEGRENADE = 9
    CSWeapon_ELITE = 10
    CSWeapon_FIVESEVEN = 11
    CSWeapon_UMP45 = 12
    CSWeapon_SG550 = 13
    CSWeapon_GALIL = 14
    CSWeapon_FAMAS = 15
    CSWeapon_USP = 16
    CSWeapon_AWP = 17
    CSWeapon_MP5NAVY = 18
    CSWeapon_M249 = 19
    CSWeapon_M3 = 20
    CSWeapon_M4A1 = 21
    CSWeapon_TMP = 22
    CSWeapon_G3SG1 = 23
    CSWeapon_FLASHBANG = 24
    CSWeapon_DEAGLE = 25
    CSWeapon_SG552 = 26
    CSWeapon_AK47 = 27
    CSWeapon_KNIFE = 28
    CSWeapon_P90 = 29
    CSWeapon_SHIELD = 30
    CSWeapon_KEVLAR = 31
    CSWeapon_ASSAULTSUIT = 32
    CSWeapon_NIGHTVISION = 33
    CSWeapon_GALILAR = 34
    CSWeapon_BIZON = 35
    CSWeapon_MAG7 = 36
    CSWeapon_NEGEV = 37
    CSWeapon_SAWEDOFF = 38
    CSWeapon_TEC9 = 39
    CSWeapon_TASER = 40
    CSWeapon_HKP2000 = 41
    CSWeapon_MP7 = 42
    CSWeapon_MP9 = 43
    CSWeapon_NOVA = 44
    CSWeapon_P250 = 45
    CSWeapon_SCAR17 = 46
    CSWeapon_SCAR20 = 47
    CSWeapon_SG556 = 48
    CSWeapon_SSG08 = 49
    CSWeapon_KNIFE_GG = 50
    CSWeapon_MOLOTOV = 51
    CSWeapon_DECOY = 52
    CSWeapon_INCGRENADE = 53
    CSWeapon_DEFUSER = 54
    CSWeapon_HEAVYASSAULTSUIT = 55
    CSWeapon_CUTTERS = 56
    CSWeapon_HEALTHSHOT = 57
    CSWeapon_KNIFE_T = 59
    CSWeapon_M4A1_SILENCER = 60
    CSWeapon_USP_SILENCER = 61
    CSWeapon_CZ75A = 63
    CSWeapon_REVOLVER = 64
    CSWeapon_TAGGRENADE = 68
    CSWeapon_FISTS = 69
    CSWeapon_BREACHCHARGE = 70
    CSWeapon_TABLET = 72
    CSWeapon_MELEE = 74
    CSWeapon_AXE = 75
    CSWeapon_HAMMER = 76
    CSWeapon_SPANNER = 78
    CSWeapon_KNIFE_GHOST = 80
    CSWeapon_FIREBOMB = 81
    CSWeapon_DIVERSION = 82
    CSWeapon_FRAGGRENADE = 83
    CSWeapon_SNOWBALL = 84
    CSWeapon_BUMPMINE = 85
    CSWeapon_MAX_WEAPONS_NO_KNIFES = 86
    CSWeapon_BAYONET = 500
    CSWeapon_KNIFE_CLASSIC = 503
    CSWeapon_KNIFE_FLIP = 505
    CSWeapon_KNIFE_GUT = 506
    CSWeapon_KNIFE_KARAMBIT = 507
    CSWeapon_KNIFE_M9_BAYONET = 508
    CSWeapon_KNIFE_TATICAL = 509
    CSWeapon_KNIFE_FALCHION = 512
    CSWeapon_KNIFE_SURVIVAL_BOWIE = 514
    CSWeapon_KNIFE_BUTTERFLY = 515
    CSWeapon_KNIFE_PUSH = 516
    CSWeapon_KNIFE_CORD = 517
    CSWeapon_KNIFE_CANIS = 518
    CSWeapon_KNIFE_URSUS = 519
    CSWeapon_KNIFE_GYPSY_JACKKNIFE = 520
    CSWeapon_KNIFE_OUTDOOR = 521
    CSWeapon_KNIFE_STILETTO = 522
    CSWeapon_KNIFE_WIDOWMAKER = 523
    CSWeapon_KNIFE_SKELETON = 525
    CSWeapon_MAX_WEAPONS = 526


class CstrikeNatives(SourceModNativesMixin):
    @native
    def CS_RespawnPlayer(self, client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_SwitchTeam(self, client: int, team: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_DropWeapon(self, client: int, weapon_index: int, toss: bool, blockhook: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_TerminateRound(self, delay: float, reason: CSRoundEndReason, blockhook: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_GetTranslatedWeaponAlias(self, alias: str, weapon: str, size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_GetWeaponPrice(self, client: int, id: CSWeaponID, defaultprice: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CS_GetClientClanTag(self, client: int, buffer: str, size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CS_SetClientClanTag(self, client: int, tag: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_GetTeamScore(self, team: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CS_SetTeamScore(self, team: int, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_GetMVPCount(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CS_SetMVPCount(self, client: int, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_GetClientContributionScore(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CS_SetClientContributionScore(self, client: int, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_GetClientAssists(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CS_SetClientAssists(self, client: int, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_AliasToWeaponID(self, alias: str) -> CSWeaponID:
        raise SourcePawnUnboundNativeError

    @native
    def CS_WeaponIDToAlias(self, weapon_id: CSWeaponID, destination: str, len_: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CS_IsValidWeaponID(self, id: CSWeaponID) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CS_UpdateClientModel(self, client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CS_ItemDefIndexToID(self, i_def_index: int) -> CSWeaponID:
        raise SourcePawnUnboundNativeError

    @native
    def CS_WeaponIDToItemDefIndex(self, id: CSWeaponID) -> int:
        raise SourcePawnUnboundNativeError
