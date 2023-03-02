# SourcePawn defines
from __future__ import annotations

import ctypes
from enum import IntEnum
from typing import List, Tuple

import construct as cs
from construct_typed import csfield, FlagsEnumBase, TFlagsEnum

from smx.struct import Struct

SPFILE_MAGIC = 0x53504646

###
# File format verison number.
# 0x0101 - SourcePawn 1.0 initial version used by SourceMod 1.0.
# 0x0102 - SourcePawn 1.1 used by SourceMod 1.1+.
# 0x0200 - Used by spcomp2.
#
# The major version bits (8-15) indicate a product number. Consumers should
# reject any version for a different product.
#
# The minor version bits (0-7) indicate a compatibility revision. Any minor
# version higher than the current version should be rejected.
#
SP1_VERSION_1_0 = 0x0101
SP1_VERSION_1_1 = 0x0102
SP1_VERSION_1_7 = 0x0107
SP1_VERSION_MIN = SP1_VERSION_1_0
SP1_VERSION_MAX = SP1_VERSION_1_7
SP2_VERSION_MIN = 0x0200
SP2_VERSION_MAX = 0x0200

SPFILE_COMPRESSION_NONE = 0
SPFILE_COMPRESSION_GZ   = 1

###
# Version 9: Initial version.
# Version 10: DEBUG code flag removed; no bytecode changes.
# Version 11: Not used; no changes.
# Version 12: PROC/RETN semantic changes.
# Version 13: Feature flags in code headers.
#
# https:#github.com/alliedmodders/sourcepawn/blob/cd3275790e330/include/smx/smx-headers.h#L62-L66
#
SP_CODEVERS_MINIMUM       = 9
SP_CODEVERS_SM_LEGACY     = 10
SP_CODEVERS_FEATURE_MASK  = 13
SP_CODEVERS_CURRENT       = SP_CODEVERS_FEATURE_MASK
SP_CODEVERS_ALWAYS_REJECT = 0x7f

SP_FLAG_DEBUG = (1 << 0)

SP_SYM_VARIABLE     = 1   # Cell that has an address and that can be fetched directly (lvalue)
SP_SYM_REFERENCE    = 2   # VARIABLE, but must be dereferenced
SP_SYM_ARRAY        = 3   # Symbol is an array
SP_SYM_REFARRAY     = 4   # An array passed by reference (i.e. a pointer)
SP_SYM_FUNCTION     = 9   # Symbol is a function
SP_SYM_VARARGS      = 11  # Variadic argument start.

SP_NATIVE_UNBOUND   = 0  # Native is undefined
SP_NATIVE_BOUND     = 1  # Native is bound

SP_NTVFLAG_OPTIONAL = (1 << 0) # Native is optional

SP_DBG_SCOPE_GLOBAL = 0
SP_DBG_SCOPE_LOCAL  = 1
SP_DBG_SCOPE_STATIC = 2

#: Maximum number of parameters in a function signature
SP_MAX_EXEC_PARAMS = 32
#: Maximum number of arguments when calling a function (relates to the bit pattern of sEXPRSTART)
SP_MAX_CALL_ARGUMENTS = 127

ucell = ctypes.c_uint32
cell = ctypes.c_int32

# Base type of all ctypes. Not importable anywhere.
PyCSimpleType = type(cell)


class SPCodeFeature(FlagsEnumBase):
    Deprecated0 = 1 << 0

    # This feature adds the INIT_ARRAY opcode, and requires that multi-dimensional
    # arrays use direct internal addressing.
    DirectArrays = 1 << 1

    # This feature adds the HEAP_SAVE and HEAP_RESTORE opcodes.
    HeapScopes = 1 << 2


class SPFileSection(Struct):
    """File section header format."""
    nameoffs: int = csfield(cs.Int32ul)  # Relative offset into global string table
    dataoffs: int = csfield(cs.Int32ul)  # Offset into the data section of the file
    size: int = csfield(cs.Int32ul)      # Size of the section's entry in the data section


class SPFileHdr(Struct):
    """File header format.  If compression is 0, then disksize may be 0
    to mean that only the imagesize is needed."""
    magic: int = csfield(cs.Int32ul)         # Magic number
    version: int = csfield(cs.Int16ul)       # Version code
    compression: int = csfield(cs.Int8ul)    # Compression algorithm
    disksize: int = csfield(cs.Int32ul)      # Size on disk
    imagesize: int = csfield(cs.Int32ul)     # Size in memory
    sections: int = csfield(cs.Int8ul)       # Number of sections
    stringtab: int = csfield(cs.Int32ul)     # Offset to string table
    dataoffs: int = csfield(cs.Int32ul)      # Offset to file proper (any compression starts here)


