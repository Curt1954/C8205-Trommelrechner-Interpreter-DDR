#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_testhandbuch.py -- erzeugt C8205-Testhandbuch_A4.pdf (redaktionell, nach C8205-Interpreter-PDF.md).

Bausteine: pdflib.py (liegt daneben). Der Text steht in diesem Skript und wird von Hand aus
C8205-Interpreter-Durchführung_eines_Tests.md nachgezogen. Alle Auszüge des Interpreters (Bildschirm und
Protokoll) stammen aus echten Läufen: das Skript führt die Beispiele bei jedem Aufruf mit dem aktuellen
c8205_interp.py aus (auf einer eigenen, leeren Trommel in einem Temporärordner; das Projekt bleibt unverändert).

Aufruf (aus dem Ordner dieses Skripts, Projektwurzel = Ordner mit c8205_interp.py):
    python3 build_testhandbuch.py --proj .. --aus ../PDF/C8205-Testhandbuch_A4.pdf [--stand 08.10.2026]

Die Beispieltests (bspA, bspB, pruef-wahr, ...) liegen im Ordner Handbuch-Tests/ neben diesem Skript
(Vorgabe; Schalter --handbuchtests). Sie gehören nicht zu den Regressionstests in Tests/.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pdflib as L
from pdflib import (ST, INK, MUTED, RULE, FRAME_W, h1, h2, P, bullets, numbered, note, tbl, code, figure,
                    make_toc, Head)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Flowable, CondPageBreak

GREEN, RED, BLUE = L.GREEN, L.RED, L.BLUE


class Raw(str):
    """Text mit fertigem Paragraph-Markup (wird von fmt nicht maskiert)."""


_fmt_orig = L.fmt


def _fmt(s, code_size=8.0):
    return str(s) if isinstance(s, Raw) else _fmt_orig(s, code_size)


L.fmt = _fmt
GREY = colors.HexColor('#6B7280')
FILL = colors.HexColor('#F3F4F6')


# ------------------------------------------------------------------------------------------ Beispielläufer
class Beispiele:
    """Führt Tests mit dem aktuellen Interpreter aus (eigene leere Trommel, Ausgaben in einem Temporärordner)."""

    def __init__(self, proj, hbtests):
        self.proj = os.path.abspath(proj)
        self.interp = os.path.join(self.proj, 'c8205_interp.py')
        self.md = os.path.join(self.proj, 'markdown-dateien')
        self.tmp = tempfile.mkdtemp(prefix='testhandbuch_')
        # Arbeitsordner: Kopien von Tests/, virtuelle_Geraete/ und den Beispieltests; Ausgaben der Tests
        # (Stanzer, Schreibwerk) landen so in den Kopien, das Projekt bleibt unverändert.
        for name, ziel in (('Tests', os.path.join(self.proj, 'Tests')),
                           ('virtuelle_Geraete', os.path.join(self.proj, 'virtuelle_Geraete')),
                           ('Handbuch-Tests', os.path.abspath(hbtests))):
            shutil.copytree(ziel, os.path.join(self.tmp, name))
        self.trommel = os.path.join(self.tmp, 'trommel.txt')
        self.leere_trommel()

    def hbtext(self, name):
        with open(os.path.join(self.tmp, 'Handbuch-Tests', name), encoding='utf-8') as f:
            return f.read().rstrip('\n')

    def leere_trommel(self, pfad=None):
        with open(pfad or self.trommel, 'w', newline='') as f:
            for a in range(4096):
                f.write('%04o: 00000000000\n' % a)

    def lauf(self, tests, extra=(), trommel=None, out='Test-Protokolle'):
        """Ein Aufruf; liefert (Rückkehrcode, Ausgabe mit gekürzten Pfaden)."""
        if isinstance(tests, str):
            tests = [tests]
        cmd = [sys.executable, self.interp, '--mdverz', self.md, '--trommel', trommel or self.trommel,
               '--out', os.path.join(self.tmp, out)] + list(extra) + list(tests)
        r = subprocess.run(cmd, cwd=self.tmp, capture_output=True, text=True)
        text = (r.stdout + r.stderr).replace(self.tmp + '/', '')
        return r.returncode, text.strip('\n')

    def protokoll(self, name, stufe_datei=None):
        pfad = stufe_datei or os.path.join(self.tmp, 'Test-Protokolle', name, 'protokoll.txt')
        with open(pfad, encoding='utf-8') as f:
            return f.read().split('\n')


def zeilen(text):
    return text.strip('\n').split('\n')


def ab(zl, muster, start=0):
    """Index der ersten Zeile ab start, die mit muster beginnt."""
    for i in range(start, len(zl)):
        if zl[i].lstrip().startswith(muster):
            return i
    raise ValueError('Zeile nicht gefunden: ' + muster)


# ------------------------------------------------------------------------------------------ Abbildungen
def _txt(c, x, y, s, font='DV', size=8, color=INK, anchor='c'):
    c.setFont(font, size)
    c.setFillColor(color)
    if anchor == 'c':
        c.drawCentredString(x, y, s)
    elif anchor == 'l':
        c.drawString(x, y, s)


def _pfeil(c, x1, y1, x2, y2, color=INK, dash=None, head=4.2):
    import math
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(0.9)
    if dash:
        c.setDash(*dash)
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    c.line(x1, y1, bx, by)
    c.setDash()
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(bx + head * 0.5 * math.sin(ang), by - head * 0.5 * math.cos(ang))
    p.lineTo(bx - head * 0.5 * math.sin(ang), by + head * 0.5 * math.cos(ang))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()


def _kasten(c, x, y, w, h, lines, border=INK, dash=None, double=False, lw=1.0, fill=None):
    """Rechteck mit zentriertem Text; lines = [(text, bold)] von oben nach unten."""
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
        c.rect(x, y, w, h, stroke=0, fill=1)
    c.setStrokeColor(border)
    c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    c.rect(x, y, w, h, stroke=1, fill=0)
    if double:
        c.rect(x + 3, y + 3, w - 6, h - 6, stroke=1, fill=0)
    c.restoreState()
    n = len(lines)
    lead = 10.2
    y0 = y + h / 2 + (n - 1) * lead / 2 - 2.6
    for i, (t, b) in enumerate(lines):
        _txt(c, x + w / 2, y0 - i * lead, t, 'DV-B' if b else 'DV', 7.8 if b else 7.4, INK if b else INK)


class Abb1(Flowable):
    """Lebenslauf eines Tests."""
    H = 182

    def wrap(self, aw, ah):
        return FRAME_W, self.H

    def draw(self):
        c = self.canv
        yr1, yr2 = 120, 52                                 # Unterkanten Zeile 1/2
        _kasten(c, 0, yr1, 112, 40, [('Testdatei', True), ('lesen', False)])
        # Raute: Formale Prüfung
        cx, cy, hw, hh = 200, yr1 + 20, 68, 30
        c.saveState()
        c.setStrokeColor(INK)
        c.setLineWidth(1.0)
        p = c.beginPath()
        p.moveTo(cx - hw, cy); p.lineTo(cx, cy + hh); p.lineTo(cx + hw, cy); p.lineTo(cx, cy - hh); p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.restoreState()
        _txt(c, cx, cy + 1.5, 'Formale Prüfung', 'DV-B', 7.8)
        _txt(c, cx, cy - 8.5, 'Format · Marken · Tasten', 'DV', 7.0)
        _kasten(c, 300, yr1, 112, 40, [('Tastenfolge', True), ('vorausinterpretiert', False)])
        _kasten(c, 423, yr1, 112, 40, [('Knotenautomat', True), ('ab Konnektor B / Knoten 19', False),
                                       ('oder Knoten 54', False)])
        _pfeil(c, 112, cy, cx - hw, cy)
        _pfeil(c, cx + hw, cy, 300, cy, GREEN)
        _pfeil(c, 412, cy, 423, cy)
        # Zeile 2
        _kasten(c, 138, yr2, 124, 42, [('Test startet nicht', True), ('Meldung, keine Korrektur', False),
                                       ('Rückkehrcode 16', False)], border=RED, dash=(3, 2.4), lw=1.1)
        _pfeil(c, cx, cy - hh, cx, yr2 + 42, RED, dash=(3, 2.4))
        _txt(c, cx + 5, yr2 + 55, 'Unstimmigkeit', 'DV', 7, RED, 'l')
        _kasten(c, 300, yr2, 112, 42, [('Ergebnisprüfung', True), ('Test wahr / Test falsch', False),
                                       ('(Rückkehrcode 0 / 6)', False)])
        _kasten(c, 423, yr2, 112, 42, [('Endzustand', True), ('Stopp, Fehler, Halt …', False)],
                double=True, lw=1.1)
        _pfeil(c, 479, yr1, 479, yr2 + 42)
        _pfeil(c, 423, yr2 + 21, 412, yr2 + 21, GREEN)
        # Protokoll
        _kasten(c, 0, 0, FRAME_W, 31, [('Protokoll (Bildschirm / Datei, je nach #PROT STUFE)', True),
                                       ('Ausgangsbedingungen · Knotenzeilen · Diagnose bei Befehl 164 · Ende · Ergebnisprüfung', False)],
                border=GREY, dash=(1, 2.4), lw=1.0)
        for x in (356, 479):
            _pfeil(c, x, yr2, x, 31, GREY, dash=(1, 2.4), head=0.01)


class Abb2(Flowable):
    """Die drei Teile einer Testdatei."""
    H = 112

    def wrap(self, aw, ah):
        return FRAME_W, self.H

    def draw(self):
        c = self.canv
        bw = (FRAME_W - 2 * 12) / 3.0
        spec = [
            ('1  Trommeldatei', None,
             ['Trommeldatei:', '#DOK-0001 Text', '#SPEI-0001 3000-3001', '#PROT STUFE=2', '0000: 00003000211',
              '0001: 00003001210', '… Zellen + Testmarken'], []),
            ('2  Tastenfolge', None, ['Tastenfolge:', 'H G R'],
             ['Bedienhandlungen am Pult', '→ Ausgangszustand von', '   Registern und Flags']),
            ('3  Prüfungen (optional)', (3, 2.4), ['Prüfungen:', 'BZ=0004 AC=00000000145 US=1',
                                                  '3001: 00000000045'], ['Sollwerte für den Endzustand']),
        ]
        for i, (titel, dash, mono, grau) in enumerate(spec):
            x = i * (bw + 12)
            c.saveState()
            c.setStrokeColor(INK)
            c.setLineWidth(1.0)
            if dash:
                c.setDash(*dash)
            c.rect(x, 0, bw, self.H, stroke=1, fill=0)
            c.restoreState()
            c.saveState()
            c.setFillColor(FILL)
            c.rect(x + 0.5, self.H - 20, bw - 1, 19.5, stroke=0, fill=1)
            c.restoreState()
            _txt(c, x + bw / 2, self.H - 14, titel, 'DV-B', 8.4)
            y = self.H - 34
            for t in mono:
                _txt(c, x + 8, y, t, 'DVM', 6.8, INK, 'l')
                y -= 9.6
            y -= 3
            for t in grau:
                _txt(c, x + 8, y, t, 'DV', 7.2, MUTED, 'l')
                y -= 9.6


class Abb3(Flowable):
    """Vom Quelltext zum Testauftrag."""
    H = 98

    def wrap(self, aw, ah):
        return FRAME_W, self.H

    def draw(self):
        c = self.canv
        bw, gap, y, h = 95.0, 15.0, 52, 46
        inh = [
            [('Quelltext .asm', True), ('mit Leerbefehl', False), ('164 xxxx', False)],
            [('c82ass.sh', True), ('Assembler', False), ('(c82ass)', False)],
            [('Name.test', True), ('Trommeldatei', False), ('Adresse: Wert # Zeile', False)],
            [('Tests/asm_NNNN_', True), ('Name.txt', True), ('Testauftrag', False)],
            [('Lauf', True), ('Python-Interpreter', False), ('Test wahr / falsch', False)],
        ]
        for i, lines in enumerate(inh):
            x = i * (bw + gap)
            _kasten(c, x, y, bw, h, lines, border=BLUE if i == 3 else INK, lw=1.2 if i == 3 else 1.0)
            if i < 4:
                _pfeil(c, x + bw, y + h / 2, x + bw + gap, y + h / 2)
        x4 = 3 * (bw + gap)
        _kasten(c, x4 - 105, 0, 305, 30, [('von Hand ergänzt: Marken · Tastenfolge · Prüfungen', False)],
                border=GREY, dash=(1, 2.4))
        _pfeil(c, x4 + bw / 2, 30, x4 + bw / 2, y, BLUE)


def abb(cls, nr, text):
    return figure(cls(), 'Abbildung %d: %s' % (nr, text))

# ------------------------------------------------------------------------------------------ Hilfen für den Text
def wd(*f):
    s = float(sum(f))
    return [FRAME_W * x / s for x in f]


def kurz(text, *schnitte):
    """Auszug aus einer Ausgabe: schnitte = Zeilenlisten, dazwischen eine Zeile '…'."""
    out = []
    for i, sch in enumerate(schnitte):
        if i:
            out.append('…')
        out.extend(sch)
    return '\n'.join(out)


def deckblatt(S, stand, ex_datum):
    S += [P('C 8205 – Testhandbuch', 'title'),
          P('Wie ein Test aufgebaut ist, wie er abläuft und wie man sein Ergebnis liest', 'subtitle')]
    S += [P('Dieses Dokument beschreibt das Testkonzept des Projekts: Jeder simulierte „Rechnerlauf“ ist ein Test, '
            'unabhängig davon, ob ihn der Python-Interpreter oder eine KI (Claude-Interpreter) ausführt. Ein Test '
            'besteht aus einer Trommeldatei (Speicherinhalt), einer Tastenfolge (Bedienhandlungen) und optional '
            'Prüfungen (Sollwerte).')]
    S += [P('Quelle: `C8205-Interpreter-Durchführung_eines_Tests.md` (Stand 07.10.2026, mit Abschnitt 2c „Die Trommel '
            'als persistente Datei“), ergänzt um die Beobachtungen aus Läufen mit `c8205_interp.py` (Fassung vom '
            '07.10.2026, zuletzt geändert unter „Änderung 07.10.2026“) und mit dem Assembler `c82ass` (Version 0.2). '
            'Alle gezeigten Bildschirm- und Protokollauszüge des Interpreters sind echte Läufe vom %s auf leerer '
            'Trommel; nur der Auszug aus dem Assemblerlauf (3.3) stammt vom 05.10.2026. Kürzungen sind mit „…“ '
            'gekennzeichnet, lange Pfade sind verkürzt.' % ex_datum)]
    S += note('hinweis', 'Abgrenzung: Wie man den Interpreter aufruft (Schalter, Fehlermeldungen), steht im PDF '
              '„Bedienungsanleitung Python-Interpreter“. Dieses Handbuch erklärt, was ein Test ist und warum er so '
              'aufgebaut ist; für Rechner und Bedienpult siehe „Rechnerbeschreibung“ und „Bedienpult und Peripherie“. '
              'Die Beispieltests dieses Handbuchs (`bspA`, `bspB`, `pruef-wahr`, `vorlage` u. a.) liegen im Ordner '
              '`Handbuch-Tests/` und gehören nicht zu den Regressionstests in `Tests/` (11.1).')
    S += note('achtung', 'Grundsatz „laut scheitern“: Bei einer Unklarheit, einem Widerspruch oder einer fehlenden '
              'Festlegung wird der Test angehalten und das gemeldet – es wird nichts stillschweigend angenommen oder '
              'repariert.')
    S += [P('**Legende**', 'body'), Spacer(1, 1)]
    S += tbl([
        ['Zeichen', 'Bedeutung'],
        ['`Trommeldatei:` `Tastenfolge:` `Prüfungen:`', 'die drei Teile einer Testdatei (Kapitel 2)'],
        ['`#DOK` `#SPEI` `#SPUR` `#PROT`', 'Testmarke: Zeile mit #, die nur für den Test gilt und in der Hardware '
                                           'keine Entsprechung hat (3.2)'],
        ['`--leser1` `--leser2` `--stanzer1` `--sw-ausgabe` `--k0`',
         'Geräte-Zeile: ordnet der Testdatei ein virtuelles Gerät zu (3.4)'],
        ['Python- / Claude-Interpreter', 'die beiden Ausführenden desselben Testformats (1.1, Kapitel 10)'],
        [Raw('<font color="#2563EB"><b>Hinweis</b></font> / <font color="#D97706"><b>Achtung</b></font>'),
         'blauer bzw. orangefarbener Balken: nützliche Ergänzung bzw. Stelle, an der Tests scheitern oder Regelwerk '
         'und Interpreter abweichen'],
        ['grauer Block', 'Dateiinhalt oder Terminalausgabe in Festbreitenschrift; Eingaben stehen hinter `$`'],
        ['Abbildungen',
         Raw('<font color="#15803D"><b>grün</b></font> = positiv / weiter, <font color="#B91C1C"><b>rot gestrichelt'
             '</b></font> = Fehler / Test startet nicht, <font color="#6B7280"><b>grau punktiert</b></font> = '
             'Verweis, schwarz = neutraler Ablauf')],
    ], wd(2.6, 5.4))
    S += [P('Zuerst steht die Kurzanleitung „Test starten“ (Claude-Interpreter ohne Python und Python-Interpreter). '
            'Die Kapitel folgen dem Lebenslauf eines Tests: Einordnung (1), Aufbau (2), die drei Teile Trommeldatei (3, '
            'mit den Regeln der persistenten Trommel in 3.5), Tastenfolge (4) und Prüfungen (5), dann die formale '
            'Prüfung vor dem Start (6), die Diagnose (7), das Protokoll (8), Ein- und Ausgabe (9), der '
            'Claude-Interpreter (10), die Referenztests (11) sowie Checkliste und Vorlage (12).')]
    S.append(PageBreak())


