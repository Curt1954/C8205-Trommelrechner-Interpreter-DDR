# -*- coding: utf-8 -*-
"""Erzeugt "Bausteininterpretiersystem BIS"/markdown-dateien/C8205-BIS_A4.pdf nach C8205-Interpreter-PDF.md (4.6, 6a, 3a).

Quelle:  Bausteininterpretiersystem BIS/markdown-dateien/C8205-Interpreter-BIS.md   (Wortlaut-PDF, Abschnitt 6a)
Aufruf:  python3 erzeuge_bis_pdf.py [--stand TT.MM.JJJJ] [--quelle PFAD] [--ziel PFAD]

Das Skript legt die Deckblattdaten aus PDF.md 4.6 fest (Titel, Untertitel, Art, Bereich) und ruft
md2pdf.convert() auf; Schriften, Kopf-/Fusszeile, Deckblatt und Tabellenstil kommen aus pdflib.py.
Version der Quelle und Stand (Erzeugungsdatum) werden beim Erzeugen gelesen, nicht von Hand gesetzt.
Der Skriptname erscheint auf dem Deckblatt in der Zeile "Erzeugt mit" (PDF.md 4.2).

Das PDF liegt, wie die Quelle, in "Bausteininterpretiersystem BIS/markdown-dateien/" (C8205-Projektstruktur.md,
Abschnitt 3a). Die zweite Datei dieses Ordners, C8205-Interpreter-Objektdatei_Listing.md, bekommt kein eigenes
PDF (Entscheidung des Projektinhabers, 12.10.2026); sie ist nicht Quelle dieses Skripts.
Der Umbruch folgt unveraendert md2pdf.py.
"""
import os
import sys
import argparse

HIER = os.path.dirname(os.path.abspath(__file__))


def _finde_md2pdf_ordner():
    """md2pdf.py liegt in PDF/pdf-layout-scripte/ (oder neben diesem Skript) und bringt pdflib.py eingebettet mit."""
    d = HIER
    while True:
        for ordner in (d, os.path.join(d, 'PDF', 'pdf-layout-scripte')):
            if os.path.isfile(os.path.join(ordner, 'md2pdf.py')):
                return ordner
        p = os.path.dirname(d)
        if p == d:
            sys.exit('md2pdf.py oberhalb von %s nicht gefunden (erwartet in PDF/pdf-layout-scripte/).' % HIER)
        d = p


sys.path.insert(0, _finde_md2pdf_ordner())
import md2pdf as M                             # zuerst: registriert das eingebettete pdflib
import pdflib as L

# ------------------------------------------------------------------ Deckblattdaten (PDF.md 4.6)
QUELLE_NAME = 'C8205-Interpreter-BIS.md'
QUELLE_ORDNER = os.path.join('Bausteininterpretiersystem BIS', 'markdown-dateien')
PDF_NAME = 'C8205-BIS_A4.pdf'
TITEL = 'Bausteininterpretationssystem'
UNTERTITEL = 'Bausteine, Kleines Eingabeprogramm (KEP) und Minimalprogramm'
ART = 'BESCHREIBUNG'
BEREICH = 'BIS'
SKRIPT = os.path.basename(__file__)

# ------------------------------------------------------------------ Deckblatt: Zeile "Erzeugt mit" (PDF.md 4.2)
_zeichne_deckblatt = L.zeichne_deckblatt


def _deckblatt_mit_skript(c, d, total):
    _zeichne_deckblatt(c, dict(d, erzeugt_mit=SKRIPT), total)


L.zeichne_deckblatt = _deckblatt_mit_skript


# ------------------------------------------------------------------ Quelle suchen
def finde_quelle():
    """Quelle: erster Ordner ueber diesem Skript, der <QUELLE_ORDNER>/<Quelle> enthaelt."""
    d = HIER
    while True:
        pfad = os.path.join(d, QUELLE_ORDNER, QUELLE_NAME)
        if os.path.isfile(pfad):
            return pfad
        p = os.path.dirname(d)
        if p == d:
            sys.exit('Quelle %s oberhalb von %s nicht gefunden (Schalter --quelle verwenden).'
                     % (os.path.join(QUELLE_ORDNER, QUELLE_NAME), HIER))
        d = p


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--quelle', default=None, help='Vorgabe: %s/%s' % (QUELLE_ORDNER.replace(os.sep, '/'), QUELLE_NAME))
    ap.add_argument('--ziel', default=None, help='Vorgabe: neben der Quelle (%s)' % PDF_NAME)
    ap.add_argument('--stand', default=L.heute(), help='TT.MM.JJJJ; Vorgabe: Erzeugungsdatum')
    a = ap.parse_args()
    src = a.quelle or finde_quelle()
    if not os.path.isfile(src):
        sys.exit('Quelle nicht gefunden: %s' % src)
    ziel = a.ziel or os.path.join(os.path.dirname(os.path.abspath(src)), PDF_NAME)
    n = M.convert(src, ziel, TITEL, UNTERTITEL, ART, BEREICH, a.stand, quelle_name=QUELLE_NAME)
    print('Abschnitte:', n)
    for x in M.NOTES:
        print('HINWEIS:', x)
    print('geschrieben:', ziel)


if __name__ == '__main__':
    main()
