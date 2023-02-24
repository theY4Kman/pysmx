from __future__ import annotations

import ctypes
import dataclasses
import logging
import struct
import sys
import typing
from copy import deepcopy
from ctypes import (
    addressof,
    c_byte,
    c_char_p,
    c_float,
    c_int16,
    c_int8,
    c_void_p,
    memmove,
    memset,
    POINTER,
    pointer,
    sizeof,
)
from datetime import datetime
from enum import IntFlag
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Tuple, Type, TYPE_CHECKING, TypeVar, Union

from smx.definitions import cell, PyCSimpleType, RTTIControlByte, SP_MAX_EXEC_PARAMS, ucell
from smx.exceptions import SourcePawnPluginError, SourcePawnPluginNativeError
from smx.opcodes import opcodes, SourcePawnInstruction
from smx.pawn import SMXInstructions
from smx.rtti import RTTI
from smx.sourcemod.natives.base import convert_return_value, WritableString
from smx.sourcemod.system import SourceModSystem

if TYPE_CHECKING:
    from smx.reader import SourcePawnPlugin

logger = logging.getLogger(__name__)

V = TypeVar('V')
CType = TypeVar('CType', bound=PyCSimpleType)


def list_pop(lst, index=-1, default=None):
    try:
        return lst.pop(index)
    except IndexError:
        return default


def tohex(val):
    return '%x' % ucell(val).value


