from __future__ import annotations

import re
from ctypes import c_char, c_char_p
from typing import Any, Dict, List, Sequence, TYPE_CHECKING

from smx import vm
from smx.definitions import (
    cell,
    Myinfo,
    RTTI_VAR_CLASS_ARG,
    RTTI_VAR_CLASS_GLOBAL,
    RTTI_VAR_CLASS_LOCAL,
    RTTI_VAR_CLASS_STATIC,
    SP_NATIVE_BOUND,
    SP_NATIVE_UNBOUND,
    SP_SYM_ARRAY,
    SP_SYM_FUNCTION,
    SP_SYM_REFARRAY,
    SP_SYM_REFERENCE,
    SP_SYM_VARARGS,
    SP_SYM_VARIABLE,
    SPFdbgArrayDim,
)
from smx.rtti import RTTI

if TYPE_CHECKING:
    from smx.plugin import SourcePawnPlugin

RGX_INLINE_NAME = re.compile(r'^\.(\d+)\.(\w+)')


def extract_stringtable(base: bytes, stringbase: int, size: int) -> Dict[int, str]:
    stringtable = {}
    buf = base[stringbase:]
    offset = 0
    while offset <= size:
        s = c_char_p(buf[offset:]).value
        stringtable[offset] = s.decode('utf-8')
        offset += len(s) + 1

    return stringtable


class _PluginChild:
    """A thing that receives a plug-in and other info, and does stuff with it"""

    def __init__(self, plugin: SourcePawnPlugin):
        self.plugin = plugin


class StringtableNameMixin:
    plugin: SourcePawnPlugin
    _name: int

    @property
    def name(self):
        return self.plugin.stringtable.get(self._name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self}>'


class StringtableName(StringtableNameMixin, _PluginChild):
    def __init__(self, plugin, name):
        super().__init__(plugin)
        self._name = name


class PCode(_PluginChild):
    def __init__(self, plugin, pcode, size, version, flags):
        super().__init__(plugin)
        self.pcode = pcode
        self.size = size
        self.version = version
        self.flags = flags


class Public(StringtableName):
    def __init__(self, plugin, code_offs, funcid, name):
        super().__init__(plugin, name)
        self.code_offs = code_offs
        self.funcid = funcid

    def get_function_name(self) -> str:
        if self.name:
            match = RGX_INLINE_NAME.match(self.name)
            if match and int(match.group(1)) == self.code_offs:
                return match.group(2)
        return self.name

    def is_inline(self):
        if self.name:
            match = RGX_INLINE_NAME.match(self.name)
            # XXX: heuristic
            if match and int(match.group(1)) == self.code_offs:
                return True
        return False

    def __str__(self):
        return 'Public function "%s" (id: %d, code_offs: %d)' % (
            self.name, self.funcid, self.code_offs)


class Pubvar(StringtableName):
    def __init__(self, plugin, offs, name):
        super().__init__(plugin, name)
        self.offs = offs

        # Special case for myinfo
        if self.name == 'myinfo':
            # FIXME: this attr dangling off pubvar sucks
            myinfo_offs = Myinfo.parse(self.plugin.base[self.offs:])
            self.myinfo = {
                name: self.plugin._get_data_string(offs)
                for name, offs in vars(myinfo_offs).items()
            }
        else:
            self.myinfo = None

    @property
    def value(self):
        return self.plugin.base[self.offs:]


class Native(StringtableName):
    STATUS_NAMES = {
        SP_NATIVE_BOUND: 'bound',
        SP_NATIVE_UNBOUND: 'unbound'
    }

    def __init__(self, plugin, flags, pfn, status, user, name):
        super().__init__(plugin, name)
        self.flags = flags
        self.pfn = pfn
        self.status = status
        self.user = user

    def __str__(self):
        status = self.STATUS_NAMES.get(self.status, '')
        return ' '.join((status, 'native')).capitalize() + ' "%s"' % self.name


class Tag(StringtableName):
    def __init__(self, plugin, tagid, name):
        super().__init__(plugin, name)
        self.tagid = tagid

    def __str__(self):
        return 'Tag "%s" (id: %d)' % (self.name, self.tagid)


class TypedSymbol:
    def parse_value(self, value: int, amx: vm.SourcePawnAbstractMachine) -> Any | None:
        """Parse the given value using the symbol's typing info"""
        raise value


class RTTITypedSymbol(TypedSymbol):
    rtti: RTTI | None

    def parse_value(self, value: int, amx: vm.SourcePawnAbstractMachine) -> Any | None:
        if self.rtti:
            return self.rtti.interpret_value(value, amx)


class RTTINamedTypedSymbol(RTTITypedSymbol, StringtableNameMixin):
    def __str__(self) -> str:
        if self.rtti:
            return f'{self.name} :: {self.rtti}'
        return self.name


class RTTIEnum(TypedSymbol, StringtableName):
    pass


class RTTIMethod(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, pcode_start: int, pcode_end: int, signature: int):
        super().__init__(plugin, name)
        self.pcode_start = pcode_start
        self.pcode_end = pcode_end
        self.signature = signature

        self.rtti = plugin.rtti_function_from_offset(signature)

        self.associated_locals: Dict[int, RTTIDbgVar] = {}


class RTTINative(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, signature: int):
        super().__init__(plugin, name)

        self.signature = signature
        self.rtti = plugin.rtti_function_from_offset(signature)


