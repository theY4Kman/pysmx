from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    SourceModNativesMixin,
    WritableString,
    native,
)
from smx.sourcemod.natives.clients import AuthIdType


class DialogType(IntEnum):
    DialogType_Msg = 0
    DialogType_Menu = 1
    DialogType_Text = 2
    DialogType_Entry = 3
    DialogType_AskConnect = 4


class EngineVersion(IntEnum):
    Engine_Unknown = 0
    Engine_Original = 1
    Engine_SourceSDK2006 = 2
    Engine_SourceSDK2007 = 3
    Engine_Left4Dead = 4
    Engine_DarkMessiah = 5
    Engine_Left4Dead2 = 7
    Engine_AlienSwarm = 8
    Engine_BloodyGoodTime = 9
    Engine_EYE = 10
    Engine_Portal2 = 11
    Engine_CSGO = 12
    Engine_CSS = 13
    Engine_DOTA = 14
    Engine_HL2DM = 15
    Engine_DODS = 16
    Engine_TF2 = 17
    Engine_NuclearDawn = 18
    Engine_SDK2013 = 19
    Engine_Blade = 20
    Engine_Insurgency = 21
    Engine_Contagion = 22
    Engine_BlackMesa = 23
    Engine_DOI = 24


class FindMapResult(IntEnum):
    FindMap_Found = 0
    FindMap_NotFound = 1
    FindMap_FuzzyMatch = 2
    FindMap_NonCanonical = 3
    FindMap_PossiblyAvailable = 4


class ClientRangeType(IntEnum):
    RangeType_Visibility = 0
    RangeType_Audibility = 1


class HalflifeNatives(SourceModNativesMixin):
    @native
    def LogToGame(self, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetRandomSeed(self, seed: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetRandomFloat(self, f_min: float, f_max: float) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetRandomInt(self, nmin: int, nmax: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsMapValid(self, map_: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FindMap(self, map_: str, foundmap: str, maxlen: int) -> FindMapResult:
        raise SourcePawnUnboundNativeError

    @native
    def GetMapDisplayName(self, map_: str, display_name: str, maxlen: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsDedicatedServer(self) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetEngineTime(self) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetGameTime(self) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetGameTickCount(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetGameFrameTime(self) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GetGameDescription(self, buffer: WritableString, original: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetGameFolderName(self, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetCurrentMap(self, buffer: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PrecacheModel(self, model: str, preload: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PrecacheSentenceFile(self, file: str, preload: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PrecacheDecal(self, decal: str, preload: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def PrecacheGeneric(self, generic: str, preload: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsModelPrecached(self, model: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsDecalPrecached(self, decal: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsGenericPrecached(self, generic: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def PrecacheSound(self, sound: str, preload: bool) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsSoundPrecached(self, sound: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CreateDialog(self, client: int, kv: SourceModHandle, type_: DialogType) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GuessSDKVersion(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetEngineVersion(self) -> EngineVersion:
        raise SourcePawnUnboundNativeError

    @native
    def PrintToChat(self, client: int, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PrintCenterText(self, client: int, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def PrintHintText(self, client: int, format_: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ShowVGUIPanel(self, client: int, name: str, kv: SourceModHandle, show: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CreateHudSynchronizer(self) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def SetHudTextParams(self, x: float, y: float, hold_time: float, r: int, g: int, b: int, a: int, effect: int, fx_time: float, fade_in: float, fade_out: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetHudTextParamsEx(self, x: float, y: float, hold_time: float, color1: Array[int], color2: Array[int], effect: int, fx_time: float, fade_in: float, fade_out: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ShowSyncHudText(self, client: int, sync: SourceModHandle, message: str, *args) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def ClearSyncHud(self, client: int, sync: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ShowHudText(self, client: int, channel: int, message: str, *args) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def EntIndexToEntRef(self, entity: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def EntRefToEntIndex(self, ref: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def MakeCompatEntRef(self, ref: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientsInRange(self, origin: Array[float], range_type: ClientRangeType, clients: Array[int], size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetServerAuthId(self, auth_type: AuthIdType, auth: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetServerSteamAccountId(self) -> int:
        raise SourcePawnUnboundNativeError
