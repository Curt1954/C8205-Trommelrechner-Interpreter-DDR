#!/bin/bash
# interpreter_test.sh -- Trommel leeren, den Test pj2-bis-minimalprogramm-alle-druck-up assemblieren und mit dem
#                        TEST-Interpreter ausfuehren; zeigt Trommel, Eingabedatei und Protokollende.
# Aufruf (von ueberall): bash Testausfuehrungen/interpreter_test.sh
#
# Weg: Testdatei mit #TROMMEL=MP. Der Quelltext (pj2-bis-minimalprogramm-alle-druck-up.asm) traegt als Kommentarzeilen
#      ; #TROMMEL=MP, ; --k0 ..., ; --sw-ausgabe ...; mit -t uebernimmt der Assembler sie in die .test. Es wird kein
#      Lochstreifen gelesen; das Minimalprogramm kommt aus der Trommelvorlage Trommel/Trommelvorlagen/MP.txt.
# Erwartet: "Test wahr". Alle Lademethoden: markdown-dateien/C8205-Interpreter-Durchführung_eines_Tests.md, Abschnitt 2k.
cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." || exit 2   # Projektstamm: eine Ebene ueber Testausfuehrungen/

clear
echo Test mit dem TEST-Interpreter unter Benutzung der vorinstallierten Trommel MP.txt
echo

python3 ./testscripte/erzeuge_leere_trommel.py

cd ./Assembler
bn2="pj2-bis-minimalprogramm-alle-druck-up"
./c82ass.sh -p ./Projekt_2 -s "$bn2".asm -t ../Tests/"$bn2".test 1>/dev/null
cd ..

ls ./Tests/"$bn2".test
head -30 ./Trommel/trommel.txt

python3 c8205_interp.py --MODUS=TEST ./Tests/"$bn2".test
head -30 ./Trommel/trommel.txt
echo
echo Der Test startet durch Tastenfolge: H G R in der Test-Durchführungsdatei ./Tests/"$bn2".test
echo Das Startbefehl kommt aus der K0-Datei, Sie enthält 10 0000 2000 000 ., also den Sofortbefehl 10, Befehl 000 2000.
echo
ls ./Test-virtuelleGeraete/T-SW-Eingabe/pj2-bis-minimalprogramm-alle-druck-up.txt
cat ./Test-virtuelleGeraete/T-SW-Eingabe/pj2-bis-minimalprogramm-alle-druck-up.txt
echo
tail -20 ./Test-Protokolle/pj2-bis-minimalprogramm-alle-druck-up/protokoll.txt
