from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, TYPE_CHECKING

from smx.sourcemod.natives.admin import AdminNatives
from smx.sourcemod.natives.adminmenu import AdminmenuNatives
from smx.sourcemod.natives.adt_array import AdtArrayNatives
from smx.sourcemod.natives.adt_stack import AdtStackNatives
from smx.sourcemod.natives.adt_trie import AdtTrieNatives
from smx.sourcemod.natives.banning import BanningNatives
from smx.sourcemod.natives.base import MethodMap
from smx.sourcemod.natives.basecomm import BasecommNatives
from smx.sourcemod.natives.bitbuffer import BitbufferNatives
from smx.sourcemod.natives.clientprefs import ClientprefsNatives
from smx.sourcemod.natives.clients import ClientsNatives
from smx.sourcemod.natives.commandfilters import CommandfiltersNatives
from smx.sourcemod.natives.commandline import CommandlineNatives
from smx.sourcemod.natives.console import ConsoleNatives, ConsoleNatives
from smx.sourcemod.natives.convars import ConvarsNatives
from smx.sourcemod.natives.core import CoreNatives
from smx.sourcemod.natives.cstrike import CstrikeNatives
from smx.sourcemod.natives.datapack import DatapackNatives
from smx.sourcemod.natives.dbi import DbiNatives
from smx.sourcemod.natives.dhooks import DhooksNatives
from smx.sourcemod.natives.entity import EntityNatives
from smx.sourcemod.natives.entity_prop_stocks import EntityPropStocksNatives
from smx.sourcemod.natives.entitylump import EntitylumpNatives
from smx.sourcemod.natives.events import EventsNatives
from smx.sourcemod.natives.files import FilesNatives, FilesNatives
from smx.sourcemod.natives.float import FloatNatives, FloatNatives
from smx.sourcemod.natives.functions import FunctionsNatives
from smx.sourcemod.natives.geoip import GeoipNatives
from smx.sourcemod.natives.halflife import HalflifeNatives
from smx.sourcemod.natives.handles import HandlesNatives, HandlesNatives
from smx.sourcemod.natives.keyvalues import KeyvaluesNatives
from smx.sourcemod.natives.lang import LangNatives
from smx.sourcemod.natives.logging import LoggingNatives
from smx.sourcemod.natives.mapchooser import MapchooserNatives
from smx.sourcemod.natives.menus import MenusNatives
from smx.sourcemod.natives.nextmap import NextmapNatives
from smx.sourcemod.natives.profiler import ProfilerNatives
from smx.sourcemod.natives.protobuf import ProtobufNatives
from smx.sourcemod.natives.regex import RegexNatives
from smx.sourcemod.natives.sdkhooks import SdkhooksNatives
from smx.sourcemod.natives.sdktools import SdktoolsNatives
from smx.sourcemod.natives.sdktools_client import SdktoolsClientNatives
from smx.sourcemod.natives.sdktools_engine import SdktoolsEngineNatives
from smx.sourcemod.natives.sdktools_entinput import SdktoolsEntinputNatives
from smx.sourcemod.natives.sdktools_entoutput import SdktoolsEntoutputNatives
from smx.sourcemod.natives.sdktools_functions import SdktoolsFunctionsNatives
from smx.sourcemod.natives.sdktools_gamerules import SdktoolsGamerulesNatives
from smx.sourcemod.natives.sdktools_sound import SdktoolsSoundNatives
from smx.sourcemod.natives.sdktools_stringtables import SdktoolsStringtablesNatives
from smx.sourcemod.natives.sdktools_tempents import SdktoolsTempentsNatives
from smx.sourcemod.natives.sdktools_trace import SdktoolsTraceNatives
from smx.sourcemod.natives.sdktools_variant_t import SdktoolsVariantTNatives
from smx.sourcemod.natives.sdktools_voice import SdktoolsVoiceNatives
from smx.sourcemod.natives.shell import ShellNatives, ShellNatives
from smx.sourcemod.natives.sorting import SortingNatives
from smx.sourcemod.natives.sourcemod import SourceModIncNatives
from smx.sourcemod.natives.string import StringNatives, StringNatives
from smx.sourcemod.natives.textparse import TextparseNatives
from smx.sourcemod.natives.tf2 import Tf2Natives
from smx.sourcemod.natives.timers import TimerNatives, TimerNatives
from smx.sourcemod.natives.topmenus import TopmenusNatives
from smx.sourcemod.natives.usermessages import UsermessagesNatives
from smx.sourcemod.natives.vector import VectorNatives

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

    AdminmenuNatives,
    AdminNatives,
    AdtArrayNatives,
    AdtStackNatives,
    AdtTrieNatives,
    BanningNatives,
    BasecommNatives,
    BitbufferNatives,
    ClientprefsNatives,
    ClientsNatives,
    CommandfiltersNatives,
    CommandlineNatives,
    ConsoleNatives,
    ConvarsNatives,
    CoreNatives,
    CstrikeNatives,
    DatapackNatives,
    DbiNatives,
    DhooksNatives,
    EntitylumpNatives,
    EntityNatives,
    EntityPropStocksNatives,
    EventsNatives,
    FilesNatives,
    FloatNatives,
    FunctionsNatives,
    GeoipNatives,
    HalflifeNatives,
    HandlesNatives,
    KeyvaluesNatives,
    LangNatives,
    LoggingNatives,
    MapchooserNatives,
    MenusNatives,
    NextmapNatives,
    ProfilerNatives,
    ProtobufNatives,
    RegexNatives,
    SdkhooksNatives,
    SdktoolsClientNatives,
    SdktoolsEngineNatives,
    SdktoolsEntinputNatives,
    SdktoolsEntoutputNatives,
    SdktoolsFunctionsNatives,
    SdktoolsGamerulesNatives,
    SdktoolsNatives,
    SdktoolsSoundNatives,
    SdktoolsStringtablesNatives,
    SdktoolsTempentsNatives,
    SdktoolsTraceNatives,
    SdktoolsVariantTNatives,
    SdktoolsVoiceNatives,
    ShellNatives,
    SortingNatives,
    SourceModIncNatives,
    StringNatives,
    TextparseNatives,
    Tf2Natives,
    TimerNatives,
    TopmenusNatives,
    UsermessagesNatives,
    VectorNatives,
):
    pass


class SourceModTestNatives(
    BaseSourceModNatives,

    FloatNatives,
    ShellNatives,
):
    """Natives used in testing only"""
