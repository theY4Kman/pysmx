from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class TFClassType(IntEnum):
    TFClass_Unknown = 0
    TFClass_Scout = 1
    TFClass_Sniper = 2
    TFClass_Soldier = 3
    TFClass_DemoMan = 4
    TFClass_Medic = 5
    TFClass_Heavy = 6
    TFClass_Pyro = 7
    TFClass_Spy = 8
    TFClass_Engineer = 9


class TFTeam(IntEnum):
    TFTeam_Unassigned = 0
    TFTeam_Spectator = 1
    TFTeam_Red = 2
    TFTeam_Blue = 3


class TFCond(IntEnum):
    TFCond_Slowed = 0
    TFCond_Zoomed = 1
    TFCond_Disguising = 2
    TFCond_Disguised = 3
    TFCond_Cloaked = 4
    TFCond_Ubercharged = 5
    TFCond_TeleportedGlow = 6
    TFCond_Taunting = 7
    TFCond_UberchargeFading = 8
    TFCond_Unknown1 = 9
    TFCond_CloakFlicker = 9
    TFCond_Teleporting = 10
    TFCond_Kritzkrieged = 11
    TFCond_Unknown2 = 12
    TFCond_TmpDamageBonus = 12
    TFCond_DeadRingered = 13
    TFCond_Bonked = 14
    TFCond_Dazed = 15
    TFCond_Buffed = 16
    TFCond_Charging = 17
    TFCond_DemoBuff = 18
    TFCond_CritCola = 19
    TFCond_InHealRadius = 20
    TFCond_Healing = 21
    TFCond_OnFire = 22
    TFCond_Overhealed = 23
    TFCond_Jarated = 24
    TFCond_Bleeding = 25
    TFCond_DefenseBuffed = 26
    TFCond_Milked = 27
    TFCond_MegaHeal = 28
    TFCond_RegenBuffed = 29
    TFCond_MarkedForDeath = 30
    TFCond_NoHealingDamageBuff = 31
    TFCond_SpeedBuffAlly = 32
    TFCond_HalloweenCritCandy = 33
    TFCond_CritCanteen = 34
    TFCond_CritDemoCharge = 35
    TFCond_CritHype = 36
    TFCond_CritOnFirstBlood = 37
    TFCond_CritOnWin = 38
    TFCond_CritOnFlagCapture = 39
    TFCond_CritOnKill = 40
    TFCond_RestrictToMelee = 41
    TFCond_DefenseBuffNoCritBlock = 42
    TFCond_Reprogrammed = 43
    TFCond_CritMmmph = 44
    TFCond_DefenseBuffMmmph = 45
    TFCond_FocusBuff = 46
    TFCond_DisguiseRemoved = 47
    TFCond_MarkedForDeathSilent = 48
    TFCond_DisguisedAsDispenser = 49
    TFCond_Sapped = 50
    TFCond_UberchargedHidden = 51
    TFCond_UberchargedCanteen = 52
    TFCond_HalloweenBombHead = 53
    TFCond_HalloweenThriller = 54
    TFCond_RadiusHealOnDamage = 55
    TFCond_CritOnDamage = 56
    TFCond_UberchargedOnTakeDamage = 57
    TFCond_UberBulletResist = 58
    TFCond_UberBlastResist = 59
    TFCond_UberFireResist = 60
    TFCond_SmallBulletResist = 61
    TFCond_SmallBlastResist = 62
    TFCond_SmallFireResist = 63
    TFCond_Stealthed = 64
    TFCond_MedigunDebuff = 65
    TFCond_StealthedUserBuffFade = 66
    TFCond_BulletImmune = 67
    TFCond_BlastImmune = 68
    TFCond_FireImmune = 69
    TFCond_PreventDeath = 70
    TFCond_MVMBotRadiowave = 71
    TFCond_HalloweenSpeedBoost = 72
    TFCond_HalloweenQuickHeal = 73
    TFCond_HalloweenGiant = 74
    TFCond_HalloweenTiny = 75
    TFCond_HalloweenInHell = 76
    TFCond_HalloweenGhostMode = 77
    TFCond_MiniCritOnKill = 78
    TFCond_DodgeChance = 79
    TFCond_ObscuredSmoke = 79
    TFCond_Parachute = 80
    TFCond_BlastJumping = 81
    TFCond_HalloweenKart = 82
    TFCond_HalloweenKartDash = 83
    TFCond_BalloonHead = 84
    TFCond_MeleeOnly = 85
    TFCond_SwimmingCurse = 86
    TFCond_HalloweenKartNoTurn = 87
    TFCond_FreezeInput = 87
    TFCond_HalloweenKartCage = 88
    TFCond_HasRune = 89
    TFCond_RuneStrength = 90
    TFCond_RuneHaste = 91
    TFCond_RuneRegen = 92
    TFCond_RuneResist = 93
    TFCond_RuneVampire = 94
    TFCond_RuneWarlock = 95
    TFCond_RunePrecision = 96
    TFCond_RuneAgility = 97
    TFCond_GrapplingHook = 98
    TFCond_GrapplingHookSafeFall = 99
    TFCond_GrapplingHookLatched = 100
    TFCond_GrapplingHookBleeding = 101
    TFCond_AfterburnImmune = 102
    TFCond_RuneKnockout = 103
    TFCond_RuneImbalance = 104
    TFCond_CritRuneTemp = 105
    TFCond_PasstimeInterception = 106
    TFCond_SwimmingNoEffects = 107
    TFCond_EyeaductUnderworld = 108
    TFCond_KingRune = 109
    TFCond_PlagueRune = 110
    TFCond_SupernovaRune = 111
    TFCond_Plague = 112
    TFCond_KingAura = 113
    TFCond_SpawnOutline = 114
    TFCond_KnockedIntoAir = 115
    TFCond_CompetitiveWinner = 116
    TFCond_CompetitiveLoser = 117
    TFCond_NoTaunting_DEPRECATED = 118
    TFCond_HealingDebuff = 118
    TFCond_PasstimePenaltyDebuff = 119
    TFCond_GrappledToPlayer = 120
    TFCond_GrappledByPlayer = 121
    TFCond_ParachuteDeployed = 122
    TFCond_Gas = 123
    TFCond_BurningPyro = 124
    TFCond_RocketPack = 125
    TFCond_LostFooting = 126
    TFCond_AirCurrent = 127
    TFCond_HalloweenHellHeal = 128
    TFCond_PowerupModeDominant = 129


