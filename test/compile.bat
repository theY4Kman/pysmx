SETLOCAL ENABLEEXTENSIONS
SET me=%~n0
SET parent=%~dp0

set scripting_dir=C:\Users\theY4Kman\Downloads\sourcemod-1.8.0-git5915-windows\addons\sourcemod\scripting
set spcomp=%scripting_dir%\spcomp.exe

%spcomp% %parent%\test.sp -o %parent%\test.smx
%spcomp% -a %parent%\test.sp -o %parent%\test.asm
