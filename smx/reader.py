from __future__ import annotations

import io
import re
import zlib
from ctypes import c_char, c_char_p
from typing import Any, Dict, List

from smx import vm
from smx.definitions import (
    cell,
    Myinfo,
    RTTI_TYPE_ID_COMPLEX,
    RTTI_TYPE_ID_INLINE,
    RTTI_VAR_CLASS_ARG,
    RTTI_VAR_CLASS_GLOBAL,
    RTTI_VAR_CLASS_LOCAL,
    RTTI_VAR_CLASS_STATIC,
    SmxRTTIClassDefTable,
    SmxRTTIDebugMethodTable,
    SmxRTTIDebugVarTable,
    SmxRTTIEnumStructFieldTable,
    SmxRTTIEnumStructTable,
    SmxRTTIEnumTable,
    SmxRTTIFieldTable,
    SmxRTTIMethodTable,
    SmxRTTINativeTable,
    SmxRTTITypedefTable,
    SmxRTTITypesetTable,
    SP1_VERSION_1_0,
    SP1_VERSION_1_1,
    SP1_VERSION_1_7,
    SP_CODEVERS_ALWAYS_REJECT,
    SP_CODEVERS_CURRENT,
    SP_CODEVERS_MINIMUM,
    SP_FLAG_DEBUG,
    SP_NATIVE_BOUND,
    SP_NATIVE_UNBOUND,
    SP_SYM_ARRAY,
    SP_SYM_FUNCTION,
    SP_SYM_REFARRAY,
    SP_SYM_REFERENCE,
    SP_SYM_VARARGS,
    SP_SYM_VARIABLE,
    SPFdbgFile,
    SPFdbgInfo,
    SPFdbgLine,
    SPFdbgNative,
    SPFdbgNtvTab,
    SPFdbgSymbol,
    SPFILE_COMPRESSION_GZ,
    SPFILE_COMPRESSION_NONE,
    SPFILE_MAGIC,
    SPFileCode,
    SPFileData,
    SPFileHdr,
    SPFileNatives,
    SPFilePublics,
    SPFilePubvars,
    SPFileSection,
    SPFileTag,
)
from smx.exceptions import (
    SourcePawnPluginError,
    SourcePawnPluginFormatError,
    SourcePawnPluginNativeError,
)
from smx.rtti import parse_type_id, RTTI, RTTIParser

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


def _invalid_native():
    raise SourcePawnPluginNativeError("Invalid native")


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
        super(StringtableName, self).__init__(plugin)
        self._name = name


class PCode(_PluginChild):
    def __init__(self, plugin, pcode, size, version, flags):
        super(PCode, self).__init__(plugin)
        self.pcode = pcode
        self.size = size
        self.version = version
        self.flags = flags


class Public(StringtableName):
    def __init__(self, plugin, code_offs, funcid, name):
        super(Public, self).__init__(plugin, name)
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
        super(Pubvar, self).__init__(plugin, name)
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
        super(Native, self).__init__(plugin, name)
        self.flags = flags
        self.pfn = pfn
        self.status = status
        self.user = user

    def __str__(self):
        status = self.STATUS_NAMES.get(self.status, '')
        return ' '.join((status, 'native')).capitalize() + ' "%s"' % self.name


class Tag(StringtableName):
    def __init__(self, plugin, tagid, name):
        super(Tag, self).__init__(plugin, name)
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
        super(RTTIMethod, self).__init__(plugin, name)
        self.pcode_start = pcode_start
        self.pcode_end = pcode_end
        self.signature = signature

        self.rtti = plugin.rtti_function_from_offset(signature)

        self.associated_locals: Dict[int, RTTIDbgVar] = {}


class RTTINative(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, signature: int):
        super(RTTINative, self).__init__(plugin, name)

        self.signature = signature
        self.rtti = plugin.rtti_function_from_offset(signature)


class RTTITypedef(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, type_id: int):
        super(RTTITypedef, self).__init__(plugin, name)

        self.type_id = type_id
        self.rtti = plugin.rtti_from_type_id(type_id)


class RTTITypeset(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, signature: int):
        super(RTTITypeset, self).__init__(plugin, name)

        self.signature = signature
        self.rtti = plugin.rtti_from_type_id(signature)


