# TODO(zk): test with other plugin handles
import pytest
from pytest_lambda import lambda_fixture

from smx.sourcemod.natives.sourcemod import PlInfo


class TestPluginInfo:
    handle_type = lambda_fixture(params=[
        pytest.param('my_handle', id='GetMyHandle()'),
        pytest.param('invalid_handle', id='INVALID_HANDLE'),
    ])

    @pytest.fixture
    def get_handle_source(self, handle_type):
        if handle_type == 'my_handle':
            # language=SourcePawn
            return '''
                Handle get_handle() {
                    return GetMyHandle();
                }
            '''
        elif handle_type == 'invalid_handle':
            # language=SourcePawn
            return '''
                Handle get_handle() {
                    return INVALID_HANDLE;
                }
            '''
        else:
            raise ValueError(f'Unknown handle type {handle_type!r}')

    @pytest.fixture
    def compile_plugin(self, compile_plugin, get_handle_source):
        def compile_with_get_handle(source: str, *args, **kwargs):
            return compile_plugin(source + get_handle_source, *args, **kwargs)
        return compile_with_get_handle

    def test_GetPluginFilename(self, compile_plugin):
        # language=SourcePawn
        source = '''
            public void OnPluginStart() {
                char buffer[PLATFORM_MAX_PATH];
                GetPluginFilename(get_handle(), buffer, sizeof(buffer));
                PrintToServer("%s", buffer);
            }
        '''

        base_name = 'expected'
        source_name = f'{base_name}.sp'
        plugin = compile_plugin(source, filename=source_name)

        plugin.run()

        expected = f'{base_name}.smx'
        actual = plugin.runtime.get_console_output()
        assert expected == actual

    @pytest.mark.parametrize('info_type', [
        pytest.param(info_type, id=name)
        for name, info_type in PlInfo.__members__.items()
    ])
    def test_GetPluginInfo(self, compile_plugin, info_type):
        # language=SourcePawn
        source = '''
            public void OnPluginStart() {
                char buffer[255];
                GetPluginInfo(get_handle(), PlInfo_%s, buffer, sizeof(buffer));
                PrintToServer(buffer);
            }
        ''' % info_type.name
        plugin = compile_plugin(source)

        plugin.run()

        expected = plugin.myinfo[info_type.name.lower()]
        actual = plugin.runtime.get_console_output()
        assert expected == actual
