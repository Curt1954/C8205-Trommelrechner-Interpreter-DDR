@echo off
rem r300_eingabe_lauf_und_auswertung.bat - Windows-Pendant: echter Tk-Lauf von r300_eingabe und Auswertung. Aus dem Projektordner oder per Doppelklick.
rem Fenster waehrend des Laufs (ca. 50 s) NICHT anfassen. Ergebnis: r300_eingabe_debug.log, r300_eingabe_trommel_nach_lauf.txt, r300_eingabe_bericht.txt
cd /d "%~dp0.."
py -c "import tkinter" 2>nul || (echo Kein Tkinter: dieser Lauf braucht ein echtes Fenster. & exit /b 2)
del /Q r300_eingabe_debug.log 2>nul
call testscripte\r300_eingabe_grafik.bat
if not exist r300_eingabe_debug.log (echo Kein Debug-Log entstanden. & exit /b 2)
py testscripte\r300_eingabe_log_auswerten.py r300_eingabe_debug.log r300_eingabe_trommel_nach_lauf.txt r300_eingabe_bericht.txt
echo Auswertung: Rueckgabewert %errorlevel%  -  Bericht: r300_eingabe_bericht.txt
exit /b %errorlevel%
