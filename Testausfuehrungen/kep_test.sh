#!/bin/bash
# kep_test.sh -- KEP (Kleines Eingabeprogramm), Minimalprogramm v6 und Druckprogramm (als KEP-Lochstreifen) assemblieren,
#               KEP und v6 mit dem TEST-Interpreter auf die Trommel laden, danach das GRAFIK-Fenster starten.
# Aufruf (von ueberall): bash Testausfuehrungen/kep_test.sh
#
# Weg: KEP-Lochstreifen. Der Quelltext des Druckprogramms (...-KEP.asm) ist absolut adressiert und traegt vor start
#      das Pragma ;#; LEITADRESSE 00; assembliert wird mit --ABSPR (Datei .kep nach Leser1). Das KEP liest den Streifen.
# Alle Lademethoden und ihr Angang am Quelltext: markdown-dateien/C8205-Interpreter-Durchführung_eines_Tests.md, Abschnitt 2k.
cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." || exit 2   # Projektstamm: eine Ebene ueber Testausfuehrungen/

clear
echo Laden des KEP mit TEST-Interpreter
echo Assemblieren des Druckprogrammes als binaer codierter KEP-Lochstreifen
echo Laden des Druckprogrammes mit Hilfe des KEP
echo Test mit dem GRAFIK-Interpreter
echo

python3 ./testscripte/erzeuge_leere_trommel.py

bn="bsp_5_18_kep"
bn2="pj2-bis_minimalprogramm_v6"
bn3="pj2-BIS-alle-druck-up-KEP"

cd ./Assembler
./c82ass.sh -p Claude_bsp_reassemblierung/"$bn" -s "$bn".asm -t ../Tests/"$bn".test
./c82ass.sh -p Projekt_2 -s "$bn2".asm -t ../Tests/"$bn2".test
./c82ass.sh -p ./Projekt_2 -s "$bn3".asm -o ../virtuelle_Geraete/Leser1/"$bn3".kep --ABSPR

cd ..
python3 c8205_interp.py --MODUS=TEST Tests/"$bn".test --LOADONLY
python3 c8205_interp.py --MODUS=TEST ./Tests/"$bn2".test --LOADONLY

head -n 10 ./Trommel/trommel.txt

./c8205_grafik.sh --HWCHECK

# Bedienung am GRAFIK-Fenster (Ablauf wie Durchfuehrung_eines_Tests.md, 2j.1):
# 1. mit  H G M+ E E M- K1 R  das KEP starten: es liest den Streifen aus Leser1 (Lesedauer beachten, kein Haenger).
# 2. Nach dem Lesen mit H anhalten, dann H G R: Zelle 0000 springt nach 2000.
# 3. Erwartete Ausgabe auf SW: 4567 / 0765 432 / 0765 4321 065; das Programm haelt bei BZ=2017.
