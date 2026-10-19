#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_checkpoint4_tests.py - Tests zu den offenen Punkten aus Checkpoint 3 (Stufe 1):
  (1) Ein Fehler im Geraet (Leserordner fehlt, Leserpfad ist Datei, Stanzerpfad ist Datei) bricht den Rechner NICHT ab, sondern der
      Lauf endet mit Meldung (ok=False, "Geraet nicht nutzbar ..."); danach laesst sich der Rechner mit H G R neu starten.
  (2) H waehrend einer Endlosschleife mit Ausgabebefehlen (Stanzer, Schreibwerk): der Lauf endet, R setzt fort.
  (3) H waehrend des Dauerlaufs mit echter Trommel-Wartezeit: Reaktionszeit gemessen.
  (4) Stanzer im Rechnerlauf: stanzer.ls wird angelegt, ein zweiter Lauf schreibt fort (kein Ueberschreiben).
Aufruf:  python3 testscripte/grafik_checkpoint4_tests.py        (aus dem Projektordner)
Wichtig: nicht gleichzeitig mit anderen zeitkritischen Suiten starten (ein Kern: Zeitgrenzen reissen).
"""
import os
import sys
import threading
import time
import unittest

PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJEKT); sys.path.insert(0, os.path.join(PROJEKT, 'grafik-interpreter-module'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c8205_grafik as G                       # noqa: E402
from grafik_kern_tests import Basis            # noqa: E402
import grafik_geraete_tests as GT              # noqa: E402

# Lesen eines Lochbilds von Leser 1 (wie Tests/lb-002_ohne_Irrung_Zeichen.txt)
LB002 = GT.LB002

# Programm aus Tests/bsp_seite_42_025_stanzer.test: Anwahl K1, drei Zeichen stanzen, Halt bei BZ=2014
STANZER_PROGRAMM = {
    0o0000: 0o2000000, 0o2000: 0o4600030, 0o2001: 0o2014211, 0o2002: 0o2020240, 0o2003: 0o2017025,
    0o2004: 0o2015211, 0o2005: 0o2020240, 0o2006: 0o2017025, 0o2007: 0o2016211, 0o2010: 0o2020240,
    0o2011: 0o2017025, 0o2012: 0o1164, 0o2013: 0o20, 0o2014: 0o610030, 0o2015: 0o620030,
    0o2016: 0o430030, 0o2017: 0o2021240, 0o2022: 0o777,
}
STANZER_ERWARTET = '00110001\n00110010\n00100011\n'

# Endlosschleife: Anwahl K1 (Stanzer), dann immer wieder ein Zeichen stanzen (030 0610), Sprung zurueck
STANZER_SCHLEIFE = {0: 0o2000000, 0o2000: 0o4600030, 0o2001: 0o610030, 0o2002: 0o2001000}
# Endlosschleife: Anwahl K2 (Schreibwerk), dann immer wieder Druck "1" (030 0010), Sprung zurueck
SW_SCHLEIFE = {0: 0o3100000, 0o3100: 0o4500030, 0o3101: 0o10030, 0o3102: 0o3101000}
# Endlosschleife ohne Ausgabe: Sprung auf sich selbst; jeder Befehlsabruf wartet auf die Trommel
SPRUNG_AUF_SICH = {0: 0o0}


class Hilfe(Basis):
    def lauf_thread(self, r, vorher=('H', 'G')):
        self.tasten(r, *vorher)
        erg = {}

        def lauf():
            try:
                r.taste('R')
                erg['r'] = r.lauf_wenn_gewuenscht()
            except BaseException as e:          # darf nie vorkommen: der Rechner bricht nicht ab
                erg['exc'] = e
        t = threading.Thread(target=lauf, daemon=True)
        t.start()
        return t, erg

    def warte_bis(self, bedingung, sek=10.0):
        ende = time.time() + sek
        while time.time() < ende:
            if bedingung():
                return True
            time.sleep(0.005)
        return False

    def stanzer_zeilen(self, ordner):
        p = os.path.join(ordner, 'stanzer.ls')
        if not os.path.isfile(p):
            return []
        with open(p, encoding='utf-8') as f:
            return f.read().split('\n')[:-1]

    def pruefe_gehalten_mit_meldung(self, t, erg, r):
        t.join(10)
        self.assertFalse(t.is_alive(), 'der Lauf muss enden (Rechner haelt)')
        self.assertNotIn('exc', erg, f'der Rechner darf nicht mit einer Ausnahme abbrechen: {erg.get("exc")!r}')
        res = erg['r']
        self.assertFalse(res['ok'])
        self.assertIn('Geraet nicht nutzbar', res['grund'])
        self.assertFalse(r.laeuft)
        return res


class GeraetefehlerHalten(Hilfe):
    def test_leserordner_fehlt_rechner_haelt_und_startet_neu(self):
        fehlt = os.path.join(self.verz, 'gibt_es_noch_nicht')
        r = self.rechner(LB002)
        G.richte_geraete_ein(r, leser1=fehlt)
        t, erg = self.lauf_thread(r)
        self.pruefe_gehalten_mit_meldung(t, erg, r)
        # Ordner anlegen, Datei hinein, mit H G R neu starten: derselbe Rechner, dasselbe Leserobjekt
        os.makedirs(fehlt)
        GT.schreibe(fehlt, 'lb.txt', ['00000001'])
        t, erg = self.lauf_thread(r)
        t.join(10)
        self.assertFalse(t.is_alive())
        self.assertNotIn('exc', erg)
        self.assertTrue(erg['r']['ok'])
        self.assertEqual((r.m.BZ, r.m.AC), (0o2003, 1))
        self.assertTrue(os.path.isfile(os.path.join(fehlt, 'LOCHSTREIFENKORB', 'lb.txt')))

    def test_leserpfad_ist_eine_datei(self):
        datei = GT.schreibe(self.verz, 'keinordner.txt', ['00000001'])
        r = self.rechner(LB002)
        G.richte_geraete_ein(r, leser1=datei)
        t, erg = self.lauf_thread(r)
        self.pruefe_gehalten_mit_meldung(t, erg, r)
        self.assertTrue(os.path.isfile(datei), 'die Datei darf dabei nicht angetastet werden')

    def test_ungueltige_zeile_im_lochstreifen(self):
        d = os.path.join(self.verz, 'Leser1')
        os.makedirs(d)
        GT.schreibe(d, 'kaputt.txt', ['0000000X'])
        r = self.rechner(LB002)
        G.richte_geraete_ein(r, leser1=d)
        t, erg = self.lauf_thread(r)
        self.pruefe_gehalten_mit_meldung(t, erg, r)
        self.assertTrue(os.path.isfile(os.path.join(d, 'kaputt.txt')), 'fehlerhafte Datei bleibt liegen')

    def test_stanzerpfad_ist_eine_datei(self):
        datei = GT.schreibe(self.verz, 'stanzer_datei.txt', ['x'])
        r = self.rechner(STANZER_PROGRAMM)
        G.richte_geraete_ein(r, stanzer1=datei)
        t, erg = self.lauf_thread(r)
        self.pruefe_gehalten_mit_meldung(t, erg, r)


class StanzerImLauf(Hilfe):
    def test_stanzer_legt_an_und_schreibt_fort(self):
        ordner = os.path.join(self.verz, 'Stanzer1')
        r = self.rechner(STANZER_PROGRAMM)
        G.richte_geraete_ein(r, stanzer1=ordner)
        t, erg = self.lauf_thread(r)
        t.join(10)
        self.assertFalse(t.is_alive())
        self.assertNotIn('exc', erg)
        self.assertEqual((r.m.BZ, r.m.fl['US']), (0o2014, 1))                 # wie in TEST (bsp_seite_42_025_stanzer)
        self.assertEqual(''.join(z + '\n' for z in self.stanzer_zeilen(ordner)), STANZER_ERWARTET)
        # zweiter Lauf (H G R): die Datei wird fortgeschrieben, nicht ueberschrieben
        t, erg = self.lauf_thread(r)
        t.join(10)
        self.assertFalse(t.is_alive())
        self.assertEqual(''.join(z + '\n' for z in self.stanzer_zeilen(ordner)), STANZER_ERWARTET * 2)


class HBeiAusgabe(Hilfe):
    def test_h_in_der_stanzer_schleife_und_r_setzt_fort(self):
        ordner = os.path.join(self.verz, 'Stanzer1')
        r = self.rechner(STANZER_SCHLEIFE)
        G.richte_geraete_ein(r, stanzer1=ordner)
        t, erg = self.lauf_thread(r)
        self.assertTrue(self.warte_bis(lambda: len(self.stanzer_zeilen(ordner)) >= 5), 'es muss gestanzt werden')
        r.unterbrechen()
        t.join(10)
        self.assertFalse(t.is_alive(), 'H muss die Ausgabeschleife beenden')
        self.assertNotIn('exc', erg)
        self.assertEqual(r.m.fl['H'], 1)
        n1 = len(self.stanzer_zeilen(ordner))
        time.sleep(0.3)
        self.assertEqual(len(self.stanzer_zeilen(ordner)), n1, 'nach H darf nicht weitergestanzt werden')
        # R setzt fort
        t, erg = self.lauf_thread(r, vorher=())
        self.assertTrue(self.warte_bis(lambda: len(self.stanzer_zeilen(ordner)) >= n1 + 5), 'R muss die Schleife fortsetzen')
        r.unterbrechen()
        t.join(10)
        self.assertFalse(t.is_alive())
        self.assertTrue(all(z == '00110001' for z in self.stanzer_zeilen(ordner)), 'jede Zeile ein vollstaendiges Lochbild')

    def test_h_in_der_schreibwerk_schleife_und_r_setzt_fort(self):
        r = self.rechner(SW_SCHLEIFE)
        t, erg = self.lauf_thread(r)
        self.assertTrue(self.warte_bis(lambda: len(r.sw.alles()) >= 5), 'es muss gedruckt werden')
        r.unterbrechen()
        t.join(10)
        self.assertFalse(t.is_alive(), 'H muss die Druckschleife beenden')
        self.assertNotIn('exc', erg)
        self.assertEqual(r.m.fl['H'], 1)
        n1 = len(r.sw.alles())
        time.sleep(0.3)
        self.assertEqual(len(r.sw.alles()), n1)
        t, erg = self.lauf_thread(r, vorher=())
        self.assertTrue(self.warte_bis(lambda: len(r.sw.alles()) >= n1 + 5), 'R muss den Druck fortsetzen')
        r.unterbrechen()
        t.join(10)
        self.assertFalse(t.is_alive())

    def test_h_waehrend_der_trommel_wartezeit_reaktionszeit(self):
        r = self.rechner(SPRUNG_AUF_SICH)
        t, erg = self.lauf_thread(r)
        self.assertTrue(self.warte_bis(lambda: self.trommel.statistik().get('rd_wr_zugriffe', 0) >= 50), 'Trommel muss arbeiten')
        z0 = time.time()
        r.unterbrechen()
        t.join(10)
        dauer = time.time() - z0
        self.assertFalse(t.is_alive())
        self.assertNotIn('exc', erg)
        self.assertLess(dauer, 1.0, f'H reagiert zu langsam: {dauer:.3f} s')
        self.assertEqual(r.m.fl['H'], 1)
        print(f'\n  Reaktionszeit H (Trommel-Dauerlauf): {dauer * 1000:.1f} ms', end='')


if __name__ == '__main__':
    unittest.main(verbosity=2)
