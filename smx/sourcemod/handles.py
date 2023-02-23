from __future__ import annotations

from typing import Any, Callable, Dict


class SourceModHandle:
    def __init__(self, id: int, obj: Any, on_close: Callable[[], None] | None = None):
        self.id = id
        self.obj = obj
        self.on_close = on_close

    def close(self):
        if self.on_close:
            self.on_close()


class SourceModHandles:
    """Emulates SourceMod's handles"""

    def __init__(self, sys):
        self.sys = sys
        self._handle_counter = 0
        self._handles: Dict[int, SourceModHandle] = {}
        # TODO(zk): cloning support? ref counting?

    def __getitem__(self, handle_id):
        return self._handles[handle_id].obj

    def new_handle(self, obj, on_close: Callable[[], None] | None = None):
        self._handle_counter += 1
        handle_id = self._handle_counter
        self._handles[handle_id] = SourceModHandle(handle_id, obj, on_close=on_close)
        return handle_id

    def close_handle(self, handle_id):
        handle = self._handles.pop(handle_id)
        handle.close()
