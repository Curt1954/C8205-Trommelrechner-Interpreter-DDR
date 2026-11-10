#!/bin/bash
# einmal_vergleich.sh -- Beweist, dass das Makro GK_MATH (c82ass.makros) jeden Teil nur einmal erzeugt:
# Je Paar <n>.asm (mit Wiederholungsaufrufen) und <n>_ref.asm (ohne) muessen Objektdatei und Symboltabelle
# bitgleich sein. Danach laufen die drei Tests <n> mit asm_und_test.sh (Rechenergebnisse und Halt).
# Aufruf (von ueberall): bash Assembler/Claude/gk_math_einmal/einmal_vergleich.sh ; Rueckgabecode 0 = alles in Ordnung.
export LC_ALL=C.UTF-8
hier="$(cd "$(dirname "$0")" && pwd)"
asm="$(cd "$hier/../.." && pwd)"
rc=0
cd "$asm" || exit 3
for n in einmal_mix einmal_sub einmal_add; do
    for v in "$n" "${n}_ref"; do
        ./c82ass.sh -p Claude/gk_math_einmal -s "$v.asm" --no-color > "/tmp/$v.asslog" 2>&1 || { echo "FEHLER: $v.asm assembliert nicht (siehe /tmp/$v.asslog)"; rc=1; }
    done
    if cmp -s "$hier/$n.obj" "$hier/${n}_ref.obj" && cmp -s "$hier/$n.sym" "$hier/${n}_ref.sym"; then
        echo "OK:     $n  gleich $n""_ref (Objekt und Symbole): die Wiederholungen erzeugen nichts"
    else
        echo "ABWEICHUNG: $n unterscheidet sich von ${n}_ref (Code doppelt erzeugt?)"; rc=1
    fi
done
for n in einmal_mix einmal_sub einmal_add; do
    ./asm_und_test.sh Claude/gk_math_einmal "$n" 2>&1 | grep -E '^(Test wahr|Test falsch|Ende:)' | sed "s/^/$n: /"
    [ "${PIPESTATUS[0]}" -eq 0 ] || rc=1
done
exit $rc