class RTTIEnumStruct(TypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, fields: List[RTTIEnumStructField]):
        super(RTTIEnumStruct, self).__init__(plugin, name)
        self.fields = fields


class RTTIEnumStructField(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, type_id: int, offset: int):
        super(RTTIEnumStructField, self).__init__(plugin, name)

        self.type_id = type_id
        self.offset = offset

        self.rtti = plugin.rtti_from_type_id(type_id)


class RTTIClassDef(TypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, flags: int, fields: List[RTTIField]):
        super(RTTIClassDef, self).__init__(plugin, name)

        self.flags = flags
        self.fields = fields


class RTTIField(RTTINamedTypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, flags: int, type_id: int):
        super(RTTIField, self).__init__(plugin, name)

        self.flags = flags
        self.type_id = type_id

        self.rtti = plugin.rtti_from_type_id(type_id)


class _DbgChild:
    """A shathingermabob that does stuff with the PluginDebug class"""

    def __init__(self, debug: PluginDebug):
        self.debug = debug

    @property
    def plugin(self) -> SourcePawnPlugin:
        return self.debug.plugin


class DbgFile(_DbgChild):
    def __init__(self, debug, addr, name):
        super(DbgFile, self).__init__(debug)
        self.addr = addr
        self._name = name

    @property
    def name(self):
        return self.debug.stringtable.get(self._name)

    def __str__(self):
        return 'DbgFile "%s" (addr: %d)' % (self.name, self.addr)


class DbgLine(_DbgChild):
    def __init__(self, debug, addr, line):
        super(DbgLine, self).__init__(debug)
        self.addr = addr
        self.line = line

    def __str__(self):
        return 'DbgLine #%d (addr: %d)' % (self.line, self.addr)


class DbgSymbol(TypedSymbol, _DbgChild):
    SYMBOL_TYPE_NAMES = {
        SP_SYM_VARIABLE: 'variable',
        SP_SYM_REFERENCE: 'byref variable',
        SP_SYM_ARRAY: 'array',
        SP_SYM_REFARRAY: 'byref array',
        SP_SYM_FUNCTION: 'function',
        SP_SYM_VARARGS: 'varargs start'
    }

    def __init__(self, debug, addr, tagid, codestart, codeend, ident,
                 vclass, dimcount, name, arraydims):
        super(DbgSymbol, self).__init__(debug)

        self.addr = addr  # Address rel to DAT or stack frame
        self.tagid = tagid  # Tag id
        self.codestart = codestart  # Start scope validity in code
        self.codeend = codeend  # End scope validity in code
        self.ident = ident  # Variable type
        self.vclass = vclass  # Scope class (local vs global)
        self.dimcount = dimcount  # Dimension count (for arrays)
        self.arraydims = arraydims
        self._name = name

    @property
    def name(self):
        return self.debug.stringtable.get(self._name)

    @property
    def tag(self):
        if self.debug.plugin.tags:
            return self.debug.plugin.tags[self.tagid]

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


class RTTIDbgVar(RTTINamedTypedSymbol, StringtableNameMixin, _DbgChild):
    VCLASS_NAMES = {
        RTTI_VAR_CLASS_GLOBAL: 'global',
        RTTI_VAR_CLASS_LOCAL: 'local',
        RTTI_VAR_CLASS_STATIC: 'static',
        RTTI_VAR_CLASS_ARG: 'arg',
    }

    def __init__(
        self,
        debug: PluginDebug,
        address: int,
        vclass: int,
        name: int,
        code_start: int,
        code_end: int,
        type_id: int
    ):
        super(RTTIDbgVar, self).__init__(debug)
        self.address = address
        self.vclass = vclass
        self.vclass_kind = vclass & 0b11
        self._name = name
        self.code_start = code_start
        self.code_end = code_end
        self.type_id = type_id

        self.rtti = self.debug.plugin.rtti_from_type_id(self.type_id)

        self.associated_method: RTTIMethod | None = None

    @property
    def is_global(self) -> bool:
        return self.vclass_kind == RTTI_VAR_CLASS_GLOBAL

    @property
    def name(self):
        return self.debug.plugin.stringtable.get(self._name)

    def parse_value(self, value: int, amx: vm.SourcePawnAbstractMachine) -> Any | None:
        return self.rtti.interpret_value(value, amx)

    def __str__(self) -> str:
        table_name = 'globals' if self.is_global else 'locals'
        # TODO(zk): typing info
        return f'.dbg.{table_name}({self.name})'


