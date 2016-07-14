# SourcePawn defines
import ctypes

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
