from __future__ import annotations

import dataclasses
import re
from ctypes import c_int
from functools import wraps
from typing import Sequence, TYPE_CHECKING

from smx.definitions import cell, ucell
from smx.exceptions import SourcePawnStringFormatError

if TYPE_CHECKING:
    from smx.vm import SourcePawnAbstractMachine

RGX_NUMBER = re.compile(r'[-+]?\d+')
FMT_LADJUST     = 0x00000004  # left adjustment
FMT_ZEROPAD     = 0x00000080  # zero (as opposed to blank) pad
FMT_UPPERDIGITS = 0x00000200  # make alpha digits uppercase
NULL = 0


def _check_fmt_args(x, arg, args):
    if (arg + x) > args:
        raise SourcePawnStringFormatError(
            'String formatted incorrectly - parameter %d (total %d)' %
            (arg, args))


def has_flag(v, flag):
    return (v & flag) == flag


def has_flags(v, flags):
    # TODO: use generator to allow for early escape (profile first)
    return all(map(lambda f: has_flag(v, f), flags))


def atoi(s, length=False):
    """Reads in digits from a string till a non-digit is found"""
    m = RGX_NUMBER.match(s)
    if m is None:
        raise ValueError('invalid literal for atoi(): %s' % s)
    if length:
        return int(m.group()), m.end()
    else:
        return int(m.group())


def render_fmt(fmt_char, flags, width, precision=None):
    ladj = '-' if has_flag(flags, FMT_LADJUST) else ''
    zero = '0' if has_flag(flags, FMT_ZEROPAD) else ''
    wdth = str(width) if width > 0 else ''
    prec = ('.%d' % precision) if precision is not None else ''
    return '%' + ladj + zero + wdth + prec + fmt_char


def render_int(val, flags, width):
    s = render_fmt('d', flags, width) % val
    # SourceMod differs from Python in that it will left adjust with zeroes
    if has_flags(flags, (FMT_LADJUST,FMT_ZEROPAD)):
        s = s.replace(' ', '0')
    return s


def render_string(val, flags, width, precision):
    return render_fmt('s', flags, width, precision) % val


def render_bin(val, flags, width):
    s = bin(val)[2:]
    return render_string(s, flags, width, None)


def render_hex(val, flags, width):
    s = render_fmt('x', flags, width) % val
    # SourceMod differs from Python in that it will left adjust with zeroes
    if has_flags(flags, (FMT_LADJUST,FMT_ZEROPAD)):
        s = s.replace(' ', '0')
    return s


def render_float(val, flags, width, precision):
    # TODO: SourceMod does not round the last digit, we need to match this
    return render_fmt('f', flags, width, precision) % val


def formatfunc(matches, eats=0, incr=True):
    """
    Marks a function as a format handler
    @type   matches: iterable -> str[1]
    @param  matches: An iterable of characters the format function supports
    @type   eats: int
    @param  eats: The number of arguments the format function uses up on
                successful formatting (returning non-None)
    @type   incr: bool
    @param  incr: Whether or not to increment i after return
    """
    def inner(f):
        func = f
        if eats > 0:
            def wrapper(*args, **kwargs):
                state = kwargs['state'] if 'state' in kwargs else args[-1]
                _check_fmt_args(eats, state.arg - 1, state.num_args)
                return f(*args, **kwargs)
            func = wraps(f)(wrapper)

        func.formatfunc = True
        func.matches = matches
        func.eats = eats
        func.incr = incr

        return func
    return inner


def isformatfunc(f):
    return callable(f) and hasattr(f, 'formatfunc') and f.formatfunc


@dataclasses.dataclass
class PrintfState:
    i: int
    fmt: str
    out: str
    flags: int
    width: int
    precision: int | None
    arg: int
    num_args: int
    amx: SourcePawnAbstractMachine
    params: Sequence[int]
    sz_format: str | None


