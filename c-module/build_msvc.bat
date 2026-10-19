@echo off
rem Visual Studio (x64 Native Tools Prompt). NICHT getestet.
rem Baut trommel.dll (fuer Python/ctypes) und testframe_koinzidenz.exe
cl /nologo /O2 /W3 /DC8205_BUILD_DLL /LD trommel.c bahnsperre.c unterbrechung.c /Fe:trommel.dll winmm.lib
if errorlevel 1 exit /b 1
cl /nologo /O2 /W3 testframe_koinzidenz.c trommel.c bahnsperre.c unterbrechung.c /Fe:testframe_koinzidenz.exe winmm.lib
if errorlevel 1 exit /b 1
testframe_koinzidenz.exe
