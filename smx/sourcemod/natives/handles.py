from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import native, SourceModNativesMixin


class HandlesNatives(SourceModNativesMixin):
    @native
    def CloseHandle(self, handle_id: int) -> None:
        # TODO(zk): run time error if handle is invalid
        self.sys.handles.close_handle(handle_id)

    @native
    def CloneHandle(self, hndl: SourceModHandle, plugin: SourceModHandle) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def IsValidHandle(self, hndl: SourceModHandle) -> bool:
        return hndl.id in self.sys.handles
