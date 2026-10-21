#!/bin/bash
# Version 1.00-026
# Vollstaendige Pruefung des Assemblers c82ass fuer Entwickler und CI (aus beliebigem Verzeichnis aufrufbar):
#   1. Uebersetzen mit -Wall -Wextra -Wshadow -Werror: der Quelltext muss ohne Warnung uebersetzen.
#   2. Regressionstest (139 Programme gegen Referenz, Negativtests) mit dem normalen Binary.
#   3. Dasselbe Binary-Paar mit AddressSanitizer + UBSan (inkl. Leak-Pruefung); jede Meldung ist ein Fehler.
#
#   Regressionstest/pruefe_alles.sh            alles
#   Regressionstest/pruefe_alles.sh --ohne-asan   ohne Schritt 3 (z. B. wenn libasan fehlt)
#
# Rueckgabe: 0 = alles in Ordnung, sonst die Nummer des fehlgeschlagenen Schritts (1, 2, 3).
# Es entstehen nur Dateien in einem temporaeren Verzeichnis; im Projekt bleibt nichts liegen.

HIER=$(cd "$(dirname "$0")" && pwd)
ASM=$(cd "$HIER/.." && pwd)
SRC="$ASM/Sourcecode/ca82_protokoll.c $ASM/Sourcecode/ca82_standards.c $ASM/Sourcecode/ca82_symbole.c $ASM/Sourcecode/ca82_berichte.c $ASM/Sourcecode/ca82_makros.c $ASM/Sourcecode/ca82_zustand.c $ASM/Sourcecode/ca82_hilfen.c $ASM/Sourcecode/ca82_fehler.c $ASM/Sourcecode/ca82_quelle.c $ASM/Sourcecode/ca82_listing.c $ASM/Sourcecode/ca82_pass0.c $ASM/Sourcecode/ca82_pass1.c $ASM/Sourcecode/ca82_pass2.c $ASM/Sourcecode/ca82_ausdruck.c $ASM/Sourcecode/ca82_codierung.c $ASM/Sourcecode/ca82_pass3.c $ASM/Sourcecode/ca82_fluss.c $ASM/Sourcecode/ca82_testdatei.c $ASM/Sourcecode/ca82_main.c"
TMP=$(mktemp -d) || exit 1
trap 'rm -rf "$TMP"' EXIT
ASAN=1; [ "$1" = "--ohne-asan" ] && ASAN=0

echo "== 1. Uebersetzen mit -Werror"
gcc -O2 -Wall -Wextra -Wshadow -Werror -o "$TMP/c82ass" $SRC || { echo "FEHLER: Uebersetzung mit Warnungen oder Fehlern"; exit 1; }

echo "== 2. Regressionstest (normales Binary)"
"$HIER/regressionstest.sh" --binary "$TMP/c82ass" || { echo "FEHLER: Regressionstest"; exit 2; }

if [ $ASAN = 1 ]; then
    echo "== 3. Regressionstest unter AddressSanitizer/UBSan"
    gcc -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=undefined -fno-omit-frame-pointer \
        -o "$TMP/c82ass_asan" $SRC || { echo "FEHLER: Uebersetzung mit Sanitizern"; exit 3; }
    ASAN_OPTIONS=detect_leaks=1:abort_on_error=0 "$HIER/regressionstest.sh" --binary "$TMP/c82ass_asan" \
        || { echo "FEHLER: Regressionstest unter Sanitizern"; exit 3; }
fi
echo "ALLES IN ORDNUNG"
