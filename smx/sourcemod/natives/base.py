from __future__ import annotations

import ctypes
import inspect
import struct
import typing
from ctypes import c_float, c_long, pointer
from functools import wraps
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterator,
    List,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    TYPE_CHECKING,
    Union,
)

from smx.compat import get_annotations, NoneType, StrEnum
from smx.definitions import cell, PyCSimpleType, ucell
from smx.sourcemod.handles import SourceModHandle
from smx.struct import cast_value

if TYPE_CHECKING:
    from smx.sourcemod.natives import SourceModNatives
    from smx.sourcemod.system import SourceModSystem
    from smx.vm import SourcePawnAbstractMachine
    from smx.runtime import PluginFunction, SourcePawnPluginRuntime


def sp_ctof(value: int):
    """Takes a raw value and ctypes casts it to a Python float value"""
    cf = pointer(c_long(value))
    return cast_value(c_float, cf)


def sp_ftoc(value: float) -> int:
    return struct.unpack('<L', struct.pack('<f', value))[0]


class NativeParamType(StrEnum):
    CELL = 'cell'
    BOOL = 'bool'
    FLOAT = 'float'
    STRING = 'string'
    WRITABLE_STRING = 'writable_string'
    HANDLE = 'handle'
    FUNCTION = 'function'
    ARRAY = 'array'
    POINTER = 'pointer'
    VARARGS = '...'


NativeReturnType = Union[NoneType, bool, float, int, SourceModHandle]


def convert_return_value(rval: NativeReturnType) -> int:
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
    elif isinstance(rval, SourceModHandle):
        return rval.id
    else:
        raise TypeError(f'Unsupported return value {rval!r}')


class NativeImpl:
    is_native = True

    impl: Callable[..., float | int | bool | None]
    native_func: Callable[..., float | int | bool | None] | None
    param_types: List[Tuple[NativeParamType, type]] | None

    _annotation_ns: ClassVar[Dict[str, Any]] | None = None

    def __init__(self, impl: Callable[..., float | int | bool | None]):
        self.impl = impl
        self.native_func = None
        self.param_types = None

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.param_types is None:
            self._init_params()

        if self.native_func is None:
            @wraps(self.impl)
            def _native(natives: SourceModNatives, params: Sequence[int]):
                return self(natives, params)

            _native.is_native = True
            self.native_func = _native

        return self.native_func.__get__(instance, owner)

    def __call__(self, natives: SourceModNatives, params: Sequence[int]):
        num_params = params[0]
        args = params[1:1 + num_params]

        interpreted_args = []
        i = 0
        for param_type, coerce in self.param_types:
            if param_type == NativeParamType.VARARGS:
                interpreted_args.extend(args[i:])
                break

            arg = args[i]
            if param_type == NativeParamType.CELL:
                interpreted_args.append(coerce(arg))
            elif param_type == NativeParamType.BOOL:
                interpreted_args.append(coerce(arg))
            elif param_type == NativeParamType.FLOAT:
                interpreted_args.append(coerce(sp_ctof(arg)))
            elif param_type == NativeParamType.STRING:
                interpreted_args.append(coerce(natives.amx._getheapstring(arg)))
            elif param_type == NativeParamType.WRITABLE_STRING:
                s = arg
                i += 1
                maxlen = args[i]
                interpreted_args.append(WritableString(natives.amx, s, maxlen))
            elif param_type in (NativeParamType.ARRAY, NativeParamType.POINTER):
                interpreted_args.append(coerce(natives.amx, arg))
            elif param_type == NativeParamType.HANDLE:
                interpreted_args.append(natives.sys.handles.get_raw(arg))
            elif param_type == NativeParamType.FUNCTION:
                interpreted_args.append(natives.runtime.get_function_by_id(arg))
            else:
                raise ValueError('Unsupported param type %s' % param_type)

            i += 1

        rval = self.impl(natives, *interpreted_args)
        return convert_return_value(rval)

    def _init_params(self):
        from smx.runtime import PluginFunction

        sig = inspect.signature(self.impl)

        local_ns = self._get_annotation_ns()
        global_ns = self.impl.__globals__
        annotations = get_annotations(self.impl, globals=global_ns, locals=local_ns, eval_str=True)

        self.param_types = []
        for i, param in enumerate(sig.parameters.values()):
            if i == 0 and param.name == 'self':
                continue

            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                self.param_types.append((NativeParamType.VARARGS, Any))
                continue

            annotation = annotations.get(param.name, param.annotation)
            origin = getattr(annotation, '__origin__', annotation)
            if origin is Union:
                members = annotation.__args__
                if NoneType in members and len(members) == 2:
                    annotation = members[0]
                    origin = getattr(annotation, '__origin__', annotation)
                else:
                    raise TypeError(f'Unsupported parameter type {annotation !r}')

            if (
                annotation is inspect.Parameter.empty
                or origin in (cell, ucell)
                or issubclass(origin, int)
            ):
                self.param_types.append((NativeParamType.CELL, origin))
            elif issubclass(origin, bool):
                self.param_types.append((NativeParamType.BOOL, origin))
            elif issubclass(origin, float):
                self.param_types.append((NativeParamType.FLOAT, origin))
            elif issubclass(origin, str):
                self.param_types.append((NativeParamType.STRING, origin))

            elif issubclass(origin, Pointer):
                self.param_types.append((NativeParamType.POINTER, origin))
            elif issubclass(origin, Array):
                self.param_types.append((NativeParamType.ARRAY, origin))
            elif annotation is WritableString:
                self.param_types.append((NativeParamType.WRITABLE_STRING, WritableString))

            elif annotation is SourceModHandle or origin is SourceModHandle:
                self.param_types.append((NativeParamType.HANDLE, SourceModHandle))
            elif annotation is PluginFunction:
                self.param_types.append((NativeParamType.FUNCTION, PluginFunction))

            else:
                raise TypeError(f'Unsupported parameter type {annotation !r}')

    @classmethod
    def _get_annotation_ns(cls) -> Dict[str, Any]:
        if cls._annotation_ns is None:
            from smx.plugin import SourcePawnPlugin
            from smx.runtime import PluginFunction

            cls._annotation_ns = {
                'typing': typing,
                'PluginFunction': PluginFunction,
                'SourceModHandle': SourceModHandle,
                'SourcePawnPlugin': SourcePawnPlugin,
                'WritableString': WritableString,
            }

        return cls._annotation_ns


