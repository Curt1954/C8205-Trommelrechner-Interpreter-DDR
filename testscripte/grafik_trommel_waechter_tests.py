# -*- coding: utf-8 -*-
"""Pruefungen zum Trommelwaechter (OP-19, entschieden 21.10.2026, Variante b), mit Gegenproben. Aufruf: python3 -I testscripte/grafik_trommel_waechter_tests.py
Arbeitet nur in einem Temp-Ordner; Trommel/trommel.txt des Projekts wird nicht angefasst."""
import io, os, shutil, subprocess, sys, tempfile, unittest
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import grafik_trommel_waechter as W
SKRIPT = os.path.join(HIER, 'grafik_trommel_waechter.py')


class Waechter(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        os.makedirs(os.path.join(self.d, 'Trommel'))
        self.txt = os.path.join(self.d, 'Trommel', 'trommel.txt'); self.basp = os.path.join(self.d, 'Trommel', 'trommel.basp')
        with open(self.txt, 'w') as f: f.write('0000: 00000000000\n')
        with open(self.basp, 'w') as f: f.write('000000\n')
        self.stand = os.path.join(self.d, 'stand.json')

    def _lauf(self, was):
        return subprocess.run([sys.executable, '-I', SKRIPT, was, self.stand, self.d], capture_output=True, text=True)

    def test_unveraendert_rc0(self):
        self.assertEqual(self._lauf('merken').returncode, 0)
        r = self._lauf('pruefen'); self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.assertIn('unveraendert', r.stdout)

    def test_gegenprobe_trommel_veraendert_rc1(self):
        self._lauf('merken')
        with open(self.txt, 'a') as f: f.write('0001: 00000000001\n')
        r = self._lauf('pruefen'); self.assertEqual(r.returncode, 1); self.assertIn('trommel.txt', r.stdout)
        self.assertNotIn('trommel.basp hat', r.stdout)

    def test_gegenprobe_schalterdatei_veraendert_rc1(self):
        self._lauf('merken')
        with open(self.basp, 'w') as f: f.write('000001\n')
        r = self._lauf('pruefen'); self.assertEqual(r.returncode, 1); self.assertIn('trommel.basp', r.stdout)

    def test_gegenprobe_datei_geloescht_rc1(self):
        self._lauf('merken'); os.remove(self.txt)
        r = self._lauf('pruefen'); self.assertEqual(r.returncode, 1); self.assertIn('fehlt', r.stdout)

    def test_gegenprobe_datei_entsteht_rc1(self):
        os.remove(self.basp); self._lauf('merken')
        with open(self.basp, 'w') as f: f.write('000000\n')
        self.assertEqual(self._lauf('pruefen').returncode, 1)

    def test_fehlt_vorher_und_nachher_rc0(self):
        os.remove(self.basp); self._lauf('merken'); self.assertEqual(self._lauf('pruefen').returncode, 0)

    def test_gleicher_inhalt_neu_geschrieben_rc0(self):
        """Nur der Inhalt zaehlt, nicht die Aenderungszeit."""
        self._lauf('merken')
        with open(self.txt) as f: s = f.read()
        with open(self.txt, 'w') as f: f.write(s)
        self.assertEqual(self._lauf('pruefen').returncode, 0)

    def test_stand_fehlt_rc2(self):
        self.assertEqual(self._lauf('pruefen').returncode, 2)

    def test_aufruf_falsch_rc2(self):
        r = subprocess.run([sys.executable, '-I', SKRIPT, 'unfug'], capture_output=True, text=True); self.assertEqual(r.returncode, 2)

    def test_funktionen_ohne_unterprozess(self):
        W.merken(self.stand, self.d); aus = io.StringIO(); self.assertEqual(W.pruefen(self.stand, self.d, aus), 0)
        with open(self.txt, 'a') as f: f.write('x')
        self.assertEqual(W.pruefen(self.stand, self.d, io.StringIO()), 1)

    def test_projekt_ordner_ist_vorgabe(self):
        """Ohne Ordnerangabe gilt der Projektordner (Elternordner von testscripte/); der Stand wird dort nur gelesen."""
        self.assertEqual(W.PROJ, os.path.dirname(HIER))
        s = W.stand(W.PROJ); self.assertEqual(set(s), set(W.DATEIEN))


if __name__ == '__main__':
    unittest.main(verbosity=1)
