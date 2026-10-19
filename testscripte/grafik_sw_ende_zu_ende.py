# -*- coding: utf-8 -*-
"""Pruefungen Stufe 3, Ende-zu-Ende (Checkpoint 37: keine Vormerkung, Anzeige jedes angenommenen Zeichens, zwei Eingaben im Abstand von 0,1 s; Checkpoint 23: B-1 behoben, Schalterstellung SW liegt in m.sw_schalter): ein Programm (ziffern, sw_zwei_ziffern) laeuft auf dem ECHTEN GRAFIK-Rechner (c8205_grafik.Rechner, echte
K0Warteschlange, SwSenke); das SW-Fenster wird durch die Logikschicht (SwAnzeige + SwEingabe) ersetzt, die ein Faden im
25-ms-Takt wie die Tk-Schicht bedient. Verglichen werden Ausgabe, Endzustand der Register und Verhalten bei Zeichenlage GB.
Nicht geprueft wird hier das echte Tk-Fenster.
Aufruf: python3 -I testscripte/grafik_sw_ende_zu_ende.py"""
import os, queue, random, shutil, sys, tempfile, threading, time, unittest
HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
import c8205_interp as I
from grafik_sw import SwAnzeige, SwEingabe

ZEIT = 6.0        # Hoechstdauer eines Laufs in Sekunden


def erwartete_ausgabe(name):
    with open(os.path.join(PROJ, 'Test-Ergebnisvergleiche', name + '-sw-ausgabe.txt'), encoding='utf-8') as fh:
        return fh.read()


