@echo off
setlocal

rem c8205_grafik.bat - Startscript fuer den Modus GRAFIK unter Windows (Pult-Fenster, SW-Fenster, Toene).
rem Aufruf (aus jedem Ordner):  c8205_grafik.bat [Schalter ...]
rem
rem Alle Schalter gehen unveraendert an c8205_grafik.py; Hilfe: c8205_grafik.bat -h
rem Rueckgabewert = der von c8205_grafik.py (0 = normal, 8 = Abbruch mit Strg+C, 16 = Start nicht moeglich).
rem Gleichwertig ist: python c8205_interp.py [Schalter ...]   (ohne --MODUS startet GRAFIK).
rem
rem ACHTUNG: Die Trommeldatei (Trommel\trommel.txt) ist der Speicher des Rechners. Programme veraendern sie.
rem          Wer die Ausgangsbelegung behalten will, sichert die Datei vorher oder startet mit  --trommel EIGENE_KOPIE.txt
rem
rem Windows: Teilabnahme am 26.10.2026 (Start, Trommel-Modul, Grundgeraeusch, Lochbandleser und Stanzer gehoert); Rest offen,
rem          siehe GRAFIK_Beschreibung 9.2 und GRAFIK_Pruefverfahren 9.
rem Toene: Mit Mischer (winmm) laeuft derselbe Aufbau wie unter Linux; Startzeile "Toene unter Windows ueber den Mischer (winmm)".
rem        Laesst sich winmm nicht oeffnen, gilt der Rueckfall winsound mit Hinweis und Zeile "Grund: ...".

cd /d "%~dp0" || exit /b 16

set "PYTHONWARNINGS=ignore::ResourceWarning"
set "PYTHONDONTWRITEBYTECODE=1"

where python >nul 2>&1
if errorlevel 1 (
    echo FEHLER: python nicht gefunden. 1>&2
    exit /b 16
)

dir /b "c-module\python\c8205_trommel*.pyd" >nul 2>&1
if errorlevel 1 (
    echo FEHLER: das C-Modul c8205_trommel ^(echte Trommel^) fehlt in c-module\python\. 1>&2
    echo   Bauen:  cd c-module\python ^&^& bau_trommel_mingw.bat   ^(braucht 64-Bit-MinGW-w64 und 64-Bit-Python im PATH^) 1>&2
    exit /b 16
)

python c8205_grafik.py %*

endlocal & exit /b %ERRORLEVEL%
