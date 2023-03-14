from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    Array,
    Pointer,
    SourceModNativesMixin,
    native,
)


TraceEntityFilter = Callable
TraceEntityEnumerator = Callable


class RayType(IntEnum):
    RayType_EndPoint = 0
    RayType_Infinite = 1


class SdktoolsTraceNatives(SourceModNativesMixin):
    @native
    def TR_GetPointContents(self, pos: Array[float], entindex: Pointer[int]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetPointContentsEnt(self, entindex: int, pos: Array[float]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TR_TraceRay(self, pos: Array[float], vec: Array[float], flags: int, rtype: RayType) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_TraceHull(self, pos: Array[float], vec: Array[float], mins: Array[float], maxs: Array[float], flags: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_EnumerateEntities(self, pos: Array[float], vec: Array[float], mask: int, rtype: RayType, enumerator: TraceEntityEnumerator, data: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_EnumerateEntitiesHull(self, pos: Array[float], vec: Array[float], mins: Array[float], maxs: Array[float], mask: int, enumerator: TraceEntityEnumerator, data: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_EnumerateEntitiesSphere(self, pos: Array[float], radius: float, mask: int, enumerator: TraceEntityEnumerator, data: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_EnumerateEntitiesBox(self, mins: Array[float], maxs: Array[float], mask: int, enumerator: TraceEntityEnumerator, data: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_EnumerateEntitiesPoint(self, pos: Array[float], mask: int, enumerator: TraceEntityEnumerator, data: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_TraceRayFilter(self, pos: Array[float], vec: Array[float], flags: int, rtype: RayType, filter_: TraceEntityFilter, data: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_TraceHullFilter(self, pos: Array[float], vec: Array[float], mins: Array[float], maxs: Array[float], flags: int, filter_: TraceEntityFilter, data: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_ClipRayToEntity(self, pos: Array[float], vec: Array[float], flags: int, rtype: RayType, entity: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_ClipRayHullToEntity(self, pos: Array[float], vec: Array[float], mins: Array[float], maxs: Array[float], flags: int, entity: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_ClipCurrentRayToEntity(self, flags: int, entity: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_TraceRayEx(self, pos: Array[float], vec: Array[float], flags: int, rtype: RayType) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def TR_TraceHullEx(self, pos: Array[float], vec: Array[float], mins: Array[float], maxs: Array[float], flags: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def TR_TraceRayFilterEx(self, pos: Array[float], vec: Array[float], flags: int, rtype: RayType, filter_: TraceEntityFilter, data: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def TR_TraceHullFilterEx(self, pos: Array[float], vec: Array[float], mins: Array[float], maxs: Array[float], flags: int, filter_: TraceEntityFilter, data: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def TR_ClipRayToEntityEx(self, pos: Array[float], vec: Array[float], flags: int, rtype: RayType, entity: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def TR_ClipRayHullToEntityEx(self, pos: Array[float], vec: Array[float], mins: Array[float], maxs: Array[float], flags: int, entity: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def TR_ClipCurrentRayToEntityEx(self, flags: int, entity: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetFraction(self, hndl: SourceModHandle) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetFractionLeftSolid(self, hndl: SourceModHandle) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetStartPosition(self, hndl: SourceModHandle, pos: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetEndPosition(self, pos: Array[float], hndl: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetEntityIndex(self, hndl: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetDisplacementFlags(self, hndl: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetSurfaceName(self, hndl: SourceModHandle, buffer: str, maxlen: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetSurfaceProps(self, hndl: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetSurfaceFlags(self, hndl: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetPhysicsBone(self, hndl: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TR_AllSolid(self, hndl: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def TR_StartSolid(self, hndl: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def TR_DidHit(self, hndl: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetHitGroup(self, hndl: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetHitBoxIndex(self, hndl: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TR_GetPlaneNormal(self, hndl: SourceModHandle, normal: Array[float]) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def TR_PointOutsideWorld(self, pos: Array[float]) -> bool:
        raise SourcePawnUnboundNativeError
