from __future__ import division

import logging
import re
import time
from ctypes import *
from functools import wraps

import six

from smx.engine import engine_time
from smx.definitions import *
from smx.exceptions import SourcePawnStringFormatError
from smx.struct import cast_value

__all__ = ['SourceModNatives', 'SourceModSystem']

logger = logging.getLogger(__name__)


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
                _check_fmt_args(eats, state.arg - 1, state.args)
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

    @formatfunc('.', incr=False)
    def precision(self, ch, state):
        state.i += 1 # Eat the period
        prec,chars = atoi(state.fmt[state.i:], length=True)
        state.precision = None if prec < 0 else prec
        state.i += chars
        state.sz_format += '.' + str(prec)

    @formatfunc('0')
    def zeropad(self, ch, state):
        state.flags |= FMT_ZEROPAD

    @formatfunc('123456789', incr=False)
    def width(self, ch, state):
        state.width,chars = atoi(state.fmt[state.i:], length=True)
        state.i += chars
        state.sz_format += str(state.width)

    @formatfunc('%')
    def percent(self, ch, state):
        return '%'

    @formatfunc('c', eats=1)
    def char(self, ch, state):
        addr = state.amx._getheapcell(state.params[state.arg])
        val = state.amx._local_to_char(addr)
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
        val = ucell(val).value
        h = render_hex(val, state.flags, state.width)
        if ch.isupper():
            h = h.upper()
        return h


def atcprintf(_amx, _fmt, _params, _arg, formatter=PrintfFormatter()):
    _len = len(_fmt)

    class PrintfState:
        i = 0
        fmt = _fmt
        out = ''
        flags = 0
        width = 0
        precision = None
        arg = _arg
        args = _params[0]
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

        do_break = False
        while state.i < _len:
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


def sp_ctof(value):
    """Takes a raw value and ctypes casts it to a Python float value"""
    cf = pointer(c_long(value))
    return cast_value(c_float, cf)


class WritableString(object):
    """Wrapper around string offset and maxlength for easy writing"""

    def __init__(self, natives, string_offs, max_length):
        self.natives = natives
        self.string_offs = string_offs
        self.max_length = max_length

    def write(self, s):
        num_chars = min(len(s), self.max_length)
        self.natives.amx._writeheap(self.string_offs, ctypes.create_string_buffer(s.encode('utf8'), num_chars))
        return num_chars


def interpret_params(natives, params, *types):
    """Convert VM params into native Python types

    Supported types:
     - cell: for integers (or "any:" tag)
     - bool: a cell cast to boolean
     - float: floating point numbers
     - string: dereferenced pointer into DATA containing a string
     - writable_string: eats two params (String:s, maxlength) and returns a
            special object with a .write('string') method, for writing strings
            back to the plugin.
     - handle: a handle ID dereferenced to its backing object

    TODO: varargs

    :param natives: SourceModNatives instance
    :type natives: SourceModNatives
    :param params: Iterable of params from the VM
    :param types: list of strings describing how to interpret params
    """
    num_params = params[0]
    args = params[1:1 + num_params]
    i = 0
    for type in types:
        arg = args[i]
        if type == 'cell' or type is None:
            yield arg
        elif type == 'bool':
            yield bool(arg)
        elif type == 'float':
            yield sp_ctof(arg)
        elif type == 'string':
            yield natives.amx._local_to_string(arg)
        elif type == 'writable_string':
            s = arg
            i += 1
            maxlen = args[i]
            yield WritableString(natives, s, maxlen)
        elif type == 'handle':
            yield natives.sys.handles[arg]
        else:
            raise ValueError('Unsupported param type %s' % type)

        i += 1


def native(f, *types):
    """Labels a function/method as a native

    Optionally, takes a list of param types to automatically perform parameter
    unpacking. For example:

        @native('string', 'string', 'string', 'cell', 'bool', 'float', 'bool', 'float')
        def CreateConVar(name, default_value, description, flags, has_min, min, has_max, max):
            # ...
    """
    interpret = False
    if isinstance(f, six.string_types):
        types = (f,) + types
        interpret = True
        f = None

    def _native(fn):
        if interpret:
            original_fn = fn

            @wraps(original_fn)
            def _wrapped(self, params):
                interpreted = tuple(interpret_params(self, params, *types))
                return original_fn(self, *interpreted)
            fn = _wrapped

        fn.is_native = True
        return fn

    if f is None:
        return _native
    else:
        return _native(f)


class ConVar(object):
    def __init__(self, name, default_value, description='', flags=0, min=None, max=None):
        self.name = name
        self.value = self.default_value = default_value
        self.description = description
        self.flags = flags
        self.min = min
        self.max = max

    def __str__(self):
        return self.value

    def __repr__(self):
        return '<ConVar %s %r>' % (self.name, self.value)