class Lauf:
    """Ein Programm aus Tests/<name>.test, Eingabe als Liste getippter Zeichen."""

    def __init__(self, name, eingabe, lage_erzwingen=None, seed=1, sw=True, rechner_lage=None, abstand=0.25, lage_unbestimmt=False):
        import c8205_grafik as G
        from grafik_trommel import GrafikTrommel, GrafikAbbruch
        self.G, self.Abbruch = G, GrafikAbbruch
        self.name, self.eingabe, self.rechner_lage = name, list(eingabe), rechner_lage
        # G3-008 (18.10.2026): Ist die Lage des SW unbestimmt, geht vor dem ersten Zeichen IMMER ein Umschaltzeichen zum Rechner. Die Programme
        # dieser Tests (ziffern_*, sw_zwei_ziffern) kennen kein Umschaltzeichen; deshalb steht das SW hier, wenn nichts anderes verlangt ist,
        # auf KB (der Benutzer hat vorher schon getippt). lage_unbestimmt=True: Vorzustand unbestimmt, wie nach dem Einschalten.
        self.lage_erzwingen = lage_erzwingen if (lage_erzwingen or lage_unbestimmt) else 'KB'
        self.sw_stellung = sw                   # True: Schalter SW wird nach dem H gedrueckt (Eingabe vom SW-Fenster); False: Stellung T
        self.dir = tempfile.mkdtemp()
        self.alt = os.getcwd(); os.chdir(self.dir)
        random.seed(seed)                       # Machine() waehlt die Anfangs-Zeichenlage zufaellig
        self.t = I.Test(os.path.join(PROJ, 'Tests', name + '.test'))
        assert not self.t.fehler, self.t.fehler
        pfad = os.path.join(self.dir, 'trommel.txt')
        shutil.copy(os.path.join(PROJ, 'virtuelle_Geraete', 'Trommel', 'trommel.txt'), pfad)
        if self.t.trommel_vor == 'LEER':
            I.schreibe_leere_trommeldatei(pfad)
        mem = {}
        with open(pfad, encoding='utf-8', newline='') as fh:
            for z in fh:
                mm = I.TROMMEL_ZEILE_RE.match(z); mem[int(mm.group(1), 8)] = int(mm.group(2), 8)
        mem.update({a & I.MASK12: w & I.MASK33 for a, w in self.t.mem.items()})
        with open(pfad, 'w', encoding='utf-8', newline='') as fh:
            fh.write(''.join(f'{a:04o}: {mem.get(a, 0):011o}\n' for a in range(4096)))
        graph = G.lade_graph(os.path.join(PROJ, 'markdown-dateien'))
        self.trommel = GrafikTrommel(pfad)
        self.r = G.Rechner(graph, self.trommel, pult_modus=False)
        # wie das SW-Fenster: Ausgabe des Rechners (Senke) und angenommene Eingabe laufen durch EINE Warteschlange in die Anzeige
        self.q = queue.Queue(); self.teile = []          # teile: (Quelle 'A' Ausgabe | 'E' Eingabe, Text) in der Reihenfolge der Anzeige
        self.anzeige, self.sw = SwAnzeige(), SwEingabe(self.r.m.k0, self.r.m, echo=lambda t: self.q.put(('E', t)), abstand=abstand)   # Abstand der zwei Eingaben: 0,25 s statt 0,1 s, damit der Lauf auf einem belasteten Rechner nicht schwankt (0,1 s prueft grafik_sw_tests)
        self.r.sw.hoere(lambda t: self.q.put(('A', t)))
        self.protokoll = []                              # (Zeichen, Antwort von tippen(), Lage beim Tippen)
        self.zweite = []                                 # Ergebnis jeder zweiten Eingabe (liefern()): 'geliefert' | 'blockiert'
        self.fehler = None

    def _zeichnen(self):
        """Im Takt: Warteschlange in die Anzeige (wie SwFenster._zeichnen)."""
        try:
            while True:
                quelle, text = self.q.get_nowait()
                self.teile.append((quelle, text)); self.anzeige.schreibe(text)
        except queue.Empty:
            pass

    def ausgabe(self):
        self._zeichnen(); return ''.join(t for q, t in self.teile if q == 'A')

    def eingabe_angezeigt(self):
        self._zeichnen(); return ''.join(t for q, t in self.teile if q == 'E')

    def schliessen(self):
        self.r.abbrechen(); self.trommel.schliessen(); os.chdir(self.alt); shutil.rmtree(self.dir, ignore_errors=True)

    def _rechner(self):
        try:
            tasten = [t for t in self.t.tasten if self.sw_stellung or t.upper() not in ('SW=1', 'SW+')]   # Stellung T: eigene SW=1 der Testdatei weglassen
            #                                                           Stellung SW (Eingabe vom SW-Fenster) nach dem H, wie im Pult-Start
            i = 1 if tasten and tasten[0].upper() == 'H' else 0
            ok, _ = self.r.folge(tasten[:i] + (['SW=1'] if self.sw_stellung else []) + tasten[i:])
            if ok and not self.r.m.halted and not self.r.m.fl['H']:
                self.ergebnis = self.r.lauf()
        except self.Abbruch:
            pass
        except Exception as e:                                       # im Faden: nicht verlieren
            self.fehler = f'{type(e).__name__}: {e}'

    def ausfuehren(self, zeit=ZEIT):
        th = threading.Thread(target=self._rechner, daemon=True); th.start()
        rest = list(self.eingabe); ende = time.time() + zeit
        while th.is_alive() and time.time() < ende:
            erg = self.sw.liefern()                                   # Takt des Fensters: zweite Eingabe, wenn ihre Zeit gekommen ist
            if erg: self.zweite.append(erg)
            self._zeichnen()
            if rest and self.sw.zweite is None and self.sw.erwartet():      # erwartet() = 011 aktiv und noch kein Zeichen fuer ihn da
                z = rest.pop(0)
                if self.lage_erzwingen and not self.protokoll:          # nur das erste getippte Zeichen: SW steht in dieser Lage
                    self.sw.lage = self.lage_erzwingen
                if self.rechner_lage and not self.protokoll:            # Lage des RECHNERS (darf fuer die Eingabe keine Rolle spielen)
                    self.r.m.zeichenlage = self.rechner_lage
                lage = self.sw.lage                                     # Lage des SW beim Tippen
                self.protokoll.append((z, self.sw.tippen(z), lage))
            time.sleep(0.005)
        beendet = not th.is_alive()
        self._zeichnen()
        if not beendet:
            self.r.abbrechen(); th.join(2)
        return beendet


