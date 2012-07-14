from .smxdefs import *
from .opcodes import *

class SourcePawnPluginRuntime(object):
    """Executes SourcePawn plug-ins"""

    def __init__(self, plugin):
        self.plugin = plugin

    def run(self, main='OnPluginStart'):
        """Executes the plugin's main function"""
