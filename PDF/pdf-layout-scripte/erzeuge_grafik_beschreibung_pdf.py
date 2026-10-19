# -*- coding: utf-8 -*-
"""Erzeugt PDF/C8205-GRAFIK_Beschreibung_A4.pdf nach C8205-Interpreter-PDF.md (4.6, 6a, 3a).

Quelle:  markdown-dateien/C8205-Interpreter-GRAFIK_Beschreibung.md   (Wortlaut-PDF, Abschnitt 6a)
Aufruf:  python3 PDF/pdf-layout-scripte/erzeuge_grafik_beschreibung_pdf.py [--stand TT.MM.JJJJ] [--quelle PFAD] [--ziel PFAD]

Das Skript legt die Deckblattdaten aus PDF.md 4.6 fest (Titel, Untertitel, Art, Bereich) und ruft
md2pdf.convert() auf; Schriften, Kopf-/Fusszeile, Deckblatt und Tabellenstil kommen aus pdflib.py.
Version der Quelle und Stand (Erzeugungsdatum) werden beim Erzeugen gelesen, nicht von Hand gesetzt.

Zusaetzlich zu md2pdf.py gilt hier (PDF.md 3a.6, Ueberschriften nie allein am Seitenende): Eine
Ueberleitung bleibt mit dem Folgeblock zusammen. Als Ueberleitung zaehlt ein Absatz oder Listenpunkt,
der nur aus einer Fettschrift-Zeile besteht (z. B. "**Anlegen und Fortführen der Datei**") oder mit
einem Doppelpunkt endet.
"""

