#!/bin/bash
# Baut das Minimalprogramm und seine Pruefprogramme, laedt sie auf die Trommel und startet den GRAFIK-Interpreter.
# Das Skript liegt in ./testscripte; gearbeitet wird im Projektverzeichnis (eine Ebene darueber).
#
# Aufruf:  testscripte/pj2-bis_minimalprogramm_test.sh [--NO_GRAFIK] [BASISNAME [AUSWAHL]]
#   --NO_GRAFIK  nach dem Laden wird der GRAFIK-Interpreter nicht gestartet (z. B. fuer Regressionstests); der Schalter
#                darf an beliebiger Stelle stehen
#   BASISNAME    Basisname des Minimalprogramms ohne .asm (Vorgabe: pj2-bis_minimalprogramm_v6)
#   AUSWAHL      optional (ohne Menue): Nummer oder Kurzname des zu ladenden Pruefprogramms, 0 = nur das Minimalprogramm
# Im Menue endet die Auswahl mit der ersten gueltigen Ziffer (oder dem Kurznamen); danach startet der GRAFIK-Interpreter.
#
# Pruefprogramme: Quelltext  BASISNAME_test_KURZNAME.asm  im Ordner Assembler/Projekt_2 (Ausnahme alle-druck-up: pj2-bis-minimalprogramm-alle-druck-up.asm,
# Hauptprogramm ab 02000, das Adressdruck, Befehlsdruck und Triadendruck nacheinander ausfuehrt; Ausgabe 4567 / 0765 432 / 0765 4321 065).
# Jedes Pruefprogramm liegt auf 02000 und wird im geladenen Minimalprogramm mit dem Sofortbefehl 000 2000 angesprungen
# (Eingabe K1 = 1, K2 = 0, Wort 00002000000:  1 0 0 0 0 0 2 0 0 0 0 0 0 .). Es endet mit einem unbedingten Stopp;
# was es erwartet und was es ausgibt, steht im Kopf seines Quelltextes. Beim Laden eines weiteren Pruefprogramms
# wird das vorige ueberschrieben (gleiche Adressen); das Minimalprogramm bleibt auf der Trommel.
#
# Neues Pruefprogramm aufnehmen: eine Zeile in die Liste "pruefprogramme" eintragen, Quelltext anlegen. Ist der Quelltext
# noch nicht vorhanden, erscheint der Eintrag im Menue als "(noch nicht vorhanden)" und wird nicht gebaut.
#
# Die Trommel wird nicht zurueckgesetzt (dazu vorher python3 testscripte/erzeuge_leere_trommel.py).

# Kurzname|Beschreibung[|Basisname des Quelltextes]  (Reihenfolge = Menuenummer)
# Ohne dritten Eintrag heisst der Quelltext BASISNAME_test_KURZNAME.asm; mit drittem Eintrag Assembler/Projekt_2/<Basisname>.asm.
pruefprogramme=(
  "druck|Druck: Triadendruck von vier Oktalzahlen auf SW"
  "adresse|Adresseneingabe"
  "wort|Eingabe eines Wortes mit Kennzeichen"
  "progst|Eingabe eines Programmstueckes"
  "alle-druck-up|Alle Druckunterprogramme nacheinander: Adressdruck, Befehlsdruck, Triadendruck|pj2-bis-minimalprogramm-alle-druck-up"
)

HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HIER/.." || exit 1

par1=""      # Basisname des Minimalprogramms
par_lv=""    # Auswahl des Pruefprogramms (optional)
no_grafik=0  # 1: GRAFIK-Interpreter nicht starten
for arg in "$@"; do
  case "$arg" in
    --NO_GRAFIK|--NO-GRAFIK) no_grafik=1 ;;
    *) if [ "$par1" = "" ]; then par1="$arg"; elif [ "$par_lv" = "" ]; then par_lv="$arg"; fi ;;
  esac
done

bn="pj2-bis_minimalprogramm_v6"
if [ "$par1" != "" ]; then
  bn="$par1"
fi

dir="Assembler/Projekt_2"

kurz()  { echo "${pruefprogramme[$1]%%|*}"; }
beschr(){ local r="${pruefprogramme[$1]#*|}"; echo "${r%%|*}"; }
# Basisname des Quelltextes: dritter Eintrag, sonst BASISNAME_test_KURZNAME
basis() { local r="${pruefprogramme[$1]#*|}"; if [ "$r" != "${r#*|}" ] && [ "${r#*|}" != "" ]; then echo "${r#*|}"; else echo "${bn}_test_$(kurz "$1")"; fi; }
quelle(){ echo "$dir/$(basis "$1").asm"; }
test_datei(){ echo "$dir/$(basis "$1").test"; }

