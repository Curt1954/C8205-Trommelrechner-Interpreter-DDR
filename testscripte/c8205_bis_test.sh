#!/bin/bash
# Skripte liegen in ./testscripte; gearbeitet wird immer im Projektverzeichnis (eine Ebene darüber).
HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HIER/.." || exit 1
# Aufruf: ./c8205_bis_test.sh TESTDATEI [Schalter ...]
# Tests der BIS-Bausteine setzen das Minimalprogramm auf der Trommel voraus.
# Dieses Skript laedt es zuerst (Tests/pj2-bis_minimalprogramm.test) und fuehrt dann den
# angegebenen Test aus. Die Trommel wird nicht zurueckgesetzt (dazu vorher
# python3 testscripte/erzeuge_leere_trommel.py aufrufen).

MINIMAL="Tests/pj2-bis_minimalprogramm.test"

# Testdatei mit der Kopfzeile "Prüfungen: False" (Test soll bewusst "Test falsch" ergeben, rc 6)?
# Ohne Pfad wird die Datei auch in Tests/ gesucht, wie es der Interpreter tut.
erwartet_falsch() {
    local f=$1
    [ -f "$f" ] || f="Tests/$f"
    [ -f "$f" ] && grep -q -E '^Prüfungen:[[:space:]]*[Ff][Aa][Ll][Ss][Ee][[:space:]]*$' "$f"
}

if [ $# -lt 1 ]; then
    echo "Aufruf: $0 TESTDATEI [Schalter ...]"
    exit 1
fi

echo "=== Schritt 1: Minimalprogramm laden ($MINIMAL) ==="
# Der Rueckgabecode des Ladeschritts wird ignoriert (er hat keine Pruefungen); der Rueckgabecode des Skripts ist der des eigentlichen Tests.
./c8205_interpreter.sh "$MINIMAL"

echo
echo "=== Schritt 2: $1 ==="
# Soll der Test bewusst "Test falsch" ergeben ("Prüfungen: False" in der Testdatei), läuft er mit --NO-TERMOUT:
# keine Prüfzeilen mit FEHLER und kein "Test falsch" am Bildschirm. Der Rückkehrcode bleibt 6.
zusatz=()
if erwartet_falsch "$1"; then
    zusatz=(--NO-TERMOUT)
fi
./c8205_interpreter.sh "$@" "${zusatz[@]}"
