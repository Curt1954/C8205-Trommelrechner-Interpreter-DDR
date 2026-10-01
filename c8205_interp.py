#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C8205-Interpreter (Python-Stuetze), interpretativer Modus: alle Zeiten = 0.

Aufruf:  python3 c8205_interp.py [--graph DATEI] [--t2 DATEI] [--out VERZ|DATEI.log]
         [--leser1 PFAD] [--leser2 PFAD] [--stanzer1 PFAD]
         [--k0 tastatur|datei=PFAD] TEST.txt [TEST2.txt ...]
         --out mit Endung (z. B. Protokolle/test1.log): das Protokoll wird genau in diese Datei geschrieben
         (fehlende Ordner werden angelegt; nur mit einem Test). Ohne Endung: Verzeichnis, Protokoll dann
         in VERZ/<Testname>/protokoll.txt. Eine Protokolldatei entsteht nur bei #PROT STUFE=2.

Regeln (aus "C8205-Interpreter-Durchführung_eines_Tests.md"):
  * Der Knotengraph wird WORTLAUTGETREU aus der Datei "C8205-Interpreter-Eingänge_der_Knoten.md" gelesen und abgelaufen.
  * Vereinfachende Beschreibungen duerfen den Graphen nicht veraendern. Unklares wird als Stub gemeldet
    (Abbruch mit Meldung), nie stillschweigend "repariert".
  * Formale Pruefung vor Start (Abschnitt 5); bei Unstimmigkeit startet der Test NICHT.
  * #PROT STUFE=0/1/2: 0 = kein Knotenprotokoll, 1 = Knotenzeilen auf dem Bildschirm,
    2 = Knotenzeilen nur in protokoll.txt. Die #DOK-Diagnose (Befehl 164) erscheint stets auf dem Bildschirm.
  * Befehlszeilenschalter --knotentest (Standard: aus): nur wenn gesetzt, enthalten die Knotenprotokolle
    die Zeilen der durchlaufenen Knoten (K001 KON B ..., K004 TST 002 ... -> falsch). Ohne den Schalter
    bleiben davon nur die BR-Zeilen (nach Knoten 009), Diagnose und Fehler-/Stub-Meldungen.
