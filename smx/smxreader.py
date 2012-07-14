import zlib
from ctypes import *
from newstruct import *

SPFILE_MAGIC    = 0x53504646
SPFILE_VERSION  = 0x0102

SPFILE_COMPRESSION_NONE = 0
SPFILE_COMPRESSION_GZ   = 1

SP_CODEVERS_JIT1    = 9
SP_CODEVERS_JIT2    = 10

SP_FLAG_DEBUG   = (1<<0)

SP_SYM_VARIABLE     = 1  # Cell that has an address and that can be fetched directly (lvalue)
SP_SYM_REFERENCE    = 2  # VARIABLE, but must be dereferenced
SP_SYM_ARRAY        = 3  # Symbol is an array
SP_SYM_REFARRAY     = 4  # An array passed by reference (i.e. a pointer)
SP_SYM_FUNCTION     = 9  # Symbol is a function
SP_SYM_VARARGS      = 11 # Variadic argument start.

SP_NATIVE_UNBOUND   = 0  # Native is undefined
SP_NATIVE_BOUND     = 1  # Native is bound

SP_NTVFLAG_OPTIONAL = (1<<0) # Native is optional


class SourcePawnPluginError(Exception):
    pass
class SourcePawnPluginFormatError(SourcePawnPluginError):
    pass
class SourcePawnPluginNativeError(SourcePawnPluginError):
    pass


