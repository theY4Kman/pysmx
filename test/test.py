if __name__ == '__main__':
    from smx import SourcePawnPlugin
    import sys

    with open('test.smx', 'rb') as fp:
        plugin = SourcePawnPlugin(fp)
        print plugin