class ZifferEndeZuEnde(unittest.TestCase):
    def pruefe(self, name, eingabe, vorweg='', echo=None, **kw):
        l = Lauf(name, eingabe, **kw)
        try:
            beendet = l.ausfuehren()
            self.assertIsNone(l.fehler)
            self.assertTrue(beendet, f'{name}: Rechner wartete noch ({l.protokoll}) Anzeige={l.anzeige.text()!r}')
            soll = vorweg + erwartete_ausgabe(name)
            self.assertEqual(l.r.sw.alles(), soll)                    # Senke == erwartete Ausgabe der Testdatei
            self.assertEqual(l.ausgabe(), soll)                       # Fenster bekam dieselbe Ausgabe ...
            self.assertEqual(l.eingabe_angezeigt(), echo if echo is not None else eingabe[:1])   # ... und zusaetzlich jedes angenommene Zeichen (S3-04 neu)
            wahr, zeilen = I.pruefe_ergebnis(l.t, l.r.m)
            self.assertTrue(wahr, '\n'.join(map(str, zeilen)))        # Register/Flags/Speicherzellen wie in der Testdatei
            return l
        finally:
            l.schliessen()

    def test_ziffer_0_programmende(self):
        self.pruefe('ziffern_0', '0')

    def test_ziffer_1(self):
        self.pruefe('ziffern_1', '1')

    def test_ziffer_2(self):
        self.pruefe('ziffern_2', '2')

    def test_ziffer_3(self):
        self.pruefe('ziffern_3', '3')

    def test_ziffern_4_bis_9_werden_uebergangen(self):
        l = self.pruefe('ziffern_uebergehen', '456789' + '2', echo='456789' + '2')      # jede angenommene Ziffer wird angezeigt, auch die uebergangenen
        self.assertEqual([z for z, a, _ in l.protokoll if a == 'geliefert'].count('2'), 1)

    def test_in_beiden_zeichenlagen(self):
        """Regel des Projektinhabers (18.10.2026): Fuer die Eingabe am SW zaehlt nur die Lage des SW, nie die des Rechners.
        SW auf KB: nur die Ziffer geht an den Rechner (sofort geliefert), gleich ob der Rechner auf KB oder GB steht.
        SW auf GB: zuerst Um. KB, dann die Ziffer, der Rechner bekommt ZWEI Eingabezeichen. ziffern_2 kennt Um. KB nicht (G4-017: kein Neubeginn,
        Sprung nach 0047 = Programmtext). Seit 18.10.2026 07:56 gibt es keine Vormerkung: Die Ziffer (zweite Eingabe, 0,25 s spaeter) kommt an, wenn das
        Programm dann wieder bei 011 ist (hier ja: der Interpreter ohne Schreibwerk-Zeit); sonst waere sie blockiert und der Bediener muesste erneut tippen."""
        for rechner in ('KB', 'GB'):
            with self.subTest(sw='KB', rechner=rechner):
                l = self.pruefe('ziffern_2', '2', lage_erzwingen='KB', rechner_lage=rechner)
                self.assertEqual(l.protokoll[0][1:], ('geliefert', 'KB'))
                self.assertEqual(len(l.protokoll), 1)
        for rechner in ('KB', 'GB'):
            with self.subTest(sw='GB', rechner=rechner):
                # G4-017: ziffern_2 kennt kein Umschaltzeichen (U-12, F-58). Um. KB springt per Sprung-Umstellung nach 0040 ODER 047 = 0047, dort liegt
                # Programmtext, kein Neubeginn. Geprueft wird deshalb nur, was die Regel verlangt: SW auf GB -> der Rechner bekommt ZWEI Eingabezeichen
                # (Um. KB, dann die Ziffer), die Lage des SW wird KB, die Aufforderung steht einmal im Fenster. Ein Programmende wird nicht erwartet.
                l = Lauf('ziffern_2', '2', lage_erzwingen='GB', rechner_lage=rechner)
                try:
                    l.ausfuehren(zeit=4)
                    self.assertIsNone(l.fehler)
                    self.assertEqual([(a, g) for _, a, g in l.protokoll], [('folgt', 'GB')])      # Um. KB geliefert, die Ziffer folgt
                    self.assertEqual(l.zweite, ['geliefert'])                                      # zweite Eingabe: 011 war aktiv
                    self.assertEqual(l.sw.lage, 'KB')
                    self.assertEqual(l.ausgabe(), 'Geben Sie eine Ziffer von 0-3 ein\n')           # Aufforderung einmal; Programm kennt Um. KB nicht
                    self.assertEqual(l.eingabe_angezeigt(), '2')
                finally:
                    l.schliessen()

    def test_mehrere_anfangslagen(self):
        for seed in (1, 2, 3, 4, 5, 6):
            with self.subTest(seed=seed):
                self.pruefe('ziffern_3', '3', seed=seed)

    def test_tippen_vor_dem_eingabe_halt_ist_blockiert(self):
        l = Lauf('ziffern_1', '1')
        try:
            self.assertEqual(l.sw.tippen('1'), 'blockiert')            # Rechner laeuft noch nicht: kein 011 aktiv
            self.assertIsNone(l.sw.zweite); self.assertEqual(l.eingabe_angezeigt(), '')      # keine Anzeige, nichts wartet
            self.assertTrue(l.ausfuehren()); self.assertIsNone(l.fehler)
            self.assertEqual(l.r.sw.alles(), erwartete_ausgabe('ziffern_1'))
        finally:
            l.schliessen()

    def test_eingabe_nach_dem_ende_blockiert_und_nicht_angezeigt(self):
        l = Lauf('ziffern_1', '1')
        try:
            self.assertTrue(l.ausfuehren())
            self.assertEqual(l.eingabe_angezeigt(), '1')               # die erste Ziffer war angenommen und ist angezeigt
            self.assertEqual(l.sw.tippen('1'), 'blockiert')            # Programm ist zu Ende: kein 011, Taste blockiert
            self.assertEqual(l.eingabe_angezeigt(), '1'); self.assertEqual(l.ausgabe(), erwartete_ausgabe('ziffern_1'))   # nichts Neues angezeigt
        finally:
            l.schliessen()


