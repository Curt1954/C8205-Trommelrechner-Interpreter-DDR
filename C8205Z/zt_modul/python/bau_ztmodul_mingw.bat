@echo off
rem Baut c8205_ztmodul.pyd mit MinGW-w64 ohne setuptools.
rem Ablage: C8205Z\zt_modul\python\   Aufruf dort:  bau_ztmodul_mingw.bat
rem plattform.h und c8205_api.h kommen aus c-module\ (Vorgabe ..\..\..\c-module, ueberschreibbar mit  set SIM=...)
setlocal
cd /d "%~dp0"

if not defined SIM set "SIM=..\..\..\c-module"
where gcc >nul 2>&1 || (echo FEHLER: gcc nicht gefunden. & exit /b 1)
for /f "delims=" %%i in ('python -c "import sysconfig;print(sysconfig.get_paths()['include'])"') do set "PYINC=%%i"
for /f "delims=" %%i in ('python -c "import sys;print(sys.base_prefix)"') do set "PYBASE=%%i"
if not exist "%PYBASE%\libs\python3.lib" (echo FEHLER: %PYBASE%\libs\python3.lib fehlt. & exit /b 1)

gcc -static -shared -O2 -std=gnu11 -DPy_LIMITED_API=0x03080000 -DZT_OHNE_TROMMEL=1 -static-libgcc ^
    -I"%PYINC%" -I.. -I"%SIM%" ^
    -o c8205_ztmodul.pyd ^
    c8205_ztmodul.c ..\zt_modul.c ^
    -L"%PYBASE%\libs" -l:python3.lib -lwinmm
if errorlevel 1 (echo FEHLER beim Bauen. & exit /b 1)
echo OK: c8205_ztmodul.pyd
endlocal
