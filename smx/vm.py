from __future__ import annotations

import ctypes
import dataclasses
import itertools
import logging
import os.path
import struct
import typing
from contextlib import contextmanager
from ctypes import (
    addressof,
    c_byte,
    c_char_p,
    c_float,
    c_int16,
    c_int8,
    c_uint8,
    c_void_p,
    memmove,
    memset,
    POINTER,
    pointer,
    sizeof,
)
from enum import Enum
from typing import Any, List, NamedTuple, Tuple, Type, TYPE_CHECKING, TypeVar

from smx.compat import hexlify
from smx.definitions import cell, PyCSimpleType, SPCodeFeature, ucell
from smx.errors import SourcePawnErrorCode
from smx.exceptions import SourcePawnPluginError, SourcePawnRuntimeError
from smx.opcodes import opcodes, SourcePawnInstruction
from smx.pawn import SMXInstructions
from smx.sourcemod.system import SourceModSystem

if TYPE_CHECKING:
    from typing import NoReturn

    from smx.plugin import SourcePawnPlugin
    from smx.reader import DbgFile, DbgLine, Native, RTTIMethod
    from smx.runtime import SourcePawnPluginRuntime

logger = logging.getLogger(__name__)

V = TypeVar('V')
CType = TypeVar('CType', bound=PyCSimpleType)


class FrameType(Enum):
    INTERNAL = 0
    SCRIPTED = 1
    NATIVE = 2


@dataclasses.dataclass
class Frame:
    plugin: SourcePawnPlugin
    frm: int
    addr: int | None
    native: Native | None
    return_addr: int

    @property
    def type(self) -> FrameType:
        # XXX(zk): when is the frame type ever INTERNAL?
        if self.native:
            return FrameType.NATIVE
        else:
            return FrameType.SCRIPTED

    def is_scripted_frame(self) -> bool:
        return self.type == FrameType.SCRIPTED

    def is_native_frame(self) -> bool:
        return self.type == FrameType.NATIVE

    def is_internal_frame(self) -> bool:
        return self.type == FrameType.INTERNAL

    @property
    def name(self) -> str | None:
        if self.native:
            return self.native.name

        meth = self.meth
        if meth is not None:
            return meth.name

        return None

    @property
    def meth(self) -> RTTIMethod | None:
        if self.addr:
            return self.plugin.find_method_by_addr(self.addr)

    @property
    def line(self) -> DbgLine | None:
        if self.addr:
            return self.plugin.find_line_by_addr(self.addr)

    @property
    def file(self) -> DbgFile | None:
        if self.addr:
            return self.plugin.find_file_by_addr(self.addr)


class StackValue(NamedTuple):
    addr: int
    value: PyCSimpleType
    frame: Frame


def dump_stack(frames: List[Frame]) -> str:
    """Dump the current stack trace to a string"""
    lines = []
    for i, frame in enumerate(reversed(frames)):
        if frame.is_internal_frame():
            continue

        name = frame.name
        if not name:
            lines.append(f'  [{i}] <unknown>')
            continue

        if frame.is_scripted_frame():
            dbg_file = frame.file
            filename = os.path.basename(dbg_file.name) if dbg_file else '<unknown>'

            dbg_line = frame.line
            assert dbg_line

            desc = f'{filename}::{name}, line {dbg_line.number}'
        else:
            desc = f'{name}()'

        lines.append(f'  [{i}] {desc}')

    return '\n'.join(lines)


@dataclasses.dataclass
class AbsoluteIndirectionVectorData:
    addr: int
    iv_cursor: int
    data_cursor: int
    dims: List[int]


