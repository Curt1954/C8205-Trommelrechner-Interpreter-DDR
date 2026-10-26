#!/bin/bash
# testwahl.sh -- listet alle Tests in ./Tests mit Dateiname und Kurzinhalt, laesst einen Test
# ueber eine dreistellige Ziffernfolge waehlen und fuehrt ihn aus.
#
# Aufruf (von ueberall; das Skript wechselt selbst in den Projektstamm, eine Ebene ueber Testausfuehrungen/):
#   bash Testausfuehrungen/testwahl.sh [Suchtext]      Suchtext filtert die Liste (Name oder Kurzinhalt)
#   bash Testausfuehrungen/testwahl.sh -n [Suchtext]   nur Liste, keine Auswahl
#
# Ablauf nach der Wahl, immer vom Projektstamm aus:
#   1. Assembler: Gibt es zum Test einen Quelltext gleichen Namens (Assembler/**/<name>.asm), laeuft
#      Assembler/c82ass.sh -p <Ordner> -s <name>.asm -t ../Tests/asm_erzeugt/<name>.test
#      Die erzeugte .test landet in Tests/asm_erzeugt/ (zum Vergleichen). Sie ersetzt NICHT Tests/<name>.test,
#      weil dort von Hand ergaenzte Zeilen (Pruefungen:, #TROMMEL=, --k0 ...) stehen, die der Assembler nicht erzeugt.
#      Es folgt eine kurze Gegenueberstellung (diff) beider Dateien.
#      Gibt es keinen Quelltext (Treiber-Tests *.txt u. a.), wird der Assemblerlauf uebersprungen.
#      Ausnahme v6_test_druck, v6_test_adresse, v6_test_wort, v6_test_progst (Pruefprogramme des BIS-Minimalprogramms):
#      Schritt 1 ist  bash testscripte/pj2-bis_minimalprogramm_test.sh --NO-GRAFIK pj2-bis_minimalprogramm_v6 <kurz>
#      (baut Minimalprogramm und Pruefprogramme, laedt beide auf die Trommel; der GRAFIK-Interpreter wird nicht gestartet).
#      Der Test selbst (Schritt 2) leert die Trommel wegen #TROMMEL=LEER und laeuft mit eingebettetem Abbild.
#   2. Interpreter: python3 c8205_interp.py --MODUS=TEST --trommel <Projektstamm>/Trommel/trommel.txt Tests/<Datei>
#      Die Trommel in ./Trommel wird so benutzt, wie sie dort liegt; das Skript leert oder aendert sie nicht.
#      (Enthaelt der Test selbst #TROMMEL=LEER, leert der Interpreter sie auf Anweisung des Tests.)
#   3. Danach wird die Protokolldatei des Tests (Test-Protokolle/<test>/protokoll.txt) im vi geoeffnet; nach :q geht es weiter.
#   Eingabe <nnn>a (z. B. 174a) startet KEINEN Test, sondern oeffnet den Assembler-Quelltext des Tests (Assembler/**/<name>.asm,
#   bei den vier v6_test_* Assembler/Projekt_2/pj2-bis_minimalprogramm_v6_test_<kurz>.asm) im vi; nach :q geht es mit der Auswahl weiter.
#   Gibt es keinen Quelltext (Treiber-Tests), wird stattdessen die Testdatei Tests/<Datei> selbst im vi geoeffnet (mit Hinweis).
#   Die Eintraege <nnn>a stehen nicht zusaetzlich in der Liste.
#   Ansehen der Trommel nach dem Lauf: grep -n '^3000' Trommel/trommel.txt
#
# Rueckgabe: Rueckgabecode des zuletzt gelaufenen Interpreters (0 wahr, 4 ohne Pruefung, 6 falsch, 8 Laufzeitfehler,
#            16 formale Pruefung negativ); 2 bei falschem Aufruf.
export LC_ALL=C.UTF-8
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2   # Projektstamm: eine Ebene ueber Testausfuehrungen/
STAMM=$PWD

