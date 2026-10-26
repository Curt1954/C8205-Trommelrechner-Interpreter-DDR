#!/bin/bash
# zt_grafik_tests.sh - Zusatztrommeln (--C8205Z) im Modus GRAFIK gegen TEST pruefen (Gleichwertigkeit, ohne Zeiten).
# Aufruf: bash C8205Z/Tests_Z/zt_grafik_tests.sh      (laeuft von ueberall; wechselt in den Projektstamm)
# Voraussetzung: das Erweiterungsmodul c8205_ztmodul ist gebaut (cd C8205Z/zt_modul/python && python3 setup.py build_ext --inplace --force)
#                Mit --force bauen: nach dem Auspacken eines Zips gilt ein altes .so sonst als aktuell und wird nicht neu uebersetzt
#                (dann fehlt z. B. letzte_adresse und der HW-Check zeigt ueberall ---). Kontrolle:
#                python3 -c "import c8205_ztmodul as m; print(m.__file__, hasattr(m,'letzte_adresse'))"   (muss True ausgeben)
#                und c8205_trommel (c-module/python) ist gebaut.
# Je Test (zt-001, zt-002: Test wahr; zt-003: ohne Anwahl) und je Trommelzeit (alt, echt, schnell):
#   (A) TEST (Python-Interpreter, c8205_zt.py, Zeit 0), (B) GRAFIK ohne Fenster mit c8205_ztmodul. Verglichen werden die Haupttrommel
#   und die Dateien zt1..zt4 (Byte fuer Byte), die Endregister (BZ, AC, Flags) und bei zt-003 der Halt mit Flag A.
# Alle Dateien liegen in einem Wegwerf-Ordner. Rueckgabe 0 = alles gleich.
export LC_ALL=C.UTF-8
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1
W=$(mktemp -d)
fehler=0
for n in zt-001_hin_zurueck zt-002_zwei_trommeln zt-003_ohne_anwahl; do
    t="C8205Z/Tests_Z/$n.test"
    keys=$(grep -A1 '^Tastenfolge' "$t" | tail -1 | sed 's/#.*//')
    rm -rf "$W/A" && mkdir -p "$W/A"
    python3 -I c8205_interp.py --MODUS=TEST --NO-TERMOUT --C8205Z="$W/A/zt" --trommel "$W/A/trommel.txt" --out "$W/A/prot" "$t" >"$W/A/log" 2>&1
    rcA=$?
    for z in alt echt schnell; do
        B="$W/B_$z"; rm -rf "$B" && mkdir -p "$B"
        cp "$W/A/trommel.txt" "$B/trommel.txt"
        python3 -I c8205_interp.py --MODUS=TEST --NO-TERMOUT --LOADONLY --trommel "$B/trommel.txt" "$t" >/dev/null 2>&1
        timeout 120 python3 c8205_grafik.py --ohne-fenster --STUMM --trommelzeit "$z" --trommel "$B/trommel.txt" --C8205Z="$B/zt" --entwickler-tasten "$keys" >"$B/log" 2>&1
        rcB=$?
        ok=1
        # Haupttrommel und Zusatztrommeln gleich (zt-003 hat keine Uebertragung: nur die leere Trommel pruefen)
        if [ "$n" != "zt-003_ohne_anwahl" ]; then
            cmp -s "$W/A/trommel.txt" "$B/trommel.txt" || ok=0
            for k in 1 2 3 4; do cmp -s "$W/A/zt/zt$k.txt" "$B/zt/zt$k.txt" || ok=0; done
            [ "$rcA" -eq 0 ] && [ "$rcB" -eq 0 ] || ok=0
            regA=$(grep -h "^Ende" "$B/log" | sed 's/.*BZ=/BZ=/')
            case "$regA" in BZ=*"US=1"*) ;; *) ok=0;; esac
        else
            [ "$rcA" -eq 8 ] || ok=0
            grep -q "A=1" "$B/log" || ok=0
        fi
        if [ "$ok" -eq 1 ]; then echo "$n [$z]: gleich ok"; else echo "$n [$z]: ABWEICHUNG (TEST rc=$rcA, GRAFIK rc=$rcB)  FEHLER"; fehler=1; fi
    done
done
rm -rf "$W"
exit $fehler
