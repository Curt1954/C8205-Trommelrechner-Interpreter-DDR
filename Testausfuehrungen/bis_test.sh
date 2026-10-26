#!/bin/bash
# bis_test.sh - Druckprogramm auf dem BIS (Minimalprogramm v6) vorbereiten und GRAFIK starten
# Aufruf (von ueberall): bash Testausfuehrungen/bis_test.sh
#
# Ablauf: 1. Trommel leeren   2. KEP, BIS (v6) und Druckprogramm assemblieren
#         3. Nur das KEP mit dem TEST-Interpreter (--LOADONLY) auf die Trommel laden   4. GRAFIK starten
# Das BIS kommt ueber das KEP und Kanal K2 auf die Trommel, das Druckprogramm ueber das BIS und K1.
# Das Druckprogramm (.obj, binaerer Objektstreifen) liegt in Leser1, das BIS als KEP-Lochstreifen (.kep) in Leser2;
# beide Baender werden am Fenster eingelesen.
# Quelltext-Angang: Druckprogramm ohne Pragma LEITADRESSE (relativ, Hauptleitadresse 21 3000 bei der Eingabe);
#                   BIS-.kep mit --ABSPR (Pragma LEITADRESSE 00 im v6-Quelltext).
# Alle Lademethoden und ihr Angang am Quelltext: markdown-dateien/C8205-Interpreter-Durchführung_eines_Tests.md, Abschnitt 2k.

cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." || exit 2    # Projektstamm: eine Ebene ueber Testausfuehrungen/
clear                                                   # Bildschirm leeren
echo Laden des KEP mit TEST-Interpreter                 # Ansagen zum Ablauf
echo Laden des BIs mit dem KEP
echo Assemblieren des Druckprogrammes als BIS-Objektcode-Lochstreifen
echo Laden des Druckprogrammes mit Hilfe des BIS
echo Test mit dem GRAFIK-Interpreter
echo

# Trommel leeren: alle Zellen 00000000000 (die Testdateien unten laden mit KEEP, leeren also nicht selbst)
python3 ./testscripte/erzeuge_leere_trommel.py

bn="bsp_5_18_kep"                                       # Name des Kleinen Eingabeprogramms KEP (Anleitung 5.18)
bn2="pj2-bis_minimalprogramm_v6"                        # Name des BIS, Minimalprogramm v6
bn3="pj2-BIS-alle-druck-up-BIS"                         # Name des Druckprogrammes (alle Druckunterprogramme)

cd ./Assembler                                          # c82ass.sh laeuft nur aus dem Ordner Assembler
# KEP assemblieren, Testdatei nach Tests/ (zum Laden auf die Trommel)
./c82ass.sh -p Claude_bsp_reassemblierung/"$bn" -s "$bn".asm -t ../Tests/"$bn".test

# BIS (v6) assemblieren, Testdatei nach Tests/
./c82ass.sh -p Projekt_2 -s "$bn2".asm -t ../Tests/"$bn2".test

# Druckprogramm assemblieren: binaerer Objektcode-Lochstreifen (.obj) nach Leser1 (Ordner, Name aus -s)
./c82ass.sh -p ./Projekt_2 -s "$bn3".asm -o ../virtuelle_Geraete/Leser1/

# BIS (v6) nochmals assemblieren: absolut adressierter, vom KEP ladbarer Lochstreifen (.kep) nach Leser2
./c82ass.sh -p ./Projekt_2 -s "$bn2".asm -o ../virtuelle_Geraete/Leser2/"$bn2".kep --ABSPR

cd ..                                                   # zurueck in den Projektstamm
# NUR das KEP auf die Trommel laden (Testdatei mit #TROMMEL=LEER: Trommel vorher leer), Test selbst nicht ausfuehren
python3 c8205_interp.py --MODUS=TEST Tests/"$bn".test --LOADONLY

# zur Kontrolle die ersten 10 Zeilen der Trommel anzeigen (Zellen 0000 bis 0011)
head -n 10 ./Trommel/trommel.txt

# GRAFIK-Fenster mit Pult starten; --HWCHECK blendet das zweite Fenster mit BZ, BR, AC, AR ein, mit Ton (kein --STUMM)
./c8205_grafik.sh --HWCHECK

# Bedienung am GRAFIK-Fenster:
# 1. mit  H G M+ E E M- K2 R  das KEP starten (Kanal K2 vor R waehlen): es liest das BIS (.kep) von Leser 2.
# 2. dann  H G R  um das BIS zu starten; als Leitadresse fuer das Druckprogramm 21 3000. eingeben (ohne Leerzeichen).
# 3. Dann K1 waehlen, der Lochstreifen (.obj) wird geladen. Am Ende steht wieder das BIS in der Kennzeicheneingabe.
# 4. Dort die Startadresse eingeben: K0  10 3000 000 .  (ohne Leerzeichen)
# Das Druckprogramm testet nun die 3 Ausgabeunterprogramme des BIS und beendet sich.
