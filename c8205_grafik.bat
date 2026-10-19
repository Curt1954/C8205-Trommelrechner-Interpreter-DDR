@echo off
setlocal

rem c8205_grafik.bat - Startscript fuer den Modus GRAFIK unter Windows (Pult-Fenster, SW-Fenster, Toene).
rem Aufruf (aus jedem Ordner):  c8205_grafik.bat [Schalter ...]
rem
rem Alle Schalter gehen unveraendert an c8205_grafik.py; Hilfe: c8205_grafik.bat -h
rem Rueckgabewert = der von c8205_grafik.py (0 = normal, 8 = Abbruch mit Strg+C, 16 = Start nicht moeglich).
rem Gleichwertig ist: python c8205_interp.py [Schalter ...]   (ohne --MODUS startet GRAFIK).
rem
rem ACHTUNG: Die Trommeldatei (virtuelle_Geraete\Trommel\trommel.txt) ist der Speicher des Rechners. Programme veraendern sie.
rem          Wer die Ausgangsbelegung behalten will, sichert die Datei vorher oder startet mit  --trommel EIGENE_KOPIE.txt
rem
rem NICHT GETESTET unter Windows (nach c8205_grafik.sh und c8205_interpreter.bat gebaut, Stand 19.10.2026).
rem Toene: Der Mischer ueber winmm ist unter Windows noch nicht getestet (Hinweis beim Start); Rechnertoene laufen ueber winsound.

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
    echo   Bauen:  cd c-module\python ^&^& python setup.py build_ext --inplace   ^(braucht Visual Studio Build Tools oder MinGW-w64^) 1>&2
    exit /b 16
)

python c8205_grafik.py %*

endlocal & exit /b %ERRORLEVEL%
