from __future__ import annotations

from ctypes import sizeof
from typing import TYPE_CHECKING

from smx.definitions import cell
from smx.exceptions import SourcePawnRuntimeError
from smx.sourcemod.natives import FloatNatives
from smx.sourcemod.natives.base import native, SourceModNativesMixin, WritableString

if TYPE_CHECKING:
    from smx.runtime import PluginFunction
    from smx.interfaces import ParamCopyFlag, ParamStringFlag


def _format_float(value: float) -> str:
    # The C standard library's printf() function uses 6 digits of precision
    # for floats if precision not specified, so we must recreate that behaviour.
    return f'{value:.06f}'


class ShellNatives(SourceModNativesMixin):
    """Natives used when running sourcepawn's test suite"""

    @native('cell')
    def printnum(self, value: int) -> int:
        s = f'{value}\n'
        self.runtime.printf(s)
        return len(s)

    @native('cell')
    def writenum(self, value: int) -> int:
        s = f'{value}'
        self.runtime.printf(s)
        return len(s)

    @native('float')
    def printfloat(self, value: float) -> int:
        s = f'{_format_float(value)}\n'
        self.runtime.printf(s)
        return len(s)

    @native('float')
    def writefloat(self, value: float) -> int:
        s = f'{_format_float(value)}'
        self.runtime.printf(s)
        return len(s)

    @native('...')
    def printnums(self, *addrs) -> int:
        nums = [self.amx._getheapcell(addr) for addr in addrs]
        self.runtime.printf(', '.join(str(x) for x in nums) + '\n')
        return 1

    @native('string')
    def print(self, value: str) -> int:
        self.runtime.printf(value)
        return len(value)

    @native
    def dump_stack_trace(self):
        self.runtime.printf(self.amx.dump_stack() + '\n')

    @native
    def report_error(self):
        self.runtime.amx.report_error('What the crab?!')

    @native
    def donothing(self):
        return 1

    @native('cell')
    def dynamic_native(self, arg: int) -> int:
        # XXX(zk): should this probe more?
        return arg

    # TODO(zk): add conveniences for by-ref params
    @native('cell', 'cell', 'cell', 'cell')
    def access_2d_array(self, array_addr: int, x: int, y: int, out_addr: int) -> int:
        row_addr = self.amx._getheapcell(array_addr + x * sizeof(cell))
        value = self.amx._getheapcell(row_addr + y * sizeof(cell))
        self.amx._writeheap(out_addr, cell(value))
        return 1

    @native('function', 'cell')
    def invoke(self, func: PluginFunction, count: int) -> int:
        for i in range(count):
            try:
                func.invoke()
            except SourcePawnRuntimeError as e:
                self.runtime.printf(e.debug_output())
                return 0

        return 1

    @native('function', 'cell')
    def execute(self, func: PluginFunction, count: int) -> int:
        ok = 0
        for i in range(count):
            try:
                func.execute()
            except SourcePawnRuntimeError as e:
                self.runtime.printf(e.debug_output())
                continue
            else:
                ok += 1

        return ok

    @native('function', 'writable_string', 'cell', 'cell')
    def call_with_string(
        self,
        fn: PluginFunction,
        buffer: WritableString,
        sz_flags: ParamStringFlag,
        cp_flags: ParamCopyFlag,
    ) -> int:
        # TODO(zk): allow passing WritableString directly to push_string_ex
        fn.push_string_ex(buffer.read(), buffer.max_length, sz_flags, cp_flags)
        fn.push_cell(buffer.max_length)

        call_rval, did_succeed = fn.invoke()
        if not did_succeed:
            return 0

        buffer.write(call_rval.args[0], null_terminate=True)
        return call_rval.rval

    # TODO(zk): add some convenience wrappers around heap addresses
    @native('cell', 'cell', 'cell', 'function')
    def copy_2d_array_to_callback(
        self,
        flat_array_addr: int,
        length: int,
        stride: int,
        callback: PluginFunction,
    ) -> None:
        with self.amx._heap_scope():
            copied_array_addr = self.amx._heap_alloc_2d_array(length, stride, init_addr=flat_array_addr)
            callback(copied_array_addr, length, stride)
            return 0

    @native('cell', 'cell')
    def assert_eq(self, lhs: int, rhs: int) -> None:
        # TODO(zk): report error on comp failure
        assert lhs == rhs

    CloseHandle = donothing

    @native('cell')
    def __float_ctor(self, int_val: int):
        # XXX(zk): is this supposed to reinterpret a cell as a float? or turn an int into a float?
        return float(int_val)

    float = __float_ctor

    __float_add = FloatNatives.FloatAdd
    __float_sub = FloatNatives.FloatSub
    __float_mul = FloatNatives.FloatMul
    __float_div = FloatNatives.FloatDiv

    @native('float', 'float')
    def __float_mod(self, dividend: float, divisor: float) -> float:
        return dividend % divisor

    @native('float', 'float')
    def __float_gt(self, lhs: float, rhs: float) -> bool:
        return lhs > rhs

    @native('float', 'float')
    def __float_ge(self, lhs: float, rhs: float) -> bool:
        return lhs >= rhs

    @native('float', 'float')
    def __float_lt(self, lhs: float, rhs: float) -> bool:
        return lhs < rhs

    @native('float', 'float')
    def __float_le(self, lhs: float, rhs: float) -> bool:
        return lhs <= rhs

    @native('float', 'float')
    def __float_eq(self, lhs: float, rhs: float) -> bool:
        return lhs == rhs

    @native('float', 'float')
    def __float_ne(self, lhs: float, rhs: float) -> bool:
        return lhs != rhs

    @native('float')
    def __float_not(self, value: float) -> bool:
        if value == float('nan'):
            return True
        return not value
