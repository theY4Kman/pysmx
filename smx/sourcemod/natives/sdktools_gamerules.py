from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import Array, SourceModNativesMixin, native


class RoundState(IntEnum):
    RoundState_Init = 0
    RoundState_Pregame = 1
    RoundState_StartGame = 2
    RoundState_Preround = 3
    RoundState_RoundRunning = 4
    RoundState_TeamWin = 5
    RoundState_Restart = 6
    RoundState_Stalemate = 7
    RoundState_GameOver = 8
    RoundState_Bonus = 9
    RoundState_BetweenRounds = 10


class SdktoolsGamerulesNatives(SourceModNativesMixin):
    @native
    def GameRules_GetProp(self, prop: str, size: int, element: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GameRules_SetProp(self, prop: str, value: int, size: int, element: int, change_state: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GameRules_GetPropFloat(self, prop: str, element: int) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GameRules_SetPropFloat(self, prop: str, value: float, element: int, change_state: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GameRules_GetPropEnt(self, prop: str, element: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GameRules_SetPropEnt(self, prop: str, other: int, element: int, change_state: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GameRules_GetPropVector(self, prop: str, vec: Array[float], element: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GameRules_SetPropVector(self, prop: str, vec: Array[float], element: int, change_state: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GameRules_GetPropString(self, prop: str, buffer: str, maxlen: int, element: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GameRules_SetPropString(self, prop: str, buffer: str, change_state: bool, element: int) -> int:
        raise SourcePawnUnboundNativeError
