@echo off
setlocal

rem Aufruf: c8205_interpreter.bat [Schalter ...] TESTDATEI [Schalter ...]
rem Beispiel: c8205_interpreter.bat --NO-TERMOUT Tests\x.txt --knotentest
rem           c8205_interpreter.bat Tests\x.txt --leser1 virtuelle_Geraete\Leser1
rem Die Testdatei darf an beliebiger Stelle stehen; Schalter mit eigenem
rem Wertargument (z. B. "--out DATEI") werden dabei erkannt, damit ihr Wert
rem nicht versehentlich als Testdatei gilt.
rem Hinweis: Werte mit "=" (z. B. --k0 datei=PFAD) in Anfuehrungszeichen setzen:
rem          --k0 "datei=band\k0"

set "file="
set "rest="
set "wert_folgt=0"

:schleife
if "%~1"=="" goto fertig
if "%wert_folgt%"=="1" goto wert
set "a=%~1"
if "%a:~0,1%"=="-" goto schalter

rem Kein Schalter: erste Testdatei bestimmt den Protokollnamen,
rem weitere Testdateien gehen an den Interpreter (er erlaubt mehrere).
if defined file goto weitere
set "file=%~1"
goto weiter

:weitere
set "rest=%rest% "%~1""
goto weiter

:schalter
set "rest=%rest% "%~1""
call :ist_wertschalter "%~1"
if not errorlevel 1 set "wert_folgt=1"
goto weiter

:wert
set "rest=%rest% "%~1""
set "wert_folgt=0"
goto weiter

:weiter
shift
goto schleife

:fertig
if not defined file (
    echo Test-Datei fehlt.
    exit /b 1
)

rem Dateiname ohne Pfad, Endung durch .log ersetzen
for %%f in ("%file%") do set "prot_file=%%~nf.log"

rem Vorgaben zuerst, dann die vom Benutzer uebergebenen Schalter; bei doppelter
rem Angabe (z. B. --out, --mdverz) gilt der spaeter genannte, also der vom Benutzer.
python c8205_interp.py --mdverz .\markdown-dateien --out "Test-Protokolle\%prot_file%" "%file%" %rest%

endlocal & exit /b %ERRORLEVEL%

rem Schalter des Interpreters, die ein eigenes Wertargument mitnehmen
rem (Liste wie in c8205_interpreter.sh). Rueckgabe 0 = Wertschalter, 1 = nicht.
:ist_wertschalter
for %%s in (--mdverz --leser1 --lochbandleser1 --leser2 --lochbandleser2 --stanzer1 --lochbandstanzer1 --sw-ausgabe --k0 --out --pruefe-stanzer1 --pruefe-sw-ausgabe) do (
    if "%~1"=="%%s" exit /b 0
)
exit /b 1
