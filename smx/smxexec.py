import struct
from ctypes import *
from .sourcemod import *
from .smxdefs import *
from .opcodes import *


class SourcePawnAbstractMachine(object):
    ZERO = cell(0)

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

    def init(self):
        self.COD = self.plugin.pcode.pcode
        self.DAT = self.plugin.data

        self.code = buffer(self.plugin.base, self.COD,
                           self.plugin.pcode.size)
        self.heap = (c_byte * (self.plugin.memsize - self.plugin.datasize))()

        self.STP = len(self.heap)
        self.STK = self.STP

        self.sm_natives = SourceModNatives(self)

        self.initialized = True

    @property
    def _cip(self):
        cip = self.CIP
        self.CIP += 4
        return cip

    def _getcodecell(self):
        cip = self._cip
        off = cip + 4
        return struct.unpack('<L', self.code[cip:off])[0]

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

    def _instr(self):
        return self._getcodecell()

    def _getparam(self):
        return self._getcodecell()

    def _push(self, value):
        """Pushes a cell onto the stack"""
        self.STK -= sizeof(cell)
        self._writeheap(self.STK, cell(value))

    def _write(self, addr, value):
        memmove(addr, pointer(value), sizeof(value))
    def _writestack(self, value):
        self._writeheap(self.STK, value)
    def _writeheap(self, offset, value):
        self._write(addressof(self.heap) + offset, value)

    def _pop(self):
        v = self._getheapcell(self.STK)
        self.STK += sizeof(cell)
        return v

    def _nativecall(self, index, paramoffs):
        try:
            native = self.plugin.natives.values()[index-1]
        except IndexError:
            raise SourcePawnPluginNativeError('Invalid native index %d' % index)

        pyfunc = getattr(self.sm_natives, native.name, None)
        if pyfunc is None or not callable(pyfunc):
            raise NotImplementedError('Native %s not implemented, yet' %
                                      native.name)

        params = cast(self.heap, POINTER(cell))
        params_ptr = cast(pointer(params), POINTER(c_void_p))
        params_ptr.contents.value += paramoffs

        pyfunc(params)

    def _execute(self, code_offs):
        if not self.initialized:
            self.init()

        self.CIP = code_offs
        while self.CIP < self.plugin.pcode.size:
            c = self._instr()
            op = c & ((1 << sizeof(cell)*4)-1)

            if op == opcodes.load_pri:
                offs = self._getparam()
                self.PRI = self._getdatacell(offs)
            elif op == opcodes.load_alt:
                offs = self._getparam()
                self.ALT = self._getdatacell(offs)
            
            elif op == opcodes.load_s_pri:
                offs = self._getparam()
                self.PRI = self._getdatacell(self.FRM + offs)
            elif op == opcodes.load_s_alt:
                offs = self._getparam()
                self.ALT = self._getdatacell(self.FRM + offs)
            
            elif op == opcodes.lref_pri:
                raise NotImplementedError
            
            elif op == opcodes.lref_alt:
                raise NotImplementedError
            
            elif op == opcodes.lref_s_pri:
                offs = self._getparam()
                offs = self._getdatacell(self.FRM + offs)
                self.PRI = self._getdatacell(offs)
            elif op == opcodes.lref_s_alt:
                offs = self._getparam()
                offs = self._getdatacell(self.FRM + offs)
                self.ALT = self._getdatacell(offs)
            
            elif op == opcodes.load_i:
                # TODO: memory checking
                self.PRI = self._getdatacell(self.PRI)
            
            elif op == opcodes.lodb_i:
                # TODO: memory checking
                offs = self._getparam()
                if offs == 1:
                    self.PRI = self._getdatabyte(self.PRI)
                elif offs == 2:
                    self.PRI = self._getdatashort(self.PRI)
                elif offs == 4:
                    self.PRI = self._getdatacell(self.PRI)
            
            elif op == opcodes.const_pri:
                raise NotImplementedError
            
            elif op == opcodes.const_alt:
                raise NotImplementedError
            
            elif op == opcodes.addr_pri:
                raise NotImplementedError
            
            elif op == opcodes.addr_alt:
                raise NotImplementedError
            
            elif op == opcodes.stor_pri:
                raise NotImplementedError
            
            elif op == opcodes.stor_alt:
                raise NotImplementedError
            
            elif op == opcodes.stor_s_pri:
                raise NotImplementedError
            
            elif op == opcodes.stor_s_alt:
                raise NotImplementedError
            
            elif op == opcodes.sref_pri:
                raise NotImplementedError
            
            elif op == opcodes.sref_alt:
                raise NotImplementedError
            
            elif op == opcodes.sref_s_pri:
                raise NotImplementedError
            
            elif op == opcodes.sref_s_alt:
                raise NotImplementedError
            
            elif op == opcodes.stor_i:
                raise NotImplementedError
            
            elif op == opcodes.strb_i:
                raise NotImplementedError
            
            elif op == opcodes.lidx:
                raise NotImplementedError
            
            elif op == opcodes.lidx_b:
                raise NotImplementedError
            
            elif op == opcodes.idxaddr:
                raise NotImplementedError
            
            elif op == opcodes.idxaddr_b:
                raise NotImplementedError
            
            elif op == opcodes.align_pri:
                raise NotImplementedError
            
            elif op == opcodes.align_alt:
                raise NotImplementedError
            
            elif op == opcodes.lctrl:
                raise NotImplementedError
            
            elif op == opcodes.sctrl:
                raise NotImplementedError
            
            elif op == opcodes.move_pri:
                raise NotImplementedError
            
            elif op == opcodes.move_alt:
                raise NotImplementedError
            
            elif op == opcodes.xchg:
                raise NotImplementedError
            
            elif op == opcodes.push_pri:
                raise NotImplementedError
            
            elif op == opcodes.push_alt:
                raise NotImplementedError
            
            elif op == opcodes.push_r:
                raise NotImplementedError
            
            elif op == opcodes.push_c:
                self._push(self._getparam())
            
            elif op == opcodes.push:
                raise NotImplementedError
            
            elif op == opcodes.push_s:
                raise NotImplementedError
            
            elif op == opcodes.pop_pri:
                raise NotImplementedError
            
            elif op == opcodes.pop_alt:
                raise NotImplementedError
            
            elif op == opcodes.stack:
                raise NotImplementedError
            
            elif op == opcodes.heap:
                raise NotImplementedError
            
            elif op == opcodes.proc:
                self._push(self.FRM)
                self.FRM = self.STK
                # TODO: CHKMARGIN
            
            elif op == opcodes.ret:
                self.FRM = self._pop()
                offs = self._pop()
                # TODO: verify return address
                self.CIP = offs
            
            elif op == opcodes.retn:
                self.FRM = self._pop()
                offs = self._pop()
                # TODO: verify return address
                self.CIP = offs
                self.STK += self._getstackcell() + sizeof(cell)
            
            elif op == opcodes.call:
                raise NotImplementedError
            
            elif op == opcodes.call_pri:
                raise NotImplementedError
            
            elif op == opcodes.jump:
                raise NotImplementedError
            
            elif op == opcodes.jrel:
                raise NotImplementedError
            
            elif op == opcodes.jzer:
                raise NotImplementedError
            
            elif op == opcodes.jnz:
                raise NotImplementedError
            
            elif op == opcodes.jeq:
                raise NotImplementedError
            
            elif op == opcodes.jneq:
                raise NotImplementedError
            
            elif op == opcodes.jless:
                raise NotImplementedError
            
            elif op == opcodes.jleq:
                raise NotImplementedError
            
            elif op == opcodes.jgrtr:
                raise NotImplementedError
            
            elif op == opcodes.jgeq:
                raise NotImplementedError
            
            elif op == opcodes.jsless:
                raise NotImplementedError
            
            elif op == opcodes.jsleq:
                raise NotImplementedError
            
            elif op == opcodes.jsgrtr:
                raise NotImplementedError
            
            elif op == opcodes.jsgeq:
                raise NotImplementedError
            
            elif op == opcodes.shl:
                raise NotImplementedError
            
            elif op == opcodes.shr:
                raise NotImplementedError
            
            elif op == opcodes.sshr:
                raise NotImplementedError
            
            elif op == opcodes.shl_c_pri:
                raise NotImplementedError
            
            elif op == opcodes.shl_c_alt:
                raise NotImplementedError
            
            elif op == opcodes.shr_c_pri:
                raise NotImplementedError
            
            elif op == opcodes.shr_c_alt:
                raise NotImplementedError
            
            elif op == opcodes.smul:
                raise NotImplementedError
            
            elif op == opcodes.sdiv:
                raise NotImplementedError
            
            elif op == opcodes.sdiv_alt:
                raise NotImplementedError
            
            elif op == opcodes.umul:
                raise NotImplementedError
            
            elif op == opcodes.udiv:
                raise NotImplementedError
            
            elif op == opcodes.udiv_alt:
                raise NotImplementedError
            
            elif op == opcodes.add:
                raise NotImplementedError
            
            elif op == opcodes.sub:
                raise NotImplementedError
            
            elif op == opcodes.sub_alt:
                raise NotImplementedError
            
            elif op == getattr(opcodes, 'and'):
                raise NotImplementedError
            
            elif op == getattr(opcodes, 'or'):
                raise NotImplementedError
            
            elif op == opcodes.xor:
                raise NotImplementedError
            
            elif op == getattr(opcodes, 'not'):
                raise NotImplementedError
            
            elif op == opcodes.neg:
                raise NotImplementedError
            
            elif op == opcodes.invert:
                raise NotImplementedError
            
            elif op == opcodes.add_c:
                raise NotImplementedError
            
            elif op == opcodes.smul_c:
                raise NotImplementedError
            
            elif op == opcodes.zero_pri:
                self.PRI = 0
            
            elif op == opcodes.zero_alt:
                self.ALT = 0
            
            elif op == opcodes.zero:
                offs = self._getparam()
                self._writeheap(offs, self.ZERO)
            
            elif op == opcodes.zero_s:
                raise NotImplementedError
            
            elif op == opcodes.sign_pri:
                raise NotImplementedError
            
            elif op == opcodes.sign_alt:
                raise NotImplementedError
            
            elif op == opcodes.eq:
                raise NotImplementedError
            
            elif op == opcodes.neq:
                raise NotImplementedError
            
            elif op == opcodes.less:
                raise NotImplementedError
            
            elif op == opcodes.leq:
                raise NotImplementedError
            
            elif op == opcodes.grtr:
                raise NotImplementedError
            
            elif op == opcodes.geq:
                raise NotImplementedError
            
            elif op == opcodes.sless:
                raise NotImplementedError
            
            elif op == opcodes.sleq:
                raise NotImplementedError
            
            elif op == opcodes.sgrtr:
                raise NotImplementedError
            
            elif op == opcodes.sgeq:
                raise NotImplementedError
            
            elif op == opcodes.eq_c_pri:
                raise NotImplementedError
            
            elif op == opcodes.eq_c_alt:
                raise NotImplementedError
            
            elif op == opcodes.inc_pri:
                raise NotImplementedError
            
            elif op == opcodes.inc_alt:
                raise NotImplementedError
            
            elif op == opcodes.inc:
                raise NotImplementedError
            
            elif op == opcodes.inc_s:
                raise NotImplementedError
            
            elif op == opcodes.inc_i:
                raise NotImplementedError
            
            elif op == opcodes.dec_pri:
                raise NotImplementedError
            
            elif op == opcodes.dec_alt:
                raise NotImplementedError
            
            elif op == opcodes.dec:
                raise NotImplementedError
            
            elif op == opcodes.dec_s:
                raise NotImplementedError
            
            elif op == opcodes.dec_i:
                raise NotImplementedError
            
            elif op == opcodes.movs:
                raise NotImplementedError
            
            elif op == opcodes.cmps:
                raise NotImplementedError
            
            elif op == opcodes.fill:
                raise NotImplementedError
            
            elif op == opcodes.halt:
                raise NotImplementedError
            
            elif op == opcodes.bounds:
                raise NotImplementedError
            
            elif op == opcodes.sysreq_pri:
                raise NotImplementedError
            
            elif op == opcodes.sysreq_c:
                raise NotImplementedError
            
            elif op == opcodes.file:
                raise NotImplementedError
            
            elif op == opcodes.line:
                raise NotImplementedError
            
            elif op == opcodes.symbol:
                raise NotImplementedError
            
            elif op == opcodes.srange:
                raise NotImplementedError
            
            elif op == opcodes.jump_pri:
                raise NotImplementedError
            
            elif op == opcodes.switch_:
                raise NotImplementedError
            
            elif op == opcodes.casetbl:
                raise NotImplementedError
            
            elif op == opcodes.swap_pri:
                raise NotImplementedError
            
            elif op == opcodes.swap_alt:
                raise NotImplementedError
            
            elif op == opcodes.push_adr:
                raise NotImplementedError
            
            elif op == opcodes.nop:
                pass
            
            elif op == opcodes.sysreq_n:
                offs = self._getparam()
                val = self._getparam()
                self._push(val)
                self.PRI = self._nativecall(offs, self.STK)
            
            elif op == opcodes.symtag:
                raise NotImplementedError
            
            elif op == opcodes.dbreak:
                # TODO
                pass
            
            elif op == opcodes.push2_c:
                raise NotImplementedError
            
            elif op == opcodes.push2:
                raise NotImplementedError
            
            elif op == opcodes.push2_s:
                raise NotImplementedError
            
            elif op == opcodes.push2_adr:
                raise NotImplementedError
            
            elif op == opcodes.push3_c:
                raise NotImplementedError
            
            elif op == opcodes.push3:
                raise NotImplementedError
            
            elif op == opcodes.push3_s:
                raise NotImplementedError
            
            elif op == opcodes.push3_adr:
                raise NotImplementedError
            
            elif op == opcodes.push4_c:
                raise NotImplementedError
            
            elif op == opcodes.push4:
                raise NotImplementedError
            
            elif op == opcodes.push4_s:
                raise NotImplementedError
            
            elif op == opcodes.push4_adr:
                raise NotImplementedError
            
            elif op == opcodes.push5_c:
                raise NotImplementedError
            
            elif op == opcodes.push5:
                raise NotImplementedError
            
            elif op == opcodes.push5_s:
                raise NotImplementedError
            
            elif op == opcodes.push5_adr:
                raise NotImplementedError
            
            elif op == opcodes.load_both:
                raise NotImplementedError
            
            elif op == opcodes.load_s_both:
                raise NotImplementedError
            
            elif op == opcodes.const_:
                raise NotImplementedError
            
            elif op == opcodes.const_s:
                raise NotImplementedError
            
            elif op == opcodes.sysreq_d:
                raise NotImplementedError
            
            elif op == opcodes.sysreq_nd:
                raise NotImplementedError
            
            elif op == opcodes.tracker_push_c:
                raise NotImplementedError
            
            elif op == opcodes.tracker_pop_setheap:
                raise NotImplementedError
            
            elif op == opcodes.genarray:
                raise NotImplementedError
            
            elif op == opcodes.genarray_z:
                raise NotImplementedError
            
            elif op == opcodes.stradjust_pri:
                raise NotImplementedError
            
            elif op == opcodes.stackadjust:
                raise NotImplementedError
            
            elif op == opcodes.endproc:
                raise NotImplementedError
            
            elif op == opcodes.fabs:
                raise NotImplementedError
            
            elif op == opcodes.float_:
                raise NotImplementedError
            
            elif op == opcodes.floatadd:
                raise NotImplementedError
            
            elif op == opcodes.floatsub:
                raise NotImplementedError
            
            elif op == opcodes.floatmul:
                raise NotImplementedError
            
            elif op == opcodes.floatdiv:
                raise NotImplementedError
            
            elif op == opcodes.rnd_to_nearest:
                raise NotImplementedError
            
            elif op == opcodes.rnd_to_floor:
                raise NotImplementedError
            
            elif op == opcodes.rnd_to_ceil:
                raise NotImplementedError
            
            elif op == opcodes.rnd_to_zero:
                raise NotImplementedError
            
            elif op == opcodes.floatcmp:
                raise NotImplementedError

            else:
                ######################
                print opcodes[op]


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
