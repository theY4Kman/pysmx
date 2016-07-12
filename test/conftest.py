import os
import sys
REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, REPO_DIR)

import pytest


@pytest.fixture(scope='session')
def REPO_DIR():
    REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return REPO_DIR


@pytest.fixture(scope='session')
def TEST_DIR(REPO_DIR):
    return os.path.join(REPO_DIR, 'test')
