# -*- coding: utf-8 -*-
"""G4-011: Abstand zwischen Umschalttaste und Zeichentaste bei gehaltener Umschalttaste (ohne Tkinter)."""
import os, sys, unittest, time
HIER = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
import grafik_sw_fenster as F


class Ev:
    def __init__(self, keysym, char='', state=0):
        self.keysym, self.char, self.state = keysym, char, state


class Rec:
    def __init__(self): self.abstaende = []
    def tippen(self, z, a): self.abstaende.append(a); return 'geliefert'
    puffer = []
    def erwartet(self): return True          # G4-009: das Debug-Log des Fensters fragt '011 aktiv' ab


def fenster():
    w = F.SwFenster.__new__(F.SwFenster)
    w._umschalt, w._letzte_taste, w.eingabe = {}, 0.0, Rec()
    return w


class Abstand(unittest.TestCase):
    def test_gehaltene_umschalttaste_verzoegert_nicht(self):
        w = fenster()
        w._taste(Ev('Shift_L'))
        w._umschalt['Shift_L'] -= 5.0              # Umschalt wird seit 5 s gehalten
        w._letzte_taste = time.monotonic() - 0.2   # letzte Zeichentaste vor 0,2 s
        w._taste(Ev('colon', ':', 1))
        a = w.eingabe.abstaende[0]
        self.assertEqual(a, F.SwFenster.ABSTAND_MAX)          # 0,2 s echter Abstand, begrenzt auf den Deckel (G4-011b: 0,1 s)

    def test_erste_taste_nach_umschalt_echter_abstand(self):
        w = fenster()
        w._taste(Ev('Shift_L'))
        w._umschalt['Shift_L'] -= 0.08
        w._taste(Ev('A', 'A', 1))
        self.assertTrue(0.07 < w.eingabe.abstaende[0] < 0.2, w.eingabe.abstaende)

    def test_deckel(self):
        w = fenster()
        w._taste(Ev('Shift_L'))
        w._umschalt['Shift_L'] -= 9.0
        w._taste(Ev('A', 'A', 1))
        self.assertEqual(w.eingabe.abstaende[0], F.SwFenster.ABSTAND_MAX)

    def test_kurzer_echter_abstand_bleibt_unter_dem_deckel(self):
        w = fenster()
        w._taste(Ev('Shift_L'))
        w._umschalt['Shift_L'] -= 5.0              # Umschalt wird seit 5 s gehalten
        w._letzte_taste = time.monotonic() - 0.04  # letzte Zeichentaste vor 0,04 s: schneller als der Deckel, es gilt der echte Abstand
        w._taste(Ev('colon', ':', 1))
        a = w.eingabe.abstaende[0]
        self.assertTrue(0.03 < a < F.SwFenster.ABSTAND_MAX, a)

    def test_deckel_ist_hoechstens_die_anforderung(self):
        self.assertLessEqual(F.SwFenster.ABSTAND_MAX, 0.1)   # Anforderung: zwei Eingaben im Abstand von etwa 0,1 s

    def test_ohne_umschalt_kein_abstand(self):
        w = fenster()
        w._taste(Ev('a', 'a'))
        self.assertIsNone(w.eingabe.abstaende[0])


if __name__ == '__main__':
    unittest.main()