def inhaltsverzeichnis(S):
    S += [Paragraph('Inhaltsverzeichnis', ST['h1']), Spacer(1, 4), make_toc(), PageBreak()]


# ------------------------------------------------------------------------------------------ Kurzanleitung
def kurzanleitung(S):
    S += [Head('Kurzanleitung: Test starten', 0)]
    S += [P('Ein Test besteht aus der Testdatei (Kapitel 2 bis 5) und, wenn er Geräte nutzt, aus Dateien für diese '
            'Geräte. Ausgeführt wird er auf einem von zwei Wegen: durch eine KI ohne Python (Weg A) oder durch '
            '`c8205_interp.py` (Weg B). Beide arbeiten denselben Knotengraphen mit demselben Testformat ab und führen '
            'das Protokoll im selben Format.')]
    S += [Head('A Mit dem Claude-Interpreter (ohne Python)', 1)]
    S += numbered([
        '**Unterhaltung beginnen**, in der Sie Dateien hochladen können. Die KI führt den Knotengraphen von Hand aus; '
        'es wird kein Programm gestartet.',
        '**Regelwerk hochladen**: die Dateien aus Kapitel 10.1 (Ordner `markdown-dateien/`; die Faustregel dort sagt, '
        'was Sie weglassen können).',
        '**Testdatei bereitstellen**: nach Kapitel 3 bis 5 schreiben (Vorlage in 12.2) und hochladen oder in die '
        'Nachricht kopieren. Geräte-Zeilen wie `--leser1` gelten hier als virtuelle Zuordnung (3.4). '
        'Lochstreifendateien legen Sie bereit; die KI fordert sie an, wenn ein Eingabebefehl sie braucht (9.1). '
        'Eine Trommeldatei braucht die KI nicht: Zellen, die der Test nicht nennt, gelten als 0 (3.5).',
        '**Startanweisung** in den Chat schreiben, zum Beispiel wie im Block darunter. Der Text ist ein Vorschlag und '
        'nicht Teil des Regelwerks.',
        '**Ergebnis lesen**: Endzeile, Ergebnisprüfung `Test wahr` oder `Test falsch` und das Protokoll im Format der '
        'Stufe 2 (Kapitel 8). Rückkehrcodes (5.2) gibt es nur beim Python-Aufruf. Stanzer- und '
        'Schreibwerk-Ausgabe stellt die KI am Testende als Datei bereit (9.3). Weicht das Ergebnis vom Python-Lauf '
        'ab, siehe 1.1 (Rolle jetzt).'])
    S += code('Führe den hochgeladenen Test <Testname> als Claude-Interpreter aus, ohne Python oder ein anderes Programm.\n'
              'Regelwerk sind die hochgeladenen .md-Dateien. Prüfe zuerst die Testdatei formal.\n'
              'Arbeite dann den Knotengraphen (Eingänge_der_Knoten, Variablentabelle T2 in Beschreibung_der_Knoten)\n'
              'Knoten für Knoten ab und führe das Protokoll in der Stufe, die #PROT STUFE vorgibt.\n'
              'Bei jeder Unklarheit, jedem Widerspruch und jeder fehlenden Festlegung: anhalten und rückfragen,\n'
              'nichts annehmen. Gib am Ende die Endzeile und die Ergebnisprüfung (Test wahr / Test falsch) aus.',
              'Vorschlag für die Startanweisung (Weg A); <Testname> durch den Namen der hochgeladenen Testdatei ersetzen.')
    S += [Head('B Mit dem Python-Interpreter', 1)]
    S += numbered([
        '**Voraussetzung**: Python 3, sonst nichts (nur Standardbibliothek). Im Projektordner liegen `c8205_interp.py` '
        'und daneben `markdown-dateien/`; der Interpreter liest daraus `Eingänge_der_Knoten.md` und '
        '`Beschreibung_der_Knoten.md` (anderer Ort: Schalter `--mdverz`). Außerdem muss die Trommeldatei '
        '`virtuelle_Geraete/Trommel/trommel.txt` vorhanden sein; leer erzeugen mit `python3 erzeuge_leere_trommel.py` '
        '(anderer Ort: Schalter `--trommel`; 3.5).',
        '**Testdatei ablegen**: in `Tests/` (die Endung ist frei, der Assembler erzeugt `.test`). Geräte ordnen Sie per '
        'Schalter oder Zeile zu (3.4); Dateien dafür liegen üblicherweise unter `virtuelle_Geraete/`.',
        '**Starten**: direkt oder mit dem Wrapper, der das Protokoll nach `Test-Protokolle/` schreibt. Die Trommel '
        'behält ihren Inhalt von Test zu Test und von Aufruf zu Aufruf; für einen Lauf auf leerer Trommel vorher '
        '`python3 erzeuge_leere_trommel.py` aufrufen (3.5).',
        '**Ergebnis lesen**: Endzeile `Ende: …`, Ergebnisprüfung `Test wahr` oder `Test falsch` und der Rückkehrcode '
        '(5.2: 0 wahr, 4 ohne Prüfung, 6 falsch, 8 Laufzeitfehler, 16 Vorab-Prüfung negativ oder Trommeldatei '
        'fehlerhaft, 2 ungültiger Aufruf). Knotenzeilen im Protokoll erscheinen mit `--knotentest` und '
        '`#PROT STUFE=2` (Kapitel 8).'])
    S += code('$ python3 erzeuge_leere_trommel.py                  # leere Trommel (alle 4096 Zellen 0)\n'
              '$ python3 c8205_interp.py Tests/0015-030.txt\n'
              '$ ./c8205_interpreter.sh 0015-030.txt        # Linux/macOS, Protokoll: Test-Protokolle/0015-030.log\n'
              'C:\\> c8205_interpreter.bat 0015-030.txt      # Windows\n'
              '$ ./compute_all_tests.sh                     # Sammellauf über Tests/*.txt (11.1)',
              'Aufrufe nach README und Bedienungsanleitung. Für dieses Handbuch ausgeführt wurde der Aufruf mit python3; '
              'die Wrapper nicht.')
    S += note('hinweis', 'Alle Schalter, die Geräte und die Fehlermeldungen des Python-Interpreters beschreibt das PDF '
              '„Bedienungsanleitung Python-Interpreter“ (Quelle: `Python_Interpreter.md`). Wo sich die beiden Wege bei '
              'Ein- und Ausgabe unterscheiden, zeigt die Gegenüberstellung in 9.3. Die Kurzanleitung steht auch als '
              'Abschnitt 1b in `Durchführung_eines_Tests.md`.')
    S.append(PageBreak())


# ------------------------------------------------------------------------------------------ Kapitel 1 und 2
def kap1_2(S):
    S += h1('1 Einordnung und Voraussetzungen')
    S += [P('Das Gesamtprojekt beschreibt zwei Aspekte: erstens die Hardware und die in der Elektronik angelegten '
            'Beziehungen (Knotenautomat), zweitens davon abweichend oder ergänzend die Annahmen für die interpretative '
            'Abarbeitung eines Befehls. Der zweite Aspekt ist die Voraussetzung jedes Tests.')]
    S += bullets([
        '**Alle Zeiten sind 0.** Zeitliche Abhängigkeiten werden in ihrer Reihenfolge betrachtet, führen aber nicht zu '
        'Wartezeiten.',
        '**Der Rechner ist eingeschaltet.** Jeder Test setzt das voraus.',
        '**Der Vor-Zustand** vom Einschalten bis zum Beginn der Interpretation der Befehlsschleife am Konnektor B '
        '(Knoten 1 des Graphen) ist vollständig bestimmt durch die betätigten Tasten und Schalter und den '
        'Trommelinhalt, d. h. den Inhalt der persistenten Trommel, nachdem die Zeilen des Tests auf sie geschrieben '
        'wurden (3.5). Register, die der Test nicht nennt, starten mit 0.'])
    S += h2('1.1 Zwei Ausführende, ein Format')
    S += [P('Ein und derselbe Test kann auf zwei Arten ausgeführt werden. Beide benutzen denselben Knotengraphen, '
            'dasselbe Testformat und dasselbe Protokollformat.')]
    S += tbl([
        ['', 'Python-Interpreter', 'Claude-Interpreter (KI)'],
        ['Wie', '`c8205_interp.py` läuft den Knotengraphen deterministisch und automatisiert ab',
         'Eine KI erhält das komplette Regelwerk als Kontext und die Testdatei und arbeitet den Graphen manuell, '
         'Knoten für Knoten, ab'],
        ['Stärke', 'schnell, reproduzierbar (bei definiertem Trommelstand, 3.5)',
         'erlaubt Rückfragen und Erläuterungen während der Abarbeitung'],
        ['Schwäche', 'keine Rückfrage bei unklaren Stellen: der Lauf meldet einen Stub und bricht ab',
         'langsamer, nicht deterministisch reproduzierbar (abhängig von Modell und Sitzung)'],
        ['Trommel', 'persistente Datei `trommel.txt`; behält ihren Inhalt über Tests und Aufrufe hinweg',
         'keine Trommeldatei; nicht genannte Zellen gelten als 0 (wie ein Python-Lauf auf leerer Trommel)'],
        ['Rolle jetzt', 'Normalbetrieb für laufende Testläufe',
         'unabhängige Gegenprobe: weichen die Ergebnisse ab, liegt ein Fehler in einem von beiden vor – oder eine '
         'unklare Stelle im Regelwerk'],
        ['Rolle bei Erweiterungen', 'übernimmt neue oder geänderte Befehle erst danach',
         'neue oder geänderte Befehle/Anweisungen werden zuerst hier durchgespielt'],
    ], wd(1.5, 3.2, 3.6), first_bold=True)
    S += note('hinweis', 'Diese Aufgabenteilung gilt modellneutral für jede interpretierende KI, nicht nur für Claude. '
              'Bei unklaren Regelwerk-Stellen darf die ausführende KI Rückfragen stellen, statt eigenmächtig zu '
              'entscheiden. Die Zahl der Rückfragen hängt vom Modell ab.')
    S += h2('1.2 Ein Test im Überblick')
    S += abb(Abb1, 1, 'Lebenslauf eines Tests. Rot gestrichelt: der Fall, in dem der Test nicht startet („laut '
                      'scheitern“). Der Startpunkt im Knotenautomaten hängt vom Zustand nach der Tastenfolge ab (4.4).')
    S += [P('Der Lauf endet immer mit einer Endzeile; die Ergebnisprüfung erfolgt nur nach ordnungsgemäßem Ende. '
            'Zwischendurch, aber nur bei Bedarf: die Diagnose bei Befehl 164 (Kapitel 7) und die Ein-/Ausgabe über '
            'Geräte (Kapitel 9).')]

    S += h1('2 Aufbau einer Testdatei')
    S += abb(Abb2, 2, 'Die drei Teile einer Testdatei (eine Textdatei, die drei Teile stehen in dieser Reihenfolge, '
                      'Teil 3 darf fehlen). Die Zeilen `Trommeldatei:`, `Tastenfolge:` und `Prüfungen:` leiten jeweils '
                      'einen Teil ein.')
    S += tbl([
        ['Teil', 'Pflicht?', 'Legt fest', 'Kapitel'],
        ['Trommeldatei', 'ja', 'die Zellen, die vor dem Start auf die Trommel geschrieben werden (ein Ausschnitt; sie '
                               'überlagern deren Inhalt, 3.5), die Testmarken (`#DOK`, `#SPEI`, `#SPUR`, `#PROT`) und '
                               'die Geräte-Zeilen', '3'],
        ['Tastenfolge', 'ja', 'Bedienhandlungen am Pult → Ausgangszustand von Registern und Flags vor Konnektor B', '4'],
        ['Prüfungen', 'nein', 'Sollwerte für Register, Flags, Speicherzellen und Ausgabedateien nach Testende', '5'],
    ], wd(1.5, 1.0, 6.2, 1.0), first_bold=True)
    S += note('hinweis', 'Dateiname: `NNNN-<Operationscodes>.txt` für Testdateien in `Tests/` (z. B. '
              '`0004-210_544_020.txt`), `asm_NNNN_<Programmname>.txt` für Testaufträge aus Assemblerläufen. Das '
              'Protokoll trägt denselben Namen mit der Endung `.log` in `Test-Protokolle/`.')


