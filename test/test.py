import pytest

import smx.compiler


@pytest.fixture(scope='session')
def compile():
    def compile(code, **options):
        # TODO: auto-insert #include <sourcemod> and default Plugin:myinfo
        plugin = smx.compiler.compile(code)
        plugin.runtime.amx.print_verification = False
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


# @pytest.mark.xfail(reason='rvals from inner calls currently unsupported')
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
    """)

    # This works
    assert plugin.runtime.call_function_by_name('ReturnTwentyThreeInner') == 23

    # But this doesn't
    # assert plugin.runtime.call_function_by_name('ReturnTwentyThree') == 23
