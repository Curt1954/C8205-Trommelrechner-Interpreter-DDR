#!/bin/bash
# migrate_virtuelle_geraete.sh - Migration der Geraeteverzeichnisse (Schritt 1: Code, Tests, Skripte; OHNE Dokumentation)
#
# Aufruf (im Projektverzeichnis, dort wo c8205_interp.py liegt):
#     ./migrate_virtuelle_geraete.sh -n        Trockenlauf: zeigt nur, was geschehen wuerde (aendert nichts)
#     ./migrate_virtuelle_geraete.sh           Migration ausfuehren
#     ./migrate_virtuelle_geraete.sh -p DIR    Projektverzeichnis DIR statt des aktuellen
#
# Vorher:   virtuelle_Geraete/{Leser1,Leser1_02,Leser2,Stanzer1,SW-Ausgabe,T-SW-Eingabe,Trommel}
# Nachher:  Test-virtuelleGeraete/{Leser1,Leser1_02,Leser2,Stanzer1,SW-Ausgabe,T-SW-Eingabe}   (nur TEST-Interpreter)
#           virtuelle_Geraete/{Leser1,Leser2,Stanzer1}                                          (neu, leer; nur GRAFIK)
#           Trommel/{trommel.txt,trommel.basp,trommel_r300_eingabe.txt}                         (gemeinsam, beide Interpreter)
#
# Was angepasst wird:
#   Tests/*                       alle Pfade virtuelle_Geraete/ -> Test-virtuelleGeraete/   (alle Tests laufen nur mit --MODUS=TEST)
#   Assembler/**                  Testaufruf-Hinweise in Kommentaren, ebenso
#   c8205_interp.py (TEST)        Standard fuer --trommel -> Trommel/trommel.txt; Trommelvorlagen -> Trommel/Trommelvorlagen
#   c8205_grafik.py (GRAFIK)      Standard fuer --trommel -> Trommel/trommel.txt; Leser1/Leser2/Stanzer1 bleiben in virtuelle_Geraete/
#   c8205_*.sh/.bat, c-module/trommel.h, testscripte/*    Pfade bzw. Kommentare
# NICHT angefasst: Dokumentation (markdown-dateien, CSV, PDF-Skripte, README) - das ist Schritt 2; Test-Protokolle/ (erzeugte Logs).
#
# Das Script bricht ab, wenn das Ziel schon existiert (kein doppeltes Ausfuehren). Mit git werden die Ordner per git mv verschoben.
# Danach: Pruefung aller Pfade der Testmakrozeilen und Liste der noch verbliebenen Fundstellen (Dokumentation).

set -u
TROCKEN=0
PROJ="."
while [ $# -gt 0 ]; do
    case "$1" in
        -n|--dry-run) TROCKEN=1 ;;
        -p) shift; PROJ="${1:-.}" ;;
        -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
        *) echo "unbekannter Schalter: $1" >&2; exit 2 ;;
    esac
    shift
done

cd "$PROJ" || { echo "FEHLER: Verzeichnis $PROJ nicht gefunden" >&2; exit 2; }
[ -f c8205_interp.py ] && [ -f c8205_grafik.py ] || { echo "FEHLER: hier ist nicht das Projektverzeichnis (c8205_interp.py/c8205_grafik.py fehlen)" >&2; exit 2; }
[ -d virtuelle_Geraete ]        || { echo "FEHLER: virtuelle_Geraete/ fehlt - schon migriert?" >&2; exit 2; }
[ -d virtuelle_Geraete/Trommel ] || { echo "FEHLER: virtuelle_Geraete/Trommel/ fehlt - schon migriert?" >&2; exit 2; }
[ ! -e Test-virtuelleGeraete ]  || { echo "FEHLER: Test-virtuelleGeraete/ existiert bereits - schon migriert?" >&2; exit 2; }
[ ! -e Trommel ]                || { echo "FEHLER: Trommel/ existiert bereits im Projektverzeichnis" >&2; exit 2; }