def warte_auf_eingabe(l, sek=5):
    th = threading.Thread(target=l._rechner, daemon=True); th.start()
    ende = time.time() + sek
    while time.time() < ende and l.r.m.k0._wartet_auf is None:
        time.sleep(0.01)
    return th


class SchalterStellung(unittest.TestCase):
    """B-1 (behoben in Checkpoint 23): der Anwahlbefehl K0 wertet die Schalterstellung SW aus (m.sw_schalter), nicht das durch den
    Anwahlbefehl K2 geloeschte Flag. Ist T gewaehlt, nimmt das SW-Fenster nichts an (nur die Pult-Tastatur)."""

    def test_schalter_gedrueckt_nach_k2_anwahl_wartet_auf_sw(self):
        l = Lauf('ziffern_2', '2')
        try:
            warte_auf_eingabe(l)
            self.assertTrue(l.r.sw_gedrueckt)
            self.assertEqual(l.r.m.k0._wartet_auf, 'SW')
            self.assertEqual((l.r.m.fl['SW'], l.r.m.fl['T'], l.r.m.fl['K2']), (1, 0, 0))
            self.assertTrue(l.sw.erwartet())
        finally:
            l.schliessen()

    def test_schalter_geloest_wartet_auf_t_fenster_nimmt_nichts_an(self):
        l = Lauf('ziffern_2', '2', sw=False)
        try:
            warte_auf_eingabe(l)
            self.assertFalse(l.r.sw_gedrueckt)
            self.assertEqual(l.r.m.k0._wartet_auf, 'T')
            self.assertFalse(l.sw.erwartet())
            self.assertEqual(l.sw.tippen('2'), 'blockiert')
            time.sleep(0.3)
            self.assertEqual(l.r.m.k0._wartet_auf, 'T')                 # wartet weiter auf die Pult-Tastatur
        finally:
            l.schliessen()

    def test_anwahlbefehl_liest_schalter_auch_ohne_k2_davor(self):
        import c8205_interp as I2
        m = I2.Machine(trommel=None)
        for stellung, erwartet in ((1, (0, 1)), (0, (1, 0))):
            for kanal_davor in (0o4600, 0o4500, 0o4400, None):         # K1, K2, K3 oder keine Anwahl vor K0
                m.sw_schalter = stellung
                if kanal_davor is not None:
                    m.AR = kanal_davor; I2.a028(m)
                    self.assertEqual((m.fl['T'], m.fl['SW']), (0, 0))
                m.AR = 0o4700; I2.a028(m)
                self.assertEqual((m.fl['T'], m.fl['SW']), erwartet, (stellung, kanal_davor))


