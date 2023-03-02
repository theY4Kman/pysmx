from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from pytest_lambda import lambda_fixture

import smx

pytest_plugins = [
    # Load our icdiff-based pretty diffs plugin
    'test.plugins.pretty_diffs',
]

test_dir = lambda_fixture(lambda: Path(__file__).parent.resolve(), scope='session')
repo_dir = lambda_fixture(lambda test_dir: test_dir.parent, scope='session')

plugin_root_path = lambda_fixture(lambda test_dir: test_dir / 'game_root/addons/sourcemod', scope='session')


myinfo = lambda_fixture(lambda request: {
    'name': request.node.name,
    'author': 'Test Author',
    'description': request.node.nodeid,
    'version': '1.0.0',
    'url': 'https://github.com/they4kman/pysmx',
})


@pytest.fixture
def myinfo_sp(myinfo) -> str:
    entries = [
        f'{key} = "{value}"'
        for key, value in myinfo.items()
    ]
    body = textwrap.indent(',\n'.join(entries), '  ')
    defn = f'public Plugin:myinfo = {{\n{body}\n}};'
    return defn


@pytest.fixture
def compile_plugin(myinfo_sp, plugin_root_path):
    def compile_plugin(
        source,
        *,
        include_myinfo: bool = True,
        root_path: str | Path = plugin_root_path,
        spew: bool = True,
        spew_stack: bool = True,
        **options
    ):
        if include_myinfo:
            source = f'{myinfo_sp}\n\n{source}'
        return smx.compile_plugin(source, root_path=root_path, spew=spew, spew_stack=spew_stack, **options)

    return compile_plugin