class SPFileCode(Struct):
    """File-encoded format of the ".code" section."""
    codesize: int = csfield(cs.Int32ul)    # Codesize in bytes
    cellsize: int = csfield(cs.Int8ul)     # Cellsize in bytes
    codeversion: int = csfield(cs.Int8ul)  # Version of opcodes supported
    flags: int = csfield(cs.Int16ul)       # Flags
    main: int = csfield(cs.Int32ul)        # Address to "main," if any
    code: int = csfield(cs.Int32ul)        # Relative offset to code

    ##
    # List of features flags that this code requires.
    #
    # This field is only guaranteed to be present when codeversion >= 13 or
    # higher. Note that newer spcomp versions will still include a 0-filled
    # value. This is legal since anything between the end of the code header
    # and the code buffer is undefined. The field should still be ignored.
    #
    features: int = csfield(TFlagsEnum(cs.Int32ul, SPCodeFeature))


class SPFileData(Struct):
    """File-encoded format of the ".data" section."""
    datasize: int = csfield(cs.Int32ul)  # Size of data section in memory
    memsize: int = csfield(cs.Int32ul)   # Total mem required (includes data)
    data: int = csfield(cs.Int32ul)      # File offset to data (helper)


class SPFilePublics(Struct):
    """File-encoded format of the ".publics" section."""
    address: int = csfield(cs.Int32ul)  # Address relative to code section
    name: int = csfield(cs.Int32ul)     # Index into nametable


class SPFileNatives(Struct):
    """File-encoded format of the ".natives" section."""
    name: int = csfield(cs.Int32ul)  # Index into nametable


class SPFilePubvars(Struct):
    """File-encoded format of the ".pubvars" section."""
    address: int = csfield(cs.Int32ul)  # Address relative to the DAT section
    name: int = csfield(cs.Int32ul)     # Index into nametable


class SPFileTag(Struct):
    """File-encoded format of the ".tags" section."""
    tag_id: int = csfield(cs.Int32ul)  # Tag ID from compiler
    name: int = csfield(cs.Int32ul)    # Index into nametable


class SPFdbgInfo(Struct):
    """File-encoded debug information table."""
    num_files: int = csfield(cs.Int32ul)   # number of files
    num_lines: int = csfield(cs.Int32ul)   # number of lines
    num_syms: int = csfield(cs.Int32ul)    # number of symbols
    num_arrays: int = csfield(cs.Int32ul)  # number of symbols which are arrays


class SPFdbgFile(Struct):
    """File-encoded debug file table."""
    addr: int = csfield(cs.Int32ul)  # Address into code
    name: int = csfield(cs.Int32ul)  # Offset into debug nametable


class SPFdbgLine(Struct):
    """File-encoded debug line table."""
    addr: int = csfield(cs.Int32ul)  # Address into code
    line: int = csfield(cs.Int32ul)  # Line number


class SPFdbgArrayDim(Struct):
    """File-encoded debug array dimension information."""
    tagid: int = csfield(cs.Int16ul)  # Tag id
    size: int = csfield(cs.Int32ul)   # Size of dimension


class SPFdbgSymbol(Struct):
    """File-encoded debug symbol information."""
    addr: int = csfield(cs.Int32ul)        # Address rel to DAT or stack frame
    tagid: int = csfield(cs.Int16ul)       # Tag id
    codestart: int = csfield(cs.Int32ul)   # Start scope validity in code
    codeend: int = csfield(cs.Int32ul)     # End scope validity in code
    ident: int = csfield(cs.Int8ul)        # Variable type
    vclass: int = csfield(cs.Int8ul)       # Scope class (local vs global)
    dimcount: int = csfield(cs.Int16ul)    # Dimension count (for arrays)
    name: int = csfield(cs.Int32ul)        # Offset into debug nametable

    dims: List[SPFdbgArrayDim] = csfield(SPFdbgArrayDim[cs.this.dimcount])


