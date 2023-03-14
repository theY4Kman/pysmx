from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from smx.errors import SourcePawnErrorCode
    from smx.vm import SourcePawnAbstractMachine


class SourcePawnPluginError(Exception):
    """Base exception type for SourcePawn-related errors"""


class SourcePawnPluginFormatError(SourcePawnPluginError):
    """Errors reading SMX files"""


class SourcePawnPluginNativeError(SourcePawnPluginError):
    """Invalid native, or error invoking native"""


class SourcePawnUnboundNativeError(SourcePawnPluginNativeError, NotImplementedError):
    """Native not bound to an implementation"""


class SourcePawnStringFormatError(SourcePawnPluginNativeError):
    """Error during string formatting natives (PrintToChat, etc)"""


class SourcePawnOpcodeDeprecated(DeprecationWarning):
    """Deprecated opcode encountered during execution"""


class SourcePawnOpcodeNotSupported(SourcePawnOpcodeDeprecated):
    """Unsupported opcode encountered during execution"""


class SourcePawnOpcodeNotGenerated(SourcePawnOpcodeDeprecated):
    """A Pawn opcode was encountered which is not generated by spcomp"""


class SourcePawnRuntimeError(SourcePawnPluginError, RuntimeError):
    """Error encountered during execution of a SourcePawn program"""

    def __init__(self, msg: str, amx: SourcePawnAbstractMachine, *, code: SourcePawnErrorCode | None = None):
        super().__init__(msg)
        self.amx = amx
        self.frames = [copy(frame) for frame in amx._frames]
        self.code = code

    def dump_stack(self) -> str:
        """Dump the current stack trace to a string"""
        from smx.vm import dump_stack
        return dump_stack(self.frames)

    def debug_output(self) -> str:
        """Dump the current stack trace and error message to a string"""
        return f'Exception thrown: {self}\n{self.dump_stack()}\n'

    def stderr(self) -> str:
        """Format stderr like SourceMod would"""
        for frame in self.frames:
            if frame.meth:
                break
        else:
            return f'Exception thrown: {self}\n'

        frame_name = frame.name or '<unknown>'
        return f'Error executing {frame_name}: {self}\n'
