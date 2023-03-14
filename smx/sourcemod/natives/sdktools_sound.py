from __future__ import annotations

from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import (
    Array,
    Pointer,
    SourceModNativesMixin,
    WritableString,
    native,
)


NormalSHook = Callable
AmbientSHook = Callable


class SdktoolsSoundNatives(SourceModNativesMixin):
    @native
    def PrefetchSound(self, name: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetSoundDuration(self, name: str) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def EmitAmbientSound(self, name: str, pos: Array[float], entity: int, level: int, flags: int, vol: float, pitch: int, delay: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FadeClientVolume(self, client: int, percent: float, outtime: float, holdtime: float, intime: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def StopSound(self, entity: int, channel: int, name: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def EmitSound(self, clients: Array[int], num_clients: int, sample: str, entity: int, channel: int, level: int, flags: int, volume: float, pitch: int, speakerentity: int, origin: Array[float], dir_: Array[float], update_pos: bool, soundtime: float, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def EmitSoundEntry(self, clients: Array[int], num_clients: int, sound_entry: str, sample: str, entity: int, channel: int, level: int, seed: int, flags: int, volume: float, pitch: int, speakerentity: int, origin: Array[float], dir_: Array[float], update_pos: bool, soundtime: float, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def EmitSentence(self, clients: Array[int], num_clients: int, sentence: int, entity: int, channel: int, level: int, flags: int, volume: float, pitch: int, speakerentity: int, origin: Array[float], dir_: Array[float], update_pos: bool, soundtime: float, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetDistGainFromSoundLevel(self, soundlevel: int, distance: float) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def AddAmbientSoundHook(self, hook: AmbientSHook) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddNormalSoundHook(self, hook: NormalSHook) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveAmbientSoundHook(self, hook: AmbientSHook) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveNormalSoundHook(self, hook: NormalSHook) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetGameSoundParams(self, game_sound: str, channel: Pointer[int], sound_level: Pointer[int], volume: Pointer[float], pitch: Pointer[int], sample: WritableString, entity: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def PrecacheScriptSound(self, soundname: str) -> bool:
        raise SourcePawnUnboundNativeError