class SPFdbgNtvArg(Struct):
    """An argument of a .dbg.natives entry

    Each is followed by an SPFdbgArrayDim (sp_fdbg_arraydim_t) for each dimcount.
    """
    ident: int = csfield(cs.Int8ul)       # Variable type
    tagid: int = csfield(cs.Int16ul)      # Tag id
    dimcount: int = csfield(cs.Int16ul)   # Dimension count (for arrays)
    name: int = csfield(cs.Int32ul)       # Offset into debug nametable

    dims: List[SPFdbgArrayDim] = csfield(SPFdbgArrayDim[cs.this.dimcount])


class SPFdbgNative(Struct):
    """An entry in the .dbg.natives section.

    Each is followed by an SPFdbgNtvArg (sp_fdbg_ntvarg_t) for each argument.
    """
    index: int = csfield(cs.Int32ul)  # Native index in the plugin.
    name: int = csfield(cs.Int32ul)   # Offset into debug nametable.
    tagid: int = csfield(cs.Int16ul)  # Return tag.
    nargs: int = csfield(cs.Int16ul)  # Number of formal arguments.

    args: List[SPFdbgNtvArg] = csfield(SPFdbgNtvArg[cs.this.nargs])


class SPFdbgNtvTab(Struct):
    """Header for the ".dbg.natives" section.

    It is followed by a number of SPFdbgNative (sp_fdbg_native_t) entries.
    """
    num_entries: int = csfield(cs.Int32ul)  # Number of entries
    natives: List[SPFdbgNative] = csfield(SPFdbgNative[cs.this.num_entries])


class SmxRTTITableHeader(Struct):
    """All row-based RTTI tables have this layout."""
    header_size: int = csfield(cs.Int32ul)  # Size of the header; row data is immediately after.
    row_size: int = csfield(cs.Int32ul)     # Size of each row in the table.
    row_count: int = csfield(cs.Int32ul)    # Number of elements in the table.


class SmxRTTIEnum(Struct):
    """An entry in the rtti.enums table"""
    name: int = csfield(cs.Int32ul)  # Index into the names table.

    # Reserved - must be 0.
    reserved0: int = csfield(cs.Int32ul)
    reserved1: int = csfield(cs.Int32ul)
    reserved2: int = csfield(cs.Int32ul)


class SmxRTTIEnumTable(Struct):
    """The rtti.enums table."""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    enums: List[SmxRTTIEnum] = csfield(SmxRTTIEnum[cs.this.header.row_count])


class SmxRTTIMethod(Struct):
    """An entry in the rtti.methods table"""
    # Index into the name table.
    name: int = csfield(cs.Int32ul)

    # Function location, range is [pcode_start, pcode_end).
    pcode_start: int = csfield(cs.Int32ul)
    pcode_end: int = csfield(cs.Int32ul)

    # Method signature; offset into rtti.data. The encoding at this offset is:
    #    FormalArgs    uint8
    #    Variadic?     uint8
    #    ReturnType    <return-type>
    #    Params*       <param>
    #
    # <return-type> must be kVoid or a <type>.
    # <param> must be: kByRef? <type>
    signature: int = csfield(cs.Int32ul)


class SmxRTTIMethodTable(Struct):
    """The rtti.methods table."""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    methods: List[SmxRTTIMethod] = csfield(SmxRTTIMethod[cs.this.header.row_count])


class SmxRTTINative(Struct):
    """An entry in the rtti.natives table

    The rows must be identical to the native table mapping.
    """
    # Index into the name table.
    name: int = csfield(cs.Int32ul)

    # Method signature; see smx_rtti_method::signature.
    signature: int = csfield(cs.Int32ul)


class SmxRTTINativeTable(Struct):
    """The rtti.natives table."""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    natives: List[SmxRTTINative] = csfield(SmxRTTINative[cs.this.header.row_count])


class SmxRTTITypedef(Struct):
    """An entry in the rtti.typedefs table"""
    # Index into the name table.
    name: int = csfield(cs.Int32ul)

    # Type identifier. The type must be a concrete type, not an entry in the
    # typedef table.
    type_id: int = csfield(cs.Int32ul)


class SmxRTTITypedefTable(Struct):
    """The rtti.typedefs table."""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    typedefs: List[SmxRTTITypedef] = csfield(SmxRTTITypedef[cs.this.header.row_count])


class SmxRTTITypeset(Struct):
    """An entry in the rtti.typesets table"""
    # Index into the name table.
    name: int = csfield(cs.Int32ul)

    # Typeset signature; offset into rtti.data. The encoding is:
    #    NumTypes      uint32
    #    Types*        type
    signature: int = csfield(cs.Int32ul)


