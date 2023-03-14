from __future__ import annotations

import enum
from enum import IntEnum
from typing import TYPE_CHECKING

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import Array, MethodMap, native, SourceModNativesMixin, WritableString

if TYPE_CHECKING:
    from smx.plugin import SourcePawnPlugin


class PluginStatus(enum.IntEnum):
    Running = 0     # Plugin is running
    Paused = 1      # Plugin is loaded but paused
    Error = 2       # Plugin is loaded but errored/locked
    Loaded = 3      # Plugin has passed loading and can be finalized
    Failed = 4      # Plugin has a fatal failure
    Created = 5     # Plugin is created but not initialized
    Uncompiled = 6  # Plugin is not yet compiled by the JIT
    BadLoad = 7     # Plugin failed to load
    Evicted = 8     # Plugin was unloaded due to an error


class PlInfo(enum.IntEnum):
    Name = 0
    Author = 1
    Description = 2
    Version = 3
    URL = 4


class APLRes(IntEnum):
    APLRes_Success = 0
    APLRes_Failure = 1
    APLRes_SilentFailure = 2


class FeatureType(IntEnum):
    FeatureType_Native = 0
    FeatureType_Capability = 1


class FeatureStatus(IntEnum):
    FeatureStatus_Available = 0
    FeatureStatus_Unavailable = 1
    FeatureStatus_Unknown = 2


class NumberType(IntEnum):
    NumberType_Int8 = 0
    NumberType_Int16 = 1
    NumberType_Int32 = 2


class Address(IntEnum):
    Address_Null = 0


class GameData:
    pass


class PluginIterator:
    pass


class FrameIterator:
    pass


class GameDataMethodMap(MethodMap):
    @native
    def GetOffset(self, this: SourceModHandle[GameData], key: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetKeyValue(self, this: SourceModHandle[GameData], key: str, buffer: str, maxlen: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetAddress(self, this: SourceModHandle[GameData], name: str) -> Address:
        raise SourcePawnUnboundNativeError

    @native
    def GetMemSig(self, this: SourceModHandle[GameData], name: str) -> Address:
        raise SourcePawnUnboundNativeError


class PluginIteratorMethodMap(MethodMap):
    @native
    def Next(self, this: SourceModHandle[PluginIterator]) -> bool:
        raise SourcePawnUnboundNativeError


class FrameIteratorMethodMap(MethodMap):
    @native
    def Next(self, this: SourceModHandle[FrameIterator]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Reset(self, this: SourceModHandle[FrameIterator]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetFunctionName(self, this: SourceModHandle[FrameIterator], buffer: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetFilePath(self, this: SourceModHandle[FrameIterator], buffer: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError


class SourceModIncNatives(SourceModNativesMixin):
    GameData = GameDataMethodMap()
    PluginIterator = PluginIteratorMethodMap()
    FrameIterator = FrameIteratorMethodMap()

    @native
    def GetMyHandle(self) -> SourceModHandle[SourcePawnPlugin]:
        return self.sys.handles.new_handle(self.runtime.plugin)

    @native
    def GetPluginIterator(self) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def MorePlugins(self, iter_: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadPlugin(self, iter_: SourceModHandle) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    # TODO(zk)
    # @native
    # def GetPluginStatus(self, handle: SourceModHandle[SourcePawnPlugin] | None) -> PluginStatus:
    #     if handle is None:
    #         plugin = self.runtime.plugin
    #     else:
    #         plugin = handle.obj
    #
    #     return plugin.status

    @native
    def GetPluginFilename(self, handle: SourceModHandle[SourcePawnPlugin] | None, buffer: WritableString) -> None:
        if handle is None:
            plugin = self.runtime.plugin
        else:
            plugin = handle.obj

        buffer.write(plugin.filename)

    # TODO(zk)
    # @native
    # def IsPluginDebugging(self, handle: SourceModHandle[SourcePawnPlugin] | None) -> bool:
    #     if handle is None:
    #         plugin = self.runtime.plugin
    #     else:
    #         plugin = handle.obj
    #
    #     return plugin.is_debugging

    @native
    def GetPluginInfo(
        self,
        handle: SourceModHandle[SourcePawnPlugin] | None,
        info: PlInfo,
        buf: WritableString
    ) -> bool:
        if handle is None:
            plugin = self.runtime.plugin
        else:
            plugin = handle.obj

        value = plugin.myinfo.get(info.name.lower())
        if value is None:
            return False

        buf.write(value)
        return True

    @native
    def FindPluginByNumber(self, order_num: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def SetFailState(self, string: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def ThrowError(self, fmt: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LogStackTrace(self, fmt: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetTime(self, big_stamp: Array[int]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FormatTime(self, buffer: WritableString, format_: str, stamp: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LoadGameConfigFile(self, file: str) -> SourceModHandle[GameData]:
        raise SourcePawnUnboundNativeError

    @native
    def GameConfGetOffset(self, gc: SourceModHandle, key: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GameConfGetKeyValue(self, gc: SourceModHandle, key: str, buffer: str, maxlen: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GameConfGetAddress(self, gameconf: SourceModHandle, name: str) -> Address:
        raise SourcePawnUnboundNativeError

    @native
    def GetSysTickCount(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def AutoExecConfig(self, auto_create: bool, name: str, folder: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def RegPluginLibrary(self, name: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LibraryExists(self, name: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetExtensionFileStatus(self, name: str, error: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetMapListCompatBind(self, name: str, file: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetFeatureStatus(self, type_: FeatureType, name: str) -> FeatureStatus:
        raise SourcePawnUnboundNativeError

    @native
    def RequireFeature(self, type_: FeatureType, name: str, fmt: str, *args) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def LoadFromAddress(self, addr: Address, size: NumberType) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def StoreToAddress(self, addr: Address, data: int, size: NumberType, update_mem_access: bool) -> None:
        raise SourcePawnUnboundNativeError
