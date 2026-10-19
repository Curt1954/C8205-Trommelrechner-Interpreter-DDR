# -*- coding: utf-8 -*-
"""erzeuge_bedienungsanleitung_pdf.py -- erzeugt C8205-Bedienungsanleitung_Interpreter_A4.pdf
(redaktionell, nach C8205-Interpreter-PDF.md; Bausteine aus pdflib.py).

Quellen:  markdown-dateien/C8205-Interpreter-Python_Interpreter.md        (Hauptquelle, Abschnitte 1-13)
          markdown-dateien/C8205-Interpreter-Durchführung_eines_Tests.md   (Testformat, Marken, Prüfungen)
Aufruf:   python3 PDF/pdf-layout-scripte/erzeuge_bedienungsanleitung_pdf.py [ZIEL.pdf] [--stand TT.MM.JJJJ]
                                                                           [--wurzel PROJEKTORDNER] [--behalte-labor]
                                                                           [--ohne-abnahme]
Vorgabe:  PDF/C8205-Bedienungsanleitung_Interpreter_A4.pdf (eine Ebene über dem Ordner dieses Skripts); der Projektordner
          wird oberhalb des Skripts gesucht (erster Ordner mit c8205_interp.py und markdown-dateien/).

Aufbau (PDF.md 4.4): Seite 1 Deckblatt (4.2, Daten aus 4.6), Seite 2 Lesehinweise, Seite 3 Inhaltsverzeichnis,
dann der Inhalt (Kapitel 1-9, Anhang A-C). Kapitel beginnen nicht auf neuer Seite (3a.6); nur die Kurzreferenz
(Kapitel 9) steht auf einer eigenen, einzeln druckbaren Seite (Python_Interpreter.md 14.3).

Beispiele (Python_Interpreter.md 14.3/14.4): Alle Terminalausgaben stammen aus echten Läufen. Das Skript legt einen
Wegwerf-Arbeitsordner an, kopiert c8205_interp.py, die Wrapper, erzeuge_leere_trommel.py und die beiden
Regelwerk-Dateien des Knotengraphen hinein und führt jedes Beispiel dort über ein Pseudo-Terminal aus (damit der
Interpreter seine Farben ausgibt: Dunkelgelb = Schreibwerk, Rot = Gerätefehler). Die Trommeldatei des Projekts wird
nicht berührt. Erwartete Rückkehrcodes sind je Beispiel angegeben; weicht ein Lauf ab, bricht die Erzeugung ab, weil
dann der Text der Anleitung nicht mehr zum Interpreter passt.

Version der Quellen und Stand (Erzeugungsdatum) werden beim Erzeugen gelesen, nicht von Hand gesetzt (PDF.md 4.3).
Die Version des Interpreters stammt aus `python3 c8205_interp.py --version`.
"""

# ---------------------------------------------------------------------------------------------
# Eigenstaendig: Die Module pdflib.py sind unten als Quelltext eingebettet und werden
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

import argparse
import os
import pty
import re
import select
import shutil
import subprocess
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
import pdflib as L
from pdflib import (ST, P, bullets, h1, h2, note, fmt, esc, FRAME_W, INK, MUTED, RULE, CODE_BG, HEAD_BG, RED,
                    make_toc, merge_intro, head_with_block)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, CondPageBreak

# ------------------------------------------------------------------ Deckblattdaten (PDF.md 4.6, 8)
PDF_NAME = 'C8205-Bedienungsanleitung_Interpreter_A4.pdf'
TITEL = 'Bedienungsanleitung Python-Interpreter'
UNTERTITEL = 'Aufruf, Schalter und Geräte von c8205_interp.py'
ART = 'HANDBUCH'
BEREICH = 'INTERPRETER'
QUELLEN = ['C8205-Interpreter-Python_Interpreter.md', 'C8205-Interpreter-Durchführung_eines_Tests.md']
BESCHREIBUNG = ('Diese Anleitung zeigt, wie man Testprogramme für den Cellatron C 8205 schreibt, mit dem '
                'Python-Interpreter ausführt und die Ergebnisse liest: Aufruf und Schalter, Aufbau der Testdatei, '
                'Ein- und Ausgabegeräte, Endzeile, Protokoll und Fehlermeldungen. Sie richtet sich an Personen, die '
                'den Aufbau des Interpreters nicht kennen. Den Rechner selbst beschreiben die PDFs '
                '„Rechnerbeschreibung“ und „Bedienpult und Peripherie“.')
KOPF_LEGENDE = 'Eingaben nach „$“ · Ausgabe des Rechners (Schreibwerk) in Dunkelgelb · Meldungen zu Geräten in Rot („FEHLER:“)'

PROTOKOLLKOPF_ALT = False     # wird in kap6() aus dem echten Protokoll gesetzt
SW_FARBE = '#8A6D00'          # Dunkelgelb: Ausgabe des Rechners über das Schreibwerk (Python_Interpreter.md 14.3)
INTERP_VERSION = '?'          # wird in main() aus --version gelesen


def set_stand(stand):
    """Stand = Erzeugungsdatum (PDF.md 4.3); gleicher Wert auf Deckblatt und in der Fusszeile."""
    L.STAND = stand
    L.FOOTER_LEFT = 'C8205-Interpreter-Projekt · Stand ' + stand


L.HEADER_TITLE = 'C 8205 – ' + TITEL
L.HEADER_LEGEND = KOPF_LEGENDE


# ------------------------------------------------------------------ Dateien finden (Umlaute in Dateinamen)
def finde_datei(ordner, name):
    """Info-ZIP-unzip ohne UTF-8-Namen legt 'ü' als '#U00fc' ab; beide Schreibweisen werden gefunden."""
    maskiert = ''.join(c if ord(c) < 128 else '#U%04x' % ord(c) for c in name)
    for n in (name, maskiert):
        pfad = os.path.join(ordner, n)
        if os.path.isfile(pfad):
            return pfad
    sys.exit('FEHLER: Quelle nicht gefunden: %s' % os.path.join(ordner, name))


# ------------------------------------------------------------------ Tabellen
def tbl(rows, fr, **kw):
    """Tabelle nach PDF.md 3a.3 (pdflib.tbl); fr = Spaltenanteile (Summe 1)."""
    return L.tbl(rows, [f * FRAME_W for f in fr], **kw)


def tbl_markup(rows, fr):
    """Wie tbl, aber die Zellen sind fertiges reportlab-Markup (für die Farblegende)."""
    cell, cellh = ST['cell'], ST['cellh']
    data = [[Paragraph(v, cellh if r == 0 else cell) for v in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[f * FRAME_W for f in fr], repeatRows=1)
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                           ('LEFTPADDING', (0, 0), (-1, -1), 4.5), ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
                           ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                           ('LINEBELOW', (0, 0), (-1, -1), 0.4, RULE), ('BOX', (0, 0), (-1, -1), 0.5, RULE),
                           ('BACKGROUND', (0, 0), (-1, 0), HEAD_BG)]))
    return [KeepTogether([t]), Spacer(1, 7)]


# ------------------------------------------------------------------ Terminalblöcke mit Farbe (PDF.md 3a.5)
_ANSI = re.compile(r'\x1b\[(\d+)m')
_STIL_VON_CODE = {'33': 'sw', '31': 'err'}


def ansi_zeilen(text):
    """Zerlegt Terminaltext mit ANSI-Farben in Zeilen aus (Text, Stil)-Stücken. Stil: None | 'sw' | 'err'."""
    zeilen, aktuell, stil = [], [], None

    def add(s, st):
        nonlocal aktuell
        teile = s.split('\n')
        for i, t in enumerate(teile):
            if i > 0:
                zeilen.append(aktuell)
                aktuell = []
            if t:
                if aktuell and aktuell[-1][1] == st:
                    aktuell[-1] = (aktuell[-1][0] + t, st)
                else:
                    aktuell.append((t, st))

    pos = 0
    for m in _ANSI.finditer(text):
        add(text[pos:m.start()], stil)
        stil = None if m.group(1) == '0' else _STIL_VON_CODE.get(m.group(1))
        pos = m.end()
    add(text[pos:], stil)
    if aktuell:
        zeilen.append(aktuell)
    return zeilen


def _markup(text, stil):
    t = esc(text).replace(' ', '&nbsp;')
    if stil == 'cmd':
        return '<b>%s</b>' % t
    if stil == 'sw':
        return '<font color="%s"><b>%s</b></font>' % (SW_FARBE, t)
    if stil == 'err':
        return '<font color="#%s">%s</font>' % (RED.hexval()[2:], t)
    return t


def _spannen(zeile, maxc, einzug='    '):
    """Umbruchstellen wie pdflib._wrap_line, aber als Spannen der Originalzeile: [(Einzug, von, bis)]."""
    if len(zeile) <= maxc:
        return [('', 0, len(zeile))]
    res, pos, erste = [], 0, True
    while len(zeile) - pos > (maxc if erste else maxc - len(einzug)):
        lim = maxc if erste else maxc - len(einzug)
        rest = zeile[pos:]
        cut = rest.rfind(' ', int(lim * 0.55), lim)
        if cut <= 0:
            cut = lim
        res.append(('' if erste else einzug, pos, pos + cut))
        pos += cut
        while pos < len(zeile) and zeile[pos] == ' ':
            pos += 1
        erste = False
    res.append(('' if erste else einzug, pos, len(zeile)))
    return res


def tcode(zeilen, caption=None, keep=14):
    """Codeblock mit Farbstücken (zeilen: Liste von Listen aus (Text, Stil)); Maße und Trennregeln wie pdflib.code."""
    maxc = int((FRAME_W - 16) / pdfmetrics.stringWidth('0', 'DVM', ST['code'].fontSize)) - 1
    rows, plain = [], []
    for z in zeilen:
        text = ''.join(t for t, _ in z)
        grenzen, p = [], 0
        for t, s in z:
            grenzen.append((p, p + len(t), s))
            p += len(t)
        for einzug, a, b in _spannen(text.rstrip(), maxc):
            mk = esc(einzug).replace(' ', '&nbsp;')
            for (s0, s1, s) in grenzen:
                lo, hi = max(a, s0), min(b, s1)
                if lo < hi:
                    mk += _markup(text[lo:hi], s)
            rows.append([Paragraph(mk or '&nbsp;', ST['code'])])
            plain.append((einzug + text[a:b]).strip())
    t2 = Table(rows, colWidths=[FRAME_W], splitByRow=1)
    t2.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), CODE_BG),
                            ('LINEBEFORE', (0, 0), (0, -1), 3.2, MUTED),
                            ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                            ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, 0), 4), ('BOTTOMPADDING', (0, -1), (-1, -1), 4)]))
    n = len(rows)
    t2._isLongCode = n > 12
    if n > 12:       # lange Blöcke nur an Leerzeilen trennen (oben mind. 6, unten mind. 4 Zeilen), sonst spätestens nach 40
        blank = {i for i, p in enumerate(plain) if not p}
        erlaubt, last = set(), 0
        for i in range(5, n - 4):
            if i in blank or i - last >= 40:
                erlaubt.add(i)
                last = i
        cmds = [('NOSPLIT', (0, 0), (-1, 5)), ('NOSPLIT', (0, n - 4), (-1, n - 1))]
        for i in range(5, n - 4):
            if i not in erlaubt:
                cmds.append(('NOSPLIT', (0, i), (-1, i + 1)))
        t2.setStyle(TableStyle(cmds))
    teile = [t2, Paragraph(fmt(caption), ST['cap']) if caption else Spacer(1, 6)]
    if n <= min(keep, 12):
        kt = KeepTogether(teile)
        kt._isCode = True
        return [kt]
    return teile


# ------------------------------------------------------------------ Beispiel-Labor: echte Läufe
def _pty_lauf(cmd, cwd, env_zusatz=None, limit=600):
    """Führt cmd über bash in einem Pseudo-Terminal aus; liefert (Text mit ANSI-Farben, Rückkehrcode)."""
    master, slave = pty.openpty()
    env = dict(os.environ)
    env.pop('NO_COLOR', None)
    env.update({'PYTHONIOENCODING': 'utf-8', 'TERM': 'xterm', 'COLUMNS': '80', 'LC_ALL': 'C.UTF-8'})
    env.pop('DISPLAY', None)
    env.pop('WAYLAND_DISPLAY', None)
    if env_zusatz:
        env.update(env_zusatz)
    p = subprocess.Popen(['bash', '-c', cmd], cwd=cwd, stdin=subprocess.DEVNULL, stdout=slave, stderr=slave,
                         env=env, close_fds=True)
    os.close(slave)
    buf = b''
    while True:
        try:
            r, _, _ = select.select([master], [], [], limit)
            if not r:
                p.kill()
                sys.exit('FEHLER: Beispiel läuft länger als %d s: %s' % (limit, cmd))
            d = os.read(master, 65536)
        except OSError:
            break
        if not d:
            break
        buf += d
    p.wait()
    os.close(master)
    return buf.decode('utf-8', 'replace').replace('\r\n', '\n'), p.returncode


