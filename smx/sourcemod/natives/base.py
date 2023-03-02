from __future__ import annotations

import ctypes
import struct
from ctypes import c_float, c_long, pointer
from functools import wraps
from typing import Any, Callable, Sequence, Type, TYPE_CHECKING

from smx.compat import Literal
from smx.struct import cast_value

if TYPE_CHECKING:
    from smx.sourcemod.natives import SourceModNatives
    from smx.sourcemod.system import SourceModSystem
    from smx.vm import SourcePawnAbstractMachine
    from smx.runtime import SourcePawnPluginRuntime


def sp_ctof(value: int):
    """Takes a raw value and ctypes casts it to a Python float value"""
    cf = pointer(c_long(value))
    return cast_value(c_float, cf)


def sp_ftoc(value: float) -> int:
    return struct.unpack('<L', struct.pack('<f', value))[0]


NativeParamType = Literal['cell', 'bool', 'float', 'string', 'writable_string', 'handle', 'function', '...']


# TODO(zk): convert this all to use RTTI
def interpret_params(natives: SourceModNatives, params: Sequence[int], *param_types: NativeParamType):
    """Convert VM params into native Python types

    Supported types:
     - cell: for integers (or "any:" tag)
     - bool: a cell cast to boolean
     - float: floating point numbers
     - string: dereferenced pointer into heap containing a string
     - writable_string: eats two params (String:s, maxlength) and returns a
            special object with a .write('string') method, for writing strings
            back to the plugin.
     - handle: a handle ID dereferenced to its backing object
     - function: a funcid wrapped as a PluginFunction
     - ...: variadic params, interpreted as cells

    :param natives: SourceModNatives instance
    :param params: Iterable of params from the VM
    :param param_types: list of strings describing how to interpret params
    """
    num_params = params[0]
    args = params[1:1 + num_params]
    i = 0
    for param_type in param_types:
        if param_type == '...':
            remaining_params = args[i:]
            yield from remaining_params
            return

        arg = args[i]
        if param_type == 'cell' or param_type is None:
            yield arg
        elif param_type == 'bool':
            yield bool(arg)
        elif param_type == 'float':
            yield sp_ctof(arg)
        elif param_type == 'string':
            yield natives.amx._getheapstring(arg)
        elif param_type == 'writable_string':
            s = arg
            i += 1
            maxlen = args[i]
            yield WritableString(natives.amx, s, maxlen)
        elif param_type == 'handle':
            yield natives.sys.handles[arg]
        elif param_type == 'function':
            yield natives.runtime.get_function_by_id(arg)
        else:
            raise ValueError('Unsupported param type %s' % param_type)

        i += 1


def convert_return_value(rval: Any) -> int:
    """Convert a native return value to a cell"""
    if rval is None:
        # XXX(zk): is this how SM handles a void native?
        return 0
    elif isinstance(rval, bool):
        return int(rval)
    elif isinstance(rval, float):
        return sp_ftoc(rval)
    elif isinstance(rval, int):
        return rval
    else:
        raise TypeError(f'Unsupported return value {rval!r}')


def native(f: Callable[..., Any] | NativeParamType, *types: NativeParamType, interpret: bool = True):
    """Labels a function/method as a native

    Optionally, takes a list of param types to automatically perform parameter
    unpacking. For example:

        @native('string', 'string', 'string', 'cell', 'bool', 'float', 'bool', 'float')
        def CreateConVar(name, default_value, description, flags, has_min, min, has_max, max):
            # ...

    """
    if isinstance(f, str):
        if not interpret:
            raise ValueError('Cannot specify types without interpret=True')

        types = (f,) + types
        f = None

    def _native(fn):
        if interpret:
            original_fn = fn

            @wraps(original_fn)
            def _wrapped(self, params):
                interpreted = tuple(interpret_params(self, params, *types))
                rval = original_fn(self, *interpreted)
                return convert_return_value(rval)
            fn = _wrapped

        fn.is_native = True
        return fn

    if f is None:
        return _native
    else:
        return _native(f)


class SourceModNativesMixin:
    sys: SourceModSystem
    amx: SourcePawnAbstractMachine
    runtime: SourcePawnPluginRuntime

    def __init_subclass__(cls):
        # Allow native methods to begin with __ without getting mangled
        mangled_prefix = f'_{cls.__name__}__'
        for name, attr in dict(vars(cls)).items():
            if name.startswith(mangled_prefix):
                unmangled_name = name[len(mangled_prefix)-2:]
                setattr(cls, unmangled_name, attr)
                delattr(cls, name)


class _MethodMapDescriptor:
    def __init__(self, method_map: Type[MethodMap]):
        self.method_map = method_map


class MethodMap(SourceModNativesMixin):
    def __init__(self):
        self._name: str | None = None

    def __set_name__(self, owner, name):
        # XXX(zk): individual, per-instance names?
        self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self._name not in instance.__dict__:
            # TODO(zk): less ugly?
            method_map = self.__class__()
            method_map.amx = instance.amx
            method_map.sys = instance.sys
            method_map.runtime = instance.runtime
            instance.__dict__[self._name] = method_map

        return instance.__dict__[self._name]


class WritableString:
    """Wrapper around string offset and maxlength for easy writing"""

    def __init__(self, amx: SourcePawnAbstractMachine, string_offs, max_length):
        self.amx = amx
        self.string_offs = string_offs
        self.max_length = max_length

    def __str__(self):
        return self.read()

    def read(self) -> str:
        return self.amx._local_to_string(self.string_offs)

    def write(self, s: str | bytes, *, null_terminate: bool = False):
        if not isinstance(s, bytes):
            s = s.encode('utf8')

        num_bytes = num_bytes_written = min(len(s), self.max_length)
        if null_terminate:
            s += b'\0'
            num_bytes = min(len(s), self.max_length)

        self.amx._writeheap(self.string_offs, ctypes.create_string_buffer(s, num_bytes))
        return num_bytes_written
