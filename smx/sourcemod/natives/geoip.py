from __future__ import annotations

from enum import IntEnum

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import (
    SourceModNativesMixin,
    WritableString,
    native,
)


class Continent(IntEnum):
    CONTINENT_UNKNOWN = 0
    CONTINENT_AFRICA = 1
    CONTINENT_ANTARCTICA = 2
    CONTINENT_ASIA = 3
    CONTINENT_EUROPE = 4
    CONTINENT_NORTH_AMERICA = 5
    CONTINENT_OCEANIA = 6
    CONTINENT_SOUTH_AMERICA = 7


class GeoipNatives(SourceModNativesMixin):
    @native
    def GeoipCode2(self, ip: str, ccode: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipCode3(self, ip: str, ccode: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipRegionCode(self, ip: str, ccode: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipContinentCode(self, ip: str, ccode: str) -> Continent:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipCountry(self, ip: str, name: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipCountryEx(self, ip: str, name: WritableString, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipContinent(self, ip: str, name: WritableString, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipRegion(self, ip: str, name: WritableString, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipCity(self, ip: str, name: WritableString, client: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipTimezone(self, ip: str, name: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipLatitude(self, ip: str) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipLongitude(self, ip: str) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def GeoipDistance(self, lat1: float, lon1: float, lat2: float, lon2: float, system: int) -> float:
        raise SourcePawnUnboundNativeError
