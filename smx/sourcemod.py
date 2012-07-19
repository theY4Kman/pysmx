import re
from ctypes import *
from .smxdefs import *

__all__ = ['SourceModNatives']


RGX_NUMBER = re.compile(r'[-+]?\d+')

FMT_LADJUST     = 0x00000004 # left adjustment
FMT_ZEROPAD     = 0x00000080 # zero (as opposed to blank) pad
FMT_UPPERDIGITS = 0x00000200 # make alpha digits uppercase

NULL = 0


class SourcePawnStringFormatError(SourcePawnPluginNativeError):
    pass


def has_flag(v, flag):
    return (v & flag) == flag
def has_flags(v, flags):
    return all(map(lambda f: has_flag(v,f), flags))


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


def formatfunc(matches, eats=0, inc=True):
    """
    Marks a function as a format handler
    @type   matches: iterable -> str[1]
    @param  matches: An iterable of characters the format function supports
    @type   eats: int
    @param  eats: The number of arguments the format function uses up on
                successful formatting (returning non-None)
    @type   inc: bool
    @param  inc: Whether or not to increment i after return
    """
    def inner(f):
        f.formatfunc = True
        f.matches = matches
        f.eats = eats
        f.inc = inc
        return f
    return inner

def isformatfunc(f):
    return callable(f) and hasattr(f, 'formatfunc') and f.formatfunc

class PrintfFormatter(object):
    def __init__(self):
        # A mapping of format characters to their format functions
        self.format_chars = { }

        for obj in map(lambda n: getattr(self, n), dir(self)):
            if isformatfunc(obj):
                for c in obj.matches:
                    self.format_chars[c] = obj

    @formatfunc('-')
    def ladjust(self, ch, state):
        state.flags |= FMT_LADJUST

    @formatfunc('.', inc=False)
    def precision(self, ch, state):
        state.i += 1 # Eat the period
        prec,chars = atoi(state.fmt[state.i:], length=True)
        state.precision = None if prec < 0 else prec
        state.i += chars

    @formatfunc('0')
    def zeropad(self, ch, state):
        state.flags |= FMT_ZEROPAD

    @formatfunc('123456789', inc=False)
    def width(self, ch, state):
        state.width,chars = atoi(state.fmt[state.i:], length=True)
        state.i += chars

    @formatfunc('c', eats=1)
    def char(self, ch, state):
        val = state.amx._local_to_char(state.params[state.arg])
        return val[0]

    @formatfunc('id', eats=1)
    def integer(self, ch, state):
        val = state.amx._getheapcell(state.params[state.arg])
        val = c_int(val).value
        return render_int(val, state.flags, state.width)

    @formatfunc('u', eats=1)
    def unsigned_integer(self, ch, state):
        val = state.amx._getheapcell(state.params[state.arg])
        return render_int(val, state.flags, state.width)

    @formatfunc('f', eats=1)
    def floating_point(self, ch, state):
        val = state.amx._getheapcell(state.params[state.arg])
        val = state.amx._sp_ctof(cell(val))
        if state.precision is None:
            state.precision = 6
        return render_float(val, state.flags, state.width, state.precision)

    @formatfunc('s', eats=1)
    def string(self, ch, state):
        if state.params[state.arg] == NULL:
            val = '(null)'
            state.precision = None
        else:
            val = state.amx._local_to_string(state.params[state.arg])
        return render_string(val, state.flags, state.width, state.precision)

    @formatfunc('b', eats=1)
    def binary(self, ch, state):
        val = state.amx._getheapcell(state.params[state.arg])
        return render_bin(val, state.flags, state.width)

    @formatfunc('L', eats=1)
    def client_info(self, ch, state):
        raise NotImplementedError

    @formatfunc('N', eats=1)
    def client_name(self, ch, state):
        raise NotImplementedError

    @formatfunc('T')
    def translate_client_lang(self, ch, state):
        raise NotImplementedError

    @formatfunc('t')
    def translate_server_lang(self, ch, state):
        raise NotImplementedError

    @formatfunc('xX', eats=1)
    def hexadecimal(self, ch, state):
        val = state.amx._getheapcell(state.params[state.arg])
        h = render_hex(val, state.flags, state.width)
        if ch.isupper():
            h = h.upper()
        return h



def atcprintf(_amx, _fmt, _params, _arg, _args, formatter=PrintfFormatter()):
    _len = len(_fmt)

    class PrintfState:
        i = 0
        fmt = _fmt
        out = ''
        flags = 0
        width = 0
        precision = None
        arg = _arg
        args = _args
        amx = _amx
        params = _params
        sz_format = None

    state = PrintfState()
    while state.i < _len:
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

        while state.i < _len:
            ch = state.fmt[state.i]
            inc = True
            if ch in formatter.format_chars:
                f = formatter.format_chars[ch]
                inc = f.inc
                out = f(ch, state)
                if out is not None:
                    state.out += str(out)
                    state.arg += f.eats
                    if inc:
                        state.i += 1
                    break
                state.sz_format += ch

            else:
                state.out += ch
                break

            if inc:
                state.i += 1

    return state.out


def native(f):
    """Labels a function/method as a native"""
    f.is_native = True
    return f

class SourceModNatives(object):
    def __init__(self, amx):
        """
        @type   amx: smx.smxexec.SourcePawnAbstractMachine
        @param  amx: The abstract machine owning these natives
        """
        self.amx = amx
        self.runtime = amx.plugin.runtime

    def printf(self, msg):
        return self.runtime.printf(msg)

    def get_native(self, funcname):
        if hasattr(self, funcname):
            func = getattr(self, funcname)
            if (callable(func) and hasattr(func, 'is_native') and
                func.is_native):
                return func
        return None

    @native
    def PrintToServer(self, params):
        fmt = self.amx._local_to_string(params[1])
        out = atcprintf(self.amx, fmt, params, 2, params[0]-1)
        self.printf(out)
