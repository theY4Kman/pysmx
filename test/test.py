import textwrap

import pytest

import smx.compiler


@pytest.fixture
def myinfo(request):
    return {
        'name': request.node.name,
        'author': 'Test Author',
        'description': request.node.nodeid,
        'version': '1.0.0',
        'url': 'https://github.com/they4kman/pysmx',
    }


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
def compile(myinfo_sp):
    def compile(source, *, include_myinfo: bool = True, **options):
        if include_myinfo:
            source = f'{myinfo_sp}\n\n{source}'
        plugin = smx.compiler.compile(source, **options)
        return plugin
    return compile


@pytest.mark.parametrize('value', [True, False])
def test_bool_literal_return(value, compile):
    plugin = compile('''
        public bool:Test() {
            return %s;
        }
    ''' % ('true' if value else 'false'))
    rval = plugin.runtime.call_function_by_name('Test')
    assert rval is value


@pytest.mark.parametrize('integer', [
    0,
    1,
    2147483647,
    -2147483648,
])
def test_integer_literal_return(integer, compile):
    plugin = compile('''
        public Test() {
            return %d;
        }
    ''' % integer)
    assert plugin.runtime.call_function_by_name('Test') == integer


def test_float_literal_return(compile):
    plugin = compile('''
        public Float:Test() {
            return 12.0;
        }
    ''')
    rval = plugin.runtime.call_function_by_name('Test')
    assert rval == 12.0
    assert isinstance(rval, float)


def test_string_return(compile):
    plugin = compile('''
        String:Test() {
            new String:s[] = "hiss";
            return s;
        }
        public DontOptimizeOutTest() {
            Test();
        }
    ''')
    rval = plugin.runtime.call_function_by_name('Test')
    assert rval == 'hiss'


def test_function_calling(compile):
    plugin = compile("""
        public OnPluginStart()
        {
            for (new i; i<5; i++)
                func();
            PrintToServer("end");
        }

        func()
        {
            PrintToServer("func");
        }
    """)

    plugin.run()
    assert plugin.runtime.get_console_output() == '''
        func
        func
        func
        func
        func
        end
    '''.strip().replace(' ', '')


def test_interpreter(compile):
    plugin = compile("""
        #include <sourcemod>

        public Plugin:myinfo = {
            name = "PySMX Test",
            author = "theY4Kman",
            description = "Test plug-in for the PySMX VM",
            version = "0.0",
            url = "https://github.com/theY4Kman/pysmx/"
        };

        public OnPluginStart()
        {
            new percent = 100;
            for (new i=0; i<10; i++)
                percent += i;

            PrintToServer("%s function%c work %d%% (+/- %.3f) of the time! No longer 0x%x -- now we're 0x%X!", "Format", 's', percent, 5.3, 0xdeadbeef, 0xcafed00d);
            Test();

            CreateTimer(1.0, Timer_Callback, 5);
        }

        Test()
        {
            PrintToServer("Called Test()");
        }

        public Action:Timer_Callback(Handle:timer, any:data)
        {
            PrintToServer("Timer fired with: %d", data);
        }

        new i_GlobalValue = 1337;
        public ReturnGlobal() {
            return i_GlobalValue;
        }

        public ReturnTwentyThree() {
            return ReturnTwentyThreeInner();
        }

        ReturnTwentyThreeInner() {
            return 23;
        }
    """, include_myinfo=False)

    assert plugin.runtime.call_function_by_name('ReturnTwentyThree') == 23
    assert plugin.runtime.call_function_by_name('ReturnTwentyThreeInner') == 23


def test_convar_int(compile):
    plugin = compile('''
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


def test_convar_string(compile):
    plugin = compile('''
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
