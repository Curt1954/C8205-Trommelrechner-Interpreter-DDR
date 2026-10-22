@echo off
rem Version 1.00-030
rem c82ass.bat - Windows-Pendant zum Linux-Skript "c82ass"
rem Erzeugt den C8205-Assembler fuer Windows 10 mit dem MinGW-w64-Compiler.
rem Voraussetzung: gcc.exe (MinGW-w64) muss im PATH liegen, z.B. ueber
rem                MSYS2 ("pacman -S mingw-w64-x86_64-gcc") oder eine
rem                eigenstaendige MinGW-w64-Installation.
rem Aufruf: In diesem Verzeichnis (Assembler\) per Doppelklick oder
rem         "c82ass.bat" in der Eingabeaufforderung starten.
rem Siehe C8205_Assembler_Dokumentation.md, Abschnitt 1.1 (Verzeichnisstruktur).

if not exist _Windows mkdir _Windows

gcc -O2 -Wall -Wextra -Wshadow --static -o .\_Windows\c82ass.exe .\Sourcecode\ca82_protokoll.c .\Sourcecode\ca82_standards.c .\Sourcecode\ca82_symbole.c .\Sourcecode\ca82_berichte.c .\Sourcecode\ca82_makros.c .\Sourcecode\ca82_zustand.c .\Sourcecode\ca82_hilfen.c .\Sourcecode\ca82_fehler.c .\Sourcecode\ca82_quelle.c .\Sourcecode\ca82_listing.c .\Sourcecode\ca82_pass0.c .\Sourcecode\ca82_pass1.c .\Sourcecode\ca82_pass2.c .\Sourcecode\ca82_ausdruck.c .\Sourcecode\ca82_codierung.c .\Sourcecode\ca82_pass3.c .\Sourcecode\ca82_fluss.c .\Sourcecode\ca82_testdatei.c .\Sourcecode\ca82_main.c

if errorlevel 1 (
    echo.
    echo *** Fehler beim Uebersetzen. ***
    exit /b 1
)

echo.
echo Erzeugt: _Windows\c82ass.exe
