import re
import zlib
from collections import OrderedDict, defaultdict
from ctypes import *

from smx import vm
from smx.definitions import *
from smx.exceptions import (
    SourcePawnPluginNativeError,
    SourcePawnPluginError,
    SourcePawnPluginFormatError)
from smx.struct import *


RGX_INLINE_NAME = re.compile(r'^\.(\d+)\.(\w+)')


def _extract_strings(buffer, num_strings=1):
    strings = []
    offset = 0
    for i in xrange(num_strings):
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
    buf = buffer(base, stringbase, size)
    offset = 0
    while offset <= size:
        s = c_char_p(buf[offset:]).value
        stringtable[offset] = s
        offset += len(s)+1

    return stringtable


def _invalid_native():
    raise SourcePawnPluginNativeError("Invalid native")


class SourcePawnPlugin(object):
    class sp_file_section(NoAlignStruct):
        """File section header format."""
        nameoffs = cf_uint32()      # Relative offset into global string table
        dataoffs = cf_uint32()      # Offset into the data section of the file
        size = cf_uint32()          # Size of the section's entry in the data section

    class sp_file_hdr(NoAlignStruct):
        """File header format.  If compression is 0, then disksize may be 0
        to mean that only the imagesize is needed."""
        magic = cf_uint32()         # Magic number
        version = cf_uint16()       # Version code
        compression = cf_uint8()    # Compression algorithm
        disksize = cf_uint32()      # Size on disk
        imagesize = cf_uint32()     # Size in memory
        sections = cf_uint8()       # Number of sections
        stringtab = cf_uint32()     # Offset to string table
        dataoffs = cf_uint32()      # Offset to file proper (any compression starts here)

    class sp_file_code(NoAlignStruct):
        """File-encoded format of the ".code" section."""
        codesize = cf_uint32()      # Codesize in bytes
        cellsize = cf_uint8()       # Cellsize in bytes
        codeversion = cf_uint8()    # Version of opcodes supported
        flags = cf_uint16()         # Flags
        main = cf_uint32()          # Address to "main," if any
        code = cf_uint32()          # Relative offset to code

    class sp_file_data(NoAlignStruct):
        """File-encoded format of the ".data" section."""
        datasize = cf_uint32()      # Size of data section in memory
        memsize = cf_uint32()       # Total mem required (includes data)
        data = cf_uint32()          # File offset to data (helper)

    class sp_file_publics(NoAlignStruct):
        """File-encoded format of the ".publics" section."""
        address = cf_uint32()       # Address relative to code section
        name = cf_uint32()          # Index into nametable

    class sp_file_natives(NoAlignStruct):
        """File-encoded format of the ".natives" section."""
        name = cf_uint32()          # Index into nametable

    class sp_file_pubvars(NoAlignStruct):
        """File-encoded format of the ".pubvars" section."""
        address = cf_uint32()       # Address relative to the DAT section
        name = cf_uint32()          # Index into nametable

    class sp_file_tag(NoAlignStruct):
        """File-encoded tag info."""
        tag_id = cf_uint32()        # Tag ID from compiler
        name = cf_uint32()          # Index into nametable

    class sp_fdbg_info(NoAlignStruct):
        """File-encoded debug information table."""
        num_files = cf_uint32()     # number of files
        num_lines = cf_uint32()     # number of lines
        num_syms = cf_uint32()      # number of symbols
        num_arrays = cf_uint32()    # number of symbols which are arrays

    class sp_fdbg_file(NoAlignStruct):
        """File-encoded debug file table."""
        addr = cf_uint32()          # Address into code
        name = cf_uint32()          # Offset into debug nametable

    class sp_fdbg_line(NoAlignStruct):
        """File-encoded debug line table."""
        addr = cf_uint32()          # Address into code
        line = cf_uint32()          # Line number

    class sp_fdbg_symbol(NoAlignStruct):
        """File-encoded debug symbol information."""
        addr = cf_int32()           # Address rel to DAT or stack frame
        tagid = cf_int16()          # Tag id
        codestart = cf_uint32()     # Start scope validity in code
        codeend = cf_uint32()       # End scope validity in code
        ident = cf_uint8()          # Variable type
        vclass = cf_uint8()         # Scope class (local vs global)
        dimcount = cf_uint16()      # Dimension count (for arrays)
        name = cf_uint32()          # Offset into debug nametable

    class sp_fdbg_arraydim(NoAlignStruct):
        """Occurs after an fdbg_symbol entry, for each dimension."""
        tagid = cf_int16()          # Tag id
        size = cf_uint32()          # Size of dimension

    class sp_fdbg_ntvtab(NoAlignStruct):
        """Header for the ".dbg.natives" section.

        It is followed by a number of sp_fdbg_native_t entries.
        """
        num_entries = cf_uint32()   # Number of entries

    class sp_fdbg_native(NoAlignStruct):
        """An entry in the .dbg.natives section.

        Each is followed by an sp_fdbg_ntvarg_t for each argument.
        """
        index = cf_uint32()         # Native index in the plugin.
        name = cf_uint32()          # Offset into debug nametable.
        tagid = cf_int16()          # Return tag.
        nargs = cf_uint16()         # Number of formal arguments.

    class sp_fdbg_ntvarg(NoAlignStruct):
        """Each entry is followed by an sp_fdbg_arraydim_t for each dimcount."""
        ident = cf_uint8()          # Variable type
        tagid = cf_int16()          # Tag id
        dimcount = cf_uint16()      # Dimension count (for arrays)
        name = cf_uint32()          # Offset into debug nametable


    class StringtableName(object):
        @property
        def name(self):
            return self.plugin.stringtable.get(self._name)


    class PCode(object):
        def __init__(self, plugin, pcode, size, version, flags):
            self.plugin = plugin
            self.pcode = pcode
            self.size = size
            self.version = version
            self.flags = flags


    class Public(StringtableName):
        def __init__(self, plugin, code_offs, funcid, name):
            self.plugin = plugin
            self.code_offs = code_offs
            self.funcid = funcid
            self._name = name

        def get_function_name(self):
            if self.name:
                match = RGX_INLINE_NAME.match(self.name)
                if match and int(match.group(1)) == self.code_offs:
                    return match.group(2)
            return self.name

        def is_inline(self):
            if self.name:
                match = RGX_INLINE_NAME.match(self.name)
                if match and int(match.group(1)) == self.code_offs:
                    return True
            return False

        def __str__(self):
            return 'Public function "%s" (id: %d, code_offs: %d)' % (
                self.name, self.funcid, self.code_offs)


    class Pubvar(StringtableName):
        class Myinfo(NoAlignStruct):
            name = cf_uint32()
            description = cf_uint32()
            author = cf_uint32()
            version = cf_uint32()
            url = cf_uint32()

        def __init__(self, plugin, offs, name):
            self.plugin = plugin
            self.offs = offs
            self._name = name

            # Special case for myinfo
            if self.name == 'myinfo':
                myinfo_offs = self.Myinfo(self.plugin.base, self.offs)
                self.myinfo = dict(map(
                    lambda o: (o[0],self.plugin._get_data_string(getattr(
                        myinfo_offs, o[0]))), myinfo_offs._fields_))

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
            self.plugin = plugin
            self.flags = flags
            self.pfn = pfn
            self.status = status
            self.user = user
            self._name = name

        def __str__(self):
            status = self.STATUS_NAMES.get(self.status, '')
            return ' '.join((status, 'native')).capitalize() + ' "%s"' % self.name


    class Tag(StringtableName):
        def __init__(self, plugin, tagid, name):
            self.plugin = plugin
            self.tagid = tagid
            self._name = name

        def __str__(self):
            return 'Tag "%s" (id: %d)' % (self.name, self.tagid)


    def _pubvar(self, offs, name):
        return self.Pubvar(self, offs, name)
    def _public(self, code_offs, funcid, name):
        return self.Public(self, code_offs, funcid, name)
    def _pcode(self, pcode, size, version, flags):
        return self.PCode(self, pcode, size, version, flags)
    def _native(self, flags, pfn, status, user, name):
        return self.Native(self, flags, pfn, status, user, name)
    def _tag(self, tagid, name):
        return self.Tag(self, tagid, name)


    class Debug(object):
        class DbgFile(object):
            def __init__(self, debug, addr, name):
                self.debug = debug
                self.addr = addr
                self._name = name

            @property
            def name(self):
                return self.debug.stringtable.get(self._name)

            def __str__(self):
                return 'DbgFile "%s" (addr: %d)' % (self.name, self.addr)

        class DbgLine(object):
            def __init__(self, debug, addr, line):
                self.debug = debug
                self.addr = addr
                self.line = line

            def __str__(self):
                return 'DbgLine #%d (addr: %d)' % (self.line, self.addr)

        class DbgSymbol(object):
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
                self.debug = debug

                self.addr = addr            # Address rel to DAT or stack frame
                self.tagid = tagid          # Tag id
                self.codestart = codestart  # Start scope validity in code
                self.codeend = codeend      # End scope validity in code
                self.ident = ident          # Variable type
                self.vclass = vclass        # Scope class (local vs global)
                self.dimcount = dimcount    # Dimension count (for arrays)
                self.arraydims = arraydims
                self._name = name

            @property
            def name(self):
                return self.debug.stringtable.get(self._name)

            @property
            def tag(self):
                return self.debug.plugin.tags[self.tagid]

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

                fmt = 'DbgSymbol {name} ({ident}, stringidx: {stringidx})'
                return fmt.format(
                    name=('"%s"' % self.name) if self.name else '<unnamed>',
                    ident=self.SYMBOL_TYPE_NAMES.get(self.ident, 'unknown'),
                    stringidx=self._name,
                )

        def __init__(self, plugin):
            self.plugin = plugin

            self.unpacked = False
            self.stringbase = None
            self.stringtable = {}

            self.files = None
            self.lines = None
            self.symbols = None

            self.files_num = None
            self.lines_num = None
            self.syms_num = None

        def extract_stringtable(self, size, stringbase=None):
            if stringbase is None:
                stringbase = self.stringbase
            if stringbase is None:
                raise ValueError('Invalid stringbase')

            self.stringtable = extract_stringtable(self.plugin.base,
                                                   stringbase, size)
            return self.stringtable


        def _get_string(self, offset):
            if self.stringbase is None:
                raise SourcePawnPluginError(
                    'No debug stringbase to grab strings from')
            return c_char_p(self.plugin.base[self.stringbase + offset:]).value

        def _file(self, addr, name):
            return self.DbgFile(self, addr, name)
        def _line(self, addr, line):
            return self.DbgLine(self, addr, line)
        def _symbol(self, addr, tagid, codestart, codeend, ident, vclass,
                    dimcount, name, arraydims=()):
            return self.DbgSymbol(self, addr, tagid, codestart, codeend,
                                  ident, vclass, dimcount, name, arraydims)


    def __init__(self, filelike=None):
        self.name = '<unnamed>'
        self.debug = self.Debug(self)
        self.filled = False

        self.base = None
        self.stringbase = None
        self.stringtable = None
        self.stringtab = None

        self.data = None
        self.datasize = None
        self.memsize = None
        self.pcode = None

        self.tags = None
        self.publics = None
        self.publics_by_offs = None
        self.pubvars = None
        self.natives = None

        if buffer is not None:
            self.extract_from_buffer(filelike)

    def __str__(self):
        if hasattr(self, 'myinfo'):
            return self.myinfo['name'] + ' by ' + self.myinfo['author']
        if self.name:
            return self.name
        if self.filled:
            return 'Nameless SourcePawn Plug-in'
        return 'Empty SourcePawn Plug-in'

    def _get_runtime(self):
        if hasattr(self, '_runtime'):
            return self._runtime
        self._runtime = vm.SourcePawnPluginRuntime(self)
        return self._runtime
    def _set_runtime(self, value):
        self._runtime = value
    runtime = property(_get_runtime, _set_runtime)

    def run(self):
        self.runtime.run()

    def _get_flags(self):
        if not hasattr(self, 'pcode') or self.pcode is None:
            raise AttributeError('%s instance has no attribute \'flags\'' %
                                 type(self))
        return self.pcode.flags
    def _set_flags(self, value):
        if not hasattr(self, 'pcode') or self.pcode is None:
            raise AttributeError('%s instance has no attribute \'flags\'' %
                                 type(self))
        self.pcode.flags = value
    flags = property(_get_flags, _set_flags)

    def _get_data_string(self, dataoffset):
        return c_char_p(self.base[self.data + dataoffset:]).value

    def _get_data_char(self, dataoffset):
        return c_char_p(self.base[self.data + dataoffset:]).value[0]

    def _get_string(self, stroffset):
        return c_char_p(self.base[self.stringbase + stroffset:]).value

    def extract_from_buffer(self, fp):
        if isinstance(fp, file) and hasattr(fp, 'name'):
            self.name = fp.name

        hdr = self.sp_file_hdr(fp.read(sizeof(self.sp_file_hdr)))

        if hdr.magic != SPFILE_MAGIC:
            raise SourcePawnPluginFormatError(
                'Invalid magic number 0x%08x (expected 0x%08x)' %
                (hdr.magic, SPFILE_MAGIC))

        if hdr.version == 0x0101:
            self.debug.unpacked = True

        self.stringtab = hdr.stringtab

        _hdr_size = sizeof(hdr)
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

        self.base = buffer(base)

        _total_sectsize = sizeof(self.sp_file_section) * hdr.sections
        _sections = (self.sp_file_section * hdr.sections)()
        memmove(addressof(_sections),
                buffer(self.base, _hdr_size, _total_sectsize)[:],
                _total_sectsize)

        sections = OrderedDict()
        for sect in _sections[:hdr.sections]:
            name = c_char_p(buffer(self.base,
                                   self.stringtab + sect.nameoffs)[:]).value
            sections[name] = sect

        if '.names' in sections:
            sect = sections['.names']
            self.stringbase = sect.dataoffs
            self.stringtable = extract_stringtable(self.base, sect.dataoffs,
                                                   sect.size)
        else:
            raise SourcePawnPluginError('Could not locate string base')

        if '.code' in sections:
            cod = self.sp_file_code(self.base, sections['.code'].dataoffs)

            if cod.codeversion < SP_CODEVERS_JIT1:
                raise SourcePawnPluginFormatError(
                    "Code version %d is too old" % cod.codeversion)
            elif cod.codeversion > SP_CODEVERS_JIT2:
                raise SourcePawnPluginFormatError(
                    "Code version %d is too new" % cod.codeversion)

            pcode = hdr.dataoffs + cod.code
            self.pcode = self._pcode(pcode, cod.codesize, cod.codeversion,
                                     cod.flags)
        else:
            raise SourcePawnPluginFormatError('.code section not found!')

        if '.data' in sections:
            sect = sections['.data']
            dat = self.sp_file_data(self.base, sect.dataoffs)
            self.data = sect.dataoffs + dat.data
            self.datasize = dat.datasize
            self.memsize = dat.memsize
        else:
            raise SourcePawnPluginFormatError('.data section not found!')

        if '.tags' in sections:
            sect = sections['.tags']

            self.tags = {}
            _tagsize = sizeof(self.sp_file_tag)
            self.num_tags = sect.size / _tagsize

            tags = (self.sp_file_tag * self.num_tags)()
            memmove(addressof(tags),
                    buffer(self.base, sect.dataoffs, sect.size)[:], sect.size)

            for index, tag in enumerate(tags[:self.num_tags]):
                # XXX: why do String, Float, etc have ridiculously high tag_ids?
                # XXX: Tag "String" (id: 1073741828)
                # XXX: Tag "Float" (id: 1073741829)
                self.tags[index] = self._tag(tag.tag_id, tag.name)

        # Functions defined as public
        if '.publics' in sections:
            sect = sections['.publics']

            self.publics = OrderedDict()
            self.inlines = defaultdict(dict)
            self.publics_by_offs = {}
            _publicsize = sizeof(self.sp_file_publics)
            self.num_publics = sect.size / _publicsize

            # Make our Struct array for easy access
            publics = (self.sp_file_publics * self.num_publics)()
            memmove(addressof(publics),
                    buffer(self.base, sect.dataoffs, sect.size)[:], sect.size)

            for i,pub in enumerate(publics[:self.num_publics]):
                code_offs = pub.address
                funcid = (i << 1) | 1
                _pub = self._public(code_offs, funcid, pub.name)
                self.publics[_pub.name] = _pub
                self.publics_by_offs[code_offs] = _pub

                if _pub.is_inline():
                    self.inlines[_pub.get_function_name()] = _pub

        # Variables defined as public, most importantly myinfo
        if '.pubvars' in sections:
            sect = sections['.pubvars']

            self.pubvars = []
            self.num_pubvars = sect.size / sizeof(self.sp_file_pubvars)

            # Make our Struct array for easy access
            pubvars = (self.sp_file_pubvars * self.num_pubvars)()
            memmove(addressof(pubvars),
                    buffer(self.base, sect.dataoffs, sect.size)[:], sect.size)

            for pubvar in pubvars[:self.num_pubvars]:
                offs = self.data + pubvar.address
                pubvar = self._pubvar(offs, pubvar.name)
                self.pubvars.append(pubvar)

                if pubvar.name == 'myinfo':
                    self.myinfo = pubvar.myinfo
                    self.name = self.myinfo['name']

        if '.natives' in sections:
            sect = sections['.natives']

            self.natives = OrderedDict()
            self.num_natives = sect.size / sizeof(self.sp_file_natives)

            # Make our Struct array for easy access
            natives = (self.sp_file_natives * self.num_natives)()
            memmove(addressof(natives),
                    buffer(self.base, sect.dataoffs, sect.size)[:], sect.size)

            for native in natives[:self.num_natives]:
                native = self._native(0, _invalid_native,
                                      SP_NATIVE_UNBOUND, None, native.name)
                self.natives[native.name] = native

        if '.dbg.strings' in sections:
            self.debug.stringbase = sections['.dbg.strings'].dataoffs
            self.debug.extract_stringtable(sections['.dbg.strings'].size)

        if '.dbg.info' in sections:
            inf = self.sp_fdbg_info(self.base, sections['.dbg.info'].dataoffs)
            self.debug.info = inf

        if '.dbg.natives' in sections:
            sect = sections['.dbg.natives']
            self.debug.natives = OrderedDict()

            a_offset = [0]
            def read(klass):
                inst = klass(self.base, sect.dataoffs + a_offset[0])
                a_offset[0] += sizeof(klass)
                return inst

            ntvtab = read(self.sp_fdbg_ntvtab)
            num_natives = ntvtab.num_entries

            for i in xrange(num_natives):
                native = read(self.sp_fdbg_native)
                ntvargs = []
                for _ in xrange(native.nargs):
                    ntvarg = read(self.sp_fdbg_ntvarg)
                    ntvarg.dims = [read(self.sp_fdbg_arraydim)
                                   for _ in xrange(ntvarg.dimcount)]
                    ntvargs.append(ntvarg)
                native.args = ntvargs
                self.debug.natives[native.index] = native

        if '.dbg.files' in sections:
            sect = sections['.dbg.files']

            num_dbg_files = sect.size / sizeof(self.sp_fdbg_file)
            files = (self.sp_fdbg_file * num_dbg_files)()
            memmove(addressof(files),
                    buffer(self.base, sect.dataoffs, sect.size)[:], sect.size)

            self.debug.files = []
            for dbg_file in files[:num_dbg_files]:
                self.debug.files.append(
                    self.debug._file(dbg_file.addr, dbg_file.name)
                )

        if '.dbg.lines' in sections:
            sect = sections['.dbg.lines']

            num_dbg_lines = sect.size / sizeof(self.sp_fdbg_line)
            lines = (self.sp_fdbg_line * num_dbg_lines)()
            memmove(addressof(lines),
                    buffer(self.base, sect.dataoffs, sect.size)[:], sect.size)

            self.debug.lines = []
            for line in lines[:num_dbg_lines]:
                self.debug.lines.append(
                    self.debug._line(line.addr, line.line)
                )

        if '.dbg.symbols' in sections:
            sect = sections['.dbg.symbols']

            self.debug.symbols = []
            self.debug.symbols_by_addr = OrderedDict()
            i = 0
            while i < sect.size:
                sym = self.sp_fdbg_symbol(self.base, sect.dataoffs + i)
                i += sizeof(self.sp_fdbg_symbol)

                symbol = self.debug._symbol(sym.addr, sym.tagid, sym.codestart,
                                            sym.codeend, sym.ident, sym.vclass,
                                            sym.dimcount, sym.name)

                symbol.arraydims = []
                for _ in xrange(sym.dimcount):
                    dim = self.sp_fdbg_arraydim(self.base, sect.dataoffs + i)
                    i += sizeof(self.sp_fdbg_arraydim)
                    symbol.arraydims.append(dim)

                self.debug.symbols.append(symbol)
                self.debug.symbols_by_addr[symbol.addr] = symbol

        if self.flags & SP_FLAG_DEBUG and (self.debug.files is None or
                                           self.debug.lines is None or
                                           self.debug.symbols is None):
            raise SourcePawnPluginFormatError(
                'Debug flag found, but debug information incomplete')

        self.filled = True