class SourceModNatives(object):
    def __init__(self, sys):
        """
        @type   sys: smx.sourcemod.SourceModSystem
        @param  sys: The SourceMod system emulator owning these natives
        """
        self.sys = sys
        self.amx = self.sys.amx
        self.runtime = self.amx.plugin.runtime

    def printf(self, msg):
        return self.runtime.printf(msg)

    def get_native(self, funcname):
        if hasattr(self, funcname):
            func = getattr(self, funcname)
            if callable(func) and getattr(func, 'is_native', False):
                return func

    @native
    def PrintToServer(self, params):
        fmt = self.amx._local_to_string(params[1])
        out = atcprintf(self.amx, fmt, params, 2)
        self.printf(out)

    @native('float', 'cell', 'cell', 'cell')
    def CreateTimer(self, interval, func, data, flags):
        """
        native Handle:CreateTimer(Float:interval, Timer:func, any:data=INVALID_HANDLE, flags=0)

        Creates a basic timer.  Calling CloseHandle() on a timer will end the timer.

        @param interval    Interval from the current game time to execute the given function.
        @param func        Function to execute once the given interval has elapsed.
        @param data        Handle or value to pass through to the timer callback function.
        @param flags       Flags to set (such as repeatability or auto-Handle closing).
        @return            Handle to the timer object.  You do not need to call CloseHandle().
                               If the timer could not be created, INVALID_HANDLE will be returned.
        """
        logger.info('Interval: %f, func: %d, data: %d, flags: %d' % (interval, func, data, flags))
        return self.sys.timers.create_timer(interval, func, data, flags)

    @native
    def CreateConVar(self, params):
        name = self.amx._local_to_string(params[1])
        default_value = self.amx._local_to_string(params[2])
        description = self.amx._local_to_string(params[3])
        flags = params[4]
        has_min = bool(params[5])
        min = sp_ctof(params[6]) if has_min else None
        has_max = bool(params[7])
        max = sp_ctof(params[8]) if has_max else None

        cvar = ConVar(name, default_value, description, flags, min, max)
        self.sys.convars[name] = cvar
        return self.sys.handles.new_handle(cvar)

    @native
    def GetConVarInt(self, params):
        handle = params[1]
        cvar = self.sys.handles[handle]
        return int(cvar.value)

    @native('handle', 'writable_string')
    def GetConVarString(self, cvar, buf):
        return buf.write(cvar.value)


class SourceModHandles(object):
    """Emulates SourceMod's handles"""

    def __init__(self, sys):
        self.sys = sys
        self._handle_counter = 0
        self._handles = {}

    def new_handle(self, obj):
        self._handle_counter += 1
        handle_id = self._handle_counter
        self._handles[handle_id] = obj
        return handle_id

    def __getitem__(self, handle_id):
        return self._handles[handle_id]


class SourceModTimers(object):
    """Handles SourceMod timers"""

    TIMER_REPEAT = (1<<0)               # Timer will repeat until it returns Plugin_Stop
    TIMER_FLAG_NO_MAPCHANGE = (1<<1)    # Timer will not carry over mapchanges
    TIMER_HNDL_CLOSE = (1<<9)           # Deprecated define, replaced by below
    TIMER_DATA_HNDL_CLOSE = (1<<9)      # Timer will automatically call CloseHandle() on its data when finished

    def __init__(self, sys):
        """
        @type   sys: smx.sourcemod.SourceModSystem
        @param  sys: The SourceMod system emulator owning these natives
        """
        self.sys = sys
        self._timers = []

    def create_timer(self, interval, callback, data, flags):
        handle_id = self.sys.handles.new_handle(None)  # TODO: uhh, actual timer objects

        def timer_callback():
            # XXX: call this enter_frame instead?
            # self.sys.runtime.amx._dummy_frame()
            return self.sys.runtime.call_function(callback, handle_id, data)

        # TODO: repeating timers
        self._timers.append((engine_time() + interval, timer_callback))
        return handle_id

    def has_timers(self):
        return bool(self._timers)

    def poll_for_timers(self):
        while self.has_timers():
            time.sleep(self.sys.interval_per_tick)
            self.sys.tick()

            to_call = [f for call_after, f in self._timers
                       if self.sys.last_tick > call_after]
            self._timers = [(call_after, f) for call_after, f in self._timers
                            if self.sys.last_tick <= call_after]

            for callback in to_call:
                callback()


class SourceModSystem(object):
    """Emulates all SourcePawn -> SourceMod interactions"""

    def __init__(self, amx):
        """
        @type   amx: smx.vm.SourcePawnAbstractMachine
        @param  amx: The abstract machine owning these natives
        """
        self.amx = amx
        self.plugin = self.amx.plugin
        self.runtime = self.plugin.runtime

        self.natives = SourceModNatives(self)
        self.timers = SourceModTimers(self)
        self.handles = SourceModHandles(self)

        self.tickrate = 66
        self.interval_per_tick = 1.0 / self.tickrate
        self.last_tick = None

        self.convars = {}

    def tick(self):
        self.last_tick = engine_time()