class TFHoliday(IntEnum):
    TFHoliday_Invalid = -1


class TFObjectType(IntEnum):
    TFObject_CartDispenser = 0
    TFObject_Dispenser = 0
    TFObject_Teleporter = 1
    TFObject_Sentry = 2
    TFObject_Sapper = 3


class TFObjectMode(IntEnum):
    TFObjectMode_None = 0
    TFObjectMode_Entrance = 0
    TFObjectMode_Exit = 1


class Tf2Natives(SourceModNativesMixin):
    @native
    def TF2_IgnitePlayer(self, client: int, attacker: int, duration: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_RespawnPlayer(self, client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_RegeneratePlayer(self, client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_AddCondition(self, client: int, condition: TFCond, duration: float, inflictor: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_RemoveCondition(self, client: int, condition: TFCond) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_SetPlayerPowerPlay(self, client: int, enabled: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_DisguisePlayer(self, client: int, team: TFTeam, class_type: TFClassType, target: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_RemovePlayerDisguise(self, client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_StunPlayer(self, client: int, duration: float, slowdown: float, stunflags: int, attacker: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_MakeBleed(self, client: int, attacker: int, duration: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_GetResourceEntity(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_GetClass(self, classname: str) -> TFClassType:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_IsHolidayActive(self, holiday: TFHoliday) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_IsPlayerInDuel(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def TF2_RemoveWearable(self, client: int, wearable: int) -> None:
        raise SourcePawnUnboundNativeError
