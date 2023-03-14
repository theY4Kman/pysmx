from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import MethodMap, SourceModNativesMixin, native


class EntityLumpEntry:
    pass


class EntityLumpEntryMethodMap(MethodMap):
    @native
    def Get(self, this: SourceModHandle[EntityLumpEntry], index: int, keybuf: str, keylen: int, valbuf: str, vallen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Update(self, this: SourceModHandle[EntityLumpEntry], index: int, key: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Insert(self, this: SourceModHandle[EntityLumpEntry], index: int, key: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Erase(self, this: SourceModHandle[EntityLumpEntry], index: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Append(self, this: SourceModHandle[EntityLumpEntry], key: str, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FindKey(self, this: SourceModHandle[EntityLumpEntry], key: str, start: int) -> int:
        raise SourcePawnUnboundNativeError


class EntitylumpNatives(SourceModNativesMixin):
    EntityLumpEntry = EntityLumpEntryMethodMap()