class RTTITypedef(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, type_id: int):
        super().__init__(plugin, name)

        self.type_id = type_id
        self.rtti = plugin.rtti_from_type_id(type_id)


class RTTITypeset(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, signature: int):
        super().__init__(plugin, name)

        self.signature = signature
        self.rtti = plugin.rtti_from_type_id(signature)


class RTTIEnumStruct(TypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, fields: List[RTTIEnumStructField]):
        super().__init__(plugin, name)
        self.fields = fields


class RTTIEnumStructField(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, type_id: int, offset: int):
        super().__init__(plugin, name)

        self.type_id = type_id
        self.offset = offset

        self.rtti = plugin.rtti_from_type_id(type_id)


class RTTIClassDef(TypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, flags: int, fields: List[RTTIField]):
        super().__init__(plugin, name)

        self.flags = flags
        self.fields = fields


class RTTIField(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, flags: int, type_id: int):
        super().__init__(plugin, name)

        self.flags = flags
        self.type_id = type_id

        self.rtti = plugin.rtti_from_type_id(type_id)


class DbgFile(StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, addr, name):
        super().__init__(plugin, name)
        self.addr = addr

    def __str__(self):
        return f'{self.name!r} (addr: {hex(self.addr)})'


class DbgLine(_PluginChild):
    def __init__(self, plugin: SourcePawnPlugin, addr, line):
        super().__init__(plugin)
        self.addr = addr
        self.line = line

    @property
    def number(self):
        # Lines are zero-indexed for some reason
        return self.line + 1

    def __str__(self):
        return f'#{self.number:d} (addr: {hex(self.addr)})'

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self}>'


class DbgSymbol(TypedSymbol, StringtableName):
    SYMBOL_TYPE_NAMES = {
        SP_SYM_VARIABLE: 'variable',
        SP_SYM_REFERENCE: 'byref variable',
        SP_SYM_ARRAY: 'array',
        SP_SYM_REFARRAY: 'byref array',
        SP_SYM_FUNCTION: 'function',
        SP_SYM_VARARGS: 'varargs start'
    }

    def __init__(
        self,
        plugin: SourcePawnPlugin,
        addr: int,
        tagid: int,
        codestart: int,
        codeend: int,
        ident: int,
        vclass: int,
        dimcount: int,
        name: int,
        arraydims: Sequence[SPFdbgArrayDim],
    ):
        super().__init__(plugin, name)

        self.addr = addr  # Address rel to DAT or stack frame
        self.tagid = tagid  # Tag id
        self.codestart = codestart  # Start scope validity in code
        self.codeend = codeend  # End scope validity in code
        self.ident = ident  # Variable type
        self.vclass = vclass  # Scope class (local vs global)
        self.dimcount = dimcount  # Dimension count (for arrays)
        self.arraydims = arraydims

    @property
    def tag(self):
        if self.plugin.tags:
            return self.plugin.tags[self.tagid]

    def parse_value(self, value: int, amx: vm.SourcePawnAbstractMachine) -> Any | None:
        """Parse the given value using the symbol's typing info"""
        if not self.tag:
            return None

        tag_name = self.tag.name
        if tag_name == 'Float':
            return amx._sp_ctof(cell(value))
        elif tag_name == 'bool':
            return bool(value)
        elif tag_name == 'String':
            op, args, _, _ = amx._executed[-3]
            assert op == 'stack'
            assert len(args) == 1
            size = int(args[0], 0x10)
            rval = (c_char * size).from_buffer(amx.heap, value).value
            return rval.decode('utf-8')

    def __str__(self):
        tag = self.tag.name
        name = self.name
        suffix = ''
        if self.ident == SP_SYM_FUNCTION:
            suffix = '()'
        elif self.ident == SP_SYM_ARRAY:
            suffix = ''.join('[%d]' % d.size for d in self.arraydims)

        fmt = '.dbg.symbol({tag}:{name}{suffix})'
        return fmt.format(tag=tag, name=name, suffix=suffix)


class RTTIDbgVar(RTTINamedTypedSymbol, StringtableName):
    VCLASS_NAMES = {
        RTTI_VAR_CLASS_GLOBAL: 'global',
        RTTI_VAR_CLASS_LOCAL: 'local',
        RTTI_VAR_CLASS_STATIC: 'static',
        RTTI_VAR_CLASS_ARG: 'arg',
    }

    def __init__(
        self,
        plugin: SourcePawnPlugin,
        address: int,
        vclass: int,
        name: int,
        code_start: int,
        code_end: int,
        type_id: int
    ):
        super().__init__(plugin, name)
        self.address = address
        self.vclass = vclass
        self.vclass_kind = vclass & 0b11
        self.code_start = code_start
        self.code_end = code_end
        self.type_id = type_id

        self.rtti = self.plugin.rtti_from_type_id(self.type_id)

        self.associated_method: RTTIMethod | None = None

    @property
    def is_global(self) -> bool:
        return self.vclass_kind == RTTI_VAR_CLASS_GLOBAL

    def parse_value(self, value: int, amx: vm.SourcePawnAbstractMachine) -> Any | None:
        return self.rtti.interpret_value(value, amx)

    def __str__(self) -> str:
        table_name = 'globals' if self.is_global else 'locals'
        # TODO(zk): typing info
        return f'.dbg.{table_name}({self.name})'
