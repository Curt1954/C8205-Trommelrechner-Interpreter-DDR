#!/bin/bash
# grafik_alle_tests.sh - alle Pruefungen von Stufe 1 nacheinander (ein Kern: NICHT parallel starten).
# Aufruf (aus dem Projektordner oder von ueberall):  bash testscripte/grafik_alle_tests.sh [--schnell]
#   --schnell   ohne die beiden Gleichwertigkeitslaeufe TEST/GRAFIK (die dauern am laengsten)
# Ergebnis: je Block eine Zeile OK/FEHLER, am Ende eine Summe; Rueckgabewert 0 nur, wenn alle Bloecke bestanden haben.
# Linux; unter Windows nicht getestet.
cd "$(dirname "$0")/.." || exit 2
export PYTHONWARNINGS=ignore::ResourceWarning      # die Warnungen kommen aus dem unveraenderten c8205_interp.py
export PYTHONDONTWRITEBYTECODE=1                   # keine __pycache__-Ordner im Paket
export C8205_FENSTERLAGE=aus                       # FL-001: die Tests duerfen die gemerkte Fensterlage des Benutzers nicht beschreiben (die Fensterlage-Tests setzen einen eigenen Pfad)
LOG=$(mktemp -d)
ok=0; fehler=0
block() {   # block "Name" Befehl...
  local name="$1"; shift
  local t0=$SECONDS
  if "$@" >"$LOG/$ok$fehler.log" 2>&1; then
    printf 'OK      %-58s %4d s\n' "$name" $((SECONDS - t0)); ok=$((ok + 1))
  else
    printf 'FEHLER  %-58s %4d s  (Ausgabe unten)\n' "$name" $((SECONDS - t0)); fehler=$((fehler + 1))
    sed 's/^/        | /' "$LOG/$ok$((fehler - 1)).log" | tail -40
  fi
}
# OP-19 (entschieden 21.10.2026, Variante b): Trommel/trommel.txt und trommel.basp duerfen sich waehrend des Sammellaufs nicht aendern.
# Stand vor dem ersten Block merken; der letzte Block (unten) vergleicht. Ist der Stand nicht zu merken, zaehlt das als Fehler (ohne Vergleich).
if ! python3 -I testscripte/grafik_trommel_waechter.py merken "$LOG/trommel_stand.json"; then
  echo "FEHLER  Trommelwaechter: Stand vor dem Lauf nicht zu merken"; fehler=$((fehler + 1))
fi
block "Kern (grafik_kern_tests)"                  python3 testscripte/grafik_kern_tests.py
block "Geraete (grafik_geraete_tests)"            python3 testscripte/grafik_geraete_tests.py
block "Checkpoint 4 (Geraetefehler, H, Stanzer)"  python3 testscripte/grafik_checkpoint4_tests.py
block "Checkpoint 5 (Korb, Leser, Stanzer)"       python3 testscripte/grafik_checkpoint5_tests.py
block "Stufe 2 (Pult-Steuerung, Fenster mit Ersatzmodul)" python3 testscripte/grafik_pult_tests.py
block "Stufe 3 (SW-Fenster: Logik, Eingabe, Ersatzmodul)"   python3 -I testscripte/grafik_sw_tests.py
block "Stufe 3 (Ende-zu-Ende: ziffern, sw_zwei_ziffern, Schalter SW)" python3 -I testscripte/grafik_sw_ende_zu_ende.py
block "Stufe 3 (SW-Eingabe ueber Pult-Tasten, Lage des SW)"            python3 -I testscripte/grafik_sw_pult_test.py
block "Stufe 4 (Toene: Mischer, Rechnerton, Leser, Stanzer, Schreibwerkzeit, Klangwahl, Selektor SW, Ausfall)" python3 -I testscripte/grafik_stufe4_tests.py
block "Stufe 5 (--MODUS: Standard GRAFIK, TEST wie bisher, Wrapper)" python3 -I testscripte/grafik_stufe5_tests.py
block "Tastaturbelegung (--TASTATUR de|en)" python3 -I testscripte/grafik_tastatur_tests.py
block "Abstand Umschalttaste und Zeichentaste (G4-011)" python3 -I testscripte/grafik_sw_abstand_tests.py
block "Stufe 3 (Trockenlauf des Tk-Tests, ohne Tkinter; echter Lauf: testscripte/grafik_sw_tk_test.py)" python3 -I testscripte/grafik_sw_tk_test.py --ohne-tk --bericht /tmp/sw_tk_trocken.txt
block "Stufe 2 (Stresstest Pult/Rechner-Thread, 3 x 6 s)" bash -c 'for s in 3 5 6; do python3 -I testscripte/grafik_pult_stress.py 6 $s 2>/dev/null || exit 1; done'
block "Trommel-Erweiterungsmodul (Python)"        bash -c 'cd c-module/python && python3 -m unittest test_c8205_trommel'
block "C-Module: make test-alle (3 Testrahmen)"   bash -c 'cd c-module && make test-alle && make clean'
if [ "${1:-}" != "--schnell" ]; then
  block "Gleichwertigkeit TEST/GRAFIK (--alle)"         python3 testscripte/grafik_gleichwertigkeit.py --alle
  block "Gleichwertigkeit mit neuen Geraeten"           python3 testscripte/grafik_gleichwertigkeit.py --neue-geraete
fi
block "Trommelwaechter (Selbsttest mit Gegenproben)"  python3 -I testscripte/grafik_trommel_waechter_tests.py
block "Trommelwaechter (trommel.txt und trommel.basp unveraendert)" python3 -I testscripte/grafik_trommel_waechter.py pruefen "$LOG/trommel_stand.json"
echo "----"
echo "Bloecke bestanden: $ok, fehlgeschlagen: $fehler"
rm -rf "$LOG"
[ "$fehler" -eq 0 ]
