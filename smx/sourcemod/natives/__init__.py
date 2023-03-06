from __future__ import annotations

from typing import Any, Callable, Dict, TYPE_CHECKING

from smx.sourcemod.natives.base import MethodMap, native
from smx.sourcemod.natives.console import ConsoleNatives
from smx.sourcemod.natives.convars import ConVarNatives
from smx.sourcemod.natives.files import FilesNatives
from smx.sourcemod.natives.float import FloatNatives
from smx.sourcemod.natives.handles import HandlesNatives
from smx.sourcemod.natives.shell import ShellNatives
from smx.sourcemod.natives.sourcemod import SourceModIncNatives
from smx.sourcemod.natives.string import StringNatives
from smx.sourcemod.natives.timers import TimerNatives

if TYPE_CHECKING:
    from smx.sourcemod.system import SourceModSystem


class BaseSourceModNatives:
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

    @classmethod
    def _get_all_natives(cls) -> Dict[str, Callable[..., Any]]:
        natives = {}
        for name in dir(cls):
            obj = getattr(cls, name)
            if callable(obj) and getattr(obj, 'is_native', False):
                natives[name] = obj
        return natives


class SourceModNatives(
    BaseSourceModNatives,

    ConsoleNatives,
    ConVarNatives,
    FilesNatives,
    FloatNatives,
    HandlesNatives,
    SourceModIncNatives,
    StringNatives,
    TimerNatives,
):
    pass


class SourceModTestNatives(
    BaseSourceModNatives,

    FloatNatives,
    ShellNatives,
):
    """Natives used in testing only"""
