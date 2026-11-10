#!/bin/bash
# zt_tests.sh - Tests der Zusatztrommeln (Schalter --C8205Z) in C8205Z/Tests_Z/ ausfuehren.
# Aufruf: bash C8205Z/Tests_Z/zt_tests.sh        (laeuft von ueberall; wechselt in den Projektstamm)
# Erwartet: zt-001 und zt-002 rc 0 (Test wahr), zt-003 rc 8 (Stub: Ausgabe-Halt ohne Anwahl);
# zt-004 rc 0 (ZT-Zellen-Pruefung wahr, #ZTROMMEL=LEER), zt-005 rc 6 (eine ZT-Zelle falsch), zt-006 rc 16 (Formfehler in den ZT-Zeilen),
# zt-007 OHNE --C8205Z rc 0 (ZT-Marken und ZT-Zeilen, auch fehlerhafte, kommentarlos ignoriert).
# (Die Probe ztl_probe_3000 ist entfallen: ihre Dateien gingen verloren; ztl_tests.py deckt das Laden ueber das BIS ab.)
# Danach ztl_tests.py (ZTL gegen das Format, 8 Faelle, rund 10 s; Quelltexte Assembler/Claude/ztl/ztl.asm und Assembler/Claude/ztl_test/ztd_stub.asm),
# danach zt_repo_test.py (Python-Hilfsprogramm zt_repo.py gegen das Format, rund 80 Pruefungen, Ausgabe "Test wahr", rc 0).
# Mit dem Argument ztc zusaetzlich ztc_test.py (ZTC, rund 135 Pruefungen, mehrere Minuten).
# Mit dem Argument ztd zusaetzlich ztd_tests.py (ZTD ueber die Kette BIS - ZTL - ZTD, 17 Faelle einschliesslich der Kette ZTC - ZTL - ZTD, rund eine Minute).
# Mit dem Argument ztdpy zusaetzlich ztd_py_tests.py (ZTD Fassung A aus dem Python-Generator, 114 Pruefungen, rund 2 Minuten).
# Die ZT-Dateien liegen in einem Wegwerf-Ordner, nicht in Trommel/ZT/.
export LC_ALL=C.UTF-8
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1
ZTV=$(mktemp -d)
fehler=0
for t in zt-001_hin_zurueck:0 zt-002_zwei_trommeln:0 zt-003_ohne_anwahl:8 zt-004_zt_zellenpruefung:0 zt-005_zt_zellenpruefung_falsch:6 zt-006_zt_zellenpruefung_form:16; do
    n=${t%%:*}; soll=${t##*:}
    python3 -I c8205_interp.py --MODUS=TEST --NO-TERMOUT --C8205Z="$ZTV" --out "$ZTV/prot" "C8205Z/Tests_Z/$n.test" >/dev/null 2>&1
    rc=$?
    if [ "$rc" -eq "$soll" ]; then echo "$n: rc=$rc ok"; else echo "$n: rc=$rc, erwartet $soll  FEHLER"; fehler=1; fi
done
python3 -I c8205_interp.py --MODUS=TEST --NO-TERMOUT --out "$ZTV/prot" "C8205Z/Tests_Z/zt-007_zt_ohne_schalter.test" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then echo "zt-007_zt_ohne_schalter: rc=$rc ok"; else echo "zt-007_zt_ohne_schalter: rc=$rc, erwartet 0  FEHLER"; fehler=1; fi
rm -rf "$ZTV"
python3 -I C8205Z/Tests_Z/ztl_tests.py >"$ZTV.ztl.log" 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then echo "ztl_tests: rc=0 ok ($(tail -1 "$ZTV.ztl.log"))"; else echo "ztl_tests: rc=$rc  FEHLER"; cat "$ZTV.ztl.log"; fehler=1; fi
rm -f "$ZTV.ztl.log"
python3 -I C8205Z/Tests_Z/zt_repo_test.py >"$ZTV.repo.log" 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then echo "zt_repo_test: rc=0 ok ($(tail -2 "$ZTV.repo.log" | head -1))"; else echo "zt_repo_test: rc=$rc  FEHLER"; cat "$ZTV.repo.log"; fehler=1; fi
rm -f "$ZTV.repo.log"
# ZTC (Assembler/Claude/ztc/ztc.asm) im Interpreter gegen zt_repo.py; nur mit dem Argument ztc, dauert einige Minuten (Lochstreifen lesen, --max-knoten)
if [ "$1" = "ztc" ]; then
    python3 -I C8205Z/Tests_Z/ztc_test.py >"$ZTV.ztc.log" 2>&1
    rc=$?
    if [ "$rc" -eq 0 ]; then echo "ztc_test: rc=0 ok ($(tail -2 "$ZTV.ztc.log" | head -1))"; else echo "ztc_test: rc=$rc  FEHLER"; tail -30 "$ZTV.ztc.log"; fehler=1; fi
    rm -f "$ZTV.ztc.log"
fi
# ZTD (Assembler/Claude/ztd/ztd.asm) ueber BIS - ZTL - ZTD im Interpreter gegen zt_repo.py; nur mit dem Argument ztd
if [ "$1" = "ztd" ] || [ "$2" = "ztd" ]; then
    python3 -I C8205Z/Tests_Z/ztd_tests.py >"$ZTV.ztd.log" 2>&1
    rc=$?
    if [ "$rc" -eq 0 ]; then echo "ztd_tests: rc=0 ok ($(tail -1 "$ZTV.ztd.log"))"; else echo "ztd_tests: rc=$rc  FEHLER"; tail -30 "$ZTV.ztd.log"; fehler=1; fi
    rm -f "$ZTV.ztd.log"
fi
# ZTD Fassung A (Assembler/Claude/ztd_py/ztd_py.asm, aus dem Generator; eigener Dialog, eigener Abnahmetest); nur mit dem Argument ztdpy
if [ "$1" = "ztdpy" ] || [ "$2" = "ztdpy" ]; then
    python3 -I C8205Z/Tests_Z/ztd_py_tests.py >"$ZTV.ztdpy.log" 2>&1
    rc=$?
    if [ "$rc" -eq 0 ]; then echo "ztd_py_tests: rc=0 ok ($(tail -2 "$ZTV.ztdpy.log" | head -1))"; else echo "ztd_py_tests: rc=$rc  FEHLER"; tail -30 "$ZTV.ztdpy.log"; fehler=1; fi
    rm -f "$ZTV.ztdpy.log"
fi
exit $fehler
