import sys
sys.path.append('..')

if __name__ == '__main__':
    import os.path
    import sys
    from smx import SourcePawnPlugin

    if len(sys.argv[1:]) > 0:
        path = ' '.join(sys.argv[1:])
    else:
        path = 'test.smx'

    with open(path, 'rb') as fp:
        plugin = SourcePawnPlugin(fp)
        print 'Loaded %s...' % plugin

        if os.path.exists('test.asm'):
            with open('test.asm', 'rb') as asm_fp:
                plugin.runtime.amx._verify_asm(asm_fp.read())

    plugin.run()