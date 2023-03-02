from smx.sourcemod.natives.base import native, SourceModNativesMixin


class HandlesNatives(SourceModNativesMixin):
    @native('cell')
    def CloseHandle(self, handle_id: int) -> None:
        # TODO(zk): run time error if handle is invalid
        self.sys.handles.close_handle(handle_id)