"""
import argparse
import os
import random
import re
import sys

MASK33 = (1 << 33) - 1
MASK12 = 0xFFF

# physische Zugriffsreihenfolge der Trommel: PHYS_LOG[physische Position p] = logische Sektoradresse
# (Magnettrommel.md, Abschnitt Speichernumerierung/Interleaving; alle Werte oktal)
PHYS_LOG = [0o00,0o15,0o32,0o07,0o24,0o01,0o16,0o33,
            0o10,0o25,0o02,0o17,0o34,0o11,0o26,0o03,
            0o20,0o35,0o12,0o27,0o04,0o21,0o36,0o13,
            0o30,0o05,0o22,0o37,0o14,0o31,0o06,0o23]

TABELLE1 = [   # (Nr, Klbuch, Gbuch, Ausgabe-Adresse (3 Oktalstellen), Ascii GB, Ascii KB, Eingabe-Adresse, Sprung-Umstellung)
    (1, '1', '<', '001', 60, 49, 1, False),
    (2, '2', '"', '002', 34, 50, 2, False),
    (3, '3', '≈', '023', 0, 51, 3, False),
    (4, '4', '[', '004', 91, 52, 4, False),
    (5, '5', '>', '025', 62, 53, 5, False),
    (6, '6', "'", '026', 39, 54, 6, False),
    (7, '7', '≋', '007', 0, 55, 7, False),
    (8, '8', '~', '010', 126, 56, 8, False),
    (9, '9', ']', '031', 93, 57, 9, False),
    (10, '0', '#', '020', 35, 48, 0, False),
    (11, '%', '*', '174', 42, 37, 60, False),
    (12, 'Tabulator', 'Tabulator', '155', 9, 9, 61, True),
    (13, 'q', 'Q', '130', 81, 113, 40, False),
    (14, 'w', 'W', '166', 87, 119, 54, False),
    (15, 'e', 'E', '045', 69, 101, 21, False),
    (16, 'r', 'R', '111', 82, 114, 41, False),
    (17, 't', 'T', '163', 84, 116, 51, False),
    (18, 'z', 'Z', '171', 90, 122, 57, False),
    (19, 'u', 'U', '144', 85, 117, 52, False),
    (20, 'i †', 'I', '051', 73, 105, 25, False),
    (21, 'o', 'O', '106', 79, 111, 38, False),
    (22, 'p', 'P', '127', 80, 112, 39, False),
    (23, ':', '(', '015', 40, 58, 13, True),
    (24, '+', '=', '040', 61, 43, 16, True),
    (25, 'Um. KB', 'Um. KB', '117', 0, 0, 47, True),
    (26, 'Um. GB', 'Um. GB', '057', 0, 0, 31, True),
    (27, 'a', 'A', '061', 65, 97, 17, False),
    (28, 's', 'S', '142', 83, 115, 50, False),
    (29, 'd', 'D', '064', 68, 100, 20, False),
    (30, 'f', 'F', '046', 70, 102, 22, False),
    (31, 'g', 'G', '067', 71, 103, 23, False),
    (32, 'h', 'H', '070', 72, 104, 24, False),
    (33, 'j', 'J', '121', 74, 106, 33, False),
    (34, 'k', 'K', '122', 75, 107, 34, False),
    (35, 'l', 'L', '103', 76, 108, 35, False),
    (36, '`', ';', '160', 59, 96, 48, False),
    (37, '/', ')', '141', 41, 47, 49, True),
    (38, 'SatzMarke', 'WRZL', '272', 10, 10, 26, True),
    (39, 'y', 'Y', '150', 89, 121, 56, False),
    (40, 'x', 'X', '147', 88, 120, 55, False),
    (41, 'c', 'C', '043', 67, 99, 19, False),
    (42, 'v', 'V', '165', 86, 118, 53, False),
    (43, 'b', 'B', '062', 66, 98, 18, False),
    (44, 'n', 'N', '105', 78, 110, 37, False),
    (45, 'm', 'M', '124', 77, 109, 36, False),
    (46, ',', '?', '153', 63, 44, 59, True),
    (47, '.', '!', '073', 33, 46, 27, True),
    (48, '-', '△', '100', 465, 45, 32, True),
    (49, 'Leertaste', 'ZR', '032', 32, 32, 10, False),
    (50, 'Irrung Zeichen', 'Irrung Zeichen', '377', 0, 0, None, False),
    (51, 'Irrung Satz', 'Irrung Satz', '016', 0, 0, 14, True),
    (52, 'Transport (Relikt)', 'Transport (Relikt)', '177', 0, 0, 63, False),
]
AUSGABE_ZEILE = {r[3]: r for r in TABELLE1 if r[0] != 52}      # Zeile 52 (Transport) ist ein Relikt
EINGABE_ZEILE = {r[6]: r for r in TABELLE1 if r[6] is not None and r[0] != 52}
EINGABE_ZEILE[0o36] = (0, 'Irrung Block', 'Irrung Block', '', 0, 0, 0o36, True)   # IB, Kodetabellen 3.3


def octs(v, n):
    return format(v, 'o').rjust(n, '0')


def sgn(w):
    """33-Bit-Wort als vorzeichenbehaftete Dualzahl (Zweierkomplement, z0 = Vorzeichen)."""
    w &= MASK33
    return w - (1 << 33) if (w >> 32) else w


class Stub(Exception):
    """Nicht (oder nicht eindeutig) definiert / nicht implementiert -> Test bricht laut ab."""


class LaufFehler(Exception):
    """Fehler beim Ablauf des Knotengraphen (Geraet nicht nutzbar, Stub, fehlender Ausgang)."""


# ----------------------------------------------------------------------------------------------
# Einlesen von Knotengraph und Variablentabelle T2
# ----------------------------------------------------------------------------------------------
def load_graph(path):
    g = {}
    for raw in open(path, encoding='utf-8'):
        line = raw.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        parts = [p.strip() for p in line.split(';', 4)]
        if len(parts) < 5:
            continue
        num = int(parts[0])
        typ, text, outs = parts[2], parts[3], parts[4]
        n = dict(num=num, typ=typ, text=text, out=None, wahr=None, falsch=None, end=False, anw=None)
        m = re.fullmatch(r'\$ANWEISUNG-(\d+)', text)
        if m:
            n['anw'] = int(m.group(1))
        if outs.strip() == '---':
            n['end'] = True
        else:
            for tgt, _inp, kind in re.findall(r'(\d+)\((\d+)(?: (falsch|wahr))?\)', outs):
                if kind == 'falsch':
                    n['falsch'] = int(tgt)
                elif kind == 'wahr':
                    n['wahr'] = int(tgt)
                else:
                    n['out'] = int(tgt)
        g[num] = n
    return g


def load_t2(path):
    t2 = {}
    for raw in open(path, encoding='utf-8'):
        m = re.match(r'\s*ANWEISUNG-(\d+)\s*;', raw)
        if m:
            t2[int(m.group(1))] = raw.split(';')[1].strip() if ';' in raw else ''
    return t2


# ----------------------------------------------------------------------------------------------
# Testdatei einlesen und formal pruefen (Abschnitt 2 und 5 der Testbeschreibung)
# ----------------------------------------------------------------------------------------------
class Test:
    def __init__(self, path):
        self.path = path
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.mem = {}
        self.dok = []          # Liste (xxxx, text) in Dateireihenfolge
        self.spei = []         # Liste (xxxx, start, ende) in Dateireihenfolge
        self.spur = []         # Liste (xxxx, adresse) in Dateireihenfolge
        self.stufe = None
        self.tasten = []
        self.zeilen = []       # uebernommene Adresszeilen (fuer das Protokoll)
        self.pruef_reg = {}    # Abschnitt 3a: Register/Flag-Sollwerte, Schluessel -> int
        self.pruef_mem = {}    # Abschnitt 3a: Speicher-Sollwerte, Adresse -> int
        self._pruef_regzeile_gesehen = False
        self.fehler = []
        self.hinweise = []
        self._parse()

    # Abschnitt 3a: zulaessige Schluessel der Pruefungen-Register/Flag-Zeile, mit Sollbreite (Oktalstellen)
    PRUEF_SCHLUESSEL = {'BZ': 4, 'AC': 11, 'AR': 4, 'FE': 1, 'FUE': 1, 'BS': 1, 'US': 1,
                        'E': 1, 'A': 1, 'V1': 1, 'V2': 1}

    def _parse_pruef_regzeile(self, s, nr):
        s2 = s.split('#', 1)[0].strip()
        if not s2:
            return
        for tok in s2.split():
            mt = re.fullmatch(r'([A-Z0-9]+)=([0-7]+)', tok)
            if not mt:
                self.fehler.append(f'Zeile {nr}: Pruefungen: ungueltiges Element {tok!r}')
                continue
            key, val = mt.group(1), mt.group(2)
            if key not in self.PRUEF_SCHLUESSEL:
                self.fehler.append(f'Zeile {nr}: Pruefungen: unbekannter Schluessel {key!r}')
                continue
            breite = self.PRUEF_SCHLUESSEL[key]
            if len(val) != breite:
                self.fehler.append(f'Zeile {nr}: Pruefungen: {key}={val!r} hat nicht {breite} Oktalstellen')
                continue
            if breite == 1 and val not in ('0', '1'):
                self.fehler.append(f'Zeile {nr}: Pruefungen: Flag {key}={val!r} muss 0 oder 1 sein')
                continue
            if key in self.pruef_reg:
                self.fehler.append(f'Zeile {nr}: Pruefungen: Schluessel {key} mehrfach angegeben')
                continue
            self.pruef_reg[key] = int(val, 8)

    def _parse(self):
        modus = 'trommel'
        for nr, raw in enumerate(open(self.path, encoding='utf-8'), 1):
            line = raw.rstrip('\n').rstrip()
            s = line.strip()
            if not s:
                continue
            if s.lower().startswith('trommeldatei'):
                modus = 'trommel'
                continue
            if s.lower().startswith('tastenfolge'):
                modus = 'tasten'
                rest = s.split(':', 1)[1].strip() if ':' in s else ''
                self.tasten += rest.split()
                continue
            if s.lower().startswith('pr\u00fcfungen') or s.lower().startswith('pruefungen'):
                modus = 'pruefungen'
                rest = s.split(':', 1)[1].strip() if ':' in s else ''
                if rest:
                    self._parse_pruef_regzeile(rest, nr)
                    self._pruef_regzeile_gesehen = True
                continue
            if modus == 'pruefungen':
                m_mem = re.fullmatch(r'([0-7]{4}):\s*([0-7]{11})\s*(#.*)?', s)
                if m_mem:
                    a, w = int(m_mem.group(1), 8), int(m_mem.group(2), 8)
                    if a in self.pruef_mem and self.pruef_mem[a] != w:
                        self.fehler.append(f'Zeile {nr}: Pruefungen: Adresse {m_mem.group(1)} '
                                            f'widersprüchlich mehrfach belegt')
                    self.pruef_mem[a] = w
                elif not self._pruef_regzeile_gesehen:
                    self._parse_pruef_regzeile(s, nr)
                    self._pruef_regzeile_gesehen = True
                else:
                    self.fehler.append(f'Zeile {nr}: Pruefungen: ungueltige Zeile: {s!r}')
                continue
            if modus == 'tasten':
                self.tasten += s.split()
                continue
            m = re.fullmatch(r'#DOK-([0-7]{4})\s*(.*)', s)
            if m:
                self.dok.append((int(m.group(1), 8), m.group(2)))
                continue
            if s.startswith('#DOK'):
                self.fehler.append(f'Zeile {nr}: fehlerhafte Testmarke #DOK: {s!r}')
                continue
            m = re.fullmatch(r'#SPEI-([0-7]{4})\s+([0-7]{4})-([0-7]{4})', s)
            if m:
                self.spei.append((int(m.group(1), 8), int(m.group(2), 8), int(m.group(3), 8)))
                continue
            if s.startswith('#SPEI'):
                self.fehler.append(f'Zeile {nr}: fehlerhafte Testmarke #SPEI: {s!r}')
                continue
            m = re.fullmatch(r'#SPUR-([0-7]{4})\s+([0-7]{4})', s)
            if m:
                self.spur.append((int(m.group(1), 8), int(m.group(2), 8)))
                continue
            if s.startswith('#SPUR'):
                self.fehler.append(f'Zeile {nr}: fehlerhafte Testmarke #SPUR: {s!r}')
                continue
            m = re.fullmatch(r'#PROT\s+STUFE=(\S+)', s)
            if m:
                if self.stufe is not None:
                    self.fehler.append(f'Zeile {nr}: #PROT STUFE mehrfach')
                if m.group(1) not in ('0', '1', '2'):
                    self.fehler.append(f'Zeile {nr}: #PROT STUFE={m.group(1)} ungueltig (0,1,2)')
                else:
                    self.stufe = int(m.group(1))
                continue
            if s.startswith('#'):
                continue
            m = re.fullmatch(r'([0-7]{4}):\s*([0-7]{11})\s*(#.*)?', s)
            if not m:
                self.fehler.append(f'Zeile {nr}: ungueltiges Zeilenformat: {s!r}')
                continue
            a, w = int(m.group(1), 8), int(m.group(2), 8)
            if a in self.mem and self.mem[a] != w:
                self.fehler.append(f'Zeile {nr}: Adresse {m.group(1)} widerspruechlich belegt')
            self.mem[a] = w
            self.zeilen.append(f'{m.group(1)}: {m.group(2)}')
        if self.stufe is None:
            self.stufe = 1
        # #SPEI/#SPUR sind von #DOK unabhaengig (einzeln zulaessig); nur die Spanne von #SPEI wird geprueft
        for x, s0, e0 in self.spei:
            if not s0 <= e0:
                self.fehler.append(f'#SPEI-{octs(x,4)} {octs(s0,4)}-{octs(e0,4)}: keine gueltige Spanne')
        if not self.tasten:
            self.fehler.append('Tastenfolge fehlt')


# ----------------------------------------------------------------------------------------------
# Rechnerzustand
# ----------------------------------------------------------------------------------------------
class Machine:
    FLAGS = ['E', 'A', 'T', 'SW', 'K1', 'K2', 'K3', 'FE', 'FUE', 'BS', 'US', 'V1', 'V2', 'H', 'SP']

    def __init__(self, mem):
        self.mem = dict(mem)
        self.AC = self.BZ = self.AR = self.OR = self.adr = 0
        self.fl = {k: 0 for k in self.FLAGS}
        self.x_merker = 0
        self.zaehler = 0
        self.start_sek = 0
        self.vgl_ac = 0
        self.vgl_v = 0
        self.halted = False
        self.halt_grund = ''
        self.came_from = None
        self.diag_hook = None
        self.sw_lage = random.choice(['KB', 'GB'])   # Zeichenlage des Schreibwerks beim Netz-Einschalten zufaellig
        self.sw_zeilenanfang = True                  # Terminal-Cursor am Zeilenanfang (SW-Ausgabe)
        self.log = lambda s: None
        self.leser = {1: None, 2: None}              # Lochbandleser 1/2 (Kanal K1/K2), None = nicht angegeben
        self.stanzer = None                          # Lochbandstanzer 1 (Kanal K1)
        self.eingabe_sprung = False
        self.k0 = None                               # K0-Eingabequelle (--k0), None = nicht angegeben
        self.zeichenlage = 'KB'                      # Zeichenlage der Eingabe (rechnerweit, Start KB)
        self.vor_phase2 = False                      # Automat steht vor Phase II (nach E unter gehaltenem M)
        self.br_aufgestellt = False                  # BR aufgestellt, noch nicht ausgefuehrt (Ue, E-Schritt): R startet bei Knoten 19
        self.lese_adr = False                        # Eingabe-Lesebefehl: Operand ist die Adresse selbst

    def rd(self, a):
        return self.mem.get(a & MASK12, 0)      # nicht genannte Zellen = 0 (O-2, geklaert)

    def wr(self, a, v):
        self.mem[a & MASK12] = v & MASK33

    @property
    def B(self): return (self.OR >> 6) & 7
    @property
    def A(self): return (self.OR >> 3) & 7
    @property
    def Z(self): return self.OR & 7
    @property
    def L(self): return self.Z & 1
    @property
    def R(self): return self.Z >> 1
    @property
    def z30(self): return 1 if self.Z >= 4 else 0

    def ac_neg(self, r_abhaengig=False):
        if r_abhaengig and self.R == 1:
            return (self.AC & 1) == 1
        return ((self.AC >> 32) & 1) == 1


def sektor(a):
    return a & 0o37


# ----------------------------------------------------------------------------------------------
# Tests (Rueckgabe bool) und Anweisungen (ANWEISUNG-nnn aus der Variablentabelle T2)
# ----------------------------------------------------------------------------------------------
def t002(m):
    r = m.x_merker
    m.x_merker = 0
    return bool(r)

def t003(m): return True                        # interpretativ: Koinzidenz immer erfuellt
def t006(m): return m.B not in (0, 1) and m.A in (5, 7) and m.L == 1
def t008(m): return m.B <= 1 and m.A in (4, 5, 7)

def t009(m):
    B, A = m.B, m.A
    v1, v2 = m.fl['V1'], m.fl['V2']
    v3 = v1 and v2
    return bool((B == 0 and A == 4 and m.ac_neg()) or
                (B == 0 and A == 5 and not m.ac_neg()) or
                (B == 1 and A == 4 and (v1 or v3)) or
                (B == 1 and A == 5 and (v2 or v3)) or
                (B == 0 and A == 7 and m.fl['FUE']) or
                (B == 1 and A == 7 and v3))

def t011(m): return m.L == 1
def t013(m): return m.B <= 1 and m.A == 2 and m.z30 == 1
def t014(m): return m.B <= 1 and m.A == 2 and m.z30 == 0
def t015(m): return m.B <= 1 and m.A == 1
def t016(m): return m.B <= 1 and m.A == 3
def t018(m): return m.B <= 1 and m.A in (0, 4, 5, 7)
def t019(m): return m.B == 3
def t020(m): return bool(m.fl['FUE'])
def t023(m): return m.B >= 4
def t031(m): return bool(m.fl['BS'])
def t034(m): return m.B == 3
def t036(m): return m.B <= 1 and m.A == 0
def t038(m): return m.B == 2
def t040(m): return m.B >= 4 and m.zaehler == 32
def t041(m): return m.B in (6, 7) and m.start_sek != 0 and sektor(m.AR) == 0o23
def t042(m): return m.B in (5, 7) and m.ac_neg(r_abhaengig=True)
def t043(m): return m.B <= 1 and m.A in (2, 6) and m.z30 == 0

def t024(m):
    # normale Abbruchbedingung (040 ODER 041); die X-Bedingung (042) wird an Knoten 73 getestet
    return t040(m) or t041(m)


def a044(m):
    m.x_merker = 1                  # Merker wird erst bei Auswertung an Knoten 4 (002) geloescht


def a001(m):                        # gleichzeitig, Altwerte
    t_ar, t_bz = m.AR, m.BZ
    m.AR = t_bz
    m.BZ = (t_ar + 1) & MASK12

def a004(m): pass                   # interpretativ ohne Wirkung

def a005(m):
    w = m.rd(m.AR)
    m.OR = w & 0x1FF
    m.adr = (w >> 9) & MASK12

def a007(m): m.BZ = m.adr
def a010(m): m.OR = m.OR & ~0o070   # T2: "interne Umstellung auf A=0"
def a012(m): m.AC = 0

def a021(m):
    B, A, Z, R = m.B, m.A, m.Z, m.R
    a = m.AR
    lese, m.lese_adr = m.lese_adr, False

    def addsub(sub, cond_pos):
        ac, v = sgn(m.AC), sgn(a) if lese else sgn(m.rd(a))     # Eingabe-Lesebefehl addiert die Adresse selbst
        res = ac - v if sub else ac + v
        if B in (2, 3) and R == 0:      # Ueberlauf nur bei Einzel-/markierten Einzelbefehlen ohne R
            m.fl['FUE'] = 0 if -(1 << 32) <= res < (1 << 32) else 1
        m.AC = res & MASK33

    if B == 1 and A == 6:               # Leer-Befehl (Z>=4): keine Operation, Loeschung lief in Phase III
        pass
    elif A == 0:
        m.AC &= m.rd(a)
    elif A == 1:
        addsub(False, None)
    elif A == 2:
        addsub(True, None)
    elif A == 3:
        if B == 3 and Z in (0, 1):
            pass                        # nur Vergleichersetzen
        elif Z == 3:
            pass                        # Leer-Operation (Einzelbefehlsuebersicht, geht der Formel vor)
        elif Z == 2:
            pass                        # Befehlsliste 4.3 (A=3, Z=2): z32=L=0 -> AC := Vr AC, keine Addition;
                                        # die Rechtsverschiebung (R=1) leistet die Resultatbehandlung a022
        else:
            addsub(not m.ac_neg(), None)   # AC<0: Addition, AC>=0: Subtraktion
    elif A == 4:
        m.wr(a, m.AC)
    elif A == 5:
        if Z % 2 == 1:
            raise Stub(f'Befehl {B}{A}{Z}: R-Operation muesste ueber Knoten 10/37/38 laufen')
        m.wr(a, m.AC & m.rd(a))
    elif A == 6:
        m.wr(a, (~m.AC & MASK33) & m.rd(a))
    elif A == 7:
        if Z % 2 == 1:
            raise Stub(f'Befehl {B}{A}{Z}: R-Minus-Operation muesste ueber Knoten 10/37/38 laufen')
        if Z == 2:
            if (m.AC & 1) == 0:
                m.wr(a, 0)
        elif not m.ac_neg():
            m.wr(a, 0)
    m.zaehler += 1


def a022(m):
    R = m.R
    if m.B == 1 and m.A == 6 and m.Z >= 4:
        # Leer-Befehl (Befehlsliste Nr. 66/67: 164, 166 "Leer-Operation ohne Loeschen"): OHNE Resultatbehandlung,
        # das Z-Feld erzeugt hier keine Verschiebung (die Loeschung bei Z=5,7 lief bereits in Phase III).
        R = 0
    if R == 1:
        m.AC = (m.AC >> 1) & MASK33
    elif R == 2:
        m.AC = (m.AC << 1) & MASK33
    elif R == 3:
        m.AC = ((m.AC << 1) & MASK33) | ((m.AC >> 32) & 1)
    if (m.B, m.A, m.Z) == (1, 6, 4) and m.diag_hook:
        m.diag_hook(m)                  # Hook nach ANWEISUNG-022 (Abschnitt 7 der Testbeschreibung)

def a025(m):
    m.AR = (m.AR & ~0o37) | ((m.AR + 0o15) & 0o37)     # naechster Sektor in physischer Folge

def a026(m): m.BZ = (((m.AC >> 9) & MASK12) | m.adr) & MASK12
def a027(m): m.OR = m.OR & ~(1 << 5)
def a029(m):
    feld = (m.AC >> 9) & MASK12
    feld |= (m.BZ >> 1)
    m.AC = (m.AC & ~(MASK12 << 9)) | ((feld & MASK12) << 9)

def a030(m):
    if m.came_from == 42:
        m.fl['US'] = 1
        m.halt_grund = 'Unbedingter Stop (US:=1)'
    elif m.came_from == 43:
        m.fl['BS'] = 1
        m.halt_grund = 'Bedingter Stop (BS:=1)'
    else:
        m.halt_grund = 'Halt wegen Ueberlauf (FUE bereits 1)'
    m.halted = True

def a035(m):
    m.fl['V1'] = m.fl['V2'] = 1
    m.vgl_ac = m.AC
    m.vgl_v = m.rd(m.AR) if m.A <= 3 else 0

def a037(m):
    ac, v = sgn(m.vgl_ac), sgn(m.vgl_v)
    if ac < v:
        m.fl['V1'], m.fl['V2'] = 1, 0
    elif ac > v:
        m.fl['V1'], m.fl['V2'] = 0, 1
    else:
        m.fl['V1'] = m.fl['V2'] = 1


def sw_zeichen(m, zeile):
    """Text fuer die Ausgabe einer Tabelle-1-Zeile in der aktuellen SW-Zeichenlage."""
    nr, kl, gb, _, a_gb, a_kb = zeile[:6]
    a = a_kb if m.sw_lage == 'KB' else a_gb
    if a in (9, 10, 32) or 33 <= a <= 255:
        return chr(a)
    name = kl if m.sw_lage == 'KB' else gb
    return f'<{name or "Nr." + str(nr)}>'


ROT = '\033[31m'
RESET = '\033[0m'
GERAETE = {'leser1': None, 'leser2': None, 'stanzer1': None, 'k0': None}


class KonfigFehler(Stub):
    """Geraet wird benutzt, ist aber nicht (oder falsch) angegeben."""


def rot(m, text):
    """Fehlermeldung auf dem Terminal (stderr), rot wenn Terminal."""
    if not m.sw_zeilenanfang:
        sys.stdout.write('\n')
        m.sw_zeilenanfang = True
    sys.stdout.flush()
    if sys.stderr.isatty() and 'NO_COLOR' not in os.environ:
        text = ROT + text + RESET
    sys.stderr.write(text + '\n')
    sys.stderr.flush()


class Leser:
    """Lochbandleser: PFAD = Datei (ein Streifen) oder Verzeichnis (Streifen in Namensreihenfolge).
    Eine Zeile je Lochungszeile: acht Zeichen 0/1 fuer w v u p 8 4 2 1; Leerzeilen = Vorspann."""
    def __init__(self, pfad):
        self.pfad = pfad
        self.dateien = None
        self.idx = 0
        self.zeilen = None
        self.pos = 0

    def naechste(self):
        if self.dateien is None:
            if os.path.isdir(self.pfad):
                self.dateien = sorted(os.path.join(self.pfad, f) for f in os.listdir(self.pfad)
                                      if os.path.isfile(os.path.join(self.pfad, f)) and not f.startswith('.'))
            elif os.path.isfile(self.pfad):
                self.dateien = [self.pfad]
            else:
                raise KonfigFehler(f'Lochstreifen-Pfad nicht gefunden: {self.pfad}')
        while True:
            if self.zeilen is None:
                if self.idx >= len(self.dateien):
                    return None
                with open(self.dateien[self.idx], encoding='utf-8') as fh:
                    self.zeilen = [x.strip() for x in fh]
                self.pos = 0
            while self.pos < len(self.zeilen):
                z = self.zeilen[self.pos]
                self.pos += 1
                if not z:
                    continue
                if not re.fullmatch(r'[01]{8}', z):
                    raise KonfigFehler(f'Lochstreifen {self.dateien[self.idx]}: ungueltige Zeile {z!r}')
                return z
            self.zeilen = None
            self.idx += 1


class Stanzer:
    """Lochbandstanzer: PFAD = Datei (oder Verzeichnis -> stanzer-ausgabe.txt darin); eine Zeile je Zeichen."""
    def __init__(self, pfad):
        self.pfad = os.path.join(pfad, 'stanzer-ausgabe.txt') if os.path.isdir(pfad) else pfad
        self.begonnen = False

    def stanze(self, lb):
        d = os.path.dirname(os.path.abspath(self.pfad))
        os.makedirs(d, exist_ok=True)
        with open(self.pfad, 'a' if self.begonnen else 'w', encoding='utf-8') as fh:
            fh.write(format(lb, '08b') + '\n')
        self.begonnen = True


ROW_NR = {r[0]: r for r in TABELLE1}


def _norm(s):
    return re.sub(r'[\s.]', '', s).upper()


NAMEN = {}
for _r in TABELLE1:
    if _r[0] != 52:
        for _nm in (_r[1], _r[2]):
            if len(_nm) > 1:
                NAMEN.setdefault(_norm(_nm), _r)
NAMEN.update({'ZR': ROW_NR[49], 'WM': ROW_NR[12], 'TAB': ROW_NR[12], 'WRZL': ROW_NR[38],
              'IS': ROW_NR[51], 'IB': EINGABE_ZEILE[0o36]})

# Pult-Tastatur (K0, Schalter SW nicht gedrueckt = Flag T): nur 0-9 + - , . : ZR WM IS IB (B und D haben
# keinen Code und sind "nicht weiter benoetigt"). Bei gedrueckter SW-Taste sind alle Codes der Tabelle 1 eingebbar.
T_ERLAUBT = {_r[6] for _r in TABELLE1
             if _r[6] is not None and _r[0] != 52 and _r[1] in list('0123456789+-,.:')}
T_ERLAUBT |= {ROW_NR[49][6], ROW_NR[12][6], ROW_NR[51][6], 0o36}


def k0_zeile(tok, lage):
    """Tabelle-1-Zeile zu einem K0-Zeichen (Host-Zeichen oder Name wie ZR, WM, IS, IB, TAB, WRZL)."""
    if tok == ' ':
        return ROW_NR[49]
    if len(tok) == 1:
        code = ord(tok)
        for ci in ((4, 5) if lage == 'GB' else (5, 4)):          # Ascii GB = Index 4, Ascii KB = Index 5
            for r in TABELLE1:
                if r[0] != 52 and r[6] is not None and r[ci] == code:
                    return r
        return None
    return NAMEN.get(_norm(tok))


class K0Quelle:
    """K0-Eingabe: 'tastatur' (Host-Tastatur, ein Tastendruck je Eingabebefehl) oder 'datei=PFAD'
    (Textdatei, ein Zeichen oder Name je Zeile, '#' = Kommentar)."""
    def __init__(self, spec):
        self.tast = spec == 'tastatur'
        self.pfad = None if self.tast else spec.split('=', 1)[1]
        self.zeilen = None
        self.pos = 0

    def naechstes(self):
        """Naechstes Zeichen/Name oder None (Ende)."""
        if self.tast:
            if sys.stdin.isatty():
                if sys.platform == 'win32':
                    import msvcrt
                    c = msvcrt.getch().decode('utf-8', errors='replace')
                else:
                    import termios, tty
                    fd = sys.stdin.fileno()
                    alt = termios.tcgetattr(fd)
                    try:
                        tty.setcbreak(fd)                   # Taste sofort, kein Echo, Strg+C wirkt weiter
                        c = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, alt)
            else:
                c = sys.stdin.read(1)
            return c or None
        if self.zeilen is None:
            try:
                with open(self.pfad, encoding='utf-8') as fh:
                    self.zeilen = [x.rstrip('\r\n') for x in fh]
            except OSError as e:
                raise KonfigFehler(f'K0-Datei nicht lesbar: {self.pfad} ({e.strerror})')
        while self.pos < len(self.zeilen):
            z = self.zeilen[self.pos]
            self.pos += 1
            if z == '' or z.startswith('#'):
                continue
            return z if len(z) == 1 else z.strip()
        return None

SW_FARBE = '\033[33m'          # dunkelgelb (ANSI 33); Ausgabe durch Ausgabebefehle
SW_RESET = '\033[0m'

def sw_schreibe(m, s):
    if sys.stdout.isatty() and 'NO_COLOR' not in os.environ:
        sys.stdout.write(SW_FARBE + s + SW_RESET)
    else:
        sys.stdout.write(s)
    sys.stdout.flush()
    m.sw_zeilenanfang = s.endswith('\n')

def a028(m):
    a = m.AR
    if a & 0o4000:                              # Anwahlbefehl (a1 >= 4): Kanal waehlen
        kanal = {0o7: 0, 0o6: 1, 0o5: 2, 0o4: 3}.get((a >> 6) & 0o7)
        if kanal is None:
            raise Stub(f'Anwahlbefehl {octs(a,4)}: a2 < 4 nicht definiert')
        for k in (1, 2, 3):
            m.fl[f'K{k}'] = 1 if k == kanal else 0
        if kanal == 0:
            m.fl['T'], m.fl['SW'] = (0, 1) if m.fl['SW'] else (1, 0)
        else:
            m.fl['T'] = m.fl['SW'] = 0
        return
    m.fl['A'] = 1                               # Ausgabebefehl: Zeichen ueber Ausgabe-Adresse
    z = AUSGABE_ZEILE.get(format((a >> 3) & 0o377, 'o').rjust(3, '0'))
    if m.fl['K2']:                              # K2 = Schreibwerk (SW), unabhaengig vom Schalter SW
        if z is None:
            m.log(f'Hinweis: Ausgabe-Adresse {octs(a,4)} nicht in Tabelle 1 - keine Ausgabe')
        elif z[3] == '117':
            m.sw_lage = 'KB'                    # wirkt, erzeugt aber keine sichtbare Ausgabe
        elif z[3] == '057':
            m.sw_lage = 'GB'
        else:
            sw_schreibe(m, sw_zeichen(m, z))
    elif m.fl['K1']:                            # K1 = Lochbandstanzer 1
        if m.stanzer is None:
            rot(m, 'FEHLER: Ausgabe auf Lochbandstanzer 1 (Kanal K1) angefordert, aber --stanzer1 nicht angegeben.')
            raise KonfigFehler('--stanzer1 nicht angegeben')
        if z is None:
            m.log(f'Hinweis: Ausgabe-Adresse {octs(a,4)} nicht in Tabelle 1 - nichts gestanzt')
        else:
            m.stanzer.stanze(int(z[3], 8))
    # K0, K3: keine Ausgabe
    m.fl['A'] = 0

def a017(m): pass                               # T2: keine eigenstaendige Wirkung ueber 028 hinaus

def a032(m):                                    # Ausfuehren der Eingabe (Leser K1/K2, Pult-Tastatur/Schreibwerk K0)
    m.fl['E'] = 1
    if m.fl['K1'] or m.fl['K2']:
        k = 1 if m.fl['K1'] else 2
        leser = m.leser.get(k)
        if leser is None:
            rot(m, f'FEHLER: Eingabe von Lochbandleser {k} (Kanal K{k}) angefordert, aber --leser{k} nicht angegeben.')
            raise KonfigFehler(f'--leser{k} nicht angegeben')
        try:
            z = leser.naechste()
        except KonfigFehler as e:
            rot(m, f'FEHLER: Lochbandleser {k}: {e}')
            raise
        if z is None:                           # kein Streifen mehr: Rechner wartet unendlich, Flag E bleibt 1
            m.halted = True
            m.halt_grund = f'Lochbandleser {k}: kein Lochstreifen mehr - Rechner wartet (Flag E bleibt 1)'
            return
        lb = int(z, 2)
        if bin(lb).count('1') % 2 == 0:         # gerade Zahl gelochter Spuren = Geraetefehler
            m.fl['FE'] = 1
            m.halted = True
            m.halt_grund = f'Fehler bei Eingabe (FE): gerade Zahl von Lochungen ({z})'
            return
        ea = (lb & 0x0F) | ((lb >> 1) & 0x30)
        e = EINGABE_ZEILE.get(ea)
        if e is None:
            raise Stub(f'Eingabeadresse {ea:02o} (Lochbild {z}) kommt in Tabelle 1 nicht vor')
    elif not m.fl['K3'] and (m.fl['T'] or m.fl['SW']):       # K0: Tastatur (T) oder Schreibwerk (SW)
        modus = 'Schreibwerk (SW)' if m.fl['SW'] else 'Pult-Tastatur (T)'
        if m.k0 is None:
            rot(m, f'FEHLER: Eingabe ueber K0 ({modus}) angefordert, aber --k0 nicht angegeben '
                   f'(--k0 tastatur | --k0 datei=PFAD).')
            raise KonfigFehler('--k0 nicht angegeben')
        while True:
            try:
                tok = m.k0.naechstes()
            except KonfigFehler as ex:
                rot(m, f'FEHLER: {ex}')
                raise
            if tok is None:                     # Quelle zu Ende: sofortiger Halt (EINGABE_ENDE)
                m.halted = True
                m.halt_grund = 'EINGABE_ENDE: K0-Eingabequelle zu Ende (Flag E bleibt 1)'
                return
            e = k0_zeile(tok, m.zeichenlage)
            if e is None:
                grund = f'Zeichen {tok!r} kommt in Tabelle 1 nicht vor'
            elif m.fl['T'] and e[6] not in T_ERLAUBT:
                grund = (f'{tok!r} ist an der Pult-Tastatur (T) nicht eingebbar - '
                         f'nur 0-9 + - , . : ZR WM IS IB (fuer alle Codes: Schalter SW druecken)')
            else:
                break
            if m.k0.tast:                       # Taste ohne Wirkung: weiter auf gueltige Taste warten
                continue
            rot(m, f'FEHLER: K0-Eingabe: {grund}.')
            raise KonfigFehler(grund)
        ea = e[6]
    else:
        raise Stub('Eingabebefehl: Kanal K3 bzw. kein Kanal angewaehlt - keine Eingabe moeglich')
    m.AR |= ea
    m.eingabe_sprung = e[7]
    if e[0] == 25:                              # Um. KB / Um. GB aendern die Zeichenlage der Eingabe
        m.zeichenlage = 'KB'
    elif e[0] == 26:
        m.zeichenlage = 'GB'
    m.fl['E'] = 0

def a033(m):                                    # Umstellung nach der Eingabe
    if m.eingabe_sprung:
        m.OR &= ~0o070                          # A := 0 (unbedingter Sprung)
    else:
        m.OR = (m.OR & ~0o700) | (((m.B + 2) & 7) << 6)     # B := B+2, A bleibt 1 (Lesebefehl)
        m.lese_adr = True

def make_stub(n):
    def f(m):
        raise Stub(f'ANWEISUNG-{n:03d} ist noch nicht implementiert (Ein-/Ausgabe o. ae.)')
    return f

FUNCS = {}
for _n, _f in list(globals().items()):
    mm = re.fullmatch(r'([ta])(\d{3})', _n)
    if mm:
        FUNCS[int(mm.group(2))] = _f

TYP = {'Konnektor': 'KON', 'Phasenzuordnung': 'PHA', 'Anweisung': 'ANW', 'Test': 'TST'}


# ----------------------------------------------------------------------------------------------
# Tastenfolge (Abschnitt 3): nur die dort beschriebenen Faelle sind definiert
# ----------------------------------------------------------------------------------------------
def tastenfolge(m, tokens, run_e=None):
    """Wertet die Tastenfolge aus. run_e fuehrt einen Einzelschritt E ohne M ueber den Knotengraphen aus."""
    eff = []
    ok = True
    mhalt = False                 # M hat nur die Stellungen "gedrueckt" und "losgelassen"; Token M = M+ und sofort M-
    e_unter_m = 0                 # Anzahl E-Schritte waehrend des aktuellen Haltens von M
    or_basis = m.OR               # OR ohne den Beitrag von M (M verknuepft disjunktiv mit 025)
    sw_gedrueckt = False
    toks = list(tokens)

    def or_neu():
        m.OR = or_basis | (0o025 if mhalt else 0)

    for t in toks:
        u = t.upper().replace('\u00dc', 'UE')
        if u == 'H':
            m.fl['H'] = 1
            eff.append('H  : Schalter H-R -> "H", Flag H := 1')
        elif u == 'G':
            for k in m.fl:
                if k not in ('H', 'T', 'BS', 'SP'):     # BS, SP: eingerastete Schalter, G kann sie mechanisch nicht loesen
                    m.fl[k] = 0
            m.fl['T'], m.fl['SW'] = (0, 1) if sw_gedrueckt else (1, 0)
            m.AR = 0
            m.adr = 0
            or_basis = 0
            or_neu()
            m.BZ = 0
            m.br_aufgestellt = False
            m.vor_phase2 = False
            m.fl['US'] = 1                # Rechner steht nach G im Halt-Zustand: US := 1 (loescht ST oder R)
            eff.append('G  : alle Flags ausser H,T,BS,SP := 0 (BS, SP: eingerastete Schalter); BR := 0000 000 (AR:=0000, OR:=000); US := 1; K0 angewaehlt, '
                       + ('SW gedrueckt -> SW := 1' if sw_gedrueckt else 'SW nicht gedrueckt -> T := 1')
                       + '; <BZ> := 0 (vorweggenommene Wirkung des Sprungs nach 0000)')
        elif u.startswith('SW') and (u.find('DRUECK') >= 0 or u in ('SW=1', 'SW+')):
            sw_gedrueckt = True
            m.fl['SW'], m.fl['T'] = 1, 0
            eff.append('SW gedrueckt: Schalter SW -> Flag SW := 1, T := 0')
        elif u.startswith('SW') and ('LOS' in u or u in ('SW=0', 'SW-')):
            sw_gedrueckt = False
            m.fl['SW'], m.fl['T'] = 0, 1
            eff.append('SW geloest (Stellung T): Flag SW := 0, T := 1')
        elif u == 'M' or (u.startswith('M') and (any(w in u for w in ('DRUECK', 'HALT')) or u == 'M+')) \
                or (u.startswith('M') and ('LOS' in u or u == 'M-')):
            press = u == 'M' or u == 'M+' or any(w in u for w in ('DRUECK', 'HALT'))
            release = u == 'M' or not press
            if press:
                if mhalt:
                    ok = False
                    eff.append('?? : M gedrueckt, obwohl M bereits gedrueckt ist')
                    continue
                mhalt = True
                e_unter_m = 0
                or_basis = m.OR
                or_neu()
                eff.append('M gedrueckt halten: OR := OR ODER 025 (BR = AR 025)' if u != 'M'
                           else 'M  : (= M gedrueckt, sofort losgelassen) OR := OR ODER 025 -> BR = AR 025')
            if release:
                if not mhalt:
                    ok = False
                    eff.append('?? : M losgelassen, obwohl M nicht gedrueckt ist')
                    continue
                mhalt = False
                if e_unter_m == 0:
                    # kein E unter M: BR = AR 025 bleibt aufgestellt und wird erst durch E oder R ausgefuehrt
                    or_basis |= 0o025
                    m.br_aufgestellt = True
                    or_neu()
                    if u != 'M':
                        eff.append('M loslassen: kein E unter M -> BR = AR 025 bleibt aufgestellt (Ausfuehrung durch E oder R)')
                else:
                    or_neu()
                    eff.append('M loslassen: OR-Verknuepfung mit 025 entfaellt fuer Folgeschritte')
        elif u[:2] in ('BS', 'SP') and len(u) > 2 and (u[2:] in ('=1', '+', '=0', '-') or any(w in u for w in ('DRUECK', 'LOS'))):
            name = u[:2]
            press = u[2:] in ('=1', '+') or 'DRUECK' in u
            m.fl[name] = 1 if press else 0
            eff.append(f'{name} : Schalter {name} ' + ('gedrueckt (eingerastet) -> ' if press else 'geloest -> ') + f'Flag {name} := {m.fl[name]}')
        elif u == 'ST':
            if not (m.fl['US'] or m.fl['BS']):
                eff.append('ST : elektronisch verriegelt, Rechner steht weder im bedingten noch im unbedingten Stopp -> keine Wirkung')
            else:
                or_basis |= 0o240
                or_neu()
                m.fl['US'] = 0
                m.br_aufgestellt = True
                eff.append(f'ST : (US oder BS) OR := OR ODER 240 -> BR = {octs(m.adr,4)} {octs(m.OR,3)}, AR unveraendert; US := 0 (aufgestellt, nicht ausgefuehrt)')
        elif u == 'UE':
            if not m.fl['H']:
                eff.append('Ue : nur bei Schalter H wirksam, H nicht gesetzt -> keine Wirkung')
            else:
                m.AR = 0o7777
                m.adr = 0o7777
                or_basis |= 0o240
                or_neu()
                m.br_aufgestellt = True
                eff.append(f'Ue : AR := 7777; OR := OR ODER 240 -> BR = 7777 {octs(m.OR,3)} (Transport, aufgestellt, nicht ausgefuehrt)')
        elif u == 'E' and mhalt:
            # E unter gehaltenem M (Bedienpult 4.3, Durchfuehrung 4.3, Beispiel B): Phase IV fuehrt "AR 025" aus,
            # danach Phase I; Phase II ist verhindert. Wirkung (Autor): BZ := BZ+1, AR := BZ, und <AC> steht
            # mit BZ+1 im Adressfeld (Beispiel B nach 4xE: <AC> = 0000 0005 000). Loeschbit von 025 -> AC ersetzt.
            m.BZ = (m.BZ + 1) & MASK12
            m.AR = m.BZ
            m.AC = ((m.BZ + 1) & MASK12) << 9
            m.vor_phase2 = True
            e_unter_m += 1
            eff.append(f'E  : (M gehalten) Befehlsentnahme gesperrt, BZ := {octs(m.BZ,4)}, AR := {octs(m.AR,4)}, '
                       f'AC := {octs(m.AC,11)} (BZ+1 im Adressfeld)')
        elif u == 'E':
            if run_e is None:
                ok = False
                eff.append('?? : Einzelschritt E ohne M ist hier nicht ausfuehrbar')
            elif not m.fl['H']:
                eff.append('E  : nur bei Schalter H wirksam, H nicht gesetzt -> keine Wirkung')
            elif m.halted:
                eff.append(f'E  : Automat steht im Stopp ({m.halt_grund}) -> keine weitere Ausfuehrung')
            else:
                eff.append(run_e())
        elif u == 'R':
            if mhalt:
                ok = False
                eff.append('?? : R bei noch gedruecktem M (M muss vorher losgelassen werden)')
            m.fl['H'] = 0
            m.fl['US'] = 0
            eff.append('R  : Schalter H-R -> "R", Flag H := 0, US := 0; Interpretation beginnt bei Konnektor B'
                       + (' bzw. bei Knoten 19, wenn BR aufgestellt ist' if m.br_aufgestellt else ''))
        else:
            ok = False
            eff.append(f'?? : Taste/Schritt {t!r} ist im Regelwerk (Abschnitt 3) nicht definiert')
    if mhalt:
        ok = False
        eff.append('?? : Tastenfolge endet mit gedrueckter Taste M (M muss losgelassen werden)')
    if toks[-1:] and toks[-1].upper() == 'R':
        if m.fl['H'] != 0:
            ok = False
    elif m.fl['H'] != 1:
        ok = False
        eff.append('?? : Tastenfolge endet weder mit R noch im Halt (H) - Ausgangszustand nicht definiert')
    else:
        eff.append('Ende der Tastenfolge ohne R: Rechner bleibt im Halt (H)')
    return ok, eff


# ----------------------------------------------------------------------------------------------
# Lauf durch den Knotengraphen
# ----------------------------------------------------------------------------------------------
def lauf(test, graph, t2, outdir, max_knoten=2_000_000, knotentest=False):
    m = Machine(test.mem)
    for k, key in ((1, 'leser1'), (2, 'leser2')):
        if GERAETE[key]:
            m.leser[k] = Leser(GERAETE[key])
    if GERAETE['stanzer1']:
        m.stanzer = Stanzer(GERAETE['stanzer1'])
    if GERAETE['k0']:
        m.k0 = K0Quelle(GERAETE['k0'])
    stufe = test.stufe
    zeilen = []          # Knotenprotokoll (bei Stufe 1 -> Bildschirm, bei 2 -> Datei)
    diag_screen = []     # Diagnoseausgaben (stets Bildschirm)
    m.log = lambda s: zeilen.append(s)
    kopf = []

    def diag(mm):
        out = []
        for x, text in test.dok:
            if x == mm.adr:
                out.append(f'#DOK-{octs(x,4)} {text}')
        for x, s0, e0 in test.spei:
            if x == mm.adr:
                out.append(f'#SPEI-{octs(x,4)} {octs(s0,4)}-{octs(e0,4)}')
                for a in range(s0, e0 + 1):
                    out.append(f'{octs(a,4)}: {octs(mm.rd(a),11)}')
        for x, aaaa in test.spur:
            if x == mm.adr:
                out.append(f'#SPUR-{octs(x,4)} {octs(aaaa,4)}')
                spur = aaaa & ~0o37
                for log in PHYS_LOG:
                    a = spur | log
                    out.append(f'{octs(a,4)}: {octs(mm.rd(a),11)}')
        if not out:
            return                  # keine Marke passt zur Befehlsadresse: keine Ausgabe
        diag_screen.extend(out)
        zeilen.extend(['--- Diagnose (Befehl 164) ---'] + out + ['--- Ende Diagnose ---'])

    m.diag_hook = diag

    def br_zeile(vor):
        f = m.fl
        zeilen.append(f'  BR={octs(m.adr,4)} {octs(m.OR,3)}  (vor Knoten {vor:03d})  '
                      f'BZ={octs(m.BZ,4)} AC={octs(m.AC,11)} F\u00dc={f["FUE"]} '
                      f'V1={f["V1"]} V2={f["V2"]} V3={f["V1"] & f["V2"]}')

    def exec_node(node):
        """Fuehrt genau einen Knoten aus und liefert den Folgeknoten (None: kein Ausgang)."""
        n = graph[node]
        typ = n['typ']
        zusatz = ''
        br_nach = None
        if node == 2:
            br_zeile(2)             # Befehlsregister vor Knoten 2 (Beginn Phase I)
        try:
            if typ == 'Konnektor':
                bez = n['text']
                ziel = n['out']
                if ziel is None:
                    for k, o in graph.items():
                        if o['typ'] == 'Konnektor' and o['text'] == bez and o['out'] is not None and k != node:
                            ziel = o['out']
                            if k == 7:
                                br_nach = 7
                            break
                text = f'KON {bez}'
                nxt = ziel
            elif typ == 'Phasenzuordnung':
                text = 'PHA ' + n['text'].replace('Beginn ', '')
                if 'Phase IV' in n['text']:
                    m.zaehler = 0
                    m.start_sek = sektor(m.AR)
                nxt = n['out']
            elif typ == 'Anweisung':
                f = FUNCS.get(n['anw'])
                if f is None:
                    raise Stub(f'ANWEISUNG-{n["anw"]:03d} unbekannt')
                f(m)
                text = f'ANW {n["anw"]:03d}'
                nxt = n['out']
            elif typ == 'Test':
                f = FUNCS.get(n['anw'])
                if f is None:
                    raise Stub(f'ANWEISUNG-{n["anw"]:03d} unbekannt')
                r = f(m)
                text = f'TST {n["anw"]:03d}'
                zusatz = ' -> wahr' if r else ' -> falsch'
                nxt = n['wahr'] if r else n['falsch']
            else:
                raise Stub(f'Knotentyp {typ!r} unbekannt')
        except KonfigFehler as e:
            fe = f'Geraet nicht nutzbar (Knoten {node}): {e}'
            zeilen.append(f'K{node:03d} {fe}')
            raise LaufFehler(fe)
        except Stub as e:
            fe = f'STUB bei Knoten {node}: {e}'
            zeilen.append(f'K{node:03d} {fe}')
            raise LaufFehler(fe)
        if knotentest:
            # nur mit --knotentest: Zeilen der getesteten Knoten (Kxxx KON/PHA/ANW/TST ...)
            zeilen.append(f'K{node:03d} {text} BZ={octs(m.BZ,4)} AR={octs(m.AR,4)} AC={octs(m.AC,11)}{zusatz}')
        if br_nach:
            # Konnektor-Sprung zu Knoten 7 (Konnektor 1): Knoten 7 wird uebersprungen, die BR-Zeile steht
            # unmittelbar nach der Konnektorzeile, also direkt vor Knoten 7 (bzw. dessen Nachfolger 6).
            br_zeile(br_nach)
        if n.get('end'):
            return None
        return nxt

    def run_e():
        """Taste E (ohne M): ab Knoten 19 (BR aufgestellt) Phase IV, I, II, III, Halt vor erneutem Eintritt in Knoten 19 (HP3)."""
        node = 8 if m.vor_phase2 else 19       # nach E unter M steht der Automat vor Phase II
        m.vor_phase2 = False
        schritt = 0
        while True:
            schritt += 1
            if schritt > max_knoten:
                raise LaufFehler('Abbruch: Knotenlimit im Einzelschritt E erreicht')
            if node == 19 and schritt > 1:
                break
            nxt = exec_node(node)
            if m.halted:
                return f'E  : Einzelschritt endet im Stopp: {m.halt_grund}'
            if nxt is None:
                raise LaufFehler(f'Knoten {node} hat keinen Ausgang')
            m.came_from = node
            node = nxt
        m.br_aufgestellt = True
        return (f'E  : Einzelschritt (Phase IV, I, II, III), Halt vor Knoten 019; '
                f'BR={octs(m.adr,4)} {octs(m.OR,3)} BZ={octs(m.BZ,4)} AR={octs(m.AR,4)} AC={octs(m.AC,11)}')

    try:
        ok, eff = tastenfolge(m, test.tasten, run_e)
    except LaufFehler as e:
        return dict(ok=False, grund=str(e), kopf=kopf, zeilen=zeilen, diag=diag_screen, m=m)

    kopf.append(f'Test {test.name}')
    kopf.append('')
    kopf.append('== 1. Ausgangsbedingungen ==')
    kopf.append('Trommeldatei (uebernommen, Ausschnitt; nicht genannte Zellen = 0):')
    kopf += ['  ' + z for z in test.zeilen]
    for x, text in test.dok:
        kopf.append(f'  #DOK-{octs(x,4)} {text}')
    for x, s0, e0 in test.spei:
        kopf.append(f'  #SPEI-{octs(x,4)} {octs(s0,4)}-{octs(e0,4)}')
    for x, aaaa in test.spur:
        kopf.append(f'  #SPUR-{octs(x,4)} {octs(aaaa,4)}')
    kopf.append(f'  #PROT STUFE={stufe}')
    kopf.append('Tastenfolge: ' + ' '.join(test.tasten))
    kopf += ['  ' + e for e in eff]
    kopf.append('  Nicht spezifizierte Register (AC, ...) starten mit 0.')
    if not ok:
        return dict(ok=False, grund='Tastenfolge nicht gueltig/definiert', kopf=kopf, zeilen=[], diag=[], m=m)

    if m.halted or m.fl['H']:
        # Tastenfolge endet im Halt (ohne R) oder der Einzelschritt endete im Stopp: der Automat laeuft nicht weiter
        grund = m.halt_grund if m.halted else 'Halt (Schalter H): Tastenfolge endet ohne R'
        return dict(ok=True, grund=grund, kopf=kopf, zeilen=zeilen, diag=diag_screen, m=m, knoten=0)

    node = 19 if m.br_aufgestellt else 1
    zaehl = 0
    fehler = None
    while not m.halted:
        zaehl += 1
        if zaehl > max_knoten:
            fehler = 'Abbruch: Knotenlimit erreicht (Endlosschleife?)'
            break
        try:
            nxt = exec_node(node)
        except LaufFehler as e:
            fehler = str(e)
            break
        if m.halted:
            break
        if nxt is None:
            fehler = f'Knoten {node} hat keinen Ausgang'
            break
        m.came_from = node
        node = nxt

    return dict(ok=fehler is None, grund=fehler or m.halt_grund, kopf=kopf, zeilen=zeilen,
                diag=diag_screen, m=m, knoten=zaehl)


def flags_text(m):
    return ' '.join(f'{k}={m.fl[k]}' for k in ('FE', 'FUE', 'BS', 'US', 'E', 'A', 'V1', 'V2'))


# ----------------------------------------------------------------------------------------------
# Ergebnispruefung (Abschnitt 3a der Testbeschreibung): optionaler Abschnitt "Pruefungen:"
# ----------------------------------------------------------------------------------------------
def pruefe_ergebnis(test, m):
    """Liefert None, wenn keine Pruefungen-Sektion vorhanden ist, sonst (wahr, zeilen)."""
    if not test.pruef_reg and not test.pruef_mem:
        return None
    wahr = True
    zeilen = []
    for key, soll in test.pruef_reg.items():
        if key == 'BZ':
            ist, breite = m.BZ, 4
        elif key == 'AC':
            ist, breite = m.AC, 11
        elif key == 'AR':
            ist, breite = m.AR, 4
        else:
            ist, breite = m.fl[key], 1
        gut = (ist == soll)
        wahr = wahr and gut
        zeilen.append(f'  {key}: soll={octs(soll, breite)} ist={octs(ist, breite)} '
                      f'{"OK" if gut else "FEHLER"}')
    for a in sorted(test.pruef_mem):
        soll = test.pruef_mem[a]
        ist = m.rd(a)
        gut = (ist == soll)
        wahr = wahr and gut
        zeilen.append(f'  {octs(a,4)}: soll={octs(soll,11)} ist={octs(ist,11)} {"OK" if gut else "FEHLER"}')
    return wahr, zeilen


def finde_testdatei(pfad, here):
    """Testdatei wie angegeben; sonst nur ueber den Dateinamen unterhalb des aktuellen Verzeichnisses
    und des Skript-Verzeichnisses suchen (Gross-/Kleinschreibung und Unicode-Form egal)."""
    import unicodedata
    if os.path.isfile(pfad):
        return pfad
    def norm(s):
        return unicodedata.normalize('NFC', s).casefold()
    ziel = norm(os.path.basename(pfad))
    treffer = []
    for wurzel in dict.fromkeys([os.getcwd(), here]):
        for d, dirs, files in os.walk(wurzel):
            dirs[:] = [x for x in dirs if not x.startswith('.') and x not in ('Protokolle', 'ergebnis')]
            for fn in files:
                if norm(fn) == ziel:
                    q = os.path.join(d, fn)
                    if q not in treffer:
                        treffer.append(q)
    if not treffer:
        return None
    return treffer[0] if len(treffer) == 1 else treffer


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('tests', nargs='+')
    ap.add_argument('--graph', default=os.path.join(here, 'C8205-Interpreter-Eingänge_der_Knoten.md'))
    ap.add_argument('--t2', default=os.path.join(here, 'C8205-Interpreter-Beschreibung_der_Knoten.md'))
    ap.add_argument('--leser1', '--lochbandleser1', metavar='PFAD', help='Lochstreifen fuer Leser 1 (Kanal K1): Datei oder Verzeichnis')
    ap.add_argument('--leser2', '--lochbandleser2', metavar='PFAD', help='Lochstreifen fuer Leser 2 (Kanal K2): Datei oder Verzeichnis')
    ap.add_argument('--stanzer1', '--lochbandstanzer1', metavar='PFAD', help='Ausgabedatei des Stanzers 1 (Kanal K1)')
    ap.add_argument('--k0', metavar='QUELLE', help="K0-Eingabe: 'tastatur' oder 'datei=PFAD' "
                    "(Textdatei, ein Zeichen oder Name wie ZR/WM/IS/IB/TAB/WRZL je Zeile)")
    ap.add_argument('--out', default=os.path.join(here, 'ergebnis'))
    ap.add_argument('--knotentest', action='store_true', default=False,
                    help='Knotenzeilen (Kxxx ...) ins Protokoll aufnehmen; Standard: aus (BR-Zeilen, Diagnose '
                    'und Fehlermeldungen bleiben immer erhalten)')
    args = ap.parse_args()
    GERAETE.update(leser1=args.leser1, leser2=args.leser2, stanzer1=args.stanzer1, k0=args.k0)
    if args.k0 and not (args.k0 == 'tastatur' or args.k0.startswith('datei=')):
        ap.error("--k0: 'tastatur' oder 'datei=PFAD' erwartet")

    out_ist_datei = bool(os.path.splitext(args.out)[1])
    if out_ist_datei and len(args.tests) > 1:
        ap.error('--out mit Dateiendung (' + args.out + ') ist nur mit genau einer Testdatei zulaessig')

    graph = load_graph(args.graph)
    t2 = load_t2(args.t2)
    fehlend = sorted({n['anw'] for n in graph.values() if n['anw'] and n['anw'] not in t2})
    if fehlend:
        print('WARNUNG: im Graph referenzierte ANWEISUNG-Nummern fehlen in T2:', fehlend)
    nichtimpl = sorted(n for n in {x['anw'] for x in graph.values() if x['anw']} if n not in FUNCS)
    if nichtimpl:
        print('WARNUNG: nicht implementierte ANWEISUNG-Nummern:', nichtimpl)

    for pfad in args.tests:
        gefunden = finde_testdatei(pfad, here)
        if isinstance(gefunden, list):
            print(f'\nFEHLER: Testdatei {pfad!r} nicht eindeutig gefunden:')
            for g in gefunden:
                print('  -', g)
            continue
        if gefunden is None:
            print(f'\nFEHLER: Testdatei nicht gefunden: {pfad!r} (aktuelles Verzeichnis: {os.getcwd()})')
            continue
        if gefunden != pfad:
            print(f'Testdatei: {gefunden}')
        pfad = gefunden
        t = Test(pfad)
        print(f'\n=== Test {t.name} (#PROT STUFE={t.stufe}) ===')
        for h in t.hinweise:
            print(h)
        if t.fehler:
            print('FORMALE PRUEFUNG NEGATIV - Test startet nicht, Klaerung erforderlich:')
            for f in t.fehler:
                print('  -', f)
            continue
        r = lauf(t, graph, t2, args.out, knotentest=args.knotentest)
        m = r['m']
        if not m.sw_zeilenanfang:
            print()
        if not r['ok']:
            print('TEST NICHT ORDNUNGSGEMAESS BEENDET:', r['grund'])
        if t.stufe == 1:
            print('-- Knotenzustaende --')
            for z in r['zeilen']:
                print(z)
        if r['diag'] and t.stufe != 1:
            print('-- Diagnose --')
            for z in r['diag']:
                print(z)
        print(f'Ende: {r["grund"]} | Knoten: {r.get("knoten", 0)} | BZ={octs(m.BZ,4)} AC={octs(m.AC,11)} '
              f'AR={octs(m.AR,4)} | {flags_text(m)}')

        # Abschnitt 3a: Ergebnispruefung (falls im Test angegeben) - stets auf dem Bildschirm,
        # unabhaengig von #PROT STUFE, analog zur #DOK-Diagnose (Abschnitt 7)
        pruef = pruefe_ergebnis(t, m)
        pruef_ausgabe = []
        if pruef is not None:
            if not r['ok']:
                pruef_ausgabe = ['Ergebnispruefung: nicht durchgefuehrt '
                                 '(Test nicht ordnungsgemaess beendet)']
            else:
                wahr, pzeilen = pruef
                pruef_ausgabe = ['Ergebnispruefung:'] + pzeilen + [f'Test {"wahr" if wahr else "falsch"}']
            for z in pruef_ausgabe:
                print(z)

        if t.stufe == 2:
            if out_ist_datei:
                p = args.out
                os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
            else:
                d = os.path.join(args.out, t.name)
                os.makedirs(d, exist_ok=True)
                p = os.path.join(d, 'protokoll.txt')
            with open(p, 'w', encoding='utf-8') as fh:
                fh.write('\n'.join(r['kopf']) + '\n\n== 2. Zustaende des Knotenautomaten ==\n')
                fh.write('\n'.join(r['zeilen']) + '\n\n')
                fh.write(f'== Ende ==\n{r["grund"]}\nBZ={octs(m.BZ,4)} AC={octs(m.AC,11)} AR={octs(m.AR,4)} '
                         f'{flags_text(m)}\n')
                if pruef_ausgabe:
                    fh.write('\n== 3. Ergebnispruefung ==\n' + '\n'.join(pruef_ausgabe) + '\n')
            print('Protokolldatei:', p)
        elif out_ist_datei:
            print(f'Hinweis: keine Protokolldatei {args.out}, da #PROT STUFE={t.stufe} '
                  f'(Datei entsteht nur bei #PROT STUFE=2).')


if __name__ == '__main__':
    main()
