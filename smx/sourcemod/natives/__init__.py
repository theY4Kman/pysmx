from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, TYPE_CHECKING

from smx.sourcemod.natives.base import MethodMap
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
    from smx.runtime import SourcePawnPluginRuntime
    from smx.sourcemod.system import SourceModSystem


RGX_NATIVE = re.compile(
    r'''
    ^native\s+
    (?P<return_type>\S+)\s+
    (?P<name>\w+)\s*
    \((?P<params>[^)]*)\)\s*
    (?:;|$)
    ''',
    re.VERBOSE | re.MULTILINE,
)


class BaseSourceModNatives:
    def __init__(self, sys: SourceModSystem):
        """
        :param sys:
            The SourceMod system emulator owning these natives
        """
        self.sys = sys
        self.amx = self.sys.amx
        self.runtime: SourcePawnPluginRuntime = self.amx.plugin.runtime

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

    @staticmethod
    def _read_include_file_natives(include_dir: str | Path | None = None) -> List[Tuple[Path, str]]:
        """Get names of all natives in SourceMod's scripting/include dir"""
        if include_dir is None:
            from smx.compiler import INCLUDE_DIR
            include_dir = INCLUDE_DIR
        include_dir = Path(include_dir)

        natives = []
        for inc_path in include_dir.glob('**/*.inc'):
            contents = inc_path.read_text()
            for match in RGX_NATIVE.finditer(contents):
                natives.append((inc_path, match.group('name')))

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
