import os

import pytest

from smx import SourcePawnPlugin
from smx.interpreter import Interpreter


@pytest.fixture(scope='session')
def path_to_test_smx(TEST_DIR):
    return os.path.join(TEST_DIR, 'test.smx')


@pytest.yield_fixture
def test_smx_file(path_to_test_smx):
    with open(path_to_test_smx, 'rb') as fp:
        yield fp


@pytest.mark.skipif(True, reason='Abandoned interpret.cpp port for now')
def test_interpreter(test_smx_file):
    plugin = SourcePawnPlugin(test_smx_file)
    interpreter = Interpreter(plugin)
    assert interpreter.call_function_by_name('OnPluginStart') == 1337


def test_original_interpreter(test_smx_file):
    plugin = SourcePawnPlugin(test_smx_file)
    assert plugin.runtime.call_function_by_name('ReturnTwentyThree') == 23



def legacy_test():
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
