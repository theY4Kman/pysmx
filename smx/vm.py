from __future__ import annotations

import logging
import struct
import sys
from ctypes import *
from datetime import datetime
from typing import TYPE_CHECKING, List, Any, Dict, TypeVar, Tuple

from smx.definitions import ucell, cell
from smx.exceptions import (
    SourcePawnPluginNativeError,
    SourcePawnPluginError,
)
from smx.opcodes import opcodes
from smx.pawn import SMXInstructions
from smx.sourcemod import SourceModSystem

if TYPE_CHECKING:
    from smx.reader import SourcePawnPlugin

logger = logging.getLogger(__name__)

V = TypeVar('V')


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

        self.data = None  # Actual data section in memory
        self.code = None  # Code section in memory
        self.heap = None

        self.smsys = None           # Our local copy of the SourceMod system emulator
        self.sm_natives = None      # Our local copy of the SourceMod Python natives
        self.instructions = None    # The SMX instructions methods

        # Records the current stack in a list
        # Each item is (data_offset, c_type())
        self._stack = None

        # TODO: tie this to the current frame
        self._executed = None      # The list of instructions executed
        self._instr_params = None  # List of parameters retrieved during the current instruction

        # The current instruction being executed
        self.instr = None
        # Whether code is running (i.e. a halt instruction has not been encountered since execution start)
        self.halted = None

    def init(self):
        self.COD = self.plugin.pcode.pcode
        self.DAT = self.plugin.data

        # TODO(zk): use memoryview to prevent copying
        self.data = self.plugin.base[self.DAT:][:self.plugin.datasize]
        self.code = self.plugin.base[self.COD:][:self.plugin.pcode.size]
        self.heap = (c_byte * (self.plugin.memsize - self.plugin.datasize))()

        self.STP = len(self.heap)
        self.STK = self.STP
        self.FRM = self.STK  # XXX: this is a guess. Is this correct?

        self.smsys = SourceModSystem(self)
        self.sm_natives = self.smsys.natives
        self.instructions = SMXInstructions()

        self._stack = []
        self._executed = []
        self._instr_params = []

        self.instr = 0
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

    def _getheapcell(self, offset):
        heap = cast(self.heap, POINTER(cell))
        heap_ptr = cast(pointer(heap), POINTER(c_void_p))
        heap_ptr.contents.value += offset
        return heap.contents.value

    def _getstackcell(self, offset=0):
        return self._getheapcell(self.STK + offset)

    def _getdatabyte(self, offset):
        return struct.unpack('<b', self.data[offset:offset+sizeof(c_int8)])[0]

    def _getdatashort(self, offset):
        return struct.unpack('<h', self.data[offset:offset+sizeof(c_int16)])[0]

    def _local_to_string(self, addr):
        return self.plugin._get_data_string(addr)

    def _local_to_char(self, addr):
        return self.plugin._get_data_char(addr)

    def _sp_ctof(self, val: cell) -> float:
        """Cast a cell to a float"""
        return cast(pointer(val), POINTER(c_float)).contents.value

    def _sp_ftoc(self, val: float) -> cell:
        """Shove a float into a cell"""
        return cell(struct.unpack('<L', struct.pack('<f', val))[0])

    ###

    def _record_instr_param(self, value: V) -> V:
        self._instr_params.append(value)
        return value

    def _instr(self):
        return self._getcodecell()

    def _getparam(self, *, peek: bool = False, save: bool = True):
        param = self._getcodecell(peek=peek)
        if save:
            self._record_instr_param(param)
        return param

    def _getparam_p(self):
        return self._getparam()

    def _getparam_op(self):
        param = self.instr & 0xffff
        self._record_instr_param(param)
        return param

    def _skipparam(self, n=1):
        for x in range(n):
            self._getparam()

    def _popparam(self, *, save: bool = True):
        param = self._pop()
        if save:
            self._record_instr_param(param)
        return param

    def _popparam_float(self):
        param = self._popparam(save=False)
        param = self._sp_ctof(cell(param))
        self._record_instr_param(param)
        return param

    ###

    def _push(self, value):
        """Pushes a cell onto the stack"""
        self.STK -= sizeof(cell)
        val = cell(value)
        self._writeheap(self.STK, val)
        self._stack.append((self.STK, val))

    def _pop(self):
        v = self._getheapcell(self.STK)
        self.STK += sizeof(cell)
        self._stack.pop()
        return v

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

        params = cast(self.heap, POINTER(cell))
        params_ptr = cast(pointer(params), POINTER(c_void_p))
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
        c = self._instr()
        self.instr = c
        op = c & ((1 << sizeof(cell)*4)-1)

        opname = opcodes[op]
        self._instr_params = []
        self._executed.append((opname, self._instr_params, None, None))

        if hasattr(self.instructions, opname):
            op_handler = getattr(self.instructions, opname)
            op_handler(self)
        else:
            ######################
            # TODO: handle this intentionally
            logger.info(opcodes[op])


class PluginFunction:
    def __init__(self, runtime: SourcePawnPluginRuntime, func_id, code_offs):
        self.runtime: SourcePawnPluginRuntime = runtime
        self.func_id = func_id
        self.code_offs = code_offs

    def __call__(self, *args):
        if not self.runtime.amx.initialized:
            self.runtime.amx.init()

        # CODE 0 always seems to be a HALT instruction.
        return_addr = 0
        self.runtime.amx._push(return_addr)

        # TODO: handle args
        num_args = 0
        self.runtime.amx._push(num_args)

        rval = self.runtime.amx._execute(self.code_offs)
        return rval


class SourcePawnPluginRuntime:
    """Executes SourcePawn plug-ins"""

    def __init__(self, plugin: SourcePawnPlugin):
        """
        :param plugin:
            Plug-in object to envelop a runtime context around
        """
        self.plugin = plugin

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
