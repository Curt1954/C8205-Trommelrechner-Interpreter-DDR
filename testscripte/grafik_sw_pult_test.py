# -*- coding: utf-8 -*-
"""Pruefung Stufe 3, SW-Eingabe ueber das Bedienpult (Tasten) gemaess Dokumentation (Bedienpult_mit_Schaltern.md, GRAFIK_Beschreibung §4.5):
Netzschalter, Hochlauf, Taste SW (Schalter SW gedrueckt, T geloest), G, R; das Programm sw_zwei_ziffern (Tests/sw_zwei_ziffern.test) liest zwei
Ziffern ueber K0 (Anwahlbefehl) vom SW-Fenster (Logikschicht SwAnzeige + SwEingabe, Tk-Fenster ersetzt).
Regel des Projektinhabers 18.10.2026: Es zaehlt nur die Lage des SW, nie die des Rechners. SW auf KB: nur die Ziffer. SW auf GB: Um. KB, dann die
Ziffer (der Rechner bekommt ZWEI Eingabezeichen, 0,1 s Abstand, jedes nur bei aktivem 011). Seit Checkpoint 37: keine Vormerkung, jedes angenommene
Zeichen wird angezeigt. Aufruf: python3 -I testscripte/grafik_sw_pult_test.py"""
import os, queue, shutil, sys, tempfile, threading, time, unittest
HIER = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HIER); sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
import c8205_interp as I
import c8205_grafik as G
from grafik_trommel import GrafikTrommel
from grafik_pult import PultSteuerung, BETRIEB
from grafik_sw import SwAnzeige, SwEingabe

PULT = os.path.join(PROJ, 'pult')
SOLL = 'Erste Ziffer 0-3:\nErste: 2\n'      # wird unten gegen die Sollausgabe der Testdatei geprueft


def soll():
    with open(os.path.join(PROJ, 'Test-Ergebnisvergleiche', 'sw_zwei_ziffern-sw-ausgabe.txt'), encoding='utf-8') as fh:
        return fh.read()


class PultLauf:
    def __init__(self, rechner_lage='KB', sw_lage='KB', schalter='SW'):
        self.dir = tempfile.mkdtemp(); self.alt = os.getcwd(); os.chdir(self.dir)
        t = I.Test(os.path.join(PROJ, 'Tests', 'sw_zwei_ziffern.test')); assert not t.fehler, t.fehler
        pfad = os.path.join(self.dir, 'trommel.txt')
        shutil.copy(os.path.join(PROJ, 'Trommel', 'trommel.txt'), pfad)
        mem = {}
        with open(pfad, encoding='utf-8', newline='') as fh:
            for z in fh:
                mm = I.TROMMEL_ZEILE_RE.match(z); mem[int(mm.group(1), 8)] = int(mm.group(2), 8)
        mem.update({a & I.MASK12: w & I.MASK33 for a, w in t.mem.items()})
        with open(pfad, 'w', encoding='utf-8', newline='') as fh:
            fh.write(''.join(f'{a:04o}: {mem.get(a, 0):011o}\n' for a in range(4096)))
        self.tr = GrafikTrommel(pfad)
        self.r = G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), self.tr, pult_modus=True)
        self.r.m.zeichenlage = rechner_lage
        self.s = PultSteuerung(PULT, self.r, hochlauf_s=0.01, auslauf_s=0.01, tastenzeit_s=0.0)
        self.q = queue.Queue(); self.teile = []                        # eine Warteschlange fuer Ausgabe ('A') und angenommene Eingabe ('E') wie im Fenster
        self.anzeige, self.sw = SwAnzeige(), SwEingabe(self.r.m.k0, self.r.m, echo=lambda t: self.q.put(('E', t)), abstand=0.1)
        self.sw.lage = sw_lage
        self.r.sw.hoere(lambda t: self.q.put(('A', t)))
        self.geliefert = []                                            # K0-Zeichen, die der Rechner vom SW bekommen hat
        orig = self.r.m.k0.annehmen
        def spion(q, tok, **kw):
            ok = orig(q, tok, **kw)
            if ok and q == 'SW': self.geliefert.append(tok)
            return ok
        self.r.m.k0.annehmen = spion
        self.stop = threading.Event(); self.schalter = schalter
        def lauf():
            try:
                while not self.stop.is_set(): self.r.leerlauf(); self.r.lauf_wenn_gewuenscht(); time.sleep(0.002)
            except G.GrafikAbbruch: pass
        self.s.bei_betrieb = lambda: (self.r.taste('H'), threading.Thread(target=lauf, daemon=True).start())

    def starten(self):
        """Netzschalter, Hochlauf, Taste SW bzw. T, dann G und R (wie in der Dokumentation)."""
        self.s.netz_klick(0.0); self.s.tick(1.0)
        assert self.s.netz == BETRIEB
        if self.schalter == 'SW':                                      # Stellung T ist die Grundstellung (Wippe T/SW)
            assert self.s.klick('SW', 1.0), 'Taste SW nicht annehmbar'
        assert self.s.klick('G', 1.1); assert self.s.klick('R', 1.2)

    def _zeichnen(self):
        try:
            while True:
                quelle, text = self.q.get_nowait(); self.teile.append((quelle, text)); self.anzeige.schreibe(text)
        except queue.Empty:
            pass

    def ausgabe(self):
        self._zeichnen(); return ''.join(t for q, t in self.teile if q == 'A')

    def eingabe_angezeigt(self):
        self._zeichnen(); return ''.join(t for q, t in self.teile if q == 'E')

    def warte(self, bed, sek=5.0):
        t0 = time.time()
        while time.time() - t0 < sek:
            self.sw.liefern()
            self._zeichnen()
            if bed(): return True
            time.sleep(0.005)
        return False

    def tippe(self, z):
        assert self.warte(lambda: self.sw.erwartet()), f'kein Eingabe-Halt fuer {z!r}'
        return self.sw.tippen(z)

    def schliessen(self):
        self.stop.set(); self.r.abbrechen(); self.tr.schliessen(); os.chdir(self.alt); shutil.rmtree(self.dir, ignore_errors=True)


