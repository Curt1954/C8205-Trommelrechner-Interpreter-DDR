@echo off
rem r300_eingabe_grafik.bat - Windows-Pendant zu r300_eingabe_grafik.sh (ohne Faktor). Aus dem Projektordner starten.
cd /d "%~dp0.."
copy /Y Trommel\trommel_r300_eingabe.txt r300_eingabe_trommel_nach_lauf.txt >nul
py c8205_grafik.py --STUMM --netz-schnell --HWCHECK --BASP 000000 --trommel r300_eingabe_trommel_nach_lauf.txt --WIEDERGABE Tests\r300_eingabe_klickspur.txt --DEBUGLOG r300_eingabe_debug.log
echo Rueckgabewert %errorlevel%  -  Debug-Log: r300_eingabe_debug.log