class SourcePawnAbstractMachine:
    ZERO = cell(0)

    def __init__(self, runtime: SourcePawnPluginRuntime, plugin: SourcePawnPlugin):
        """
        :param runtime:
            Runtime of the plug-in this Abstract Machine will run

        :param plugin:
            The plug-in this Abstract Machine will run
        """
        self.initialized = False
        self.runtime = runtime
        self.plugin = plugin

        self.PRI = 0  # primary register (ALU, general purpose)
        self.ALT = 0  # alternate register (general purpose)
        self.FRM = 0  # stack frame pointer, stack-relative memory reads and
                      # writes are relative to the address in this register
        self.CIP = 0  # code instruction pointer
        self.DAT = 0  # offset to the start of the data
        self.COD = 0  # offset to the start of the code
        self.STP = 0  # stack top
        self.STK = 0  # stack index, indicates the current position in the
                      # stack. The stack runs downwards from the STP register
                      # towards zero
        self.HEA = 0  # heap pointer. Dynamically allocated memory comes from
                      # the heap and the HEA register indicates the top of the
                      # heap
        self._hp_scope: int = 0

        self.data = None  # Actual data section in memory
        self.code = None  # Code section in memory
        self.heap = None

        self.smsys = None           # Our local copy of the SourceMod system emulator
        self.sm_natives = None      # Our local copy of the SourceMod Python natives
        self.instructions: SMXInstructions | None = None    # The SMX instructions methods

        # Records the current stack in a list
        # Each item is (data_offset, c_type())
        self._stack = None

        # The list of instructions executed
        # TODO: tie this to the current frame
        self._executed: List[Tuple[int, SourcePawnInstruction, Tuple[int, ...], Any]] = []

        # The current instruction being executed
        self.instr = None
        # Address of the current instruction being executed
        self.instr_addr = None
        # Whether code is running (i.e. a halt instruction has not been encountered since execution start)
        self.halted = None

    def init(self):
        self.COD = self.plugin.pcode.pcode
        self.DAT = self.plugin.data

        # TODO(zk): use memoryview to prevent copying
        self.data = self.plugin.base[self.DAT:][:self.plugin.datasize]
        self.code = self.plugin.base[self.COD:][:self.plugin.pcode.size]

        self.heap = (c_byte * self.plugin.memsize)()
        memmove(self.heap, self.data, self.plugin.datasize)
        # XXX(zk): is this necessary? does ctypes automatically zero out requested memory?
        memset(addressof(self.heap) + self.plugin.datasize, 0, self.plugin.memsize - self.plugin.datasize)

        self.HEA = self.plugin.datasize
        self.STP = len(self.heap)
        self.STK = self.STP
        self.FRM = self.STK  # XXX: this is a guess. Is this correct?

        self.smsys = SourceModSystem(self)
        self.sm_natives = self.smsys.natives
        self.instructions = SMXInstructions()

        self._stack = []
        self._executed = []

        self.instr = 0
        self.instr_addr = 0
        self.halted = False

        self.initialized = True

    def _cip(self):
        cip = self.CIP
        self.CIP += sizeof(cell)
        return cip

    def _halt(self, offs):
        self.halted = True

    def _jumprel(self, offset):
        """Returns the abs address to jump to"""
        addr = self._readcodecell(offset)
        return addr

    def _getcodecell(self, *, peek=False):
        cip = self._cip() if not peek else self.CIP
        return self._readcodecell(cip)

    def _readcodecell(self, address):
        off = address + 4
        return struct.unpack('<l', self.code[address:off])[0]

    def _getdatacell(self, offset):
        val, = struct.unpack('<l', self.data[offset:offset + sizeof(cell)])
        return val

    def _getheap(self, offset: int, ctype: Type[CType]) -> Any:
        heap = ctypes.cast(self.heap, POINTER(ctype))
        heap_ptr = ctypes.cast(pointer(heap), POINTER(c_void_p))
        heap_ptr.contents.value += offset
        return heap.contents.value

    def _getheapcell(self, offset: int) -> int:
        return self._getheap(offset, cell)

    def _getheapbyte(self, offset: int) -> int:
        return self._getheap(offset, c_int8)

    def _getheapshort(self, offset: int) -> int:
        return self._getheap(offset, c_int16)

    def _getstackcell(self, offset=0):
        return self._getheapcell(self.STK + offset)

    def _getdatabyte(self, offset):
        return struct.unpack('<b', self.data[offset:offset+sizeof(c_int8)])[0]

    def _getdatashort(self, offset):
        return struct.unpack('<h', self.data[offset:offset+sizeof(c_int16)])[0]

    def _getheapstring(self, offset) -> str:
        return c_char_p(addressof(self.heap) + offset).value.decode('utf-8')

    def _local_to_string(self, addr):
        return self.plugin._get_data_string(addr)

    def _local_to_char(self, addr):
        return self.plugin._get_data_char(addr)

    def _sp_ctof(self, val: cell) -> float:
        """Cast a cell to a float"""
        return ctypes.cast(pointer(val), POINTER(c_float)).contents.value

    def _sp_ftoc(self, val: float) -> cell:
        """Shove a float into a cell"""
        return cell(struct.unpack('<L', struct.pack('<f', val))[0])

    ###

    def _instr(self):
        return self._getcodecell()

    def _getparam(self, *, peek: bool = False):
        param = self._getcodecell(peek=peek)
        return param

    def _getparam_op(self):
        param = self.instr & 0xffff
        return param

    def _skipparam(self, n=1):
        for x in range(n):
            self._getparam()

    def _popparam(self):
        param = self._pop()
        return param

    def _popparam_float(self):
        param = self._popparam()
        param = self._sp_ctof(cell(param))
        return param

    ###

    def _push(self, value):
        """Pushes a cell onto the stack"""
        self.STK -= sizeof(cell)
        val = cell(value)
        self._writeheap(self.STK, val)
        self._stack.append((self.STK, val))

    def _pop(self):
        v = self._peek()
        self.STK += sizeof(cell)
        self._stack.pop()
        return v

    def _peek(self):
        return self._getheapcell(self.STK)

    def _filter_stack(self, new_stk):
        self._stack = [(addr, value) for addr, value in self._stack if addr >= new_stk]

    def _stack_set(self, set_addr, set_val):
        """
        When writing directly to the stack, instead of popping and pushing, we
        need to manually find and update values.
        """
        index = None
        for i, (addr, val) in enumerate(self._stack):
            if set_addr == addr:
                index = i
                break

        if index is not None:
            self._stack[index] = (set_addr, set_val)

    ###

    def _write(self, addr, value):
        memmove(addr, pointer(value), sizeof(value))

    def _writestack(self, value):
        self._writeheap(self.STK, value)

    def _writeheap(self, offset, value):
        self._write(addressof(self.heap) + offset, value)

    ###

    def _nativecall(self, index, paramoffs):
        try:
            native = tuple(self.plugin.natives.values())[index]
        except IndexError:
            raise SourcePawnPluginNativeError(
                'Invalid native index %d' % index)

        pyfunc = self.sm_natives.get_native(native.name)
        if pyfunc is None:
            raise NotImplementedError('Native %s not implemented, yet' %
                                      native.name)

        params = ctypes.cast(self.heap, POINTER(cell))
        params_ptr = ctypes.cast(pointer(params), POINTER(c_void_p))
        params_ptr.contents.value += paramoffs

        return pyfunc(params)

    def _pubcall(self, func_id):
        if not func_id & 1:
            raise SourcePawnPluginError(
                'Invalid public function ID %d' % func_id)

        index = func_id >> 1

        try:
            # TODO(zk): store publics by index, as well
            func = tuple(self.plugin.publics.values())[index]
        except IndexError:
            raise SourcePawnPluginError(
                'Invalid public function index %d' % index)

        return self._execute(func.code_offs)

    def _execute(self, code_offs):
        if not self.initialized:
            self.init()

        self.halted = False
        self.CIP = code_offs
        while not self.halted and self.CIP < self.plugin.pcode.size:
            self._step()

        rval = self.runtime.amx.PRI

        # Peer into debugging symbols to interpret return value as native Python type
        func = self.plugin.debug.symbols_by_addr.get(code_offs)
        if func:
            parsed_rval = func.parse_value(rval, self)
            if parsed_rval is not None:
                rval = parsed_rval

        return rval

    def _step(self):
        self.instr_addr = self.CIP
        c = self._instr()
        self.instr = c
        op = c & ((1 << sizeof(cell)*4)-1)

        instr = opcodes[op]
        params = instr.read_params(self)

        exec_entry = (self.instr_addr, instr, tuple(params), None)
        self._executed.append(exec_entry)

        op_handler = getattr(self.instructions, instr.method, None)
        if not op_handler:
            ######################
            # TODO: handle this intentionally
            logger.info(opcodes[op])
            return

        rval = None
        try:
            rval = op_handler(self, *params)
        finally:
            if rval is not None:
                self._executed[-1] = exec_entry[:-1] + (rval,)

            if self.runtime.spew:
                formatted_params = instr.format_params(self, params)
                spew_line = f'0x{self.instr_addr:08x}: {instr.name} {", ".join(formatted_params)}'

                # TODO(zk): use logger?
                if rval is not None:
                    if isinstance(rval, int):
                        rval = f'{hex(rval):>10} ({rval})'
                    spew_line = f'{spew_line:<70}-> {rval}'

                if self.runtime.spew_stack:
                    stk = [f'[{hex(addr)}/{hex(self.STK-addr)}] {hex(value.value)}' for addr, value in self._stack]
                    spew_line = f'{spew_line:<100} STK: {", ".join(stk)}'

                print(spew_line)


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


