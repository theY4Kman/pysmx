from datetime import datetime
import string
import struct
from ctypes import *
import sys
from .sourcemod import *
from .smxdefs import *
from .opcodes import *


class SourcePawnVerificationError(SourcePawnPluginError):
    pass



class SourcePawnAbstractMachine(object):
    ZERO = cell(0)

    class SMXInstructions(object):
        def load_pri(self, amx):
            offs = amx._getparam()
            amx.PRI = amx._getdatacell(offs)

        def load_alt(self, amx):
            offs = amx._getparam()
            amx.ALT = amx._getdatacell(offs)

        def load_s_pri(self, amx):
            offs = amx._getparam()
            amx.PRI = amx._getdatacell(amx.FRM + offs)

        def load_s_alt(self, amx):
            offs = amx._getparam()
            amx.ALT = amx._getdatacell(amx.FRM + offs)

        def proc(self, amx):
            amx._push(amx.FRM)
            amx.FRM = amx.STK
            # TODO: CHKMARGIN

        def lref_s_pri(self, amx):
            offs = amx._getparam()
            offs = amx._getdatacell(amx.FRM + offs)
            amx.PRI = amx._getdatacell(offs)

        def lref_s_alt(self, amx):
            offs = amx._getparam()
            offs = amx._getdatacell(amx.FRM + offs)
            amx.ALT = amx._getdatacell(offs)

        def load_i(self, amx):
            # TODO: memory checking
            amx.PRI = amx._getdatacell(amx.PRI)

        def lodb_i(self, amx):
            # TODO: memory checking
            offs = amx._getparam()
            if offs == 1:
                amx.PRI = amx._getdatabyte(amx.PRI)
            elif offs == 2:
                amx.PRI = amx._getdatashort(amx.PRI)
            elif offs == 4:
                amx.PRI = amx._getdatacell(amx.PRI)

        def sysreq_n(self, amx):
            offs = amx._getparam()
            val = amx._getparam()
            amx._push(val)
            amx.PRI = amx._nativecall(offs, amx.STK)

        def push_c(self, amx):
            amx._push(amx._getparam())

        def ret(self, amx):
            amx.FRM = amx._pop()
            offs = amx._pop()
            # TODO: verify return address
            amx.CIP = offs

        def retn(self, amx):
            amx.FRM = amx._pop()
            offs = amx._pop()
            # TODO: verify return address
            amx.CIP = offs
            amx.STK += amx._getstackcell() + sizeof(cell)

        def zero_pri(self, amx):
            amx.PRI = 0
        def zero_alt(self, amx):
            amx.ALT = 0

        def zero(self, amx):
            offs = amx._getparam()
            amx._writeheap(offs, amx.ZERO)

        def dbreak(self, amx):
            # TODO
            pass

        def nop(self, amx):
            pass

        def lref_pri(self, amx): raise NotImplementedError
        def lref_alt(self, amx): raise NotImplementedError

        def const_pri(self, amx):
            amx.PRI = amx._getparam()
        def const_alt(self, amx):
            amx.ALT = amx._getparam()

        def addr_pri(self, amx): raise NotImplementedError
        def addr_alt(self, amx): raise NotImplementedError

        def stor_pri(self, amx):
            offs = amx._getparam_p()
            amx._writeheap(offs, cell(amx.PRI))
        def stor_alt(self, amx):
            offs = amx._getparam_p()
            amx._writeheap(offs, cell(amx.ALT))

        def stor_s_pri(self, amx):
            offs = amx._getparam_p()
            amx._writeheap(amx.FRM + offs, cell(amx.PRI))
        def stor_s_alt(self, amx):
            offs = amx._getparam_p()
            amx._writeheap(amx.FRM + offs, cell(amx.ALT))

        def sref_pri(self, amx): raise NotImplementedError
        def sref_alt(self, amx): raise NotImplementedError
        def sref_s_pri(self, amx): raise NotImplementedError
        def sref_s_alt(self, amx): raise NotImplementedError

        def stor_i(self, amx):
            # TODO: verify address
            amx._writeheap(amx.ALT, cell(amx.PRI))

        def strb_i(self, amx): raise NotImplementedError
        def lidx(self, amx): raise NotImplementedError
        def lidx_b(self, amx): raise NotImplementedError
        def idxaddr(self, amx): raise NotImplementedError
        def idxaddr_b(self, amx): raise NotImplementedError
        def align_pri(self, amx): raise NotImplementedError
        def align_alt(self, amx): raise NotImplementedError
        def lctrl(self, amx): raise NotImplementedError
        def sctrl(self, amx): raise NotImplementedError
        def move_pri(self, amx): raise NotImplementedError
        def move_alt(self, amx): raise NotImplementedError
        def xchg(self, amx): raise NotImplementedError

        def push_pri(self, amx):
            amx._push(amx.PRI)
        def push_alt(self, amx):
            amx._push(amx.ALT)

        def push_r(self, amx): raise NotImplementedError
        def push(self, amx): raise NotImplementedError
        def push_s(self, amx): raise NotImplementedError

        def pop_pri(self, amx):
            amx.PRI = amx._pop()
        def pop_alt(self, amx):
            amx.ALT = amx._pop()

        def stack(self, amx): raise NotImplementedError

        def heap(self, amx):
            offs = amx._getparam()
            amx.ALT = amx.HEA
            amx.HEA += offs
            # TODO: CHKMARGIN CHKHEAP

        def call(self, amx):
            amx._push(amx.CIP + sizeof(cell))
            amx.CIP = amx._jumprel(amx.CIP)
            # Update our ASM verification
            amx._verify_jump(amx.CIP, is_call=True)

        def call_pri(self, amx): raise NotImplementedError
        def jump(self, amx): raise NotImplementedError
        def jrel(self, amx): raise NotImplementedError
        def jzer(self, amx): raise NotImplementedError
        def jnz(self, amx): raise NotImplementedError
        def jeq(self, amx): raise NotImplementedError
        def jneq(self, amx): raise NotImplementedError
        def jless(self, amx): raise NotImplementedError
        def jleq(self, amx): raise NotImplementedError
        def jgrtr(self, amx): raise NotImplementedError
        def jgeq(self, amx): raise NotImplementedError
        def jsless(self, amx): raise NotImplementedError
        def jsleq(self, amx): raise NotImplementedError
        def jsgrtr(self, amx): raise NotImplementedError
        def jsgeq(self, amx): raise NotImplementedError
        def shl(self, amx): raise NotImplementedError
        def shr(self, amx): raise NotImplementedError
        def sshr(self, amx): raise NotImplementedError
        def shl_c_pri(self, amx): raise NotImplementedError
        def shl_c_alt(self, amx): raise NotImplementedError
        def shr_c_pri(self, amx): raise NotImplementedError
        def shr_c_alt(self, amx): raise NotImplementedError
        def smul(self, amx): raise NotImplementedError
        def sdiv(self, amx): raise NotImplementedError
        def sdiv_alt(self, amx): raise NotImplementedError
        def umul(self, amx): raise NotImplementedError
        def udiv(self, amx): raise NotImplementedError
        def udiv_alt(self, amx): raise NotImplementedError
        def add(self, amx): raise NotImplementedError
        def sub(self, amx): raise NotImplementedError
        def sub_alt(self, amx): raise NotImplementedError
        def dand(self, amx): raise NotImplementedError
        def dor(self, amx): raise NotImplementedError
        def xor(self, amx): raise NotImplementedError
        def dnot(self, amx): raise NotImplementedError
        def neg(self, amx): raise NotImplementedError
        def invert(self, amx): raise NotImplementedError
        def add_c(self, amx): raise NotImplementedError
        def smul_c(self, amx): raise NotImplementedError
        def zero_s(self, amx): raise NotImplementedError
        def sign_pri(self, amx): raise NotImplementedError
        def sign_alt(self, amx): raise NotImplementedError
        def eq(self, amx): raise NotImplementedError
        def neq(self, amx): raise NotImplementedError
        def less(self, amx): raise NotImplementedError
        def leq(self, amx): raise NotImplementedError
        def grtr(self, amx): raise NotImplementedError
        def geq(self, amx): raise NotImplementedError
        def sless(self, amx): raise NotImplementedError
        def sleq(self, amx): raise NotImplementedError
        def sgrtr(self, amx): raise NotImplementedError
        def sgeq(self, amx): raise NotImplementedError
        def eq_c_pri(self, amx): raise NotImplementedError
        def eq_c_alt(self, amx): raise NotImplementedError
        def inc_pri(self, amx): raise NotImplementedError
        def inc_alt(self, amx): raise NotImplementedError
        def inc(self, amx): raise NotImplementedError
        def inc_s(self, amx): raise NotImplementedError
        def inc_i(self, amx): raise NotImplementedError
        def dec_pri(self, amx): raise NotImplementedError
        def dec_alt(self, amx): raise NotImplementedError
        def dec(self, amx): raise NotImplementedError
        def dec_s(self, amx): raise NotImplementedError
        def dec_i(self, amx): raise NotImplementedError
        def movs(self, amx): raise NotImplementedError
        def cmps(self, amx): raise NotImplementedError
        def fill(self, amx): raise NotImplementedError
        def halt(self, amx):
            offs = amx._getparam()
            amx._halt(offs)
            # TODO

        def bounds(self, amx): raise NotImplementedError
        def sysreq_pri(self, amx): raise NotImplementedError
        def sysreq_c(self, amx): raise NotImplementedError
        def file(self, amx): raise NotImplementedError
        def line(self, amx): raise NotImplementedError
        def symbol(self, amx): raise NotImplementedError
        def srange(self, amx): raise NotImplementedError
        def jump_pri(self, amx): raise NotImplementedError
        def switch_(self, amx): raise NotImplementedError
        def casetbl(self, amx): raise NotImplementedError
        def swap_pri(self, amx): raise NotImplementedError
        def swap_alt(self, amx): raise NotImplementedError
        def push_adr(self, amx): raise NotImplementedError
        def symtag(self, amx): raise NotImplementedError
        def push2_c(self, amx):
            amx._push(amx._getparam())
            amx._push(amx._getparam())

        def push2(self, amx): raise NotImplementedError
        def push2_s(self, amx): raise NotImplementedError
        def push2_adr(self, amx): raise NotImplementedError
        def push3_c(self, amx): raise NotImplementedError
        def push3(self, amx): raise NotImplementedError
        def push3_s(self, amx): raise NotImplementedError
        def push3_adr(self, amx): raise NotImplementedError
        def push4_c(self, amx): raise NotImplementedError
        def push4(self, amx): raise NotImplementedError
        def push4_s(self, amx): raise NotImplementedError
        def push4_adr(self, amx): raise NotImplementedError
        def push5_c(self, amx): raise NotImplementedError
        def push5(self, amx): raise NotImplementedError
        def push5_s(self, amx): raise NotImplementedError
        def push5_adr(self, amx): raise NotImplementedError
        def load_both(self, amx): raise NotImplementedError
        def load_s_both(self, amx): raise NotImplementedError
        def const_(self, amx): raise NotImplementedError
        def const_s(self, amx): raise NotImplementedError
        def sysreq_d(self, amx): raise NotImplementedError
        def sysreq_nd(self, amx): raise NotImplementedError
        def tracker_push_c(self, amx): raise NotImplementedError
        def tracker_pop_setheap(self, amx): raise NotImplementedError
        def genarray(self, amx): raise NotImplementedError
        def genarray_z(self, amx): raise NotImplementedError
        def stradjust_pri(self, amx): raise NotImplementedError
        def stackadjust(self, amx): raise NotImplementedError
        def endproc(self, amx): raise NotImplementedError
        def fabs(self, amx): raise NotImplementedError
        def float_(self, amx): raise NotImplementedError
        def floatadd(self, amx): raise NotImplementedError
        def floatsub(self, amx): raise NotImplementedError
        def floatmul(self, amx): raise NotImplementedError
        def floatdiv(self, amx): raise NotImplementedError
        def rnd_to_nearest(self, amx): raise NotImplementedError
        def rnd_to_floor(self, amx): raise NotImplementedError
        def rnd_to_ceil(self, amx): raise NotImplementedError
        def rnd_to_zero(self, amx): raise NotImplementedError
        def floatcmp(self, amx): raise NotImplementedError


    def __init__(self, runtime, plugin):
        """
        @type   runtime: smx.smxexec.SourcePawnPluginRuntime
        @param  runtime: Runtime of the plug-in this Abstract Machine will run
        @type   plugin: smx.smxreader.SourcePawnPlugin
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

        self.sm_natives = None # Our local copy of the SourceMod Python natives
        self.instructions = None # The SMX instructions methods

        # Records the current stack in a list
        # Each item is (data_offset, c_type())
        self._stack = None

        # Instruction verification (match spcomp -a)
        self._verification = None
        self._func_offs = None  # dict(funcname=code_offs)
        self._to_match = None   # The list of instructions to match
        self._executed = None   # The list of instructions executed
        self._processed = None  # A zipped list of the instructions executed
                                # and expected

        self.halted = None # Whether a halt instruction has been executed

    def init(self):
        self.COD = self.plugin.pcode.pcode
        self.DAT = self.plugin.data

        self.code = buffer(self.plugin.base, self.COD,
                           self.plugin.pcode.size)
        self.heap = (c_byte * (self.plugin.memsize - self.plugin.datasize))()

        self.STP = len(self.heap)
        self.STK = self.STP

        self.sm_natives = SourceModNatives(self)
        self.instructions = self.SMXInstructions()

        self._stack = []

        self.halted = False

        self.initialized = True

    def _cip(self):
        cip = self.CIP
        self.CIP += 4
        return cip

    def _halt(self, offs):
        self.halted = True

    def _jumprel(self, offset):
        """Returns the abs address to jump to"""
        return self._readcodecell(offset)

    def _getcodecell(self, peek=False):
        cip = self._cip() if not peek else self.CIP
        return self._readcodecell(cip)

    def _readcodecell(self, address):
        off = address + 4
        return struct.unpack('<L', self.code[address:off])[0]

    def _getdatacell(self, offset):
        addr = self.plugin.data + offset
        return struct.unpack('<L', self.plugin.base[addr:addr+sizeof(cell)])[0]

    def _getheapcell(self, offset):
        heap = cast(self.heap, POINTER(cell))
        heap_ptr = cast(pointer(heap), POINTER(c_void_p))
        heap_ptr.contents.value += offset
        return heap.contents.value

    def _getstackcell(self, offset=0):
        return self._getheapcell(self.STK + offset)

    def _getdatabyte(self, offset):
        addr = self.plugin.data + offset
        return struct.unpack('<B',
                             self.plugin.base[addr:addr+sizeof(c_uint8)])[0]

    def _getdatashort(self, offset):
        addr = self.plugin.data + offset
        return struct.unpack('<H',
                             self.plugin.base[addr:addr+sizeof(c_uint16)])[0]

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

    def _getparam(self, peek=False):
        param = self._getcodecell(peek)
        if self._verification:
            self._executed[-1][1].append('%x' % param)
        return param
    def _getparam_p(self):
        return self._getparam() >> (sizeof(cell)*4)

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

    def _write(self, addr, value):
        memmove(addr, pointer(value), sizeof(value))
    def _writestack(self, value):
        self._writeheap(self.STK, value)
    def _writeheap(self, offset, value):
        self._write(addressof(self.heap) + offset, value)

    def _nativecall(self, index, paramoffs):
        try:
            native = self.plugin.natives.values()[index-1]
        except IndexError:
            raise SourcePawnPluginNativeError('Invalid native index %d' % index)

        pyfunc = self.sm_natives.get_native(native.name)
        if pyfunc is None:
            raise NotImplementedError('Native %s not implemented, yet' %
                                      native.name)

        params = cast(self.heap, POINTER(cell))
        params_ptr = cast(pointer(params), POINTER(c_void_p))
        params_ptr.contents.value += paramoffs

        pyfunc(params)

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

        self._verification = { '': list() }
        self._func_offs = { }
        self._to_match = list()
        self._executed = list()
        self._processed = list()

        sz_lines = map(string.strip, asm.splitlines())
        lines = list(enumerate(sz_lines, 1))
        lines = filter(lambda l: l[1], lines)
        lines = filter(lambda l: not l[1].startswith(';'), lines)
        proc_name = None
        last_offs = None
        for lineno,line in lines:
            # Lines starting with capital letters are sections, ignore them
            if line[0].isupper():
                if line.startswith('CODE'):
                    offs = line[line.rfind(';')+1:].strip()
                    last_offs = int(offs, 16)
                continue

            spl = line.split(';', 1)
            comment = ''
            if len(spl) > 1:
                comment = spl[1].strip()
            sz_instr = spl[0].strip()

            instr_spl = sz_instr.split(' ')
            args = instr_spl[1:]

            instr = instr_spl[0].replace('.', '_')
            instr = fixes.get(instr, instr)
            if instr == 'proc':
                proc_name = comment
                self._func_offs[last_offs] = proc_name
                if proc_name not in self._verification:
                    self._verification[proc_name] = list()

            elif instr in ('ret', 'retn'):
                proc_name = None

            instr_tuple = (instr, args, sz_instr, lineno)
            self._verification[''].append(instr_tuple)
            if proc_name is not None:
                self._verification[proc_name].append(instr_tuple)

    def _verify_jump(self, address, is_call=False):
        self._processed += zip(self._to_match, self._executed)
        self._executed = list()
        self._to_match = list()

        funcname = self._get_funcname_by_offs(address)
        if funcname is not None:
            self._to_match += self._verification[funcname]
            # The ASM uses labels, so let's fake the label as a param
            if is_call:
                self._processed[-1][1][1].append(funcname)
        else:
            print 'Verification fault:'
            print '  Unrecognized jump to 0x%08x' % address

    def _get_funcname_by_offs(self, code_offs):
        funcname = None
        if code_offs in self.plugin.publics_by_offs:
            funcname = self.plugin.publics_by_offs[code_offs].name
        elif code_offs in self._func_offs:
            funcname = self._func_offs[code_offs]
        return funcname

    def _execute(self, code_offs):
        if not self.initialized:
            self.init()

        if self._verification:
            funcname = self._get_funcname_by_offs(code_offs)
            if funcname is None:
                raise SourcePawnVerificationError(
                    'Could not recognize current function (code_offs: %d)' %
                    code_offs)
            if funcname not in self._verification:
                raise SourcePawnVerificationError(
                    'Function %s not found in ASM source' % funcname)

            self._to_match += self._verification[funcname]

        self.CIP = code_offs
        while not self.halted and self.CIP < self.plugin.pcode.size:
            c = self._instr()
            op = c & ((1 << sizeof(cell)*4)-1)

            if self._verification:
                self._executed.append((opcodes[op], list(), None))

            if hasattr(self.instructions, opcodes[op]):
                getattr(self.instructions, opcodes[op])(self)
            else:
                ######################
                print opcodes[op]

        if self._verification:
            faults = 0
            self._processed += zip(self._to_match, self._executed)
            for expected,actual in self._processed:
                expected_instr = ' '.join((expected[0],) + tuple(expected[1]))
                actual_instr = ' '.join((actual[0],) + tuple(actual[1]))

                if expected_instr != actual_instr:
                    faults += 1
                    print 'Verification fault (ASM line %d):' % expected[3]
                    print '%10s%s' % ('Expected: ', expected_instr)
                    print '%10s%s' % ('Actual: ', actual_instr)
                    print

            print '%d verification fault%s' % (faults, "s"[faults==1:])


class PluginFunction(object):
    def __init__(self, runtime, func_id, code_offs):
        """
        @type   runtime: smx.smxexec.SourcePawnPluginRuntime
        """
        self.runtime = runtime
        self.func_id = func_id
        self.code_offs = code_offs

    def __call__(self, *args, **kwargs):
        self.runtime.amx._execute(self.code_offs)


class SourcePawnPluginRuntime(object):
    """Executes SourcePawn plug-ins"""

    def __init__(self, plugin):
        """
        @type   plugin: smx.smxreader.SourcePawnPlugin
        @param  plugin: Plug-in object to envelop a runtime context around
        """
        self.plugin = plugin

        self.amx = SourcePawnAbstractMachine(self, self.plugin)

        self.pubfuncs = {}

        # Saves all the lines printed to the server console
        self.console = [] # list((datetime, msg_str))
        self.console_redirect = sys.stdout

    def printf(self, msg):
        self.console.append((datetime.now(), msg))
        if self.console_redirect is not None:
            print >> self.console_redirect, msg

    def get_function_by_name(self, name):
        if name in self.pubfuncs:
            return self.pubfuncs[name]

        if name in self.plugin.publics:
            pub = self.plugin.publics[name]
            func = PluginFunction(self, pub.funcid, pub.code_offs)
            self.pubfuncs[name] = func
            return func

        return None

    def run(self, main='OnPluginStart'):
        """Executes the plugin's main function"""
        func = self.get_function_by_name(main)
        func()
