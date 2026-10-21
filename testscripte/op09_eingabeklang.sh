#!/bin/bash
# op09_eingabeklang.sh - Handpruefung H-7 / OP-09: Eingabeklang beim ersten Zeichen im SW-Fenster.
# Laedt einen Test (Abschnitt "Trommeldatei:" aus Tests/NAME.test) auf eine FRISCHE, leere Trommel in einer Arbeitskopie
# (Trommel/trommel.txt bleibt unberuehrt) und startet GRAFIK mit Fenster, mit Ton und mit --DEBUGLOG.
#
# Aufruf aus jedem Ordner:   testscripte/op09_eingabeklang.sh [NAME] [--nur-vorbereiten]
#   NAME  Test in Tests/ ohne Endung; Vorgabe sw_zwei_ziffern (liest Ziffern ueber SW ein, bestaetigt jede mit Ausgabe;
#         das Programm waehlt K0/SW selbst an, Zelle 0000 beginnt mit 030 04500, danach 030 04700)
#   --nur-vorbereiten   nur Trommelkopie anlegen und pruefen, kein Fenster (auch ohne Bildschirm moeglich)
#
# Ablauf am Pult:  Netz ein, G, R.  Dann sofort im SW-Fenster als ERSTES Zeichen die Ziffer 2 tippen (Taste kurz und deutlich druecken,
# loslassen), danach 3.  Das erste Zeichen nach dem Einschalten ist das Paar (Umschaltzeichen, Zeichen), siehe Beschreibung §6.10 Nr. 3.
# Danach Fenster schliessen (X) und die Zeilen im Log lesen:   grep -E "Taste|Loslassen|Eingabeklang" op09_debug.log
#   SW Taste ... -> folgt                     Umschaltzeichen angenommen, Zeichen wartet
#   SW zweite Eingabe beim Loslassen -> geliefert
#   SW Eingabeklang '2' ...                   Klang wurde angefordert.  Fehlt diese Zeile: Paar/Puffer/zweiter 011.
#                                             Steht sie da und es blieb still: Tonstrom (Abspielprogramm).
cd "$(dirname "$0")/.." || exit 2
NAME=sw_zwei_ziffern; NUR=0
for a in "$@"; do
  case "$a" in --nur-vorbereiten) NUR=1 ;; *) NAME="$a" ;; esac
done
TEST="Tests/$NAME.test"
[ -f "$TEST" ] || { echo "FEHLER: $TEST nicht gefunden" >&2; exit 2; }
KOPIE="op09_trommel.txt"
python3 -I - "$TEST" "$KOPIE" <<'PY' || exit 2
import re, sys
test, ziel = sys.argv[1], sys.argv[2]
zellen = {}
innen = False
for z in open(test, encoding='utf-8'):
    z = z.rstrip('\n')
    if z.strip() == 'Trommeldatei:':
        innen = True
        continue
    if not innen:
        continue
    m = re.match(r'^([0-7]{4}):\s*([0-7]{11})\b', z)
    if m:
        zellen[int(m.group(1), 8)] = m.group(2)
if not zellen:
    sys.exit('FEHLER: keine Zellen im Abschnitt "Trommeldatei:" von ' + test)
with open(ziel, 'w', encoding='utf-8', newline='\n') as f:
    for a in range(4096):
        f.write('%04o: %s\n' % (a, zellen.get(a, '0' * 11)))
print(f'{test}: {len(zellen)} Zellen auf leere Trommel geladen -> {ziel}')
PY
if [ "$NUR" = 1 ]; then
  python3 c8205_grafik.py --STUMM --ohne-fenster --BASP 000000 --trommel "$KOPIE" --entwickler-tasten "H" >/dev/null 2>&1
  echo "Vorbereitung ok (Rueckgabewert $?), kein Fenster gestartet."
  exit 0
fi
echo "Start: Netz ein, G, R; dann im SW-Fenster als erstes Zeichen 2 tippen, danach 3.  Log: op09_debug.log"
./c8205_grafik.sh --BASP 000000 --trommel "$KOPIE" --DEBUGLOG op09_debug.log
echo "Rueckgabewert $?  -  Log: op09_debug.log   (grep -E \"Taste|Loslassen|Eingabeklang\" op09_debug.log)"
