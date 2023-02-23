import pytest


def test_convar_int(compile_plugin):
    # language=SourcePawn
    plugin = compile_plugin('''
        new Handle:g_cvar = INVALID_HANDLE;
        public TestCreateConVar() {
            g_cvar = CreateConVar("pysmx_num", "350", "description");
        }
        public TestGetConVarInt() {
            return GetConVarInt(g_cvar);
        }
    ''')

    plugin.runtime.call_function_by_name('TestCreateConVar')
    value = plugin.runtime.call_function_by_name('TestGetConVarInt')
    assert value == 350


def test_convar_float(compile_plugin):
    # language=SourcePawn
    plugin = compile_plugin('''
        new Handle:g_cvar = INVALID_HANDLE;
        public TestCreateConVar() {
            g_cvar = CreateConVar("pysmx_num", "3.14", "description");
        }
        public float TestGetConVarFloat() {
            return GetConVarFloat(g_cvar);
        }
    ''')

    plugin.runtime.call_function_by_name('TestCreateConVar')
    value = plugin.runtime.call_function_by_name('TestGetConVarFloat')
    assert value == pytest.approx(3.14)


def test_convar_string(compile_plugin):
    # language=SourcePawn
    plugin = compile_plugin('''
        new Handle:g_cvar = INVALID_HANDLE;
        public TestCreateConVar() {
            g_cvar = CreateConVar("pysmx_num", "Unique", "description");
        }
        String:TestGetConVar() {
            new String:buffer[12];
            GetConVarString(g_cvar, buffer, sizeof(buffer));
            return buffer;
        }
        public DontOptimizeOutTestGetConVar() {
            TestGetConVar();
        }
    ''')

    plugin.runtime.call_function_by_name('TestCreateConVar')
    value = plugin.runtime.call_function_by_name('TestGetConVar')
    assert value == 'Unique'
