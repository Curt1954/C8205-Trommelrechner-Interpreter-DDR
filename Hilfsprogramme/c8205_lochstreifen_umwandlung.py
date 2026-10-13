#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
c8205_lochstreifen_umwandlung.py -- Hilfsprogramm zum C8205-Interpreter (c8205_interp.py)

Wandelt eine Textdatei in einen binaer codierten virtuellen R300-Lochstreifen um
(--IN-BIN, Vorgabe) oder umgekehrt einen binaer codierten Lochstreifen in eine Textdatei
(--IN-TXT).

Aufruf:
    python3 c8205_lochstreifen_umwandlung.py --STANZER AUSGABE --LESER EINGABE [--IN-BIN | --IN-TXT]

    --LESER    Pflicht. Eingabe: bei --IN-BIN die Textdatei, bei --IN-TXT der Lochstreifen
               (jeweils auch ein Verzeichnis mit Dateien).
    --STANZER  Pflicht. Ausgabe: bei --IN-BIN der Lochstreifen, bei --IN-TXT die Textdatei.
               Datei, oder Verzeichnis (dann VERZ/stanzer-ausgabe.txt).
    Beide muessen angegeben werden.
    --IN-BIN   Text -> binaer codierter R300-Lochstreifen (Vorgabe).
    --IN-TXT   binaer codierter R300-Lochstreifen -> Text (Umkehrung).

Verarbeitet werden nur Zeichen des R300-Kodes (Kodetabelle 1, Spalte "Ausgabe-Adresse").
Alle anderen Zeichen werden uebersprungen und am Ende gemeldet. Die Zeichenlage
(Klbuch/Gbuch) wird nicht im Text angegeben, sondern ergibt sich aus dem Zeichen: Das
Programm stanzt "Um. KB" bzw. "Um. GB" selbst, sobald ein Zeichen die andere Lage braucht
(Anfangslage KB, wie beim Eingabe-Hilfsprogramm). Zeilenende wird zu SatzMarke/WRZL,
Tabulator zu Tabulator, Leerzeichen zu Leertaste/ZR.

Rueckrichtung (--IN-TXT): wie die Anzeige. Um. KB/Um. GB wirken nur (Zeichenlage), "Irrung Zeichen"
loescht das letzte Zeichen der Zeile, "Irrung Satz" die ganze bisherige Zeile; SatzMarke/WRZL wird
zum Zeilenende. Zeilen ohne Datenlochung (00000000), ungueltige Zeilen, Zeilen mit gerader
Lochzahl (Paritaetsfehler), unbekannte Lochungen und Transport (Relikt) werden uebersprungen und gemeldet.

Ausgabeformat (wie --stanzer1 des Interpreters): eine Lochungszeile je Zeichen, 8 Ziffern
0/1 in der Spurfolge  w v u p 8 4 2 1  (1 = gelocht), Zeilenende "\\n".