def _extract_strings(buffer, num_strings=1):
    strings = []
    offset = 0
    for i in xrange(num_strings):
        s = c_char_p(buffer[offset:]).value
        strings.append(s)
        offset += len(s)+1
    return tuple(strings)


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


    class PCode(object):
        def __init__(self, plugin, pcode, size, version, flags):
            self.plugin = plugin
            self.pcode = pcode
            self.size = size
            self.version = version
            self.flags = flags


    class Public(object):
        def __init__(self, plugin, code_offs, funcid, name):
            self.plugin = plugin
            self.code_offs = code_offs
            self.funcid = funcid
            self.name = name

        def __str__(self):
            return 'Public function "%s" (id: %d, code_offs: %d)' % (
                self.name, self.funcid, self.code_offs)


    class Pubvar(object):
        class Myinfo(NoAlignStruct):
            name = cf_uint32()
            description = cf_uint32()
            author = cf_uint32()
            version = cf_uint32()
            url = cf_uint32()

        def __init__(self, plugin, offs, name):
            self.plugin = plugin
            self.offs = offs
            self.name = name

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


    class Native(object):
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
            self.name = name

        def __str__(self):
            status = self.STATUS_NAMES.get(self.status, '')
            return ' '.join((status, 'native "%s"' % self.name)).capitalize()


    def _pubvar(self, offs, name):
        return self.Pubvar(self, offs, name)
    def _public(self, code_offs, funcid, name):
        return self.Public(self, code_offs, funcid, name)
    def _pcode(self, pcode, size, version, flags):
        return self.PCode(self, pcode, size, version, flags)
    def _native(self, flags, pfn, status, user, name):
        return self.Native(self, flags, pfn, status, user, name)


    class Debug(object):
        def __init__(self):
            self.unpacked = False
            self.stringbase = None

            self.files = None
            self.lines = None
            self.symbols = None

            self.files_num = None
            self.lines_num = None
            self.syms_num = None


    def __init__(self, filelike=None):
        self.name = '<unnamed>'
        self.debug = self.Debug()
        self.filled = False

        self.base = None
        self.stringbase = None
        self.stringtab = None

        self.data = None
        self.pcode = None

        self.num_publics = None
        self.publics = None

        self.num_pubvars = None
        self.pubvars = None

        self.num_natives = None
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

        sect = self.sp_file_section()
        _sectsize = sizeof(sect)
        for sectnum in xrange(hdr.sections):
            sect.pack_into(buffer(self.base, _hdr_size + sectnum * _sectsize))
            name = c_char_p(buffer(self.base,
                                   self.stringtab + sect.nameoffs)[:]).value
            if name == '.names':
                self.stringbase = sect.dataoffs
                break

        if self.stringbase is None:
            raise SourcePawnPluginError('Could not locate string base')

        for sectnum in xrange(hdr.sections):
            sect.pack_into(buffer(self.base, _hdr_size + sectnum * _sectsize))
            sectnameoff = self.stringtab + sect.nameoffs
            sectname = c_char_p(self.base[sectnameoff:]).value

            if self.pcode is None and sectname == '.code':
                cod = self.sp_file_code(self.base, sect.dataoffs)

                if cod.codeversion < SP_CODEVERS_JIT1:
                    raise SourcePawnPluginFormatError(
                        "Code version %d is too old" % cod.codeversion)
                elif cod.codeversion > SP_CODEVERS_JIT2:
                    raise SourcePawnPluginFormatError(
                        "Code version %d is too new" % cod.codeversion)

                pcode = hdr.dataoffs + cod.code
                self.pcode = self._pcode(pcode, cod.codesize, cod.codeversion,
                                         cod.flags)

            elif self.data is None and sectname == '.data':
                dat = self.sp_file_data(self.base, sect.dataoffs)
                self.data = sect.dataoffs + dat.data

            # Functions defined as public
            elif self.publics is None and sectname == '.publics':
                self.publics = []
                _publicsize = sizeof(self.sp_file_publics)
                self.num_publics = sect.size / _publicsize

                # Make our Struct array for easy access
                publics = (self.sp_file_publics * self.num_publics)()
                memmove(addressof(publics),
                        buffer(self.base,sect.dataoffs, sect.size)[:],
                        sect.size)

                for i in xrange(self.num_publics):
                    pub = publics[i]
                    sz_name = self._get_string(pub.name)
                    code_offs = self.data + pub.address
                    funcid = (i << 1) | 1

                    self.publics.append(self._public(code_offs, funcid,
                                                     sz_name))

            # Variables defined as public, most importantly myinfo
            elif self.pubvars is None and sectname == '.pubvars':
                if self.data is None:
                    raise SourcePawnPluginError(
                        '.data section not found in time!')

                self.pubvars = []
                self.num_pubvars = sect.size / sizeof(self.sp_file_pubvars)

                # Make our Struct array for easy access
                pubvars = (self.sp_file_pubvars * self.num_pubvars)()
                memmove(addressof(pubvars),
                        buffer(self.base, sect.dataoffs, sect.size)[:],
                        sect.size)

                for i in xrange(self.num_pubvars):
                    pubvar = pubvars[i]
                    sz_name = self._get_string(pubvar.name)
                    offs = self.data + pubvar.address

                    pubvar = self._pubvar(offs, sz_name)
                    self.pubvars.append(pubvar)

                    if pubvar.name == 'myinfo':
                        self.myinfo = pubvar.myinfo
                        self.name = self.myinfo['name']

            elif self.natives is None and sectname == '.natives':
                self.natives = []
                self.num_natives = sect.size / sizeof(self.sp_file_natives)

                # Make our Struct array for easy access
                natives = (self.sp_file_natives * self.num_natives)()
                memmove(addressof(natives),
                        buffer(self.base, sect.dataoffs, sect.size)[:],
                        sect.size)

                for i in xrange(self.num_natives):
                    native = natives[i]
                    sz_name = self._get_string(native.name)

                    native = self._native(0, _invalid_native,
                                          SP_NATIVE_UNBOUND, None, sz_name)
                    self.natives.append(native)

            elif self.debug.lines_num is None and sectname == '.dbg.info':
                inf = self.sp_fdbg_info(self.base, sect.dataoffs)

                self.debug.files_num = inf.num_files
                self.debug.lines_num = inf.num_lines
                self.debug.syms_num = inf.num_syms

            elif sectname == '.dbg.natives':
                self.debug.unpacked = False

            elif self.debug.files is None and sectname == '.dbg.files':
                self.debug.files = self.sp_fdbg_file(self.base, sect.dataoffs)
            elif self.debug.lines is None and sectname == '.dbg.lines':
                self.debug.lines = self.sp_fdbg_line(self.base, sect.dataoffs)
            elif self.debug.symbols is None and sectname == '.dbg.symbols':
                self.debug.symbols = self.sp_fdbg_symbol(self.base, sect.dataoffs)
            elif self.debug.stringbase is None and sectname == '.dbg.strings':
                self.debug.stringbase = sect.dataoffs

        if self.pcode is None or self.data is None:
            raise SourcePawnPluginFormatError('.code and/or .data section not found')

        if self.flags & SP_FLAG_DEBUG and (self.debug.files is None or
                                           self.debug.lines is None or
                                           self.debug.symbols is None):
            raise SourcePawnPluginFormatError(
                'Debug flag found, but debug information incomplete')

        self.filled = True
