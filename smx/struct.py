import ctypes
from dataclasses import dataclass
from typing import TypeVar, Type, BinaryIO, Dict, Any, List

import construct as cs
from construct_typed import DataclassMixin, DataclassStruct, Construct

__ctypes__ = [
    'c_bool',
    'c_byte',
    'c_char',
    'c_char_p',
    'c_double',
    'c_float',
    'c_int',
    'c_int16',
    'c_int32',
    'c_int64',
    'c_int8',
    'c_long',
    'c_longdouble',
    'c_longlong',
    'c_short',
    'c_size_t',
    'c_ssize_t',
    'c_ubyte',
    'c_uint',
    'c_uint16',
    'c_uint32',
    'c_uint64',
    'c_uint8',
    'c_ulong',
    'c_ulonglong',
    'c_ushort',
    'c_void_p',
    'c_voidp',
    'c_wchar',
    'c_wchar_p'
]
__cftypes__ = [
    'cf_bool',
    'cf_byte',
    'cf_char',
    'cf_char_p',
    'cf_double',
    'cf_float',
    'cf_int',
    'cf_int16',
    'cf_int32',
    'cf_int64',
    'cf_int8',
    'cf_long',
    'cf_longdouble',
    'cf_longlong',
    'cf_short',
    'cf_size_t',
    'cf_ssize_t',
    'cf_ubyte',
    'cf_uint',
    'cf_uint16',
    'cf_uint32',
    'cf_uint64',
    'cf_uint8',
    'cf_ulong',
    'cf_ulonglong',
    'cf_ushort',
    'cf_void_p',
    'cf_voidp',
    'cf_wchar',
    'cf_wchar_p'
]
__static_all__ = ['StructField', 'field', 'StructBase', 'Struct', 'NoAlignStruct', 'cast_value']
__all__ = __cftypes__ + __static_all__


# We can't import this directly, so grab it from any C type
PyCSimpleType = type(ctypes.c_byte)


def cast_value(ctyp, value):
    return ctypes.cast(value, ctypes.POINTER(ctyp)).contents.value


class StructField:
    creation_counter = 0

    def __init__(self, ctyp=None, width=None):
        if ctyp is not None and not hasattr(self, 'ctyp'):
            if type(ctyp) == StructField:
                self.ctyp = ctyp.ctyp
            elif type(ctyp) != PyCSimpleType:
                raise TypeError('Struct field must be passed a ctype')
            else:
                self.ctyp = ctyp

        elif not hasattr(self, 'ctyp'):
            raise ValueError('ctyp must be passed to a vanilla StructField')

        self.width = width

        self.creation_counter = StructField.creation_counter
        StructField.creation_counter += 1


field = StructField


class StructBase(type(ctypes.LittleEndianStructure)):
    def __new__(cls, cls_name, bases, attrs):
        fields = []
        order = {}
        module = attrs.pop('__module__')
        new_attrs = {'__module__': module}
        for name, value in attrs.items():
            if isinstance(value, StructField):
                fields.append((name, value.ctyp))
                order[name] = value.creation_counter
            else:
                new_attrs[name] = value

        fields = sorted(fields, key=lambda o: order[o[0]])

        for base in bases:
            if hasattr(base, '_fields_'):
                fields = base._fields_ + fields

        new_attrs['_fields_'] = fields

        super_new = super(StructBase, cls).__new__
        new_class = super_new(cls, cls_name, bases, new_attrs)

        return new_class


class Struct(ctypes.LittleEndianStructure, metaclass=StructBase):
    _fields_ = []

    def __repr__(self):
        return '{klass}({fields})'.format(
            klass=self.__class__.__name__,
            fields=', '.join('%s=%r' % (attr, getattr(self, attr))
                             for attr, _ in self._fields_)
        )


class NoAlignStruct(Struct):
    _pack_ = 1


def ctyp_field_init(self, width=None):
    StructField.__init__(self, width=width)


_TYPED_STRUCT_AS_STRUCT_KEY = '__struct'

StructT = TypeVar('StructT', bound='Struct')


class _ConStructMeta(type):
    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        cls = dataclass(cls)
        return cls


class ConStruct(DataclassMixin, metaclass=_ConStructMeta):
    @classmethod
    def as_struct(cls) -> cs.Struct:
        if not hasattr(cls, _TYPED_STRUCT_AS_STRUCT_KEY):
            setattr(cls, _TYPED_STRUCT_AS_STRUCT_KEY, DataclassStruct(cls))
        return getattr(cls, _TYPED_STRUCT_AS_STRUCT_KEY)

    @classmethod
    def build(cls: Type[StructT], obj: StructT, **contextkw) -> bytes:
        return cls.as_struct().build(obj, **contextkw)

    @classmethod
    def build_stream(cls: Type[StructT], obj: StructT, stream: BinaryIO, **contextkw) -> None:
        cls.as_struct().build_stream(obj, stream, **contextkw)

    @classmethod
    def parse(cls: Type[StructT], data: bytes, **contextkw) -> StructT:
        return cls.as_struct().parse(data, **contextkw)

    @classmethod
    def parse_stream(cls: Type[StructT], stream: BinaryIO, **contextkw) -> StructT:
        return cls.as_struct().parse_stream(stream, **contextkw)

    def __class_getitem__(cls, count) -> Construct:
        return cls.as_struct()[count]

    @classmethod
    def sizeof(cls, **contextkw) -> int:
        return cls.as_struct().sizeof(**contextkw)


def _init_ctype_fields(glb: Dict[str, Any]) -> List[str]:
    ctypes_found = []
    for name, field_name in zip(__ctypes__, __cftypes__):
        if not hasattr(ctypes, name):
            continue
        ctyp = getattr(ctypes, name)
        field_ctyp = type('_%s_StructField' % name,
                          (StructField,), {'ctyp': ctyp, '__init__': ctyp_field_init})
        glb[field_name] = field_ctyp
        ctypes_found.append(field_name)

    return ctypes_found


__all__ = __static_all__ + _init_ctype_fields(globals()) + ['ConStruct']