# ------------------------------------------------------------------------------------------ Kapitel 3
def kap3(S, ex):
    S += h1('3 Schritt 1: die Trommeldatei')
    S += [P('Der Trommelinhalt, den ein Test braucht, wird vor Beginn jedes Tests als Textdatei mit festem Aufbau '
            'übermittelt (Abschnitt `Trommeldatei:` der Testdatei). Er ist nur ein Ausschnitt (adressweise) der '
            'Gesamttrommel: Der Interpreter schreibt ihn vor dem Start auf die Trommel und überlagert damit die '
            'vorhandenen Werte; Zellen, die er nicht nennt, behalten ihren bisherigen Inhalt (3.5).')]
    S += h2('3.1 Zeilenformat')
    S += code('Adresse: Wert [# Bemerkung]')
    S += bullets([
        '**Adresse:** 4 Oktalstellen (12 Bit). **Wert:** 11 Oktalstellen (33 Bit), mit Vornullen ergänzt. Alle Zahlen '
        'oktal.',
        'Leerzeilen werden übergangen. Zeilen mit `#` sind Kommentar; ein Kommentar darf – durch mindestens ein '
        'Leerzeichen getrennt – hinter einer Adresse:Wert-Zeile stehen und gilt ab dem `#` bis Zeilenende.',
        'Der Wert besteht aus vier führenden Stellen „beliebig“ (z₀–z₁₁) und sieben Stellen Befehl: `0000 3000 211` = '
        'Adresse 3000, Operation 211.'])
    S += code('# Beginn Programmbefehle\n0000: 00003000211\n0001: 00003001210\n0002: 00000000020\n'
              '# Beginn Datenbereich\n3000: 00000000100 # Startwert der Schleife\n3001: 00000000045')
    S += note('achtung', 'Eine nicht genannte Zelle behält ihren bisherigen Inhalt; auf leerer Trommel (und beim '
              'Claude-Interpreter) ist das 0. Als Befehl gelesen ist 0 der unbedingte Sprung nach Adresse 0000. '
              'Programme müssen deshalb mit einem Stopp-Befehl `00000000020` enden, sonst läuft der Test in eine '
              'Endlosschleife und bricht nach dem Knotenlimit ab.')
    S += h2('3.2 Testmarken')
    S += [P('Testmarken sehen aus wie Kommentare, sind aber keine folgenlosen Kommentare. Sie sind eine von der '
            'Hardware abweichende Ergänzung, die ausschließlich der besseren Durchführung der Tests dient.')]
    S += tbl([
        ['Marke', 'Bedeutung', 'Hinweise'],
        ['`#DOK-xxxx <Text>`', 'freier Text zum Test; xxxx oktal. Löst beim Leerbefehl 164 mit der Adresse xxxx die '
                               'Diagnoseausgabe aus (Kapitel 7)',
         'darf mehrfach mit derselben Nummer vorkommen (Ausgabe in Dateireihenfolge)'],
        ['`#SPEI-xxxx ssss-eeee`', 'gibt zusätzlich den Speicherbereich ssss bis eeee aus',
         'ssss und eeee oktal, gültige Spanne (ssss ≤ eeee); mehrfach zulässig; nach Regelwerk nur zu einem '
         'vorhandenen `#DOK-xxxx` (Abweichung im Interpreter: Kapitel 6)'],
        ['`#SPUR-xxxx aaaa`', 'gibt zusätzlich die ganze Spur aus, in der aaaa liegt (alle 32 Zellen, in physischer '
                              'Zugriffsreihenfolge der Trommel)',
         'welcher Sektor von aaaa gemeint ist, spielt keine Rolle (Bahn-Nr. = aaaa ohne die unteren 5 Bit); '
         'mehrfach zulässig'],
        ['`#PROT STUFE=n`', 'Protokolltiefe: 0 / 1 / 2 (Kapitel 8)', 'höchstens einmal; fehlt sie, gilt Stufe 1'],
    ], wd(2.2, 3.6, 3.6))
    S += [P('Reihenfolge der Ausgabe zu einem xxxx: zuerst alle `#DOK`-Texte, danach alle `#SPEI`-Bereiche, danach '
            'alle `#SPUR`-Spuren, jeweils in Dateireihenfolge.')]
    S += h2('3.3 Testauftrag aus einem Assemblerlauf')
    S += [P('Eine Trommeldatei von Hand zu schreiben ist wegen der oktalen Adressen mühsam. Für Programme in '
            'Assemblersprache übernimmt das der Assembler `c82ass`: Er wandelt ein mit symbolischen Adressen '
            'geschriebenes Programm in Oktalbefehle um. Von den erzeugten Dateien wird nur `<name>.test` benötigt; sie '
            'enthält die Trommeldatei im Zeilenformat von 3.1, jede Zeile mit der zugehörigen Quelltextzeile als '
            'Bemerkung, dazu Platzhalter für Testmarken und Tastenfolge.')]
    S += code('2007: 00002006241 # beginn: 241 i ; I:=0\n2010: 00002003210 # schleife: 210 azv ; ac:=(azv+i)')
    S += abb(Abb3, 3, 'Vom Quelltext zum Testauftrag. Von Hand ergänzt werden nur die Debug-Anweisungen, die '
                      'Startbedingungen und die Prüfungen.')
    S += numbered([
        'Im Assembler-Quelltext an der Stelle, an der ausgewertet werden soll, einen Leerbefehl 164 mit einer '
        'vierstelligen Debug-Nummer als Adresse vorsehen, z. B. `halt: 164 0001`. Die Nummer muss zu den Testmarken '
        '`#DOK-`/`#SPEI-`/`#SPUR-` des Testauftrags passen.',
        '`c82ass.sh -p <Projekt> -s <name>` aufrufen.',
        '`<name>.test` als Testauftrag `Tests/asm_NNNN_<name>.txt` ablegen und die Platzhalter ergänzen: die '
        'Testmarken (`#DOK`, `#SPEI`, `#PROT STUFE=n`), die Tastenfolge, ggf. den Leerbefehl 164 und optional den '
        'Abschnitt `Prüfungen:`.'])
    S += [P('Der Assembler meldet am Ende seines Laufs, welche Dateien er erzeugt hat (echte Ausgabe von `c82ass` v0.2 '
            'für `bsp_5_16`, Auszug vom 05.10.2026):')]
    S += code('C8205 Assembler C82aas Version 0.2\nPass 0\nVerarbeite \'c82ass.makros\', Erzeuge Macroersetzungen\n\n'
              'Pass 1\nLöse Literale auf\n\n'
              'Pass 2\nLöse Symbole auf nach Projekt_1/bsp_5.16/bsp_5_16.log und Projekt_1/bsp_5.16/bsp_5_16.sym\n\n'
              'Pass 3\nErzeuge Kennzeichen-Befehle in Objektdatei Projekt_1/bsp_5.16/bsp_5_16.obj\n…\n'
              'Ausgabe als Minimalprogramm-Objektdatei nach: Projekt_1/bsp_5.16/bsp_5_16.obj\n'
              'Ausgabe der formatierten Speicherbelegung nach: Projekt_1/bsp_5.16/bsp_5_16.dmp\n'
              'Ausgabe der Testdatei (Spalten 1,3,4,5 fuer K1=00/01) nach: Projekt_1/bsp_5.16/bsp_5_16.test')
    S += [P('Beispiel eines fertigen Testauftrags (gekürzt; Quelltext `Assembler/Projekt_1/bsp_5.16/bsp_5_16.asm`, '
            'Test `Tests/asm_0001_bsp_5_16.txt`):')]
    S += code('Trommeldatei:\n#DOK-0001 Test eines mit Assembler assemblierten Programmes\n#SPEI-0001 2027-2033\n'
              '#SPEI-0001 2100-2104\n#PROT STUFE=2\n0000: 00002000000 # 000 go\n2000: 00002007000 # go: 000 beginn\n'
              '... (weitere Zeilen unverändert aus bsp_5_16.test)\n'
              '2025: 00000001164 # halt: 164 0001 ;DEBUG Nr. 0001 aktivieren\n2026: 00000000020 # 020 0 ;halt\n...\n\n'
              'Tastenfolge:\nH G R')
    rc, out = ex.lauf('Tests/asm_0001_bsp_5_16.txt')
    zl = zeilen(out)
    S += [P('Im Beispiel startet `H G R` bei Adresse 0000; dort steht ein Sprung zum Programmanfang. Der echte Lauf '
            'dieses Testauftrags endet mit `Test wahr` (Rückkehrcode %d):' % rc)]
    S += code('$ python3 c8205_interp.py Tests/asm_0001_bsp_5_16.txt\n' +
              kurz(out, zl[:1], [zl[ab(zl, 'Ende:')]], zl[ab(zl, 'Ergebnispruefung'):ab(zl, 'Ergebnispruefung') + 1] +
                   ['Test wahr']))
    S += [P('Die Knotenzahl der Endzeile ist fassungsabhängig (Hinweis in 8.2).', 'cap')]
    S += h2('3.4 Geräte-Zeilen --leser1, --leser2, --stanzer1, --sw-ausgabe und --k0')
    S += [P('Der Testauftrag kann seine Geräte selbst mitbringen: die Lochstreifen für Leser 1 und 2, die Ausgabe des '
            'Stanzers, die Schreibwerk-Ausgabe (Kanal K2) und die K0-Eingabequelle. Dazu steht je eine Zeile in der '
            'Testdatei, an beliebiger Stelle, üblicherweise bei den Testmarken im Teil `Trommeldatei:`. Anders als die '
            'Testmarken beginnen diese Zeilen nicht mit `#`, sondern wie die gleichnamigen Schalter des '
            'Python-Interpreters mit `--`. Ein Kommentar `# …` am Zeilenende wird ignoriert.')]
    S += tbl([
        ['Zeile', 'Bedeutung', 'Hinweise'],
        ['`--leser1 PFAD`', 'Lochstreifendatei des Lesers 1 (Kanal K1)',
         'Datei oder Ordner; ein Ordner wird in Namensreihenfolge gelesen, für einen Test ist eine einzelne Datei '
         'sicherer; höchstens einmal'],
        ['`--leser2 PFAD`', 'Lochstreifendatei des Lesers 2 (Kanal K2)', 'wie `--leser1`'],
        ['`--stanzer1 PFAD`', 'Ausgabedatei bzw. Ausgabeordner des Stanzers (Kanal K1)',
         'Datei `stanzer-ausgabe.txt`; nur bei tatsächlicher Ausgabe angelegt; höchstens einmal'],
        ['`--sw-ausgabe PFAD`', 'jede Ausgabe auf K2 geht in die Datei `PFAD/sw-ausgabe.txt` statt ans Terminal',
         'die Datei wird nur bei tatsächlicher Ausgabe angelegt und später angehängt; WRZL schließt die aktuelle Zeile '
         'ab; höchstens einmal'],
        ['`--k0 datei=PFAD`', 'die Eingaben für K0 (T und SW) kommen aus Datei oder Ordner statt vom Terminal',
         'ein Zeichen oder Name je Zeile; höchstens einmal; der Pfad muss vorhanden sein'],
    ], wd(2.3, 3.5, 3.9))
    S += bullets([
        '**Vorrang:** Ist derselbe Schalter beim Aufruf angegeben, gilt die Kommandozeile; die Zeile der Testdatei wird '
        'übergangen.',
        '**Relative Pfade** gelten wie auf der Kommandozeile vom aktuellen Ordner des Aufrufs aus, nicht vom Ordner '
        'der Testdatei.',
        '**Formale Prüfung:** Zeile ohne Wert, doppelte Zeile, `--k0` ohne `datei=` und ein nicht vorhandener '
        '`--k0`-, `--leser1`- oder `--leser2`-Pfad lassen den Test nicht starten.',
        '**Claude-Interpreter:** Jede dieser Zeilen gilt als virtuelle Zuordnung bei der Testdefinition.'])
    S += code('Trommeldatei:\n#DOK-0001 Unterprogrammtechnik, Sprung mit Rückkehrabsicht, 025\n--sw-ausgabe SW-Ausgabe\n'
              '#SPEI-0001 2012-2027\n#PROT STUFE=2\n...')
    rc, out = ex.lauf('Handbuch-Tests/sw-zeile.txt')
    zl = zeilen(out)
    ausg = open(os.path.join(ex.tmp, 'SW-Ausgabe', 'sw-ausgabe.txt'), encoding='utf-8').read().strip()
    S += [P('Der Lauf dieses Tests (`Handbuch-Tests/sw-zeile.txt`: drei Unterprogramme geben je ein Zeichen aus) '
            'schreibt die Zeichen A B C nach `SW-Ausgabe/sw-ausgabe.txt`; am Terminal erscheint nur die Diagnose, keine '
            'Schreibwerk-Zeichen:')]
    S += code('$ python3 c8205_interp.py Handbuch-Tests/sw-zeile.txt\n' +
              kurz(out, zl[:4], ['… (Speicherzeilen 2012 bis 2027) …'],
                   [zl[ab(zl, 'Ende:')]], ['Test wahr']) + '\n\n$ cat SW-Ausgabe/sw-ausgabe.txt\n' + ausg)
    S += note('hinweis', 'Die Ausgabe ist `ABC` oder `abc`: Die Zeichenlage KB/GB des Schreibwerks wird beim Start '
              'zufällig gesetzt. Wer die Ausgabe mit `--pruefe-sw-ausgabe` prüfen will, setzt die Lage im Programm '
              'selbst (Befehl `Um. KB` bzw. `Um. GB`; Beispiel mit echtem Lauf in der Bedienungsanleitung, '
              'Abschnitt 3.6).')
    S += note('hinweis', 'Alle fünf Zeilenformen sind im Interpreter umgesetzt (Änderung 04.10.2026 (4)); im Lauf '
              '`lb-001` (9.1) wird `--leser1` als Zeile verwendet. Die frühere Abweichung zwischen Regelwerk und '
              'Interpreter ist damit beseitigt.')
    kap3_5(S, ex)


def kap3_5(S, ex):
    S += h2('3.5 Die Trommel als persistente Datei (Python-Interpreter)')
    S += [P('„Trommeldatei“ steht im Projekt für zwei verschiedene Dinge, die nicht zu verwechseln sind: den '
            '**Abschnitt** `Trommeldatei:` **einer Testdatei** (die `Adresse: Wert`-Zeilen und Testmarken des Tests; hier '
            'auch „Trommelabschnitt“) und die **Datei** `trommel.txt` des Python-Interpreters (Vorgabe '
            '`virtuelle_Geraete/Trommel/trommel.txt`, Schalter `--trommel`): der ganze Speicher mit 4096 Zeilen. Das '
            'Schlüsselwort `Trommeldatei:` in der Testdatei bleibt unverändert.')]
    S += [P('Regeln für den Python-Interpreter (Einzelheiten, Meldungen und Schalter: Bedienungsanleitung bzw. '
            '`Python_Interpreter.md`, Abschnitt 8.5):')]
    S += numbered([
        '**Dauerhaft.** Die Trommel wird nicht je Test neu aufgebaut, sondern behält ihren Inhalt über Tests und '
        'Aufrufe hinweg. Alle Speicherzugriffe der Befehle (Lesen und Schreiben) laufen über sie; jede geschriebene '
        'Zelle wird in der Datei nachgeführt (spätestens am Ende des Aufrufs).',
        '**Zeilenformat der Datei:** genau 4096 Zeilen `aaaa: ttttttttttt`, Adressen lückenlos aufsteigend `0000` bis '
        '`7777`, keine Kommentar- und Leerzeilen (anders als im Trommelabschnitt der Testdatei).',
        '**Übernahme der Testzeilen:** Vor dem Start des Tests schreibt der Interpreter die `Adresse: Wert`-Zeilen des '
        'Trommelabschnitts auf die Trommel (Überlagerung). Eine Zelle, die der Test nennt, hat danach genau diesen '
        'Wert; eine Zelle, die er nicht nennt, behält den Wert, den sie vorher hatte. Register und Flags starten '
        'dagegen bei jedem Test neu (Kapitel 4).',
        '**Formale Prüfung:** Die Trommeldatei wird einmal je Aufruf vor dem ersten Test geprüft (Kapitel 6). Ist sie '
        'fehlerhaft oder nicht vorhanden, startet kein Test des Aufrufs.',
        '**Zurücksetzen:** Der Interpreter setzt die Trommel nie zurück und legt die Datei nie an. Eine leere Trommel '
        '(alle Zellen `00000000000`) erzeugt das Hilfsskript `erzeuge_leere_trommel.py`; es überschreibt eine '
        'vorhandene Datei.'])
    # echtes Beispiel: nach bspA stehen die Zellen des Tests in der Datei
    tr = os.path.join(ex.tmp, 'trommel_zeigen.txt')
    ex.leere_trommel(tr)
    ex.lauf('Handbuch-Tests/bspA.txt', trommel=tr)
    tz = open(tr, encoding='utf-8').read().split('\n')
    n = len(tz) - 1
    sel = [tz[0], tz[1], tz[2], tz[3], '…', tz[0o3000], tz[0o3001], tz[0o3002], '…', tz[n - 1]]
    S += code('\n'.join(sel),
              'Auszug aus `trommel.txt` nach einem Lauf von `bspA` (Kapitel 8): %d Zeilen, 18 Byte je Zeile. Die vom Test '
              'geschriebenen Zellen 0000 bis 0002 und 3000, 3001 stehen in der Datei, alles übrige (z. B. 3002) ist 0.' % n)
    S += [P('**Folgen für die Testdefinition**', 'body')]
    S += bullets([
        'Das Ergebnis eines Tests hängt vom Trommelstand vor dem Test ab, sobald der Test eine Zelle **liest oder '
        'prüft** (Befehle, `#SPEI`/`#SPUR`, Speicherprüfzeilen in `Prüfungen:`), die er nicht selbst im '
        'Trommelabschnitt belegt. Solche Tests sind nur auf leerer Trommel reproduzierbar.',
        '**Empfehlung:** Ein Test nennt alle Zellen, auf die sich sein Ergebnis stützt, auch die mit Wert 0 '
        '(`aaaa: 00000000000`). Dann ist er von der Vorgeschichte unabhängig. Wo das nicht gewollt ist, wird vor dem '
        'Lauf eine leere Trommel erzeugt.',
        '**Reihenfolge:** Bei mehreren Tests auf derselben Trommel (mehrere Testdateien in einem Aufruf, mehrere '
        'Aufrufe nacheinander, Sammelläufe wie `compute_all_tests.sh`) bestimmt die Reihenfolge den Anfangszustand '
        'jedes Tests.',
        '**Sollwerte** (Kapitel 5 und Regressionsläufe) gelten für einen Lauf auf leerer Trommel oder für einen Test, '
        'der seine Zellen selbst nennt.',
        '**Protokoll:** Der Abschnitt „Ausgangsbedingungen“ (8.1) zeigt nur die vom Test geschriebenen Zeilen, nicht '
        'den ganzen Trommelinhalt vor dem Test.'])
    # echtes Beispiel: Reihenfolgeeffekt
    ex.leere_trommel()
    rc1, out1 = ex.lauf('Tests/bsp_seite_42_025-sw-ausgabe.test')
    ex.leere_trommel()
    ex.lauf('Tests/bsp_seite_40.test')
    rc2, out2 = ex.lauf('Tests/bsp_seite_42_025-sw-ausgabe.test')
    z2 = zeilen(out2)
    fehl = [l.strip() for l in z2 if l.strip().endswith('FEHLER')]
    ex.leere_trommel()
    S += [P('Echtes Beispiel: `bsp_seite_42_025-sw-ausgabe` prüft die Zellen 2024 bis 2027 auf 0, ohne sie zu '
            'belegen. Auf leerer Trommel ist er `Test wahr` (Rückkehrcode %d); nach `bsp_seite_40`, das 2024 bis 2026 '
            'belegt, ist er `Test falsch` (Rückkehrcode %d):' % (rc1, rc2))]
    S += code('$ python3 erzeuge_leere_trommel.py\n$ python3 c8205_interp.py Tests/bsp_seite_42_025-sw-ausgabe.test\n'
              '…\nTest wahr                                   # Rückkehrcode %d\n\n'
              '$ python3 erzeuge_leere_trommel.py\n$ python3 c8205_interp.py Tests/bsp_seite_40.test\n'
              '$ python3 c8205_interp.py Tests/bsp_seite_42_025-sw-ausgabe.test\n…\n%s\n…\nTest falsch                                  '
              '# Rückkehrcode %d' % (rc1, '\n'.join(fehl), rc2))
    S += [P('**Claude-Interpreter.** Er hat keine Trommeldatei. Er legt nur die Zeilen des Trommelabschnitts an; '
            'Zellen, die der Test nicht nennt, gelten als 0, entsprechend einem Python-Lauf auf leerer Trommel. Für die '
            'Gegenprobe (1.1) wird der Python-Lauf deshalb auf einer frisch erzeugten, leeren Trommel gestartet.')]


