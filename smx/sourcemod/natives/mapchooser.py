from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.adt_array import ArrayList
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class NominateResult(IntEnum):
    Nominate_Added = 0
    Nominate_Replaced = 1
    Nominate_AlreadyInVote = 2
    Nominate_InvalidMap = 3
    Nominate_VoteFull = 4


class MapChange(IntEnum):
    MapChange_Instant = 0
    MapChange_RoundEnd = 1
    MapChange_MapEnd = 2


class MapchooserNatives(SourceModNativesMixin):
    @native
    def NominateMap(self, map_: str, force: bool, owner: int) -> NominateResult:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveNominationByMap(self, map_: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveNominationByOwner(self, owner: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetExcludeMapList(self, array: SourceModHandle[SourceModHandle[ArrayList]]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetNominatedMapList(self, maparray: SourceModHandle[SourceModHandle[ArrayList]], ownerarray: SourceModHandle[SourceModHandle[ArrayList]]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CanMapChooserStartVote(self) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def InitiateMapChooserVote(self, when: MapChange, inputarray: SourceModHandle[SourceModHandle[ArrayList]]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def HasEndOfMapVoteFinished(self) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def EndOfMapVoteEnabled(self) -> bool:
        raise SourcePawnUnboundNativeError
