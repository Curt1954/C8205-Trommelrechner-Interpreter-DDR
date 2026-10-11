#!/bin/bash
# Aufruf: ./c8205_interpreter.sh [Schalter ...] TESTDATEI [Schalter ...]
# Beispiel: ./c8205_interpreter.sh --NO-TERMOUT Tests/x.txt --knotentest
#           ./c8205_interpreter.sh Tests/x.txt --leser1 virtuelle_Geraete/Leser1
# Die Testdatei darf an beliebiger Stelle stehen; Schalter mit eigenem
# Wertargument (z. B. "--out DATEI") werden dabei erkannt, damit ihr Wert
# nicht versehentlich als Testdatei gilt.

# Schalter des Interpreters, die ein eigenes Wertargument mitnehmen:
ist_wertschalter() {
    case "$1" in
        --mdverz|--leser1|--lochbandleser1|--leser2|--lochbandleser2|--stanzer1|--lochbandstanzer1|--sw-ausgabe|--k0|--out|--pruefe-stanzer1|--pruefe-sw-ausgabe|--zwischenablage)
            return 0 ;;
        *)
            return 1 ;;
    esac
}

file=""
rest=()
wert_folgt=0
for a in "$@"; do
    if [ "$wert_folgt" = 1 ]; then
        rest+=("$a")
        wert_folgt=0
        continue
    fi
    case "$a" in
        -*)
            rest+=("$a")
            if ist_wertschalter "$a"; then
                wert_folgt=1
            fi
            ;;
        *)
            if [ -z "$file" ]; then
                file="$a"              # erste Testdatei: bestimmt den Protokollnamen
            else
                rest+=("$a")           # weitere Testdateien (der Interpreter erlaubt mehrere)
            fi
            ;;
    esac
done

if [ -z "$file" ]; then
    echo "Test-Datei fehlt."
    exit 1
fi

# Dateiname ohne Pfad, Endung durch .log ersetzen
prot_file="$(basename "$file")"
prot_file="${prot_file%.*}.log"

# Vorgaben zuerst, dann die vom Benutzer übergebenen Schalter; bei doppelter
# Angabe (z. B. --out, --mdverz) gilt der später genannte, also der vom Benutzer.
python3 c8205_interp.py --mdverz ./markdown-dateien --out "Test-Protokolle/$prot_file" "$file" "${rest[@]}"