@dataclasses.dataclass
class RelativeIndirectionVectorData:
    addr: int        # array base
    dims: List[int]  # Dimension sizes
    data_offs: int   # Current offset AFTER the indirection vectors (data)


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

        # Stack of frame pointers — one for each nested CALL executed
        self._frames: List[Frame] = []

        # Records the current stack in a list
        # Each item is (data_offset, c_type())
        self._stack: List[StackValue] = []

        # The list of instructions executed
        # TODO: tie this to the current frame
        self._executed: List[Tuple[int, SourcePawnInstruction, Tuple[int, ...], Any]] = []

        # The current instruction being executed
        self.instr = None
        # Address of the current instruction being executed
        self.instr_addr: int = 0
        # The current line being executed, if applicable
        self.instr_line: DbgLine | None = None
        # Whether code is running (i.e. a halt instruction has not been encountered since execution start)
        self.halted = None

        # Stores the runtime exception, if any
        self.exception = None

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
        self._hp_scope = self.HEA
        self.STP = len(self.heap)
        self.STK = self.STP
        self.FRM = self.STK  # XXX: this is a guess. Is this correct?

        self.smsys = SourceModSystem(self, **self.runtime.smsys_options)
        self.sm_natives = self.smsys.natives
        self.instructions = SMXInstructions()

        self._stack = []
        self._executed = []

        self.instr = 0
        self.instr_addr = 0
        self.instr_line = None
        self.halted = False

        self.exception = None

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

    def _getheapchar(self, offset: int) -> int:
        return self._getheap(offset, c_uint8)

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
        self._stack.append(StackValue(self.STK, val, self._cur_frame()))

    def _pop(self):
        v = self._peek()
        self.STK += sizeof(cell)
        self._stack.pop()
        return v

    def _peek(self, offset: int = 0):
        return self._getheapcell(self.STK + offset)

    def _filter_stack(self, new_stk):
        self._stack = [sv for sv in self._stack if sv.addr >= new_stk]

    def _stack_set(self, set_addr, set_val):
        """
        When writing directly to the stack, instead of popping and pushing, we
        need to manually find and update values.
        """
        index = None
        for i, sv in enumerate(self._stack):
            if set_addr == sv.addr:
                index = i
                break

        if index is not None:
            self._stack[index] = StackValue(set_addr, set_val, self._cur_frame())

    ###

    def _push_frame(
        self,
        return_addr: int,
        *,
        addr: int | None = None,
        native: Native | int | None = None,
    ) -> Frame:
        if addr is None and native is None:
            raise ValueError('addr or native must be provided')

        # Save current FRM to stack
        self._push(self.FRM)

        saved_hp_scope = self._enter_heap_scope()
        self._push(saved_hp_scope)

        self.FRM = self.STK
        # TODO: CHKMARGIN

        frame = Frame(
            plugin=self.plugin,
            frm=self.FRM,
            addr=addr,
            native=native,
            return_addr=return_addr,
        )
        self._frames.append(frame)

        return frame

    def _pop_frame(self) -> Frame:
        self.STK = self.FRM

        saved_hp_scope = self._pop()
        self._leave_heap_scope(saved_hp_scope)

        self.FRM = self._pop()
        frame = self._frames.pop()

        return frame

    def _enter_heap_scope(self):
        saved_hp_scope = self._heap_alloc(sizeof(cell))
        self._writeheap(saved_hp_scope, cell(self._hp_scope))
        return saved_hp_scope

    def _leave_heap_scope(self, saved_hp_scope: int | None = None):
        if saved_hp_scope is None:
            saved_hp_scope = self._hp_scope
        self._hp_scope = self._getheapcell(saved_hp_scope)
        self.HEA = saved_hp_scope
        return saved_hp_scope

    @contextmanager
    def _heap_scope(self):
        self._enter_heap_scope()
        try:
            yield
        finally:
            self._leave_heap_scope()

    def _cur_frame(self) -> Frame | None:
        return self._frames[-1] if self._frames else None

    ###

    def _write(self, addr, value):
        memmove(addr, pointer(value), sizeof(value))

    def _writestack(self, value, **kwargs):
        self._writeheap(self.STK, value, **kwargs)

    def _writeheap(self, offset, value, **kwargs):
        addr = self._throw_if_bad_addr(offset, **kwargs)
        self._write(addr, value)

    def _throw_if_bad_addr(self, offset: int, *, is_heap: bool = False) -> int:
        if (
            offset < 0 or
            not is_heap and (self.HEA <= offset < self.STK or offset >= self.STP) or
            is_heap and (offset < self.HEA or offset >= self.STK)
        ):
            # TODO(zk): report actual error code
            raise ValueError(f'Address {offset} is out of bounds')

        return addressof(self.heap) + offset

    ###

    def _heap_alloc(self, amount: int) -> int:
        out = self.HEA
        self.HEA += amount
        return out

    def _generate_array(self, dims: List[int], *, auto_zero: bool) -> int:
        num_cells = dims[0]
        iv_size = 0
        for dim in dims[1:]:
            # TODO(zk): check array too big
            num_cells *= dim
            num_cells += dim
            iv_size *= dim
            iv_size += dim * sizeof(cell)

        num_bytes = num_cells * sizeof(cell)
        base_addr = self._heap_alloc(num_bytes)

        if auto_zero:
            memset(addressof(self.heap) + base_addr + iv_size, 0, num_bytes - iv_size)

        if self.plugin.uses_direct_arrays():
            info = AbsoluteIndirectionVectorData(
                addr=base_addr,
                dims=dims,
                iv_cursor=0,
                data_cursor=iv_size,
            )
            self._gen_absolute_indirection_vectors(info, len(dims) - 1)
            assert info.iv_cursor == iv_size
            assert info.data_cursor == num_bytes
        else:
            offs = self._gen_relative_indirection_vectors(base_addr, dims)
            assert offs == num_cells

        return base_addr

    def _gen_absolute_indirection_vectors(self, info: AbsoluteIndirectionVectorData, dim: int) -> int:
        if dim == 0:
            next_addr = info.data_cursor
            info.data_cursor += info.dims[0] * sizeof(cell)
            return next_addr

        iv_base_offset = info.iv_cursor
        info.iv_cursor += info.dims[dim] * sizeof(cell)

        for i in range(info.dims[dim]):
            next_array_offset = self._gen_absolute_indirection_vectors(info, dim - 1)
            iv_cell = iv_base_offset + i * sizeof(cell)
            next_array_addr = info.addr + next_array_offset
            self._writeheap(info.addr + iv_cell, cell(next_array_addr))

        return iv_base_offset

    def _gen_relative_indirection_vectors(self, base_addr: int, dims: List[int]) -> int:
        info = RelativeIndirectionVectorData(
            addr=base_addr,
            dims=list(reversed(dims)),
            data_offs=0,
        )
        info.data_offs = self._calc_indirection(info, 0)
        self._generate_inner_array_indirection_vectors(info, 0, 0)
        return info.data_offs

    def _calc_indirection(self, info: RelativeIndirectionVectorData, dim: int) -> int:
        size = info.dims[dim]
        if dim < len(info.dims) - 2:
            size += info.dims[dim] * self._calc_indirection(info, dim + 1)
        return size

    def _generate_inner_array_indirection_vectors(
        self,
        info: RelativeIndirectionVectorData,
        dim: int,
        cur_offs: int
    ) -> int:
        write_offs = cur_offs
        cur_offs += info.dims[dim]

        if len(info.dims) > 2 and dim < len(info.dims) - 2:
            for i in range(info.dims[dim]):
                self._writeheap(
                    offset=info.addr + write_offs * sizeof(cell),
                    value=cell((cur_offs - write_offs) * sizeof(cell)),
                )
                write_offs += 1
                cur_offs = self._generate_inner_array_indirection_vectors(info, dim + 1, cur_offs)
        else:
            for i in range(info.dims[dim]):
                self._writeheap(
                    offset=info.addr + write_offs * sizeof(cell),
                    value=cell((info.data_offs - write_offs) * sizeof(cell)),
                )
                write_offs += 1
                info.data_offs += info.dims[dim + 1]

        return cur_offs

    def _heap_alloc_2d_array(self, length: int, stride: int, *, init_addr: int | None = None) -> int:
        array_addr = self._generate_array([stride, length], auto_zero=init_addr is None)

        if init_addr is not None:
            init_phys = addressof(self.heap) + init_addr
            for i in range(length):
                elt_base = self._getheapcell(array_addr + i * sizeof(cell))
                if not self.plugin.uses_direct_arrays():
                    elt_base += array_addr + i * sizeof(cell)

                init_row = (cell * stride).from_address(init_phys + i * stride * sizeof(cell))
                self._writeheap(elt_base, init_row)

        return array_addr

    ###

    @typing.overload
    def report_error(self, code: SourcePawnErrorCode, msg: str | None = None) -> NoReturn: ...

    @typing.overload
    def report_error(self, msg: str) -> NoReturn: ...

    def report_error(self, code_or_msg: SourcePawnErrorCode | str, msg: str | None = None) -> NoReturn:
        assert not self.exception

        if isinstance(code_or_msg, str):
            msg = code_or_msg
            code = SourcePawnErrorCode.USER
        else:
            code = code_or_msg

        if msg is None:
            msg = code.msg

        self.exception = SourcePawnRuntimeError(msg, amx=self, code=code)
        raise self.exception

    def report_out_of_bounds_error(self, addr: int, bounds: int) -> NoReturn:
        if bounds == 0x7fffffff:
            # This is an internal protection against negative indices on arrays with unknown size.
            self.report_error(
                SourcePawnErrorCode.ARRAY_BOUNDS,
                f'Array index out-of-bounds (index {addr})',
            )
        else:
            self.report_error(
                SourcePawnErrorCode.ARRAY_BOUNDS,
                f'Array index out-of-bounds (index {addr}, limit {bounds + 1})',
            )

    def dump_stack(self) -> str:
        """Dump the current stack trace to a string"""
        return dump_stack(self._frames)

    ###

    def _nativecall(self, index: int, paramoffs: int):
        try:
            native = self.plugin.natives[index]
        except IndexError:
            self.report_error(SourcePawnErrorCode.INVALID_NATIVE)
            return

        self._push_frame(0, native=native)
        try:
            pyfunc = self.sm_natives.get_native(native.name)
            if pyfunc is None:
                self.report_error(SourcePawnErrorCode.INVALID_NATIVE)
                return

            params = ctypes.cast(self.heap, POINTER(cell))
            params_ptr = ctypes.cast(pointer(params), POINTER(c_void_p))
            params_ptr.contents.value += paramoffs

            return pyfunc(params)
        finally:
            self._pop_frame()

    def _pubcall(self, func_id):
        if not func_id & 1:
            raise SourcePawnPluginError(
                'Invalid public function ID %d' % func_id)

        index = func_id >> 1

        try:
            # TODO(zk): store publics by index, as well
            func = tuple(self.plugin.publics_by_name.values())[index]
        except IndexError:
            raise SourcePawnPluginError(
                'Invalid public function index %d' % index)

        return self._execute(func.code_offs)

    def _execute(self, code_offs):
        if not self.initialized:
            self.init()

        if self.runtime.spew:
            print(f'\nBeginning execution at {hex(code_offs)}')

        self.halted = False
        self.CIP = code_offs
        while not self.halted and self.CIP < self.plugin.pcode.size:
            self._step()

        rval = self.runtime.amx.PRI

        # Peer into debugging symbols to interpret return value as native Python type
        func = self.plugin.find_symbol_by_addr(code_offs)
        if func:
            parsed_rval = func.parse_value(rval, self)
            if parsed_rval is not None:
                rval = parsed_rval

        return rval

    def _step(self):
        self.instr_addr = self.CIP
        frame = self._cur_frame()
        if frame:
            frame.addr = self.instr_addr

        c = self._instr()
        self.instr = c
        op = c & ((1 << sizeof(cell)*4)-1)

        instr = opcodes[op]
        params = instr.read_params(self)

        exec_entry = (self.instr_addr, instr, tuple(params), None)
        self._executed.append(exec_entry)

        spew_line = ''
        if self.runtime.spew:
            formatted_params = instr.format_params(self, params)
            spew_line = f'{self.instr_addr:05x}: {instr.name} {", ".join(formatted_params)}'
            print(spew_line, end='')

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
                if rval is not None:
                    if isinstance(rval, int):
                        rval = f'{hex(rval):>10} ({rval})'
                    elif isinstance(rval, bytes):
                        rval = hexlify(rval)
                    spew_line = f'{spew_line:<70}-> {rval}'

                if self.runtime.spew_stack:
                    stack_groups = itertools.groupby(self._stack, key=lambda sv: sv.frame)
                    stack_groups_str = []
                    for frame, frame_stack in stack_groups:
                        prefix = ''

                        if frame:
                            stp = frame.frm
                            name = frame.name or hex(frame.frm)
                            prefix = f'{name} - '
                        else:
                            stp = self.STP

                        frame_stack_values = [
                            f'[{hex(sv.addr):>4}/{hex(sv.addr-stp):>4}] {hex(sv.value.value)}'
                            for sv in frame_stack
                        ]
                        stack_groups_str.append(prefix + ', '.join(frame_stack_values))

                    stk = ' || '.join(stack_groups_str)
                    spew_line = f'{spew_line:<100} : {stk}'

                # TODO(zk): use logger?
                print('\r' + spew_line)
