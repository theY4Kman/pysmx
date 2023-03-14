from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    MethodMap,
    SourceModNativesMixin,
    native,
)
from smx.sourcemod.natives.sdktools import SDKFuncConfSource
from smx.sourcemod.natives.sourcemod import Address


ListenCB = Callable
DHookRemovalCB = Callable
DHookCallback = Callable


class ObjectValueType(IntEnum):
    ObjectValueType_Int = 0
    ObjectValueType_Bool = 1
    ObjectValueType_Ehandle = 2
    ObjectValueType_Float = 3
    ObjectValueType_CBaseEntityPtr = 4
    ObjectValueType_IntPtr = 5
    ObjectValueType_BoolPtr = 6
    ObjectValueType_EhandlePtr = 7
    ObjectValueType_FloatPtr = 8
    ObjectValueType_Vector = 9
    ObjectValueType_VectorPtr = 10
    ObjectValueType_CharPtr = 11
    ObjectValueType_String = 12


class ListenType(IntEnum):
    ListenType_Created = 0
    ListenType_Deleted = 1


class ReturnType(IntEnum):
    ReturnType_Unknown = 0
    ReturnType_Void = 1
    ReturnType_Int = 2
    ReturnType_Bool = 3
    ReturnType_Float = 4
    ReturnType_String = 5
    ReturnType_StringPtr = 6
    ReturnType_CharPtr = 7
    ReturnType_Vector = 8
    ReturnType_VectorPtr = 9
    ReturnType_CBaseEntity = 10
    ReturnType_Edict = 11


class HookParamType(IntEnum):
    HookParamType_Unknown = 0
    HookParamType_Int = 1
    HookParamType_Bool = 2
    HookParamType_Float = 3
    HookParamType_String = 4
    HookParamType_StringPtr = 5
    HookParamType_CharPtr = 6
    HookParamType_VectorPtr = 7
    HookParamType_CBaseEntity = 8
    HookParamType_ObjectPtr = 9
    HookParamType_Edict = 10
    HookParamType_Object = 11


class ThisPointerType(IntEnum):
    ThisPointer_Ignore = 0
    ThisPointer_CBaseEntity = 1
    ThisPointer_Address = 2


class HookType(IntEnum):
    HookType_Entity = 0
    HookType_GameRules = 1
    HookType_Raw = 2


class CallingConvention(IntEnum):
    CallConv_CDECL = 0
    CallConv_THISCALL = 1
    CallConv_STDCALL = 2
    CallConv_FASTCALL = 3


class HookMode(IntEnum):
    Hook_Pre = 0
    Hook_Post = 1


class MRESReturn(IntEnum):
    MRES_ChangedHandled = -2
    MRES_ChangedOverride = -1
    MRES_Ignored = 0
    MRES_Handled = 1
    MRES_Override = 2
    MRES_Supercede = 3


class DHookPassFlag(IntEnum):
    DHookPass_ByVal = 1
    DHookPass_ByRef = 2
    DHookPass_ODTOR = 4
    DHookPass_OCTOR = 8
    DHookPass_OASSIGNOP = 16


class DHookRegister(IntEnum):
    DHookRegister_Default = 0
    DHookRegister_AL = 1
    DHookRegister_CL = 2
    DHookRegister_DL = 3
    DHookRegister_BL = 4
    DHookRegister_AH = 5
    DHookRegister_CH = 6
    DHookRegister_DH = 7
    DHookRegister_BH = 8
    DHookRegister_EAX = 9
    DHookRegister_ECX = 10
    DHookRegister_EDX = 11
    DHookRegister_EBX = 12
    DHookRegister_ESP = 13
    DHookRegister_EBP = 14
    DHookRegister_ESI = 15
    DHookRegister_EDI = 16
    DHookRegister_XMM0 = 17
    DHookRegister_XMM1 = 18
    DHookRegister_XMM2 = 19
    DHookRegister_XMM3 = 20
    DHookRegister_XMM4 = 21
    DHookRegister_XMM5 = 22
    DHookRegister_XMM6 = 23
    DHookRegister_XMM7 = 24
    DHookRegister_ST0 = 25


class DHookParam:
    pass


class DHookReturn:
    pass


class DHookSetup:
    pass


class DynamicHook(DHookSetup):
    pass


class DynamicDetour(DHookSetup):
    pass


