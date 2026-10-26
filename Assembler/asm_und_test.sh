#!/bin/bash
# asm_und_test.sh -- assembliert ein Programm, ergänzt die vom Assembler erzeugte .test um eine
# Prüfung und startet den TEST-Interpreter. Alles in einem Aufruf; von überall startbar.
#
# Aufruf:  Assembler/asm_und_test.sh <ordner_mit_asm> <name>[.asm] [AAAA=WERT ...]
#
#   <ordner_mit_asm>  Projektordner, relativ zu Assembler/ (wie bei c82ass.sh -p) oder absolut
#   <name>            Quelltext ohne oder mit .asm
#   AAAA=WERT         erwartete Ergebniszellen, Adresse 4 und Wert 11 Oktalziffern,
#                     z. B. 0001=00000000017 0002=00000000005
#                     (die erwarteten Werte vorher von Hand herleiten, nicht aus einem Lauf abschreiben)
#
# Ergänzt in <ordner>/<name>.test (wird bei jedem Assemblerlauf neu erzeugt):
#   - #TROMMEL=LEER unter #PROT STUFE=2 (falls noch keine #TROMMEL=-Zeile da ist),
#   - #SPEI-0001 auf den Bereich der genannten Ergebniszellen (statt 0000-0000),
#   - am Ende "Prüfungen:" mit US=1 und den genannten Zellen (falls noch kein Prüfungen:-Abschnitt da ist).
# Ohne Ergebniszellen wird nur US=1 geprüft.
#
# Rückgabe: Rückgabecode des Assemblers, wenn dieser fehlschlägt (16), sonst der des Interpreters
#           (0 Test wahr, 4 ohne Prüfung, 6 Test falsch, 8 Laufzeitfehler, 16 formale Prüfung negativ, 2 Aufruf falsch);
#           2 bei falschem Aufruf dieses Skripts.
# Nebenwirkung: Der Assembler schreibt Assembler/projekdetails, der Interpreter ändert Trommel/trommel.txt
#               (mit #TROMMEL=LEER wird sie zuvor geleert) und schreibt Test-Protokolle/<test>/.

if [ $# -lt 2 ]; then
    sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//' | head -12
    exit 2
fi

stamm=$(cd "$(dirname "$0")/.." && pwd) || exit 2
ordner="$1"; name="${2%.asm}"; shift 2

for z in "$@"; do
    echo "$z" | grep -qE '^[0-7]{4}=[0-7]{11}$' || { echo "Ungültige Ergebniszelle '$z' (erwartet AAAA=WERT mit 4 und 11 Oktalziffern)"; exit 2; }
done

# 1. Assemblieren (immer aus Assembler/ starten)
cd "$stamm/Assembler" || exit 2
./c82ass.sh -p "$ordner" -s "$name.asm" --WARN=ALLE --no-color
rc=$?
if [ $rc -ne 0 ]; then echo "Assembler: Rückgabecode $rc, kein Test."; exit $rc; fi

test_datei="$(cd "$ordner" && pwd)/$name.test"
[ -f "$test_datei" ] || { echo "Keine .test erzeugt: $test_datei"; exit 2; }

# 2. .test ergänzen
python3 - "$test_datei" "$@" <<'PY'
import re, sys
pfad, zellen = sys.argv[1], sys.argv[2:]
t = open(pfad, encoding='utf-8').read()
if not re.search(r'^#TROMMEL=', t, re.M):
    t = re.sub(r'^(#PROT STUFE=\d+[^\n]*\n)', r'\1#TROMMEL=LEER\n', t, count=1, flags=re.M)
    if '#TROMMEL=LEER' not in t:
        t = t.replace('Trommeldatei:\n', 'Trommeldatei:\n#TROMMEL=LEER\n', 1)
if zellen:
    adr = sorted(int(z.split('=')[0], 8) for z in zellen)
    t = re.sub(r'^#SPEI-0001 [0-7]{4}-[0-7]{4}', '#SPEI-0001 %04o-%04o' % (adr[0], adr[-1]), t, count=1, flags=re.M)
if not re.search(r'^Prüfungen:', t, re.M):
    t = t.rstrip('\n') + '\n\nPrüfungen:\nUS=1\n' + ''.join('%s: %s\n' % tuple(z.split('=')) for z in zellen)
open(pfad, 'w', encoding='utf-8').write(t)
PY
[ $? -eq 0 ] || { echo "Ergänzen der .test fehlgeschlagen"; exit 2; }

# 3. Interpreter (aus dem Projektstamm, ohne Benutzer-Site-Pakete)
cd "$stamm" || exit 2
python3 -I c8205_interp.py --MODUS=TEST "$test_datei"
exit $?