# Prueft die Trommel nach dem Laden: Zahl der belegten Zellen und ob das Minimalprogramm (0262, 0040) noch darauf steht
trommel_pruefen() {
  python3 - "$1" <<'PY'
import sys
z = {}
for l in open('Trommel/trommel.txt', encoding='utf-8'):
    a, _, w = l.partition(':')
    z[a.strip()] = w.strip()
n = sum(1 for w in z.values() if w and set(w) != {'0'})
ok = all(z.get(a, '0') and set(z.get(a, '0')) != {'0'} for a in ('0001', '0040', '0262'))
print('Trommel nach %s: %d belegte Zellen, Minimalprogramm (0001, 0040, 0262) %s' % (sys.argv[1], n, 'vorhanden' if ok else 'FEHLT'))
sys.exit(0 if ok else 1)
PY
}

# Minimalprogramm und alle vorhandenen Pruefprogramme werden neu gebaut (Abbruch bei Assemblerfehlern)
( cd Assembler || exit 1
  ./c82ass.sh -p Projekt_2 -s "$bn".asm || exit 1
  for i in "${!pruefprogramme[@]}"; do
    q="$(quelle "$i")"
    if [ -f "../$q" ]; then
      ./c82ass.sh -p Projekt_2 -s "$(basis "$i")".asm || exit 1
    fi
  done
) || { echo "Assemblerlauf fehlgeschlagen"; exit 1; }

# Minimalprogramm auf die Trommel laden (Test nicht ausfuehren)

echo
echo "python3 c8205_interp.py --MODUS=TEST \"$dir/$bn\".test --LOADONLY"
python3 c8205_interp.py --MODUS=TEST "$dir/$bn".test --LOADONLY

echo "head -n 30 ./Trommel/trommel.txt"
head -n 30 ./Trommel/trommel.txt

trommel_pruefen "Minimalprogramm" || exit 1

# Auswahl (Nummer oder Kurzname) in einen Index umsetzen; Ergebnis in $idx (leer = ungueltig)
waehle() {
  idx=""
  local w="$1" i
  for i in "${!pruefprogramme[@]}"; do
    if [ "$w" = "$((i+1))" ] || [ "$w" = "$(kurz "$i")" ]; then idx="$i"; fi
  done
}

loop_var=1
while [ $loop_var -eq 1 ]; do
   if [ "$par_lv" != "" ]; then
      _frage="$par_lv"
      loop_var=0
   else
      echo
      for i in "${!pruefprogramme[@]}"; do
        hinweis=""
        [ -f "$(quelle "$i")" ] || hinweis="  (noch nicht vorhanden)"
        echo "$((i+1)) -- $(beschr "$i")$hinweis"
      done
      echo
      echo "Nummer oder Kurzname auswaehlen, 0 = Ende"
      read _frage
   fi
   if [ "$_frage" = "" ] || [ "$_frage" = "0" ]; then
      loop_var=0
      continue
   fi
   waehle "$_frage"
   if [ "$idx" = "" ]; then
      echo "Unbekannte Auswahl: $_frage"
      [ "$par_lv" != "" ] && exit 1
      continue
   fi
   if [ ! -f "$(quelle "$idx")" ]; then
      echo "Pruefprogramm $(kurz "$idx") ist noch nicht vorhanden: $(quelle "$idx")"
      [ "$par_lv" != "" ] && exit 1
      continue
   fi
   # Pruefprogramm zusaetzlich laden; das Minimalprogramm bleibt auf der Trommel
   python3 c8205_interp.py --MODUS=TEST "$(test_datei "$idx")" --LOADONLY
   trommel_pruefen "$(kurz "$idx")" || { echo "Das Minimalprogramm steht nicht mehr auf der Trommel (Marke #TROMMEL=LEER in $(test_datei "$idx")?)"; exit 1; }
   echo "$(beschr "$idx"): im Minimalprogramm den Sofortbefehl 000 2000 eingeben:  1 0 0 0 0 0 2 0 0 0 0 0 0 ."
   loop_var=0   # gueltige Auswahl: Schleife beenden, der GRAFIK-Interpreter startet
done

if [ $no_grafik -eq 1 ]; then
   echo "--NO_GRAFIK: GRAFIK-Interpreter wird nicht gestartet"
   exit 0
fi

./c8205_grafik.sh --HWCHECK
