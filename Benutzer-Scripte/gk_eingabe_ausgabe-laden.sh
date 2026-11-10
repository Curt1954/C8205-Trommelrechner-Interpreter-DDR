
#!/usr/bin/env bash

BASIS=/home/shared_folder_1/scan/fertig/neu
TROMMEL="$BASIS/Trommel"
LESER1="$BASIS/virtuelle_Geraete/Leser1"
LOCHSTREIFEN="$BASIS/Lochstreifen"
BAISIS="$BASIS"


echo
echo "Automatik:  gk_eingabe_ausgabe laden"
echo

cd "$BASIS" || exit 1

QUELLE="$LOCHSTREIFEN/"im_BIS-Format/Sonstige/gk_ausgabe.obj 
ZIEL="$LESER1"/

cp "$QUELLE" "$ZIEL" 
SSS=`ls -1 "$ZIEL"gk_ausgabe.obj`
if [ "$SSS" != "$ZIEL""gk_ausgabe.obj" ]; then
   echo fehlt
   exit
else
  echo "$ZIEL""gk_ausgabe.obj  vorhanden" 
fi

echo "Starte Grafikinterpreter"
echo "./c8205_grafik.sh  --trommelzeit echt --LS-LESER-TYP=FS751"

# Grafikprogramm starten
./c8205_grafik.sh \
    --trommelzeit echt \
    --LS-LESER-TYP=FS751

exit $?


