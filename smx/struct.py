import ctypes
from dataclasses import dataclass
from typing import BinaryIO, Type, TypeVar

import construct as cs
from construct_typed import Construct, DataclassMixin, DataclassStruct

__all__ = ['Struct', 'cast_value']

StructT = TypeVar('StructT', bound='Struct')


_TYPED_STRUCT_AS_STRUCT_KEY = '__struct'


def cast_value(ctyp, value):
    return ctypes.cast(value, ctypes.POINTER(ctyp)).contents.value


class _StructMeta(type):
    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        cls = dataclass(cls)
        return cls


class Struct(DataclassMixin, metaclass=_StructMeta):
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
