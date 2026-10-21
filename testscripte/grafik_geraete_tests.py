#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_geraete_tests.py - Tests fuer grafik_geraete.py (Leser: Ordner, Aenderungszeit, LOCHSTREIFENKORB, aktives Warten;
Stanzer: stanzer.ls fortschreiben; Start: gleicher Ordner) und fuer das Zusammenspiel mit dem Rechner.
Aufruf:  python3 testscripte/grafik_geraete_tests.py        (aus dem Projektordner)
Wichtig: nicht gleichzeitig mit den zeitkritischen Trommel-/Kerntests starten (ein Kern: Zeitgrenzen reissen).
"""
import os
import sys
import tempfile
import threading
import time
import unittest

PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJEKT); sys.path.insert(0, os.path.join(PROJEKT, 'grafik-interpreter-module'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c8205_grafik as G                                           # noqa: E402
from c8205_interp import KonfigFehler                              # noqa: E402
from grafik_geraete import GrafikLeser, GrafikStanzer, pruefe_verschieden, KORB   # noqa: E402
from grafik_trommel import GrafikAbbruch                           # noqa: E402
from grafik_kern_tests import Basis                                # noqa: E402


def schreibe(ordner, name, zeilen, mtime=None):
    p = os.path.join(ordner, name)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(''.join(z + '\n' for z in zeilen))
    if mtime is not None:
        os.utime(p, ns=(mtime, mtime))
    return p


def inhalt(pfad):
    with open(pfad, encoding='utf-8') as f:
        return f.read()


def lies_alle(leser, n):
    return [leser.naechste() for _ in range(n)]


class LeserEinheit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_reihenfolge_aenderungszeit_vor_name(self):
        schreibe(self.d, 'a_neu.txt', ['00000011'], mtime=2_000_000_000_000_000_000)
        schreibe(self.d, 'z_alt.txt', ['00000001'], mtime=1_000_000_000_000_000_000)
        self.assertEqual(lies_alle(GrafikLeser(self.d), 2), ['00000001', '00000011'])

    def test_gleiche_zeit_dann_dateiname(self):
        t = 1_500_000_000_000_000_000
        schreibe(self.d, 'b.txt', ['00000010'], mtime=t)
        schreibe(self.d, 'a.txt', ['00000001'], mtime=t)
        self.assertEqual(lies_alle(GrafikLeser(self.d), 2), ['00000001', '00000010'])

    def test_komplett_gelesen_in_den_korb_teilgelesen_bleibt(self):
        schreibe(self.d, 'band.txt', ['00000001', '00000010', '00000100'])
        le = GrafikLeser(self.d)
        lies_alle(le, 2)
        self.assertTrue(os.path.isfile(os.path.join(self.d, 'band.txt')), 'teilgelesen: bleibt liegen')
        self.assertFalse(os.path.exists(os.path.join(self.d, KORB)))
        le.naechste()                                           # letztes Lochbild
        self.assertFalse(os.path.exists(os.path.join(self.d, 'band.txt')))
        self.assertTrue(os.path.isfile(os.path.join(self.d, KORB, 'band.txt')), 'komplett gelesen: im Korb')

    def test_gleicher_name_im_korb_wird_ueberschrieben(self):
        """OP-34, entschieden 21.10.2026 (Variante a): Liegt im Korb schon eine Datei gleichen Namens, wird sie ohne Meldung ueberschrieben."""
        os.makedirs(os.path.join(self.d, KORB))
        schreibe(os.path.join(self.d, KORB), 'band.txt', ['11111111'])          # alte Datei im Korb
        schreibe(self.d, 'band.txt', ['00000001'])                              # neue Datei gleichen Namens
        self.assertEqual(GrafikLeser(self.d).naechste(), '00000001')
        self.assertEqual(os.listdir(os.path.join(self.d, KORB)), ['band.txt'])
        self.assertEqual(inhalt(os.path.join(self.d, KORB, 'band.txt')), '00000001\n')     # nur noch die neue
        self.assertFalse(os.path.exists(os.path.join(self.d, 'band.txt')))

    def test_nachruecken_in_einem_aufruf_und_leerzeilen(self):
        schreibe(self.d, 'eins.txt', ['00000001', '', '00000010'], mtime=1_000_000_000_000_000_000)
        schreibe(self.d, 'zwei.txt', ['00000100'], mtime=2_000_000_000_000_000_000)
        le = GrafikLeser(self.d)
        self.assertEqual(lies_alle(le, 3), ['00000001', '00000010', '00000100'])
        self.assertEqual(sorted(os.listdir(os.path.join(self.d, KORB))), ['eins.txt', 'zwei.txt'])

    def test_neustart_liest_teilgelesene_von_vorn(self):
        schreibe(self.d, 'band.txt', ['00000001', '00000010'])
        self.assertEqual(GrafikLeser(self.d).naechste(), '00000001')     # Netz-Aus: Objekt verworfen
        self.assertEqual(lies_alle(GrafikLeser(self.d), 2), ['00000001', '00000010'])

    def test_punktdateien_und_unterordner_bleiben_unbeachtet(self):
        os.makedirs(os.path.join(self.d, 'unter'))
        schreibe(os.path.join(self.d, 'unter'), 'x.txt', ['00000001'])
        schreibe(self.d, '.versteckt', ['00000010'])
        schreibe(self.d, 'echt.txt', ['00000100'])
        self.assertEqual(GrafikLeser(self.d).naechste(), '00000100')

    def test_fehler_sind_konfigfehler(self):
        schreibe(self.d, 'kaputt.txt', ['00000001', 'xyz'])
        with self.assertRaises(KonfigFehler):
            GrafikLeser(self.d).naechste()
        with self.assertRaises(KonfigFehler):
            GrafikLeser(os.path.join(self.d, 'gibt_es_nicht')).naechste()

    def test_korb_ist_eine_datei_datei_bleibt_liegen(self):
        schreibe(self.d, KORB, ['egal'])                         # LOCHSTREIFENKORB als Datei
        os.makedirs(os.path.join(self.d, 'l'))
        l = os.path.join(self.d, 'l')
        schreibe(l, 'band.txt', ['00000001'])
        with open(os.path.join(l, KORB), 'w'):
            pass
        with self.assertRaises(KonfigFehler):
            GrafikLeser(l).naechste()
        self.assertTrue(os.path.isfile(os.path.join(l, 'band.txt')))

    def test_wartet_aktiv_ruft_haken_und_nimmt_neue_datei(self):
        le = GrafikLeser(self.d, takt=0.01)
        aufrufe = []

        def haken():
            aufrufe.append(le.wartet)
            if len(aufrufe) == 3:
                schreibe(self.d, 'spaet.txt', ['00000001'])
        le.aufruf_beim_warten = haken
        self.assertEqual(le.naechste(), '00000001')
        self.assertEqual(aufrufe, [True, True, True])
        self.assertFalse(le.wartet)

    def test_ausnahme_im_haken_laesst_zustand_heil(self):
        le = GrafikLeser(self.d, takt=0.01)

        def haken():
            raise RuntimeError('H')
        le.aufruf_beim_warten = haken
        with self.assertRaises(RuntimeError):
            le.naechste()
        self.assertFalse(le.wartet)
        schreibe(self.d, 'band.txt', ['00000001'])
        le.aufruf_beim_warten = None
        self.assertEqual(le.naechste(), '00000001')

    def test_abbrechen_beendet_das_warten(self):
        le = GrafikLeser(self.d, takt=0.01)
        threading.Timer(0.1, le.abbrechen).start()
        with self.assertRaises(GrafikAbbruch):
            le.naechste()


class StanzerEinheit(unittest.TestCase):
    def test_anlegen_anhaengen_nie_ueberschreiben(self):
        with tempfile.TemporaryDirectory() as d:
            ordner = os.path.join(d, 'neu', 'Stanzer1')
            GrafikStanzer(ordner).stanze(0o101)
            self.assertEqual(inhalt(os.path.join(ordner, 'stanzer.ls')), '01000001\n')
            GrafikStanzer(ordner).stanze(0o377)                  # zweiter Start: fortschreiben
            self.assertEqual(inhalt(os.path.join(ordner, 'stanzer.ls')), '01000001\n11111111\n')

    def test_pfad_ist_eine_datei(self):
        with tempfile.TemporaryDirectory() as d:
            p = schreibe(d, 'datei.txt', ['x'])
            with self.assertRaises(KonfigFehler):
                GrafikStanzer(p).stanze(1)


class Start(unittest.TestCase):
    def test_gleicher_ordner_ist_startfehler(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(KonfigFehler):
                pruefe_verschieden(d, d + os.sep)
            self.assertEqual(G.hauptprogramm(['--leser1', d, '--leser2', d]), G.RC_START)

    def test_verschiedene_ordner_gehen(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            pruefe_verschieden(d1, d2)
            pruefe_verschieden(d1, None)


# 0000: Sprung nach 2000; 2000: Anwahl Kanal K1 (Leser 1); 2001: Eingabe-Halt 1. Art; 2002: unbedingter Stopp;
# Zelle 0001 = 1 (das addiert die Eingabe der Ziffer 1 zum AC). Wie Tests/lb-002_ohne_Irrung_Zeichen.txt.
LB002 = {0: 0o00002000000, 0o2000: 0o00004600030, 0o2001: 0o010, 0o2002: 0o020, 1: 1}


class MitRechner(Basis):
    def leser_ordner(self):
        d = os.path.join(self.verz, 'Leser1')
        os.makedirs(d)
        return d

    def starte(self, r):
        self.tasten(r, 'H', 'G')
        erg = {}

        def lauf():
            r.taste('R')
            erg['r'] = r.lauf_wenn_gewuenscht()
        t = threading.Thread(target=lauf)
        t.start()
        return t, erg

    def test_lochbild_wird_gelesen_und_datei_wandert_in_den_korb(self):
        d = self.leser_ordner()
        schreibe(d, 'lb.txt', ['00000001'])
        r = self.rechner(LB002)
        G.richte_geraete_ein(r, leser1=d)
        t, erg = self.starte(r)
        t.join(10)
        self.assertFalse(t.is_alive())
        m = r.m
        self.assertEqual((m.BZ, m.AC, m.fl['US'], m.fl['E'], m.fl['FE']), (0o2003, 1, 1, 0, 0))   # wie lb-002 in TEST
        self.assertTrue(os.path.isfile(os.path.join(d, KORB, 'lb.txt')))

    def test_leerer_ordner_wartet_dann_kommt_die_datei(self):
        d = self.leser_ordner()
        r = self.rechner(LB002)
        G.richte_geraete_ein(r, leser1=d)
        t, erg = self.starte(r)
        le = r.m.leser[1]
        for _ in range(200):
            if le.wartet:
                break
            time.sleep(0.02)
        self.assertTrue(le.wartet, 'der Leser muss im Eingabe-Halt aktiv warten')
        self.assertTrue(t.is_alive())
        self.assertEqual(r.m.fl['E'], 1, 'Lampe E leuchtet beim Warten')
        schreibe(d, 'spaet.txt', ['00000001'])
        t.join(10)
        self.assertFalse(t.is_alive())
        self.assertEqual((r.m.BZ, r.m.AC), (0o2003, 1))

    def test_h_beendet_das_warten_und_die_datei_bleibt_nutzbar(self):
        d = self.leser_ordner()
        r = self.rechner(LB002)
        G.richte_geraete_ein(r, leser1=d)
        t, erg = self.starte(r)
        le = r.m.leser[1]
        for _ in range(200):
            if le.wartet:
                break
            time.sleep(0.02)
        self.assertTrue(le.wartet)
        r.unterbrechen()
        t.join(10)
        self.assertFalse(t.is_alive(), 'H muss das Warten auf den Leser beenden')
        self.assertFalse(le.wartet)
        self.assertEqual(r.m.fl['H'], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
