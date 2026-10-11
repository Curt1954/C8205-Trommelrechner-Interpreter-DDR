#!/bin/bash
# Entfernt die vom Assembler c82ass erzeugten Dateien, die der Interpreter nicht benutzt:
# .log, .mqo, .obj und .sym in den Projektordnern unter Assembler/.
# Behalten werden: .asm (Quelltext), .test (Trommeldatei), .dmp (Listing) und alles andere.
#
# Aufruf:  ./asm_aufraeumen.sh              nur anzeigen, was gelöscht würde (Trockenlauf)
#          ./asm_aufraeumen.sh --loeschen   tatsächlich löschen
#
# Das Skript gehört in den Ordner Assembler/ und arbeitet nur unterhalb davon.
# Nicht angefasst werden Dokumentation/, Sourcecode/, _Linux/ und _Windows/.
# Der Assembler legt die Dateien bei jedem Lauf neu an; nichts geht dauerhaft verloren.

cd "$(dirname "$0")" || exit 1

treffer() {
    find . -type f \
        \( -name '*.log' -o -name '*.mqo' -o -name '*.obj' -o -name '*.sym' \) \
        -not -path './Dokumentation/*' \
        -not -path './Sourcecode/*' \
        -not -path './_Linux/*' \
        -not -path './_Windows/*'
}

anzahl=$(treffer | wc -l)

if [ "$1" = "--loeschen" ]; then
    treffer | while IFS= read -r datei; do rm -- "$datei"; done
    echo "$anzahl Dateien gelöscht."
else
    treffer
    echo "---"
    echo "$anzahl Dateien würden gelöscht. Zum Löschen: $0 --loeschen"
fi
