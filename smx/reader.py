from __future__ import annotations

import io
import re
import zlib
from collections import defaultdict
from ctypes import c_char, c_char_p
from typing import Any, Dict, List, Type

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
    SmxRTTIDebugVarTable,
    SmxRTTIMethodTable,
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
    SPFdbgArrayDim,
    SPFdbgFile,
    SPFdbgInfo,
    SPFdbgLine,
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
from smx.struct import ConStruct

RGX_INLINE_NAME = re.compile(r'^\.(\d+)\.(\w+)')


def _extract_strings(buffer, num_strings=1):
    strings = []
    offset = 0
    for i in range(num_strings):
        s = c_char_p(buffer[offset:]).value
        strings.append(s)
        offset += len(s)+1
    return tuple(strings)


def _extract_strings_size(buffer, size=0):
    strings = []
    offset = 0
    while offset < size:
        s = c_char_p(buffer[offset:]).value
        strings.append(s)
        offset += len(s)+1
    return tuple(strings)


def extract_stringtable(base, stringbase, size):
    stringtable = {}
    buf = base[stringbase:]
    offset = 0
    while offset <= size:
        s = c_char_p(buf[offset:]).value
        stringtable[offset] = s.decode('utf-8')
        offset += len(s)+1

    return stringtable


def _invalid_native():
    raise SourcePawnPluginNativeError("Invalid native")


class _PluginChild:
    """A thing that receives a plug-in and other info, and does stuff with it"""
    def __init__(self, plugin: SourcePawnPlugin):
        self.plugin = plugin


class StringtableName(_PluginChild):
    def __init__(self, plugin, name):
        super(StringtableName, self).__init__(plugin)
        self._name = name

    @property
    def name(self):
        return self.plugin.stringtable.get(self._name)


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

    def __str__(self):
        return 'Pubvar "%s" (offs: %d)' % (self.name, self.offs)

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
    def parse_value(self, value: int, spvm: vm.SourcePawnAbstractMachine) -> Any | None:
        """Parse the given value using the symbol's typing info"""
        raise NotImplementedError


class RTTIMethod(TypedSymbol, StringtableName):
    def __init__(self, plugin: SourcePawnPlugin, name: int, pcode_start: int, pcode_end: int, signature: int):
        super(RTTIMethod, self).__init__(plugin, name)
        self.pcode_start = pcode_start
        self.pcode_end = pcode_end
        self._signature = signature

        self.rtti = plugin.rtti_from_type_id(signature)

    def __str__(self):
        # TODO(zk): add signature
        return f'Method "{self.name}" [{self.pcode_start}:{self.pcode_end}]'

    def parse_value(self, value: int, spvm: vm.SourcePawnAbstractMachine) -> Any | None:
        if self.rtti:
            return self.rtti.interpret_value(value, spvm)


class _DbgChild:
    """A shathingermabob that does stuff with the PluginDebug class"""

    def __init__(self, debug: PluginDebug):
        self.debug = debug


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

    def parse_value(self, value: int, spvm: vm.SourcePawnAbstractMachine) -> Any | None:
        """Parse the given value using the symbol's typing info"""
        if not self.tag:
            return None

        tag_name = self.tag.name
        if tag_name == 'Float':
            return spvm._sp_ctof(cell(value))
        elif tag_name == 'bool':
            return bool(value)
        elif tag_name == 'String':
            op, args, _, _ = spvm._executed[-3]
            assert op == 'stack'
            assert len(args) == 1
            size = int(args[0], 0x10)
            rval = (c_char * size).from_buffer(spvm.heap, value).value
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


class RTTIDbgVar(TypedSymbol, _DbgChild):
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

    @property
    def name(self):
        return self.debug.plugin.stringtable.get(self._name)

    def parse_value(self, value: int, spvm: vm.SourcePawnAbstractMachine) -> Any | None:
        return self.rtti.interpret_value(value, spvm)

    def __str__(self) -> str:
        table_name = 'globals' if self.vclass_kind == RTTI_VAR_CLASS_GLOBAL else 'locals'
        # TODO(zk): typing info
        return f'.dbg.{table_name}({self.name})'