# ------------------------------------------------------------------------------------------ Kapitel 4
def kap4(S, ex):
    S += h1('4 Schritt 2: die Tastenfolge')
    S += [P('Nach der Trommeldatei folgt eine Tastenfolge. Sie wird auf die Ebene von Registern (mit ihren Bits) und '
            'Flags (0/1) heruntergebrochen und legt so den Ausgangszustand des Rechners vor dem Eintritt in Konnektor B '
            'vollständig fest.')]
    S += note('hinweis', 'Prinzip: Tastenfolgen werden nicht nur als Rohschalterzustände betrachtet, sondern bis zur '
              'Wirkung der dadurch geladenen oder ausgelösten Instruktion vorausinterpretiert. Dadurch kann der Automat '
              'ab Konnektor B im regulären Vier-Phasen-Zyklus laufen, ohne dass der manuelle Eingriff selbst im '
              'Knotengraphen als Sonderfall behandelt werden müsste. Beispiel: G lädt die Instruktion 0000 000 '
              '(Sprung nach 0000); dass BZ danach 0000 ist, ist das vorweggenommene Ergebnis dieses Sprungs '
              '(⟨BZ⟩ := a, ANWEISUNG-007), nicht die unmittelbare Wirkung von G selbst.')
    S += h2('4.1 Beispiel A: Ansprung des Speicherplatzes 0000 (direkt)')
    S += [P('Trommeldatei wie in Abschnitt 3.1, Tastenfolge `H G R`:')]
    S += tbl([
        ['Schritt', 'Aktion', 'Wirkung auf Register und Flags'],
        ['1', 'Schalter H-R → „H“', 'Flag H := 1'],
        ['2', 'Taste „G“', 'alle Flags außer H, T, BS und SP werden gelöscht, danach US := 1; BR := „0000 000“ '
                           '(unbedingter Sprung nach Speicherplatz 0000, AR := 0000, OR := 000); K0 angewählt, SW nicht '
                           'gedrückt → Flag T := 1; ⟨BZ⟩ := 0 als vorweggenommenes Ergebnis des Sprungs'],
        ['3', 'Schalter H-R → „R“', 'Flag H := 0, US := 0; die Interpretation setzt bei Konnektor B fort, mit '
                                    'BZ = 0000'],
    ], wd(1.0, 2.6, 8.4))
    S += h2('4.2 Beispiel B: Ansprung eines beliebigen Speicherplatzes (hier 0004)')
    S += code('# Beginn Programmbefehle\n0004: 00003000211\n0005: 00003001210\n0006: 00000000020\n'
              '# Beginn Datenbereich\n3000: 00000000100\n3001: 00000000045\n\nTastenfolge:\n'
              'H G M-gedrückt-halten E E E E M-loslassen R')
    S += tbl([
        ['Schritt', 'Aktion', 'Wirkung auf Register und Flags'],
        ['1', 'H-R → „H“', 'Flag H := 1'],
        ['2', 'Taste „G“', 'alle Flags außer H, T, BS, SP := 0; BR := „0000 000“; K0 angewählt, T := 1'],
        ['3', '„M“ gedrückt halten', 'OR := OR ∨ 025 → BR := „0000 025“ (Sprung mit Rückkehrabsicht, Adresse 0000)'],
        ['4', '1. „E“', 'Befehlsentnahme (Phase II) durch gehaltenes M verhindert; BZ := 0001, AR := 0001; ⟨AC⟩ := '
                        '0000 0002 000 (Rücksprungadresse BZ+1 im Adressfeld)'],
        ['5', '2. „E“', 'BZ := 0002, AR := 0002; ⟨AC⟩ := 0000 0003 000'],
        ['6', '3. „E“', 'BZ := 0003, AR := 0003; ⟨AC⟩ := 0000 0004 000'],
        ['7', '4. „E“', 'BZ := 0004, AR := 0004; ⟨AC⟩ := 0000 0005 000'],
        ['8', '„M“ loslassen', 'die OR-Verknüpfung mit 025 entfällt für Folgeschritte'],
        ['9', 'H-R → „R“', 'Flag H := 0; Interpretation bei Konnektor B mit BZ = 0004 → der nächste Befehl wird aus '
                           'Adresse 0004 entnommen'],
    ], wd(1.0, 2.6, 8.4))
    S += note('hinweis', 'Das Original beschreibt bei diesem Fall als ersten Schritt „Schalter H-R → R“. Das war '
              'vermutlich ein Tippfehler: G, M und E sind nur bei Stellung „H“ wirksam. Die Tastenfolge verwendet '
              'deshalb „H“; im Bedienpult-Dokument (Abschnitt 4.4) wurde das am 02.10.2026 ebenfalls korrigiert.')
    rc, out = ex.lauf('Handbuch-Tests/bspB.txt', ['--knotentest', '--NO-TERMOUT', '--out',
                                                  os.path.join(ex.tmp, 'bspB.log')])
    pl = ex.protokoll('', os.path.join(ex.tmp, 'bspB.log'))
    i0 = ab(pl, 'Tastenfolge:')
    i1 = ab(pl, 'Nicht spezifizierte', i0)
    S += [P('Das echte Protokoll (Stufe 2) dieses Beispiels (`Handbuch-Tests/bspB.txt`) zeigt dieselbe Wirkung. Die '
            'Zeilen der Tasten sind vom Interpreter formuliert; der AC steht oktal, elf Stellen:')]
    S += code('\n'.join(l.rstrip() for l in pl[i0:i1 + 1]))
    S += note('hinweis', 'Der Protokollauszug stammt aus `Handbuch-Tests/bspB.txt` mit dem Stopp-Befehl in Zelle 0006. '
              'Die Trommeldatei in „Durchführung eines Tests“ (3.2) nennt für den Stopp die Zelle 0002 mit dem Wert '
              '`00000004020`; ein Programm ab 0004 liefe damit nicht zu einem Stopp, sondern über Zelle 0006 (auf '
              'leerer Trommel = 0, Sprung nach 0000) in eine Endlosschleife.')
    S += h2('4.3 Festlegungen zu den Tasten M, Ü, E, ST, BS, SP')
    S += tbl([
        ['Taste', 'Festlegung'],
        ['E unter gehaltenem M',
         'Jedes E führt Phase IV (BR = ⟨AR⟩ 025: Sprung mit Rückkehrabsicht mit Löschen) und Phase I aus; Phase II ist '
         'gesperrt. Nach dem n-ten E (Start mit BZ = b): BZ := b+n, AR := BZ, und der AC enthält im Adressfeld '
         '(z₁₂–z₂₃) den Wert BZ+1, übrige Stellen 0 (das Löschbit von 025 ersetzt den AC, es wird nicht aufsummiert). '
         'Danach steht der Automat vor Phase II: ein E (nach Loslassen von M) beginnt bei Phase II (Knoten 8), ein R '
         'bei Konnektor B.'],
        ['M',
         'M hat nur zwei Stellungen: „gedrückt“ (M+) und „losgelassen“ (M-). Das Token M allein = M+ und sofort M- '
         '(Antippen). Bei M+: OR := OR ∨ 025. Wurde unter M kein E betätigt (Antippen), bleibt BR = „⟨AR⟩ 025“ '
         'aufgestellt und wird erst durch E oder R ausgeführt. Wurde mindestens ein E betätigt, entfällt der Beitrag '
         '025 beim Loslassen; übrige Anteile im OR, z. B. von Ü, bleiben. Ist der aufgestellte BR ein Sprung mit '
         'Rückkehrabsicht (025, 027, 125, 127), beginnt die Ausführung bei Konnektor 4 (Knoten 54), nicht bei '
         'Knoten 19 (4.4).'],
        ['Ü',
         'nur bei gesetztem H wirksam. AR := 7777 (überschreibt unbedingt), OR := OR ∨ 240; BR = „7777 240“ '
         'aufgestellt, noch nicht ausgeführt. Ausgeführt durch E oder R (beides beginnt bei Knoten 19, Ende der '
         'Phase-III-Arbeit). Entsteht BR aus dem Operationsteil eines Stopp-Befehls (02Z, Z<4), ergibt 02Z ∨ 240 nicht '
         'Transport, sondern 26Z (Konjunktion mit negiertem AC): „7777 26Z“. Nur wenn OR vorher 000 war (z. B. nach '
         'G), entsteht 240.'],
        ['ST',
         'einzige Taste, die nicht an H gebunden ist, dafür elektronisch verriegelt: nur wirksam bei Bedingtem Stopp '
         '(BS) oder Unbedingtem Stopp (US). OR := OR ∨ 240; AR unverändert; US := 0; BR aufgestellt (Start bei '
         'Knoten 19 durch E oder R). Nach einem Stopp-Befehl (02Z, 06Z mit Z<4) entsteht dadurch ebenfalls 26Z, nach '
         'G (OR = 000) dagegen 240. US entsteht in einer Tastenfolge durch G und wird durch ST oder R gelöscht; ohne '
         'vorheriges G steht der Rechner zu Beginn nicht im Stopp.'],
        ['BS, SP',
         'einrastende Schalter. BS=1/SP=1 setzen das gleichnamige Flag auf 1, BS=0/SP=0 auf 0; mehr geschieht nicht. '
         'Da die Schalter mechanisch einrasten, lässt G sie unverändert (wie H). Nicht an H gebunden und in jeder '
         'Reihenfolge zu den anderen Tasten zulässig.'],
        ['E (ohne M)',
         'Phase IV und I, dann Phase II und III, danach Halt (Halt-Punkt = Eintritt in Knoten 19). Nur bei gesetztem H '
         'wirksam.'],
        ['Ende der Folge',
         'Eine Tastenfolge darf ohne R enden; dann bleibt der Rechner im Halt, und das Ergebnis ist der Zustand nach '
         'dem letzten Schritt.'],
    ], wd(1.7, 8.3), first_bold=True)
    S += h2('4.4 Wo der Lauf nach „R“ beginnt')
    S += tbl([
        ['Zustand nach der Tastenfolge', 'Startpunkt'],
        ['kein Befehl in BR aufgestellt (z. B. `H G R`)', 'Konnektor B (Knoten 1) mit dem Wert in BZ; Phase I lädt den '
                                                          'Befehl'],
        ['BR aufgestellt, noch nicht ausgeführt (nach Ü, ST, M ohne E oder nach E ohne M)',
         'Knoten 19 (Ende der Phase-III-Arbeit); Phase IV führt BR aus'],
        ['BR von M ist ein Sprung mit Rückkehrabsicht (025, 027, 125, 127)',
         'Konnektor 4 (Knoten 54): Phase III gilt als abgelaufen; nur die Resultatbehandlung (Linksverschiebung des AC) '
         'wirkt, danach wird der nächste Befehl aus der Zelle entnommen, die AR nennt (Knotenfolge 54, 55, 59, 61, '
         '62, 63, 7, 6, 5, 8)'],
        ['Tastenfolge endet im Halt (kein R)', 'es wird nichts mehr ausgeführt; Ergebnis = Zustand nach dem letzten '
                                               'Token'],
    ], wd(4.3, 5.7))
    rc, out = ex.lauf('Tests/tk-001_US_H_M_R.txt', ['--knotentest', '--NO-TERMOUT', '--out',
                                                    os.path.join(ex.tmp, 'tk001.log')])
    pl = ex.protokoll('', os.path.join(ex.tmp, 'tk001.log'))
    j0 = ab(pl, 'R  :')
    j1 = ab(pl, 'K008 PHA')
    S += [P('Zum Lesen der dritte Fall als echter Protokollauszug (`Tests/tk-001_US_H_M_R.txt`, Tastenfolge `H G M R`, '
            'Zelle 0000 enthält den Stopp 020 mit Adresse 0005; aus dem Protokoll der Stufe 2 mit `--knotentest`):')]
    S += code('\n'.join(l.rstrip() for l in pl[j0:j1 + 1]) + '\n…')
    S += [P('Der Lauf beginnt bei `K054 KON 4`, nicht bei Konnektor B. Die Zeile `BR=0000 005` zeigt den Operationsteil '
            'nach der Umstellung auf den Stopp-Befehl; danach wird die Zelle 0000 über Phase II gelesen (BZ = 0001, '
            'AR = 0005).')]
    S += h2('4.5 Weitere typische Bedienfolgen (Fälle 1 bis 6)')
    S += [P('Die folgenden Folgen sind unabhängig voneinander: Jede führt nur die Wirkung ihrer eigenen, tatsächlich '
            'aufgeführten Tasten aus. Es gibt keinen gemeinsamen Vor-Zustand; nicht genannte Register und Flags bleiben '
            'unberührt. Sie dienen der Illustration, sie gehören nicht zum Teststart.')]
    S += tbl([
        ['Fall', 'Folge', 'Wirkung'],
        ['1', '`H G`', 'Flags außer H, T, BS, SP := 0 (damit auch FÜ, FE gelöscht), US := 1; BR := „0000 000“; K0, '
                       'T := 1; BZ unverändert. Ohne R bleibt der Automat im Halt – das Programm ist unterbrochen.'],
        ['2', '`ST`', 'nur im Stopp (BS oder US) wirksam: OR := OR ∨ 240, AR bleibt, US := 0; BR aufgestellt, Start bei '
                      'Knoten 19 durch E oder R. H bleibt unberührt.'],
        ['3', '`H Ü R`', 'Ü wirkt, weil H gesetzt ist: AR := 7777, BR := „7777 (OR ∨ 240)“. R: H := 0, Fortsetzung bei '
                         'Phase IV → Ausführung von BR.'],
        ['4', '`H M R`', 'M (Antippen): OR := OR ∨ 025 → BR := „⟨AR⟩ (OR ∨ 025)“; kein E unter M, BR bleibt '
                         'aufgestellt. R: bei Sprung mit Rückkehrabsicht (025, 027) Fortsetzung bei Konnektor 4 '
                         '(Knoten 54), sonst bei Knoten 19.'],
        ['5', '`H G Ü E`', 'Ergebnis: ⟨7777⟩ := ⟨AC⟩ (AC in Zelle 7777 transportiert). E (einzelner Tipp): Phase IV '
                           'führt „7777 240“ aus, dann Phase I, II, III; danach Halt (H bleibt 1) mit neu geladenem BR '
                           'aus Zelle ⟨BZ⟩.'],
        ['6', '`H G M+ E M- E`', 'Ergebnis: ⟨AC⟩ := ⟨BZ⟩+2. Das erste E (unter M) führt Phase IV aus; Phase II bleibt '
                                 'gesperrt. Nach M-Loslassen führt das zweite E Phase II und III aus; danach Halt. '
                                 'Zusatzregel: Mehrfaches erstes E erhöht die im AC abgelegte Adresse je um 1 '
                                 '(zweimal: ⟨BZ⟩+3, und Zelle 0002 wird als nächster Befehl aufgestellt).'],
    ], wd(0.8, 2.2, 9.0))
    S += [P('Übertragung auf BS, FÜ und FE: BS verhält sich wie US, alle vier Fälle sind anwendbar; zusätzlich '
            'beseitigt auch das Lösen des Schalters BS=0 allein den Stopp (der Ablauf geht dann wie bei nicht erfüllter '
            'Schalterbedingung weiter). FÜ: nur Fall 1; dazu ein eigener Fall „H; E gedrückt halten; G; E loslassen“, '
            'der nur den Überlauf löscht statt aller Flags und BR. FE: nur durch G aufhebbar (Fall 1).')]
    S += note('achtung', 'Die Zuordnung „US/BS wird übergangen“ aus dem Bedienpult-Dokument ist keine aus der '
              'Tastenfolge ableitbare Tatsache, sondern gilt nur unter der Zusatzannahme, dass AR/OR zufällig gerade den '
              'US-Befehl enthalten. Das gehört zur Anwendung, nicht zur Definition der Sequenzen. Ob die Hardware nach '
              '„H, G“ wirklich US = 1 anzeigt, ist in der Originaldokumentation nicht belegt und bleibt offen; '
              'wirkungslos ist es in jedem Fall, weil „R“ US unabhängig von seinem Wert überwindet.')


