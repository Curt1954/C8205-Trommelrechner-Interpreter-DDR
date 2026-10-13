#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt C8205-Testuebersicht_A4.pdf aus test_tabelle.md.

Gestaltung nach C8205-Interpreter-PDF.md (Version 0.03-003):
  - A4 hoch, Rand 30 pt, DejaVu Sans / Bold / Mono (Abschnitte 1, 2)
  - Deckblatt auf Seite 1 ohne Kopf-/Fusszeile (Abschnitt 4.1 bis 4.3)
  - Kopf- und Fusszeile ab Seite 2 (Abschnitte 3, 3a.1), Textelemente (3a.2)
  - Tabellenstil: dunkler Kopf, kein Zebramuster, kein Gitter, Kopf wiederholt sich,
    letzte Zeile nie allein auf der Folgeseite (3a.3)
  - 'Seite X / Y' und 'Umfang' stammen aus einem zweiten Durchlauf (4.7)
Die Version der Quelle wird aus der Zeile 'Version: y.xx-zzz' der MD-Datei gelesen. Fehlt sie, bricht das
Skript mit einer Fehlermeldung ab und erzeugt kein PDF (4.3). Der Stand ist das Erzeugungsdatum.

Aufruf (aus beliebigem Verzeichnis):
    python3 erzeuge_testuebersicht_pdf.py [--md test_tabelle.md] [--pdf C8205-Testuebersicht_A4.pdf]
                                          [--stand TT.MM.JJJJ]
