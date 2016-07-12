import pytest

from smx.compiler import compile


# @pytest.mark.xfail(reason='rvals from inner calls currently unsupported')
def test_interpreter():
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
