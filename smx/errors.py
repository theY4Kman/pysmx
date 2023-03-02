from enum import IntEnum


class SourcePawnErrorCode(IntEnum):
    NONE = 0, 'No error occurred'
    FILE_FORMAT = 1, 'Unrecognizable file format'
    DECOMPRESSOR = 2, 'Decompressor was not found'
    HEAPLOW = 3, 'Not enough space on the heap'
    PARAM = 4, 'Invalid parameter or parameter type'
    INVALID_ADDRESS = 5, 'Invalid plugin address'
    NOT_FOUND = 6, 'Object or index not found'
    INDEX = 7, 'Invalid index or index not found'
    STACKLOW = 8, 'Not enough space on the stack'
    NOTDEBUGGING = 9, 'Debug section not found or debug not enabled'
    INVALID_INSTRUCTION = 10, 'Invalid instruction'
    MEMACCESS = 11, 'Invalid memory access'
    STACKMIN = 12, 'Stack went below stack boundary'
    HEAPMIN = 13, 'Heap went below heap boundary'
    DIVIDE_BY_ZERO = 14, 'Divide by zero'
    ARRAY_BOUNDS = 15, 'Array index is out of bounds'
    INSTRUCTION_PARAM = 16, 'Instruction contained invalid parameter'
    STACKLEAK = 17, 'Stack memory leaked by native'
    HEAPLEAK = 18, 'Heap memory leaked by native'
    ARRAY_TOO_BIG = 19, 'Dynamic array is too big'
    TRACKER_BOUNDS = 20, 'Tracker stack is out of bounds'
    INVALID_NATIVE = 21, 'Native is not bound'
    PARAMS_MAX = 22, 'Maximum number of parameters reached'
    NATIVE = 23, 'Native detected error'
    NOT_RUNNABLE = 24, 'Plugin not runnable'
    ABORTED = 25, 'Call was aborted'
    CODE_TOO_OLD = 26, 'Plugin format is too old'
    CODE_TOO_NEW = 27, 'Plugin format is too new'
    OUT_OF_MEMORY = 28, 'Out of memory'
    INTEGER_OVERFLOW = 29, 'Integer overflow'
    TIMEOUT = 30, 'Script execution timed out'
    USER = 31, 'Custom error'
    FATAL = 32, 'Fatal error'

    msg: str

    def __new__(cls, value: int, msg: str):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.msg = msg
        return obj
