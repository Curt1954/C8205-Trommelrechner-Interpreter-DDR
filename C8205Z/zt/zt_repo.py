# -*- coding: utf-8 -*-
"""
zt_repo.py - Python-Hilfsprogramm zum Schreiben und Pruefen des ZT-Repository-Formats (C 8205Z).

Version: 0.01-002 (Neufassung nach ZT-Repository_Aufgabenstellung.md 0.01-006; die Fassung 0.01-001 ging verloren)
Python 3.11, nur Standardbibliothek. Kein Teil des Simulators; Gegenprobe fuer ZTC, ZTL, ZTD und ihre Tests.

Aufruf (von ueberall):  python3 C8205Z/zt/zt_repo.py VERZ format T | anlegen T | liste | add NAME OBJ | del NAME | pruefen | belegung
  VERZ = Ordner mit zt1.txt .. zt4.txt (Zeilen "aaaa: ttttttttttt", 4096 je Datei; fehlende Dateien gelten als leer),
  T = Trommel 0 bis 3 (ZT1 bis ZT4). Alle Aenderungen sind alles-oder-nichts (Zustand vor dem Fehler bleibt erhalten).

Bausteine: ZtSatz (die vier Trommeln im Speicher, laden/speichern, Belegungsliste), Archiv (Formatieren, Anker, Namensbloecke,
Segmente, add/del/holen/pruefen), obj_lesen (.obj als Lochstreifen oder Text -> Worte und Kennzeichen), ZEICHEN_LOCH.
"""
import copy
import os
import sys

WORT = (1 << 33) - 1
SPUREN = 128
ZELLEN = 32
GROESSE = SPUREN * ZELLEN
LISTENKENNUNG = 0o25147361025
REPOSITORY_KENNUNG = 0o61350247316
BLOCKKENNUNG = 0o34716052613
FORMATVERSION = 1
SEGMENT_SPUREN = 16
WORTE_JE_SPUR = 25
WORTE_JE_SEGMENT = SEGMENT_SPUREN * WORTE_JE_SPUR     # 400 dezimal
GRUPPEN = (0, 6, 12, 18, 24)                          # Anfangszellen der fuenf Gruppen (dezimal)
NN_VORGABE = 0o100

# Lochbild (Spuren w v u p 8 4 2 1) der Zeichen einer .obj, Kodetabelle 1 (Ausgabe-Adresse)
ZEICHEN_LOCH = {'0': 0o20, '1': 0o01, '2': 0o02, '3': 0o23, '4': 0o04, '5': 0o25, '6': 0o26, '7': 0o07, '8': 0o10, '9': 0o31,
                '.': 0o73, '/': 0o141}
LOCH_ZEICHEN = {v: k for k, v in ZEICHEN_LOCH.items()}

# Eingabeadresse (Tabelle 1, Spalte "Eingabe Adresse") der Zeichen eines Namens; Leerzeichen/ZR = 12
TABELLE1 = {'0': 0o00, '1': 0o01, '2': 0o02, '3': 0o03, '4': 0o04, '5': 0o05, '6': 0o06, '7': 0o07, '8': 0o10, '9': 0o11,
            ' ': 0o12,
            'A': 0o21, 'B': 0o22, 'C': 0o23, 'D': 0o24, 'E': 0o25, 'F': 0o26, 'G': 0o27, 'H': 0o30, 'I': 0o31,
            'J': 0o41, 'K': 0o42, 'L': 0o43, 'M': 0o44, 'N': 0o45, 'O': 0o46, 'P': 0o47, 'Q': 0o50, 'R': 0o51,
            'S': 0o62, 'T': 0o63, 'U': 0o64, 'V': 0o65, 'W': 0o66, 'X': 0o67, 'Y': 0o70, 'Z': 0o71}
ADRESSE_ZEICHEN = {v: k for k, v in TABELLE1.items()}

