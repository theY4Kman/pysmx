from __future__ import absolute_import, print_function

import logging
import struct
import sys
from ctypes import *
from datetime import datetime

import six
from six.moves import xrange

from smx.definitions import *
from smx.exceptions import (
    SourcePawnVerificationError,
    SourcePawnPluginNativeError,
    SourcePawnPluginError,
)
from smx.opcodes import opcodes
from smx.pawn import SMXInstructions
from smx.sourcemod import SourceModSystem

logger = logging.getLogger(__name__)


def list_pop(lst, index=-1, default=None):
    try:
        return lst.pop(index)
    except IndexError:
        return default


def tohex(val):
    return '%x' % ucell(val).value


class SourcePawnAbstractMachine(object):
    ZERO = cell(0)

    def __init__(self, runtime, plugin):
        """
        @type   runtime: smx.vm.SourcePawnPluginRuntime
        @param  runtime: Runtime of the plug-in this Abstract Machine will run
        @type   plugin: smx.reader.SourcePawnPlugin
        @param  plugin: The plug-in this Abstract Machine will run
        """
        self.initialized = False
        self.runtime = runtime
        self.plugin = plugin

        self.PRI = 0 # primary register (ALU, general purpose)
        self.ALT = 0 # alternate register (general purpose)
        self.FRM = 0 # stack frame pointer, stack-relative memory reads and
                     # writes are relative to the address in this register
        self.CIP = 0 # code instruction pointer
        self.DAT = 0 # offset to the start of the data
        self.COD = 0 # offset to the start of the code
        self.STP = 0 # stack top
        self.STK = 0 # stack index, indicates the current position in the
                     # stack. The stack runs downwards from the STP register
                     # towards zero
        self.HEA = 0 # heap pointer. Dynamically allocated memory comes from
                     # the heap and the HEA register indicates the top of the
                     # heap

        self.data = None # Actual data section in memory
        self.code = None # Code section in memory

        self.smsys = None           # Our local copy of the SourceMod system emulator
        self.sm_natives = None      # Our local copy of the SourceMod Python natives
        self.instructions = None    # The SMX instructions methods

        # Records the current stack in a list
        # Each item is (data_offset, c_type())
        self._stack = None

        # Instruction verification (match spcomp -a)
        self.print_verification = False
        self._verification = None
        self._func_offs = None  # dict(funcname=code_offs)
        self._label_offs = None # dict(labeltitle=code_offs)
        self._offs_to_func = None   # dict(code_offs=funcname)
        self._offs_to_label = None  # dict(code_offs=labeltitle)
        self._label_offs = None # dict(labeltitle=code_offs)
        self._to_match = None   # The list of instructions to match
        # TODO: tie this to the current frame
        self._executed = None   # The list of instructions executed
        self._processed = None  # A zipped list of the instructions executed
                                # and expected

        self.instr = None # The current instruction being executed
        self.halted = None  # Whether code is running (i.e. a halt instruction)
                            # has not been encountered since execution start

    def init(self):
        self.COD = self.plugin.pcode.pcode
        self.DAT = self.plugin.data

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
        # Update our ASM verification
        self._verify_jump(addr)
        return addr

    def _getcodecell(self, peek=False):
        cip = self._cip() if not peek else self.CIP
        return self._readcodecell(cip)

    def _readcodecell(self, address):
        off = address + 4
        return struct.unpack('<l', self.code[address:off])[0]

    def _getdatacell(self, offset):
        addr = self.plugin.data + offset
        return struct.unpack('<l', self.plugin.base[addr:][:sizeof(cell)])[0]

    def _getheapcell(self, offset):
        heap = cast(self.heap, POINTER(cell))
        heap_ptr = cast(pointer(heap), POINTER(c_void_p))
        heap_ptr.contents.value += offset
        return heap.contents.value

    def _getstackcell(self, offset=0):
        return self._getheapcell(self.STK + offset)

    def _getdatabyte(self, offset):
        addr = self.plugin.data + offset
        return struct.unpack('<b',
                             self.plugin.base[addr:addr+sizeof(c_int8)])[0]

    def _getdatashort(self, offset):
        addr = self.plugin.data + offset
        return struct.unpack('<h',
                             self.plugin.base[addr:addr+sizeof(c_int16)])[0]

    def _local_to_string(self, addr):
        return self.plugin._get_data_string(addr)

    def _local_to_char(self, addr):
        return self.plugin._get_data_char(addr)

    def _sp_ctof(self, val):
        """
        Casts a cell to a float
        @type   val: smx.smxdefs.cell
        """
        return cast(pointer(val), POINTER(c_float)).contents.value


    def _instr(self):
        return self._getcodecell()

    def _getparam(self, peek=False, label=False):
        param = self._getcodecell(peek)
        if self._verification:
            self._add_arg(param, label=label)
        return param

    def _getparam_p(self, label=False):
        return self._getparam(label=label)

    def _getparam_op(self, label=False):
        param = self.instr & 0xffff
        if self._verification:
            self._add_arg(param, label=label)
        return param

    def _skipparam(self, n=1, label=False):
        for x in xrange(n):
            # We use _getparam to hit our verification code
            self._getparam(label=label)


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
        # TODO: update _stack to use an OrderedDict
        index = None
        for i,(addr,val) in enumerate(self._stack):
            if set_addr == addr:
                index = i
                break

        if index is not None:
            self._stack[index] = (set_addr, set_val)


    def _write(self, addr, value):
        memmove(addr, pointer(value), sizeof(value))
    def _writestack(self, value):
        self._writeheap(self.STK, value)
    def _writeheap(self, offset, value):
        self._write(addressof(self.heap) + offset, value)


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
            func = self.plugin.publics.values()[index]
        except IndexError:
            raise SourcePawnPluginError(
                'Invalid public function index %d' % index)

        return self._execute(func.code_offs)

    def _verify_asm(self, asm):
        """
        Reads in the output of spcomp -a <source.sp>, and verifies the
        instructions match what's executed exactly.
        """
        # TODO: handle calls
        fixes = {
            'break': 'dbreak',
            'not': 'dnot',
            'or': 'dor',
            'and': 'dand'
        }

        self._verification = {'': []}
        self._func_offs = {}
        self._label_offs = {}
        self._to_match = []
        self._executed = []
        self._processed = []

        sz_lines = map(lambda s: s.strip(), asm.splitlines())
        lines = list(enumerate(sz_lines, 1))
        lines = filter(lambda l: l[1], lines)
        lines = filter(lambda l: not l[1].startswith(';'), lines)

        proc_name = None
        label_name = None

        last_offs = None
        cur_offs = 0
        cur_section = None
        for lineno, line in lines:
            # Lines starting with capital letters are sections, ignore them
            if line[0].isupper():
                cur_section = line.split(' ', 1)[0]
                if line.startswith('CODE'):
                    offs = line[line.rfind(';')+1:].strip()
                    cur_offs = last_offs = int(offs, 16)
                continue

            # Skip dump dummy instructions under DATA sections
            if cur_section == 'DATA':
                continue

            spl = line.split(';', 1)
            comment = ''
            if len(spl) > 1:
                comment = spl[1].strip()
            sz_instr = spl[0].strip()

            instr_spl = sz_instr.split(' ')
            args = instr_spl[1:]
            instr = instr_spl[0]

            if instr.startswith('l.'):
                label_name = instr
                self._label_offs[cur_offs] = label_name
                if label_name not in self._verification:
                    self._verification[label_name] = list()
                continue

            instr = instr.replace('.', '_')
            instr = fixes.get(instr, instr)
            if instr == 'proc':
                proc_name = comment
                self._func_offs[last_offs] = proc_name
                if proc_name not in self._verification:
                    self._verification[proc_name] = list()

            cur_offs += sizeof(cell) * len(instr_spl)

            instr_tuple = (instr, args, sz_instr, lineno)
            self._verification[''].append(instr_tuple)
            if proc_name is not None:
                self._verification[proc_name].append(instr_tuple)
            if label_name is not None:
                self._verification[label_name].append(instr_tuple)

        self._offs_to_label = dict(zip(self._label_offs.values(), self._label_offs.keys()))
        self._offs_to_func = dict(zip(self._func_offs.values(), self._func_offs.keys()))

    def _verify_jump(self, address, no_param=False):
        if not self._verification:
            return

        old_to_match = self._to_match[:1]
        self._to_match = list()

        codename = self._get_funcname_by_offs(address)
        if codename is not None:
            self._to_match = self._verification[codename]
            # The ASM uses labels, so let's fake the label as a param
            if not no_param:
                self._add_arg(codename, label=True)
        elif self.print_verification:
            logger.info('Verification fault:')
            logger.info('  Unrecognized jump to 0x%08x' % address)

        self._processed += zip(old_to_match, self._executed)
        self._executed = list()

    def _asm_alias(self, codename):
        """Takes either a function or label name, and returns the alias used
        in the ASM file."""
        if codename.startswith('l.'):
            return codename[2:]

        try:
            code_offs = int(codename, 16)
            alias = self._get_funcname_by_offs(code_offs)
            if alias is not None:
                if alias.startswith('l.'):
                    return alias[2:]
                return alias

        except ValueError:
            pass

        return codename

    def _add_arg(self, arg, offset=-1, label=False):
        if not isinstance(arg, six.string_types):
            arg = tohex(arg)
        if label:
            arg = self._asm_alias(arg)

        if self._executed:
            self._executed[offset][1].append(arg)
        elif self._processed:
            self._processed[offset][1][1].append(arg)

    def _get_funcname_by_offs(self, code_offs):
        if code_offs in self.plugin.publics_by_offs:
            return self.plugin.publics_by_offs[code_offs].get_function_name()
        elif code_offs in self._func_offs:
            return self._func_offs[code_offs]
        elif code_offs in self._label_offs:
            return self._label_offs[code_offs]

    def _get_offs_by_name(self, name):
        if name in self._offs_to_label:
            return self._offs_to_label[name]
        elif name in self._offs_to_func:
            return self._offs_to_func[name]

    def _execute(self, code_offs, verify_offs=True):
        if not self.initialized:
            self.init()

        if verify_offs and self._verification:
            funcname = self._get_funcname_by_offs(code_offs)
            if funcname is None:
                raise SourcePawnVerificationError(
                    'Could not recognize current function (code_offs: %d)' %
                    code_offs)
            if funcname not in self._verification:
                raise SourcePawnVerificationError(
                    'Function %s not found in ASM source' % funcname)

        self.halted = False
        self.CIP = code_offs
        while not self.halted and self.CIP < self.plugin.pcode.size:
            self._step()

            # Update our processed instructions list
            if self._verification and self._executed:
                matched = list_pop(self._to_match, 0, ())
                executed = self._executed[-1]
                self._processed.append((matched, executed))

        if self._verification:
            faults = 0
            self._processed += zip(self._to_match, self._executed)
            for expected,actual in self._processed:
                if not expected:
                    expected = ('<blank>', '<blank>', '<blank>', -1)
                expected_instr = ' '.join((expected[0],) + tuple(expected[1]))
                actual_instr = ' '.join((actual[0],) + tuple(actual[1]))

                if expected_instr != actual_instr and self.print_verification:
                    faults += 1
                    logger.info('Verification fault (ASM line %d):' % expected[3])
                    logger.info('%10s%s' % ('Expected: ', expected_instr))
                    logger.info('%10s%s' % ('Found: ', actual_instr))
                    print()

            if self.print_verification:
                logger.info('%d verification fault%s' % (faults, "s"[faults==1:]))

        rval = self.runtime.amx.PRI

        # Peer into debugging symbols to interpret return value as native Python type
        func = self.plugin.debug.symbols_by_addr.get(code_offs)
        if func:
            rv_tag = func.tag
            if rv_tag:
                tag_name = func.tag.name
                if tag_name == 'Float':
                    rval = self._sp_ctof(cell(rval))
                elif tag_name == 'bool':
                    rval = bool(rval)
                elif tag_name == 'String':
                    op, args, _, _ = self._executed[-3]
                    assert op == 'stack'
                    assert len(args) == 1
                    size = int(args[0], 0x10)
                    rval = (c_char * size).from_buffer(self.heap, rval).value
                    rval = rval.decode('utf-8')

        return rval

    def _step(self):
        if self._verification:
            codename = self._get_funcname_by_offs(self.CIP)
            if codename is not None:
                self._to_match = self._verification[codename][:]

        c = self._instr()
        self.instr = c
        op = c & ((1 << sizeof(cell)*4)-1)

        opname = opcodes[op]
        self._executed.append((opname, [], None, None))

        if hasattr(self.instructions, opname):
            op_handler = getattr(self.instructions, opname)
            op_handler(self)
        else:
            ######################
            # TODO: handle this intentionally
            logger.info(opcodes[op])


