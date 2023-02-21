from __future__ import annotations

import dataclasses
from ctypes import c_char, c_uint8
from typing import Any, Tuple, TYPE_CHECKING

from smx.definitions import (
    cell,
    RTTI_CB_INDEXED_TYPES,
    RTTI_CB_RAW_TYPES,
    RTTI_MAX_TYPE_ID_KIND,
    RTTI_MAX_TYPE_ID_PAYLOAD,
    RTTIControlByte,
)

if TYPE_CHECKING:
    from smx.vm import SourcePawnAbstractMachine


def make_type_id(payload: int, kind: int) -> int:
    """Make a type identifier from a payload and kind."""
    assert payload <= RTTI_MAX_TYPE_ID_PAYLOAD, f'payload {payload} is too large (max {RTTI_MAX_TYPE_ID_PAYLOAD})'
    assert kind <= RTTI_MAX_TYPE_ID_KIND, f'kind {kind} is too large (max {RTTI_MAX_TYPE_ID_KIND})'
    return (payload << 4) | kind & RTTI_MAX_TYPE_ID_KIND


def parse_type_id(type_id: int) -> Tuple[int, int]:
    """Parse a type identifier into a payload and kind."""
    return (type_id >> 4) & RTTI_MAX_TYPE_ID_PAYLOAD, type_id & RTTI_MAX_TYPE_ID_KIND


@dataclasses.dataclass
class RTTI:
    """Class representing runtime type information."""

    type: RTTIControlByte
    index: int = 0
    inner: RTTI | None = None
    is_const: bool = False

    # Arguments
    is_by_ref: bool = False

    # Function type only
    args: list[RTTI] = dataclasses.field(default_factory=list)
    is_variadic: bool = False

    def __post_init__(self):
        if not isinstance(self.type, RTTIControlByte):
            self.type = RTTIControlByte(self.type)

    def interpret_value(self, value: int, amx: SourcePawnAbstractMachine) -> Any | None:
        if self.type == RTTIControlByte.BOOL:
            return bool(value)
        elif self.type in (RTTIControlByte.ANY, RTTIControlByte.INT32, RTTIControlByte.CHAR8):
            return value
        elif self.type == RTTIControlByte.FLOAT32:
            # TODO(zk): less roundabout parsing?
            return amx._sp_ctof(cell(value))
        elif self.type == RTTIControlByte.FIXED_ARRAY:
            if self.inner.type == RTTIControlByte.CHAR8:
                buf = (c_char * self.index).from_buffer(amx.heap, value).value
                return buf.decode('utf-8')
            else:
                cells = (cell * self.index).from_buffer(amx.heap, value)
                return [self.inner.interpret_value(c, amx) for c in cells]
        else:
            assert False, f'Unknown RTTI type {self.type}'


class RTTIParser:
    """Class for parsing runtime type information."""

    def __init__(self, data: bytes, offset: int):
        self.data = data
        self.offset = offset

        self.is_const: bool = False

    def decode(self) -> RTTI | None:
        # NOTE: _match must be first, as it modifies self.offset
        self.is_const = self._match(RTTIControlByte.CONST) or self.is_const

        type_ = RTTIControlByte(self._read_uint8())
        if type_ in RTTI_CB_RAW_TYPES:
            return RTTI(type=type_)

        if type_ == RTTIControlByte.FIXED_ARRAY:
            size = self.decode_uint32()
            inner = self.decode()
            return RTTI(type=type_, inner=inner, index=size)

        if type_ == RTTIControlByte.ARRAY:
            inner = self.decode()
            return RTTI(type=type_, inner=inner)

        if type_ in RTTI_CB_INDEXED_TYPES:
            index = self.decode_uint32()
            return RTTI(type=type_, index=index)

        if type_ == RTTIControlByte.FUNCTION:
            return self.decode_function()

    def decode_uint32(self) -> int:
        value = 0
        shift = 0
        while True:
            b = self.data[self.offset]
            self.offset += 1
            value |= (b & 0x7f) << shift
            if not b & 0x80:
                break
            shift += 7
        return value

    def decode_function(self) -> RTTI:
        argc = self._read_uint8()
        is_variadic = self._match(RTTIControlByte.VARIADIC)

        if self._match(RTTIControlByte.VOID):
            return_type = RTTI(type=RTTIControlByte.VOID)
        else:
            return_type = self.decode_new()

        function_type = RTTI(type=RTTIControlByte.FUNCTION, is_variadic=is_variadic, inner=return_type)
        for _ in range(argc):
            is_by_ref = self._match(RTTIControlByte.BY_REF)
            arg_type = self.decode_new()
            arg_type.is_by_ref = is_by_ref
            function_type.args.append(arg_type)

        return function_type

    def decode_new(self) -> RTTI:
        was_const = self.is_const
        self.is_const = False

        result = self.decode()
        assert result
        result.is_const = self.is_const

        self.is_const = was_const
        return result

    def _match(self, v: int) -> bool:
        if self.data[self.offset] != v:
            return False

        self.offset += 1
        return True

    def _read_uint8(self) -> int:
        v = c_uint8.from_buffer_copy(self.data[self.offset:]).value
        self.offset += 1
        return v
