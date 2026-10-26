#!/bin/bash
# asm_alle.sh - assembliert alle .asm-Dateien unterhalb eines Verzeichnisses mit c82ass.sh
#
# Aufruf:  ./asm_alle.sh [-n] [Basisverzeichnis]        (Vorgabe: ./)
#          -n  vorhandene Tests/<name>.test NICHT ueberschreiben (die neue .test wird verworfen)
#
# Fuer jede gefundene Datei  <Pfad>/<name>.asm  wird aufgerufen:
#     ./c82ass.sh -p <Pfad> -s <name>.asm -t ../Tests/<name>.test
# Die .test-Datei geht also immer nach Tests/ (neben Assembler/), nicht in den Projektpfad. Ein vorhandenes
# Tests/<name>.test wird ueberschrieben! Tragen mehrere .asm in diesem Lauf denselben Namen, heisst die
# .test ab dem zweiten Vorkommen Tests/<Ordnername>_<name>.test (Hinweis am Ende). Nach dem Assemblieren
# werden <name>.log, <name>.mqo und <name>.sym im Projektpfad geloescht (bei einem Fehler bleiben sie
# zur Fehlersuche stehen). .obj, .dmp und .kep bleiben.
# Bei fehlerfreiem Lauf erscheint KEINE Meldung. Nur bei einem Fehler wird die Datei gemeldet,
# gefolgt von den Fehlerzeilen des Assemblers. Rueckgabewert: 0 = alles fehlerfrei, 1 = Fehler.
# Ein Fehler liegt vor, wenn c82ass.sh mit Rueckgabewert <> 0 endet (der Assembler liefert bei
# jedem Fehler einen Rueckgabewert <> 0). Die Ausgabe wird NICHT nach Woertern durchsucht: das
# Programmlisting enthaelt auch die Kommentare des Quelltexts, und ein Kommentar mit dem Wort
# "Fehler" wuerde sonst faelschlich als Fehler gemeldet. Zur Anzeige im Fehlerfall werden nur
# die Zeilen herausgesucht, die mit "Fehler:" beginnen (Meldungen des Assemblers) sowie
# Listingzeilen mit der Marke EE.
#
# Gleiche Meldungen werden nur einmal gezeigt, mit angehaengtem Zaehler "(Nx)"; je Datei hoechstens
# 30 verschiedene Zeilen (danach nur noch die Zahl der weggelassenen).
#
# Nicht geprueft werden (zaehlt als "uebersprungen", Ausgabe am Ende):
#  - alles unter Regressionstest, Sourcecode und Dokumentation (dort liegen absichtlich fehlerhafte
#    Negativtests; die prueft Regressionstest/regressionstest.sh gegen ihre .erwartet-Dateien),
#  - jede .asm, die in den ersten 15 Zeilen "Negativtest" oder "absichtlicher Fehler" enthaelt
#    (Gross-/Kleinschreibung egal): so kennzeichnet man ein Programm, das den Fehler beabsichtigt.

nicht_ueberschreiben=0
if [ "$1" = "-n" ]; then nicht_ueberschreiben=1; shift; fi
basis="${1:-.}"
cd "$(dirname "$0")" || exit 2          # c82ass.sh liegt neben diesem Script
[ -x ./c82ass.sh ] || { echo "FEHLER: ./c82ass.sh nicht gefunden oder nicht ausfuehrbar" >&2; exit 2; }
[ -d "$basis" ]    || { echo "FEHLER: Verzeichnis '$basis' existiert nicht" >&2; exit 2; }

testverz="../Tests"
[ -d "$testverz" ] || { echo "FEHLER: Verzeichnis '$testverz' (Tests/ neben Assembler/) existiert nicht" >&2; exit 2; }

# Namen, die mehrfach vorkommen (nur gleiche .test-Namen wuerden sich in Tests/ ueberschreiben)
declare -A vorkommen
while IFS= read -r asm; do
    n="$(basename "$asm" .asm)"; vorkommen[$n]=$(( ${vorkommen[$n]:-0} + 1 ))
