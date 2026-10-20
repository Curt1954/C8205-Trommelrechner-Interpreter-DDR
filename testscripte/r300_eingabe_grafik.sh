#!/bin/sh
# r300_eingabe_grafik.sh - GRAFIK mit --HWCHECK und --WIEDERGABE fuer das Eingabeprogramm r300_eingabe (RE-001).
# Aufruf aus dem Projektordner:   sh testscripte/r300_eingabe_grafik.sh [Faktor]      (Faktor z. B. 2 = alle Zeitabstaende verdoppeln)
# Braucht Python 3 mit Tkinter, einen Bildschirm und das gebaute C-Modul (wie c8205_grafik.sh). Das Fenster waehrend des Laufs NICHT anfassen
# (rund 50 Sekunden; die Wiedergabe tippt selbst im SW-Fenster und schaltet am Ende das Netz aus).
# Ergebnis: r300_eingabe_debug.log  (bitte zurueckschicken, dazu r300_eingabe_trommel_nach_lauf.txt)
cd "$(dirname "$0")/.." || exit 2
F="${1:-1}"
SPUR=Tests/r300_eingabe_klickspur.txt
if [ "$F" != "1" ]; then
  python3 -I - "$F" <<'PY' > r300_eingabe_klickspur_langsam.txt || exit 2
import sys
f = float(sys.argv[1])
for z in open('Tests/r300_eingabe_klickspur.txt', encoding='utf-8'):
    if z.startswith('#') or not z.strip():
        print(z.rstrip('\n'))
    else:
        t, rest = z.strip().split(None, 1)
        print(f'{float(t) * f:9.3f} {rest}')
PY
  SPUR=r300_eingabe_klickspur_langsam.txt
fi
cp Trommel/trommel_r300_eingabe.txt r300_eingabe_trommel_nach_lauf.txt || exit 2
python3 c8205_grafik.py --STUMM --netz-schnell --HWCHECK --BASP 000000 --trommel r300_eingabe_trommel_nach_lauf.txt \
  --WIEDERGABE "$SPUR" --DEBUGLOG r300_eingabe_debug.log
echo "Rueckgabewert $?  -  Debug-Log: r300_eingabe_debug.log"
