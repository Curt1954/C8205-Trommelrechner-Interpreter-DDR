#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erzeugt aus denselben .md-Quellen beide PDFs des Knotenautomaten nach C8205-Interpreter-PDF.md:

    C8205-Knotengraph_A4.pdf    Ablaufplan (Graphviz, feste Kachelung 2 Spalten, Kacheln in Helvetica)
    C8205-Knotentabellen_A4.pdf Knotentabelle, Variablentabelle T2, Lesart (DejaVu Sans)

Quellen (im Ordner --mdverz):
    C8205-Interpreter-Eingänge_der_Knoten.md      Knotentabelle
    C8205-Interpreter-Beschreibung_der_Knoten.md  Variablentabelle T2

Beide PDFs entstehen aus EINEM Einlesen, damit Zahlen, Stand und Inhalt nicht auseinanderlaufen.
Optional (--interp c8205_interp.py) wird das Einlesen gegen load_graph()/load_t2() des Interpreters geprüft.

Aufruf:  python3 erzeuge_knoten_pdfs.py --mdverz markdown-dateien --ausgabe PDF [--interp c8205_interp.py]
"""
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
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mdverz', default='markdown-dateien')
    ap.add_argument('--ausgabe', default='PDF')
    ap.add_argument('--interp', default=None, help='c8205_interp.py: Einlesen gegen load_graph()/load_t2() prüfen')
    ap.add_argument('--nur', choices=['graph', 'tabellen'], default=None)
    ap.add_argument('--dot-behalten', default=None, help='Ordner, in den die Graphviz-Zwischendateien kopiert werden')
    a = ap.parse_args()
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
        n = knotentabellen(d, os.path.join(a.ausgabe, 'C8205-Knotentabellen_A4.pdf'))
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
