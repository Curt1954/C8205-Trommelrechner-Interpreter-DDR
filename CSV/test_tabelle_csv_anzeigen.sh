#!/bin/bash
# Oeffnet test_tabelle.csv in LibreOffice Calc und markiert Zellen der letzten
# Spalte gruen, deren Wert groesser ist als der in der Spalte davor.
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

if letzte_spalte < 1:
    print("Zu wenige Spalten zum Vergleichen.")
    sys.exit(0)

anzahl_gruen = 0
for zeile in range(1, letzte_zeile + 1):  # Zeile 0 = Ueberschrift
    links = sheet.getCellByPosition(letzte_spalte - 1, zeile)
    rechts = sheet.getCellByPosition(letzte_spalte, zeile)
    if rechts.Value > links.Value:
        rechts.CellBackColor = 0x00FF00
        anzahl_gruen += 1
    else:
        rechts.CellBackColor = -1

print(f"Gruen markiert: {anzahl_gruen} Zellen")

doc.CurrentController.setActiveSheet(sheet)
frame = doc.CurrentController.Frame
frame.ContainerWindow.setVisible(True)
print("Fertig.")
PY

# Python ist fertig, LibreOffice bleibt offen, bis das Fenster geschlossen wird
wait "$LO_PID"

