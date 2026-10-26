#!/bin/bash
# Oeffnet test_tabelle.csv in LibreOffice Calc und richtet die Ansicht ein:
#   - Zeilenumbruch in allen Zellen, feste Spaltenbreiten, Zeilenhoehe nach Inhalt
#   - fette, eingefrorene Kopfzeile
#   - gelb:   "Inhalt des Tests" ist nur ein Platzhalter ("[Tastenfolge: ...]"
#             bzw. "(keine #DOK-Beschreibung ...)") -> #DOK-Zeile in der Testdatei fehlt
#   - orange: "ASM-Quelltext" ist nur vermutet bzw. Voraussetzung
#             (Spalte "ASM-Zuordnung" ist nicht leer)
# Funktioniert aus jedem Verzeichnis (Pfade relativ zum Skript).

SKRIPTDIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
DATEI="${1:-$SKRIPTDIR/test_tabelle.csv}"
PORT=2002
PROFIL="/tmp/lo_uno_profil_$PORT"

if [ ! -f "$DATEI" ]; then
    echo "Fehler: Datei nicht gefunden: $DATEI" >&2
    exit 1
fi
DATEI="$(readlink -f "$DATEI")"

# Eigenes Profil -> immer neue Instanz mit UNO-Socket, auch wenn LibreOffice schon laeuft
libreoffice \
    -env:UserInstallation="file://$PROFIL" \
    --accept="socket,host=127.0.0.1,port=$PORT;urp;StarOffice.ComponentContext" \
    --norestore \
    --nodefault \
    --nofirststartwizard &

LO_PID=$!

python3 - "$DATEI" "$PORT" <<'PY'
import sys
import time
import uno
from com.sun.star.connection import NoConnectException

datei = sys.argv[1]
port = sys.argv[2]

local_ctx = uno.getComponentContext()
resolver = local_ctx.ServiceManager.createInstanceWithContext(
    "com.sun.star.bridge.UnoUrlResolver", local_ctx
)

# Auf den UNO-Server warten (bis ca. 30 s)
ctx = None
for _ in range(60):
    try:
        ctx = resolver.resolve(
            f"uno:socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext"
        )
        break
    except NoConnectException:
        time.sleep(0.5)
if ctx is None:
    print("Fehler: keine Verbindung zu LibreOffice (Port %s)." % port)
    sys.exit(1)

smgr = ctx.ServiceManager
desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

url = uno.systemPathToFileUrl(datei)


def prop(name, value):
    p = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    p.Name = name
    p.Value = value
    return p


# 59 = Semikolon, 34 = Anfuehrungszeichen, 76 = UTF-8, 1 = ab Zeile 1
props = (
    prop("FilterName", "Text - txt - csv (StarCalc)"),
    prop("FilterOptions", "59,34,76,1"),
)

doc = desktop.loadComponentFromURL(url, "_blank", 0, props)
if doc is None:
    print(f"Fehler: {datei} konnte nicht geoeffnet werden.")
    sys.exit(1)

sheet = doc.Sheets.getByIndex(0)

cursor = sheet.createCursor()
cursor.gotoEndOfUsedArea(False)
letzte_zeile = cursor.RangeAddress.EndRow
letzte_spalte = cursor.RangeAddress.EndColumn

print(f"Letzte Zeile:  {letzte_zeile + 1}")
print(f"Letzte Spalte: {letzte_spalte + 1}")

# Spaltenbreiten (1/100 mm) in der Reihenfolge der Spalten:
# Testdatei, Inhalt, Geraete/Vergleichsdatei, ASM-Quelltext, ASM-Zuordnung
BREITEN = [6500, 9500, 9500, 8000, 4500]
for sp, breite in enumerate(BREITEN):
    if sp <= letzte_spalte:
        sheet.Columns.getByIndex(sp).Width = breite

# Zeilenumbruch in allen Zellen, Inhalt oben ausgerichtet, Zeilenhoehe nach Inhalt
bereich = sheet.getCellRangeByPosition(0, 0, letzte_spalte, letzte_zeile)
bereich.IsTextWrapped = True
bereich.CellBackColor = -1  # alte Markierungen zuruecksetzen
try:
    bereich.VertJustify = uno.Enum("com.sun.star.table.CellVertJustify", "TOP")
except Exception as e:
    print("Hinweis: Ausrichtung oben nicht gesetzt:", e)
bereich.Rows.OptimalHeight = True

# Kopfzeile fett (150.0 = FontWeight.BOLD)
sheet.getCellRangeByPosition(0, 0, letzte_spalte, 0).CharWeight = 150.0


def spalte(praefix):
    """Spaltennummer anhand der Kopfzeile (Anfang des Titels) oder None."""
    for sp in range(letzte_spalte + 1):
        if sheet.getCellByPosition(sp, 0).String.startswith(praefix):
            return sp
    return None


sp_inhalt = spalte("Inhalt")
sp_asm = spalte("ASM-Quelltext")
sp_zuordnung = spalte("ASM-Zuordnung")

GELB = 0xFFF59D
ORANGE = 0xFFCC80
PLATZHALTER = ("[Tastenfolge", "(keine #DOK")
anzahl_gelb = 0
anzahl_orange = 0
for zeile in range(1, letzte_zeile + 1):  # Zeile 0 = Ueberschrift
    if sp_inhalt is not None:
        zelle = sheet.getCellByPosition(sp_inhalt, zeile)
        if zelle.String.startswith(PLATZHALTER):
            zelle.CellBackColor = GELB
            anzahl_gelb += 1
    if sp_asm is not None and sp_zuordnung is not None:
        zuordnung = sheet.getCellByPosition(sp_zuordnung, zeile)
        if zuordnung.String.strip():
            zuordnung.CellBackColor = ORANGE
            sheet.getCellByPosition(sp_asm, zeile).CellBackColor = ORANGE
            anzahl_orange += 1

print(f"Gelb markiert (nur Platzhalter statt Beschreibung): {anzahl_gelb} Zellen")
print(f"Orange markiert (ASM vermutet / Voraussetzung):     {anzahl_orange} Zeilen")

doc.CurrentController.setActiveSheet(sheet)
try:
    doc.CurrentController.freezeAtPosition(0, 1)  # Kopfzeile einfrieren
except Exception as e:
    print("Hinweis: Kopfzeile nicht eingefroren:", e)
frame = doc.CurrentController.Frame
frame.ContainerWindow.setVisible(True)
print("Fertig.")
PY

# Python ist fertig, LibreOffice bleibt offen, bis das Fenster geschlossen wird
wait "$LO_PID"
