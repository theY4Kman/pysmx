from pytest_lambda import lambda_fixture, static_fixture


def test_function_calling(compile_plugin):
    # language=SourcePawn
    plugin = compile_plugin(r"""
        public OnPluginStart() {
            for (new i; i<5; i++) {
                func();
            }
            PrintToServer("end");
        }

        func() {
            PrintToServer("func\n");
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


def test_function_calling_with_args(compile_plugin):
    # language=SourcePawn
    plugin = compile_plugin('''
        String:Snakes(const char[] msg) {
            char buffer[512];
            int n = strcopy(buffer, sizeof(buffer), "hiss: ");
            strcopy(buffer[n], sizeof(buffer)-n, msg);
            return buffer;
        }
        public DontOptimizeOutSnakes() {
            Snakes("");
        }
    ''')

    func = plugin.runtime.get_function_by_name('Snakes')

    expected = 'hiss: hello world'
    actual = func('hello world')
    assert expected == actual


class TestInterpreter:
    source = static_fixture(
        # language=SourcePawn
        """
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
        """,
        scope='class',
    )
    plugin = lambda_fixture(
        lambda source, compile_plugin: compile_plugin(source, include_myinfo=False)
    )

    def test_global_return(self, plugin):
        expected = 1337
        actual = plugin.runtime.call_function_by_name('ReturnGlobal')
        assert expected == actual

    def test_constant_return(self, plugin):
        expected = 23
        actual = plugin.runtime.call_function_by_name('ReturnTwentyThreeInner')
        assert expected == actual

    def test_inner_function_return(self, plugin):
        expected = 23
        actual = plugin.runtime.call_function_by_name('ReturnTwentyThree')
        assert expected == actual
