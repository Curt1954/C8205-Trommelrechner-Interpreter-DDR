#!/bin/bash
# c8205_zip_packen.sh -- packt das Projektverzeichnis zu "C8205 Simulator V.M.P-NNN.zip"
# und zu der schlanken Variante "C8205 Simulator V.M.P-NNN Claude.zip".
# Aufruf (von überall):  ./c8205_zip_packen.sh [--gesamt | --claude] [--ohne-pruefung] [V.M.P]
#
# NNN ist eine eigene, fortlaufende, dreistellige Build-Nummer. Gesamtversion und Build-Nummer stehen
# in der Zähldatei .build-nummer im Projektstamm, eine Zeile:
#     V.M.P-NNN          (z. B. 0.95.7-002)
# Das ist die Nummer, die der NÄCHSTE Lauf verwendet. Nach einem erfolgreichen Lauf schreibt das
# Skript V.M.P-(NNN+1) zurück. Ein abgebrochener Lauf lässt die Datei unverändert und verbraucht
# keine Nummer. Fehlt die Datei oder ist ihr Inhalt ungültig, bricht das Skript mit einer
# Meldung ab. Ein Aufrufparameter V.M.P ersetzt die Version aus der Datei; weicht er von ihr ab,
# beginnt die Build-Nummer bei 001. Beide Zips eines Laufs tragen dieselbe Nummer. Die Datei
# .build-nummer kommt in keines der Zips.
# Zusätzlich trägt das Skript die verwendete Nummer in die Zeile
#     **Letzter Build:** V.M.P-NNN
# von markdown-dateien/C8205-Versionierung.md ein (fehlt die Zeile, hängt es sie am Dateiende an),
# BEVOR gepackt wird, damit die MD im Zip zur Zip-Nummer passt. Das ist nur eine Anzeige; gelesen
# wird sie nicht. Bricht der Lauf ab, werden alle MD-Fassungen auf den alten Stand zurückgesetzt.
# Gibt es C8205-Versionierung.md in mehreren Ordnern (Dublettenprüfung!), werden alle Kopien
# gleichzeitig geändert und bleiben identisch.
#
# Ohne Schalter entstehen beide Fassungen in einem Lauf:
#   C8205 Simulator V.M.P-NNN.zip          Gesamt-Zip (alles)
#   C8205 Simulator V.M.P-NNN Claude.zip   schlanke Variante für KI-Sitzungen
# Mit --gesamt entsteht nur das Gesamt-Zip, mit --claude nur die schlanke Variante.
# Vor dem Packen prüft das Skript, ob gleichnamige .md-Dateien in verschiedenen Ordnern denselben
# Inhalt haben, und bricht bei Fehlern ab. Mit --ohne-pruefung wird diese Prüfung übersprungen.
# (Die frühere Prüfung, ob alle Pfade in Backticks aus CLAUDE.md existieren, gibt es nicht mehr.)
#
# Die schlanke Variante: Das Auflisten zeigt rund 40 % weniger Einträge.
# Es fehlen: PDFs (außer unter C8205Z/) und ihre Erzeugungsskripte (pdf-layout-scripte/), die Testtabelle
# (Testausfuehrungen/test_tabelle*; die Skripte dort bleiben drin), pult/, ton/,
# README.en.md, Test-Protokolle.zip, __pycache__ sowie die vom Assembler
# erzeugten Dateien .log .mqo .obj .sym unter Assembler/. Es bleiben .asm, .dmp und .test.
# virtuelle_Geraete/ bleibt drin (Standardpfade von Leser und Stanzer, nur wenige KB).
# C8205Z/ (ZT-Zusatztrommel) kommt komplett in die schlanke Variante, auch seine PDFs.
# Der GRAFIK-Interpreter läuft mit --ohne-fenster --STUMM auch ohne pult/ und ton/.
# Wer am GRAFIK-Fenster, am Pult oder an den Klängen arbeitet, nimmt das Gesamt-Zip.
# In beiden Fassungen tragen alle .sh-Dateien die Rechte 0755 (das Skript schreibt das Zip dafür nach dem Packen mit
# Python-zipfile neu; ohne python3 nur eine Warnung).
# In beiden Fassungen steht CLAUDE.md als erster Eintrag (Python-zipfile liest sie, Einzeiler siehe CLAUDE.md; nie unzip).
#
# 1. Die Gesamtversion V.M.P und die Build-Nummer kommen aus der Zähldatei .build-nummer
#    (nicht mehr aus der Release-Tabelle in C8205-Versionierung.md). Ein Aufrufparameter
#    V.M.P überschreibt die Version aus der Datei.
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

