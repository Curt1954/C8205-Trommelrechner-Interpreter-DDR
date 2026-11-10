
#!/usr/bin/env bash

BASIS=/home/shared_folder_1/scan/fertig/neu
TROMMEL="$BASIS/Trommel"
LESER1="$BASIS/virtuelle_Geraete/Leser1"
LOCHSTREIFEN="$BASIS/Lochstreifen"
BAISIS="$BASIS"


echo
echo "Automatik:  BIS mittels KEP laden"
echo

echo
echo "Achtung: Trommel wird gelöscht."
echo "Fortsetzen [y/N]?"
read -r _frage

if [ "$_frage" != "y" ]; then
    echo "Abgebrochen."
    exit 0
fi


# Leertrommel bereitstellen
if [ ! -f "$TROMMEL/Leertrommel.txt" ]; then
    echo "Fehler: Leertrommel.txt fehlt."
    exit 1
fi

cp "$TROMMEL/Leertrommel.txt" "$TROMMEL/trommel.txt" || exit 1


KEPTEST="$LOCHSTREIFEN"/das_KEP_im_TEST-Format/bsp_5_18_kep.test
cd "$BASIS" || exit 1
./c8205_interpreter.sh "$KEPTEST"

QUELLE="$LOCHSTREIFEN/"im_KEP-Format/BIS-Minimalprogramm/pj2-bis_minimalprogramm_v6.kep 
ZIEL="$LESER1"/

cp "$QUELLE" "$ZIEL" 
SSS=`ls -1 "$ZIEL"pj2-bis_minimalprogramm_v6.kep`
if [ "$SSS" != "$ZIEL""pj2-bis_minimalprogramm_v6.kep" ]; then
   echo fehlt
   exit
else
  echo "$ZIEL""pj2-bis_minimalprogramm_v6.kep  vorhanden" 
fi

echo "Starte Grafikinterpreter"
echo "./c8205_grafik.sh --ohne-fenster --STUMM --entwickler-tasten \"H G M+ E E M+ K1 R\" --trommelzeit schnell --LS-LESER-TYP=FS751"

# Grafikprogramm starten
./c8205_grafik.sh \
    --ohne-fenster \
    --STUMM \
    --entwickler-tasten "H G M+ E E M+ K1 R" \
    --trommelzeit schnell \
    --LS-LESER-TYP=FS751

exit $?


