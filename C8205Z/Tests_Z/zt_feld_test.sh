#!/bin/bash
# zt_feld_test.sh - Beispielprogramm Assembler/Claude/zt_feld/zt_feld.asm (32 Konstanten -> ZT2 Adresse 01000 -> Spur 0200) pruefen.
# Aufruf: bash C8205Z/Tests_Z/zt_feld_test.sh      (laeuft von ueberall; wechselt in den Projektstamm)
# Erwartet: Test wahr (rc 0) mit --C8205Z, rc 8 ohne den Schalter (601 ist dort Leeroperation, der Halt-Test schlaegt fehl).
export LC_ALL=C.UTF-8
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1
T=Assembler/Claude/zt_feld/zt_feld.test
ZTV=$(mktemp -d)
python3 -I c8205_interp.py --MODUS=TEST --NO-TERMOUT --C8205Z="$ZTV" --out "$ZTV/prot" "$T" >/dev/null 2>&1; rc=$?
echo "zt_feld mit --C8205Z: rc=$rc (erwartet 0)"
echo "ZT2 Adresse 01000, erste und letzte Zelle:"; grep -E '^(1000|1037):' "$ZTV/zt2.txt"
python3 -I c8205_interp.py --MODUS=TEST --NO-TERMOUT --out "$ZTV/prot2" "$T" >/dev/null 2>&1; rc2=$?
echo "zt_feld ohne Schalter: rc=$rc2 (erwartet ungleich 0)"
rm -rf "$ZTV"
[ "$rc" -eq 0 ] && [ "$rc2" -ne 0 ]
