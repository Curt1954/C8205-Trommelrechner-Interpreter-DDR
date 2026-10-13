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
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_bm_anfang.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_buchstabe_wie_null.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_gb_in_ziffern.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_wr_anfang.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_adresseneingabe_zv_wie_null.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_bm_vor_k1.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_doppelpunkt_im_wort.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_gb_im_wort.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_gb_vor_k1.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_irrung_zeichen_im_wort.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_irrung_zeichen_vor_k1.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_is_im_wort.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_is_vor_k1.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_k1_1_punkt.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_k1_2_punkt.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_kb_im_wort.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_kb_vor_k1.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_null_punkt.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_wort_basis.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_wr_im_wort.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_wr_vor_k1.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_wr_zwischen_k1_k2.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_zr_im_wort.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_zr_vor_k1.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_kz_zv_vor_k1.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_adressaenderung_k2.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_hla_auf_band.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_hla_neu_mitten.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_hla_vorbesetzt.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_null_punkt.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_relativadresse.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_schlusszeichen_bm.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_schlusszeichen_sofort.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_sofortbefehl_sprung.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_sofortbefehl_start.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_sofortbefehl_us.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_unzulaessiges_zeichen.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_wr_im_wort.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_zeichen_zwischen_woertern.txt
"$HIER/c8205_bis_test.sh" Tests/pj2-bis_ps_zv_fehler.txt