nur_liste=0
if [ "$1" = "-n" ]; then nur_liste=1; shift; fi
filter=$1

[ -d Tests ] || { echo "Ordner ./Tests fehlt (Projektstamm = Ordner ueber Testausfuehrungen/)."; exit 2; }
[ -f c8205_interp.py ] || { echo "c8205_interp.py fehlt im Projektstamm."; exit 2; }

# Kurzinhalt einer Testdatei: erste #DOK-Zeile (ohne Marke), sonst erste Kommentarzeile, sonst Hinweis
kurz() {
    local d=$1 z
    z=$(grep -m1 -E '^#DOK-[0-9]+' "$d" | sed -E 's/^#DOK-[0-9]+[[:space:]]*//')
    if [ -z "$z" ]; then
        z=$(grep -E '^#[[:space:]]*[^#[:space:]]' "$d" | grep -v -E '^#(TROMMEL|PROT|SPEI|STARTE|INTERRUPT)' | head -1 | sed -E 's/^#[[:space:]]*//')
    fi
    [ -z "$z" ] && z="(ohne Beschreibung)"
    printf '%s' "${z:0:78}"
}

# Soll-Dateien der Dateipruefungen sind keine Tests (wie in compute_all_tests.sh)
DATEIEN=()
while IFS= read -r f; do
    case "$f" in *-ausgabe.txt|*_erwartet.txt) continue;; esac
    DATEIEN+=("$f")
done < <(cd Tests && ls -1 *.test *.txt 2>/dev/null | sort)