class Labor:
    """Wegwerf-Arbeitsordner mit Kopie des Interpreters, in dem die Beispiele wirklich laufen."""
    BASIS = ('c8205_interp.py', 'c8205_interpreter.sh', 'c8205_interpreter.bat', 'erzeuge_leere_trommel.py',
             'markdown-dateien')

    def __init__(self, wurzel):
        self.dir = tempfile.mkdtemp(prefix='c8205_anleitung_')
        for n in self.BASIS[:4]:
            quelle = os.path.join(wurzel, n)
            if not os.path.isfile(quelle):                 # z. B. erzeuge_leere_trommel.py liegt in testscripte/
                quelle = os.path.join(wurzel, 'testscripte', n)
            shutil.copy2(quelle, self.dir)
            if n == 'erzeuge_leere_trommel.py':            # Skript liegt im Projekt in testscripte/ und nimmt das Projektverzeichnis
                ziel = os.path.join(self.dir, n)           # eine Ebene höher an; im Arbeitsordner liegt es im Stamm
                with open(ziel, encoding='utf-8') as f:
                    t = f.read()
                t = t.replace('os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
                              'os.path.dirname(os.path.abspath(__file__))')
                with open(ziel, 'w', encoding='utf-8', newline='') as f:
                    f.write(t)
        md = os.path.join(self.dir, 'markdown-dateien')
        os.makedirs(md)
        for n in ('C8205-Interpreter-Eingänge_der_Knoten.md', 'C8205-Interpreter-Beschreibung_der_Knoten.md'):
            shutil.copy2(finde_datei(os.path.join(wurzel, 'markdown-dateien'), n), os.path.join(md, n))
        self.lauefe = 0

    def aufraeumen(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def neu(self):
        """Leerer Arbeitsstand: alle Beispieldateien weg, leere Trommel erzeugen."""
        for n in os.listdir(self.dir):
            if n not in self.BASIS:
                pf = os.path.join(self.dir, n)
                shutil.rmtree(pf) if os.path.isdir(pf) else os.remove(pf)
        self.leere_trommel()

    def leere_trommel(self):
        out, rc = _pty_lauf('python3 erzeuge_leere_trommel.py', self.dir)
        if rc != 0:
            sys.exit('FEHLER: erzeuge_leere_trommel.py: %s' % out)

    def schreibe(self, pfad, text, binaer=None):
        ziel = os.path.join(self.dir, pfad)
        os.makedirs(os.path.dirname(ziel) or self.dir, exist_ok=True)
        with open(ziel, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)

    def dateien(self, liste, neu=True, zeigen=True):
        """Legt Dateien an (zuvor leerer Stand, wenn neu) und liefert die Codeblöcke mit Dateinamen als Unterschrift."""
        if neu:
            self.neu()
        s = []
        for pfad, text in liste:
            self.schreibe(pfad, text)
            if zeigen:
                s += L.code(text.rstrip('\n'), caption='Datei `%s`' % pfad)
        return s

    def sitzung(self, befehle, erwarte=None, kuerze=(), zeilen=None, caption=None, ersetze=(), leer=True):
        """Führt Befehle aus und liefert EINEN Terminalblock (Eingaben nach $ fett, Schreibwerk dunkelgelb, Fehler rot).
        erwarte: Liste der erwarteten Rückkehrcodes je Befehl (None = nicht prüfen); der Code stammt aus der
        Zeile 'Rückkehrcode: n', falls der Befehl sie ausgibt, sonst vom Prozess.
        kuerze: [(Anfang_von, Anfang_bis, Ersatztext, Muster)] ersetzt die Zeilen von der ersten mit Anfang_von bis zur
        ersten mit Anfang_bis (einschließlich) durch eine Hinweiszeile; alle ersetzten Zeilen müssen auf Muster passen.  zeilen: nur die ersten n Ausgabezeilen, danach '…'."""
        if leer:       # jede Sitzung beginnt auf frisch erzeugter leerer Trommel (Lesehinweise: „jeweils auf leerer Trommel“)
            self.leere_trommel()
        block = []
        for i, cmd in enumerate(befehle):
            block.append([('$ ' + cmd, 'cmd')])
            out, rc = _pty_lauf(cmd, self.dir)
            self.lauefe += 1
            out = out.replace(self.dir + os.sep, '').replace(self.dir, '.')
            if 'c8205_interp' in cmd:        # der Interpreter beginnt seine Ausgabe mit einer Leerzeile
                out = out.lstrip('\n')
            m = re.search(r'Rückkehrcode:\s*(\d+)', out)
            ist = int(m.group(1)) if m else rc
            if erwarte and i < len(erwarte) and erwarte[i] is not None and ist != erwarte[i]:
                sys.exit('FEHLER: Beispiel passt nicht zum Interpreter (Rückkehrcode %s statt %s):\n  %s\n%s'
                         % (ist, erwarte[i], cmd, out))
            for alt, neu_ in ersetze:
                out = out.replace(alt, neu_)
            ausgabe = ansi_zeilen(out)
            while ausgabe and not ausgabe[-1]:
                ausgabe.pop()
            for von, bis, text, muster in kuerze:
                txt = [''.join(t for t, _ in z) for z in ausgabe]
                a = next((k for k, x in enumerate(txt) if x.startswith(von)), None)
                b = next((k for k in range(a, len(txt)) if txt[k].startswith(bis)), None) if a is not None else None
                if b is None:
                    sys.exit('FEHLER: Kürzung %r..%r passt nicht zur Ausgabe von: %s' % (von, bis, cmd))
                if not all(re.search(muster, x) for x in txt[a:b + 1]):     # es darf nur Gleichförmiges weggelassen werden
                    sys.exit('FEHLER: Kürzung %r..%r würde abweichende Zeilen verbergen: %s' % (von, bis, cmd))
                ausgabe[a:b + 1] = [[(text, None)]]
            if zeilen and len(ausgabe) > zeilen:
                ausgabe = ausgabe[:zeilen] + [[('…', None)]]
            block += ausgabe
        return tcode(block, caption=caption)

    def ausgabe(self, befehl):
        """Nur ausführen und den Text zurückgeben (für Abnahme und Bedingungen im Text)."""
        out, rc = _pty_lauf(befehl, self.dir)
        return re.sub(r'\x1b\[\d+m', '', out), rc

    def lies(self, pfad):
        with open(os.path.join(self.dir, pfad), encoding='utf-8') as f:
            return f.read()


# Hinweiskasten zum Fenster „SW Ausgabe“: steht an vier Stellen (Python_Interpreter.md 14.3)
FENSTER_HINWEIS = ('**Fenster „SW Ausgabe“** (`--SW-TERMINAL`)**.** Das Fenster bleibt **immer offen**, auch nach dem '
                   'Ende des Tests, bis Sie es mit Klick auf X schließen. Es läuft als eigener Prozess; jeder Aufruf '
                   'öffnet ein neues Fenster. Text im Fenster lässt sich mit der Maus markieren und kopieren: sofort '
                   'beim Loslassen der Maustaste, mit Strg+C oder Strg+Einfg oder über das Kontextmenü (rechte '
                   'Maustaste). Das gilt unter Linux und unter Windows.')


# ------------------------------------------------------------------ Testdateien der Beispiele
RK = 'echo "Rückkehrcode: $?"'          # Standardabschluss der Beispielbefehle


def kopf3(text):
    """Fette Einleitungszeile eines Unterabschnitts (bleibt mit dem Folgenden zusammen); die Richtlinie kennt nur H1/H2."""
    stil = ParagraphStyle('kopf3', parent=ST['body'], keepWithNext=1, spaceBefore=4, spaceAfter=3)
    return Paragraph('<b>%s</b>' % fmt(text), stil)       # fmt kennt kein Fett um Code herum: Fett wird außen gesetzt


def cmd(c):
    """Befehl mit anschließender Ausgabe des Rückkehrcodes."""
    return '%s; %s' % (c, RK)


T_0015 = """Trommeldatei:
#DOK-0015 Test Ausgabebefehl
#PROT STUFE=2
0001: 00007240000
7240: 00004500030
7241: 00002720030
7242: 00000570030
7243: 00001210030
7244: 00001170030
7245: 00000610030
7246: 00000700030
7247: 00001110030
7250: 00000320030
7251: 00000010030
7252: 00000310030
7253: 00000070030
7254: 00000020030
7255: 00000015164
7256: 00000000020

Tastenfolge:
H G M-drücken E M-loslassen R
"""
T_AC = """Trommeldatei:
#PROT STUFE=0
#AC=00000000100
0000: 00003000210 # AC := AC + <3000>
0001: 00000000020
3000: 00000000045
Tastenfolge:
H G R
"""
T_BZ = """Trommeldatei:
#PROT STUFE=0
#BZ=0010
0011: 00000000020
Tastenfolge:
H M-drücken E M-loslassen R
"""
T_AC2 = """Trommeldatei:
#PROT STUFE=0
#AC=00000000100
#AC=00000000200
0000: 00000000020
Tastenfolge:
H G R
"""
T_STARTE = """Trommeldatei:
#PROT STUFE=0
#STARTE 4
0004: 00003000211 # 211 Laden
0005: 00003001210 # 210 Addieren
0006: 00000000020 # 020 Stopp
3000: 00000000100
3001: 00000000045

Prüfungen:
BZ=0007 AC=00000000145 US=1
"""
T_INT1 = """Trommeldatei:
#PROT STUFE=0
0000: 00003000211 # 211 Laden
#INTERRUPT H R
0001: 00003001210 # 210 Addieren
0002: 00000000020 # 020 Stopp
3000: 00000000100
3001: 00000000045
Tastenfolge:
H G R
Prüfungen:
BZ=0003 AC=00000000145 US=1
"""
T_INT2 = """Trommeldatei:
#PROT STUFE=0
0000: 00003000211 # 211 Laden
#INTERRUPT H G Ü E # Transport AC nach 7777, Test endet (letzte Taste E)
0001: 00003001210 # 210 Addieren
0002: 00000000020 # 020 Stopp
3000: 00000000100
3001: 00000000045
Tastenfolge:
H G R
Prüfungen:
7777: 00000000100
"""
T_INTF = """Trommeldatei:
#PROT STUFE=0
#INTERRUPT H R # Fehler: vor der ersten Befehlszeile
0000: 00000000020
0001: 00000000020
Tastenfolge:
H G R
"""
T_SPRUNG = """Trommeldatei:
#PROT STUFE=0
0004: 00000000020
Tastenfolge:
H G M+ E E E E M- R
"""
T_HALT = """Trommeldatei:
#PROT STUFE=0
0000: 00000000020
Tastenfolge:
H G
"""
T_UEE = """Trommeldatei:
#PROT STUFE=0
0000: 00000000020
Tastenfolge:
H G Ü E
"""
T_PRUEFE_OHNE = """Trommeldatei:
#PROT STUFE=0
0000: 00000000020
Tastenfolge:
H G R
Prüfungen:
US=1
--pruefe-stanzer1 soll.txt
"""
T_FALSE = """Trommeldatei:
#PROT STUFE=0
0000: 00003000211
0001: 00000000020
3000: 00000000100
Tastenfolge:
H G R
Prüfungen: False
AC=00000000101
"""
T_FORMAL = """Trommeldatei:
#PROT STUFE=0
0000: 000000002
0001: 00000000020
0001: 00000000010
Tastenfolge:
H G R
"""
T_SWZEILE = """Trommeldatei:
--sw-ausgabe SW-Ausgabe # Schreibwerk-Ausgabe in Datei
#PROT STUFE=0
0000: 00004500030
0001: 00001170030
0002: 00000250030
0003: 00000730030
0004: 00000000020
Tastenfolge:
H G R
"""
T_SWPRUEFE = T_SWZEILE.replace('H G R\n', 'H G R\nPrüfungen:\nUS=1\n--pruefe-sw-ausgabe sw-soll.txt\n')
T_TROMMEL_A = """Trommeldatei:
#PROT STUFE=0
0000: 00000000020
3000: 00000000100
Tastenfolge:
H G R
"""
T_TROMMEL_B = """Trommeldatei:
#PROT STUFE=0
0000: 00000000020
Tastenfolge:
H G R
Prüfungen:
US=1
3000: 00000000100
"""
T_STOP = """Trommeldatei:
#PROT STUFE=0
0000: 00000000020
Tastenfolge:
H G R
"""
T_STOP2 = T_STOP.replace('STUFE=0', 'STUFE=2')


# ------------------------------------------------------------------ Lesehinweise (Seite 2) und Inhaltsverzeichnis (Seite 3)
def lesehinweise():
    s = [Paragraph('Lesehinweise', ST['h1'])]
    s.append(P('**Gilt für:** `c8205_interp.py`, Version **%s** (Abfrage: `python3 c8205_interp.py --version`), zusammen '
               'mit den Wrappern `c8205_interpreter.sh` und `c8205_interpreter.bat` und dem Hilfsskript '
               '`erzeuge_leere_trommel.py`. Alle Beispiele dieser Anleitung sind beim Erzeugen des PDFs mit dieser Version '
               'ausgeführt worden, jeweils auf frisch erzeugter leerer Trommel; die Ausgaben sind übernommen, nicht von '
               'Hand geschrieben. Ändert sich der Interpreter (neuer Schalter, neues Token, neue Meldung), muss das PDF '
               'neu erzeugt werden.' % INTERP_VERSION))
    s.append(P('**Zielgruppe:** Personen, die Testprogramme für den C 8205 schreiben und durchrechnen, ohne den Aufbau des '
               'Interpreters zu kennen. Kenntnisse über Oktalzahlen und Register werden nicht vorausgesetzt; Begriffe stehen '
               'im Glossar (Anhang A).'))
    s.append(P('**Abgrenzung:** Die Anleitung erklärt die Bedienung des Interpreters, nicht den Rechner. Zum Rechner siehe die '
               'PDFs „Rechnerbeschreibung“ und „Bedienpult und Peripherie“; das Testformat im Wortlaut der Quelle steht im PDF '
               '„Durchführung eines Tests“, eine Einführung in das Schreiben von Tests im „Testhandbuch“.'))
    s.append(P('Legende der Darstellung', 'h2'))
    ink = '#%s' % INK.hexval()[2:]
    s += tbl_markup([
        ['Darstellung', 'Bedeutung'],
        ['<font name="DVM" size="8"><b>$ befehl</b></font>',
         'Eingabe im Terminal (Befehl, den Sie tippen), in Fettschrift.'],
        ['Normale Zeile', 'Ausgabe des Interpreters.'],
        ['<font color="%s"><b>Dunkelgelb</b></font>' % SW_FARBE,
         'Ausgabe des Rechners über das Schreibwerk (Kanal K2), ebenfalls fett. Im Schwarz-Weiß-Druck erkennen Sie sie an der '
         'Zeile selbst (z. B. „Jahr 1972“) und am Hinweis im Text.'],
        ['<font color="#%s">Rot</font>' % RED.hexval()[2:],
         'Fehlermeldung zu einem Gerät. Jede solche Meldung beginnt mit „FEHLER:“, damit sie auch ohne Farbe auffällt. Meldungen '
         'der Vorab-Prüfungen (Aufruf, Testdatei, Trommeldatei) erscheinen ohne Farbe, z. B. als „FORMALE PRUEFUNG NEGATIV“ '
         'oder „FEHLER: Testdatei nicht gefunden“.'],
        ['Hinweis / Achtung', 'Blauer Balken: nützliche Ergänzung. Orangefarbener Balken: Stelle, an der Tests häufig scheitern '
                              'oder an der Hardware und Interpreter abweichen.'],
    ], [0.22, 0.78])
    s.append(P('Schreibweisen', 'h2'))
    s += bullets([
        'Dateinamen, Schalter und Eingaben stehen in `Festbreitenschrift`.',
        'Zahlen in Testdateien und Registerwerten sind **oktal** (Ziffern 0–7). Wo Ziffern dezimal gemeint sind, steht es dabei.',
        'Kanäle heißen immer K0 bis K3. Geräte heißen Lochstreifenleser (Kürzel Leser), Lochstreifenstanzer (Stanzer) und '
        'Schreibwerk (SW).',
        '**Testdatei** ist die Datei, die Sie dem Interpreter geben. **Trommelabschnitt** ist ihr erster Teil '
        '(`Trommeldatei:`: die Zellen, die der Test vor dem Start auf die Trommel schreibt), **Tastenfolge** ihr zweiter Teil '
        '(die Bedienhandlungen). **Trommeldatei** ohne Zusatz ist die persistente Datei `trommel.txt`, der Speicher des '
        'Interpreters.',
        'Die Zahl hinter „Knoten:“ in der Endzeile ist fassungsabhängig und kein Sollwert. Ordnernamen und Pfade der '
        'Beispiele sind frei gewählt.'])
    s.append(P('**Verwandte PDFs:** Rechnerbeschreibung · Bedienpult und Peripherie · Testhandbuch · Durchführung eines Tests · '
               'Einzelbefehlsliste · Kodetabellen · Knotengraph · Lochstreifen-Hilfsprogramme · Einstieg für Neueinsteiger · '
               'Projektüberblick (Verweise: Anhang C).'))
    s.append(PageBreak())
    s.append(Paragraph('Inhaltsverzeichnis', ST['h1']))
    s.append(make_toc())
    s.append(PageBreak())
    return s


# ------------------------------------------------------------------ Kapitel 1
def kap1():
    s = h1('1 Zu dieser Anleitung')
    s += h2('1.1 Was der Interpreter tut')
    s.append(P('Der Interpreter führt Programme des Rechners C 8205 interpretativ aus. Er läuft den Knotengraphen des '
               'Befehlsablaufs (Phasen I bis IV) ab und bildet Register, Flags, Trommelspeicher und Peripherie nach. Alle Zeiten '
               '(Wortzeit, Wartezeit auf die Trommel) sind 0; die Trommeldrehung wird nicht nachgebildet. Die Trommel selbst ist '
               'eine persistente Textdatei (`virtuelle_Geraete/Trommel/trommel.txt`): Ihr Inhalt bleibt über Tests und Aufrufe '
               'hinweg erhalten (Abschnitt 3.7).'))
    s.append(P('Sie benutzen den Interpreter, um'))
    s += bullets(['Testprogramme des C 8205 nachvollziehbar durchzurechnen (auf Wunsch Knoten für Knoten protokolliert),',
                  'das Verhalten des Regelwerks zu prüfen,',
                  'Ein- und Ausgabe (Schreibwerk, Lochstreifenleser, Stanzer, Pult-Tastatur) am Terminal zu erproben.'])
    s += note('hinweis', '**Grundsatz „laut scheitern“.** Der Interpreter läuft den Graphen wortlautgetreu ab. Ist etwas unklar '
                         'oder fehlt eine Festlegung, meldet er das und hält an; er rät nie und „repariert“ nichts stillschweigend. '
                         'Ein Test, der nicht startet, ist daher kein Defekt, sondern eine Meldung, die Sie lesen sollten.')
    s += h2('1.2 Wie die Anleitung aufgebaut ist')
    s += tbl([['Kapitel', 'Inhalt', 'Wann lesen?'],
              ['2 Erste Schritte', 'Voraussetzungen, Ordner, Trommeldatei erzeugen, erster Lauf', 'beim ersten Mal'],
              ['3 Tests schreiben', 'Trommelabschnitt, Marken, Tastenfolge, Prüfungen, Geräte-Zeilen, Trommel zwischen den Tests',
               'beim Anlegen eines Tests'],
              ['4 Interpreter starten', 'Aufruf, Schalter, Wrapper, Rückkehrcodes', 'bei jedem Lauf'],
              ['5 Ein- und Ausgabe', 'Kanäle, Schreibwerk und Ausgabefenster, Leser, Stanzer, Tastatur', 'bei Zeichen-Ein-/Ausgabe'],
              ['6 Ergebnisse lesen', 'Endzeile, Diagnose, Protokoll, Ergebnisprüfung', 'nach jedem Lauf'],
              ['7 Wenn etwas schiefgeht', 'Fehlerverzeichnis mit Ursache, Abhilfe und Rückkehrcode, Beispiele', 'bei Meldungen'],
              ['8 Beispiele', 'Beispiele Schritt für Schritt zum Nachmachen', 'zum Ausprobieren'],
              ['9 Kurzreferenz', 'eine Seite zum Ausdrucken', 'zum Nachschlagen'],
              ['Anhang A bis C', 'Glossar, Grenzen des Interpreters, Verweise auf das Regelwerk', 'bei Bedarf']],
             [0.25, 0.5, 0.25], first_bold=True)
    s += h2('1.3 Stand und Neuerungen')
    s.append(P('Die Anleitung gilt für die Interpreter-Version auf Seite 2. Gegenüber der Anleitung vom 08.10.2026 (damals noch '
               'ohne Versionsnummer) sind neu:'))
    s += bullets([
        'Die **Versionsnummer** des Interpreters (Form `y.xx-zzz`) und der Schalter `--version` (Kapitel 4).',
        'Das **Ausgabefenster** „SW Ausgabe“ mit den Schaltern `--SW-TERMINAL` und `--zwischenablage`; es zeigt auch das Echo '
        'der K0-Eingabe (Kapitel 4 und 5).',
        'Die Testmarken `#STARTE n` (Makro für den Ansprung eines Speicherplatzes) und `#INTERRUPT H …` '
        '(Unterbrechung des Programmlaufs mit weiteren Tasten) (Abschnitt 3.2).',
        'Die Beispiele laufen bei jeder Erzeugung des PDFs neu; ihre Ausgaben sind immer die der genannten Version.'])
    return s


# ------------------------------------------------------------------ Kapitel 2
def kap2(lab):
    s = h1('2 Erste Schritte')
    s += h2('2.1 Voraussetzungen')
    s += bullets([
        '**Python 3.** Es wird nur die Standardbibliothek benutzt; es ist nichts zu installieren.',
        'Verzeichnis `markdown-dateien/` neben `c8205_interp.py` (Vorgabe für `--mdverz`) mit '
        '`C8205-Interpreter-Eingänge_der_Knoten.md` (Knotengraph) und `C8205-Interpreter-Beschreibung_der_Knoten.md` '
        '(Variablentabelle T2). Der Interpreter liest beide bei jedem Start; fehlt eine, endet der Aufruf mit Rückkehrcode 2.',
        'Die Trommeldatei `virtuelle_Geraete/Trommel/trommel.txt` neben `c8205_interp.py` (Vorgabe für `--trommel`): genau '
        '4096 Zeilen, les- und beschreibbar. Der Interpreter legt sie nie selbst an; Abschnitt 2.3 zeigt, wie Sie sie erzeugen.',
        'Optional der Wrapper `c8205_interpreter.sh` (Linux/macOS) bzw. `c8205_interpreter.bat` (Windows), ebenfalls im Ordner '
        'des Skripts.',
        'Ein Terminal mit ANSI-Farben (für Dunkelgelb und Rot). Ohne Terminal oder mit gesetztem `NO_COLOR` erscheint reiner Text.',
        '**Nur für das Ausgabefenster:** `tkinter` (Linux: `sudo apt install python3-tk`; unter Windows und macOS im '
        'Python-Installer von python.org enthalten) und eine grafische Oberfläche. Zum Kopieren aus dem Fenster unter Linux '
        'optional `xsel` oder `xclip` (X11) bzw. `wl-clipboard` (Wayland); unter Windows ist nichts nachzuinstallieren.'])
    s += note('hinweis', 'Der Dateiname der Knotengraph-Datei enthält ein „ä“. Findet der Interpreter sie nicht (z. B. wegen der '
                         'Zeichenkodierung eines Archivs), geben Sie das Verzeichnis mit `--mdverz` an.')
    s += h2('2.2 Ordner')
    s += L.code("""Projektordner/
  c8205_interp.py
  c8205_interpreter.sh     c8205_interpreter.bat
  erzeuge_leere_trommel.py erzeugt bzw. leert die Trommeldatei
  markdown-dateien/        Regelwerk (u. a. Eingänge_der_Knoten.md, Beschreibung_der_Knoten.md)
  Tests/                   Testdateien (.txt)
  Test-Protokolle/         Protokolle (.log), vom Wrapper angelegt
  virtuelle_Geraete/
    Trommel/trommel.txt    die Trommel: immer benutzt (4096 Zeilen)
    Leser1/ Leser2/ Stanzer1/ SW-Ausgabe/ T-SW-Eingabe/
                           Ablage für virtuelle Geräte (NICHT automatisch benutzt)""")
    s += note('hinweis', 'Die Ordner `Leser1/`, `Leser2/`, `Stanzer1/`, `SW-Ausgabe/` und `T-SW-Eingabe/` unter '
                         '`virtuelle_Geraete/` werden nicht automatisch benutzt. Sie wirken nur, wenn Sie den Schalter beim Aufruf '
                         'angeben (auch beim Wrapper: `./c8205_interpreter.sh Tests/x.txt --leser1 virtuelle_Geraete/Leser1`, '
                         'Abschnitt 4.3) oder wenn die Testdatei den Pfad als Geräte-Zeile selbst mitbringt (Abschnitt 3.6). Die '
                         'einzige Datei unter `virtuelle_Geraete/`, die der Interpreter immer benutzt, ist `Trommel/trommel.txt`.')
    s += h2('2.3 Die Trommeldatei erzeugen')
    s.append(P('Der Interpreter braucht bei jedem Aufruf die Trommeldatei, seinen Speicher. Er legt sie nie selbst an und setzt '
               'sie nie zurück. Erzeugen Sie sie einmal und immer dann neu, wenn Sie eine leere Trommel brauchen '
               '(Abschnitt 3.7):'))
    lab.neu()
    s.append(Spacer(1, 1))
    s += lab.sitzung(['python3 erzeuge_leere_trommel.py',
                      'wc -l virtuelle_Geraete/Trommel/trommel.txt',
                      'head -n 3 virtuelle_Geraete/Trommel/trommel.txt',
                      'python3 erzeuge_leere_trommel.py --aus trommeln/leer.txt',
                      'cmp virtuelle_Geraete/Trommel/trommel.txt trommeln/leer.txt && echo gleich'])
    s.append(P('Das Skript schreibt 4096 Zeilen `aaaa: ttttttttttt` mit dem Wert `00000000000` (Adressen 0000 bis 7777, oktal, '
               'Zeilenende LF) und überschreibt eine vorhandene Datei ohne Rückfrage. Mit `--aus PFAD` entsteht die Datei an '
               'anderer Stelle; fehlende Ordner werden angelegt. Das Skript gibt nichts aus; im Beispiel prüfen `wc` und `head` '
               'das Ergebnis.'))
    s += note('achtung', 'Alle Beispiele dieser Anleitung laufen auf einer leeren Trommel. Wer sie nachmacht, erzeugt vor jedem '
                         'Beispiel eine leere Trommel; sonst hängt das Ergebnis vom Inhalt ab, den frühere Läufe hinterlassen '
                         'haben (Abschnitt 3.7).')
    s += h2('2.4 Der erste Lauf')
    s.append(P('Legen Sie die Datei `Tests/0015-030.txt` mit folgendem Inhalt an. Das Programm wählt K2 an und gibt auf dem '
               'Schreibwerk einen Text aus.'))
    s += lab.dateien([('Tests/0015-030.txt', T_0015)])
    s.append(P('Starten Sie den Test mit dem Wrapper:'))
    s += lab.sitzung(['./c8205_interpreter.sh Tests/0015-030.txt',
                      'grep -E "^(0001|7240|7256):" virtuelle_Geraete/Trommel/trommel.txt'], erwarte=[4, None])
    s.append(P('Das Programm hat den Text „Jahr 1972“ ausgegeben (dunkelgelb; die Leerzeile davor ist ein Zeilenumbruch des '
               'Programms) und mit einem unbedingten Stopp gehalten. Die Zeile „Ende: …“ fasst den Endzustand zusammen '
               '(Kapitel 6). Das ausführliche Protokoll liegt in `Test-Protokolle/0015-030.log`. Die Zellen des Trommelabschnitts '
               'stehen jetzt auch in der Trommeldatei, wie die `grep`-Ausgabe zeigt.'))
    s += note('achtung', 'Die Schreibweise der Buchstaben („Jahr“, „JAHR“ oder „jahr“) hängt von der Zeichenlage KB/GB des '
                         'Schreibwerks ab, die beim Start zufällig gesetzt wird. Dieses Programm gibt selbst Umschaltzeichen aus; ohne '
                         'solche Zeichen wäre die Groß-/Kleinschreibung zufällig. Auch die „Knoten“-Zahl der Endzeile ist '
                         'fassungsabhängig und kein fester Sollwert.')
    return s


# ------------------------------------------------------------------ Kapitel 3
def kap3(lab):
    s = h1('3 Tests schreiben')
    s.append(P('Eine Testdatei besteht aus zwei Teilen, optional drei: Der Teil `Trommeldatei:` (der Trommelabschnitt) nennt die '
               'Zellen, die vor dem Test auf die Trommel geschrieben werden, der Teil `Tastenfolge:` die Bedienhandlungen am '
               'Pult vor dem Start, der Teil `Prüfungen:` (optional) die erwarteten Ergebnisse.'))

    # ---- 3.1
    s += h2('3.1 Trommelabschnitt')
    s.append(P('Jede Zeile hat die Form `Adresse: Wert [# Bemerkung]`. Die Adresse hat vier Oktalstellen, der Wert elf. Der Wert '
               'besteht aus vier Stellen „beliebig“ und sieben Stellen Befehl (vier Adresse + drei Operation): `00004500030` ist '
               'also Adresse `4500`, Operation `030`. Leerzeilen und Zeilen, die mit `#` beginnen, werden übergangen; ein '
               'Kommentar darf hinter einer `Adresse: Wert`-Zeile stehen, wenn mindestens ein Leerzeichen davorsteht. Nicht '
               'genannte Zellen behalten ihren bisherigen Inhalt; auf einer leeren Trommel sind das 0 (Abschnitt 3.7).'))
    s += L.code("""# Beginn Programmbefehle
0000: 00003000211
0001: 00003001210
0002: 00000000020
# Beginn Datenbereich
3000: 00000000100 # Startwert
3001: 00000000045""")
    s += note('achtung', 'Eine Zelle, die weder der Test noch ein früherer Lauf belegt hat, ist 0, und der Wert 0 ist als Befehl der '
                         'unbedingte Sprung nach Adresse 0000. Läuft Ihr Programm über sein Ende hinaus, springt es zurück an den '
                         'Anfang. Schließen Sie jedes Programm mit einem Stopp-Befehl `00000000020` ab. Weil die Trommel zwischen '
                         'den Tests erhalten bleibt, kann eine „leere“ Zelle auch Reste eines früheren Tests enthalten '
                         '(Abschnitt 3.7).')
    s += note('hinweis', 'Wenn Sie in Assemblersprache programmieren, erzeugt der Assembler `c82ass` diese Zeilen für Sie (Datei '
                         '`<n>.test`); Sie ergänzen nur Testmarken und Tastenfolge. Siehe PDF „Testhandbuch“.')

    # ---- 3.2
    s += h2('3.2 Testmarken')
    s.append(P('Testmarken sehen aus wie Kommentare (`#`), haben aber eine Wirkung. Sie gehören nur zum Test; es gibt sie in der '
               'Hardware nicht.'))
    s += tbl([['Marke', 'Wirkung'],
              ['`#DOK-xxxx Text`', 'Kommentar zum Test (`xxxx` oktal). Beim Befehl 164 („Leerbefehl“) mit der Adresse `xxxx` wird '
                                   'der Text als Diagnose ausgegeben, unabhängig von der Protokollstufe. Mehrfach zulässig.'],
              ['`#SPEI-xxxx ssss-eeee`', 'Speicherbereich `ssss` bis `eeee` (oktal, `ssss ≤ eeee`), der beim Befehl 164 mit der '
                                         'Adresse `xxxx` ausgegeben wird. Unabhängig von `#DOK`: auch einzeln und mehrfach zulässig.'],
              ['`#SPUR-xxxx aaaa`', 'Ganze Spur (Bahn), in der `aaaa` liegt: alle 32 Zellen in physischer Zugriffsreihenfolge der '
                                    'Trommel, ausgegeben beim Befehl 164 mit der Adresse `xxxx`. Unabhängig von `#DOK`.'],
              ['`#PROT STUFE=n`', 'Protokollstufe des Tests (höchstens einmal): 0 = kein Knotenprotokoll, 1 = Knotenzeilen auf dem '
                                  'Bildschirm, 2 = Knotenzeilen nur in der Protokolldatei. Fehlt die Marke, gilt 1.'],
              ['`#AC=ooooooooooo`', 'Anfangswert des Akkumulators, 11 Oktalziffern (höchstens einmal). Fehlt die Marke, startet der '
                                    'AC mit 0.'],
              ['`#BZ=oooo`', 'Anfangswert des Befehlszählers, 4 Oktalziffern (höchstens einmal). Fehlt die Marke, startet der BZ '
                             'mit 0.'],
              ['`#STARTE n`', 'Makro für die Tastenfolge `H G M+ E … E M- R` (`n` Anschläge `E`): Ansprung des Speicherplatzes `n`. '
                              '`n` hat 1 bis 4 Oktalziffern; höchstens einmal; ersetzt die Tastenfolge.'],
              ['`#INTERRUPT H <Tasten>`', 'Unterbricht den Programmlauf nach dem Befehl der davorstehenden Zeile und bedient die '
                                          'angegebenen Tasten. Nur zwischen zwei Befehlszeilen; höchstens einmal je Befehlszeile.']],
             [0.27, 0.73])
    s += note('achtung', 'Die Diagnose erscheint nur, wenn der Test den Befehl 164 mit passender Adresse ausführt. Schreiben Sie ihn '
                         'an die Stelle, an der Sie auswerten wollen: `00000020164` an Adresse 0002 löst die Marken mit '
                         '`xxxx = 0020` aus. Der Leerbefehl wird zuerst ausgeführt, die Diagnose erscheint danach. Eine '
                         'automatische Zustandszeile gibt es nicht.')

    s.append(kopf3('Anfangswerte `#AC=` und `#BZ=`'))
    s.append(P('Beide Marken stehen im Trommelabschnitt, sind voneinander unabhängig und einzeln oder zusammen zulässig. Sie '
               'setzen Akkumulator und Befehlszähler als Anfangszustand vor der ersten Taste. Die Taste `G` wirkt danach '
               'unverändert: Sie lässt AC und BZ unberührt, stellt aber das Befehlsregister auf einen Sprung nach 0000. `#BZ=` '
               'wirkt daher nur, solange keine Taste `G` davor kommt, z. B. bei der Tastenfolge '
               '`H M-drücken E M-loslassen R`. Das erste Beispiel startet mit AC = 100 und addiert die Zelle 3000 (45):'))
    s += lab.dateien([('Tests/ac-start.txt', T_AC)])
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/ac-start.txt')], erwarte=[4])
    s.append(P('Das zweite Beispiel hat keine Taste `G`: `#BZ=0010` setzt den Befehlszähler, das `E` unter gehaltenem `M` zählt '
               'auf 0011 und der Ablauf beginnt dort:'))
    s += lab.dateien([('Tests/bz-start.txt', T_BZ)], neu=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/bz-start.txt')], erwarte=[4])
    s.append(P('Ein ungültiger Wert (falsche Stellenzahl, Ziffer 8 oder 9, leerer Wert) oder eine doppelte Marke ist ein Fehler '
               'der formalen Prüfung (Abschnitt 3.5). Beispiel: In `Tests/ac-doppelt.txt` steht `#AC=` zweimal.'))
    s += lab.dateien([('Tests/ac-doppelt.txt', T_AC2)], neu=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/ac-doppelt.txt')], erwarte=[16])

    s.append(kopf3('Das Makro `#STARTE n`'))
    s.append(P('`#STARTE n` ersetzt die Tastenfolge zum Ansprung des Speicherplatzes `n` (Muster aus Abschnitt 3.3). `n` ist eine '
               'Oktalzahl mit 1 bis 4 Ziffern und zugleich die Zahl der Anschläge `E`: `#STARTE 12` löst 10 (dezimal) Anschläge '
               'aus und spricht den Speicherplatz `0012` an. Die Marke steht an beliebiger Stelle außer im Teil `Prüfungen:`, '
               'üblicherweise bei den Testmarken; der Teil `Tastenfolge:` darf dann fehlen. Enthält er Tasten, ist das ein '
               'Formfehler, ebenso ein fehlender oder ungültiger Wert und eine doppelte Marke. `#AC=`, `#BZ=` und `#INTERRUPT` '
               'sind mit dem Makro verträglich. Im Protokoll erscheinen lange `E`-Folgen unter gehaltenem `M` gekürzt; die '
               'Rechnung ist davon nicht berührt.'))
    s += lab.dateien([('Tests/start-4.txt', T_STARTE)], neu=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/start-4.txt')], erwarte=[0])
    s += note('achtung', '`#STARTE 0` ergibt die Folge `H G M+ M- R`, also ein Antippen von `M` ohne `E`. Das ist kein schlichter '
                         'Start bei 0000, sondern ein aufgestellter Sprung mit Rückkehrabsicht nach 0000. Für einen Start bei '
                         '0000 dient `H G R`.')

    s.append(kopf3('Die Marke `#INTERRUPT`'))
    s.append(P('`#INTERRUPT` bildet einen Eingriff des Bedieners mitten im Programm nach. Die Zeile steht im Trommelabschnitt '
               '**zwischen zwei Befehlszeilen** und gehört zu der Zeile davor (Adresse `p`). Nach dem Befehl auf `p` wird der '
               'Lauf unterbrochen, aber nur, wenn er sequentiell weiterläuft (BZ = `p+1`); springt der Befehl woandershin, bleibt '
               'die Zeile ohne Wirkung. Die erste Taste muss `H` sein; danach folgen beliebige zulässige Tasten, eine gehaltene '
               'Taste wird mit `+`, ihr Loslassen mit `-` geschrieben. Endet die Folge mit `R` oder `ST`, läuft das Programm '
               'weiter; jede andere letzte Taste beendet den Test an dieser Stelle im Halt, und `Prüfungen:` gilt für diesen '
               'Zustand. Die Zeile ist keine Speicherzelle und kein Sprungziel. Im ersten Beispiel läuft das Programm nach der '
               'Unterbrechung weiter:'))
    s += lab.dateien([('Tests/int-weiter.txt', T_INT1)], neu=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/int-weiter.txt')], erwarte=[0])
    s.append(P('Im zweiten Beispiel transportiert die Unterbrechung den AC nach Zelle 7777 (`H G Ü E`); die letzte Taste ist `E`, '
               'der Test endet daher im Halt, und die Prüfung gilt für den Zustand danach:'))
    s += lab.dateien([('Tests/int-transport.txt', T_INT2)], neu=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/int-transport.txt')], erwarte=[0])
    s += note('achtung', 'Ohne vorheriges `G` ist das OR der Operationsteil des letzten Befehls: `H Ü E` ergibt nach einem '
                         'Ladebefehl 211 die Operation 251, nicht 240. Für den reinen Transport nach 7777 ist `H G Ü E` nötig. '
                         'Formfehler (Beispiel in Kapitel 7): `#INTERRUPT` vor der ersten oder hinter der letzten Befehlszeile, '
                         'ohne Tasten, mit erster Taste außer `H`, mit unzulässiger M-Folge, zweimal hinter derselben Befehlszeile.')

    # ---- 3.3
    s += h2('3.3 Tastenfolge')
    s.append(P('Die Tastenfolge (hinter `Tastenfolge:`) legt den Ausgangszustand fest. Die Token stehen durch Leerzeichen getrennt '
               'in einer oder mehreren Zeilen; Groß-/Kleinschreibung ist gleichgültig. Sie endet mit `R` (dann ist `H` am Ende '
               'gelöst) oder im Halt (`H` bleibt gesetzt, z. B. `H G Ü E`). Beides ist gültig. Endet sie weder mit `R` noch im '
               'Halt, startet der Test nicht.'))
    s += tbl([['Token', 'Wirkung'],
              ['`H`', 'Schalter H-R auf „H“: Flag H := 1'],
              ['`G`', 'Generallöschen: alle Flags außer H, T, BS, SP := 0, danach US := 1; AR := 0000, OR := 000 '
                      '(Befehlsregister 0000 000: unbedingter Sprung nach 0000); Kanal K0 angewählt (T := 1, bei gedrücktem SW: '
                      'SW := 1). **AC und BZ bleiben unverändert**; BZ := 0 entsteht erst, wenn `R` oder `E` (ohne `M`) den '
                      'Sprung ausführt.'],
              ['`M+`, `M-drücken`, `M-gedrückt-halten`', 'M gedrückt halten: OR := OR ODER 025'],
              ['`M-`, `M-loslassen`', 'M loslassen: der Beitrag 025 im OR entfällt'],
              ['`M`', 'Antippen = `M+` und sofort `M-`: OR := OR ODER 025, BR bleibt aufgestellt. `R` startet bei Knoten 54, wenn '
                      'BR ein Sprung mit Rückkehrabsicht ist (025, 027, 125, 127), sonst bei Knoten 19.'],
              ['`E` (mit gehaltenem M)', 'BZ := BZ + 1, AR := BZ, AC := BZ+1 im Adressfeld; Befehlsentnahme gesperrt'],
              ['`E` (ohne M)', 'nur bei H: Einzelschritt über den Knotengraphen ab Knoten 19 (nach `M` mit Sprung mit '
                               'Rückkehrabsicht ab Knoten 54), Halt vor erneutem Eintritt in Knoten 19']],
             [0.27, 0.73])
    s += tbl([['Token', 'Wirkung'],
              ['`BS=1`, `SP=1` (auch `BS+`, `SP+`)', 'Schalter gedrückt und eingerastet: Flag BS bzw. SP := 1'],
              ['`BS=0`, `SP=0` (auch `BS-`, `SP-`)', 'Schalter gelöst: Flag := 0. `G` löst die Schalter nicht.'],
              ['`ST`', 'nicht an H gebunden, nur bei US oder BS wirksam (sonst keine Wirkung): OR := OR ODER 240, AR bleibt, '
                       'US := 0; BR aufgestellt. Nach einem Stopp-Befehl ist das die Operation 26Z, nach `G` die Operation 240.'],
              ['`Ü` (auch `UE`)', 'nur bei H: AR := 7777, OR := OR ODER 240; BR aufgestellt'],
              ['`SW=1`, `SW+`, `SW-drücken`', 'Schalter SW gedrückt: Flag SW := 1, T := 0'],
              ['`SW=0`, `SW-`, `SW-loslassen`', 'Schalter SW gelöst: Flag SW := 0, T := 1'],
              ['`K0`, `K1`, `K2`, `K3`', 'Kanaltaste (rastend): Flag des gewählten Kanals := 1, die der anderen := 0; bei `K0` '
                                         'zusätzlich T oder SW je nach Schalter SW. Ein im Programm ausgeführter Anwahlbefehl '
                                         'übersteuert die Einstellung.'],
              ['`R`', 'Schalter H-R auf „R“: H := 0, US := 0; Ablauf beginnt bei Konnektor B (bei aufgestelltem BR bei '
                      'Knoten 19, nach `M` mit Sprung mit Rückkehrabsicht bei Knoten 54)']],
             [0.27, 0.73])
    s += note('achtung', '`SW=1` muss vor `G` stehen, weil `G` daraus für K0 T oder SW ableitet. Die Kanaltasten `K0` … `K3` stehen '
                         'nach `G`, weil `G` den Kanal K0 wieder anwählt. Nach `Ü`, `ST` oder `E` (ohne M) ist BR aufgestellt: folgt '
                         '`R`, beginnt der Ablauf bei Knoten 19 statt bei Konnektor B.')
    s.append(P('Ungültig (der Test startet nicht): `M-` ohne `M+`, `M+` bei gedrücktem M, `R` oder Ende bei gedrücktem M, '
               'unbekannte Token. Die Eingabetasten (0…9, `+` usw.) gehören nicht in die Tastenfolge; Eingaben an K0 stehen in '
               'Abschnitt 5.4.'))
    s.append(P('Muster: Sprung nach Speicherplatz n. Mit `H G M+ E … E M- R` (n-mal `E`) beginnt der Ablauf bei Adresse n; kürzer '
               'schreibt man `#STARTE n` (Abschnitt 3.2). Beispiel n = 4, das Programm steht ab Adresse 0004:'))
    s += lab.dateien([('Tests/sprung-n.txt', T_SPRUNG)], neu=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/sprung-n.txt')], erwarte=[4])
    s.append(P('Der Ablauf hat bei Adresse 0004 begonnen und dort gehalten (BZ=0005). Der AC enthält – wie bei der Taste `M` '
               'üblich – im Adressfeld die um 1 erhöhte Adresse (`…05000`). Rückkehrcode 4: Der Test enthält keine Prüfung '
               '(Abschnitt 4.4).'))
    s.append(P('Tastenfolge im Halt. Endet die Tastenfolge ohne `R`, startet der Rechner nicht; der Lauf endet sofort mit dem Grund '
               '„Halt (Schalter H)“ und dem Rückkehrcode 4. Beispiel: Tastenfolge `H G`.'))
    s += lab.dateien([('Tests/halt-ende.txt', T_HALT)], neu=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/halt-ende.txt')], erwarte=[4])
    s.append(P('Auch `H G Ü E` endet im Halt: `Ü` stellt den Transport-Befehl auf, `E` (ohne `M`) führt genau einen Schritt aus '
               '(Einzelschritt) und hält wieder.'))
    s += lab.dateien([('Tests/ue-e.txt', T_UEE)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/ue-e.txt')], erwarte=[4])

    # ---- 3.4
    s += h2('3.4 Prüfungen (optional)')
    s.append(P('Hinter der Tastenfolge kann ein Teil `Prüfungen:` stehen. Er enthält höchstens eine Zeile mit Zuweisungen '
               '`SCHLÜSSEL=WERT` für Register und Flags (`BZ`, `AC`, `AR`, `FE`, `FUE`, `BS`, `US`, `E`, `A`, `V1`, `V2`; `BZ` und '
               '`AR` vierstellig, `AC` elfstellig, Flags 0 oder 1, jeder Schlüssel höchstens einmal), beliebig viele '
               'Speicherzeilen `Adresse: Wert` und bis zu zwei Dateiprüfungen. Nicht genannte Schlüssel werden nicht geprüft.'))
    s += L.code("""Prüfungen:
BZ=0004 AC=00000000145 US=1
3000: 00000000100
--pruefe-stanzer1 soll.txt""")
    s.append(P('Der Interpreter vergleicht nach dem Lauf jeden Wert einzeln und meldet `Test wahr` oder `Test falsch` (Beispiele in '
               'Abschnitt 6.5). `--pruefe-stanzer1 DATEI` und `--pruefe-sw-ausgabe DATEI` vergleichen die vom Lauf erzeugte '
               'Stanzer- bzw. Schreibwerk-Datei mit der Soll-Datei `DATEI`; ein Name ohne Ordner liegt neben der Testdatei. '
               'Jede Zeile steht höchstens einmal; der Schalter gleichen Namens auf der Kommandozeile hat Vorrang. Die '
               'Dateiprüfung setzt das zugehörige Gerät voraus (`--stanzer1` bzw. `--sw-ausgabe`, auch als Geräte-Zeile). '
               'Die Speicherzeilen lesen den aktuellen Trommelstand, auch mit Resten früherer Tests: Prüfen Sie nur Zellen, die '
               'der Test selbst nennt, oder starten Sie auf leerer Trommel (Abschnitt 3.7). Dateiprüfung ohne Gerät ist ein '
               'formaler Fehler:'))
    s += lab.dateien([('Tests/pruefe-ohne.txt', T_PRUEFE_OHNE)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/pruefe-ohne.txt')], erwarte=[16])
    s += note('hinweis', 'Bricht der Lauf vorher ab (Stub, Gerätefehler), wird nicht geprüft; die Ausgabe lautet dann '
                         '„Ergebnisprüfung: nicht durchgeführt“, und der Test gilt nicht automatisch als „falsch“. Ein leerer '
                         'Abschnitt `Prüfungen:` gilt als fehlender.')
    # Prüfungen: False -- in der Quelle „Durchführung eines Tests“ (3a.5) beschrieben; hier wird geprüft, ob der Interpreter es kennt
    lab.dateien([('Tests/pruef-false.txt', T_FALSE)], neu=True, zeigen=False)
    probe, _ = lab.ausgabe(cmd('python3 c8205_interp.py --MODUS=TEST Tests/pruef-false.txt'))
    if "ungueltiges Element 'False'" not in probe:
        sys.exit('FEHLER: Der Interpreter kennt „Prüfungen: False“ jetzt. Abschnitt 3.4 der Anleitung (Achtung-Kasten) und '
                 'Anhang B anpassen, dann Skript ändern.\n' + probe)
    s += note('achtung', 'Die Quelle „Durchführung eines Tests“ beschreibt die Kopfzeile `Prüfungen: False` (Negativtests, die '
                         '`Test falsch` ergeben sollen). Diese Fassung des Interpreters kennt sie noch nicht: Der Test startet '
                         'nicht, sondern endet mit Rückkehrcode 16. Schreiben Sie bis dahin `Prüfungen:` ohne Zusatz und rechnen '
                         'Sie mit `Test falsch` (Rückkehrcode 6).')
    s += lab.dateien([('Tests/pruef-false.txt', T_FALSE)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/pruef-false.txt')], erwarte=[16])

    # ---- 3.5
    s += h2('3.5 Formale Prüfung vor dem Start')
    s.append(P('Vor dem Start prüft der Interpreter: Zeilenformat, keine Adresse mit widersprüchlichem Wert, gültige `#SPEI`-Spanne, '
               'gültige `#PROT`-Stufe, gültige Marken `#AC=` und `#BZ=` (je höchstens einmal), gültige `#INTERRUPT`-Zeilen, '
               'gültiges `#STARTE`, vorhandene und gültige Tastenfolge (bei `#STARTE` entfällt sie), gültiger `Prüfungen:`-Teil '
               'sowie die angegebenen Geräte-Pfade (`--leser1`, `--leser2`, `--k0 datei=`, auch als Zeile der Testdatei). Bei '
               'einer Unstimmigkeit startet der Test nicht (Rückkehrcode 16) und wird nicht eigenmächtig korrigiert. Die '
               'Trommeldatei wird nicht je Test, sondern einmal vor dem ersten Test des Aufrufs geprüft (Abschnitt 3.7).'))
    s += lab.dateien([('Tests/formal.txt', T_FORMAL)], neu=True)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/formal.txt')], erwarte=[16])
    s.append(P('Zeile 3 hat nur neun statt elf Stellen im Wert; Adresse 0001 kommt zweimal mit verschiedenen Werten vor.'))

    # ---- 3.6
    s += h2('3.6 Geräte in der Testdatei')
    s.append(P('Der Test kann seine Geräte selbst festlegen. Dazu steht je eine Zeile in der Testdatei, an beliebiger Stelle, '
               'üblicherweise bei den Testmarken im Trommelabschnitt. Die Zeilen haben dieselbe Form wie die gleichnamigen '
               'Schalter:'))
    s += L.code("""--leser1 PFAD                 # Lochstreifen für Leser 1 (K1): Datei oder Ordner
--leser2 PFAD                 # Lochstreifen für Leser 2 (K2): Datei oder Ordner
--stanzer1 PFAD               # Ausgabedatei bzw. -ordner des Stanzers 1 (K1)
--sw-ausgabe PFAD             # Schreibwerk-Ausgabe (K2) nach PFAD/sw-ausgabe.txt
--k0 datei=PFAD               # K0-Eingabe (T und SW) aus Datei oder Ordner""")
    s += bullets([
        'Jede Zeile darf höchstens einmal vorkommen; ein Kommentar `# …` am Zeilenende ist zulässig.',
        'Die Kommandozeile hat Vorrang: Ist derselbe Schalter beim Aufruf angegeben, gilt dessen Wert; die Zeile der Testdatei wird '
        'übergangen.',
        'Ein relativer Pfad gilt vom aktuellen Ordner des Aufrufs aus (wie auf der Kommandozeile), nicht vom Ordner der Testdatei.',
        'Eine Zeile ohne Wert, eine doppelte Zeile, `--k0` ohne `datei=` und ein nicht vorhandener Leser- oder `--k0`-Pfad sind '
        'Formfehler: Der Test startet nicht (Rückkehrcode 16; Beispiel in Kapitel 7).',
        'Zeigt `--leser1` oder `--leser2` auf einen Ordner, erscheint ein Hinweis: Alle Dateien darin werden als Lochstreifen '
        'gelesen; für einen Test ist eine einzelne Datei sicherer.',
        '`--SW-TERMINAL` ist **keine** Geräte-Zeile: Der Schalter gilt nur auf der Kommandozeile; als Zeile der Testdatei ist er '
        'ein Formfehler (Rückkehrcode 16).',
        'Mit der Zeile `--sw-ausgabe SW-Ausgabe` braucht der Aufruf keinen Schalter; am Terminal erscheint nichts, die Zeichen '
        'stehen in `SW-Ausgabe/sw-ausgabe.txt`.'])
    s.append(P('Beispiel: Die Testdatei `sw-zeile.txt` wählt K2 an, stellt mit `Um. KB` (Ausgabe-Adresse `117x`) die '
               'Kleinbuchstabenlage ein, damit die Ausgabe nicht vom Zufall abhängt, und gibt die Zeichen 5 und Punkt aus; die '
               'Zeile `--sw-ausgabe SW-Ausgabe` steht bei den Testmarken. Das Terminal zeigt nur die Endzeile, die Zeichen '
               'stehen in der Datei:'))
    s += lab.dateien([('Tests/sw-zeile.txt', T_SWZEILE)], neu=True)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/sw-zeile.txt'), 'cat SW-Ausgabe/sw-ausgabe.txt'], erwarte=[4, None])

    # ---- 3.7
    s += h2('3.7 Die Trommel zwischen den Tests')
    s.append(P('Die Trommel ist keine Datei je Test, sondern eine dauerhafte Textdatei (Vorgabe '
               '`virtuelle_Geraete/Trommel/trommel.txt`, Schalter `--trommel`). Sie hält ihren Inhalt über Tests und Aufrufe '
               'hinweg. Der Trommelabschnitt einer Testdatei ist davon zu unterscheiden: Er nennt nur die Zellen, die der Test '
               'vor dem Start auf die Trommel schreibt.'))
    s += bullets([
        '**Format:** genau 4096 Zeilen `aaaa: ttttttttttt` (vier Oktalstellen Adresse, Doppelpunkt, Leerzeichen, elf '
        'Oktalstellen Wert, Zeilenende LF) in aufsteigender Adresse 0000 bis 7777, jede Adresse genau einmal; keine Kommentar- '
        'und keine Leerzeilen.',
        '**Prüfung:** Die Trommeldatei wird einmal je Aufruf vor dem ersten Test geprüft. Ist sie fehlerhaft oder nicht vorhanden, '
        'startet kein Test des Aufrufs (Rückkehrcode 16, Kapitel 7).',
        '**Beginn eines Tests:** Der Interpreter schreibt die Zeilen des Trommelabschnitts auf die Trommel; sie überlagern die '
        'vorhandenen Werte. Zellen, die der Test nicht nennt, behalten ihren bisherigen Inhalt. Register, Flags und Geräte '
        'beginnen dagegen bei jedem Test neu.',
        '**Während des Tests:** Jeder Schreibzugriff eines Befehls ändert die Zelle auch in der Datei. Nach dem Test bleibt der '
        'Endzustand stehen; er ist der Anfangszustand des nächsten Tests, auch wenn ein Aufruf mehrere Testdateien '
        'nacheinander abarbeitet.',
        '**Zurücksetzen:** Der Interpreter setzt die Trommel nie zurück und legt die Datei nie an. Eine leere Trommel erzeugt '
        '`python3 erzeuge_leere_trommel.py` (Abschnitt 2.3).'])
    s += note('achtung', 'Ein Test, der eine Zelle liest oder prüft, die er im Trommelabschnitt nicht selbst nennt, erbt deren Inhalt '
                         'von den vorigen Läufen. Das gilt auch für Prüfungen mit Sollwert 0 auf einer nicht belegten Zelle. '
                         'Empfehlung: Nennen Sie alle Zellen, auf die sich das Ergebnis stützt, auch mit Wert 0 '
                         '(`3000: 00000000000`), oder erzeugen Sie vor dem Lauf eine leere Trommel. Dann ist der Test von der '
                         'Vorgeschichte unabhängig.')
    s.append(P('Das vollständige Beispiel mit zwei Tests, die dieselbe Zelle 3000 benutzen, und mit dem Schalter `--trommel` steht '
               'in Abschnitt 8.5.'))
    s += note('hinweis', 'Die Reihenfolge der Tests bestimmt den Anfangszustand jedes Tests. Sammelläufe über viele Testdateien '
                         'liefern nur dann reproduzierbare Ergebnisse, wenn jeder Test seine Zellen selbst nennt oder die '
                         'Reihenfolge feststeht. Sollwerte aus Regressionsläufen gelten für einen Lauf auf leerer Trommel.')
    s += note('hinweis', 'Die Trommeldatei muss LF-Zeilenenden haben (jede Zeile 18 Byte). Eine Datei mit CRLF (z. B. unter '
                         'Windows im Textmodus erzeugt oder durch Git umgewandelt) erkennt der Interpreter beim Start und weist sie '
                         'ab (Rückkehrcode 16, Kapitel 7); `erzeuge_leere_trommel.py` schreibt immer LF.')
    return s


# ------------------------------------------------------------------ weitere Testdateien (Kapitel 4 bis 8)
T_UEBERLAUF = """Trommeldatei:
#PROT STUFE=0
0000: 00003000211 # AC := <3000>
0001: 00003001210 # AC := AC + <3001>
0002: 00003001210 # AC := AC + <3001>
0003: 00000000020
3000: 37777777777
3001: 00000000001
Tastenfolge:
H G R
"""
T_SPUR = """Trommeldatei:
#SPUR-0010 4000
#PROT STUFE=0
0000: 00000100164 # Leerbefehl, Diagnose #SPUR-0010
0001: 00000000020
4001: 00000000007
Tastenfolge:
H G R
"""
T_KURZ = """Trommeldatei:
#PROT STUFE=1
0000: 00003000211 # AC := <3000>
0001: 00000000020
3000: 00000000100
Tastenfolge:
H G R
"""
T_TFDEMO = """Trommeldatei:
#PROT STUFE=2
0000: 00000000020
Tastenfolge:
SW=1 SW=0 BS=1 SP=1 H G Ü ST BS=0 SP=0 R
"""
T_KANAL = """Trommeldatei:
#PROT STUFE=2
0000: 00000000020
Tastenfolge:
H G M K0 K1 K2 K3
"""
T_ACLOG = """Trommeldatei:
#PROT STUFE=2
#AC=00000000100
#BZ=0010
0011: 00000000020
Tastenfolge:
H M-drücken E M-loslassen R
"""
T_PFALSCH = """Trommeldatei:
#DOK-0001 Test Ladebefehl und Addition
#PROT STUFE=0
0000: 00003000211 # AC := <3000>
0001: 00003001210 # AC := AC + <3001>
0002: 00000001164 # Leerbefehl, Diagnose #DOK-0001
0003: 00000000020 # Stopp
3000: 00000000100
3001: 00000000045
Tastenfolge:
H G R
Prüfungen:
BZ=0003 AC=00000000145
"""
T_PWAHR = T_PFALSCH.replace('BZ=0003 AC=00000000145\n',
                            'BZ=0004 AC=00000000145 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0\n3000: 00000000100\n'
                            '3001: 00000000045\n')
T_STANZER = """Trommeldatei:
#PROT STUFE=0
0000: 00004600030 # K1 anwählen
0001: 00000250030 # Ausgabe der Ziffer 5 (025x)
0002: 00000730030 # Ausgabe des Punktes (073x)
0003: 00000000020
Tastenfolge:
H G R
"""
T_STANZER_PR = """Trommeldatei:
#PROT STUFE=0
--stanzer1 out/band.txt
0000: 00004600030
0001: 00000250030
0002: 00000730030
0003: 00000000020
Tastenfolge:
H G R
Prüfungen:
US=1
--pruefe-stanzer1 soll.txt
"""
SOLL = '00010101\n00111011\n'
SOLL_FALSCH = '00010101\n00111111\n'
T_LESER = """Trommeldatei:
#PROT STUFE=0
0000: 00004600030 # K1 anwählen
0001: 00000000011 # Eingabe-Halt mit Löschen
0002: 00000000020 # Stopp
0005: 00000000042 # Konstante: Inhalt der Zelle 0005
Tastenfolge:
H G R
"""
T_LESER2 = T_LESER.replace('00004600030 # K1', '00004500030 # K2')
T_K0 = """Trommeldatei:
#PROT STUFE=0
0000: 00004700030 # K0 anwählen
0001: 00000000011 # Eingabe-Halt mit Löschen
0002: 00000000020 # Stopp
0007: 00000000007 # Konstante: Inhalt der Zelle 0007
Tastenfolge:
H G R
"""
T_STUB = """Trommeldatei:
#PROT STUFE=0
0000: 00000250030 # Ausgabe der Ziffer 5 ohne Anwahl eines Kanals
0001: 00000000020
Tastenfolge:
H G R
"""
T_TFM = """Trommeldatei:
#PROT STUFE=0
0000: 00000000020
Tastenfolge:
H G M- R
"""
T_ENDLOS = """Trommeldatei:
#PROT STUFE=0
0000: 00003000211 # AC := <3000>
3000: 00000000100
Tastenfolge:
H G R
"""
T_GERAET_LEER = """Trommeldatei:
#PROT STUFE=0
--stanzer1
0000: 00000000020
Tastenfolge:
H G R
"""
T_S1R1 = """Trommeldatei:
#DOK-0020 s1-R1: GX-Transport mit Rechtsverschiebung
#SPEI-0020 4000-4037
#PROT STUFE=0
0000: 00003000211
0001: 00004001542
0003: 00000000020
0010: 00000020164
3000: 00000000006
Tastenfolge:
H G R
"""


# ------------------------------------------------------------------ Kapitel 4
def kap4(lab):
    s = h1('4 Interpreter starten')
    s += h2('4.1 Kommandozeile')
    s += L.code("""python3 c8205_interp.py --MODUS=TEST [--mdverz VERZ] [--trommel PFAD] [--out VERZ|DATEI.log]
        [--leser1 PFAD] [--leser2 PFAD] [--stanzer1 PFAD] [--sw-ausgabe PFAD]
        [--k0 datei=PFAD] [--knotentest] [--NO-TERMOUT] [--SW-TERMINAL]
        [--zwischenablage auto|tk|system]
        [--pruefe-stanzer1 DATEI] [--pruefe-sw-ausgabe DATEI] [--BASP abcdef]  TEST.txt [TEST2.txt ...]
python3 c8205_interp.py --version""")
    s += tbl([['Schalter', 'Wirkung', 'Vorgabe'],
              ['`TEST.txt`', 'Testdatei(en). Ist der Pfad nicht vorhanden, wird der Dateiname unterhalb des aktuellen Ordners und '
                             'des Skript-Ordners gesucht (Groß-/Kleinschreibung egal). Bei mehreren Treffern werden sie aufgelistet '
                             'und der Test startet nicht.', '–'],
              ['`--MODUS TEST|GRAFIK`', 'Betriebsart (auch `--modus`, `--MODUS=X`; Groß-/Kleinschreibung gleich; der letzte Wert gewinnt). '
                                        'Ohne Angabe startet GRAFIK (Pult- und SW-Fenster). Testläufe mit Testdatei brauchen `--MODUS=TEST`; '
                                        'eine Testdatei im Modus GRAFIK wird ignoriert und mit Hinweis auf stderr gemeldet. Unbekannter Wert: '
                                        'Rückkehrcode 2. Die Wrapper setzen `--MODUS=TEST`.', '`GRAFIK`'],
              ['`--mdverz VERZ`', 'Verzeichnis mit den beiden Regelwerk-Dateien `C8205-Interpreter-Eingänge_der_Knoten.md` '
                                  '(Knotengraph) und `C8205-Interpreter-Beschreibung_der_Knoten.md` (Variablentabelle T2); fehlt eine, '
                                  'bricht der Start ab (Rückkehrcode 2).', '`markdown-dateien/` neben dem Skript'],
              ['`--trommel PFAD`', 'Die Trommeldatei (4096 Zeilen `aaaa: ttttttttttt`, LF), der persistente Speicher. Sie wird '
                                   'einmal vor dem ersten Test geprüft; ist sie fehlerhaft oder fehlt sie, startet kein Test '
                                   '(Rückkehrcode 16). Nur auf der Kommandozeile, nicht als Zeile der Testdatei. Standardpfad: '
                                   '`virtuelle_Geraete/Trommel/trommel.txt` neben dem Skript.', 'Standard-Trommel'],
              ['`--out …`', 'Mit Dateiendung (z. B. `Test-Protokolle/t1.log`): Protokoll genau in diese Datei (Ordner werden '
                            'angelegt; nur mit einem Test). Ohne Endung: Ordner, Protokoll dann in `ORDNER/<Testname>/protokoll.txt`.',
               '`Test-Protokolle/`'],
              ['`--leser1 PFAD`, `--leser2 PFAD`', 'Lochstreifen (Datei oder Ordner) für Leser 1 (Kanal K1) bzw. Leser 2 (K2). Auch '
                                                   'als Zeile der Testdatei möglich (Abschnitt 3.6).', 'nicht angegeben'],
              ['`--stanzer1 PFAD`', 'Ausgabedatei des Stanzers 1 (Kanal K1); ein Ordner (auch ein Name mit „/“ am Ende) ergibt '
                                    '`stanzer-ausgabe.txt` darin. Auch als Zeile der Testdatei möglich.', 'nicht angegeben'],
              ['`--sw-ausgabe PFAD`', 'Schreibwerk-Ausgabe (Kanal K2) in die Datei `sw-ausgabe.txt` dieses Verzeichnisses '
                                      '(ohne Endung: Verzeichnis, wird angelegt). Angelegt erst bei der ersten Ausgabe eines Tests, '
                                      'danach angehängt. Auch als Zeile der Testdatei möglich.', 'Ausgabe ans Terminal'],
              ['`--k0 datei=PFAD`', 'Eingabequelle für Kanal K0 (T und SW): Datei oder Ordner mit einem Zeichen oder Namen je '
                                    'Zeile. Auch als Zeile der Testdatei möglich.', 'Eingabe vom Terminal'],
              ['`--pruefe-stanzer1` `DATEI`', 'Dateiprüfung: vergleicht die über `--stanzer1` erzeugte Datei mit der Soll-Datei '
                                            '`DATEI` (ein Name ohne Ordner liegt neben der Testdatei). Setzt `--stanzer1` voraus; '
                                            'nur mit einer Testdatei. Auch als Zeile im Teil `Prüfungen:` möglich (Abschnitt 3.4).',
               'keine Prüfung'],
              ['`--pruefe-sw-ausgabe` `DATEI`', 'wie `--pruefe-stanzer1`, aber für die über `--sw-ausgabe` erzeugte Datei '
                                              '`sw-ausgabe.txt`; setzt `--sw-ausgabe` voraus.', 'keine Prüfung'],
              ['`--knotentest`', 'Nimmt die Zeilen der durchlaufenen Knoten (`Kxxx …`) in das Knotenprotokoll auf. Ändert weder '
                                 'den Ablauf noch die „Knoten“-Zahl der Endzeile.', 'aus'],
              ['`--NO-TERMOUT`', 'Unterdrückt alle Ausgaben des Interpreters selbst am Terminal (Ausnahmen: vom C8205-Programm '
                                 'erzeugte Zeichen, Meldungen bei fehlgeschlagener Vorab-Prüfung und zur Trommeldatei). Der '
                                 'Schalter ist case-sensitiv, genau so zu schreiben.', 'aus'],
              ['`--SW-TERMINAL`', 'Öffnet neben dem Terminal das Textfenster „SW Ausgabe“ (130 × 36 Zeichen, verschiebbar) und '
                                  'gibt jede Schreibwerk-Ausgabe (K2) **zusätzlich** dort aus, gleichgültig ob `--sw-ausgabe` '
                                  'gesetzt ist; außerdem erscheint jede angenommene K0-Eingabe als Echo in Dunkelgelb (Abschnitt 5.4). '
                                  'Braucht `tkinter` und eine grafische Oberfläche; fehlt eines davon, erscheint eine Warnung und '
                                  'der Test läuft ohne Fenster. Nur auf der Kommandozeile; als Zeile der Testdatei ein Formfehler.',
               'aus (kein Fenster)'],
              ['`--zwischenablage` `auto|tk|system`', 'Kopierverfahren des Fensters „SW Ausgabe“ (nur mit `--SW-TERMINAL`): `auto` '
                                                    'versucht zuerst ein Systemprogramm bzw. die Win32-API und nur bei Misserfolg '
                                                    'Tk; `tk` nutzt nur die Tk-Zwischenablage; `system` nur Systemprogramm bzw. '
                                                    'Win32-API. Gedacht für Umgebungen mit eigenem Zwischenablage-Abgleich (z. B. '
                                                    'virtuelle Maschinen).', '`auto`'],
              ['`--BASP abcdef`, `--basp abcdef`', 'Bahnsperrenschalter der Magnettrommel: sechs Ziffern `0`/`1` (1 = EIN); '
                                                   'a = Hauptschalter, b bis f = Zusatzschalter 0040, 0100, 0200, 0400, 1000. '
                                                   'Auch in der Form `--BASP=abcdef`, z. B. `--BASP=111000`. Jede andere Eingabe '
                                                   'wird mit der Kurzhilfe abgelehnt (Rückkehrcode 2). Bei einem Wert ungleich '
                                                   '`000000` nennt der Interpreter den Parameter am Bildschirm und im '
                                                   'Protokollkopf. **Die Wirkung (Schreibsperre der Trommel) ist noch nicht '
                                                   'umgesetzt:** der Wert wird nur geprüft und gespeichert. Nur auf der '
                                                   'Kommandozeile, nicht in der Testdatei.', '`000000` (alle aus)'],
              ['`--version`', 'Gibt die Versionsnummer des Interpreters (Form `y.xx-zzz`) aus und endet mit Rückkehrcode 0, ohne '
                              'einen Test auszuführen; eine Testdatei ist nicht anzugeben.', '–'],
              ['`-h`, `--help`', 'Hilfetext mit allen Schaltern.', '–']],
             [0.23, 0.59, 0.18])
    s += note('hinweis', FENSTER_HINWEIS)
    s.append(P('Die langen Bezeichnungen `--lochbandleser1`, `--lochbandleser2` und `--lochbandstanzer1` sind gleichwertig. Ein '
               'nicht angegebenes Gerät ist kein Fehler, solange das Programm es nicht benutzt. Benutzt es das Programm doch, '
               'erscheint eine rote Fehlermeldung und der Test endet (Kapitel 7). Ausnahmen: K0-Eingabe (Terminal) und '
               'Schreibwerk-Ausgabe (Terminal) haben eine Vorgabe und erzeugen auch ohne Schalter keinen Fehler.'))
    s.append(P('**Version abfragen.** `--version` braucht keine Testdatei und führt keinen Test aus. Die Wrapper sind für Testläufe '
               'gedacht; die Version fragen Sie direkt mit `python3` ab. Die Nummer ist fassungsabhängig und kein fester Sollwert.'))
    lab.neu()
    s += lab.sitzung([cmd('python3 c8205_interp.py --version')], erwarte=[0])
    s.append(P('Fehlerhafte Aufrufe zeigen die Kurzhilfe und enden mit Rückkehrcode 2:'))
    s += lab.dateien([('Tests/a.txt', T_STOP), ('Tests/b.txt', T_STOP)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST --out ergebnis.log Tests/a.txt Tests/b.txt')], erwarte=[2])
    s.append(P('Liegen die Regelwerk-Dateien nicht in `markdown-dateien/`, geben Sie das Verzeichnis mit '
               '`--mdverz ./markdown-dateien` an; der Wrapper tut das schon (Abschnitt 4.3).'))

    s += h2('4.2 Mehrere Tests, Protokollort')
    s += bullets([
        'Mehrere Testdateien hintereinander: `python3 c8205_interp.py --MODUS=TEST Tests/a.txt Tests/b.txt`. Dann nur `--out` ohne '
        'Dateiendung benutzen. Die Tests laufen nacheinander auf derselben Trommel (Abschnitt 3.7).',
        '`--out Test-Protokolle/t1.log` mit mehreren Tests wird abgelehnt (Beispiel oben, Rückkehrcode 2). Dasselbe gilt für '
        '`--pruefe-stanzer1` und `--pruefe-sw-ausgabe`.',
        'Eine Protokolldatei entsteht nur bei `#PROT STUFE=2`; bei Stufe 0 oder 1 erscheint bei angegebenem `--out` ein Hinweis.'])
    s += lab.dateien([('Tests/kurz2.txt', T_STOP2)], neu=False, zeigen=False)
    s += lab.sitzung(['python3 c8205_interp.py --MODUS=TEST --out ergebnis Tests/kurz2.txt', 'ls ergebnis/kurz2'], erwarte=[4, 0])

    s += h2('4.3 Wrapper')
    s.append(P('Der Wrapper nimmt eine Testdatei entgegen, leitet sie an den Interpreter und schreibt das Protokoll nach '
               '`Test-Protokolle/<Testname>.log` (der Name der Testdatei mit der Endung `.log`). Alle weiteren Argumente gibt er '
               'unverändert an den Interpreter weiter, sodass jeder Schalter aus Abschnitt 4.1 auch über den Wrapper nutzbar ist. '
               'Ohne Testdatei meldet er „Test-Datei fehlt.“ (Code 1). Die Testdatei darf an beliebiger Stelle stehen; in dieser '
               'Anleitung steht sie der Übersicht halber zuerst.'))
    s += L.code("""$ ./c8205_interpreter.sh Tests/0015-030.txt                             # Linux/macOS
> c8205_interpreter.bat Tests\\0015-030.txt                              # Windows

# mit zusätzlichen Schaltern:
$ ./c8205_interpreter.sh Tests/x.txt --leser1 virtuelle_Geraete/Leser1
$ ./c8205_interpreter.sh Tests/x.txt --leser1 band5.txt --knotentest
$ ./c8205_interpreter.sh Tests/x.txt --trommel andere/trommel.txt
$ ./c8205_interpreter.sh Tests/x.txt --mdverz ./markdown-dateien

# Kern des Linux-Wrappers:
python3 c8205_interp.py --MODUS=TEST --mdverz ./markdown-dateien --out "Test-Protokolle/$prot_file" "$file" "${rest[@]}\"""")
    s += note('hinweis', 'Die Vorgaben des Wrappers (`--mdverz`, `--out`) stehen vor den weitergereichten Schaltern; bei doppelter '
                         'Angabe gilt der zuletzt genannte, ein eigenes `--out` überschreibt also die Vorgabe. Die Wrapper erkennen '
                         'Schalter mit eigenem Wertargument (`--out`, `--trommel`, `--stanzer1`, `--sw-ausgabe`, '
                         '`--pruefe-stanzer1`, `--pruefe-sw-ausgabe`, `--zwischenablage` u. a.); der Wert gilt nie als Testdatei. '
                         'Unter Windows (`.bat`) müssen Werte mit Gleichheitszeichen in Anführungszeichen stehen, z. B. '
                         '`--k0 "datei=band\\k0"`; Pfade mit Leerzeichen ebenfalls. Der Wrapper setzt die Trommel nicht zurück '
                         'und übergibt `--trommel` nicht. Es wird eine Testdatei je Aufruf verarbeitet.')

    s += h2('4.4 Rückkehrcodes')
    s.append(P('Der Interpreter liefert dem Betriebssystem einen Rückkehrcode, der sich stets auf **genau einen** Test bezieht; bei '
               'mehreren Testdateien in einem Aufruf zählt der zuletzt bearbeitete. Der Wrapper gibt den Code unverändert weiter. '
               'Ob ein Test „wahr“ oder „falsch“ war, lässt sich so ohne Auswertung der Bildschirmzeilen prüfen.'))
    s += tbl([['Code', 'Bedeutung'],
              ['0', 'Prüfung definiert (Teil `Prüfungen:` und/oder Dateiprüfung) und Ergebnis `Test wahr`.'],
              ['4', 'Lauf ordnungsgemäß beendet, aber keine Prüfung angegeben (weder `Prüfungen:` noch `--pruefe-…`).'],
              ['6', 'Prüfung definiert, Ergebnis `Test falsch` (auch: Soll- oder Ist-Datei fehlt, Dateiinhalt verschieden).'],
              ['8', 'Sonstige Laufzeitfehler: Stub, Gerät nicht nutzbar, Knotenlimit, Abbruch mit Strg+C.'],
              ['16', 'Vorab-Fehler, der Test startet nicht: formale Prüfung negativ (u. a. fehlender Geräte-Pfad, `--pruefe-…` '
                     'ohne Gerät, `--SW-TERMINAL` als Zeile der Testdatei), Trommeldatei fehlt oder ist fehlerhaft, ungültige '
                     'Tastenfolge, Testdatei nicht gefunden oder nicht eindeutig.'],
              ['2', 'Ungültiger Aufruf: unbekannter oder falsch angegebener Schalter, fehlende Regelwerk-Dateien, `--out` mit '
                    'Dateiendung bei mehreren Tests. Es startet kein Test.']],
             [0.1, 0.9], first_bold=True)
    return s


# ------------------------------------------------------------------ Kapitel 5
def kap5(lab):
    s = h1('5 Ein- und Ausgabe')
    s.append(P('Ein Programm wählt einen Kanal mit einem Anwahlbefehl (Operation 030 mit Adresse 4400…4700) aus. Danach wirken '
               'Eingabe- und Ausgabebefehle auf das zugehörige Gerät.'))
    s += tbl([['Anwahl', 'Kanal', 'Eingabe', 'Ausgabe', 'Schalter'],
              ['`4700 030`', 'K0', 'Pult-Tastatur (T) oder Schreibwerk (SW)', 'keine', '`--k0`'],
              ['`4600 030`', 'K1', 'Lochstreifenleser 1', 'Lochstreifenstanzer 1', '`--leser1`, `--stanzer1`'],
              ['`4500 030`', 'K2', 'Lochstreifenleser 2', 'Schreibwerk (Terminal)', '`--leser2`, `--sw-ausgabe`, `--SW-TERMINAL`'],
              ['`4400 030`', 'K3', 'frei', 'frei', '– (nicht benutzt)']],
             [0.15, 0.08, 0.27, 0.22, 0.28])
    s.append(P('Ein Ausgabe-Halt-Befehl (`a 030` mit `a₁ ≤ 3`) gibt das Zeichen aus, dessen Ausgabe-Adresse (die ersten drei '
               'Oktalstellen von `a`, Kodetabelle 1) passt. Während der Ausgabe ist Flag A = 1. Der Stanzer wertet alle acht Bits '
               'aus, das Schreibwerk nur sechs (Spuren v u 8 4 2 1; die Spuren w und p ändern das Zeichen nicht).'))
    s += note('achtung', 'Ein Ausgabe-Halt ohne angewähltes Ausgabegerät (Kanal K0, K3 oder gar keine Anwahl) liegt außerhalb des '
                         'definierten Betriebs: Der Rechner würde mit gesetztem Flag A stoppen, der Interpreter meldet das als Stub '
                         'und lässt A = 1 (Endzeile `A=1`). Dasselbe gilt für eine nicht existierende Anwahl. Kanal K3 hat kein '
                         'Gerät und wird in dieser Ausbaustufe nie benutzt.')

    s += h2('5.1 Schreibwerk-Ausgabe (K2)')
    s += bullets([
        'Die Schreibwerk-Ausgabe läuft immer über Kanal K2; die Stellung des Schalters SW hat keinen Einfluss (SW betrifft nur die '
        'Eingabeseite, Kanal K0).',
        'Ohne `--sw-ausgabe` erscheint jedes Zeichen sofort auf dem Terminal in Dunkelgelb.',
        'Mit `--sw-ausgabe PFAD` erscheint nichts am Terminal; die Zeichen gehen in `PFAD/sw-ausgabe.txt` (bei der ersten Ausgabe '
        'eines Tests neu angelegt, danach angehängt). `WRZL` schließt die aktuelle Zeile ab.',
        'Mit `--SW-TERMINAL` erscheint jedes Zeichen **zusätzlich** im Fenster „SW Ausgabe“ (nur Text, 130 × 36 Zeichen, '
        'verschiebbar, Vorgabe rechts unten auf dem Desktop), gleichgültig ob `--sw-ausgabe` gesetzt ist; Datei bzw. Terminal '
        'bleiben wie beschrieben. Das Fenster läuft als eigener Prozess und überlebt den Interpreter und sein Terminal.',
        'Die Zeichenlage KB/GB wird beim Start zufällig gesetzt. `Um. KB` (Ausgabe-Adresse `117x`) und `Um. GB` (`057x`) stellen '
        'sie um; sie wirken, geben aber selbst nichts aus. Ohne Umschaltzeichen im Programm ist die Groß-/Kleinschreibung also '
        'zufällig.',
        'Zeichen ohne sichtbare Darstellung erscheinen als `<n>` (z. B. `<Irrung Zeichen>`); `SatzMarke` (`272x`) ist ein '
        'Zeilenumbruch.',
        'Ist eine Ausgabe-Adresse nicht in Tabelle 1, erscheint nichts (Hinweis im Protokoll).',
        'Bei `STUFE=1` mit `--knotentest` erscheinen die Knotenzeilen erst nach dem Lauf; die Schreibwerk-Ausgabe steht davor.'])
    s += note('hinweis', FENSTER_HINWEIS)
    s.append(kopf3('Markieren und Kopieren im Fenster'))
    s.append(P('Der Text im Fenster lässt sich mit der Maus markieren (auch Doppel- und Dreifachklick). Kopiert wird sofort beim '
               '**Loslassen der Maustaste**, mit **Strg+C**, **Strg+Umschalt+C** oder **Strg+Einfg** (auch wenn der Tastaturfokus '
               'nicht im Textfeld liegt) und über das **Kontextmenü** (rechte Maustaste; auf macOS auch mittlere Taste bzw. '
               'Strg+Klick) mit „Kopieren“ und „Alles markieren“. Strg+A markiert den gesamten Text. Jedes erfolgreiche Kopieren '
               'meldet sich kurz in der Titelleiste („kopiert (N Zeichen, Verfahren)“), ein Fehlschlag mit „Kopieren '
               'fehlgeschlagen“ (Kapitel 7). Derselbe Text wird innerhalb von 5 Sekunden nicht erneut in die Zwischenablage gelegt.'))
    s.append(P('Das Verfahren wählt `--zwischenablage`. Mit `auto` (Vorgabe) wird zuerst ein Systemprogramm benutzt, das die '
               'Zwischenablage dauerhaft übernimmt: unter Windows die Win32-API, unter Linux `wl-copy` (Wayland), `xsel` oder '
               '`xclip` (X11), unter macOS `pbcopy`, unter WSL zusätzlich `clip.exe`. Die Auswahl erfolgt bei jedem Kopieren nach '
               'den Umgebungsvariablen und den installierten Programmen; fehlende werden übersprungen. Die Tk-Zwischenablage ist der '
               'Rückfall. In virtuellen Maschinen entscheidet das Gast-Zusatzprogramm, wie der Text zum Host kommt; probieren Sie '
               'dort `--zwischenablage system` oder `tk`.'))
    s.append(P('Beispiele (die Fenster selbst lassen sich hier nicht abbilden; im Fenster steht `Jahr 1972`, das Terminal zeigt '
               'weiter die Zeilen des Interpreters):'))
    s += L.code("""$ python3 c8205_interp.py --MODUS=TEST --SW-TERMINAL Tests/0015-030.txt
$ python3 c8205_interp.py --MODUS=TEST --SW-TERMINAL --zwischenablage system Tests/0015-030.txt
$ python3 c8205_interp.py --MODUS=TEST --SW-TERMINAL --sw-ausgabe virtuelle_Geraete/SW-Ausgabe Tests/0015-030.txt""")

    s += h2('5.2 Lochstreifenleser (K1, K2)')
    s.append(P('`--leser1` und `--leser2` nehmen eine **Datei** (ein Streifen) oder einen **Ordner** (Streifen in '
               'Namensreihenfolge). Pro Eingabebefehl wird eine Zeile gelesen: acht Zeichen `0`/`1` für die Spuren `w v u p 8 4 2 1` '
               '(die Transportspur wird nicht dargestellt). Leerzeilen sind Vorspann und werden übergangen.'))
    s += bullets([
        'Ungerade Zahl gelochter Spuren = gültig. Gerade Zahl = Fehler bei Eingabe: Flag FE := 1, der Lauf hält.',
        'Ausnahme „Irrung Zeichen“ (`11111111`, alle acht Spuren): keine Paritätsprüfung, kein FE, nicht ins Adressregister '
        'übernommen. Der Eingabebefehl überspringt die Zeile und liest das nächste Zeichen.',
        'Die Eingabeadresse wird aus dem Lochbild berechnet und muss in Tabelle 1 vorkommen; sie wird mit dem Adressregister '
        'ODER-verknüpft.',
        'Danach wird der Befehl umgestellt: bei Sprung-Umstellung „ja“ (z. B. `:`, `.`, `,`, Tabulator, `Um. KB`, `Um. GB`) zu '
        'einem unbedingten Sprung an `a ODER Eingabeadresse`; bei „nein“ (Ziffern, Buchstaben) zu einem Lesebefehl, der den '
        '**Inhalt der Zelle** `a ODER Eingabeadresse` zum AC addiert (nicht die Eingabeadresse selbst).',
        'Ist der Streifen zu Ende, wartet der Interpreter still (ohne Meldung) auf eine neu in den Pfad kopierte Streifendatei (der '
        'reale Leser würde ebenfalls warten); ein nicht vorhandener Pfad verhindert den Teststart. Strg+C beendet das Warten '
        '(Rückkehrcode 8).'])
    s += note('achtung', 'Die Ziffer 5 liefert nicht den Wert 5 im AC, sondern den Inhalt der Zelle 0005 (ODER Adressteil des '
                         'Eingabebefehls). Ist die Zelle nicht belegt, bleibt der AC 0. Legen Sie die gewünschten Konstanten in den '
                         'Trommelabschnitt, auch wenn der Wert 0 ist: Die Trommel behält Reste früherer Läufe (Abschnitt 3.7). '
                         'Beispiel in Abschnitt 8.3.')
    s += h2('5.3 Lochstreifenstanzer (K1)')
    s.append(P('`--stanzer1 PFAD` ist die Ausgabedatei (bei einem Ordner: `stanzer-ausgabe.txt` darin). Je gestanztem Zeichen '
               'entsteht eine Zeile mit acht Zeichen `0`/`1` für `w v u p 8 4 2 1`. Die Datei wird beim ersten gestanzten Zeichen '
               'eines Laufs neu angelegt (nicht angehängt) und nur angelegt, wenn wirklich gestanzt wird. Anders als beim '
               'Schreibwerk gibt es keinen Terminal-Ausweg: Ohne `--stanzer1` endet ein Test, der auf K1 ausgibt, mit der roten '
               'Fehlermeldung aus Kapitel 7.'))
    s += h2('5.4 Pult-Tastatur und Schreibwerk-Eingabe (K0)')
    s.append(P('Ohne `--k0` liest der Interpreter einen Tastendruck je Eingabebefehl vom Terminal (ohne Echo, ohne Enter; Strg+C '
               'wirkt). `--k0 datei=PFAD` (oder die gleichnamige Zeile der Testdatei) liest eine Textdatei mit einem Zeichen oder '
               'Namen je Zeile (`ZR`, `WM`, `IS`, `IB`, `TAB`, `WRZL` oder Namen aus Tabelle 1; Zeilen mit `#` sind Kommentar). '
               '`PFAD` darf ein Ordner mit mehreren Dateien sein, die in alphanumerischer Reihenfolge gelesen werden. Ist die '
               'Eingabe zu Ende, wartet der Interpreter still auf eine neu in den Pfad kopierte Datei; ein nicht vorhandener Pfad '
               'verhindert den Teststart.'))
    s += tbl([['Zustand', 'Eingebbar'],
              ['SW nicht gedrückt (Flag T, Pult-Tastatur)', 'nur `0`–`9`, `+`, `-`, `,`, `.`, `:`, `ZR`, `WM`, `IS`, `IB` (19 Codes). '
                                                            '`B` und `D` haben keinen Code und sind nicht eingebbar.'],
              ['SW gedrückt (Flag SW, Schreibwerk)', 'alle Zeichen der Tabelle 1']], [0.35, 0.65])
    s.append(P('Ein nicht erlaubtes Zeichen wird bei `datei=` mit roter Meldung abgelehnt (der Test endet); bei Terminal-Eingabe wird '
               'der Tastendruck ignoriert und auf die nächste gültige Taste gewartet. Zeichen werden über die Spalten „Ascii '
               'KB/GB“ der Kodetabelle gefunden; die Eingabe-Zeichenlage (Start KB, geändert durch gelesenes `Um. KB`/`Um. GB`) '
               'bestimmt, welche Spalte zuerst durchsucht wird. Nur bei Terminal-Eingabe ohne weitere Zeichen (z. B. '
               'geschlossenes stdin) endet der Lauf mit `EINGABE_ENDE`:'))
    s += lab.dateien([('Tests/k0-ziffer.txt', T_K0)], neu=True, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/k0-ziffer.txt < /dev/null')], erwarte=[4])
    s.append(P('**Echo im Fenster.** Mit `--SW-TERMINAL` erscheint jedes **angenommene** K0-Zeichen (T oder SW; vom Terminal oder '
               'aus `--k0 datei=PFAD`) zusätzlich als Echo in Dunkelgelb im Fenster „SW Ausgabe“; die Ausgaben des Rechners stehen '
               'dort in der Standardfarbe, so lassen sich Eingabe und Ausgabe unterscheiden. Das Echo zeigt das Zeichen wie das '
               'Schreibwerk (Namen ohne Zeichen als `<n>`) in der gerade gültigen Zeichenlage. Nicht angenommene Zeichen und die '
               'Eingaben der Lochstreifenleser erscheinen nicht. Ohne den Schalter gibt es kein Echo.'))
    s += note('hinweis', 'Unter Linux/macOS wird `termios`, unter Windows `msvcrt.getch()` benutzt. Unter Windows kann Strg+C in '
                         'Ausnahmefällen als normales Zeichen ankommen; im Zweifel hilft Strg+Pause oder das Schließen des '
                         'Konsolenfensters.')
    return s


# ------------------------------------------------------------------ Kapitel 6
def kap6(lab):
    s = h1('6 Ergebnisse lesen')
    s += h2('6.1 Bildschirmausgabe')
    s.append(P('Je Test erscheinen der Reihe nach: die Kopfzeile `=== Test <n> (#PROT STUFE=n) ===`, die Schreibwerk-Zeichen des '
               'Programms, eine eventuelle Diagnose (`-- Diagnose --`), bei Stufe 1 und `--knotentest` die Knotenzeilen, die '
               'Endzeile und – falls der Test Prüfungen enthält – die Ergebnisprüfung.'))
    s += h2('6.2 Die Endzeile')
    s += L.code('Ende: <Grund> | Knoten: n | BZ=… AC=… AR=… | FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0')
    s += tbl([['Teil', 'Bedeutung'],
              ['<Grund>', 'warum der Lauf endete (Tabelle unten)'],
              ['Knoten: n', 'Zahl der durchlaufenen Knoten (fassungsabhängig, kein Sollwert, keine Zeitangabe)'],
              ['BZ, AR', 'Befehlszähler und Adressregister, vierstellig oktal'],
              ['AC', 'Akkumulator, elfstellig oktal'],
              ['FE', 'Fehler bei Eingabe'],
              ['FUE', 'Überlauf (FÜ)'],
              ['BS, US', 'bedingter bzw. unbedingter Stopp'],
              ['E, A', 'Eingabe- bzw. Ausgabebefehl aufgestellt (der Lauf wartet noch auf ein Gerät; bei einem Ausgabe-Stub bleibt '
                       'A = 1)'],
              ['V1, V2', 'Vergleicher (V3 = V1 und V2)']], [0.2, 0.8], first_bold=True)
    s += tbl([['Endgrund', 'Bedeutung'],
              ['Unbedingter Stop (US:=1)', 'Programm hat ordnungsgemäß gehalten'],
              ['Bedingter Stop (BS:=1)', 'bedingter Stopp-Befehl bei eingerastetem Schalter BS'],
              ['Halt wegen Ueberlauf (FUE bereits 1)', 'Überlauf-Halt; weder US noch BS gesetzt, nur FÜ'],
              ['Fehler bei Eingabe (FE)', 'gerade Zahl von Lochungen gelesen'],
              ['EINGABE_ENDE', 'Terminal-Eingabe (K0) ohne weitere Zeichen, z. B. geschlossenes stdin. Bei Leser und `--k0 datei=` '
                               'gibt es kein Ende, sondern stilles Warten.'],
              ['Halt (Schalter H): Tastenfolge endet ohne R', 'Tastenfolge endete im Halt (gültig, z. B. `H G Ü E`)'],
              ['Halt (Schalter H): INTERRUPT nach Befehl pppp endet ohne R/ST',
               'Die Tastenfolge eines `#INTERRUPT` endete weder mit `R` noch mit `ST` (gültig; Abschnitt 3.2)'],
              ['Geraet nicht nutzbar …', 'Gerät nicht angegeben oder Datei/Zeichen ungültig (rote Meldung davor; davor steht auch die '
                                         'Zeile „TEST NICHT ORDNUNGSGEMAESS BEENDET“). Gilt nicht für K0 (Terminal) und '
                                         'K2-Ausgabe (Terminal).'],
              ['STUB bei Knoten n …', 'Regelwerk unvollständig oder außerhalb des definierten Betriebs: Kanal K3 benutzt, '
                                      'Ausgabe-Halt ohne Gerät (Kapitel 7)'],
              ['Abbruch: Knotenlimit erreicht (Endlosschleife?)', 'Der Lauf hat die Sicherheitsgrenze von über 2 Millionen Knoten '
                                                                  'überschritten: Das Programm hält nie an (Kapitel 7).'],
              ['Tastenfolge nicht gueltig/definiert', 'Test startete nicht (Abschnitt 3.3)']], [0.4, 0.6])
    s.append(P('Beispiel für den Endgrund „Halt wegen Überlauf“: Der Test addiert zweimal 1 zu 37777777777, der größten positiven '
               'Zahl; nach dem Überlauf hält der Rechner, es ist weder US noch BS gesetzt, nur FUE=1.'))
    s += lab.dateien([('Tests/ueberlauf.txt', T_UEBERLAUF)], neu=True, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/ueberlauf.txt')], erwarte=[4])

    s += h2('6.3 Diagnose bei Befehl 164')
    s.append(P('Der Leerbefehl 164 löst die Diagnose aus, wenn für seine Adresse `xxxx` Testmarken definiert sind. Reihenfolge: '
               'zuerst die `#DOK`-Texte (Dateireihenfolge), dann alle `#SPEI`-Bereiche, dann alle `#SPUR`-Spuren; jede '
               'Speicherzelle steht als `aaaa: wwwwwwwwwww`. Vor `#SPEI`/`#SPUR` steht die auslösende Marke selbst als Zeile. Die '
               'Marken sind unabhängig voneinander (auch ein einzelnes `#SPEI` ohne `#DOK` gibt seine Zellen aus); passt keine '
               'Marke, entfällt die Diagnose ganz. Ein Beispiel mit `#SPEI` zeigt Abschnitt 8.4. Eine `#SPUR`-Marke gibt alle 32 '
               'Zellen der Spur in der Reihenfolge aus, in der sie unter dem Kopf der Trommel vorbeilaufen (die Adressen springen: '
               '4000, 4015, 4032, 4007 …, nicht 4000, 4001, 4002 …); im Beispiel steht in der Zelle 4001 der Wert 7:'))
    s += lab.dateien([('Tests/spur-demo.txt', T_SPUR)], neu=True, zeigen=False)
    s += lab.sitzung(['python3 c8205_interp.py --MODUS=TEST Tests/spur-demo.txt'], erwarte=[4])
    s += note('achtung', 'Die Leer-Befehle 164 und 166 laufen ohne Resultatbehandlung: Das Z-Feld erzeugt keine Verschiebung des AC.')

    s += h2('6.4 Knotenprotokoll und Protokolldatei')
    s.append(P('Bei `#PROT STUFE=1` erscheinen die Knotenzeilen auf dem Bildschirm, bei `STUFE=2` in der Protokolldatei – aber nur, '
               'wenn Sie mit `--knotentest` aufrufen. Ohne den Schalter entfallen die Zeilen `Kxxx …`; erhalten bleiben die '
               '`BR=`-Zeilen (vor Knoten 2 und 7), die Diagnose sowie Fehler- und Stub-Meldungen.'))
    s += lab.dateien([('Tests/kurz.txt', T_KURZ)], neu=True, zeigen=False)
    s += lab.sitzung(['python3 c8205_interp.py --MODUS=TEST --knotentest Tests/kurz.txt'], zeilen=15,
                     caption='Auszug: die ersten 15 Zeilen der Ausgabe.')
    s += tbl([['Zeile', 'Lesart'],
              ['`Kxxx ANW nnn BZ=… AR=… AC=…`', 'Knoten xxx, Typ Anweisung (ANW), ANWEISUNG-nnn; danach BZ, AR und AC, jeweils oktal'],
              ['`Kxxx TST nnn … -> falsch`', 'Knoten xxx, Typ Test (TST), ANWEISUNG-nnn; `-> wahr` oder `-> falsch` ist das '
                                             'Testergebnis'],
              ['`KON`, `PHA`', 'Konnektor bzw. Phasenzuordnung („Phase I“ … „Phase IV“)'],
              ['`BR=aaaa ooo (vor Knoten 002) …`', 'Befehlsregister (Adressteil und Operationsteil des geladenen Befehls) vor Beginn '
                                                   'von Phase I; dazu BZ, AC, Überlauf FÜ und die Vergleicher V1, V2, V3']],
             [0.34, 0.66])
    s.append(P('Die Protokolldatei (nur bei `STUFE=2`) hat bis zu vier Abschnitte: `== 1. Ausgangsbedingungen ==` (die vom Test '
               'geschriebenen Zellen, Anfangswerte, Tastenfolge mit der Wirkung jeder Taste), `== 2. Zustaende des '
               'Knotenautomaten ==`, `== Ende ==` und, falls der Test Prüfungen enthält, `== 3. Ergebnispruefung ==`. Beispiel '
               'einer Tastenfolge mit vielen Token (aus Abschnitt 8.2):'))
    s += lab.dateien([('Tests/tf-demo.txt', T_TFDEMO)], neu=True, zeigen=False)
    s += lab.sitzung(['python3 c8205_interp.py --MODUS=TEST --out Test-Protokolle/tf-demo.log Tests/tf-demo.txt',
                      'cat Test-Protokolle/tf-demo.log'], erwarte=[4, None])
    log = lab.lies('Test-Protokolle/tf-demo.log')
    global PROTOKOLLKOPF_ALT
    PROTOKOLLKOPF_ALT = 'nicht genannte Zellen = 0' in log
    if PROTOKOLLKOPF_ALT:
        s += note('hinweis', 'Die Kopfzeile des Abschnitts 1 lautet „Trommeldatei (uebernommen, Ausschnitt; nicht genannte Zellen = '
                             '0)“. Das ist ein Rest aus der Zeit vor der persistenten Trommel: Nicht genannte Zellen haben nicht '
                             'unbedingt den Wert 0, sondern den Inhalt der Trommeldatei (Abschnitt 3.7). Das Protokoll zeigt nur die '
                             'Zellen des Trommelabschnitts.')
    s.append(P('Zeilen für `#AC=` und `#BZ=` erscheinen, wenn die Marken gesetzt sind:'))
    s += lab.dateien([('Tests/ac-log.txt', T_ACLOG)], neu=False, zeigen=False)
    s += lab.sitzung(['python3 c8205_interp.py --MODUS=TEST --out Test-Protokolle/ac-log.log Tests/ac-log.txt',
                      'cat Test-Protokolle/ac-log.log'], erwarte=[4, None])

    s += h2('6.5 Ergebnisprüfung')
    s.append(P('Hat die Testdatei einen `Prüfungen:`-Teil und endete der Lauf ordnungsgemäß, folgt auf die Endzeile die Prüfung: je '
               'Wert Soll und Ist mit OK oder FEHLER, danach `Test wahr` oder `Test falsch`. Sie erscheint unabhängig von '
               '`#PROT STUFE`; bei `STUFE=2` steht dasselbe als Abschnitt `== 3. Ergebnispruefung ==` am Ende der Protokolldatei.'))
    s += lab.dateien([('Tests/pruef-falsch.txt', T_PFALSCH)], neu=True, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/pruef-falsch.txt')], erwarte=[6])
    s.append(P('`Test wahr` gibt es nur, wenn alle angegebenen Prüfungen übereinstimmen. Hier stimmt BZ nicht (soll 0003, ist 0004); '
               'der AC stimmt. Rückkehrcode 6 (Abschnitt 4.4). Beispiel mit Erfolg: Abschnitt 8.4.'))
    s.append(kopf3('Dateiprüfungen'))
    s.append(P('`--pruefe-stanzer1` und `--pruefe-sw-ausgabe` erscheinen im selben Block hinter den Einzelprüfungen, je Prüfung eine '
               'Zeile:'))
    s += tbl([['Zeile', 'Bedeutung'],
              ['Stanzer 1: soll=<Soll-Datei> ist=<Ist-Datei> OK', 'Inhalt (zeilenweise) gleich; für das Schreibwerk steht '
                                                                   '„Schreibwerk:“ davor.'],
              ['… FEHLER (Soll-Datei fehlt)', 'Die Soll-Datei existiert nicht (Name ohne Ordner: neben der Testdatei suchen).'],
              ['… FEHLER (Ist-Datei fehlt, vom Lauf nicht angelegt)', 'Der Lauf hat nichts gestanzt bzw. ausgegeben; eine übrig '
                                                                       'gebliebene Datei eines früheren Laufs zählt nicht.'],
              ['… FEHLER (Inhalt verschieden, diff):', 'Darunter der Unterschied im Format `diff -u` (Soll gegen Ist, höchstens '
                                                       '100 Zeilen, danach „… n weitere diff-Zeilen nicht angezeigt“).']],
             [0.4, 0.6])
    s.append(P('Beispiel: Der Stanzer-Test aus Abschnitt 8.3 gegen eine Soll-Datei, die in der letzten Zeile abweicht:'))
    lab.dateien([('Tests/stanzer-pruefe.txt', T_STANZER_PR), ('Tests/soll.txt', SOLL), ('Tests/soll-falsch.txt', SOLL_FALSCH)],
                neu=True, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST --pruefe-stanzer1 soll-falsch.txt Tests/stanzer-pruefe.txt')], erwarte=[6])
    s.append(P('Der Rückkehrcode folgt dem Gesamtergebnis (0 oder 6). Mit `--NO-TERMOUT` entfällt die Bildschirmausgabe; das '
               'Ergebnis steht dann bei `#PROT STUFE=2` in der Protokolldatei und im Rückkehrcode.'))
    return s


# ------------------------------------------------------------------ Kapitel 7
FEHLER = [
    # (Meldung, Ursache, Abhilfe, Code)
    ('Abbruch: Knotenlimit erreicht (Endlosschleife?)',
     'Programm läuft ohne Stopp-Befehl weiter, z. B. weil eine leere Zelle (Wert 0 = Sprung nach 0000) erreicht wird',
     'Stopp-Befehl `00000000020` hinter das Programmende schreiben; Programmfluss prüfen', '8'),
    ('Ausgabe auf Lochbandstanzer 1 (Kanal K1) angefordert, aber --stanzer1 nicht angegeben.',
     'Programm stanzt, Schalter fehlt', '`--stanzer1 PFAD` angeben (Schalter oder Zeile)', '8'),
    ('Eingabe von Lochbandleser n (Kanal Kn) angefordert, aber --lesern nicht angegeben.',
     'Programm liest von K1/K2, Schalter fehlt', '`--leser1` bzw. `--leser2` angeben (Schalter oder Zeile)', '8'),
    ('FEHLER: Trommeldatei "…" ist formal fehlerhaft - Test(s) starten nicht: mit Zeilen wie „Trommeldatei nicht gefunden: …“, '
     '„Trommeldatei hat n Zeilen; erwartet werden genau 4096 …“, „Zeile n: ungueltiges Format …“, „Zeile n: Adresse aaaa erwartet, '
     'gefunden bbbb.“, „Trommeldatei hat CRLF-Zeilenenden …“',
     'Trommeldatei fehlt, hat nicht genau 4096 Zeilen, eine Zeile hat das falsche Format, die Adressen sind nicht lückenlos '
     'aufsteigend oder die Zeilenenden sind CRLF statt LF',
     '`--trommel` bzw. Pfad prüfen; leere Trommel mit `python3 erzeuge_leere_trommel.py` neu erzeugen (Abschnitt 2.3); es startet '
     'kein Test', '16'),
    ('FEHLER: Trommeldatei "…" kann nicht geoeffnet werden: …',
     'Datei lässt sich nicht zum Schreiben öffnen (Rechte, schreibgeschützt)', 'Schreibrechte prüfen; es startet kein Test', '16'),
    ('FORMALE PRUEFUNG NEGATIV - Test startet nicht, Klaerung erforderlich:',
     'Testdatei formal fehlerhaft (Zeilenformat, doppelte Adresse, `#SPEI`-Spanne, `#PROT`, `#AC`/`#BZ`, `#INTERRUPT`, '
     '`#STARTE`, Tastenfolge, `Prüfungen:`, Geräte-Zeile oder -Pfad)', 'die genannte Zeile korrigieren (Abschnitt 3.5)', '16'),
    ('K0-Datei nicht lesbar: …', 'Datei fehlt oder ist nicht lesbar', 'Pfad prüfen', '8'),
    ("K0-Eingabe: '…' ist an der Pult-Tastatur (T) nicht eingebbar …", 'Zeichen ist an T nicht erlaubt (z. B. B, Buchstaben)',
     '`SW=1` vor `G` in die Tastenfolge oder ein anderes Zeichen', '8'),
    ('K0: Eingabe-Pfad nicht gefunden: …', 'bei `--k0 datei=PFAD` (Schalter oder Zeile) existiert der Pfad nicht', 'Pfad prüfen',
     '16'),
    ("--k0: 'datei=PFAD' erwartet …", 'ungültiger Wert für `--k0` (Schalter: Code 2; Zeile der Testdatei: Code 16)',
     '`--k0 datei=PFAD` schreiben', '2 / 16'),
    ('Knotenbeschreibung nicht gefunden: … / Knotengraph nicht gefunden: …',
     'eine der beiden Regelwerk-Dateien fehlt im `--mdverz`-Verzeichnis', '`--mdverz` korrekt angeben oder Datei dorthin legen',
     '2'),
    ('Kopieren fehlgeschlagen (Titelleiste des Fensters „SW Ausgabe“)',
     'Kein Kopierverfahren hat funktioniert (Linux: weder `wl-copy`/`xsel`/`xclip` noch Tk-Zwischenablage erreichbar; Windows: '
     'Zwischenablage von einem anderen Programm gesperrt)',
     '`--zwischenablage system` bzw. `tk` versuchen; unter Linux `xsel`, `xclip` oder `wl-clipboard` installieren; in virtuellen '
     'Maschinen das Gast-Zusatzprogramm prüfen', '–'),
    ('Lochbandleser n: Lochstreifen-Pfad nicht gefunden: …', 'Pfad falsch', 'Pfad prüfen', '16'),
    ('Lochstreifen …: ungueltige Zeile …', 'Zeile ist nicht acht Zeichen aus `0`/`1`', 'Streifendatei korrigieren', '8'),
    ('--out mit Dateiendung … ist nur mit genau einer Testdatei zulaessig', '`--out x.log` zusammen mit mehreren Tests',
     'Ordner ohne Endung verwenden oder Tests einzeln starten', '2'),
    ('--pruefe-stanzer1 ohne --stanzer1: … / --pruefe-sw-ausgabe ohne --sw-ausgabe: …',
     'Dateiprüfung ohne das zugehörige Gerät; es gäbe keine Ist-Datei', 'passenden Geräteschalter ergänzen (Schalter oder Zeile '
     'der Testdatei)', '16'),
    ('--pruefe-stanzer1/--pruefe-sw-ausgabe sind nur mit genau einer Testdatei zulaessig', 'Dateiprüfung mit mehreren Testdateien',
     'Tests einzeln starten', '2'),
    ('STUB bei Knoten n: …', 'eine vom Programm benutzte Funktion ist nicht umgesetzt oder liegt außerhalb des definierten '
                              'Betriebs (siehe unten)', 'Meldung und Testdatei notieren; Programm prüfen', '8'),
    ('Tastenfolge nicht gueltig/definiert', 'unbekanntes Token, weder `R` noch Halt am Ende, M nicht losgelassen',
     'Abschnitt 3.3', '16'),
    ('Testdatei nicht gefunden: …', 'Name weder als Pfad noch unterhalb der Suchordner vorhanden',
     'Pfad, Schreibweise und aktuellen Ordner prüfen (wird mit angezeigt)', '16'),
    ('Testdatei … nicht eindeutig gefunden', 'mehrere Dateien gleichen Namens', 'vollständigen Pfad angeben', '16'),
    ('WARNUNG: --SW-TERMINAL: kein Ausgabefenster moeglich: …',
     '`tkinter` fehlt oder es gibt keine grafische Oberfläche (unter Linux `DISPLAY` nicht gesetzt)',
     '`python3-tk` installieren bzw. in einer grafischen Sitzung starten; der Test läuft trotzdem, nur ohne Fenster',
     'Code des Tests'),
    ('Zeile n: --leser1/--leser2/--stanzer1/--sw-ausgabe/--k0 …',
     'Formfehler einer Geräte-Zeile der Testdatei: ohne Wert, mehrfach, `--k0` ohne `datei=`',
     'Zeile korrigieren; jede Zeile höchstens einmal (Abschnitt 3.6)', '16'),
    ('Zeile n: --SW-TERMINAL ist nur als Kommandozeilenschalter zulaessig, nicht in der Testdatei',
     'Der Schalter steht als Zeile in der Testdatei', 'Zeile entfernen; `--SW-TERMINAL` beim Aufruf angeben', '16'),
    ('Zeile n: #INTERRUPT: …', 'Formfehler einer `#INTERRUPT`-Zeile (z. B. vor der ersten Befehlszeile, erste Taste nicht `H`)',
     'Zeile korrigieren (Abschnitt 3.2)', '16'),
    ('Das Fenster „SW Ausgabe“ bleibt nach dem Test offen', 'gewollt: Das Fenster schließt sich nie von selbst',
     'mit Klick auf X schließen (jeder Aufruf mit `--SW-TERMINAL` öffnet ein eigenes Fenster)', '–'),
]


def kap7(lab):
    s = h1('7 Wenn etwas schiefgeht')
    s.append(P('Gerätefehler erscheinen in Rot auf dem Terminal (Standardfehlerausgabe, nur mit Terminal gefärbt) und beginnen mit '
               '„FEHLER:“. Danach folgt die Zeile „TEST NICHT ORDNUNGSGEMAESS BEENDET: …“ und die Endzeile. Meldungen der '
               'Vorab-Prüfungen (Testdatei, Trommeldatei, Aufruf) erscheinen ohne Farbe. Das Fehlerverzeichnis ist alphabetisch '
               'nach dem Meldungstext geordnet; die letzte Spalte nennt den Rückkehrcode (Abschnitt 4.4).'))

    def schluessel(e):
        return re.sub(r'^[-\s]+', '', e[0]).lower()

    rows = [['Meldung (Anfang)', 'Ursache', 'Abhilfe', 'Code']]
    rows += [list(e) for e in sorted(FEHLER, key=schluessel)]
    s += tbl(rows, [0.30, 0.27, 0.33, 0.10])
    s.append(P('**Stub.** Ein Stub ist kein Fehler des Aufrufs, sondern die Meldung „diese Stelle des Regelwerks ist nicht umgesetzt“ '
               'bzw. „außerhalb des definierten Betriebs“. Für die 512 Operationscodes gibt es keinen Stub mehr. Ein Stub tritt auf, '
               'wenn ein Programm auf Kanal K3 ein- oder ausgibt, wenn ein Ausgabe-Halt ohne Ausgabegerät ausgeführt wird (Kanal K0, '
               'K3 oder keine Anwahl; A bleibt 1), wenn ein Anwahlbefehl mit `a₂ < 4` benutzt wird oder wenn eine Eingabeadresse in '
               'Tabelle 1 nicht vorkommt. Notieren Sie Meldung und Testdatei; der Test wurde nicht „repariert“.'))

    s.append(kopf3('Beispiele'))
    s.append(P('**Gerät nicht angegeben.** Der Test aus Abschnitt 8.3 liest von Leser 1; ohne `--leser1` endet er mit der roten '
               'Meldung, Rückkehrcode 8:'))
    s += lab.dateien([('Tests/leser-ziffer.txt', T_LESER), ('Tests/stanzer-zeichen.txt', T_STANZER)], neu=True, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/leser-ziffer.txt')], erwarte=[8])
    s.append(P('Entsprechend für den Stanzer (Test `stanzer-zeichen.txt`, Abschnitt 8.3) ohne `--stanzer1`; der Ausgabebefehl steht '
               'aufgestellt (A=1):'))
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/stanzer-zeichen.txt')], erwarte=[8])
    s.append(P('**Zeichen an der Pult-Tastatur nicht eingebbar.** Die Datei `band/k0b.txt` enthält das Zeichen `B`; der Test '
               'benutzt die Pult-Tastatur (T), an der `B` keinen Code hat:'))
    lab.dateien([('Tests/k0-ziffer.txt', T_K0)], neu=False, zeigen=False)
    lab.schreibe('band/k0b.txt', 'B\n')
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST --k0 datei=band/k0b.txt Tests/k0-ziffer.txt')], erwarte=[8])
    s.append(P('**Stub: Ausgabe ohne angewähltes Gerät.** Das Programm gibt die Ziffer 5 aus, ohne vorher einen Kanal anzuwählen. '
               'Nach dem Original hält der Rechner mit Flag A; der Interpreter meldet das als Stub und lässt A = 1:'))
    s += lab.dateien([('Tests/stub-ausgabe.txt', T_STUB)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/stub-ausgabe.txt')], erwarte=[8])
    s.append(P('**Tastenfolge ungültig.** Hier fehlt vor `M-` ein `M+` (Test `tf-m.txt`, Tastenfolge `H G M- R`):'))
    s += lab.dateien([('Tests/tf-m.txt', T_TFM)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/tf-m.txt')], erwarte=[16])
    s.append(P('**Programm ohne Stopp (Endlosschleife).** Das Programm lädt eine Zahl und läuft dann in die leere Zelle 0001 (Wert 0). '
               'Ein Befehl mit dem Wert 0 ist der unbedingte Sprung nach Adresse 0000: Das Programm beginnt von vorn und endet nie. '
               'Nach über zwei Millionen Knoten bricht der Interpreter ab.'))
    s += lab.dateien([('Tests/endlos.txt', T_ENDLOS)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/endlos.txt')], erwarte=[8])
    s.append(P('**Geräte-Zeile ohne Wert.** Die Testdatei enthält in Zeile 3 die Zeile `--stanzer1` ohne Pfad:'))
    s += lab.dateien([('Tests/geraet-leer.txt', T_GERAET_LEER)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/geraet-leer.txt')], erwarte=[16])
    s.append(P('**Schalter als Zeile der Testdatei.** `--SW-TERMINAL` gilt nur auf der Kommandozeile:'))
    s += lab.dateien([('Tests/sw-term-zeile.txt', T_STOP.replace('#PROT STUFE=0\n', '#PROT STUFE=0\n--SW-TERMINAL\n'))],
                     neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/sw-term-zeile.txt')], erwarte=[16])
    s.append(P('**Unterbrechung an falscher Stelle.** Die Zeile `#INTERRUPT` steht vor der ersten Befehlszeile (Test `int-fehler.txt`):'))
    s += lab.dateien([('Tests/int-fehler.txt', T_INTF)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/int-fehler.txt')], erwarte=[16])
    s.append(P('**Testdatei nicht gefunden.**'))
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/gibtsnicht.txt')], erwarte=[16])
    s.append(P('**Pfad der K0-Eingabe nicht vorhanden.** Ein nicht vorhandener `--leser1`-, `--leser2`- oder `--k0`-Pfad wird schon '
               'vor dem Start gemeldet, auch wenn er als Zeile der Testdatei steht:'))
    lab.dateien([('Tests/a.txt', T_STOP)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST --k0 datei=band/gibtsnicht.txt Tests/a.txt')], erwarte=[16])
    s.append(P('**Kein Ausgabefenster möglich.** Ohne grafische Oberfläche (hier: `DISPLAY` nicht gesetzt) oder ohne `tkinter` läuft '
               'der Test trotz `--SW-TERMINAL` weiter, nur ohne Fenster:'))
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST --SW-TERMINAL Tests/a.txt')], erwarte=[4])
    s.append(P('**Vorab-Meldungen bleiben sichtbar.** Mit `--NO-TERMOUT` entfällt die Kopfzeile `=== Test … ===`, die Meldung der '
               'formalen Prüfung bleibt:'))
    lab.dateien([('Tests/formal.txt', T_FORMAL)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST --NO-TERMOUT Tests/formal.txt')], erwarte=[16])
    s.append(P('**Regelwerk-Dateien fehlen.** Ein Verzeichnis ohne die beiden `.md`-Dateien ergibt Rückkehrcode 2; mit dem richtigen '
               '`--mdverz` läuft derselbe Test:'))
    s += lab.sitzung(['mkdir -p leer', cmd('python3 c8205_interp.py --MODUS=TEST --mdverz leer Tests/a.txt'),
                      cmd('python3 c8205_interp.py --MODUS=TEST --mdverz ./markdown-dateien Tests/a.txt')], erwarte=[None, 2, 4])
    s.append(P('**Trommeldatei fehlt.** Der Interpreter legt sie nie selbst an; er meldet es vor dem ersten Test, auch mit '
               '`--NO-TERMOUT`:'))
    s += lab.sitzung(['rm -f virtuelle_Geraete/Trommel/trommel.txt', cmd('python3 c8205_interp.py --MODUS=TEST Tests/a.txt'),
                      cmd('python3 c8205_interp.py --MODUS=TEST --NO-TERMOUT Tests/a.txt')], erwarte=[None, 16, 16])
    s.append(P('**Trommeldatei fehlerhaft.** Hier ist die Datei auf 100 Zeilen gekürzt:'))
    s += lab.sitzung(['python3 erzeuge_leere_trommel.py', 'mkdir -p trommeln',
                      'head -n 100 virtuelle_Geraete/Trommel/trommel.txt > trommeln/kurz.txt',
                      cmd('python3 c8205_interp.py --MODUS=TEST --trommel trommeln/kurz.txt Tests/a.txt')], erwarte=[None, None, None, 16])
    s.append(P('**Trommeldatei mit CRLF-Zeilenenden.** Die Datei wurde nachträglich mit Windows-Zeilenenden versehen:'))
    s += lab.sitzung(['python3 erzeuge_leere_trommel.py --aus trommeln/crlf.txt', "sed -i 's/$/\\r/' trommeln/crlf.txt",
                      cmd('python3 c8205_interp.py --MODUS=TEST --trommel trommeln/crlf.txt Tests/a.txt')], erwarte=[None, None, 16])
    return s


# ------------------------------------------------------------------ Kapitel 8
T_SOLL_SW = '5.\n'


def kap8(lab):
    s = h1('8 Beispiele Schritt für Schritt')
    s.append(P('Alle Beispiele sind lauffähig und mit der auf Seite 2 genannten Version ausgeführt, jeweils nach '
               '`python3 erzeuge_leere_trommel.py`. Legen Sie die Dateien wie angegeben an; die Ordner `Tests/` und `band/` im '
               'Projektordner sind frei wählbar. Die Zahl hinter „Knoten:“ ist fassungsabhängig.'))

    # ---- 8.1
    s += h2('8.1 Ausgabe auf dem Schreibwerk')
    s.append(P('Das Grundbeispiel steht in Abschnitt 2.4: Testdatei `Tests/0015-030.txt`, Aufruf mit dem Wrapper, Ausgabe „Jahr 1972“ '
               'in Dunkelgelb. Verwendet werden die Token `H`, `G`, `M-drücken`, `E`, `M-loslassen`, `R` und die Marken `#DOK`, '
               '`#PROT STUFE=2`. Mit `--sw-ausgabe` erscheint der Text nicht am Terminal, sondern in '
               '`SW-Ausgabe/sw-ausgabe.txt`; mit `--NO-TERMOUT` zusätzlich keine Zeile des Interpreters:'))
    lab.dateien([('Tests/0015-030.txt', T_0015)], neu=True, zeigen=False)
    s += lab.sitzung(['python3 c8205_interp.py --MODUS=TEST --NO-TERMOUT --sw-ausgabe SW-Ausgabe Tests/0015-030.txt',
                      'cat SW-Ausgabe/sw-ausgabe.txt'])
    s.append(P('Die Testdatei kann das Gerät selbst mitbringen und die Ausgabedatei gleich prüfen. `Tests/sw-zeile.txt` (Abschnitt 3.6) '
               'stellt `Um. KB` voran, damit das Ergebnis nicht von der zufälligen Zeichenlage abhängt; danach folgen die Ziffer 5 '
               'und der Punkt. Mit der Zeile `--pruefe-sw-ausgabe sw-soll.txt` im Teil `Prüfungen:` (Soll-Datei neben der '
               'Testdatei, Inhalt `5.`) bewertet der Test die Ausgabe selbst; dasselbe leistet der Schalter beim Aufruf:'))
    s += lab.dateien([('Tests/sw-pruefe.txt', T_SWPRUEFE), ('Tests/sw-soll.txt', T_SOLL_SW)], neu=True)
    lab.schreibe('Tests/sw-zeile.txt', T_SWZEILE)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/sw-pruefe.txt'),
                      cmd('python3 c8205_interp.py --MODUS=TEST --pruefe-sw-ausgabe sw-soll.txt Tests/sw-zeile.txt')], erwarte=[0, 0])
    s.append(P('Mit dem Ausgabefenster (`--SW-TERMINAL`, wahlweise mit `--zwischenablage`) erscheint dieselbe Ausgabe zusätzlich in '
               'einem eigenen Fenster:'))
    s += L.code("""$ python3 c8205_interp.py --MODUS=TEST --SW-TERMINAL Tests/0015-030.txt
$ python3 c8205_interp.py --MODUS=TEST --SW-TERMINAL --zwischenablage system Tests/0015-030.txt""")
    s.append(P('Im Fenster „SW Ausgabe“ steht `Jahr 1972`. Das Terminal zeigt wie zuvor die Zeilen des Interpreters (ohne '
               '`--sw-ausgabe` auch die dunkelgelbe Ausgabe). Mit `--sw-ausgabe virtuelle_Geraete/SW-Ausgabe` geht dieselbe Ausgabe '
               'zusätzlich in die Datei `sw-ausgabe.txt`.'))
    s += note('hinweis', FENSTER_HINWEIS)

    # ---- 8.2
    s += h2('8.2 Alle Bedientasten in einer Tastenfolge')
    s.append(P('Die Tastenfolge `SW=1 SW=0 BS=1 SP=1 H G Ü ST BS=0 SP=0 R` benutzt die Token `SW`, `BS`, `SP`, `H`, `G`, `Ü`, `ST` und '
               '`R`. Das Programm besteht nur aus einem Stopp-Befehl; wichtig ist das Protokoll (Stufe 2), das die Wirkung jedes '
               'Tokens zeigt (Abschnitt 6.4).'))
    s += lab.dateien([('Tests/tf-demo.txt', T_TFDEMO)], neu=True)
    s += lab.sitzung(['python3 c8205_interp.py --MODUS=TEST --out Test-Protokolle/tf-demo.log Tests/tf-demo.txt'], erwarte=[4])
    s.append(P('Das Protokoll zeigt: `ST` wirkt hier, weil `G` zuvor US gesetzt hat (Verriegelung). Durch `Ü` und `ST` steht BR=7777 240 '
               'aufgestellt; `R` startet deshalb bei Knoten 19, führt den Transport aus und hält danach.'))
    s.append(kopf3('Kanaltasten K0 bis K3'))
    s.append(P('Die Kanaltasten stehen nach `G`. Die Tastenfolge `H G M K0 K1 K2 K3` endet im Halt (kein `R`); das Protokoll zeigt, '
               'was jede Taste einstellt. Ein im Programm ausgeführter Anwahlbefehl (`4400`…`4700 030`) übersteuert die Einstellung '
               'später.'))
    s += lab.dateien([('Tests/kanal-demo.txt', T_KANAL)], neu=False)
    s += lab.sitzung(['python3 c8205_interp.py --MODUS=TEST --out Test-Protokolle/kanal-demo.log Tests/kanal-demo.txt',
                      'cat Test-Protokolle/kanal-demo.log'], erwarte=[4, None])

    # ---- 8.3
    s += h2('8.3 Zeichen vom Lochstreifen lesen und auf den Stanzer ausgeben')
    s.append(kopf3('Leser: die Ziffer 5'))
    s.append(P('Programm: `0000: 00004600030` (K1 anwählen), `0001: 00000000011` (Eingabe-Halt mit Löschen), `0002: 00000000020` '
               '(Stopp), dazu die Konstante `0005: 00000000042`. Streifendatei `band/band5.txt` mit einer leeren Zeile (Vorspann) und '
               '`00010101` (die Ziffer 5: Spuren p, 4, 1). Die Eingabeadresse 05 wird mit dem Adressteil 0000 zur Adresse 0005 '
               'verknüpft; der AC erhält den **Inhalt** der Zelle 0005, nicht die Zahl 5.'))
    s += lab.dateien([('Tests/leser-ziffer.txt', T_LESER), ('band/band5.txt', '\n00010101\n')], neu=True)
    lab.schreibe('band/band5i.txt', '\n11111111\n00010101\n')
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST --leser1 band/band5.txt Tests/leser-ziffer.txt')], erwarte=[4])
    s.append(P('Der AC enthält den Inhalt 42 der Zelle 0005. Ohne `--leser1` endet derselbe Test mit der Fehlermeldung aus Kapitel 7. '
               'Steht vor der Ziffer die Zeile `11111111` („Irrung Zeichen“, `band/band5i.txt`), ist das Ergebnis dasselbe: Die Zeile '
               'wird übersprungen.'))
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST --leser1 band/band5i.txt Tests/leser-ziffer.txt')], erwarte=[4])
    s.append(P('Mit dem Zeichen `:` (Zeile `00001101`) und dem Eingabe-Halt `0001: 00000000010` springt das Programm statt zu addieren '
               'nach 0015 (Sprung-Umstellung „ja“). Mit der Anwahl `4500 030` statt `4600 030` und `--leser2` liest derselbe Test '
               'von Leser 2:'))
    lab.dateien([('Tests/leser2-ziffer.txt', T_LESER2)], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST --leser2 band/band5.txt Tests/leser2-ziffer.txt')], erwarte=[4])

    s.append(kopf3('Stanzer: Zeichen 5 und Punkt'))
    s.append(P('Programm: `0000: 00004600030` (K1 anwählen), `0001: 00000250030` (Ausgabe der Ziffer 5, Ausgabe-Adresse `025x`), '
               '`0002: 00000730030` (Ausgabe des Punktes, `073x`), `0003: 00000000020`.'))
    lab.dateien([('Tests/stanzer-zeichen.txt', T_STANZER)], neu=False, zeigen=False)
    s += lab.sitzung(['python3 c8205_interp.py --MODUS=TEST --stanzer1 out/band.txt Tests/stanzer-zeichen.txt', 'cat out/band.txt'],
                     erwarte=[4, None])
    s.append(P('Die Datei `out/band.txt` enthält die Zeilen `00010101` und `00111011`. Der Ordner `out/` muss nicht existieren; er '
               'wird angelegt. Ohne `--stanzer1` endet der Test mit der roten Fehlermeldung aus Kapitel 7.'))
    s.append(kopf3('Stanzer-Datei gegen eine Soll-Datei prüfen'))
    s.append(P('Soll der Test die gestanzte Datei selbst bewerten, steht die Dateiprüfung im Teil `Prüfungen:` (Abschnitt 3.4). Die '
               'Testdatei bringt Gerät und Prüfung mit; die Soll-Datei `soll.txt` liegt neben der Testdatei und enthält die Zeilen '
               '`00010101` und `00111011`:'))
    s += lab.dateien([('Tests/stanzer-pruefe.txt', T_STANZER_PR), ('Tests/soll.txt', SOLL)], neu=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/stanzer-pruefe.txt')], erwarte=[0])
    s.append(P('Abweichender Inhalt, fehlende Soll-Datei oder fehlende Ist-Datei ergibt `Test falsch` (Rückkehrcode 6; Beispiel mit '
               '`diff` in Abschnitt 6.5). Für die Schreibwerk-Datei gilt dasselbe mit `--sw-ausgabe` und `--pruefe-sw-ausgabe` '
               '(Abschnitt 8.1).'))
    s.append(kopf3('K0: Eingabe aus einer Datei'))
    s.append(P('Programm: `0000: 00004700030` (K0 anwählen), `0001: 00000000011` (Eingabe-Halt mit Löschen), `0002: 00000000020`, dazu '
               'die Konstante `0007: 00000000007`. Die Datei `band/k0.txt` enthält eine Zeile `7`.'))
    lab.dateien([('Tests/k0-ziffer.txt', T_K0), ('band/k0.txt', '7\n')], neu=False, zeigen=False)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST --k0 datei=band/k0.txt Tests/k0-ziffer.txt')], erwarte=[4])
    s.append(P('Der AC enthält den Inhalt der Zelle 0007. Mit `SW=1` vor `G` (Schreibwerk statt Tastatur) ist auch das Zeichen `B` '
               'eingebbar; an der Pult-Tastatur nicht (Kapitel 7).'))

    # ---- 8.4
    s += h2('8.4 Diagnose, Speicherauszug und Prüfungen')
    s.append(P('Verkürzter Gruppen-Transport mit Rechtsverschiebung (Test `s1-R1`): Der AC startet mit 6; der Befehl `4001 542` '
               'überträgt ihn in die Spur 40xx, solange der AC nicht negativ wird. Der Leerbefehl 164 (Adresse 0020) löst die '
               'Diagnose mit `#SPEI-0020 4000-4037` aus.'))
    s += lab.dateien([('Tests/s1-R1.txt', T_S1R1)], neu=True)
    s += note('achtung', 'Der Leerbefehl steht in Zelle 0010, nicht in 0002. Nach einem X-Abbruch (verkürzte Gruppen-/Wiederholungsbefehle '
                         'mit B = 5 oder 7) holt der Rechner den nächsten Befehl ohne Wartezeit aus dem Sektor, der gerade unter dem '
                         'Kopf liegt: Die Spur kommt aus dem Befehlszähler (hier Spur 00), der Sektor ist der Sektor der letzten '
                         'bearbeiteten Zelle plus zwei Wortzeiten (hier 4016: Sektor 16 + 32 = 50, modulo 40 = 10, oktal). Der Befehl '
                         'muss also nicht in Zelle b+1 stehen. Steht er dort, findet der Interpreter in 0010 den Wert 0, also den '
                         'Sprung nach 0000, und das Programm läuft endlos. Danach läuft das Programm bei 0003 weiter.')
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/s1-R1.txt')], erwarte=[4],
                     kuerze=[('4003: ', '4015: ', '… (4003 bis 4015: jeweils 00000000000) …', r': 00000000000$'),
                             ('4020: ', '4037: ', '… (4020 bis 4037: jeweils 00000000000) …', r': 00000000000$')],
                     caption='Speicherzeilen gekürzt (die Adressen laufen oktal).')
    s.append(P('Es werden zwei Zellen geschrieben. In Zelle 4001 landet der AC (6); danach schiebt die Resultatbehandlung ihn nach '
               'rechts (AC = 3). Bei R = 1 gilt z₃₂ als Vorzeichen: z₃₂ = 1, der AC zählt also als „negativ“ (X-Bedingung). '
               'Operation und Resultatbehandlung werden noch mit einer weiteren Zelle ausgeführt (4016 := 3, AC danach 1), danach '
               'bricht der Befehl ab.'))
    s.append(P('Test mit Prüfungen: Der folgende Test lädt eine Zahl, addiert eine zweite und prüft Register, Flags und zwei '
               'Speicherzellen (ein Beispiel mit `Test falsch` steht in Abschnitt 6.5):'))
    s += lab.dateien([('Tests/pruef-wahr.txt', T_PWAHR)], neu=True)
    s += lab.sitzung([cmd('python3 c8205_interp.py --MODUS=TEST Tests/pruef-wahr.txt')], erwarte=[0])
    s.append(P('Rückkehrcode 0 (`Test wahr`). Dieselbe Testdatei ohne Prüfungen ergäbe 4.'))

    # ---- 8.5
    s += h2('8.5 Trommel über mehrere Tests und eigene Trommeldatei')
    s.append(P('`trommel-b` schreibt Zelle 3000 nicht, prüft sie aber auf 100; `trommel-a` schreibt dort 100 und hält. Auf leerer '
               'Trommel ist `trommel-b` falsch (Rückkehrcode 6); nach `trommel-a` ist es wahr; beide Tests in einem Aufruf ergeben '
               'dasselbe. Eine zweite, leere Trommel liegt unter `trommeln/leer.txt` und wird mit `--trommel` gewählt; mit dem Pfad '
               'der Standard-Trommel ergibt `--trommel` dasselbe wie der Aufruf ohne den Schalter.'))
    s += lab.dateien([('Tests/trommel-a.txt', T_TROMMEL_A), ('Tests/trommel-b.txt', T_TROMMEL_B)], neu=True)
    PY = 'python3 c8205_interp.py --MODUS=TEST'
    s += lab.sitzung(['python3 erzeuge_leere_trommel.py', cmd(PY + ' Tests/trommel-b.txt'), cmd(PY + ' Tests/trommel-a.txt'),
                      cmd(PY + ' Tests/trommel-b.txt'), 'python3 erzeuge_leere_trommel.py',
                      cmd(PY + ' Tests/trommel-a.txt Tests/trommel-b.txt'),
                      'python3 erzeuge_leere_trommel.py --aus trommeln/leer.txt',
                      cmd(PY + ' --trommel trommeln/leer.txt Tests/trommel-b.txt'),
                      cmd(PY + ' --trommel virtuelle_Geraete/Trommel/trommel.txt Tests/trommel-b.txt')],
                     erwarte=[None, 6, 4, 0, None, 0, None, 6, 0])
    s.append(P('Die letzte Zeile zeigt: `--trommel` mit dem Pfad der Standard-Trommel ergibt dasselbe wie der Aufruf ohne den '
               'Schalter. Der Wrapper übergibt `--trommel` nicht; eine andere Trommel steht hinter der Testdatei: '
               '`./c8205_interpreter.sh Tests/x.txt --trommel andere/trommel.txt` (Abschnitt 4.3).'))
    return s


# ------------------------------------------------------------------ Kapitel 9: Kurzreferenz (eine Seite, einzeln druckbar)
def kap9():
    s = [PageBreak(), Marke('kurz_anfang')]
    s += h1('9 Kurzreferenz')
    s += L.code("""python3 c8205_interp.py --MODUS=TEST [Schalter] TEST.txt [TEST2.txt ...]
./c8205_interpreter.sh TEST.txt [Schalter]       # Protokoll nach Test-Protokolle/TEST.log""")
    s += tbl([['Schalter', 'Wirkung (Standard)'],
              ['`--trommel P`', 'Trommeldatei, bleibt über Tests und Aufrufe erhalten (`virtuelle_Geraete/Trommel/trommel.txt`); '
                                'leer erzeugen: `python3 erzeuge_leere_trommel.py [--aus PFAD]`'],
              ['`--mdverz V` · `--out V|F.log`', 'Regelwerk-Ordner (`markdown-dateien/`) · Protokoll in Ordner `V/<Test>/protokoll.txt` '
                                                 'oder Datei `F.log` (nur 1 Test); `Test-Protokolle/`'],
              ['`--leser1 P` `--leser2 P` `--stanzer1 P`', 'Streifen (Datei/Ordner) für K1/K2 · Stanzerdatei K1; Zeilen `0`/`1` für '
                                                           'w v u p 8 4 2 1'],
              ['`--sw-ausgabe P` · `--k0 datei=P`', 'Schreibwerk (K2) in `P/sw-ausgabe.txt` statt ans Terminal · K0-Eingabe aus Datei '
                                                    'statt vom Terminal. Alle fünf Geräteschalter auch als Zeile der Testdatei'],
              ['`--pruefe-stanzer1 D` `--pruefe-sw-ausgabe D`', 'Ist- gegen Soll-Datei D vergleichen (setzt das Gerät voraus; nur 1 '
                                                                'Test); auch als Zeile in `Prüfungen:`'],
              ['`--knotentest` · `--NO-TERMOUT`', 'Knotenzeilen `Kxxx` ins Protokoll (aus) · Ausgaben des Interpreters am Terminal '
                                                  'unterdrücken, Groß-/Kleinschreibung beachten (aus)'],
              ['`--SW-TERMINAL` · `--zwischenablage M`', 'Ausgabefenster „SW Ausgabe“ (aus; nur Kommandozeile) · Kopierverfahren '
                                                         '`auto`, `tk`, `system` (`auto`)'],
              ['`--version` · `-h`', 'Version `y.xx-zzz` ausgeben · Hilfetext']],
             [0.30, 0.70])
    s += note('hinweis', FENSTER_HINWEIS)
    s += tbl([['Marke, Token, Kanal', 'Wirkung'],
              ['`#DOK-xxxx T` `#SPEI-xxxx s-e` `#SPUR-xxxx a`', 'bei Befehl 164 mit Adresse `xxxx`: Text · Speicher `s`…`e` · ganze '
                                                                'Spur von `a`'],
              ['`#PROT STUFE=n` · `#AC=` · `#BZ=`', '0 kein, 1 Bildschirm (Standard), 2 Datei · Anfangswerte AC (11 Stellen), BZ (4)'],
              ['`#STARTE n` · `#INTERRUPT H …`', '`H G M+ E … E M- R` (n-mal `E`), ersetzt die Tastenfolge · Unterbrechung nach der '
                                                 'Zeile davor, `R`/`ST` setzt fort'],
              ['`H` `R` `G`', 'Halt · Rechnen (H := 0, US := 0, Start) · Generallöschen, danach US := 1, K0; `SW=1` vorher setzen'],
              ['`M+` `M-` `M` `E`', 'M halten/loslassen/antippen (OR ∨ 025); `R` nach `M` mit Sprung mit Rückkehrabsicht: Knoten 54 · '
                                    '`E` Einzelschritt, unter M: BZ + 1'],
              ['`Ü` `ST` `SW=1/0` `BS=1/0` `SP=1/0`', 'AR := 7777, OR ∨ 240 (nur bei H) · OR ∨ 240, US := 0 (nur bei US/BS) · '
                                                       'Schreibwerk/Tastatur · einrastende Schalter'],
              ['`K0` … `K3` · Anwahl `4700` … `4400` + `030`', 'Kanaltaste (nach `G`), im Programm übersteuert. K0 Tastatur (T)/Schreibwerk (SW), '
                                                                'keine Ausgabe · K1 Leser 1/Stanzer 1 · K2 Leser 2/Schreibwerk '
                                                                '(dunkelgelb) · K3 frei (Stub)'],
              ['`Trommeldatei:`', 'Zeilen `aaaa: wwwwwwwwwww [# …]`, Testmarken, Geräte-Zeilen; nicht genannte Zellen behalten ihren '
                                  'Inhalt'],
              ['`Tastenfolge:` · `Prüfungen:`', 'Token, Ende mit `R` oder im Halt · optional: `BZ=… AC=… FE=…`, Zeilen `aaaa: w…`, '
                                                '`--pruefe-…`'],
              ['Endzeile · Rückkehrcode', '`Ende: Grund | Knoten: n | BZ AC AR | FE FUE BS US E A V1 V2` · 0 wahr, 4 ohne Prüfung, '
                                          '6 falsch, 8 Laufzeitfehler, 16 Vorab-Fehler, 2 ungültiger Aufruf']],
             [0.34, 0.66])
    s.append(Marke('kurz_ende'))
    return s


# ------------------------------------------------------------------ Anhänge
def anhang_a():
    s = [PageBreak(), Marke('anhang_a')]
    s += h1('Anhang A: Glossar')
    s += tbl([['Begriff', 'Erklärung'],
              ['Akkumulator (AC)', 'Rechenregister (33 Bit); einziger Weg zum Abspeichern in die Trommel'],
              ['Befehlszähler (BZ)', 'Register (12 Bit) mit der Adresse des nächsten Befehls'],
              ['Adressregister (AR)', 'Register (12 Bit), wählt die Trommelzelle für jeden Zugriff'],
              ['Operationsregister (OR)', 'Register (9 Bit) mit dem Operationsteil des aktuellen Befehls (BAZ)'],
              ['Befehlsregister (BR)', 'Adreßteil (12 Bit) und OR (9 Bit); im Protokoll `BR=aaaa ooo`'],
              ['Flag', 'Speicher für 0 oder 1 (E, A, T, SW, K1–K3, FE, FÜ, BS, US, V1, V2, H, SP); eine Lampe zeigt ihn, ein Schalter '
                       'kann ihn setzen'],
              ['Trommel', 'Magnettrommelspeicher: 4096 Zellen à 33 Bit. Im Interpreter eine persistente Textdatei (`trommel.txt`, '
                          '4096 Zeilen); ihr Inhalt bleibt über Tests und Aufrufe erhalten'],
              ['Trommeldatei', 'die Datei `trommel.txt` (bzw. der Pfad von `--trommel`): der Speicher des Interpreters. Nicht zu '
                               'verwechseln mit dem Teil `Trommeldatei:` einer Testdatei'],
              ['Trommelabschnitt', 'der Teil `Trommeldatei:` einer Testdatei: die Zellen, die der Test vor dem Start auf die Trommel '
                                   'schreibt'],
              ['Sektor / Bahn (Spur)', '32 Sektoren je Bahn; 128 Bahnen. Eine Adresse besteht aus Bahn (7 Bit) und Sektor (5 Bit)'],
              ['Oktal', 'Zahlen zur Basis 8 (Ziffern 0–7); alle Zahlen in Testdateien'],
              ['Knoten, Konnektor', 'Elemente des Knotengraphen (Anweisung, Test, Phasenzuordnung, Konnektor); der Interpreter läuft ihn ab'],
              ['Phase I bis IV', 'die vier Abschnitte eines Befehlszyklus: Zähleraufstellung, Befehlsentnahme, Adressaufstellung, '
                                 'Ausführung'],
              ['ANWEISUNG-nnn', 'Beschreibung eines Knotens in Tabelle T2; im Interpreter eine eigene Funktion'],
              ['Stub', 'Meldung „an dieser Stelle fehlt eine Umsetzung“ bzw. „außerhalb des definierten Betriebs“; der Test hält an'],
              ['Testmarke', 'Zeile mit `#`, die nur der Testdurchführung dient (`#DOK`, `#SPEI`, `#SPUR`, `#PROT`, `#AC`, `#BZ`, '
                            '`#STARTE`, `#INTERRUPT`)'],
              ['Makro `#STARTE`', 'Kurzschreibweise für die Tastenfolge zum Ansprung eines Speicherplatzes (`H G M+ E … E M- R`)'],
              ['Unterbrechung (`#INTERRUPT`)', 'Eingriff des Bedieners mitten im Programm: weitere Tasten nach dem Befehl der Zeile davor'],
              ['Ausgabefenster „SW Ausgabe“', 'Textfenster, das `--SW-TERMINAL` öffnet; zeigt Schreibwerk-Ausgabe und K0-Echo'],
              ['Zeichenlage KB/GB', 'Klein-/Großbuchstaben-Lage; beim Schreibwerk zufällig gesetzt, umgeschaltet durch '
                                    'Umschaltzeichen'],
              ['Kanal K0 bis K3', 'Anwahl der Ein-/Ausgabegeräte (Tabelle in Kapitel 5)'],
              ['T / SW', 'Subflags für K0: Pult-Tastatur bzw. Schreibwerk statt Tastatur (alternativ)'],
              ['Sprung-Umstellung', 'Eigenschaft eines Zeichens der Kodetabelle: Der Eingabebefehl wird in einen Sprung umgestellt '
                                    '(z. B. `:`, `.`)'],
              ['Irrung Zeichen', 'Lochbild `11111111` (alle acht Spuren); am Leser von der Paritätsprüfung ausgenommen und übersprungen'],
              ['Tastenfolge', 'die Bedienhandlungen am Pult, die den Ausgangszustand festlegen'],
              ['Dateiprüfung', 'Vergleich der vom Lauf erzeugten Stanzer- bzw. Schreibwerk-Datei mit einer Soll-Datei (`--pruefe-…`)'],
              ['Rückkehrcode', 'Zahl, die der Interpreter dem Betriebssystem liefert (0, 2, 4, 6, 8, 16; Abschnitt 4.4)'],
              ['Wortzeit', 'Zeit, in der ein Wort unter dem Kopf durchläuft (104 µs); im Interpreter 0']],
             [0.27, 0.73], first_bold=True)
    return s


def anhang_b(protokollkopf_alt):
    s = h1('Anhang B: Grenzen des Interpreters')
    items = [
        'Zeiten sind 0: Es gibt keine Wartezeiten und keine Zeitmessung; die Pufferung der Ausgabe (1-Zeichen-Puffer) wird nicht '
        'nachgebildet.',
        'Kanal K3 wird nicht benutzt (Festlegung des Autors); Programme auf K3 und ein Ausgabe-Halt ohne Ausgabegerät liegen '
        'außerhalb des definierten Betriebs und enden mit einem Stub.',
        'Die Schreibwerk-Ausgabe geht ohne `--sw-ausgabe` an das Terminal, mit dem Schalter in die Datei `sw-ausgabe.txt`; mit '
        '`--SW-TERMINAL` zusätzlich in ein Fenster. Ein Warten auf den Schalter SW findet nicht statt. Die Stanzer-Ausgabe '
        'entspricht dem Regelwerk (eine 0/1-Zeile je Zeichen); den Dateinamen bestimmen Sie mit `--stanzer1`. Der Stanzer hat keine '
        'Terminal-Ausgabe.',
        'Das Ausgabefenster braucht `tkinter` und eine grafische Oberfläche; es läuft als eigener Prozess und schließt sich nie von '
        'selbst. Jeder Aufruf mit `--SW-TERMINAL` öffnet ein neues Fenster.',
        'Die früheren Schalter `--k0 tastatur` und `--leser-ende` gibt es nicht mehr: Ohne `--k0` wird vom Terminal gelesen, Leser '
        'und `--k0 datei=` warten am Ende still auf eine neue Datei.',
        'Ein Transportloch außerhalb des Vorspanns (nach dem Original der Paritätsprüfung unterworfen) ist im Streifenformat nicht '
        'darstellbar und nicht umgesetzt; die Auslegung steht noch aus.',
        'Der Rückkehrcode bezieht sich auf genau einen Test, bei mehreren Testdateien auf den zuletzt bearbeiteten.',
        'Die Trommel wird nie zurückgesetzt; Tests sind nur dann voneinander unabhängig, wenn sie ihre Zellen selbst nennen oder die '
        'Trommel vorher neu erzeugt wird (Abschnitt 3.7). Es gibt keine Sperre gegen gleichzeitige Läufe auf derselben Trommeldatei.',
        'Nach einem X-Abbruch (B = 5 oder 7) steht der Folgebefehl nicht in Zelle b+1, sondern im Sektor, der zeitlich fällig ist '
        '(Abschnitt 8.4); Tests mit Folgebefehl in b+1 laufen sonst in eine Endlosschleife.',
        '`B` und `D` (Pult-Tasten) haben keinen Code. `WM` = Tabulator (Eingabe-Adresse 075), `IB` = Eingabe-Adresse 036; die '
        'Tabellenzeile 52 („Transport“) wird nicht benutzt.',
        'Der Interpreter ist wortlautgetreu nach dem Knotengraphen: ANWEISUNG-001 gilt in Phase I und III; die Resultatbehandlung '
        'gilt für jeden Befehl außer den Leer-Befehlen 164/166; bei B = 5 und 7 entscheidet bei R ≠ 1 das Bit z₀, bei R = 1 das '
        'Bit z₃₂ über den X-Abbruch.',
        'Die Kopfzeile `Prüfungen: False` (Negativtests, Quelle „Durchführung eines Tests“, Abschnitt 3a.5) wertet diese Fassung '
        'nicht aus (Abschnitt 3.4).']
    if protokollkopf_alt:
        items.insert(8, 'Im Protokoll (Abschnitt 1) trägt die Kopfzeile noch den Text „nicht genannte Zellen = 0“ aus der Zeit vor der '
                        'persistenten Trommel; das Protokoll zeigt nur die Zellen des Trommelabschnitts (Abschnitt 6.4).')
    s += bullets(items)
    return s


def anhang_c():
    s = h1('Anhang C: Verweise auf das Regelwerk')
    s += tbl([['Thema', 'Dokument'],
              ['Rechner, Phasen, Register, Trommel', 'PDF „Rechnerbeschreibung“ (Quellen: Überblick_und_Gesamtaufbau, '
                                                     'Datenstruktur…, Magnettrommel)'],
              ['Tasten, Schalter, Kanäle, Leser, Stanzer, Schreibwerk', 'PDF „Bedienpult und Peripherie“ (Quellen: '
                                                                       'Bedienpult_mit_Schaltern, Lochstreifenleser)'],
              ['Befehle und Formeln', 'PDF „Einzelbefehlsliste“ (Quelle: Befehlsliste.md)'],
              ['Zeichenkodes, Tabelle 1', 'PDF „Kodetabellen“'],
              ['Knotengraph und Variablentabelle T2', 'PDF „Knotengraph“ und „Knotentabellen“; Quellen Eingänge_der_Knoten.md, '
                                                      'Beschreibung_der_Knoten.md'],
              ['Tests schreiben, Beispiele, Protokolle lesen', 'PDF „Testhandbuch“'],
              ['Testdefinition, Testdatei und Protokoll im Wortlaut', 'PDF „Durchführung eines Tests“ (Quelle: '
                                                                      'Durchführung_eines_Tests.md)'],
              ['Assembler `c82ass` (erzeugt die `.test`-Dateien)', 'PDF „Assemblerdokumentation“'],
              ['Lochstreifen erzeugen, anzeigen und umwandeln (für `--leser1`, `--leser2`)', 'PDF „Lochstreifen-Hilfsprogramme“'],
              ['Orientierung für neue Leser, Lesereihenfolge der Dokumente', 'PDF „Einstieg für Neueinsteiger“'],
              ['Gesamtüberblick des Projekts', 'PDF „Projektüberblick“'],
              ['Cache der BAZ-Wirkungen', '`baz-wirkungstabelle.md` (vom Python-Interpreter nicht gelesen)']], [0.45, 0.55])
    return s


# ------------------------------------------------------------------ Seitenmarken (Prüfung: Kurzreferenz = genau eine Seite)
from reportlab.platypus import Flowable

SEITEN = {}


class Marke(Flowable):
    """Unsichtbare Marke; merkt sich die Seite, auf der sie gesetzt wird (letzter Durchlauf von multiBuild zählt)."""

    def __init__(self, name):
        Flowable.__init__(self)
        self.name = name
        self.width = self.height = 0

    def wrap(self, aw, ah):
        return 0, 0

    def draw(self):
        SEITEN[self.name] = self.canv.getPageNumber()


# ------------------------------------------------------------------ Abnahme (Python_Interpreter.md 14.4)
def _norm(t):
    t = t.lower().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    return re.sub(r'[^a-z0-9]', '', t)


def pdf_text(pdf):
    try:
        return subprocess.run(['pdftotext', '-raw', pdf, '-'], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        from pypdf import PdfReader
        return '\n'.join(p.extract_text() or '' for p in PdfReader(pdf).pages)


def abnahme(lab, pdf, md_pfad):
    """Prüft das fertige PDF gegen die Abnahmeregeln; Fehler -> Rückgabe False, Hinweise werden gedruckt."""
    text = pdf_text(pdf)
    flach = ' '.join(text.split())
    nt = _norm(text)
    fehler, warn = [], []
    # 1. jeder Schalter aus --help kommt vor
    hilfe, _ = lab.ausgabe('python3 c8205_interp.py --help')
    schalter = sorted(set(re.findall(r'(?<![\w-])(--[A-Za-z][\w-]*)', hilfe)))
    fehlt = [x for x in schalter if x not in flach]
    if fehlt:
        fehler.append('Schalter aus --help fehlen im PDF: %s' % ', '.join(fehlt))
    if '-h' not in flach:
        fehler.append('Schalter -h fehlt')
    # 2. Marken, Token und Meldungen, die in jedem Fall vorkommen müssen
    muss = ['#STARTE', '#INTERRUPT', '#AC=', '#BZ=', '#DOK', '#SPEI', '#SPUR', '#PROT', 'M-drücken', 'M-loslassen',
            'M-gedrückt-halten', 'BS=1', 'BS=0', 'SP=1', 'SP=0', 'SW=1', 'SW=0', 'K0', 'K3', 'EINGABE_ENDE',
            'Kopieren fehlgeschlagen', 'Rückkehrcode', 'INTERP_VERSION']
    muss.remove('INTERP_VERSION')
    muss.append(INTERP_VERSION)
    fehlt = [x for x in muss if x not in flach]
    if fehlt:
        fehler.append('Pflichtbegriffe fehlen: %s' % ', '.join(fehlt))
    # 3. jede Meldung aus Abschnitt 10 der Quelle steht im Fehlerverzeichnis
    with open(md_pfad, encoding='utf-8') as f:
        md = f.read()
    a = md.index('## 10.')
    b = md.index('## 11.')
    for zeile in md[a:b].splitlines():
        if not zeile.startswith('| ') or zeile.startswith('| Meldung') or zeile.startswith('|---'):
            continue
        zelle = zeile.split(' | ')[0].lstrip('| ').strip()
        teile = re.findall(r'`([^`]+)`', zelle) or [zelle]
        kern = _norm(teile[0].replace('…', ''))[:18]
        if kern and kern not in nt:
            warn.append('Meldung aus Abschnitt 10 nicht gefunden: %s' % teile[0])
    # 4. Kurzreferenz steht auf genau einer Seite und ist einzeln druckbar
    k0, k1, an = SEITEN.get('kurz_anfang'), SEITEN.get('kurz_ende'), SEITEN.get('anhang_a')
    if not (k0 and k1 and an) or k0 != k1 or an != k1 + 1:
        fehler.append('Kurzreferenz ist nicht genau eine eigene Seite (Anfang %s, Ende %s, Anhang A ab %s)' % (k0, k1, an))
    for w in warn:
        print('ABNAHME (Hinweis):', w)
    for e in fehler:
        print('ABNAHME (FEHLER):', e)
    if not fehler:
        print('ABNAHME ok: %d Schalter, %d Pflichtbegriffe, Kurzreferenz auf Seite %s' % (len(schalter), len(muss), k0))
    return not fehler


def kopf3_binden(story):
    """Eine Einleitungszeile (kopf3) bleibt mit dem folgenden, zusammenhängenden Block (Absatz + kurzer Codeblock) auf einer
    Seite; reportlab verschachtelt KeepTogether-Blöcke nicht zuverlässig, deshalb wird zu einem flachen Block zusammengefasst."""
    out = []
    for fl in story:
        if out and isinstance(fl, KeepTogether) and isinstance(out[-1], Paragraph) and out[-1].style.name == 'kopf3':
            kopf = out.pop()
            kt = KeepTogether([kopf] + list(fl._content))
            kt._isCode = False
            out.append(kt)
        else:
            out.append(fl)
    return out


def kopf_nicht_einsam(story):
    """Eine Überschrift, auf die ein mit dem Folgenden verbundener Absatz (z. B. vor langem Codeblock) folgt, braucht Platz
    für Überschrift, Absatz und die ersten Codezeilen; sonst bleibt sie allein am Seitenende stehen."""
    for i in range(1, len(story) - 1):
        if isinstance(story[i], L.Head) and isinstance(story[i - 1], CondPageBreak):
            nxt = story[i + 1]
            if isinstance(nxt, Paragraph) and getattr(nxt, 'keepWithNext', 0):
                story[i - 1] = CondPageBreak(max(150, story[i - 1].height))
    return story


# ------------------------------------------------------------------ Hauptprogramm
def finde_wurzel(start):
    """Projektordner: erster Ordner über dem Skript mit c8205_interp.py und markdown-dateien/."""
    d = start
    while True:
        if os.path.isfile(os.path.join(d, 'c8205_interp.py')) and os.path.isdir(os.path.join(d, 'markdown-dateien')):
            return d
        p = os.path.dirname(d)
        if p == d:
            sys.exit('Projektordner (mit c8205_interp.py und markdown-dateien/) oberhalb von %s nicht gefunden '
                     '(Schalter --wurzel verwenden).' % start)
        d = p


def main():
    global INTERP_VERSION
    ap = argparse.ArgumentParser(description='Erzeugt ' + PDF_NAME)
    ap.add_argument('ziel', nargs='?', default=None, help='Vorgabe: PDF/' + PDF_NAME)
    ap.add_argument('--stand', default=L.heute(), help='TT.MM.JJJJ; Vorgabe: Erzeugungsdatum')
    ap.add_argument('--wurzel', default=None, help='Projektordner; Vorgabe: oberhalb dieses Skripts gesucht')
    ap.add_argument('--behalte-labor', action='store_true', help='Arbeitsordner der Beispiele nicht löschen (zur Kontrolle)')
    ap.add_argument('--ohne-abnahme', action='store_true', help='Abnahmeprüfung am Ende überspringen')
    a = ap.parse_args()
    wurzel = os.path.abspath(a.wurzel) if a.wurzel else finde_wurzel(HIER)
    mddir = os.path.join(wurzel, 'markdown-dateien')
    out = a.ziel or os.path.join(wurzel, 'PDF', PDF_NAME)
    set_stand(a.stand)
    quellen = [(n, L.lese_version(finde_datei(mddir, n))) for n in QUELLEN]      # bricht ab, wenn eine Versionszeile fehlt
    lab = Labor(wurzel)
    try:
        v, rc = lab.ausgabe('python3 c8205_interp.py --version')
        m = re.search(r'c8205_interp\.py\s+(\d+\.\d+-\d+)', v)
        if rc != 0 or not m:
            sys.exit('FEHLER: Version des Interpreters nicht lesbar: %s' % v)
        INTERP_VERSION = m.group(1)
        print('Interpreter %s; Quellen: %s' % (INTERP_VERSION, ', '.join('%s %s' % q for q in quellen)))
        L.COVER = dict(titel=TITEL, untertitel=UNTERTITEL, art=ART, bereich=BEREICH, quellen=quellen, stand=a.stand,
                       pdf_name=os.path.basename(out), erzeugt_mit=os.path.basename(__file__), beschreibung=BESCHREIBUNG)
        story = [Spacer(1, 1), PageBreak()]                        # Seite 1: Deckblatt (vom Canvas gezeichnet)
        story += lesehinweise()                                    # Seite 2 und 3
        for teil in (kap1(), kap2(lab), kap3(lab), kap4(lab), kap5(lab), kap6(lab), kap7(lab), kap8(lab), kap9(),
                     anhang_a(), anhang_b(PROTOKOLLKOPF_ALT), anhang_c()):
            story += teil
        print('Beispiele ausgeführt: %d Läufe' % lab.lauefe)
        while story and isinstance(story[-1], Spacer):      # Abstand hinter der letzten Tabelle würde eine leere Seite erzeugen
            story.pop()
        st = kopf_nicht_einsam(head_with_block(kopf3_binden(merge_intro(story))))
        d = L.Doc(out)
        d.title = TITEL
        d.author = 'C8205-Interpreter-Projekt'
        d.subject = '%s · Quellen: %s · Interpreter %s' % (ART.capitalize(), ', '.join('%s %s' % q for q in quellen),
                                                           INTERP_VERSION)
        d.multiBuild(st, canvasmaker=L.NumberedCanvas)
        print('geschrieben:', out)
        ok = True if a.ohne_abnahme else abnahme(lab, out, finde_datei(mddir, QUELLEN[0]))
    finally:
        if a.behalte_labor:
            print('Arbeitsordner der Beispiele:', lab.dir)
        else:
            lab.aufraeumen()
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