def _new_callable_params() -> List[ParamInfo]:
    return [ParamInfo() for _ in range(SP_MAX_EXEC_PARAMS)]


class PluginFunction(ICallable):
    def __init__(self, runtime: SourcePawnPluginRuntime, func_id: int, code_offs: int):
        self.runtime: SourcePawnPluginRuntime = runtime
        self.func_id = func_id
        self.code_offs = code_offs

        self.rtti_method = self.runtime.plugin.rtti_methods_by_addr[code_offs]
        self.rtti_args = self.rtti_method.rtti.args

        #: Holds arguments for the current invocation
        self._params: List[ParamInfo] = []

    def __call__(self, *args):
        call_rval, did_succeed = self.call(*args)
        return call_rval.rval

    def call(self, *args):
        if not self.runtime.amx.initialized:
            self.runtime.amx.init()

        self._params = []

        for i, arg in enumerate(args):
            if i >= len(self.rtti_args):
                if self.rtti_args[-1].is_variadic:
                    rtti_arg = self.rtti_args[-1]
                else:
                    raise ValueError(f'Expected {len(self.rtti_args)} arguments, got {len(args)}')
            else:
                rtti_arg = self.rtti_args[i]

            if isinstance(arg, (int, bool, float)):
                if rtti_arg.is_by_ref:
                    # XXX(zk): are there any cases we *don't* want to copy back?
                    self.push_cell_by_ref(arg, ParamCopyFlag.COPYBACK)
                else:
                    self.push_cell(arg)

            elif isinstance(arg, (str, bytes)):
                if rtti_arg.is_by_ref:
                    string_flags = ParamStringFlag.UTF8 if isinstance(arg, str) else ParamStringFlag.BINARY
                    string_flags |= ParamStringFlag.COPY
                    self.push_string_ex(arg, len(arg), string_flags, ParamCopyFlag.COPYBACK)
                else:
                    self.push_string(arg)

            else:
                try:
                    arg_iter = iter(arg)
                except TypeError:
                    raise TypeError(f'Invalid argument type {type(arg)}: {arg!r}')

                arg = list(arg_iter)
                if rtti_arg.is_by_ref:
                    self.push_array(arg, ParamCopyFlag.COPYBACK)
                else:
                    self.push_array(arg)

        return self.invoke()

    def _add_param(self) -> ParamInfo:
        if len(self._params) >= SP_MAX_EXEC_PARAMS:
            raise ValueError(f'Cannot add more than {SP_MAX_EXEC_PARAMS} parameters')

        param = ParamInfo()
        self._params.append(param)
        return param

    def push_cell(self, value: int):
        param = self._add_param()
        param.value = value
        param.marked = False
        return param

    def push_cell_by_ref(self, value: int, flags: ParamCopyFlag = 0):
        param = self.push_array([value], flags)
        param.is_scalar = True
        return param

    def push_float(self, value: float):
        return self.push_cell(typing.cast(int, value))

    def push_float_by_ref(self, value: float, flags: ParamCopyFlag = 0):
        return self.push_cell_by_ref(typing.cast(int, value), flags)

    def push_array(self, value: List[int | float] | None, flags: ParamCopyFlag = 0):
        param = self._add_param()
        param.value = value
        param.is_scalar = False
        param.marked = True
        param.size = len(value) if value is not None else 0
        param.flags = flags if value is not None else 0
        param.is_string = False
        return param

    def push_string(self, value: str):
        return self.push_string_ex(value, len(value) + 1, ParamStringFlag.COPY, 0)

    def push_string_ex(self, value: str, length: int, string_flags: ParamStringFlag = 0, copy_flags: ParamCopyFlag = 0):
        param = self._add_param()
        param.value = value
        param.is_scalar = False
        param.marked = True
        param.size = length
        param.flags = copy_flags
        param.is_string = True
        param.string_flags = string_flags
        return param

    def execute(self) -> Tuple[CallableReturnValue | None, int]:
        # TODO(zk): clear pending exceptions

        rval, err = self.invoke()
        if not err:
            # TODO(zk): return exception code
            return None, -1

        # TODO(zk): constant for "no exception"
        return rval, 0

    def invoke(self) -> Tuple[CallableReturnValue | None, bool]:
        # TODO(zk): check runnable
        # TODO(zk): check error state

        # Copy params, allowing reentrancy (calls within calls, yo)
        params = deepcopy(self._params)

        args: List[int] = []
        for param in params:
            # Is this marked as an array?
            if param.marked:
                if not param.is_string:
                    # Allocate a normal/generic array
                    param.local_addr, param.phys_addr = self.runtime.heap_alloc(param.size)
                    if param.value is not None:
                        values = [convert_return_value(v) for v in param.value]
                        array = (cell * len(values))(*values)
                        self.runtime.amx._writeheap(param.local_addr, array)

                else:  # is_string
                    num_cells = (param.size + sizeof(cell) - 1) // sizeof(cell)
                    param.local_addr, param.phys_addr = self.runtime.heap_alloc(num_cells)

                    if param.string_flags & ParamStringFlag.COPY and param.value is not None:
                        # TODO(zk): forego these flags for PluginFunction
                        if param.string_flags & ParamStringFlag.UTF8:
                            assert isinstance(param.value, str)
                            value = param.value.encode('utf-8')
                        elif param.string_flags & ParamStringFlag.BINARY:
                            assert isinstance(param.value, bytes)
                            value = param.value
                        else:
                            assert isinstance(param.value, str)
                            value = param.value.encode('latin-1')
                        buf = WritableString(self.runtime.amx, param.local_addr, param.size)
                        buf.write(value)

                args.append(param.local_addr)

            else:  # not array
                args.append(convert_return_value(param.value))

        # TODO(zk): handle exception states
        rval = self._call(args)

        out_args_rev: List[ParamValueT | None] = []
        for i, param in reversed(tuple(enumerate(params))):
            if not param.marked:
                out_args_rev.append(param.value)
                continue

            if i < len(self.rtti_args):
                rtti_arg = self.rtti_args[i]
            elif self.rtti_args[-1].is_variadic:
                rtti_arg = self.rtti_args[-1]
            else:
                # Default cell type
                rtti_arg = RTTI(self.runtime.plugin, type=RTTIControlByte.ANY)

            if param.flags & ParamCopyFlag.COPYBACK:
                if param.is_string:
                    out_args_rev.append(rtti_arg.interpret_value(param.local_addr, self.runtime.amx))
                elif param.is_scalar:
                    val = self.runtime.amx._getheapcell(param.local_addr)
                    out_args_rev.append(rtti_arg.interpret_value(val, self.runtime.amx))
                else:
                    cells = self.runtime.amx._getheap(param.local_addr, (cell * param.size))
                    values = [rtti_arg.interpret_value(c.value, self.runtime.amx) for c in cells]
                    out_args_rev.append(values)

            self.runtime.heap_pop(param.local_addr)

        call_rval = CallableReturnValue(rval, out_args_rev[::-1])
        return call_rval, True

    def _call(self, args: List[int]) -> Any:
        if not self.runtime.amx.initialized:
            self.runtime.amx.init()

        # Save current runtime state
        prev_stk = self.runtime.amx.STK
        prev_hea = self.runtime.amx.HEA
        prev_frm = self.runtime.amx.FRM
        prev_hp_scope = self.runtime.amx._hp_scope
        prev_cip = self.runtime.amx.CIP

        # CODE 0 always seems to be a HALT instruction,
        # so when we RETN, we'll halt.
        self.runtime.amx.CIP = 0

        self.runtime.amx._push(len(args))
        for arg in reversed(args):
            self.runtime.amx._push(arg)

        # Abide by calling conventions
        self.runtime.amx.instructions.call(self.runtime.amx, self.code_offs)

        # Execute the function body
        rval = self.runtime.amx._execute(self.code_offs)

        # Restore the previous runtime state
        self.runtime.amx.STK = prev_stk
        self.runtime.amx.HEA = prev_hea
        self.runtime.amx.FRM = prev_frm
        self.runtime.amx._hp_scope = prev_hp_scope
        self.runtime.amx.CIP = prev_cip

        return rval


