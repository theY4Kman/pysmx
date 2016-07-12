import os

import pytest

from smx import SourcePawnPlugin


@pytest.fixture(scope='session')
def path_to_smx(TEST_DIR):
    return os.path.join(TEST_DIR, 'afk_manager', 'afk_manager4.smx')


@pytest.fixture(scope='session')
def path_to_asm(TEST_DIR):
    return os.path.join(TEST_DIR, 'afk_manager', 'afk_manager4.asm')


@pytest.yield_fixture
def smx_file(path_to_smx):
    with open(path_to_smx, 'rb') as fp:
        yield fp


@pytest.yield_fixture
def asm_file(path_to_asm):
    with open(path_to_asm, 'r') as fp:
        yield fp


#XXX############################################################################################### don't commit me!
# @pytest.mark.test
#XXX############################################################################################### don't commit me!
def test_interpreter(smx_file, asm_file):
    plugin = SourcePawnPlugin(smx_file)
    plugin.runtime.amx._verify_asm(asm_file.read())
    assert plugin.runtime.call_function_by_name('ActionToString', 1) == 'Plugin_Continue'
    assert plugin.runtime.call_function_by_name('ReturnTwentyThree') == 23
