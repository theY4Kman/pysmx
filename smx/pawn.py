from __future__ import annotations

import itertools
from ctypes import c_uint16, c_uint32, c_uint8, sizeof
from typing import TYPE_CHECKING

from smx.definitions import cell, ucell
from smx.exceptions import SourcePawnOpcodeDeprecated, SourcePawnOpcodeNotGenerated, SourcePawnOpcodeNotSupported
from smx.struct import cast_value

if TYPE_CHECKING:
    from smx.vm import SourcePawnAbstractMachine


class SMXInstructions:
    def load_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI = amx._getheapcell(offs)

    def load_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT = amx._getheapcell(offs)

    def load_s_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI = amx._getheapcell(offs)

    def load_s_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT = amx._getheapcell(offs)

    def lref_s_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getdatacell(offs)
        amx.PRI = amx._getdatacell(ref)

    def lref_s_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getdatacell(offs)
        amx.ALT = amx._getdatacell(ref)

    def load_i(self, amx: SourcePawnAbstractMachine):
        # TODO: memory checking
        amx.PRI = amx._getdatacell(amx.PRI)

    def lodb_i(self, amx: SourcePawnAbstractMachine, offs: int):
        # TODO: memory checking
        if offs == 1:
            amx.PRI = amx._getdatabyte(amx.PRI)
        elif offs == 2:
            amx.PRI = amx._getdatashort(amx.PRI)
        elif offs == 4:
            amx.PRI = amx._getdatacell(amx.PRI)

    # Native calls
    def sysreq_n(self, amx: SourcePawnAbstractMachine, native_index: int, num_params: int):
        amx._push(num_params)
        amx.PRI = amx._nativecall(native_index, amx.STK)
        amx.STK += (num_params + 1) * sizeof(cell)  # +1 to remove number of params
        # keep our Python stack in check
        amx._filter_stack(amx.STK)

    def sysreq_c(self, amx: SourcePawnAbstractMachine, native_index: int):
        amx._nativecall(native_index, amx.STK)
        # keep our Python stack in check
        amx._filter_stack(amx.STK)

    def call(self, amx: SourcePawnAbstractMachine, addr: int):
        amx._push(amx.CIP)
        amx.CIP = addr

    def retn(self, amx: SourcePawnAbstractMachine):
        amx.FRM = amx._pop()
        return_addr = amx._pop()
        amx.CIP = return_addr
        num_params = amx._pop()  # XXX: why do this here?

    def proc(self, amx: SourcePawnAbstractMachine):
        amx._push(amx.FRM)
        amx.FRM = amx.STK
        # TODO: CHKMARGIN

    def endproc(self, amx: SourcePawnAbstractMachine):
        pass

    def zero_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 0

    def zero_alt(self, amx: SourcePawnAbstractMachine):
        amx.ALT = 0

    def zero(self, amx: SourcePawnAbstractMachine, offs: int):
        amx._writeheap(offs, amx.ZERO)

    def break_(self, amx: SourcePawnAbstractMachine):
        # TODO
        pass

    def nop(self, amx: SourcePawnAbstractMachine):
        pass

    def lref_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getdatacell(offs)
        amx.PRI = amx._getdatacell(ref)

    def lref_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getdatacell(offs)
        amx.ALT = amx._getdatacell(ref)

    def const_pri(self, amx: SourcePawnAbstractMachine, val: int):
        amx.PRI = val

    def const_alt(self, amx: SourcePawnAbstractMachine, val: int):
        amx.ALT = val

    def addr_pri(self, amx: SourcePawnAbstractMachine, val: int):
        amx.PRI = val

    def addr_alt(self, amx: SourcePawnAbstractMachine, val: int):
        amx.ALT = val

    def stor_pri(self, amx: SourcePawnAbstractMachine, addr: int):
        amx._writeheap(addr, cell(amx.PRI))

    def stor_alt(self, amx: SourcePawnAbstractMachine, addr: int):
        amx._writeheap(addr, cell(amx.ALT))

    def stor_s_pri(self, amx: SourcePawnAbstractMachine, addr: int):
        val = cell(amx.PRI)
        amx._writeheap(addr, val)
        # Keep our Python stack list updated
        amx._stack_set(addr, val)

    def stor_s_alt(self, amx: SourcePawnAbstractMachine, addr: int):
        val = cell(amx.ALT)
        amx._writeheap(addr, val)
        # Keep our Python stack list updated
        amx._stack_set(addr, val)

    def sref_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getdatacell(offs)
        amx._writeheap(ref, cell(amx.PRI))

    def sref_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getdatacell(offs)
        amx._writeheap(ref, cell(amx.ALT))

    def sref_s_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getdatacell(offs)
        amx._writeheap(ref, cell(amx.PRI))

    def sref_s_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        ref = amx._getdatacell(offs)
        amx._writeheap(ref, cell(amx.ALT))

    def stor_i(self, amx: SourcePawnAbstractMachine):
        amx._writeheap(amx.ALT, cell(amx.PRI))

    def strb_i(self, amx: SourcePawnAbstractMachine, number: int):
        # TODO: memory checking
        if number == 1:
            amx._writeheap(amx.ALT, c_uint8(amx.PRI))
        elif number == 2:
            amx._writeheap(amx.ALT, c_uint16(amx.PRI))
        elif number == 4:
            amx._writeheap(amx.ALT, c_uint32(amx.PRI))

    def lidx(self, amx: SourcePawnAbstractMachine):
        offs = amx.PRI + sizeof(cell) + amx.ALT
        amx.PRI = amx._getdatacell(offs)

    def lidx_b(self, amx: SourcePawnAbstractMachine, offs: int):
        offs = (amx.PRI << offs) + amx.ALT
        amx.PRI = amx._getdatacell(offs)

    def idxaddr(self, amx: SourcePawnAbstractMachine):
        amx.PRI = amx.PRI * sizeof(cell) + amx.ALT

    def idxaddr_b(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI = (amx.PRI << offs) + amx.ALT

    def move_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI = amx.ALT

    def move_alt(self, amx: SourcePawnAbstractMachine):
        amx.ALT = amx.PRI

    def xchg(self, amx: SourcePawnAbstractMachine):
        amx.ALT, amx.PRI = amx.PRI, amx.ALT

    def push_pri(self, amx: SourcePawnAbstractMachine):
        amx._push(amx.PRI)

    def push_alt(self, amx: SourcePawnAbstractMachine):
        amx._push(amx.ALT)

    def pop_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI = amx._pop()

    def pop_alt(self, amx: SourcePawnAbstractMachine):
        amx.ALT = amx._pop()

    def stack(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT = amx.STK
        amx.STK += offs
        # Keep our Python stack list up to date
        amx._filter_stack(amx.STK)
        # TODO: CHKMARGIN CHKHEAP

    def heap(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT = amx.HEA
        amx.HEA += offs
        # TODO: CHKMARGIN CHKHEAP

    # Jumps
    def jump(self, amx: SourcePawnAbstractMachine, addr: int):
        amx.CIP = addr

    def jzer(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI == 0:
            amx.CIP = addr

    def jnz(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI != 0:
            amx.CIP = addr

    def jeq(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI == amx.ALT:
            amx.CIP = addr

    def jneq(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI != amx.ALT:
            amx.CIP = addr

    def jsless(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI < amx.ALT:
            amx.CIP = addr

    def jsleq(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI <= amx.ALT:
            amx.CIP = addr

    def jsgrtr(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI > amx.ALT:
            amx.CIP = addr

    def jsgeq(self, amx: SourcePawnAbstractMachine, addr: int):
        if amx.PRI >= amx.ALT:
            amx.CIP = addr

    # Shifts
    def shl(self, amx: SourcePawnAbstractMachine):
        amx.PRI <<= amx.ALT

    def shr(self, amx: SourcePawnAbstractMachine):
        pri = cast_value(ucell, amx.PRI)
        amx.PRI = pri >> amx.ALT

    def sshr(self, amx: SourcePawnAbstractMachine):
        amx.PRI >>= amx.ALT

    def shl_c_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI <<= offs

    def shl_c_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT <<= offs

    def shr_c_pri(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI >>= offs

    def shr_c_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.ALT >>= offs

    # Multiplication
    def smul(self, amx: SourcePawnAbstractMachine):
        amx.PRI *= amx.ALT

    def smul_c(self, amx: SourcePawnAbstractMachine, offs: int):
        amx.PRI *= offs

    # Division
    def sdiv(self, amx: SourcePawnAbstractMachine, offs: int):
        if amx.PRI == 0:
            raise ZeroDivisionError

        amx.PRI = amx.PRI / offs
        amx.ALT = amx.PRI % offs

        if amx.ALT != 0 and (amx.ALT ^ offs) < 0:
            amx.PRI -= 1
            amx.ALT += offs

    def sdiv_alt(self, amx: SourcePawnAbstractMachine, offs: int):
        if amx.PRI == 0:
            raise ZeroDivisionError

        amx.ALT = amx.ALT / offs
        amx.PRI = amx.ALT % offs

        if amx.PRI != 0 and (amx.PRI ^ offs) < 0:
            amx.ALT -= 1
            amx.PRI += offs

    # Bitwise operators
    def and_(self, amx: SourcePawnAbstractMachine):
        amx.PRI &= amx.ALT

    def or_(self, amx: SourcePawnAbstractMachine):
        amx.PRI |= amx.ALT

    def xor(self, amx: SourcePawnAbstractMachine):
        amx.PRI ^= amx.ALT

    def not_(self, amx: SourcePawnAbstractMachine):
        amx.PRI = not amx.PRI

    def neg(self, amx: SourcePawnAbstractMachine):
        amx.PRI = -amx.PRI

    def invert(self, amx: SourcePawnAbstractMachine):
        amx.PRI = ~amx.PRI

    # Adding
    def add(self, amx: SourcePawnAbstractMachine):
        amx.PRI += amx.ALT

    def add_c(self, amx: SourcePawnAbstractMachine, value: int):
        amx.PRI += value

    # Subtracting
    def sub(self, amx: SourcePawnAbstractMachine):
        amx.PRI = amx.PRI - amx.ALT

    def sub_alt(self, amx: SourcePawnAbstractMachine):
        amx.PRI = amx.ALT - amx.PRI

    def zero_s(self, amx: SourcePawnAbstractMachine, offs: int):
        amx._writeheap(offs, cell(0))

    def sign_pri(self, amx: SourcePawnAbstractMachine):
        """Keeps lower 8 bits, sign extending"""
        amx.PRI = (amx.PRI << 24) >> 24

    def sign_alt(self, amx: SourcePawnAbstractMachine):
        """Keeps lower 8 bits, sign extending"""
        amx.PRI = (amx.PRI << 24) >> 24

    # Comparisons
    def eq(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI == amx.ALT else 0

    def neq(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI != amx.ALT else 0

    def sless(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI < amx.ALT else 0

    def sleq(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI <= amx.ALT else 0

    def sgrtr(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI > amx.ALT else 0

    def sgeq(self, amx: SourcePawnAbstractMachine):
        amx.PRI = 1 if amx.PRI >= amx.ALT else 0

    def eq_c_pri(self, amx: SourcePawnAbstractMachine, val: int):
        amx.PRI = 1 if amx.PRI == val else 0

    def eq_c_alt(self, amx: SourcePawnAbstractMachine, val: int):
        amx.PRI = 1 if amx.ALT == val else 0

    # Incrementation
    def inc_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI += 1

    def inc_alt(self, amx: SourcePawnAbstractMachine):
        amx.ALT += 1

    def inc(self, amx: SourcePawnAbstractMachine, addr: int):
        val = amx._getheapcell(addr)
        amx._writeheap(addr, cell(val + 1))

    def inc_s(self, amx: SourcePawnAbstractMachine, addr: int):
        val = cell(amx._getheapcell(addr) + 1)
        amx._writeheap(addr, val)
        amx._stack_set(addr, val)

    def inc_i(self, amx: SourcePawnAbstractMachine):
        offs = cast_value(cell, amx.PRI)
        val = amx._getheapcell(offs)
        amx._writeheap(offs, cell(val + 1))

    # Decrementation
    def dec_pri(self, amx: SourcePawnAbstractMachine):
        amx.PRI -= 1

    def dec_alt(self, amx: SourcePawnAbstractMachine):
        amx.ALT -= 1

    def dec(self, amx: SourcePawnAbstractMachine, addr: int):
        val = amx._getheapcell(addr)
        amx._writeheap(addr, cell(val - 1))

    def dec_s(self, amx: SourcePawnAbstractMachine, addr: int):
        val = cell(amx._getheapcell(addr) - 1)
        amx._writeheap(addr, val)
        amx._stack_set(addr, val)

    def dec_i(self, amx: SourcePawnAbstractMachine):
        offs = cast_value(cell, amx.PRI)
        val = amx._getheapcell(offs)
        amx._writeheap(offs, cell(val - 1))

    def movs(self, amx: SourcePawnAbstractMachine, num_bytes: int):
        amx.heap[amx.ALT:][:num_bytes] = amx.heap[amx.PRI:][:num_bytes]

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

    def bounds(self, amx: SourcePawnAbstractMachine, offs: int):
        # XXX(zk): does this need to do anything else?
        pass

    def switch_(self, amx: SourcePawnAbstractMachine):
        # +1 to skip the CASETBL opcode
        cptr = amx._jumprel(amx.CIP) + sizeof(cell)

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

    def casetbl(self, amx: SourcePawnAbstractMachine):
        pass

    def swap_pri(self, amx: SourcePawnAbstractMachine):
        offs = amx._getheapcell(amx.STK)
        amx._writeheap(amx.STK, amx.PRI)
        amx.PRI = offs

    def swap_alt(self, amx: SourcePawnAbstractMachine):
        offs = amx._getheapcell(amx.STK)
        amx._writeheap(amx.STK, amx.ALT)
        amx.ALT = offs

    def _macro_push_n(self, amx, *offsets):
        for offs in offsets:
            val = amx._getheapcell(offs)
            amx._push(val)

    push = push2 = push3 = push4 = push5 = _macro_push_n
    push_s = push2_s = push3_s = push4_s = push5_s = _macro_push_n

    def _macro_push_n_c(self, amx, *values):
        for val in values:
            amx._push(val)

    push_c = push2_c = push3_c = push4_c = push5_c = _macro_push_n_c

    def _macro_push_n_adr(self, amx, *offsets):
        for offs in offsets:
            amx._push(offs)

    push_adr = push2_adr = push3_adr = push4_adr = push5_adr = _macro_push_n_adr

    def load_both(self, amx: SourcePawnAbstractMachine, pri_offs: int, alt_offs: int):
        amx.PRI = amx._getdatacell(pri_offs)
        amx.ALT = amx._getdatacell(alt_offs)

    load_s_both = load_both

    def const_(self, amx: SourcePawnAbstractMachine, offs: int, val: int):
        amx._writeheap(offs, cell(val))

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

    def genarray(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def genarray_z(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def stradjust_pri(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def stackadjust(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError


    def ldgfn_pri(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def rebase(self, amx: SourcePawnAbstractMachine):
        pass

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
            amx._writeheap(iv_vec_addr, tpl_iv_vec)

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

    def initarray_pri(self, amx: SourcePawnAbstractMachine, *args):
        self._initarray(amx, True, *args)

    def initarray_alt(self, amx: SourcePawnAbstractMachine, *args):
        self._initarray(amx, False, *args)

    def heap_save(self, amx: SourcePawnAbstractMachine):
        pass

    def heap_restore(self, amx: SourcePawnAbstractMachine):
        pass


    def fabs(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def float_(self, amx: SourcePawnAbstractMachine):
        raise NotImplementedError

    def floatadd(self, amx: SourcePawnAbstractMachine):
        left = amx._popparam_float()
        right = amx._popparam_float()
        amx.PRI = amx._sp_ftoc(left + right)

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
