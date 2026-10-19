#!/bin/bash
# Skripte liegen in ./testscripte; gearbeitet wird immer im Projektverzeichnis (eine Ebene darüber).
HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HIER/.." || exit 1
# Alle Tests ausführen; Rückkehrcode 0 (Test wahr) und 4 (keine Prüfung definiert) werden nicht gemeldet.
# Rückkehrcode 6 wird bei einer Testdatei mit der Kopfzeile "Prüfungen: False" ebenfalls nicht gemeldet
# (der Test soll bewusst "Test falsch" ergeben).
# Die Geräte der Tests (Lochstreifen für Leser 1 und 2, Schreibwerk-Ausgabe, K0) stehen als Zeilen
# --leser1 / --leser2 / --sw-ausgabe / --k0 in den Testdateien selbst. Hier wird nur der Stanzer 1 für alle Läufe
# global vorgegeben; ein Schalter der Kommandozeile hat Vorrang vor der Zeile der Testdatei.

L1=virtuelle_Geraete/Leser1

# Testdatei mit der Kopfzeile "Prüfungen: False" (Test soll bewusst "Test falsch" ergeben, rc 6)?
# Ohne Pfad wird die Datei auch in Tests/ gesucht, wie es der Interpreter tut.
erwartet_falsch() {
    local f=$1
    [ -f "$f" ] || f="Tests/$f"
    [ -f "$f" ] && grep -q -E '^Prüfungen:[[:space:]]*[Ff][Aa][Ll][Ss][Ee][[:space:]]*$' "$f"
}

# Einen Lauf ausführen und den Rückkehrcode melden: lauf TESTDATEI [weitere Schalter]
lauf() {
    local dat=$1; shift
    ./c8205_interpreter.sh "$dat" --NO-TERMOUT --stanzer1 virtuelle_Geraete/Stanzer1/ "$@"
    local rc=$?
    case $rc in
        0|4) ;;
        1)  echo "$dat: rc=1  Wrapper: Testdatei fehlt" ;;
        2)  echo "$dat: rc=2  ungültiger Aufruf (Schalter, Regelwerk-Dateien, --out)" ;;
        6)  erwartet_falsch "$dat" || echo "$dat: rc=6  Test falsch" ;;
        8)  echo "$dat: rc=8  Laufzeitfehler (Stub, Gerät nicht nutzbar, Abbruch)" ;;
        16) echo "$dat: rc=16 Vorab-Prüfung fehlgeschlagen (Test nicht gestartet)" ;;
        *)  echo "$dat: rc=$rc  unbekannter Rückkehrcode" ;;
    esac
}

for dat in Tests/*.txt; do
    # Soll-Dateien der Dateiprüfungen sind keine Tests; die Tests des BIS (pj2-bis_*) setzen das Minimalprogramm
    # auf der Trommel voraus und laufen mit test_bis.sh
    # st-004* und st-005 setzen einen bestimmten Trommelinhalt voraus (Zelle 0001); sie laufen unten mit ihren Vorbedingungen
    case "$dat" in *-ausgabe.txt|*_erwartet.txt|Tests/pj2-bis_*.txt|Tests/st-004_*.txt|Tests/st-005_*.txt) continue;; esac
    lauf "$dat"
done

# Tests mit Voraussetzung auf der Trommel: Die Trommel behält ihren Inhalt von Test zu Test, im Lauf über alle Tests
# stünde in Zelle 0001 sonst, was der vorige Test dort hinterlassen hat.
#  - st-004*: Minimalprogramm des BIS (Tests/pj2-bis_minimalprogramm.test); Zelle 0001 wird von den Tests nicht verändert
#  - st-005:  Druckroutine aus Tests/asm_druck_tastenfolge.txt (Zelle 0001 = Sprung zum Druck von BZ und AC)
python3 "$HIER/erzeuge_leere_trommel.py"
# Das Minimalprogramm wartet nach dem Laden auf Tastatureingabe; hier nicht: Standardeingang geschlossen (rc 4, keine Prüfungen)
lauf Tests/pj2-bis_minimalprogramm.test </dev/null
lauf Tests/st-004_STARTE_1000_druck_interrupt.txt
lauf Tests/st-004_STARTE_1000_druck_interrupt_neu.txt
lauf Tests/asm_druck_tastenfolge.txt
lauf Tests/st-005_STARTE_1000_druck_mit_druckroutine.txt

python3 "$HIER/erzeuge_leere_trommel.py"

# Zusatzlauf: derselbe Test mit einem zweiten Streifen (der Schalter überstimmt die Zeile --leser1 der Testdatei;
# das Protokoll des Tests wird dabei überschrieben)
lauf Tests/lb-003_Paritaetsfehler.txt --leser1 $L1/lb-003_irrung_zeichen_dann_paritaetsfehler.txt
