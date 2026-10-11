# -*- coding: utf-8 -*-
"""Markdown -> PDF nach C8205-Interpreter-PDF.md (Abschnitt 6a, Fliesstext-/Tabellendokumente).

A4 hoch, Rand 30 pt, Kopf +26 pt, Fuss +14 pt, DejaVu Sans / Sans Mono, Fusszeile 'Seite X / Y'.
Die Quelle wird im Wortlaut uebernommen: weich umbrochene Zeilen werden zu einem Absatz zusammengefuehrt,
Listen (auch verschachtelt), Tabellen, Codebloecke und Zitate bleiben erhalten.

Aufruf:  python3 md2pdf.py QUELLE.md ZIEL.pdf "Kurztitel" [--toc-levels 2]
"""
import re
import sys
import argparse

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # pdflib.py liegt daneben
import pdflib as L                                              # Schriften, Farben, Stile
from pdflib import (ST, INK, MUTED, RULE, CODE_BG, HEAD_BG, FRAME_W, M, W, H, HEAD, FOOT, esc,
                    ORANGE, ORANGE_BG)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle, KeepTogether, CondPageBreak,
                                PageBreak, BaseDocTemplate, PageTemplate, Frame)
from reportlab.platypus.tableofcontents import TableOfContents

# ------------------------------------------------------------------ Konfiguration (pro Dokument gesetzt)
CFG = dict(header_title='', header_legend='', footer_left='', title='', subject='')

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
        if ch == '|' and not inc:
            cells.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    cells.append(''.join(cur).strip())
    return cells


def starts_block(l):
    return (not l.strip()) or FENCE.match(l) or HEADING.match(l) or l.startswith('|') or l.startswith('>') \
        or LISTM.match(l)


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
        # Absatz
        para = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not (FENCE.match(lines[i]) or HEADING.match(lines[i])
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


def quote_block(paras, width):
    cells = [Paragraph(inline(p), ST['note']) for p in paras]
    t = Table([['', cells]], colWidths=[3.2, width - 3.2], hAlign='RIGHT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), ORANGE), ('BACKGROUND', (1, 0), (1, 0), ORANGE_BG),
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
    for b in blocks:
        kind = b[0]
        if kind == 'h':
            out += head(b[2], min(b[1] - 2, 2) if b[1] >= 2 else 0)
        elif kind == 'p':
            out.append(Paragraph(inline(b[1]), pstyle('body', indent, leftIndent=indent)))
        elif kind == 'code':
            out += code_block(b[1], width)
        elif kind == 'table':
            out += table_block(b[1], width)
        elif kind == 'quote':
            out += quote_block(b[1], width)
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
class Canvas(L.NumberedCanvas):
    def _decorate(self, total):
        pg = self._pageNumber
        self.saveState()
        if pg >= 2:
            self.setFillColor(INK)
            self.setFont('DV-B', 11)
            self.drawString(M, H - M - 8, CFG['header_title'])
            self.setFillColor(MUTED)
            self.setFont('DV', 8)
            self.drawString(M, H - M - 20, CFG['header_legend'])
            self.setStrokeColor(RULE)
            self.setLineWidth(0.5)
            self.line(M, H - M - 24.5, W - M, H - M - 24.5)
        self.setFillColor(MUTED)
        self.setFont('DV', 7.5)
        self.drawString(M, M - 2, CFG['footer_left'])
        self.drawRightString(W - M, M - 2, 'Seite %d / %d' % (pg, total))
        self.restoreState()


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


def convert(src, dst, kurztitel, stand, toc_levels=2, cover_break=True, quelle_name=None):
    raw = open(src, encoding='utf-8').read().replace('\r\n', '\n')
    lines = raw.split('\n')
    blocks = parse_blocks(lines, top=True)
    # Titel: erste Ueberschrift der Ebene 1
    title = None
    if blocks and blocks[0][0] == 'h' and blocks[0][1] == 1:
        title = blocks[0][2]
        blocks = blocks[1:]
    title = title or kurztitel
    quelle = quelle_name or src.split('/')[-1]
    CFG.update(header_title=kurztitel, header_legend='Quelle: %s · im Wortlaut der Quelle' % quelle,
               footer_left='C8205-Interpreter-Projekt · Stand ' + stand, title=title,
               subject='PDF-Ausgabe von ' + quelle)
    nsec = sum(1 for b in blocks if b[0] == 'h' and b[1] == 2)
    story = [Paragraph(inline(title, 13), ST['title']),
             Paragraph('%s · Stand %s' % (esc(kurztitel), stand), ST['subtitle']),
             Paragraph('Dieses PDF gibt die Quelldatei <font name="DVM" size="8">%s</font> im Wortlaut wieder '
                       '(%d Abschnitte). Weich umbrochene Zeilen sind zu Absätzen zusammengeführt; Listen, Tabellen, '
                       'Codeblöcke und Zitate entsprechen der Quelle. Maßgeblich bleibt die .md-Datei; '
                       'dieses PDF wird nicht automatisch nachgeführt (Stand siehe oben und Fußzeile).'
                       % (esc(quelle), nsec), ST['body']),
             Spacer(1, 6), Paragraph('<b>Inhalt</b>', ST['h2'])]
    toc = TableOfContents(dotsMinLevel=0)
    toc.levelStyles = [ST['toc1'], ST['toc2']]
    toc.tableStyle = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 1.2),
                                 ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2)])
    story.append(toc)
    if cover_break:
        story.append(PageBreak())
    else:
        story.append(Spacer(1, 10))
    body = render(blocks)
    story += body
    story = head_with_block(merge_intros(story))
    d = Doc(dst)
    d.toc_levels = toc_levels
    d.multiBuild(story, canvasmaker=Canvas)
    return nsec


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('kurztitel')
    ap.add_argument('--stand', default='07.10.2026')
    ap.add_argument('--toc-levels', type=int, default=2)
    ap.add_argument('--no-cover-break', action='store_true')
    a = ap.parse_args()
    n = convert(a.src, a.dst, a.kurztitel, a.stand, a.toc_levels, not a.no_cover_break)
    print('Abschnitte:', n)
    for x in NOTES:
        print('HINWEIS:', x)
