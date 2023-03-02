from __future__ import annotations

import io
import zlib
from collections import defaultdict
from ctypes import c_char_p
from typing import Dict, List

import more_bisect

import smx.runtime
from smx.definitions import (
    Myinfo,
    RTTI_TYPE_ID_COMPLEX,
    RTTI_TYPE_ID_INLINE,
    SmxRTTIClassDefTable,
    SmxRTTIDebugMethodTable, SmxRTTIDebugVarTable,
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
    SP_FLAG_DEBUG, SP_NATIVE_UNBOUND,
    SPCodeFeature,
    SPFdbgFile,
    SPFdbgInfo,
    SPFdbgLine,
    SPFdbgNative, SPFdbgNtvTab,
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
from smx.exceptions import SourcePawnPluginError, SourcePawnPluginFormatError, SourcePawnPluginNativeError
from smx.reader import (
    DbgFile,
    DbgLine,
    DbgSymbol,
    extract_stringtable,
    Native,
    PCode,
    Public,
    Pubvar,
    RTTIClassDef,
    RTTIDbgVar,
    RTTIEnum,
    RTTIEnumStruct,
    RTTIEnumStructField,
    RTTIField,
    RTTIMethod,
    RTTINative,
    RTTITypedef,
    RTTITypeset,
    Tag,
    TypedSymbol,
)
from smx.rtti import parse_type_id, RTTI, RTTIParser


class SourcePawnPlugin:
    def __init__(self, filelike=None, **runtime_options):
        self.runtime_options = runtime_options

        self.name: str = '<unnamed>'
        self.filled: bool = False

        self.base: bytes | None = None
        self.stringbase: int | None = None
        self.stringtable: Dict[int, str] | None = None
        self.stringtab: int | None = None

        self.data: int | None = None
        self.datasize: int | None = None
        self.memsize: int | None = None
        self.pcode: PCode | None = None

        self.features: SPCodeFeature = SPCodeFeature.Deprecated0
        self.is_unpacked: bool = False

        self.tags: Dict[int, Tag] = {}
        self.inlines: Dict[str, Public] = {}
        self.publics_by_id: Dict[int, Public] = {}
        self.publics_by_name: Dict[str, Public] = {}
        self.publics_by_offs: Dict[int, Public] = {}
        self.pubvars: List[Pubvar] = []
        self.natives: List[Native] = []
        self.natives_by_name: Dict[str, Native] = {}

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

        self.rtti_dbg_vars: List[RTTIDbgVar] = []
        self.rtti_globals: List[RTTIDbgVar] = []
        self.rtti_locals: List[RTTIDbgVar] = []

        self.dbg_info: SPFdbgInfo | None = None
        self.dbg_files: List[DbgFile] = []
        self.dbg_lines: List[DbgLine] = []
        self.dbg_symbols: List[DbgSymbol] = []
        self.dbg_natives: List[SPFdbgNative] = []
        self.dbg_natives_by_index: Dict[int, SPFdbgNative] = {}

        self.symbols_by_addr: Dict[int, List[TypedSymbol]] = defaultdict(list)

        self.num_tags: int = 0
        self.num_publics: int = 0
        self.num_pubvars: int = 0
        self.num_natives: int = 0

        self._runtime: smx.runtime.SourcePawnPluginRuntime | None = None
        self.myinfo: Myinfo | None = None

        # TODO(zk): allow bytes blobs
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
            self._runtime = smx.runtime.SourcePawnPluginRuntime(self, **self.runtime_options)
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

    def uses_direct_arrays(self) -> bool:
        return bool(self.features & SPCodeFeature.DirectArrays)

    def uses_heap_scopes(self) -> bool:
        return bool(self.features & SPCodeFeature.HeapScopes)

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

    def find_symbols_by_addr(self, addr: int) -> List[TypedSymbol]:
        return self.symbols_by_addr[addr]

    def find_symbol_by_addr(self, addr: int) -> TypedSymbol | None:
        syms = self.find_symbols_by_addr(addr)
        if syms:
            return syms[0]

    def find_method_by_addr(self, addr: int) -> RTTIMethod | None:
        meth = self.rtti_methods_by_addr.get(addr)
        if meth:
            return meth

        for meth in self.rtti_methods:
            if meth.pcode_start <= addr <= meth.pcode_end:
                return meth

    def find_line_by_addr(self, addr: int) -> DbgLine | None:
        if not self.dbg_lines:
            return None

        line_idx = more_bisect.last_pos_le(addr, self.dbg_lines, key=lambda line: line.addr)
        if line_idx is not None:
            return self.dbg_lines[line_idx]

    def find_file_by_addr(self, addr: int) -> DbgFile | None:
        if not self.dbg_files:
            return None

        file_idx = more_bisect.last_pos_le(addr, self.dbg_files, key=lambda file: file.addr)
        if file_idx is not None:
            return self.dbg_files[file_idx]

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

        if hdr.version == SP1_VERSION_1_0:
            self.is_unpacked = True

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

            self.features = cod.features

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
                self.publics_by_id[pub.funcid] = pub
                self.publics_by_name[pub.name] = pub
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
                self.natives.append(native)
                self.natives_by_name[native.name] = native

        if '.dbg.info' in sections:
            sect = sections['.dbg.info']
            info = SPFdbgInfo.parse(self.base[sect.dataoffs:])
            self.dbg_info = info

        if '.dbg.natives' in sections:
            sect = sections['.dbg.natives']

            ntvtab = SPFdbgNtvTab.parse(self.base[sect.dataoffs:])
            for native in ntvtab.natives:
                self.dbg_natives.append(native)
                self.dbg_natives_by_index[native.index] = native

        if '.dbg.files' in sections:
            sect = sections['.dbg.files']

            num_dbg_files = sect.size // SPFdbgFile.sizeof()
            files = SPFdbgFile[num_dbg_files].parse(self.base[sect.dataoffs:])

            for dbg_file in files:
                self.dbg_files.append(DbgFile(self, dbg_file.addr, dbg_file.name))

        if '.dbg.lines' in sections:
            sect = sections['.dbg.lines']

            num_dbg_lines = sect.size // SPFdbgLine.sizeof()
            lines = SPFdbgLine[num_dbg_lines].parse(self.base[sect.dataoffs:])

            for line in lines:
                self.dbg_lines.append(DbgLine(self, line.addr, line.line))

        if '.dbg.symbols' in sections:
            sect = sections['.dbg.symbols']

            i = 0
            while i < sect.size:
                sym = SPFdbgSymbol.parse(self.base[sect.dataoffs + i:])
                i += SPFdbgSymbol.sizeof()

                self.dbg_symbols.append(DbgSymbol(
                    plugin=self,
                    addr=sym.addr,
                    tagid=sym.tagid,
                    codestart=sym.codestart,
                    codeend=sym.codeend,
                    ident=sym.ident,
                    vclass=sym.vclass,
                    dimcount=sym.dimcount,
                    name=sym.name,
                    arraydims=sym.dims,
                ))

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
                self.symbols_by_addr[entry.pcode_start].append(rtti_method)

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
            if 'rtti.enumstruct_fields' not in sections:
                raise SourcePawnPluginFormatError('rtti.enumstruct_fields section is missing, but required by rtti.enumstructs')

            sect = sections['rtti.enumstruct_fields']
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
                    plugin=self,
                    address=var.address,
                    vclass=var.vclass,
                    name=var.name,
                    code_start=var.code_start,
                    code_end=var.code_end,
                    type_id=var.type_id,
                )

                self.rtti_dbg_vars.append(rtti_var)
                if rtti_var.is_global:
                    self.rtti_globals.append(rtti_var)
                else:
                    self.rtti_locals.append(rtti_var)
                self.symbols_by_addr[rtti_var.address].append(rtti_var)

        if '.dbg.methods' in sections:
            sect = sections['.dbg.methods']
            debug_methods_table = SmxRTTIDebugMethodTable.parse(self.base[sect.dataoffs:])

            last_locals = (
                [m.first_local for m in debug_methods_table.methods[1:]] + [len(self.rtti_locals)]
            )
            for entry, last_local in zip(debug_methods_table.methods, last_locals):
                rtti_method = self.rtti_methods[entry.method_index]
                rtti_locals = self.rtti_locals[entry.first_local:last_local]
                for rtti_var in rtti_locals:
                    rtti_var.associated_method = rtti_method
                    rtti_method.associated_locals[rtti_var.address] = rtti_var

        self.filled = True


def _invalid_native():
    raise SourcePawnPluginNativeError("Invalid native")
