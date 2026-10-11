#!/bin/bash
# Tests des BIS: erst das Minimalprogramm auf die Trommel, dann der eigentliche Test.
LINIE="-----------------------------------------------------------------------------------"

clear
echo "python3 erzeuge_leere_trommel.py"
python3 erzeuge_leere_trommel.py || exit 1

./c8205_bis_test.sh Tests/pj2-bis_minimalprogramm.test

echo "$LINIE"
./c8205_bis_test.sh Tests/pj2-bis_adressendruck.txt
./c8205_bis_test.sh Tests/pj2-bis_adresseneingabe_4stellig.txt
./c8205_bis_test.sh Tests/pj2-bis_adresseneingabe_8stellig.txt
./c8205_bis_test.sh Tests/pj2-bis_adresseneingabe_null.txt
./c8205_bis_test.sh Tests/pj2-bis_adresseneingabe_ueberzaehlig.txt
./c8205_bis_test.sh Tests/pj2-bis_adresseneingabe_ziffer8_halt.txt
./c8205_bis_test.sh Tests/pj2-bis_adresseneingabe_ziffer9_erste.txt
./c8205_bis_test.sh Tests/pj2-bis_adresseneingabe_zr.txt
./c8205_bis_test.sh Tests/pj2-bis_befehlsdruck.txt
./c8205_bis_test.sh Tests/pj2-bis_druck_bz_ac.txt
