from ctypes import *

__all__ = ['SourceModNatives']

class SourceModNatives(object):
    def __init__(self, amx):
        """
        @type   amx: smx.smxexec.SourcePawnAbstractMachine
        @param  amx: The abstract machine owning these natives
        """
        self.amx = amx
        self.plugin = self.amx.plugin

    def __local_to_string(self, offset):
        return self.plugin._get_data_string(offset)

    def PrintToServer(self, params):
        fmt = self.__local_to_string(params[1])
        print fmt