class PluginDebug(_PluginChild):
    def __init__(self, plugin):
        super(PluginDebug, self).__init__(plugin)

        self.unpacked = False
        self.stringbase = None
        self.stringtable = {}

        self.files: List[DbgFile] | None = None
        self.lines: List[DbgLine] | None = None
        self.symbols: List[DbgSymbol] | None = None
        self.vars: List[RTTIDbgVar] | None = None
        self.symbols_by_addr: Dict[int, TypedSymbol] | None = None

    def extract_stringtable(self, size: int, stringbase=None):
        if stringbase is None:
            stringbase = self.stringbase
        if stringbase is None:
            raise ValueError('Invalid stringbase')

        self.stringtable = extract_stringtable(self.plugin.base, stringbase, size)
        return self.stringtable

    def _get_string(self, offset):
        if self.stringbase is None:
            raise SourcePawnPluginError(
                'No debug stringbase to grab strings from')
        return c_char_p(self.plugin.base[self.stringbase + offset:]).value

    # FIXME: talk about a useless layer of abstraction
    def _file(self, addr, name):
        return DbgFile(self, addr, name)

    def _line(self, addr, line):
        return DbgLine(self, addr, line)

    def _symbol(self, addr, tagid, codestart, codeend, ident, vclass,
                dimcount, name, arraydims=()):
        return DbgSymbol(self, addr, tagid, codestart, codeend, ident, vclass,
                         dimcount, name, arraydims)


