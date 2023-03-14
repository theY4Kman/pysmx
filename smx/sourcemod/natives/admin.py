from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import (
    Array,
    Pointer,
    SourceModNativesMixin,
    WritableString,
    native,
)


class AdminFlag(IntEnum):
    Admin_Reservation = 0
    Admin_Generic = 1
    Admin_Kick = 2
    Admin_Ban = 3
    Admin_Unban = 4
    Admin_Slay = 5
    Admin_Changemap = 6
    Admin_Convars = 7
    Admin_Config = 8
    Admin_Chat = 9
    Admin_Vote = 10
    Admin_Password = 11
    Admin_RCON = 12
    Admin_Cheats = 13
    Admin_Root = 14
    Admin_Custom1 = 15
    Admin_Custom2 = 16
    Admin_Custom3 = 17
    Admin_Custom4 = 18
    Admin_Custom5 = 19
    Admin_Custom6 = 20


class OverrideType(IntEnum):
    Override_Command = 1
    Override_CommandGroup = 2


class OverrideRule(IntEnum):
    Command_Deny = 0
    Command_Allow = 1


class ImmunityType(IntEnum):
    Immunity_Default = 1
    Immunity_Global = 2


class GroupId(IntEnum):
    INVALID_GROUP_ID = -1


class AdminId(IntEnum):
    INVALID_ADMIN_ID = -1


class AdmAccessMode(IntEnum):
    Access_Real = 0
    Access_Effective = 1


class AdminCachePart(IntEnum):
    AdminCache_Overrides = 0
    AdminCache_Groups = 1
    AdminCache_Admins = 2


class AdminNatives(SourceModNativesMixin):
    @native
    def DumpAdminCache(self, part: AdminCachePart, rebuild: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def AddCommandOverride(self, cmd: str, type_: OverrideType, flags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetCommandOverride(self, cmd: str, type_: OverrideType, flags: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def UnsetCommandOverride(self, cmd: str, type_: OverrideType) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CreateAdmGroup(self, group_name: str) -> GroupId:
        raise SourcePawnUnboundNativeError

    @native
    def FindAdmGroup(self, group_name: str) -> GroupId:
        raise SourcePawnUnboundNativeError

    @native
    def SetAdmGroupAddFlag(self, id: GroupId, flag: AdminFlag, enabled: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdmGroupAddFlag(self, id: GroupId, flag: AdminFlag) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdmGroupAddFlags(self, id: GroupId) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetAdmGroupImmunity(self, id: GroupId, type_: ImmunityType, enabled: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdmGroupImmunity(self, id: GroupId, type_: ImmunityType) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetAdmGroupImmuneFrom(self, id: GroupId, other_id: GroupId) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdmGroupImmuneCount(self, id: GroupId) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdmGroupImmuneFrom(self, id: GroupId, number: int) -> GroupId:
        raise SourcePawnUnboundNativeError

    @native
    def AddAdmGroupCmdOverride(self, id: GroupId, name: str, type_: OverrideType, rule: OverrideRule) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdmGroupCmdOverride(self, id: GroupId, name: str, type_: OverrideType, rule: Pointer[OverrideRule]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def RegisterAuthIdentType(self, name: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def CreateAdmin(self, name: str) -> AdminId:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdminUsername(self, id: AdminId, name: WritableString) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def BindAdminIdentity(self, id: AdminId, auth: str, ident: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetAdminFlag(self, id: AdminId, flag: AdminFlag, enabled: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdminFlag(self, id: AdminId, flag: AdminFlag, mode: AdmAccessMode) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdminFlags(self, id: AdminId, mode: AdmAccessMode) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def AdminInheritGroup(self, id: AdminId, gid: GroupId) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdminGroupCount(self, id: AdminId) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdminGroup(self, id: AdminId, index: int, name: WritableString) -> GroupId:
        raise SourcePawnUnboundNativeError

    @native
    def SetAdminPassword(self, id: AdminId, password: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdminPassword(self, id: AdminId, buffer: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FindAdminByIdentity(self, auth: str, identity: str) -> AdminId:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveAdmin(self, id: AdminId) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FlagBitsToBitArray(self, bits: int, array: Array[bool], max_size: int) -> int:
        i = 0
        for i in range(min(max_size, len(AdminFlag))):
            array[i] = bool(bits & (1 << i))
        return i

    @native
    def FlagBitArrayToBits(self, array: Array[bool], max_size: int) -> int:
        bits = 0
        for i in range(min(max_size, len(AdminFlag))):
            bits |= array[i] << i
        return bits & 0xFFFFFFFF

    @native
    def FlagArrayToBits(self, array: Array[AdminFlag], num_flags: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FlagBitsToArray(self, bits: int, array: Array[AdminFlag], max_size: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FindFlagByName(self, name: str, flag: Pointer[AdminFlag]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FindFlagByChar(self, c: int, flag: Pointer[AdminFlag]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FindFlagChar(self, flag: AdminFlag, c: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def ReadFlagString(self, flags: str, numchars: Pointer[int]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def CanAdminTarget(self, admin: AdminId, target: AdminId) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def CreateAuthMethod(self, method: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SetAdmGroupImmunityLevel(self, gid: GroupId, level: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdmGroupImmunityLevel(self, gid: GroupId) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SetAdminImmunityLevel(self, id: AdminId, level: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetAdminImmunityLevel(self, id: AdminId) -> int:
        raise SourcePawnUnboundNativeError
