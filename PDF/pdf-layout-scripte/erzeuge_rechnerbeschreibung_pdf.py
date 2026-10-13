# -*- coding: utf-8 -*-
"""erzeuge_rechnerbeschreibung_pdf.py -- erzeugt C8205-Rechnerbeschreibung_A4.pdf (redaktionell, nach
C8205-Interpreter-PDF.md; Bausteine aus pdflib.py).

Aufruf:  python3 erzeuge_rechnerbeschreibung_pdf.py [ZIEL.pdf] [--stand TT.MM.JJJJ] [--md ORDNER_MIT_DEN_QUELLEN]
Seite 1 ist das Deckblatt (PDF.md Abschnitt 4), Seite 2 enthaelt Lesehinweise und Inhaltsverzeichnis (4.4).
Vorgabe: PDF/C8205-Rechnerbeschreibung_A4.pdf in der Projektwurzel
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
import sys

import pdflib as L
from pdflib import (ST, P, bullets, h1, h2, note, fmt, figure, FRAME_W, M, W, H, INK, MUTED, RULE, BLUE,
                    BLUE_BG, ORANGE, ORANGE_BG, HEAD_BG, make_toc, merge_intro, head_with_block)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak

ABGLEICH_INTERP = '08.10.2026'      # Datum des letzten Abgleichs der Annahmen in Kapitel 9 mit c8205_interp.py
ABB_DIR = ['.']          # Ordner der Abbildungen (<md-Ordner>/abbildungen), main() setzt ihn

QUELLEN = ['C8205-Interpreter-Überblick_und_Gesamtaufbau.md',
           'C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md',
           'C8205-Interpreter-Magnettrommel.md',
           'C8205-Interpreter-Befehlsliste.md',
           'C8205-Interpreter-Eingänge_der_Knoten.md']
STAND = L.heute()


def set_stand(stand):
    """Stand = Erzeugungsdatum (PDF.md 4.3); gleicher Wert auf Deckblatt und in der Fusszeile."""
    global STAND
    STAND = stand
    L.STAND = stand
    L.FOOTER_LEFT = 'C8205-Interpreter-Projekt · Stand ' + stand


set_stand(STAND)
L.HEADER_TITLE = 'C 8205 – Rechnerbeschreibung'
L.HEADER_LEGEND = 'Zahlen oktal, sofern nicht anders vermerkt · ⟨x⟩ = Inhalt von x · z₀ … z₃₂ = Bitstellen des Maschinenwortes'

GREY_BG = colors.HexColor('#F0F0F0')
SEL = colors.HexColor('#FFE5B4')


# ------------------------------------------------------------------ Tabellen (dunkler Kopf, kein Zebra; PDF.md 3a.3)
def tbl(rows, fr, first_bold=False, code_cols=(), fs=8.5, center_cols=(), keep=True):
    cell = ParagraphStyle('c', parent=ST['cell'], fontSize=fs, leading=fs * 1.27)
    cellc = ParagraphStyle('cc', parent=cell, alignment=1)
    cellh = ParagraphStyle('ch', parent=ST['cellh'], fontSize=fs, leading=fs * 1.27)
    data = []
    for r, row in enumerate(rows):
        line = []
        for c, v in enumerate(row):
            if r == 0:
                line.append(Paragraph(fmt(v), cellh))
            else:
                t = fmt('`%s`' % v) if (c in code_cols and v and '`' not in v) else fmt(v)
                if first_bold and c == 0:
                    t = '<b>%s</b>' % t
                line.append(Paragraph(t, cellc if c in center_cols else cell))
        data.append(line)
    widths = [f * FRAME_W for f in fr]
    t = Table(data, colWidths=widths, repeatRows=1)
    sty = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('LEFTPADDING', (0, 0), (-1, -1), 4.5), ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
           ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
           ('LINEBELOW', (0, 0), (-1, -1), 0.4, RULE), ('BOX', (0, 0), (-1, -1), 0.5, RULE),
           ('BACKGROUND', (0, 0), (-1, 0), HEAD_BG)]
    if len(rows) >= 3:
        sty.append(('NOSPLIT', (0, len(rows) - 2), (-1, len(rows) - 1)))
    t.setStyle(TableStyle(sty))
    _w, h = t.wrap(FRAME_W, 2000)
    if keep and len(rows) <= 12 and h <= 230:
        return [KeepTogether([t]), Spacer(1, 7)]
    return [t, Spacer(1, 7)]


# ------------------------------------------------------------------ Abbildungen
def box(d, x, y, w, h, title, lines=(), fill=BLUE_BG, stroke=BLUE, fs=7.4):
    d.add(Rect(x, y, w, h, fillColor=fill, strokeColor=stroke, strokeWidth=0.9))
    n = len(lines) + (1 if title else 0)
    ty = y + h / 2 + (n - 1) * 5.4
    if title:
        d.add(String(x + w / 2, ty - 2.5, title, fontName='Helvetica-Bold', fontSize=fs + 0.4, textAnchor='middle',
                     fillColor=INK))
        ty -= 10.8
    for ln in lines:
        d.add(String(x + w / 2, ty - 2.5, ln, fontName='Helvetica', fontSize=fs, textAnchor='middle', fillColor=INK))
        ty -= 10.8


def arrow(d, x1, y1, x2, y2, both=False, color=colors.black):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=0.9))
    import math
    def head(xa, ya, xb, yb):
        a = math.atan2(yb - ya, xb - xa)
        s = 4.6
        d.add(Polygon([xb, yb, xb - s * math.cos(a - 0.4), yb - s * math.sin(a - 0.4),
                       xb - s * math.cos(a + 0.4), yb - s * math.sin(a + 0.4)], fillColor=color, strokeColor=color))
    head(x1, y1, x2, y2)
    if both:
        head(x2, y2, x1, y1)


def abb1():
    d = Drawing(FRAME_W, 205)
    GR = colors.HexColor('#6B7280')
    box(d, 0, 175, 168, 28, '', ['Stromversorgung', '220 V, 50 Hz, ca. 1500 VA'], fill=GREY_BG, stroke=GR)
    box(d, 0, 116, 140, 28, '', ['Pult-Tastatur', 'Kanal K0'])
    box(d, 0, 76, 140, 28, '', ['Lochstreifenleser 1', 'Kanal K1'])
    box(d, 0, 36, 140, 28, '', ['Lochstreifenleser 2', 'Kanal K2'])
    box(d, 160, 64, 44, 70, '', ['Eingabe-', 'puffer'], fill=ORANGE_BG, stroke=GR)
    for y in (130, 90, 50):
        arrow(d, 140, y, 160, 99)
    d.add(Rect(222, 20, 190, 170, fillColor=BLUE_BG, strokeColor=BLUE, strokeWidth=0.9))
    d.add(String(317, 175, 'Zentraleinheit', fontName='Helvetica-Bold', fontSize=8.2, textAnchor='middle', fillColor=INK))
    box(d, 232, 104, 170, 56, 'Leitwerk', ['BZ · AR · BR (a + OR)', 'Steuerung Phasen I–IV'], fill=colors.white)
    box(d, 232, 30, 170, 56, 'Rechenwerk', ['AC · Vergleicher V1/V2', '+, −, UND, Verschiebung'], fill=colors.white)
    arrow(d, 204, 99, 222, 99)
    box(d, 432, 112, 103, 46, 'Magnettrommel', ['128 Spuren × 32 Sektoren', '× 33 Bit'], fill=GREY_BG, stroke=GR)
    arrow(d, 402, 132, 432, 132, both=True)
    box(d, 432, 48, 44, 38, '', ['Ausgabe-', 'puffer'], fill=ORANGE_BG, stroke=GR)
    arrow(d, 402, 58, 432, 58)
    box(d, 497, 62, 38, 16, '', ['SW (K2)'], fs=7)
    box(d, 497, 38, 38, 16, '', ['LS (K1)'], fs=7)
    arrow(d, 476, 72, 497, 70)
    arrow(d, 476, 62, 497, 46)
    return d


def abb2():
    d = Drawing(FRAME_W, 92)
    cw = (FRAME_W - 1) / 33.0
    x0 = 0
    ytop, hf, hn = 38, 16, 14
    fields = [(0, 11, 'beliebig', GREY_BG), (12, 18, 'Spur (7 Bit)', colors.HexColor('#DCE8F8')),
              (19, 23, 'Sektor (5 Bit)', colors.HexColor('#C9DBF2')), (24, 26, 'B', colors.HexColor('#FFF0DC')),
              (27, 29, 'A', colors.HexColor('#FFE0B0')), (30, 31, 'R', colors.HexColor('#FDE3E3')),
              (32, 32, 'L', colors.HexColor('#F8C9C9'))]
    for a, b, t, col in fields:
        x = x0 + a * cw
        d.add(Rect(x, ytop + hn, (b - a + 1) * cw, hf, fillColor=col, strokeColor=INK, strokeWidth=0.5))
        d.add(String(x + (b - a + 1) * cw / 2, ytop + hn + 5, t, fontName='Helvetica', fontSize=7.2,
                     textAnchor='middle', fillColor=INK))
    for i in range(33):
        d.add(Rect(x0 + i * cw, ytop, cw, hn, fillColor=colors.white, strokeColor=INK, strokeWidth=0.5))
        d.add(String(x0 + i * cw + cw / 2, ytop + 4, str(i), fontName='Helvetica', fontSize=6.4, textAnchor='middle',
                     fillColor=INK))
    # Klammer oben
    xa, xb = x0 + 12 * cw, x0 + 33 * cw
    d.add(Line(xa, ytop + hn + hf + 10, xb, ytop + hn + hf + 10, strokeColor=BLUE, strokeWidth=0.8))
    d.add(Line(xa, ytop + hn + hf + 10, xa, ytop + hn + hf + 5, strokeColor=BLUE, strokeWidth=0.8))
    d.add(Line(xb, ytop + hn + hf + 10, xb, ytop + hn + hf + 5, strokeColor=BLUE, strokeWidth=0.8))
    d.add(String((xa + xb) / 2, ytop + hn + hf + 14, 'Maschinenbefehl z₁₂–z₃₂ (21 Bit) = BR', fontName='DV-B',
                 fontSize=7.4, textAnchor='middle', fillColor=INK))
    # Klammern unten
    def under(a, b, y, text, anchor='middle'):
        x1, x2 = x0 + a * cw, x0 + (b + 1) * cw
        d.add(Line(x1, y, x2, y, strokeColor=INK, strokeWidth=0.6))
        d.add(String((x1 + x2) / 2, y - 9, text, fontName='DV', fontSize=6.8, textAnchor='middle', fillColor=INK))
    under(12, 23, ytop - 6, 'Adresse a (ADR) z₁₂–z₂₃, 12 Bit')
    under(24, 32, ytop - 6, 'Operation OP = BAZ, 9 Bit')
    under(30, 32, ytop - 22, 'Z (3 Bit)')
    return d


def abb3():
    order = [['00', '15', '32', '07', '24', '01', '16', '33'], ['10', '25', '02', '17', '34', '11', '26', '03'],
             ['20', '35', '12', '27', '04', '21', '36', '13'], ['30', '05', '22', '37', '14', '31', '06', '23']]
    hi = {'00', '01', '02', '03'}
    d = Drawing(FRAME_W, 140)
    lw = 52
    cw = (FRAME_W - lw) / 8.0
    for r, row in enumerate(order):
        y = 140 - 30 - r * 34
        d.add(String(0, y + 6, 'Pos. %d0–%d7' % (r, r) if False else 'Pos. %02o–%02o' % (r * 8, r * 8 + 7),
                     fontName='DV', fontSize=6.6, fillColor=INK))
        for c, v in enumerate(row):
            x = lw + c * cw
            pos = r * 8 + c
            d.add(String(x + cw / 2, y + 22, '%02o' % pos, fontName='DV', fontSize=6.2, textAnchor='middle',
                         fillColor=MUTED))
            d.add(Rect(x, y, cw, 20, fillColor=SEL if v in hi else colors.white, strokeColor=INK, strokeWidth=0.6))
            d.add(String(x + cw / 2, y + 6.5, v, fontName='DV-B', fontSize=8.6, textAnchor='middle', fillColor=INK))
    return d


def abb4():
    d = Drawing(FRAME_W, 128)
    bw, bh, y = 108, 64, 58
    xs = [0, 142.3, 284.7, 427]
    data = [('Phase I', ['Befehlszähler-', 'aufstellung', '', '⟨AR⟩ := ⟨BZ⟩ = BADR']),
            ('Phase II', ['Befehlsentnahme,', 'Operationsaufst.', '', '⟨BZ⟩ := ADR;', '⟨OR⟩ := OP']),
            ('Phase III', ['Befehlsadressen-', 'aufstellung', '', '⟨AR⟩ := ADR;', '⟨BZ⟩ := BADR+1']),
            ('Phase IV', ['Operations-', 'ausführung', '', 'gemäß ⟨OR⟩ = OP'])]
    for x, (t, lines) in zip(xs, data):
        d.add(Rect(x, y, bw, bh, fillColor=BLUE_BG, strokeColor=BLUE, strokeWidth=0.9))
        d.add(String(x + bw / 2, y + bh - 12, t, fontName='DV-B', fontSize=8, textAnchor='middle', fillColor=INK))
        ly = y + bh - 24
        for ln in lines:
            d.add(String(x + bw / 2, ly, ln, fontName='DV', fontSize=6.6, textAnchor='middle', fillColor=INK))
            ly -= 8.2
    for i in range(3):
        x1 = xs[i] + bw
        x2 = xs[i + 1]
        arrow(d, x1, y + bh / 2 + 4, x2, y + bh / 2 + 4)
        if i in (0, 2):
            d.add(String((x1 + x2) / 2, y + bh / 2 + 12, '(K)', fontName='DV-B', fontSize=7.4, textAnchor='middle',
                         fillColor=ORANGE))
    xm = (xs[2] + bw + xs[3]) / 2
    d.add(Line(xm, y + bh / 2 + 4, xm, y - 6, strokeColor=MUTED, strokeWidth=0.7, strokeDashArray=[1.5, 2]))
    d.add(Rect(xm - 142, y - 46, 292, 40, fillColor=ORANGE_BG, strokeColor=ORANGE, strokeWidth=0.8))
    d.add(String(xm + 4, y - 22, 'Eingriff von außen zwischen Phase III und IV:', fontName='DV', fontSize=6.8,
                 textAnchor='middle', fillColor=INK))
    d.add(String(xm + 4, y - 33, 'AC-Löschung, Stopp, Start (Tasten E, G, M, Ü, ST; Schalter H-R)', fontName='DV',
                 fontSize=6.8, textAnchor='middle', fillColor=INK))
    return d


# ------------------------------------------------------------------ Inhalt
def story():
    s = []
    # ---- Seite 1: Deckblatt (zeichnet pdflib.NumberedCanvas, PDF.md Abschnitt 4)
    s += [Spacer(1, 1), PageBreak()]
    # ---- Seite 2: Lesehinweise, danach Inhaltsverzeichnis (PDF.md 4.4)
    s.append(Paragraph('Lesehinweise', ST['h1']))
    s.append(P('**Schreibweisen:** Zahlen sind oktal, sofern nicht „dezimal“ vermerkt ist. ⟨x⟩ bedeutet „Inhalt von x“, '
               'z₀ … z₃₂ sind die Bitstellen eines Maschinenwortes (z₀ links). Weitere Schreibweisen: Kapitel 3.'))
    s.append(P('**Abgrenzung:** Angaben zum Bedienpult stehen nur, soweit sie zur Einordnung nötig sind. Die Annahmen für die interpretative '
               'Abarbeitung (Kapitel 9) sind mit c8205_interp.py abgeglichen (Stand des Abgleichs: %s).' % ABGLEICH_INTERP))
    s += note('achtung', 'Alle Zeitangaben dieses Dokuments (Wortzeit, Wartezeit, Zugriffszeit) beschreiben die '
                         'Hardware. Der Python-Interpreter rechnet dagegen mit Zeit 0 (Kapitel 9).')
    s.append(P('**Verwandte PDFs:** Bedienpult und Peripherie · Einzelbefehlsliste · Kodetabellen · Knotengraph · '
               'Bedienungsanleitung des Interpreters · Testhandbuch · BIS.'))
    s.append(P('Legende dieses Dokuments', 'h2'))
    s += tbl([['Zeichen', 'Bedeutung'],
              ['Hinweis (blauer Balken)', 'Ergänzung, die das Verständnis erleichtert.'],
              ['Achtung (orangefarbener Balken)', 'Stelle, an der man sich leicht irrt oder an der Hardware und '
                                                  'Interpreter abweichen.'],
              ['Grafiken', 'Schematisch, nicht maßstäblich; sie zeigen die Zusammenhänge, nicht das Aussehen des '
                           'Geräts.']], [0.3, 0.7])
    s.append(Paragraph('Inhaltsverzeichnis', ST['h1']))
    s.append(make_toc())
    s.append(PageBreak())

    # ---- 1
    s += h1('1 Einordnung und Leistungsdaten')
    s.append(P('Der C 8205 ist ein Einadreßautomat: Jeder Befehl nennt genau eine Speicheradresse, die zweite Größe '
               'jeder Operation steht im Akkumulator. Er wurde 1968 in der DDR gebaut. Bei zeitoptimaler '
               'Programmierung führt er etwa 2000 verdrahtete Operationen je Sekunde aus.'))
    s.append(P('Als Vorzüge werden genannt:'))
    s += bullets(['geringer technischer Aufwand der Zentraleinheit (nur ca. 400 Transistoren und 2000 Dioden),',
                  'die Magnettrommel als vergleichsweise billiges Speichermedium mit relativ kleiner Zugriffszeit,',
                  'für einen Kleinrechner hohe Operationsgeschwindigkeit,',
                  'Programmierhilfen in Form sogenannter Interpretersysteme, die den Programmieraufwand wesentlich '
                  'verringern.'])
    s.append(P('Eingesetzt wird er für wissenschaftlich-technische und mathematisch-ökonomische Berechnungen, zur '
               'Datenverarbeitung in begrenztem Umfang und als Hilfs- oder Satellitenrechner im Rahmen eines Systems '
               'von Rechnern.'))
    s += note('hinweis', 'Der Begriff „Interpretersystem“ in dieser historischen Aufzählung meint Programmiersysteme '
                         'auf dem C 8205 selbst. Er ist nicht zu verwechseln mit dem Python-Interpreter dieses '
                         'Projekts, der den Rechner nachbildet.')
    s += tbl([['Kenngröße', 'Wert'],
              ['Stromversorgung', '220 V ± 10 %, 50 ± 1 Hz, rund 1500 VA'],
              ['Zentraleinheit', 'Rechenwerk und Leitwerk; ca. 400 Transistoren, 2000 Dioden'],
              ['Wortlänge', '33 Bit (Maschinenwort)'],
              ['Speicher', 'Magnettrommel, 4096 Maschinenworte (128 Spuren × 32 Sektoren)'],
              ['Adressierung', '12 Bit Adreßteil → 4096 Zellen; 9 Bit Operationsteil → 512 Bitkombinationen'],
              ['Befehlssatz', '512 Codes, davon etwa 370 mit voneinander verschiedener Wirkung '
                              '(Einzelbefehlsliste: 372), zusammengesetzt aus rund 20 Grundoperationen'],
              ['Operationsgeschwindigkeit', 'Einzelbefehle min. 0,5 ms (≈ 1900 Op/s) · Organisationsbefehle min. '
                                            '0,4 ms (≈ 2400 Op/s) · Gruppen-/Wiederholungsbefehle bis ca. 9000 Op/s']],
             [0.27, 0.73], first_bold=True)

    # ---- 2
    s += h1('2 Geräteaufbau')
    s.append(P('Der Rechner besteht aus der Stromversorgungseinheit und der Zentraleinheit (Rechenwerk und Leitwerk). '
               'Zur unmittelbar zugeordneten (1.) Peripherie gehören der Magnettrommelspeicher, das Bedienpult mit '
               'Tastatur, Lampenfeld und Bahnsperrenschaltern, zwei Lochstreifenleser, ein Lochstreifenstanzer und '
               'ein Schreibwerk für alphanumerische Ein- und Ausgabe.'))
    s += figure(abb1(), 'Abbildung 1: Informationsfluss zwischen den Baueinheiten. Tastatur und beide Leser '
                             'speisen über einen Puffer die Zentraleinheit; Ausgaben laufen über einen weiteren Puffer '
                             'zu Schreibwerk (SW) und Lochstreifenstanzer (LS).')
    s += tbl([['Gerät', 'Kanal', 'Richtung', 'Geschwindigkeit / Besonderheit'],
              ['Pult-Tastatur bzw. Schreibwerk-Eingabe', 'K0', 'Eingabe',
               'Zeicheneingabe von Hand; Schalter T/SW wählt Tastatur oder Schreibwerk'],
              ['Lochstreifenleser 1', 'K1', 'Eingabe',
               '130 Zeichen/s (Standardleser, mechanisch mit Metallbürsten); 8-Kanal- oder 5-Kanal-Kode'],
              ['Lochstreifenstanzer', 'K1', 'Ausgabe', 'max. 50 Zeichen/s; 8-Kanal-Kode mit Paritätslochung'],
              ['Lochstreifenleser 2', 'K2', 'Eingabe', 'wie Leser 1'],
              ['Schreibwerk', 'K2', 'Ausgabe', 'max. 10 Zeichen/s; Zeichenkode R 300'],
              ['(frei)', 'K3', '—', 'beim C 8205 ist kein Gerät zugeordnet']],
             [0.27, 0.09, 0.12, 0.52])
    s += L.bild(os.path.join(ABB_DIR[0], 'C8205-Abb-Gesamtansicht.png'),
                'Abbildung 2: Gesamtansicht des C 8205 (Foto, Originalunterlagen). 1 Lochbandstanzer, 2 Peripherietisch, '
                '3 Leser 2, 4 Leser 1, 5 Tastatur-Anzeige-Einheit (Bedienpult), 6 Rechentisch, 7 SVE-Tisch '
                '(Stromversorgungstisch), 8 Ein- und Ausgabe-Schreibwerk, 9 Schreibwerktisch.')
    s.append(P('Als 2. Peripherie (wechselnd anschließbar) kommen lochbanderzeugende und lochbandverarbeitende Geräte '
               'in einem beliebigen 5-Kanal- oder 8-Kanal-Kode in Frage; beim 8-Kanal-Kode liegt die Paritätslochung '
               'im 5. Kanal. Programmsysteme werden meist im 8-Kanal-R300-Kode oder im 5-Kanal-CCITT-2-Kode '
               '(Telegraphenalphabet Nr. 2) geliefert. Die Zeichenkodes stehen im PDF „Kodetabellen“, Bedienelemente '
               'und Geräteverhalten im PDF „Bedienpult und Peripherie“.'))

    # ---- 3
    s += h1('3 Zahlen und Schreibweisen')
    s += tbl([['Thema', 'Festlegung'],
              ['Zahlensystem', 'Zahlen in Befehlen, Registern und im Speicher sind oktal, außer wenn ausdrücklich '
                               '„dual“ oder „dezimal“ gesagt wird. Bitbreiten, Nummern von Elementen und Zeitangaben '
                               'in diesem Dokument sind dezimal.'],
              ['Inhalt von', 'Spitze Klammern bedeuten „Inhalt von“: bei Registern die einzige Lesart; beim Speicher '
                             'ist 1000 die Adresse 1000, ⟨1000⟩ der Inhalt dieser Zelle. Sie gelten an Stelle einer '
                             'Qualifizierung, da sie nur bei Registern und Speicherinhalten vorkommen.'],
              ['Bitstellen', 'Die 33 Bit eines Maschinenwortes heißen von links nach rechts z₀, z₁, …, z₃₂ (2³³ '
                             'mögliche Wörter). Je drei Bit bilden eine Triade, also eine Oktalziffer: 11 Triaden '
                             't₁₀ bis t₀.'],
              ['Zahlendarstellung', 'Dualzahlen, ganze Zahlen und Gleitkommazahlen: Abschnitt 3.1; externe '
                                    'Darstellung und Tetraden (Konvention des BIS): Abschnitt 3.2.'],
              ['Namensbereiche', 'Flags, Register, Felder des Befehlswortes sowie Knoten und Konnektoren des '
                                 'Knotengraphen sind getrennte Bereiche; gleiche Namen sind zulässig (Flag A / Feld A, '
                                 'Feld B / Konnektor B). Außerhalb des eigenen Bereichs wird qualifiziert: „Flag A“, '
                                 '„Feld A“.']],
             [0.18, 0.82], first_bold=True)
    s += h2('3.1 Dualzahlen, ganze Zahlen und Gleitkommazahlen')
    s.append(P('Ob ein Maschinenwort eine Zahl, einen Befehl oder ein Zeichen darstellt, bestimmt allein das Programm. '
               'Verdrahtet sind nur Addition und Subtraktion; bei ihnen deutet das Rechenwerk das Wort als '
               '**Dualzahl in Festkommadarstellung**. z₀ ist das Vorzeichen, z₃₂ das niederwertigste Bit (z₁ ist das '
               'höchstwertige Betragsbit); bei vorzeichenlosen Zahlen ist z₀ das höchstwertige Bit. Die Stellung des '
               'Kommas wird nicht festgelegt. Multiplikation und Division sind nicht verdrahtet, sondern werden durch '
               'Programme mit Gruppenbefehlen gebildet; die Stellung des Kommas legt dort die Programmierung fest '
               '(Programmieranleitung 6.1 gebrochen, 6.2 ganz).'))
    s += tbl([['Darstellung', 'Komma', 'Zahlenwert', 'Bereich, Besonderheiten'],
              ['Gebrochene Festkommazahl', 'z. B. zwischen z₀ und z₁',
               'positiv: z = Σ zᵢ · 2⁻ⁱ (i = 1 … 32); negativ: Zweierkomplement 2 − z, d. h. alle Bits vor dem '
               'niedrigstwertigen mit 1 besetzten Bit werden negiert', 'z₀ = Vorzeichen (0 = +)'],
              ['Ganze Festkommazahl', 'hinter z₃₂',
               'positiv: z = Σ zᵢ · 2^(32−i), z₀ = 0; negativ: Zweierkomplement 2³³ − z, z₀ = 1; die Null gilt als '
               'positiv', '−2³² ≤ z ≤ 2³² − 1; die kleinste positive Zahl ist die Eins (Wort `00000000001`). '
                          'Addition und Subtraktion sind dieselben Befehle, nur die Deutung des Wortes ändert sich '
                          '(Programmieranleitung 6.2)'],
              ['Gleitkommazahl', '—',
               'z = m · 2ᵉ mit normalisierter Mantisse 0,5 ≤ |m| < 1 für z ≠ 0; Aufbau des Wortes siehe unten',
               'reine Programmkonvention: der Rechner kennt keine Gleitkommabefehle, das Programm interpretiert das '
               'Maschinenwort (Programmieranleitung 6.3, Abb. 28)']],
             [0.17, 0.14, 0.37, 0.32], first_bold=True)
    s.append(P('Aufteilung des Maschinenwortes bei Gleitkommazahlen:'))
    s += tbl([['Bits', 'Inhalt', 'Breite'],
              ['z₀', 'Vorzeichen der Mantisse (0 = +, 1 = −), Vorzeichen-Betrags-Darstellung', '1 Bit'],
              ['z₁ – z₆', 'Maschinenexponent e′ = e + 32 = Σ eᵢ · 2ⁱ (i = 0 … 5); höchstwertiges Bit e₅ = z₁, '
                          'niederwertigstes e₀ = z₆', '6 Bit'],
              ['z₇ – z₃₂', 'Mantissenbetrag m₁ m₂ … m₂₆ (m₁ = z₇, m₂₆ = z₃₂)', '26 Bit']], [0.14, 0.72, 0.14])
    s += bullets(['Die Mantisse steht **nicht** im Zweierkomplement, sondern als Betrag mit getrenntem Vorzeichen z₀. '
                  'Wegen der Normalisierung ist m₁ = 1.',
                  'Exponentenbereich 0 ≤ e′ ≤ 63, also −32 ≤ e ≤ 31; Mantissenbereich 0,5 ≤ |m| ≤ 1 − 2⁻²⁶. '
                  'Zahlenbereich 2⁻³³ ≤ |z| ≤ (1 − 2⁻²⁶) · 2³¹ sowie z = 0.',
                  '**Null:** eindeutig mᵢ = 0 (i = 1 … 26) und e′ = 0, das ist das Wort `00000000000` (positive Null). '
                  'Die Bitkombination „negative Null“ (z₀ = 1, Rest 0) ist keine gültige Darstellung.',
                  '**Beispiel:** z = −16 = −0,5 · 2⁵ ist `1 100101 1000…0` (Vorzeichen, Exponent e′ = 37, '
                  'Mantissenbetrag), oktal `62600000000`; zum Vergleich ist z = +16 das Wort `22600000000`.'])
    s.append(P('Folgerungen aus dem Aufbau (genutzt in den Beispielprogrammen 6.3.1 bis 6.3.3; Testaufträge '
               '`Tests/bsp_6_3_1_*.txt`, `bsp_6_3_2_*.txt`, `bsp_6_3_3_*.txt`):'))
    s += bullets(['**Betrag:** Linksverschiebung wirft z₀ heraus, die anschließende Rechtsverschiebung setzt z₀ = 0 ein.',
                  '**Vorzeichenumkehr:** Addition der Konstante `40000000000` (nur z₀ gesetzt) kehrt z₀ um. Bei x < 0 '
                  'entsteht dabei ein Überlauf, der durch einen nachfolgenden Überlaufsprung gelöscht werden muss, '
                  'sonst hält der Rechner an. Die Null darf nicht umgekehrt werden (sonst „negative Null“); sie wird '
                  'vorher mit dem Vergleichersprung 3 abgefangen.',
                  '**Betragsvergleich:** Weil der Exponent vor der Mantisse steht, ordnen die Betragswörter (z₀ = 0) '
                  'wie die ganzen Zahlen: |a| < |b| genau dann, wenn das Wort von |a| als ganze Zahl kleiner ist. Der '
                  'markierte Einzelbefehl genügt.'])
    s += h2('3.2 Externe Darstellung und Tetraden (Konvention des BIS)')
    s.append(P('Die folgenden Darstellungen gehören nicht zur Hardware, sondern zum Bausteininterpretationssystem BIS '
               '(Ergänzung vom 07.10.2026; Quelle: BIS-Dokumentation, siehe PDF „BIS“). Der Rechner kennt weder '
               'Gleitkomma noch Dezimalumwandlung noch Tetraden; das Programm bzw. das BIS interpretiert die '
               'Maschinenworte.'))
    s += bullets(['**Externe Gleitkommazahl** (Ein- und Ausgabe): entweder übliche Dezimalschreibweise `(±) a,b` oder '
                  'z = ± m · 10ᴱ mit 0,1 ≤ m < 1 (für z ≠ 0). Der Exponent E wird nicht erhöht, er besteht aus '
                  'Vorzeichen und Betrag. Form: Vorzeichen, höchstens acht Mantissenziffern, Exponentenvorzeichen, '
                  'Exponent (die Vorzeichen sind optional).',
                  '**Eingabezahlenbereich:** E darf bei der Eingabe nicht größer als 8 sein, also '
                  '|z| ≤ (1 − 10⁻⁸) · 10⁸; die kleinste eingebbare Zahl ≠ 0 ist 10⁻⁹. In Dezimalschreibweise ist die '
                  'größte Zahl 99 999 999, die kleinste ≠ 0 ist 0,000000001.',
                  '**Genauigkeit:** 26 Dualstellen der Mantisse entsprechen 7 Dezimalstellen; nur 7 Ziffern lassen '
                  'sich genau verarbeiten. Die achte Mantissenziffer der externen Form ist nicht mehr exakt '
                  'darstellbar.',
                  '**Tetraden:** Jede Dezimalziffer steht als vierstellige Dualzahl. Ein Maschinenwort fasst höchstens '
                  'acht Tetraden t₇ … t₀ (z₀–z₃₁, linksbündig); z₃₂ bleibt frei und wird nicht ausgewertet. Extern: '
                  'höchstens acht Dezimalziffern ohne Vorzeichen, z ≤ 99 999 999. Die Tetraden t₇ … t₀ sind nicht mit '
                  'den Oktal-Triaden t₁₀ … t₀ zu verwechseln.',
                  '**Beispiel:** Die externe Zahl 2 8 1 3 6 9 0 5 ergibt das Wort `0010 1000 0001 0011 0110 1001 0000 '
                  '0101 0`, oktal `12011551012`.',
                  '**Rechnen** mit Tetraden ist nicht vorgesehen: Das BIS enthält nur Programme zur Ein- und Ausgabe. '
                  'Der Assembler `c82ass` kennt keine Gleitkomma- oder Tetraden-Literale; solche Wörter werden als '
                  'Oktalzahl mit führender 0 mit `dw` angegeben (z. B. −16: `dw 062600000000`).'])

    # ---- 4
    s += h1('4 Maschinenwort und Befehlswort')
    s.append(P('Das interne Maschinenwort hat 33 Bit. Es kann gleichermaßen eine Zahl, einen Befehl oder Alpha-Zeichen '
               'darstellen; die Art der Interpretation bestimmt das Programm, auch verschiedenartige Interpretationen '
               'innerhalb eines Wortes sind möglich. Ein Befehl belegt die Bits z₁₂ bis z₃₂ (21 Bit); die zwölf '
               'höheren Bits z₀ bis z₁₁ sind „beliebig“.'))
    s += figure(abb2(), 'Abbildung 3: Aufbau eines 33-Bit-Maschinenwortes, wenn es als Befehl interpretiert wird. '
                        '33 Bit = 11 Oktalziffern (Triaden t₁₀ … t₀) · Spur 7 Bit (128 Spuren) · Sektor 5 Bit '
                        '(32 Sektoren). Bitstelle z₀ … z₃₂ (links → rechts) · B = Befehlstyp · A = Operationsart · '
                        'Z = Operationszusatz = R + L.')
    s += tbl([['Feld', 'Bits', 'Breite', 'Bedeutung'],
              ['„beliebig“', 'z₀ – z₁₁', '12 Bit', 'für den Befehl ohne Bedeutung (Original-Bezeichnung)'],
              ['Maschinenbefehl', 'z₁₂ – z₃₂', '21 Bit', 'steht während der Ausführung im Befehlsregister BR'],
              ['Adresse a (ADR)', 'z₁₂ – z₂₃', '12 Bit', 'Adreßteil: Spur z₁₂–z₁₈ (7 Bit), Sektor z₁₉–z₂₃ (5 Bit); in '
                                                       'Oktalziffern a₁ a₂ a₃ a₄'],
              ['Operation (BAZ, OP)', 'z₂₄ – z₃₂', '9 Bit', 'Operationsteil; steht im Operationsregister OR'],
              ['B – Befehlstyp', 'z₂₄ – z₂₆', '3 Bit', 'Werte 0 … 7, siehe Kapitel 8'],
              ['A – Operationsart', 'z₂₇ – z₂₉', '3 Bit', 'Bedeutung hängt vom Befehlstyp B ab'],
              ['Z – Operationszusatz', 'z₃₀ – z₃₂', '3 Bit', 'besteht aus R und L'],
              ['R – Resultatbehandlung', 'z₃₀ – z₃₁', '2 Bit',
               'keine / Rechtsverschiebung / Linksverschiebung / zyklische Linksverschiebung'],
              ['L – Löschbit', 'z₃₂', '1 Bit', 'L = 1: der Akkumulator wird in Phase III gelöscht']],
             [0.22, 0.14, 0.09, 0.55])
    s += note('achtung', 'Das Feld R (Resultatbehandlung) ist nicht der R-Befehl (indirekter Lesebefehl, '
                         'Operationscodes mit B ≥ 2, A = 5 und Z ungerade) und auch nicht die Taste bzw. '
                         'Schalterstellung „R“ (Rechnen) am Bedienpult. Ebenso sind Flag A und Feld A verschieden.')
    s.append(P('Ein Maschinenbefehl hat die Form ADR OP, z. B. `7774 240`: Adresse 7774, Operation 240 (Transport). '
               'Ein Befehl liegt in der Regel als Teil eines Maschinenwortes auf einer Befehlsadresse BADR im '
               'Trommelspeicher. Das Operationsregister OR enthält den Operationsteil BAZ, das Befehlsregister BR die '
               'Verkettung BR := a ‖ OR.'))
    s.append(P('**Adresseinheit (1°):** Die Originaldokumentation schreibt 1° für eine Adresseinheit, also die nächste '
               'Speicherzelle (z. B. ⟨BZ⟩ + 1° beim Sprungbefehl). In Registern, die nur Adressen enthalten (BZ, AR), '
               'und bei Rechnungen mit Adressen ist 1° = 1. Steht eine Adresse im Maschinenwort, so liegt sie in '
               'z₁₂–z₂₃, und es folgen die 9 Bit der Operation; in Oktalschreibweise (11 Stellen) lautet das Wort '
               '`0000 a₁a₂a₃a₄ BAZ`. Eine im Speicher abgelegte Adresseinheit ist daher im ganzen Maschinenwort nicht '
               '1, sondern 1° = `00000001000` (oktal, kurz `01000`, wie `adreinheit dw 01000` in der '
               'Assemblerdokumentation). Der Interpreter rechnet intern mit der Adresse allein (12 Bit), dort ist '
               '1° = 1.'))

    # ---- 5
    s += h1('5 Register und Flags')
    s += h2('5.1 Register')
    s += tbl([['Register', 'Breite', 'Art', 'Bedeutung'],
              ['AC', '33 Bit', 'Umlaufregister', 'Akkumulator; einziger Ausgangspunkt für das Abspeichern in die '
                                                   'Trommel'],
              ['V1 / V2', '1 Bit je', 'Flip-Flops', 'Vergleicher; zusammen der Pseudovergleicher V3 (V3 = „V1 = 1 und '
                                                    'V2 = 1“); dieselben Elemente wie die Flags V1 und V2'],
              ['OR', '9 Bit', 'statisch (Schiebekette)', 'Operationsregister, identisch mit BAZ'],
              ['BZ', '12 Bit', 'Umlaufregister', 'Befehlszähler; enthält die Adresse BADR des nächstabzuarbeitenden '
                                                  'Befehls'],
              ['AR', '12 Bit', 'statisch (Schiebekette)', 'Adreßregister; Zellenwähler für jeden Trommelzugriff'],
              ['BR', '21 Bit', '—', 'Befehlsregister, BR := a ‖ OR (Adreßteil a, 12 Bit, und OR, 9 Bit)']],
             [0.1, 0.1, 0.22, 0.58], first_bold=True)
    s.append(P('BZ und AC sind Umlaufregister: Sie befinden sich technisch auf der Trommel. Ein Lesekopf erfasst die '
               'Bit-Belegung eines Platzes, ein Umformer bereitet das erneute Aufsprechen über einen Sprechkopf vor, '
               'ein Löschkopf setzt die Plätze auf 0. Die zentrale Taktsteuerung sorgt dafür, dass der Zustand eines '
               'Umlaufregisters zu Beginn jeder Wortzeit stets derselbe ist. OR und AR sind statische Register '
               '(Schiebekette): Die Information wird seriell ein- und herausgeschoben, der Zustand jeder Stelle ist '
               'zu jedem Zeitpunkt abgreifbar.'))
    s.append(P('**Zugriffsrichtung zur Trommel:** Eine Entnahme gespeicherter Information ist zum Rechenwerk, zum '
               'Befehlszähler und zum Operationsregister hin möglich. Eine Abspeicherung ist dagegen nur vom '
               'Akkumulator her möglich. Weil es kein Indexregister gibt, laufen Adreßrechnungen über den AC.'))
    s += h2('5.2 Flags')
    s.append(P('Ein Flag ist ein elektronischer Speicher für 0 oder 1. Es setzt seinen Wert nicht selbst, sondern wird '
               'vom Rechenwerk oder vom Menschen über einen Schalter belegt; wer zuletzt setzt, bestimmt den Zustand. '
               'Den meisten Flags ist im Bedienpult eine Lampe zugeordnet. Schalter, Flag und Lampe desselben Namens '
               'sind eine Sache: der Schalter ist die Handlung, das Flag der gespeicherte Zustand, die Lampe seine '
               'Anzeige.'))
    s += tbl([['Flag', 'Bedeutung'],
              ['E', '= 1, wenn ein Eingabebefehl aufgestellt ist. Zur Eingabe ist zusätzlich die Anwahl eines '
                    'Eingabegerätes erforderlich. E erlischt nach der Eingabe eines Zeichens mit der Umstellung des '
                    'Eingabebefehls; E erlischt nicht, wenn der Eingabebefehl nicht ausgeführt wird (z. B. fehlende '
                    'Anwahl), und leuchtet bei erneutem Eingabebefehl sofort wieder'],
              ['A', '= 1, wenn ein Ausgabebefehl aufgestellt ist. Zur Ausgabe ist zusätzlich die Anwahl eines '
                    'Ausgabegerätes erforderlich. A erlischt mit der Umstellung des Ausgabebefehls (nach der Übergabe '
                    'des Zeichens an den 1-Zeichen-Puffer, nicht erst nach Abschluss der Geräteausgabe) und leuchtet '
                    'bei erneutem Ausgabebefehl sofort wieder. Fehlt die benötigte Anwahl oder ist die programmierte '
                    'Anwahl nicht existent, stoppt der Rechner mit gesetztem Flag A (Lampe A)'],
              ['T', 'Subflag: = 1 für „Tastatur aktiv“ im Kanal K0'],
              ['SW', 'Subflag: = 1 für „Schreibwerk aktiv“ im Kanal K0 (T und SW sind alternativ)'],
              ['K1, K2, K3', '= 1, wenn der Kanal 1, 2 bzw. 3 angewählt ist'],
              ['FE', '= 1: „Fehler bei Eingabe“; tritt ein, wenn im 8-Kanal-Kode ein Zeichen mit gerader Zahl von '
                     'Lochungen gelesen werden soll (Paritätskontrolle). Ausgenommen sind „Irrung Zeichen“ und das '
                     'Transportloch im Vorspann: Sie werden bei der Lochbandeingabe übersprungen '
                     '(Originaldokumentation 4.3.2.2, Abb. 16)'],
              ['FÜ', '= 1, wenn ein Überlauf auftritt. Ein Halt wegen Überlauf setzt weder US noch BS; angezeigt wird '
                     'nur FÜ (Lampe FÜ)'],
              ['BS', '= 1, wenn ein programmierter „bedingter Stopp“ wirksam wird, d. h. wenn der Befehl abgearbeitet '
                     'wird und der Auswahlschalter BS eingerastet ist. Ist der Schalter nicht eingerastet, bleibt BS '
                     '= 0 und der Befehl hat keine Wirkung'],
              ['US', '= 1, wenn der Rechner einen „unbedingten Stopp“-Befehl ausführt (immer, sobald der Befehl '
                     'abgearbeitet wird; der Adreßteil des Befehls kann dem Adreßregister entnommen werden)'],
              ['V1, V2', 'Vergleicher; V3 ist die Sprechweise für „V1 = 1 und V2 = 1“'],
              ['H', '= 1, wenn der Schalter H-R auf „H“ (Halt) steht, = 0 bei „R“ (Rechnen)'],
              ['SP', '= 1, wenn der Selektor-Schalter SP gesetzt ist (Bedingung für den bedingten Sprung mit '
                     'Rückkehrabsicht)']],
             [0.12, 0.88], first_bold=True, keep=False)
    s += h2('5.3 Anzeige des Arbeitszustands')
    s.append(P('Die Lampen H, R, US, BS, FÜ, FE, E und A zeigen das Rechnen oder den Grund für die Unterbrechung des '
               'Befehlsablaufs an. Ein Anhalten erfolgt grundsätzlich nach der Phase III. Bei gesetztem Schalter H '
               'leuchtet die Lampe H; im Zustand „Rechnen“ darf von diesen Lampen nur R leuchten.'))
    s += bullets(['US leuchtet beim Befehl „Unbedingter Stopp“, BS beim programmierten „Bedingten Stopp“ bei gesetztem '
                  'Schalter BS.',
                  'FÜ leuchtet bei Überlauf (Unterbrechung nur bei Einzelbefehlen ohne Verschiebung, wenn der '
                  'nachfolgende Befehl kein Überlaufsprung ist).',
                  'FE leuchtet bei einem durch die Paritätskontrolle ermittelten Eingabefehler im 8-Kanal-Kode.',
                  'Die Lampen K0 („T-SW“), K1, K2, K3 zeigen den angewählten Kanal; bei K0 unterscheiden T und SW '
                  'zwischen Tastatur und Schreibwerk.',
                  'Die Lampen V(1-2) zeigen den Vergleicherstand zur Zeit des Setzens: Lampe 1 = Vergleicher 1, '
                  'Lampe 2 = Vergleicher 2, beide = Vergleicher 3.',
                  'Die untere Lampenreihe zeigt das Befehlsregister in Triaden: vier Triaden Adreßteil (Gewichte '
                  '1000, 100, 10, 1 oktal), drei Triaden Operationsteil (B, A, Z).'])

    # ---- 6
    s += h1('6 Die Magnettrommel')
    s.append(P('Der gesamte Speicher liegt magnetisch auf einer Trommel, organisiert in Zellen (Maschinenworten). Die '
               'Trommel hat 128 Spuren (auch Bahnen genannt) mit je 32 Sektoren: 128 × 32 = 4096 Maschinenworte à '
               '33 Bit. Eine 12-Bit-Adresse gliedert sich in die Bahn-Nummer (7 Bit) und die Sektor-Nummer (5 Bit). '
               'Die Trommel dreht mit 18 000 min⁻¹ (300 Umdrehungen je Sekunde); je Spur werden 32 Wörter à 33 Bit '
               'geschrieben, die Arbeitsfrequenz der seriellen Verarbeitung beträgt rund 316 kHz.'))
    s.append(P('Eine Wortzeit ist die Zeit, in der ein gespeichertes Wort unter dem Lesekopf durchläuft: '
               '33 : 316 kHz ≈ 104 µs ≈ 0,1 ms. Die mittlere Zugriffszeit beträgt 1,67 ms, die maximale 3,33 ms.'))
    s += h2('6.1 Logische und physische Reihenfolge der Sektoren')
    s.append(P('Die logische Reihenfolge der Sektoren einer Spur (Adressierung) entspricht nicht der physischen Abfolge '
               'auf der Trommel. Die Leseelektronik konnte aus Leistungsgründen nicht jeden physisch aufeinander'
               'folgenden Sektor nacheinander lesen, sondern jeweils nur jeden 6. (gezählt einschließlich des gerade '
               'gelesenen, also 5 Positionen weiter; vier Sektoren werden übersprungen). Die logische Sektoradresse '
               'wird entsprechend dieser Zugriffsreihenfolge vergeben. Daraus ergibt sich (mindestens teilweise) die '
               'Wartezeit.'))
    s += figure(abb3(), 'Abbildung 4: Physische Zugriffsreihenfolge der 32 Sektoren einer Spur (oktal). Grau: '
                        'physische Position; in den Kästchen: logische Sektoradresse. Orange: die logischen Sektoren '
                        '00–03, die physisch jeweils 5 Positionen auseinander liegen (Schritt +05). Nach einem Zugriff '
                        'kann erst wieder die 6. logisch folgende Zelle ohne Verlust gelesen werden.')
    rows = [['Position (physisch)', '00', '01', '02', '03', '04', '05', '06', '07'],
            ['logische Sektoradresse', '00', '15', '32', '07', '24', '01', '16', '33'],
            ['Position (physisch)', '10', '11', '12', '13', '14', '15', '16', '17'],
            ['logische Sektoradresse', '10', '25', '02', '17', '34', '11', '26', '03'],
            ['Position (physisch)', '20', '21', '22', '23', '24', '25', '26', '27'],
            ['logische Sektoradresse', '20', '35', '12', '27', '04', '21', '36', '13'],
            ['Position (physisch)', '30', '31', '32', '33', '34', '35', '36', '37'],
            ['logische Sektoradresse', '30', '05', '22', '37', '14', '31', '06', '23']]
    s += tbl(rows, [0.28] + [0.09] * 8, center_cols=range(1, 9), first_bold=True)
    s.append(P('Von einer logischen Adresse L zur logisch nächsten L+1 beträgt der Abstand der Positionen durchgehend '
               '+05 (oktal). Umgekehrt entspricht der Schritt zur physisch benachbarten Position durchgehend +15 '
               '(oktal) in der logischen Adresse. Beide Schrittweiten sind zueinander invers modulo 40 (oktal): '
               '05 · 15 ≡ 01.'))
    s.append(P('**Bahnwahl:** Jede Bahn wird über eine eigene Elektronik gewählt; die Schaltzeit ist für alle Bahnen '
               'gleich und vernachlässigbar (0 gesetzt). Ein Bahnwechsel kostet daher keine zusätzliche Wartezeit; '
               'ausschlaggebend für die Zugriffszeit ist allein die Sektorposition innerhalb der gewählten Bahn.'))
    s += h2('6.2 Zeitoptimale Programmierung')
    s.append(P('Anders als bei einem Speicher mit wahlfreiem, gleichmäßig schnellem Zugriff ist die Zugriffszeit '
               'variabel: Direkt nach einem Zugriff ist erst wieder die 6. logisch folgende Zelle ohne Wartezeit '
               'erreichbar. Liegen Programm und Daten so verteilt, dass der jeweils nächste Zugriff genau auf diese '
               'Distanz fällt, ist der Ablauf zeitoptimal; andernfalls muss unter Umständen eine volle Umdrehung '
               'abgewartet werden. Ausgehend von der aktuellen Adresse A liegt die frühestens ohne Wartezeit '
               'erreichbare Zelle bei (oktal, mod 40):'))
    s += tbl([['Befehlsart', 'Folgeadresse'], ['Einzelbefehl', 'A+32 ; A+07'], ['Gruppenbefehl', 'A+32 ; A+07 ; A+24'],
              ['Sprung', 'A+24']], [0.3, 0.7], first_bold=True)
    s += note('hinweis', 'Diese Formeln sind eine Programmier- und Layout-Hilfe zur Vermeidung von Wartezeit, keine '
                         'Eigenschaft der Befehlsausführung selbst.')
    s.append(P('**Positionen statt Sektornummern (abgeleitet).** Der logische Schritt +1 entspricht +05 Positionen. Ein '
               'logischer Abstand d (in Sektoren) entspricht daher 5·d mod 32 Positionen (dezimal), jede Position eine '
               'Wortzeit (104 µs):'))
    s += tbl([['logischer Abstand zum Befehl (oktal, mod 40)', 'Positionen', 'Verwendung'],
              ['+01', '5', 'nächster Befehl bei fortlaufendem Programm'],
              ['+32', '2', 'Operand eines Einzelbefehls'],
              ['+07', '3', 'Operand eines Einzelbefehls'],
              ['+24', '4', 'Folgebefehl nach einem Sprung']], [0.4, 0.14, 0.46], center_cols=(1,))
    s.append(P('Der Operandensektor eines Befehls in Sektor s ist also (s+32) oder (s+07) mod 40 (oktal); die Spur '
               'spielt keine Rolle, da ein Bahnwechsel keine Zeit kostet. Die Befehle selbst legt man fortlaufend ab; '
               'optimiert wird die Lage der Operanden und der Sprungziele.'))
    s.append(P('**Reihenfolge der Phasen und Wartezeiten.** Im zeitlichen Ablauf gehört Phase I '
               '(Befehlszähleraufstellung) bereits zum nächsten Befehl: die Reihenfolge je Befehl ist II, III, IV, I. '
               'Die beiden Wartezeiten heißen W₁ (zwischen Phase I und der Entnahme des nächsten Befehls in Phase II) '
               'und W₂ (zwischen Phase III und Phase IV, bis der Operandensektor erreicht ist).'))
    s.append(P('**Mindestablauf (abgeleitet),** in Positionen ab der Befehlsentnahme (Phase II = 0):'))
    s += tbl([['Befehl', 'Ablauf', 'Wortzeiten bis zur nächsten Befehlsentnahme'],
              ['Einzelbefehl, Operand bei +32', 'II 0, III 1, IV 2, I 3, W₁ 4, nächster Befehl 5', '5'],
              ['Einzelbefehl, Operand bei +07', 'II 0, III 1, W₂ 2, IV 3, I 4, nächster Befehl 5', '5'],
              ['Sprung', 'II 0, III 1, IV 2, I 3, nächster Befehl 4', '4']], [0.3, 0.5, 0.2], center_cols=(2,))
    s.append(P('Das deckt sich mit den Zeitangaben in Kapitel 7 (Einzelbefehle mindestens 5 Wortzeiten, '
               'Organisationsbefehle mindestens 4 Wortzeiten).'))
    s.append(P('**Beispiel 1: Operand nicht optimal.** Der Befehl `7716 211` steht in Zelle 4000 (Sektor 00). Sein '
               'Operandensektor 16 ist weder +32 noch +07. Ablauf: II in Sektor 00, III in 15, W₂ über 32, 07, 24 und '
               '01, IV in 16, I in 33, dann W₁ von Sektor 10 bis Sektor 24 (der nächsten Umdrehung), nächster Befehl '
               'in Sektor 01. Von Befehl zu Befehl vergehen 37 Wortzeiten (abgeleitet: 4 Positionen W₂, 29 Positionen '
               'W₁), das ist eine Trommelumdrehung mehr als nötig.'))
    s.append(P('**Beispiel 2: Sprung als Umweg.** Lässt sich der Operand nicht verlegen, setzt man einen unbedingten '
               'Sprung `xx24 000` in die Zelle (Sektor 00), verlegt den Lesebefehl in Sektor 24 und lässt ihn von dort '
               'auf den Operandensektor 16 zugreifen (24+32 mod 40 = 16). Der nächste Befehl folgt in Sektor 25. Von '
               'Befehl zu Befehl vergehen nur 9 Wortzeiten (Sprung 4, Einzelbefehl 5, abgeleitet). Die '
               'Programmieranleitung nennt eine Ersparnis von 28 Wortzeiten (37 − 9 = 28). Der Preis ist eine '
               'zusätzliche Zelle für den Sprung; der Befehl in Sektor 24 muss dafür frei sein.'))
    s.append(P('**Beispiel 3: Algebraischer Ausdruck** (Programmieranleitung 5.19.1, Aufgabe wie 5.5). Transkription '
               'nach Seitenabbild; die Spalte „Abstand“ ist abgeleitet (Positionen von der Befehlszelle zum Operanden- '
               'bzw. Sprungziel-Sektor, Tabelle in 6.1):'))
    s += tbl([['Adr.', 'Inhalt', 'Bemerkung', 'Abstand'],
              ['3003', '3006 000', 'Sprung zum Programmstart', '15'],
              ['3006', '3000 215', '⟨AC⟩ := 2a', '2'],
              ['3007', '3001 220', '⟨AC⟩ := 2a − b', '2'],
              ['3010', '3002 224', '⟨AC⟩ := 2·(2a − b − c)', '2'],
              ['3011', '3031 000', 'Sprung', '16'],
              ['3031', '3000 214', '⟨AC⟩ := 2·2·(2a − b − c) + a', '3'],
              ['3032', '3001 220', '⟨AC⟩ := x', '3']], [0.1, 0.16, 0.6, 0.14], code_cols=(0, 1), center_cols=(3,))
    s.append(P('Alle Rechenbefehle entnehmen ihren Operanden zeitoptimal (2 bzw. 3 Positionen). Die beiden Sprünge sind '
               'dagegen nicht wartefrei (wartefrei wäre +24, also 4 Positionen; von 3011 aus 3035). Das ist offenbar '
               'beabsichtigt: Die Sprungziele sind durch die Operandenlage bestimmt, denn Zelle 3000 ist nur von '
               'Sektor 06 (+32) oder Sektor 31 (+07) aus wartefrei erreichbar. Nach der Programmieranleitung vergeht '
               'von der Entnahme des ersten Befehls bis zur Entnahme des letzten Operanden „genau eine '
               'Trommelumdrehung“ weniger als in 5.5 (dort ca. 2⅔ Umdrehungen); diese Angabe ist hier nicht '
               'nachgerechnet.'))
    s.append(P('**Folgerungen für die Programmierung (abgeleitet).**'))
    s += bullets(['Befehle fortlaufend ablegen, Operanden (Variablen, Konstanten, Adreßwörter) auf Sektor +32 oder +07 '
                  'zum benutzenden Befehl legen. Mit `equ` und `db` lassen sich die dafür nötigen Lücken einstellen; '
                  'die Lücken können mit Daten gefüllt werden.',
                  'Ein Operand, der von mehreren Befehlen benutzt wird, ist nur für Befehle in passenden Sektoren '
                  'optimal erreichbar. Sonst entscheidet man je Befehl zwischen Wartezeit und Umweg über einen Sprung.',
                  'Ein Sprung hat sein wartefreies Ziel bei +24. Jedes andere Ziel kostet Wartezeit.'])
    s += h2('6.3 Bahnsperrenschalter')
    s.append(P('Die Bahnsperrenschalter schützen innerhalb der Spuren 0000 bis 1740 (oktal) bestimmte, auswählbare '
               'Bahnengruppen gegen irrtümliches Überschreiben; der Befehlsablauf bleibt unbeeinflusst (reine '
               'Schreibschutz-Funktion). Es gibt sechs Schalter mit den Kennzeichnungen 0001, 0040, 0100, 0200, 0400 '
               'und 1000; im Grundzustand sind alle AUS. Der Schalter 0001 („EIN–AUS“) ist der Hauptschalter, die '
               'übrigen fünf sind Zusatzschalter. Sie befinden sich physisch an der Rückseite der '
               'Tastatur-Anzeige-Einheit; für die Testdefinition gehören sie zum Bedienpult (Bezeichnungen BSP_0001 … '
               'BSP_1000).'))
    s.append(P('Bei Hauptschalter AUS sind alle Spuren offen. Bei Hauptschalter EIN gilt eine Bahn B (Bahn-Nr. als '
               'Ganzzahl; 0 = Spur 0000, 1 = Spur 0040, … 37 oktal = Spur 1740) genau dann als gesperrt, wenn B eine '
               '– auch leere – Bit-Teilmenge der eingeschalteten Zusatzschalter ist. Dabei entsprechen 0040 → Bit 0, '
               '0100 → Bit 1, 0200 → Bit 2, 0400 → Bit 3, 1000 → Bit 4 der Bahn-Nr. Spur 0000 ist damit bei '
               'Hauptschalter EIN immer gesperrt. Bahnen ab Spur 2000 (Bahn-Nr. ≥ 32) sind über diese Schalter nie '
               'sperrbar.'))
    s += h2('6.4 Nachbildung im Interpreter: die persistente Trommeldatei')
    s.append(P('Der Python-Interpreter bildet den Speicher als dauerhafte Textdatei nach (Ergänzung vom 07.10.2026; '
               'Vorgabe `virtuelle_Geraete/Trommel/trommel.txt`, Schalter `--trommel`):'))
    s += bullets(['**Format:** genau 4096 Zeilen `aaaa: ttttttttttt` (Adresse und Wert oktal), je Zelle eine Zeile, '
                  'geordnet nach der **logischen** Adresse `0000` bis `7777` – nicht nach der physischen Reihenfolge '
                  'der Sektoren aus 6.1.',
                  '**Zeitverhalten:** Wortzeit, Wartezeit und Zugriffszeit werden nicht nachgebildet, alle Zeiten sind '
                  '0; die Formeln aus 6.2 bleiben eine Layout-Hilfe.',
                  '**Persistenz:** Der Inhalt bleibt über Tests und Aufrufe hinweg erhalten. Die Zeilen einer '
                  'Testdatei überlagern ihn, nicht genannte Zellen behalten ihren Wert; jede Zelländerung eines '
                  'Befehls wird sofort in der Datei nachgeführt. Register, Flags und Geräte beginnen dagegen bei jedem '
                  'Test neu.',
                  '**Zurücksetzen:** Der Interpreter setzt die Trommel nie zurück und legt die Datei nie an. Eine leere '
                  'Trommel erzeugt `python3 erzeuge_leere_trommel.py`; fehlt die Datei oder ist sie formal fehlerhaft, '
                  'startet kein Test (Rückkehrcode 16).'])
    s += note('achtung', 'Ein Test, der Zellen liest oder prüft, die er nicht selbst belegt, hängt vom Trommelstand '
                         'vor dem Lauf ab und ist nur auf leerer Trommel reproduzierbar. Einzelheiten im PDF '
                         '„Testhandbuch“ und in „Bedienungsanleitung Python-Interpreter“.')

    # ---- 7
    s += h1('7 Der Befehlszyklus: vier Phasen')
    s.append(P('Als Zellenwähler wird in jedem Fall das Adreßregister AR benutzt. Bei Entnahmen aus dem Speicher treten '
               'wegen der Magnettrommel im Allgemeinen Wartezeiten auf, weil der gewünschte Sektor erst unter die '
               'Lese-Schreib-Einrichtung gedreht werden muss. Der Befehlszyklus gliedert sich in vier Phasen; zwischen '
               'ihnen liegt jeweils eine Koinzidenz-Wartezeit (K).'))
    s += figure(abb4(), 'Abbildung 5: Die vier Phasen eines Befehlszyklus. Jede Phase dauert eine Wortzeit (104 µs). '
                        '(K) = Koinzidenz-Wartezeit: W₁ nach Phase I, W₂ nach Phase III.')
    s += tbl([['Phase', 'Bezeichnung', 'Wirkung'],
              ['I', 'Befehlszähleraufstellung', 'Füllen des Zellenwählers AR mit BADR: ⟨AR⟩ := ⟨BZ⟩ = BADR'],
              ['(K)', 'W₁ – Wartezeit', 'Die Trommel dreht sich bis zum Sektor, der durch ⟨AR⟩ = BADR vorgegeben ist.'],
              ['II', 'Befehlsentnahme und Operationsaufstellung', 'Entnahme des Befehls ADR OP: ⟨BZ⟩ := ADR; '
                                                                  '⟨OR⟩ := OP'],
              ['III', 'Befehlsadressenaufstellung', 'Füllen von AR mit ADR; gleichzeitig Rücktransport von BADR nach '
                                                   'BZ und Erhöhung um 1: ⟨AR⟩ := ⟨BZ⟩ = ADR, gleichzeitig ⟨BZ⟩ := '
                                                   '⟨AR⟩ + 1 = BADR + 1'],
              ['(K)', 'W₂ – Wartezeit', 'Die Trommel dreht sich bis zum Sektor, der durch ⟨AR⟩ = ADR vorgegeben ist.'],
              ['IV', 'Operationsausführung', 'Ausführung entsprechend ⟨OR⟩ = OP']],
             [0.09, 0.3, 0.61], center_cols=(0,))
    s += note('achtung', '„Gleichzeitig“ heißt: Beide Teilanweisungen werden mit den Registerwerten ausgewertet, die '
                         'unmittelbar vor dem Schritt galten. In Phase III ergibt sich das neue BZ deshalb aus dem '
                         'alten AR (BADR), also BADR + 1, nicht ADR + 1.')
    s.append(P('Die Tabelle ist ein vergröberter Prinzip-Ablauf: Sie nennt je Phase nur die charakteristische '
               'Hauptwirkung. Nebeneffekte, die in der Elektronik gleichzeitig ablaufen, können davon abweichend an '
               'anderer Stelle im Zyklus auftreten – das ist keine Inkonsistenz, sondern Folge der vereinfachten '
               'Darstellung.'))
    s.append(P('**Eingriff von außen:** Zwischen Phase III und Phase IV kann von außen eingegriffen werden '
               '(AC-Löschung, Stopp, Start). Die Wirkung der Tasten E, G, M, Ü, ST und des Schalters H-R steht im PDF '
               '„Bedienpult und Peripherie“.'))
    s.append(P('**Zeitbedarf je Befehl** (einschließlich Befehlszähler, Befehlsentnahme, Entschlüsselung, Aufstellen '
               'der Befehlsadresse und ggf. Wartezeiten):'))
    s += tbl([['Befehlsart', 'minimale Zeit', 'maximal Op/s'],
              ['Einzelbefehle', '0,5 ms (genauer 5 Wortzeiten = 0,52 ms)', '1900'],
              ['Organisationsbefehle', '0,4 ms (genauer 4 Wortzeiten = 0,416 ms)', '2400'],
              ['Gruppen-/Wiederholungsbefehle', '—', 'bis ca. 9000']], [0.3, 0.5, 0.2], first_bold=True)
    s += h2('7.1 Informationszustand nach den Phasen')
    s.append(P('Die Programmieranleitung (Abschnitt 2.2 „Befehlsschleife“) gibt für jede Phase den Zustand von BZ, AR, '
               'OR und AC an. Bezeichnungen: b = Adresse des abzuarbeitenden Befehls, a = sein Adreßteil, ω = sein '
               'Operationsteil, ω* = Operationsteil nach einer eventuellen Umstellung in Phase II (R-Befehle, bedingte '
               'Sprünge mit erfüllter Bedingung), R₋₁ = Resultat des vorangegangenen Befehls, R = Resultat dieses '
               'Befehls. Vor Phase I steht im BZ die Adresse b des nächsten Befehls.'))
    s += tbl([['nach Phase', 'BZ', 'AR', 'OR', 'AC'],
              ['I', 'in der Quelle nicht angegeben', 'b', 'ω₋₁', 'R₋₁'],
              ['II', 'a', 'b', 'ω', 'R₋₁'],
              ['III', 'b+1', 'a', 'ω*', 'in der Quelle nicht angegeben (bei L=1 gelöscht)'],
              ['IV', 'b+1', 'a', 'ω*', 'R']], [0.13, 0.25, 0.1, 0.1, 0.42], center_cols=(0,))
    s += bullets(['**Wartezeiten:** W₁ liegt zwischen Phase I und Phase II (bis die Sektornummer von b unter dem Kopf '
                  'steht), W₂ zwischen Phase III und Phase IV (Sektornummer von a). Beide sind Vielfache der Wortzeit. '
                  'Im Knotengraphen sind das die Koinzidenztests an den Knoten 5/6 (W₁) sowie 26/27 und 57/64 (W₂).',
                  '**Phase IV** kann mehrere Wortzeiten benötigen: je nach Befehlstyp wird die Operation 1- bis '
                  '32-mal ausgeführt, jede Ausführung kostet eine Wortzeit.',
                  '**Entfall von W₁:** Endet ein GX- oder WX-Befehl unter den Bedingungen des X-Abbruchs, entfällt die '
                  'Koinzidenzprüfung vor Phase II (Knoten 4, ANWEISUNG-002).',
                  '**Befehlsentnahme nach X-Abbruch** (Ergänzung 04.10.2026): Ohne Wartezeit W₁ kommt der nächste '
                  'Befehl nicht aus Zelle b+1, sondern aus der Spur des Befehlszählers und dem Sektor, der in der '
                  'zweiten Wortzeit nach dem Abbruch unter dem Kopf liegt (Sektor der Zusatzzelle plus zwei physische '
                  'Schritte, je +15 oktal; Befehlsliste 4.1.6). AR und BZ bleiben b+1, nach Phase III des entnommenen '
                  'Befehls ist BZ = b+2. Ein Programm muss den Folgebefehl daher in den fälligen Sektor legen '
                  '(Beispiel: Oktaldruck, Programmieranleitung 5.17, Test `bsp_5_17_oktaldruck`). Siehe auch 8.4.',
                  '**Phase I und BZ (abgeleitet):** Liest man „gleichzeitig“ wie im Knotengraphen (Registerwerte vor '
                  'dem Knoten), ergibt Phase I für den BZ den alten AR-Wert + 1 statt b+1. Das ist folgenlos, weil '
                  'Phase II den BZ neu setzt.'])
    s += h2('7.2 Besonderheiten im Phasenablauf')
    s.append(P('Quelle: Programmieranleitung, Abschnitt 2.2.2 bis 2.2.4, 4.2.1 und 4.3.2.10.'))
    s += bullets(['**Phase II:** Bei R-Befehlen wird der Adreßteil im BZ disjunktiv mit den Adreßstellen des AC '
                  'verknüpft und der Operationsteil umgestellt. Bedingte Sprungbefehle werden bei erfüllter Bedingung '
                  'in unbedingte umgestellt. Als bedingte Sprungbefehle gelten Negativsprung, Positivsprung, '
                  'Überlaufsprung, Vergleichersprung 1, 2 und 3 sowie der bedingte Sprung mit Rückkehrabsicht.',
                  '**Phase III:** Eine geforderte AC-Löschung geschieht hier. Bei einem Sprung mit Rückkehrabsicht wird '
                  'der AC disjunktiv mit dem um 1 Bit rechtsverschobenen BZ verknüpft. Ein programmierter Stopp '
                  'erfolgt am Ende der Phase III, die Fortsetzung hängt von der Bedienung ab. Eingabe-Halt- und '
                  'Ausgabe-Halt-Befehle werden einer Sonderbehandlung unterworfen (die Programmieranleitung nennt dazu '
                  'keine Einzelheiten). Zum Ausgabe-Halt gibt die Originaldokumentation (4.3.2.5, Abb. 21) an: Von der '
                  'Stelle unmittelbar nach der Löschanweisung bis zum Beginn der Phase I vergehen mindestens zwei '
                  'Wortzeiten; eine Umstellung der Operation nach Phase III in Überlaufsprung oder Vergleichersprung 3 '
                  'ist bedeutungslos, weil die Sprungbedingung nur in Phase II ausgewertet werden kann (siehe 8.2, '
                  'Ausgabe-/Anwahlbefehl).',
                  '**Nach Phase III:** Bei einem bedingten Sprung mit nicht erfüllter Bedingung folgt nach einer '
                  'Wortzeit Phase I. Bei unbedingten Sprüngen und bedingten Sprüngen mit erfüllter Bedingung folgt die '
                  'Resultatbehandlung in Phase IV, ebenso bei allen anderen Befehlen.',
                  '**Resultatbehandlung:** Sie geschieht nach der Operation in Phase IV. Bei Organisationsbefehlen, die '
                  'diesen Teil der Befehlsschleife nicht durchlaufen, ist sie wirkungslos, auch wenn die Z-Bits R≠0 '
                  'enthalten (z. B. Leer-Befehl 164).',
                  '**Markierte Einzelbefehle** erzeugen zusätzlich einen von drei Vergleichszuständen.',
                  '**Überlauf:** Überlauf bedeutet, dass der Übertrag von z₁ nach z₀ vom Übertrag von z₀ zur nicht mehr '
                  'vorhandenen Maschinenstelle verschieden ist. Er wird nur bei Addition, Subtraktion und bedingter '
                  'Addition bzw. Subtraktion als Einzelbefehl oder als markierter Einzelbefehl ohne '
                  'Resultatbehandlung (R=0, d. h. Z=0 oder 1) eingeschaltet, sowie bei Befehlen, die in solche '
                  'umgestellt werden. Ist im vorhergehenden Befehl ein Überlauf erfolgt und der abzuarbeitende Befehl '
                  'kein Überlaufsprung, wird die Befehlsschleife vor Phase IV unterbrochen (im Knotengraphen: Halt '
                  'wegen Überlauf, Lampe FÜ). Der Überlaufsprung wird dann bereits in Phase II in einen unbedingten '
                  'Sprung umgestellt, gleichzeitig wird der Überlauf gelöscht.',
                  '**Überlauftest nach Ausgabe-Halt und Anwahl:** Bei vorhandenem Überlauf folgt nach der '
                  'Zeichenausgabe bzw. der Anwahl ein Halt wegen Überlauf (Knoten 80/81, Ergänzung 04.10.2026); '
                  'Phase IV läuft bei diesen Befehlen nicht ab, deshalb gibt es keine Resultatbehandlung.'])

    # ---- 8
    s += h1('8 Befehlsarten im Überblick')
    s.append(P('Der Operationsteil BAZ wird bitweise dekodiert; die drei Triaden B, A, Z haben im Sinne eines '
               'analytischen Befehlscodes weitgehend selbständige Bedeutung. Wegen des halbanalytischen Aufbaus ist '
               'nicht jede der 512 Kombinationen sinnvoll belegt, es gibt auch Kombinationen gleicher Wirkung; daher '
               'bleiben etwa 370 verschiedene Befehle. Die vollständige Liste steht im PDF „Einzelbefehlsliste“.'))
    s += h2('8.1 Befehlstyp B')
    s += tbl([['B', 'Befehlstyp', 'Kurzbeschreibung'],
              ['0', 'Organisationsbefehl 1. Art', 'Sprünge, Stopp, Ein-/Ausgabe, Anwahl; je nach Operationsart können '
                                                  'die Phasen I oder IV entfallen'],
              ['1', 'Organisationsbefehl 2. Art', 'wie B = 0, Phasenablauf modifizierbar; Vergleichersprünge'],
              ['2', 'Einzelbefehl', 'Operation bezieht sich auf eine Speicherzelle'],
              ['3', 'Markierter Einzelbefehl', 'wie Einzelbefehl, zusätzlich wird ein Vergleichszustand (V1/V2) '
                                               'erzeugt'],
              ['4', 'Gruppenbefehl (G)', 'Phase IV bezieht sich auf alle 32 Zellen der Spur, zu der die Adresse '
                                         'gehört (Phase IV wird 32-mal durchlaufen)'],
              ['5', 'Verkürzter Gruppenbefehl (GX)', 'wie G, zusätzlich Abbruch bei negativem AC (X-Bedingung)'],
              ['6', 'Wiederholungsbefehl (W)', 'wie G, aber Abbruch bei Sektor 23 (oktal); 1 ≤ n ≤ 32 Wiederholungen; '
                                               'Startadresse mit Sektor 0 wirkt wie G'],
              ['7', 'Verkürzter Wiederholungsbefehl (WX)', 'wie W, zusätzlich X-Bedingung']],
             [0.06, 0.32, 0.62], center_cols=(0,))
    s += h2('8.2 Operationsart A bei Organisations- und Einzelbefehlen')
    s += tbl([['A', 'B = 0', 'B = 1', 'B = 2 (Einzelbefehl)'],
              ['0', 'Unbedingter Sprung', 'Unbedingter Sprung 2. Art', 'Konjunktion in AC: ⟨AC⟩ := ⟨AC⟩ ∧ ⟨a⟩'],
              ['1', 'Eingabebefehl 1. Art (Eingabe-Halt)', 'Eingabebefehl 2. Art',
               'Festkomma-Addition: ⟨AC⟩ := ⟨AC⟩ + ⟨a⟩'],
              ['2', 'Z = 0–3: Unbedingter Stop · Z = 4–7: Sprung mit Rückkehrabsicht', 'wie B = 0 (2. Art)',
               'Festkomma-Subtraktion: ⟨AC⟩ := ⟨AC⟩ − ⟨a⟩'],
              ['3', 'Ausgabe-/Anwahlbefehl', 'Ausgabe-/Anwahlbefehl', 'bedingte Addition/Subtraktion'],
              ['4', 'Negativ-Sprung (⟨AC⟩ < 0)', 'Vergleicher-Sprung 1 (V1 oder V3)', 'Transport: ⟨a⟩ := ⟨AC⟩'],
              ['5', 'Positiv-Sprung (⟨AC⟩ ≥ 0)', 'Vergleicher-Sprung 2 (V2 oder V3)',
               'Z gerade: Konjunktion im Speicher · Z ungerade: R-Befehl (indirektes Lesen)'],
              ['6', 'Z = 0–3: Bedingter Stop (Schalter BS) · Z = 4–7: Bedingter Sprung mit Rückkehrabsicht '
                    '(Schalter SP)',
               'Z = 0–3: Bedingter Stop 2. Art · Z = 4–7: Leer-Befehl', 'Konjunktion im Speicher mit negiertem AC'],
              ['7', 'Überlauf-Sprung', 'Vergleicher-Sprung 3 (nur V3)',
               'Vorzeichenbefehl (bedingte Speicherlöschung) bzw. R-Minuslesebefehl']],
             [0.05, 0.33, 0.28, 0.34], center_cols=(0,), keep=False)
    s += note('hinweis', 'Varianten bei B = 2 (Befehlsliste 4.3; gleiches gilt für die Typen 3 bis 7): '
                         '**A = 3, Z = 2 oder 3:** ist das niederwertigste Bit z₃₂ des AC gleich 1, wird ⟨a⟩ addiert, '
                         'dann folgt die Rechtsverschiebung (Anwendung: Multiplikation, Programmieranleitung 6.1.2 und '
                         '6.2.1); z₃₂ ist hier **nicht** das Löschbit. **A = 7, Z = 2:** Speicherlöschung, wenn '
                         'z₃₂(AC) = 0. **A = 7, Z = 3:** ⟨AC⟩ := 0.')
    s.append(P('**Notation der Sprungbefehle** (Originaldokumentation): Jeder Sprungbefehl ist eine '
               'Fallunterscheidung: nächster Befehl := a, falls die Sprungbedingung erfüllt ist, sonst nächster Befehl '
               ':= ⟨BZ⟩ + 1°. Beim unbedingten Sprung (000) gilt immer a. Die Bedingungen: 040 ⟨AC⟩ < 0; 050 ⟨AC⟩ ≥ 0; '
               '070 Überlauf; 140 Vergleicher 1 oder 3; 150 Vergleicher 2 oder 3; 170 Vergleicher 3 (gilt für alle '
               'Z-Werte). 1° ist die Adresseinheit (Kapitel 4). Bei nicht erfüllter Bedingung wird der Befehl aus Zelle '
               'b+1 geholt, ohne Phase IV und ohne Verschiebung.'))
    s.append(P('**Ausgabe-/Anwahlbefehl (030–037):** Die Anwahl erfolgt mit a = 4700 (Kanal 0: Tastatur oder '
               'SW-Eingabe), 4600 (Kanal 1: Leser 1 oder Stanzer) und 4500 (Kanal 2: Leser 2 oder SW-Ausgabe); sie '
               'bleibt bis zur nächsten Anwahl erhalten. Ist z₁₂ = 0, wird ein Zeichen ausgegeben (Stanzer: Bits '
               'z₁₃–z₂₀, 1 = gelocht; Schreibwerk: nur z₁₄, z₁₅, z₁₇–z₂₀). Fehlt das Ausgabegerät (K0, K3, keine '
               'Anwahl) oder wird eine nicht existierende Anwahl programmiert, stoppt der Rechner mit gesetztem Flag A. '
               'Der AC unterliegt nur der Löschanweisung; Phase IV läuft nicht ab. Die acht Operationsteile 030–037 '
               'unterscheiden sich nur durch die Löschanweisung. Von der Löschanweisung (Phase III) bis zum Beginn der '
               'Phase I vergehen mindestens zwei Wortzeiten (Originaldokumentation 4.3.2.5, Abb. 21; im Interpreter '
               'Wartezeit 0). Eine Umstellung der Operation nach Phase III in Überlaufsprung oder Vergleichersprung 3 '
               'ist für die Wirkung bedeutungslos, weil die Sprungbedingung nur vorher in Phase II ausgewertet wird. '
               'Bei vorhandenem Überlauf folgt nach der Ausgabe bzw. Anwahl ein Halt wegen Überlauf.'))
    s.append(P('**Markierte Einzelbefehle (B = 3):** Zur Wirkung des Einzelbefehls kommt das Setzen des Vergleichers '
               'hinzu. Verglichen wird der Akkumulatorinhalt nach Phase III (bei L = 1 also 0) mit v; dabei ist '
               'v = ⟨a⟩ für A ≤ 3 und v = 0 für A ≥ 4. Am Ende von Phase III werden beide Vergleicher eingeschaltet '
               '(V3); in Phase IV wird nur bei Ungleichheit korrigiert, und zwar stets entgegengesetzt: Bei ⟨AC⟩ < v '
               'bleibt V1 an, bei ⟨AC⟩ > v bleibt V2 an, bei Gleichheit bleiben beide an. Bei Gruppen- und '
               'Wiederholungsbefehlen (B = 4 … 7) gilt dieselbe Operationsart wie bei B = 2, ausgeführt für mehrere '
               'Zellen.'))
    s += h2('8.3 Operationszusatz Z')
    s += tbl([['Z (oktal)', 'Löschbit L', 'R (Wert)', 'Wirkung'],
              ['0', '0', '0', 'keine Löschung, keine Resultatbehandlung'],
              ['1', '1', '0', 'Löschen des AC (in Phase III), keine Resultatbehandlung'],
              ['2', '0', '1', 'keine Löschung, Rechtsverschiebung: ⟨AC⟩ := ½·⟨AC⟩, z₀ := 0'],
              ['3', '1', '1', 'Löschen, Rechtsverschiebung'],
              ['4', '0', '2', 'keine Löschung, Linksverschiebung: ⟨AC⟩ := 2·⟨AC⟩, z₃₂ := 0'],
              ['5', '1', '2', 'Löschen, Linksverschiebung'],
              ['6', '0', '3', 'keine Löschung, zyklische Linksverschiebung (z₀ wird nach z₃₂ übertragen)'],
              ['7', '1', '3', 'Löschen, zyklische Linksverschiebung']], [0.12, 0.14, 0.12, 0.62],
             center_cols=(0, 1, 2))
    s.append(P('Die Resultatbehandlung geschieht nach der Operation in Phase IV und bezieht sich auf den Akkumulator; '
               'bei einigen Organisationsbefehlen wird dieser Teil nicht durchlaufen und ist dann wirkungslos. Das '
               'Löschbit wirkt in Phase III. Kein Verschiebebefehl erzeugt einen Überlauf: ein Überlauf entsteht nur '
               'bei Addition, Subtraktion, bedingter Addition/Subtraktion oder R-Operation, und nur bei R = 0 (Z = 0 '
               'oder 1, ohne Resultatbehandlung; Programmieranleitung 4.3.2.10).'))
    s += h2('8.4 Abbruch bei Gruppen- und Wiederholungsbefehlen')
    s += bullets(['**Normal (G, GX):** nach 32 bearbeiteten Sektoren. **W, WX:** mit der Zelle des Sektors 23 (bei '
                  'Startadresse mit Sektor 0 nach 32 Sektoren). Sektor 23 liegt in der Tabelle in 6.1 auf Position 37, '
                  'ist also die physisch letzte Zelle der Spur (abgeleitet); die Befehlsliste formuliert dasselbe als '
                  '„Abbruch, sobald die Sektornummer 00 erreicht ist“.',
                  '**X-Bedingung (GX, WX):** Der Abbruch erfolgt, wenn der AC negativ wird; Vorzeichen ist z₀, bei '
                  'Rechtsverschiebung (R = 1) stattdessen z₃₂. Operation und Resultatbehandlung werden noch mit einer '
                  'weiteren Zelle (Zusatzzelle) ausgeführt, danach folgt der Abbruch.',
                  'Erfüllen sich normale und X-Bedingung gleichzeitig, hat die normale Bedingung Vorrang (Abb. 10 der '
                  'Originaldokumentation, Befehlsliste 4.1.6).',
                  'Nach einem X-Abbruch wird der nächste Befehl ohne Wartezeit W₁ sofort entnommen: Die Spur ergibt '
                  'sich aus dem Befehlszähler, der Sektor aus der Trommellage in der zweiten Wortzeit nach dem Abbruch '
                  '(in der ersten folgt Phase I). Das ist der Sektor der Zusatzzelle plus zwei physische Schritte (je '
                  '+15 oktal) und im Allgemeinen nicht der Sektor von b+1. Wurde der X-Befehl aus der Zelle b '
                  'entnommen, so hat der Befehlszähler nach Phase III des nächsten Befehls den Inhalt b+2; ist der '
                  'nächste Befehl ein tatsächlich ausgeführter Sprung, wird dieser Inhalt nicht ausgewertet, sonst '
                  'kommt der folgende Befehl aus Zelle b+2.'])
    s += note('achtung', 'Auch im Interpreter, der sonst ohne Zeiten rechnet, hängt das Ergebnis nach einem X-Abbruch '
                         'von der Trommellage ab: Der Folgebefehl muss im fälligen Sektor liegen, nicht in Zelle b+1 '
                         '(Kapitel 9).')

    # ---- 9
    s += h1('9 Hardware und interpretative Abarbeitung')
    s.append(P('Das Gesamtprojekt beschreibt zwei Aspekte: erstens die Hardware mit den in der Elektronik angelegten '
               'Beziehungen, die als Knotenautomat rekonstruiert wurde, und zweitens davon abweichend die Annahmen für '
               'eine interpretative Abarbeitung eines Befehls. Der Knotenautomat hat 80 Knoten (Nummern 1 bis 81, '
               'Nr. 77 entfällt): 37 Anweisungen, 27 Tests, 10 Konnektoren und 6 Phasenzuordnungen für die vier '
               'Phasen. Wichtigste Annahme der interpretativen Abarbeitung: Alle Zeiten sind 0. Zeitliche '
               'Abhängigkeiten werden in ihrer Reihenfolge betrachtet, führen aber nicht zu Wartezeiten; die '
               'Trommeldrehung wird nicht nachgebildet. Die Sektorfolge der Trommel geht dennoch ein: Gruppen- und '
               'Wiederholungsbefehle bearbeiten die Zellen in der physischen Folge (ANWEISUNG-025: a := a+15 mod 40), '
               'und nach einem X-Abbruch bestimmt die Trommellage den Sektor der Befehlsentnahme (8.4).'))
    s.append(P('Der Speicher ist im Interpreter die persistente Trommeldatei (6.4). Der Vollständigkeitstest '
               '`c8205_befehlssweep.py` prüft alle 512 Operationscodes gegen den Knotengraphen; einen Stub gibt es für '
               'keinen Code mehr, nur K3 wird nicht benutzt.'))
    s.append(P('Die Phasen I bis IV entsprechen den Phasenzuordnungs-Knoten des Knotengraphen (Beginn Phase I: Knoten 2, '
               'Phase II: Knoten 8, Phase III: Knoten 15, Phase IV: Knoten 31, 61 und 67). Der Knotengraph wird im PDF '
               '„Knotengraph“ dargestellt; wie man ihn ablaufen lässt, steht im „Testhandbuch“.'))
    s.append(P('**Stopp-Zustände im Knotengraphen:** Ein programmierter Stopp erfolgt am Ende der Phase III. Der '
               'unbedingte Stopp (Knoten 45) setzt nur US, der bedingte Stopp bei gesetztem Schalter BS (Knoten 79) '
               'nur BS. Ein Halt wegen Überlauf (Knoten 30, 46, 58, 66 und 81) setzt weder US noch BS; angezeigt wird '
               'nur FÜ. Die Fortsetzung nach einem Stopp hängt von der Bedienung ab und ist im Knotenautomaten nicht '
               'durch eigene Knoten abgebildet (Endzustände ohne Ausgang).'))
    s.append(P('**Einstiegsknoten nach einem Stopp:** Der Interpreter wertet die Tastenfolge aus, stellt das '
               'Befehlsregister auf und beginnt bei einem Einstiegsknoten (Originaldokumentation 4.3.2.3, Abb. 19; '
               'Einzelheiten im PDF „Bedienpult und Peripherie“):'))
    s += tbl([['Tastenfolge', 'Einstiegsknoten', 'Folge'],
              ['ST, Ü, E ohne M', '19', 'Ausführung des aufgestellten BR, z. B. bei B = 2: Wartezeit W₂, '
                                        'Überlauftest, Phase IV'],
              ['M ohne E, BR = Sprung mit Rückkehrabsicht (025, 027, 125, 127)', '54 (Konnektor 4)',
               'Phase III gilt als abgelaufen; nur Überlauftest und Resultatbehandlung, dann Phase II'],
              ['M ohne E, anderer BR', '19', 'Ausführung des BR ab Knoten 19, z. B. bedingter Sprung mit '
                                             'Rückkehrabsicht 065/067: Knoten 24, 55, 60, dann Phase I']],
             [0.34, 0.16, 0.5])
    s += note('achtung', 'Die Zeitangaben aus Kapitel 6 und 7 (104 µs, Zugriffszeiten, Op/s) beschreiben den realen '
                         'Rechner. Der Interpreter ermittelt weder Wortzeiten noch Wartezeiten; seine „Knotenzahl“ im '
                         'Protokoll ist keine Zeitangabe. Um die zeitoptimale Programmierung (6.2) am Interpreter zu '
                         'prüfen, müsste dieser die Trommelposition (Wortzeitzähler mod 32 und Reihenfolge der '
                         'Magnettrommel-Tabelle) mitführen.')

    # ---- 10
    s += h1('10 Wo steht was? – Verweise')
    s += tbl([['Thema', 'Dokument'],
              ['Tasten, Schalter, Lampen, Kanalanwahl, Geräte', 'PDF „Bedienpult und Peripherie“'],
              ['Alle 512 Operationscodes mit Wirkung', 'PDF „Einzelbefehlsliste“'],
              ['Zeichenkodes (Lochstreifenkode, R 300, CCITT-2)', 'PDF „Kodetabellen“'],
              ['Ablauf der Befehlsverarbeitung als Graph', 'PDF „Knotengraph“ (Tabellenform: „Knotentabellen“)'],
              ['Tests schreiben und Protokolle lesen; Trommel bei Tests', 'PDF „Testhandbuch“'],
              ['Bedienung des Python-Interpreters', 'PDF „Bedienungsanleitung Python-Interpreter“'],
              ['Bausteininterpretationssystem BIS (Dezimalzahlen, Gleitkomma, Tetraden, Kleines Eingabeprogramm)',
               'PDF „BIS“'],
              ['Assembler c82ass', 'PDF „Assembler-Dokumentation“'],
              ['Projektüberblick, Dokumentenlandkarte', 'PDF „Projektüberblick“']], [0.55, 0.45])
    return s


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
    ap = argparse.ArgumentParser(description='Erzeugt C8205-Rechnerbeschreibung_A4.pdf')
    ap.add_argument('ziel', nargs='?', default=None)
    ap.add_argument('--stand', default=L.heute(), help='TT.MM.JJJJ; Vorgabe: Erzeugungsdatum')
    ap.add_argument('--md', default=None, help='Ordner mit den .md-Quellen; Vorgabe: markdown-dateien/ in der Projektwurzel')
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    wurzel = finde_wurzel(here)
    mddir = a.md or os.path.join(wurzel, 'markdown-dateien')
    ABB_DIR[0] = os.path.join(mddir, 'abbildungen')
    if a.ziel:
        out = a.ziel
    else:
        out = os.path.join(wurzel, 'PDF', 'C8205-Rechnerbeschreibung_A4.pdf')
    set_stand(a.stand)
    quellen = [(n, L.lese_version(os.path.join(mddir, n))) for n in QUELLEN]    # bricht ab, wenn eine Versionszeile fehlt
    L.COVER = dict(
        titel='Rechnerbeschreibung',
        untertitel='Aufbau, Register, Maschinenwort, Zahlendarstellung, Magnettrommel und Befehlszyklus des Cellatron C 8205',
        art='BESCHREIBUNG', bereich='RECHNER UND REGELWERK', quellen=quellen, stand=a.stand,
        pdf_name=os.path.basename(out), erzeugt_mit=os.path.basename(__file__),
        beschreibung='Dieses Dokument beschreibt den Rechner selbst: wie er aufgebaut ist, wie ein Maschinenwort und ein '
                     'Befehl aussehen, wie die Magnettrommel organisiert ist und wie ein Befehl in vier Phasen abgearbeitet '
                     'wird. Es richtet sich an Leser, die das Projekt nicht im Detail verfolgt haben, und ersetzt keines der '
                     'Fachdokumente, sondern führt in sie ein.')
    st = head_with_block(merge_intro(story()))
    d = L.Doc(out)
    d.title = 'Rechnerbeschreibung'
    d.author = 'C8205-Interpreter-Projekt'
    d.subject = 'Beschreibung · Quellen: ' + ', '.join('%s %s' % q for q in quellen)
    d.multiBuild(st, canvasmaker=L.NumberedCanvas)
    print('geschrieben:', out)


if __name__ == '__main__':
    main()
