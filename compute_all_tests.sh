#!/bin/bash
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
    case "$dat" in *-ausgabe.txt|*_erwartet.txt|Tests/pj2-bis_*.txt) continue;; esac
    lauf "$dat"
done

erzeuge_leere_trommel.py

# Zusatzlauf: derselbe Test mit einem zweiten Streifen (der Schalter überstimmt die Zeile --leser1 der Testdatei;
# das Protokoll des Tests wird dabei überschrieben)
lauf Tests/lb-003_Paritaetsfehler.txt --leser1 $L1/lb-003_irrung_zeichen_dann_paritaetsfehler.txt
