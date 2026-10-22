#!/bin/bash
# Version 1.00-030
# Regressionstest fuer den C8205-Assembler c82ass.
#
#   Regressionstest/regressionstest.sh                  prueft alle .asm gegen die Referenz (normaler Lauf und Lauf mit --ABSPR)
#                                                       und fuehrt die Negativtests aus
#   Regressionstest/regressionstest.sh --referenz       schreibt die Referenz neu (nach bewusster Aenderung des Assemblers)
#   Regressionstest/regressionstest.sh --binary PFAD    anderes Binary als _Linux/c82ass pruefen
#   Regressionstest/regressionstest.sh Projekt_1 ...    nur die genannten Verzeichnisse (relativ zu Assembler)
#   Option -v: Unterschiede im Wortlaut anzeigen
#
# Rueckgabe: 0 = alles gleich, 1 = Abweichung oder fehlgeschlagener Negativtest, 2 = Aufruffehler.
# Gearbeitet wird in einem temporaeren Verzeichnis; im Projekt entstehen keine Dateien
# (auch keine projekdetails).

HIER=$(cd "$(dirname "$0")" && pwd)
ASM=$(cd "$HIER/.." && pwd)
BIN="$ASM/_Linux/c82ass"
REFERENZ="$HIER/referenz"
NEGATIV="$HIER/negativ"
MODUS=pruefen
VERBOSE=0
VERZ=()
ENDUNGEN="obj mqo sym dmp test log rc"
ENDUNGEN_KEP="kep rck"      # Lauf mit --ABSPR: Lochstreifen .kep und Rueckgabecode (.rck); die uebrigen Dateien des Laufs entsprechen dem normalen Lauf und werden nicht doppelt verglichen

while [ $# -gt 0 ]; do
    case "$1" in
        --referenz) MODUS=referenz ;;
        --binary)   shift; BIN=$(cd "$(dirname "$1")" 2>/dev/null && pwd)/$(basename "$1") ;;
        -v)         VERBOSE=1 ;;
        -h|--help)  sed -n '2,13p' "$0"; exit 0 ;;
        -*)         echo "Unbekannte Option: $1" >&2; exit 2 ;;
        *)          VERZ+=("$1") ;;
    esac
    shift
done

if [ ! -x "$BIN" ]; then
    echo "Assembler-Binary nicht gefunden: $BIN (zuerst make_c82ass.sh ausfuehren)" >&2
    exit 2
fi

TMP=$(mktemp -d) || exit 2
trap 'rm -rf "$TMP"' EXIT
MAKROS="$ASM/c82ass.makros"; [ -f "$MAKROS" ] || MAKROS="$ASM/Sourcecode/c82ass.makros"
cp "$MAKROS" "$TMP/" 2>/dev/null

