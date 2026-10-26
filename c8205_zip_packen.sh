#!/bin/bash
# c8205_zip_packen.sh -- packt das Projektverzeichnis zu "C8205 Simulator V.M.P-NNN.zip"
# und zu der schlanken Variante "C8205 Simulator V.M.P-NNN Claude.zip".
# Aufruf (von überall):  ./c8205_zip_packen.sh [--gesamt | --claude] [--ohne-pruefung] [V.M.P]
#
# NNN ist eine eigene, fortlaufende, dreistellige Build-Nummer. Sie steht in der Versionierungs-MD
# markdown-dateien/C8205-Versionierung.md in der Zeile
#     **Letzter Build:** V.M.P-NNN
# (fehlt die Zeile, hängt das Skript sie am Dateiende an). Jeder Lauf zählt NNN um 1 hoch;
# bei einer neuen Gesamtversion V.M.P beginnt sie wieder bei 001. Beide Zips eines Laufs
# tragen dieselbe Nummer. Das Skript schreibt die neue Nummer in die MD, BEVOR gepackt wird,
# damit die MD im Zip zur Zip-Nummer passt. Bricht der Lauf ab, werden alle MD-Fassungen
# auf den alten Stand zurückgesetzt, ein fehlgeschlagener Lauf verbraucht also keine Nummer.
# Gibt es C8205-Versionierung.md in mehreren Ordnern (Dublettenprüfung!), werden alle Kopien
# gleichzeitig geändert und bleiben identisch.
#
# Ohne Schalter entstehen beide Fassungen in einem Lauf:
#   C8205 Simulator V.M.P-NNN.zip          Gesamt-Zip (alles)
#   C8205 Simulator V.M.P-NNN Claude.zip   schlanke Variante für KI-Sitzungen
# Mit --gesamt entsteht nur das Gesamt-Zip, mit --claude nur die schlanke Variante.
# Vor dem Packen prüft das Skript (1) ob alle Pfade in Backticks aus CLAUDE.md existieren und (2) ob
# gleichnamige .md-Dateien in verschiedenen Ordnern denselben Inhalt haben, und bricht bei Fehlern ab.
# Mit --ohne-pruefung werden beide Prüfungen übersprungen.
#
# Die schlanke Variante: Das Auflisten zeigt rund 40 % weniger Einträge.
# Es fehlen: PDFs und ihre Erzeugungsskripte (pdf-layout-scripte/), die Testtabelle
# (Testausfuehrungen/test_tabelle*; die Skripte dort bleiben drin), pult/, ton/,
# README.en.md, Test-Protokolle.zip, __pycache__ sowie die vom Assembler
# erzeugten Dateien .log .mqo .obj .sym unter Assembler/. Es bleiben .asm, .dmp und .test.
# virtuelle_Geraete/ bleibt drin (Standardpfade von Leser und Stanzer, nur wenige KB).
# Der GRAFIK-Interpreter läuft mit --ohne-fenster --STUMM auch ohne pult/ und ton/.
# Wer am GRAFIK-Fenster, am Pult oder an den Klängen arbeitet, nimmt das Gesamt-Zip.
# In beiden Fassungen steht CLAUDE.md als erster Eintrag (unzip -p <zip> CLAUDE.md liest sie).
#
# 1. Die Gesamtversion V.M.P wird aus der Release-Tabelle in
#    markdown-dateien/C8205-Versionierung.md (Abschnitt 11, Spalte "Gesamtversion")
#    gebildet: höchste Eintragung der Form `vV.M.P`. Ein Aufrufparameter V.M.P
#    überschreibt sie (z. B. wenn das Release noch nicht in der Tabelle steht).
# 2. Zuerst entstehen zwei Sub-Zips im Projektstamm:
#      Test-Protokolle.zip   <- Test-Protokolle/
#      Regressionstest.zip   <- Assembler/Regressionstest/   (Pfade im Zip: Assembler/Regressionstest/...,
#                                                              entpacken also im Projektstamm)
# 3. Das Gesamt-Zip enthält alles im Projektstamm (wie  zip -r name.zip * ),
#    aber nicht .git, nicht __pycache__, nicht Test-Protokolle/ und nicht Assembler/Regressionstest/
#    (dafür aber die beiden Sub-Zips) und nicht frühere Gesamt-Zips "C8205 Simulator *.zip".
# 4. Danach werden die beiden Sub-Zips im Projektstamm wieder entfernt; sie liegen im Gesamt-Zip.
set -u
cd "$(dirname "$0")" || exit 1

command -v zip >/dev/null || { echo "zip nicht gefunden"; exit 1; }

versionsdatei="markdown-dateien/C8205-Versionierung.md"
[ -f "$versionsdatei" ] || { echo "$versionsdatei fehlt"; exit 1; }

# Schalter: standardmäßig beide Fassungen
mache_gesamt=1
mache_claude=1
pruefen=1
while [ $# -ge 1 ]; do
   case "$1" in
      --claude) mache_gesamt=0; shift ;;
      --gesamt) mache_claude=0; shift ;;
      --ohne-pruefung) pruefen=0; shift ;;
      *) break ;;
   esac