class PluginDebug(_PluginChild):
    def __init__(self, plugin: SourcePawnPlugin):
        super(PluginDebug, self).__init__(plugin)

        self.unpacked = False
        self.stringbase = None
        self.stringtable = {}

        self.files: List[DbgFile] = []
        self.lines: List[DbgLine] = []
        self.symbols: List[DbgSymbol] = []
        self.vars: List[RTTIDbgVar] = []
        self.globals: List[RTTIDbgVar] = []
        self.locals: List[RTTIDbgVar] = []
        self.natives: Dict[int, SPFdbgNative] = {}
        self.symbols_by_addr: Dict[int, TypedSymbol] = {}

    def extract_stringtable(self, size: int, stringbase: bytes | None = None):
        if stringbase is None:
            stringbase = self.stringbase
        if stringbase is None:
            raise ValueError('Invalid stringbase')

        self.stringtable = extract_stringtable(self.plugin.base, stringbase, size)
        return self.stringtable

    def _get_string(self, offset: int):
        if self.stringbase is None:
            raise SourcePawnPluginError(
                'No debug stringbase to grab strings from')
        return c_char_p(self.plugin.base[self.stringbase + offset:]).value

    def _add_file(self, addr, name):
        file = DbgFile(self, addr, name)
        self.files.append(file)
        return file

    def _add_line(self, addr, line):
        line = DbgLine(self, addr, line)
        self.lines.append(line)
        return line

    def _add_symbol(
        self, addr, tagid, codestart, codeend, ident, vclass, dimcount, name, arraydims=()
    ):
        symbol = DbgSymbol(self, addr, tagid, codestart, codeend, ident, vclass, dimcount, name, arraydims)
        self.symbols.append(symbol)
        self.symbols_by_addr[addr] = symbol
        return symbol


