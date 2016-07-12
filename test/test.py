import os

import pytest

from smx import SourcePawnPlugin


@pytest.fixture(scope='session')
def path_to_test_smx(TEST_DIR):
    return os.path.join(TEST_DIR, 'test.smx')


@pytest.yield_fixture
def test_smx_file(path_to_test_smx):
    with open(path_to_test_smx, 'rb') as fp:
        yield fp


# @pytest.mark.xfail(reason='rvals from inner calls currently unsupported')
def test_interpreter(test_smx_file):
    plugin = SourcePawnPlugin(test_smx_file)

    # This works
    assert plugin.runtime.call_function_by_name('ReturnTwentyThreeInner') == 23

    # But this doesn't
    assert plugin.runtime.call_function_by_name('ReturnTwentyThree') == 23