# ---------------------------------------------------------------------------------------------
# Eigenstaendig: Die Module pdflib.py, md2pdf.py sind unten als Quelltext eingebettet und werden
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
    'md2pdf': ('md2pdf.py', r'''# -*- coding: utf-8 -*-
"""Markdown -> PDF nach C8205-Interpreter-PDF.md (Abschnitt 6a, Fliesstext-/Tabellendokumente).

A4 hoch, Rand 30 pt, Kopf +26 pt, Fuss +14 pt, DejaVu Sans / Sans Mono, Fusszeile 'Seite X / Y'.
Seite 1 ist das Deckblatt (PDF.md Abschnitt 4), Seite 2 das Inhaltsverzeichnis, der Inhalt beginnt auf Seite 3.
Die Quelle wird im Wortlaut uebernommen: weich umbrochene Zeilen werden zu einem Absatz zusammengefuehrt,
Listen (auch verschachtelt), Tabellen, Codebloecke und Zitate bleiben erhalten.
Bilder: Zeile "![Bildunterschrift](pfad.png)" (Pfad relativ zur .md-Datei) wird als Abbildung mit Bildunterschrift gesetzt
(pdflib.bild; Druckgroesse aus der im PNG gespeicherten Aufloesung). Folgt unmittelbar ein Absatz, der ganz aus einer
kursiven Zeile "*Abbildung N: ...*" besteht (so zeigt ihn auch GitHub unter dem Bild), ist er die Bildunterschrift.
Zitate (>) werden nach PDF.md 3a.4 gesetzt: **Hinweis** blau, **Achtung** orange (auch ein Absatz 'Wichtig:' davor), sonst neutral grau;
'---' wird zur Haarlinie.

Aufruf:  python3 md2pdf.py QUELLE.md ZIEL.pdf "Titel" --untertitel "..." --art REFERENZ --bereich INTERPRETER
         [--stand TT.MM.JJJJ] [--toc-levels 2] [--beschreibung "..."]   (Titel, Untertitel, Art, Bereich: PDF.md 4.6)
"""
import re
import sys
import argparse

import os
import pdflib as L                                              # Schriften, Farben, Stile
from pdflib import (ST, INK, MUTED, RULE, CODE_BG, HEAD_BG, FRAME_W, M, W, H, HEAD, FOOT, esc,
                    ORANGE, ORANGE_BG, BLUE, BLUE_BG)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle, KeepTogether, CondPageBreak,
                                PageBreak, BaseDocTemplate, PageTemplate, Frame, HRFlowable)
from reportlab.platypus.tableofcontents import TableOfContents

# ------------------------------------------------------------------ Konfiguration (pro Dokument gesetzt)
CFG = dict(header_title='', header_legend='', footer_left='', title='', subject='')
BASE_DIR = ['.']          # Ordner der Quelle (.md); relative Bildpfade werden dort aufgeloest (convert setzt ihn)

# ------------------------------------------------------------------ Inline-Auszeichnung
_CODE = re.compile(r'`([^`]+)`')
_BOLD = re.compile(r'\*\*(.+?)\*\*')
_ITAL = re.compile(r'(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])')


def inline(s, code_size=8.0):
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return '\x00%d\x00' % (len(codes) - 1)

    s = _CODE.sub(keep, s)
    s = esc(s)
    s = _BOLD.sub(r'<b>\1</b>', s)
    s = _ITAL.sub(r'<i>\1</i>', s)

    def back(m):
        c = codes[int(m.group(1))]
        t = esc(c)
        if len(c) <= 45:
            t = t.replace(' ', '&nbsp;')
        else:                                   # lange Spans duerfen an einzelnen Leerzeichen umbrechen
            t = re.sub(r'  +', lambda mm: '&nbsp;' * len(mm.group(0)), t)
        return '<font name="DVM" size="%s">%s</font>' % (code_size, t)

    return re.sub('\x00(\\d+)\x00', back, s)


# ------------------------------------------------------------------ Parser
FENCE = re.compile(r'^(\s*)```')
HEADING = re.compile(r'^(#{1,4})\s+(.*\S)\s*$')
LISTM = re.compile(r'^(\s*)([-*]|\d+\.)(\s+)(.*)$')
TITLE = re.compile(r'^\*\* (.+?) \*\*\s*$')
HRULE = re.compile(r'^\s{0,3}(-{3,}|\*{3,}|_{3,})\s*$')          # waagerechte Linie der Quelle ("---")


def indent_of(l):
    return len(l) - len(l.lstrip(' '))


def split_row(line):
    """Zellen einer Tabellenzeile; '|' innerhalb von `...` trennt nicht."""
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    cells, cur, inc = [], [], False
    for ch in s:
        if ch == '`':
            inc = not inc
        if ch == '|' and cur and cur[-1] == '\\':     # maskierter Strich '\|' (auch in `...`): Zeichen '|', kein Trenner
            cur[-1] = '|'
        elif ch == '|' and not inc:
            cells.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    cells.append(''.join(cur).strip())
    return cells


IMAGE = re.compile(r'^!\[(.*?)\]\((\S+?)\)\s*$')        # ![Bildunterschrift](pfad)


def starts_block(l):
    return (not l.strip()) or FENCE.match(l) or HEADING.match(l) or l.startswith('|') or l.startswith('>') \
        or LISTM.match(l) or HRULE.match(l) or IMAGE.match(l.strip())


NOTES = []        # Auffaelligkeiten beim Parsen (Listenstart mitten im Absatz usw.)


def parse_blocks(lines, top=False):
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = FENCE.match(line)
        if m:
            ind = len(m.group(1))
            i += 1
            body = []
            while i < n and not (FENCE.match(lines[i]) and lines[i].strip() == '```'):
                body.append(lines[i][ind:] if indent_of(lines[i]) >= ind else lines[i].lstrip(' '))
                i += 1
            i += 1
            out.append(('code', body))
            continue
        if HRULE.match(line):
            out.append(('hr',))
            i += 1
            continue
        m = HEADING.match(line)
        if m:
            out.append(('h', len(m.group(1)), m.group(2)))
            i += 1
            continue
        m = TITLE.match(line)
        if m and top:
            out.append(('h', 1, m.group(1)))
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < n and lines[i].startswith('|'):
                cells = split_row(lines[i])
                if not all(re.fullmatch(r':?-{2,}:?', c) for c in cells):
                    rows.append(cells)
                i += 1
            out.append(('table', rows))
            continue
        if line.startswith('>'):
            paras, cur = [], []
            while i < n and lines[i].startswith('>'):
                t = lines[i][1:].strip()
                if t:
                    cur.append(t)
                elif cur:
                    paras.append(' '.join(cur))
                    cur = []
                i += 1
            if cur:
                paras.append(' '.join(cur))
            out.append(('quote', paras))
            continue
        m = LISTM.match(line)
        if m:
            ind = len(m.group(1))
            items = []
            while i < n:
                m = LISTM.match(lines[i])
                if not m or len(m.group(1)) != ind:
                    break
                marker = m.group(2)
                cind = ind + len(marker) + len(m.group(3))
                item = [m.group(4)]
                i += 1
                while i < n:
                    l = lines[i]
                    if not l.strip():
                        j = i + 1
                        while j < n and not lines[j].strip():
                            j += 1
                        if j < n and indent_of(lines[j]) > ind:
                            item.append('')
                            i += 1
                            continue
                        break
                    if indent_of(l) > ind:
                        item.append(l[cind:] if indent_of(l) >= cind else l.lstrip(' '))
                        i += 1
                        continue
                    lm = LISTM.match(l)
                    if lm and len(lm.group(1)) <= ind:
                        break
                    if starts_block(l):
                        break
                    item.append(l.strip())          # lazy continuation
                    i += 1
                items.append((marker, parse_blocks(item)))
            out.append(('list', items))
            continue
        m = IMAGE.match(line.strip())
        if m:
            out.append(('img', m.group(1), m.group(2)))
            i += 1
            continue
        # Absatz
        para = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not (FENCE.match(lines[i]) or HEADING.match(lines[i])
                                                 or HRULE.match(lines[i]) or IMAGE.match(lines[i].strip())
                                                 or lines[i].startswith('|') or lines[i].startswith('>')):
            lm = LISTM.match(lines[i])
            if lm:
                NOTES.append('Liste beginnt direkt nach Absatzzeile: %r / %r' % (para[-1][-50:], lines[i][:50]))
                break
            para.append(lines[i].strip())
            i += 1
        out.append(('p', ' '.join(para)))
    return out


# ------------------------------------------------------------------ Flowables
_styles = {}


def pstyle(base, indent=0.0, **kw):
    key = (base, indent, tuple(sorted(kw.items())))
    if key not in _styles:
        _styles[key] = ParagraphStyle('%s_%s_%d' % (base, indent, len(_styles)), parent=ST[base], **kw)
    return _styles[key]


_head_n = [0]


class MHead(Paragraph):
    def __init__(self, text, level):
        sty = {0: 'h1', 1: 'h2', 2: 'h2'}[level]
        st = pstyle(sty, keepWithNext=1) if level < 2 else pstyle('h2', fontSize=9.2, leading=12, spaceBefore=5,
                                                                    spaceAfter=3, keepWithNext=1)
        Paragraph.__init__(self, inline(text, 9.0), st)
        self.toc_level = level
        self.toc_text = text.replace('`', '')
        _head_n[0] += 1
        self.toc_key = 'k%d' % _head_n[0]


def head(text, level):
    cp = {0: 60, 1: 48, 2: 40}[level]
    return [CondPageBreak(cp), MHead(text, level)]


def wrap_line(line, maxc, indent='    '):
    return L._wrap_line(line, maxc, indent)


def code_block(lines, width):
    lines = list(lines)
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    lines = [ln.replace('\t', '    ') for ln in lines]
    maxc = int((width - 16) / pdfmetrics.stringWidth('0', 'DVM', ST['code'].fontSize)) - 1
    wrapped = [w for ln in lines for w in wrap_line(ln.rstrip(), maxc)]
    rows = [[Paragraph(esc(w).replace(' ', '&nbsp;') or '&nbsp;', ST['code'])] for w in wrapped]
    t = Table(rows, colWidths=[width], splitByRow=1, hAlign='RIGHT')
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), CODE_BG),
                           ('LINEBEFORE', (0, 0), (0, -1), 3.2, MUTED),
                           ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                           ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                           ('TOPPADDING', (0, 0), (-1, 0), 4), ('BOTTOMPADDING', (0, -1), (-1, -1), 4)]))
    n = len(rows)
    if n > 12:        # lange Bloecke: nur an Leerzeilen trennen (oben >= 6, unten >= 4 Zeilen), spaetestens alle 40
        blank = {i for i, w in enumerate(wrapped) if not w.strip()}
        allowed, last = set(), 0
        for i in range(5, n - 4):
            if i in blank or i - last >= 40:
                allowed.add(i)
                last = i
        cmds = [('NOSPLIT', (0, 0), (-1, 5)), ('NOSPLIT', (0, n - 4), (-1, n - 1))]
        for i in range(5, n - 4):
            if i not in allowed:
                cmds.append(('NOSPLIT', (0, i), (-1, i + 1)))
        t.setStyle(TableStyle(cmds))
        t._long = True
        return [t, Spacer(1, 6)]
    kt = KeepTogether([t, Spacer(1, 6)])
    kt._short = True
    return [kt]


def _tokens(cell, fs):
    """(breite, ) der unteilbaren Teile einer Zelle: Code-Spans (<= 45 Zeichen) am Stueck, sonst Woerter."""
    ws = []
    pos = 0
    for m in _CODE.finditer(cell):
        for w in re.split(r'[\s/]+', cell[pos:m.start()].replace('**', '').replace('*', '')):
            if w:
                ws.append(pdfmetrics.stringWidth(w, 'DV-B', fs))
        c = m.group(1)
        parts = [c] if len(c) <= 45 else re.split(r'\s+', c)
        for w in parts:
            ws.append(pdfmetrics.stringWidth(w, 'DVM', fs - 0.9))
        pos = m.end()
    for w in re.split(r'[\s/]+', cell[pos:].replace('**', '').replace('*', '')):
        if w:
            ws.append(pdfmetrics.stringWidth(w, 'DV-B', fs))
    return ws


def col_widths(rows, width, fs=8.5):
    ncol = max(len(r) for r in rows)
    cw = fs * 0.55
    mean, minw = [], []
    for c in range(ncol):
        cells = [r[c] if c < len(r) else '' for r in rows]
        mean.append(sum(len(re.sub(r'[`*]', '', x)) for x in cells) / len(cells))
        longest = max((w for x in cells for w in _tokens(x, fs)), default=20)
        minw.append(min(max(30.0, longest + 11), 0.58 * width))
    want = [max(m, 4) * cw + 10 for m in mean]
    if sum(minw) >= width:
        k = width / sum(minw)
        return [w * k for w in minw]
    extra = width - sum(minw)
    need = [max(w - m, 0.0) for w, m in zip(want, minw)]
    tot = sum(need)
    if tot <= 0:
        return [m + extra / ncol for m in minw]
    if tot <= extra:       # alles passt: Rest proportional verteilen
        rest = extra - tot
        return [m + nd + rest * (w / sum(want)) for m, nd, w in zip(minw, need, want)]
    return [m + extra * nd / tot for m, nd in zip(minw, need)]


def table_block(rows, width, fs=8.5):
    ncol = max(len(r) for r in rows)
    rows = [r + [''] * (ncol - len(r)) for r in rows]
    cell = ParagraphStyle('c', parent=ST['cell'], fontSize=fs, leading=fs * 1.27)
    cellh = ParagraphStyle('ch', parent=ST['cellh'], fontSize=fs, leading=fs * 1.27)
    data = [[Paragraph(inline(v, fs - 0.9), cellh if r == 0 else cell) for v in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=col_widths(rows, width, fs), repeatRows=1, hAlign='RIGHT')
    sty = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('LEFTPADDING', (0, 0), (-1, -1), 4.5), ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
           ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
           ('LINEBELOW', (0, 0), (-1, -1), 0.4, RULE), ('BOX', (0, 0), (-1, -1), 0.5, RULE),
           ('BACKGROUND', (0, 0), (-1, 0), HEAD_BG)]
    if len(rows) >= 3:
        sty.append(('NOSPLIT', (0, len(rows) - 2), (-1, len(rows) - 1)))
    t.setStyle(TableStyle(sty))
    _w, h = t.wrap(width, 2000)
    if len(rows) <= 10 and h <= 190:
        kt = KeepTogether([t, Spacer(1, 7)])
        kt._short = True
        return [kt]
    return [t, Spacer(1, 7)]


_LEADIN = re.compile(r'^\**\s*(Hinweis|Achtung|Wichtig)\s*:\s*\**$', re.I)


def quote_kind(paras, prev=None):
    """Art des Kastens nach PDF.md 3a.4 und Abschnitt 5: 'hinweis' (blau), 'achtung' (orange) oder 'zitat' (neutral).
    Massgeblich ist das Stichwort, mit dem der Text beginnt (**Hinweis ...**, **Achtung ...**); steht es allein im
    vorangehenden Absatz ('Wichtig:'), gilt dieser. Ein Zitat ohne Stichwort ist kein Kasten und bekommt keine Farbe
    (Blau und Orange sind den beiden Kaesten vorbehalten)."""
    first = paras[0].lstrip() if paras else ''
    m = re.match(r'\*\*(Hinweis|Achtung)\b', first, re.I)
    if m:
        return ('hinweis' if m.group(1).lower() == 'hinweis' else 'achtung'), None
    if prev is not None and prev[0] == 'p' and _LEADIN.match(prev[1].strip()):
        w = _LEADIN.match(prev[1].strip()).group(1).lower()
        return ('hinweis' if w == 'hinweis' else 'achtung'), prev[1].strip().strip('*').strip()
    return 'zitat', None


def quote_block(paras, width, kind='achtung', leadin=None):
    bar, bg = {'hinweis': (BLUE, BLUE_BG), 'achtung': (ORANGE, ORANGE_BG), 'zitat': (MUTED, CODE_BG)}[kind]
    if leadin:                      # Stichwort aus dem vorangehenden Absatz, fett am Anfang des Kastens
        paras = ['**%s** %s' % (leadin, paras[0])] + list(paras[1:])
    cells = [Paragraph(inline(p), ST['note']) for p in paras]
    t = Table([['', cells]], colWidths=[3.2, width - 3.2], hAlign='RIGHT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), bar), ('BACKGROUND', (1, 0), (1, 0), bg),
        ('LEFTPADDING', (0, 0), (0, 0), 0), ('RIGHTPADDING', (0, 0), (0, 0), 0),
        ('LEFTPADDING', (1, 0), (1, 0), 7), ('RIGHTPADDING', (1, 0), (1, 0), 6),
        ('TOPPADDING', (1, 0), (1, 0), 4.5), ('BOTTOMPADDING', (1, 0), (1, 0), 4.5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    kt = KeepTogether([t, Spacer(1, 6)])
    kt._short = True
    return [kt]


def render(blocks, indent=0.0):
    out = []
    width = FRAME_W - indent
    skip = set()                                    # als Bildunterschrift verbrauchte Absaetze
    for bi, b in enumerate(blocks):
        kind = b[0]
        if bi in skip:
            continue
        if kind == 'h':
            out += head(b[2], min(b[1] - 2, 2) if b[1] >= 2 else 0)
        elif kind == 'p':
            out.append(Paragraph(inline(b[1]), pstyle('body', indent, leftIndent=indent)))
        elif kind == 'img':
            cap = b[1]
            nxt = blocks[bi + 1] if bi + 1 < len(blocks) else None
            if nxt and nxt[0] == 'p':                               # *Abbildung N: ...* direkt unter dem Bild
                m = re.fullmatch(r'\*(Abb(?:ildung|\.)[^*]*)\*', nxt[1].strip())
                if m:
                    cap = m.group(1)
                    skip.add(bi + 1)
            fig = L.bild(os.path.join(BASE_DIR[0], b[2]), cap, breite=width)
            fig[0]._short = True                                    # kurzer Einleitungsabsatz bleibt beim Bild
            out += fig
        elif kind == 'hr':
            out.append(HRFlowable(width='100%', thickness=0.5, color=RULE, spaceBefore=3, spaceAfter=7))
        elif kind == 'code':
            out += code_block(b[1], width)
        elif kind == 'table':
            out += table_block(b[1], width)
        elif kind == 'quote':
            qk, leadin = quote_kind(b[1], blocks[bi - 1] if bi else None)
            if leadin:              # Absatz mit dem Stichwort allein wandert in den Kasten
                out.pop()
            out += quote_block(b[1], width, qk, leadin)
        elif kind == 'list':
            for marker, sub in b[1]:
                bt = '•' if marker in '-*' else marker
                lead = 15.0 if marker in '-*' else (16.0 if len(marker) <= 2 else 21.0)
                first, rest = (sub[0], sub[1:]) if sub and sub[0][0] == 'p' else (None, sub)
                text = first[1] if first else ''
                out.append(Paragraph(inline(text), pstyle('body', indent, leftIndent=indent + lead,
                                                          bulletIndent=indent, spaceAfter=2.5),
                                     bulletText=bt))
                out += render(rest, indent + lead)
            out.append(Spacer(1, 2.5))
    return out


def merge_intros(story):
    """Absatz mit ':' am Ende direkt vor kurzem Code-/Tabellenblock wandert mit ihm auf die naechste Seite."""
    res = []
    for fl in story:
        if getattr(fl, '_short', False) and res and isinstance(res[-1], Paragraph) \
                and not isinstance(res[-1], MHead) and res[-1].style.name.startswith('body') \
                and (res[-1].text.rstrip().endswith(':') or len(res[-1].getPlainText()) < 200):
            prev = res.pop()
            res.append(KeepTogether([prev] + list(fl._content)))
        elif isinstance(fl, Table) and getattr(fl, '_long', False) and res and isinstance(res[-1], Paragraph) \
                and not isinstance(res[-1], MHead):
            res[-1].keepWithNext = 1
            res.append(fl)
        else:
            res.append(fl)
    return res


def head_with_block(story):
    for i in range(2, len(story)):
        fl = story[i]
        if isinstance(story[i - 1], MHead) and isinstance(story[i - 2], CondPageBreak) and isinstance(fl, KeepTogether):
            try:
                h = sum(c.wrap(FRAME_W, 5000)[1] + getattr(c, 'getSpaceAfter', lambda: 0)() for c in fl._content)
            except Exception:
                continue
            story[i - 2] = CondPageBreak(min(h + 34, 330))
    return story


# ------------------------------------------------------------------ Dokument
class Doc(BaseDocTemplate):
    def __init__(self, fn):
        BaseDocTemplate.__init__(self, fn, pagesize=L.A4, leftMargin=M, rightMargin=M, topMargin=M,
                                 bottomMargin=M, title=CFG['title'], author='C8205-Interpreter-Projekt',
                                 subject=CFG['subject'])
        self.addPageTemplates([PageTemplate(id='p', frames=[
            Frame(M, M + FOOT, FRAME_W, H - 2 * M - HEAD - FOOT, id='f', leftPadding=0, rightPadding=0,
                  topPadding=6, bottomPadding=0)])])

    toc_levels = 2

    def afterFlowable(self, fl):
        if isinstance(fl, MHead):
            self.canv.bookmarkPage(fl.toc_key)
            self.canv.addOutlineEntry(fl.toc_text, fl.toc_key, level=fl.toc_level, closed=False)
            if fl.toc_level < self.toc_levels:
                self.notify('TOCEntry', (fl.toc_level, fl.toc_text, self.page, fl.toc_key))


def convert(src, dst, titel, untertitel, art, bereich, stand, toc_levels=2, quelle_name=None, beschreibung=None):
    raw = open(src, encoding='utf-8').read().replace('\r\n', '\n')
    lines = raw.split('\n')
    BASE_DIR[0] = os.path.dirname(os.path.abspath(src))
    blocks = parse_blocks(lines, top=True)
    # erste Ueberschrift der Ebene 1 (Titelzeile der Quelle) entfaellt: Titel steht auf dem Deckblatt
    if blocks and blocks[0][0] == 'h' and blocks[0][1] == 1:
        blocks = blocks[1:]
    quelle = quelle_name or os.path.basename(src)
    version = L.lese_version(src)                                   # bricht ab, wenn die Versionszeile fehlt
    nsec = sum(1 for b in blocks if b[0] == 'h' and b[1] == 2)
    L.COVER = dict(titel=titel, untertitel=untertitel, art=art, bereich=bereich, quellen=[(quelle, version)],
                   stand=stand, pdf_name=os.path.basename(dst), beschreibung=beschreibung or L.STANDARD_BESCHREIBUNG)
    L.HEADER_TITLE = 'C 8205 – ' + titel
    L.HEADER_LEGEND = 'Quelle: %s · im Wortlaut der Quelle' % quelle
    L.FOOTER_LEFT = 'C8205-Interpreter-Projekt · Stand ' + stand
    CFG.update(title=titel, subject='%s · Quelle: %s %s' % (art.capitalize(), quelle, version))
    story = [Spacer(1, 1), PageBreak()]                             # Seite 1: Deckblatt (wird vom Canvas gezeichnet)
    if nsec:                                                        # Seite 2: Inhaltsverzeichnis
        toc = TableOfContents(dotsMinLevel=0)
        toc.levelStyles = [ST['toc1'], ST['toc2']]
        toc.tableStyle = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 1.2),
                                     ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2)])
        story += [Paragraph('Inhaltsverzeichnis', ST['h1']), toc, PageBreak()]
    story += render(blocks)
    story = head_with_block(merge_intros(story))
    d = Doc(dst)
    d.toc_levels = toc_levels
    d.multiBuild(story, canvasmaker=L.NumberedCanvas)
    return nsec


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('titel', help='Titel auf dem Deckblatt (PDF.md 4.6)')
    ap.add_argument('--untertitel', required=True)
    ap.add_argument('--art', required=True, choices=L.ARTEN)
    ap.add_argument('--bereich', required=True, choices=L.BEREICHE)
    ap.add_argument('--stand', default=L.heute(), help='TT.MM.JJJJ; Vorgabe: Erzeugungsdatum')
    ap.add_argument('--toc-levels', type=int, default=2)
    ap.add_argument('--beschreibung', default=None, help='Kurzbeschreibung (Zone C); Vorgabe: Standardsatz fuer Wortlaut-PDFs')
    a = ap.parse_args()
    n = convert(a.src, a.dst, a.titel, a.untertitel, a.art, a.bereich, a.stand, a.toc_levels, None, a.beschreibung)
    print('Abschnitte:', n)
    for x in NOTES:
        print('HINWEIS:', x)
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

import os
import sys
import argparse

HIER = os.path.dirname(os.path.abspath(__file__))
import pdflib as L
import md2pdf as M
from reportlab.platypus import Paragraph, CondPageBreak

# ------------------------------------------------------------------ Deckblattdaten (PDF.md 4.6)
QUELLE_NAME = 'C8205-Interpreter-GRAFIK_Beschreibung.md'
PDF_NAME = 'C8205-GRAFIK_Beschreibung_A4.pdf'
TITEL = 'GRAFIK-Interpreter: Beschreibung'
UNTERTITEL = 'Zweck, Fenster, Geräte, Töne, Aufruf und Grenzen des GRAFIK-Modus im Wortlaut der Quelle'
ART = 'BESCHREIBUNG'
BEREICH = 'INTERPRETER'


# ------------------------------------------------------------------ Layout: Ueberleitung bleibt beim Folgeblock
def _ueberleitung(fl):
    if not isinstance(fl, Paragraph) or isinstance(fl, M.MHead):
        return False
    if not fl.style.name.startswith('body'):
        return False
    t = fl.text.strip()
    nur_fett = t.startswith('<b>') and t.endswith('</b>') and t.count('<b>') == 1
    return nur_fett or t.endswith(':')


_merge_intros_md2pdf = M.merge_intros


def _ueberschriftenfolgen(story):
    """Folgen sich Ueberschriften unmittelbar (z. B. 6.2 und 6.2.1), steht vor jeder ein eigenes
    CondPageBreak. Das der zweiten Ueberschrift loest dann den Umbruch aus, nachdem die erste schon
    allein am Seitenende steht. Hier: ein gemeinsamer Umbruch vor der Folge (Summe der Mindesthoehen)."""
    res = []
    for fl in story:
        if isinstance(fl, M.MHead) and len(res) >= 2 and isinstance(res[-1], CondPageBreak) \
                and isinstance(res[-2], M.MHead):
            vorher = res.pop()                                  # CondPageBreak dieser Ueberschrift
            j = len(res) - 2                                    # CondPageBreak der Vorgaengerin suchen
            while j >= 0 and not isinstance(res[j], CondPageBreak):
                j -= 1
            if j >= 0:
                res[j] = CondPageBreak(res[j].height + vorher.height)
        res.append(fl)
    return res


def _merge_intros_mit_ueberleitung(story):
    story = _merge_intros_md2pdf(story)        # zuerst die Regeln von md2pdf.py (Absatz + kurzer Block)
    story = _ueberschriftenfolgen(story)
    for fl in story:
        if _ueberleitung(fl):
            fl.keepWithNext = 1
    return story


M.merge_intros = _merge_intros_mit_ueberleitung


# ------------------------------------------------------------------ Quelle suchen
def finde_quelle(wurzel):
    """Quelldatei im Ordner markdown-dateien/. Info-ZIP-unzip ohne UTF-8-Namen legt 'ü' als '#U00fc' ab."""
    ordner = os.path.join(wurzel, 'markdown-dateien')
    for name in (QUELLE_NAME, QUELLE_NAME.replace('ü', '#U00fc')):
        pfad = os.path.join(ordner, name)
        if os.path.isfile(pfad):
            return pfad
    sys.exit('Quelle nicht gefunden: %s' % os.path.join(ordner, QUELLE_NAME))


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
    wurzel = finde_wurzel(HIER)
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--quelle', default=None, help='Vorgabe: markdown-dateien/' + QUELLE_NAME)
    ap.add_argument('--ziel', default=None, help='Vorgabe: PDF/' + PDF_NAME)
    ap.add_argument('--stand', default=L.heute(), help='TT.MM.JJJJ; Vorgabe: Erzeugungsdatum')
    a = ap.parse_args()
    ziel = a.ziel or os.path.join(wurzel, 'PDF', PDF_NAME)
    src = a.quelle or finde_quelle(wurzel)
    n = M.convert(src, ziel, TITEL, UNTERTITEL, ART, BEREICH, a.stand, quelle_name=QUELLE_NAME)
    print('Abschnitte:', n)
    for x in M.NOTES:
        print('HINWEIS:', x)
    print('geschrieben:', ziel)


if __name__ == '__main__':
    main()
