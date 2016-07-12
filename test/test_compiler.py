from smx.compiler import compile


def test_compiler():
    plugin = compile('''
        #include <sourcemod>

        public Plugin:myinfo = {
            name = "pysmx compiler test",
            author = "theY4Kman",
            description = "",
            version = "0",
            url = "https://github.com/theY4Kman/pysmx/"
        };

        public OnPluginStart() {}
        public ReturnTwelve() { return 12; }
    ''')

    assert plugin.name == 'pysmx compiler test'
    assert plugin.runtime.call_function_by_name('ReturnTwelve') == 12
