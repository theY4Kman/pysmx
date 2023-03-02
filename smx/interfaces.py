from __future__ import annotations

import dataclasses
from enum import IntFlag
from typing import Any, List, NamedTuple, Tuple, Union


class ParamCopyFlag(IntFlag):
    COPYBACK = (1 << 0)


class ParamStringFlag(IntFlag):
    UTF8 = (1 << 0)
    COPY = (1 << 1)
    BINARY = (1 << 2)


ParamScalarValueT = Union[int, float]
ParamArrayValueT = Union[str, bytes, List[ParamScalarValueT]]
ParamValueT = Union[ParamScalarValueT, ParamArrayValueT]


@dataclasses.dataclass
class ParamInfo:
    value: ParamValueT | None = None

    #: Whether the input was a scalar or a list of values
    is_scalar: bool = True

    #: Whether this is a pseudo-param holding a return value buffer addr,
    #: and should not be included in the nargs for the call.
    is_rval_buffer: bool = False

    #: Copy-back flags
    flags: ParamCopyFlag = 0

    # XXX(zk): this is a terrible name. ported from SM
    #: Whether this is marked as being used
    marked: bool = False

    #: Size of array in cells, or string in bytes
    size: int = 0

    #: Whether this is a string
    is_string: bool = False

    #: String flags
    string_flags: ParamStringFlag = 0

    #: Local addr of allocated memory for the param
    local_addr: int = -1
    #: Physical addr of allocated memory for the param
    phys_addr: int = -1


class CallableReturnValue(NamedTuple):
    rval: Any
    args: List[ParamValueT]


class ICallable:
    def push_cell(self, value: int):
        raise NotImplementedError

    def push_cell_by_ref(self, value: int, flags: ParamCopyFlag = 0):
        raise NotImplementedError

    def push_float(self, value: float):
        raise NotImplementedError

    def push_float_by_ref(self, value: float, flags: ParamCopyFlag = 0):
        raise NotImplementedError

    # TODO(zk): allow ctypes inputs?
    def push_array(self, value: List[int | float] | None, flags: ParamCopyFlag = 0):
        raise NotImplementedError

    def push_string(self, value: str):
        raise NotImplementedError

    def push_string_ex(self, value: str, length: int, string_flags: ParamStringFlag = 0, copy_flags: ParamCopyFlag = 0):
        raise NotImplementedError

    # TODO(zk): return result
    def execute(self) -> Tuple[CallableReturnValue | None, int]:
        raise NotImplementedError

    # TODO(zk): return result
    def invoke(self) -> Tuple[CallableReturnValue | None, bool]:
        raise NotImplementedError
