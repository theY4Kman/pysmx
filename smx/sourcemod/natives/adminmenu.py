from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import SourceModNativesMixin, native
from smx.sourcemod.natives.topmenus import TopMenu


class AdminmenuNatives(SourceModNativesMixin):
    @native
    def GetAdminTopMenu(self) -> SourceModHandle[SourceModHandle[TopMenu]]:
        raise SourcePawnUnboundNativeError

    @native
    def AddTargetsToMenu(self, menu: SourceModHandle, source_client: int, in_game_only: bool, alive_only: bool) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def AddTargetsToMenu2(self, menu: SourceModHandle, source_client: int, flags: int) -> int:
        raise SourcePawnUnboundNativeError
