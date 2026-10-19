# -*- coding: utf-8 -*-
"""Pruefmittel zu Anforderung S3-13 und S3-18 (Sperre statt Warten; keine Vormerkung, kein Programmende als Regel), GRAFIK_Beschreibung §5 (alt: Dok. 09), Befund B-1 / B-6.
Version: VM-003 (Checkpoint 37; VM-002 aus Checkpoint 32 pruefte die Vormerkung nach Entscheidung A, VM-001 aus Checkpoint 31 bildete die Anwahl K2 falsch nach).
Der Dateiname bleibt, damit die Verweise in GRAFIK_Beschreibung §5 (alt: Dok. 09) gelten. Aendert KEINEN Programmcode. Nicht Teil von grafik_alle_tests.sh.

Entscheidung des Projektinhabers 18.10.2026 (07:44, 07:56): Eine Eingabe wird nur angenommen und angezeigt, wenn im Moment der Eingabe ein 011 aktiv
ist, sonst ist die Taste blockiert. Ein Zeichen in der anderen Lage kommt als zwei Eingaben (Umschaltzeichen, Zeichen) im Abstand von etwa 0,1 s;
die zweite braucht wieder einen aktiven 011 (S3-11). Kein Warten, keine Vormerkung, keine Programmende-Regel.
  - test_kontrolle_schneller_rechner       : Rechner wieder bei 011, bevor die zweite Eingabe faellig ist: beide Eingaben kommen an, das Zeichen erscheint einmal.
  - test_s3_13_zweite_eingabe_blockiert_waehrend_k2 : das alte Echo-Programm (r300_eingabe: nach jedem Zeichen K2 anwaehlen, Ausgabe, K0 wieder) braucht laenger als
                                            0,1 s: die zweite Eingabe ist blockiert, geht verloren, erscheint nicht und wartet NICHT bis zum naechsten 011.
                                            (Ein Programm, das so arbeitet, ist als Eingabeprogramm nicht korrekt, S3-13.)
  - test_s3_18_kein_programmende_regel     : Der Rechner endet nach dem Umschaltzeichen: kein 011, die zweite Eingabe ist blockiert; nichts bleibt stehen, das Fenster fordert den Fokus nicht.
  - test_schalter_sw_losgelassen_blockiert : Schalter SW (m.sw_schalter) losgelassen, K0 bleibt: die Taste ist blockiert.
Maschinenmodell (wie c8205_interp.py Zeile 1555 bis 1563): Die Anwahl K1 bis K3 loescht die Flags T und SW; die Rueckkehr zu K0
setzt sie aus dem SCHALTER m.sw_schalter wieder.
Aufruf: python3 -I testscripte/grafik_sw_vormerkung_s3_13.py"""
import os, sys, threading, time, unittest
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HIER)); sys.path.insert(0, os.path.join(os.path.dirname(HIER), 'grafik-interpreter-module')); sys.path.insert(0, HIER)
from grafik_sw import SwEingabe
from grafik_k0 import K0Warteschlange


class Maschine:
    def __init__(self):
        self.sw_schalter = 1                       # Schalterstellung SW (gedrueckt)
        self.fl = {'SW': 1, 'T': 0, 'K1': 0, 'K2': 0, 'K3': 0}; self.zeichenlage = 'KB'

    def anwahl(self, kanal):
        """Wie c8205_interp.py: K1..K3 loescht T und SW; K0 setzt sie aus dem Schalter."""
        for k in (1, 2, 3):
            self.fl[f'K{k}'] = 1 if k == kanal else 0
        if kanal == 0:
            self.fl['T'], self.fl['SW'] = (0, 1) if self.sw_schalter else (1, 0)
        else:
            self.fl['T'] = self.fl['SW'] = 0


def warte(bed, s=2.0):
    t0 = time.time()
    while time.time() - t0 < s:
        if bed():
            return True
        time.sleep(0.005)
    return False


