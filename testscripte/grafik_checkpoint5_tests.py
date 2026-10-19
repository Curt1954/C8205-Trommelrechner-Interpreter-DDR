#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_checkpoint5_tests.py - Tests zu den offenen Punkten aus Checkpoint 4 (Stufe 1), soweit sie sich testen lassen:
  (1) KonfigFehler beim Verschieben in den LOCHSTREIFENKORB (Leser-Ebene und Rechner-Ebene). Das letzte Lochbild wird dann NICHT
      geliefert, die Datei bleibt liegen (Standardannahme (a) im Kopf von grafik_geraete.py). Gepruefte Ausloeser:
        - eine Datei mit dem Namen LOCHSTREIFENKORB steht im Leserordner (funktioniert auch als root),
        - Verschieben schlaegt mit PermissionError fehl (nachgestellt, weil Schreibschutz als root nicht greift),
        - echter Schreibschutz des Leserordners (nur wenn nicht als root; sonst uebersprungen).
  (2) Der Leser liest eine Datei beim Oeffnen vollstaendig: Aenderungen an der geoeffneten Datei werden nicht bemerkt
      (festgehaltenes Ist-Verhalten, kein Sollwert aus der GRAFIK_Beschreibung).
  (3) Stanzer: Fehlerpfad "stanzer.ls ist ein Ordner" und Schreiben ohne Zwischenspeicher (jede Zeile sofort in der Datei).
