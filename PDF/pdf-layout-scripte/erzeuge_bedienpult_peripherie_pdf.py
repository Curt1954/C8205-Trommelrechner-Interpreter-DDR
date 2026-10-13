# -*- coding: utf-8 -*-
"""erzeuge_bedienpult_peripherie_pdf.py -- erzeugt C8205-Bedienpult_und_Peripherie_A4.pdf (redaktionell, nach
C8205-Interpreter-PDF.md; Bausteine aus pdflib.py).

Quellen: C8205-Interpreter-Bedienpult_mit_Schaltern.md und C8205-Interpreter-Lochstreifenleser.md (enthaelt auch
Stanzer und Schreibwerk); ergaenzend Datenstruktur_und_Verarbeitungseinheiten.md (Flags E, A, FE) und Kodetabellen.md.

Aufruf:  python3 erzeuge_bedienpult_peripherie_pdf.py [ZIEL.pdf] [--stand TT.MM.JJJJ] [--md ORDNER_MIT_DEN_QUELLEN]
Seite 1 ist das Deckblatt (PDF.md Abschnitt 4), Seite 2 enthaelt Lesehinweise und Inhaltsverzeichnis (4.4).
Vorgabe: PDF/C8205-Bedienpult_und_Peripherie_A4.pdf in der Projektwurzel
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

ABB_DIR = ['.']          # Ordner der Abbildungen (<md-Ordner>/abbildungen), main() setzt ihn

QUELLEN = ['C8205-Interpreter-Bedienpult_mit_Schaltern.md',
           'C8205-Interpreter-Lochstreifenleser.md']
STAND = L.heute()


def set_stand(stand):
    """Stand = Erzeugungsdatum (PDF.md 4.3); gleicher Wert auf Deckblatt und in der Fusszeile."""
    global STAND
    STAND = stand
    L.STAND = stand
    L.FOOTER_LEFT = 'C8205-Interpreter-Projekt · Stand ' + stand


set_stand(STAND)
L.HEADER_TITLE = 'C 8205 – Bedienpult und Peripherie'
L.HEADER_LEGEND = 'Taste/Schalter = Handlung · Flag = gespeicherter Zustand · Lampe = Anzeige (gleicher Name, eine Sache)'


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


# ------------------------------------------------------------------ Abbildung 1 (schematisch, gezeichnet)
def gruppe(d, x, y, w, h, title, lines=(), fill=BLUE_BG, stroke=BLUE, fs=7.2):
    d.add(Rect(x, y, w, h, fillColor=fill, strokeColor=stroke, strokeWidth=0.9))
    n = len(lines) + (1 if title else 0)
    ty = y + h / 2 + (n - 1) * 5.2
    if title:
        d.add(String(x + w / 2, ty - 2.5, title, fontName='Helvetica-Bold', fontSize=fs + 0.5, textAnchor='middle',
                     fillColor=INK))
        ty -= 10.4
    for ln in lines:
        d.add(String(x + w / 2, ty - 2.5, ln, fontName='Helvetica', fontSize=fs, textAnchor='middle', fillColor=INK))
        ty -= 10.4


def abb1():
    d = Drawing(FRAME_W, 214)
    GRN = colors.HexColor('#F3F4F6')
    w = FRAME_W
    # Lampenfeld oben
    gruppe(d, 0, 176, w, 36, 'Lampenfeld: zeigt die Flags',
           ['E · A · T · SW · K1 · K2 · K3 · FE · FÜ · BS · US · V1 · V2 · H · SP    (darunter: Befehlsregister AR/OR)'],
           fill=GRN, stroke=MUTED)
    # Zeile 2: Netzschalter, H-R, Tasten, SW
    gruppe(d, 0, 118, 92, 50, 'Netzschalter', ['Netz ein/aus', 'Stromversorgung'])
    gruppe(d, 100, 118, 110, 50, 'Schalter H-R', ['H (Halt) | R (Rechnen)', 'gegenseitig verriegelt'])
    gruppe(d, 218, 118, 200, 50, 'Tasten E · G · M · Ü · ST',
           ['E Einzelschritt · G Generallöschen · M Manuell', 'Ü Übertrag · ST Start', 'E, G, M, Ü nur bei H wirksam'])
    gruppe(d, 426, 118, w - 426, 50, 'Schalter SW', ['T | SW', 'Tastatur / Schreibwerk', '(bei K0)'])
    # Zeile 3: Kanaltasten, Selektoren
    gruppe(d, 0, 60, 300, 50, 'Kanalauswahltasten',
           ['K0 Tastatur / SW-Eingabe · K1 Leser 1 / Stanzer', 'K2 Leser 2 / SW-Ausgabe · K3 frei'])
    gruppe(d, 308, 60, w - 308, 50, 'Selektoren (einrastend)',
           ['SP: bedingter Sprung mit Rückkehr', 'BS: bedingter Stopp'])
    # Zeile 4: Eingabetasten, Rückseite, Stanzer
    gruppe(d, 0, 0, 262, 52, 'Eingabetasten',
           ['0 … 9 · + · − · , · . · : · B · D · ZR · WM · IS · IB', '(nur bei K0, Schalter SW auf T, Eingabe-Halt)'],
           fill=ORANGE_BG, stroke=ORANGE)
    gruppe(d, 270, 0, 150, 52, 'Rückseite der Pult-Einheit',
           ['Bahnsperrenschalter (6):', '0001 · 0040 · 0100 · 0200 · 0400 · 1000'], fill=GRN, stroke=MUTED, fs=6.8)
    gruppe(d, 428, 0, w - 428, 52, 'Am Stanzer', ['Schalter LS', '(Motor-Dauerlauf)'], fill=GRN, stroke=MUTED)
    return d


def story():
    s = []
    # ---- Seite 1: Deckblatt (zeichnet pdflib.NumberedCanvas, PDF.md Abschnitt 4)
    s += [Spacer(1, 1), PageBreak()]
    # ---- Seite 2: Lesehinweise, danach Inhaltsverzeichnis (PDF.md 4.4)
    s.append(Paragraph('Lesehinweise', ST['h1']))
    s.append(P('**Quellen und Stand:** C8205-Interpreter-Bedienpult_mit_Schaltern.md und C8205-Interpreter-Lochstreifenleser.md '
               '(enthält auch Stanzer und Schreibwerk); ergänzend Datenstruktur_und_Verarbeitungseinheiten.md (Flags E, A, FE) '
               'und Kodetabellen.md. Die Bahnsperrenschalter beschreibt das PDF „Rechnerbeschreibung“.'))
    s.append(P('**Zusammenhang mit dem Interpreter:** Der Python-Interpreter kennt keine Schalter zum Anfassen. Die '
               'Bedienhandlungen werden in der Tastenfolge einer Testdatei geschrieben (Kapitel 8); Leser, Stanzer und '
               'Schreibwerk werden durch Dateien bzw. das Terminal nachgebildet (PDF „Bedienungsanleitung '
               'Python-Interpreter“).'))
    s.append(P('Legende dieses Dokuments', 'h2'))
    s += tbl([['Zeichen', 'Bedeutung'],
              ['Schalter / Taste / Flag', 'Bedienelement, gespeicherter Zustand und Lampe tragen denselben Namen und sind '
                                          'eine Sache.'],
              ['Hinweis (blauer Balken)', 'Ergänzung, die das Verständnis erleichtert.'],
              ['Achtung (orangefarbener Balken)', 'Stelle, an der man sich leicht irrt oder an der Hardware und '
                                                  'Interpreter abweichen.'],
              ['Grafiken', 'Schematisch bzw. neu gezeichnet nach den Originalunterlagen; sie zeigen die Zusammenhänge, '
                           'nicht das Aussehen des Geräts.']], [0.3, 0.7])
    s.append(Paragraph('Inhaltsverzeichnis', ST['h1']))
    s.append(make_toc())
    s.append(PageBreak())

    # ---- 1
    s += h1('1 Das Bedienpult im Überblick')
    s.append(P('Im Bedienpult sind Schalter, Eingabetasten und Lampen angeordnet. Der Rechner reagiert als Hardware auf den '
               'Zustand seiner Flags; ein Mensch beeinflusst den Rechner über die Schalter. Die Schalterzustände werden in '
               'gleichnamigen Flags als 0/1-Werte gespeichert. Beispiel: Wird der Schalter BS gesetzt, kann der Rechner das '
               'auswerten, wenn ein entsprechender Befehl es abtestet; dass BS gesetzt ist, steht im Flag BS und leuchtet in '
               'der Lampe BS.'))
    s += L.figure(abb1(), 'Abbildung 1: Bedienelemente des Pults (schematisch). Die Anordnung ist frei gewählt; sie zeigt, '
                          'welche Gruppen es gibt. B und D sind Sondertasten für den Programmbaustein-Ansprung des BIS und '
                          'werden nicht weiter benötigt.')
    s.append(P('Das Bedienpult heißt in den Originalunterlagen „Tastatur-Anzeige-Einheit“. Oben liegt das Lampenfeld. '
               'Darunter stehen links die Kanalauswahltasten K0 bis K3, paarweise untereinander (K0 über K1, K2 über K3), und '
               'rechts die Schalter SP, BS und LS sowie die Umschalttaste T-SW (beschriftet „SW“). Unten liegt die Tastatur. '
               'Auf dem Foto tragen die Schalter rechts die Beschriftung „BSt“ und „LSt“; dieses Regelwerk schreibt '
               'durchgehend „BS“ und „LS“.'))
    s += L.bild(os.path.join(ABB_DIR[0], 'C8205-Abb-Bedienpult_Foto.png'),
                'Abbildung 2: Das Bedienpult des C 8205 (Foto, Originalunterlagen)', max_hoehe=250)
    s.append(P('**Lampenfeld.** Die obere Reihe (große Lampen) zeigt die Zustände E, A, T, SW, K1, K2, K3, FE, FÜ, BS, US, R, '
               'H, B und N; T und SW gehören zur Anzeige des Kanals K0. Die Lampe B ist die Betriebsanzeige, die Lampe N zeigt '
               'an, dass die Netzstromversorgung anliegt; unter N sitzt ein Schlüsselschalter. Die untere Reihe zeigt das '
               'Befehlsregister in Triaden zu je drei Lampen mit den Gewichten 4, 2, 1: vier Triaden Adreßregister AR '
               '(oktale Wertigkeiten 1000, 100, 10, 1) und drei Triaden Operationsregister OR (B, A, Z). Rechts davon zeigen '
               'die Lampen V 1 und V 2 den Vergleicherstand. Die Bedeutung der Zustandslampen steht bei den Flags in '
               'Datenstruktur_und_Verarbeitungseinheiten.md.'))
    s += L.bild(os.path.join(ABB_DIR[0], 'C8205-Abb-Lampenfeld.png'),
                'Abbildung 3: Lampenfeld des Bedienpults mit Gewichten und Wertigkeiten der Befehlsregisteranzeige '
                '(neu gezeichnet nach Abb. 6 „Lampenfeld“ der Bedienungsanleitung des C 8205)', max_hoehe=230)
    s.append(P('**Tastenanordnung.** Abbildung 4 zeigt die Tasten nach der Zeichnung „Tastatur des C 8205“; die '
               'Kanalauswahltasten K0 bis K3 stehen hier nach dem Foto. Gestrichelt umrandet sind die drei Gruppen, die die '
               'Zeichnung ausweist:'))
    s += bullets(['**Tasten mit Rollensperre:** E, M, G, Ü,',
                  '**Schalter mit Rollensperre:** T und SW,',
                  '**Tasten mit Entriegelung und Rollensperre:** B, +, 1, 3, 5, 7, 9, „.“, „:“, D, −, 0, 2, 4, 6, 8, „,“, ZR, '
                  'IS, IB und WM.'])
    s.append(P('H und R (gegeneinander verriegelt, s. Schalter H-R) und ST (elektronisch verriegelt) gehören keiner Gruppe '
               'an. Die Zeichnung erklärt die Begriffe „Rollensperre“ und „Entriegelung“ nicht.'))
    s += L.bild(os.path.join(ABB_DIR[0], 'C8205-Abb-Tastatur_Bedienpult.png'),
                'Abbildung 4: Tastatur des Bedienpults mit den Tastengruppen (neu gezeichnet nach der Zeichnung „Tastatur des '
                'C 8205“ und dem Foto)', max_hoehe=260)
    s += tbl([['Gruppe', 'Elemente', 'Wirkt auf'],
              ['Stromversorgung', 'Netzschalter', 'Betriebsbereitschaft (Voraussetzung jedes Betriebs)'],
              ['Betriebsart', 'Schalter H-R', 'Flag H; Halt bzw. Rechnen'],
              ['Eingriffstasten', 'E, G, M, Ü, ST', 'Register BR/AR/OR/AC/BZ, Flags'],
              ['Eingabeart K0', 'Schalter SW (Stellung T/SW)', 'Flags T und SW'],
              ['Kanalwahl', 'K0, K1, K2, K3', 'Flags K1–K3, T/SW'],
              ['Selektoren', 'SP, BS', 'Flags SP, BS'],
              ['Zeicheneingabe', '0…9, +, −, „,“, „.“, „:“, B, D, ZR, WM, IS, IB',
               'Adressregister AR (bei aufgestelltem Eingabe-Halt)'],
              ['Speicherschutz', 'Bahnsperrenschalter (rückseitig)', 'Schreibschutz der Trommel'],
              ['Stanzer', 'Schalter LS', 'Motor-Dauerlauf des Stanzers']], [0.2, 0.42, 0.38], first_bold=True)

    # ---- 2
    s += h1('2 Netzschalter und Schalter H-R')
    s.append(P('Der Netzschalter schaltet die Stromversorgung des Rechners ein; das ist Voraussetzung für jeden Betrieb. '
               'Jeder Test setzt voraus, dass der Rechner eingeschaltet ist.'))
    s.append(P('Der Schalter H-R (Halt – Rechnen) besteht aus zwei gegeneinander verriegelten Tasten H und R; immer nur '
               'eine der beiden ist gedrückt.'))
    s += bullets(['**Stellung H:** Der Rechner geht in den Halt-Zustand (Stopp-Zustand) über. Durch Einrasten von H kann die '
                  'Befehlsabwicklung unterbrochen werden; unabhängig vom Zeitpunkt des Eingriffs im Phasenablauf wird erst '
                  'nach der nächsten Phase III gestoppt.',
                  '**Stellung R:** Die Sperre ist aufgehoben, die Abarbeitung des Programms wird fortgesetzt.'])
    s.append(P('Die Tasten E, M, G, Ü und der Schalter SW lassen sich nur bei Stellung H betätigen. Die Taste ST ist '
               'elektronisch verriegelt (Kapitel 3).'))

    # ---- 3
    s += h1('3 Die Tasten E, G, M, Ü, ST und der Schalter SW')
    s.append(P('Diese Tasten greifen in den Phasenablauf ein; der Eingriff ist zwischen Phase III und Phase IV möglich '
               '(vgl. PDF „Rechnerbeschreibung“). Bis auf ST sind sie nur bei Schalter H-R in Stellung H wirksam. Die '
               'Tabelle fasst die Wirkung zusammen; darunter stehen Einzelheiten.'))
    s += tbl([['Taste', 'Name', 'Bedingung', 'Wirkung'],
              ['E', 'Einzelschritt', 'nur bei H',
               'Befehlsfolge in Einzelschritten abarbeiten (Phase IV und I, bei Loslassen Phase II und III, dann Halt)'],
              ['G', 'Generallöschen', 'nur bei H',
               'beseitigt Stopp und Überlauf, löscht das Befehlsregister (BR = „0000 000“ = unbedingter Sprung nach 0000); '
               'wählt K0 an; AC und BZ unverändert'],
              ['M', 'Manuell', 'nur bei H',
               'OR := OR ∨ 025 (Sprung mit Rückkehrabsicht); nach G ergibt sich „0000 025“; nach einem Stop-Befehl siehe 7.6'],
              ['Ü', 'Übertrag', 'nur bei H',
               'AR := 7777 (oktal), OR := OR ∨ 240 (Transport); nach einem Stop-Befehl entsteht 26Z (7.6)'],
              ['ST', 'Start', 'nur bei US oder BS',
               'OR := OR ∨ 240; AR unverändert; US wird gelöscht; nach einem Stop-Befehl entsteht 26Z (7.6)'],
              ['SW', 'Schalter T/SW', 'nur bei H', 'unterscheidet bei K0 zwischen Tastatur- und Schreibwerkeingabe']],
             [0.08, 0.15, 0.15, 0.62], first_bold=True)

    s += h2('3.1 Taste E – Einzelschritt')
    s.append(P('Mit E kann eine Befehlsfolge in Einzelschritten abgearbeitet werden. Beim Niederdrücken werden entsprechend '
               'dem Phasenablauf Phase IV und Phase I freigegeben; solange E gedrückt bleibt, steht der Automat vor Phase II. '
               'Beim Loslassen werden Phase II und Phase III durchlaufen, danach stoppt die Abarbeitung wieder. Erneutes '
               'Anschlagen löst den nächsten Schritt aus. Bei verkürzten Gruppen- bzw. Wiederholungsbefehlen mit X-Abbruch '
               'wird bei gedrückter E-Taste das Einschalten von Phase II nicht verhindert. Bei gedrückter M-Taste verhindert '
               'E die Befehlsentnahme in Phase II.'))

    s += h2('3.2 Taste G – Generallöschen')
    s.append(P('G beseitigt einen programmierten Stopp sowie einen eventuellen Überlauf und löscht das Befehlsregister; '
               'dessen Einstellung „0000 000“ bedeutet „unbedingter Sprung nach Speicherplatz Null“. Zusätzlich wird Kanal K0 '
               'angewählt. Auf Akkumulator- und Befehlszählerinhalt hat G keinen Einfluss.'))
    s += note('hinweis', 'G kann eingerastete Schalter mechanisch nicht bedienen und ändert deshalb die Flags SP und BS nicht '
                         '(ebenso wenig H).')

    s += h2('3.3 Taste M – Manuell')
    s.append(P('M verknüpft den Inhalt des Operationsregisters disjunktiv mit der Operation 025 (Sprung mit Rückkehrabsicht). '
               'Nach vorherigem G ergibt sich damit „0000 025“. Bei gedrückter M-Taste und Betätigung von E wird die '
               'Befehlsentnahme in Phase II verhindert.'))
    s.append(P('Nach einem unbedingten Stopp (Befehl 02Z, Z<4) entsteht aus 02Z ∨ 025 die Operation 025 (Z = 0, 1) oder 027 '
               '(Z = 2, 3). Da Phase III des Stop-Befehls bereits abgelaufen ist, wird von dieser Operation nur die '
               'Resultatbehandlung ausgeführt (Linksverschiebung des AC, bei 027 zyklisch); die Sprungoperation selbst '
               '(Sichern der Rückkehradresse im AC) und die Löschanweisung gehören zu Phase III und entfallen. Anschließend '
               'wird der nächste Befehl aus der Speicherzelle entnommen, die im Adreßteil des Stop-Befehls angegeben ist '
               '(Phase II mit AR).'))
    s += note('hinweis', 'Für den Interpreter hat M nur die zwei Stellungen „gedrückt“ und „losgelassen“. Das Antippen M in '
                         'einer Tastenfolge ist gleichbedeutend mit M gedrückt und sofort losgelassen (Beispiel Fall 4 in 7.1: '
                         'H, M, R).')

    s += h2('3.4 Taste Ü – Übertrag')
    s.append(P('Ü ist nur bei Schalter H-R in Stellung H wirksam, sonst ohne Wirkung. Die Taste stellt im Adressregister die '
               'Adresse 7777 (oktal) ein und verknüpft den Inhalt des Operationsregisters disjunktiv mit der Operation 240 '
               '(Transport, wenn OR vorher 000 war, z. B. nach G). Nach einem Stop-Befehl entsteht stattdessen die Operation '
               '26Z: Phase IV läuft dann mit dem Befehl „7777 26Z“ (7.6).'))

    s += h2('3.5 Taste ST – Start')
    s.append(P('ST verknüpft den Inhalt des Operationsregisters disjunktiv mit der Operation 240. Die Taste ist elektronisch '
               'verriegelt: Sie wirkt nur, wenn der Rechner im Zustand „Bedingter Stopp“ oder „Unbedingter Stopp“ steht. Nach '
               'einem Stop-Befehl (02Z bzw. 06Z, Z<4) entsteht so die Operation 26Z (Konjunktion mit negiertem '
               'Akkumulatorinhalt); die Fortsetzung verläuft wie bei dieser Operation (7.6).'))
    s += note('hinweis', 'Für den Interpreter ist ST nicht an Stellung H gebunden; ohne US/BS bleibt ST ohne Wirkung. Wirkung: '
                         'OR := OR ∨ 240, AR bleibt, US wird gelöscht. BR ist danach aufgestellt und wird durch E oder R '
                         'ausgeführt.')

    s += h2('3.6 Schalter SW (Stellungen T / SW)')
    s.append(P('Der Schalter SW (Stellungen T und SW, daher auch „T-SW“) unterscheidet beim Anwahlkanal K0 zwischen '
               'Tastatureingabe und Schreibwerkeingabe. Drücken von SW setzt das Flag SW; Lösen (Stellung T) löscht das Flag '
               'SW und setzt stattdessen das Flag T – T und SW sind alternativ. Bei Benutzung des Schreibwerks zur Eingabe '
               'muss SW gedrückt sein, Tastatureingabe geht nur bei Stellung T. Der Schalter selbst hat keinen Einfluss auf die '
               'Anwahl eines peripheren Gerätes.'))

    # ---- 4
    s += h1('4 Eingabetasten')
    s.append(P('Die Eingabetasten umfassen die Zeichen 0…9, +, −, „,“, „.“, „:“, B, D, ZR, WM, IS und IB. Sie sind nur '
               'betätigbar, wenn'))
    s += bullets(['Kanal K0 angewählt ist,', 'Schalter SW in Stellung T steht und',
                  'ein Eingabe-Halt-Befehl im Befehlsregister steht.'])
    s.append(P('**Wirkung:** Ist ein Eingabebefehl aufgestellt, stoppt der Automat nach Phase III. Beim Anschlagen wird die '
               'dem Zeichen zugeordnete Eingabeverschlüsselung (gemäß R-300-Code, Kodetabellen Tabelle 1) disjunktiv mit dem '
               'Inhalt des Adressregisters verknüpft; danach wird die Sperre durch Umstellung des Eingabebefehls aufgehoben.'))
    s.append(P('Zeitlich (Originaldokumentation 4.3.2.2): Mit dem Niederdrücken der Taste finden Paritätsprüfung und '
               'Auswertung der Operationsumstellungsbedingung statt; mit dem Loslassen beginnt die Fortsetzung der '
               'Befehlsschleife mit der disjunktiven Übernahme des Zeichens ins Adreßregister. Die Sonderzeichen „Irrung '
               'Zeichen“ und „Transportloch im Vorspann“ entfallen bei Tastatur- und Schreibwerkeingabe.'))
    s.append(P('Sonderbedeutung einzelner Tasten:'))
    s += tbl([['Taste', 'Bedeutung'],
              ['ZR', 'Zwischenraum, identisch mit Leerzeichen'],
              ['WM', 'Wortmarke, identisch mit dem Code für Tabulator (TAB)'],
              ['IS', 'Irrung Satz (gemäß Codetabelle)'],
              ['IB', 'Irrung Block (gemäß Codetabelle)'],
              ['B', '(nicht der Buchstabe B) Sondertaste für Programmbaustein-Ansprung des BIS, nicht weiter benötigt'],
              ['D', '(nicht der Buchstabe D) Sondertaste für Programmbaustein-Ansprung des BIS, nicht weiter benötigt']],
             [0.14, 0.86], first_bold=True)
    s += note('achtung', 'Die Eingabetasten gehören nicht in die Tastenfolge einer Testdatei; sie werden als K0-Eingabe '
                         'während des Ablaufs bedient (Kapitel 8).')

    # ---- 5
    s += h1('5 Kanalauswahl')
    s.append(P('Jede Kanalauswahltaste wählt einen Kanal gleichzeitig für Ein- und Ausgabe aus, wobei Eingabe- und '
               'Ausgabegerät unterschiedlich sein können; ob der Eingabe- oder der Ausgabeaspekt genutzt wird, bestimmt der '
               'abgearbeitete Befehl. Maßgebend ist der Moment des Drückens: Das entsprechende Flag wird auf 1 gesetzt, die '
               'Flags der anderen drei Kanäle auf 0.'))
    s.append(P('**Besonderheit K0:** Diese Taste hat kein eigenes Flag, sondern die zwei Subflags T (Tastatur) und SW '
               '(Schreibwerk statt Tastatur) sind ihr zugeordnet. Beim Drücken von K0 ist der Zustand des Schalters SW '
               '(Kapitel 3.6) maßgeblich: Ist SW gedrückt, wird beim Drücken von K0 das Flag SW gesetzt, sonst das Flag T. '
               'Anstelle der Tasten kann die Kanalanwahl auch per Befehl erfolgen; er berücksichtigt den Schalterstatus SW '
               'analog.'))
    s += tbl([['Taste', 'Anwahlverschlüsselung (programmiert)', 'Gerät'],
              ['K0', '4700 030', 'Tastatureingabe* / Schreibwerkeingabe*'],
              ['K1', '4600 030', 'Leser 1 / Lochbandstanzer'],
              ['K2', '4500 030', 'Leser 2 / Schreibwerkausgabe'],
              ['K3', '4400 030', 'frei (kein Gerät zugeordnet)']], [0.12, 0.38, 0.5], first_bold=True, code_cols=(1,))
    s.append(P('* Eingabe bei K0 je nach Stellung des Schalters SW (T: Tastatur, SW: Schreibwerk).'))

    # ---- 6
    s += h1('6 Selektoren SP und BS, Schalter LS')
    s.append(P('SP und BS sind einrastende Schalter: Gedrückt bleiben sie eingerastet, bis ein Mensch sie löst; das '
               'gleichnamige Flag ist 1, solange der Schalter eingerastet ist, und 0, wenn er gelöst ist. Zur Definition einer '
               'Tastenfolge genügt: Schalter gedrückt → Flag := 1, Schalter gelöst → Flag := 0.'))
    s.append(P('Die Stellungen werden als Bedingungen für die Befehle „Bedingter Sprung mit Rückkehrabsicht“ (SP) und '
               '„Bedingter Stopp“ (BS) interpretiert; die Bedingung ist erfüllt, wenn der entsprechende Schalter gesetzt ist. '
               'Bei ausgeführtem Bedingten Stopp bleibt der Automat nach Phase III stehen; durch Lösen des Schalters BS kann '
               'die Sperre aufgehoben werden.'))
    s.append(P('**Schalter LS** (Lochbandstanzer) ist nur für den physischen Rechner von Bedeutung; bei der interpretativen '
               'Nachbildung der Befehlsverarbeitung spielt er keine Rolle. Bei gesetztem LS läuft der Motor des '
               'Lochbandstanzers ständig (sinnvoll bei Stanzvorgängen in kurzen Abständen unterhalb der '
               '3-Sekunden-Abschaltverzögerung); bei nicht gesetztem LS läuft der Motor nicht, ein Stanzvorgang beginnt dann '
               'erst nach Ablauf der Einschaltverzögerung (Hochlauf).'))
    s += note('achtung', '„SW“ bezeichnet im Zusammenhang mit LS keinen zweiten Schalter, sondern die Stellung SW des '
                         'Schalters T-SW. Auf die Schreibwerk**ausgabe** über K2 hat diese Stellung keinen Einfluss; die '
                         'Ausgabe über K2 ist jederzeit möglich. Die Stellung SW betrifft nur die Eingabeseite (Zeicheneingabe '
                         'über das Schreibwerk an Kanal K0).')
    s.append(P('**Bahnsperrenschalter:** Sie sind räumlich und bedientechnisch am Bedienpult angesiedelt (rückseitig an der '
               'Tastatur-Anzeige-Einheit), werden aber inhaltlich von der Magnettrommel ausgewertet. Die vollständige '
               'Beschreibung steht daher im PDF „Rechnerbeschreibung“.'))

    # ---- 7
    s += h1('7 Typische Bedienabläufe (Eingriffsmöglichkeiten)')
    s += h2('7.1 Betriebszustände beseitigen: US, BS, FÜ, FE')
    s.append(P('**Zustand „Unbedingter Stopp“ (US)** kann geändert werden durch:'))
    s += L.numbered(['Schalter H-R → H; Taste G – Programm wird unterbrochen.',
                     'Schalter H-R → H; Taste G; Taste ST – US wird übergangen (Sprung zur Adresse des US-Befehls).',
                     'Schalter H-R → H; Taste Ü; Schalter H-R → R – US wird übergangen (Speicherplatz 7777 oktal wird '
                     'angesprungen/geändert).',
                     'Schalter H-R → H; Taste M; Schalter H-R → R – Sprung zur Adresse des US-Befehls, Akkumulatorinhalt wird '
                     'der Resultatbehandlung unterworfen.'])
    s.append(P('**Zustand „Bedingter Stopp“ (BS)** verhält sich wie US (gleiche Fälle 1 bis 4), zusätzlich: Lösen des Schalters '
               'BS. Das Lösen von BS ist ein eigener Weg aus dem Stopp und führt wie eine nicht erfüllte Schalterbedingung '
               'über den Überlauftest und eine Wortzeit zu Phase I. Bei Fall 4 ergibt 06Z ∨ 025 (= 065 oder 067) einen '
               'bedingten Sprung mit Rückkehrabsicht, der ohne Phase IV und ohne Verschiebung mit dem nächsten Befehl '
               '(Phase I) weiterläuft.'))
    s.append(P('**Zustand „Überlauf“ (FÜ)** wird beseitigt durch:'))
    s += L.numbered(['Schalter H-R → H; Taste G – Programm wird unterbrochen.',
                     'Schalter H-R → H; Taste E gedrückt halten; Taste G; Taste E loslassen – nur der Überlauf wird gelöscht '
                     '(Generallöschen bei gedrückter Einzelschritt-Taste).'])
    s.append(P('**Zustand „Fehler bei Eingabe“ (FE)** kann nur durch Generallöschen (G) aufgehoben werden.'))

    s += h2('7.2 Akkumulator nach Speicherplatz 7777 transportieren')
    s += L.numbered(['Schalter H-R in Stellung H', 'Taste G anschlagen', 'Taste Ü anschlagen', 'Taste E anschlagen'])
    s.append(P('Der Inhalt des Akkumulators wird nach dem Speicherplatz 7777 (oktal) transportiert. Der in den Schritten 2 '
               'und 3 aufgestellte Befehl „7777 240“ wird durch Schritt 4 ausgeführt.'))

    s += h2('7.3 Befehlszähler in den Akkumulator holen')
    s += L.numbered(['Schalter H-R in Stellung H', 'Taste G anschlagen', 'Taste M gedrückt lassen',
                     'Taste E anschlagen', 'Taste M loslassen', 'Taste E anschlagen'])
    s.append(P('Danach steht im Akkumulator die um 2 Einheiten erhöhte Adresse des nächsten abzuarbeitenden Befehls (meist ein '
               'Sprung in ein Druckprogramm). Wird in Schritt 4 E zweimal angeschlagen, steht die um 3 Einheiten erhöhte '
               'Adresse im Akkumulator, Speicherplatz 0002 wird als nächster Befehl aufgestellt. Alternativ kann im '
               'Haltzustand durch Niederdrücken von E (außer bei X-Befehlen) der Befehlszählerstand im Adressteil des '
               'Befehlsregisters sichtbar gemacht werden.'))
    s += note('achtung', 'Schritt 6 ist „Taste E anschlagen“, nicht „Schalter H-R → R“ (Wortlaut der Originaldokumentation). '
                         'Der Ansprung eines Druckprogramms nach einer Programmunterbrechung endet dagegen mit „SP lösen“ und '
                         'R (siehe PDF „BIS“).')

    s += h2('7.4 Manueller Ansprung einer Speicherzelle')
    s.append(P('**Ansprung des Platzes 0000:**'))
    s += L.numbered(['Schalter H-R → H', 'Taste G', 'Schalter H-R → R'])
    s.append(P('**Ansprung eines beliebigen Speicherplatzes n:**'))
    s += L.numbered(['Schalter H-R → H', 'Taste G', 'Taste M gedrückt halten', 'Taste E n-mal anschlagen',
                     'Taste M loslassen', 'Schalter H-R → R'])

    s += h2('7.5 Das „Kleine Eingabeprogramm“')
    s.append(P('Das Kleine Eingabeprogramm ermöglicht die Eingabe von Befehlen, Zahlen und Hilfsadressen über ein einfaches '
               'Leseprogramm. Es liegt auf Spur 0, wird über Speicherplatz 0002 angesprungen, ist bei gesetztem Sperrschalter '
               'gegen Überschreiben gesichert und nur über eine Serviceeinheit bei völlig gelöschtem Speicher nutzbar.'))
    s.append(P('Es verarbeitet nur die Zeichen 0, 1, Punkt, Doppelpunkt und Zwischenraum ZR. Worte werden entsprechend ihrer '
               'dualen Darstellung eingegeben (Beginn beim ersten von Null verschiedenen Bit möglich) und im Akkumulator '
               'aufgebaut. „.“ und „:“ dienen als Schlusszeichen:'))
    s += bullets(['„:“ speichert die aufgebaute Information als Befehl auf Speicherplatz 7723 (Leitbefehl).',
                  '„.“ führt den Leitbefehl aus (bei Transportbefehl „a1 a2 a3 a4 240“ wird das zuvor aufgebaute Wort nach '
                  'Zelle a1 a2 a3 a4 abgespeichert) und erhöht dessen Adresse um 1, sofern kein Sprungbefehl vorliegt.',
                  '„ZR“ löscht die im Akkumulator aufgebaute Information, solange noch kein Schlusszeichen gegeben wurde.'])

    s += h2('7.6 Fortsetzung nach einem Stopp')
    s.append(P('Ein programmierter Stopp (unbedingter Stop 1. Art: A = 2 und Z<4; bedingter Stop bei gesetztem Schalter BS) '
               'unterbricht die Befehlsschleife am Ende der Phase III, also **vor der Wartezeit W₂**. Die Lampe US bzw. BS '
               'zeigt ihn an. Ein Halt wegen Überlauf zeigt nur die Lampe FÜ. Weil Phase III des Stop-Befehls bereits '
               'abgelaufen ist, wirken die Tasten nicht auf Phase III, sondern bilden einen neuen Befehl, der ab Phase IV '
               'ausgeführt wird:'))
    s += tbl([['Bedienung', 'Operationsteil (OR des Stop-Befehls 02Z, Z<4)', 'Ablauf'],
              ['`ST`', 'OR ∨ 240 = 26Z (Konjunktion mit negiertem AC, ⟨a⟩ := (¬AC) ∧ ⟨a⟩)',
               'Wartezeit W₂, Überlauftest, Phase IV mit ⟨AR⟩ 26Z, dann Phase I'],
              ['`H Ü R`', 'wie ST, zusätzlich AR := 7777', 'wie ST, Phase IV mit „7777 26Z“'],
              ['`H M R`', 'OR ∨ 025 = 025 oder 027 (Sprung mit Rückkehrabsicht)',
               'Überlauftest, Phase IV nur mit Resultatbehandlung (Linksverschiebung, bei 027 zyklisch), Wartezeit W₁, '
               'Phase II: nächster Befehl aus der im Adreßteil des Stop-Befehls angegebenen Zelle (AR)'],
              ['Lösen des Schalters BS (nur bedingter Stopp)', '–',
               'wie nicht erfüllte Schalterbedingung: Überlauftest, eine Wortzeit, Phase I']], [0.2, 0.34, 0.46])
    s += bullets(['Nach G (OR = 000) ergibt dieselbe Tastenkombination eine andere Operation: Ü und ST führen zu 240 '
                  '(Transport), M zu 025.',
                  'Beim bedingten Stopp (06Z) ergibt ST/Ü ebenfalls 26Z (aus der Rechnung 06Z ∨ 240 abgeleitet; das Original '
                  'nennt nur den unbedingten Stopp). H M R ergibt 065 oder 067 und läuft wie ein nicht ausgeführter Sprung mit '
                  'Phase I weiter.',
                  'Nach einem Halt wegen Überlauf zeigt Abb. 19 der Originaldokumentation keine Fortsetzung durch ST, Ü oder '
                  'M; der Überlauf wird durch G beseitigt (7.1).',
                  'Im Interpreter werden diese Folgen als Tastenfolge vorab ausgewertet (Kapitel 8). Einstiegsknoten: ST, Ü, E '
                  '→ Knoten 19; M mit Sprung mit Rückkehrabsicht → Knoten 54.'])

    # ---- 8
    s += h1('8 Bedienhandlungen im Test: die Token der Tastenfolge')
    s.append(P('Eine Tastenfolge beschreibt die Bedienhandlungen am Pult, die den Ausgangszustand vor dem Eintritt in den '
               'Befehlsablauf festlegen (PDF „Durchführung eines Tests“). Sie besteht aus Token, die durch Leerzeichen '
               'getrennt in einer oder mehreren Zeilen stehen; `#` beginnt einen Kommentar bis zum Zeilenende. Groß- und '
               'Kleinschreibung ist gleichgültig. Die Wirkungen sind die der oben beschriebenen Tasten und Schalter.'))
    s += tbl([['Token', 'Bedeutung und Wirkung'],
              ['`H`', 'Schalter H-R auf H: Flag H := 1'],
              ['`R`', 'Schalter H-R auf R: Flag H := 0; zusätzlich US := 0. Der Befehlsablauf beginnt (Startpunkte: s. unten)'],
              ['`G`', 'Generallöschen (nur bei H): alle Flags außer H, T, BS und SP := 0 (BS und SP sind eingerastete Schalter, '
                      'G kann sie mechanisch nicht lösen); AR := 0000, OR := 000 (BR = „0000 000“); K0 wird angewählt '
                      '(T := 1, bei gedrücktem Schalter SW: SW := 1); BZ und AC bleiben unverändert; danach US := 1 (wird '
                      'durch ST oder R wieder gelöscht)'],
              ['`M+` (auch `M-drücken`, `M-gedrückt-halten`)', 'M gedrückt halten (nur bei H): OR := OR ∨ 025'],
              ['`M-` (auch `M-loslassen`)', 'M loslassen. Wurde unter gehaltenem M kein E betätigt, bleibt BR = ⟨AR⟩ 025 '
                                            'aufgestellt. Wurde mindestens ein E betätigt, entfällt der Beitrag 025 im OR '
                                            '(übrige Anteile, z. B. von Ü, bleiben)'],
              ['`M`', 'Antippen, gleichbedeutend mit `M+` und sofort danach `M-`'],
              ['`E`', 'Einzelschritt (nur bei H). Ohne M: Phase IV und I, dann Phase II und III, danach Halt (Halt-Punkt vor '
                      'Knoten 19). Steht der Automat nach einem E unter M vor Phase II, beginnt E bei Phase II. Unter '
                      'gehaltenem M: Phase II entfällt; BZ := BZ+1, AR := BZ, der AC enthält im Adressfeld den Wert BZ+1 '
                      '(übrige Stellen 0)'],
              ['`Ü`', 'Übertrag (nur bei H, sonst ohne Wirkung): AR := 7777, OR := OR ∨ 240; BR ist aufgestellt und noch nicht '
                      'ausgeführt'],
              ['`ST`', 'Start (nicht an H gebunden, aber nur bei US oder BS wirksam, sonst ohne Wirkung): OR := OR ∨ 240, AR '
                       'unverändert, US := 0; BR ist aufgestellt und noch nicht ausgeführt'],
              ['`SW=1` (auch `SW+`, `SW-drücken`)', 'Schalter SW gedrückt: Flag SW := 1, T := 0'],
              ['`SW=0` (auch `SW-`, `SW-loslassen`)', 'Schalter SW gelöst: Flag SW := 0, T := 1'],
              ['`BS=1`, `SP=1` (auch `BS+`, `SP+`)', 'Selektorschalter gedrückt und eingerastet: gleichnamiges Flag := 1'],
              ['`BS=0`, `SP=0` (auch `BS-`, `SP-`)', 'Selektorschalter gelöst: gleichnamiges Flag := 0'],
              ['`K0` … `K3`', 'Kanalauswahltaste: Flag des gewählten Kanals := 1, die Flags der anderen drei Kanäle := 0 '
                              '(K0: T oder SW je nach Schalter SW)']], [0.3, 0.7], keep=False)
    s.append(P('**Hinweise:**'))
    s += bullets(['`SW` muss vor `G` gesetzt werden, weil `G` daraus für K0 das Flag T oder SW ableitet.',
                  'Die Eingabetasten (0…9, +, − usw.) gehören nicht in die Tastenfolge; sie werden als K0-Eingabe während des '
                  'Ablaufs bedient.',
                  'Eine Tastenfolge wird bis zur Wirkung der dadurch aufgestellten Instruktion vorausinterpretiert. Sie muss '
                  'den Ausgangszustand vollständig definieren und endet mit `R` oder im Halt (H gesetzt). Endet sie ohne `R`, '
                  'bleibt der Rechner im Halt; das Ergebnis ist der Zustand nach dem letzten Schritt.',
                  '**Startpunkte nach `R`:** Ist keine Instruktion in BR aufgestellt (z. B. nach `H G R` oder '
                  '`H G M+ E … E M- R`), beginnt der Ablauf bei Konnektor B mit dem in BZ stehenden Wert. Ist BR aufgestellt '
                  'und noch nicht ausgeführt (nach `Ü`, `ST`, `M` ohne E oder nach `E` ohne M), beginnt der Ablauf bei '
                  'Knoten 19 (Ausführung von BR). Ausnahme: Ist der durch `M` (ohne E) aufgestellte BR ein Sprung mit '
                  'Rückkehrabsicht (B = 0 oder 1, A = 2, Z ≥ 4: 025, 027, 125, 127), gilt Phase III als abgelaufen; der '
                  'Ablauf beginnt dann bei Konnektor 4 (Knoten 54) und führt nur die Resultatbehandlung aus.',
                  '**Makro `#STARTE n`:** steht in einer Testdatei für die Tastenfolge `H G M+ E … E M- R` mit n Anschlägen '
                  'von `E`, also den Ansprung des Speicherplatzes n (7.4).',
                  '**Tastenfolge als Argument von `#INTERRUPT`:** Dieselben Token dürfen auch hinter `#INTERRUPT H` stehen '
                  'und unterbrechen dann den Programmlauf zwischen zwei Befehlen. Endet eine solche Folge mit `R` oder `ST`, '
                  'läuft das Programm weiter, sonst endet der Test im Halt.'])

    # ---- 9
    s += h1('9 Peripherie: Lochstreifenleser')
    s.append(P('Hardwarebeschreibung des Lochstreifenlesers 303 am Rechner C 8205. „Lochband“ und „Lochstreifen“ sind '
               'Synonyme; hier heißt das Gerät „Lochstreifenleser“ (Kürzel LL) bzw. „Leser“.'))
    s += tbl([['Merkmal', 'Angabe'],
              ['Bezeichnung', 'Lochbandleser 303'],
              ['Hersteller', 'Secura-Werke'],
              ['Vorgänger', 'Leser 301 (der 303 war dessen Nachfolger)'],
              ['Bandbreite', 'normalerweise 8-spurige Lochbänder'],
              ['Bauform', 'mit Gehäuse als Auftischgerät oder gehäuselos zum Einbau in die Gerätefrontblende'],
              ['Einsatz', 'u. a. am Computer „Cellatron C8205“ sowie an Papierverarbeitungsmaschinen'],
              ['Ausführung „Doppel-Lochbandleser 303“', 'Am Rechner hängt Leser 1 an Kanal K1 und Leser 2 an Kanal K2'],
              ['Geschwindigkeit', '130 Zeichen/s (Standardleser des C 8205; mechanisch, Metallbürsten)']],
             [0.3, 0.7], first_bold=True)
    s += note('hinweis', 'Anschluss: Leser 1 hängt an Kanal K1, Leser 2 an Kanal K2, Stanzer 1 an Kanal K1. Kanal K3 ist '
                         'beim C 8205 „frei“ (kein Gerät zugeordnet). K0 ist Tastatur- bzw. Schreibwerk-Eingabe, kein '
                         'Lochstreifenleser.')
    s.append(P('**Fehler und Flag FE.** FE („Fehler bei Eingabe“) ist ein logischer Fehler, also ein Fehler in den '
               'einzugebenden Daten; er kann bei Ausgabe nicht auftreten. Alle anderen Fehler bei Ein- und Ausgabe sind '
               'physische Fehler (Fehler der Geräteelektronik) und werden nicht in Flags des Rechners abgebildet. Eine Zeile '
               'mit gerader Zahl gelochter Spuren (kein gültiges Zeichen, z. B. „Irrung Zeichen“) ist ein solcher '
               'logischer Fehler: Flag FE wird gesetzt und der Rechner stoppt. Ausgenommen sind Zeilen ohne Datenlochung '
               '(Vorspann), die der Leser überliest.'))

    s += h2('9.1 Lochbild und Kode')
    s.append(P('Die Tabelle 1 selbst (Lochbilder, Spaltenbedeutungen, Konsistenzprüfung, Sonderzeilen) steht im PDF '
               '„Kodetabellen“. Hier die Kurzfassung. Die Spuren heißen w v u p 8 Tr 4 2 1; Tr ist die Transportlochung ohne '
               'Information. Die acht Datenspuren haben folgende Bitwerte im Lochbild:'))
    s += tbl([['Spur', '1', '2', '4', '8', 'p', 'u', 'v', 'w'],
              ['Bitwert', '1', '2', '4', '10₈', '20₈', '40₈', '100₈', '200₈']],
             [0.18] + [0.1025] * 8, first_bold=True, center_cols=tuple(range(1, 9)))
    s += bullets(['**Parität:** Alle gültigen Zeichen haben eine ungerade Zahl gelochter Datenspuren (p ergänzt). Eine Zeile '
                  'mit gerader Zahl gelochter Spuren ist kein gültiges Zeichen und beim Lesen ein Gerätefehler (Flag FE wird '
                  'gesetzt, der Rechner stoppt). „Irrung Zeichen“ wird bei der Eingabe von der Paritätsprüfung ausgeschlossen '
                  'und übersprungen.',
                  '**Leser:** Maßgebend ist die Spalte „Eingabe Adresse“, ein Wert des Lesers, der ihn sendet; der Rechner '
                  'muss ihn interpretieren. **Stanzer:** Maßgebend ist die Spalte „Ausgabe-Adresse“, ein Wert des Rechners, '
                  'der ihn sendet; die Stanzer-Elektronik muss ihn interpretieren. Über den Stanzer sind alle Zeichen der '
                  'Spalte „Ausgabe-Adresse“ ausgebbar, alle anderen nicht.',
                  '**„Irrung Zeichen“ / „Irrung Satz“:** Der Rechner benutzt sie nicht; sie dienen der menschlichen '
                  'Datenerfassung auf Lochstreifen.',
                  '**Sprung-Umstellung:** gehört zur Befehlsdefinition, nicht zur Leserdefinition.'])

    s += h2('9.2 Zeichenlage Klein-/Großbuchstaben')
    s += bullets(['Um. KB und Um. GB bedeuten „Umschalten KB“ bzw. „Umschalten GB“.',
                  'Die Zeichenlage Klbuch/Gbuch existiert physisch nur am Schreibwerk (SW): je nachdem, ob der Umschalter der '
                  'Schreibmaschine eingerastet ist oder nicht; von dort kommt sie auch.',
                  'Der Rechner steht nach dem Einschalten auf KB und merkt sich die Zeichenlage übergreifend, d. h. alle Leser '
                  'werden damit beurteilt – es sei denn (und das ist die Regel), über den Leser kommt explizit ein '
                  'Umschaltzeichen. Da immer nur ein Kanal gleichzeitig aktiv sein kann, entsteht kein Problem.',
                  'Zeicheneingabe über das SW: K0 muss angewählt (durch Taste oder Befehl) und der Schalter SW gedrückt sein. '
                  'Wird an der Schreibmaschine die Umschalttaste KB oder GB gedrückt, bekommt der Rechner auch das als Zeichen '
                  'zugestellt. Umschaltzeichen werden nur eingegeben, wenn der schreibende Mensch es vorsieht; es gibt keine '
                  'Automatik.',
                  'Bei der Ausgabe durch den Rechner werden Umschaltzeichen nur ausgegeben, wenn das Programm es vorsieht; es '
                  'gibt keine Automatik.',
                  '„Irrung Zeichen“ und „Irrung Satz“ sind in beiden Zeichenlagen gleich.'])

    s += h2('9.3 Ablauf einer Zeicheneingabe')
    s += L.numbered(['Im Rechenwerk wird ein Eingabebefehl ausgeführt („Eingabe-Halt“, Oberbegriff für zwei '
                     'Eingabebefehlsarten, deren Unterschied hier nicht relevant ist).',
                     'Er veranlasst den Leser, dessen Kanal angewählt ist (Kx mit x ≠ 0), eine Position (Lochungszeile) vom '
                     'Lochstreifen zu lesen, sofern einer eingelegt ist. Während dieses Vorgangs ist das Flag E gesetzt '
                     '(„=1, wenn ein Eingabebefehl aufgestellt ist“).',
                     'Ist kein Lochstreifen eingelegt, wartet der Leser unendlich; der Rechner bleibt mit gesetztem Flag E '
                     'stehen (kein Fehler).',
                     'Ist ein Lochstreifen eingelegt, werden die Lochungen gemäß Tabelle 1 gelesen und in eine '
                     'Eingabeadresse umgerechnet; diese ist ein Wert des Lesers, der ihn sendet.',
                     'Die Eingabeadresse wird an das Rechenwerk übergeben, das mit ihrer Hilfe den Eingabebefehl abschließt '
                     '(das Wie gehört zur Befehlsdefinition).',
                     'Damit ist die Zeicheneingabe abgeschlossen; Flag E wird gelöscht, und der nächste Befehl kann '
                     'verarbeitet werden.'])
    s.append(P('Wie das Zeichen intern im Speicher kodiert wird, hängt davon ab, ob zeicheneingabe-übergreifend vorher ein '
               'Zeichen Klbuch oder Gbuch gelesen wurde (Zeichenlage rechnerweit, Anfang KB).'))
    s.append(P('**Bedienung am Leser: Streifen einlegen und Streifenende**'))
    s += bullets(['Der Lochstreifen kann schon eingelegt werden, wenn der Rechner noch gar keine Eingabe anfordert. Er bleibt '
                  'dann einfach stehen und wartet, bis das der Fall ist.',
                  'Fordert der Rechner eine Eingabe an und ist kein Streifen eingelegt, bleibt der Rechner mit gesetztem '
                  'Flag E stehen; das ist kein Fehler. Wird der Streifen dann eingelegt, beginnt die Eingabe sofort; '
                  'Transportlochungen (Zeilen ohne Datenlochung) werden überlesen.',
                  'Der Streifen wird so lange transportiert, wie Eingabebefehle vorliegen, bis er aus dem Leser herausfällt. '
                  'Liegen keine Eingabebefehle vor, bleibt der Streifen mittendrin stehen.'])

    # ---- 10
    s += h1('10 Peripherie: Lochstreifenstanzer')
    s += tbl([['Merkmal', 'Angabe'],
              ['Bezeichnung', 'Lochbandstanzer Cellatron C8021 (Kürzel LS; Kürzel-Kollision mit dem Schalter LS, Kapitel 12)'],
              ['Bauform', 'Einbaugerät'],
              ['Anzahl am Rechner', 'höchstens 1 Stanzer'],
              ['Kanal', 'K1 (gemeinsam mit Leser 1); nur ein Stanzer vorhanden, anders als bei den zwei Lesern'],
              ['Geschwindigkeit', '50 Zeichen/s (maximale Stanzgeschwindigkeit); ein Zeichen dauert 20 ms'],
              ['Kode', '8-Kanal-Code (Tabelle 1 / R-300-Kode), Paritätslochung im 5. Bit (Spur p, Bitwert 20₈ = 2⁴)']],
             [0.25, 0.75], first_bold=True)
    s.append(P('Bei voller Leistung können nach der Originaldokumentation (4.3.2.5) zwischen zwei aufeinanderfolgenden '
               'Ausgabe-Halt-Befehlen höchstens 4,5 Trommelumdrehungen liegen.'))
    s += note('hinweis', 'Die Rechnung aus 20 ms und 32 × 104 µs = 3,3 ms je Umdrehung ergäbe etwa 6 Umdrehungen; die Angabe '
                         'des Originals ist unverändert übernommen.')
    s.append(P('Der Stanzer erzeugt die Lochungen in den Spuren w v u p 8 Tr 4 2 1 (w höchstwertig), gemäß Spalte '
               '„Ausgabe-Adresse C8205 oktal“ der Kodetabellen. Ausgebbar sind ausschließlich die dort enthaltenen Zeichen.'))
    s.append(P('**Motorsteuerung:** Der Stanzermotor läuft nicht dauerhaft, sondern läuft automatisch an, sobald ein Zeichen '
               'ausgegeben werden soll, und schaltet nach einer Abschaltverzögerung (3 Sekunden, Kapitel 6) automatisch wieder '
               'ab, wenn keine weiteren Zeichen folgen. Bei kleinen Ausgabelücken würde das zu ständigem Ein- und Ausschalten '
               'führen; dem wirkt der Schalter LS entgegen (eingerastet: Motor läuft dauerhaft weiter).'))
    s.append(P('**Vorspann:** Ein Vorspann von ca. 5 cm sollte gestanzt werden, damit der fertige Lochstreifen gut in einen '
               'Leser eingelegt werden kann.'))
    s.append(P('**Fehlerbehandlung:** FE ist ein rein logischer Eingabefehler und kann bei Ausgabe nicht auftreten; '
               'physische Fehler der Stanzer-Elektronik werden nicht in Flags abgebildet.'))

    s += h2('10.1 Ablauf einer Zeichenausgabe')
    s.append(P('Der Ablauf entspricht dem der Eingabe (9.3), jedoch mit Flag A statt E.'))
    s += L.numbered(['Ein Ausgabebefehl wird im Rechenwerk ausgeführt („Ausgabe-Halt“). Das Zeichen wird, sobald der '
                     '1-Zeichen-Puffer frei ist, in den Puffer übertragen; der Rechner wartet bis dahin. Die Ausgabe aus dem '
                     'Puffer über das Gerät läuft danach unabhängig von der Zentraleinheit, die Befehlsschleife wird '
                     'gleichzeitig fortgesetzt.',
                     'Kanal K1 muss angewählt sein; während des Vorgangs ist Flag A gesetzt („=1, wenn ein Ausgabebefehl '
                     'aufgestellt ist“).',
                     'Ist kein Streifen eingelegt bzw. zu Ende, kann der Stanzer das Zeichen im Puffer nicht abarbeiten; der '
                     'Rechner bleibt dann beim nächsten Ausgabe-Halt, der den belegten Puffer nicht füllen kann, mit gesetztem '
                     'Flag A stehen (kein Fehler) – analog zum Leser.',
                     'Ist ein Streifen eingelegt, wird die Lochung gemäß Tabelle 1 (Spalte Ausgabe-Adresse) für das '
                     'auszugebende Zeichen gestanzt.',
                     'Flag A wird mit der Umstellung des Ausgabebefehls gelöscht, also sobald das Zeichen im '
                     '1-Zeichen-Puffer liegt, nicht erst nach Abschluss des Stanzens; der nächste Befehl kann verarbeitet '
                     'werden.',
                     'Die zu stanzende Bitkombination ist identisch mit den Bits z₁₃ bis z₂₀ des Adreßteils; mit 1 besetzte '
                     'Bits werden gelocht, mit 0 besetzte bleiben ungelocht (Lochkanal 1 = z₂₀, 2 = z₁₉, 3 = z₁₈, 4 = z₁₇, '
                     '5 = z₁₆, 6 = z₁₅, 7 = z₁₄, 8 = z₁₃). Damit kann jeder beliebige Kode mit höchstens 8 Kanälen '
                     'realisiert werden.',
                     'Gibt es für den Ausgabe-Halt keine passende Anwahl, stoppt der Rechner mit gesetztem Flag A (Lampe A '
                     'leuchtet).'])
    s += note('achtung', 'Beim Interpreter gilt Wartezeit = 0: Puffer und Stanzvorgang werden nicht zeitlich nachgebildet.')

    # ---- 11
    s += h1('11 Peripherie: Schreibwerk (Ausgabe)')
    s.append(P('Hardwarebeschreibung der Schreibwerk-Ausgabe. Die Schreibwerk-**Eingabe** (Tastatur- bzw. SW-Zeicheneingabe '
               'über Kanal K0) ist in Kapitel 3.6, 4 und 5 beschrieben; hier geht es um die Ausgabeseite und, am Ende, um '
               'die Tastatur des Schreibwerks.'))
    s += tbl([['Merkmal', 'Angabe'],
              ['Bezeichnung', 'Schreibwerk (SW), für alphanumerische Ein- und Ausgabe'],
              ['Geschwindigkeit', 'max. 10 Zeichen/s; voll ausgenutzt, wenn zwischen zwei aufeinanderfolgenden '
                                  'Ausgabe-Halt-Befehlen nicht mehr als 28 Trommelumdrehungen liegen (Original 4.3.2.5)'],
              ['Kanal (Ausgabe)', 'K2 (gemeinsam mit Leser 2 für die Eingabe)']], [0.25, 0.75], first_bold=True)
    s += note('hinweis', 'Die Rechnung aus 100 ms und 3,3 ms je Umdrehung ergäbe etwa 30 Umdrehungen; die Angabe des Originals '
                         'ist unverändert übernommen.')
    s.append(P('**Kanal und Schalter SW.** Die Ausgabe über Kanal K2 ist unabhängig von der Stellung des Schalters T-SW '
               'jederzeit möglich; dieser Schalter wirkt sich ausschließlich auf die Eingabeseite von Kanal K0 aus (Kapitel 6).'))
    s.append(P('**KB/GB-Gedächtnis bei der Ausgabe.** Bei der Eingabe sind „Umschaltung KB“ (Kleinbuchstabe) und '
               '„Umschaltung GB“ (Großbuchstabe) Zeichen wie jedes andere (9.2). Bei der Ausgabe dagegen besitzt das '
               'Schreibwerk für diese Umschaltung ein Gedächtnis: KB und GB sind zueinander alternativ, genau ein Zustand ist '
               'jeweils aktiv.'))
    s += bullets(['Beim Netz-Einschalten wird dieser Zustand (KB oder GB) – auch für den Interpreter – zufällig gesetzt. '
                  'Davon getrennt ist die Zeichenlage der Eingabe, die der Rechner nach dem Einschalten auf KB hat; beide '
                  'Zustände sind voneinander unabhängig.',
                  'Die Ausgabe über K2 verwendet die jeweils aktuelle KB/GB-Stellung, um das auszugebende Zeichen als Klein- '
                  'oder Großbuchstabe darzustellen.',
                  'Der Zustand wird durch Ausgabe eines Zeichens mit entsprechender Ausgabe-Adresse umgeschaltet: '
                  'Ausgabe-Adresse `117x` (oktal) schaltet KB ein, `057x` (oktal) schaltet GB ein. x steht für eine '
                  'beliebige Oktalziffer (0–7).'])
    s += h2('11.1 Ablauf einer Zeichenausgabe')
    s.append(P('Analog zu 9.3 beim Leser und 10.1 beim Stanzer, mit Kanal K2 und Flag A:'))
    s += L.numbered(['Ein Ausgabebefehl wird im Rechenwerk ausgeführt („Ausgabe-Halt“). Das Zeichen geht, sobald der '
                     '1-Zeichen-Puffer frei ist, in den Puffer; die Ausgabe über das Schreibwerk läuft dann unabhängig von der '
                     'Zentraleinheit, die Befehlsschleife wird gleichzeitig fortgesetzt.',
                     'Kanal K2 muss angewählt sein; während des Vorgangs ist Flag A gesetzt.',
                     'Das Zeichen wird gemäß Tabelle 1 geschrieben, in der aktuellen KB/GB-Stellung. Maßgeblich sind nur sechs '
                     'Bits des Adreßteils: z₁₄, z₁₅ und z₁₇ bis z₂₀ (Spuren v u 8 4 2 1, nach dem in der Schreibmaschine '
                     'verdrahteten Kode); z₁₃ (Spur w) und z₁₆ (Spur p) werden nicht ausgewertet. Zwei Ausgabe-Adressen, die '
                     'sich nur in diesen beiden Bits unterscheiden, erzeugen dasselbe Zeichen. Gedruckt werden können nur '
                     'Zeichen, die auf der Schreibwerktastatur vorhanden sind. Die meisten zulässigen Adressen sind doppelt '
                     'belegt; die Unterscheidung erfolgt über KB/GB. Bei 10 Zeichen/s dauert ein Zeichen 100 ms.',
                     'Flag A wird mit der Umstellung des Ausgabebefehls gelöscht, also sobald das Zeichen im '
                     '1-Zeichen-Puffer liegt; der nächste Befehl kann verarbeitet werden.'])
    s.append(P('**Kein Wartezustand:** Anders als bei Leser und Stanzer gibt es kein „Papier eingelegt / nicht eingelegt“. Das '
               'Schreibwerk ist immer bereit; fehlt das Papier, schreibt es auf die Andruckwalze des Papiertransports.'))
    s.append(P('**Zeichen ohne Schreibwerk-Entsprechung:** Ist die Ausgabe-Adresse kein darstellbares Zeichen (z. B. „Irrung '
               'Zeichen“, „Transport“), passiert nichts.'))
    s.append(P('**Kein Ausgabegerät angewählt:** Ist für den Ausgabe-Halt kein Ausgabegerät angewählt (K0, K3, keine Anwahl) '
               'oder wird eine nicht existierende Anwahl programmiert, stoppt der Rechner mit gesetztem Flag A (Lampe A '
               'leuchtet). Die Anwahl bleibt bei eingeschaltetem Rechner erhalten, bis eine neue sie löscht.'))
    s.append(P('**Fehlerbehandlung:** Es gibt keine Fehlerbehandlung im Rechner. Tritt ein (physischer) Fehler auf, sind Ein- '
               'und Ausgabe blockiert, und der Rechner bleibt stehen, sobald er einen Ein- oder Ausgabebefehl ausführen will. '
               'Wie bei Leser und Stanzer werden physische Fehler nicht in Flags abgebildet.'))

    s += h2('11.2 Tastatur des Schreibwerks (Eingabe)')
    s.append(P('Die Tastatur des Schreibwerks ist die Eingabeseite des Schreibwerks. Bei den Tasten mit zwei Zeichen steht oben '
               'das Zeichen der Großbuchstabenlage, unten das der Kleinbuchstabenlage; „KB“ und „GB“ schalten die Lage um. '
               'Die Taste mit zwei Kreisen ist unbenutzt und nicht eingabefähig. Die Taste mit £ (oben) und $ (unten), dem '
               'Pfundzeichen, ist eingabefähig.'))
    s += L.bild(os.path.join(ABB_DIR[0], 'C8205-Abb-Tastatur_Schreibwerk.png'),
                'Abbildung 5: Tastatur des Schreibwerks (neu gezeichnet nach Abb. 14 „Schreibwerktastatur“ und der Zeichnung '
                '„Tastatur des Schreibwerkes“ der Originalunterlagen). Grau: Taste ohne Funktion', max_hoehe=250)
    s.append(P('Die Beschriftungen der Zeichnung und die Bezeichnungen der Bedienelemente in Abb. 13 „Schreibwerk“ der '
               'Originalunterlagen (Nummer in Klammern) entsprechen einander so:'))
    s += tbl([['Taste', 'Bezeichnung in der Zeichnung', 'Bezeichnung in Abb. 13'],
              ['ganz links oben (senkrechter Strich)', 'Randversteller', 'Randstellertaste (70)'],
              ['oben rechts, Pfeil nach rechts', 'Rücktaste', 'Rücktaste (49)'],
              ['oben rechts, Minuszeichen', 'Tab. löschen', 'Tabulator löschen (48)'],
              ['rechts neben der Taste mit = und +', 'Tab. setzen', 'Tabulator setzen (47)'],
              ['hohe Taste rechts', 'WRZL', 'Wagenrücklauf mit Zeilenschaltung (50)'],
              ['hohe Taste links', '–', 'Wagenrücklauf ohne Zeilenschaltung (71)'],
              ['unten links, Pfeil nach oben', 'Zeilenschaltung-ZV', 'Zeilenschalttaste (74)'],
              ['lange Taste unten', 'Leertaste-ZWR', 'Leertaste (54)'],
              ['unten rechts, Pfeil nach links', 'Tab. Auslösung', 'Tabulatortaste (53)'],
              ['KB', 'KB', 'Umschalttaste für Kleinbuchstaben (73)'],
              ['GB', 'GB', 'Umschalttaste für Großbuchstaben (52)']], [0.36, 0.28, 0.36])
    s.append(P('Zwei weitere Bedienelemente sitzen als Rädchen neben der Tastatur und sind in der Abbildung nicht dargestellt: '
               'der Farbbandumschalter (72) links und der Anschlagregler (51) rechts.'))

    # ---- 12
    s += h1('12 Gleiche Namen, verschiedene Dinge')
    s.append(P('Namensgleichheiten werden dokumentiert, nicht aufgelöst. Die Tabelle nennt die Fälle, in denen dasselbe Wort in '
               'diesem Dokument zwei Dinge bezeichnet.'))
    s += tbl([['Name', 'Bedeutungen'],
              ['E', 'Flag E („=1, wenn ein Eingabebefehl aufgestellt ist“; für den Leser relevant) und Taste E '
                    '(Einzelschritt am Bedienpult): getrennte Namensdomänen (Flag vs. Taste)'],
              ['SW', 'Schalter SW (Stellungen T/SW), Flag SW, Stellung SW dieses Schalters und das Schreibwerk selbst; '
                     'auf die Ausgabe über K2 hat der Schalter keinen Einfluss'],
              ['LS', 'Schalter LS am Pult (Motor-Dauerlauf) und Kürzel LS für den Lochbandstanzer (Bezeichnung vs. Schalter)'],
              ['w, v, u, p', 'Spurbezeichnungen der Lochspuren und gleichlautende Zeichen w, v, u, p in Tabelle 1 (Klbuch): '
                             'andere Domäne (Lochspur vs. Zeichen)'],
              ['1, 2, 4, 8', 'Spuren 1, 2, 4, 8 und die Ziffern 1, 2, 4, 8 der Tabelle sowie die BCD-Zahlen (Stanzzonen 0, 11, '
                             '12 und Ziffernwerte)'],
              ['Leser 1 / Leser 2', 'Kanalnamen und „Doppel-Lochbandleser“ (am Rechner Leser 1 an K1, Leser 2 an K2); für die '
                                    'Leserdefinition ohne Belang'],
              ['Transport', 'Tabellenzeile „Transport“ (Relikt, nie benutzt), „Transport Vorspann“ (tatsächlicher Transport '
                            'ohne Datenlochung), Spur Tr (Transportlochung) und der Transportmechanismus des Lesers '
                            '(Reibrad/Zahnrad): verschiedene Dinge mit demselben Wortstamm'],
              ['B, D', 'Sondertasten für den Programmbaustein-Ansprung des BIS, nicht die Buchstaben B und D'],
              ['KB / GB', 'Eingabe: Zeichen wie jedes andere; Ausgabe: Gedächtnis des Schreibwerks (zwei voneinander '
                          'unabhängige Zustände, Kapitel 11)']], [0.18, 0.82], first_bold=True)
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
    ap = argparse.ArgumentParser(description='Erzeugt C8205-Bedienpult_und_Peripherie_A4.pdf')
    ap.add_argument('ziel', nargs='?', default=None)
    ap.add_argument('--stand', default=L.heute(), help='TT.MM.JJJJ; Vorgabe: Erzeugungsdatum')
    ap.add_argument('--md', default=None, help='Ordner mit den .md-Quellen; Vorgabe: markdown-dateien/ in der Projektwurzel')
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    wurzel = finde_wurzel(here)
    mddir = a.md or os.path.join(wurzel, 'markdown-dateien')
    ABB_DIR[0] = os.path.join(mddir, 'abbildungen')
    out = a.ziel or os.path.join(wurzel, 'PDF', 'C8205-Bedienpult_und_Peripherie_A4.pdf')
    set_stand(a.stand)
    quellen = [(n, L.lese_version(os.path.join(mddir, n))) for n in QUELLEN]    # bricht ab, wenn eine Versionszeile fehlt
    L.COVER = dict(
        titel='Bedienpult und Peripherie',
        untertitel='Tasten, Schalter, Lampen, Kanäle, Lochstreifenleser, -stanzer und Schreibwerk',
        art='BESCHREIBUNG', bereich='RECHNER UND REGELWERK', quellen=quellen, stand=a.stand,
        pdf_name=os.path.basename(out), erzeugt_mit=os.path.basename(__file__),
        beschreibung='Dieses Dokument beschreibt, wie der Rechner bedient wird und wie er mit der Außenwelt Zeichen '
                     'austauscht. 1968 gab es keine Bildschirme mit anklickbaren Schaltflächen: Man bediente den Rechner über '
                     'räumlich konzentrierte Schalter und Tasten, Lampen zeigten die Zustände. Beschrieben werden das '
                     'Bedienpult mit seinen Tasten und Schaltern, die Kanalauswahl, die typischen Eingriffe und die '
                     'angeschlossenen Geräte Lochstreifenleser, Lochstreifenstanzer und Schreibwerk.')
    st = head_with_block(merge_intro(story()))
    d = L.Doc(out)
    d.title = 'C8205 – Bedienpult und Peripherie'
    d.author = 'C8205-Interpreter-Projekt'
    d.subject = 'Beschreibung · Quellen: ' + ', '.join('%s %s' % q for q in quellen)
    d.multiBuild(st, canvasmaker=L.NumberedCanvas)
    print('geschrieben:', out)


if __name__ == '__main__':
    main()