# ------------------------------------------------------------------------------------------ Kapitel 5
def kap5(S, ex):
    S += h1('5 Schritt 3 (optional): Prüfungen')
    S += [P('Nach der Tastenfolge kann ein dritter Abschnitt `Prüfungen:` folgen. Fehlt er, endet der Test ohne '
            'automatische Ergebnisprüfung. Ist er vorhanden, vergleicht der Interpreter nach der interpretativen '
            'Abarbeitung den Endzustand mit den Sollwerten und vermerkt `Test wahr` oder `Test falsch`. Dadurch wird '
            'jeder Testlauf zum Regressionstest: Ein neuer Lauf wird gegen die zuletzt bestätigten Sollwerte '
            'verglichen, ohne dass ein Mensch das Protokoll erneut lesen muss.')]
    S += h2('5.1 Aufbau')
    S += tbl([
        ['Teil', 'Inhalt'],
        ['1. Register-/Flag-Zeile (höchstens eine)',
         'Zuweisungen `SCHLÜSSEL=WERT`, durch Leerzeichen getrennt, beliebige Reihenfolge. Schlüssel: `BZ`, `AC`, `AR`, '
         '`FE`, `FUE` (für FÜ), `BS`, `US`, `E`, `A`, `V1`, `V2` – genau die Teilmenge, die auch die Endzeile des '
         'Interpreters ausgibt. Nicht vorgesehen: OR, H, SP, T, SW, K1–K3. Die Zeile muss nicht vollständig sein; jeder '
         'Schlüssel höchstens einmal. `BZ=` und `AR=`: 4 Oktalstellen · `AC=`: 11 Oktalstellen · Flags: genau 0 oder 1.'],
        ['2. Speicherprüfzeilen (beliebig viele)',
         'je eine pro Zeile im Format `Adresse: Wert` (4 + 11 Oktalstellen): Inhalt, den die Trommeladresse nach '
         'Testende haben muss. Verglichen wird mit dem Trommelstand nach dem Lauf; bei Adressen, die der Test nicht '
         'selbst belegt, hängt der Istwert vom Trommelstand vor dem Test ab (3.5). Dieselbe Adresse darf nicht mit '
         'widersprüchlichem Sollwert auftreten.'],
        ['3. Dateiprüfungen (höchstens zwei)',
         'je eine Zeile `--pruefe-stanzer1 DATEI` bzw. `--pruefe-sw-ausgabe DATEI` (Abschnitt 5.4).'],
    ], wd(2.6, 7.4), first_bold=True)
    S += [P('Fehlt die Register-/Flag-Zeile, beginnt der Abschnitt unmittelbar mit Speicherprüfzeilen. Ein leerer '
            'Abschnitt `Prüfungen:` gilt wie ein fehlender; ein Abschnitt, der nur Dateiprüfungen enthält, ist gültig.')]
    S += code('Prüfungen:\nBZ=0004 AC=00000000145 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0\n3000: 00000000100\n'
              '3001: 00000000045')
    S += h2('5.2 Auswertung und Ausgabe')
    S += bullets([
        'Die Prüfung erfolgt erst nach Abschluss der Abarbeitung, gegen den dann erreichten Endzustand.',
        'Jede angegebene Zuweisung und jede Speicherzeile wird einzeln verglichen; zu jeder wird Soll und Ist '
        'ausgegeben, damit im Fehlerfall sofort sichtbar ist, welche Prüfung abweicht.',
        '`Test wahr` gibt es nur, wenn alle Einzelprüfungen stimmen (einschließlich der Dateiprüfungen nach 5.4); sobald '
        'mindestens eine abweicht, ist das Ergebnis `Test falsch`.',
        'Die Ausgabe erfolgt stufenunabhängig auf dem Bildschirm (wie die Diagnose zu Befehl 164); bei Protokollstufe 2 '
        'zusätzlich am Ende der Protokolldatei (Abschnitt `== 3. Ergebnisprüfung ==`), im Anschluss an die Endzeile.',
        '**Test ohne ordnungsgemäßes Ende:** Bricht die Abarbeitung vorher ab (Stub, Laufzeitfehler, Knotenlimit), wird '
        'keine Prüfung vorgenommen und stattdessen vermerkt, dass sie entfällt (`Ergebnisprüfung: nicht durchgeführt '
        '(Test nicht ordnungsgemäß beendet)`). Ein solcher Fall gilt nicht automatisch als `Test falsch`.'])
    rw, ow = ex.lauf('Handbuch-Tests/pruef-wahr.txt')
    rf, of = ex.lauf('Handbuch-Tests/pruef-falsch.txt')
    zw, zf = zeilen(ow), zeilen(of)
    S += [P('Beispiel: derselbe Lauf, einmal mit richtigem und einmal mit falschem Sollwert (`BZ=0003` statt '
            '`BZ=0004`; `Handbuch-Tests/pruef-wahr.txt` und `pruef-falsch.txt`):')]
    S += code('$ python3 c8205_interp.py Handbuch-Tests/pruef-wahr.txt\n' + ow + '\n\n'
              '$ python3 c8205_interp.py Handbuch-Tests/pruef-falsch.txt\n' +
              '\n'.join(zf[:ab(zf, 'Ende:') + 1] + zf[ab(zf, 'Ergebnispruefung'):ab(zf, 'Ergebnispruefung') + 3]) +
              '\n… (übrige Zeilen wie oben, alle OK)\n' + zf[-1])
    S += [P('Der Interpreter meldet das Ergebnis auch als Rückkehrcode an das Betriebssystem; er bezieht sich immer auf '
            'genau einen Test:')]
    S += tbl([
        ['Code', 'Bedeutung'],
        ['0', 'keine Vorab-Prüfungs-Fehler; `Prüfungen:`-Abschnitt und/oder Dateiprüfung definiert und Ergebnis `Test wahr`'],
        ['4', 'keine Vorab-Prüfungs-Fehler; weder `Prüfungen:`-Abschnitt noch Dateiprüfung angegeben'],
        ['6', 'Prüfung definiert, aber Ergebnis `Test falsch` (auch: Soll- oder Ist-Datei fehlt, Dateiinhalt verschieden)'],
        ['8', 'sonstige Laufzeitfehler (Stub, Gerät nicht nutzbar, Abbruch mit Strg+C)'],
        ['16', 'Vorab-Prüfung negativ (Formfehler, ungültige Tastenfolge, ungültiger `Prüfungen:`-Abschnitt, fehlender '
               'Geräte-Pfad, Testdatei nicht gefunden) oder Trommeldatei fehlerhaft, nicht vorhanden bzw. nicht '
               'beschreibbar (3.5)'],
        ['2', 'ungültiger Aufruf (unbekannter Schalter, fehlende Regelwerk-Dateien); der Interpreter startet keinen Test'],
    ], wd(1.0, 9.0))
    S += [P('Im Beispiel liefern `pruef-wahr` den Code %d und `pruef-falsch` den Code %d; ein Test ohne `Prüfungen:` '
            '(etwa `spur`, Kapitel 7) endet mit 4.' % (rw, rf))]
    S += h2('5.3 Typische Sollwerte')
    S += tbl([
        ['Wenn der Test …', 'prüfen Sie'],
        ['mit einem Stopp-Befehl endet', '`US=1`, `BZ=` (um 1 hinter dem Stopp-Befehl), `AC=` mit dem erwarteten Ergebnis'],
        ['Zahlen in den Speicher schreibt', 'die Zielzellen als Speicherprüfzeilen (Zellen, die der Test selbst belegt, '
                                            'oder Lauf auf leerer Trommel, 3.5); Vorsicht bei Gruppenbefehlen: sie '
                                            'überschreiben bis zu 32 Zellen einer Spur'],
        ['einen Überlauf erwartet', '`FUE=1`'],
        ['eine Eingabe liest', '`E=0`, `FE=0` und den AC; mit leerem Leser: `E=1`'],
        ['Vergleichersprünge benutzt', '`V1=`, `V2=` (V3 = beide 1)'],
        ['auf Stanzer oder Schreibwerk ausgibt', 'die Dateiprüfung nach 5.4'],
    ], wd(3.6, 6.4))
    S += h2('5.4 Dateiprüfungen für Stanzer und Schreibwerk')
    S += [P('Programme, die auf Kanal K1 (Lochstreifenstanzer) oder K2 (Schreibwerk) ausgeben, erzeugen eine '
            'Ausgabedatei (`stanzer-ausgabe.txt` bzw. `sw-ausgabe.txt`). Zwei weitere, ebenfalls optionale Prüfungen '
            'vergleichen diese Dateien mit je einer Soll-Datei. Sie stehen als Zeile im Abschnitt `Prüfungen:` der '
            'Testdatei (je Zeile eine Prüfung, jede höchstens einmal); der Python-Interpreter nimmt sie zusätzlich als '
            'Schalter der Kommandozeile entgegen, und ein Schalter hat Vorrang vor der Zeile der Testdatei. Beim '
            'Claude-Interpreter gilt die entsprechende virtuelle Zuordnung bei der Testdefinition.')]
    S += tbl([
        ['Zeile / Schalter', 'Soll-Datei wird verglichen mit'],
        ['`--pruefe-stanzer1 DATEI`', 'der Datei, die der Lauf über `--stanzer1 PFAD` (Schalter oder Zeile der '
                                      'Testdatei, 3.4) erzeugt hat (bei einem Verzeichnis: `stanzer-ausgabe.txt` darin)'],
        ['`--pruefe-sw-ausgabe DATEI`', 'der Datei, die der Lauf über `--sw-ausgabe PFAD` (Schalter oder Zeile der '
                                        'Testdatei, 3.4) erzeugt hat (bei einem Verzeichnis: `sw-ausgabe.txt` darin)'],
    ], wd(3.0, 7.0))
    S += [P('Beide Prüfungen können einzeln oder gemeinsam angegeben werden, auch zusammen mit Register-, Flag- und '
            'Speicherprüfungen.')]
    S += bullets([
        '**Soll-Datei:** die hinter dem Schalter genannte DATEI. Ein reiner Dateiname ohne Verzeichnis liegt im '
        'Verzeichnis der Testdatei (üblicherweise `Tests/`); eine Angabe mit Verzeichnis gilt, wie sie geschrieben ist.',
        '**Ist-Datei:** die vom Lauf erzeugte Ausgabedatei. Maßgeblich ist nur eine Datei, die dieser Lauf angelegt hat; '
        'eine übrig gebliebene Datei aus einem früheren Lauf gilt als nicht vorhanden, wenn der Lauf selbst keine '
        'Ausgabe auf dem Gerät vorgenommen hat.',
        '**Prüfung falsch:** Soll-Datei fehlt, Ist-Datei fehlt (auch beide) oder der Inhalt unterscheidet sich. '
        'Verglichen wird zeilenweise wie bei `diff`; Unterschiede nur im Zeilenende (CR LF gegen LF) oder ein fehlendes '
        'Zeilenende nach der letzten Zeile zählen nicht, Leerzeichen am Zeilenende dagegen schon. **Prüfung wahr:** '
        'beide Dateien vorhanden und zeilenweise gleich.',
        '**Gesamtergebnis:** `Test wahr` nur, wenn jede Einzelprüfung nach 5.1 und jede Dateiprüfung wahr ist. Wie bei '
        '5.2 entfallen die Dateiprüfungen, wenn der Test nicht ordnungsgemäß endet.',
        '**Ausgabe:** je Dateiprüfung eine Zeile mit Soll- und Ist-Pfad und `OK` bzw. `FEHLER` samt Grund (Soll-Datei '
        'fehlt, Ist-Datei fehlt, vom Lauf nicht angelegt, Inhalt verschieden); bei verschiedenem Inhalt folgt der '
        '`diff` (Soll gegen Ist, höchstens 100 Zeilen).',
        '**Formale Prüfung:** `--pruefe-stanzer1` ist nur zusammen mit `--stanzer1`, `--pruefe-sw-ausgabe` nur zusammen '
        'mit `--sw-ausgabe` zulässig (Schalter oder Zeile der Testdatei), weil sonst keine Ist-Datei existieren kann. '
        'Als Schalter der Kommandozeile sind beide nur bei einer Testdatei je Aufruf zulässig. Eine fehlende '
        'Soll-Datei ist kein Formfehler, sondern das Prüfergebnis falsch.'])
    os.makedirs(os.path.join(ex.tmp, 'Stanzer1'), exist_ok=True)
    rs, os_ = ex.lauf('Tests/bsp_seite_42_025_stanzer.test', ['--stanzer1', 'Stanzer1'])
    zs = zeilen(os_)
    st_ausg = open(os.path.join(ex.tmp, 'Stanzer1', 'stanzer-ausgabe.txt'), encoding='utf-8').read().rstrip('\n')
    S += [P('Beispiel (echter Lauf, `Tests/bsp_seite_42_025_stanzer.test`): Das Programm wählt K1 an (4600 030) und '
            'stanzt drei Zeichen; die Soll-Datei `Tests/bsp_seite_42_025_stanzer-stanzer-ausgabe.txt` enthält die Zeilen '
            '`00110001`, `00110010` und `00100011`. Ende der Testdatei:')]
    S += code('Prüfungen:\nBZ=2014 AC=00002012000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0\n2012: 00000001164\n'
              '...\n2022: 00000000777\n--pruefe-stanzer1 bsp_seite_42_025_stanzer-stanzer-ausgabe.txt')
    S += code('$ python3 c8205_interp.py --stanzer1 Stanzer1 Tests/bsp_seite_42_025_stanzer.test\n' +
              kurz(os_, zs[:4], ['… (Speicherzeilen 2012 bis 2027) …'], [zs[ab(zs, 'Ende:')]],
                   [zs[ab(zs, 'Ergebnispruefung')], zs[ab(zs, 'BZ:')], '… (übrige Zeilen alle OK)',
                    zs[ab(zs, 'Stanzer 1:')], 'Test wahr']) + '\n\n$ cat Stanzer1/stanzer-ausgabe.txt\n' + st_ausg)
    S += [P('Rückkehrcode %d bei `Test wahr`, 6 bei `Test falsch`.' % rs)]