Aufruf:  python3 testscripte/grafik_checkpoint5_tests.py        (aus dem Projektordner)
Wichtig: nicht gleichzeitig mit anderen zeitkritischen Suiten starten (ein Kern).
"""
import os
import stat
import sys
import unittest
from unittest import mock

PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJEKT); sys.path.insert(0, os.path.join(PROJEKT, 'grafik-interpreter-module'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c8205_grafik as G                                       # noqa: E402
from c8205_interp import KonfigFehler                          # noqa: E402
from grafik_geraete import GrafikLeser, GrafikStanzer, KORB, STANZER_DATEI   # noqa: E402
from grafik_trommel import GrafikAbbruch                       # noqa: E402
import grafik_checkpoint4_tests as C4                          # noqa: E402
import grafik_geraete_tests as GT                              # noqa: E402

EIN_ROOT = hasattr(os, 'geteuid') and os.geteuid() == 0


def leserordner(verz, zeilen, name='lb.txt'):
    d = os.path.join(verz, 'Leser1')
    os.makedirs(d)
    GT.schreibe(d, name, zeilen)
    return d


def korb_als_datei(ordner):
    """Legt eine DATEI an dort, wo der Leser den Ordner LOCHSTREIFENKORB braucht: makedirs scheitert (FileExistsError).
    Die Aenderungszeiten werden ausdruecklich gesetzt: alle uebrigen Dateien sind aelter. Der Leser waehlt nach Aenderungszeit, bei
    Gleichstand nach Dateiname ('LOCHSTREIFENKORB' kommt vor 'lb.txt'); auf Dateisystemen mit grober Zeitaufloesung (Checkpoint 5:
    bei einem Rechner mit Netzlaufwerk/gemeinsamem Ordner aufgetreten) wurde sonst die Korb-Datei als Lochstreifen gelesen."""
    pfad = GT.schreibe(ordner, KORB, ['ich bin kein Ordner'])
    jetzt = os.stat(pfad).st_mtime_ns
    for n in os.listdir(ordner):
        if n != KORB:
            os.utime(os.path.join(ordner, n), ns=(jetzt - 100 * 10**9, jetzt - 100 * 10**9))
    return pfad


class KorbFehlerLeser(C4.Hilfe):
    def test_korb_ist_eine_datei_letztes_lochbild_wird_nicht_geliefert(self):
        d = leserordner(self.verz, ['00000001', '00000010'])
        korb = korb_als_datei(d)
        leser = GrafikLeser(d)
        self.assertEqual(leser.naechste(), '00000001')                 # nicht das letzte: noch kein Verschieben
        with self.assertRaises(KonfigFehler) as ctx:
            leser.naechste()                                           # das letzte Lochbild: Verschieben scheitert
        self.assertIn(KORB, str(ctx.exception))
        self.assertTrue(os.path.isfile(os.path.join(d, 'lb.txt')), 'die Datei bleibt liegen')
        self.assertTrue(os.path.isfile(korb), 'die Datei LOCHSTREIFENKORB darf nicht angetastet werden')
        # Zustand bleibt heil: derselbe Fehler noch einmal, das Lochbild wird auch jetzt nicht geliefert
        with self.assertRaises(KonfigFehler):
            leser.naechste()
        # Ursache beseitigen: dasselbe Leserobjekt liefert das letzte Lochbild und verschiebt die Datei
        os.remove(korb)
        self.assertEqual(leser.naechste(), '00000010')
        self.assertTrue(os.path.isfile(os.path.join(d, KORB, 'lb.txt')))
        self.assertFalse(os.path.exists(os.path.join(d, 'lb.txt')))

    def test_nach_neustart_wird_die_liegengebliebene_datei_von_vorn_gelesen(self):
        d = leserordner(self.verz, ['00000001', '00000010'])
        korb_als_datei(d)
        leser = GrafikLeser(d)
        leser.naechste()
        with self.assertRaises(KonfigFehler):
            leser.naechste()
        os.remove(os.path.join(d, KORB))
        neu = GrafikLeser(d)                                           # wie ein neuer Start des Rechners
        self.assertEqual(neu.naechste(), '00000001')                   # von vorn, nicht ab dem letzten Lochbild
        self.assertEqual(neu.naechste(), '00000010')
        self.assertTrue(os.path.isfile(os.path.join(d, KORB, 'lb.txt')))

    def test_einzeiler_scheitert_schon_beim_ersten_lochbild(self):
        d = leserordner(self.verz, ['00000001'])
        korb_als_datei(d)
        leser = GrafikLeser(d)
        with self.assertRaises(KonfigFehler):
            leser.naechste()
        self.assertTrue(os.path.isfile(os.path.join(d, 'lb.txt')))

    def test_verschieben_mit_permissionerror_nachgestellt(self):
        d = leserordner(self.verz, ['00000001', '00000010'])
        leser = GrafikLeser(d)
        leser.naechste()
        with mock.patch('grafik_geraete.shutil.move', side_effect=PermissionError(13, 'Permission denied')):
            with self.assertRaises(KonfigFehler) as ctx:
                leser.naechste()
        self.assertIn('nicht nach LOCHSTREIFENKORB verschoben werden', str(ctx.exception))
        self.assertIn('Permission denied', str(ctx.exception))
        self.assertTrue(os.path.isfile(os.path.join(d, 'lb.txt')))
        self.assertEqual(leser.naechste(), '00000010')                 # ohne Patch geht es weiter

    @unittest.skipIf(EIN_ROOT or not hasattr(os, 'chmod') or os.name == 'nt',
                     'echter Schreibschutz greift als root (und unter Windows) nicht')
    def test_echter_schreibschutz_des_leserordners(self):
        d = leserordner(self.verz, ['00000001', '00000010'])
        leser = GrafikLeser(d)
        leser.naechste()
        alt = os.stat(d).st_mode
        os.chmod(d, stat.S_IRUSR | stat.S_IXUSR)                       # nur lesen: kein Anlegen des Korbs
        try:
            with self.assertRaises(KonfigFehler):
                leser.naechste()
            self.assertTrue(os.path.isfile(os.path.join(d, 'lb.txt')))
        finally:
            os.chmod(d, alt)                                           # sonst laesst sich der Testordner nicht loeschen


class KorbFehlerRechner(C4.Hilfe):
    def test_rechner_haelt_mit_meldung_und_liest_nach_behebung(self):
        d = leserordner(self.verz, ['00000001'])
        korb = korb_als_datei(d)
        r = self.rechner(C4.LB002)
        G.richte_geraete_ein(r, leser1=d)
        t, erg = self.lauf_thread(r)
        res = self.pruefe_gehalten_mit_meldung(t, erg, r)
        self.assertIn(KORB, res['grund'])
        self.assertTrue(os.path.isfile(os.path.join(d, 'lb.txt')), 'Datei bleibt liegen')
        # Ursache beseitigen, mit H G R neu starten: derselbe Rechner liest das Lochbild
        os.remove(korb)
        t, erg = self.lauf_thread(r)
        t.join(10)
        self.assertFalse(t.is_alive())
        self.assertNotIn('exc', erg)
        self.assertTrue(erg['r']['ok'])
        self.assertEqual((r.m.BZ, r.m.AC), (0o2003, 1))
        self.assertTrue(os.path.isfile(os.path.join(d, KORB, 'lb.txt')))


class LeserLiestBeimOeffnenVollstaendig(C4.Hilfe):
    def test_aenderung_an_der_geoeffneten_datei_bleibt_unbemerkt(self):
        d = leserordner(self.verz, ['00000001', '00000010'])
        leser = GrafikLeser(d)
        self.assertEqual(leser.naechste(), '00000001')
        with open(os.path.join(d, 'lb.txt'), 'a', encoding='utf-8') as f:
            f.write('00000100\n')                                      # nach dem Oeffnen angehaengt
        self.assertEqual(leser.naechste(), '00000010')                 # letztes Lochbild der beim Oeffnen gelesenen Fassung
        with open(os.path.join(d, KORB, 'lb.txt'), encoding='utf-8') as f:
            self.assertEqual(f.read().split(), ['00000001', '00000010', '00000100'])   # der Zusatz liegt im Korb, wurde nie geliefert
        leser.aufruf_beim_warten = leser.abbrechen                     # sonst wartet naechste() endlos auf eine neue Datei
        with self.assertRaises(GrafikAbbruch):
            leser.naechste()


class StanzerFehlerUndSchreiben(C4.Hilfe):
    def test_stanzer_ls_ist_ein_ordner(self):
        ordner = os.path.join(self.verz, 'Stanzer1')
        os.makedirs(os.path.join(ordner, STANZER_DATEI))               # ein ORDNER mit dem Namen der Stanzerdatei
        with self.assertRaises(KonfigFehler) as ctx:
            GrafikStanzer(ordner).stanze(0b00110001)
        self.assertIn('nicht beschreibbar', str(ctx.exception))
        r = self.rechner(C4.STANZER_PROGRAMM)
        G.richte_geraete_ein(r, stanzer1=ordner)
        t, erg = self.lauf_thread(r)
        self.pruefe_gehalten_mit_meldung(t, erg, r)

    def test_jede_zeile_steht_sofort_in_der_datei(self):
        ordner = os.path.join(self.verz, 'Stanzer1')
        s = GrafikStanzer(ordner)
        erwartet = []
        for lb in (0b00110001, 0b00000000, 0b11111111, 0b00100011):
            s.stanze(lb)
            erwartet.append(format(lb, '08b'))
            self.assertEqual(self.stanzer_zeilen(ordner), erwartet, 'nichts bleibt im Puffer')


if __name__ == '__main__':
    unittest.main(verbosity=2)
