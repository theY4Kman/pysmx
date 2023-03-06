# TODO(zk): test with other plugin handles

def test_GetPluginFilename(compile_plugin):
    # language=SourcePawn
    source = '''
        public void OnPluginStart() {
            char buffer[PLATFORM_MAX_PATH];
            GetPluginFilename(INVALID_HANDLE, buffer, sizeof(buffer));
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
