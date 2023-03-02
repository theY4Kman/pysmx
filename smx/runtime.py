from __future__ import annotations

import sys
import typing
from copy import deepcopy
from ctypes import addressof, sizeof
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, TYPE_CHECKING

from smx.definitions import cell, RTTIControlByte, SP_MAX_EXEC_PARAMS
from smx.interfaces import (
    CallableReturnValue,
    ICallable,
    ParamCopyFlag,
    ParamInfo,
    ParamStringFlag,
    ParamValueT,
)
from smx.rtti import RTTI
from smx.sourcemod.natives.base import convert_return_value, WritableString
from smx.vm import SourcePawnAbstractMachine

if TYPE_CHECKING:
    from smx.plugin import SourcePawnPlugin


class SourcePawnPluginRuntime:
    """Executes SourcePawn plug-ins"""

    def __init__(
        self,
        plugin: SourcePawnPlugin,
        *,
        spew: bool = False,
        spew_stack: bool = False,
        root_path: str | Path | None = None,
        smsys_options: Dict[str, Any] | None = None,
    ):
        """
        :param plugin:
            Plug-in object to envelop a runtime context around

        :param spew:
            Whether to print out traces of instructions as they are executed

        :param spew_stack:
            If spew=True, whether to print out the stack as each instruction is executed

        :param root_path:
            Base path for all calls to `Build_Path` native (with the `Path_SM` — the only available
            flag at time of writing).

        :param smsys_options:
            Options to pass when initializing the `SourceModSystem` instance used by the runtime.

        """
        self.plugin = plugin
        self.spew = spew
        self.spew_stack = spew_stack
        self.root_path = Path(root_path or '.').resolve()
        self.smsys_options = smsys_options or {}

        self.amx = SourcePawnAbstractMachine(self, self.plugin)

        self.pubfuncs_by_name: Dict[str, PluginFunction] = {}
        self.pubfuncs_by_id: Dict[int, PluginFunction] = {}

        self.last_tick = None

        # Saves all the lines printed to the server console
        self.console: List[Tuple[datetime, str]] = []
        self.console_redirect = sys.stdout

    def printf(self, msg) -> None:
        self.console.append((datetime.now(), msg))
        if self.console_redirect is not None:
            print(msg, file=self.console_redirect, end='')

    def get_console_output(self) -> str:
        return ''.join(msg for time, msg in self.console)

    def get_console_lines(self) -> List[str]:
        return [msg for time, msg in self.console]

    def get_function_by_name(self, name: str) -> PluginFunction | None:
        if name in self.pubfuncs_by_name:
            return self.pubfuncs_by_name[name]

        pub = None
        if name in self.plugin.publics_by_name:
            pub = self.plugin.publics_by_name[name]
        elif name in self.plugin.inlines:
            pub = self.plugin.inlines[name]

        if pub:
            func = PluginFunction(self, pub.funcid, pub.code_offs)
            self.pubfuncs_by_id[pub.funcid] = func
            self.pubfuncs_by_name[name] = func
            return func

        return None

    def get_function_by_id(self, funcid: int) -> PluginFunction | None:
        if funcid in self.pubfuncs_by_id:
            return self.pubfuncs_by_id[funcid]

        pub = self.plugin.publics_by_id.get(funcid)
        if pub is None:
            return None

        func = PluginFunction(self, pub.funcid, pub.code_offs)
        self.pubfuncs_by_id[funcid] = func
        self.pubfuncs_by_name[pub.name] = func
        return func

    def call_function_by_name(self, name: str, *args) -> Any:
        func = self.get_function_by_name(name)
        if not func:
            raise ValueError(f'{name!r} is not a valid public function name')
        return func(*args)

    def call_function_by_id(self, funcid: int, *args) -> Any:
        func = self.get_function_by_id(funcid)
        if not func:
            raise ValueError(f'{funcid!r} is not a valid public function ID')
        return func(*args)

    def call_function(self, pubindex, *args) -> None:
        # CODE 0 always seems to be a HALT instruction.
        return_addr = 0
        self.amx._push(return_addr)

        for arg in args:
            self.amx._push(arg)
        self.amx._push(len(args))

        self.amx._pubcall(pubindex)

    def run(self, main: str = 'OnPluginStart') -> Any:
        """Executes the plugin's main function"""
        self.amx.init()
        self.amx.smsys.tick()

        rval = self.call_function_by_name(main)

        self.amx.smsys.timers.poll_for_timers()
        return rval

    def heap_alloc(self, num_cells: int) -> Tuple[int, int]:
        """Allocates a bounded block of memory on the secondary stack of a plugin

        Note that although called a heap, it is in fact a stack.

        :param num_cells:
            Number of cells to allocate

        :return:
            A tuple of (local_addr, phys_addr), where local_addr is the heap offset
            used to deallocate the memory, and phys_addr is the physical address
            where values may be written to

        """
        num_bytes = num_cells * sizeof(cell)

        # TODO(zk): check stack margin

        bounds_addr = self.amx.HEA
        self.amx._writeheap(bounds_addr, cell(num_cells), is_heap=True)
        self.amx.HEA += sizeof(cell)
        local_addr = self.amx.HEA
        phys_addr = addressof(self.amx.heap) + self.amx.HEA

        self.amx.HEA += num_bytes

        return local_addr, phys_addr

    def heap_pop(self, local_addr: int) -> None:
        """Pops a heap address off the heap/secondary stack

        Use this to free memory allocated with heap_alloc()

        Note that in SourcePawn, the heap is in fact a bottom-up stack.
        Deallocations with this method should be performed in precisely the REVERSE order.
        """
        bounds_addr = local_addr - sizeof(cell)
        num_bytes = self.amx._getheapcell(bounds_addr) * sizeof(cell)
        if self.amx.HEA - num_bytes != local_addr:
            # TODO(zk): richer exception, with SM's code (5, SP_ERROR_INVALID_ADDRESS)
            raise RuntimeError('Invalid address')

        self.amx.HEA = bounds_addr