class SperreStattWarten(unittest.TestCase):
    def _start(self, k2_dauer=0.0, anzahl=None, abstand=0.1):
        """Rechner-Faden: holt ein Token, ist k2_dauer Sekunden bei K2 (kein 011), waehlt K0 wieder an; endet nach 'anzahl' Token."""
        m = Maschine(); k0 = K0Warteschlange(m); echo = []
        e = SwEingabe(k0, m, echo=echo.append, abstand=abstand); e.lage = 'KB'
        erhalten, stop = [], threading.Event()

        def rechner():
            n = 0
            while not stop.is_set():
                try:
                    t = k0.naechstes()
                except Exception:
                    return
                erhalten.append(t); n += 1
                if k2_dauer:                     # wie r300_eingabe (alt): gemein: K2 anwaehlen, Ausgabe, K0 wieder anwaehlen
                    m.anwahl(2); time.sleep(k2_dauer); m.anwahl(0)
                if anzahl is not None and n >= anzahl:
                    return                        # Programmende (Stopp): der Rechner holt nichts mehr
        th = threading.Thread(target=rechner, daemon=True); th.start()
        return m, k0, e, erhalten, echo, stop, th

    def _takt(self, e, sek):
        t0 = time.time(); erg = []
        while time.time() - t0 < sek:
            r = e.liefern()
            if r: erg.append(r)
            time.sleep(0.005)
        return erg

    def test_kontrolle_schneller_rechner(self):
        m, k0, e, erhalten, echo, stop, th = self._start()
        try:
            self.assertTrue(warte(e.erwartet)); self.assertEqual(e.tippen('A'), 'folgt')
            self.assertEqual(self._takt(e, 0.25), ['geliefert'])
            self.assertEqual(erhalten, ['Um. GB', 'A']); self.assertEqual(echo, ['A'])
        finally:
            stop.set(); k0.abbrechen()

    def test_s3_13_zweite_eingabe_blockiert_waehrend_k2(self):
        m, k0, e, erhalten, echo, stop, th = self._start(k2_dauer=0.3)
        try:
            self.assertTrue(warte(e.erwartet)); self.assertEqual(e.tippen('A'), 'folgt')
            self.assertEqual(self._takt(e, 0.2), ['blockiert'])              # bei 0,1 s ist der Rechner bei K2, kein 011 aktiv
            self.assertEqual(echo, [])                                       # nicht angezeigt
            self.assertTrue(warte(e.erwartet, 3.0))                          # Rechner wieder bei 011 ...
            self.assertEqual(self._takt(e, 0.3), [])                         # ... und es kommt nichts nach: kein Warten, keine Vormerkung
            self.assertEqual(erhalten, ['Um. GB']); self.assertEqual(echo, []); self.assertIsNone(e.zweite)
        finally:
            stop.set(); k0.abbrechen()

    def test_s3_18_kein_programmende_regel(self):
        m, k0, e, erhalten, echo, stop, th = self._start(anzahl=1)        # Rechner nimmt nur das Umschaltzeichen und endet
        try:
            self.assertTrue(warte(e.erwartet)); self.assertEqual(e.tippen('A'), 'folgt')
            th.join(2.0)
            self.assertEqual(self._takt(e, 0.25), ['blockiert'])
            self.assertFalse(e.eingabe_aktiv()); self.assertIsNone(e.zweite); self.assertEqual(echo, [])
            self.assertEqual(e.tippen('b'), 'blockiert')                     # und es bleibt blockiert
        finally:
            stop.set(); k0.abbrechen()

    def test_schalter_sw_losgelassen_blockiert(self):
        m, k0, e, erhalten, echo, stop, th = self._start()
        try:
            self.assertTrue(warte(e.erwartet))
            m.sw_schalter = 0; m.anwahl(0)                                   # Schalter SW losgelassen, K0 bleibt: Quelle T
            self.assertTrue(warte(lambda: not e.erwartet()))
            self.assertEqual(e.tippen('a'), 'blockiert'); self.assertEqual(erhalten, []); self.assertEqual(echo, [])
        finally:
            stop.set(); k0.abbrechen()


if __name__ == '__main__':
    unittest.main(verbosity=2)
