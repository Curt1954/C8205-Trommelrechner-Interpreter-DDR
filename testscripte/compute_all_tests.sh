#!/bin/bash
# compute_all_tests.sh - fuehrt alle Testauftraege in Tests/ aus und meldet nur Abweichungen (Rueckkehrcode weder 0 noch 4).
# Skripte liegen in ./testscripte; gearbeitet wird immer im Projektverzeichnis (eine Ebene darüber).
HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HIER/.." || exit 1
# Absicherung (Ausgabe soll klein bleiben, weil jede Zeile im Claude-Chat Limit kostet):
#  - LC_ALL=C.UTF-8 wird hier selbst gesetzt (Falle 3 der CLAUDE.md).
#  - Vorprüfung: Fehlt eine Datei mit Umlaut im Namen, wurde das Zip ohne LC_ALL entpackt; Abbruch mit einer Zeile (rc 3),
#    statt den Interpreter 170-mal mit seiner Usage-Meldung (rund 140 KB) aufzurufen.
#  - Je Lauf wird die Ausgabe des Interpreters aufgefangen; bei Abweichung erscheinen höchstens 3 Zeilen (die letzten),
#    sonst nichts. Ausgaben der Tests selbst (Schreibwerk-Texte) erscheinen nicht mehr.
#  - Nach 3 Läufen mit rc 1 oder 2 (Umgebungs- oder Aufruffehler) bricht das Skript ab (rc 3).
#  - Letzte Zeile immer: "compute_all_tests: N Laeufe, M Abweichungen". Rückgabe 0 = keine Abweichung, 1 = Abweichungen, 3 = Abbruch.
export LC_ALL=C.UTF-8
if [ ! -f "markdown-dateien/C8205-Interpreter-Eingänge_der_Knoten.md" ]; then
    echo "compute_all_tests: ABBRUCH - Datei mit Umlaut im Namen fehlt (Zip ohne 'export LC_ALL=C.UTF-8' entpackt?). Neu entpacken."
    exit 3
fi
ANZAHL=0; ABWEICHUNGEN=0; UMGEBUNGSFEHLER=0
# Alle Tests ausführen; Rückkehrcode 0 (Test wahr) und 4 (keine Prüfung definiert) werden nicht gemeldet.
# Rückkehrcode 6 wird bei einer Testdatei mit der Kopfzeile "Prüfungen: False" ebenfalls nicht gemeldet
# (der Test soll bewusst "Test falsch" ergeben).
# Die Geräte der Tests (Lochstreifen für Leser 1 und 2, Schreibwerk-Ausgabe, K0) stehen als Zeilen
# --leser1 / --leser2 / --sw-ausgabe / --k0 in den Testdateien selbst. Hier wird nur der Stanzer 1 für alle Läufe
# global vorgegeben; ein Schalter der Kommandozeile hat Vorrang vor der Zeile der Testdatei.

L1=Test-virtuelleGeraete/Leser1

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
    local aus; aus=$(mktemp)
    ./c8205_interpreter.sh "$dat" --NO-TERMOUT --stanzer1 Test-virtuelleGeraete/Stanzer1/ "$@" >"$aus" 2>&1
    local rc=$?
    ANZAHL=$((ANZAHL + 1))
    local meldung=""
    case $rc in
        0|4) ;;
        1)  meldung="rc=1  Wrapper: Testdatei fehlt"; UMGEBUNGSFEHLER=$((UMGEBUNGSFEHLER + 1)) ;;
        2)  meldung="rc=2  ungültiger Aufruf (Schalter, Regelwerk-Dateien, --out)"; UMGEBUNGSFEHLER=$((UMGEBUNGSFEHLER + 1)) ;;
        6)  erwartet_falsch "$dat" || meldung="rc=6  Test falsch" ;;
        8)  meldung="rc=8  Laufzeitfehler (Stub, Gerät nicht nutzbar, Abbruch)" ;;
        16) meldung="rc=16 Vorab-Prüfung fehlgeschlagen (Test nicht gestartet)" ;;
        *)  meldung="rc=$rc  unbekannter Rückkehrcode" ;;
    esac
    if [ -n "$meldung" ]; then
        ABWEICHUNGEN=$((ABWEICHUNGEN + 1))
        echo "$dat: $meldung"
        tail -n $([ "$rc" -eq 2 ] && echo 1 || echo 3) "$aus" | cut -c1-200 | sed 's/^/    | /'
    fi
    rm -f "$aus"
    if [ "$UMGEBUNGSFEHLER" -ge 3 ]; then
        echo "compute_all_tests: ABBRUCH nach $ANZAHL Läufen - 3 Umgebungs- oder Aufruffehler (rc 1/2); Ursache beheben (LC_ALL? Zip vollständig?)."
        exit 3
    fi
}

for dat in Tests/*.txt; do
    # Soll-Dateien der Dateiprüfungen sind keine Tests
    # st-005 setzt einen bestimmten Trommelinhalt voraus (Zelle 0001); er läuft unten mit seinen Vorbedingungen
    case "$dat" in *-ausgabe.txt|*_erwartet.txt|Tests/st-005_*.txt) continue;; esac
    lauf "$dat"
done

# Tests des BIS-Minimalprogramms v6 (Tests/pj2-bis_v6_*.test): jeder Test traegt das Abbild des Minimalprogramms selbst
# und setzt #TROMMEL=LEER; erzeugt von testscripte/erzeuge_v6_randfaelle.py (Randfaelle) bzw. von Hand (Programmstueck)
for dat in Tests/pj2-bis_v6_*.test; do
    lauf "$dat" </dev/null
done

# Tests mit Voraussetzung auf der Trommel: Die Trommel behält ihren Inhalt von Test zu Test, im Lauf über alle Tests
# stünde in Zelle 0001 sonst, was der vorige Test dort hinterlassen hat.
#  - st-005:  Druckroutine aus Tests/asm_druck_tastenfolge.txt (Zelle 0001 = Sprung zum Druck von BZ und AC)
python3 "$HIER/erzeuge_leere_trommel.py"
lauf Tests/asm_druck_tastenfolge.txt
lauf Tests/st-005_STARTE_1000_druck_mit_druckroutine.txt

python3 "$HIER/erzeuge_leere_trommel.py"

# Zusatzlauf: derselbe Test mit einem zweiten Streifen (der Schalter überstimmt die Zeile --leser1 der Testdatei;
# das Protokoll des Tests wird dabei überschrieben)
lauf Tests/lb-003_Paritaetsfehler.txt --leser1 $L1/lb-003_irrung_zeichen_dann_paritaetsfehler.txt

echo "compute_all_tests: $ANZAHL Laeufe, $ABWEICHUNGEN Abweichungen"
[ "$ABWEICHUNGEN" -eq 0 ]