class SourcePawnPluginRuntime:
    """Executes SourcePawn plug-ins"""

    def __init__(
        self,
        plugin: SourcePawnPlugin,
        *,
        spew: bool = False,
        spew_stack: bool = False,
        root_path: str | Path | None = None
    ):
        """
        :param plugin:
            Plug-in object to envelop a runtime context around

        :param spew:
            Whether to print out traces of instructions as they are executed

        :param spew_stack:
            If spew=True, whether to print out the stack as each instruction is executed
        """
        self.plugin = plugin
        self.spew = spew
        self.spew_stack = spew_stack
        self.root_path = Path(root_path or '.').resolve()

        self.amx = SourcePawnAbstractMachine(self, self.plugin)

        self.pubfuncs: Dict[str, PluginFunction] = {}

        self.last_tick = None

        # Saves all the lines printed to the server console
        self.console: List[Tuple[datetime, str]] = []
        self.console_redirect = sys.stdout

    def printf(self, msg) -> None:
        self.console.append((datetime.now(), msg))
        if self.console_redirect is not None:
            print(msg, file=self.console_redirect)

    def get_console_output(self) -> str:
        return '\n'.join(msg for time, msg in self.console)

    def get_console_lines(self) -> List[str]:
        return [msg for time, msg in self.console]

    def get_function_by_name(self, name: str) -> PluginFunction | None:
        if name in self.pubfuncs:
            return self.pubfuncs[name]

        pub = None
        if name in self.plugin.publics:
            pub = self.plugin.publics[name]
        elif name in self.plugin.inlines:
            pub = self.plugin.inlines[name]

        if pub:
            func = PluginFunction(self, pub.funcid, pub.code_offs)
            self.pubfuncs[name] = func
            return func

        return None

    def call_function_by_name(self, name: str, *args, **kwargs) -> Any:
        func = self.get_function_by_name(name)
        if not func:
            raise NameError('"%s" is not a valid public function name' % name)
        return func(*args, **kwargs)

    def call_function(self, pubindex, *args) -> None:
        # CODE 0 always seems to be a HALT instruction.
        return_addr = 0
        self.amx._push(return_addr)

        for arg in args:
            self.amx._push(arg)
        self.amx._push(len(args))

        self.amx._pubcall(pubindex)

    def run(self, main: str = 'OnPluginStart') -> Any:
        """Executes the plugin's main function"""
        self.amx.init()
        self.amx.smsys.tick()

        rval = self.call_function_by_name(main)

        self.amx.smsys.timers.poll_for_timers()
        return rval

    def heap_alloc(self, num_cells: int) -> Tuple[int, int]:
        """Allocates a bounded block of memory on the secondary stack of a plugin

        Note that although called a heap, it is in fact a stack.

        :param num_cells:
            Number of cells to allocate

        :return:
            A tuple of (local_addr, phys_addr), where local_addr is the heap offset
            used to deallocate the memory, and phys_addr is the physical address
            where values may be written to

        """
        num_bytes = num_cells * sizeof(cell)

        # TODO(zk): check stack margin

        bounds_addr = self.amx.HEA
        self.amx._writeheap(bounds_addr, cell(num_cells))
        self.amx.HEA += sizeof(cell)
        local_addr = self.amx.HEA
        phys_addr = addressof(self.amx.heap) + self.amx.HEA

        self.amx.HEA += num_bytes

        return local_addr, phys_addr

    def heap_pop(self, local_addr: int) -> None:
        """Pops a heap address off the heap/secondary stack

        Use this to free memory allocated with heap_alloc()

        Note that in SourcePawn, the heap is in fact a bottom-up stack.
        Deallocations with this method should be performed in precisely the REVERSE order.
        """
        bounds_addr = local_addr - sizeof(cell)
        num_bytes = self.amx._getheapcell(bounds_addr) * sizeof(cell)
        if self.amx.HEA - num_bytes != local_addr:
            # TODO(zk): richer exception, with SM's code (5, SP_ERROR_INVALID_ADDRESS)
            raise RuntimeError('Invalid address')

        self.amx.HEA = bounds_addr
