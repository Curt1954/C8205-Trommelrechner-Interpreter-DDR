@echo off
rem Baut c8205_trommel.pyd mit MinGW-w64 ohne setuptools.
rem Ablage: c-module\python\   Aufruf dort:  bau_trommel_mingw.bat
setlocal
cd /d "%~dp0"

set PATH=C:\msys64-mkl\ucrt64\bin;%PATH%

where gcc >nul 2>&1 || (echo FEHLER: gcc nicht gefunden. & exit /b 1)
for /f "delims=" %%i in ('python -c "import sysconfig;print(sysconfig.get_paths()['include'])"') do set "PYINC=%%i"
for /f "delims=" %%i in ('python -c "import sys;print(sys.base_prefix)"') do set "PYBASE=%%i"
if not exist "%PYBASE%\libs\python3.lib" (echo FEHLER: %PYBASE%\libs\python3.lib fehlt. & exit /b 1)

gcc -static -shared -O2 -std=gnu11 -DPy_LIMITED_API=0x03080000 -D_WIN32_WINNT=0x0601 -DWINVER=0x0601 -static-libgcc ^
    -I"%PYINC%" -I.. ^
    -o c8205_trommel.pyd ^
    c8205_trommel_modul.c ..\trommel.c ..\bahnsperre.c ..\unterbrechung.c ..\tonmisch.c ^
    -L"%PYBASE%\libs" -l:python3.lib -lwinmm
if errorlevel 1 (echo FEHLER beim Bauen. & exit /b 1)
echo OK: c8205_trommel.pyd
endlocal
