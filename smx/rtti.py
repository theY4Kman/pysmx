from __future__ import annotations

import dataclasses
from ctypes import c_char, c_uint8, sizeof
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
    from smx.plugin import SourcePawnPlugin
    from smx.vm import SourcePawnAbstractMachine


def make_type_id(kind: int, payload: int) -> int:
    """Make a type identifier from a kind and payload."""
    assert payload <= RTTI_MAX_TYPE_ID_PAYLOAD, f'payload {payload} is too large (max {RTTI_MAX_TYPE_ID_PAYLOAD})'
    assert kind <= RTTI_MAX_TYPE_ID_KIND, f'kind {kind} is too large (max {RTTI_MAX_TYPE_ID_KIND})'
    return (payload << 4) | kind & RTTI_MAX_TYPE_ID_KIND


def parse_type_id(type_id: int) -> Tuple[int, int]:
    """Parse a type identifier into a kind and payload."""
    kind = type_id & RTTI_MAX_TYPE_ID_KIND
    payload = (type_id >> 4) & RTTI_MAX_TYPE_ID_PAYLOAD
    return kind, payload


# TODO(zk): move these into RTTIControlByte
RTTI_CB_NAMES = {
    RTTIControlByte.BOOL: 'bool',
    RTTIControlByte.ANY: 'any',
    RTTIControlByte.INT32: 'int',
    RTTIControlByte.FLOAT32: 'float',
    RTTIControlByte.CHAR8: 'char',
    RTTIControlByte.TOP_FUNCTION: 'Function',
}


@dataclasses.dataclass
class RTTI:
    """Class representing runtime type information."""

    plugin: SourcePawnPlugin

    type: RTTIControlByte | int
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

    def __str__(self) -> str:
        if self.type in RTTI_CB_RAW_TYPES:
            return RTTI_CB_NAMES[self.type]

        if self.type == RTTIControlByte.FIXED_ARRAY:
            return f'{self.inner}[{self.index}]'

        if self.type == RTTIControlByte.ARRAY:
            return f'{self.inner}[]'

        if self.type == RTTIControlByte.ENUM:
            return self.plugin.rtti_enums[self.index].name

        if self.type == RTTIControlByte.TYPEDEF:
            return self.plugin.rtti_typedefs[self.index].name

        if self.type == RTTIControlByte.TYPESET:
            return self.plugin.rtti_typesets[self.index].name

        if self.type == RTTIControlByte.CLASSDEF:
            return self.plugin.rtti_class_defs[self.index].name

        if self.type == RTTIControlByte.FUNCTION:
            return_type = str(self.inner)

            args = [arg.format_as_arg() for arg in self.args]
            if self.is_variadic:
                args.append('...')

            return f'functon {return_type} ({", ".join(args)})'

        if self.type == RTTIControlByte.ENUM_STRUCT:
            return self.plugin.rtti_enum_structs[self.index].name

        if self.type == RTTIControlByte.VOID:
            return 'void'

    def bytes_sizeof(self) -> int | None:
        """Return the size of this type in bytes.

        For functions, this is the size of the return value. Size of non-fixed arrays is unknown,
        and will return None. Sizes of more complex types, such as enums, typedefs, or classes
        are currently unimplemented.
        """
        if self.type is RTTIControlByte.VOID:
            return 0
        elif self.type is RTTIControlByte.CHAR8:
            return 1
        elif self.type in (
            RTTIControlByte.BOOL,
            RTTIControlByte.INT32,
            RTTIControlByte.FLOAT32,
            RTTIControlByte.ANY,
        ):
            return 4

        if self.type == RTTIControlByte.FIXED_ARRAY:
            return self.inner.bytes_sizeof() * self.index

        if self.type == RTTIControlByte.FUNCTION:
            return self.inner.bytes_sizeof()

    def cells_sizeof(self) -> int | None:
        """Return the size of this type in cells.

        For functions, this is the size of the return value. Size of non-fixed arrays is unknown,
        and will return None. Sizes of more complex types, such as enums, typedefs, or classes
        are currently unimplemented.
        """
        size = self.bytes_sizeof()
        if size is not None:
            return (size + 3) // sizeof(cell)

    def format_as_arg(self) -> str:
        if self.is_by_ref:
            return f'&{self}'
        return str(self)

    def interpret_value(
        self,
        value: int,
        amx: SourcePawnAbstractMachine,
        *,
        size: int | None = None,
    ) -> Any | None:
        if self.type == RTTIControlByte.BOOL:
            return bool(value)
        elif self.type in (RTTIControlByte.ANY, RTTIControlByte.INT32, RTTIControlByte.CHAR8):
            return value
        elif self.type == RTTIControlByte.FLOAT32:
            # TODO(zk): less roundabout parsing?
            return amx._sp_ctof(cell(value))
        elif self.type in (RTTIControlByte.FIXED_ARRAY, RTTIControlByte.ARRAY):
            if self.type is RTTIControlByte.ARRAY:
                if size is None:
                    raise ValueError(f'Cannot interpret dynamic array without known size. Please pass `size`.')
            else:
                size = self.index

            if self.inner.type == RTTIControlByte.CHAR8:
                buf = (c_char * size).from_buffer(amx.heap, value).value
                return buf.decode('utf-8')
            else:
                cells = (cell * size).from_buffer(amx.heap, value)
                return [self.inner.interpret_value(c, amx) for c in cells]
        elif self.type == RTTIControlByte.FUNCTION:
            return self.inner.interpret_value(value, amx)
        elif self.type == RTTIControlByte.VOID:
            return None
        else:
            assert False, f'Unknown RTTI type {self.type}'


class RTTIParser:
    """Class for parsing runtime type information."""

    def __init__(self, plugin: SourcePawnPlugin, data: bytes, offset: int):
        self.plugin = plugin

        self.data = data
        self.offset = offset

        self.is_const: bool = False

    def decode(self) -> RTTI | None:
        # NOTE: _match must be first, as it modifies self.offset
        self.is_const = self._match(RTTIControlByte.CONST) or self.is_const

        type_ = self._read_uint8()
        try:
            type_ = RTTIControlByte(type_)
        except ValueError:
            pass

        if type_ in RTTI_CB_RAW_TYPES:
            return RTTI(self.plugin, type=type_)

        if type_ == RTTIControlByte.FIXED_ARRAY:
            size = self.decode_uint32()
            inner = self.decode()
            return RTTI(self.plugin, type=type_, inner=inner, index=size)

        if type_ == RTTIControlByte.ARRAY:
            inner = self.decode()
            return RTTI(self.plugin, type=type_, inner=inner)

        if type_ in RTTI_CB_INDEXED_TYPES:
            index = self.decode_uint32()
            return RTTI(self.plugin, type=type_, index=index)

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
            return_type = RTTI(self.plugin, type=RTTIControlByte.VOID)
        else:
            return_type = self.decode_new()

        function_type = RTTI(self.plugin, type=RTTIControlByte.FUNCTION, is_variadic=is_variadic, inner=return_type)
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