zeige_liste() {
    local i f k
    for ((i=0; i<${#DATEIEN[@]}; i++)); do
        f=${DATEIEN[$i]}
        k=$(kurz "Tests/$f")
        if [ -n "$filter" ] && ! printf '%s %s' "$f" "$k" | grep -qi -- "$filter"; then continue; fi
        printf '%03d  %-48s %s\n' "$((i+1))" "$f" "$k"
    done
}

fuehre_aus() {
    local f=$1 name asm ordner rc
    name=${f%.*}
    echo
    echo "=== Test ${f} ==="
    asm=$(find Assembler -path Assembler/Regressionstest -prune -o -name "$name.asm" -print 2>/dev/null | sort | head -1)
    case "$name" in
        v6_test_druck|v6_test_adresse|v6_test_wort|v6_test_progst)
            # Die vier Pruefprogramme des BIS-Minimalprogramms: Quelltext heisst pj2-bis_minimalprogramm_v6_test_<kurz>.asm,
            # gebaut und geladen wird ueber testscripte/pj2-bis_minimalprogramm_test.sh (ohne GRAFIK-Interpreter)
            kz=${name#v6_test_}
            echo "--- 1. Assembler: testscripte/pj2-bis_minimalprogramm_test.sh --NO-GRAFIK pj2-bis_minimalprogramm_v6 $kz"
            bash testscripte/pj2-bis_minimalprogramm_test.sh --NO-GRAFIK pj2-bis_minimalprogramm_v6 "$kz" </dev/null
            rc=$?
            [ $rc -ne 0 ] && echo "Assembler/Laden: Rueckgabecode $rc (Fehler) - der Test wird trotzdem mit der vorhandenen Tests/$f gestartet."
            asm=""
            ;;
        *)
    if [ -n "$asm" ]; then
        ordner=$(dirname "$asm"); ordner=${ordner#Assembler/}
        mkdir -p Tests/asm_erzeugt
        echo "--- 1. Assembler: $asm  ->  Tests/asm_erzeugt/$name.test"
        ( cd Assembler && ./c82ass.sh -p "$ordner" -s "$name.asm" -t "../Tests/asm_erzeugt/$name.test" --WARN=ALLE --no-color )
        rc=$?
        if [ $rc -ne 0 ]; then
            echo "Assembler: Rueckgabecode $rc (Fehler) - der Test wird trotzdem mit der vorhandenen Tests/$f gestartet."
        elif [ -f "Tests/$name.test" ]; then
            echo "--- Unterschied erzeugte .test (<) zu Tests/$name.test (>), erste 20 Zeilen:"
            diff "Tests/asm_erzeugt/$name.test" "Tests/$name.test" | cut -c1-110 | head -20
            echo "--- (Ende Unterschied)"
        fi
    else
        echo "--- 1. Assembler: kein Quelltext $name.asm unter Assembler/ - uebersprungen"
    fi
            ;;
    esac
    echo "--- 2. Interpreter: Trommel $STAMM/Trommel/trommel.txt (unveraendert, wie sie liegt)"
    aus=$(mktemp)
    python3 -I c8205_interp.py --MODUS=TEST --trommel "$STAMM/Trommel/trommel.txt" "Tests/$f" </dev/null 2>&1 | tee "$aus"
    rc=${PIPESTATUS[0]}
    prot=$(sed -n 's/^Protokolldatei: //p' "$aus" | tail -1)
    rm -f "$aus"
    echo "--- Rueckgabecode Interpreter: $rc (0 wahr, 4 ohne Pruefung, 6 falsch, 8 Laufzeitfehler, 16 formale Pruefung negativ)"
    # Protokolldatei des Tests im vi oeffnen (nur an einem Terminal)
    if [ -n "$prot" ] && [ -f "$prot" ]; then
        if [ -t 0 ]; then
            echo "--- 3. Protokolldatei im vi: $prot"
            vi "$prot"
        else
            echo "--- 3. Protokolldatei (vi nur am Terminal): $prot"
        fi
    fi
    return $rc
}

# Assembler-Quelltext eines Tests im vi oeffnen (Eingabe <nnn>a), ohne Quelltext die Testdatei; startet keinen Test
zeige_quelle() {
    local f=$1 name asm
    name=${f%.*}
    case "$name" in
        v6_test_druck|v6_test_adresse|v6_test_wort|v6_test_progst)
            asm=Assembler/Projekt_2/pj2-bis_minimalprogramm_v6_test_${name#v6_test_}.asm;;
        *)  asm=$(find Assembler -path Assembler/Regressionstest -prune -o -name "$name.asm" -print 2>/dev/null | sort | head -1);;
    esac
    echo
    if [ -z "$asm" ] || [ ! -f "$asm" ]; then
        echo "Zu $f gibt es keinen Assembler-Quelltext ($name.asm unter Assembler/); stattdessen die Testdatei:"
        asm="Tests/$f"
    fi
    if [ -t 0 ]; then
        echo "--- im vi: $asm"
        vi "$asm"
    else
        echo "--- (vi nur am Terminal): $asm"
    fi
    return 0
}

zeige_liste
[ $nur_liste -eq 1 ] && exit 0
echo
rc=0
while true; do
    read -r -p "Test waehlen (3 Ziffern, 3 Ziffern + a = Quelltext im vi, l = Liste, q = Ende): " eing || exit $rc
    case "$eing" in
        q|Q|"") exit $rc;;
        l|L) zeige_liste; continue;;
    esac
    quelle=0
    case "$eing" in *[aA]) quelle=1; eing=${eing%?};; esac
    if ! [[ "$eing" =~ ^[0-9]{1,3}$ ]]; then echo "Bitte eine dreistellige Ziffernfolge, z. B. 007 (007a: Quelltext im vi)."; continue; fi
    nr=$((10#$eing))
    if [ "$nr" -lt 1 ] || [ "$nr" -gt "${#DATEIEN[@]}" ]; then echo "Nummer ausserhalb 001-$(printf '%03d' ${#DATEIEN[@]})."; continue; fi
    if [ $quelle -eq 1 ]; then zeige_quelle "${DATEIEN[$((nr-1))]}"; continue; fi
    fuehre_aus "${DATEIEN[$((nr-1))]}"
    rc=$?
    echo
done