class PluginFunction(ICallable):
    def __init__(self, runtime: SourcePawnPluginRuntime, func_id: int, code_offs: int):
        self.runtime: SourcePawnPluginRuntime = runtime
        self.func_id = func_id
        self.code_offs = code_offs

        self.rtti_method = self.runtime.plugin.rtti_methods_by_addr.get(code_offs)
        self.rtti_args = self.rtti_method.rtti.args if self.rtti_method else None

        #: Holds arguments for the current invocation
        self._params: List[ParamInfo] = []

    def __call__(self, *args):
        call_rval, did_succeed = self.call(*args)
        return call_rval.rval

    def call(self, *args):
        if not self.rtti_method and args:
            raise TypeError(
                'Method has no type information. '
                'Arguments must be specified manually using push_xyz methods.'
            )

        if not self.runtime.amx.initialized:
            self.runtime.amx.init()

        if self.rtti_method:
            self._params = []
            self.push_params(*args)

        return self.invoke()

    def push_params(self, *args) -> None:
        """Push appropriate SP params for the given Python args, using RTTI info"""
        for i, arg in enumerate(args):
            if i >= len(self.rtti_args):
                if self.rtti_args[-1].is_variadic:
                    rtti_arg = self.rtti_args[-1]
                else:
                    raise ValueError(f'Expected {len(self.rtti_args)} arguments, got {len(args)}')
            else:
                rtti_arg = self.rtti_args[i]

            if isinstance(arg, (int, bool, float)):
                if rtti_arg.is_by_ref:
                    # XXX(zk): are there any cases we *don't* want to copy back?
                    self.push_cell_by_ref(arg, ParamCopyFlag.COPYBACK)
                else:
                    self.push_cell(arg)

            elif isinstance(arg, (str, bytes)):
                if rtti_arg.is_by_ref:
                    string_flags = ParamStringFlag.UTF8 if isinstance(arg, str) else ParamStringFlag.BINARY
                    string_flags |= ParamStringFlag.COPY
                    self.push_string_ex(arg, len(arg), string_flags, ParamCopyFlag.COPYBACK)
                else:
                    self.push_string(arg)

            else:
                try:
                    arg_iter = iter(arg)
                except TypeError:
                    raise TypeError(f'Invalid argument type {type(arg)}: {arg!r}')

                arg = list(arg_iter)
                if rtti_arg.is_by_ref:
                    self.push_array(arg, ParamCopyFlag.COPYBACK)
                else:
                    self.push_array(arg)

    def _add_param(self) -> ParamInfo:
        if len(self._params) >= SP_MAX_EXEC_PARAMS:
            raise ValueError(f'Cannot add more than {SP_MAX_EXEC_PARAMS} parameters')

        param = ParamInfo()
        self._params.append(param)
        return param

    def push_cell(self, value: int):
        param = self._add_param()
        param.value = value
        param.marked = False
        return param

    def push_cell_by_ref(self, value: int, flags: ParamCopyFlag = 0):
        param = self.push_array([value], flags)
        param.is_scalar = True
        return param

    def push_float(self, value: float):
        return self.push_cell(typing.cast(int, value))

    def push_float_by_ref(self, value: float, flags: ParamCopyFlag = 0):
        return self.push_cell_by_ref(typing.cast(int, value), flags)

    def push_array(self, value: List[int | float] | None, flags: ParamCopyFlag = 0):
        param = self._add_param()
        param.value = value
        param.is_scalar = False
        param.marked = True
        param.size = len(value) if value is not None else 0
        param.flags = flags if value is not None else 0
        param.is_string = False
        return param

    def push_string(self, value: str):
        return self.push_string_ex(value, len(value) + 1, ParamStringFlag.COPY, 0)

    def push_string_ex(self, value: str, length: int, string_flags: ParamStringFlag = 0, copy_flags: ParamCopyFlag = 0):
        param = self._add_param()
        param.value = value
        param.is_scalar = False
        param.marked = True
        param.size = length
        param.flags = copy_flags
        param.is_string = True
        param.string_flags = string_flags
        return param

    def execute(self) -> Tuple[CallableReturnValue | None, int]:
        # TODO(zk): clear pending exceptions

        rval, err = self.invoke()
        if not err:
            # TODO(zk): return exception code
            return None, -1

        # TODO(zk): constant for "no exception"
        return rval, 0

    def invoke(self) -> Tuple[CallableReturnValue | None, bool]:
        # TODO(zk): check runnable
        # TODO(zk): check error state

        # Copy params, allowing reentrancy (calls within calls, yo)
        params = deepcopy(self._params)

        return_type = self.rtti_method.rtti.inner if self.rtti_method else None
        if return_type and return_type.type == RTTIControlByte.FIXED_ARRAY:
            # If the return type is a fixed array, we need to heap-allocate a buffer for it,
            # and push its address before the other arguments.
            rval_param = ParamInfo(
                is_scalar=False,
                is_rval_buffer=True,
                marked=True,
                size=return_type.cells_sizeof(),
            )
            params.append(rval_param)

        args: List[int] = []
        for param in params:
            # Is this marked as an array?
            if param.marked:
                if not param.is_string:
                    # Allocate a normal/generic array
                    param.local_addr, param.phys_addr = self.runtime.heap_alloc(param.size)
                    if param.value is not None:
                        values = [convert_return_value(v) for v in param.value]
                        array = (cell * len(values))(*values)
                        self.runtime.amx._writeheap(param.local_addr, array)

                else:  # is_string
                    num_cells = (param.size + sizeof(cell) - 1) // sizeof(cell)
                    param.local_addr, param.phys_addr = self.runtime.heap_alloc(num_cells)

                    if param.string_flags & ParamStringFlag.COPY and param.value is not None:
                        # TODO(zk): forego these flags for PluginFunction
                        if param.string_flags & ParamStringFlag.UTF8:
                            assert isinstance(param.value, str)
                            value = param.value.encode('utf-8')
                        elif param.string_flags & ParamStringFlag.BINARY:
                            assert isinstance(param.value, bytes)
                            value = param.value
                        else:
                            assert isinstance(param.value, str)
                            value = param.value.encode('latin-1')
                        buf = WritableString(self.runtime.amx, param.local_addr, param.size)
                        buf.write(value, null_terminate=True)

                if param.is_rval_buffer:
                    # Push the rval buf addr before all other args (in essence, the last arg),
                    # but don't include it in `args`, so `self._call` won't include it in the
                    # number of args passed to the function.
                    self.runtime.amx._push(param.local_addr)
                else:
                    args.append(param.local_addr)

            else:  # not array
                args.append(convert_return_value(param.value))

        # TODO(zk): handle exception states
        rval = self._call(args)

        out_args_rev: List[ParamValueT | None] = []
        for i, param in reversed(tuple(enumerate(params))):
            if not param.marked:
                out_args_rev.append(param.value)
                continue

            if param.is_rval_buffer:
                rtti_arg = return_type
            elif i < len(self.rtti_args):
                rtti_arg = self.rtti_args[i]
            elif self.rtti_args[-1].is_variadic:
                rtti_arg = self.rtti_args[-1]
            else:
                # Default cell type
                rtti_arg = RTTI(self.runtime.plugin, type=RTTIControlByte.ANY)

            if param.flags & ParamCopyFlag.COPYBACK:
                if param.is_string:
                    out_args_rev.append(rtti_arg.interpret_value(param.local_addr, self.runtime.amx, size=param.size))
                elif param.is_scalar:
                    val = self.runtime.amx._getheapcell(param.local_addr)
                    out_args_rev.append(rtti_arg.interpret_value(val, self.runtime.amx))
                else:
                    cells = self.runtime.amx._getheap(param.local_addr, (cell * param.size))
                    values = [rtti_arg.interpret_value(c.value, self.runtime.amx) for c in cells]
                    out_args_rev.append(values)

            self.runtime.heap_pop(param.local_addr)

        call_rval = CallableReturnValue(rval, out_args_rev[::-1])
        return call_rval, True

    def _call(self, args: List[int]) -> Any:
        if not self.runtime.amx.initialized:
            self.runtime.amx.init()

        # Save current runtime state
        prev_stk = self.runtime.amx.STK
        prev_hea = self.runtime.amx.HEA
        prev_frm = self.runtime.amx.FRM
        prev_hp_scope = self.runtime.amx._hp_scope
        prev_cip = self.runtime.amx.CIP
        prev_halted = self.runtime.amx.halted

        # CODE 0 always seems to be a HALT instruction,
        # so when we RETN, we'll halt.
        self.runtime.amx.CIP = 0

        for arg in reversed(args):
            self.runtime.amx._push(arg)
        self.runtime.amx._push(len(args))

        # Abide by calling conventions
        self.runtime.amx.instructions.call(self.runtime.amx, self.code_offs)

        try:
            # Execute the function body
            return self.runtime.amx._execute(self.code_offs)
        finally:
            # Restore the previous runtime state
            self.runtime.amx.STK = prev_stk
            self.runtime.amx._filter_stack(prev_stk)
            self.runtime.amx.HEA = prev_hea
            self.runtime.amx.FRM = prev_frm
            self.runtime.amx._hp_scope = prev_hp_scope
            self.runtime.amx.CIP = prev_cip
            self.runtime.amx.halted = prev_halted
