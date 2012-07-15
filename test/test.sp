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
    PrintToServer("Test!");
}