# ------------------------------------------------------------------------------------------ Kapitel 6
def kap6(S, ex):
    S += h1('6 Formale Gültigkeitsprüfung vor dem Start')
    S += [P('Vor jedem Test werden Trommeldatei, Tastenfolge, Prüfungen und Testmarken formal geprüft. Der Test startet '
            'nur, wenn die Prüfung insgesamt positiv verläuft. Bei einer Unstimmigkeit darf er nicht eigenmächtig '
            'korrigiert und gestartet werden; die Durchführung wartet auf eine Klärung mit dem Auftraggeber.')]
    S += tbl([
        ['Bereich', 'Geprüft wird'],
        ['Trommeldatei (Abschnitt der Testdatei)',
         'Zeilenformat (Adresse 4, Wert 11 Oktalstellen, nur Oktalzahlen, zulässige Kommentar- und Leerzeilen); keine '
         'Adresse mit widersprüchlichem Wert mehrfach belegt'],
        ['Persistente Trommel (Python-Interpreter)',
         'Die Datei `trommel.txt` muss vorhanden und beschreibbar sein und genau 4096 Zeilen `aaaa: ttttttttttt` mit '
         'lückenlos aufsteigenden Adressen `0000` bis `7777` enthalten. Die Prüfung gilt für den ganzen Aufruf und läuft '
         'einmal vor dem ersten Test; schlägt sie fehl, startet kein Test (3.5)'],
        ['`#SPEI-xxxx`', 'nach Regelwerk: nur zu einem im selben Test definierten `#DOK-xxxx` gleicher Nummer; ssss-eeee '
                         'bildet eine gültige Spanne'],
        ['`#PROT STUFE=n`', 'n ist 0, 1 oder 2; höchstens einmal; Fehlen ist gültig (Standard: 1)'],
        ['Tastenfolge', 'ergibt einen vollständig definierten Ausgangszustand. Ungültig: M- ohne vorheriges M+, zweites '
                        'M+ bei gedrücktem M, R oder Ende bei gedrücktem M, unbekannte Tasten, Ende weder mit R noch im '
                        'Halt. Gültig, aber ohne Wirkung: Ü und E bei nicht gesetztem H.'],
        ['Geräte-Zeilen', '`--leser1`, `--leser2`, `--stanzer1`, `--sw-ausgabe`, `--k0`: Zeile mit Wert; jede höchstens '
                          'einmal; `--k0` in der Form `datei=PFAD`; die Pfade von `--k0`, `--leser1` und `--leser2` '
                          'müssen vorhanden sein (3.4)'],
        ['Prüfungen:', 'unbekannte Schlüssel, falsche Stellenzahl oder unzulässiger Wert, mehrfach genannter Schlüssel, '
                       'Zeile außerhalb des Adresse:Wert-Formats, widersprüchlich mehrfach belegte Prüfadresse'],
        ['Dateiprüfungen', '`--pruefe-stanzer1` setzt `--stanzer1`, `--pruefe-sw-ausgabe` setzt `--sw-ausgabe` voraus; '
                           'höchstens eine Zeile je Prüfung; als Schalter nur bei einer Testdatei je Aufruf (5.4)'],
    ], wd(2.7, 7.3), first_bold=True)
    rc, out = ex.lauf('Handbuch-Tests/formfehler.txt')
    S += [P('Beispiel 1: Eine Testdatei mit drei Fehlern in der Trommeldatei (`Handbuch-Tests/formfehler.txt`). Der '
            'Interpreter nennt alle Zeilenfehler auf einmal, startet nicht und liefert den Rückkehrcode %d:' % rc)]
    S += code(ex.hbtext('formfehler.txt') + '\n\n$ python3 c8205_interp.py Handbuch-Tests/formfehler.txt\n' + out +
              '\nRückkehrcode: %d' % rc)
    S += [P('Die Tastenfolge dieser Datei ist ebenfalls ungültig (`M-loslassen` ohne vorheriges '
            '`M-gedrückt-halten`). Sie wird erst bewertet, wenn die Trommeldatei formal in Ordnung ist; nach Korrektur '
            'der Zeilen meldet der Interpreter sie als nächstes:')]
    rc, out = ex.lauf('Handbuch-Tests/tastenfehler.txt')
    S += code(ex.hbtext('tastenfehler.txt') + '\n\n$ python3 c8205_interp.py Handbuch-Tests/tastenfehler.txt\n' + out +
              '\nRückkehrcode: %d' % rc)
    rc, out = ex.lauf('Tests/gibtsnicht.txt')
    out = re.sub(r'\(aktuelles Verzeichnis: [^)]*\)', '(aktuelles Verzeichnis: …/c8205)', out)
    S += [P('Auch ein Aufruf mit nicht vorhandener Testdatei meldet das laut und startet nichts (Rückkehrcode %d):' % rc)]
    S += code('$ python3 c8205_interp.py Tests/gibtsnicht.txt\n' + out)
    # Trommeldatei fehlerhaft (echter Lauf mit einer beschädigten Kopie)
    tz = open(ex.trommel, encoding='utf-8').read().split('\n')
    tz[2] = '0002 00000000000'
    kaputt = os.path.join(ex.tmp, 'trommel_kaputt.txt')
    open(kaputt, 'w', newline='', encoding='utf-8').write('\n'.join(tz))
    rc, out = ex.lauf('Handbuch-Tests/vorlage.txt', trommel=kaputt)
    S += [P('Beispiel 2: Die Trommeldatei selbst ist fehlerhaft (hier in einer Kopie `trommel_kaputt.txt`: in Zeile 3 '
            'fehlt der Doppelpunkt). Der Interpreter prüft sie einmal je Aufruf, nennt die Fehler (höchstens 50) und '
            'führt keinen Test aus (Rückkehrcode %d). Abhilfe: leere Trommel mit `erzeuge_leere_trommel.py` neu '
            'erzeugen (3.5).' % rc)]
    S += code('$ python3 c8205_interp.py --trommel trommel_kaputt.txt Handbuch-Tests/vorlage.txt\n' + out +
              '\nRückkehrcode: %d' % rc)
    S += note('achtung', 'Abweichung Regelwerk ↔ Interpreter (Fassung 07.10.2026): Das Regelwerk (Durchführung eines '
              'Tests, Abschnitt 5) lässt `#SPEI` nur zu einem `#DOK` gleicher Nummer zu. Der Python-Interpreter prüft das '
              'nicht; er gibt die Zellen auch ohne `#DOK` aus (Interpreter-Dokument: `#SPEI` und `#SPUR` brauchen kein '
              '`#DOK`). Ob das Regelwerk oder der Interpreter anzupassen ist, ist nicht entschieden.')
    rc, out = ex.lauf('Handbuch-Tests/spei-ohne-dok.txt')
    S += [P('Echter Lauf zu dieser Abweichung (`Handbuch-Tests/spei-ohne-dok.txt`: Befehl 164 mit Adresse 0007, '
            '`#SPEI-0007`, aber kein `#DOK-0007`; Rückkehrcode %d, weil kein `Prüfungen:`-Abschnitt vorhanden ist):' % rc)]
    S += code(ex.hbtext('spei-ohne-dok.txt') + '\n\n$ python3 c8205_interp.py Handbuch-Tests/spei-ohne-dok.txt\n' + out)
    S += note('hinweis', 'Grundsatz „laut scheitern“ (gilt ebenso später bei der Abarbeitung des Knotengraphen): Ergibt '
              'sich eine Unklarheit, ein Widerspruch oder eine fehlende Festlegung, wird das laut gemeldet und der Test '
              'angehalten, statt eigenmächtig eine Annahme zu treffen. Das gilt unabhängig davon, ob '
              'Python-Interpreter oder KI den Test ausführen.')


# ------------------------------------------------------------------------------------------ Kapitel 7
def kap7(S, ex):
    S += h1('7 Diagnose beim Leerbefehl 164')
    S += [P('Die Diagnoseausgabe gibt während des Laufs Zwischenstände aus. Sie ist, wie die Marken `#DOK` und `#SPEI`, '
            'eine von der Hardware abweichende Zusatzdefinition ohne Entsprechung in der Elektronik.')]
    S += h2('7.1 Auslösebedingung')
    S += [P('Tritt in der Befehlsfolge der Befehl 164 (oktal; Leerbefehl, B = 1, A = 6, Z = 4) mit einer Adresse a auf '
            'und ist für xxxx = a eine Testmarke `#DOK-xxxx` definiert, wird zusätzlich zur regulären Abarbeitung die '
            'Diagnose ausgegeben. Der Python-Interpreter wählt zur Adresse a die zugehörigen `#DOK`-Texte, '
            '`#SPEI`-Bereiche und `#SPUR`-Spuren unabhängig voneinander aus (Abweichung in Kapitel 6); passt keine '
            'Marke, entfällt die Diagnose ganz.')]
    S += h2('7.2 Ablauf')
    S += numbered([
        'Der Befehl 164 wird zuerst genau so interpretiert, wie es der Knotenautomat vorgibt; die Ausführung selbst '
        'erfährt keine Sonderbehandlung.',
        'Danach wird ausgegeben: die Testmarke `#DOK-xxxx` mit ihrem Text.',
        'Ist zu xxxx ein `#SPEI-xxxx ssss-eeee` definiert: die Markenzeile selbst und alle Zellen ssss bis eeee '
        'zeilenweise `Adresse: Wert`.',
        'Ist ein `#SPUR-xxxx aaaa` definiert: danach, nach allen `#SPEI`-Ausgaben, die Markenzeile und alle 32 Zellen '
        'der Spur in physischer Zugriffsreihenfolge der Trommel, Format wie bei `#SPEI`.',
        'Danach wird die Interpretation regulär fortgesetzt.'])
    S += [P('Die Diagnose erscheint stufenunabhängig immer auf dem Bildschirm; bei Stufe 2 zusätzlich in der '
            'Protokolldatei. Nach dem Regelwerk gehören zur Textzeile auch BZ, AC und die Flags FE, FÜ, BS, US, E, A; '
            'der Python-Interpreter gibt diese Zeile nicht aus (Änderung 29.09.2026: es stehen Marke, Text und '
            'Speicherzeilen da).')]
    rc, out = ex.lauf('Handbuch-Tests/spur.txt')
    zl = zeilen(out)
    i0 = ab(zl, '#SPUR-0020')
    S += [P('Beispiel mit `#SPUR`: Der Test (`Handbuch-Tests/spur.txt`) hält bei Befehl 164 (Adresse 0020) und gibt die '
            'Spur der Zelle 4001 aus. Die Zellen erscheinen in der Reihenfolge der Trommel, nicht aufsteigend (vgl. '
            'Tabelle in der Rechnerbeschreibung, Kapitel 6.1):')]
    S += code(ex.hbtext('spur.txt') + '\n\n$ python3 c8205_interp.py Handbuch-Tests/spur.txt\n' +
              '\n'.join(zl[:i0 + 8] + ['… (25 weitere Zellen, alle 0, in Trommelreihenfolge) …', zl[ab(zl, 'Ende:')]]))
    S += [P('Zelle für Zelle: 4000, 4015, 4032, 4007, 4024, 4001, … – das ist die Spalte „logische Sektoradresse“ der '
            'physischen Reihenfolge (Interleaving, Schritt +05 oktal).')]
    S += note('hinweis', 'Die Leerbefehle 164 und 166 werden ohne Resultatbehandlung ausgeführt (das Z-Feld bewirkt '
              'keine Verschiebung des AC). Es ist daher unschädlich, die Marke an eine beliebige Programmstelle zu '
              'setzen, und sie eignet sich zum Messpunkt zwischen zwei Schritten.')


# ------------------------------------------------------------------------------------------ Kapitel 8
def kap8(S, ex):
    S += h1('8 Protokoll und Protokolltiefe')
    S += tbl([
        ['`#PROT STUFE=`', 'Knotenprotokoll', 'Protokolldatei', 'Diagnose (164) und Prüfung'],
        ['0', 'keines', 'keine', 'immer auf dem Bildschirm'],
        ['1 (Standard)', 'auf dem Bildschirm, knapp: eine Zeile je durchlaufenem Knoten', 'keine',
         'immer auf dem Bildschirm'],
        ['2', 'in der Protokolldatei', 'ja (für den ganzen Test, auch ohne Ausgabebefehle)', 'Bildschirm und Datei'],
    ], wd(1.7, 3.4, 3.0, 2.3), first_bold=True)
    S += [P('Die Stufen sind nützlich vor allem bei Programmen mit vielen Durchläufen (z. B. Schleifen über Gruppen- '
            'oder Wiederholungsbefehle), bei denen ein Protokoll jedes einzelnen Knotens unübersichtlich lang würde. Der '
            'Python-Interpreter nimmt die Knotenzeilen nur auf, wenn er mit `--knotentest` aufgerufen wird '
            '(Bedienungsanleitung, Abschnitt 6.4).')]
    S += h2('8.1 Inhalt der Protokolldatei (Stufe 2)')
    S += numbered([
        '**Ausgangsbedingungen:** die vom Test übernommenen Trommelzeilen (nicht der ganze Trommelinhalt, 3.5) und die '
        'Tastenfolge mit ihrer Wirkung auf Register und Flags.',
        '**Zustände des Knotenautomaten:** die ab Konnektor B (oder dem Startpunkt nach 4.4) erreichten Knoten in der '
        'durchlaufenen Reihenfolge, mit BZ, AR und AC.',
        '**Debug-Ausgaben** nach Kapitel 7 (`#DOK`, `#SPEI`, `#SPUR`).',
        '**Ende:** Endgrund und Endzeile; danach, falls ein `Prüfungen:`-Abschnitt vorhanden ist, die Ergebnisprüfung mit '
        'Soll und Ist je Wert (einschließlich der Dateiprüfungen nach 5.4) und dem Gesamtergebnis.'])
    rc, out = ex.lauf('Handbuch-Tests/bspA.txt', ['--knotentest', '--NO-TERMOUT', '--out',
                                                  os.path.join(ex.tmp, 'bspA.log')])
    pl = [l.rstrip() for l in ex.protokoll('', os.path.join(ex.tmp, 'bspA.log'))]
    iT = ab(pl, 'Tastenfolge:')
    i2 = ab(pl, '== 2.')
    iK17 = ab(pl, 'K017 ')
    iK45 = ab(pl, 'K045 ')
    auszug = pl[:iT + 1] + ['… (Wirkung je Taste wie in 4.1)'] + pl[i2:iK17 + 1] + ['…'] + pl[iK45:]
    while auszug and not auszug[-1].strip():
        auszug.pop()
    S += [P('Zum Lesen ein echter Protokollauszug (Beispiel A aus Abschnitt 4.1: Laden, Addieren, Stopp; '
            '`Handbuch-Tests/bspA.txt`, die Marke `#PROT STUFE=2` und `--knotentest` waren gesetzt):')]
    S += code('$ python3 c8205_interp.py --knotentest --NO-TERMOUT --out bspA.log Handbuch-Tests/bspA.txt\n' +
              '\n'.join(auszug))
    S += note('achtung', 'Die Überschrift „Trommeldatei (uebernommen, Ausschnitt; nicht genannte Zellen = 0)“ im '
              'Protokoll stammt noch aus der Zeit vor der persistenten Trommel und trifft seit 07.10.2026 nicht mehr '
              'zu: Nicht genannte Zellen behalten ihren bisherigen Inhalt (3.5). Die Zeilen darunter sind nur die vom '
              'Test geschriebenen Zellen, nicht der ganze Trommelinhalt. Ob der Interpreter oder das Regelwerk '
              'angepasst wird, ist nicht entschieden.')
    S += h2('8.2 Eine Knotenzeile lesen')
    S += tbl([
        ['Zeile', 'Lesart'],
        ['`K001 KON B BZ=0000 AR=0000 AC=…`', 'Knoten 1 (Konnektor B): Eintritt in den Ablauf. Danach BZ, AR, AC oktal.'],
        ['`BR=0000 000 (vor Knoten 002) …`', 'Befehlsregister (Adressteil und Operationsteil) vor Beginn von Phase I; dazu '
                                             'BZ, AC, FÜ, V1, V2, V3. Die Zeile steht auch vor Knoten 7 (Sprung über '
                                             'Konnektor 1 aus Knoten 63), wie im Auszug aus 4.4: `BR=0000 005 (vor '
                                             'Knoten 007)`.'],
        ['`K002 PHA Phase I …`', 'Phasenzuordnung: Beginn der Phase I (analog Phase II: Knoten 8, III: 15, IV: 31/61/67)'],
        ['`K003 ANW 001 BZ=0001 AR=0000 …`', 'Knoten 3 ist eine Anweisung, ANWEISUNG-001: AR := BZ und gleichzeitig '
                                             'BZ := AR + 1 mit den alten Werten. BZ=0001 ist deshalb richtig (nicht '
                                             '0000+1 mit neuem AR).'],
        ['`K004 TST 002 … -> falsch`', 'Knoten 4, ein Test (ANWEISUNG-002, „X-Abbruch-Merker gesetzt?“): Ergebnis falsch '
                                       '→ weiter über den falsch-Ausgang'],
        ['`K016 ANW 001 …`', 'derselbe Anweisungs-Typ in Phase III (Knoten 16): AR wird auf die Operandenadresse '
                             'gestellt; BZ := alter AR + 1 = BADR + 1'],
        ['`K045 ANW 030 …`', 'ANWEISUNG-030, unbedingter Stopp: Endknoten, US := 1'],
        ['`K054 KON 4 …`', 'Konnektor 4 (Knoten 54): Einstieg nach M mit Sprung mit Rückkehrabsicht; Phase III gilt als '
                           'abgelaufen (4.4)'],
    ], wd(3.2, 6.8))
    S += note('hinweis', 'Die „Knoten“-Zahl der Endzeile und die Zahl der Knotenzeilen sind fassungsabhängig und keine '
              'Zeitangabe (alle Zeiten sind 0). Sie eignen sich nicht als Sollwert eines Tests.')


