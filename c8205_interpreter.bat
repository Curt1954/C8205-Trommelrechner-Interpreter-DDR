@echo off
setlocal

set "file=%~1"

if "%file%"=="" (
    echo Test-Datei fehlt.
    exit /b 1
)

rem Dateiname ohne Pfad und ohne Endung, .log anhaengen
set "prot_file=%~n1.log"

python c8205_interp.py --out "Protokolle\%prot_file%" "%file%"

endlocal
