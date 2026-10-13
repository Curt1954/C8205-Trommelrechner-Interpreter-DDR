#!/bin/bash
# Aufruf: ./make_pdf.sh erzeuge_projektstruktur_pdf.py [weitere Schalter, z. B. --stand 12.10.2026]
cd "$(dirname "$0")" || exit 1

layout_script="$1"
if [ -z "$layout_script" ]; then
   echo "Layout-Script fehlt (z. B. erzeuge_projektstruktur_pdf.py)"
   exit 1
fi
shift

# Skript in irgendeinem Ordner pdf-layout-scripte suchen (PDF/, BIS, Assembler, CSV)
pfad=$(find . -path "*/pdf-layout-scripte/$layout_script" -print -quit)
if [ -z "$pfad" ]; then
   echo "Skript $layout_script nicht in einem Ordner pdf-layout-scripte gefunden"
   exit 1
fi

python3 "$pfad" "$@"

