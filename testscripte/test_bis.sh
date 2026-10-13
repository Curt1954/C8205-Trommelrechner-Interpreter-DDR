#!/bin/bash
# Skripte liegen in ./testscripte; gearbeitet wird immer im Projektverzeichnis (eine Ebene darüber).
HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HIER/.." || exit 1
# Tests des BIS: erst das Minimalprogramm auf die Trommel, dann der eigentliche Test.
LINIE="-----------------------------------------------------------------------------------"

clear
echo "python3 testscripte/erzeuge_leere_trommel.py"
python3 "$HIER/erzeuge_leere_trommel.py" || exit 1

"$HIER/c8205_bis_test.sh" Tests/pj2-bis_minimalprogramm.test

echo "$LINIE"
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adressendruck.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_4stellig.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_8stellig.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_null.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_ueberzaehlig.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_ziffer8_halt.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_ziffer9_erste.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_zr.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_befehlsdruck.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_druck_bz_ac.txt
