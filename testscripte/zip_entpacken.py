#!/usr/bin/env python3
"""zip_entpacken.py -- entpackt, listet und liest Zips mit Python-zipfile statt mit `unzip`.

Warum: `unzip` macht in der POSIX-Locale aus Umlauten im Dateinamen `#U00e4`
(z. B. `C8205-Interpreter-Eing#U00e4nge_der_Knoten.md`); der Interpreter bricht dann mit
"Knotengraph nicht gefunden" ab. Python-zipfile liest die UTF-8-Namen unabhaengig von der Locale richtig.
Das ist der Standardweg fuer jede Claude-Sitzung (CLAUDE.md, Handbuch Abschnitt 2); `unzip` wird nicht benutzt.

Aufruf (immer mit -I, siehe unten):
  python3 -I testscripte/zip_entpacken.py <zip> <zielordner>        entpacken (Zielordner neu oder leer)
  python3 -I testscripte/zip_entpacken.py -l <zip> [teilname]       Namen listen (nur die, die teilname enthalten)
  python3 -I testscripte/zip_entpacken.py -p <zip> <pfad>           eine Datei auf stdout ausgeben (wie unzip -p)

Beim Entpacken:
  - Namen: UTF-8 (Flag 0x800) oder, bei aelteren Zips ohne Flag, CP437; ist der CP437-Name in Wahrheit UTF-8,
    wird er so gelesen (Windows-/Linux-Zips).
  - Rechte: die im Zip gespeicherten Unix-Rechte werden gesetzt (ausfuehrbare .sh bleiben ausfuehrbar).
  - Pfade mit `..` oder absolute Pfade werden verweigert (das Zip ist Fremdinhalt).
Rueckgabe: 0 ok, 1 Fehler im Zip oder Pfad nicht gefunden, 2 Aufruf falsch.
Zum Entpacken ohne dieses Skript (es liegt selbst im Zip) steht die Einzeiler-Fassung in CLAUDE.md, Schnellstart.
"""
import os
import sys
import zipfile


def name_von(info):
    """Dateiname als Text; nur korrigieren, wenn das Zip das UTF-8-Flag nicht setzt."""
    n = info.filename
    if not (info.flag_bits & 0x800):
        try:
            n = n.encode("cp437").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            n = info.filename
    return n


def sicher(ziel, name):
    p = os.path.normpath(os.path.join(ziel, name))
    wurzel = os.path.normpath(ziel)
    if os.path.isabs(name) or not (p == wurzel or p.startswith(wurzel + os.sep)):
        raise ValueError("unsicherer Pfad im Zip: %r" % name)
    return p


def entpacken(zippfad, ziel):
    z = zipfile.ZipFile(zippfad)
    if os.path.isdir(ziel) and os.listdir(ziel):
        print("Zielordner %s ist nicht leer; neuen, leeren Ordner angeben." % ziel, file=sys.stderr)
        return 2
    anzahl = 0
    for info in z.infolist():
        name = name_von(info)
        p = sicher(ziel, name)
        if info.is_dir() or name.endswith("/"):
            os.makedirs(p, exist_ok=True)
            continue
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(z.read(info))
        modus = (info.external_attr >> 16) & 0o777
        os.chmod(p, modus if modus else 0o644)
        anzahl += 1
    print("%d Dateien nach %s entpackt." % (anzahl, ziel))
    return 0


def main(a):
    try:
        if len(a) == 2 and a[0] not in ("-l", "-p"):
            return entpacken(a[0], a[1])
        if a and a[0] == "-l" and len(a) in (2, 3):
            z = zipfile.ZipFile(a[1])
            teil = a[2] if len(a) == 3 else ""
            for info in z.infolist():
                n = name_von(info)
                if teil in n:
                    print(n)
            return 0
        if a and a[0] == "-p" and len(a) == 3:
            z = zipfile.ZipFile(a[1])
            for info in z.infolist():
                if name_von(info) == a[2]:
                    sys.stdout.buffer.write(z.read(info))
                    return 0
            print("nicht im Zip: %s" % a[2], file=sys.stderr)
            return 1
    except (zipfile.BadZipFile, OSError, ValueError) as e:
        print("Fehler: %s" % e, file=sys.stderr)
        return 1
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    print("Aufruf: zip_entpacken.py <zip> <zielordner> | -l <zip> [teilname] | -p <zip> <pfad>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
