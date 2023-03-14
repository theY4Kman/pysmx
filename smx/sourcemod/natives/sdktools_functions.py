from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import (
    Array,
    Pointer,
    SourceModNativesMixin,
    WritableString,
    native,
)


class SdktoolsFunctionsNatives(SourceModNativesMixin):
    @native
    def RemovePlayerItem(self, client: int, item: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GivePlayerItem(self, client: int, item: str, i_sub_type: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetPlayerWeaponSlot(self, client: int, slot: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IgniteEntity(self, entity: int, time: float, npc: bool, size: float, level: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ExtinguishEntity(self, entity: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TeleportEntity(self, entity: int, origin: Array[float], angles: Array[float], velocity: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ForcePlayerSuicide(self, client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SlapPlayer(self, client: int, health: int, sound: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FindEntityByClassname(self, start_ent: int, classname: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientEyeAngles(self, client: int, ang: Array[float]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CreateEntityByName(self, classname: str, force_edict_index: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def DispatchSpawn(self, entity: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DispatchKeyValue(self, entity: int, key_name: str, value: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DispatchKeyValueFloat(self, entity: int, key_name: str, value: float) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DispatchKeyValueVector(self, entity: int, key_name: str, vec: Array[float]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientAimTarget(self, client: int, only_clients: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetTeamCount(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetTeamName(self, index: int, name: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetTeamScore(self, index: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetTeamScore(self, index: int, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetTeamClientCount(self, index: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetTeamEntity(self, team_index: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntityModel(self, entity: int, model: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetPlayerDecalFile(self, client: int, hex: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetPlayerJingleFile(self, client: int, hex: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetServerNetStats(self, in_amount: Pointer[float], out_amout: Pointer[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def EquipPlayerWeapon(self, client: int, weapon: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ActivateEntity(self, entity: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetClientInfo(self, client: int, key: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetClientName(self, client: int, name: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GivePlayerAmmo(self, client: int, amount: int, ammotype: int, suppress_sound: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntityCollisionGroup(self, entity: int, collision_group: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def EntityCollisionRulesChanged(self, entity: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetEntityOwner(self, entity: int, owner: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LookupEntityAttachment(self, entity: int, name: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetEntityAttachment(self, entity: int, attachment: int, origin: Array[float], angles: Array[float]) -> bool:
        raise SourcePawnUnboundNativeError