class SmxRTTITypesetTable(Struct):
    """The rtti.typesets table."""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    typesets: List[SmxRTTITypeset] = csfield(SmxRTTITypeset[cs.this.header.row_count])


class SmxRTTIEnumStruct(Struct):
    """An entry in the rtti.enumstructs table"""
    # Index into the name table.
    name: int = csfield(cs.Int32ul)

    # First row in the rtti.enumstruct_fields table. Rows up to the next
    # enumstruct's first row, or the end of the enumstruct table, are
    # owned by this entry.
    first_field: int = csfield(cs.Int32ul)

    # Size of the enum struct in cells.
    size: int = csfield(cs.Int32ul)


class SmxRTTIEnumStructTable(Struct):
    """The rtti.enumstructs table."""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    enumstructs: List[SmxRTTIEnumStruct] = csfield(SmxRTTIEnumStruct[cs.this.header.row_count])


class SmxRTTIEnumStructField(Struct):
    """An entry in the rtti.enumstruct_fields table"""
    # Index into the name table.
    name: int = csfield(cs.Int32ul)

    # Type id.
    type_id: int = csfield(cs.Int32ul)

    # Offset from the base address, in cells.
    offset: int = csfield(cs.Int32ul)


class SmxRTTIEnumStructFieldTable(Struct):
    """The rtti.es_fields table."""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    fields: List[SmxRTTIEnumStructField] = csfield(SmxRTTIEnumStructField[cs.this.header.row_count])


class SmxRTTIClassDef(Struct):
    """An entry in the rtti.classdef table"""
    # Bits 0-1 indicate the definition type.
    flags: int = csfield(cs.Int32ul)

    # Index into the name table.
    name: int = csfield(cs.Int32ul)

    # First row in the rtti.fields table. Rows up to the next classdef's first
    # row, or the end of the fields table, are owned by this classdef.
    first_field: int = csfield(cs.Int32ul)

    # Unused, currently 0.
    reserved0: int = csfield(cs.Int32ul)
    reserved1: int = csfield(cs.Int32ul)
    reserved2: int = csfield(cs.Int32ul)
    reserved3: int = csfield(cs.Int32ul)


class SmxRTTIClassDefTable(Struct):
    """The rtti.classdef table."""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    classdefs: List[SmxRTTIClassDef] = csfield(SmxRTTIClassDef[cs.this.header.row_count])


class SmxRTTIField(Struct):
    """An entry in the rtti.fields table"""
    # Currently 0.
    flags: int = csfield(cs.Int16ul)

    # Index into the name table.
    name: int = csfield(cs.Int32ul)

    # Type id.
    type_id: int = csfield(cs.Int32ul)


class SmxRTTIFieldTable(Struct):
    """The rtti.fields table."""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    fields: List[SmxRTTIField] = csfield(SmxRTTIField[cs.this.header.row_count])


RTTI_CLASS_DEF_TYPE_STRUCT = 0x0

# A type identifier is a 32-bit value encoding a type. It is encoded as
# follows:
#   bits 0-3:  type kind
#   bits 4-31: type payload
#
# The kind is a type signature that can be completely inlined in the
# remaining 28 bits.
RTTI_TYPE_ID_INLINE = 0x0
# The payload is an index into the rtti.data section.
RTTI_TYPE_ID_COMPLEX = 0x1

RTTI_MAX_TYPE_ID_PAYLOAD = 0xfffffff
RTTI_MAX_TYPE_ID_KIND = 0xf


# These are control bytes for type signatures.
#
# uint32 values are encoded with a variable length encoding:
#   0x00  - 0x7f:    1 byte
#   0x80  - 0x7fff:  2 bytes
#   0x8000 - 0x7fffff: 3 bytes
#   0x800000 - 0x7fffffff: 4 bytes
#   0x80000000 - 0xffffffff: 5 bytes

class RTTIControlByte(IntEnum):
    # This section encodes raw types.
    BOOL = 0x01
    INT32 = 0x06
    FLOAT32 = 0x0c
    CHAR8 = 0x0e
    ANY = 0x10
    TOP_FUNCTION = 0x11

    # This section encodes multi-byte raw types.

    # kFixedArray is followed by:
    #    Size          uint32
    #    Type          <type>
    #
    # kArray is followed by:
    #    Type          <type>
    FIXED_ARRAY = 0x30
    ARRAY = 0x31

    # kFunction is always followed by the same encoding as in
    # smx_rtti_method::signature.
    FUNCTION = 0x32

    # Each of these is followed by an index into an appropriate table.
    ENUM = 0x42  # rtti.enums
    TYPEDEF = 0x43  # rtti.typedefs
    TYPESET = 0x44  # rtti.typesets
    CLASSDEF = 0x45  # rtti.classdefs
    ENUM_STRUCT = 0x46  # rtti.enumstructs

    # This section encodes special indicator bytes that can appear within multi-byte types.

    # For function signatures, indicating no return value.
    VOID = 0x70
    # For functions, indicating the last argument of a function is variadic.
    VARIADIC = 0x71
    # For parameters, indicating pass-by-ref.
    BY_REF = 0x72
    # For reference and compound types, indicating const.
    CONST = 0x73


