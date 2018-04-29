from __future__ import division

from ctypes import sizeof, c_uint8, c_uint16, c_uint32

from six.moves import xrange

from smx.definitions import cell, ucell
from smx.exceptions import (
    SourcePawnOpcodeNotGenerated,
    SourcePawnOpcodeDeprecated,
    SourcePawnOpcodeNotSupported,
    Done,
)
from smx.struct import cast_value


class SMXInstructions(object):
    def load_pri(self, amx):
        offs = amx._getparam()
        amx.PRI = amx._getdatacell(offs)

    def load_alt(self, amx):
        offs = amx._getparam()
        amx.ALT = amx._getdatacell(offs)

    def load_s_pri(self, amx):
        offs = amx._getparam_p()
        amx.PRI = amx._getheapcell(amx.FRM + offs)

    def load_s_alt(self, amx):
        offs = amx._getparam()
        amx.ALT = amx._getheapcell(amx.FRM + offs)

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

    # Native calls
    def sysreq_n(self, amx):
        native_index = amx._getparam()
        num_params = amx._getparam()
        amx._push(num_params)
        amx.PRI = amx._nativecall(native_index, amx.STK)
        amx.STK += (num_params + 1) * sizeof(cell)  # +1 to remove number of params
        # keep our Python stack in check
        amx._filter_stack(amx.STK)

    def sysreq_c(self, amx):
        native_index = amx._getparam()
        amx._nativecall(native_index, amx.STK)
        # keep our Python stack in check
        amx._filter_stack(amx.STK)

    def call(self, amx):
        amx._push(amx.CIP + sizeof(cell))
        amx.CIP = amx._jumprel(amx.CIP)

    def retn(self, amx):
        amx.FRM = amx._pop()
        return_addr = amx._pop()
        amx.CIP = return_addr  # TODO: verify return address
        num_params = amx._pop()  # XXX: why do this here?

    def proc(self, amx):
        amx._push(amx.FRM)
        amx.FRM = amx.STK
        # TODO: CHKMARGIN

    def endproc(self, amx):
        pass

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

    def lref_pri(self, amx):
        offs = amx._getparam()
        offs = amx._getdatacell(offs)
        amx.PRI = amx._getdatacell(offs)

    def lref_alt(self, amx):
        offs = amx._getparam()
        offs = amx._getdatacell(offs)
        amx.ALT = amx._getdatacell(offs)

    def const_pri(self, amx):
        amx.PRI = amx._getparam()

    def const_alt(self, amx):
        amx.ALT = amx._getparam()

    def addr_pri(self, amx):
        amx.PRI = amx._getparam()
        amx.PRI += amx.FRM

    def addr_alt(self, amx):
        amx.ALT = amx._getparam()
        amx.ALT += amx.FRM

    def stor_pri(self, amx):
        offs = amx._getparam()
        amx._writeheap(offs, cell(amx.PRI))

    def stor_alt(self, amx):
        offs = amx._getparam()
        amx._writeheap(offs, cell(amx.ALT))

    def stor_s_pri(self, amx):
        offs = amx._getparam_p()
        addr = amx.FRM + offs
        val = cell(amx.PRI)
        amx._writeheap(addr, val)
        # Keep our Python stack list updated
        amx._stack_set(addr, val)

    def stor_s_alt(self, amx):
        offs = amx._getparam_p()
        addr = amx.FRM + offs
        val = cell(amx.ALT)
        amx._writeheap(addr, val)
        # Keep our Python stack list updated
        amx._stack_set(addr, val)

    def sref_pri(self, amx):
        offs = amx._getparam()
        offs = amx._getdatacell(offs)
        amx._writeheap(offs, cell(amx.PRI))

    def sref_alt(self, amx):
        offs = amx._getparam()
        offs = amx._getdatacell(offs)
        amx._writeheap(offs, cell(amx.ALT))

    def sref_s_pri(self, amx):
        offs = amx._getparam()
        offs = amx._getdatacell(amx.FRM + offs)
        amx._writeheap(offs, cell(amx.PRI))

    def sref_s_alt(self, amx):
        offs = amx._getparam()
        offs = amx._getdatacell(amx.FRM + offs)
        amx._writeheap(offs, cell(amx.ALT))

    def stor_i(self, amx):
        # TODO: verify address
        amx._writeheap(amx.ALT, cell(amx.PRI))

    def strb_i(self, amx):
        # TODO: memory checking
        number = amx._getparam()
        if number == 1:
            amx._writeheap(amx.ALT, c_uint8(amx.PRI))
        elif number == 2:
            amx._writeheap(amx.ALT, c_uint16(amx.PRI))
        elif number == 4:
            amx._writeheap(amx.ALT, c_uint32(amx.PRI))

    def lidx(self, amx):
        offs = amx.PRI + sizeof(cell) + amx.ALT
        # TODO: verify address
        amx.PRI = amx._getdatacell(offs)

    def lidx_b(self, amx):
        offs = amx._getparam()
        offs = (amx.PRI << offs) + amx.ALT
        # TODO: verify address
        amx.PRI = amx._getdatacell(offs)

    def idxaddr(self, amx):
        amx.PRI = amx.PRI * sizeof(cell) + amx.ALT

    def idxaddr_b(self, amx):
        offs = amx._getparam()
        amx.PRI = (amx.PRI << offs) + amx.ALT

    def move_pri(self, amx):
        amx.PRI = amx.ALT

    def move_alt(self, amx):
        amx.ALT = amx.PRI

    def xchg(self, amx):
        amx.ALT, amx.PRI = amx.PRI, amx.ALT

    def push_pri(self, amx):
        amx._push(amx.PRI)

    def push_alt(self, amx):
        amx._push(amx.ALT)

    def pop_pri(self, amx):
        amx.PRI = amx._pop()

    def pop_alt(self, amx):
        amx.ALT = amx._pop()

    def stack(self, amx):
        offs = amx._getparam()
        amx.ALT = amx.STK
        amx.STK += offs
        # Keep our Python stack list up to date
        amx._filter_stack(amx.STK)
        # TODO: CHKMARGIN CHKHEAP

    def heap(self, amx):
        offs = amx._getparam()
        amx.ALT = amx.HEA
        amx.HEA += offs
        # TODO: CHKMARGIN CHKHEAP

    # Jumps
    def jump(self, amx):
        amx.CIP = amx._jumprel(amx.CIP)

    def jzer(self, amx):
        if amx.PRI == 0:
            amx.CIP = amx._jumprel(amx.CIP)
        else:
            amx._skipparam(label=True)

    def jnz(self, amx):
        if amx.PRI != 0:
            amx.CIP = amx._jumprel(amx.CIP)
        else:
            amx._skipparam(label=True)

    def jeq(self, amx):
        if amx.PRI == amx.ALT:
            amx.CIP = amx._jumprel(amx.CIP)
        else:
            amx._skipparam(label=True)

    def jneq(self, amx):
        if amx.PRI != amx.ALT:
            amx.CIP = amx._jumprel(amx.CIP)
        else:
            amx._skipparam(label=True)

    def jsless(self, amx):
        if amx.PRI < amx.ALT:
            amx.CIP = amx._jumprel(amx.CIP)
        else:
            amx._skipparam(label=True)

    def jsleq(self, amx):
        if amx.PRI <= amx.ALT:
            amx.CIP = amx._jumprel(amx.CIP)
        else:
            amx._skipparam(label=True)

    def jsgrtr(self, amx):
        if amx.PRI > amx.ALT:
            amx.CIP = amx._jumprel(amx.CIP)
        else:
            amx._skipparam(label=True)

    def jsgeq(self, amx):
        if amx.PRI >= amx.ALT:
            amx.CIP = amx._jumprel(amx.CIP)
        else:
            amx._skipparam(label=True)

    # Shifts
    def shl(self, amx):
        amx.PRI <<= amx.ALT

    def shr(self, amx):
        pri = cast_value(ucell, amx.PRI)
        amx.PRI = pri >> amx.ALT

    def sshr(self, amx):
        amx.PRI >>= amx.ALT

    def shl_c_pri(self, amx):
        offs = amx._getparam()
        amx.PRI <<= offs

    def shl_c_alt(self, amx):
        offs = amx._getparam()
        amx.ALT <<= offs

    def shr_c_pri(self, amx):
        offs = amx._getparam()
        amx.PRI >>= offs

    def shr_c_alt(self, amx):
        offs = amx._getparam()
        amx.ALT >>= offs

    # Multiplication
    def smul(self, amx):
        amx.PRI *= amx.ALT

    def smul_c(self, amx):
        offs = amx._getparam()
        amx.PRI *= offs

    # Division
    def sdiv(self, amx):
        if amx.PRI == 0:
            raise ZeroDivisionError

        offs = amx._getparam()
        amx.PRI = amx.PRI / offs
        amx.ALT = amx.PRI % offs

        if amx.ALT != 0 and (amx.AL ^ offs) < 0:
            amx.PRI -= 1
            amx.ALT += offs

    def sdiv_alt(self, amx):
        if amx.PRI == 0:
            raise ZeroDivisionError

        offs = amx._getparam()
        amx.ALT = amx.ALT / offs
        amx.PRI = amx.ALT % offs

        if amx.PRI != 0 and (amx.PRI ^ offs) < 0:
            amx.ALT -= 1
            amx.PRI += offs

    # Bitwise operators
    def dand(self, amx):
        amx.PRI &= amx.ALT

    def dor(self, amx):
        amx.PRI |= amx.ALT

    def xor(self, amx):
        amx.PRI ^= amx.ALT

    def dnot(self, amx):
        amx.PRI = not amx.PRI

    def neg(self, amx):
        amx.PRI = -amx.PRI

    def invert(self, amx):
        amx.PRI = ~amx.PRI

    # Adding
    def add(self, amx):
        amx.PRI += amx.ALT

    def add_c(self, amx):
        value = amx._getparam()
        amx.PRI += value

    # Subtracting
    def sub(self, amx):
        amx.PRI = amx.PRI - amx.ALT

    def sub_alt(self, amx):
        amx.PRI = amx.ALT - amx.PRI

    def zero_s(self, amx):
        offs = amx._getparam()
        amx._writeheap(amx.FRM + offs, cell(0))

    def sign_pri(self, amx):
        """Keeps lower 8 bits, sign extending"""
        amx.PRI = (amx.PRI << 24) >> 24

    def sign_alt(self, amx):
        """Keeps lower 8 bits, sign extending"""
        amx.PRI = (amx.PRI << 24) >> 24

    # Comparisons
    def eq(self, amx):
        amx.PRI = 1 if amx.PRI == amx.ALT else 0

    def neq(self, amx):
        amx.PRI = 1 if amx.PRI != amx.ALT else 0

    def sless(self, amx):
        amx.PRI = 1 if amx.PRI < amx.ALT else 0

    def sleq(self, amx):
        amx.PRI = 1 if amx.PRI <= amx.ALT else 0

    def sgrtr(self, amx):
        amx.PRI = 1 if amx.PRI > amx.ALT else 0

    def sgeq(self, amx):
        amx.PRI = 1 if amx.PRI >= amx.ALT else 0

    def eq_c_pri(self, amx):
        val = amx._getparam()
        amx.PRI = 1 if amx.PRI == val else 0

    def eq_c_alt(self, amx):
        val = amx._getparam()
        amx.PRI = 1 if amx.ALT == val else 0

    # Incrementation
    def inc_pri(self, amx):
        amx.PRI += 1

    def inc_alt(self, amx):
        amx.ALT += 1

    def inc(self, amx):
        offs = cast_value(cell, amx._getparam())
        val = amx._getheapcell(offs)
        amx._writeheap(cell(val + 1))

    def inc_s(self, amx):
        offs = amx._getparam_p()
        addr = amx.FRM + offs
        val = cell(amx._getheapcell(addr) + 1)
        amx._writeheap(addr, val)
        amx._stack_set(addr, val)

    def inc_i(self, amx):
        offs = cast_value(cell, amx.PRI)
        val = amx._getheapcell(offs)
        amx._writeheap(offs, cell(val + 1))

    # Decrementation
    def dec_pri(self, amx):
        amx.PRI -= 1

    def dec_alt(self, amx):
        amx.ALT -= 1

    def dec(self, amx):
        offs = cast_value(cell, amx._getparam())
        val = amx._getheapcell(offs)
        amx._writeheap(cell(val - 1))

    def dec_s(self, amx):
        offs = amx._getparam_p()
        addr = amx.FRM + offs
        val = cell(amx._getheapcell(addr) - 1)
        amx._writeheap(addr, val)
        amx._stack_set(addr, val)

    def dec_i(self, amx):
        offs = cast_value(cell, amx.PRI)
        val = amx._getheapcell(offs)
        amx._writeheap(offs, cell(val - 1))

    def movs(self, amx):
        # TODO: verify addresses
        bytes = amx._getparam()
        amx.heap[amx.ALT:][:bytes] = amx.heap[amx.PRI:][:bytes]

    def fill(self, amx):
        # TODO: verify addresses
        offs = amx._getparam()
        i = amx.ALT
        while offs >= sizeof(cell):
            amx._writeheap(i, cell(amx.PRI))
            i += sizeof(cell)
            offs -= sizeof(cell)

    def halt(self, amx):
        # When the developer calls a plugin function using pysmx, the special
        # return address 0 is used, where the compiler seems to always leave a
        # halt instr.
        param = amx._getparam()
        amx._halt(param)

        # NOTE: it is assumed PRI contains the exit value, which in our case is
        #       the final return value.

    def bounds(self, amx):
        offs = amx._getparam()
        # TODO: verify addresses

    # switch()
    def switch_(self, amx):
        # +1 to skip the CASETBL opcode
        cptr = amx._jumprel(amx.CIP) + sizeof (cell)

        # TODO: assert amx.CIP == OP_CASETBL
        # preset to none-matched case
        amx.CIP = amx._jumprel(cptr + sizeof(cell))

        # number of records in the case table
        i = amx._readcodecell(cptr)

        # Check each case
        while i > 0 and amx._getheapcell(cptr) != amx.PRI:
            i -= 1
            cptr += 2

        if i > 0:
            amx.CIP = amx._jumprel(cptr + 1)  # case found

    def casetbl(self, amx):
        pass

    def swap_pri(self, amx):
        offs = amx._getheapcell(amx.STK)
        amx._writeheap(amx.STK, amx.PRI)
        amx.PRI = offs

    def swap_alt(self, amx):
        offs = amx._getheapcell(amx.STK)
        amx._writeheap(amx.STK, amx.ALT)
        amx.ALT = offs

    def _macro_push_n(self, amx, n):
        for x in xrange(n):
            offs = amx._getparam()
            val = amx._getheapcell(offs)
            amx._push(val)

    def push(self, amx):
        self._macro_push_n(amx, 1)

    def push2(self, amx):
        self._macro_push_n(amx, 2)

    def push3(self, amx):
        self._macro_push_n(amx, 3)

    def push4(self, amx):
        self._macro_push_n(amx, 4)

    def push5(self, amx):
        self._macro_push_n(amx, 5)

    def _macro_push_n_c(self, amx, n):
        for x in xrange(n):
            amx._push(amx._getparam())

    def push_c(self, amx):
        self._macro_push_n_c(amx, 1)

    def push2_c(self, amx):
        self._macro_push_n_c(amx, 2)

    def push3_c(self, amx):
        self._macro_push_n_c(amx, 3)

    def push4_c(self, amx):
        self._macro_push_n_c(amx, 4)

    def push5_c(self, amx):
        self._macro_push_n_c(amx, 5)

    def _macro_push_n_s(self, amx, n):
        for x in xrange(n):
            offs = amx._getparam()
            val = amx._getheapcell(amx.FRM + offs)
            amx._push(val)

    def push_s(self, amx):
        self._macro_push_n_s(amx, 1)

    def push2_s(self, amx):
        self._macro_push_n_s(amx, 2)

    def push3_s(self, amx):
        self._macro_push_n_s(amx, 3)

    def push4_s(self, amx):
        self._macro_push_n_s(amx, 4)

    def push5_s(self, amx):
        self._macro_push_n_s(amx, 5)

    def _macro_push_n_adr(self, amx, n):
        for x in xrange(n):
            offs = amx._getparam()
            amx._push(amx.FRM + offs)

    def push_adr(self, amx):
        self._macro_push_n_adr(amx, 1)

    def push2_adr(self, amx):
        self._macro_push_n_adr(amx, 2)

    def push3_adr(self, amx):
        self._macro_push_n_adr(amx, 3)

    def push4_adr(self, amx):
        self._macro_push_n_adr(amx, 4)

    def push5_adr(self, amx):
        self._macro_push_n_adr(amx, 5)

    def load_both(self, amx):
        offs = amx._getparam()
        amx.PRI = amx._getdatacell(offs)
        offs = amx._getparam()
        amx.ALT = amx._getdatacell(offs)

    def load_s_both(self, amx):
        offs = amx._getparam_p()
        amx.PRI = amx._getheapcell(amx.FRM + offs)
        offs = amx._getparam_p()
        amx.ALT = amx._getheapcell(amx.FRM + offs)

    def const_(self, amx):
        offs = amx._getparam()
        val = amx._getparam()
        amx._writeheap(offs, cell(val))

    def const_s(self, amx):
        offs = amx._getparam()
        val = amx._getparam()
        amx._writeheap(amx.FRM + offs, cell(val))

    def align_pri(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def align_alt(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def lctrl(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def sctrl(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def push_r(self, amx):
        raise SourcePawnOpcodeDeprecated

    def ret(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def call_pri(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def jrel(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def jless(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def jleq(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def jgrtr(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def jgeq(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def umul(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def udiv(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def udiv_alt(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def less(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def leq(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def grtr(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def geq(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def cmps(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def sysreq_pri(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def file(self, amx):
        raise SourcePawnOpcodeDeprecated

    def line(self, amx):
        raise SourcePawnOpcodeDeprecated

    def symbol(self, amx):
        raise SourcePawnOpcodeDeprecated

    def srange(self, amx):
        raise SourcePawnOpcodeDeprecated

    def jump_pri(self, amx):
        raise SourcePawnOpcodeNotGenerated

    def symtag(self, amx):
        raise SourcePawnOpcodeDeprecated

    def sysreq_d(self, amx):
        raise SourcePawnOpcodeNotSupported

    def sysreq_nd(self, amx):
        raise SourcePawnOpcodeNotSupported

    def tracker_push_c(self, amx):
        raise NotImplementedError

    def tracker_pop_setheap(self, amx):
        raise NotImplementedError

    def genarray(self, amx):
        raise NotImplementedError

    def genarray_z(self, amx):
        raise NotImplementedError

    def stradjust_pri(self, amx):
        raise NotImplementedError

    def stackadjust(self, amx):
        raise NotImplementedError

    def fabs(self, amx):
        raise NotImplementedError

    def float_(self, amx):
        raise NotImplementedError

    def floatadd(self, amx):
        raise NotImplementedError

    def floatsub(self, amx):
        raise NotImplementedError

    def floatmul(self, amx):
        raise NotImplementedError

    def floatdiv(self, amx):
        raise NotImplementedError

    def rnd_to_nearest(self, amx):
        raise NotImplementedError

    def rnd_to_floor(self, amx):
        raise NotImplementedError

    def rnd_to_ceil(self, amx):
        raise NotImplementedError

    def rnd_to_zero(self, amx):
        raise NotImplementedError

    def floatcmp(self, amx):
        raise NotImplementedError
