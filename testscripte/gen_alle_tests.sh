#!/bin/bash
# gen_alle_tests.sh -- erzeugt und testet alle Programme, die einen Python-Generator haben
# (<Ordner>/gen/<n>_gen.py irgendwo unter Assembler/, z. B. Assembler/Claude/<ordner>/ und Assembler/Projekt_ZT_LOADER/...;
# Bibliothek Assembler/Claude/gen_lib/c82gen.py).
# Aufruf: bash testscripte/gen_alle_tests.sh        (von überall)
# Rückgabe: 0 alle Tests wahr, 1 mindestens einer nicht wahr, 2 kein Generator gefunden.
stamm=$(cd "$(dirname "$0")/.." && pwd) || exit 2
export LC_ALL=C.UTF-8
fehler=0; anzahl=0
for g in $(find "$stamm/Assembler" -path '*/gen/*_gen.py' | sort); do
    n=$(basename "$g" _gen.py)
    ordner=$(dirname "$(dirname "$g")")
    anzahl=$((anzahl + 1))
    if [ -f "$(dirname "$g")/${n}_test.sh" ]; then   # Programm mit eigenem Test (z. B. ZTD: laeuft nur ueber ZTL, nicht allein)
        ausgabe=$(bash "$(dirname "$g")/${n}_test.sh" 2>&1); rc=$?
    else
        ausgabe=$(bash "$stamm/Assembler/asm_und_test.sh" "$ordner" "$n" 2>&1); rc=$?
    fi
    if [ $rc -eq 0 ]; then echo "wahr   ${ordner#$stamm/Assembler/}/$n"; else echo "FALSCH ${ordner#$stamm/Assembler/}/$n (rc $rc)"; echo "$ausgabe" | tail -25; fehler=1; fi
done
[ $anzahl -eq 0 ] && { echo "Kein Generator gefunden."; exit 2; }
echo "$anzahl Generator(en), Ergebnis: $([ $fehler -eq 0 ] && echo alle wahr || echo FEHLER)"
exit $fehler
