# Defines all the SourcePawn opcodes and provides helpers
from __future__ import annotations

from typing import Dict, List, NamedTuple, Tuple, TYPE_CHECKING

from smx.compat import iskeyword, StrEnum

if TYPE_CHECKING:
    from smx.vm import SourcePawnAbstractMachine

__all__ = ['sp_opcodes_list', 'opcodes']


class StackAddr(int):
    """Stack-relocated address, recording delta and absolute value"""

    offset: int

    def __new__(cls, addr: int, offset: int):
        inst = super().__new__(cls, addr)
        inst.offset = offset
        return inst


class SourcePawnInstructionParam(StrEnum):
    CONSTANT = 'constant'
    STACK = 'stack'
    JUMP = 'jump'
    FUNCTION = 'function'
    NATIVE = 'native'
    ADDRESS = 'address'

    def read(self, amx: SourcePawnAbstractMachine) -> int:
        if self in (P.CONSTANT, P.JUMP, P.FUNCTION, P.NATIVE, P.ADDRESS):
            return amx._getparam()
        elif self is P.STACK:
            offset = amx._getparam()
            return StackAddr(amx.FRM + offset, offset)
        else:
            raise ValueError(f'Unknown SourcePawnInstructionParam {self!r}')

    def format(self, amx: SourcePawnAbstractMachine, value: int) -> str:
        arg: str
        display: str | None = None

        if self is P.CONSTANT:
            arg = hex(value)
            display = str(value)

        elif self is P.JUMP:
            arg = hex(value)
            delta = value - amx.instr_addr
            display = f'{"+" if delta >= 0 else "-"}{hex(abs(delta))}'

        elif self is P.STACK:
            if isinstance(value, StackAddr):
                arg = f'{hex(value.offset)}/{hex(value)}'
            else:
                arg = hex(value)

            meth = amx.plugin.find_method_by_addr(amx.instr_addr)
            if meth:
                sym = meth.associated_locals.get(value.offset)
                if sym:
                    display = getattr(sym, 'name', None)

        elif self in (P.FUNCTION, P.ADDRESS):
            arg = hex(value)
            sym = amx.plugin.find_symbol_by_addr(value)
            if sym:
                display = getattr(sym, 'name', None)

        elif self is P.NATIVE:
            arg = str(value)
            if 0 <= value < len(amx.plugin.rtti_natives):
                display = amx.plugin.rtti_natives[value].name

        else:
            arg = hex(value)

        if display is None:
            return arg

        return f'{arg} ({display})'


# Convenience alias, for brevity
P = SourcePawnInstructionParam


class SourcePawnInstruction(NamedTuple):
    name: str
    method: str
    params: Tuple[SourcePawnInstructionParam, ...]
    is_generated: bool

    def __str__(self):
        return self.name

    def __repr__(self):
        return repr(self.name)

    def read_params(self, amx: SourcePawnAbstractMachine) -> List[int]:
        return [p.read(amx) for p in self.params]

    def format_params(self, amx: SourcePawnAbstractMachine, values: List[int]) -> List[str]:
        return [p.format(amx, value) for p, value in zip(self.params, values)]


def _instruction(
    name: str,
    *params: SourcePawnInstructionParam,
    method: str | None = None,
    is_generated: bool = True
) -> SourcePawnInstruction:
    if method is None:
        if iskeyword(name):
            method = f'{name}_'
        else:
            method = name
        method = method.replace('.', '_')

    return SourcePawnInstruction(name=name, method=method, params=params, is_generated=is_generated)


def _G(name: str, *params: SourcePawnInstructionParam, method: str | None = None) -> SourcePawnInstruction:
    return _instruction(name, *params, method=method, is_generated=True)


def _U(name: str, *params: SourcePawnInstructionParam, method: str | None = None) -> SourcePawnInstruction:
    return _instruction(name, *params, method=method, is_generated=False)