Standard: test_tabelle.md wird im Verzeichnis des Skripts oder darueber gesucht (CSV/); das PDF entsteht
neben der MD-Quelle. Das Skript benoetigt nur reportlab und die DejaVu-Schriften, nicht pdflib.py oder md2pdf.py.
Der Stand ist das Erzeugungsdatum, ausser --stand setzt ihn (z. B. um den Stand eines vorhandenen PDFs zu
reproduzieren).
"""
import argparse
import datetime
import os
import re
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

# --- Deckblattdaten dieses PDFs (Zeile in Abschnitt 4.6 der Richtlinie) ----------------------------------
PDF_NAME = "C8205-Testuebersicht_A4.pdf"
TITEL = "Testübersicht"
UNTERTITEL = "Alle Tests mit Inhalt, Geräte- und Vergleichsdateien und zugehörigem ASM-Quelltext"
ART = "REFERENZ"
BEREICH = "INTERPRETER"
KENNUNG = "C 8205 · Simulation eines DDR-Kleinrechners von 1968"
AUTOR = "C8205-Interpreter-Projekt"
SKRIPT = os.path.basename(__file__)
AKTUALITAET = ("Maßgeblich bleibt die Quelldatei. Dieses PDF wird nicht automatisch nachgeführt: Es ist aktuell, "
               "solange die Version oben mit der Versionszeile der Quelldatei übereinstimmt.")

# --- Schrift (Abschnitt 2) ------------------------------------------------------------------------------------
FD = "/usr/share/fonts/truetype/dejavu/"
for name, datei in (("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"), ("DV-I", "DejaVuSans-Oblique.ttf"),
                    ("DV-BI", "DejaVuSans-BoldOblique.ttf"), ("DVM", "DejaVuSansMono.ttf"),
                    ("DVM-B", "DejaVuSansMono-Bold.ttf"), ("DVM-I", "DejaVuSansMono-Oblique.ttf"),
                    ("DVM-BI", "DejaVuSansMono-BoldOblique.ttf")):
    pdfmetrics.registerFont(TTFont(name, FD + datei))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")
pdfmetrics.registerFontFamily("DVM", normal="DVM", bold="DVM-B", italic="DVM-I", boldItalic="DVM-BI")

# --- Farben (4.1) ---------------------------------------------------------------------------------------------
INK = colors.HexColor("#1F2937")
GREY = colors.HexColor("#6B7280")
LINE = colors.HexColor("#D1D5DB")
FILL = colors.HexColor("#F3F4F6")
DARK = colors.HexColor("#374151")

# --- Geometrie (Abschnitte 1, 3a.1) --------------------------------------------------------------------------
W, H = A4
RAND = 30.0
FRAME_W = W - 2 * RAND                   # 535,28 pt
FRAME_TOP, FRAME_BOTTOM = 56.0, 44.0     # Satzspiegel: 56 pt vom oberen bis 44 pt vom unteren Rand
FRAME_H = H - FRAME_TOP - FRAME_BOTTOM   # 741,89 pt
PAD_X, PAD_Y = 4.5, 3.0                  # Zellen-Innenabstand (3a.3)

# Spaltenbreiten der Testtabelle (Summe = FRAME_W); Umbruch nach Leerzeichen, '/', '_' und '-'
SPALTENBREITEN = [105.0, 138.0, 96.0, 108.28, 88.0]

S_FLIESS = ParagraphStyle("fliess", fontName="DV", fontSize=9.2, leading=12.6, textColor=INK, spaceAfter=4.5,
                          allowWidows=0, allowOrphans=0)
S_TAB = ParagraphStyle("tab", fontName="DV", fontSize=8.5, leading=10.8, textColor=INK)
S_TABKOPF = ParagraphStyle("tabkopf", parent=S_TAB, fontName="DV-B", textColor=colors.white)
S_TABFOLGE = ParagraphStyle("tabfolge", parent=S_TAB, spaceBefore=3)   # weiterer Eintrag in derselben Zelle

VERSION_RE = re.compile(r"^Version: (\d+\.\d{2}-\d{3})$", re.M)


# --- Quelle lesen --------------------------------------------------------------------------------------------
def zellen(zeile):
    z = zeile.strip()
    if z.startswith("|"):
        z = z[1:]
    if z.endswith("|") and not z.endswith("\\|"):
        z = z[:-1]
    return [t.replace("\\|", "|").strip().replace("<br>", "\n") for t in re.split(r"(?<!\\)\|", z)]


def lies_quelle(pfad):
    """-> (Version, [('absatz', text) | ('tabelle', [zeilen])])"""
    if not os.path.exists(pfad):
        sys.exit(f"Fehler: Quelldatei nicht gefunden: {pfad}")
    with open(pfad, encoding="utf-8") as f:
        text = f.read()
    m = VERSION_RE.search(text)
    if not m:
        sys.exit(f"Fehler: {os.path.basename(pfad)} enthält keine Zeile 'Version: y.xx-zzz' "
                 "(C8205-Interpreter-PDF.md, 4.3). Es wird kein PDF erzeugt.")
    elemente = []
    for block in re.split(r"\n\s*\n", text[m.end():].strip("\n")):
        zl = [z for z in block.split("\n") if z.strip()]
        if not zl:
            continue
        if zl[0].lstrip().startswith("|"):
            zeilen = [zellen(z) for z in zl]
            zeilen = [z for z in zeilen if not all(re.fullmatch(r":?-+:?", c) for c in z)]  # Trennzeile
            elemente.append(("tabelle", zeilen))
        else:
            elemente.append(("absatz", " ".join(z.strip() for z in zl)))
    return m[1], elemente


def inline(text):
    """Escapen und `code` als Sans Mono."""
    t = escape(text)
    return re.sub(r"`([^`]+)`", lambda m: f'<font name="DVM" size="8.3">{m[1]}</font>', t)


# --- Umbruch von Dateinamen und Pfaden ----------------------------------------------------------------------
def umbrechen(text, breite, font="DV", size=8.5):
    """Zeilen (Liste); Umbruchstellen nach Leerzeichen, '/', '_' und '-' (reportlab bricht an '-' und '/'
    nicht um), sonst Zeichenumbruch als Notbehelf."""
    ergebnis = []
    for zeile in text.split("\n"):
        aktuell = ""
        for tok in re.findall(r"[^ /_\-]*[ /_\-]|[^ /_\-]+", zeile):
            if stringWidth((aktuell + tok).rstrip(), font, size) <= breite:
                aktuell += tok
                continue
            if aktuell:
                ergebnis.append(aktuell.rstrip())
            aktuell = tok
            while stringWidth(aktuell, font, size) > breite and len(aktuell) > 1:
                k = len(aktuell)
                while k > 1 and stringWidth(aktuell[:k], font, size) > breite:
                    k -= 1
                if "." in aktuell[:k] and aktuell.rfind(".", 0, k) > 1:
                    k = aktuell.rfind(".", 0, k) + 1       # lieber hinter dem Punkt trennen (Dateiendung)
                ergebnis.append(aktuell[:k])
                aktuell = aktuell[k:]
        ergebnis.append(aktuell.rstrip())
    return ergebnis


# --- Tabelle: Zeilenhöhen berechnen und seitenweise aufteilen (3a.3) -----------------------------------------
def tabellen_bausteine(zeilen):
    """-> (Kopfzellen, Datenzellen, Kopfhöhe, Zeilenhöhen, Breiten)"""
    kopf = zeilen[0]
    n = len(kopf)
    breiten = SPALTENBREITEN if n == len(SPALTENBREITEN) else [FRAME_W / n] * n
    innen = [b - 2 * PAD_X for b in breiten]

    def zelle(text, i):
        """Jede Zeile des Zelltexts (z. B. mehrere Dateien) ist ein eigener Absatz."""
        absaetze = [Paragraph("<br/>".join(escape(z) for z in umbrechen(eintrag, innen[i] - 0.5)),
                              S_TAB if n == 0 else S_TABFOLGE)
                    for n, eintrag in enumerate(text.split("\n"))]
        return absaetze if len(absaetze) > 1 else absaetze[0]

    kopfzellen = [Paragraph(escape(k), S_TABKOPF) for k in kopf]
    daten = [[zelle(c, i) for i, c in enumerate(z)] for z in zeilen[1:]]

    # Zeilenhöhen misst reportlab an einer Probetabelle mit demselben Stil (Absatzabstände, Innenabstand)
    probe = Table([kopfzellen] + daten, colWidths=breiten, hAlign="LEFT")
    probe.setStyle(tabellenstil())
    probe.wrap(FRAME_W, 10 ** 6)
    hoehen = list(probe._rowHeights)
    return kopfzellen, daten, hoehen[0], hoehen[1:], breiten


def seitenteile(kopfhoehe, hoehen, platz_erste, platz):
    """Zeilenindizes je Seite; die letzte Zeile steht nie allein auf der Folgeseite."""
    teile, akt, belegt, frei = [], [], kopfhoehe, platz_erste
    for i, h in enumerate(hoehen):
        if akt and belegt + h > frei:
            teile.append(akt)
            akt, belegt, frei = [], kopfhoehe, platz
        akt.append(i)
        belegt += h
    teile.append(akt)
    if len(teile) > 1 and len(teile[-1]) == 1 and len(teile[-2]) >= 2:
        teile[-1].insert(0, teile[-2].pop())
    return teile


def tabellenstil():
    return TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DV"), ("FONTSIZE", (0, 0), (-1, -1), 8.5),   # Tabellenvorgabe sonst Helvetica
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), PAD_X), ("RIGHTPADDING", (0, 0), (-1, -1), PAD_X),
        ("TOPPADDING", (0, 0), (-1, -1), PAD_Y), ("BOTTOMPADDING", (0, 0), (-1, -1), PAD_Y),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE),   # Zeilenlinie
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),         # Rahmen; kein Zebramuster, kein Gitter
    ])


def tabelle_seite(kopfzellen, daten, kopfhoehe, hoehen, breiten, indizes):
    t = Table([kopfzellen] + [daten[i] for i in indizes], colWidths=breiten,
              rowHeights=[kopfhoehe] + [hoehen[i] for i in indizes], hAlign="LEFT")
    t.setStyle(tabellenstil())
    return t


# --- Deckblatt (Abschnitt 4.2) --------------------------------------------------------------------------------
def deckblatt(c, ctx):
    M = 56.7
    x0, x1 = M, W - M
    spalte = x1 - x0
    ytop = H - M
    asc = 0.93                                   # Oberlänge der DejaVu-Schrift (Anteil der Schriftgröße)

    # Zone A: Kennung und Bereichsetikett
    lab = BEREICH.upper()
    lw, bh = stringWidth(lab, "DV-B", 8) + 12, 8 * 1.17 + 6
    base = ytop - 3 - 8 * asc
    c.setFillColor(DARK)
    c.roundRect(x1 - lw, ytop - bh, lw, bh, 2, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("DV-B", 8)
    c.drawString(x1 - lw + 6, base, lab)
    c.setFillColor(GREY)
    c.setFont("DV", 9)
    c.drawString(x0, base, KENNUNG)
    c.setStrokeColor(DARK)
    c.setLineWidth(2)
    c.line(x0, ytop - 22, x1, ytop - 22)

    # Zone B: Dokumentart, Titel, Untertitel
    y = H - 0.27 * H                             # Oberkante der Überzeile
    c.saveState()                                # Zeichenabstand gilt nur für die Überzeile
    t = c.beginText(x0, y - 9 * asc)
    t.setFont("DV-B", 9)
    t.setFillColor(GREY)
    t.setCharSpace(1)
    t.textOut(ART)
    c.drawText(t)
    c.restoreState()
    y -= 9 + 8
    groesse = 26
    zeilen = simpleSplit(TITEL, "DV-B", groesse, spalte)
    if len(zeilen) > 2:
        groesse = 22
        zeilen = simpleSplit(TITEL, "DV-B", groesse, spalte)
        if len(zeilen) > 2:
            sys.exit("Fehler: Titel passt nicht in zwei Zeilen (4.3: Titel kürzen).")
    lead = 31 * groesse / 26
    c.setFillColor(INK)
    c.setFont("DV-B", groesse)
    for i, z in enumerate(zeilen):
        c.drawString(x0, y - groesse * asc - (lead - groesse) / 2 - i * lead, z)
    y -= len(zeilen) * lead + 10
    sub = simpleSplit(UNTERTITEL, "DV", 12, spalte)
    if len(sub) > 2:
        sys.exit("Fehler: Untertitel passt nicht in zwei Zeilen (4.3).")
    c.setFillColor(GREY)
    c.setFont("DV", 12)
    for i, z in enumerate(sub):
        c.drawString(x0, y - 12 * asc - 2 - i * 16, z)

    # Zone F: Fuß (von unten gerechnet)
    fuss_y = M
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.line(x0, fuss_y + 12, x1, fuss_y + 12)
    c.setFillColor(GREY)
    c.setFont("DV", 7.5)
    c.drawString(x0, fuss_y, AUTOR)
    c.setFont("DVM", 7.5)
    c.drawRightString(x1, fuss_y, PDF_NAME)

    # Zone E: Aktualitätshinweis (Unterkante 24 pt über der Linie von Zone F)
    zl = simpleSplit(AKTUALITAET, "DV", 8.5, spalte - 3 - 16)
    eh = len(zl) * 11.5 + 16
    ey = fuss_y + 12 + 24
    c.setFillColor(FILL)
    c.rect(x0, ey, spalte, eh, stroke=0, fill=1)
    c.setFillColor(DARK)
    c.rect(x0, ey, 3, eh, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("DV", 8.5)
    for i, z in enumerate(zl):
        c.drawString(x0 + 3 + 8, ey + eh - 8 - 8.5 * asc - i * 11.5, z)

    # Zone D: Angabenblock (Unterkante 14 pt über Zone E)
    zeilen_d = [("Quelle", ctx["md_name"], "mono", ctx["version"]),
                ("Stand", ctx["stand"], "sans", None),
                ("Umfang", f"{ctx['gesamt']} Seiten, A4 hoch", "sans", None),
                ("Erzeugt mit", SKRIPT, "mono", None)]
    zh = 4 + 11 + 4
    yd = ey + eh + 14
    c.setLineWidth(0.5)
    for i, (bez, wert, art, rechts) in enumerate(reversed(zeilen_d)):
        unten = yd + i * zh
        oben = unten + zh
        c.setStrokeColor(LINE)
        c.line(x0, oben, x1, oben)
        if i == 0:
            c.line(x0, unten, x1, unten)
        grund = unten + 4 + 8.5 * 0.26
        c.setFillColor(GREY)
        c.setFont("DV", 8.5)
        c.drawString(x0, grund, bez)
        c.setFillColor(INK)
        c.setFont("DVM" if art == "mono" else "DV", 8 if art == "mono" else 8.5)
        c.drawString(x0 + 90, grund, wert)
        if rechts:
            c.setFont("DV", 8.5)
            c.drawRightString(x1, grund, rechts)


# --- Kopf- und Fußzeile (Abschnitte 3, 3a.1) -----------------------------------------------------------------
def kopf_fuss(c, ctx):
    c.setFillColor(INK)
    c.setFont("DV-B", 11)
    c.drawString(RAND, H - 38, f"C 8205 – {TITEL}")
    c.setFillColor(GREY)
    c.setFont("DV", 8)
    c.drawString(RAND, H - 50, f"Quelle: {ctx['md_name']} · im Wortlaut der Quelle")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.line(RAND, H - 54.5, W - RAND, H - 54.5)
    c.line(RAND, 41, W - RAND, 41)
    c.setFont("DV", 7.5)
    c.drawString(RAND, 28, f"{AUTOR} · Stand {ctx['stand']}")
    c.drawRightString(W - RAND, 28, f"Seite {c.getPageNumber()} / {ctx['gesamt']}")


# --- Aufbau ---------------------------------------------------------------------------------------------------
def baue(md_pfad, pdf_pfad, version, elemente, gesamt, stand):
    ctx = {"md_name": os.path.basename(md_pfad), "version": version, "stand": stand, "gesamt": gesamt}
    doc = BaseDocTemplate(pdf_pfad, pagesize=A4, title=TITEL, author=AUTOR,
                          subject=f"{ART} · {ctx['md_name']} {version}", creator=SKRIPT,
                          initialFontName="DV", initialFontSize=9.2,   # kein Helvetica als Vorgabeschrift
                          leftMargin=RAND, rightMargin=RAND, topMargin=FRAME_TOP, bottomMargin=FRAME_BOTTOM)
    frame = Frame(RAND, FRAME_BOTTOM, FRAME_W, FRAME_H, leftPadding=0, rightPadding=0, topPadding=0,
                  bottomPadding=0, id="satzspiegel")
    klein = Frame(0, 0, 1, 1, id="leer")
    doc.addPageTemplates([
        PageTemplate(id="deckblatt", frames=[klein], onPage=lambda c, d: deckblatt(c, ctx)),
        PageTemplate(id="inhalt", frames=[frame], onPage=lambda c, d: kopf_fuss(c, ctx)),
    ])
    story = [NextPageTemplate("inhalt"), PageBreak()]
    belegt = 0.0
    tabelle = None
    for art, inhalt in elemente:
        if art == "absatz":
            p = Paragraph(inline(inhalt), S_FLIESS)
            belegt += p.wrap(FRAME_W, 10000)[1] + S_FLIESS.spaceAfter
            story.append(p)
        else:
            tabelle = inhalt
    if tabelle:
        story.append(Spacer(1, 6))
        belegt += 6
        kopfz, daten, kopfh, hoehen, breiten = tabellen_bausteine(tabelle)
        teile = seitenteile(kopfh, hoehen, FRAME_H - belegt - 2, FRAME_H - 2)
        assert sum(len(t) for t in teile) == len(daten), "Tabellenzeilen gingen verloren"
        for n, idx in enumerate(teile):
            if n:
                story.append(PageBreak())
            story.append(tabelle_seite(kopfz, daten, kopfh, hoehen, breiten, idx))
    doc.build(story)
    return doc.page, (len(daten) if tabelle else 0)


QUELLE_NAME = "test_tabelle.md"


def finde_quelle(hier):
    """test_tabelle.md im Verzeichnis des Skripts oder in einem Verzeichnis darueber (CSV/)."""
    d = hier
    while True:
        pfad = os.path.join(d, QUELLE_NAME)
        if os.path.isfile(pfad):
            return pfad
        eltern = os.path.dirname(d)
        if eltern == d:
            return os.path.join(hier, QUELLE_NAME)          # nicht gefunden: lies_quelle meldet den Fehler
        d = eltern


def main():
    hier = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md", default=None, help=f"Quelle (Standard: {QUELLE_NAME} im Skriptverzeichnis oder darueber)")
    ap.add_argument("--pdf", default=None, help=f"Ausgabe (Standard: {PDF_NAME} neben der MD-Quelle)")
    ap.add_argument("--stand", default=None, help="TT.MM.JJJJ; Standard: Erzeugungsdatum")
    a = ap.parse_args()
    a.md = a.md or finde_quelle(hier)
    a.pdf = a.pdf or os.path.join(os.path.dirname(os.path.abspath(a.md)), PDF_NAME)

    version, elemente = lies_quelle(a.md)
    stand = a.stand or datetime.date.today().strftime("%d.%m.%Y")
    if not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", stand):
        sys.exit(f"Fehler: --stand muss TT.MM.JJJJ sein, nicht {stand!r}.")
    seiten, zeilen = baue(a.md, a.pdf, version, elemente, 0, stand)           # 1. Durchlauf: Seitenzahl
    seiten2, _ = baue(a.md, a.pdf, version, elemente, seiten, stand)         # 2. Durchlauf: mit "Seite X / Y"
    if seiten2 != seiten:
        sys.exit(f"Fehler: Seitenzahl schwankt ({seiten} / {seiten2}).")
    print(f"geschrieben: {a.pdf}")
    print(f"{seiten} Seiten, {zeilen} Tabellenzeilen, Quelle {os.path.basename(a.md)} Version {version}, Stand {stand}")


if __name__ == "__main__":
    main()
