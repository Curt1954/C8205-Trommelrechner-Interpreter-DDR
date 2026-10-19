#!/bin/sh
# Startet den C8205-Assembler (aus dem Verzeichnis Assembler aufrufen).
# Zusaetzlich zur Schreibweise des Assemblers (-WARN=SYM) wird --WARN=SYM akzeptiert
# und als -WARN=SYM durchgereicht. Alle anderen Argumente bleiben unveraendert.
for arg do
    shift
    case "$arg" in
        --[Ww][Aa][Rr][Nn]=*) set -- "$@" "${arg#-}" ;;
        *)                    set -- "$@" "$arg" ;;
    esac
done
./_Linux/c82ass "$@"