class SourcePawnPlugin:
    def __init__(self, filelike=None):
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
        self.rtti_methods: Dict[str, RTTIMethod] | None = None

        self.tags: Dict[int, Tag] | None = None
        self.inlines: Dict[str, Public] | None = None
        self.publics: Dict[str, Public] | None = None
        self.publics_by_offs: Dict[int, Public] | None = None
        self.pubvars: Dict[str, Pubvar] | None = None
        self.natives: Dict[str, Native] | None = None

        self.num_tags: int | None = None
        self.num_publics: int | None = None
        self.num_pubvars: int | None = None
        self.num_natives: int | None = None

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
            self._runtime = vm.SourcePawnPluginRuntime(self)
        return self._runtime

    @runtime.setter
    def runtime(self, value):
        self._runtime = value

    def run(self):
        self.runtime.run()

    @property
    def flags(self):
        if self.pcode is None:
            raise AttributeError('%s instance has no attribute \'flags\'' %
                                 type(self))
        return self.pcode.flags

    @flags.setter
    def flags(self, value):
        if self.pcode is None:
            raise AttributeError('%s instance has no attribute \'flags\'' %
                                 type(self))
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

        payload, kind = parse_type_id(type_id)

        if kind == RTTI_TYPE_ID_INLINE:
            parser = RTTIParser(payload.to_bytes(4, 'little', signed=False), 0)
            return parser.decode_new()

        elif kind == RTTI_TYPE_ID_COMPLEX:
            # XXX(zk): WHY +2?? It seems to work, but I don't know why.
            #  Is the RTTIParser wrong? Is there some ushort I've failed to read in rtti.data?
            parser = RTTIParser(self.rtti_data, payload + 2)
            return parser.decode_new()


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

            self.tags = {}
            _tagsize = SPFileTag.sizeof()
            self.num_tags = sect.size // _tagsize

            tags = SPFileTag[self.num_tags].parse(self.base[sect.dataoffs:])

            for index, tag in enumerate(tags[:self.num_tags]):
                # XXX: why do String, Float, etc have ridiculously high tag_ids?
                # XXX: Tag "String" (id: 1073741828)
                # XXX: Tag "Float" (id: 1073741829)
                self.tags[index] = Tag(self, tag.tag_id, tag.name)

        # Functions defined as public
        if '.publics' in sections:
            sect = sections['.publics']

            self.publics = {}
            self.inlines = defaultdict(dict)
            self.publics_by_offs = {}
            _publicsize = SPFilePublics.sizeof()
            self.num_publics = sect.size // _publicsize

            # Make our Struct array for easy access
            publics = SPFilePublics[self.num_publics].parse(self.base[sect.dataoffs:])

            for i, pub in enumerate(publics[:self.num_publics]):
                code_offs = pub.address
                funcid = (i << 1) | 1
                _pub = Public(self, code_offs, funcid, pub.name)
                self.publics[_pub.name] = _pub
                self.publics_by_offs[code_offs] = _pub

                if _pub.is_inline():
                    self.inlines[_pub.get_function_name()] = _pub

        # Variables defined as public, most importantly myinfo
        if '.pubvars' in sections:
            sect = sections['.pubvars']

            self.pubvars = []
            self.num_pubvars = sect.size // SPFilePubvars.sizeof()

            # Make our Struct array for easy access
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

            self.natives = {}
            self.num_natives = sect.size // SPFileNatives.sizeof()

            # Make our Struct array for easy access
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
            self.debug.natives = {}

            a_offset = 0

            def read(klass: Type[ConStruct]):
                nonlocal a_offset
                inst = klass.parse(self.base[sect.dataoffs + a_offset:])
                a_offset += klass.sizeof()
                return inst

            ntvtab = read(SPFdbgNtvTab)

            for native in ntvtab.natives:
                self.debug.natives[native.index] = native

        if '.dbg.files' in sections:
            sect = sections['.dbg.files']

            num_dbg_files = sect.size // SPFdbgFile.sizeof()
            files = SPFdbgFile[num_dbg_files].parse(self.base[sect.dataoffs:])

            self.debug.files = []
            for dbg_file in files[:num_dbg_files]:
                self.debug.files.append(
                    self.debug._file(dbg_file.addr, dbg_file.name)
                )

        if '.dbg.lines' in sections:
            sect = sections['.dbg.lines']

            num_dbg_lines = sect.size // SPFdbgLine.sizeof()
            lines = SPFdbgLine[num_dbg_lines].parse(self.base[sect.dataoffs:])

            self.debug.lines = []
            for line in lines[:num_dbg_lines]:
                self.debug.lines.append(
                    self.debug._line(line.addr, line.line)
                )

        if '.dbg.symbols' in sections:
            sect = sections['.dbg.symbols']

            self.debug.symbols = []

            if self.debug.symbols_by_addr is None:
                self.debug.symbols_by_addr = {}

            i = 0
            while i < sect.size:
                sym = SPFdbgSymbol.parse(self.base[sect.dataoffs + i:])
                i += SPFdbgSymbol.sizeof()

                symbol = self.debug._symbol(sym.addr, sym.tagid, sym.codestart,
                                            sym.codeend, sym.ident, sym.vclass,
                                            sym.dimcount, sym.name)

                symbol.arraydims = []
                for _ in range(sym.dimcount):
                    dim = SPFdbgArrayDim.parse(self.base[sect.dataoffs + i:])
                    i += SPFdbgArrayDim.sizeof()
                    symbol.arraydims.append(dim)

                self.debug.symbols.append(symbol)
                self.debug.symbols_by_addr[symbol.addr] = symbol

        if 'rtti.data' in sections:
            sect = sections['rtti.data']
            self.rtti_data = self.base[sect.dataoffs:sect.dataoffs + sect.size]

        if 'rtti.methods' in sections:
            sect = sections['rtti.methods']
            methods_table = SmxRTTIMethodTable.parse(self.base[sect.dataoffs:])

            if self.debug.symbols_by_addr is None:
                self.debug.symbols_by_addr = {}

            self.rtti_methods = {}
            for meth in methods_table.methods:
                rtti_method = RTTIMethod(
                    plugin=self,
                    name=meth.name,
                    pcode_start=meth.pcode_start,
                    pcode_end=meth.pcode_end,
                    signature=meth.signature,
                )
                self.rtti_methods[meth.name] = rtti_method
                self.debug.symbols_by_addr[meth.pcode_start] = rtti_method

        for rtti_var_sect_name in ('.dbg.globals', '.dbg.locals'):
            if rtti_var_sect_name not in sections:
                continue

            if self.debug.vars is None:
                self.debug.vars = []
            if self.debug.symbols_by_addr is None:
                self.debug.symbols_by_addr = {}

            sect = sections[rtti_var_sect_name]
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
                self.debug.symbols_by_addr[rtti_var.address] = rtti_var

        if self.flags & SP_FLAG_DEBUG and (self.debug.files is None or
                                           self.debug.lines is None or
                                           self.debug.symbols_by_addr is None):
            raise SourcePawnPluginFormatError(
                'Debug flag found, but debug information incomplete')

        self.filled = True
