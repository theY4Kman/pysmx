# SourcePawn defines
from __future__ import division

import ctypes

from smx.struct import *


SPFILE_MAGIC = 0x53504646

SPFILE_COMPRESSION_NONE = 0
SPFILE_COMPRESSION_GZ   = 1

SP_CODEVERS_JIT1    = 9
SP_CODEVERS_JIT2    = 10

SP_FLAG_DEBUG = (1<<0)

SP_SYM_VARIABLE     = 1  # Cell that has an address and that can be fetched directly (lvalue)
SP_SYM_REFERENCE    = 2  # VARIABLE, but must be dereferenced
SP_SYM_ARRAY        = 3  # Symbol is an array
SP_SYM_REFARRAY     = 4  # An array passed by reference (i.e. a pointer)
SP_SYM_FUNCTION     = 9  # Symbol is a function
SP_SYM_VARARGS      = 11 # Variadic argument start.

SP_NATIVE_UNBOUND   = 0  # Native is undefined
SP_NATIVE_BOUND     = 1  # Native is bound

SP_NTVFLAG_OPTIONAL = (1<<0) # Native is optional

SP_DBG_SCOPE_GLOBAL = 0
SP_DBG_SCOPE_LOCAL  = 1
SP_DBG_SCOPE_STATIC = 2

ucell = ctypes.c_uint32
cell = ctypes.c_int32


class sp_file_section(NoAlignStruct):
    """File section header format."""
    nameoffs = cf_uint32()  # Relative offset into global string table
    dataoffs = cf_uint32()  # Offset into the data section of the file
    size = cf_uint32()  # Size of the section's entry in the data section


class sp_file_hdr(NoAlignStruct):
    """File header format.  If compression is 0, then disksize may be 0
    to mean that only the imagesize is needed."""
    magic = cf_uint32()  # Magic number
    version = cf_uint16()  # Version code
    compression = cf_uint8()  # Compression algorithm
    disksize = cf_uint32()  # Size on disk
    imagesize = cf_uint32()  # Size in memory
    sections = cf_uint8()  # Number of sections
    stringtab = cf_uint32()  # Offset to string table
    dataoffs = cf_uint32()  # Offset to file proper (any compression starts here)


class sp_file_code(NoAlignStruct):
    """File-encoded format of the ".code" section."""
    codesize = cf_uint32()  # Codesize in bytes
    cellsize = cf_uint8()  # Cellsize in bytes
    codeversion = cf_uint8()  # Version of opcodes supported
    flags = cf_uint16()  # Flags
    main = cf_uint32()  # Address to "main," if any
    code = cf_uint32()  # Relative offset to code


class sp_file_data(NoAlignStruct):
    """File-encoded format of the ".data" section."""
    datasize = cf_uint32()  # Size of data section in memory
    memsize = cf_uint32()  # Total mem required (includes data)
    data = cf_uint32()  # File offset to data (helper)


class sp_file_publics(NoAlignStruct):
    """File-encoded format of the ".publics" section."""
    address = cf_uint32()  # Address relative to code section
    name = cf_uint32()  # Index into nametable


class sp_file_natives(NoAlignStruct):
    """File-encoded format of the ".natives" section."""
    name = cf_uint32()  # Index into nametable


class sp_file_pubvars(NoAlignStruct):
    """File-encoded format of the ".pubvars" section."""
    address = cf_uint32()  # Address relative to the DAT section
    name = cf_uint32()  # Index into nametable


class sp_file_tag(NoAlignStruct):
    """File-encoded tag info."""
    tag_id = cf_uint32()  # Tag ID from compiler
    name = cf_uint32()  # Index into nametable


class sp_fdbg_info(NoAlignStruct):
    """File-encoded debug information table."""
    num_files = cf_uint32()  # number of files
    num_lines = cf_uint32()  # number of lines
    num_syms = cf_uint32()  # number of symbols
    num_arrays = cf_uint32()  # number of symbols which are arrays


class sp_fdbg_file(NoAlignStruct):
    """File-encoded debug file table."""
    addr = cf_uint32()  # Address into code
    name = cf_uint32()  # Offset into debug nametable


class sp_fdbg_line(NoAlignStruct):
    """File-encoded debug line table."""
    addr = cf_uint32()  # Address into code
    line = cf_uint32()  # Line number


class sp_fdbg_symbol(NoAlignStruct):
    """File-encoded debug symbol information."""
    addr = cf_int32()  # Address rel to DAT or stack frame
    tagid = cf_int16()  # Tag id
    codestart = cf_uint32()  # Start scope validity in code
    codeend = cf_uint32()  # End scope validity in code
    ident = cf_uint8()  # Variable type
    vclass = cf_uint8()  # Scope class (local vs global)
    dimcount = cf_uint16()  # Dimension count (for arrays)
    name = cf_uint32()  # Offset into debug nametable


class sp_fdbg_arraydim(NoAlignStruct):
    """Occurs after an fdbg_symbol entry, for each dimension."""
    tagid = cf_int16()  # Tag id
    size = cf_uint32()  # Size of dimension


class sp_fdbg_ntvtab(NoAlignStruct):
    """Header for the ".dbg.natives" section.

    It is followed by a number of sp_fdbg_native_t entries.
    """
    num_entries = cf_uint32()  # Number of entries


class sp_fdbg_native(NoAlignStruct):
    """An entry in the .dbg.natives section.

    Each is followed by an sp_fdbg_ntvarg_t for each argument.
    """
    index = cf_uint32()  # Native index in the plugin.
    name = cf_uint32()  # Offset into debug nametable.
    tagid = cf_int16()  # Return tag.
    nargs = cf_uint16()  # Number of formal arguments.


class sp_fdbg_ntvarg(NoAlignStruct):
    """Each entry is followed by an sp_fdbg_arraydim_t for each dimcount."""
    ident = cf_uint8()  # Variable type
    tagid = cf_int16()  # Tag id
    dimcount = cf_uint16()  # Dimension count (for arrays)
    name = cf_uint32()  # Offset into debug nametable


class Myinfo(NoAlignStruct):
    name = cf_uint32()
    description = cf_uint32()
    author = cf_uint32()
    version = cf_uint32()
    url = cf_uint32()