class SwEingabeUeberPult(unittest.TestCase):
    def _beide_ziffern(self, rechner_lage, sw_lage='KB'):
        l = PultLauf(rechner_lage, sw_lage)
        try:
            l.starten()
            self.assertTrue(l.r.sw_gedrueckt)                                  # Taste SW wirkt: Schalter SW gedrueckt, T geloest
            self.assertEqual((l.r.m.fl['SW'], l.r.m.fl['T']), (1, 0))
            self.assertEqual(l.tippe('2'), 'geliefert')
            self.assertEqual(l.tippe('3'), 'geliefert')                        # zweite Eingabe nach Anwahlbefehl K2: weiter vom SW
            self.assertTrue(l.warte(lambda: not l.r.laeuft and l.r.m.halted))
            self.assertEqual(l.geliefert, ['2', '3'])                          # je Ziffer EIN Eingabezeichen, Lage des Rechners ohne Wirkung
            self.assertEqual(l.ausgabe(), soll()); self.assertEqual(l.eingabe_angezeigt(), '23')      # Ausgabe wie Soll, dazu die zwei angenommenen Ziffern
            self.assertEqual(l.r.sw.alles(), soll())
        finally:
            l.schliessen()

    def test_vorzustand_unbestimmt_erste_ziffer_mit_umschaltzeichen(self):
        """G3-008 (18.10.2026): Nach dem Einschalten ist die Lage des SW unbestimmt: vor der ersten Ziffer geht IMMER Um. KB zum Rechner,
        danach die Ziffer; das SW steht dann auf KB. Die Lage des Rechners hat keine Wirkung. Geprueft wird nur, was das Fenster dem Rechner
        sendet: das Programm sw_zwei_ziffern kennt kein Umschaltzeichen und holt danach keine Ziffer mehr (Befund, GRAFIK_Beschreibung §5 (alt: Dok. 09) U-12)."""
        for rechner in ('KB', 'GB'):
            with self.subTest(rechner=rechner):
                l = PultLauf(rechner, None)
                try:
                    self.assertIsNone(l.sw.lage)
                    l.starten()
                    self.assertEqual(l.tippe('2'), 'folgt'); self.assertEqual(l.sw.lage, 'KB')
                    self.assertTrue(l.warte(lambda: l.geliefert[:1] == ['Um. KB']))
                    self.assertEqual(l.geliefert[0], 'Um. KB')                   # das Umschaltzeichen kam zuerst beim Rechner an
                finally:
                    l.schliessen()

    def test_sw_auf_kb_rechner_auf_kb(self):
        self._beide_ziffern('KB')

    def test_sw_auf_kb_rechner_auf_gb_nur_die_ziffer(self):
        self._beide_ziffern('GB')

    def test_sw_auf_gb_zuerst_um_kb_dann_ziffer(self):
        l = PultLauf('KB', 'GB')
        try:
            l.starten()
            self.assertEqual(l.tippe('2'), 'folgt')                            # SW auf GB, Ziffer braucht KB: erst Um. KB, die Ziffer folgt nach 0,1 s
            self.assertTrue(l.warte(lambda: l.geliefert[:1] == ['Um. KB']))
            self.assertEqual(l.sw.lage, 'KB')
            time.sleep(0.5)                                                    # G4-007: die zweite Eingabe ist gesendet oder wartet im Puffer auf einen 011 (sw_zwei_ziffern holt nach dem Umschaltzeichen keinen mehr)
            self.assertEqual(l.geliefert[0], 'Um. KB')                         # der Rechner hat die Lage des SW als erstes Eingabezeichen bekommen
            # Je nach Programm ist bei der zweiten Eingabe ein 011 aktiv oder nicht; in jedem Fall gilt: angezeigt ist genau, was angekommen ist
            self.assertEqual(l.eingabe_angezeigt(), ''.join(t for t in l.geliefert if not t.startswith('Um.')))
        finally:
            l.schliessen()

    def test_taste_t_statt_sw_das_fenster_nimmt_nichts_an(self):
        l = PultLauf('KB', 'KB', schalter='T')
        try:
            l.starten()
            self.assertTrue(l.warte(lambda: l.r.m.k0._wartet_auf is not None))
            self.assertEqual(l.r.m.k0._wartet_auf, 'T')
            self.assertEqual(l.sw.tippen('2'), 'blockiert')
            self.assertEqual(l.geliefert, []); self.assertEqual(l.eingabe_angezeigt(), '')
        finally:
            l.schliessen()


if __name__ == '__main__':
    unittest.main(verbosity=1)