done < <(find "$basis" \( -name Regressionstest -o -name Sourcecode -o -name Dokumentation \) -prune -o -type f -name '*.asm' -print | sort)
declare -A gesehen

anzahl=0; fehler=0; uebersprungen=0; umbenannt=0; ueberschrieben=0; behalten=0
while IFS= read -r asm; do
    asm="${asm#./}"
    pfad="$(dirname "$asm")"
    datei="$(basename "$asm")"
    if head -n 15 "$asm" | grep -qiE 'negativtest|absichtlicher fehler'; then
        uebersprungen=$((uebersprungen+1)); continue
    fi
    anzahl=$((anzahl+1))

    name="${datei%.asm}"
    testname="$name"
    if [ "${vorkommen[$name]:-0}" -gt 1 ]; then
        if [ -n "${gesehen[$name]}" ]; then
            testname="$(basename "$pfad")_$name"; umbenannt=$((umbenannt+1))
            echo "Hinweis: Name '$name' mehrfach; .test fuer $asm heisst Tests/$testname.test" >&2
        fi
        gesehen[$name]=1
    fi
    ziel="$testverz/$testname.test"; tmpziel=0
    if [ -f "$ziel" ]; then
        if [ $nicht_ueberschreiben -eq 1 ]; then ziel="$(mktemp -d)/$testname.test"; tmpziel=1; behalten=$((behalten+1))
        else ueberschrieben=$((ueberschrieben+1)); fi
    fi

    ausgabe="$(./c82ass.sh -p "$pfad" -s "$datei" -t "$ziel" 2>&1)"
    rc=$?
    [ $tmpziel -eq 1 ] && rm -rf -- "$(dirname "$ziel")"
    if [ $rc -eq 0 ]; then
        rm -f -- "$pfad/$name.log" "$pfad/$name.mqo" "$pfad/$name.sym"
    fi
    ausgabe="$(printf '%s\n' "$ausgabe" | sed 's/\x1b\[[0-9;]*m//g')"     # Farbcodes entfernen

    if [ $rc -ne 0 ]; then
        meldungen="$(printf '%s\n' "$ausgabe" | grep -E '^Fehler:|^[0-9 ]{4}: EE ')"
        [ -n "$meldungen" ] || meldungen="$(printf '%s\n' "$ausgabe" | tail -n 5)"   # Rueckfall: Ende der Ausgabe
        fehler=$((fehler+1))
        echo "FEHLER in $asm (Rueckgabewert $rc):"
        printf '%s\n' "$meldungen" | awk '
            { if (!($0 in n)) { zeile[++z] = $0 } n[$0]++ }
            END { for (i = 1; i <= z; i++) {
                      if (i > 30) { printf "... %d weitere verschiedene Zeilen weggelassen\n", z - 30; break }
                      printf "%s%s\n", zeile[i], (n[zeile[i]] > 1 ? "  (" n[zeile[i]] "x)" : "") } }' | sed 's/^/    /'
    fi
done < <(find "$basis" \( -name Regressionstest -o -name Sourcecode -o -name Dokumentation \) -prune -o -type f -name '*.asm' -print | sort)

[ $behalten -gt 0 ] && echo "Hinweis: $behalten vorhandene Tests/*.test unveraendert gelassen (-n)" >&2
[ $ueberschrieben -gt 0 ] && echo "Hinweis: $ueberschrieben vorhandene Tests/*.test ueberschrieben" >&2
[ $uebersprungen -gt 0 ] && echo "Hinweis: $uebersprungen Negativprogramm(e) uebersprungen, $anzahl geprueft" >&2
[ $anzahl -eq 0 ] && echo "Hinweis: keine .asm-Dateien unter '$basis' gefunden" >&2
rm -f projekdetails*               # wird bei jedem Lauf neu geschrieben
[ $fehler -eq 0 ]

