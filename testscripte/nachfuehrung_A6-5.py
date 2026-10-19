#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nachführung A6-5: zwei GRAFIK-PDFs in Dokumentation und Versionierung eintragen.

Aufruf (im Projektordner):  python3 testscripte/nachfuehrung_A6-5.py            # Probelauf, schreibt nichts
                            python3 testscripte/nachfuehrung_A6-5.py --anwenden # schreibt die Dateien

Der Probelauf zeigt je Datei alte und neue Version. Die Versionsnummern werden aus den Dateien gelesen
(Build + 1), nicht fest vorgegeben. Findet das Skript einen Ankertext nicht genau einmal oder sind die
Zeilen schon eingetragen, bricht es ab und ändert nichts.
"""
import datetime
import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(WURZEL, 'markdown-dateien')
HEUTE = datetime.date.today().strftime('%d.%m.%Y')
VER = re.compile(r'^(Version:\s*)(\d+\.\d{2})-(\d{3})[ \t]*$', re.M)

B = 'C8205-GRAFIK_Beschreibung_A4.pdf'
P = 'C8205-GRAFIK_Pruefverfahren_A4.pdf'
U_B = 'Zweck, Fenster, Geräte, Töne, Aufruf und Grenzen des GRAFIK-Modus im Wortlaut der Quelle'
U_P = 'Wie man prüft, dass der GRAFIK-Interpreter das Soll der Beschreibung erfüllt: Läufe, Tests, Abnahme'

ALT_SATZ = 'Dieses Dokument ist **nicht** in `make_all_pdf.sh` eingetragen.'


def einfuegen_nach(text, anker_zeile_beginn, neu, name):
    """Fügt `neu` hinter der Zeile ein, die mit anker_zeile_beginn anfängt (genau eine)."""
    zeilen = text.split('\n')
    idx = [i for i, z in enumerate(zeilen) if z.startswith(anker_zeile_beginn)]
    if len(idx) != 1:
        sys.exit('ABBRUCH %s: Anker %r %d-mal gefunden (erwartet 1)' % (name, anker_zeile_beginn, len(idx)))
    zeilen[idx[0] + 1:idx[0] + 1] = neu
    return '\n'.join(zeilen)


def ersetzen(text, alt, neu, name):
    if text.count(alt) != 1:
        sys.exit('ABBRUCH %s: Text %r %d-mal gefunden (erwartet 1)' % (name, alt[:50], text.count(alt)))
    return text.replace(alt, neu)


def lies(name):
    pfad = os.path.join(WURZEL, name)
    with open(pfad, encoding='utf-8', newline='') as f:
        t = f.read()
    if '\r\n' in t:
        sys.exit('ABBRUCH %s: CRLF-Zeilenenden, Skript nur fuer LF' % name)
    if B in t and name != 'markdown-dateien/C8205-Versionierung.md':
        sys.exit('ABBRUCH %s: %s schon eingetragen' % (name, B))
    return pfad, t


def bump(text, name):
    m = VER.search(text)
    if not m:
        sys.exit('ABBRUCH %s: keine Versionszeile' % name)
    alt = '%s-%s' % (m.group(2), m.group(3))
    neu = '%s-%03d' % (m.group(2), int(m.group(3)) + 1)
    return VER.sub(lambda x: x.group(1) + neu, text, count=1), alt, neu


def main():
    anwenden = '--anwenden' in sys.argv
    ergebnis = {}      # Pfad -> neuer Text
    vers = {}          # kurzer Name -> (alt, neu)

    def bearbeite(name, kurz, fn):
        pfad, t = lies(name)
        t = fn(t)
        t, alt, neu = bump(t, name)
        ergebnis[pfad] = t
        vers[kurz] = (alt, neu)

    # 1. Stand-Satz in den zwei Quellen
    bearbeite('markdown-dateien/C8205-Interpreter-GRAFIK_Beschreibung.md', 'GRAFIK_Beschreibung',
              lambda t: ersetzen(t, ALT_SATZ, 'Das PDF dazu (`%s`) wird mit `make_all_pdf.sh` erzeugt.' % B, 'Beschreibung'))
    bearbeite('markdown-dateien/C8205-Interpreter-GRAFIK_Pruefverfahren.md', 'GRAFIK_Pruefverfahren',
              lambda t: ersetzen(t, ALT_SATZ, 'Das PDF dazu (`%s`) wird mit `make_all_pdf.sh` erzeugt.' % P, 'Pruefverfahren'))

    # 2. PDF.md: Tabelle 4.6 und Quellenliste in Abschnitt 8
    def pdf_md(t):
        t = einfuegen_nach(t, '| `C8205-Durchfuehrung_eines_Tests_A4.pdf`', [
            '| `%s` | GRAFIK-Interpreter: Beschreibung | %s | BESCHREIBUNG | INTERPRETER |' % (B, U_B),
            '| `%s` | GRAFIK-Interpreter: Prüfverfahren | %s | HANDBUCH | INTERPRETER |' % (P, U_P)], 'PDF.md 4.6')
        t = einfuegen_nach(t, '  Abschnitt 6a, erzeugt mit `PDF/pdf-layout-scripte/erzeuge_durchfuehrung_pdf.py`', [
            '- `%s` (Quelle: C8205-Interpreter-GRAFIK_Beschreibung.md; Wortlaut nach' % B,
            '  Abschnitt 6a, erzeugt mit `PDF/pdf-layout-scripte/erzeuge_grafik_beschreibung_pdf.py`, das `md2pdf.py` aufruft)',
            '- `%s` (Quelle: C8205-Interpreter-GRAFIK_Pruefverfahren.md; Wortlaut nach' % P,
            '  Abschnitt 6a, erzeugt mit `PDF/pdf-layout-scripte/erzeuge_grafik_pruefverfahren_pdf.py`, das `md2pdf.py` aufruft)'],
            'PDF.md Abschnitt 8')
        return t
    bearbeite('markdown-dateien/C8205-Interpreter-PDF.md', 'PDF', pdf_md)

    # 3. README.md, README.en.md, Projektueberblick (PDF-Tabellen)
    bearbeite('README.md', 'README.md', lambda t: einfuegen_nach(t, '| `C8205-Durchfuehrung_eines_Tests_A4.pdf`', [
        '| `%s` | Der GRAFIK-Interpreter: Zweck, Fenster, Geräte, Töne, Aufruf, Grenzen (Wortlaut der Quelle) |' % B,
        '| `%s` | Prüfverfahren des GRAFIK-Interpreters: Läufe, Tests, Abnahme |' % P], 'README.md'))
    bearbeite('README.en.md', 'README.en.md', lambda t: einfuegen_nach(t, '| `C8205-Durchfuehrung_eines_Tests_A4.pdf`', [
        '| `%s` | The GRAFIK interpreter: purpose, windows, devices, sounds, call, limits (in the wording of the source) |' % B,
        '| `%s` | Test procedure for the GRAFIK interpreter: runs, tests, acceptance |' % P], 'README.en.md'))
    bearbeite('markdown-dateien/C8205-Interpreter-Projektueberblick.md', 'Projektueberblick',
              lambda t: einfuegen_nach(t, '| `C8205-Durchfuehrung_eines_Tests_A4.pdf`', [
                  '| `%s` | Der GRAFIK-Interpreter: Zweck, Fenster, Geräte, Töne, Aufruf und Grenzen im Wortlaut der Quelle |' % B,
                  '| `%s` | Prüfverfahren des GRAFIK-Interpreters: Läufe, Tests, Abnahme im Wortlaut der Quelle |' % P],
                  'Projektueberblick'))

    # 4. Versionierung: neuer Eintrag (neueste Zeile zuerst) und eigene Versionszeile
    def versionierung(t):
        nr_alt = VER.search(t)
        nr_neu = '%s-%03d' % (nr_alt.group(2), int(nr_alt.group(3)) + 1)
        teile = '; '.join('`%s` %s' % (k, v[1]) for k, v in vers.items())
        zeile = ('| %s | %s | Stufe 6 (A6-5): Die zwei GRAFIK-PDFs (`%s`, `%s`) stehen in `make_all_pdf.sh` '
                 '(neue Skripte `erzeuge_grafik_beschreibung_pdf.py` und `erzeuge_grafik_pruefverfahren_pdf.py`); '
                 'der Satz „nicht in `make_all_pdf.sh` eingetragen“ in den zwei Quellen ist entfallen; Zeilen '
                 'in `PDF.md` (4.6, Abschnitt 8), den PDF-Tabellen von `README.md`, `README.en.md` und '
                 '`Projektueberblick` ergänzt. Neue Versionen: %s. Kein Code geändert. |' % (nr_neu, HEUTE, B, P, teile))
        ids = re.findall(r'^\| (\d+\.\d{2}-\d{3}) \|', t, re.M)
        if not ids:
            sys.exit('ABBRUCH Versionierung: keine Tabellenzeilen')
        hoechste = max(ids, key=lambda s: tuple(int(x) for x in re.split(r'[.-]', s)))
        zl = t.split('\n')
        i = [k for k, z in enumerate(zl) if z.startswith('| %s |' % hoechste)]
        if len(i) != 1:
            sys.exit('ABBRUCH Versionierung: Zeile %s %d-mal' % (hoechste, len(i)))
        zl.insert(i[0], zeile)
        return '\n'.join(zl)
    pfad, t = lies('markdown-dateien/C8205-Versionierung.md')
    t = versionierung(t)
    t, alt, neu = bump(t, 'Versionierung')
    ergebnis[pfad] = t
    vers['Versionierung'] = (alt, neu)

    print('%-24s %-10s -> %s' % ('Datei', 'alt', 'neu'))
    for k, (a, n) in vers.items():
        print('%-24s %-10s -> %s' % (k, a, n))
    if not anwenden:
        print('\nProbelauf: nichts geschrieben. Mit --anwenden schreiben.')
        return
    for pfad, t in ergebnis.items():
        with open(pfad, 'w', encoding='utf-8', newline='') as f:
            f.write(t)
    print('\ngeschrieben: %d Dateien. Danach beide GRAFIK-PDFs neu erzeugen:' % len(ergebnis))
    print('  ./make_pdf.sh erzeuge_grafik_beschreibung_pdf.py ; ./make_pdf.sh erzeuge_grafik_pruefverfahren_pdf.py')


if __name__ == '__main__':
    main()