class DHookParamMethodMap(MethodMap):
    @native
    def Get(self, this: SourceModHandle[DHookParam], num: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetVector(self, this: SourceModHandle[DHookParam], num: int, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetString(self, this: SourceModHandle[DHookParam], num: int, buffer: str, size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Set(self, this: SourceModHandle[DHookParam], num: int, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVector(self, this: SourceModHandle[DHookParam], num: int, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetString(self, this: SourceModHandle[DHookParam], num: int, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetObjectVar(self, this: SourceModHandle[DHookParam], num: int, offset: int, type_: ObjectValueType) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetObjectVarVector(self, this: SourceModHandle[DHookParam], num: int, offset: int, type_: ObjectValueType, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetObjectVarString(self, this: SourceModHandle[DHookParam], num: int, offset: int, type_: ObjectValueType, buffer: str, size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetObjectVar(self, this: SourceModHandle[DHookParam], num: int, offset: int, type_: ObjectValueType, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetObjectVarVector(self, this: SourceModHandle[DHookParam], num: int, offset: int, type_: ObjectValueType, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def IsNull(self, this: SourceModHandle[DHookParam], num: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GetAddress(self, this: SourceModHandle[DHookParam], num: int) -> Address:
        raise SourcePawnUnboundNativeError


class DHookReturnMethodMap(MethodMap):
    @native
    def GetVector(self, this: SourceModHandle[DHookReturn], vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetString(self, this: SourceModHandle[DHookReturn], buffer: str, size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetVector(self, this: SourceModHandle[DHookReturn], vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetString(self, this: SourceModHandle[DHookReturn], buffer: str) -> None:
        raise SourcePawnUnboundNativeError


class DHookSetupMethodMap(MethodMap):
    @native
    def SetFromConf(self, this: SourceModHandle[DHookSetup], gameconf: SourceModHandle, source: SDKFuncConfSource, name: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def AddParam(self, this: SourceModHandle[DHookSetup], type_: HookParamType, size: int, flag: DHookPassFlag, custom_register: DHookRegister) -> None:
        raise SourcePawnUnboundNativeError


class DynamicHookMethodMap(DHookSetupMethodMap):
    @native
    def FromConf(self, gameconf: SourceModHandle, name: str) -> SourceModHandle[DynamicHook]:
        raise SourcePawnUnboundNativeError

    @native
    def HookEntity(self, this: SourceModHandle[DynamicHook], mode: HookMode, entity: int, callback: DHookCallback, removalcb: DHookRemovalCB) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def HookGamerules(self, this: SourceModHandle[DynamicHook], mode: HookMode, callback: DHookCallback, removalcb: DHookRemovalCB) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def HookRaw(self, this: SourceModHandle[DynamicHook], mode: HookMode, addr: Address, callback: DHookCallback) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def RemoveHook(self, hookid: int) -> bool:
        raise SourcePawnUnboundNativeError


class DynamicDetourMethodMap(DHookSetupMethodMap):
    @native
    def FromConf(self, gameconf: SourceModHandle, name: str) -> SourceModHandle[DynamicDetour]:
        raise SourcePawnUnboundNativeError

    @native
    def Enable(self, this: SourceModHandle[DynamicDetour], mode: HookMode, callback: DHookCallback) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Disable(self, this: SourceModHandle[DynamicDetour], mode: HookMode, callback: DHookCallback) -> bool:
        raise SourcePawnUnboundNativeError


class DhooksNatives(SourceModNativesMixin):
    DHookParam = DHookParamMethodMap()
    DHookReturn = DHookReturnMethodMap()
    DHookSetup = DHookSetupMethodMap()
    DynamicHook = DynamicHookMethodMap()
    DynamicDetour = DynamicDetourMethodMap()

    @native
    def DHookAddEntityListener(self, type_: ListenType, callback: ListenCB) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookRemoveEntityListener(self, type_: ListenType, callback: ListenCB) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DHookCreate(self, offset: int, hooktype: HookType, returntype: ReturnType, thistype: ThisPointerType, callback: DHookCallback) -> SourceModHandle[DynamicHook]:
        raise SourcePawnUnboundNativeError

    @native
    def DHookCreateDetour(self, funcaddr: Address, call_conv: CallingConvention, returntype: ReturnType, this_type: ThisPointerType) -> SourceModHandle[DynamicDetour]:
        raise SourcePawnUnboundNativeError

    @native
    def DHookCreateFromConf(self, gameconf: SourceModHandle, name: str) -> SourceModHandle[DHookSetup]:
        raise SourcePawnUnboundNativeError

    @native
    def DHookSetFromConf(self, setup: SourceModHandle, gameconf: SourceModHandle, source: SDKFuncConfSource, name: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DHookEnableDetour(self, setup: SourceModHandle, post: bool, callback: DHookCallback) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DHookDisableDetour(self, setup: SourceModHandle, post: bool, callback: DHookCallback) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DHookAddParam(self, setup: SourceModHandle, type_: HookParamType, size: int, flag: DHookPassFlag, custom_register: DHookRegister) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookEntity(self, setup: SourceModHandle, post: bool, entity: int, removalcb: DHookRemovalCB, callback: DHookCallback) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGamerules(self, setup: SourceModHandle, post: bool, removalcb: DHookRemovalCB, callback: DHookCallback) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def DHookRaw(self, setup: SourceModHandle, post: bool, addr: Address, removalcb: DHookRemovalCB, callback: DHookCallback) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def DHookRemoveHookID(self, hookid: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGetParam(self, h_params: SourceModHandle, num: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGetParamVector(self, h_params: SourceModHandle, num: int, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGetParamString(self, h_params: SourceModHandle, num: int, buffer: str, size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookSetParam(self, h_params: SourceModHandle, num: int, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookSetParamVector(self, h_params: SourceModHandle, num: int, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookSetParamString(self, h_params: SourceModHandle, num: int, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGetReturn(self, h_return: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGetReturnVector(self, h_return: SourceModHandle, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGetReturnString(self, h_return: SourceModHandle, buffer: str, size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookSetReturn(self, h_return: SourceModHandle, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookSetReturnVector(self, h_return: SourceModHandle, vec: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookSetReturnString(self, h_return: SourceModHandle, value: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGetParamObjectPtrVar(self, h_params: SourceModHandle, num: int, offset: int, type_: ObjectValueType) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def DHookSetParamObjectPtrVar(self, h_params: SourceModHandle, num: int, offset: int, type_: ObjectValueType, value: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGetParamObjectPtrVarVector(self, h_params: SourceModHandle, num: int, offset: int, type_: ObjectValueType, buffer: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookSetParamObjectPtrVarVector(self, h_params: SourceModHandle, num: int, offset: int, type_: ObjectValueType, value: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGetParamObjectPtrString(self, h_params: SourceModHandle, num: int, offset: int, type_: ObjectValueType, buffer: str, size: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def DHookIsNullParam(self, h_params: SourceModHandle, num: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def DHookGetParamAddress(self, h_params: SourceModHandle, num: int) -> Address:
        raise SourcePawnUnboundNativeError