def native(impl: Callable) -> NativeImpl:
    return NativeImpl(impl)


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


V = TypeVar('V')


def get_c_type(py_type: Type[V]) -> PyCSimpleType:
    if issubclass(py_type, int):
        return cell
    elif issubclass(py_type, float):
        return ctypes.c_float
    elif issubclass(py_type, bool):
        return ctypes.c_bool
    elif issubclass(py_type, str):
        return ctypes.c_char
    elif issubclass(py_type, bytes):
        return ctypes.c_ubyte
    else:
        raise TypeError(f'Unsupported type {py_type!r}')


class BaseReference(Generic[V]):
    amx: SourcePawnAbstractMachine
    offs: int
    c_ptr: ctypes.POINTER

    py_type: ClassVar[Type]
    c_type: ClassVar[PyCSimpleType]
    _c_ptr_type: ClassVar[Type[ctypes.POINTER]]

    def __class_getitem__(cls, py_type: Type[V]) -> Type[BaseReference[V]]:
        if isinstance(py_type, TypeVar):
            return super().__class_getitem__(py_type)

        if getattr(cls, 'py_type', None) is not None:
            raise TypeError(f'{cls.__name__} already has a type set')

        cls_name = f'{cls.__name__}[{py_type.__name__}]'
        c_type = get_c_type(py_type)
        attrs = {
            'py_type': py_type,
            'c_type': c_type,
            '_c_ptr_type': ctypes.POINTER(c_type),
        }
        return typing.cast(Type[BaseReference], type(cls_name, (cls,), attrs))

    def __new__(cls, *args, **kwargs):
        if getattr(cls, 'py_type', None) is None:
            raise TypeError(f'{cls.__name__} has no type set through subscripting')
        return super().__new__(cls)

    def __init__(self, amx: SourcePawnAbstractMachine, offs: int):
        self.amx = amx
        self.offs = offs

        # The actual pointer to the data, which can be dereferenced to individual items
        self.c_ptr = self._c_ptr_type(self.amx.heap)

        # Pointer to the pointer's address, allowing us to modify that address to point where we wish
        c_ptr_addr = ctypes.cast(ctypes.pointer(self.c_ptr), ctypes.POINTER(ctypes.c_void_p))
        c_ptr_addr.contents.value = self.amx._throw_if_bad_addr(self.offs)


class Array(BaseReference[V]):
    def __getitem__(self, item: int | slice) -> V | List[V]:
        return self.c_ptr[item]

    def __setitem__(self, item: int | slice, value: V | List[V]) -> None:
        if isinstance(item, slice):
            indices = range(*item.indices(len(self)))
            for i, v in zip(indices, value):
                self.c_ptr[i] = v
        else:
            self.c_ptr[item] = value

    def __len__(self) -> int:
        # TODO(zk): allow config of static size
        return self.amx.plugin.memsize - self.offs

    def __iter__(self) -> Iterator[V]:
        for i in range(len(self)):
            yield self[i]


class Pointer(BaseReference[V]):
    def get(self) -> V:
        return self.c_ptr[0]

    def set(self, value: V) -> None:
        self.c_ptr[0] = value
