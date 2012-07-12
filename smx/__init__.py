#!/bin/env python
from smxreader import SourcePawnPlugin

if __name__ == '__main__':
    import sys
    plugin = SourcePawnPlugin(open(' '.join(sys.argv[1:]), 'rb'))
    print plugin
