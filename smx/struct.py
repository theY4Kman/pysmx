from __future__ import division

import ctypes

import six


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


class StructField(object):
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


class StructBase(type(ctypes.Structure)):
    def __new__(cls, cls_name, bases, attrs):
        fields = []
        order = {}
        module = attrs.pop('__module__')
        new_attrs = { '__module__': module }
        for name,value in attrs.items():
            if isinstance(value, StructField):
                fields.append((name, value.ctyp))
                order[name] = value.creation_counter
            else:
                new_attrs[name] = value

        fields = sorted(fields, key=lambda o: order[o[0]])

        if '_fields_' in attrs:
            if isinstance(attrs['_fields_'], list):
                new_attrs['_fields_'] = attrs['_fields_'] + fields
            else:
                raise TypeError('\'_fields_\' must be a list of pairs')
        else:
            new_attrs['_fields_'] = fields

        super_new = super(StructBase, cls).__new__
        new_class = super_new(cls, cls_name, bases, new_attrs)

        return new_class


@six.add_metaclass(StructBase)
class Struct(ctypes.Structure):
    _fields_ = []

    def __repr__(self):
        return '{klass}({fields})'.format(
            klass=self.__class__.__name__,
            fields=', '.join('%s=%r' % (attr, getattr(self, attr))
                             for attr,_ in self._fields_)
        )


class NoAlignStruct(Struct):
    _pack_ = 1


def ctyp_field_init(self, width=None):
    StructField.__init__(self, width=width)

glb = globals()
ctyp_found = []
for name,field_name in zip(__ctypes__, __cftypes__):
    if not hasattr(ctypes, name):
        continue
    ctyp = getattr(ctypes, name)
    field_ctyp = type('_%s_StructField' % name,
        (StructField,), { 'ctyp': ctyp, '__init__': ctyp_field_init })
    glb[field_name] = field_ctyp
    ctyp_found.append(field_name)

__all__ = __static_all__ + ctyp_found