Nur Python-3-Standardbibliothek; laeuft unter Linux, macOS und Windows.
Rueckgabewert: 0 = in Ordnung, 2 = Aufruf-, Lese- oder Schreibfehler.
"""

import argparse
import os
import sys

VERSION = '1.1'

# Kodetabelle 1 (R300), Zeilen 1-49 mit Zeichen: (Klbuch-Zeichen, Gbuch-Zeichen, Ausgabe-Adresse oktal).
# Identisch zu TABELLE1 in c8205_interp.py (Spalten 1, 2, 3). Die Zeichenlage-unabhaengigen Zeilen
# (Tabulator, SatzMarke/WRZL, Leertaste/ZR) stehen darunter.
ZEICHEN_TABELLE = [
    ('1', '<', '001'), ('2', '"', '002'), ('3', '\u2248', '023'), ('4', '[', '004'),
    ('5', '>', '025'), ('6', "'", '026'), ('7', '\u224b', '007'), ('8', '~', '010'),
    ('9', ']', '031'), ('0', '#', '020'), ('%', '*', '174'),
    ('q', 'Q', '130'), ('w', 'W', '166'), ('e', 'E', '045'), ('r', 'R', '111'),
    ('t', 'T', '163'), ('z', 'Z', '171'), ('u', 'U', '144'), ('i', 'I', '051'),
    ('o', 'O', '106'), ('p', 'P', '127'), (':', '(', '015'), ('+', '=', '040'),
    ('a', 'A', '061'), ('s', 'S', '142'), ('d', 'D', '064'), ('f', 'F', '046'),
    ('g', 'G', '067'), ('h', 'H', '070'), ('j', 'J', '121'), ('k', 'K', '122'),
    ('l', 'L', '103'), ('`', ';', '160'), ('/', ')', '141'),
    ('y', 'Y', '150'), ('x', 'X', '147'), ('c', 'C', '043'), ('v', 'V', '165'),
    ('b', 'B', '062'), ('n', 'N', '105'), ('m', 'M', '124'), (',', '?', '153'),
    ('.', '!', '073'), ('-', '\u25b3', '100'),
]
# Zeichen, die in beiden Lagen gleich gestanzt werden
LAGEFREI = {'\t': 0o155, '\n': 0o272, ' ': 0o032}
UM_KB = 0o117
UM_GB = 0o057

# Zeichen -> (Lage, Lochbild); Lage 'KB' / 'GB' / None (lageunabhaengig)
ZEICHEN = {}
for _kb, _gb, _code in ZEICHEN_TABELLE:
    ZEICHEN[_kb] = ('KB', int(_code, 8))
    ZEICHEN[_gb] = ('GB', int(_code, 8))
for _z, _code in LAGEFREI.items():
    ZEICHEN[_z] = (None, _code)


class Fehler(Exception):
    pass


def umwandeln(text_stuecke):
    """text_stuecke: Iterable von (Name, Text). Liefert (Lochbilder, Statistik).
    Statistik: dict mit 'zeichen', 'umschaltungen', 'uebersprungen' (dict Zeichen -> [Anzahl, Ort])."""
    lochbilder = []
    lage = 'KB'
    stat = {'zeichen': 0, 'umschaltungen': 0, 'uebersprungen': {}}
    for name, text in text_stuecke:
        zeile = 1
        for z in text:
            if z == '\r':               # Windows-Zeilenende: nur \n zaehlt
                continue
            eintrag = ZEICHEN.get(z)
            if eintrag is None:
                u = stat['uebersprungen'].setdefault(z, [0, f'{name}, Zeile {zeile}'])
                u[0] += 1
            else:
                zl, lb = eintrag
                if zl is not None and zl != lage:
                    lochbilder.append(UM_KB if zl == 'KB' else UM_GB)
                    stat['umschaltungen'] += 1
                    lage = zl
                lochbilder.append(lb)
                stat['zeichen'] += 1
            if z == '\n':
                zeile += 1
    return lochbilder, stat


# Lochbild -> (KB-Zeichen, GB-Zeichen) bzw. Funktionszeichen
LOCHBILD = {}
for _kb, _gb, _code in ZEICHEN_TABELLE:
    LOCHBILD[int(_code, 8)] = (_kb, _gb)
LOCHBILD_LAGEFREI = {_code: _z for _z, _code in LAGEFREI.items()}
IRRUNG_ZEICHEN = 0o377
IRRUNG_SATZ = 0o016
TRANSPORT = 0o177


def zurueckwandeln(stuecke):
    """stuecke: Iterable von (Name, Text). Liefert (Text, Statistik); Statistik: 'zeilen', 'zeichen',
    'meldungen' (Liste von Texten)."""
    ausgabe = []          # fertige Zeilen und Zeilenenden
    aktuell = []          # aktuelle Zeile
    lage = 'KB'
    stat = {'zeilen': 0, 'zeichen': 0, 'meldungen': []}

    def melde(text):
        stat['meldungen'].append(text)

    for name, text in stuecke:
        for nr, roh in enumerate(text.splitlines(), 1):
            z = roh.strip()
            if not z:
                continue
            ort = f'{name}, Zeile {nr}'
            if len(z) != 8 or any(c not in '01' for c in z):
                melde(f'ungültige Lochungszeile {z[:20]!r} übersprungen ({ort})')
                continue
            lb = int(z, 2)
            stat['zeilen'] += 1
            if lb == 0:                      # Vorspann ohne Datenlochung
                continue
            if lb == IRRUNG_ZEICHEN:
                if aktuell:
                    aktuell.pop()
                continue
            if bin(lb).count('1') % 2 == 0:
                melde(f'Paritätsfehler {z} übersprungen ({ort})')
                continue
            if lb == UM_KB:
                lage = 'KB'
            elif lb == UM_GB:
                lage = 'GB'
            elif lb == IRRUNG_SATZ:
                aktuell.clear()
            elif lb == TRANSPORT:
                melde(f'Transport (Relikt) {z} übersprungen ({ort})')
            elif lb in LOCHBILD_LAGEFREI:
                zeichen = LOCHBILD_LAGEFREI[lb]
                if zeichen == '\n':
                    ausgabe.append(''.join(aktuell) + '\n')
                    aktuell = []
                else:
                    aktuell.append(zeichen)
                stat['zeichen'] += 1
            elif lb in LOCHBILD:
                aktuell.append(LOCHBILD[lb][0 if lage == 'KB' else 1])
                stat['zeichen'] += 1
            else:
                melde(f'unbekannte Lochung {z} übersprungen ({ort})')
    ausgabe.append(''.join(aktuell))
    return ''.join(ausgabe), stat


def ausgabe_pfad(pfad):
    if os.path.isdir(pfad) or pfad.endswith(('/', '\\')):
        return os.path.join(pfad, 'stanzer-ausgabe.txt')
    return pfad


def gleich(a, b):
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def eingabedateien(pfad, ausgabe):
    if os.path.isdir(pfad):
        dateien = sorted(os.path.join(pfad, f) for f in os.listdir(pfad)
                         if os.path.isfile(os.path.join(pfad, f)) and not f.startswith('.'))
        dateien = [f for f in dateien if not gleich(f, ausgabe)]
        if not dateien:
            raise Fehler(f'LESER {pfad}: keine Textdatei gefunden')
        return dateien
    if os.path.isfile(pfad):
        if gleich(pfad, ausgabe):
            raise Fehler('LESER und STANZER sind dieselbe Datei')
        return [pfad]
    raise Fehler(f'LESER nicht gefunden: {pfad}')


def lese(dateien):
    for f in dateien:
        try:
            with open(f, encoding='utf-8-sig', errors='replace', newline='') as fh:
                yield os.path.basename(f), fh.read()
        except OSError as e:
            raise Fehler(f'LESER {f}: {e.strerror or e}')


def schreibe_text(pfad, text):
    try:
        os.makedirs(os.path.dirname(os.path.abspath(pfad)), exist_ok=True)
        with open(pfad, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text)
    except OSError as e:
        raise Fehler(f'STANZER {pfad}: {e.strerror or e}')


def schreibe(pfad, lochbilder):
    try:
        os.makedirs(os.path.dirname(os.path.abspath(pfad)), exist_ok=True)
        with open(pfad, 'w', encoding='ascii', newline='\n') as fh:
            fh.write(''.join(format(lb, '08b') + '\n' for lb in lochbilder))
    except OSError as e:
        raise Fehler(f'STANZER {pfad}: {e.strerror or e}')


def beschreibe(z):
    if z == '\n':
        return 'Zeilenende'
    if ord(z) < 32 or ord(z) == 127:
        return f'Steuerzeichen U+{ord(z):04X}'
    return f"'{z}' (U+{ord(z):04X})"


def main(argv=None):
    for strom in (sys.stdout, sys.stderr):
        try:
            strom.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(
        prog='c8205_lochstreifen_umwandlung.py', allow_abbrev=False,
        description='Wandelt eine Textdatei in einen binaer codierten R300-Lochstreifen um.')
    p.add_argument('--STANZER', '--stanzer', dest='stanzer', metavar='PFAD',
                   help='Pflicht. Zu erzeugender Lochstreifen (Datei oder Verzeichnis)')
    p.add_argument('--LESER', '--leser', dest='leser', metavar='PFAD',
                   help='Pflicht. Textdatei (oder Verzeichnis mit Textdateien)')
    p.add_argument('--IN-BIN', '--in-bin', dest='in_bin', action='store_true',
                   help='Text -> binär codierter R300-Lochstreifen (Vorgabe)')
    p.add_argument('--IN-TXT', '--in-txt', dest='in_txt', action='store_true',
                   help='binär codierter R300-Lochstreifen -> Text (Umkehrung)')
    p.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    a = p.parse_args(argv)
    if not a.stanzer or not a.leser:
        fehlt = [n for n, w in (('--STANZER', a.stanzer), ('--LESER', a.leser)) if not w]
        print('Fehler: --STANZER und --LESER müssen beide angegeben werden '
              f'(es fehlt: {", ".join(fehlt)}).', file=sys.stderr)
        p.print_usage(sys.stderr)
        return 2
    if a.in_bin and a.in_txt:
        print('Fehler: --IN-BIN und --IN-TXT schließen sich aus.', file=sys.stderr)
        return 2
    if a.in_txt:
        return main_txt(a)
    try:
        ziel = ausgabe_pfad(a.stanzer)
        dateien = eingabedateien(a.leser, ziel)
        lochbilder, stat = umwandeln(lese(dateien))
        schreibe(ziel, lochbilder)
    except Fehler as e:
        print(f'Fehler: {e}', file=sys.stderr)
        return 2
    for z, (n, ort) in sorted(stat['uebersprungen'].items(), key=lambda kv: -kv[1][0])[:10]:
        print(f'Warnung: {beschreibe(z)} nicht im R300-Kode, {n}x übersprungen '
              f'(zuerst: {ort})', file=sys.stderr)
    if len(stat['uebersprungen']) > 10:
        print(f'Warnung: {len(stat["uebersprungen"]) - 10} weitere nicht kodierbare Zeichen übersprungen',
              file=sys.stderr)
    if not lochbilder:
        print('Warnung: kein Zeichen des R300-Kodes gefunden, Lochstreifen ist leer', file=sys.stderr)
    uebersp = sum(n for n, _ in stat['uebersprungen'].values())
    print(f'{len(lochbilder)} Lochungszeilen nach {ziel} geschrieben '
          f'({stat["zeichen"]} Zeichen, {stat["umschaltungen"]} Zeichenlagen-Umschaltungen, '
          f'{uebersp} Zeichen übersprungen).')
    return 0


def main_txt(a):
    try:
        ziel = ausgabe_pfad(a.stanzer)
        dateien = eingabedateien(a.leser, ziel)
        text, stat = zurueckwandeln(lese(dateien))
        schreibe_text(ziel, text)
    except Fehler as e:
        print(f'Fehler: {e}', file=sys.stderr)
        return 2
    for m in stat['meldungen'][:10]:
        print(f'Warnung: {m}', file=sys.stderr)
    if len(stat['meldungen']) > 10:
        print(f'Warnung: {len(stat["meldungen"]) - 10} weitere Meldungen unterdrückt', file=sys.stderr)
    print(f'{stat["zeilen"]} Lochungszeilen gelesen, {stat["zeichen"]} Zeichen als Text nach {ziel} '
          f'geschrieben ({len(stat["meldungen"])} Zeilen übersprungen).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
