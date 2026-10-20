#!/bin/sh
# r300_eingabe_lauf_und_auswertung.sh - echter Tk-Lauf von r300_eingabe (RE-001) UND Auswertung in einem Schritt.
# Aufruf aus dem Projektordner:   sh testscripte/r300_eingabe_lauf_und_auswertung.sh [Faktor]
# Braucht Python 3 mit Tkinter und einen Bildschirm. Das Fenster waehrend des Laufs (ca. 50 s) NICHT anfassen.
# Die Trommel wird in eine KOPIE gelegt (r300_eingabe_trommel_nach_lauf.txt); Trommel/trommel.txt bleibt unberuehrt.
# Ergebnis: r300_eingabe_debug.log, r300_eingabe_trommel_nach_lauf.txt, r300_eingabe_bericht.txt (bitte alle drei zurueckschicken).
# Rueckgabewert: 0 = Lauf und Auswertung ohne Befund, 1 = Befund(e), 2 = Lauf konnte nicht gestartet werden.
cd "$(dirname "$0")/.." || exit 2
python3 -c "import tkinter" 2>/dev/null || { echo "Kein Tkinter: dieser Lauf braucht ein echtes Fenster."; exit 2; }
rm -f r300_eingabe_debug.log
sh testscripte/r300_eingabe_grafik.sh "$@" || exit 2
[ -s r300_eingabe_debug.log ] || { echo "Kein Debug-Log entstanden."; exit 2; }
python3 testscripte/r300_eingabe_log_auswerten.py r300_eingabe_debug.log r300_eingabe_trommel_nach_lauf.txt r300_eingabe_bericht.txt
R=$?
echo "Auswertung: Rueckgabewert $R  -  Bericht: r300_eingabe_bericht.txt"
exit $R