# ------------------------------------------------------------------------------------------ Kapitel 9
def kap9(S, ex):
    S += h1('9 Ein- und Ausgabe in Tests')
    S += [P('Programme können Zeichen ein- und ausgeben. Im Test werden die Geräte nur mit den Kanal- und '
            'Adresszuordnungen des Originals nachgebildet, ohne mechanische Bauteile. Jede virtuelle Datei wird nur '
            'angelegt, wenn der Test das Gerät benutzt.')]
    S += tbl([
        ['Kanal', 'Eingabe (Regelwerk)', 'Ausgabe (Regelwerk)'],
        ['K0 mit T oder SW', 'über die Host-Tastatur: pro Eingabebefehl genau ein Zeichen wird angefordert (nicht eine '
                             'Zeile); es wird nach der Kodetabelle in die Eingabeverschlüsselung umgesetzt und mit dem '
                             'Adressregister ODER-verknüpft; danach wird der Eingabebefehl umgestellt', '—'],
        ['K1', 'Leser 1: virtueller Lochstreifen (Textdatei), pro Eingabebefehl eine Zeile aus acht Zeichen 0/1 (Spuren '
               'w v u p 8 4 2 1; Tr wird nicht dargestellt)',
         'Stanzer 1: Datei, ein ausgegebenes Zeichen je Zeile, acht 0/1 in derselben Spurreihenfolge'],
        ['K2', 'Leser 2: wie Leser 1, aber getrennte Lochstreifendatei',
         'Schreibwerk: zeichenweise Textausgabe; WRZL beendet die Zeile (mehrere WRZL = Leerzeilen)'],
    ], wd(1.5, 5.0, 3.5), first_bold=True)
    S += [P('**Kanalanwahl.** Die Kanäle K0 bis K3 werden entweder durch die rastenden Pult-Tasten K0–K3 (Teil der '
            'Tastenfolge; die Taste setzt das Flag des gewählten Kanals auf 1 und die der anderen drei auf 0, bei K0 '
            'zusätzlich T oder SW je nach Schalter SW) oder durch einen Anwahlbefehl im Programm gewählt: `4700 030` = '
            'K0, `4600 030` = K1, `4500 030` = K2, `4400 030` = K3. Ein zur Laufzeit ausgeführter Anwahlbefehl '
            '**übersteuert** die zuvor per Taste eingestellte Kanalstellung. Kanal K3 bewirkt in dieser Ausbaustufe '
            'nichts (kein Gerät zugeordnet).')]
    S += [P('**K0 aus Datei.** Ist für K0 eine Eingabedatei oder ein Eingabeverzeichnis zugeordnet (`--k0 datei=PFAD`), '
            'kommen die Eingaben beider Subkanäle (T und SW) aus dieser Quelle statt vom Terminal; mehrere Dateien in '
            'einem Verzeichnis werden in alphanumerischer Reihenfolge verarbeitet. Ist der Pfad vorhanden, aber keine Datei '
            '(mehr) da, wartet der Interpreter still, bis eine neue Datei erscheint.')]
    S += h2('9.1 Lochstreifendateien')
    S += bullets([
        'Für Leser 1 und Leser 2 werden stets getrennte Dateien benutzt. Jeder Leser muss durch `--leser1` bzw. '
        '`--leser2` (Schalter oder Zeile der Testdatei, 3.4) definiert werden; fehlt die Zuordnung, ist auf dem Kanal '
        'keine Eingabe möglich.',
        'Ist die aktuelle Datei zu Ende und tritt für denselben Leser ein weiterer Eingabebefehl auf, wird eine neue '
        'Lochstreifendatei angefordert; der Python-Interpreter wartet dann still (ohne Meldung), bis eine neue Datei '
        'erscheint.',
        'Wird eine Datei nicht vollständig verbraucht, bleibt sie für den Leser geladen und wird bei einem späteren '
        'Eingabebefehl an der zuletzt entnommenen Stelle fortgesetzt.',
        'Geht der Rechner in den Halt (Stopp, Fehler-Halt oder sonst), werden alle angebrochenen Dateien beider Leser '
        'beendet und entfernt; ein neuer Test fordert seine Dateien neu an.',
        'Eine Zeile mit gerader Zahl von Einsen ist ein Fehler bei Eingabe (FE := 1, der Lauf hält). Leerzeilen sind '
        'Vorspann und werden übergangen. Das Lochbild `11111111` („Irrung Zeichen“) wird übersprungen: keine '
        'Paritätsprüfung, kein FE, nicht ins AR; der Eingabebefehl liest das nächste Zeichen (Interpreter-Dokument 8.2, '
        'Ergänzung 04.10.2026).'])
    lb = open(os.path.join(ex.tmp, 'Tests', 'lb-001_Irrung_Zeichen_uebersprungen.txt'), encoding='utf-8').read()
    lbz = [l for l in lb.split('\n') if l.strip()][:8]
    streifen = open(os.path.join(ex.tmp, 'virtuelle_Geraete', 'Leser1', 'lb-001_irrung_zeichen_dann_1.txt'),
                    encoding='utf-8').read().strip()
    rc, out = ex.lauf('Tests/lb-001_Irrung_Zeichen_uebersprungen.txt')
    zl = zeilen(out)
    S += [P('Echtes Beispiel `Tests/lb-001_Irrung_Zeichen_uebersprungen.txt`: Das Programm wählt K1 an und liest ein '
            'Zeichen. Der Streifen (`--leser1`-Zeile der Testdatei) enthält erst die Irrung `11111111`, dann die Ziffer 1 '
            '(`00000001`). Die Irrung wird übersprungen; der AC erhält den Inhalt der Zelle 0001 (Eingabeadresse 01 mit '
            'Adreßteil 0000 verknüpft):')]
    S += code('\n'.join(lbz) + '\n…\n\n$ cat virtuelle_Geraete/Leser1/lb-001_irrung_zeichen_dann_1.txt\n' + streifen +
              '\n\n$ python3 c8205_interp.py Tests/lb-001_Irrung_Zeichen_uebersprungen.txt\n' +
              kurz(out, zl[:1], [zl[ab(zl, 'Ende:')]], ['Test wahr']))
    S += [P('Rückkehrcode %d. BZ=2003, AC=00000000001, kein Fehler bei Eingabe (FE=0).' % rc)]
    S += h2('9.2 Schreibwerk')
    S += [P('Das Regelwerk beschreibt eine Ausgabe in die Datei `sw-ausgabe.txt` (höchstens einmal je Test angelegt, nur '
            'bei tatsächlicher Ausgabe, später angehängt statt überschrieben, am Testende zum Download bereitgestellt). '
            'Ist dem Test die Datei zugeordnet (Schalter `--sw-ausgabe PFAD` oder gleichnamige Zeile in der Testdatei, '
            '3.4), geht jede Ausgabe auf K2 dorthin; fehlt die Zuordnung, erscheint sie auf dem Terminal (Dunkelgelb). '
            'Beides zugleich gibt es nie. Die Ausgabe ist vom Schalter SW unabhängig; ein Warten auf SW findet nicht '
            'statt.')]
    S += note('hinweis', 'Die Schreibwerk-Ausgabe über K2 ist unabhängig vom Schalter SW (Hardwarebeschreibung und '
              'Regelwerk 6.3.1); der Schalter SW betrifft nur die Eingabeseite (K0). Für den Stanzer gibt es dagegen '
              'keinen Terminal-Ausweg: ohne `--stanzer1` unterbleibt die Ausgabe auf K1 ganz.')
    S += h2('9.3 Gegenüberstellung der Ausführenden')
    S += tbl([
        ['', 'Python-Interpreter', 'Claude-Interpreter'],
        ['K0-Eingabe', 'Terminal (ein Tastendruck je Eingabebefehl) oder `--k0 datei=PFAD` (Schalter oder Zeile der '
                       'Testdatei)', 'die KI fordert pro Eingabebefehl ein Zeichen auf dem Host-Bildschirm an und nimmt '
                                     'es entgegen'],
        ['Leser 1/2', '`--leser1`, `--leser2` (Datei oder Ordner; Schalter oder Zeile der Testdatei)',
         'die KI fordert die Lochstreifendatei für den jeweiligen Leser an'],
        ['Stanzer 1', '`--stanzer1 PFAD` (Schalter oder Zeile der Testdatei)',
         'Datei `stanzer-ausgabe.txt`, am Testende zum Download'],
        ['Schreibwerk', '`--sw-ausgabe PFAD` (Schalter oder Zeile der Testdatei) → Datei `sw-ausgabe.txt`; sonst '
                        'Terminal, Dunkelgelb', 'Datei `sw-ausgabe.txt`, am Testende zum Download'],
        ['Trommel', 'persistente Datei `trommel.txt` (3.5)', 'keine Datei; nicht genannte Zellen gelten als 0'],
        ['Protokoll', '`--out …`, bei Stufe 2 Datei', 'Datei `protokoll.txt`, am Testende zum Download'],
    ], wd(1.6, 4.4, 4.0), first_bold=True)


# ------------------------------------------------------------------------------------------ Kapitel 10
def kap10(S):
    S += h1('10 Den Claude-Interpreter einsetzen')
    S += h2('10.1 Was die KI braucht')
    S += tbl([
        ['Material', 'Zweck'],
        ['Knotengraph (`Eingänge_der_Knoten.md`) und Variablentabelle T2 (`Beschreibung_der_Knoten.md`)',
         'der Ablauf selbst und die Bedeutung jeder ANWEISUNG'],
        ['Befehlsliste (`Befehlsliste.md`)', 'die Formel je Operationscode (ANWEISUNG-021 verweist dorthin)'],
        ['`Datenstruktur_und_Verarbeitungseinheiten.md`, `Bedienpult_mit_Schaltern.md`',
         'Register, Felder, Flags; Tasten und Schalter'],
        ['Diese Testdefinition (`Durchführung_eines_Tests.md`) und die Testdatei', 'Format, Tastenfolge, Marken, '
                                                                                    'Protokoll, Trommel (2c)'],
        ['`Magnettrommel.md` (bei `#SPUR`/`#SPEI`)', 'Sektorreihenfolge der Spur'],
        ['`Kodetabellen.md`, `Lochstreifenleser.md` (bei Ein- und Ausgabe)', 'Zeichenkode; Kanäle, Leser, Stanzer, '
                                                                              'Schreibwerk'],
        ['`Überblick_und_Gesamtaufbau.md` (optional)', 'Geräteaufbau und die vier Phasen, hilfreich bei Rückfragen'],
        ['`baz-wirkungstabelle.md` (optional)',
         'Cache bereits hergeleiteter Knotenpfade und Formeln je BAZ-Wert; der Python-Interpreter liest ihn nicht. Nur '
         'verwenden, wenn die Einträge zu den aktuellen Fassungen von Knotengraph, T2 und Befehlsliste passen, sonst neu '
         'herleiten'],
    ], wd(4.6, 5.4))
    S += [P('Faustregel: Wer sich die Auswahl sparen will, lädt alle `.md`-Dateien hoch, außer `Python_Interpreter`, `PDF`, '
            '`Projektstruktur`, `Projektueberblick` und der Assembler-Dokumentation. Das kostet Kontext, den lange '
            'Protokolle brauchen. Dazu kommen die Testdatei und gegebenenfalls Dateien für Leser und K0. Eine '
            'Trommeldatei gehört nicht dazu (3.5).')]
    S += h2('10.2 Vorgehen')
    S += [P('Eine Test-Anforderungs-Datei (die Testdatei) anlegen: Aufbau nach Kapitel 2 bis 5, Vorlage in 12.2. Sie wird '
            'mit den Dateien aus 10.1 der KI übergeben. Start und Startanweisung: Kurzanleitung, Weg A. Für den '
            'Vergleich mit dem Python-Interpreter (1.1) wird dessen Lauf auf einer frisch erzeugten, leeren Trommel '
            'gestartet, weil die KI nicht genannte Zellen als 0 annimmt.')]


# ------------------------------------------------------------------------------------------ Kapitel 11
FAMILIEN = [('NNNN', 'NNNN-… (0001 bis 0024)',
             'Befehlstests; der Dateiname nennt die Operationscodes (Laden, Addieren, Transport, Sprünge, Überlauf, '
             'Speichern)'),
            ('asm_', 'asm_NNNN_…', 'Testaufträge aus Assemblerläufen (3.3), u. a. Vektor umspeichern, bedingte Sprünge, '
                                   'Sortierung'),
            ('bsp_', 'bsp_…', 'Beispielprogramme (Abschnittsnummer im Namen, z. B. bsp_6_1_4_division), darunter Tests mit '
                              'Leser, Stanzer und Schreibwerk; einzelne als .test-Datei direkt aus dem Assembler'),
            ('betrag', 'betrag.test', 'Betragsbildung (z = -|a+b| + |-b+c| + |-c+d|, erwartet z = 1)'),
            ('lb-', 'lb-…', 'Lochband: Irrung Zeichen übersprungen (lb-001), ohne Irrung (lb-002), Paritätsfehler (lb-003)'),
            ('pj2-', 'pj2-…', 'Programmbeispiele: ggT nach Euklid, Maximum von drei Zahlen (vier Fälle), Vertauschung '
                              'zweier Zahlenfelder'),
            ('sp-', 'sp-…', 'Sprungbefehle (unbedingt, zyklisch, bedingt, mit Rückkehrabsicht; Schalter SP = 0 und SP = 1)'),
            ('tk-', 'tk-…', 'Tastenfolgen (Tabelle unten): jeder Test belegt eine Festlegung aus 4.3 bis 4.5'),
            ('ziffern', 'ziffern_…', 'Ziffer 0 bis 3 über K0 aus Datei (`--k0`) einlesen und auswerten, Ausgabe auf dem '
                                     'Schreibwerk; vier Eingaben (0 bis 3) und eine Folge nicht auswertbarer Ziffern '
                                     '(`ziffern_uebergehen`)')]


def familie(n):
    if re.match(r'\d{4}[-_]', n):
        return 'NNNN'
    if n == 'betrag.test':
        return 'betrag'
    for p in ('asm_', 'bsp_', 'lb-', 'pj2-', 'sp-', 'tk-', 'ziffern'):
        if n.startswith(p):
            return p
    raise ValueError('Testfamilie unbekannt: ' + n)


def testliste(tests_dir):
    """Alle Tests wie die Schleife `Tests/*.txt Tests/*.test`, ohne Soll-Dateien."""
    fs = sorted(os.listdir(tests_dir))
    txt = [f for f in fs if f.endswith('.txt') and not f.startswith('.')]
    tst = [f for f in fs if f.endswith('.test')]
    soll = lambda f: f.endswith('-sw-ausgabe.txt') or f.endswith('-stanzer-ausgabe.txt')
    return [f for f in txt if not soll(f)], [f for f in tst if not soll(f)]


