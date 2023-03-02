from __future__ import annotations

import dataclasses
import itertools
from ctypes import addressof, c_uint16, c_uint32, c_uint8, memmove, memset, sizeof
from typing import List, TYPE_CHECKING

from smx.definitions import cell
from smx.errors import SourcePawnErrorCode
from smx.exceptions import SourcePawnOpcodeDeprecated, SourcePawnOpcodeNotGenerated, SourcePawnOpcodeNotSupported

if TYPE_CHECKING:
    from smx.vm import SourcePawnAbstractMachine


class SMXInstructions:
    def load_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI = amx._getheapcell(offs)
        return amx.PRI

    def load_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT = amx._getheapcell(offs)
        return amx.ALT

    def load_s_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI = amx._getheapcell(offs)
        return amx.PRI

    def load_s_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT = amx._getheapcell(offs)
        return amx.ALT

    def lref_s_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getheapcell(offs)
        amx.PRI = amx._getheapcell(ref)
        return amx.PRI

    def lref_s_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getheapcell(offs)
        amx.ALT = amx._getheapcell(ref)
        return amx.ALT

    def load_i(self, amx: SourcePawnAbstractMachine):
        # TODO: memory checking
        amx.PRI = amx._getheapcell(amx.PRI)
        return amx.PRI

    def lodb_i(self, amx: SourcePawnAbstractMachine, num_bytes: int):
        # TODO: memory checking
        if num_bytes == 1:
            amx.PRI = amx._getheapchar(amx.PRI)
        elif num_bytes == 2:
            amx.PRI = amx._getheapshort(amx.PRI)
        elif num_bytes == 4:
            amx.PRI = amx._getheapcell(amx.PRI)

        return amx.PRI

    # Native calls
    def sysreq_n(self, amx: SourcePawnAbstractMachine, native_index: int, num_params: int):
        amx._push(num_params)
        amx.PRI = amx._nativecall(native_index, amx.STK)
        amx.STK += (num_params + 1) * sizeof(cell)  # +1 to remove number of params
        # keep our Python stack in check
        amx._filter_stack(amx.STK)

        return amx.PRI

    def sysreq_c(self, amx: SourcePawnAbstractMachine, native_index: int):
        rval = amx._nativecall(native_index, amx.STK)
        # keep our Python stack in check
        amx._filter_stack(amx.STK)
        return rval

    def call(self, amx: SourcePawnAbstractMachine, addr: int):
        amx._push_frame(addr=addr, return_addr=amx.CIP)
        amx.CIP = addr

    def proc(self, amx: SourcePawnAbstractMachine):
        pass

    def retn(self, amx: SourcePawnAbstractMachine):
        frame = amx._pop_frame()
        amx.CIP = frame.return_addr

        # Remove params
        num_params = amx._pop()
        amx.STK += num_params * sizeof(cell)
        amx._filter_stack(amx.STK)

        return amx.PRI

    def endproc(self, amx: SourcePawnAbstractMachine):
        pass

    def zero_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 0
        return amx.PRI

    def zero_alt(self, amx: SourcePawnAbstractMachine):
        amx.ALT = 0
        return amx.ALT

    def zero(self, amx: SourcePawnAbstractMachine, offs: int):
        amx._writeheap(offs, amx.ZERO)
        return amx.ZERO

    def break_(self, amx: SourcePawnAbstractMachine):
        # TODO
        pass

    def nop(self, amx: SourcePawnAbstractMachine):
        pass

    def lref_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getheapcell(offs)
        amx.PRI = amx._getheapcell(ref)
        return amx.PRI

    def lref_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getheapcell(offs)
        amx.ALT = amx._getheapcell(ref)
        return amx.ALT

    def const_pri(self, amx: SourcePawnAbstractMachine, val: int):
        amx.PRI = val
        return amx.PRI

    def const_alt(self, amx: SourcePawnAbstractMachine, val: int):
        amx.ALT = val
        return amx.ALT

    def addr_pri(self, amx: SourcePawnAbstractMachine, val: int):
        amx.PRI = val
        return amx.PRI

    def addr_alt(self, amx: SourcePawnAbstractMachine, val: int):
        amx.ALT = val
        return amx.ALT

    def stor_pri(self, amx: SourcePawnAbstractMachine, addr: int):
        amx._writeheap(addr, cell(amx.PRI))
        return amx.PRI

    def stor_alt(self, amx: SourcePawnAbstractMachine, addr: int):
        amx._writeheap(addr, cell(amx.ALT))
        return amx.ALT

    def stor_s_pri(self, amx: SourcePawnAbstractMachine, addr: int):
        val = cell(amx.PRI)
        amx._writeheap(addr, val)
        # Keep our Python stack list updated
        amx._stack_set(addr, val)
        return amx.PRI

    def stor_s_alt(self, amx: SourcePawnAbstractMachine, addr: int):
        val = cell(amx.ALT)
        amx._writeheap(addr, val)
        # Keep our Python stack list updated
        amx._stack_set(addr, val)
        return amx.ALT

    def sref_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getheapcell(offs)
        amx._writeheap(ref, cell(amx.PRI))
        return amx.PRI

    def sref_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getheapcell(offs)
        amx._writeheap(ref, cell(amx.ALT))
        return amx.ALT

    def sref_s_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getheapcell(offs)
        amx._writeheap(ref, cell(amx.PRI))
        return amx.PRI

    def sref_s_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getheapcell(offs)
        amx._writeheap(ref, cell(amx.ALT))
        return amx.ALT

    def stor_i(self, amx: SourcePawnAbstractMachine):
        amx._writeheap(amx.ALT, cell(amx.PRI))
        return amx.PRI

    def strb_i(self, amx: SourcePawnAbstractMachine, number: int):
        # TODO: memory checking
        if number == 1:
            amx._writeheap(amx.ALT, c_uint8(amx.PRI))
        elif number == 2:
            amx._writeheap(amx.ALT, c_uint16(amx.PRI))
        elif number == 4:
            amx._writeheap(amx.ALT, c_uint32(amx.PRI))

        return amx.PRI

    def lidx(self, amx: SourcePawnAbstractMachine):
        offs = amx.PRI + sizeof(cell) + amx.ALT
        amx.PRI = amx._getheapcell(offs)
        return amx.PRI

    def lidx_b(self, amx: SourcePawnAbstractMachine, offs: int):
        offs = (amx.PRI << offs) + amx.ALT
        amx.PRI = amx._getheapcell(offs)
        return amx.PRI

    def idxaddr(self, amx: SourcePawnAbstractMachine):
        amx.PRI = amx.PRI * sizeof(cell) + amx.ALT
        return amx.PRI

    def idxaddr_b(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI = (amx.PRI << offs) + amx.ALT
        return amx.PRI

    def move_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI = amx.ALT
        return amx.PRI

    def move_alt(self, amx: SourcePawnAbstractMachine):
        amx.ALT = amx.PRI
        return amx.ALT

    def xchg(self, amx: SourcePawnAbstractMachine):
        amx.ALT, amx.PRI = amx.PRI, amx.ALT
        return amx.PRI, amx.ALT

    def push_pri(self, amx: SourcePawnAbstractMachine):
        amx._push(amx.PRI)
        return amx.PRI

    def push_alt(self, amx: SourcePawnAbstractMachine):
        amx._push(amx.ALT)
        return amx.ALT

    def pop_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI = amx._pop()
        return amx.PRI

    def pop_alt(self, amx: SourcePawnAbstractMachine):
        amx.ALT = amx._pop()
        return amx.ALT

    def stack(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT = amx.STK
        amx.STK += offs
        # Keep our Python stack list up to date
        amx._filter_stack(amx.STK)
        # TODO: CHKMARGIN CHKHEAP
        return amx.ALT

    def heap(self, amx: SourcePawnAbstractMachine, amount: int):
        amx.ALT = amx._heap_alloc(amount)
        # TODO: CHKMARGIN CHKHEAP
        return amx.ALT

    # Jumps
    def jump(self, amx: SourcePawnAbstractMachine, addr: int):
        amx.CIP = addr
        return amx.CIP

    def jzer(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI == 0:
            amx.CIP = addr
            return amx.CIP

    def jnz(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI != 0:
            amx.CIP = addr
            return amx.CIP

    def jeq(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI == amx.ALT:
            amx.CIP = addr
            return amx.CIP

    def jneq(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI != amx.ALT:
            amx.CIP = addr
            return amx.CIP

    def jsless(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI < amx.ALT:
            amx.CIP = addr
            return amx.CIP

    def jsleq(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI <= amx.ALT:
            amx.CIP = addr
            return amx.CIP

    def jsgrtr(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI > amx.ALT:
            amx.CIP = addr
            return amx.CIP

    def jsgeq(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI >= amx.ALT:
            amx.CIP = addr
            return amx.CIP

    # Shifts
    def shl(self, amx: SourcePawnAbstractMachine):
        amx.PRI <<= amx.ALT
        return amx.PRI

    def shr(self, amx: SourcePawnAbstractMachine):
        # NOTE: we must mask 32 bits, or Python will shift an infinite stream of 1s
        amx.PRI = (amx.PRI & 0xffffffff) >> amx.ALT
        return amx.PRI

    def sshr(self, amx: SourcePawnAbstractMachine):
        amx.PRI >>= amx.ALT
        return amx.PRI

    def shl_c_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI <<= offs
        return amx.PRI

    def shl_c_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT <<= offs
        return amx.ALT

    def shr_c_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI >>= offs
        return amx.PRI

    def shr_c_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT >>= offs
        return amx.ALT

    # Multiplication
    def smul(self, amx: SourcePawnAbstractMachine):
        amx.PRI *= amx.ALT
        return amx.PRI

    def smul_c(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI *= offs
        return amx.PRI

    # Division
    def _sdiv(self, amx: SourcePawnAbstractMachine, pri: bool):
        if pri:
            divisor, dividend = amx.ALT, amx.PRI
        else:
            divisor, dividend = amx.PRI, amx.ALT

        if divisor == 0:
            amx.report_error(SourcePawnErrorCode.DIVIDE_BY_ZERO)

        # -INT_MIN / -1 is an overflow.
        if divisor == -1 and dividend == -2147483648:
            amx.report_error(SourcePawnErrorCode.INTEGER_OVERFLOW)

        # NOTE: Python's int division always rounds to floor, but Pawn rounds to zero
        quotient = int(dividend / divisor)
        remainder = dividend - quotient * divisor

        amx.PRI = quotient
        amx.ALT = remainder

    def sdiv(self, amx: SourcePawnAbstractMachine):
        self._sdiv(amx, True)
        return amx.PRI, amx.ALT

    def sdiv_alt(self, amx: SourcePawnAbstractMachine):
        self._sdiv(amx, False)
        return amx.PRI, amx.ALT

    # Bitwise operators
    def and_(self, amx: SourcePawnAbstractMachine):
        amx.PRI &= amx.ALT
        return amx.PRI

    def or_(self, amx: SourcePawnAbstractMachine):
        amx.PRI |= amx.ALT
        return amx.PRI

    def xor(self, amx: SourcePawnAbstractMachine):
        amx.PRI ^= amx.ALT
        return amx.PRI

    def not_(self, amx: SourcePawnAbstractMachine):
        amx.PRI = not amx.PRI
        return amx.PRI

    def neg(self, amx: SourcePawnAbstractMachine):
        amx.PRI = -amx.PRI
        return amx.PRI

    def invert(self, amx: SourcePawnAbstractMachine):
        amx.PRI = ~amx.PRI
        return amx.PRI

    # Adding
    def add(self, amx: SourcePawnAbstractMachine):
        amx.PRI += amx.ALT
        return amx.PRI

    def add_c(self, amx: SourcePawnAbstractMachine, value: int):
        amx.PRI += value
        return amx.PRI

    # Subtracting
    def sub(self, amx: SourcePawnAbstractMachine):
        amx.PRI = amx.PRI - amx.ALT
        return amx.PRI

    def sub_alt(self, amx: SourcePawnAbstractMachine):
        amx.PRI = amx.ALT - amx.PRI
        return amx.PRI

    def zero_s(self, amx: SourcePawnAbstractMachine, offs: int):
        amx._writeheap(offs, cell(0))
        return 0

    def sign_pri(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def sign_alt(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    # Comparisons
    def eq(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI == amx.ALT else 0
        return amx.PRI

    def neq(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI != amx.ALT else 0
        return amx.PRI

    def sless(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI < amx.ALT else 0
        return amx.PRI

    def sleq(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI <= amx.ALT else 0
        return amx.PRI

    def sgrtr(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI > amx.ALT else 0
        return amx.PRI

    def sgeq(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI >= amx.ALT else 0
        return amx.PRI

    def eq_c_pri(self, amx: SourcePawnAbstractMachine, val: int):
        amx.PRI = 1 if amx.PRI == val else 0
        return amx.PRI

    def eq_c_alt(self, amx: SourcePawnAbstractMachine, val: int):
        amx.PRI = 1 if amx.ALT == val else 0
        return amx.PRI

    # Incrementation
    def inc_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI += 1
        return amx.PRI

    def inc_alt(self, amx: SourcePawnAbstractMachine):
        amx.ALT += 1
        return amx.ALT

    def inc(self, amx: SourcePawnAbstractMachine, addr: int):
        val = amx._getheapcell(addr) + 1
        amx._writeheap(addr, cell(val))
        return val

    def inc_s(self, amx: SourcePawnAbstractMachine, addr: int):
        val = amx._getheapcell(addr) + 1
        amx._writeheap(addr, cell(val))
        amx._stack_set(addr, cell(val))
        return val

    def inc_i(self, amx: SourcePawnAbstractMachine):
        # XXX(zk): does PRI need to be interpreted as ucell?
        offs = amx.PRI
        val = amx._getheapcell(offs) + 1
        amx._writeheap(offs, cell(val))
        return val

    # Decrementation
    def dec_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI -= 1
        return amx.PRI

    def dec_alt(self, amx: SourcePawnAbstractMachine):
        amx.ALT -= 1
        return amx.ALT

    def dec(self, amx: SourcePawnAbstractMachine, addr: int):
        val = amx._getheapcell(addr) - 1
        amx._writeheap(addr, cell(val))
        return val

    def dec_s(self, amx: SourcePawnAbstractMachine, addr: int):
        val = cell(amx._getheapcell(addr) - 1)
        amx._writeheap(addr, val)
        amx._stack_set(addr, val)
        return val

    def dec_i(self, amx: SourcePawnAbstractMachine):
        # XXX(zk): does PRI need to be interpreted as ucell?
        offs = amx.PRI
        val = amx._getheapcell(offs) - 1
        amx._writeheap(offs, cell(val))
        return val

    def movs(self, amx: SourcePawnAbstractMachine, num_bytes: int):
        dest = amx._throw_if_bad_addr(amx.ALT)
        source = amx._throw_if_bad_addr(amx.PRI)
        memmove(dest, source, num_bytes)
        return amx.heap[amx.ALT:][:num_bytes]

    def fill(self, amx: SourcePawnAbstractMachine, offs: int):
        i = amx.ALT
        while offs >= sizeof(cell):
            amx._writeheap(i, cell(amx.PRI))
            i += sizeof(cell)
            offs -= sizeof(cell)

    def halt(self, amx: SourcePawnAbstractMachine, param: int):
        # When the developer calls a plugin function using pysmx, the special
        # return address 0 is used, where the compiler seems to always leave a
        # halt instr.
        amx._halt(param)

        # NOTE: it is assumed PRI contains the exit value, which in our case is
        #       the final return value.

    def bounds(self, amx: SourcePawnAbstractMachine, limit: int):
        if amx.PRI & 0xffffffff > limit:
            amx.report_out_of_bounds_error(amx.PRI, limit)

    def switch(self, amx: SourcePawnAbstractMachine, casetbl_addr: int):
        cptr = casetbl_addr + sizeof(cell)  # skip actual instr
        num_cases = amx._readcodecell(cptr)

        cptr += sizeof(cell)
        default_case_addr = amx._readcodecell(cptr)

        # After casetbl's args, all cases are defined
        cptr += sizeof(cell)

        # TODO: assert amx.CIP == OP_CASETBL
        # preset to none-matched case
        amx.CIP = default_case_addr

        # number of records in the case table
        i = num_cases

        # Check each case
        while i > 0 and amx._readcodecell(cptr) != amx.PRI:
            i -= 1
            cptr += sizeof(cell) * 2

        if i > 0:
            amx.CIP = amx._jumprel(cptr + sizeof(cell))  # case found
            return amx.CIP

    def casetbl(self, amx: SourcePawnAbstractMachine, num_cases: int, addr: int):
        pass

    def swap_pri(self, amx: SourcePawnAbstractMachine):
        offs = amx._getheapcell(amx.STK)
        amx._writeheap(amx.STK, cell(amx.PRI))
        amx.PRI = offs
        return amx.PRI

    def swap_alt(self, amx: SourcePawnAbstractMachine):
        offs = amx._getheapcell(amx.STK)
        amx._writeheap(amx.STK, cell(amx.ALT))
        amx.ALT = offs
        return amx.ALT

    def _macro_push_n(self, amx, *offsets):
        values = [amx._getheapcell(offs) for offs in offsets]
        for val in values:
            amx._push(val)
        return values[0] if len(values) == 1 else values

    push = push2 = push3 = push4 = push5 = _macro_push_n
    push_s = push2_s = push3_s = push4_s = push5_s = _macro_push_n

    def _macro_push_n_c(self, amx, *values):
        for val in values:
            amx._push(val)
        return values[0] if len(values) == 1 else values

    push_c = push2_c = push3_c = push4_c = push5_c = _macro_push_n_c

    def _macro_push_n_adr(self, amx, *offsets):
        for offs in offsets:
            amx._push(offs)
        return offsets[0] if len(offsets) == 1 else offsets

    push_adr = push2_adr = push3_adr = push4_adr = push5_adr = _macro_push_n_adr

    def load_both(self, amx: SourcePawnAbstractMachine, pri_offs: int, alt_offs: int):
        amx.PRI = amx._getheapcell(pri_offs)
        amx.ALT = amx._getheapcell(alt_offs)
        return amx.PRI, amx.ALT

    load_s_both = load_both

    def const_(self, amx: SourcePawnAbstractMachine, offs: int, val: int):
        amx._writeheap(offs, cell(val))
        return val

    const_s = const_

    def align_pri(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def align_alt(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def lctrl(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def sctrl(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def push_r(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeDeprecated

    def ret(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def call_pri(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def jrel(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def jless(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def jleq(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def jgrtr(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def jgeq(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def umul(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def udiv(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def udiv_alt(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def less(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def leq(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def grtr(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def geq(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def cmps(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def sysreq_pri(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def file(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeDeprecated

    def line(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeDeprecated

    def symbol(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeDeprecated

    def srange(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeDeprecated

    def jump_pri(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def symtag(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeDeprecated

    def sysreq_d(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotSupported

    def sysreq_nd(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotSupported

    def tracker_push_c(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def tracker_pop_setheap(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def _genarray(self, amx: SourcePawnAbstractMachine, num_dims: int, auto_zero: bool):
        dims = [amx._peek(dim * sizeof(cell)) for dim in range(num_dims)]
        base_addr = amx._generate_array(dims, auto_zero=auto_zero)

        # Pop all but the last argument, which is where the array addr will be stored
        for _ in range(num_dims - 1):
            amx._pop()

        # Output the base address of the array
        amx._writestack(cell(base_addr))
        amx._stack_set(amx.STK, cell(base_addr))

        return base_addr

    def genarray(self, amx: SourcePawnAbstractMachine, num_dims: int):
        return self._genarray(amx, num_dims, False)

    def genarray_z(self, amx: SourcePawnAbstractMachine, num_dims: int):
        return self._genarray(amx, num_dims, True)

    def stradjust_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI = (amx.PRI + sizeof(cell)) << 2
        return amx.PRI

    def stackadjust(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated


    def ldgfn_pri(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def rebase(self, amx: SourcePawnAbstractMachine):
        raise SourcePawnOpcodeNotGenerated

    def _initarray(
        self,
        amx: SourcePawnAbstractMachine,
        pri: bool,
        dat_addr: int,
        iv_size: int,
        data_copy_size: int,
        data_fill_size: int,
        fill_value: int,
    ):
        array_addr = amx.PRI if pri else amx.ALT

        iv_size_bytes = iv_size * sizeof(cell)
        data_copy_size_bytes = data_copy_size * sizeof(cell)

        iv_vec_addr = array_addr
        data_vec_addr = iv_vec_addr + iv_size_bytes

        if iv_size or data_copy_size:
            tpl_iv_vec_addr = dat_addr
            tpl_data_vec_addr = tpl_iv_vec_addr + iv_size_bytes

            tpl_iv_vec = (cell * iv_size).from_buffer_copy(
                amx.data[tpl_iv_vec_addr:tpl_iv_vec_addr + iv_size_bytes]
            )
            for i, offset in enumerate(tpl_iv_vec):
                amx._writeheap(iv_vec_addr + i * sizeof(cell), cell(offset + array_addr))

            tpl_data_vec = (cell * data_copy_size).from_buffer_copy(
                amx.data[tpl_data_vec_addr:tpl_data_vec_addr + data_copy_size_bytes]
            )
            amx._writeheap(data_vec_addr, tpl_data_vec)

        if data_fill_size:
            fill_pos = data_vec_addr + data_copy_size_bytes
            fill_vec_type = cell * data_fill_size
            if fill_value:
                fill_vec = fill_vec_type(*itertools.repeat(cell(fill_value), data_fill_size))
            else:
                fill_vec = fill_vec_type()
            amx._writeheap(fill_pos, fill_vec)

        array = (cell * data_copy_size).from_address(addressof(amx.heap) + data_vec_addr + data_copy_size_bytes)
        return bytes(array)

    def initarray_pri(self, amx: SourcePawnAbstractMachine, *args):
        return self._initarray(amx, True, *args)

    def initarray_alt(self, amx: SourcePawnAbstractMachine, *args):
        return self._initarray(amx, False, *args)

    def heap_save(self, amx: SourcePawnAbstractMachine):
        return amx._enter_heap_scope()

    def heap_restore(self, amx: SourcePawnAbstractMachine):
        return amx._leave_heap_scope()


    def fabs(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def float_(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def floatadd(self, amx: SourcePawnAbstractMachine):
        left = amx._popparam_float()
        right = amx._popparam_float()
        amx.PRI = amx._sp_ftoc(left + right)
        return amx.PRI

    def floatsub(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def floatmul(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def floatdiv(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def round(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def floor(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def ceil(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def round_to_zero(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def floatcmp(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError
