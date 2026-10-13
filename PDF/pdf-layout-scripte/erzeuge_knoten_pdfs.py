#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erzeugt aus denselben .md-Quellen beide PDFs des Knotenautomaten nach C8205-Interpreter-PDF.md:

    C8205-Knotengraph_A4.pdf    Ablaufplan (Graphviz, feste Kachelung 2 Spalten, Kacheln in Helvetica)
    C8205-Knotentabellen_A4.pdf Knotentabelle, Variablentabelle T2, Lesart (DejaVu Sans);
                                Layout und Deckblatt: erzeuge_knotentabellen_pdf.py (die Funktion knotentabellen() unten
                                ist davon abgelöst und wird nicht mehr aufgerufen)

Quellen (im Ordner --mdverz):
    C8205-Interpreter-Eingänge_der_Knoten.md      Knotentabelle
    C8205-Interpreter-Beschreibung_der_Knoten.md  Variablentabelle T2

Beide PDFs entstehen aus EINEM Einlesen, damit Zahlen, Stand und Inhalt nicht auseinanderlaufen.
Optional (--interp c8205_interp.py) wird das Einlesen gegen load_graph()/load_t2() des Interpreters geprüft.

Aufruf:  python3 erzeuge_knoten_pdfs.py --mdverz markdown-dateien --ausgabe PDF [--interp c8205_interp.py]
"""

# ---------------------------------------------------------------------------------------------
# Eigenstaendig: Die Module pdflib.py, erzeuge_knotentabellen_pdf.py sind unten als Quelltext eingebettet und werden
# beim ersten Import aus diesem Skript geladen. Es werden keine weiteren .py-Dateien daneben gebraucht.
# ---------------------------------------------------------------------------------------------
import importlib.abc as _iabc
import importlib.util as _iutil
import sys as _sys

_EINGEBETTET = {
    'pdflib': ('pdflib.py', r'''# -*- coding: utf-8 -*-
"""Bausteine fuer das Testhandbuch (reportlab), nach C8205-Interpreter-PDF.md:
A4 hoch, Rand 30 pt, Kopf +26 pt, Fuss +14 pt, DejaVu Sans / Sans Mono,
Titel 16 pt fett, Kapitel 12 pt fett, Fliesstext 9-10 pt, Tabellen 8,5 pt, Fusszeile 7,5 pt."""
import re
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether, CondPageBreak, PageBreak, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents

FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV', FD + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DV-B', FD + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DV-I', FD + 'DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DV-BI', FD + 'DejaVuSans-BoldOblique.ttf'))
pdfmetrics.registerFont(TTFont('DVM', FD + 'DejaVuSansMono.ttf'))
pdfmetrics.registerFont(TTFont('DVM-B', FD + 'DejaVuSansMono-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DVM-I', FD + 'DejaVuSansMono-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DVM-BI', FD + 'DejaVuSansMono-BoldOblique.ttf'))
pdfmetrics.registerFontFamily('DV', normal='DV', bold='DV-B', italic='DV-I', boldItalic='DV-BI')
pdfmetrics.registerFontFamily('DVM', normal='DVM', bold='DVM-B', italic='DVM-I', boldItalic='DVM-BI')

W, H = A4
M = 30.0
HEAD, FOOT = 26.0, 14.0
FRAME_W = W - 2 * M
STAND = '06.10.2026'
FOOTER_LEFT = 'C8205-Interpreter-Projekt · Stand ' + STAND
HEADER_TITLE = 'C 8205 – Testhandbuch'
COVER = None          # Deckblattdaten (dict, s. zeichne_deckblatt); None = Seite 1 ist eine normale Inhaltsseite
HEADER_FROM = 2       # Kopfzeile ab dieser Seite (PDF.md Abschnitt 3a.1)
TOTAL = None          # Gesamtseitenzahl fuer 'Seite X / Y' und 'Umfang', wenn die Seiten nur ein Teil eines groesseren
                      # PDFs sind (Kachel-PDF: Vorspann hier, Kachelseiten per pypdf); None = Seitenzahl dieses Laufs
HEADER_LEGEND = ('Test = Trommeldatei + Tastenfolge (+ Prüfungen) · gleiches Format für Python- und '
                 'Claude-Interpreter · Zahlen oktal')

INK = colors.HexColor('#1F2937')
MUTED = colors.HexColor('#6B7280')
RULE = colors.HexColor('#D1D5DB')
CODE_BG = colors.HexColor('#F3F4F6')
HEAD_BG = colors.HexColor('#374151')
GREEN = colors.HexColor('#15803D')
RED = colors.HexColor('#B91C1C')
BLUE = colors.HexColor('#2563EB')
BLUE_BG = colors.HexColor('#EAF1FF')
ORANGE = colors.HexColor('#D97706')
ORANGE_BG = colors.HexColor('#FFF3E0')

ST = {}
ST['body'] = ParagraphStyle('body', fontName='DV', fontSize=9.2, leading=12.6, textColor=INK,
                            spaceAfter=4.5, alignment=TA_LEFT, allowWidows=0, allowOrphans=0)
ST['bullet'] = ParagraphStyle('bullet', parent=ST['body'], leftIndent=11, bulletIndent=1, spaceAfter=2.5)
ST['num'] = ParagraphStyle('num', parent=ST['body'], leftIndent=15, bulletIndent=0, spaceAfter=2.5)
ST['title'] = ParagraphStyle('title', fontName='DV-B', fontSize=16, leading=20, textColor=INK, spaceAfter=3)
ST['subtitle'] = ParagraphStyle('subtitle', fontName='DV', fontSize=10, leading=13, textColor=MUTED, spaceAfter=10)
ST['h1'] = ParagraphStyle('h1', fontName='DV-B', fontSize=12, leading=15, textColor=INK, spaceBefore=11,
                          spaceAfter=5)
ST['h2'] = ParagraphStyle('h2', fontName='DV-B', fontSize=10, leading=13, textColor=INK, spaceBefore=7,
                          spaceAfter=3.5)
ST['cell'] = ParagraphStyle('cell', fontName='DV', fontSize=8.5, leading=10.8, textColor=INK)
ST['cellh'] = ParagraphStyle('cellh', parent=ST['cell'], fontName='DV-B', textColor=colors.white)
ST['code'] = ParagraphStyle('code', fontName='DVM', fontSize=7.4, leading=9.0, textColor=INK)
ST['cap'] = ParagraphStyle('cap', fontName='DV', fontSize=8, leading=10.4, textColor=MUTED, spaceAfter=7,
                           spaceBefore=2)
ST['note'] = ParagraphStyle('note', fontName='DV', fontSize=8.8, leading=11.8, textColor=INK)
ST['toc1'] = ParagraphStyle('toc1', fontName='DV-B', fontSize=9, leading=11, spaceBefore=2.4, textColor=INK)
ST['toc2'] = ParagraphStyle('toc2', fontName='DV', fontSize=8.4, leading=9.8, leftIndent=14, textColor=INK)

# ---------------------------------------------------------------- Auszeichnung
_code_re = re.compile(r'`([^`]+)`')
_bold_re = re.compile(r'\*\*(.+?)\*\*')
_ital_re = re.compile(r'(?<![\w*])//(.+?)//')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def fmt(s, code_size=8.0):
    """Mini-Auszeichnung: `code`, **fett**, //kursiv//; alles andere wird maskiert."""
    parts = _code_re.split(s)
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            out.append('<font name="DVM" size="%s">%s</font>' % (code_size, esc(p).replace(' ', '&nbsp;')))
        else:
            t = esc(p)
            t = _bold_re.sub(r'<b>\1</b>', t)
            t = _ital_re.sub(r'<i>\1</i>', t)
            out.append(t)
    return ''.join(out)


def P(text, style='body'):
    return Paragraph(fmt(text), ST[style])


def bullets(items, style='bullet'):
    return [Paragraph(fmt(t), ST[style], bulletText='•') for t in items]


def numbered(items):
    return [Paragraph(fmt(t), ST['num'], bulletText='%d.' % (i + 1)) for i, t in enumerate(items)]


_head_counter = [0]


class Head(Paragraph):
    """Ueberschrift, die dem Inhaltsverzeichnis gemeldet wird (Schluessel je Objekt stabil ueber alle Durchlaeufe)."""
    def __init__(self, text, level):
        Paragraph.__init__(self, fmt(text), ST['h1' if level == 0 else 'h2'])
        self.toc_level = level
        self.toc_text = text
        _head_counter[0] += 1
        self.toc_key = 'h%d' % _head_counter[0]


def h1(t):
    return [CondPageBreak(120), Head(t, 0)]


def h2(t):
    return [CondPageBreak(85), Head(t, 1)]


# ---------------------------------------------------------------- Kaesten, Tabellen, Code
def note(kind, text, width=FRAME_W):
    """Hinweis (blau) / Achtung (orange): Balken links, Toenung."""
    bar, bg, label = (BLUE, BLUE_BG, 'Hinweis') if kind == 'hinweis' else (ORANGE, ORANGE_BG, 'Achtung')
    para = Paragraph('<b>%s</b>&nbsp;&nbsp;%s' % (label, fmt(text)), ST['note'])
    t = Table([['', para]], colWidths=[3.2, width - 3.2])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), bar), ('BACKGROUND', (1, 0), (1, 0), bg),
        ('LEFTPADDING', (0, 0), (0, 0), 0), ('RIGHTPADDING', (0, 0), (0, 0), 0),
        ('LEFTPADDING', (1, 0), (1, 0), 7), ('RIGHTPADDING', (1, 0), (1, 0), 6),
        ('TOPPADDING', (1, 0), (1, 0), 4.5), ('BOTTOMPADDING', (1, 0), (1, 0), 4.5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    return [t, Spacer(1, 6)]


def tbl(rows, widths, header=True, code_cols=(), first_bold=False, fs=8.5):
    """Tabelle mit Paragraph-Zellen; widths in pt (Summe = FRAME_W)."""
    cell = ParagraphStyle('c', parent=ST['cell'], fontSize=fs, leading=fs * 1.27)
    cellh = ParagraphStyle('ch', parent=ST['cellh'], fontSize=fs, leading=fs * 1.27)
    data = []
    for r, row in enumerate(rows):
        line = []
        for c, v in enumerate(row):
            if header and r == 0:
                line.append(Paragraph(fmt(v), cellh))
            elif c in code_cols:
                line.append(Paragraph(fmt('`%s`' % v if v and '`' not in v else v), cell))
            elif first_bold and c == 0:
                line.append(Paragraph('<b>%s</b>' % fmt(v), cell))
            else:
                line.append(Paragraph(fmt(v), cell))
        data.append(line)
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    sty = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('LEFTPADDING', (0, 0), (-1, -1), 4.5), ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
           ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
           ('LINEBELOW', (0, 0), (-1, -1), 0.4, RULE), ('BOX', (0, 0), (-1, -1), 0.5, RULE)]
    if header:
        sty += [('BACKGROUND', (0, 0), (-1, 0), HEAD_BG)]
    if len(rows) >= 3:
        sty += [('NOSPLIT', (0, len(rows) - 2), (-1, len(rows) - 1))]   # letzte Zeile nie allein auf der Folgeseite
    t.setStyle(TableStyle(sty))
    _w, h = t.wrap(FRAME_W, 2000)
    if len(rows) <= 10 and h <= 190:
        return [KeepTogether([t]), Spacer(1, 7)]
    return [t, Spacer(1, 7)]


def _wrap_line(line, maxc, indent='    '):
    """Bricht eine Codezeile auf maxc Zeichen, bevorzugt an Leerzeichen."""
    if len(line) <= maxc:
        return [line]
    out, first = [], True
    cur = line
    while len(cur) > maxc:
        lim = maxc if first else maxc - len(indent)
        cut = cur.rfind(' ', int(lim * 0.55), lim)
        if cut <= 0:
            cut = lim
        out.append(cur[:cut] if first else indent + cur[:cut])
        cur = cur[cut:].lstrip(' ')
        first = False
    out.append(indent + cur if out else cur)
    return out


def code(text, caption=None, keep=14, bg=CODE_BG, bar=MUTED):
    """Festbreitenblock (Zeilen werden vorab umbrochen; splittbar ueber Seiten)."""
    lines = text.split('\n') if isinstance(text, str) else list(text)
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    maxc = int((FRAME_W - 16) / pdfmetrics.stringWidth('0', 'DVM', ST['code'].fontSize)) - 1
    rows = []
    for ln in lines:
        for w in _wrap_line(ln.rstrip(), maxc):
            rows.append([Paragraph(esc(w).replace(' ', '&nbsp;') or '&nbsp;', ST['code'])])
    t2 = Table(rows, colWidths=[FRAME_W], splitByRow=1)
    t2.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg),
                            ('LINEBEFORE', (0, 0), (0, -1), 3.2, bar),
                            ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                            ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, 0), 4), ('BOTTOMPADDING', (0, -1), (-1, -1), 4)]))
    n = len(rows)
    t2._isLongCode = n > 12
    if n > 12:   # lange Bloecke: nur an Leerzeilen trennen (oben mind. 6, unten mind. 4 Zeilen), sonst spaetestens alle 40 Zeilen
        blank = [i for i, ln in enumerate(w for l0 in lines for w in _wrap_line(l0.rstrip(), maxc)) if not ln.strip()]
        allowed, last = [], 0
        for i in range(5, n - 4):
            if (i in blank) or (i - last >= 40):
                allowed.append(i)       # Trennung hinter Zeile i erlaubt
                last = i
        cmds = [('NOSPLIT', (0, 0), (-1, 5)), ('NOSPLIT', (0, n - 4), (-1, n - 1))]
        if allowed:
            for i in range(5, n - 4):
                if i not in allowed:
                    cmds.append(('NOSPLIT', (0, i), (-1, i + 1)))
        t2.setStyle(TableStyle(cmds))
    keep = min(keep, 12)
    parts = [t2]
    if caption:
        parts.append(Paragraph(fmt(caption), ST['cap']))
    else:
        parts.append(Spacer(1, 6))
    if len(rows) <= keep:
        kt = KeepTogether(parts)
        kt._isCode = True
        return [kt]
    return parts


def figure(drawing, caption):
    return [KeepTogether([drawing, Paragraph(fmt(caption), ST['cap'])])]


def bild(pfad, caption, breite=None, max_hoehe=340.0):
    """Rasterbild (PNG/JPEG) mit Bildunterschrift; Abbildung und Bildunterschrift bleiben zusammen (PDF.md 3a.2, 3a.6).

    Druckgroesse = Pixelzahl / im Bild gespeicherte Aufloesung (dpi; PNG-Kopfdaten, ohne Angabe 72 dpi). Sie wird auf
    die Satzspiegelbreite `breite` (Vorgabe FRAME_W) und auf `max_hoehe` begrenzt, das Seitenverhaeltnis bleibt.
    Linksbuendig. Fehlt die Datei, bricht die Erzeugung ab (kein stilles Weglassen)."""
    import os
    import sys
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import Image
    if not os.path.isfile(pfad):
        sys.exit('FEHLER: Bild nicht gefunden: %s' % pfad)
    px_w, px_h = ImageReader(pfad).getSize()
    dpi = 72.0
    try:
        from PIL import Image as PILImage
        with PILImage.open(pfad) as im:
            d = im.info.get('dpi')
            if d and float(d[0]) > 0:
                dpi = float(d[0])
    except Exception:
        pass
    w, h = px_w * 72.0 / dpi, px_h * 72.0 / dpi
    k = min(1.0, (breite or FRAME_W) / w, max_hoehe / h)
    kt = figure(Image(pfad, width=w * k, height=h * k, hAlign='LEFT'), caption)
    return kt


# ---------------------------------------------------------------- Deckblatt (PDF.md Abschnitt 4)
COVER_M = 56.69                      # 20 mm Rand auf allen vier Seiten
PROJEKTZEILE = 'C 8205 · Simulation eines DDR-Kleinrechners von 1968'
FUSS_PROJEKT = 'C8205-Interpreter-Projekt'
ARTEN = ('ÜBERBLICK', 'BESCHREIBUNG', 'REFERENZ', 'HANDBUCH', 'DIAGRAMM', 'RICHTLINIE')
BEREICHE = ('GESAMTPROJEKT', 'RECHNER UND REGELWERK', 'INTERPRETER', 'ASSEMBLER', 'BIS')
STANDARD_BESCHREIBUNG = ('Dieses PDF gibt die Quelle im Wortlaut wieder; Listen, Tabellen und Codeblöcke entsprechen der '
                         'Quelle, weich umbrochene Zeilen sind zu Absätzen zusammengeführt.')
_VERSION = re.compile(r'^(#\s*)?Version:\s*(\d+\.\d{2}-\d{3})\s*$')


def lese_version(pfad):
    """Version y.xx-zzz aus den ersten Zeilen der .md-Quelle (PDF.md 4.3). Fehlt sie, bricht die Erzeugung ab."""
    with open(pfad, encoding='utf-8') as f:
        for i, ln in enumerate(f):
            m = _VERSION.match(ln.strip())
            if m:
                return m.group(2)
            if i > 12:
                break
    raise SystemExit('FEHLER: %s hat keine Zeile "Version: y.xx-zzz" in den ersten Zeilen; kein Deckblatt moeglich '
                     '(C8205-Versionierung.md, Abschnitt 8).' % pfad)


def heute():
    return datetime.date.today().strftime('%d.%m.%Y')


def zeichne_deckblatt(c, d, total):
    """Deckblatt auf Seite 1, direkt auf den Canvas. d: titel, untertitel, art, bereich, quellen [(datei, version)],
    stand, pdf_name; optional beschreibung, erzeugt_mit, raster."""
    assert d['art'] in ARTEN, 'Dokumentart %r nicht im Wertevorrat' % d['art']
    assert d['bereich'] in BEREICHE, 'Bereich %r nicht im Wertevorrat' % d['bereich']
    x0, x1 = COVER_M, W - COVER_M
    cw = x1 - x0
    top = H - COVER_M
    c.saveState()

    # Zone A: Kennung, Bereichsetikett, Linie
    c.setFillColor(MUTED)
    c.setFont('DV', 9)
    c.drawString(x0, top - 10.3, PROJEKTZEILE)
    tw = pdfmetrics.stringWidth(d['bereich'], 'DV-B', 8)
    c.setFillColor(HEAD_BG)
    c.roundRect(x1 - tw - 12, top - 14, tw + 12, 14, 2, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont('DV-B', 8)
    c.drawString(x1 - tw - 6, top - 14 + 4.0, d['bereich'])
    c.setStrokeColor(HEAD_BG)
    c.setLineWidth(2)
    c.line(x0, top - 22, x1, top - 22)

    # Zone B: Dokumentart, Titel, Untertitel (Oberkante bei 27 % der Seitenhöhe)
    y = H * (1 - 0.27) - 7
    c.saveState()                                    # Zeichenabstand nur fuer die Ueberzeile
    t = c.beginText(x0, y)
    t.setFont('DV-B', 9)
    t.setCharSpace(1)
    t.setFillColor(MUTED)
    t.textOut(d['art'])
    c.drawText(t)
    c.restoreState()
    size, lead = 26, 31
    lines = simpleSplit(d['titel'], 'DV-B', size, cw)
    if len(lines) > 2:
        size, lead = 22, 26
        lines = simpleSplit(d['titel'], 'DV-B', size, cw)
    if len(lines) > 2:
        raise SystemExit('FEHLER: Titel %r braucht mehr als zwei Zeilen bei 22 pt; kuerzen (PDF.md 4.3).' % d['titel'])
    y -= 8 + 0.73 * size
    c.setFillColor(INK)
    c.setFont('DV-B', size)
    for i, ln in enumerate(lines):
        c.drawString(x0, y, ln)
        if i < len(lines) - 1:
            y -= lead
    sub = simpleSplit(d['untertitel'], 'DV', 12, cw)
    if len(sub) > 2:
        raise SystemExit('FEHLER: Untertitel laenger als zwei Zeilen (PDF.md 4.3).')
    y -= 0.24 * size + 10 + 9
    c.setFillColor(MUTED)
    c.setFont('DV', 12)
    for i, ln in enumerate(sub):
        c.drawString(x0, y, ln)
        if i < len(sub) - 1:
            y -= 16

    # Zone C: Kurzbeschreibung (optional)
    if d.get('beschreibung'):
        bl = simpleSplit(d['beschreibung'], 'DV', 10, cw)
        if len(bl) > 6:
            raise SystemExit('FEHLER: Kurzbeschreibung laenger als sechs Zeilen (PDF.md 4.2).')
        y -= 3 + 24 + 7
        c.setFillColor(INK)
        c.setFont('DV', 10)
        for ln in bl:
            c.drawString(x0, y, ln)
            y -= 14
        y += 14
    y_unten_b_c = y

    # Zone F: Fuss
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.line(x0, COVER_M + 12, x1, COVER_M + 12)
    c.setFillColor(MUTED)
    c.setFont('DV', 7.5)
    c.drawString(x0, COVER_M, FUSS_PROJEKT)
    c.setFont('DVM', 7.5)
    c.drawRightString(x1, COVER_M, d['pdf_name'])

    # Zone E: Aktualitaetshinweis
    mehr = len(d['quellen']) > 1
    txt = ('Maßgeblich bleiben die Quelldateien. Dieses PDF wird nicht automatisch nachgeführt: Es ist aktuell, solange die '
           'Versionen oben mit den Versionszeilen der Quelldateien übereinstimmen.') if mehr else \
          ('Maßgeblich bleibt die Quelldatei. Dieses PDF wird nicht automatisch nachgeführt: Es ist aktuell, solange die '
           'Version oben mit der Versionszeile der Quelldatei übereinstimmt.')
    el = simpleSplit(txt, 'DV', 8.5, cw - 3 - 8 - 8)
    eh = 11.5 * len(el) + 10.7
    eb = COVER_M + 12 + 24
    c.setFillColor(CODE_BG)
    c.rect(x0, eb, cw, eh, stroke=0, fill=1)
    c.setFillColor(HEAD_BG)
    c.rect(x0, eb, 3, eh, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont('DV', 8.5)
    yy = eb + eh - 13.2
    for ln in el:
        c.drawString(x0 + 3 + 8, yy, ln)
        yy -= 11.5

    # Zone D: Angabenblock (Zeilen mit Linie darueber, Linie unter der letzten)
    rows = []
    for i, (datei, ver) in enumerate(d['quellen']):
        rows.append((('Quellen' if mehr else 'Quelle') if i == 0 else '', datei, 'DVM', ver))
    rows.append(('Stand', d['stand'], 'DV', None))
    rows.append(('Umfang', '%d Seiten, A4 hoch' % total, 'DV', None))
    if d.get('erzeugt_mit'):
        rows.append(('Erzeugt mit', d['erzeugt_mit'], 'DVM', None))
    if d.get('raster'):
        rows.append(('Layoutraster', d['raster'], 'DV', None))
    rh = 19
    dtop = eb + eh + 14 + rh * len(rows)
    if dtop + 10 > y_unten_b_c - 6:
        raise SystemExit('FEHLER: Deckblatt zu voll (Angabenblock stoesst an den Textblock).')
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    for i, (lab, val, fnt, ver) in enumerate(rows):
        rt = dtop - rh * i
        c.line(x0, rt, x1, rt)
        base = rt - 12.6
        c.setFillColor(MUTED)
        c.setFont('DV', 8.5)
        c.drawString(x0, base, lab)
        c.setFillColor(INK)
        c.setFont(fnt, 8 if fnt == 'DVM' else 8.5)
        c.drawString(x0 + 90, base, val)
        if ver:
            c.setFont('DV', 8.5)
            c.drawRightString(x1, base, ver)
    c.line(x0, dtop - rh * len(rows), x1, dtop - rh * len(rows))
    c.restoreState()


# ---------------------------------------------------------------- Seitenzaehlung
def _text(v, pg):
    """Kopf-/Fusszeilentext: fester Text oder Funktion der Seitenzahl."""
    return v(pg) if callable(v) else v


def kopf_fuss(c, pg, total, titel=None, legende=None, fuss_links=None, mit_kopf=True, legende_grafik=None):
    """Kopf- und Fusszeile nach PDF.md 3a.1 auf den Canvas c (Lage, Schrift und Farben an einer Stelle).
    titel, legende, fuss_links: Text oder Funktion der Seitenzahl. legende_grafik: Zeichenfunktion f(c, x, y), die
    statt der Textlegende die Zeile 2 zeichnet (Kantenfarben auf den Kachelseiten, PDF.md 3). mit_kopf=False: nur Fusszeile."""
    c.saveState()
    if mit_kopf:
        c.setFillColor(INK)
        c.setFont('DV-B', 11)
        c.drawString(M, H - M - 8, _text(titel, pg) or '')
        if legende_grafik:
            legende_grafik(c, M, H - M - 20)
        else:
            c.setFillColor(MUTED)
            c.setFont('DV', 8)
            c.drawString(M, H - M - 20, _text(legende, pg) or '')
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(M, H - M - 24.5, W - M, H - M - 24.5)
    c.setStrokeColor(RULE)                           # Fusslinie 41 pt ueber dem unteren Rand
    c.setLineWidth(0.5)
    c.line(M, M + FOOT - 3, W - M, M + FOOT - 3)
    c.setFillColor(MUTED)
    c.setFont('DV', 7.5)
    links = _text(fuss_links, pg)
    if links:
        c.drawString(M, M - 2, links)
    c.drawRightString(W - M, M - 2, 'Seite %d / %d' % (pg, total))
    c.restoreState()


LEERSEITE_TEXT = 'Leerseite – damit die Kachelseiten paarweise nebeneinander stehen'


def zeichne_leerseite(c, pg, total, text=LEERSEITE_TEXT):
    """Leerseite vor der ersten Kachelseite (PDF.md 4.5): Vermerk grau, kursiv, mittig; keine Kopfzeile,
    Fusszeile nur mit 'Seite X / Y'."""
    c.saveState()
    c.setFillColor(MUTED)
    c.setFont('DV-I', 8)
    c.drawCentredString(W / 2, H / 2, text)
    c.restoreState()
    kopf_fuss(c, pg, total, mit_kopf=False)


class NumberedCanvas(rl_canvas.Canvas):
    """Zeichnet Deckblatt, Kopf- und Fusszeile mit 'Seite X / Y' (Y erst beim Speichern bekannt)."""
    def __init__(self, *a, **kw):
        rl_canvas.Canvas.__init__(self, *a, **kw)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n = len(self._saved)
        for st in self._saved:
            self.__dict__.update(st)
            self._decorate(n)
            rl_canvas.Canvas.showPage(self)
        rl_canvas.Canvas.save(self)

    def _decorate(self, total):
        pg = self._pageNumber
        total = TOTAL or total
        if COVER is not None and pg == 1:           # Deckblatt: weder Kopf- noch Fusszeile (PDF.md 4.1)
            zeichne_deckblatt(self, COVER, total)
            return
        kopf_fuss(self, pg, total, HEADER_TITLE, HEADER_LEGEND, FOOTER_LEFT, mit_kopf=pg >= HEADER_FROM)


class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        BaseDocTemplate.__init__(self, fn, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=M,
                                 bottomMargin=M, title='C 8205 – Testhandbuch',
                                 author='C8205-Interpreter-Projekt', subject='Testhandbuch', **kw)
        fr = Frame(M, M + FOOT, FRAME_W, H - 2 * M - HEAD - FOOT, id='f', leftPadding=0, rightPadding=0,
                   topPadding=6, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id='p', frames=[fr])])
        self._k = 0

    def afterFlowable(self, fl):
        if isinstance(fl, Head):
            key = fl.toc_key
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(fl.toc_text, key, level=fl.toc_level, closed=False)
            self.notify('TOCEntry', (fl.toc_level, fl.toc_text, self.page, key))


def make_toc():
    toc = TableOfContents(dotsMinLevel=0)
    toc.levelStyles = [ST['toc1'], ST['toc2']]
    toc.tableStyle = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 1.4),
                                 ('BOTTOMPADDING', (0, 0), (-1, -1), 1.4)])
    return toc


def merge_intro(story):
    """Ein Fliesstext-Absatz direkt vor einem kurzen Codeblock wandert mit ihm auf die naechste Seite."""
    out = []
    for fl in story:
        if getattr(fl, '_isCode', False) and out and isinstance(out[-1], Paragraph) and not isinstance(out[-1], Head) \
                and out[-1].style.name in ('body',):
            prev = out.pop()
            kt = KeepTogether([prev] + list(fl._content))
            kt._isCode = False
            out.append(kt)
        elif isinstance(fl, KeepTogether) and out and isinstance(out[-1], Paragraph) and not isinstance(out[-1], Head) \
                and out[-1].style.name == 'body' and out[-1].text.rstrip().endswith(':'):
            prev = out.pop()
            kt = KeepTogether([prev] + list(fl._content))
            kt._isCode = False
            out.append(kt)
        elif getattr(fl, '_isLongCode', False) and out and isinstance(out[-1], Paragraph) \
                and not isinstance(out[-1], Head) and out[-1].style.name in ('body',):
            out[-1].keepWithNext = 1
            out.append(fl)
        else:
            out.append(fl)
    return out


def head_with_block(story):
    """Ueberschrift direkt vor einem KeepTogether-Block: CondPageBreak vor der Ueberschrift verlangt Platz fuer beide."""
    for i in range(2, len(story)):
        fl = story[i]
        if isinstance(story[i - 1], Head) and isinstance(story[i - 2], CondPageBreak) and isinstance(fl, KeepTogether):
            try:
                h = sum(c.wrap(FRAME_W, 5000)[1] + getattr(c, 'getSpaceAfter', lambda: 0)() for c in fl._content)
            except Exception:
                continue
            story[i - 2] = CondPageBreak(min(h + 34, 330))
    return story


def build(path, story):
    story = head_with_block(merge_intro(story))
    d = Doc(path)
    d.multiBuild(story, canvasmaker=NumberedCanvas)
'''),
    'erzeuge_knotentabellen_pdf': ('erzeuge_knotentabellen_pdf.py', r'''# -*- coding: utf-8 -*-
"""Erzeugt PDF/C8205-Knotentabellen_A4.pdf nach C8205-Interpreter-PDF.md (3a, 4, 4.5, 4.6).

Quellen:  markdown-dateien/C8205-Interpreter-Eingänge_der_Knoten.md      Knotentabelle
          markdown-dateien/C8205-Interpreter-Beschreibung_der_Knoten.md  Variablentabelle T2
Aufruf:   python3 PDF/erzeuge_knotentabellen_pdf.py [--stand TT.MM.JJJJ] [--mdverz ORDNER] [--ziel PFAD]
                                                    [--interp c8205_interp.py]

Seitenfolge (PDF.md 4.5, "Knotentabellen"):
    1   Deckblatt; die Kurzbeschreibung nennt den Umfang (Knoten, Eintraege der Variablentabelle T2)
    2   Lesehinweise (Lesart, Legende der Zeilenfarben und Arten) und Inhaltsverzeichnis
    3ff Knotentabelle, Variablentabelle T2 und "Lesart, Konventionen und Ergaenzungen der Quellen",
        jedes Kapitel auf einer neuen Seite (PDF.md 3a.6)

Das Einlesen der beiden Quellen (Knoten, T2, Kommentarbloecke) liegt in erzeuge_knoten_pdfs.py und wird von
dort importiert, damit Knotengraph und Knotentabellen aus demselben Einlesen entstehen. Schriften, Kopf- und
Fusszeile, Deckblatt und Tabellenstil kommen aus pdflib.py. Version der Quellen und Stand (Erzeugungsdatum)
werden beim Erzeugen gelesen, nicht von Hand gesetzt (PDF.md 4.3); fehlt eine Versionszeile, bricht das
Skript ab. Die Zeilenfarben der Knotentabelle sind die Knotenfarben des Knotengraphen (gleiche Farbe = gleicher
Knotentyp in beiden PDFs); ihre Bedeutung steht in den Lesehinweisen (PDF.md 3a.3).
"""
import os
import re
import sys
import argparse

HIER = os.path.dirname(os.path.abspath(__file__))
import pdflib as L
import erzeuge_knoten_pdfs as K
from pdflib import ST, FRAME_W, INK, MUTED, RULE, HEAD_BG, esc
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak

# ------------------------------------------------------------------ Deckblattdaten (PDF.md 4.6)
PDF_NAME = 'C8205-Knotentabellen_A4.pdf'
TITEL = 'Knotentabellen'
UNTERTITEL = 'Knotentabelle und Variablentabelle T2 im Wortlaut der Quellen'
ART = 'REFERENZ'
BEREICH = 'RECHNER UND REGELWERK'
# Kopfzeile, Zeile 2: wichtigste Schreibweise des Dokuments (PDF.md 3a.1, hoechstens ca. 120 Zeichen)
KOPF_LEGENDE = 'A-nnn = ANWEISUNG-nnn · Eing. = Eingang des Zielknotens · falsch/wahr = Zweig eines Tests'
# Reihenfolge der Quellen = Reihenfolge auf dem Deckblatt (PDF.md Abschnitt 8)
QUELLEN = [K.F_GRAPH, K.F_T2]

# Zeilenfarben der Knotentabelle = Knotenfarben des Knotengraphen
ZEILENFARBE = {'Anweisung': K.F_ANW, 'Test': K.F_TEST, 'Phasenzuordnung': K.F_PHASE, 'Konnektor': K.F_KONN}
FARBE_END = K.F_END
MUTED_HEX = '#6B7280'

# ------------------------------------------------------------------ Stile (aus pdflib.py abgeleitet)
S_CELL = ST['cell']
S_CELLH = ST['cellh']
S_NOTE = ParagraphStyle('t2note', parent=S_CELL, fontName='DV-I', spaceBefore=2.5)
S_ART = ParagraphStyle('art', parent=ST['body'], leftIndent=44, bulletIndent=14, bulletFontName='DV-B',
                       bulletFontSize=9.2, spaceAfter=2.5)
ART_ZEILE = re.compile(r'^(\s+)(ARW|AH|ZST|V)\s{2,}(\S.*)$')     # Eintraege der Behandlungsarten im T2-Kommentarkopf
S_REF = ParagraphStyle('ref', parent=ST['body'], fontName='DV-B', fontSize=8.5, leading=11, textColor=MUTED,
                       spaceBefore=5, spaceAfter=2, keepWithNext=1)


# ------------------------------------------------------------------ Quellen finden
_finde_original = K.finde_datei


def _finde_datei(verz, name):
    """Wie K.finde_datei; zusaetzlich Dateinamen, die Info-ZIP-unzip ohne UTF-8 ablegt ('ä' -> '#U00e4')."""
    try:
        return _finde_original(verz, name)
    except FileNotFoundError:
        alt = ''.join('#U%04x' % ord(ch) if ord(ch) > 127 else ch for ch in name)
        pfad = os.path.join(verz, alt)
        if os.path.isfile(pfad):
            return pfad
        raise


K.finde_datei = _finde_datei


# ------------------------------------------------------------------ Tabellenstil (PDF.md 3a.3)
def tabelle(rows, widths, extra=()):
    """Dunkler Kopf, Zeilenlinie 0,4 pt, Rahmen 0,5 pt, kein Zebra, kein Gitter; Kopf wiederholt sich; letzte
    Zeile nie allein auf der Folgeseite; bis 10 Zeilen und 190 pt Hoehe auf einer Seite. extra: Zusatzbefehle
    (z. B. Zeilenfarben, nur mit erklaerter Bedeutung)."""
    t = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
    sty = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('LEFTPADDING', (0, 0), (-1, -1), 4.5), ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
           ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
           ('LINEBELOW', (0, 0), (-1, -1), 0.4, RULE), ('BOX', (0, 0), (-1, -1), 0.5, RULE),
           ('BACKGROUND', (0, 0), (-1, 0), HEAD_BG)]
    if len(rows) >= 3:
        sty.append(('NOSPLIT', (0, len(rows) - 2), (-1, len(rows) - 1)))
    t.setStyle(TableStyle(sty + list(extra)))
    _w, h = t.wrap(FRAME_W, 2000)
    if len(rows) <= 10 and h <= 190:
        return [KeepTogether([t]), Spacer(1, 7)]
    return [t, Spacer(1, 7)]


def kopfzeile(*titel):
    return [Paragraph(t, S_CELLH) for t in titel]


# ------------------------------------------------------------------ Kommentarbloecke der Quellen (Wortlaut)
def kommentar(zeilen):
    """Kommentarbloecke der Quellen als Absaetze und Tabellen (PDF.md 6a: weich umbrochene Zeilen werden zu
    Absaetzen zusammengefuehrt). Die Zerlegung stammt aus erzeuge_knoten_pdfs.py, die Darstellung aus 3a."""
    out, cache = [], {}

    def stil(einzug):
        if einzug not in cache:
            cache[einzug] = ParagraphStyle('k%d' % round(einzug * 10), parent=ST['body'], leftIndent=einzug,
                                           spaceAfter=2.5)
        return cache[einzug]

    def abschnitt(zl):
        items, _struct = K.einheiten(zl)
        base = min([it[1] for it in items if it[0] == 't'] or [0])
        for i, it in enumerate(items):
            if it[0] == 't':
                p = Paragraph(K.fmt_einheit(it[2]), stil(max(0, it[1] - base) * 4.4))
                if i + 1 < len(items) and items[i + 1][0] == 'tab' and it[2].rstrip().endswith(':'):
                    p.keepWithNext = 1                    # Ueberleitung bleibt bei der Tabelle (3a.6)
                out.append(p)
            else:
                _, kopf, rows, widths = it
                data = [kopfzeile(*[esc(k) for k in kopf])]
                data += [[Paragraph(esc(a), S_CELL), Paragraph(esc(b), S_CELL)] for a, b in rows]
                out.extend(tabelle(data, list(widths)))

    for g in K.gruppen(zeilen):
        rest, i = [], 0
        while i < len(g):
            m = ART_ZEILE.match(g[i])
            if not m:
                rest.append(g[i])
                i += 1
                continue
            if rest:
                abschnitt(rest)
                rest = []
            ind, art, text = len(m.group(1)), m.group(2), m.group(3).strip()
            i += 1
            while i < len(g) and not ART_ZEILE.match(g[i]) and len(g[i]) - len(g[i].lstrip()) > ind:
                text += ' ' + g[i].strip()               # tiefer eingerueckte Folgezeilen gehoeren zum Eintrag
                i += 1
            out.append(Paragraph(K.fmt_einheit(text), S_ART, bulletText=art))
        if rest:
            abschnitt(rest)
        out.append(Spacer(1, 4))
    return out


# ------------------------------------------------------------------ Knotentabelle
def _ausgang(n):
    if n['end']:
        return 'Endknoten (kein Ausgang)'
    if not n['edges']:
        return '<i><font color="%s">%s</font></i>' % (MUTED_HEX, esc(n['outs']) or '–')
    zeilen = []
    for t, i, k in n['edges']:
        pre = {'falsch': 'falsch ', 'wahr': 'wahr ', None: ''}[k]
        zeilen.append('%s→ %d (Eing. %s)' % (pre, t, i))
    return '<br/>'.join(zeilen)


def _textzelle(n, t2):
    if n['anw'] is None:
        return esc(n['text'])
    e = t2.get(n['anw'])
    code = 'A-%03d' % n['anw']
    if e and len(e['desc']) <= 100:
        return '%s %s' % (code, esc(K.kurz(e['desc'])))
    return '%s – Volltext s. Tabelle T2' % code


def knotentabelle(d):
    nodes, t2 = d['nodes'], d['t2']
    rows = [kopfzeile('Knoten', 'Eingänge', 'Typ', 'Text / Anweisung', 'Ausgänge')]
    farben = []
    for r, num in enumerate(sorted(nodes), start=1):
        n = nodes[num]
        rows.append([Paragraph(str(num), S_CELL), Paragraph(' '.join(n['ein']) or '–', S_CELL),
                     Paragraph(esc(n['typ']), S_CELL), Paragraph(_textzelle(n, t2), S_CELL),
                     Paragraph(_ausgang(n), S_CELL)])
        farben.append(('BACKGROUND', (0, r), (-1, r), FARBE_END if n['end'] else ZEILENFARBE.get(n['typ'], K.F_ANW)))
    return tabelle(rows, [48, 56, 92, 197, FRAME_W - 393], farben)


# ------------------------------------------------------------------ Variablentabelle T2
def variablentabelle(d):
    t2 = d['t2']

    def benutzt(num):
        if num in d['used']:
            return ', '.join(str(x) for x in sorted(d['used'][num]))
        if num in d['refd']:
            return 'über ' + ', '.join('A-%03d' % x for x in sorted(d['refd'][num]))
        return '–'

    def notiz(txt):
        t = esc(K.kurz(txt))
        return re.sub(r'\s+((?:Ergänzung|Korrektur) \d\d\.\d\d\.\d{4}:)', r'<br/>\1', t)

    rows = [kopfzeile('Kurzcode', 'Art', 'Beschreibung der Anweisung oder des Tests', 'benutzt in Knoten')]
    for num in sorted(t2):
        e = t2[num]
        inhalt = [Paragraph(esc(K.kurz(e['desc'])), S_CELL)]
        if e['note']:
            inhalt.append(Paragraph('<b>Anmerkung:</b> ' + notiz(e['note']), S_NOTE))
        rows.append([Paragraph('A-%03d' % num, S_CELL), Paragraph(e['art'], S_CELL), inhalt,
                     Paragraph(esc(benutzt(num)), S_CELL)])
    return tabelle(rows, [56, 36, FRAME_W - 192, 100])


# ------------------------------------------------------------------ Lesehinweise (Seite 2)
def lesehinweise():
    s = [Paragraph('Lesehinweise', ST['h1'])]
    s.append(L.P('Dieses PDF gibt die Knotentabelle und die Variablentabelle T2 des Knotenautomaten (Ablauf der '
                 'Befehlsverarbeitung) in Tabellenform wieder. Der Text stammt aus den beiden Quelldateien des '
                 'Deckblatts; die grafische Darstellung steht im PDF „Knotengraph“.'))
    s.append(Paragraph('Lesart', ST['h2']))
    s += L.bullets([
        '**Ausgänge** nennt den Zielknoten und dessen Eingang (**Eing.**), nicht den Eingang des Knotens der Zeile; '
        'bei einem Test getrennt nach falsch und wahr.',
        '**A-nnn** steht für ANWEISUNG-nnn. Die Knotentabelle zeigt den Text der Anweisung, wenn er kurz ist (bis '
        '100 Zeichen); sonst steht dort nur der Kurzcode, der Volltext in der Variablentabelle T2 (Abschnitt 2).',
        'Beide Tabellen sind aufsteigend nach Nummer geordnet (Knotennummer, Kurzcode).'])
    s.append(Spacer(1, 3))
    s.append(Paragraph('Zeilenfarben der Knotentabelle', ST['h2']))
    legende = [kopfzeile('Zeilenfarbe', 'Knotentyp und Bedeutung')]
    zeilen = [('weiß', 'Anweisung', K.F_ANW),
              ('gelb', 'Test (Verzweigung falsch / wahr)', K.F_TEST),
              ('blau', 'Phasenzuordnung (Beginn Phase I bis IV)', K.F_PHASE),
              ('grau', 'Konnektor (Verbindung über gleiche Konnektornummer; Konnektor B ist extern)', K.F_KONN),
              ('rot', 'Endknoten (kein Ausgang: Endzustand des Knotenautomaten)', K.F_END)]
    farben = []
    for r, (name, text, farbe) in enumerate(zeilen, start=1):
        legende.append([Paragraph(name, S_CELL), Paragraph(text, S_CELL)])
        farben.append(('BACKGROUND', (0, r), (0, r), farbe))
    s += tabelle(legende, [80, FRAME_W - 80], farben)
    s.append(Paragraph('Art in der Variablentabelle T2', ST['h2']))
    s += tabelle([kopfzeile('Art', 'Bedeutung'),
                  [Paragraph('ARW', S_CELL), Paragraph('Ausführung durch das Rechenwerk', S_CELL)],
                  [Paragraph('AH', S_CELL), Paragraph('Ausführung durch Hardware (nicht vom Rechenwerk)', S_CELL)],
                  [Paragraph('ZST', S_CELL), Paragraph('Endzustand des Knotenautomaten', S_CELL)],
                  [Paragraph('V', S_CELL), Paragraph('allgemein formuliert, Detailklärung offen', S_CELL)]],
                 [80, FRAME_W - 80])
    s += L.note('hinweis', 'Die Spalte „benutzt in Knoten“ der Variablentabelle ist aus der Knotentabelle berechnet '
                           'und steht nicht in der Quelle. Anmerkungen (kursiv) sind die Kommentare der Quelle hinter '
                           '„#“. Der Kurzcode A-nnn ersetzt im Text der Quellen die Schreibweise ANWEISUNG-nnn.')
    return s


# ------------------------------------------------------------------ Kurzbeschreibung (Zone C)
def kurzbeschreibung(st):
    typen = ', '.join('%d %s' % (st['typen'][k], k) for k in ('Anweisung', 'Konnektor', 'Phasenzuordnung', 'Test')
                      if k in st['typen'])
    arten = ', '.join('%d %s' % (st['arten'][k], k) for k in ('AH', 'ARW', 'ZST', 'V') if k in st['arten'])
    return ('%d Knoten (%s) und %d Einträge der Variablentabelle T2 (%s); Endknoten: %s. Die Tabellen geben die '
            'Quellen im Wortlaut wieder; die grafische Darstellung steht im PDF „Knotengraph“.'
            % (st['n'], typen, st['t2n'], arten, ', '.join(str(x) for x in st['ends'])))


# ------------------------------------------------------------------ Erzeugen
def erzeuge(d, ziel, stand=None):
    """Baut das PDF aus dem Ergebnis von K.lade(); liefert die Seitenzahl."""
    stand = stand or L.heute()
    assert len(KOPF_LEGENDE) <= 120, 'Kopfzeile, Zeile 2: hoechstens ca. 120 Zeichen (PDF.md 3a.1)'
    st = K.statistik(d)
    quellen = [(QUELLEN[0], L.lese_version(d['gpfad'])), (QUELLEN[1], L.lese_version(d['tpfad']))]  # bricht ab, wenn eine Versionszeile fehlt
    L.STAND = stand
    L.FOOTER_LEFT = 'C8205-Interpreter-Projekt · Stand ' + stand
    L.HEADER_TITLE = 'C 8205 – ' + TITEL
    L.HEADER_LEGEND = KOPF_LEGENDE
    L.COVER = dict(titel=TITEL, untertitel=UNTERTITEL, art=ART, bereich=BEREICH, quellen=quellen, stand=stand,
                   pdf_name=os.path.basename(ziel), erzeugt_mit=os.path.basename(__file__),
                   beschreibung=kurzbeschreibung(st))

    luecken = [i for i in range(1, max(d['t2']) + 1) if i not in d['t2']]
    luecken_txt = ', '.join('A-%03d' % i for i in luecken) or 'keine'

    story = [Spacer(1, 1), PageBreak()]                                   # Seite 1: Deckblatt (vom Canvas gezeichnet)
    story += lesehinweise()                                               # Seite 2: Lesehinweise, Inhaltsverzeichnis
    story += [Paragraph('Inhaltsverzeichnis', ST['h1']), L.make_toc(), PageBreak()]
    story += [L.Head('1 Knotentabelle', 0),
              L.P('Zeilenformat der Quelle: Knotennummer; Eingänge; Typ; Text; Ausgänge.')]
    story += knotentabelle(d) + [PageBreak()]
    story += [L.Head('2 Variablentabelle T2 (Anweisungen und Tests)', 0),
              L.P('Anmerkungen (kursiv) sind die Kommentare der Quelle; die Spalte „benutzt in Knoten“ ist '
                  'berechnet (Lesehinweise, Seite 2). Nummern ohne Eintrag: %s.' % luecken_txt)]
    story += variablentabelle(d) + [PageBreak()]
    story += [L.Head('3 Lesart, Konventionen und Ergänzungen der Quellen', 0)]
    story += L.h2('Knotentabelle – Kommentarkopf der Quelldatei') + kommentar(d['ghead'])
    story += L.h2('Ergänzungen zwischen den Knotenzeilen der Quelle')
    for num in sorted(d['zw']):
        for blk in d['zw'][num]:
            story.append(Paragraph('(nach Knoten %d)' % num, S_REF))
            story += kommentar(blk)
    story += L.h2('Variablentabelle T2 – Kommentarkopf der Quelldatei') + kommentar(d['thead'])

    story = L.head_with_block(L.merge_intro(story))
    doc = L.Doc(ziel)
    doc.title = TITEL                                                     # Dokumenteigenschaften (PDF.md 4.7)
    doc.author = 'C8205-Interpreter-Projekt'
    doc.subject = '%s · Quellen: %s' % (ART.capitalize(), ', '.join('%s %s' % q for q in quellen))
    doc.multiBuild(story, canvasmaker=L.NumberedCanvas)
    return doc.page


def main():
    wurzel = os.path.dirname(HIER)
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--mdverz', default=os.path.join(wurzel, 'markdown-dateien'),
                    help='Ordner mit den beiden Quellen; Vorgabe: markdown-dateien/ neben PDF/')
    ap.add_argument('--ziel', default=os.path.join(HIER, PDF_NAME))
    ap.add_argument('--stand', default=L.heute(), help='TT.MM.JJJJ; Vorgabe: Erzeugungsdatum')
    ap.add_argument('--interp', default=None, help='c8205_interp.py: Einlesen gegen load_graph()/load_t2() prüfen')
    a = ap.parse_args()
    d = K.lade(a.mdverz)
    st = K.statistik(d)
    print('%d Knoten %s, Endknoten %s; T2: %d Einträge %s, %d in Knoten verwendet'
          % (st['n'], st['typen'], st['ends'], st['t2n'], st['arten'], st['verw']))
    for w in d['warn']:
        print('WARNUNG', w)
    for m in d['pruef']:
        print('FEHLER im Einlesen/Konsistenz:', m)
    if a.interp:
        diff = K.pruefe_interpreter(d, a.interp)
        print('Abgleich mit Interpreter:', 'identisch' if not diff else '')
        for x in diff:
            print('  ABWEICHUNG', x)
    n = erzeuge(d, a.ziel, a.stand)
    print('%s: %d Seiten' % (a.ziel, n))


if __name__ == '__main__':
    main()
'''),
}


class _EinbettFinder(_iabc.MetaPathFinder, _iabc.Loader):
    def find_spec(self, name, path=None, target=None):
        if name in _EINGEBETTET:
            return _iutil.spec_from_loader(name, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        datei, quelltext = _EINGEBETTET[module.__name__]
        module.__file__ = datei
        exec(compile(quelltext, '<eingebettet:' + datei + '>', 'exec'), module.__dict__)


_sys.meta_path.insert(0, _EinbettFinder())
_sys.modules.setdefault('erzeuge_knoten_pdfs', _sys.modules[__name__])   # das eingebettete Tabellenmodul findet so dieses Skript

import json, os, re, sys, math, subprocess, tempfile, argparse, importlib.util, unicodedata, io, copy

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, PageBreak, Flowable)
from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from pypdf.generic import NameObject, StreamObject

# ---------------------------------------------------------------------------------------------
# Schriften (PDF.md Abschnitt 2): DejaVu für alles außer den Kacheln des Knotengraphen
# ---------------------------------------------------------------------------------------------
FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV', FD + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DV-B', FD + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DV-I', FD + 'DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DV-BI', FD + 'DejaVuSans-BoldOblique.ttf'))
pdfmetrics.registerFont(TTFont('DV-M', FD + 'DejaVuSansMono.ttf'))
pdfmetrics.registerFontFamily('DV', normal='DV', bold='DV-B', italic='DV-I', boldItalic='DV-BI')

# Seitengeometrie (PDF.md Abschnitt 1 und 6)
PW, PH = A4
M, HDR, FTR, OV = 30.0, 26.0, 14.0, 20.0
TW = PW - 2 * M                      # Kachel-/Inhaltsbreite
TH = PH - 2 * M - HDR - FTR          # Kachel-/Inhaltshöhe (Seiten mit Kopfzeile)

# Farben (PDF.md Abschnitt 5)
C_WAHR = colors.HexColor('#1E8A1E')
C_FALSCH = colors.HexColor('#C4252B')
C_PUNKT = colors.HexColor('#8C8C8C')
F_ANW = colors.white
F_TEST = colors.HexColor('#FFF4C2')
F_PHASE = colors.HexColor('#DCE6F5')
F_KONN = colors.HexColor('#E6E6E6')
F_END = colors.HexColor('#F5D0D0')
GRID = colors.HexColor('#8A8A8A')
KOPF = colors.HexColor('#D9D9D9')

F_GRAPH = 'C8205-Interpreter-Eingänge_der_Knoten.md'
F_T2 = 'C8205-Interpreter-Beschreibung_der_Knoten.md'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def kurz(s):
    """ANWEISUNG-nnn bzw. $ANWEISUNG-nnn -> Kurzcode A-nnn"""
    return re.sub(r'\$?ANWEISUNG-(\d{3})', r'A-\1', s)


def finde_datei(verz, name):
    p = os.path.join(verz, name)
    if os.path.exists(p):
        return p
    ziel = unicodedata.normalize('NFC', name).casefold()
    for fn in os.listdir(verz):
        if unicodedata.normalize('NFC', fn).casefold() == ziel:
            return os.path.join(verz, fn)
    raise FileNotFoundError(os.path.join(verz, name))


# ---------------------------------------------------------------------------------------------
# Einlesen
# ---------------------------------------------------------------------------------------------
def kommentar_text(s):
    t = s.lstrip()[1:]
    return t[1:] if t.startswith(' ') else t


def parse_graph(pfad):
    nodes, head, zw = {}, [], {}
    block, last = [], None

    def flush():
        nonlocal block
        b = list(block)
        while b and not b[0].strip():
            b.pop(0)
        while b and not b[-1].strip():
            b.pop()
        if b:
            if last is None:
                head.extend(b)
            else:
                zw.setdefault(last, []).append(b)
        block = []

    for raw in open(pfad, encoding='utf-8').read().split('\n'):
        s = raw.rstrip()
        if s.lstrip().startswith('#'):
            block.append(kommentar_text(s))
            continue
        if not s.strip():
            flush()
            continue
        parts = [p.strip() for p in s.split(';', 4)]
        if len(parts) < 5:
            continue
        flush()
        num = int(parts[0])
        typ, text, outs = parts[2], parts[3], parts[4]
        m = re.fullmatch(r'\$ANWEISUNG-(\d+)', text)
        end = outs.strip() == '---'
        edges = [] if end else [(int(t), int(i), k or None)
                                for t, i, k in re.findall(r'(\d+)\((\d+)(?: (falsch|wahr))?\)', outs)]
        nodes[num] = dict(num=num, ein=([] if parts[1] == '-' else parts[1].split()), typ=typ, text=text,
                          outs=outs, anw=int(m.group(1)) if m else None, end=end, edges=edges)
        last = num
    flush()
    if head and re.fullmatch(r'\*\*.*\*\*', head[0].strip()):
        head.pop(0)
    return nodes, head, zw


ART_RE = re.compile(r';\s*(ARW|AH|ZST|V)\s*$')


def parse_t2(pfad):
    t2, head, warn = {}, [], []
    for raw in open(pfad, encoding='utf-8').read().split('\n'):
        s = raw.rstrip()
        m = re.match(r'\s*ANWEISUNG-(\d+)\s*;\s*(.*)$', s)
        if m:
            num, rest = int(m.group(1)), m.group(2)
            if rest.count('#') > 1:
                warn.append(f'T2 A-{num:03d}: mehrere "#" in der Zeile')
            pre, _, com = rest.partition('#')
            pre, com = pre.rstrip(), com.strip()
            art = None
            ma = ART_RE.search(pre)
            if ma:
                art, pre = ma.group(1), pre[:ma.start()]
            else:
                mb = ART_RE.search(com)
                if mb:
                    art, com = mb.group(1), com[:mb.start()].strip()
            if art is None:
                warn.append(f'T2 A-{num:03d}: keine Art erkannt, ARW angenommen')
                art = 'ARW'
            t2[num] = dict(num=num, desc=pre.strip().rstrip(',').strip(), art=art, note=com)
        elif s.lstrip().startswith('#') and not t2:
            head.append(kommentar_text(s))
    while head and not head[0].strip():
        head.pop(0)
    if head and re.fullmatch(r'\*\*.*\*\*', head[0].strip()):
        head.pop(0)
    return t2, head, warn


def stand_datum(*texte):
    ds = set()
    for t in texte:
        for d, mo, y in re.findall(r'\b(\d{2})\.(\d{2})\.(20\d{2})\b', t):
            ds.add((int(y), int(mo), int(d)))
    y, mo, d = max(ds)
    return f'{d:02d}.{mo:02d}.{y}'


def lade(mdverz):
    gp, tp = finde_datei(mdverz, F_GRAPH), finde_datei(mdverz, F_T2)
    nodes, ghead, zw = parse_graph(gp)
    t2, thead, warn = parse_t2(tp)
    used, refd = {}, {}
    for n in nodes.values():
        if n['anw'] is not None:
            used.setdefault(n['anw'], []).append(n['num'])
    for e in t2.values():
        for r in re.findall(r'\$ANWEISUNG-(\d+)', e['desc']):
            refd.setdefault(int(r), []).append(e['num'])
    alltext = open(gp, encoding='utf-8').read() + open(tp, encoding='utf-8').read()
    d = dict(nodes=nodes, ghead=ghead, zw=zw, t2=t2, thead=thead, used=used, refd=refd,
             stand=stand_datum(alltext), gpfad=gp, tpfad=tp, warn=warn)
    d['pruef'] = validiere(d)
    return d


def validiere(d):
    nodes, t2 = d['nodes'], d['t2']
    msg = []
    eingang = {}
    for n in nodes.values():
        for t, i, k in n['edges']:
            if t not in nodes:
                msg.append(f'Knoten {n["num"]}: Ziel {t} existiert nicht')
            eingang.setdefault(t, set()).add(str(i))
    for n in nodes.values():
        if n['typ'] == 'Konnektor':
            continue
        soll = set(n['ein'])
        ist = eingang.get(n['num'], set())
        if soll != ist:
            msg.append(f'Knoten {n["num"]}: Eingänge laut Zeile {sorted(soll)} <> laut Ausgangsverweisen {sorted(ist)}')
    for a in d['used']:
        if a not in t2:
            msg.append(f'A-{a:03d} wird verwendet, steht aber nicht in T2')
    for r in d['refd']:
        if r not in t2:
            msg.append(f'A-{r:03d} wird in T2 referenziert, steht aber nicht in T2')
    return msg


def pruefe_interpreter(d, interp_pfad):
    """Gleicht das Einlesen mit load_graph()/load_t2() des Interpreters ab."""
    spec = importlib.util.spec_from_file_location('c8205_interp_check', interp_pfad)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    g, t = mod.load_graph(d['gpfad']), mod.load_t2(d['tpfad'])
    diff = []
    if set(g) != set(d['nodes']):
        diff.append(f'Knotenmenge verschieden: nur Interpreter {sorted(set(g) - set(d["nodes"]))}, '
                    f'nur PDF {sorted(set(d["nodes"]) - set(g))}')
    for num, n in d['nodes'].items():
        if num not in g:
            continue
        o = g[num]
        mine = dict(out=None, wahr=None, falsch=None)
        for tg, _i, k in n['edges']:
            mine[{'falsch': 'falsch', 'wahr': 'wahr', None: 'out'}[k]] = tg
        for f in ('out', 'wahr', 'falsch'):
            if o[f] != mine[f]:
                diff.append(f'Knoten {num}: {f} Interpreter={o[f]} PDF={mine[f]}')
        if o['end'] != n['end'] or o['anw'] != n['anw'] or o['typ'] != n['typ']:
            diff.append(f'Knoten {num}: end/anw/typ weichen ab')
    if set(t) != set(d['t2']):
        diff.append(f'T2-Nummern verschieden: {sorted(set(t) ^ set(d["t2"]))}')
    return diff


def statistik(d):
    nodes, t2 = d['nodes'], d['t2']
    typen = {}
    for n in nodes.values():
        typen[n['typ']] = typen.get(n['typ'], 0) + 1
    ends = sorted(n['num'] for n in nodes.values() if n['end'])
    arten = {}
    for e in t2.values():
        arten[e['art']] = arten.get(e['art'], 0) + 1
    return dict(n=len(nodes), typen=typen, ends=ends, arten=arten, t2n=len(t2), verw=len(d['used']))


# ---------------------------------------------------------------------------------------------
# Kommentarblöcke der Quellen -> Absätze/Tabellen (PDF.md 6a: weich umbrochene Zeilen zusammenführen)
# ---------------------------------------------------------------------------------------------
DATE_RE = re.compile(r'^(?:Ergänzung|Korrektur) \d\d\.\d\d\.\d{4}')
LABEL_RE = re.compile(r'^(?:Klarstellung\b|Hinweis\b|[^:;<>="]{1,38}:(?:\s|$))')
TERMINAL = ('.', ';', ':', '?', '!')
PAIR_RE = re.compile(r'^(\s+)(\S.*?)\s{3,}(->.*)$')
STATE_RE = re.compile(r'^\s+((?:Eintritt in Phase [IV]+)|(?:Ende Phase IV))\s{2,}(\S.*)$')
UMBRUCH_W = 105     # Quellzeilen, die vor dieser Breite mit Satzzeichen enden, gelten als bewusster Umbruch


def gruppen(zeilen):
    gr, cur = [], []
    for z in zeilen:
        if z.strip() == '':
            if cur:
                gr.append(cur)
                cur = []
        else:
            cur.append(z.rstrip())
    if cur:
        gr.append(cur)
    return gr


def einheiten(g):
    """-> Liste ('t', einzug, text, laenge_letzte_zeile) | ('tab', kopf, zeilen, spaltenbreiten)"""
    items = []
    inds = {len(z) - len(z.lstrip()) for z in g}
    struct = len(inds) >= 2           # mehrere Einzugsebenen: Quellzeilen sind bewusst strukturiert -> nicht zusammenführen
    i, n = 0, len(g)
    while i < n:
        z = g[i]
        ind = len(z) - len(z.lstrip())
        s = z.strip()
        if STATE_RE.match(z):
            rows = []
            while i < n and STATE_RE.match(g[i]):
                mm = STATE_RE.match(g[i])
                rows.append((mm.group(1), ' · '.join(re.split(r'\s{2,}', mm.group(2).strip()))))
                i += 1
            items.append(('tab', ['Zeitpunkt', 'Zustand'], rows, (105, 430)))
            continue
        nxt = g[i + 1].strip() if i + 1 < n else ''
        if PAIR_RE.match(z) or s.startswith('->') or (ind >= 2 and nxt.startswith('->')):
            rows = []
            while i < n:
                z2 = g[i]
                ind2 = len(z2) - len(z2.lstrip())
                s2 = z2.strip()
                mp = PAIR_RE.match(z2)
                if mp:
                    rows.append([mp.group(2).strip(), mp.group(3)[2:].strip()])
                elif s2.startswith('->'):
                    if rows and not rows[-1][1]:
                        rows[-1][1] = s2[2:].strip()
                    elif rows:
                        rows[-1][1] += ' ' + s2[2:].strip()
                    else:
                        rows.append(['', s2[2:].strip()])
                elif rows and ind2 >= 10:
                    rows[-1][1] += ' ' + s2
                elif i + 1 < n and g[i + 1].strip().startswith('->'):
                    rows.append([s2, ''])
                else:
                    break
                i += 1
            items.append(('tab', ['Fall', 'Einstieg / Wirkung'], [tuple(r) for r in rows], (200, 335)))
            continue
        if items and items[-1][0] == 't':
            _, pind, ptxt, plen = items[-1]
            first = s.split(' ', 1)[0]
            zwei = ' '.join(s.split(' ')[:2])
            pzwei = ' '.join(ptxt.split(' ')[:2])
            ende = ptxt.endswith(TERMINAL)
            hart = (ind != pind or bool(DATE_RE.match(s)) or (bool(LABEL_RE.match(s)) and ende) or s.startswith('-')
                    or zwei == pzwei or (ende and plen + 1 + len(first) < UMBRUCH_W))
            if not hart:
                items[-1] = ('t', pind, ptxt + ' ' + s, len(s))
                i += 1
                continue
        items.append(('t', ind, s, len(s)))
        i += 1
    return items, struct


def fmt_einheit(txt):
    t = esc(txt)
    t2 = re.sub(r'^((?:Ergänzung|Korrektur) \d\d\.\d\d\.\d{4}(?: \(\d\))?:)', r'<b>\1</b>', t)
    if t2 == t:
        t2 = re.sub(r'^([A-ZÄÖÜ][^:;&<>="]{0,36}:)(?=\s|$)', r'<b>\1</b>', t)
    return t2


def kommentar_flowables(zeilen, groesse=8.0, leading=10.2):
    out, cache = [], {}
    base_style = dict(fontName='DV', fontSize=groesse, leading=leading, spaceAfter=0.6)

    def stil(einzug):
        if einzug not in cache:
            cache[einzug] = ParagraphStyle(f'k{einzug}', leftIndent=einzug, **base_style)
        return cache[einzug]

    for g in gruppen(zeilen):
        items, struct = einheiten(g)
        base = min([it[1] for it in items if it[0] == 't'] or [0])
        for it in items:
            if it[0] == 't':
                out.append(Paragraph(fmt_einheit(it[2]), stil(max(0, (it[1] - base)) * 4.4)))
            else:
                _, kopf, rows, widths = it
                cell = ParagraphStyle('tc', fontName='DV', fontSize=groesse - 0.3, leading=leading - 0.6)
                cellb = ParagraphStyle('tcb', parent=cell, fontName='DV-B')
                data = [[Paragraph(esc(k), cellb) for k in kopf]] + \
                       [[Paragraph(esc(a), cell), Paragraph(esc(b), cell)] for a, b in rows]
                tb = Table(data, colWidths=widths, hAlign='LEFT')
                tb.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.4, GRID), ('BACKGROUND', (0, 0), (-1, 0), KOPF),
                                        ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 3),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 3), ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5)]))
                out.append(Spacer(1, 2))
                out.append(tb)
                out.append(Spacer(1, 2))
        out.append(Spacer(1, 3.5))
    return out


# ---------------------------------------------------------------------------------------------
# Kopf-/Fußzeilen
# ---------------------------------------------------------------------------------------------
def kopf_fuss(c, titel, untertitel, fusslinks, seite, gesamt, mit_kopf=True, legende=None):
    c.saveState()
    if mit_kopf:
        y = PH - M
        c.setFillColor(colors.black)
        c.setFont('DV-B', 11)
        c.drawString(M, y - 9, titel)
        c.setFont('DV', 8)
        c.setFillColor(colors.HexColor('#555555'))
        if legende:
            legende(c, M, y - 20)
        elif untertitel:
            c.drawString(M, y - 20, untertitel)
        c.setStrokeColor(GRID)
        c.setLineWidth(0.5)
        c.line(M, y - 24, PW - M, y - 24)
    c.setFont('DV', 7.5)
    c.setFillColor(colors.HexColor('#555555'))
    c.setStrokeColor(GRID)
    c.setLineWidth(0.5)
    c.line(M, M + FTR - 3, PW - M, M + FTR - 3)
    if fusslinks:
        c.drawString(M, M + 1, fusslinks)
    c.drawRightString(PW - M, M + 1, f'Seite {seite} / {gesamt}')
    c.restoreState()


def graph_legende(c, x, y):
    """Legende der Kantenfarben in der Kopfzeile jeder Kachelseite (PDF.md 3)"""
    items = [('wahr / OK', C_WAHR, None), ('falsch / Fehler', C_FALSCH, (3, 2)),
             ('Standardfluss', colors.black, None)]
    for text, col, dash in items:
        c.saveState()
        c.setStrokeColor(col)
        c.setLineWidth(0.9)
        if dash:
            c.setDash(*dash)
        c.line(x, y + 2.5, x + 22, y + 2.5)
        c.restoreState()
        c.setFillColor(colors.HexColor('#555555'))
        c.setFont('DV', 8)
        c.drawString(x + 26, y, text)
        x += 26 + pdfmetrics.stringWidth(text, 'DV', 8) + 14


class TocZeile(Flowable):
    def __init__(self, num, titel, seite):
        super().__init__()
        self.t, self.s = f'{num}  {titel}', str(seite)

    def wrap(self, aw, ah):
        self.w = aw
        return aw, 14

    def draw(self):
        c = self.canv
        c.setFont('DV', 9.5)
        c.drawString(0, 3, self.t)
        c.drawRightString(self.w, 3, self.s)
        tw = pdfmetrics.stringWidth(self.t, 'DV', 9.5) + 5
        pw = pdfmetrics.stringWidth(self.s, 'DV', 9.5) + 5
        punkt = pdfmetrics.stringWidth(' .', 'DV', 9.5)
        c.drawString(tw, 3, ' .' * int((self.w - tw - pw) / punkt))


class Sym(Flowable):
    """Zeile der Legende: Knotensymbol oder Kantenmuster + Text"""
    def __init__(self, kind, text):
        super().__init__()
        self.kind, self.text = kind, text

    def wrap(self, aw, ah):
        return aw, 17

    def draw(self):
        c = self.canv
        x0, y0, w, h = 2, 3, 28, 11
        c.saveState()
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.8)
        k = self.kind
        if k == 'konn':
            c.setFillColor(F_KONN)
            c.ellipse(x0, y0, x0 + w, y0 + h, fill=1, stroke=1)
        elif k == 'phase':
            c.setFillColor(F_PHASE)
            p = c.beginPath()
            p.moveTo(x0 + 6, y0 + h); p.lineTo(x0 + w, y0 + h); p.lineTo(x0 + w - 6, y0); p.lineTo(x0, y0); p.close()
            c.drawPath(p, fill=1, stroke=1)
        elif k == 'anw':
            c.setFillColor(F_ANW)
            c.rect(x0 + 2, y0, w - 4, h, fill=1, stroke=1)
        elif k == 'test':
            c.setFillColor(F_ANW)
            p = c.beginPath()
            p.moveTo(x0 + w / 2, y0 + h); p.lineTo(x0 + w, y0 + h / 2); p.lineTo(x0 + w / 2, y0); p.lineTo(x0, y0 + h / 2); p.close()
            c.drawPath(p, fill=1, stroke=1)
        elif k == 'end':
            c.setFillColor(F_END)
            c.rect(x0 + 2, y0, w - 4, h, fill=1, stroke=1)
            c.setFillColor(colors.transparent) if hasattr(colors, 'transparent') else None
            c.rect(x0 + 4, y0 + 2, w - 8, h - 4, fill=0, stroke=1)
        else:
            col, dash = {'wahr': (C_WAHR, None), 'falsch': (C_FALSCH, (3, 2)), 'std': (colors.black, None),
                         'punkt': (C_PUNKT, (1, 2))}[k]
            c.setStrokeColor(col)
            c.setLineWidth(1.0)
            if dash:
                c.setDash(*dash)
            c.line(x0, y0 + h / 2, x0 + w, y0 + h / 2)
        c.restoreState()
        c.setFont('DV', 9)
        c.setFillColor(colors.black)
        c.drawString(x0 + w + 9, y0 + 2, self.text)


# ---------------------------------------------------------------------------------------------
# PDF 1: Knotentabellen
# ---------------------------------------------------------------------------------------------
def hex_(col):
    return col


def knotentabellen(d, pfad):
    nodes, t2 = d['nodes'], d['t2']
    st = statistik(d)
    stand = d['stand']
    tit = 'C 8205 – Knotentabellen'
    fuss = f'C8205-Interpreter-Projekt · Stand {stand} · Knotentabellen'
    legende_kopf = 'A-nnn = ANWEISUNG-nnn · Eing. = Eingang des Zielknotens · falsch/wahr = Zweig eines Tests'

    sp = ParagraphStyle('p', fontName='DV', fontSize=9.5, leading=12.5, spaceAfter=5)
    s_t = ParagraphStyle('t', fontName='DV-B', fontSize=16, leading=20, spaceAfter=3)
    s_u = ParagraphStyle('u', fontName='DV', fontSize=9.5, leading=12, textColor=colors.HexColor('#444444'), spaceAfter=8)
    s_h = ParagraphStyle('h', fontName='DV-B', fontSize=12, leading=15, spaceBefore=4, spaceAfter=5)
    s_h2 = ParagraphStyle('h2', fontName='DV-B', fontSize=10, leading=13, spaceBefore=6, spaceAfter=3)
    s_c = ParagraphStyle('c', fontName='DV', fontSize=8.5, leading=10.5)
    s_cb = ParagraphStyle('cb', parent=s_c, fontName='DV-B')
    s_n = ParagraphStyle('n', parent=s_c, fontName='DV-I', textColor=colors.HexColor('#333333'), spaceBefore=2)
    s_ref = ParagraphStyle('ref', fontName='DV-B', fontSize=8, leading=10, textColor=colors.HexColor('#444444'),
                           spaceBefore=4, spaceAfter=1)

    def ueberschrift(text, key, titel):
        p = Paragraph(text, s_h)
        p._toc = (key, titel)
        return p

    # ----- Knotentabelle
    rowbg = {'Anweisung': F_ANW, 'Test': F_TEST, 'Phasenzuordnung': F_PHASE, 'Konnektor': F_KONN}

    def ausgang(n):
        if n['end']:
            return 'Endknoten (kein Ausgang)'
        if not n['edges']:
            return f'<i><font color="#555555">{esc(n["outs"]) or "–"}</font></i>'
        zeilen = []
        for t, i, k in n['edges']:
            pre = {'falsch': 'falsch ', 'wahr': 'wahr ', None: ''}[k]
            zeilen.append(f'{pre}→ {t} (Eing. {i})')
        return '<br/>'.join(zeilen)

    def textzelle(n):
        if n['anw'] is None:
            return esc(n['text'])
        e = t2.get(n['anw'])
        code = f'A-{n["anw"]:03d}'
        if e and len(e['desc']) <= 100:
            return f'{code} {esc(kurz(e["desc"]))}'
        return f'{code} – Volltext s. Tabelle T2'

    kdata = [[Paragraph(h, s_cb) for h in ('Knoten', 'Eingänge', 'Typ', 'Text / Anweisung', 'Ausgänge')]]
    kbg = []
    for r, num in enumerate(sorted(nodes), start=1):
        n = nodes[num]
        kdata.append([Paragraph(str(num), s_c), Paragraph(' '.join(n['ein']) or '–', s_c), Paragraph(n['typ'], s_c),
                      Paragraph(textzelle(n), s_c), Paragraph(ausgang(n), s_c)])
        kbg.append(('BACKGROUND', (0, r), (-1, r), F_END if n['end'] else rowbg.get(n['typ'], F_ANW)))
    ktab = Table(kdata, colWidths=[42, 56, 82, 240, 115], repeatRows=1)
    ktab.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.4, GRID), ('BACKGROUND', (0, 0), (-1, 0), KOPF),
                              ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 3),
                              ('RIGHTPADDING', (0, 0), (-1, -1), 3), ('TOPPADDING', (0, 0), (-1, -1), 2),
                              ('BOTTOMPADDING', (0, 0), (-1, -1), 2)] + kbg))

    # ----- Variablentabelle T2
    def benutzt(num):
        if num in d['used']:
            return ', '.join(str(x) for x in sorted(d['used'][num]))
        if num in d['refd']:
            return 'über ' + ', '.join(f'A-{x:03d}' for x in sorted(d['refd'][num]))
        return '–'

    def notiz(txt):
        t = esc(kurz(txt))
        return re.sub(r'\s+((?:Ergänzung|Korrektur) \d\d\.\d\d\.\d{4}:)', r'<br/>\1', t)

    tdata = [[Paragraph(h, s_cb) for h in ('Kurzcode', 'Art', 'Beschreibung der Anweisung oder des Tests', 'benutzt in Knoten')]]
    for num in sorted(t2):
        e = t2[num]
        inhalt = [Paragraph(esc(kurz(e['desc'])), s_c)]
        if e['note']:
            inhalt.append(Paragraph('Anmerkung: ' + notiz(e['note']), s_n))
        tdata.append([Paragraph(f'A-{num:03d}', s_c), Paragraph(e['art'], s_c), inhalt, Paragraph(esc(benutzt(num)), s_c)])
    ttab = Table(tdata, colWidths=[52, 32, 366, 85], repeatRows=1, splitInRow=1)
    ttab.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.4, GRID), ('BACKGROUND', (0, 0), (-1, 0), KOPF),
                              ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 3),
                              ('RIGHTPADDING', (0, 0), (-1, -1), 3), ('TOPPADDING', (0, 0), (-1, -1), 2),
                              ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
    luecken = [i for i in range(1, max(t2) + 1) if i not in t2]
    luecken_txt = ', '.join(f'A-{i:03d}' for i in luecken) or 'keine'

    # ----- Abschnitt 3: Lesart und Ergänzungen (Quelltext unverändert, nur Zeilen zusammengeführt)
    sek3 = [ueberschrift('3 Lesart, Konventionen und Ergänzungen der Quellen', 'sek3',
                         'Lesart, Konventionen und Ergänzungen der Quellen'),
            Paragraph('Knotentabelle – Kommentarkopf der Quelldatei:', s_h2)]
    sek3 += kommentar_flowables(d['ghead'])
    sek3.append(Paragraph('Ergänzungen zwischen den Knotenzeilen der Quelle:', s_h2))
    for num in sorted(d['zw']):
        for blk in d['zw'][num]:
            sek3.append(Paragraph(f'(nach Knoten {num})', s_ref))
            sek3 += kommentar_flowables(blk)
    sek3.append(Paragraph('Variablentabelle T2 – Kommentarkopf der Quelldatei:', s_h2))
    sek3 += kommentar_flowables(d['thead'])

    # ----- Deckblatt
    typtxt = ', '.join(f'{st["typen"][k]} {k}' for k in ('Anweisung', 'Konnektor', 'Phasenzuordnung', 'Test') if k in st['typen'])
    artenn = ', '.join(f'{st["arten"][k]} {k}' for k in ('AH', 'ARW', 'ZST', 'V') if k in st['arten'])
    legende = [
        [Paragraph('Zeilenfarbe weiß', s_c), Paragraph('Anweisung', s_c)],
        [Paragraph('Zeilenfarbe gelb', s_c), Paragraph('Test (Verzweigung falsch / wahr)', s_c)],
        [Paragraph('Zeilenfarbe blau', s_c), Paragraph('Phasenzuordnung (Beginn Phase I bis IV)', s_c)],
        [Paragraph('Zeilenfarbe grau', s_c), Paragraph('Konnektor (Verbindung über gleiche Konnektornummer; Konnektor B ist extern)', s_c)],
        [Paragraph('Zeilenfarbe rot', s_c), Paragraph('Endknoten (kein Ausgang: Endzustand des Knotenautomaten)', s_c)],
        [Paragraph('Art ARW', s_c), Paragraph('Ausführung durch das Rechenwerk', s_c)],
        [Paragraph('Art AH', s_c), Paragraph('Ausführung durch Hardware (nicht vom Rechenwerk)', s_c)],
        [Paragraph('Art ZST', s_c), Paragraph('Endzustand des Knotenautomaten', s_c)],
        [Paragraph('Art V', s_c), Paragraph('allgemein formuliert, Detailklärung offen', s_c)],
    ]
    ltab = Table(legende, colWidths=[100, 435], hAlign='LEFT')
    ltab.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.4, GRID), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                              ('BACKGROUND', (0, 0), (0, 0), F_ANW), ('BACKGROUND', (0, 1), (0, 1), F_TEST),
                              ('BACKGROUND', (0, 2), (0, 2), F_PHASE), ('BACKGROUND', (0, 3), (0, 3), F_KONN),
                              ('BACKGROUND', (0, 4), (0, 4), F_END), ('LEFTPADDING', (0, 0), (-1, -1), 3),
                              ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))

    class Doc(BaseDocTemplate):
        def afterFlowable(self, fl):
            if hasattr(fl, '_toc'):
                key, titel = fl._toc
                self.seiten[key] = self.page
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(titel, key, 0)

    def baue(gesamt, toc):
        doc = Doc(pfad, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M + FTR,
                  title='C 8205 – Knotentabellen', author='C8205-Interpreter-Projekt',
                  subject=f'Knotentabelle und Variablentabelle T2, Stand {stand}')
        doc.seiten = {}

        def erste(c, dc):
            kopf_fuss(c, tit, None, fuss, c.getPageNumber(), gesamt, mit_kopf=False)

        def weitere(c, dc):
            kopf_fuss(c, tit, legende_kopf, fuss, c.getPageNumber(), gesamt, mit_kopf=True)

        f1 = Frame(M, M + FTR, TW, PH - 2 * M - FTR, id='f1', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        f2 = Frame(M, M + FTR, TW, PH - 2 * M - FTR - HDR, id='f2', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        doc.addPageTemplates([PageTemplate(id='erste', frames=[f1], onPage=erste, autoNextPageTemplate='weitere'),
                              PageTemplate(id='weitere', frames=[f2], onPage=weitere)])
        story = [Paragraph(tit, s_t),
                 Paragraph('Knotentabelle und Variablentabelle T2 des Knotenautomaten (Befehlsablauf)', s_u),
                 Paragraph(f'<b>Quellen:</b> C8205-Interpreter-Eingänge_der_Knoten.md (Knotentabelle) und '
                           f'C8205-Interpreter-Beschreibung_der_Knoten.md (Variablentabelle T2), Stand {stand}. '
                           f'Der Text wird unverändert aus den Quellen übernommen; die grafische Darstellung steht im PDF „Knotengraph“.', sp),
                 Paragraph(f'<b>Umfang:</b> {st["n"]} Knoten ({typtxt}), {st["t2n"]} Anweisungen/Tests in T2 ({artenn}); '
                           f'Endknoten: {", ".join(str(x) for x in st["ends"])}.', sp),
                 Paragraph('<b>Lesart:</b> „Ausgänge“ nennt den Zielknoten und dessen Eingang; bei einem Test getrennt nach falsch und wahr. '
                           'Der Kurzcode A-nnn steht für ANWEISUNG-nnn; sein Volltext steht in Abschnitt 2. '
                           'Lange Texte erscheinen in der Knotentabelle nur als Kurzcode.', sp),
                 Paragraph('Legende', s_h2), ltab, Spacer(1, 10), Paragraph('Inhaltsverzeichnis', s_h2)]
        titel = [('1', 'Knotentabelle', 'sek1'), ('2', 'Variablentabelle T2 (Anweisungen und Tests)', 'sek2'),
                 ('3', 'Lesart, Konventionen und Ergänzungen der Quellen', 'sek3')]
        for num, t, key in titel:
            story.append(TocZeile(num, t, (toc or {}).get(key, '?')))
        story += [PageBreak(),
                  ueberschrift('1 Knotentabelle', 'sek1', 'Knotentabelle'),
                  Paragraph('Zeilenformat der Quelle: Knotennummer; Eingänge; Typ; Text; Ausgänge. '
                            'Die Reihenfolge ist die der Quelle (aufsteigende Knotennummer).', sp),
                  ktab, PageBreak(),
                  ueberschrift('2 Variablentabelle T2 (Anweisungen und Tests)', 'sek2', 'Variablentabelle T2 (Anweisungen und Tests)'),
                  Paragraph('Die Spalte „benutzt in Knoten“ ist aus der Knotentabelle berechnet (nicht Teil der Quelle). '
                            'Anmerkungen (kursiv) sind die Kommentare der Quelle hinter „#“. '
                            f'Nummern ohne Eintrag: {luecken_txt}.', sp),
                  ttab, PageBreak()] + sek3
        doc.build(copy.deepcopy(story))      # reportlab verändert Flowables beim Bauen: jeder Durchlauf bekommt eine Kopie
        return doc

    d1 = baue(0, None)
    d2 = baue(d1.page, d1.seiten)
    return d2.page


# ---------------------------------------------------------------------------------------------
# PDF 2: Knotengraph
# ---------------------------------------------------------------------------------------------
def back_edges(nodes):
    adj = {u: [t for t, _i, _k in nodes[u]['edges']] for u in nodes}
    state, back = {}, set()
    sys.setrecursionlimit(10000)

    def dfs(u):
        state[u] = 1
        for v in adj[u]:
            if v not in nodes:
                continue
            if state.get(v) == 1:
                back.add((u, v))
            elif v not in state:
                dfs(v)
        state[u] = 2

    for s in [1] + sorted(nodes):
        if s in nodes and s not in state:
            dfs(s)
    return back


def hauptstrang(nodes, back):
    """Längster Weg im Graphen ohne Rückkanten und ohne die ausgelassenen Kanten nach Knoten 2."""
    adj = {u: [t for t, _i, _k in nodes[u]['edges'] if (u, t) not in back and not (t == 2 and u != 1)] for u in nodes}
    memo = {}

    def lang(u):
        if u not in memo:
            best = []
            for v in adj[u]:
                w = lang(v)
                if len(w) > len(best):
                    best = w
            memo[u] = [u] + best
        return memo[u]

    return lang(1)


def dot_quelle(d, ranksep=0.34, nodesep=0.2, spine=True):
    nodes = d['nodes']
    back = back_edges(nodes)
    strang = set(hauptstrang(nodes, back)) if spine else set()
    gr = '#1E8A1E'
    rt = '#C4252B'
    L = ['digraph knoten {',
         f'  graph [rankdir=TB, nodesep={nodesep}, ranksep={ranksep}, ordering=out, fontname="Helvetica", pad=0.15];',
         '  node [fontname="Helvetica-Bold", fontsize=10, style=filled, fillcolor=white, margin="0.05,0.03"];',
         '  edge [fontname="Helvetica", fontsize=7, arrowsize=0.6];']

    def lab(num, text, bold=True):
        t = f'<B>{text}</B>' if bold else text
        return (f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0"><TR><TD><FONT POINT-SIZE="6" '
                f'COLOR="#444444">{num}</FONT></TD></TR><TR><TD>{t}</TD></TR></TABLE>>')

    for num in sorted(nodes):
        n = nodes[num]
        if n['typ'] == 'Konnektor':
            a = f'shape=ellipse, fillcolor="#E6E6E6", label={lab(num, "Konn. " + n["text"])}'
        elif n['typ'] == 'Phasenzuordnung':
            a = f'shape=parallelogram, fillcolor="#DCE6F5", label={lab(num, esc(n["text"]))}'
        elif n['typ'] == 'Test':
            a = f'shape=diamond, label={lab(num, "A-%03d" % n["anw"])}'
        else:
            code = 'A-%03d' % n['anw'] if n['anw'] is not None else esc(n['text'])
            if n['end']:
                a = f'shape=box, peripheries=2, fillcolor="#F5D0D0", label={lab(num, code)}'
            else:
                a = f'shape=box, label={lab(num, code)}'
        if num in strang:
            a += ', group=main'
        L.append(f'  n{num} [{a}];')

    for num in sorted(nodes):
        n = nodes[num]
        for t, i, k in n['edges']:
            if t == 2 and num != 1:
                continue        # Rückkanten nach Knoten 2: nicht im Layout, sondern als Sammelbus (ueberlagerung)
            col = {'wahr': gr, 'falsch': rt, None: 'black'}[k]
            at = [f'color="{col}"', f'fontcolor="{col}"']
            if k == 'falsch':
                at.append('style=dashed')
            if len(nodes[t]['ein']) > 1:
                at += [f'headlabel="{i}"', 'labelfontsize=7', 'labeldistance=1.3', f'labelfontcolor="{col}"']
            if (num, t) in back:
                at.append('constraint=false')
            L.append(f'  n{num} -> n{t} [{", ".join(at)}];')

    L.append('}')
    return '\n'.join(L)



def dot_json(dotf):
    r = subprocess.run(['dot', '-Tjson', dotf], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('dot -Tjson: ' + r.stderr)
    data = json.loads(r.stdout)
    bb = [float(x) for x in data['bb'].split(',')]
    pos = {}
    for o in data['objects']:
        nm = o.get('name', '')
        if not re.fullmatch(r'n\d+', nm):
            continue
        x, y = (float(v) for v in o['pos'].split(','))
        poly = None
        for op in o.get('_draw_', []):
            if op.get('op') in ('p', 'P'):
                poly = [tuple(pt) for pt in op['points']]
                break
        pos[int(nm[1:])] = dict(cx=x, cy=y, w=float(o['width']) * 72, h=float(o['height']) * 72, poly=poly)
    return bb, pos


def poly_x_at(poly, y, rechts=True):
    xs = []
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 - y) * (y2 - y) <= 0 and y1 != y2:
            xs.append(x1 + (x2 - x1) * (y - y1) / (y2 - y1))
    return max(xs) if rechts else min(xs)


BUS_DX, BUS_ABSTAND, EIN_DY = 12.0, 7.0, 5.6
UNTEN_EXTRA = 26.0     # Platz unter dem tiefsten Rang: der Bus-Weg läuft in der Lücke UNTER dem Rang des Quellknotens


def ueberlagerung(d, pos, gw, gh, offx, offy, extra, pfad):
    """Zeichnet (unter den Knoten) die Rückkanten nach Knoten 2 als geordneten Sammelbus rechts.
    Konnektoren gleicher Nummer werden bewusst NICHT durch Linien verbunden: die Nummer genügt. Seite: (gw+extra) x gh."""
    nodes = d['nodes']
    c = rl_canvas.Canvas(pfad, pagesize=(gw + extra, gh))
    P = lambda n: (pos[n]['cx'] + offx, pos[n]['cy'] + offy)
    farbe = {'wahr': (C_WAHR, None), 'falsch': (C_FALSCH, (3, 2)), None: (colors.black, None)}

    # --- Sammelbus nach Knoten 2
    eing = []                     # (quelle, eingang, art)
    for num in sorted(nodes):
        for t, i, k in nodes[num]['edges']:
            if t == 2 and num != 1:
                eing.append((num, i, k))
    # tiefste Quelle = äußerster Bus = oberster Eintritt (kreuzungsfrei, s. Überlegung im Kopf der Funktion)
    eing.sort(key=lambda e: pos[e[0]]['cy'])
    p2 = pos[2]
    cx2, cy2 = P(2)
    n_e = len(eing)
    xmax = max(pos[n]['cx'] + pos[n]['w'] / 2 for n in pos) + offx
    ymid = cy2 + (n_e - 1) * EIN_DY / 2
    kreuz, ausserhalb = [], []
    rang_zaehler = {}
    for k, (src, inp, art) in enumerate(eing):
        col, dash = farbe[art]
        xb = xmax + BUS_DX + k * BUS_ABSTAND
        ye = ymid - k * EIN_DY                           # oberster Eintritt zuerst
        sx0, sy = P(src)
        sx = sx0 + pos[src]['w'] / 2
        rang = [n_ for n_, q in pos.items() if abs(P(n_)[1] - sy) < 1.0]
        unten = min(P(n_)[1] - pos[n_]['h'] / 2 for n_ in rang)
        rang_n = rang_zaehler.get(round(sy), 0)
        rang_zaehler[round(sy)] = rang_n + 1
        yg = unten - 9.0 - rang_n * 3.0                    # Lücke zwischen den Rängen: dort liegen keine Knoten
        xn = poly_x_at(p2['poly'], ye - offy, True) + offx if p2['poly'] else cx2 + p2['w'] / 2
        weg = [(sx, sy), (sx + 7.0, sy), (sx + 7.0, yg), (xb, yg), (xb, ye), (xn + 4.0, ye)]
        c.saveState()
        c.setStrokeColor(col)
        c.setFillColor(col)
        c.setLineWidth(0.9)
        if dash:
            c.setDash(*dash)
        pth = c.beginPath()
        pth.moveTo(*weg[0])
        for q_ in weg[1:]:
            pth.lineTo(*q_)
        c.drawPath(pth, stroke=1, fill=0)
        c.setDash()
        pt = c.beginPath()
        pt.moveTo(xn, ye); pt.lineTo(xn + 4.6, ye + 1.8); pt.lineTo(xn + 4.6, ye - 1.8); pt.close()
        c.drawPath(pt, stroke=0, fill=1)
        c.setFont('Helvetica', 5.4)
        c.drawString(xn + 7.0, ye + 0.8, str(inp))
        c.restoreState()
        # Prüfung: liegt ein Wegpunkt außerhalb der Seite (dann würde die Verbindung abgeschnitten)?
        if any(x_ < 0 or y_ < 0 or x_ > gw + extra or y_ > gh for x_, y_ in weg):
            ausserhalb.append(src)
        # Prüfung: schneidet der Weg einen anderen Knoten (außer Quelle und Knoten 2)?
        for (xa, ya), (xe, ye_) in zip(weg, weg[1:]):
            for n2, q in pos.items():
                if n2 in (src, 2):
                    continue
                nx, ny = P(n2)
                if (min(xa, xe) < nx + q['w'] / 2 and max(xa, xe) > nx - q['w'] / 2 and
                        min(ya, ye_) < ny + q['h'] / 2 and max(ya, ye_) > ny - q['h'] / 2):
                    kreuz.append((src, n2))
    c.save()
    return dict(eing=[(s_, i_) for s_, i_, _ in eing], kreuz=kreuz, ausserhalb=ausserhalb,
                xbus=xmax + BUS_DX + (n_e - 1) * BUS_ABSTAND)


def knotengraph(d, pfad, tmp):
    nodes = d['nodes']
    st = statistik(d)
    stand = d['stand']

    # --- 1. Graphviz: einseitiges Vektor-PDF in Originalgröße
    dotf = os.path.join(tmp, 'knoten.dot')
    gpdf = os.path.join(tmp, 'knoten.pdf')
    open(dotf, 'w', encoding='utf-8').write(dot_quelle(d))
    r = subprocess.run(['dot', '-Tpdf', dotf, '-o', gpdf], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('dot: ' + r.stderr)
    box = PdfReader(gpdf).pages[0].mediabox
    gwp, ghp = float(box.width), float(box.height)
    bb, pos = dot_json(dotf)
    offx, offy = (gwp - (bb[2] - bb[0])) / 2, (ghp - (bb[3] - bb[1])) / 2     # Rand der Graphviz-Seite um den Graphen
    RAND = 8.0
    gw0, gh = (bb[2] - bb[0]) + 2 * RAND, (bb[3] - bb[1]) + 2 * RAND + UNTEN_EXTRA
    n_bus = sum(1 for n in nodes.values() for t, _i, _k in n['edges'] if t == 2 and n['num'] != 1)
    extra = BUS_DX + n_bus * BUS_ABSTAND + 6
    ovf = os.path.join(tmp, 'ueberlagerung.pdf')
    ueb = ueberlagerung(d, pos, gw0, gh, RAND, RAND + UNTEN_EXTRA, extra, ovf)
    comb = PageObject.create_blank_page(width=gw0 + extra, height=gh)
    comb.merge_page(PdfReader(ovf).pages[0])          # zuerst Bus/Verweise, darüber die Knoten (verdecken Kreuzungen)
    comb.merge_transformed_page(PdfReader(gpdf).pages[0], Transformation().translate(RAND - offx, RAND + UNTEN_EXTRA - offy))
    cw = PdfWriter()
    cw.add_page(comb)
    gpdf = os.path.join(tmp, 'knoten_komplett.pdf')
    with open(gpdf, 'wb') as f:
        cw.write(f)
    gw = gw0 + extra
    if ueb['kreuz']:
        print('HINWEIS Bus schneidet Knoten (Quelle, Knoten):', ueb['kreuz'])
    if ueb['ausserhalb']:
        raise RuntimeError(f'Bus-Weg liegt außerhalb der Seite (Verbindung würde abgeschnitten), Quellknoten: {ueb["ausserhalb"]}')
    print('Bus-Reihenfolge (Quelle, Eingang):', ueb['eing'], '| Seitenrand Graphviz', round(offx, 1), round(offy, 1))

    # --- 2. feste Kachelung: 2 Spalten, Skalierung aus der Breite (PDF.md 6)
    cols = 2
    s = (cols * TW - OV) / gw
    s = min(s, 1.0)
    rows = 1 if gh * s <= TH else math.ceil((gh * s - OV) / (TH - OV))
    cols_n = cols if gw * s > TW else 1
    ntiles = rows * cols_n

    # --- 3. Deckblatt und Referenzseiten (reportlab)
    fuss_t = 'Kacheln überlappen sich ca. 7 mm. Lesereihenfolge: zeilenweise, links → rechts, oben → unten.'
    sp = ParagraphStyle('p', fontName='DV', fontSize=9.5, leading=12.5, spaceAfter=5)
    s_t = ParagraphStyle('t', fontName='DV-B', fontSize=16, leading=20, spaceAfter=4)
    s_h2 = ParagraphStyle('h2', fontName='DV-B', fontSize=11, leading=14, spaceBefore=7, spaceAfter=3)
    s_c = ParagraphStyle('c', fontName='DV', fontSize=8.5, leading=10.5)
    s_cb = ParagraphStyle('cb', parent=s_c, fontName='DV-B')

    t2 = d['t2']
    rdata = [[Paragraph(h, s_cb) for h in ('Kurzcode', 'Volltext', 'Art')]]
    for num in sorted(t2):
        rdata.append([Paragraph(f'A-{num:03d}', s_c), Paragraph(esc(kurz(t2[num]['desc'])), s_c), Paragraph(t2[num]['art'], s_c)])
    rtab = Table(rdata, colWidths=[52, 450, 33], repeatRows=1, splitInRow=1)
    rtab.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.4, GRID), ('BACKGROUND', (0, 0), (-1, 0), KOPF),
                              ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 3),
                              ('RIGHTPADDING', (0, 0), (-1, -1), 3), ('TOPPADDING', (0, 0), (-1, -1), 2),
                              ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))

    def deck_story():
        return [
            Paragraph('C8205 Knotengraph', s_t),
            Paragraph('Ablaufplan der Befehlsverarbeitung (Phasen I bis IV) als Knoten-/Testgraph des C 8205. Quellen: '
                      f'C8205-Interpreter-Eingänge_der_Knoten.md (Graph, {st["n"]} Knoten) und '
                      f'C8205-Interpreter-Beschreibung_der_Knoten.md (Variablentabelle T2, {st["verw"]} verwendete '
                      f'Anweisungen/Tests). Stand {stand}.', sp),
            Paragraph(f'<b>Layoutraster:</b> {rows} Zeile(n) × {cols_n} Spalte(n) = {ntiles} A4-Seiten, Skalierung {round(s * 100)} %. '
                      'Die Kacheln überlappen sich um ca. 7 mm, damit Linien über Seitengrenzen hinweg weiterverfolgt werden können.', sp),
            Paragraph('<b>Lesereihenfolge:</b> zeilenweise, links nach rechts, oben nach unten. Die Position steht in der Kopfzeile jeder '
                      'Kachelseite (Blatt, Zeile, Spalte). Die Kachelseiten beginnen auf einer geraden Seitenzahl, damit sie in der '
                      'Doppelseitenansicht paarweise (Spalte 1 links, Spalte 2 rechts) erscheinen.', sp),
            Paragraph('<b>Kurzcodes:</b> A-nnn steht für ANWEISUNG-nnn der Variablentabelle T2 (Anweisung oder Test). Der Volltext steht auf '
                      'den folgenden Referenzseiten, die Anmerkungen der Quelle im PDF „Knotentabellen“. Die kleine Zahl über dem Kurzcode ist '
                      'die Knotennummer. Eine Zahl an einer Pfeilspitze nennt den Eingang des Zielknotens, wenn dieser mehrere Eingänge hat.', sp),
            Paragraph('<b>Konnektoren:</b> Konnektoren mit gleicher Nummer sind verbunden, auch wenn Ein- oder Ausgang fehlt. '
                      'Zusammengehörige Konnektoren sind nicht durch Linien verbunden, die gleiche Nummer genügt. '
                      'Konnektor B ist extern und kennzeichnet den Eintritt in den Ablauf von außerhalb.', sp),
            Paragraph('<b>Gleichzeitige Anweisungen</b> (&amp;&amp;) werden mit den Registerwerten ausgewertet, die unmittelbar vor dem Knoten galten.', sp),
            Paragraph('Knoten- und Symboltypen', s_h2),
            Sym('konn', 'Konnektor / Verweis, kein eigener Ablaufschritt (gleiche Nummer = verbunden)'),
            Sym('phase', 'Phasenzuordnung / Abschnittsmarke (Beginn Phase I bis IV)'),
            Sym('anw', 'Anweisung / Aktion (A-nnn, Volltext auf den Referenzseiten)'),
            Sym('test', 'Test / Verzweigung (A-nnn, Ausgang wahr oder falsch)'),
            Sym('end', 'Endzustand (der Knotenautomat hält an)'),
            Paragraph('Kanten und Farben', s_h2),
            Sym('wahr', 'grün, durchgezogen: positiv / wahr / OK'),
            Sym('falsch', 'rot, gestrichelt: negativ / falsch / Fehler'),
            Sym('std', 'schwarz: neutraler Standardfluss, unbedingte Weiterschaltung'),
            PageBreak(),
            Paragraph('Kurzcodes A-nnn', s_t),
            Paragraph('Kurzcode → Volltext aus der Variablentabelle T2. Art: ARW = Ausführung durch das Rechenwerk, AH = Hardware, '
                      'ZST = Endzustand, V = allgemein formuliert (Detailklärung offen).', sp),
            rtab]

    def baue_front(fn, gesamt):
        doc = BaseDocTemplate(fn, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M + FTR)

        def pg(c, dc):
            sub = 'Deckblatt und Referenzseiten' if c.getPageNumber() == 1 else 'Referenzseiten Kurzcodes A-nnn'
            kopf_fuss(c, 'C8205 Knotengraph', sub, None, c.getPageNumber(), gesamt)

        fr = Frame(M, M + FTR, TW, PH - 2 * M - FTR - HDR, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        doc.addPageTemplates([PageTemplate(id='p', frames=[fr], onPage=pg)])
        doc.build(copy.deepcopy(deck_story()))
        return doc.page

    fr0 = os.path.join(tmp, 'front0.pdf')
    k_front = baue_front(fr0, 0)                      # 1 Deckblatt + Referenzseiten
    erste_kachel = k_front + 1
    leer = 1 if erste_kachel % 2 == 1 else 0           # Kachelseiten beginnen auf gerader Seitenzahl (PDF.md 4)
    gesamt = k_front + leer + ntiles
    frp = os.path.join(tmp, 'front.pdf')
    baue_front(frp, gesamt)

    # --- 4. Kacheln: skaliertes Graph-PDF verschieben, auf den Inhaltsbereich beschneiden, Kopf/Fuß als Overlay
    writer = PdfWriter()
    for p in PdfReader(frp).pages:
        writer.add_page(p)

    ov_buf = io.BytesIO()
    oc = rl_canvas.Canvas(ov_buf, pagesize=A4)
    seitenr = k_front
    if leer:
        seitenr += 1
        oc.setFillColor(colors.HexColor('#999999'))
        oc.setFont('DV-I', 8)
        oc.drawCentredString(PW / 2, PH / 2, 'Leerseite – damit die Kachelseiten paarweise nebeneinander stehen')
        kopf_fuss(oc, '', None, None, seitenr, gesamt, mit_kopf=False)
        oc.showPage()
    yb = M + FTR
    yt = yb + TH
    blatt = 0
    kachel_specs = []
    for i in range(rows):
        for j in range(cols_n):
            blatt += 1
            seitenr += 1
            tit = f'Knotengraph  Blatt {blatt}/{ntiles} (Zeile {i + 1}/{rows}, Spalte {j + 1}/{cols_n})'
            kopf_fuss(oc, tit, None, fuss_t, seitenr, gesamt, mit_kopf=True, legende=graph_legende)
            oc.showPage()
            kachel_specs.append((i, j))
    oc.save()
    ov = PdfReader(io.BytesIO(ov_buf.getvalue()))

    pos = 0
    if leer:
        bl = PageObject.create_blank_page(width=PW, height=PH)
        bl.merge_page(ov.pages[0])
        writer.add_page(bl)
        pos = 1
    for (i, j) in kachel_specs:
        page = PageObject.create_blank_page(width=PW, height=PH)
        src = PdfReader(gpdf).pages[0]
        tx = M - j * (TW - OV)
        ty = yt - gh * s + i * (TH - OV)
        page.merge_transformed_page(src, Transformation().scale(s, s).translate(tx, ty))
        data = page.get_contents().get_data()
        clip = f'q {M:.2f} {yb:.2f} {TW:.2f} {TH:.2f} re W n\n'.encode() + data + b'\nQ\n'
        stream = StreamObject()
        stream.set_data(clip)
        page[NameObject('/Contents')] = writer._add_object(stream)
        page.merge_page(ov.pages[pos])
        pos += 1
        writer.add_page(page)

    writer.add_metadata({'/Title': 'C8205 Knotengraph', '/Author': 'C8205-Interpreter-Projekt',
                         '/Subject': f'Ablaufplan der Befehlsverarbeitung, Stand {stand}'})
    try:
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    except Exception:
        pass
    with open(pfad, 'wb') as f:
        writer.write(f)
    return dict(gesamt=gesamt, k_front=k_front, leer=leer, rows=rows, cols=cols_n, s=s, gw=gw, gh=gh)


# ---------------------------------------------------------------------------------------------
def finde_wurzel(start):
    """Projektwurzel = naechster Ordner oberhalb von start, der markdown-dateien/ enthaelt
    (die Skripte liegen in PDF/pdf-layout-scripte/, die Wurzel also zwei Ebenen darueber)."""
    d = start
    while True:
        if os.path.isdir(os.path.join(d, 'markdown-dateien')):
            return d
        p = os.path.dirname(d)
        if p == d:
            return os.path.dirname(os.path.dirname(start))
        d = p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mdverz', default=None, help='Vorgabe: markdown-dateien/ in der Projektwurzel')
    ap.add_argument('--ausgabe', default=None, help='Vorgabe: PDF/ in der Projektwurzel')
    ap.add_argument('--interp', default=None, help='c8205_interp.py: Einlesen gegen load_graph()/load_t2() prüfen')
    ap.add_argument('--nur', choices=['graph', 'tabellen'], default=None)
    ap.add_argument('--dot-behalten', default=None, help='Ordner, in den die Graphviz-Zwischendateien kopiert werden')
    a = ap.parse_args()
    wurzel = finde_wurzel(os.path.dirname(os.path.abspath(__file__)))
    a.mdverz = a.mdverz or os.path.join(wurzel, 'markdown-dateien')
    a.ausgabe = a.ausgabe or os.path.join(wurzel, 'PDF')
    os.makedirs(a.ausgabe, exist_ok=True)

    d = lade(a.mdverz)
    st = statistik(d)
    print(f'Stand {d["stand"]}: {st["n"]} Knoten {st["typen"]}, Endknoten {st["ends"]}; '
          f'T2: {st["t2n"]} Einträge {st["arten"]}, {st["verw"]} in Knoten verwendet')
    for w in d['warn']:
        print('WARNUNG', w)
    for m in d['pruef']:
        print('FEHLER im Einlesen/Konsistenz:', m)
    if a.interp:
        diff = pruefe_interpreter(d, a.interp)
        print('Abgleich mit Interpreter:', 'identisch' if not diff else '')
        for x in diff:
            print('  ABWEICHUNG', x)
    if a.nur != 'graph':
        import erzeuge_knotentabellen_pdf as T      # Layoutscript der Knotentabellen (Deckblatt, Folgeseiten nach PDF.md 3a/4)
        n = T.erzeuge(d, os.path.join(a.ausgabe, 'C8205-Knotentabellen_A4.pdf'))
        print(f'C8205-Knotentabellen_A4.pdf: {n} Seiten')
    if a.nur != 'tabellen':
        with tempfile.TemporaryDirectory() as tmp:
            info = knotengraph(d, os.path.join(a.ausgabe, 'C8205-Knotengraph_A4.pdf'), tmp)
            if a.dot_behalten:
                import shutil
                os.makedirs(a.dot_behalten, exist_ok=True)
                for fn in ('knoten.dot', 'knoten.pdf', 'knoten_komplett.pdf'):
                    shutil.copy(os.path.join(tmp, fn), a.dot_behalten)
        print(f'C8205-Knotengraph_A4.pdf: {info["gesamt"]} Seiten (Deckblatt+Referenz {info["k_front"]}, Leerseite {info["leer"]}, '
              f'Raster {info["rows"]}x{info["cols"]}, Skalierung {info["s"] * 100:.0f} %, Graph {info["gw"]:.0f}x{info["gh"]:.0f} pt)')


if __name__ == '__main__':
    main()