# Pruefung der Makrozeilen: gibt je fehlendem Pfad eine Zeile "Testdatei: Pfad" aus (Ausgabepfade: Elternordner reicht)
pruefe_makros() {
    local datei zeile pfad art p
    while IFS=: read -r datei zeile; do
        pfad=$(echo "$zeile" | sed -E 's/^--(leser1|leser2|stanzer1|sw-ausgabe|k0)[[:space:]]+(datei=)?//; s/[[:space:]]*#.*$//; s/[[:space:]]+$//')
        art=$(echo "$zeile" | sed -E 's/^--([a-z0-9-]+).*/\1/')
        [ -n "$pfad" ] || continue
        case "$art" in
            leser1|leser2|k0) [ -e "$pfad" ] || echo "$datei: $pfad" ;;
            *) p="${pfad%/}"; [ -d "$p" ] || [ -d "$(dirname "$p")" ] || echo "$datei: $pfad" ;;
        esac
    done < <(grep -HE '^--(leser1|leser2|stanzer1|sw-ausgabe|k0)[[:space:]]' Tests/* 2>/dev/null)
}
BASIS=$(mktemp); pruefe_makros | sed -E 's/: .*//' | sort -u > "$BASIS"   # Altlasten: Testdateien, deren Pfade schon VOR der Migration nicht stimmten

GIT=0
if [ -e .git ] && command -v git >/dev/null 2>&1; then GIT=1; fi
[ $TROCKEN = 1 ] && echo "=== TROCKENLAUF - es wird nichts veraendert ==="
echo "Projekt: $(pwd)    git: $([ $GIT = 1 ] && echo ja || echo nein)"

tu() {   # fuehrt aus oder zeigt nur an
    if [ $TROCKEN = 1 ]; then echo "   [Trockenlauf] $*"; else "$@" || { echo "FEHLER bei: $*" >&2; exit 1; }; fi
}
verschiebe() { if [ $GIT = 1 ]; then tu git mv "$1" "$2"; else tu mv "$1" "$2"; fi; }

# ---------------------------------------------------------------------------------------------------------------------
echo; echo "== 1. Verzeichnisse =="
echo " virtuelle_Geraete -> Test-virtuelleGeraete"
verschiebe virtuelle_Geraete Test-virtuelleGeraete
echo " Test-virtuelleGeraete/Trommel -> Trommel (gemeinsam)"
if [ $TROCKEN = 1 ]; then echo "   [Trockenlauf] mv Test-virtuelleGeraete/Trommel Trommel"; else verschiebe Test-virtuelleGeraete/Trommel Trommel; fi
echo " neu: virtuelle_Geraete/{Leser1,Leser2,Stanzer1} (leer, mit .gitkeep)"
for d in Leser1 Leser2 Stanzer1; do
    tu mkdir -p "virtuelle_Geraete/$d"
    tu touch "virtuelle_Geraete/$d/.gitkeep"
    [ $GIT = 1 ] && [ $TROCKEN = 0 ] && git add "virtuelle_Geraete/$d/.gitkeep" 2>/dev/null
done

# ---------------------------------------------------------------------------------------------------------------------
# sed-Ausdruecke (-E). Reihenfolge ist wichtig: erst Trommelvorlagen, dann Trommel, dann die Testordner.
E_TROMMEL=(
    -e "s#virtuelle_Geraete/Trommelvorlagen#Trommel/Trommelvorlagen#g"
    -e "s#'virtuelle_Geraete', 'Trommelvorlagen'#'Trommel', 'Trommelvorlagen'#g"
    -e "s#'virtuelle_Geraete', 'Trommel'#'Trommel'#g"
    -e "s#virtuelle_Geraete[/\\\\]Trommel#Trommel#g"
)
E_TESTORDNER=(
    -e "s#virtuelle_Geraete/(SW-Ausgabe|T-SW-Eingabe|Leser1_02)#Test-virtuelleGeraete/\\1#g"
    -e "s#'virtuelle_Geraete', '(SW-Ausgabe|T-SW-Eingabe|Leser1_02)'#'Test-virtuelleGeraete', '\\1'#g"
)
E_ALLES_TEST=(   # Dateien, die nur fuer den TEST-Interpreter gelten: jeder Geraetepfad wandert nach Test-virtuelleGeraete
    -e "s#virtuelle_Geraete([/\\\\])#Test-virtuelleGeraete\\1#g"
)
E_GLEICHWERTIGKEIT=(  # Vergleichsskript TEST gegen GRAFIK: der Arbeitsordner muss die Testgeraete unter dem Namen Test-virtuelleGeraete haben,
                      # weil die Tests (Makrozeilen) sie dort suchen - Quelle UND Ziel der Kopie sowie der Stanzer-Ersatz
    -e "s#'virtuelle_Geraete'#'Test-virtuelleGeraete'#g"
)

GEAENDERT=0
wende_an() {   # wende_an DATEI AUSDRUCK...
    local f="$1"; shift
    [ -f "$f" ] || return 0
    if ! LC_ALL=C sed -E "$@" "$f" | cmp -s - "$f"; then
        GEAENDERT=$((GEAENDERT + 1))
        if [ $TROCKEN = 1 ]; then echo "   [Trockenlauf] wuerde aendern: $f"; else LC_ALL=C sed -E -i "$@" "$f"; fi
    fi
}

echo; echo "== 2. Tests/* und Assembler/** (nur TEST-Interpreter) =="
n0=$GEAENDERT
for f in Tests/*; do wende_an "$f" "${E_ALLES_TEST[@]}"; done
while IFS= read -r f; do wende_an "$f" "${E_ALLES_TEST[@]}"; done < <(grep -rIl 'virtuelle_Geraete' Assembler 2>/dev/null)
echo " geaenderte Dateien: $((GEAENDERT - n0))"

echo; echo "== 3. Interpreter, Startskripte, Testscripte, C-Header =="
n0=$GEAENDERT
for f in c8205_interp.py c8205_grafik.py c8205_grafik.sh c8205_grafik.bat c-module/trommel.h testscripte/*; do
    wende_an "$f" "${E_TROMMEL[@]}" "${E_TESTORDNER[@]}"
done
# reine TEST-Dateien: alle Geraetepfade nach Test-virtuelleGeraete (Trommel zuerst, damit sie nicht mitgenommen wird)
for f in c8205_interpreter.sh c8205_interpreter.bat testscripte/compute_all_tests.sh; do
    wende_an "$f" "${E_TROMMEL[@]}" "${E_ALLES_TEST[@]}"
done
wende_an testscripte/grafik_gleichwertigkeit.py "${E_GLEICHWERTIGKEIT[@]}"
echo " geaenderte Dateien: $((GEAENDERT - n0))"

[ $TROCKEN = 1 ] && { echo; echo "Trockenlauf beendet ($GEAENDERT Dateien wuerden geaendert)."; exit 0; }

# ---------------------------------------------------------------------------------------------------------------------
echo; echo "== 4. Pruefung =="
FEHLER=0
# 4a) alle Pfade in den Makrozeilen der Tests muessen existieren; schon vorher fehlende sind nur ein Hinweis
NEUFEHLER=0; ALT=0
while IFS= read -r zeile; do
    t="${zeile%%: *}"
    if grep -qxF "$t" "$BASIS"; then echo " Hinweis (Altlast, fehlte schon vor der Migration): $zeile"; ALT=$((ALT+1))
    else echo " FEHLT durch die Migration: $zeile"; NEUFEHLER=$((NEUFEHLER+1)); fi
done < <(pruefe_makros)
FEHLER=$((FEHLER + NEUFEHLER))
echo " Makrozeilen der Tests geprueft: $NEUFEHLER neue Fehler, $ALT Altlasten"
rm -f "$BASIS"

# 4b) Trommel
for f in trommel.txt trommel.basp trommel_r300_eingabe.txt; do [ -f "Trommel/$f" ] || { echo " FEHLT: Trommel/$f"; FEHLER=$((FEHLER+1)); }; done
[ ! -e Test-virtuelleGeraete/Trommel ] || { echo " Test-virtuelleGeraete/Trommel existiert noch"; FEHLER=$((FEHLER+1)); }
echo " Trommel/: $(ls Trommel | tr '\n' ' ')"

# 4c) Python-Syntax der geaenderten .py-Dateien
if command -v python3 >/dev/null 2>&1; then
    for f in c8205_interp.py c8205_grafik.py testscripte/*.py; do
        PYTHONDONTWRITEBYTECODE=1 python3 -c "import ast,sys; ast.parse(open(sys.argv[1],encoding='utf-8').read())" "$f" 2>/dev/null \
            || { echo " SYNTAXFEHLER: $f"; FEHLER=$((FEHLER+1)); }
    done
    echo " Python-Syntax geprueft"
fi

echo; echo "== 5. Verbliebene Fundstellen 'virtuelle_Geraete' ausserhalb der Dokumentation (zur Durchsicht) =="
echo "   (erwartet: nur der GRAFIK-Standard Leser1/Leser2/Stanzer1 in c8205_grafik.py)"
grep -rIn 'virtuelle_Geraete' c8205_interp.py c8205_grafik.py c8205_*.sh c8205_*.bat c-module testscripte Tests Assembler Hilfsprogramme 2>/dev/null | cut -c1-200
echo
echo "== 6. Dokumentation (Schritt 2, bisher unveraendert): Fundstellen je Bereich =="
for d in markdown-dateien CSV PDF/pdf-layout-scripte "Bausteininterpretiersystem BIS" README.md README.en.md; do
    printf ' %-38s %s Zeilen\n' "$d" "$(grep -rIi 'virtuelle_Geraete' "$d" 2>/dev/null | wc -l)"
done

echo
if [ $FEHLER = 0 ]; then echo "Migration fertig, Pruefung ohne Fehler ($GEAENDERT Dateien geaendert)."; else echo "Migration fertig, ABER $FEHLER Pruefungsfehler - siehe oben."; fi
echo "Empfehlung: Testlauf (./testscripte/compute_all_tests.sh) und 'git status' / 'git diff --stat' ansehen."
exit $([ $FEHLER = 0 ] && echo 0 || echo 1)