STATUS_TEXT = {1: 'TROMMEL NICHT FORMATIERT', 2: 'KEIN REPOSITORY', 3: 'FORMATVERSION FREMD', 4: 'NAME UNBEKANNT',
               5: 'PLATZ REICHT NICHT', 6: 'TROMMELN VOLL', 7: 'KENNZEICHEN UNZULAESSIG', 0o10: 'NAME VORHANDEN'}   # Statusnummern oktal (Format 11.3)


class ZtFehler(Exception):
    """Fehler mit Statusnummer (Format Abschnitt 11.3)."""
    def __init__(self, status, text=''):
        self.status = status
        super().__init__(f'Status {status:o}: {STATUS_TEXT.get(status, "")} {text}'.strip())


def lagewort(t, spur):
    return t * 0o200 + spur


def lage_zerlegen(lw):
    return lw >> 7, lw & 0o177


def name_worte(name):
    """Name (bis 10 Zeichen, Gross = Klein, Buchstaben, Ziffern, Leerzeichen) -> zwei Worte (Format Abschnitt 6)."""
    n = name.upper()
    if len(n) > 10 or not n or any(c not in TABELLE1 for c in n):
        raise ValueError(f'Name unzulaessig: {name!r}')
    n = n.ljust(10)
    w = [0, 0]
    for i, c in enumerate(n):
        w[i // 5] |= TABELLE1[c] << (27 - 6 * (i % 5))
    return w


def worte_name(w0, w1):
    s = ''
    for w in (w0, w1):
        for i in range(5):
            s += ADRESSE_ZEICHEN.get((w >> (27 - 6 * i)) & 0o77, '?')
    return s.rstrip()


class Eintrag:
    def __init__(self, block, index, name, laenge, lage):
        self.block, self.index, self.name, self.laenge, self.lage = block, index, name, laenge, lage

    def __repr__(self):
        return f'Eintrag({self.name!r}, L={self.laenge:o}, Lage={self.lage:o})'


class ZtSatz:
    """Die vier Zusatztrommeln im Speicher: mem[t][adresse], t = 0..3 (ZT1..ZT4)."""

    def __init__(self, verz):
        self.verz = verz
        os.makedirs(verz, exist_ok=True)
        self.mem = [self._laden(t) for t in range(4)]

    def pfad(self, t):
        return os.path.join(self.verz, f'zt{t + 1}.txt')

    def _laden(self, t):
        m = [0] * GROESSE
        p = self.pfad(t)
        if os.path.isfile(p):
            with open(p, encoding='ascii') as f:
                for ln in f:
                    ln = ln.strip()
                    if len(ln) >= 6 and ln[4] == ':':
                        a = int(ln[:4], 8)
                        if a < GROESSE:
                            m[a] = int(ln[5:].split()[0], 8) & WORT
        return m

    def speichern(self):
        """Atomar: erst in .tmp schreiben, dann ersetzen."""
        for t in range(4):
            p = self.pfad(t)
            with open(p + '.tmp', 'w', encoding='ascii') as f:
                f.write(''.join(f'{a:04o}: {w & WORT:011o}\n' for a, w in enumerate(self.mem[t])))
            os.replace(p + '.tmp', p)

    # --- Belegungsliste (Spur 0, Zellen 0 bis 3; Spur s: Wort s >> 5, Bit z(s und 37), z0 = Bit 32)
    def belegt(self, t, s):
        return bool((self.mem[t][s >> 5] >> (32 - (s & 31))) & 1)

    def setze_belegt(self, t, s, wert=True):
        b = 1 << (32 - (s & 31))
        if wert:
            self.mem[t][s >> 5] |= b
        else:
            self.mem[t][s >> 5] &= ~b

    def formatiert(self, t):
        return self.mem[t][4] == LISTENKENNUNG

    def luecke(self, t, n):
        """Erste Folge von n freien Spuren auf Trommel t (aufwaerts), oder None."""
        lauf = 0
        for s in range(SPUREN):
            lauf = 0 if self.belegt(t, s) else lauf + 1
            if lauf == n:
                return s - n + 1
        return None

    def suche(self, n):
        """Luecke ueber ZT1..ZT4 (nicht formatierte Trommeln werden uebergangen): (t, spur) oder ZtFehler 6."""
        for t in range(4):
            if self.formatiert(t):
                s = self.luecke(t, n)
                if s is not None:
                    return t, s
        raise ZtFehler(6)

    def belege(self, t, s, n, wert=True):
        for i in range(n):
            self.setze_belegt(t, s + i, wert)

    def spur_lesen(self, t, s):
        return self.mem[t][s * ZELLEN:(s + 1) * ZELLEN]

    def wort(self, t, spur, i):
        """Wort i eines Rohdatenbereichs, der in Spur 'spur' beginnt."""
        return self.mem[t][(spur + (i >> 5)) * ZELLEN + (i & 31)]

    def setze_wort(self, t, spur, i, w):
        self.mem[t][(spur + (i >> 5)) * ZELLEN + (i & 31)] = w & WORT


def spuren_block(nn):
    return (4 * nn + 4 + ZELLEN - 1) // ZELLEN


class Archiv:
    """Repository auf einem ZtSatz. Aenderungen sind alles-oder-nichts (Rueckfall auf den Zustand vor dem Aufruf)."""

    def __init__(self, zt):
        self.zt = zt

    def _transaktion(f):
        def umhuellt(self, *a, **k):
            vorher = copy.deepcopy(self.zt.mem)
            try:
                return f(self, *a, **k)
            except Exception:
                self.zt.mem = vorher
                raise
        umhuellt.__name__ = f.__name__
        return umhuellt

    # --- Formatieren, Anker
    @_transaktion
    def formatieren(self, t):
        m = self.zt.mem[t]
        for i in range(ZELLEN):
            m[i] = 0
        m[0] = 0o40000000000
        m[4] = LISTENKENNUNG

    def anker(self):
        """(t, spur_erster_block) der ersten Trommel mit Anker, oder None; mehrere Anker zaehlt pruefen()."""
        for t in range(4):
            m = self.zt.mem[t]
            if m[4] == LISTENKENNUNG and m[5] == REPOSITORY_KENNUNG:
                return t, m[7]
        return None

    @_transaktion
    def anlegen(self, t, nn=NN_VORGABE):
        """Repository mit leerem erstem Namensblock auf Trommel t (muss formatiert sein) anlegen; liefert (t, spur)."""
        if not self.zt.formatiert(t):
            raise ZtFehler(1, f'ZT{t + 1}')
        if self.anker() is not None:
            raise ZtFehler(2, 'Repository existiert schon')
        s = self.zt.luecke(t, spuren_block(nn))
        if s is None or s == 0:
            raise ZtFehler(6)
        self._neuer_block(t, s, nn)
        m = self.zt.mem[t]
        m[5], m[6], m[7] = REPOSITORY_KENNUNG, FORMATVERSION, s
        return t, s

    def _neuer_block(self, t, s, nn):
        n = spuren_block(nn)
        self.zt.belege(t, s, n)
        for i in range(n * ZELLEN):
            self.zt.mem[t][s * ZELLEN + i] = 0
        self.zt.setze_wort(t, s, 0, BLOCKKENNUNG)
        self.zt.setze_wort(t, s, 2, nn)

    # --- Namensbloecke
    def bloecke(self):
        """Liste der Bloecke [(t, spur, nn)] in Kettenreihenfolge (Fehler: ZtFehler 2)."""
        a = self.anker()
        if a is None:
            raise ZtFehler(2)
        t, s = a
        aus, gesehen = [], set()
        while True:
            if (t, s) in gesehen or s == 0 or s >= SPUREN or self.zt.wort(t, s, 0) != BLOCKKENNUNG:
                raise ZtFehler(2, 'Blockkette beschaedigt')
            gesehen.add((t, s))
            aus.append((t, s, self.zt.wort(t, s, 2)))
            folge = self.zt.wort(t, s, 1)
            if folge == 0:
                return aus
            t, s = lage_zerlegen(folge)

    def eintraege(self):
        """Alle belegten Eintraege (Lagewort ungleich 0), in Verzeichnisreihenfolge."""
        aus = []
        for (t, s, nn) in self.bloecke():
            for j in range(nn):
                b = 4 + 4 * j
                lage = self.zt.wort(t, s, b + 3)
                if lage:
                    aus.append(Eintrag((t, s, nn), j, worte_name(self.zt.wort(t, s, b), self.zt.wort(t, s, b + 1)),
                                       self.zt.wort(t, s, b + 2), lage))
        return aus

    def _find(self, name):
        n = worte_name(*name_worte(name))
        for e in self.eintraege():
            if e.name == n:
                return e
        return None

    # --- Segmente
    def _segmente_schreiben(self, worte, kz):
        """Belegt Segmente und schreibt das Programm in Gruppenform; liefert die Liste [(t, spur)]."""
        n = len(worte)
        anzahl = max(1, (n + WORTE_JE_SEGMENT - 1) // WORTE_JE_SEGMENT)
        lagen = []
        for _ in range(anzahl):
            t, s = self.zt.suche(SEGMENT_SPUREN)
            self.zt.belege(t, s, SEGMENT_SPUREN)
            for i in range(SEGMENT_SPUREN * ZELLEN):
                self.zt.mem[t][s * ZELLEN + i] = 0
            lagen.append((t, s))
        for si, (t, s) in enumerate(lagen):
            teil = worte[si * WORTE_JE_SEGMENT:(si + 1) * WORTE_JE_SEGMENT]
            tk = kz[si * WORTE_JE_SEGMENT:(si + 1) * WORTE_JE_SEGMENT]
            for sp in range(SEGMENT_SPUREN):
                basis = (s + sp) * ZELLEN
                for g, z0 in enumerate(GRUPPEN):
                    kennung = 0
                    for i in range(5):
                        idx = sp * WORTE_JE_SPUR + g * 5 + i
                        if idx < len(teil):
                            k1, k2 = tk[idx]
                            kennung |= ((k1 << 4) | k2) << (27 - 6 * i)
                            self.zt.mem[t][basis + z0 + 1 + i] = teil[idx] & WORT
                    self.zt.mem[t][basis + z0] = kennung
            if si + 1 < anzahl:
                nt, ns = lagen[si + 1]
                self.zt.mem[t][(s + SEGMENT_SPUREN - 1) * ZELLEN + 30] = lagewort(nt, ns)
        return lagen

    def segmentkette(self, lage, laenge):
        """Liest ein Programm: (worte, kz); beschaedigte Kette -> ZtFehler 2."""
        worte, kz, gesehen = [], [], set()
        t, s = lage_zerlegen(lage)
        while len(worte) < laenge:
            if (t, s) in gesehen or s == 0 or s + SEGMENT_SPUREN > SPUREN:
                raise ZtFehler(2, 'Segmentkette beschaedigt')
            gesehen.add((t, s))
            for sp in range(SEGMENT_SPUREN):
                basis = (s + sp) * ZELLEN
                for g, z0 in enumerate(GRUPPEN):
                    kennung = self.zt.mem[t][basis + z0]
                    for i in range(5):
                        if len(worte) < laenge:
                            k = (kennung >> (27 - 6 * i)) & 0o77
                            worte.append(self.zt.mem[t][basis + z0 + 1 + i])
                            kz.append((k >> 4, k & 15))
            folge = self.zt.mem[t][(s + SEGMENT_SPUREN - 1) * ZELLEN + 30]
            if len(worte) < laenge:
                if folge == 0:
                    raise ZtFehler(2, 'Segmentkette zu kurz')
                t, s = lage_zerlegen(folge)
        return worte, kz

    def _segmente_frei(self, lage, laenge):
        t, s = lage_zerlegen(lage)
        gesehen = set()
        while lage and (t, s) not in gesehen and s:
            gesehen.add((t, s))
            self.zt.belege(t, s, SEGMENT_SPUREN, False)
            folge = self.zt.mem[t][(s + SEGMENT_SPUREN - 1) * ZELLEN + 30]
            if folge == 0:
                break
            t, s = lage_zerlegen(folge)

    # --- Programme
    @_transaktion
    def programm_hinzufuegen(self, name, worte, kz):
        """a(dd): liefert die Liste der Segmentlagen [(t, spur)]. Status 7 bei K1 ungleich 0 oder K2 ueber 9, 10 (oktal) bei vorhandenem Namen."""
        if len(worte) != len(kz):
            raise ValueError('Worte und Kennzeichen ungleich lang')
        if any(k1 != 0 or k2 > 9 for (k1, k2) in kz):
            raise ZtFehler(7)
        nw = name_worte(name)
        if self._find(name) is not None:
            raise ZtFehler(0o10)
        bl = self.bloecke()
        platz = None
        for (t, s, nn) in bl:
            for j in range(nn):
                if self.zt.wort(t, s, 4 + 4 * j + 3) == 0:
                    platz = (t, s, nn, j)
                    break
            if platz:
                break
        if platz is None:                                 # neuer Namensblock mit der Groesse des letzten
            lt, ls, nn = bl[-1]
            t, s = self.zt.suche(spuren_block(nn))
            self._neuer_block(t, s, nn)
            self.zt.setze_wort(lt, ls, 1, lagewort(t, s))
            platz = (t, s, nn, 0)
        lagen = self._segmente_schreiben(worte, kz)
        t, s, nn, j = platz
        b = 4 + 4 * j
        self.zt.setze_wort(t, s, b, nw[0])
        self.zt.setze_wort(t, s, b + 1, nw[1])
        self.zt.setze_wort(t, s, b + 2, len(worte))
        self.zt.setze_wort(t, s, b + 3, lagewort(*lagen[0]))
        self.zt.setze_wort(t, s, 3, self.zt.wort(t, s, 3) + 1)
        return lagen

    @_transaktion
    def loeschen(self, name):
        """d(el): Lagewort := 0, Belegungsbits der Segmente frei, belegt - 1; Name und Laenge bleiben stehen."""
        e = self._find(name)
        if e is None:
            raise ZtFehler(4)
        t, s, nn = e.block
        self._segmente_frei(e.lage, e.laenge)
        self.zt.setze_wort(t, s, 4 + 4 * e.index + 3, 0)
        self.zt.setze_wort(t, s, 3, self.zt.wort(t, s, 3) - 1)

    def holen(self, name):
        e = self._find(name)
        if e is None:
            raise ZtFehler(4)
        return self.segmentkette(e.lage, e.laenge)

    # --- Pruefen: (fehler, hinweise)
    def pruefen(self):
        fehler, hinweise = [], []
        anker = [t for t in range(4) if self.zt.mem[t][4] == LISTENKENNUNG and self.zt.mem[t][5] == REPOSITORY_KENNUNG]
        if len(anker) != 1:
            fehler.append(f'{len(anker)} Anker (erwartet 1)')
            return fehler, hinweise
        if self.zt.mem[anker[0]][6] != FORMATVERSION:
            fehler.append('Formatversion fremd')
        for t in range(4):
            if self.zt.formatiert(t) and not self.zt.belegt(t, 0):
                fehler.append(f'ZT{t + 1}: Bit fuer Spur 0 nicht gesetzt')
        erwartet = {(t, s) for t in range(4) for s in range(SPUREN) if s == 0 and self.zt.formatiert(t)}
        try:
            for (t, s, nn) in self.bloecke():
                erwartet |= {(t, s + i) for i in range(spuren_block(nn))}
            for e in self.eintraege():
                t, s = lage_zerlegen(e.lage)
                seen = set()
                while (t, s) not in seen and s:
                    seen.add((t, s))
                    erwartet |= {(t, s + i) for i in range(SEGMENT_SPUREN)}
                    folge = self.zt.mem[t][(s + SEGMENT_SPUREN - 1) * ZELLEN + 30]
                    if not folge:
                        break
                    t, s = lage_zerlegen(folge)
                try:
                    self.segmentkette(e.lage, e.laenge)
                except ZtFehler as x:
                    fehler.append(f'{e.name}: {x}')
        except ZtFehler as x:
            fehler.append(str(x))
        for t in range(4):
            if not self.zt.formatiert(t):
                continue
            for s in range(SPUREN):
                if (t, s) in erwartet and not self.zt.belegt(t, s):
                    fehler.append(f'ZT{t + 1} Spur {s:o}: vom Repository benutzt, aber nicht belegt')
                elif (t, s) not in erwartet and self.zt.belegt(t, s):
                    hinweise.append(f'ZT{t + 1} Spur {s:o}: belegt, gehoert nicht zum Repository (fremd)')
        return fehler, hinweise


def obj_lesen(daten):
    """.obj (bytes oder str) -> (worte, kz). Lochstreifen (Zeilen aus acht Ziffern 0/1) oder Text.
    Wort = K1 K2 Ziffern '.', ein einzelnes '0.' ist das Wort 0, '/' beendet."""
    if isinstance(daten, bytes):
        daten = daten.decode('ascii')
    teile = daten.split()
    if teile and all(len(x) == 8 and set(x) <= {'0', '1'} for x in teile):
        text = ''.join(LOCH_ZEICHEN.get(int(x, 2), '?') for x in teile)
    else:
        text = ''.join(teile)
    worte, kz = [], []
    for w in text.split('.'):
        if w.startswith('/') or w == '':
            break
        ende = '/' in w
        w = w.split('/')[0]
        if len(w) == 1:
            k1, k2, ziffern = int(w), 0, '0'
        else:
            k1, k2, ziffern = int(w[0]), int(w[1]), w[2:] or '0'
        worte.append(int(ziffern, 8) & WORT)
        kz.append((k1, k2))
        if ende:
            break
    return worte, kz


def _hauptprogramm(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    zt = ZtSatz(argv[0])
    a = Archiv(zt)
    cmd, arg = argv[1], argv[2:]
    try:
        if cmd == 'format':
            a.formatieren(int(arg[0]))
        elif cmd == 'anlegen':
            t, sp = a.anlegen(int(arg[0]))
            print(f'Namensblock auf ZT{t + 1}, Spur {sp:o}')
        elif cmd == 'liste':
            for e in a.eintraege():
                t, s = lage_zerlegen(e.lage)
                print(f'{e.name:10s} L={e.laenge:o} ZT{t + 1} Spur {s:o}')
        elif cmd == 'add':
            w, k = obj_lesen(open(arg[1], 'rb').read())
            print(a.programm_hinzufuegen(arg[0], w, k))
        elif cmd == 'del':
            a.loeschen(arg[0])
        elif cmd == 'belegung':
            for t in range(4):
                print(f'ZT{t + 1}: ' + ' '.join(f'{w:011o}' for w in zt.mem[t][:4]))
        elif cmd == 'pruefen':
            f, h = a.pruefen()
            for x in f:
                print('FEHLER', x)
            for x in h:
                print('Hinweis', x)
            return 1 if f else 0
        else:
            print('unbekanntes Kommando', cmd)
            return 2
    except ZtFehler as x:
        print('FEHLER', x)
        return 1
    zt.speichern()
    return 0


if __name__ == '__main__':
    sys.exit(_hauptprogramm(sys.argv[1:]))
