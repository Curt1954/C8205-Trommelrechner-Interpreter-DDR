# md_layout.py - Layout-Script: erzeugt aus der .md das PDF (reportlab, ohne pandoc/wkhtmltopdf).
# Gestaltung nach C8205-Interpreter-PDF.md (angenaehert): A4, DejaVu Sans, Kopf (Titel + Linie) und Fuss (Version, Stand, Seite X / Y) auf jeder Seite.
# Bilder (![Text](Datei.png)) stehen EINSCHLIESSLICH Bildunterschrift auf einer eigenen A4-Querseite, so gross wie moeglich (Trommelaufbau).
# Unterstuetzt: # bis ### , Absaetze, - und 1. Listen (auch eingerueckt), Tabellen, **fett**, *kursiv*, `code`, Bilder.
# Voraussetzung: Python-Pakete reportlab, Pillow; DejaVu-Schriften. Bilddateien neben der .md.
# Aufruf im Ordner der .md:  python3 md_layout.py [Name.md]   (Vorgabe: ZT-Repository_Aufgabenstellung.md) ; Ergebnis Name.pdf
import sys, os, re, datetime
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, NextPageTemplate, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
md = sys.argv[1] if len(sys.argv) > 1 else 'ZT-Repository_Aufgabenstellung.md'
pdf = md[:-3] + '.pdf'
txt = open(md, encoding='utf-8').read()
version = re.search(r'^Version:\s*(\S+)', txt, re.M).group(1)
titel = re.search(r'^# (.+)$', txt, re.M).group(1)
stand = datetime.date.today().strftime('%d.%m.%Y')
fd = '/usr/share/fonts/truetype/dejavu/'
for n, f in (('DV', 'DejaVuSans'), ('DVB', 'DejaVuSans-Bold'), ('DVI', 'DejaVuSans-Oblique'), ('DVM', 'DejaVuSansMono'), ('DVBI', 'DejaVuSans-BoldOblique')):
    pdfmetrics.registerFont(TTFont(n, fd + f + '.ttf'))
addMapping('DV', 0, 0, 'DV'); addMapping('DV', 1, 0, 'DVB'); addMapping('DV', 0, 1, 'DVI'); addMapping('DV', 1, 1, 'DVBI')
INK = colors.HexColor('#1a1a1a'); GREY = colors.HexColor('#555555')
def S(name, **k):
    d = dict(fontName='DV', fontSize=9, leading=12.2, textColor=INK); d.update(k)
    return ParagraphStyle(name, **d)
st = {'p': S('p', spaceAfter=4), 'h1': S('h1', fontName='DVB', fontSize=15, leading=19, spaceAfter=6),
      'h2': S('h2', fontName='DVB', fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=4, keepWithNext=1),
      'h3': S('h3', fontName='DVB', fontSize=10, leading=13, spaceBefore=7, spaceAfter=3, keepWithNext=1),
      'cell': S('cell', fontSize=8, leading=10.4), 'cellh': S('cellh', fontName='DVB', fontSize=8, leading=10.4),
      'cap': S('cap', fontName='DVB', fontSize=10, leading=13, alignment=1, spaceBefore=4)}
def inline(t):
    t = escape(t)
    t = re.sub(r'`([^`]+)`', lambda m: '<font name="DVM" size="8">%s</font>' % m.group(1), t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])', r'<i>\1</i>', t)
    return t
PW, PH = A4; M = 42.5
def deco(c, d):
    W, H = c._pagesize
    c.saveState(); c.setFont('DVB', 11); c.setFillColor(INK); c.drawString(M, H - 38, 'C 8205 – ' + titel)
    c.setStrokeColor(colors.HexColor('#999999')); c.setLineWidth(0.5); c.line(M, H - 54.5, W - M, H - 54.5); c.line(M, 41, W - M, 41)
    c.setFont('DV', 7.5); c.setFillColor(GREY)
    c.drawString(M, 28, 'C8205-Interpreter-Projekt · Version %s · Stand %s' % (version, stand))
    c.drawRightString(W - M, 28, 'Seite %d / %d' % (c.getPageNumber(), TOTAL[0])); c.restoreState()
TOTAL = [0]
def build(total):
    TOTAL[0] = total
    doc = BaseDocTemplate(pdf, pagesize=A4, title=titel, author='C8205-Interpreter-Projekt')
    fh = PH - 62 - 50
    doc.addPageTemplates([
        PageTemplate('hoch', [Frame(M, 50, PW - 2 * M, fh, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco, pagesize=A4),
        PageTemplate('quer', [Frame(M, 50, PH - 2 * M, PW - 62 - 50, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco, pagesize=landscape(A4))])
    return doc
def tabelle(rows, width):
    hdr = [c.strip() for c in rows[0].strip().strip('|').split('|')]
    body = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows[2:]]
    n = len(hdr)
    lens = [max([len(hdr[i])] + [len(r[i]) if i < len(r) else 0 for r in body]) for i in range(n)]
    w = [max(l, 6) ** 0.8 for l in lens]; k = width / sum(w); w = [x * k for x in w]
    data = [[Paragraph(inline(h), st['cellh']) for h in hdr]] + [[Paragraph(inline(r[i] if i < len(r) else ''), st['cell']) for i in range(n)] for r in body]
    t = Table(data, colWidths=w, repeatRows=1)
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')), ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9d9d9')),
                           ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                           ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
    return [t, Spacer(1, 6)]
def bild(text, datei):
    from PIL import Image as PI
    iw, ih = PI.open(datei).size
    mw, mh = PH - 2 * M, PW - 62 - 50 - 24
    k = min(mw / iw, mh / ih)
    return [NextPageTemplate('quer'), PageBreak(), Image(datei, iw * k, ih * k), Paragraph(inline(text), st['cap'])]
def parse():
    fl = []; lines = txt.split('\n'); i = 0; para = []; imode = [False]
    def add(x):
        if imode[0] and not (isinstance(x, list) and x and isinstance(x[0], NextPageTemplate)):
            fl.extend([NextPageTemplate('hoch'), PageBreak()]); imode[0] = False
        fl.extend(x if isinstance(x, list) else [x])
    def flush():
        if para: add(Paragraph(inline(' '.join(para)), st['p'])); para.clear()
    while i < len(lines):
        l = lines[i]
        if not l.strip(): flush(); i += 1; continue
        m = re.match(r'(#{1,3}) (.+)', l)
        if m: flush(); add(Paragraph(inline(m.group(2)), st['h%d' % len(m.group(1))])); i += 1; continue
        m = re.match(r'!\[(.*?)\]\((.+?)\)\s*$', l)
        if m: flush(); add(bild(m.group(1), m.group(2))); imode[0] = True; i += 1; continue
        if l.startswith('|'):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith('|'): rows.append(lines[i]); i += 1
            add(tabelle(rows, PW - 2 * M)); continue
        m = re.match(r'(\s*)(-|\d+\.) (.*)', l)
        if m:
            flush(); lvl = len(m.group(1)) // 2; mark = '•' if m.group(2) == '-' else m.group(2)
            ps = ParagraphStyle('li%d' % lvl, parent=st['p'], leftIndent=14 + 14 * lvl, bulletIndent=2 + 14 * lvl, spaceAfter=2)
            add(Paragraph(inline(m.group(3)), ps, bulletText=mark)); i += 1; continue
        para.append(l.strip()); i += 1
    flush(); return fl
fl = parse()
d = build(0); d.build(list(fl))
n = d.page
fl = parse(); d = build(n); d.build(fl)
print(pdf, d.page, 'Seiten')