def gesamtlauf(ex):
    """Alle Tests zweimal: mit leerer Trommel vor jedem Test und ohne Zurücksetzen."""
    txt, tst = testliste(os.path.join(ex.tmp, 'Tests'))
    res = {}
    for modus in ('reset', 'dirty'):
        ex.leere_trommel()
        codes = []
        for t in txt + tst:
            if modus == 'reset':
                ex.leere_trommel()
            rc, _ = ex.lauf('Tests/' + t, ['--NO-TERMOUT', '--stanzer1', 'virtuelle_Geraete/Stanzer1/'])
            codes.append((t, rc))
        res[modus] = codes
    ex.leere_trommel()
    return len(txt), len(tst), res


def kap11(S, ex, gl):
    ntxt, ntst, res = gl
    n = ntxt + ntst
    from collections import Counter
    fam = Counter(familie(t) for t, _ in res['reset'])
    cr = Counter(rc for _, rc in res['reset'])
    cd = Counter(rc for _, rc in res['dirty'])
    falsch = [t for t, rc in res['dirty'] if rc != 0]
    S += h1('11 Referenztests und Regression')
    S += h2('11.1 Testbestand und Gesamtlauf')
    S += [P('Für die Regression liegen in `Tests/` zum Stand 08.10.2026 **%d Tests** (Dateien `*.txt` und `*.test`, ohne '
            'die Soll-Dateien `*-sw-ausgabe.txt` und `*-stanzer-ausgabe.txt`; davon %d als `.txt` und %d als `.test`). '
            'Jeder dieser Tests hat einen `Prüfungen:`-Abschnitt. Ein neuer Lauf wird mit den zuletzt bestätigten '
            'Sollwerten verglichen: Endzustand von Register und Flags, erwartete Speicherinhalte, erwartete Ausgaben.'
            % (n, ntxt, ntst))]
    rows = [['Familie', 'Anzahl', 'Inhalt']]
    for key, name, text in FAMILIEN:
        rows.append([name, str(fam[key]), text])
    rows.append(['Summe', str(sum(fam.values())), ''])
    assert sum(fam.values()) == n
    S += [CondPageBreak(230)]
    S += tbl(rows, wd(2.4, 1.0, 6.6), first_bold=True)
    S += note('hinweis', 'Die Beispieltests dieses Handbuchs (`Handbuch-Tests/`) sind nicht mitgezählt. Das Glob-Muster der '
              'Soll-Dateien muss `*-sw-ausgabe.txt` heißen, nicht `*-sw-ausgabe.*`: `bsp_seite_42_025-sw-ausgabe.test` '
              'ist ein Test und keine Soll-Datei.')
    S += [P('Weil die Trommel ihren Inhalt behält (3.5), setzt der Gesamtlauf sie vor jedem Test zurück. Er liefert dann '
            'für alle %d Tests den Rückkehrcode 0:' % n)]
    zaehl = '\n'.join('%7d %d' % (c, rc) for rc, c in sorted(cr.items()))
    if list(cr) == [0]:
        zaehl += '     # %d Tests, alle mit Rückkehrcode 0' % n
    S += code('for t in Tests/*.txt Tests/*.test; do\n'
              '  case $t in *-sw-ausgabe.txt|*-stanzer-ausgabe.txt) continue;; esac\n'
              '  python3 erzeuge_leere_trommel.py                 # leere Trommel für jeden Test\n'
              '  python3 c8205_interp.py --NO-TERMOUT --stanzer1 virtuelle_Geraete/Stanzer1/ "$t" > /dev/null\n'
              '  echo "$? $(basename $t)"\n'
              'done | awk \'{print $1}\' | sort | uniq -c\n' + zaehl)
    if list(cr) == [0]:
        S += [P('Ergebnis dieses Laufs: alle %d Tests mit Rückkehrcode 0 = `Test wahr`.' % n)]
    else:
        S += note('achtung', 'Der Gesamtlauf auf zurückgesetzter Trommel lieferte nicht überall den Rückkehrcode 0: %s'
                  % ', '.join('%d × Code %d' % (c, rc) for rc, c in sorted(cr.items())))
    S += [P('Ohne das Zurücksetzen (die Trommel ist nur zu Beginn leer, die Tests laufen in der Reihenfolge der Schleife) '
            'ergibt derselbe Lauf %s; Test falsch: %s. Das ist die Reihenfolgeabhängigkeit aus 3.5, kein Fehler des '
            'Tests oder des Interpreters.'
            % (', '.join('%d × Code %d' % (c, rc) for rc, c in sorted(cd.items(), key=lambda x: x[0])),
               ', '.join('`%s`' % f for f in falsch) or 'keiner')) ]
    S += note('hinweis', 'Stand 08.10.2026: Der Sammellauf `compute_all_tests.sh` durchläuft nur `Tests/*.txt` (%d von %d '
              'Tests; die %d `.test`-Dateien nicht) und erzeugt die leere Trommel erst nach dem Lauf. Für einen '
              'Gesamtlauf über alle Tests gilt die Schleife oben.' % (ntxt, n, ntst))
    S += h2('11.2 Referenztests zu den Tastenfolgen (tk-001 bis tk-008)')
    S += [P('Die acht Tests `tk-…` stützen sich auf Festlegungen aus 4.3 bis 4.5. Die Zelle 0000 (bei tk-002 bis tk-005 '
            'auch 0001 und 0002) enthält einen Stopp-Befehl, sodass die Wirkung der Tasten im Endzustand sichtbar wird. '
            'Endzustände aus den echten Läufen (alle mit Rückkehrcode 0, `Test wahr`):')]
    rows = [['Test', 'Tastenfolge', 'BZ', 'AC', 'AR']]
    tkdir = os.path.join(ex.tmp, 'Tests')
    for f in sorted(x for x in os.listdir(tkdir) if x.startswith('tk-') and x.endswith('.txt')):
        rc, out = ex.lauf('Tests/' + f)
        m = re.search(r'Ende: .*?BZ=(\d+) AC=(\d+) AR=(\d+)', out)
        txt = open(os.path.join(tkdir, f), encoding='utf-8').read()
        folge = txt.split('Tastenfolge:')[1].split('Prüfungen')[0].strip()
        rows.append([f[:6], '`%s`' % folge, m.group(1), m.group(2), m.group(3)])
        assert rc == 0, f
    S += tbl(rows, wd(1.3, 3.4, 1.3, 2.2, 1.3), first_bold=True)
    S += note('hinweis', 'Die Endzustände sind Sollwerte im Sinne von Kapitel 5; in jedem Test stehen sie im Abschnitt '
              '`Prüfungen:`. Die Knotenzahl der Endzeile ist dagegen fassungsabhängig und kein Sollwert.')
    S += h2('11.3 Vollständigkeitstest')
    S += bullets([
        '**Vollständigkeitstest:** `c8205_befehlssweep.py` baut für alle 512 Operationscodes ein Minimalprogramm (der '
        'Befehl an Adresse 0000, der Stopp 020 an Adresse 0001) und führt es über dieselbe Knotengraph-Engine aus. Er '
        'prüft nicht die numerische Korrektheit jeder Formel, sondern nur, dass für jeden Code eine Implementierung '
        'vorhanden ist und der Automat sauber terminiert (kein Stub, kein Sackgassen-Knoten, keine erkennbare '
        'Endlosschleife).',
        '**Formelkorrektheit:** dafür dienen die regulären Tests mit Prüfungen (Kapitel 5), z. B. über '
        '`c8205_interpreter.sh`/`.bat`.',
        'Bei einem neuen oder geänderten Befehl zuerst den Claude-Interpreter benutzen (Kapitel 10), dann den Befehl in '
        '`c8205_interp.py` übernehmen, danach alle Referenztests und den Befehlssweep erneut laufen lassen.'])
    S += code('python3 c8205_befehlssweep.py                # alle 512 Codes, Kurzbericht\n'
              'python3 c8205_befehlssweep.py --verbose      # jeden Code einzeln\n'
              'python3 c8205_befehlssweep.py --code 251     # nur ein Code (oktal), im Detail')


# ------------------------------------------------------------------------------------------ Kapitel 12 und Anhang
def kap12(S, ex):
    S += h1('12 Checkliste und Vorlage')
    S += h2('12.1 Checkliste für neue Tests')
    S += numbered([
        'Programm endet mit einem Stopp-Befehl (`00000000020`)?',
        'Adressen vierstellig, Werte elfstellig, nur Ziffern 0–7?',
        'Keine Adresse doppelt mit verschiedenem Wert?',
        'Alle Zellen, auf die sich das Ergebnis stützt (gelesen oder geprüft), im Trommelabschnitt genannt, auch die mit '
        'Wert 0? Sonst ist der Test nur auf leerer Trommel reproduzierbar (3.5).',
        'Messpunkt gesetzt (`164 xxxx`) und passende `#DOK`/`#SPEI`/`#SPUR` vorhanden?',
        '`#PROT STUFE=` bewusst gewählt (Schleifen: 0 oder 2)?',
        'Tastenfolge endet mit R oder im Halt; `SW=1` vor G, wenn K0 mit Schreibwerk gebraucht wird?',
        'Wenn das Programm Zeichen liest oder schreibt: Kanal angewählt und das Gerät zugeordnet (Schalter oder Zeile '
        '`--leser1`, `--leser2`, `--stanzer1`, `--sw-ausgabe`, `--k0` in der Testdatei)?',
        'Prüfungen: mit den wichtigsten Sollwerten, damit der Test als Regressionstest taugt; bei Stanzer oder '
        'Schreibwerk zusätzlich die Dateiprüfung (`--pruefe-stanzer1`, `--pruefe-sw-ausgabe`)?'])
    S += h2('12.2 Vorlage')
    rc, out = ex.lauf('Handbuch-Tests/vorlage.txt')
    zl = zeilen(out)
    S += [P('Die Vorlage ist mit dem Python-Interpreter lauffähig (`Handbuch-Tests/vorlage.txt`) und entspricht dem Test '
            'aus Kapitel 5; bei Stufe 2 entsteht das Protokoll nach `Test-Protokolle/<Testname>/protokoll.txt`.')]
    S += code(ex.hbtext('vorlage.txt'))
    S += [P('Der echte Lauf der Vorlage (Rückkehrcode %d):' % rc)]
    S += code('$ python3 c8205_interp.py Handbuch-Tests/vorlage.txt\n' + out)


def anhang(S):
    S += h1('Anhang A: Begriffe')
    S += tbl([
        ['Begriff', 'Erklärung'],
        ['Test', 'ein simulierter Rechnerlauf: Trommeldatei + Tastenfolge (+ Prüfungen)'],
        ['Trommeldatei', 'zwei Bedeutungen: der Abschnitt `Trommeldatei:` einer Testdatei (Trommelabschnitt: '
                         '`Adresse: Wert`-Zeilen, Testmarken und Geräte-Zeilen) und die Datei `trommel.txt` des '
                         'Python-Interpreters mit dem ganzen Speicher (3.5)'],
        ['Persistente Trommel', 'die Datei `trommel.txt` (4096 Zeilen); behält ihren Inhalt über Tests und Aufrufe, wird '
                                'nur durch `erzeuge_leere_trommel.py` zurückgesetzt'],
        ['Überlagerung', 'Der Interpreter schreibt vor dem Start die Zeilen des Trommelabschnitts auf die Trommel; nicht '
                         'genannte Zellen behalten ihren Wert'],
        ['Tastenfolge', 'Bedienhandlungen am Pult, die den Ausgangszustand von Registern und Flags festlegen'],
        ['Testmarke', 'Zeile mit `#`, die nur der Testdurchführung dient (`#DOK`, `#SPEI`, `#SPUR`, `#PROT`)'],
        ['Geräte-Zeile', 'Zeile der Testdatei mit `--` (`--leser1`, `--leser2`, `--stanzer1`, `--sw-ausgabe`, `--k0`), die '
                         'ein virtuelles Gerät zuordnet'],
        ['Dateiprüfung', 'Prüfung, die die Stanzer- oder Schreibwerk-Ausgabedatei mit einer Soll-Datei vergleicht '
                         '(`--pruefe-stanzer1`, `--pruefe-sw-ausgabe`)'],
        ['Leerbefehl 164', 'Operation B = 1, A = 6, Z = 4: tut nichts (Messpunkt); löst bei passender Adresse die '
                           'Diagnose aus'],
        ['Konnektor B', 'Eintritt in den Ablauf von außen (Knoten 1 des Knotengraphen)'],
        ['Knoten 19', 'Ende der Phase-III-Arbeit; Startpunkt bei aufgestelltem Befehlsregister (nach Ü, ST, M ohne E '
                      'oder E ohne M)'],
        ['Knoten 54 (Konnektor 4)', 'Startpunkt nach M mit Sprung mit Rückkehrabsicht (025, 027, 125, 127): Phase III '
                                    'gilt als abgelaufen'],
        ['Knotenautomat', 'der Knotengraph des Befehlsablaufs mit seinen vier Knotentypen (Konnektor, Phasenzuordnung, '
                          'Anweisung, Test)'],
        ['Stub', 'Meldung „an dieser Stelle fehlt eine Umsetzung“; der Test wird angehalten'],
        ['Regressionstest', 'ein Test, dessen Sollwerte bestätigt sind und der bei jeder Änderung erneut gegen sie '
                            'verglichen wird'],
        ['Rückkehrcode', 'Ergebnis eines Interpreterlaufs für das Betriebssystem: 0 wahr, 4 ohne Prüfung, 6 falsch, '
                         '8 Laufzeitfehler, 16 Vorab-Prüfung negativ oder Trommeldatei fehlerhaft, 2 ungültiger Aufruf'],
        ['Claude-Interpreter', 'Verfahren, bei dem eine KI den Knotengraphen von Hand abarbeitet (Gegenprobe, neue '
                               'Befehle)'],
        ['Interleaving', 'logische Reihenfolge der Sektoren einer Spur ≠ physische; Schritt +05 (oktal) von logisch L nach '
                         'L+1'],
    ], wd(2.4, 7.6), first_bold=True)
    S += h1('Anhang B: Verweise')
    S += tbl([
        ['Thema', 'Dokument'],
        ['Aufruf, Schalter, Fehlermeldungen des Interpreters', 'PDF „Bedienungsanleitung Python-Interpreter“'],
        ['Rechner, Phasen, Register, Trommel', 'PDF „Rechnerbeschreibung“'],
        ['Tasten, Schalter, Geräte', 'PDF „Bedienpult und Peripherie“'],
        ['Alle Operationscodes', 'PDF „Einzelbefehlsliste“'],
        ['Zeichenkodes (Tabelle 1)', 'PDF „Kodetabellen“'],
        ['Knotengraph und T2', 'PDF „Knotengraph“'],
        ['Assembler, .test-Datei', 'PDF „Assembler-Dokumentation“'],
    ], wd(5.0, 5.0))


# ------------------------------------------------------------------------------------------ Hauptprogramm
def main():
    ap = argparse.ArgumentParser(description='Erzeugt C8205-Testhandbuch_A4.pdf')
    ap.add_argument('--proj', default=os.path.join(HERE, '..'), help='Projektwurzel (mit c8205_interp.py)')
    ap.add_argument('--handbuchtests', default=os.path.join(HERE, 'Handbuch-Tests'))
    ap.add_argument('--aus', default=None, help='Ziel-PDF; Vorgabe: <proj>/PDF/C8205-Testhandbuch_A4.pdf')
    ap.add_argument('--stand', default='08.10.2026', help='Stand (Datum) für Fußzeile und Läufe')
    args = ap.parse_args()
    proj = os.path.abspath(args.proj)
    aus = args.aus or os.path.join(proj, 'PDF', 'C8205-Testhandbuch_A4.pdf')
    os.makedirs(os.path.dirname(os.path.abspath(aus)), exist_ok=True)
    L.STAND = args.stand
    L.FOOTER_LEFT = 'C8205-Interpreter-Projekt · Stand ' + args.stand

    ex = Beispiele(proj, args.handbuchtests)
    try:
        S = []
        deckblatt(S, args.stand, args.stand)
        inhaltsverzeichnis(S)
        kurzanleitung(S)
        kap1_2(S)
        kap3(S, ex)
        kap4(S, ex)
        kap5(S, ex)
        kap6(S, ex)
        kap7(S, ex)
        kap8(S, ex)
        kap9(S, ex)
        kap10(S)
        kap11(S, ex, gesamtlauf(ex))
        kap12(S, ex)
        anhang(S)
        L.build(aus, S)
        print('geschrieben:', aus)
    finally:
        shutil.rmtree(ex.tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
