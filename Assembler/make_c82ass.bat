@echo off
rem c82ass.bat - Windows-Pendant zum Linux-Skript "c82ass"
rem Erzeugt den C8205-Assembler fuer Windows 10 mit dem MinGW-w64-Compiler.
rem Voraussetzung: gcc.exe (MinGW-w64) muss im PATH liegen, z.B. ueber
rem                MSYS2 ("pacman -S mingw-w64-x86_64-gcc") oder eine
rem                eigenstaendige MinGW-w64-Installation.
rem Aufruf: In diesem Verzeichnis (Assembler\) per Doppelklick oder
rem         "c82ass.bat" in der Eingabeaufforderung starten.
rem Siehe C8205_Assembler_Dokumentation.md, Abschnitt 1.1 (Verzeichnisstruktur).

if not exist _Windows mkdir _Windows

rem gcc -Wall -Wunused-function -o .\_Windows\c82ass.exe .\Sourcecode\ca82_protokoll.c .\Sourcecode\ca82_standards.c .\Sourcecode\ca82ass.c
gcc --static -o .\_Windows\c82ass.exe .\Sourcecode\ca82_protokoll.c .\Sourcecode\ca82_standards.c .\Sourcecode\ca82ass.c

if errorlevel 1 (
    echo.
    echo *** Fehler beim Uebersetzen. ***
    exit /b 1
)

echo.
echo Erzeugt: _Windows\c82ass.exe
