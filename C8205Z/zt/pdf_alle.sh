#!/bin/bash
# pdf_alle.sh -- erzeugt alle PDF des ZT-Repository neu und sammelt sie in C8205Z/zt.
#
# Aufruf (von ueberall):   bash C8205Z/zt/pdf_alle.sh [-b] [-h]
#   -b   zusaetzlich die Bilder neu zeichnen (grafik_quelle/zt_bild1.py und zt_bild3.py -> ZT-Trommelaufbau_1.png, _3.png),
#        BEVOR die md-PDF entstehen (Bild 2 hat keine Quelle und bleibt, wie es ist)
#   -h   diese Hilfe
#
# Was entsteht (alles in C8205Z/zt):
#   ZT-Repository_Aufgabenstellung.pdf   aus ZT-Repository_Aufgabenstellung.md   (md_layout.py, reportlab)
#   Zusatztrommel_Zeitmodell.pdf         aus Zusatztrommel_Zeitmodell.md         (md_layout.py, reportlab)
#   ZIL_Ablauf.pdf                       Flussdiagramm, 4 Seiten A3: ablauf_pdf.py im Ordner
#                                        Assembler/Projekt_ZT_LOADER/Unterprojekt_ZIL_Initialloader/zil/ablauf erzeugt es dort
#                                        (aus mk_dot.py und Graphviz) und wird hierher nach C8205Z/zt kopiert (die Kopie dort bleibt auch).
# NICHT neu erzeugbar: ZT-Trommelaufbau.pdf (Bild 1 und 2, mit matplotlib von Hand gebaut, kein Skript im Projekt); es bleibt unveraendert.
# Voraussetzung: python3 mit reportlab, Pillow, pypdf (und matplotlib fuer -b), Graphviz (dot), DejaVu-Schriften (/usr/share/fonts/truetype/dejavu).
# Rueckgabe: 0 alles erzeugt, 1 ein Schritt ist gescheitert (die uebrigen laufen trotzdem weiter), 2 Aufruf falsch oder Voraussetzung fehlt.

hier=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || exit 2
stamm=$(cd "$hier/../.." && pwd)
ablauf="$stamm/Assembler/Projekt_ZT_LOADER/Unterprojekt_ZIL_Initialloader/zil/ablauf"
bilder=0
case "$1" in
  -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  -b) bilder=1 ;;
  "") ;;
  *) echo "Unbekannte Option: $1 (Hilfe: -h)"; exit 2 ;;
esac

fehlt=0
for d in "$hier/md_layout.py" "$ablauf/ablauf_pdf.py" "$ablauf/mk_dot.py"; do
  [ -f "$d" ] || { echo "FEHLT: $d"; fehlt=1; }
done
command -v python3 >/dev/null || { echo "FEHLT: python3"; fehlt=1; }
command -v dot >/dev/null     || { echo "FEHLT: Graphviz (dot) fuer ZIL_Ablauf.pdf"; fehlt=1; }
python3 -c "import reportlab, PIL, pypdf" 2>/dev/null || { echo "FEHLT: Python-Pakete reportlab, Pillow und pypdf"; fehlt=1; }
[ $bilder = 1 ] && { python3 -c "import matplotlib" 2>/dev/null || { echo "FEHLT: matplotlib (fuer -b)"; fehlt=1; }; }
[ $fehlt = 0 ] || exit 2

rc=0
schritt() {   # schritt "Text" Befehl ...
  local text="$1"; shift
  if "$@" >/tmp/pdf_alle.$$ 2>&1; then echo "ok      $text"; else echo "FEHLER  $text"; sed 's/^/        /' /tmp/pdf_alle.$$; rc=1; fi
  rm -f /tmp/pdf_alle.$$
}

if [ $bilder = 1 ]; then
  schritt "Bild 1 (ZT-Trommelaufbau_1.png)" python3 "$hier/grafik_quelle/zt_bild1.py"
  schritt "Bild 3 (ZT-Trommelaufbau_3.png)" python3 "$hier/grafik_quelle/zt_bild3.py"
fi
schritt "ZT-Repository_Aufgabenstellung.pdf" python3 "$hier/md_layout.py" ZT-Repository_Aufgabenstellung.md
schritt "Zusatztrommel_Zeitmodell.pdf"       python3 "$hier/md_layout.py" Zusatztrommel_Zeitmodell.md
schritt "ZIL_Ablauf.pdf (mk_dot.py, dot, ablauf_pdf.py)" python3 "$ablauf/ablauf_pdf.py"
schritt "ZIL_Ablauf.pdf nach C8205Z/zt kopiert" cp "$ablauf/ZIL_Ablauf.pdf" "$hier/ZIL_Ablauf.pdf"

echo
echo "PDF in $hier:"
ls -l "$hier"/*.pdf | awk '{print "  " $6 " " $7 " " $8 "  " $5 "  " $9}' | sed "s#$hier/##"
exit $rc