# ---------------------------------------------------------------- Teil 1: Programme gegen Referenz
if [ ${#VERZ[@]} -eq 0 ]; then VERZ=("."); fi
LISTE=$(cd "$ASM" && find "${VERZ[@]}" -name '*.asm' \
          -not -path './Regressionstest/*' -not -path 'Regressionstest/*' \
          -not -path '*/Sourcecode/*' -not -path '*/Dokumentation/*' | sed 's#^\./##' | sort)

anzahl=0; abweich=0; neu=0
for rel in $LISTE; do
    dir=$(dirname "$rel"); base=$(basename "$rel" .asm)
    mkdir -p "$TMP/w/$dir"
    cp "$ASM/$rel" "$TMP/w/$dir/"
    ( cd "$TMP" && "$BIN" --no-color -p "w/$dir" -s "$base" >/dev/null 2>&1; echo $? > "w/$dir/$base.rc" )
    # zweiter Lauf mit --ABSPR in eigenem Arbeitsverzeichnis (erzeugt .kep statt .obj)
    mkdir -p "$TMP/k/$dir"
    cp "$ASM/$rel" "$TMP/k/$dir/"
    ( cd "$TMP" && "$BIN" --no-color --ABSPR -p "k/$dir" -s "$base" >/dev/null 2>&1; echo $? > "k/$dir/$base.rck" )
    anzahl=$((anzahl+1))
    if [ "$MODUS" = referenz ]; then
        mkdir -p "$REFERENZ/$dir"
        for e in $ENDUNGEN; do
            rm -f "$REFERENZ/$dir/$base.$e"
            [ -f "$TMP/w/$dir/$base.$e" ] && cp "$TMP/w/$dir/$base.$e" "$REFERENZ/$dir/$base.$e"
        done
        for e in $ENDUNGEN_KEP; do
            rm -f "$REFERENZ/$dir/$base.$e"
            [ -f "$TMP/k/$dir/$base.$e" ] && cp "$TMP/k/$dir/$base.$e" "$REFERENZ/$dir/$base.$e"
        done
        continue
    fi
    if [ ! -d "$REFERENZ/$dir" ] || ! ls "$REFERENZ/$dir/$base."* >/dev/null 2>&1; then
        echo "NEU       $rel (keine Referenz; --referenz ausfuehren)"; neu=$((neu+1)); continue
    fi
    fehler=0
    for e in $ENDUNGEN; do
        a="$REFERENZ/$dir/$base.$e"; b="$TMP/w/$dir/$base.$e"
        if [ -f "$a" ] && [ ! -f "$b" ]; then echo "ABWEICHUNG $rel: .$e fehlt"; fehler=1
        elif [ ! -f "$a" ] && [ -f "$b" ]; then echo "ABWEICHUNG $rel: .$e unerwartet erzeugt"; fehler=1
        elif [ -f "$a" ] && ! cmp -s "$a" "$b"; then
            echo "ABWEICHUNG $rel: .$e unterscheidet sich"; fehler=1
            [ $VERBOSE = 1 ] && diff "$a" "$b" | head -10
        fi
    done
    for e in $ENDUNGEN_KEP; do
        a="$REFERENZ/$dir/$base.$e"; b="$TMP/k/$dir/$base.$e"
        if [ -f "$a" ] && [ ! -f "$b" ]; then echo "ABWEICHUNG $rel: .$e (--ABSPR) fehlt"; fehler=1
        elif [ ! -f "$a" ] && [ -f "$b" ]; then echo "ABWEICHUNG $rel: .$e (--ABSPR) unerwartet erzeugt (oder keine Referenz; --referenz ausfuehren)"; fehler=1
        elif [ -f "$a" ] && ! cmp -s "$a" "$b"; then
            echo "ABWEICHUNG $rel: .$e (--ABSPR) unterscheidet sich"; fehler=1
            [ $VERBOSE = 1 ] && diff "$a" "$b" | head -10
        fi
    done
    abweich=$((abweich+fehler))
done

if [ "$MODUS" = referenz ]; then
    echo "Referenz geschrieben fuer $anzahl Programme nach $REFERENZ"
    # Referenzdateien fuer entfernte Programme aufraeumen
    ( cd "$REFERENZ" && for f in $(find . -name '*.rc' | sed 's#^\./##;s#\.rc$##'); do
          [ -f "$ASM/$f.asm" ] || { echo "entferne veraltete Referenz $f"; rm -f "$f".*; }
      done )
    exit 0
fi

# ---------------------------------------------------------------- Teil 2: Negativtests
# Jeder Test: negativ/<name>.asm und negativ/<name>.erwartet. Zeilen der .erwartet-Datei:
#   args <...>            zusaetzliche Aufrufparameter (z. B. -m w/negativ/<name>.makros fuer eine Makrodatei <name>.makros)
#   ohne-p-s              kein -p/-s anhaengen (fuer -h, --version)
#   vorher-verz <name>    vor dem Lauf im Arbeitsverzeichnis ein Verzeichnis <name> anlegen (z. B. temp_projekdetails,
#                         damit die Temp-Datei nicht angelegt werden kann); wird nach dem Test wieder entfernt
#   vorher-datei <name> <text>   vor dem Lauf im Arbeitsverzeichnis die Datei <name> mit dieser einen Zeile anlegen
#                         (z. B. projekdetails); wird nach dem Test wieder entfernt
#   farbe auto|an|aus     Farbmodus (Vorgabe: aus = --no-color; auto = kein Schalter; an = --color)
#   rc <n>                erwarteter Rueckgabecode
#   stdout|stderr <text>  Text muss (als feste Zeichenkette) vorkommen
#   nicht-stdout|nicht-stderr <text>   Text darf nicht vorkommen
#   anzahl-stdout|anzahl-stderr <n> <text>   Text muss genau n-mal vorkommen
#   datei-da <endung>...  diese Ausgabedateien muessen existieren
#   datei-weg <endung>... diese Ausgabedateien duerfen nicht existieren
#   log-da <text>         Text muss (als feste Zeichenkette) in der .log-Datei stehen
#   log-weg <text>        Text darf nicht in der .log-Datei stehen
#   escape-da | escape-weg   ESC-Zeichen in STDOUT/STDERR vorhanden bzw. nicht vorhanden
neg=0; negfehl=0
mkdir -p "$TMP/w/negativ"
for erw in "$NEGATIV"/*.erwartet; do
    [ -f "$erw" ] || continue
    name=$(basename "$erw" .erwartet)
    neg=$((neg+1))
    rm -f "$TMP/w/negativ/$name".*
    cp "$NEGATIV/$name.asm" "$TMP/w/negativ/" 2>/dev/null
    cp "$NEGATIV/$name.makros" "$TMP/w/negativ/" 2>/dev/null   # eigene Makrodatei zum Test (mit "args -m w/negativ/<name>.makros")
    args=""; ps=1; farbe=aus; vorher=()
    while read -r k rest; do
        case "$k" in
            args) args="$rest" ;;
            ohne-p-s) ps=0 ;;
            farbe) farbe="$rest" ;;
            vorher-verz)  mkdir -p "$TMP/$rest"; vorher+=("$TMP/$rest") ;;
            vorher-datei) vn=${rest%% *}; vt=${rest#* }; printf '%s\n' "$vt" > "$TMP/$vn"; vorher+=("$TMP/$vn") ;;
        esac
    done < "$erw"
    farbopt="--no-color"; [ "$farbe" = an ] && farbopt="--color"; [ "$farbe" = auto ] && farbopt=""
    psopt=""; [ $ps = 1 ] && psopt="-p w/negativ -s $name"
    ( cd "$TMP" && "$BIN" $farbopt $args $psopt >"w/negativ/$name.stdout" 2>"w/negativ/$name.stderr"; echo $? > "w/negativ/$name.rc" )
    for v in "${vorher[@]}"; do rm -rf "$v"; done
    meld=""
    ist_rc=$(cat "$TMP/w/negativ/$name.rc")
    zaehle() { grep -aF -- "$2" "$TMP/w/negativ/$name.$1" | wc -l; }
    while read -r k a b; do
        rest="$a${b:+ $b}"
        case "$k" in
            rc)            [ "$ist_rc" = "$a" ] || meld="$meld rc=$ist_rc statt $a;" ;;
            stdout|stderr) [ "$(zaehle $k "$rest")" -ge 1 ] || meld="$meld '$rest' fehlt in $k;" ;;
            nicht-stdout)  [ "$(zaehle stdout "$rest")" -eq 0 ] || meld="$meld '$rest' unerwartet in stdout;" ;;
            nicht-stderr)  [ "$(zaehle stderr "$rest")" -eq 0 ] || meld="$meld '$rest' unerwartet in stderr;" ;;
            anzahl-stdout|anzahl-stderr)
                n=$(zaehle "${k#anzahl-}" "$b"); [ "$n" -eq "$a" ] || meld="$meld '$b' kommt ${n}x vor statt ${a}x in ${k#anzahl-};" ;;
            datei-da)  for e in $a $b; do [ -f "$TMP/w/negativ/$name.$e" ] || meld="$meld .$e fehlt;"; done ;;
            datei-weg) for e in $a $b; do [ ! -f "$TMP/w/negativ/$name.$e" ] || meld="$meld .$e unerwartet vorhanden;"; done ;;
            log-da)   grep -aqF -- "$rest" "$TMP/w/negativ/$name.log" 2>/dev/null || meld="$meld '$rest' fehlt in .log;" ;;
            log-weg)  grep -aqF -- "$rest" "$TMP/w/negativ/$name.log" 2>/dev/null && meld="$meld '$rest' unerwartet in .log;" ;;
            escape-da)  cat "$TMP/w/negativ/$name.stdout" "$TMP/w/negativ/$name.stderr" | grep -aq $'\033' || meld="$meld kein ESC-Zeichen;" ;;
            escape-weg) cat "$TMP/w/negativ/$name.stdout" "$TMP/w/negativ/$name.stderr" | grep -aq $'\033' && meld="$meld ESC-Zeichen vorhanden;" ;;
        esac
    done < "$erw"
    if [ -n "$meld" ]; then echo "NEGATIVTEST $name:$meld"; negfehl=$((negfehl+1)); fi
done

echo "----"
echo "Programme: $anzahl geprueft, $abweich mit Abweichung, $neu ohne Referenz"
echo "Negativtests: $neg ausgefuehrt, $negfehl fehlgeschlagen"
[ $abweich -eq 0 ] && [ $negfehl -eq 0 ] && [ $neu -eq 0 ] && { echo "ALLES GLEICH"; exit 0; }
exit 1
