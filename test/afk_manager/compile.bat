SETLOCAL ENABLEEXTENSIONS
SET me=%~n0
SET parent=%~dp0

set scripting_dir=C:\Users\theY4Kman\Downloads\sourcemod-1.8.0-git5915-windows\addons\sourcemod\scripting
set spcomp=%scripting_dir%\spcomp.exe
set plugin_name=afk_manager4

%spcomp% %parent%\%plugin_name%.sp -o %parent%\%plugin_name%.smx _DEBUG=1
%spcomp% -a %parent%\%plugin_name%.sp -o %parent%\%plugin_name%.asm _DEBUG=1
