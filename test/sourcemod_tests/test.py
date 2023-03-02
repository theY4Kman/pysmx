import os
from pathlib import Path
from typing import List

import pytest
from pytest_lambda import lambda_fixture

import smx
import smx.plugin
from smx.exceptions import SourcePawnRuntimeError
from smx.sourcemod.natives import SourceModTestNatives
from .runtests import TestPlan as SMTestPlan, TestRunner as SMTestRunner

sourcemod_tests_dir = Path(__file__).parent


class RuntestsArgs:
    test = str(sourcemod_tests_dir)
    runtime_only = True
    coverage = False


plan = SMTestPlan(RuntestsArgs)
plan.find_tests()
for sm_test in plan.tests:
    sm_test.prepare()

runner = lambda_fixture(lambda: SMTestRunner(plan), scope='session')

core_include_dir = lambda_fixture(lambda repo_dir: repo_dir / 'smx/include', scope='session')


@pytest.mark.parametrize(
    'test',
    [t for t in plan.tests if t.type not in ('compiler-output', 'compile-only')],
    ids=lambda test: str(Path(test.path).relative_to(sourcemod_tests_dir)),
)
def test_sm_test(test, runner):
    if test.path.endswith('.sp'):
        source_dir = os.path.dirname(test.path)
        include_dirs = [sourcemod_tests_dir, source_dir]
        include_dirs += test.includes

        with open(test.path, 'r', encoding='utf-8') as fp:
            plugin = smx.compile_plugin(
                fp.read(),
                filename=os.path.basename(test.path),
                include_dir=include_dirs,
                extra_args=(
                    # Fast compilation in tests
                    '-z', '1',
                    # Disable default includes ("prefix" file — appears to be sourcemod.inc)
                    '-p', os.devnull,
                ),
            )
    else:
        with open(test.path, 'rb') as fp:
            plugin = smx.plugin.SourcePawnPlugin(fp)

    plugin.runtime.spew = True
    plugin.runtime.spew_stack = True

    # Ensure we load our testing <shell> natives
    plugin.runtime.smsys_options['natives_cls'] = SourceModTestNatives

    if not plugin.runtime.get_function_by_name('main'):
        return

    try:
        plugin.runtime.run(main='main')
    except SourcePawnRuntimeError as e:
        error_stdout = e.debug_output()
        stderr = e.stderr()
    else:
        error_stdout = ''
        stderr = ''

    stdout = plugin.runtime.get_console_output() + error_stdout

    if test.stdout_file:
        compare_output(test.get_expected_output('stdout'), stdout)
    if test.stderr_file:
        compare_output(test.get_expected_output('stderr'), stderr)


def compare_output(expected_lines: List[str], actual: str):
    actual_lines = actual.replace('\r\n', '\n').split('\n')

    # Normalize line endings to LF, but omit newline on last line
    actual_lines = [f'{line}\n' for line in actual_lines]
    actual_lines[-1] = actual_lines[-1].rstrip('\n')

    # Remove last line from stdout if it's empty and expected is one line short
    if len(actual_lines) - 1 == len(expected_lines) and not actual_lines[-1]:
        actual_lines.pop()

    expected = ''.join(expected_lines)
    actual = ''.join(actual_lines)
    assert expected == actual
