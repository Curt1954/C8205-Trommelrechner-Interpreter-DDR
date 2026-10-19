#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_kern_tests.py - Tests des GRAFIK-Kerns (Stufe 1), soweit sie ueber den Gleichwertigkeitstest hinausgehen:
Dauerbetrieb am Pult (pult_modus=True), Unterbrechung durch H, Eingabe ueber die Warteschlange mit zwei Quellen (T/SW) aus
einem zweiten Thread, Abbruch, Bahnsperre und Schalterdatei ueber GrafikTrommel.
Aufruf:  python3 testscripte/grafik_kern_tests.py        (aus dem Projektordner; braucht das gebaute C-Modul in c-module/python/)
"""
import os
import sys
import tempfile
import threading
import time
import unittest

PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJEKT); sys.path.insert(0, os.path.join(PROJEKT, 'grafik-interpreter-module'))
import c8205_interp as I          # noqa: E402
import c8205_grafik as G          # noqa: E402
from grafik_trommel import GrafikTrommel, GrafikAbbruch   # noqa: E402

GRAPH = None


def graph():
    global GRAPH
    if GRAPH is None:
        GRAPH = G.lade_graph(os.path.join(PROJEKT, 'markdown-dateien'))
    return GRAPH


def trommel_datei(verz, zellen):
    """Trommeldatei mit den Zellen {adresse: wert}, Rest 0."""
    pfad = os.path.join(verz, 'trommel.txt')
    with open(pfad, 'w', encoding='utf-8', newline='') as f:
        f.write(''.join(f'{a:04o}: {zellen.get(a, 0):011o}\n' for a in range(4096)))
    return pfad


class Basis(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.verz = self.tmp.name

    def tearDown(self):
        if getattr(self, 'trommel', None):
            self.trommel.schliessen()
        self.tmp.cleanup()

    def rechner(self, zellen, basp='000000', **kw):
        self.trommel = GrafikTrommel(trommel_datei(self.verz, zellen), basp=basp)
        return G.Rechner(graph(), self.trommel, pult_modus=True, **kw)

    def tasten(self, r, *ts):
        for t in ts:
            r.taste(t)
            r.lauf_wenn_gewuenscht()


class Dauerbetrieb(Basis):
    def test_stopp_st_r_setzt_fort(self):
        # 0001: unbedingter Sprung nach 0002 ist nicht noetig: Programm ab 0000: Stopp (020), danach Stopp (020) noch einmal
        r = self.rechner({0: 0o00000020020 | (1 << 9), 1: 0o00000020020 | (2 << 9), 2: 0o00000020020})
        self.tasten(r, 'H', 'G', 'R')
        self.assertTrue(r.m.halted)
        self.assertEqual(r.m.fl['US'], 1)
        bz1 = r.m.BZ
        self.tasten(r, 'H', 'R')                   # H hebt den Halt auf, R setzt fort
        self.assertTrue(r.m.halted or r.m.fl['US'])
        self.assertNotEqual((r.m.BZ, r.m.halt_grund), (None, None))
        self.assertGreaterEqual(r.m.BZ, bz1)

    def test_h_unterbricht_endlosschleife(self):
        # 0000: Operationsteil 000 = unbedingter Sprung, Adressteil 0000 -> Sprung auf sich selbst (Endlosschleife)
        r = self.rechner({0: (0 << 9) | 0o000})
        self.tasten(r, 'H', 'G')
        ergebnis = {}

        def lauf():
            r.taste('R')
            ergebnis['r'] = r.lauf_wenn_gewuenscht()

        t = threading.Thread(target=lauf)
        t.start()
        time.sleep(0.5)
        self.assertTrue(t.is_alive(), 'der Lauf muss ohne Eingriff weiterlaufen')
        r.unterbrechen()
        t.join(10)
        self.assertFalse(t.is_alive(), 'H muss den Lauf an der Befehlsgrenze anhalten')
        self.assertEqual(r.m.fl['H'], 1)
        self.assertTrue(ergebnis['r']['ok'])
        self.assertIn('Unterbrechung', ergebnis['r']['grund'])

    def test_k0_warteschlange_zwei_quellen(self):
        # Operationsteil 010 = Eingabebefehl 1. Art (030-037 waeren Ausgabe!), Kanal K0, Stellung T:
        # Zeichen kommt nur von T; ein Zeichen von SW wird nicht angenommen
        r = self.rechner({0: 0o010, 1: 0o020})              # 0000: Eingabe, 0001: Stopp
        k0 = r.m.k0
        self.tasten(r, 'H', 'G')
        ergebnis = {}

        def lauf():
            r.taste('R')
            ergebnis['r'] = r.lauf_wenn_gewuenscht()

        t = threading.Thread(target=lauf)
        t.start()
        for _ in range(100):
            if k0.erwartet('T'):
                break
            time.sleep(0.02)
        self.assertTrue(k0.erwartet('T'), 'der Rechner muss im Eingabe-Halt auf T warten')
        self.assertFalse(k0.erwartet('SW'))
        self.assertFalse(k0.annehmen('SW', 'A'), 'SW-Zeichen werden bei Stellung T nicht angenommen')
        self.assertTrue(k0.annehmen('T', '5'))
        t.join(10)
        self.assertFalse(t.is_alive())
        self.assertEqual(r.m.fl['E'], 0)
        # Die Ziffer wird im AR nur eingeodert und mit dem naechsten Befehl (0001: Stopp) ueberschrieben; geprueft wird
        # daher der Ablauf: Eingabe-Halt beendet (E=0), Folgebefehl 0001 ausgefuehrt (BZ=0002, unbedingter Stopp).
        self.assertEqual(r.m.BZ, 0o2)
        self.assertEqual(r.m.halt_grund, 'Unbedingter Stop (US:=1)')

    def test_abbruch_waehrend_eingabe_halt(self):
        r = self.rechner({0: 0o010})                        # 010 = Eingabebefehl 1. Art
        self.tasten(r, 'H', 'G')
        fehler = {}

        def lauf():
            try:
                r.taste('R')
                r.lauf_wenn_gewuenscht()
            except GrafikAbbruch as e:
                fehler['e'] = e

        t = threading.Thread(target=lauf)
        t.start()
        time.sleep(0.3)
        r.abbrechen()
        t.join(10)
        self.assertFalse(t.is_alive())
        self.assertIn('e', fehler)


class TrommelUndBahnsperre(Basis):
    def test_schalterdatei_und_sperre(self):
        r = self.rechner({0o100: 7}, basp='100000')
        self.assertEqual(self.trommel.basp_stellung, '100000')
        self.trommel.wr(0, 0o777)                    # Spur 0 gesperrt
        self.assertEqual(self.trommel.rd(0), 0)
        self.assertEqual(self.trommel.gesperrte_schreibzugriffe, 1)
        self.trommel.wr(0o100, 0o11)                  # Spur 2 offen
        self.assertEqual(self.trommel.rd(0o100), 0o11)
        self.trommel.schliessen()
        self.trommel = GrafikTrommel(os.path.join(self.verz, 'trommel.txt'))     # ohne --BASP: Stellung aus der Datei
        self.assertEqual(self.trommel.basp_stellung, '100000')

    def test_fehlerhafte_trommeldatei(self):
        pfad = os.path.join(self.verz, 'kaputt.txt')
        with open(pfad, 'w') as f:
            f.write('0000: 1\n')
        with self.assertRaises(I.KonfigFehler):
            GrafikTrommel(pfad)

    def test_wartezeit_ist_echt(self):
        self.rechner({})
        t0 = time.perf_counter()
        for a in range(0, 32 * 40, 33):
            self.trommel.rd(a)
        self.assertGreater(self.trommel.wartezeit_summe, 0)
        self.assertGreater(time.perf_counter() - t0, 0.0005)


if __name__ == '__main__':
    unittest.main(verbosity=2)
