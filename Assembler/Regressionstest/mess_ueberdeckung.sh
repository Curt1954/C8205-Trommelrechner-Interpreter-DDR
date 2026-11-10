#!/bin/bash
# Version 1.00-069
# Regressionstest fuer den C8205-Assembler c82ass.
#
#   Regressionstest/regressionstest.sh                  prueft alle .asm gegen die Referenz (normaler Lauf, Lauf mit --ABSPR und Lauf mit --no-opt)
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
REFNOOPT="$HIER/referenz_noopt"   # nur Programme, die ohne Optimierer anders assembliert werden
NEGATIV="$HIER/negativ"
MODUS=pruefen
MESSDIR=${MESSDIR:-/home/claude/w/cov/data}
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
mkdir -p "$TMP/N"; cp "$MAKROS" "$TMP/N/" 2>/dev/null
OPSYMTAB="$ASM/c82ass.opsym"; [ -f "$OPSYMTAB" ] || OPSYMTAB="$ASM/Sourcecode/c82ass.opsym"   # Standardtabelle der Operationscode-Namen (OPSYM)
cp "$OPSYMTAB" "$TMP/" 2>/dev/null; cp "$OPSYMTAB" "$TMP/N/" 2>/dev/null

# ---------------------------------------------------------------- Teil 1: Programme gegen Referenz
if [ ${#VERZ[@]} -eq 0 ]; then VERZ=("."); fi
LISTE=$(cd "$ASM" && find "${VERZ[@]}" -name '*.asm' \
          -not -path './Regressionstest/*' -not -path 'Regressionstest/*' \
          -not -path '*/Sourcecode/*' -not -path '*/Dokumentation/*' | sed 's#^\./##' | sort)

# Projektspezifische Makrodateien (*.macro, dazu *.inc fuer $INCLUDE, Anweisung ;#MACRODATEIn=) und Namensdateien (*.opsym, ;#OPSYM=): alle *.macro und *.opsym des Baums mit gleichem Pfad in die drei Arbeitsbaeume kopieren
# (die Makrodatei liegt oft ausserhalb des Programmordners, z. B. Claude/macro_zt_loader.macro fuer Claude/typ10eingabe)
( cd "$ASM" && find . \( -name '*.macro' -o -name '*.inc' -o -name '*.opsym' \) -not -path './Regressionstest/*' -not -path './Sourcecode/*' ) | sed 's#^\./##' | while read -r mf; do
    for wb in w k N/w; do mkdir -p "$TMP/$wb/$(dirname "$mf")"; cp "$ASM/$mf" "$TMP/$wb/$mf"; done
done

anzahl=0; abweich=0; neu=0
for rel in $LISTE; do
    dir=$(dirname "$rel"); base=$(basename "$rel" .asm)
    export GCOV_PREFIX="$MESSDIR/prog_$(echo "$rel" | tr '/' '_')" GCOV_PREFIX_STRIP=0
    mkdir -p "$TMP/w/$dir"
    cp "$ASM/$rel" "$TMP/w/$dir/"
    ( cd "$TMP" && "$BIN" --no-color -p "w/$dir" -s "$base" >/dev/null 2>&1; echo $? > "w/$dir/$base.rc" )
    # zweiter Lauf mit --ABSPR in eigenem Arbeitsverzeichnis (erzeugt .kep statt .obj)
    mkdir -p "$TMP/k/$dir"
    cp "$ASM/$rel" "$TMP/k/$dir/"
    ( cd "$TMP" && "$BIN" --no-color --ABSPR -p "k/$dir" -s "$base" >/dev/null 2>&1; echo $? > "k/$dir/$base.rck" )
    # dritter Lauf mit --no-opt (Optimierer aus) in eigenem Arbeitsverzeichnis N (gleiche Pfade wie im normalen Lauf)
    mkdir -p "$TMP/N/w/$dir"
    cp "$ASM/$rel" "$TMP/N/w/$dir/"
    ( cd "$TMP/N" && "$BIN" --no-color --no-opt -p "w/$dir" -s "$base" >/dev/null 2>&1; echo $? > "w/$dir/$base.rc" )
    anzahl=$((anzahl+1))
    if [ "$MODUS" = referenz ]; then
        # referenz_noopt/ enthaelt nur Programme, deren Ergebnis ohne Optimierer vom normalen Lauf abweicht
        rm -f "$REFNOOPT/$dir/$base."*
        abw=0
        for e in $ENDUNGEN; do
            x="$TMP/w/$dir/$base.$e"; y="$TMP/N/w/$dir/$base.$e"
            if { [ -f "$x" ] && [ ! -f "$y" ]; } || { [ ! -f "$x" ] && [ -f "$y" ]; } || { [ -f "$x" ] && ! cmp -s "$x" "$y"; }; then abw=1; fi
        done
        if [ $abw = 1 ]; then
            mkdir -p "$REFNOOPT/$dir"
            for e in $ENDUNGEN; do [ -f "$TMP/N/w/$dir/$base.$e" ] && cp "$TMP/N/w/$dir/$base.$e" "$REFNOOPT/$dir/$base.$e"; done
        fi
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
    # Lauf mit --no-opt: gegen referenz_noopt/ (falls das Programm dort steht), sonst gegen referenz/
    rd="$REFERENZ/$dir"; [ -f "$REFNOOPT/$dir/$base.rc" ] && rd="$REFNOOPT/$dir"
    for e in $ENDUNGEN; do
        a="$rd/$base.$e"; b="$TMP/N/w/$dir/$base.$e"
        if [ -f "$a" ] && [ ! -f "$b" ]; then echo "ABWEICHUNG $rel: .$e (--no-opt) fehlt"; fehler=1
        elif [ ! -f "$a" ] && [ -f "$b" ]; then echo "ABWEICHUNG $rel: .$e (--no-opt) unerwartet erzeugt"; fehler=1
        elif [ -f "$a" ] && ! cmp -s "$a" "$b"; then
            echo "ABWEICHUNG $rel: .$e (--no-opt) unterscheidet sich"; fehler=1
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
    [ -d "$REFNOOPT" ] && ( cd "$REFNOOPT" && for f in $(find . -name '*.rc' | sed 's#^\./##;s#\.rc$##'); do
          [ -f "$ASM/$f.asm" ] || { echo "entferne veraltete Referenz (--no-opt) $f"; rm -f "$f".*; }
      done )
    exit 0
fi

# ---------------------------------------------------------------- Teil 2: Negativtests
# Jeder Test: negativ/<name>.asm und negativ/<name>.erwartet. Zeilen der .erwartet-Datei:
#   (Makrodateien <name>_1.macro, <name>_2.macro ... neben dem Test werden fuer ;#MACRODATEIn= in w/negativ bereitgestellt)
#   args <...>            zusaetzliche Aufrufparameter (z. B. -m w/negativ/<name>.makros fuer eine Makrodatei <name>.makros)
#   ohne-p-s              kein -p/-s anhaengen (fuer -h, --version)
#   vorher-verz <name>    vor dem Lauf im Arbeitsverzeichnis ein Verzeichnis <name> anlegen (z. B. temp_projekdetails,
#                         damit die Temp-Datei nicht angelegt werden kann); wird nach dem Test wieder entfernt
#   (Namensdateien <name>_1.opsym, <name>_2.opsym ... neben dem Test werden fuer ;#OPSYM= in w/negativ bereitgestellt)
#   (Include-Dateien <name>_1.inc, <name>_2.inc ... neben dem Test werden fuer $INCLUDE im Quelltext in w/negativ bereitgestellt)
#   vorher-weg <name>     vor dem Lauf im Arbeitsverzeichnis die Datei <name> entfernen (z. B. c82ass.opsym); wird danach wieder angelegt
#   binary-mit-tabelle    Programm aus <Temp>/prog/_Linux/c82ass starten, die Standardtabelle liegt nur in <Temp>/prog/Sourcecode/ (Suche neben dem
#                         Programm, ab 1.00-066). Ohne diese Zeile laeuft eine Kopie des Binarys in <Temp>/bin/ ohne Tabelle daneben, damit
#                         ein Negativtest nicht die Tabelle neben dem echten Binary findet.
#   vorher-datei <name> <text>   vor dem Lauf im Arbeitsverzeichnis die Datei <name> mit dieser einen Zeile anlegen
#                         (z. B. projekdetails); wird nach dem Test wieder entfernt
#   farbe auto|an|aus     Farbmodus (Vorgabe: aus = --no-color; auto = kein Schalter; an = --color)
#   rc <n>                erwarteter Rueckgabecode
#   stdout|stderr <text>  Text muss (als feste Zeichenkette) vorkommen
#   nicht-stdout|nicht-stderr <text>   Text darf nicht vorkommen
#   anzahl-stdout|anzahl-stderr <n> <text>   Text muss genau n-mal vorkommen
#   stderr-reihe <text>   Text muss in STDERR vorkommen, und zwar in einer Zeile hinter der Zeile des vorigen stderr-reihe dieses Tests
#                         (die erste Zeile dieser Art darf irgendwo stehen); prueft die Reihenfolge der Ausgabe
#   stderr-einrueckung <n> <text>   eine Zeile von STDERR muss genau aus n Leerzeichen und dem Text bestehen (ganze Zeile);
#                         prueft die Einrueckung der Spurzeilen (bei stderr <text> geht fuehrender Leerraum beim Einlesen verloren)
#   datei-da <endung>...  diese Ausgabedateien muessen existieren
#   datei-weg <endung>... diese Ausgabedateien duerfen nicht existieren
#   log-da <text>         Text muss (als feste Zeichenkette) in der .log-Datei stehen
#   log-weg <text>        Text darf nicht in der .log-Datei stehen
#   dmp-da <text>         Text muss (als feste Zeichenkette) in der .dmp-Datei stehen
#   dmp-weg <text>        Text darf nicht in der .dmp-Datei stehen
#   escape-da | escape-weg   ESC-Zeichen in STDOUT/STDERR vorhanden bzw. nicht vorhanden
neg=0; negfehl=0
mkdir -p "$TMP/w/negativ" "$TMP/bin" "$TMP/prog/_Linux" "$TMP/prog/Sourcecode"
cp "$BIN" "$TMP/bin/c82ass"; cp "$BIN" "$TMP/prog/_Linux/c82ass"; cp "$OPSYMTAB" "$TMP/prog/Sourcecode/" 2>/dev/null
for erw in "$NEGATIV"/*.erwartet; do
    [ -f "$erw" ] || continue
    name=$(basename "$erw" .erwartet)
    export GCOV_PREFIX="$MESSDIR/neg_$name" GCOV_PREFIX_STRIP=0
    neg=$((neg+1))
    rm -f "$TMP/w/negativ/$name".*
    cp "$NEGATIV/$name.asm" "$TMP/w/negativ/" 2>/dev/null
    cp "$NEGATIV/$name.makros" "$TMP/w/negativ/" 2>/dev/null   # eigene Makrodatei zum Test (mit "args -m w/negativ/<name>.makros")
    cp "$NEGATIV/$name"_*.macro "$TMP/w/negativ/" 2>/dev/null     # projektspezifische Makrodateien zum Test (im .asm: ;#MACRODATEI1=<name>_1.macro)
    cp "$NEGATIV/$name"_*.opsym "$TMP/w/negativ/" 2>/dev/null     # Namensdateien zum Test (im .asm: ;#OPSYM=<name>_1.opsym)
    cp "$NEGATIV/$name"_*.inc "$TMP/w/negativ/" 2>/dev/null       # Include-Dateien zum Test ($INCLUDE <name>_1.inc im Quelltext, c82ass ab 1.01-009)
    args=""; ps=1; farbe=aus; vorher=(); wieder=(); binlauf="$TMP/bin/c82ass"
    while read -r k rest; do
        case "$k" in
            args) args="$rest" ;;
            ohne-p-s) ps=0 ;;
            binary-mit-tabelle) binlauf="$TMP/prog/_Linux/c82ass" ;;
            farbe) farbe="$rest" ;;
            vorher-verz)  mkdir -p "$TMP/$rest"; vorher+=("$TMP/$rest") ;;
            vorher-weg)   rm -f "$TMP/$rest"; wieder+=("$rest") ;;
            vorher-datei) vn=${rest%% *}; vt=${rest#* }; printf '%s\n' "$vt" > "$TMP/$vn"; vorher+=("$TMP/$vn") ;;
        esac
    done < "$erw"
    farbopt="--no-color"; [ "$farbe" = an ] && farbopt="--color"; [ "$farbe" = auto ] && farbopt=""
    psopt=""; [ $ps = 1 ] && psopt="-p w/negativ -s $name"
    ( cd "$TMP" && "$binlauf" $farbopt $args $psopt >"w/negativ/$name.stdout" 2>"w/negativ/$name.stderr"; echo $? > "w/negativ/$name.rc" )
    for v in "${vorher[@]}"; do rm -rf "$v"; done
    for v in "${wieder[@]}"; do cp "$OPSYMTAB" "$TMP/$v" 2>/dev/null; done
    meld=""; reihepos=0
    ist_rc=$(cat "$TMP/w/negativ/$name.rc")
    zaehle() { grep -aF -- "$2" "$TMP/w/negativ/$name.$1" | wc -l; }
    while read -r k a b; do
        rest="$a${b:+ $b}"
        case "$k" in
            rc)            [ "$ist_rc" = "$a" ] || meld="$meld rc=$ist_rc statt $a;" ;;
            stdout|stderr) [ "$(zaehle $k "$rest")" -ge 1 ] || meld="$meld '$rest' fehlt in $k;" ;;
            stderr-reihe)  zl=$(grep -aFn -- "$rest" "$TMP/w/negativ/$name.stderr" | awk -F: -v ab="$reihepos" '$1 > ab { print $1; exit }')
                           if [ -n "$zl" ]; then reihepos=$zl; else meld="$meld '$rest' fehlt in stderr oder steht nicht hinter dem vorigen stderr-reihe;"; fi ;;
            stderr-einrueckung) ez=$(printf '%*s%s' "$a" '' "$b"); [ "$(grep -axF -- "$ez" "$TMP/w/negativ/$name.stderr" | wc -l)" -ge 1 ] || meld="$meld Zeile mit $a Leerzeichen Einrueckung '$b' fehlt in stderr;" ;;
            nicht-stdout)  [ "$(zaehle stdout "$rest")" -eq 0 ] || meld="$meld '$rest' unerwartet in stdout;" ;;
            nicht-stderr)  [ "$(zaehle stderr "$rest")" -eq 0 ] || meld="$meld '$rest' unerwartet in stderr;" ;;
            anzahl-stdout|anzahl-stderr)
                n=$(zaehle "${k#anzahl-}" "$b"); [ "$n" -eq "$a" ] || meld="$meld '$b' kommt ${n}x vor statt ${a}x in ${k#anzahl-};" ;;
            datei-da)  for e in $a $b; do [ -f "$TMP/w/negativ/$name.$e" ] || meld="$meld .$e fehlt;"; done ;;
            datei-weg) for e in $a $b; do [ ! -f "$TMP/w/negativ/$name.$e" ] || meld="$meld .$e unerwartet vorhanden;"; done ;;
            log-da)   grep -aqF -- "$rest" "$TMP/w/negativ/$name.log" 2>/dev/null || meld="$meld '$rest' fehlt in .log;" ;;
            log-weg)  grep -aqF -- "$rest" "$TMP/w/negativ/$name.log" 2>/dev/null && meld="$meld '$rest' unerwartet in .log;" ;;
            dmp-da)   grep -aqF -- "$rest" "$TMP/w/negativ/$name.dmp" 2>/dev/null || meld="$meld '$rest' fehlt in .dmp;" ;;
            dmp-weg)  grep -aqF -- "$rest" "$TMP/w/negativ/$name.dmp" 2>/dev/null && meld="$meld '$rest' unerwartet in .dmp;" ;;
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