sp_opcodes_list: List[SourcePawnInstruction] = [
    _G('none'),
    _G('load.pri', P.ADDRESS),
    _G('load.alt', P.ADDRESS),
    _G('load.s.pri', P.STACK),
    _G('load.s.alt', P.STACK),
    _U('lref.pri'),
    _U('lref.alt'),
    _G('lref.s.pri', P.STACK),
    _G('lref.s.alt', P.STACK),
    _G('load.i'),
    _G('lodb.i', P.CONSTANT),
    _G('const.pri', P.CONSTANT),
    _G('const.alt', P.CONSTANT),
    _G('addr.pri', P.STACK),
    _G('addr.alt', P.STACK),
    _G('stor.pri', P.ADDRESS),
    _G('stor.alt', P.ADDRESS),
    _G('stor.s.pri', P.STACK),
    _G('stor.s.alt', P.STACK),
    _U('sref.pri'),
    _U('sref.alt'),
    _G('sref.s.pri', P.STACK),
    _G('sref.s.alt', P.STACK),
    _G('stor.i'),
    _G('strb.i', P.CONSTANT),
    _G('lidx'),
    _U('lidx.b', P.CONSTANT),
    _G('idxaddr'),
    _U('idxaddr.b', P.CONSTANT),
    _U('align.pri'),
    _U('align.alt'),
    _U('lctrl'),
    _U('sctrl'),
    _G('move.pri'),
    _G('move.alt'),
    _G('xchg'),
    _G('push.pri'),
    _G('push.alt'),
    _U('push.r'),
    _G('push.c', P.CONSTANT),
    _G('push', P.ADDRESS),
    _G('push.s', P.STACK),
    _G('pop.pri'),
    _G('pop.alt'),
    _G('stack', P.CONSTANT),
    _G('heap', P.CONSTANT),
    _G('proc'),
    _U('ret'),
    _G('retn'),
    _G('call', P.FUNCTION),
    _U('call.pri'),
    _G('jump', P.JUMP),
    _U('jrel'),
    _G('jzer', P.JUMP),
    _G('jnz', P.JUMP),
    _G('jeq', P.JUMP),
    _G('jneq', P.JUMP),
    _U('jless'),
    _U('jleq'),
    _U('jgrtr'),
    _U('jgeq'),
    _G('jsless', P.JUMP),
    _G('jsleq', P.JUMP),
    _G('jsgrtr', P.JUMP),
    _G('jsgeq', P.JUMP),
    _G('shl'),
    _G('shr'),
    _G('sshr'),
    _G('shl.c.pri', P.CONSTANT),
    _G('shl.c.alt', P.CONSTANT),
    _U('shr.c.pri', P.CONSTANT),
    _U('shr.c.alt', P.CONSTANT),
    _G('smul'),
    _G('sdiv'),
    _G('sdiv.alt'),
    _U('umul'),
    _U('udiv'),
    _U('udiv.alt'),
    _G('add'),
    _G('sub'),
    _G('sub.alt'),
    _G('and'),
    _G('or'),
    _G('xor'),
    _G('not'),
    _G('neg'),
    _G('invert'),
    _G('add.c', P.CONSTANT),
    _G('smul.c', P.CONSTANT),
    _G('zero.pri'),
    _G('zero.alt'),
    _G('zero', P.ADDRESS),
    _G('zero.s', P.STACK),
    _U('sign.pri'),
    _U('sign.alt'),
    _G('eq'),
    _G('neq'),
    _U('less'),
    _U('leq'),
    _U('grtr'),
    _U('geq'),
    _G('sless'),
    _G('sleq'),
    _G('sgrtr'),
    _G('sgeq'),
    _G('eq.c.pri', P.CONSTANT),
    _G('eq.c.alt', P.CONSTANT),
    _G('inc.pri'),
    _G('inc.alt'),
    _G('inc', P.ADDRESS),
    _G('inc.s', P.STACK),
    _G('inc.i'),
    _G('dec.pri'),
    _G('dec.alt'),
    _G('dec', P.ADDRESS),
    _G('dec.s', P.STACK),
    _G('dec.i'),
    _G('movs', P.CONSTANT),
    _U('cmps'),
    _G('fill', P.CONSTANT),
    _G('halt', P.CONSTANT),
    _G('bounds', P.CONSTANT),
    _U('sysreq.pri'),
    _G('sysreq.c', P.NATIVE),
    _U('file'),
    _U('line'),
    _U('symbol'),
    _U('srange'),
    _U('jump.pri'),
    _G('switch', P.ADDRESS),
    _G('casetbl', P.CONSTANT, P.ADDRESS),
    _G('swap.pri'),
    _G('swap.alt'),
    _G('push.adr', P.STACK),
    _G('nop'),
    _G('sysreq.n', P.NATIVE, P.CONSTANT),
    _U('symtag'),
    _G('break'),
    _G('push2.c', P.CONSTANT, P.CONSTANT),
    _G('push2', P.ADDRESS, P.ADDRESS),
    _G('push2.s', P.STACK, P.STACK),
    _G('push2.adr', P.STACK, P.STACK),
    _G('push3.c', P.CONSTANT, P.CONSTANT, P.CONSTANT),
    _G('push3', P.ADDRESS, P.ADDRESS, P.ADDRESS),
    _G('push3.s', P.STACK, P.STACK, P.STACK),
    _G('push3.adr', P.STACK, P.STACK, P.STACK),
    _G('push4.c', P.CONSTANT, P.CONSTANT, P.CONSTANT, P.CONSTANT),
    _G('push4', P.ADDRESS, P.ADDRESS, P.ADDRESS, P.ADDRESS),
    _G('push4.s', P.STACK, P.STACK, P.STACK, P.STACK),
    _G('push4.adr', P.STACK, P.STACK, P.STACK, P.STACK),
    _G('push5.c', P.CONSTANT, P.CONSTANT, P.CONSTANT, P.CONSTANT, P.CONSTANT),
    _G('push5', P.ADDRESS, P.ADDRESS, P.ADDRESS, P.ADDRESS, P.ADDRESS),
    _G('push5.s', P.STACK, P.STACK, P.STACK, P.STACK, P.STACK),
    _G('push5.adr', P.STACK, P.STACK, P.STACK, P.STACK, P.STACK),
    _G('load.both', P.ADDRESS, P.ADDRESS),
    _G('load.s.both', P.STACK, P.STACK),
    _G('const', P.ADDRESS, P.CONSTANT),
    _G('const.s', P.STACK, P.CONSTANT),
    _U('sysreq.d'),
    _U('sysreq.nd'),
    _G('trk.push.c'),
    _G('trk.pop'),
    _G('genarray', P.CONSTANT),
    _G('genarray.z', P.CONSTANT),
    _G('stradjust.pri'),
    _U('stackadjust'),
    _G('endproc'),
    _U('ldgfn.pri'),
    _U('rebase', P.ADDRESS, P.CONSTANT, P.CONSTANT),
    _G('initarray.pri', P.ADDRESS, P.CONSTANT, P.CONSTANT, P.CONSTANT, P.CONSTANT),
    _G('initarray.alt', P.ADDRESS, P.CONSTANT, P.CONSTANT, P.CONSTANT, P.CONSTANT),
    _G('heap.save'),
    _G('heap.restore'),
    _U('firstfake'),
    _G('fabs'),
    _G('float'),
    _G('float.add'),
    _G('float.sub'),
    _G('float.mul'),
    _G('float.div'),
    _G('round'),
    _G('floor'),
    _G('ceil'),
    _G('rndtozero'),
    _G('float.cmp'),
    _G('float.gt'),
    _G('float.ge'),
    _G('float.lt'),
    _G('float.le'),
    _G('float.ne'),
    _G('float.eq'),
    _G('float.not'),
]


class SourcePawnOpcodes:
    def __init__(self):
        self._by_name: Dict[str, SourcePawnInstruction] = {}
        self._by_method: Dict[str, SourcePawnInstruction] = {}

        for opcode, instr in enumerate(sp_opcodes_list):
            self._by_name[instr.name] = instr

    def __getitem__(self, item: int | str) -> SourcePawnInstruction:
        if isinstance(item, int):
            return sp_opcodes_list[item]
        else:
            try:
                return self._by_name[item]
            except KeyError:
                return self._by_method[item]

    def __getattr__(self, item):
        try:
            return self._by_method[item]
        except KeyError:
            raise AttributeError('There is no "%s" opcode' % item)


opcodes = SourcePawnOpcodes()
