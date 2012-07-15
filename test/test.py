if __name__ == '__main__':
    from smx import SourcePawnPlugin

    with open('test.smx', 'rb') as fp:
        plugin = SourcePawnPlugin(fp)
        print 'Loaded %s...' % plugin
        plugin.run()