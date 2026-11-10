echo
cd /home/shared_folder_1/scan/fertig/neu

rm -f virtuelle_Geraete/Leser1/*.obj
cp ./virtuelle_Geraete/Leser1/LOCHSTREIFENKORB/zil.obj  ./virtuelle_Geraete/Leser1/

cp ./Trommel/ZT/zt3.txt ./Trommel/ZT/zt1.txt
cp ./Trommel/Trommelvorlagen/MP.txt ./Trommel/trommel.txt

#./c8205_grafik.sh --HWCHECK  --trommelzeit echt --DEBUGLOG

./c8205_grafik.sh --HWCHECK  --trommelzeit schnell --STUMM --LS-LESER-TYP=FS751 --C8205Z

