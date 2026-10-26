#!/bin/bash
# zt_tests.sh - Tests der Zusatztrommeln (Schalter --C8205Z) in C8205Z/Tests_Z/ ausfuehren.
# Aufruf: bash C8205Z/Tests_Z/zt_tests.sh        (laeuft von ueberall; wechselt in den Projektstamm)
# Erwartet: zt-001 und zt-002 rc 0 (Test wahr), zt-003 rc 8 (Stub: Ausgabe-Halt ohne Anwahl).
# Die ZT-Dateien liegen in einem Wegwerf-Ordner, nicht in Trommel/ZT/.
export LC_ALL=C.UTF-8
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1
ZTV=$(mktemp -d)
fehler=0
for t in zt-001_hin_zurueck:0 zt-002_zwei_trommeln:0 zt-003_ohne_anwahl:8; do
    n=${t%%:*}; soll=${t##*:}
    python3 -I c8205_interp.py --MODUS=TEST --NO-TERMOUT --C8205Z="$ZTV" --out "$ZTV/prot" "C8205Z/Tests_Z/$n.test" >/dev/null 2>&1
    rc=$?
    if [ "$rc" -eq "$soll" ]; then echo "$n: rc=$rc ok"; else echo "$n: rc=$rc, erwartet $soll  FEHLER"; fehler=1; fi
done
rm -rf "$ZTV"
exit $fehler
