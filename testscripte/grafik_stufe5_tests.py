# -*- coding: utf-8 -*-
"""Pruefungen Stufe 5: Umschaltung --MODUS in c8205_interp.py (Standard GRAFIK, TEST wie bisher).
Alle Laeufe in Unterprozessen mit eigener Trommelkopie im Temp-Ordner; GRAFIK ohne echtes Tk (Ersatzmodul) und ohne Abspielprogramm
(leerer PATH), so endet der Start vor dem Aufblenden der Fenster mit Code 16.  Aufruf: python3 -I testscripte/grafik_stufe5_tests.py"""
import os, sys, shutil, subprocess, tempfile, unittest
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERP = os.path.join(PROJ, 'c8205_interp.py')
TEST = os.path.join(PROJ, 'Tests', '0001-210_211_020.txt')    # ohne Geraete- und Ausgabedateien im Projekt


class Modus(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        d = self.t.name
        os.mkdir(os.path.join(d, 'stub')); open(os.path.join(d, 'stub', 'tkinter.py'), 'w').close()
        os.mkdir(os.path.join(d, 'leer'))
        self.tr = os.path.join(d, 'trommel.txt')
        shutil.copy(os.path.join(PROJ, 'virtuelle_Geraete', 'Trommel', 'trommel.txt'), self.tr)
        self.env = dict(os.environ, PYTHONPATH=os.path.join(d, 'stub'), PATH=os.path.join(d, 'leer'), C8205_FENSTERLAGE='aus', PYTHONDONTWRITEBYTECODE='1')

    def tearDown(self):
        self.t.cleanup()

    def lauf(self, *args, env=None):
        p = subprocess.run([sys.executable, INTERP, *args], env=env or self.env, cwd=self.t.name, capture_output=True, text=True, timeout=90)
        return p.returncode, p.stdout + p.stderr

    def test_ohne_modus_ist_grafik(self):
        rc, text = self.lauf('--trommel', self.tr)
        self.assertEqual(rc, 16, text); self.assertIn('Kein Abspielprogramm gefunden', text)

    def test_modus_grafik_gross_und_klein(self):
        for a in (('--MODUS=GRAFIK',), ('--modus', 'grafik'), ('--MODUS', 'Grafik')):
            rc, text = self.lauf(*a, '--trommel', self.tr)
            self.assertEqual(rc, 16, (a, text))

    def test_testdatei_in_grafik_gibt_hinweis(self):
        rc, text = self.lauf('--trommel', self.tr, TEST)
        self.assertIn('--MODUS=TEST', text); self.assertEqual(rc, 16, text)

    def test_modus_test_laeuft_den_test(self):
        env = dict(os.environ, C8205_FENSTERLAGE='aus', PYTHONDONTWRITEBYTECODE='1')
        res = []
        for m in (('--MODUS=TEST',), ('--modus', 'test'), ('--MODUS', 'Test')):
            rc, text = self.lauf(*m, '--trommel', self.tr, '--out', os.path.join(self.t.name, 'prot'), '--NO-TERMOUT', TEST, env=env)
            res.append(rc); self.assertNotIn('Kein Abspielprogramm', text); self.assertNotIn('Hinweis: Testdateien', text)
        self.assertEqual(len(set(res)), 1, res); self.assertEqual(res[0], 0)

    def test_unbekannter_modus_code_2(self):
        rc, text = self.lauf('--MODUS=XYZ', TEST)
        self.assertEqual(rc, 2); self.assertIn('unbekannter Modus', text)

    def test_version_und_hilfe_bleiben_die_des_interpreters(self):
        rc, text = self.lauf('--version'); self.assertEqual(rc, 0); self.assertIn('0.03-', text)
        rc, text = self.lauf('--help'); self.assertEqual(rc, 0); self.assertIn('--MODUS', text); self.assertIn('TEST|GRAFIK', text)

    def test_wrapper_setzt_modus_test(self):
        sh = open(os.path.join(PROJ, 'c8205_interpreter.sh'), encoding='utf-8').read()
        bat = open(os.path.join(PROJ, 'c8205_interpreter.bat'), encoding='utf-8', errors='replace').read()
        self.assertIn('c8205_interp.py --MODUS=TEST', sh); self.assertIn('c8205_interp.py --MODUS=TEST', bat)


if __name__ == '__main__':
    unittest.main(verbosity=1)
