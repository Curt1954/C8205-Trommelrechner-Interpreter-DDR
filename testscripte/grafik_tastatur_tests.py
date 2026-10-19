# -*- coding: utf-8 -*-
"""Pruefungen fuer --TASTATUR=de|en (G4-010), ohne Tkinter."""
import os, subprocess, sys, unittest
HIER = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
import grafik_tastatur as T


class Tastatur(unittest.TestCase):
    def tearDown(self):
        T.setze('de')

    def test_vorgabe_de(self):
        self.assertEqual(T.belegung(), 'de')

    def test_setze_gross_klein_und_fehler(self):
        self.assertEqual(T.setze('EN'), 'en'); self.assertEqual(T.setze(' De '), 'de')
        with self.assertRaises(ValueError): T.setze('fr')

    def test_altgr(self):
        for k in ('at', 'bracketleft', 'EuroSign', 'asciitilde', 'bar', 'backslash'):
            self.assertTrue(T.braucht_altgr(k, 'de')); self.assertFalse(T.braucht_altgr(k, 'en'))
        T.setze('en'); self.assertFalse(T.braucht_altgr('at'))
        for k in ('colon', 'a', 'percent'):
            self.assertFalse(T.braucht_altgr(k, 'de'))

    def test_tippweise_doppelpunkt(self):
        self.assertEqual(T.tippweise(':', 'de'), 'Umschalt+.'); self.assertEqual(T.tippweise(':', 'en'), 'Umschalt+;')
        self.assertEqual(T.tippweise('A', 'de'), 'Umschalt+a')

    def test_alle_r300_zeichen_haben_tippweise(self):
        import c8205_interp as I
        for r in I.TABELLE1:
            for a in (r[4], r[5]):
                if 32 < a < 127 and chr(a) not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
                    self.assertIn(chr(a), T._TIPPWEISE, chr(a))

    def test_schalter(self):
        def rc(*a):
            return subprocess.run([sys.executable, os.path.join(PROJ, 'c8205_grafik.py'), '--ohne-fenster', *a], capture_output=True, text=True, cwd=PROJ)
        self.assertEqual(rc('--TASTATUR=fr').returncode, 16)
        self.assertIn('--TASTATUR', rc('--TASTATUR=fr').stderr)
        self.assertNotIn('--TASTATUR', rc('--TASTATUR=en', '--version').stderr)


if __name__ == '__main__':
    unittest.main()