class ZweiZiffernUeberSw(unittest.TestCase):
    """sw_zwei_ziffern (Assembler/Projekt_1/sw_zwei_ziffern): zwei Eingaben ueber SW, dazwischen ein Anwahlbefehl K2 (Ausgabe)."""

    def test_beide_ziffern_ueber_das_sw_fenster(self):
        l = Lauf('sw_zwei_ziffern', '23')
        try:
            self.assertTrue(l.ausfuehren()); self.assertIsNone(l.fehler)
            self.assertEqual([(z, a) for z, a, _ in l.protokoll], [('2', 'geliefert'), ('3', 'geliefert')])
            soll = erwartete_ausgabe('sw_zwei_ziffern')
            self.assertEqual(l.r.sw.alles(), soll)
            self.assertEqual(l.ausgabe(), soll); self.assertEqual(l.eingabe_angezeigt(), '23')      # Ausgabe wie die Sollausgabe, dazu die zwei Eingaben
            self.assertEqual(soll, 'Erste Ziffer 0-3:\nErste: 2\nZweite Ziffer 0-3:\nZweite: 3\n')
            wahr, zeilen = I.pruefe_ergebnis(l.t, l.r.m)
            self.assertTrue(wahr, '\n'.join(map(str, zeilen)))
        finally:
            l.schliessen()

    def test_uebergehen_zwischen_den_eingaben(self):
        l = Lauf('sw_zwei_ziffern', '9' + '2' + '75' + '3')
        try:
            self.assertTrue(l.ausfuehren()); self.assertIsNone(l.fehler)
            self.assertEqual(l.r.sw.alles(), erwartete_ausgabe('sw_zwei_ziffern'))
        finally:
            l.schliessen()

    def test_mit_stellung_t_bekommt_das_sw_fenster_nichts(self):
        l = Lauf('sw_zwei_ziffern', '23', sw=False)
        try:
            self.assertFalse(l.ausfuehren(zeit=1.0))                     # wartet auf die Pult-Tastatur
            self.assertEqual(l.protokoll, [])                            # das SW-Fenster hat kein Zeichen angenommen
            self.assertEqual(l.ausgabe(), 'Erste Ziffer 0-3:\n'); self.assertEqual(l.eingabe_angezeigt(), '')   # blockiert: auch keine Anzeige
        finally:
            l.schliessen()


if __name__ == '__main__':
    unittest.main(verbosity=1)