RTTI_CB_RAW_TYPES = {
    RTTIControlByte.BOOL,
    RTTIControlByte.INT32,
    RTTIControlByte.FLOAT32,
    RTTIControlByte.CHAR8,
    RTTIControlByte.ANY,
    RTTIControlByte.TOP_FUNCTION,
}

RTTI_CB_INDEXED_TYPES = {
    RTTIControlByte.ENUM,
    RTTIControlByte.TYPEDEF,
    RTTIControlByte.TYPESET,
    RTTIControlByte.CLASSDEF,
    RTTIControlByte.ENUM_STRUCT,
}


###
# The following tables are extension tables; the VM does not depend on them
# to function correctly.
#
# The new debug tables are:
#    .dbg.methods
#    .dbg.locals
#    .dbg.globals
#
# The methods table only exists to partition the locals table. Each method
# entry owns a contiguous group of rows in the locals table. The locals table
# contains both static and non-static variables.
#
# To find the owner of a global address when in function scope, first static
# methods in debug.methods should be traversed, then the .globals table.
#


class SmxRTTIDebugMethod(Struct):
    """An entry in the .dbg.methods table

    This table describes how to find local variable debug info.
    """
    # Index into the rtti.methods table.
    method_index: int = csfield(cs.Int32ul)

    # Index into .dbg.locals of the first local in this method. The number of
    # rows owned by this method can be determined by either:
    #   (1) The next method's first_local value, or
    #   (2) The end of the .locals table if this is the last method.
    first_local: int = csfield(cs.Int32ul)


class SmxRTTIDebugMethodTable(Struct):
    """A table of .dbg.methods entries"""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    methods: List[SmxRTTIDebugMethod] = csfield(SmxRTTIDebugMethod[cs.this.header.row_count])


class SmxRTTIDebugVar(Struct):
    """An entry in the rtti.debug_locals or rtti.debug_globals table"""
    # Address, the meaning of which depends on the pcode version and method
    # scope (local, static, global).
    address: int = csfield(cs.Int32sl)

    # Bits 0-1 encode what kind of variable this is; see kVarClass below.
    vclass: int = csfield(cs.Int8ul)

    # Variable name (index into the name table).
    name: int = csfield(cs.Int32ul)

    # Scope visibility, [code_start, code_end].
    code_start: int = csfield(cs.Int32ul)
    code_end: int = csfield(cs.Int32ul)

    # Variable type id.
    type_id: int = csfield(cs.Int32ul)


class SmxRTTIDebugVarTable(Struct):
    """A table of rtti.debug_locals or rtti.debug_globals table entries"""
    header: SmxRTTITableHeader = csfield(SmxRTTITableHeader.as_struct())
    vars: List[SmxRTTIDebugVar] = csfield(SmxRTTIDebugVar[cs.this.header.row_count])


# Values for smx_rtti_debug_var::vclass.
RTTI_VAR_CLASS_GLOBAL = 0x0
RTTI_VAR_CLASS_LOCAL = 0x1
RTTI_VAR_CLASS_STATIC = 0x2
RTTI_VAR_CLASS_ARG = 0x3


def rtti_decode_uint32(data: bytes, offset: int) -> Tuple[int, int]:
    """Decode a uint32 from a variable-length encoded stream.

    Returns the decoded value and the new offset.
    """
    value = 0
    shift = 0
    while True:
        b = data[offset]
        offset += 1
        value |= (b & 0x7f) << shift
        if not b & 0x80:
            break
        shift += 7
    return value, offset


class Myinfo(Struct):
    name: int = csfield(cs.Int32ul)
    description: int = csfield(cs.Int32ul)
    author: int = csfield(cs.Int32ul)
    version: int = csfield(cs.Int32ul)
    url: int = csfield(cs.Int32ul)
