#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nachführung der Projektstruktur (Abgleich mit dem tree-Auszug vom 19.10.2026).

Aufruf (im Projektordner):  python3 testscripte/nachfuehrung_projektstruktur.py            # Probelauf, schreibt nichts
                            python3 testscripte/nachfuehrung_projektstruktur.py --anwenden # schreibt die zwei Dateien

Ändert C8205-Projektstruktur.md (vier Zeilen: ton/, pult/, c-module/, testscripte/; Build +1) und trägt in
C8205-Versionierung.md einen Eintrag ein (neueste Zeile zuerst; Build +1). Versionen werden aus den Dateien gelesen.
Findet das Skript einen Ankertext nicht genau einmal oder ist alles schon eingetragen, bricht es ab und ändert nichts.
"""
import datetime
import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(WURZEL, 'markdown-dateien')
HEUTE = datetime.date.today().strftime('%d.%m.%Y')
VER = re.compile(r'^(Version:\s*)(\d+\.\d{2})-(\d{3})[ \t]*$', re.M)
MARKE = '`bild/` (`c8205_bedienpult.png`'          # nur in der neuen pult/-Zeile

AENDERUNGEN = [
    ('ton/',
     '`toene_rechner_stanzer/` (Netz ein/aus, Grundgeräusch, Stanzer)',
     '`toene_rechner_stanzer/` (Stanzerklänge `ls_motor.wav` und `ls_dauerstanzen.wav`; die dortigen Kopien von Netz ein/aus und '
     'Grundgeräusch liest kein Programm), die drei Klänge des Rechners `netz_ein_fade_in.wav`, `netz_aus_fade_out.wav` und '
     '`rechner_grundgeraeusch.wav` liegen im Ordner `ton/` selbst'),
    ('pult/',
     'Bilder und Manifest des Bedienpult-Fensters (`pult_manifest.json`)',
     'Bilder und Manifest des Bedienpult-Fensters: `pult_manifest.json`, ' + MARKE + ', das Bild des Pults) und `grafiken/` '
     '(Lampen, Dioden und Schlüsselstellungen als PNG)'),
    ('c-module/',
     'Testrahmen `testframe_*.c`, `Makefile`;',
     'Testrahmen `testframe_*.c`, `Makefile`; `c8205_api.h` (Exportmakro der gemeinsamen Bibliothek), `plattform.h` (dünne Schicht '
     'für Linux und Windows, nur von `trommel.c` eingebunden; der Windows-Zweig ist nicht übersetzt und nicht getestet) und '
     '`build_msvc.bat` (Bau von `trommel.dll` mit Visual Studio, nicht getestet);'),
    ('testscripte/',
     '`grafik_tastatur_tests.py` u. a. |',
     '`grafik_tastatur_tests.py` u. a. Dazu das Messwerkzeug `k0_schatten_haken.py` (zu Interpreter 0.03-016, nur auf eine Kopie '
     'anzuwenden) und die Prüfung des Eingabeprogramms `r300_eingabe`: `r300_eingabe_erzeugen.py` (erzeugt Quelltext, Testauftrag, '
     'K0-Eingabedatei und die Klickspur `Tests/r300_eingabe_klickspur.txt`, die derzeit nicht im Projekt liegt), '
     '`r300_eingabe_trockenlauf.py` (ohne Tkinter), `r300_eingabe_grafik.sh`/`.bat` (GRAFIK-Lauf mit `--HWCHECK` und `--WIEDERGABE`), '
     '`r300_eingabe_lauf_und_auswertung.sh`/`.bat` (Lauf und Auswertung in einem Schritt) und `r300_eingabe_log_auswerten.py` '
     '(wertet das Debug-Log aus) |'),
]


def lies(name):
    pfad = os.path.join(MD, name)
    with open(pfad, encoding='utf-8', newline='') as f:
        t = f.read()
    if '\r\n' in t:
        sys.exit('ABBRUCH %s: CRLF-Zeilenenden, Skript nur fuer LF' % name)
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
    pfad_ps, ps = lies('C8205-Projektstruktur.md')
    if MARKE in ps:
        sys.exit('ABBRUCH: die Projektstruktur ist schon nachgefuehrt (pult/-Zeile enthaelt bild/)')
    for ordner, alt, neu in AENDERUNGEN:
        if ps.count(alt) != 1:
            sys.exit('ABBRUCH Zeile %s: Ankertext %r %d-mal gefunden (erwartet 1)' % (ordner, alt[:60], ps.count(alt)))
        ps = ps.replace(alt, neu)
    ps, ps_alt, ps_neu = bump(ps, 'Projektstruktur')

    pfad_v, v = lies('C8205-Versionierung.md')
    m = VER.search(v)
    nr = '%s-%03d' % (m.group(2), int(m.group(3)) + 1)
    zeile = ('| %s | %s | Stufe 6 (A6-5): Projektstruktur gegen den tree-Auszug vom 19.10.2026 abgeglichen und nachgeführt '
             '(`Projektstruktur` %s): Zeilen zu `ton/` (die drei Rechnerklänge liegen im Hauptordner, `toene_rechner_stanzer/` '
             'enthält die Stanzerklänge), `pult/` (`bild/`, `grafiken/`), `c-module/` (`c8205_api.h`, `plattform.h`, '
             '`build_msvc.bat`) und `testscripte/` (`k0_schatten_haken.py`, `r300_eingabe_*`). Kein Code geändert. |' % (nr, HEUTE, ps_neu))
    ids = re.findall(r'^\| (\d+\.\d{2}-\d{3}) \|', v, re.M)
    if not ids:
        sys.exit('ABBRUCH Versionierung: keine Tabellenzeilen')
    hoechste = max(ids, key=lambda s: tuple(int(x) for x in re.split(r'[.-]', s)))
    zl = v.split('\n')
    i = [k for k, z in enumerate(zl) if z.startswith('| %s |' % hoechste)]
    if len(i) != 1:
        sys.exit('ABBRUCH Versionierung: Zeile %s %d-mal' % (hoechste, len(i)))
    zl.insert(i[0], zeile)
    v = '\n'.join(zl)
    v, v_alt, v_neu = bump(v, 'Versionierung')

    print('%-16s %-10s -> %s' % ('Datei', 'alt', 'neu'))
    print('%-16s %-10s -> %s' % ('Projektstruktur', ps_alt, ps_neu))
    print('%-16s %-10s -> %s' % ('Versionierung', v_alt, v_neu))
    print('geaenderte Zeilen der Projektstruktur: ' + ', '.join(a[0] for a in AENDERUNGEN))
    if not anwenden:
        print('\nProbelauf: nichts geschrieben. Mit --anwenden schreiben.')
        return
    for pfad, t in ((pfad_ps, ps), (pfad_v, v)):
        with open(pfad, 'w', encoding='utf-8', newline='') as f:
            f.write(t)
    print('\ngeschrieben: 2 Dateien. Danach das PDF der Projektstruktur neu erzeugen:  ./make_pdf.sh erzeuge_projektstruktur_pdf.py')


if __name__ == '__main__':
    main()