class PluginFunction(object):
    def __init__(self, runtime, func_id, code_offs):
        """
        @type   runtime: smx.vm.SourcePawnPluginRuntime
        """
        self.runtime = runtime
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


class SourcePawnPluginRuntime(object):
    """Executes SourcePawn plug-ins"""

    def __init__(self, plugin):
        """
        @type   plugin: smx.reader.SourcePawnPlugin
        @param  plugin: Plug-in object to envelop a runtime context around
        """
        self.plugin = plugin

        self.amx = SourcePawnAbstractMachine(self, self.plugin)

        self.pubfuncs = {}

        self.last_tick = None

        # Saves all the lines printed to the server console
        self.console = [] # list((datetime, msg_str))
        self.console_redirect = sys.stdout

    def printf(self, msg):
        self.console.append((datetime.now(), msg))
        if self.console_redirect is not None:
            print(msg, file=self.console_redirect)

    def get_console_output(self):
        return '\n'.join(msg for time, msg in self.console)

    def get_function_by_name(self, name):
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

    def call_function_by_name(self, name, *args, **kwargs):
        func = self.get_function_by_name(name)
        if not func:
            raise NameError('"%s" is not a valid public function name' % name)
        return func(*args, **kwargs)

    def call_function(self, pubindex, *args):
        # CODE 0 always seems to be a HALT instruction.
        return_addr = 0
        self.amx._push(return_addr)

        for arg in args:
            self.amx._push(arg)
        self.amx._push(len(args))

        self.amx._pubcall(pubindex)

    def run(self, main='OnPluginStart'):
        """Executes the plugin's main function"""
        self.amx.init()
        self.amx.smsys.tick()

        rval = self.call_function_by_name(main)

        self.amx.smsys.timers.poll_for_timers()
        return rval
