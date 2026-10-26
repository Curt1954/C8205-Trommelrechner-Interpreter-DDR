@echo off
rem Startet den C8205-Assembler (aus dem Verzeichnis Assembler aufrufen).
rem Akzeptiert zusaetzlich --WARN=SYM und reicht es als -WARN=SYM durch.
setlocal EnableDelayedExpansion
set PATH=C:\msys64-mkl\ucrt64\bin;%PATH%
set "ARGS="
:loop
if "%~1"=="" goto run
set "A=%~1"
if /I "!A:~0,7!"=="--WARN=" set "A=!A:~1!"
set ARGS=!ARGS! "!A!"
shift
goto loop
:run
"%~dp0_Windows\c82ass.exe" !ARGS!
endlocal