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
    PrintToServer("%s function%c work %d%% (+/- %.3f) of the time! No longer 0x%x -- now we're 0x%X!", "Format", 's', 100, 5.3, 0xdeadbeef, 0xcafed00d);
    Test();
}

Test()
{
    PrintToServer("Called Test()");
}