# Gesamtversion und Build-Nummer aus der Zähldatei .build-nummer lesen: eine Zeile V.M.P-NNN,
# die Nummer, die dieser Lauf verwendet. Nach dem Packen wird NNN + 1 zurückgeschrieben.
buildnummer_datei=".build-nummer"
[ -f "$buildnummer_datei" ] || { echo "$buildnummer_datei fehlt im Projektstamm. Anlegen mit:  echo 0.95.7-002 > $buildnummer_datei"; exit 1; }
inhalt=$(grep -v '^[[:space:]]*$' "$buildnummer_datei" | head -1 | tr -d '[:space:]')
echo "$inhalt" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+-[0-9]+$' || { echo "$buildnummer_datei: Inhalt '$inhalt' ungültig (erwartet eine Zeile V.M.P-NNN, z. B. 0.95.7-002)"; exit 1; }
datei_version="${inhalt%-*}"
datei_nr=$((10#${inhalt##*-}))
if [ $# -ge 1 ]; then
   version="$1"
else
   version="$datei_version"
fi
echo "$version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$' || { echo "Ungültige Version: $version (erwartet V.M.P)"; exit 1; }
if [ "$version" = "$datei_version" ]; then
   nr=$datei_nr
else
   nr=1
fi
[ "$nr" -ge 1 ] || nr=1     # Build 000 wird nicht vergeben
[ "$nr" -le 999 ] || { echo "Build-Überlauf ($nr) in $buildnummer_datei: nichts wird von selbst erhöht, den Projektinhaber fragen"; exit 1; }
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

# Rechte im Zip: jede .sh-Datei soll im Zip 0755 tragen, unabhängig vom Dateisystem des Rechners
# (auf NTFS oder nach einem Entpacken ohne Rechte fehlt das X-Bit, und die Skripte laufen dann in der
# Claude-Sitzung nur mit "bash <skript>"). zip kann keine Rechte setzen, deshalb wird das Zip neu geschrieben.
# zip_rechte_setzen <zipdatei>; ohne python3 nur eine Warnung (das Zip bleibt unverändert gültig).
zip_rechte_setzen() {
   local z="$1"
   if ! command -v python3 >/dev/null 2>&1; then
       echo "WARNUNG: python3 fehlt, die Rechte (.sh = 0755) im Zip \"$z\" wurden nicht gesetzt"
       return 0
   fi
   python3 -I - "$z" <<'PY' || { echo "WARNUNG: Rechte im Zip \"$z\" konnten nicht gesetzt werden (Zip bleibt unverändert)"; rm -f "$z.neu"; return 0; }
import os, sys, zipfile
quelle = sys.argv[1]
ziel = quelle + '.neu'
anzahl = 0
with zipfile.ZipFile(quelle) as zin, zipfile.ZipFile(ziel, 'w', zipfile.ZIP_DEFLATED) as zout:
    for zi in zin.infolist():
        daten = b'' if zi.is_dir() else zin.read(zi)
        if not (zi.flag_bits & 0x800):           # zip schreibt UTF-8-Namen ohne Kennzeichen: sonst würden Umlaute verfälscht
            try: zi.filename = zi.filename.encode('cp437').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError): pass
        if zi.filename.endswith('.sh') and not zi.is_dir():
            zi.create_system = 3
            zi.external_attr = (0o100755 << 16) | (zi.external_attr & 0xFFFF)
            anzahl += 1
        zout.writestr(zi, daten, compress_type=zi.compress_type)
os.replace(ziel, quelle)
print('Rechte gesetzt: %d Skripte (.sh) mit 0755' % anzahl)
PY
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
       -x ".build-nummer"
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
   # Schlanke Variante: C8205Z/ komplett nachlegen (der Ausschluss "*.pdf" oben hat dort PDFs entfernt)
   if [ "$schlank" = 1 ] && [ -d C8205Z ]; then
       zip -q -r "$ziel" C8205Z -x "*__pycache__*" -x ".git/*" -x "*/.git/*" \
          || { echo "Packen fehlgeschlagen: $ziel (C8205Z)"; exit 1; }
   fi
   zip_rechte_setzen "$ziel"
   echo "erzeugt: $ziel"
}

if [ "$pruefen" = 1 ]; then
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

# Alles gut gegangen: Build-Nummer in der MD bleibt stehen, .build-nummer wird um 1 erhöht
erfolg=1
naechste="$version-$(printf '%03d' $((nr + 1)))"
printf '%s\n' "$naechste" > "$buildnummer_datei.neu" && mv -f "$buildnummer_datei.neu" "$buildnummer_datei" \
   || { echo "WARNUNG: $buildnummer_datei konnte nicht auf $naechste gesetzt werden; der nächste Lauf würde $vollversion wieder verwenden"; exit 1; }
echo "$buildnummer_datei: nächster Lauf $naechste"
