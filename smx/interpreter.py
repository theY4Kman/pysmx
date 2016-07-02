import numpy as np

from ctypes import *

from smx.opcodes import opcodes
from smx.smxdefs import cell


class struct(object):
    """An object whose constructor accepts kwargs to set instance vars"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class sp_plugin(object):
    base = None             # Base of memory for this plugin.
    base_size = None        # Size of the entire plugin base
    pcode = None            # P-Code of plugin
    pcode_size = None       # Size of p-code
    data = None             # Data/memory layout
    data_size = None        # Size of data
    mem_size = None         # Required memory space
    flags = None            # Code flags
    debug = None            # Debug info table
    memory = None           # Data chunk
    stringbase = None       # base of string table
    publics = None          # Public functions table
    num_publics = None      # Number of publics.
    pubvars = None          # Public variables table
    num_pubvars = None      # Number of public variables
    natives = None          # Natives table
    num_natives = None      # Number of natives
    prof_flags = None       # Profiling flags
    run_flags = None        # Runtime flags
    pcode_version = None    # P-Code version number
    name = None             # Plugin/script name

    def __init__(self, plugin):
        """

        @type plugin: smx.smxreader.SourcePawnPlugin
        """
        self.base = np.array(plugin.base, np.uint8)
        self.base_size = len(plugin.base)
        self.pcode = self.base[plugin.pcode.pcode:plugin.pcode.pcode+plugin.pcode.size]
        self.pcode_size = plugin.pcode.size
        self.data = plugin.data
        self.data_size = plugin.datasize
        self.mem_size = plugin.memsize
        self.flags = plugin.flags
        self.debug = plugin.debug

        self.memory = np.zeros(self.mem_size, np.uint8)
        self.memory[:self.data_size] = plugin.data

        self.stringbase = plugin.stringbase
        self.publics = plugin.natives
        self.num_publics = len(plugin.natives)
        self.pubvars = plugin.pubvars
        self.num_pubvars = len(plugin.pubvars)
        self.natives = plugin.natives
        self.num_natives = plugin.num_natives

        self.prof_flags = None
        self.run_flags = None

        self.pcode_version = plugin.pcode.version
        self.name = plugin.name


SP_MAX_RETURN_STACK = 1024


class sp_context(struct):
    hp = None           # Heap pointer
    sp = None           # Stack pointer
    frm = None          # Frame pointer
    rval = None         # Return value from InvokeFunction()
    cip = None          # Code pointer last error occurred in
    err = None          # Error last set by interpreter
    n_err = None        # Error code set by a native
    n_idx = None        # Current native index being executed
    tracker = None
    plugin = None
    basecx = None
    vm = [None] * 8     # VM-specific pointers
    rp = None           # Return stack pointer
    rstk_cips = [0] * SP_MAX_RETURN_STACK



class BaseContext(object):
    def __init__(self, plugin):
        """

        @param plugin:
        @type plugin: smx.smxreader.SourcePawnPlugin
        """
        self.plugin = plugin

        self.ctx = sp_context()
        self.ctx.hp = self.plugin.datasize
        self.ctx.sp = self.plugin.memsize - sizeof(cell)
        self.ctx.frm = self.ctx.sp
        self.ctx.n_err = None
        self.ctx.n_idx = None
        self.ctx.rp = 0

    def get_ctx(self):
        return self.ctx


class Interpreter(object):
    def __init__(self, plugin):
        """

        @param plugin:
        @type plugin: smx.smxreader.SourcePawnPlugin
        """
        self.py_plugin = plugin
        self.plugin = sp_plugin(self.py_plugin)

    def call_function_by_name(self, name):
        pubfunc = self.py_plugin.runtime.get_function_by_name(name)
        if pubfunc is None:
            raise NameError('"%s" is not a valid function' % name)

        return self.interpret(pubfunc.code_offs)

    def is_valid_offset(self, cip):
        return cip % 4 == 0

    def interpret(self, code_start):
        code = self.plugin.pcode
        code_size = code.size

        if not self.is_valid_offset(code_start) or code_start > code_size:
            raise Exception('Invalid instruction')

        self.ctx = BaseContext(self.py_plugin).get_ctx()
        orig_frm = self.ctx.frm

        self.pri = 0
        self.alt = 0
        self.cip = code[code_start:]
        self.stk = self.plugin.memory[self.ctx.sp:]

        while True:
            op = self.cip[0]
            self.cip = self.cip[sizeof(cell):]

            opname = opcodes[op]
            methname = 'op_' + opname
            if hasattr(self, methname):
                getattr(self, methname)()
            else:
                raise Exception('Unsupported operation %s' % opname)

    def op_mov_pri(self):
        self.pri = self.alt
    def op_mov_alt(self):
        self.alt = self.pri

    def op_xchg(self):
        self.pri, self.alt = self.alt, self.pri

    def op_zero(self):
        self.write(self.cip[0], 0)
        self.cip = self.cip[sizeof(cell):]

    def op_zero_s(self):
        self.write(self.ctx.frm + self.cip[0], 0)
        self.cip = self.cip[sizeof(cell):]

    def op_push_pri(self):
        self.stk = self.stk
