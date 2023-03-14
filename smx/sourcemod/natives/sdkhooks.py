from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import Array, SourceModNativesMixin, native


SDKHookCB = Callable


class SDKHookType(IntEnum):
    SDKHook_EndTouch = 0
    SDKHook_FireBulletsPost = 1
    SDKHook_OnTakeDamage = 2
    SDKHook_OnTakeDamagePost = 3
    SDKHook_PreThink = 4
    SDKHook_PostThink = 5
    SDKHook_SetTransmit = 6
    SDKHook_Spawn = 7
    SDKHook_StartTouch = 8
    SDKHook_Think = 9
    SDKHook_Touch = 10
    SDKHook_TraceAttack = 11
    SDKHook_TraceAttackPost = 12
    SDKHook_WeaponCanSwitchTo = 13
    SDKHook_WeaponCanUse = 14
    SDKHook_WeaponDrop = 15
    SDKHook_WeaponEquip = 16
    SDKHook_WeaponSwitch = 17
    SDKHook_ShouldCollide = 18
    SDKHook_PreThinkPost = 19
    SDKHook_PostThinkPost = 20
    SDKHook_ThinkPost = 21
    SDKHook_EndTouchPost = 22
    SDKHook_GroundEntChangedPost = 23
    SDKHook_SpawnPost = 24
    SDKHook_StartTouchPost = 25
    SDKHook_TouchPost = 26
    SDKHook_VPhysicsUpdate = 27
    SDKHook_VPhysicsUpdatePost = 28
    SDKHook_WeaponCanSwitchToPost = 29
    SDKHook_WeaponCanUsePost = 30
    SDKHook_WeaponDropPost = 31
    SDKHook_WeaponEquipPost = 32
    SDKHook_WeaponSwitchPost = 33
    SDKHook_Use = 34
    SDKHook_UsePost = 35
    SDKHook_Reload = 36
    SDKHook_ReloadPost = 37
    SDKHook_GetMaxHealth = 38
    SDKHook_Blocked = 39
    SDKHook_BlockedPost = 40
    SDKHook_OnTakeDamageAlive = 41
    SDKHook_OnTakeDamageAlivePost = 42
    SDKHook_CanBeAutobalanced = 43


class UseType(IntEnum):
    Use_Off = 0
    Use_On = 1
    Use_Set = 2
    Use_Toggle = 3


class SdkhooksNatives(SourceModNativesMixin):
    @native
    def SDKHook(self, entity: int, type_: SDKHookType, callback: SDKHookCB) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SDKHookEx(self, entity: int, type_: SDKHookType, callback: SDKHookCB) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SDKUnhook(self, entity: int, type_: SDKHookType, callback: SDKHookCB) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SDKHooks_TakeDamage(self, entity: int, inflictor: int, attacker: int, damage: float, damage_type: int, weapon: int, damage_force: Array[float], damage_position: Array[float], bypass_hooks: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SDKHooks_DropWeapon(self, client: int, weapon: int, vec_target: Array[float], vec_velocity: Array[float], bypass_hooks: bool) -> None:
        raise SourcePawnUnboundNativeError
