import zlib
from ctypes import *
from newstruct import *

SPFILE_MAGIC    = 0x53504646
SPFILE_VERSION  = 0x0102

SPFILE_COMPRESSION_NONE = 0
SPFILE_COMPRESSION_GZ   = 1

SP_CODEVERS_JIT1    = 9
SP_CODEVERS_JIT2    = 10


class SourcePawnPluginError(Exception):
    pass
class SourcePawnPluginFormatError(SourcePawnPluginError):
    pass


def _extract_strings(buffer, num_strings=1):
    strings = []
    offset = 0
    for i in xrange(num_strings):
        s = c_char_p(buffer[offset:]).value
        strings.append(s)
        offset += len(s)+1
    return tuple(strings)


class SourcePawnPlugin(object):
    class sp_file_hdr(NoAlignStruct):
        magic = cf_uint32()
        version = cf_uint16()
        compression = cf_uint8()
        disksize = cf_uint32()
        imagesize = cf_uint32()
        sections = cf_uint8()
        stringtab = cf_uint32()
        dataoffs = cf_uint32()

    class sp_file_section(NoAlignStruct):
        nameoffs = cf_uint32()
        dataoffs = cf_uint32()
        size = cf_uint32()

    class sp_file_code(NoAlignStruct):
        codesize = cf_uint32()
        cellsize = cf_uint8()
        codeversion = cf_uint8()
        flags = cf_uint16()
        main = cf_uint32()
        code = cf_uint32()

    class sp_file_data(NoAlignStruct):
        datasize = cf_uint32()
        memsize = cf_uint32()
        data = cf_uint32()

    class sp_file_publics(NoAlignStruct):
        address = cf_uint32()
        name = cf_uint32()

    class sp_file_pubvars(NoAlignStruct):
        address = cf_uint32()
        name = cf_uint32()


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

        @property
        def value(self):
            return self.plugin.base[self.offs:]

    def _pubvar(self, offs, name):
        return self.Pubvar(self, offs, name)
    def _public(self, code_offs, funcid, name):
        return self.Public(self, code_offs, funcid, name)
    def _pcode(self, pcode, size, version, flags):
        return self.PCode(self, pcode, size, version, flags)


    def __init__(self, filelike=None):
        self.base = None
        self.stringbase = None
        self.stringtab = None

        self.pubvars = None
        self.publics = None
        self.data = None
        self.pcode = None

        if buffer is not None:
            self.extract_from_buffer(filelike)

    def __str__(self):
        if hasattr(self, 'myinfo'):
            return str(self.myinfo['name'] + ' by ' + self.myinfo['author'])
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
        hdr = self.sp_file_hdr(buf=fp.read(sizeof(self.sp_file_hdr)))

        if hdr.magic != SPFILE_MAGIC:
            raise SourcePawnPluginFormatError(
                'Invalid magic number 0x%08x (expected 0x%08x)' %
                (hdr.magic, SPFILE_MAGIC))

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
                pcode = hdr.dataoffs + cod.code
                self.pcode = self._pcode(pcode, cod.codesize, cod.codeversion,
                                         cod.flags)

            elif self.data is None and sectname == '.data':
                dat = self.sp_file_data(self.base, sect.dataoffs)
                self.data = sect.dataoffs + dat.data

            # Functions defined as public
            elif self.publics is None and sectname == '.public':
                self.publics = []
                _publicsize = sizeof(self.sp_file_publics)
                num_publics = sect.size / _publicsize

                # Make our Struct array for easy access
                publics = (self.sp_file_publics * num_publics)()
                memmove(addressof(publics),
                        buffer(self.base,sect.dataoffs, sect.size)[:],
                        sect.size)

                for i in xrange(num_publics):
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
                _pubvarsize = sizeof(self.sp_file_pubvars)
                num_pubvars = sect.size / _pubvarsize

                # Make our Struct array for easy access
                pubvars = (self.sp_file_pubvars * num_pubvars)()
                memmove(addressof(pubvars),
                        buffer(self.base,sect.dataoffs, sect.size)[:],
                        sect.size)

                for i in xrange(num_pubvars):
                    pubvar = pubvars[i]
                    sz_name = self._get_string(pubvar.name)
                    offs = self.data + pubvar.address

                    pubvar = self._pubvar(offs, sz_name)
                    self.pubvars.append(pubvar)

                    if pubvar.name == 'myinfo':
                        self.myinfo = pubvar.myinfo