class PrintfFormatter:
    def __init__(self):
        # A mapping of format characters to their format functions
        self.format_chars = {}

        for obj in map(lambda n: getattr(self, n), dir(self)):
            if isformatfunc(obj):
                for c in obj.matches:
                    self.format_chars[c] = obj

    @formatfunc('-')
    def ladjust(self, ch: str, state: PrintfState):
        state.flags |= FMT_LADJUST

    @formatfunc('.', incr=False)
    def precision(self, ch: str, state: PrintfState):
        state.i += 1  # Eat the period
        prec, chars = atoi(state.fmt[state.i:], length=True)
        state.precision = None if prec < 0 else prec
        state.i += chars
        state.sz_format += '.' + str(prec)

    @formatfunc('0')
    def zeropad(self, ch: str, state: PrintfState):
        state.flags |= FMT_ZEROPAD

    @formatfunc('123456789', incr=False)
    def width(self, ch: str, state: PrintfState):
        state.width,chars = atoi(state.fmt[state.i:], length=True)
        state.i += chars
        state.sz_format += str(state.width)

    @formatfunc('%')
    def percent(self, ch: str, state: PrintfState):
        return '%'

    @formatfunc('c', eats=1)
    def char(self, ch: str, state: PrintfState):
        addr = state.amx._getheapcell(state.params[state.arg])
        val = state.amx._local_to_char(addr)
        return val[0]

    @formatfunc('id', eats=1)
    def integer(self, ch: str, state: PrintfState):
        val = state.amx._getheapcell(state.params[state.arg])
        val = c_int(val).value
        return render_int(val, state.flags, state.width)

    @formatfunc('u', eats=1)
    def unsigned_integer(self, ch: str, state: PrintfState):
        val = state.amx._getheapcell(state.params[state.arg])
        return render_int(val, state.flags, state.width)

    @formatfunc('f', eats=1)
    def floating_point(self, ch: str, state: PrintfState):
        val = state.amx._getheapcell(state.params[state.arg])
        val = state.amx._sp_ctof(cell(val))
        if state.precision is None:
            state.precision = 6
        return render_float(val, state.flags, state.width, state.precision)

    @formatfunc('s', eats=1)
    def string(self, ch: str, state: PrintfState):
        if state.params[state.arg] == NULL:
            val = '(null)'
            state.precision = None
        else:
            val = state.amx._local_to_string(state.params[state.arg])
        return render_string(val, state.flags, state.width, state.precision)

    @formatfunc('b', eats=1)
    def binary(self, ch: str, state: PrintfState):
        val = state.amx._getheapcell(state.params[state.arg])
        return render_bin(val, state.flags, state.width)

    @formatfunc('L', eats=1)
    def client_info(self, ch: str, state: PrintfState):
        raise NotImplementedError

    @formatfunc('N', eats=1)
    def client_name(self, ch: str, state: PrintfState):
        raise NotImplementedError

    @formatfunc('T')
    def translate_client_lang(self, ch: str, state: PrintfState):
        raise NotImplementedError

    @formatfunc('t')
    def translate_server_lang(self, ch: str, state: PrintfState):
        raise NotImplementedError

    @formatfunc('xX', eats=1)
    def hexadecimal(self, ch: str, state: PrintfState):
        val = state.amx._getheapcell(state.params[state.arg])
        val = ucell(val).value
        h = render_hex(val, state.flags, state.width)
        if ch.isupper():
            h = h.upper()
        return h


def atcprintf(
    amx: SourcePawnAbstractMachine,
    fmt: str,
    params: Sequence[int],
    formatter: PrintfFormatter = PrintfFormatter(),
):
    fmt_len = len(fmt)

    state = PrintfState(
        i=0,
        fmt=fmt,
        out='',
        flags=0,
        width=0,
        precision=None,
        arg=0,
        num_args=len(params),
        amx=amx,
        params=params,
        sz_format=None,
    )
    while state.i < fmt_len:
        percent = state.fmt[state.i:].find('%')
        if percent == -1:
            state.out += state.fmt[state.i:]
            break

        else:
            state.out += state.fmt[state.i:state.i+percent]
            state.i += percent
            # Skip the percent
            state.i += 1

        state.flags = 0
        state.width = 0
        state.precision = None
        state.sz_format = '%'

        do_break = False
        while state.i < fmt_len:
            ch = state.fmt[state.i]
            if ch in formatter.format_chars:
                f = formatter.format_chars[ch]
                out = f(ch, state)

                if out is not None:
                    state.out += str(out)
                    state.arg += f.eats
                    do_break = True

                if f.incr:
                    state.sz_format += ch
                    state.i += 1

                if do_break:
                    break

            else:
                state.out += ch
                break

    return state.out
