from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from smx.sourcemod.natives.base import MethodMap, native
from smx.sourcemod.natives.console import ConsoleNatives
from smx.sourcemod.natives.convars import ConVarNatives
from smx.sourcemod.natives.files import FilesNatives
from smx.sourcemod.natives.float import FloatNatives
from smx.sourcemod.natives.string import StringNatives
from smx.sourcemod.natives.timers import TimerNatives

if TYPE_CHECKING:
    from smx.sourcemod.system import SourceModSystem


class SourceModNatives(
    ConsoleNatives,
    ConVarNatives,
    FilesNatives,
    FloatNatives,
    StringNatives,
    TimerNatives,
):
    def __init__(self, sys: SourceModSystem):
        """
        :param sys:
            The SourceMod system emulator owning these natives
        """
        self.sys = sys
        self.amx = self.sys.amx
        self.runtime = self.amx.plugin.runtime

    def get_native(self, qn: str) -> Callable[..., Any] | None:
        parts = qn.split('.', maxsplit=1)
        if len(parts) == 2:
            methodmap_name, func_name = parts
            methodmap = getattr(self, methodmap_name, None)
            if not isinstance(methodmap, MethodMap):
                return None

            root = methodmap
        else:
            func_name = qn
            root = self

        func = getattr(root, func_name, None)
        if callable(func) and getattr(func, 'is_native', False):
            return func

    @native('cell')
    def CloseHandle(self, handle_id: int) -> None:
        # TODO(zk): run time error if handle is invalid
        self.sys.handles.close_handle(handle_id)
