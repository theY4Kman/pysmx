#!/bin/env python
from smxreader import SourcePawnPlugin
import smxreader
import smxexec
import opcodes
import smxdefs

if __name__ == '__main__':
    import sys
    plugin = SourcePawnPlugin(open(' '.join(sys.argv[1:]), 'rb'))
    print plugin
