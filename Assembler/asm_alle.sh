#!/bin/bash
# asm_alle.sh - assembliert alle .asm-Dateien unterhalb eines Verzeichnisses mit c82ass.sh
#
# Aufruf:  ./asm_alle.sh [Basisverzeichnis]        (Vorgabe: ./)
#
# Fuer jede gefundene Datei  <Pfad>/<name>.asm  wird aufgerufen:
#     ./c82ass.sh -p <Pfad> -s <name>.asm
# Bei fehlerfreiem Lauf erscheint KEINE Meldung. Nur bei einem Fehler wird die Datei gemeldet,
# gefolgt von den Fehlerzeilen des Assemblers. Rueckgabewert: 0 = alles fehlerfrei, 1 = Fehler.
# Ein Fehler liegt vor, wenn c82ass.sh mit Rueckgabewert <> 0 endet ODER die Ausgabe eine
# Fehlermarke enthaelt ("Fehler", "ungültig", "Abbruch", Zeile mit Marke EE).

basis="${1:-.}"
cd "$(dirname "$0")" || exit 2          # c82ass.sh liegt neben diesem Script
[ -x ./c82ass.sh ] || { echo "FEHLER: ./c82ass.sh nicht gefunden oder nicht ausfuehrbar" >&2; exit 2; }
[ -d "$basis" ]    || { echo "FEHLER: Verzeichnis '$basis' existiert nicht" >&2; exit 2; }

anzahl=0; fehler=0
while IFS= read -r asm; do
    asm="${asm#./}"
    pfad="$(dirname "$asm")"
    datei="$(basename "$asm")"
    anzahl=$((anzahl+1))

    ausgabe="$(./c82ass.sh -p "$pfad" -s "$datei" 2>&1)"
    rc=$?
    ausgabe="$(printf '%s\n' "$ausgabe" | sed 's/\x1b\[[0-9;]*m//g')"     # Farbcodes entfernen
    meldungen="$(printf '%s\n' "$ausgabe" | grep -E 'Fehler|ungültig|Abbruch|^[0-9 ]{4}: EE ')"

    if [ $rc -ne 0 ] || [ -n "$meldungen" ]; then
        fehler=$((fehler+1))
        echo "FEHLER in $asm (Rueckgabewert $rc):"
        printf '%s\n' "$meldungen" | sed 's/^/    /'
    fi
done < <(find "$basis" -type f -name '*.asm' | sort)

[ $anzahl -eq 0 ] && echo "Hinweis: keine .asm-Dateien unter '$basis' gefunden" >&2
[ $fehler -eq 0 ]