class SourcePawnPlugin:
    def __init__(self, filelike=None, **runtime_options):
        self.runtime_options = runtime_options

        self.name: str = '<unnamed>'
        self.debug: PluginDebug = PluginDebug(self)
        self.filled: bool = False

        self.base: bytes | None = None
        self.stringbase: int | None = None
        self.stringtable: Dict[int, str] | None = None
        self.stringtab: int | None = None

        self.data: int | None = None
        self.datasize: int | None = None
        self.memsize: int | None = None
        self.pcode: PCode | None = None

        self.rtti_data: bytes | None = None

        self.rtti_enums: List[RTTIEnum] = []
        self.rtti_enums_by_name: Dict[str, RTTIEnum] = {}

        self.rtti_methods: List[RTTIMethod] = []
        self.rtti_methods_by_name: Dict[str, RTTIMethod] = {}
        self.rtti_methods_by_addr: Dict[int, RTTIMethod] = {}

        self.rtti_natives: List[RTTINative] = []
        self.rtti_natives_by_name: Dict[str, RTTINative] = {}

        self.rtti_typedefs: List[RTTITypedef] = []
        self.rtti_typedefs_by_name: Dict[str, RTTITypedef] = {}

        self.rtti_typesets: List[RTTITypeset] = []
        self.rtti_typesets_by_name: Dict[str, RTTITypeset] = {}

        self.rtti_enum_struct_fields: List[RTTIEnumStructField] = []
        self.rtti_enum_structs: List[RTTIEnumStruct] = []
        self.rtti_enum_structs_by_name: Dict[str, RTTIEnumStruct] = {}

        self.rtti_fields: List[RTTIField] = []
        self.rtti_class_defs: List[RTTIClassDef] = []
        self.rtti_class_defs_by_name: Dict[str, RTTIClassDef] = {}

        self.tags: Dict[int, Tag] = {}
        self.inlines: Dict[str, Public] = {}
        self.publics: Dict[str, Public] = {}
        self.publics_by_offs: Dict[int, Public] = {}
        self.pubvars: List[Pubvar] = []
        self.natives: Dict[str, Native] = {}

        self.num_tags: int = 0
        self.num_publics: int = 0
        self.num_pubvars: int = 0
        self.num_natives: int = 0

        self._runtime: vm.SourcePawnPluginRuntime | None = None
        self.myinfo: Myinfo | None = None

        if filelike is not None:
            self.extract_from_buffer(filelike)

    def __str__(self):
        if self.myinfo:
            return self.myinfo['name'] + ' by ' + self.myinfo['author']
        if self.name:
            return self.name
        if self.filled:
            return 'Nameless SourcePawn Plug-in'
        return 'Empty SourcePawn Plug-in'

    @property
    def runtime(self):
        if self._runtime is None:
            self._runtime = vm.SourcePawnPluginRuntime(self, **self.runtime_options)
        return self._runtime

    @runtime.setter
    def runtime(self, value):
        self._runtime = value

    def run(self):
        self.runtime.run()

    @property
    def flags(self):
        if self.pcode is None:
            raise AttributeError(f"{type(self)} instance has no attribute 'flags'")
        return self.pcode.flags

    @flags.setter
    def flags(self, value):
        if self.pcode is None:
            raise AttributeError(f"{type(self)} instance has no attribute 'flags'")
        self.pcode.flags = value

    def _get_data_string(self, dataoffset: int) -> str:
        return c_char_p(self.base[self.data + dataoffset:]).value.decode('utf8')

    def _get_data_char(self, dataoffset: int) -> int:
        return c_char_p(self.base[self.data + dataoffset:]).value[0]

    def _get_string(self, stroffset: int) -> str:
        return c_char_p(self.base[self.stringbase + stroffset:]).value.decode('utf8')

    def rtti_from_type_id(self, type_id: int) -> RTTI | None:
        if self.rtti_data is None:
            raise SourcePawnPluginError('No RTTI data to grab types from')

        kind, payload = parse_type_id(type_id)

        if kind == RTTI_TYPE_ID_INLINE:
            parser = RTTIParser(self, payload.to_bytes(4, 'little', signed=False), 0)
            return parser.decode_new()

        elif kind == RTTI_TYPE_ID_COMPLEX:
            parser = self.rtti_parser_from_offset(payload)
            return parser.decode_new()

    def rtti_function_from_offset(self, offset: int) -> RTTI | None:
        if self.rtti_data is None:
            raise SourcePawnPluginError('No RTTI data to grab types from')

        parser = self.rtti_parser_from_offset(offset)
        return parser.decode_function()

    def rtti_parser_from_offset(self, offset: int) -> RTTIParser:
        if self.rtti_data is None:
            raise SourcePawnPluginError('No RTTI data to grab types from')

        return RTTIParser(self, self.rtti_data, offset)

    def find_method_by_addr(self, addr: int) -> RTTIMethod | None:
        meth = self.rtti_methods_by_addr.get(addr)
        if meth:
            return meth

        for meth in self.rtti_methods:
            if meth.pcode_start <= addr <= meth.pcode_end:
                return meth

    # TODO(zk): split me up, jesus
    def extract_from_buffer(self, fp):
        if isinstance(fp, io.IOBase) and hasattr(fp, 'name'):
            self.name = fp.name

        hdr = SPFileHdr.parse_stream(fp)

        if hdr.magic != SPFILE_MAGIC:
            raise SourcePawnPluginFormatError(
                f'Invalid magic number 0x{hdr.magic:08x} (expected 0x{SPFILE_MAGIC:08x})')

        if hdr.version not in (SP1_VERSION_1_0, SP1_VERSION_1_1, SP1_VERSION_1_7):
            raise SourcePawnPluginFormatError(f'Unspported version number 0x{hdr.version:04x}')

        if hdr.version == 0x0101:
            self.debug.unpacked = True

        self.stringtab = hdr.stringtab

        _hdr_size = hdr.sizeof()
        if hdr.compression == SPFILE_COMPRESSION_GZ:
            uncompsize = hdr.imagesize - hdr.dataoffs
            compsize = hdr.disksize - hdr.dataoffs
            sectsize = hdr.dataoffs - _hdr_size

            sectheader = fp.read(sectsize)
            compdata = fp.read(compsize)
            fp.seek(0)
            fileheader = fp.read(_hdr_size)

            uncompdata = zlib.decompress(compdata, 15, uncompsize)
            base = fileheader + sectheader + uncompdata

        elif hdr.compression == SPFILE_COMPRESSION_NONE:
            fp.seek(0)
            base = fp.read()

        else:
            raise SourcePawnPluginError('Invalid compression type %d' %
                                        hdr.compression)

        self.base = base

        _sections = SPFileSection[hdr.sections].parse(base[_hdr_size:])

        sections = {}
        for sect in _sections[:hdr.sections]:
            name = c_char_p(self.base[self.stringtab + sect.nameoffs:]).value
            name = name.decode('utf-8')
            sections[name] = sect

        if '.names' in sections:
            sect = sections['.names']
            self.stringbase = sect.dataoffs
            self.stringtable = extract_stringtable(self.base, sect.dataoffs, sect.size)
        else:
            raise SourcePawnPluginError('Could not locate string base')

        if '.code' in sections:
            sect = sections['.code']
            cod = SPFileCode.parse(self.base[sect.dataoffs:])

            if cod.codeversion < SP_CODEVERS_MINIMUM:
                raise SourcePawnPluginFormatError(
                    "Code version %d is too old" % cod.codeversion)
            elif cod.codeversion == SP_CODEVERS_ALWAYS_REJECT:
                raise SourcePawnPluginFormatError(
                    "Code version %d is not supported" % cod.codeversion)
            elif cod.codeversion > SP_CODEVERS_CURRENT:
                raise SourcePawnPluginFormatError(
                    "Code version %d is too new" % cod.codeversion)

            pcode = hdr.dataoffs + cod.code
            self.pcode = PCode(self, pcode, cod.codesize, cod.codeversion, cod.flags)
        else:
            raise SourcePawnPluginFormatError('.code section not found!')

        if '.data' in sections:
            sect = sections['.data']
            dat = SPFileData.parse(self.base[sect.dataoffs:])
            self.data = sect.dataoffs + dat.data
            self.datasize = dat.datasize
            self.memsize = dat.memsize
        else:
            raise SourcePawnPluginFormatError('.data section not found!')

        if '.tags' in sections:
            sect = sections['.tags']

            self.num_tags = sect.size // SPFileTag.sizeof()
            tags = SPFileTag[self.num_tags].parse(self.base[sect.dataoffs:])

            for index, tag in enumerate(tags[:self.num_tags]):
                self.tags[index] = Tag(self, tag.tag_id, tag.name)

        # Functions defined as public
        if '.publics' in sections:
            sect = sections['.publics']

            self.num_publics = sect.size // SPFilePublics.sizeof()
            publics = SPFilePublics[self.num_publics].parse(self.base[sect.dataoffs:])

            for i, pub in enumerate(publics[:self.num_publics]):
                code_offs = pub.address
                funcid = (i << 1) | 1
                pub = Public(self, code_offs, funcid, pub.name)
                self.publics[pub.name] = pub
                self.publics_by_offs[code_offs] = pub

                if pub.is_inline():
                    self.inlines[pub.get_function_name()] = pub

        # Variables defined as public, most importantly myinfo
        if '.pubvars' in sections:
            sect = sections['.pubvars']

            self.num_pubvars = sect.size // SPFilePubvars.sizeof()
            pubvars = SPFilePubvars[self.num_pubvars].parse(self.base[sect.dataoffs:])

            for pubvar in pubvars[:self.num_pubvars]:
                offs = self.data + pubvar.address
                pubvar = Pubvar(self, offs, pubvar.name)
                self.pubvars.append(pubvar)

                if pubvar.name == 'myinfo':
                    self.myinfo = pubvar.myinfo
                    self.name = self.myinfo['name']

        if '.natives' in sections:
            sect = sections['.natives']

            self.num_natives = sect.size // SPFileNatives.sizeof()
            natives = SPFileNatives[self.num_natives].parse(self.base[sect.dataoffs:])

            for native in natives[:self.num_natives]:
                native = Native(self, 0, _invalid_native, SP_NATIVE_UNBOUND, None, native.name)
                self.natives[native.name] = native

        if '.dbg.strings' in sections:
            sect = sections['.dbg.strings']
            self.debug.stringbase = sect.dataoffs
            self.debug.extract_stringtable(sect.size)

        if '.dbg.info' in sections:
            sect = sections['.dbg.info']
            inf = SPFdbgInfo.parse(self.base[sect.dataoffs:])
            self.debug.info = inf

        if '.dbg.natives' in sections:
            sect = sections['.dbg.natives']

            ntvtab = SPFdbgNtvTab.parse(self.base[sect.dataoffs:])
            for native in ntvtab.natives:
                self.debug.natives[native.index] = native

        if '.dbg.files' in sections:
            sect = sections['.dbg.files']

            num_dbg_files = sect.size // SPFdbgFile.sizeof()
            files = SPFdbgFile[num_dbg_files].parse(self.base[sect.dataoffs:])

            for dbg_file in files:
                self.debug._add_file(dbg_file.addr, dbg_file.name)

        if '.dbg.lines' in sections:
            sect = sections['.dbg.lines']

            num_dbg_lines = sect.size // SPFdbgLine.sizeof()
            lines = SPFdbgLine[num_dbg_lines].parse(self.base[sect.dataoffs:])

            for line in lines:
                self.debug._add_line(
                    addr=line.addr,
                    line=line.line,
                )

        if '.dbg.symbols' in sections:
            sect = sections['.dbg.symbols']

            i = 0
            while i < sect.size:
                sym = SPFdbgSymbol.parse(self.base[sect.dataoffs + i:])
                i += SPFdbgSymbol.sizeof()

                self.debug._add_symbol(
                    addr=sym.addr,
                    tagid=sym.tagid,
                    codestart=sym.codestart,
                    codeend=sym.codeend,
                    ident=sym.ident,
                    vclass=sym.vclass,
                    dimcount=sym.dimcount,
                    name=sym.name,
                    arraydims=sym.dims,
                )

        if 'rtti.data' in sections:
            sect = sections['rtti.data']
            self.rtti_data = self.base[sect.dataoffs:sect.dataoffs + sect.size]

        if 'rtti.enums' in sections:
            sect = sections['rtti.enums']
            enums_table = SmxRTTIEnumTable.parse(self.base[sect.dataoffs:])

            for enum in enums_table.enums:
                rtti_enum = RTTIEnum(plugin=self, name=enum.name)
                self.rtti_enums.append(rtti_enum)
                self.rtti_enums_by_name[rtti_enum.name] = rtti_enum

        # TODO(zk): require rtti.methods and rtti.natives

        if 'rtti.methods' in sections:
            sect = sections['rtti.methods']
            methods_table = SmxRTTIMethodTable.parse(self.base[sect.dataoffs:])

            for entry in methods_table.methods:
                rtti_method = RTTIMethod(
                    plugin=self,
                    name=entry.name,
                    pcode_start=entry.pcode_start,
                    pcode_end=entry.pcode_end,
                    signature=entry.signature,
                )
                self.rtti_methods.append(rtti_method)
                self.rtti_methods_by_name[rtti_method.name] = rtti_method
                self.rtti_methods_by_addr[entry.pcode_start] = rtti_method
                self.debug.symbols_by_addr[entry.pcode_start] = rtti_method

        if 'rtti.natives' in sections:
            sect = sections['rtti.natives']
            natives_table = SmxRTTINativeTable.parse(self.base[sect.dataoffs:])

            for native in natives_table.natives:
                rtti_native = RTTINative(
                    plugin=self,
                    name=native.name,
                    signature=native.signature,
                )
                self.rtti_natives.append(rtti_native)
                self.rtti_natives_by_name[rtti_native.name] = rtti_native

        if 'rtti.typedefs' in sections:
            sect = sections['rtti.typedefs']
            typedefs_table = SmxRTTITypedefTable.parse(self.base[sect.dataoffs:])

            for typedef in typedefs_table.typedefs:
                rtti_typedef = RTTITypedef(
                    plugin=self,
                    name=typedef.name,
                    type_id=typedef.type_id,
                )
                self.rtti_typedefs.append(rtti_typedef)
                self.rtti_typedefs_by_name[rtti_typedef.name] = rtti_typedef

        if 'rtti.typesets' in sections:
            sect = sections['rtti.typesets']
            typesets_table = SmxRTTITypesetTable.parse(self.base[sect.dataoffs:])

            for typeset in typesets_table.typesets:
                rtti_typeset = RTTITypeset(
                    plugin=self,
                    name=typeset.name,
                    signature=typeset.signature,
                )
                self.rtti_typesets.append(rtti_typeset)
                self.rtti_typesets_by_name[rtti_typeset.name] = rtti_typeset

        if 'rtti.enumstructs' in sections:
            if 'rtti.es_fields' not in sections:
                raise SourcePawnPluginFormatError('rtti.es_fields section is missing, but required by rtti.enumstructs')

            sect = sections['rtti.es_fields']
            es_fields_table = SmxRTTIEnumStructFieldTable.parse(self.base[sect.dataoffs:])
            for es_field in es_fields_table.fields:
                rtti_es_field = RTTIEnumStructField(
                    plugin=self,
                    name=es_field.name,
                    type_id=es_field.type_id,
                    offset=es_field.offset,
                )
                self.rtti_enum_struct_fields.append(rtti_es_field)

            sect = sections['rtti.enumstructs']
            enumstructs_table = SmxRTTIEnumStructTable.parse(self.base[sect.dataoffs:])

            last_fields = (
                [e.first_field for e in enumstructs_table.enumstructs[1:]] + [len(self.rtti_enum_struct_fields)]
            )
            for enumstruct, last_field in zip(enumstructs_table.enumstructs, last_fields):
                rtti_enum_struct = RTTIEnumStruct(
                    plugin=self,
                    name=enumstruct.name,
                    fields=self.rtti_enum_struct_fields[enumstruct.first_field:last_field],
                )
                self.rtti_enum_structs.append(rtti_enum_struct)
                self.rtti_enum_structs_by_name[rtti_enum_struct.name] = rtti_enum_struct

        if 'rtti.classdef' in sections:
            if 'rtti.fields' not in sections:
                raise SourcePawnPluginFormatError('rtti.fields section is missing, but required by rtti.classdef')

            sect = sections['rtti.fields']
            fields_table = SmxRTTIFieldTable.parse(self.base[sect.dataoffs:])

            for field in fields_table.fields:
                rtti_field = RTTIField(
                    plugin=self,
                    name=field.name,
                    flags=field.flags,
                    type_id=field.type_id,
                )
                self.rtti_fields.append(rtti_field)

            sect = sections['rtti.classdef']
            classdef_table = SmxRTTIClassDefTable.parse(self.base[sect.dataoffs:])

            last_fields = (
                [c.first_field for c in classdef_table.classdefs[1:]] + [len(self.rtti_fields)]
            )
            for classdef, last_field in zip(classdef_table.classdefs, last_fields):
                rtti_classdef = RTTIClassDef(
                    plugin=self,
                    name=classdef.name,
                    flags=classdef.flags,
                    fields=self.rtti_fields[classdef.first_field:last_field],
                )
                self.rtti_class_defs.append(rtti_classdef)
                self.rtti_class_defs_by_name[rtti_classdef.name] = rtti_classdef

        for dbg_var_sect_name in ('.dbg.globals', '.dbg.locals'):
            if dbg_var_sect_name not in sections:
                continue

            sect = sections[dbg_var_sect_name]
            vars_tab = SmxRTTIDebugVarTable.parse(self.base[sect.dataoffs:])

            for var in vars_tab.vars:
                rtti_var = RTTIDbgVar(
                    self.debug,
                    address=var.address,
                    vclass=var.vclass,
                    name=var.name,
                    code_start=var.code_start,
                    code_end=var.code_end,
                    type_id=var.type_id,
                )

                self.debug.vars.append(rtti_var)
                if rtti_var.is_global:
                    self.debug.globals.append(rtti_var)
                else:
                    self.debug.locals.append(rtti_var)
                self.debug.symbols_by_addr[rtti_var.address] = rtti_var

        if '.dbg.methods' in sections:
            sect = sections['.dbg.methods']
            debug_methods_table = SmxRTTIDebugMethodTable.parse(self.base[sect.dataoffs:])

            last_locals = (
                [m.first_local for m in debug_methods_table.methods[1:]] + [len(self.debug.locals)]
            )
            for entry, last_local in zip(debug_methods_table.methods, last_locals):
                rtti_method = self.rtti_methods[entry.method_index]
                rtti_locals = self.debug.locals[entry.first_local:last_local]
                for rtti_var in rtti_locals:
                    rtti_var.associated_method = rtti_method
                    rtti_method.associated_locals[rtti_var.address] = rtti_var

        if self.flags & SP_FLAG_DEBUG and (self.debug.files is None or
                                           self.debug.lines is None or
                                           self.debug.symbols_by_addr is None):
            raise SourcePawnPluginFormatError(
                'Debug flag found, but debug information incomplete')

        self.filled = True
