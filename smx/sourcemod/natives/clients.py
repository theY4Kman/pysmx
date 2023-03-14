from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.admin import AdminId
from smx.sourcemod.natives.base import Array, SourceModNativesMixin, native


class NetFlow(IntEnum):
    NetFlow_Outgoing = 0
    NetFlow_Incoming = 1
    NetFlow_Both = 2


class AuthIdType(IntEnum):
    AuthId_Engine = 0
    AuthId_Steam2 = 1
    AuthId_Steam3 = 2
    AuthId_SteamID64 = 3


class ClientsNatives(SourceModNativesMixin):
    @native
    def GetMaxClients(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetMaxHumanPlayers(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientCount(self, in_game_only: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientName(self, client: int, name: str, maxlen: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientIP(self, client: int, ip: str, maxlen: int, remport: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientAuthString(self, client: int, auth: str, maxlen: int, validate: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientAuthId(self, client: int, auth_type: AuthIdType, auth: str, maxlen: int, validate: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetSteamAccountID(self, client: int, validate: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientUserId(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsClientConnected(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsClientInGame(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsClientInKickQueue(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsClientAuthorized(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsFakeClient(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsClientSourceTV(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsClientReplay(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsClientObserver(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsPlayerAlive(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientInfo(self, client: int, key: str, value: str, maxlen: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientTeam(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetUserAdmin(self, client: int, id: AdminId, temp: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetUserAdmin(self, client: int) -> AdminId:
        raise SourcePawnUnboundNativeError

    @native
    def AddUserFlags(self, client: int, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveUserFlags(self, client: int, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetUserFlagBits(self, client: int, flags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetUserFlagBits(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CanUserTarget(self, client: int, target: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RunAdminCacheChecks(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def NotifyPostAdminCheck(self, client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CreateFakeClient(self, name: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetFakeClientConVar(self, client: int, cvar: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientHealth(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientModel(self, client: int, model: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientWeapon(self, client: int, weapon: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientMaxs(self, client: int, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientMins(self, client: int, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientAbsAngles(self, client: int, ang: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientAbsOrigin(self, client: int, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientArmor(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientDeaths(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientFrags(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientDataRate(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsClientTimingOut(self, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientTime(self, client: int) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientLatency(self, client: int, flow: NetFlow) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientAvgLatency(self, client: int, flow: NetFlow) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientAvgLoss(self, client: int, flow: NetFlow) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientAvgChoke(self, client: int, flow: NetFlow) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientAvgData(self, client: int, flow: NetFlow) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientAvgPackets(self, client: int, flow: NetFlow) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientOfUserId(self, userid: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def KickClient(self, client: int, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def KickClientEx(self, client: int, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ChangeClientTeam(self, client: int, team: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientSerial(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientFromSerial(self, serial: int) -> int:
        raise SourcePawnUnboundNativeError