done

if [ $# -ge 1 ]; then
   version="$1"
else
   version=$(sed -n '/^## 11\./,$p' "$versionsdatei" \
             | grep -oE '^\| `v[0-9]+\.[0-9]+\.[0-9]+`' \
             | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)
   [ -n "$version" ] || { echo "Keine Gesamtversion in $versionsdatei (Abschnitt 11) gefunden"; exit 1; }
fi
echo "$version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$' || { echo "Ungültige Version: $version (erwartet V.M.P)"; exit 1; }

# Build-Nummer aus der Versionierungs-MD lesen ("**Letzter Build:** V.M.P-NNN")
letzter=$(sed -n 's/^\*\*Letzter Build:\*\* *//p' "$versionsdatei" | tail -1 | tr -d '[:space:]')
letzte_version="${letzter%-*}"
letzte_nr="${letzter##*-}"
case "$letzte_nr" in ''|*[!0-9]*) letzte_nr=0 ;; esac
if [ "$letzte_version" = "$version" ]; then
   nr=$((10#$letzte_nr + 1))
else
   nr=1
fi
build=$(printf '%03d' "$nr")
vollversion="$version-$build"

[ -f CLAUDE.md ] || { echo "CLAUDE.md fehlt im Projektstamm"; exit 1; }

# Alle Kopien der Versionierungs-MD (gleicher Dateiname in verschiedenen Ordnern)
mapfile -t md_kopien < <(find . -type f -name "$(basename "$versionsdatei")" \
      -not -path './.git/*' -not -path './Test-Protokolle/*' -not -path './Assembler/Regressionstest/*' | sort)

# Sicherungen für den Fall, dass der Lauf abbricht
sicherung=$(mktemp -d) || { echo "mktemp fehlgeschlagen"; exit 1; }
erfolg=0
geschrieben=0
aufraeumen() {
   local i
   if [ "$erfolg" != 1 ] && [ "$geschrieben" = 1 ]; then
      for i in "${!md_kopien[@]}"; do
         cp -p "$sicherung/$i" "${md_kopien[$i]}"
      done
      echo "Lauf abgebrochen: Build-Nummer in der Versionierungs-MD zurückgesetzt"
   fi
   rm -rf "$sicherung"
}
trap aufraeumen EXIT

# Build-Nummer in alle MD-Kopien schreiben (vor dem Packen, damit die MD im Zip passt)
build_in_md_schreiben() {
   local i f
   for i in "${!md_kopien[@]}"; do
      cp -p "${md_kopien[$i]}" "$sicherung/$i" || { echo "Sicherung fehlgeschlagen"; exit 1; }
   done
   geschrieben=1
   for f in "${md_kopien[@]}"; do
      if grep -q '^\*\*Letzter Build:\*\*' "$f"; then
         sed -i "s/^\*\*Letzter Build:\*\*.*/**Letzter Build:** $vollversion/" "$f" \
            || { echo "Schreiben in $f fehlgeschlagen"; exit 1; }
      else
         printf '\n**Letzter Build:** %s\n' "$vollversion" >> "$f" \
            || { echo "Schreiben in $f fehlgeschlagen"; exit 1; }
      fi
   done
   echo "Build-Nummer $vollversion in ${#md_kopien[@]} MD-Datei(en) eingetragen"
}

# Pfadprüfung: Jeder Pfad in Backticks in CLAUDE.md muss im Projekt existieren.
# Geprüft werden Einträge mit "/" oder mit Dateiendung (.md .py .sh .bat .txt .zip .asm .test .odt).
# Übersprungen werden Platzhalter (<...>), Muster (*), Befehle (mit Leerzeichen, = oder $) und Schalter.
# Ein Pfad gilt als vorhanden, wenn er (a) vom Projektstamm aus existiert, (b) irgendwo im Projekt als
# Pfadende vorkommt (CLAUDE.md nennt vieles kurz: "asm_und_test.sh" = Assembler/asm_und_test.sh,
# "Claude/" = Assembler/Claude/), oder (c) als Kurzform "_xyz.py" auf eine Datei "*_xyz.py" passt.
# Nicht geprüft werden absolute Pfade (/mnt/...), Platzhalter mit NNN und erzeugte Dateien
# (Regressionstest.zip liegt nur während des Packens im Stamm).
pfad_vorhanden() {
   local p="${1%/}"
   [ -e "$p" ] && return 0
   case "$p" in
      /*|*NNN*|Regressionstest.zip) return 0 ;;
   esac
   [ -n "$(find . -path ./.git -prune -o -path "*/$p" -print -quit)" ] && return 0
   case "$p" in
      _*) case "$p" in */*) ;; *) [ -n "$(find . -path ./.git -prune -o -name "*$p" -print -quit)" ] && return 0 ;; esac ;;
   esac
   return 1
}

pruefe_karte() {
   local fehler=0 anzahl=0 p
   while IFS= read -r p; do
      anzahl=$((anzahl + 1))
      if ! pfad_vorhanden "$p"; then
         echo "FEHLER: CLAUDE.md verweist auf '$p', den es nicht gibt"
         fehler=1
      fi
   done < <(grep -oE '`[^`]+`' CLAUDE.md | tr -d '`' \
            | grep -v -E '[<>*$=( ]' | grep -v -E '^(\./|-)' \
            | grep -E '/|^[^.][^ ]*\.(md|py|sh|bat|txt|zip|asm|test|odt)$' | sort -u)
   if [ "$fehler" = 1 ]; then
      echo "Packen abgebrochen: CLAUDE.md korrigieren oder die Dateien nachliefern (--ohne-pruefung überspringt die Prüfung)"
      exit 1
   fi
   echo "CLAUDE.md: $anzahl Pfade geprüft, alle vorhanden"
}

# Dublettenprüfung: Gleichnamige .md-Dateien in verschiedenen Ordnern müssen identisch sein.
# Ausgenommen sind .git, Test-Protokolle/ und Assembler/Regressionstest/ (gehen nicht ins Gesamt-Zip).
pruefe_dubletten() {
   local fehler=0 name pfad vorher="" erste=""
   while IFS=$'\t' read -r name pfad; do
      if [ "$name" != "$vorher" ]; then
         vorher="$name"
         erste="$pfad"
      elif ! cmp -s "$erste" "$pfad"; then
         echo "FEHLER: gleichnamige .md-Dateien mit verschiedenem Inhalt: '$erste' und '$pfad'"
         fehler=1
      fi
   done < <(find . -type f -name '*.md' -not -path './.git/*' -not -path './Test-Protokolle/*' \
                 -not -path './Assembler/Regressionstest/*' | awk -F/ '{print $NF "\t" $0}' | sort)
   if [ "$fehler" = 1 ]; then
      echo "Packen abgebrochen: eine der Fassungen entfernen oder abgleichen (--ohne-pruefung überspringt die Prüfung)"
      exit 1
   fi
   echo "Dubletten: keine gleichnamigen .md-Dateien mit verschiedenem Inhalt"
}

ziel_gesamt="C8205 Simulator $vollversion.zip"
ziel_claude="C8205 Simulator $vollversion Claude.zip"
echo "Gesamtversion: $version  Build: $build"

# Sub-Zip packen: sub_zip <zipdatei> <ordner>
sub_zip() {
   rm -f "$1"
   if [ -d "$2" ]; then
      zip -q -r "$1" "$2" || { echo "$1 fehlgeschlagen"; exit 1; }
      echo "erzeugt: $1"
   else
      echo "Hinweis: $2 fehlt, $1 wird nicht erzeugt"
   fi
}

# Gesamt-Zip oder schlanke Variante packen: gesamt_zip <zieldatei> <0|1 = schlank>
gesamt_zip() {
   local ziel="$1" schlank="$2"
   local ausschluss=(
       -x ".git" ".git/*" "*/.git/*"
       -x "Test-Protokolle" "Test-Protokolle/*"
       -x "Assembler/Regressionstest" "Assembler/Regressionstest/*"
       -x "C8205 Simulator *.zip"
       -x "*__pycache__*"
   )
   if [ "$schlank" = 1 ]; then
       ausschluss+=(
           -x "Test-Protokolle.zip" "README.en.md"
           -x "PDF" "PDF/*" "Testausfuehrungen/test_tabelle*" "pult" "pult/*" "ton" "ton/*"
           -x "*.pdf" "*/pdf-layout-scripte" "*/pdf-layout-scripte/*" "make_pdf.sh" "make_all_pdf.sh"
           -x "Assembler/*.log" "Assembler/*.mqo" "Assembler/*.obj" "Assembler/*.sym"
       )
   fi
   rm -f "$ziel"
   # CLAUDE.md zuerst, damit sie im Archiv der erste Eintrag ist
   zip -q "$ziel" CLAUDE.md || { echo "Packen fehlgeschlagen: $ziel"; exit 1; }
   zip -q -r "$ziel" * "${ausschluss[@]}" || { echo "Packen fehlgeschlagen: $ziel"; exit 1; }
   echo "erzeugt: $ziel"
}

if [ "$pruefen" = 1 ]; then
   pruefe_karte
   pruefe_dubletten
fi

# 0. Build-Nummer in die Versionierungs-MD eintragen (vor dem Packen)
build_in_md_schreiben

# 1. Sub-Zips (einmal, beide Fassungen brauchen sie bzw. schließen sie aus)
sub_zip "Test-Protokolle.zip" "Test-Protokolle"
sub_zip "Regressionstest.zip" "Assembler/Regressionstest"

# 2. Gesamt-Zip und/oder schlanke Variante
[ "$mache_gesamt" = 1 ] && gesamt_zip "$ziel_gesamt" 0
[ "$mache_claude" = 1 ] && gesamt_zip "$ziel_claude" 1

rm -f ./Test-Protokolle.zip ./Regressionstest.zip

# Alles gut gegangen: Build-Nummer in der MD bleibt stehen
erfolg=1
