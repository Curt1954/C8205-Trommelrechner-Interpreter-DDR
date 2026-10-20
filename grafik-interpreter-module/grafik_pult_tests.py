# -*- coding: utf-8 -*-
"""Pruefungen Stufe 2: Pult-Steuerung (ohne Tkinter) und Tk-Schicht mit Ersatzmodul. Aufruf: python3 -I testscripte/grafik_pult_tests.py"""
import os, sys, time, types, unittest
HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
from grafik_pult import PultSteuerung, AUS, HOCHLAUF, BETRIEB, AUSLAUF, ENDE
PULT = os.path.join(PROJ, 'pult')


class K0:
    def __init__(self): self.erw = False; self.got = []
    def erwartet(self, q): return self.erw and q == 'T'
    def annehmen(self, q, t):
        if not self.erwartet(q): return False
        self.got.append(t); return True


class FakeRechner:
    def __init__(self):
        self.mhalt = False; self.tokens = []; self.folgen = 0
        self.m = types.SimpleNamespace(fl={k: 0 for k in ('E','A','T','SW','K1','K2','K3','FE','FUE','BS','US','H','V1','V2')}, adr=0, OR=0, k0=K0())
        self.sw = types.SimpleNamespace(unterdruecken=False); self.abgebrochen = False
    def neue_folge(self): self.folgen += 1
    def taste(self, t):
        self.tokens.append(t)
        if t == 'H': self.m.fl['H'] = 1
        if t == 'R': self.m.fl['H'] = 0
        if t == 'M+': self.mhalt = True
        if t == 'M-': self.mhalt = False
    def abbrechen(self): self.abgebrochen = True


def betrieb(**kw):
    r = FakeRechner()
    s = PultSteuerung(PULT, r, hochlauf_s=10, auslauf_s=2, bei_ende=r.abbrechen, **kw)
    s.netz_klick(0); s.tick(10.0)
    assert s.netz == BETRIEB
    r.taste('H'); r.tokens.clear()
    return s, r


class Netz(unittest.TestCase):
    def test_start_nur_netzschalter(self):
        r = FakeRechner(); s = PultSteuerung(PULT, r)
        self.assertEqual(s.netz, AUS)
        for t in ('H', 'R', 'E', 'K1', 'G', '1'): self.assertFalse(s.klick(t, 0), t)
        g, adr, or_, v = s.lampen()
        self.assertEqual((g['N'], g['B']), ('gruen', 'dunkel'))
        self.assertTrue(all(g[k] == 'dunkel' for k in g if k not in ('N', 'B')))
    def test_hochlauf_B_rot_dann_gruen(self):
        r = FakeRechner(); ev = []
        s = PultSteuerung(PULT, r, hochlauf_s=11.3, bei_betrieb=lambda: ev.append('betrieb'))
        s.netz_klick(5.0); self.assertEqual(s.lampen()[0]['B'], 'rot')
        self.assertFalse(s.klick('H', 6.0))                  # im Hochlauf nur Netzschalter
        s.tick(16.2); self.assertEqual(s.netz, HOCHLAUF)
        s.tick(16.3); self.assertEqual((s.netz, ev, s.lampen()[0]['B']), (BETRIEB, ['betrieb'], 'gruen'))
    def test_ausschalten_im_betrieb(self):
        s, r = betrieb()
        s.netz_klick(20.0); self.assertEqual((s.netz, s.lampen()[0]['B']), (AUSLAUF, 'dunkel'))
        self.assertTrue(r.abgebrochen)
        self.assertFalse(s.klick('H', 20.5))
        self.assertIsNone(s.tick(21.9)); self.assertEqual(s.tick(22.0), ENDE)
    def test_ausschalten_im_hochlauf(self):
        r = FakeRechner(); s = PultSteuerung(PULT, r, hochlauf_s=10, auslauf_s=2)
        s.netz_klick(0); s.netz_klick(3); self.assertEqual(s.netz, AUSLAUF)
        self.assertEqual(s.tick(5), ENDE)
    def test_schluessel_grafik(self):
        r = FakeRechner(); s = PultSteuerung(PULT, r)
        sch = lambda: [z['bild'] for z in s.zeichenliste() if z['id'] == 'schluessel'][0]
        self.assertEqual(sch(), 'schluessel_aus.png'); s.netz_klick(0); self.assertEqual(sch(), 'schluessel_ein.png')
        s.netz_klick(1); self.assertEqual(sch(), 'schluessel_aus.png')


class TonProbe:
    def __init__(self): self.ev = []
    def fade_laeuft(self): return False
    def fade_in(self): self.ev.append('fade_in')
    def grund_an(self): self.ev.append('grund')
    def fade_out(self): self.ev.append('fade_out')
    def alles_aus(self): self.ev.append('aus')


class Ton(unittest.TestCase):
    def test_ablauf(self):
        t = TonProbe(); s = PultSteuerung(PULT, FakeRechner(), hochlauf_s=10, auslauf_s=2, ton=t)
        s.netz_klick(0); s.tick(10); s.netz_klick(11); s.tick(13)
        self.assertEqual(t.ev, ['fade_in', 'grund', 'fade_out', 'aus'])
    def test_klick_im_hochlauf(self):
        t = TonProbe(); s = PultSteuerung(PULT, FakeRechner(), hochlauf_s=10, auslauf_s=2, ton=t)
        s.netz_klick(0); s.netz_klick(3); self.assertEqual(t.ev, ['fade_in', 'fade_out'])
    def test_rechnerton_ohne_spieler_und_mit_attrappe(self):
        import grafik_ton, time
        n = grafik_ton.RechnerTon(os.path.join(PROJ, 'ton'), spieler=None, meldung=False)
        n.befehl = None; n.winsound = None
        n.fade_in(); n.grund_an(); n.fade_out(); n.alles_aus()          # ohne Spieler: kein Fehler
        a = grafik_ton.RechnerTon(os.path.join(PROJ, 'ton'), spieler=['sleep'], meldung=False)   # 'sleep <pfad>' endet sofort mit Fehler
        a.grund_an(); time.sleep(0.2); a.alles_aus()
        for f in ('netz_ein_fade_in.wav', 'netz_aus_fade_out.wav', 'rechner_grundgeraeusch.wav'):
            self.assertTrue(os.path.isfile(os.path.join(PROJ, 'ton', f)), f)


class TonDauer(unittest.TestCase):
    def test_dauern_und_pegel(self):
        import grafik_ton, wave, array
        t = grafik_ton.RechnerTon(os.path.join(PROJ, 'ton'), meldung=False)
        self.assertAlmostEqual(t.dauer_fade_in(), 11.29, delta=0.02); self.assertAlmostEqual(t.dauer_fade_out(), 1.95, delta=0.02)
        f = t._lang_datei(); a = array.array('h'); a.frombytes(wave.open(f).readframes(44100))
        b = array.array('h'); b.frombytes(wave.open(os.path.join(PROJ, 'ton', 'rechner_grundgeraeusch.wav')).readframes(44100))
        self.assertAlmostEqual(max(map(abs, a)) / max(map(abs, b)), 0.8, delta=0.01); t.alles_aus()
    def test_B_rot_waehrend_ganzem_fade_in(self):
        s = PultSteuerung(PULT, FakeRechner(), hochlauf_s=11.29, auslauf_s=2.0)
        s.netz_klick(0)
        for t in (0.1, 5, 11.2): s.tick(t); self.assertEqual(s.lampen()[0]['B'], 'rot', t)
        s.tick(11.3); self.assertEqual(s.lampen()[0]['B'], 'gruen')
    def test_auslauf_wartet_auf_fade_out(self):
        class T(TonProbe):
            laeuft = True
            def fade_laeuft(self): return self.laeuft
        t = T(); s = PultSteuerung(PULT, FakeRechner(), hochlauf_s=1, auslauf_s=2, ton=t)
        s.netz_klick(0); s.tick(1); s.netz_klick(2); s.tick(4.1); self.assertEqual(s.netz, AUSLAUF)   # Ton laeuft noch
        t.laeuft = False; self.assertEqual(s.tick(4.2), ENDE)
        s2 = PultSteuerung(PULT, FakeRechner(), hochlauf_s=1, auslauf_s=2, ton=T()); s2.netz_klick(0); s2.tick(1); s2.netz_klick(2)
        self.assertIsNone(s2.tick(6.9)); self.assertEqual(s2.tick(7.1), ENDE)                                                         # haengender Spieler: nach 3 s Zugabe trotzdem Ende
        self.assertEqual(s.lampen()[0]['B'], 'dunkel')


class Tasten(unittest.TestCase):
    def test_startzustand(self):
        s, r = betrieb()
        self.assertTrue(s.taste_gedrueckt('H') and s.taste_gedrueckt('T'))
        self.assertTrue(s.taste_gedrueckt('K0'))
        self.assertFalse(any(s.taste_gedrueckt(k) for k in ('K1', 'K2', 'K3', 'R', 'SW', 'SP', 'BS', 'LS')))
    def test_klicktaste_04s(self):
        s, r = betrieb()
        self.assertTrue(s.klick('G', 100.0)); self.assertTrue(s.taste_gedrueckt('G'))
        s.tick(100.24); self.assertTrue(s.taste_gedrueckt('G')); s.tick(100.26); self.assertFalse(s.taste_gedrueckt('G'))
        self.assertEqual(r.tokens, ['G'])
    def test_wippe_HR(self):
        s, r = betrieb()
        self.assertFalse(s.klick('H', 1))                    # schon eingerastet: nichts
        self.assertTrue(s.klick('R', 1)); self.assertTrue(s.taste_gedrueckt('R') and not s.taste_gedrueckt('H'))
        self.assertEqual(r.tokens, ['R']); self.assertEqual(s.lampen()[0]['R'], 'hell'); self.assertEqual(s.lampen()[0]['H'], 'dunkel')
        self.assertTrue(s.klick('H', 2)); self.assertEqual(s.lampen()[0]['H'], 'hell')
    def test_rollensperre_bei_R(self):
        s, r = betrieb(); s.klick('R', 1); r.tokens.clear()
        for t in ('E', 'M', 'G', 'UE', 'T', 'SW', '1', 'B'): self.assertFalse(s.klick(t, 2), t)
        self.assertEqual(r.tokens, [])
        for t in ('K1', 'ST', 'SP', 'BS', 'LS', 'SW_umschalt', 'H'): self.assertTrue(s.klick(t, 3), t)
    def test_wippe_TSW(self):
        s, r = betrieb()
        self.assertTrue(s.klick('SW', 1)); self.assertTrue(s.taste_gedrueckt('SW') and not s.taste_gedrueckt('T'))
        self.assertFalse(s.klick('SW', 2)); self.assertTrue(s.klick('T', 3)); self.assertEqual(r.tokens, ['SW=1', 'SW=0'])
    def test_selektoren_einrasten_einzeln(self):
        s, r = betrieb()
        s.klick('SP', 1); s.klick('BS', 1); self.assertTrue(s.taste_gedrueckt('SP') and s.taste_gedrueckt('BS'))
        s.klick('SP', 2); self.assertFalse(s.taste_gedrueckt('SP')); self.assertTrue(s.taste_gedrueckt('BS'))
        self.assertEqual(r.tokens, ['SP+', 'BS+', 'SP-'])
        s.klick('SW_umschalt', 3); self.assertTrue(r.sw.unterdruecken); s.klick('SW_umschalt', 4); self.assertFalse(r.sw.unterdruecken)
        s.klick('LS', 5); self.assertTrue(s.taste_gedrueckt('LS')); self.assertNotIn('LS+', r.tokens)
    def test_kanaltasten_genau_eine_rastet(self):
        s, r = betrieb(); s.klick('K1', 10); self.assertEqual(r.tokens, ['K1']); s.tick(20)
        self.assertEqual([k for k in ('K0', 'K1', 'K2', 'K3') if s.taste_gedrueckt(k)], ['K1'])
        s.klick('K3', 21); self.assertEqual([k for k in ('K0', 'K1', 'K2', 'K3') if s.taste_gedrueckt(k)], ['K3'])
        s.klick('K3', 22); self.assertEqual([k for k in ('K0', 'K1', 'K2', 'K3') if s.taste_gedrueckt(k)], ['K3'])
        s.klick('R', 23); s.klick('K0', 24); self.assertEqual([k for k in ('K0', 'K1', 'K2', 'K3') if s.taste_gedrueckt(k)], ['K0'])   # auch bei R
    def test_halter_M_und_E(self):
        s, r = betrieb(); s.klick('R', 0); s.klick('H', 0); r.tokens.clear()
        s.klick('M', 1, umschalt=True); self.assertTrue(s.taste_gedrueckt('M')); s.tick(2); self.assertTrue(s.taste_gedrueckt('M'))
        s.klick('E', 3); s.loslassen('E', 3.1); s.klick('E', 4); s.loslassen('E', 4.1); self.assertEqual(r.tokens, ['M+', 'E+', 'E-', 'E+', 'E-'])
        self.assertFalse(s.klick('M', 5))                    # normaler Klick auf gehaltene Taste: nichts
        self.assertFalse(s.klick('R', 5))                    # R bei gehaltenem M: wirkungslos
        s.klick('M', 6, umschalt=True); self.assertFalse(s.taste_gedrueckt('M')); self.assertEqual(r.tokens[-1], 'M-')
        s.klick('E', 7, umschalt=True); self.assertTrue(s.taste_gedrueckt('E')); s.tick(9); self.assertTrue(s.taste_gedrueckt('E'))
        s.klick('E', 10, umschalt=True); self.assertFalse(s.taste_gedrueckt('E'))
        self.assertEqual(r.tokens[-2:], ['E+', 'E-'])           # Halter: E+ beim Einrasten, E- beim Loesen
    def test_E_niederdruecken_und_loslassen_getrennt(self):
        """Maustaste gedrueckt = E+, Maustaste losgelassen = E- (Handbuch: Niederdruecken Phase IV und I, Loslassen Phase II und III)."""
        s, r = betrieb(); s.klick('R', 0); s.klick('H', 0); r.tokens.clear()
        self.assertTrue(s.klick('E', 1.0)); self.assertEqual(r.tokens, ['E+'])       # nur Niederdruecken
        s.tick(1.5); self.assertTrue(s.taste_gedrueckt('E'))
        self.assertTrue(s.loslassen('E', 2.0)); self.assertEqual(r.tokens, ['E+', 'E-'])
        self.assertFalse(s.loslassen('E', 2.1)); self.assertEqual(r.tokens, ['E+', 'E-'])   # zweites Loslassen: nichts
    def test_E_halter_loslassen_der_maus_wirkt_nicht(self):
        s, r = betrieb(); s.klick('R', 0); s.klick('H', 0); r.tokens.clear()
        s.klick('E', 1.0, umschalt=True); self.assertEqual(r.tokens, ['E+'])
        self.assertFalse(s.loslassen('E', 1.1)); self.assertEqual(r.tokens, ['E+'])      # Umschalt+Klick haelt: kein E- beim Loslassen der Maus
        self.assertFalse(s.klick('E', 2.0)); self.assertEqual(r.tokens, ['E+'])          # normaler Klick auf gehaltene Taste: nichts
        self.assertFalse(s.klick('R', 2.1))                                              # R bei gehaltenem E: wirkungslos
        s.klick('E', 3.0, umschalt=True); self.assertEqual(r.tokens, ['E+', 'E-'])
    def test_E_fokusverlust_laesst_los(self):
        s, r = betrieb(); s.klick('R', 0); s.klick('H', 0); r.tokens.clear()
        s.klick('E', 1.0); s.fokus_verloren(1.5); self.assertEqual(r.tokens, ['E+', 'E-'])
    def test_umschalt_nur_bei_E_M(self):
        s, r = betrieb(); s.klick('G', 1, umschalt=True); s.tick(2); self.assertFalse(s.taste_gedrueckt('G'))
    def test_maus_halten_M(self):
        s, r = betrieb(); s.klick('M', 1.0); self.assertEqual(r.tokens[-1], 'M+'); s.tick(1.5); self.assertTrue(s.taste_gedrueckt('M'))
        s.loslassen('M', 1.6); self.assertEqual(r.tokens[-1], 'M-'); s.tick(1.9); self.assertFalse(s.taste_gedrueckt('M'))
    def test_kurzer_klick_M_bleibt_04s(self):
        s, r = betrieb(); s.klick('M', 1.0); s.loslassen('M', 1.05); s.tick(1.2); self.assertTrue(s.taste_gedrueckt('M')); s.tick(1.31); self.assertFalse(s.taste_gedrueckt('M'))
    def test_eingabetasten_nur_bei_erwartung(self):
        s, r = betrieb()
        self.assertFalse(s.klick('1', 1)); self.assertFalse(s.taste_gedrueckt('1')); self.assertEqual(r.m.k0.got, [])
        r.m.k0.erw = True
        self.assertTrue(s.klick('1', 2)); self.assertTrue(s.klick('PLUS', 2)); self.assertTrue(s.klick('ZR', 2))
        self.assertEqual(r.m.k0.got, ['1', '+', 'ZR']); self.assertTrue(s.taste_gedrueckt('1'))
    def test_computertastatur(self):
        s, r = betrieb(); r.m.k0.erw = True
        for c in ('1', 'b', 'D', '-', ',', '.', ':', ' '): self.assertTrue(s.tastatur(c, 1), c)
        self.assertEqual(r.m.k0.got, ['1', 'B', 'D', '-', ',', '.', ':', 'ZR'])
        self.assertFalse(s.tastatur('x', 1)); self.assertFalse(s.tastatur('G', 1))
    def test_fokusverlust_laesst_maustaste_los(self):
        s, r = betrieb(); s.klick('M', 1.0); s.klick('SP', 1.0); s.fokus_verloren(5.0)
        self.assertEqual(r.tokens[-1], 'M-'); self.assertTrue(s.taste_gedrueckt('SP'))


class Diagnose(unittest.TestCase):
    def test_log_und_titel(self):
        s, r = betrieb(); z = []; s.klick_log = z.append
        s.klick('R', 1); s.klick('E', 2); s.klick('1', 3)
        self.assertIn('stellung=R', z[1]); self.assertIn('ohne Wirkung', z[1]); self.assertIn('eingabe_erwartet=False', z[2])
        self.assertFalse(s.eingabe_erwartet()); r.m.k0.erw = True; self.assertTrue(s.eingabe_erwartet())
        s.klick('1', 4); self.assertIn('WIRKT', z[3])
    def test_bei_R_nur_mit_eingabe_halt(self):
        s, r = betrieb(); s.klick('R', 1)
        for t in ('E', 'M', 'G', 'UE', 'T', 'SW', '1', 'ZR', 'IS'): self.assertFalse(s.klick(t, 2), t)      # nie frei, ausser Eingabe-Halt
        r.m.k0.erw = True
        for t in ('E', 'M', 'G', 'UE', 'T', 'SW'): self.assertFalse(s.klick(t, 3), t)                      # auch im Eingabe-Halt gesperrt
        for t in ('1', 'ZR', 'IS'): self.assertTrue(s.klick(t, 3), t)                                       # Entriegelung (Entscheidung 15.10.2026)


class Beruhigung(unittest.TestCase):
    def _lauf(self, muster, schritte=100, dt=0.002):
        from grafik_pult import Mittelung
        m = Mittelung(); t = 0.0
        for i in range(schritte):
            m.probe({'a:0': muster(i)}, t); t += dt
        return m.kopie().get('a:0')
    def test_dauer_an_aus(self):
        self.assertEqual(self._lauf(lambda i: 1), 1); self.assertEqual(self._lauf(lambda i: 0), 0)
    def test_mehrheit(self):
        self.assertEqual(self._lauf(lambda i: 1 if i % 10 < 8 else 0), 1)        # 80 % an
        self.assertEqual(self._lauf(lambda i: 1 if i % 10 < 2 else 0), 0)        # 20 % an
    def test_hysterese_bei_50_prozent(self):
        from grafik_pult import Mittelung
        m = Mittelung(); t = 0.0
        for i in range(100): m.probe({'x': 1}, t); t += 0.002
        for i in range(100): m.probe({'x': i % 2}, t); t += 0.002                # 50 %: bleibt an
        self.assertEqual(m.kopie()['x'], 1)
    def test_sofort_bei_halt(self):
        from grafik_pult import Mittelung
        m = Mittelung(); m.sofort({'x': 1}); self.assertEqual(m.kopie()['x'], 1); m.sofort({'x': 0}); self.assertEqual(m.kopie()['x'], 0)
    def test_lampen_im_lauf_gemittelt_im_halt_genau(self):
        s, r = betrieb(); r.laeuft = True
        r.m.adr = 0o0001; s.mit.sofort(s._werte())
        r.m.adr = 0o0002                                                           # Momentaufnahme, noch nicht gemittelt
        self.assertEqual(s.lampen()[1], 0o0001)
        r.laeuft = False; self.assertEqual(s.lampen()[1], 0o0002)                  # Halt: genauer Stand sofort


class Anzeige(unittest.TestCase):
    def test_zeichenliste_vollstaendig_und_dateien_da(self):
        s, r = betrieb(); zl = s.zeichenliste()
        self.assertEqual(len([z for z in zl if z['id'].startswith('lampe:')]), 15)
        self.assertEqual(len([z for z in zl if z['id'].startswith('taste:')]), 38)
        for z in zl: self.assertTrue(os.path.isfile(os.path.join(PULT, 'grafiken', z['bild'])), z['bild'])
    def test_lampen_folgen_dem_rechner(self):
        s, r = betrieb(); r.m.fl['US'] = 1; r.m.adr = 0o1234; r.m.OR = 0o123; r.m.fl['V1'] = 1
        g, adr, or_, v = s.lampen(); self.assertEqual((g['US'], adr, or_, v['V1']), ('hell', 0o1234, 0o123, True))
    def test_treffer(self):
        s, r = betrieb(); t = s.m['tasten']['G']
        self.assertEqual(s.treffer(t['x'] + 5, t['y'] + 5), 'G'); sc = s.m['schluessel']; self.assertEqual(s.treffer(sc['cx'], sc['cy']), 'NETZ')
        self.assertIsNone(s.treffer(1, 1))


class Realer_Rechner(unittest.TestCase):
    """Pult-Steuerung gegen den echten Rechner (c8205_grafik.Rechner) ohne Fenster: H G R und Eingabe ueber Pult-Klicks."""
    def test_h_g_r_und_k0(self):
        try:
            import c8205_grafik as G
            from grafik_trommel import GrafikTrommel
        except Exception as e:
            self.skipTest(f'Kern nicht ladbar: {e}')
        import shutil, tempfile, threading, time
        d = tempfile.mkdtemp()
        troms = os.path.join(PROJ, 'Trommel', 'trommel.txt'); kopie = os.path.join(d, 'trommel.txt'); shutil.copy(troms, kopie)
        graph = G.lade_graph(os.path.join(PROJ, 'markdown-dateien')); tr = GrafikTrommel(kopie)
        r = G.Rechner(graph, tr, pult_modus=True)
        s = PultSteuerung(PULT, r, hochlauf_s=0.01, auslauf_s=0.01)
        stop = threading.Event()
        def lauf():
            try:
                while not stop.is_set(): r.lauf_wenn_gewuenscht(); time.sleep(0.002)
            except G.GrafikAbbruch: pass
        s.bei_betrieb = lambda: (r.taste('H'), r.taste('SW=0'), threading.Thread(target=lauf, daemon=True).start())
        try:
            s.netz_klick(0.0); s.tick(1.0)
            self.assertEqual(s.netz, BETRIEB); self.assertEqual(r.m.fl['H'], 1)
            self.assertTrue(s.klick('G', 2.0)); time.sleep(0.05)
            self.assertTrue(s.klick('R', 2.1))
            for _ in range(200):                              # warten, bis der Rechner (Beispiel: Zelle 0000) im Eingabe-Halt oder Halt ist
                time.sleep(0.01)
                if r.m.k0.erwartet('T') or not r.laeuft: break
            time.sleep(0.2)                                   # Mittelung braucht ein Fenster (40 ms) bis zum neuen Zustand
            self.assertEqual(s.lampen()[0]['R'] == 'hell', r.m.fl['H'] == 0)
        finally:
            stop.set(); r.abbrechen(); tr.schliessen(); shutil.rmtree(d, ignore_errors=True)


class KepUeberPult(unittest.TestCase):
    """Gleiches Beispiel wie der Stufe-1-Lauf (kep_eingabe.txt, H G R), aber die K0-Zeichen kommen als Klicks auf die Pult-Eingabetasten.
    Erwartung: das Soll von Tests/bsp_5_18_kep.txt (Unbedingter Stop, BZ=3002, AC=0, G4-018; frueher BZ=2404, AC=22060635124 aus aelterer Fassung)."""
    def test_kep(self):
        try:
            import c8205_grafik as G
            from grafik_trommel import GrafikTrommel
            from c8205_interp import octs
        except Exception as e:
            self.skipTest(f'Kern nicht ladbar: {e}')
        import shutil, tempfile, threading, time
        d = tempfile.mkdtemp(); kopie = os.path.join(d, 'trommel.txt')
        shutil.copy(os.path.join(PROJ, 'Trommel', 'trommel.txt'), kopie)
        # G4-018: Das KEP-Programm steht nicht auf der mitgelieferten Trommel, sondern in Tests/bsp_5_18_kep.txt (Zeilen ab 0000, wie dort
        # beim TEST-Lauf in die Trommel geschrieben). Es wird in die KOPIE geschrieben; die gemeinsame trommel.txt bleibt unberuehrt.
        import c8205_interp as I
        kep = I.Test(os.path.join(PROJ, 'Tests', 'bsp_5_18_kep.txt'))
        mem = {}
        with open(kopie, encoding='utf-8', newline='') as fh:
            for z in fh:
                mm = I.TROMMEL_ZEILE_RE.match(z)
                mem[int(mm.group(1), 8)] = int(mm.group(2), 8)
        mem.update({a & I.MASK12: w & I.MASK33 for a, w in kep.mem.items()})
        with open(kopie, 'w', encoding='utf-8', newline='') as fh:
            fh.write(''.join(f'{a:04o}: {mem.get(a, 0):011o}\n' for a in range(4096)))
        tr = GrafikTrommel(kopie); r = G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), tr, pult_modus=True)
        s = PultSteuerung(PULT, r, hochlauf_s=0.01, auslauf_s=0.01, tastenzeit_s=0.0)
        name = {'.': 'PUNKT', ':': 'DOPPELPUNKT', 'ZR': 'ZR'}
        toks = [z.strip() for z in open(os.path.join(PROJ, 'Test-virtuelleGeraete', 'T-SW-Eingabe', 'kep_eingabe.txt'), encoding='utf-8') if z.strip() and not z.startswith('#')]
        stop = threading.Event()
        def lauf():
            try:
                while not stop.is_set(): r.lauf_wenn_gewuenscht(); time.sleep(0.002)
            except G.GrafikAbbruch: pass
        s.bei_betrieb = lambda: (r.taste('H'), r.taste('SW=0'), threading.Thread(target=lauf, daemon=True).start())
        try:
            s.netz_klick(0.0); s.tick(1.0)
            s.klick('G', 1.0); s.klick('R', 1.0)
            n = 0; t0 = time.time()
            while n < len(toks) and time.time() - t0 < 60:
                if s.klick(name.get(toks[n], toks[n]), 2.0): n += 1
                else: time.sleep(0.001)
            self.assertEqual(n, len(toks))
            for _ in range(500):
                if r.m.halted and not r.laeuft: break
                time.sleep(0.01)
            m = r.m
            wahr, zeilen = I.pruefe_ergebnis(kep, m)       # Soll steht in Tests/bsp_5_18_kep.txt (BZ=3002 AC=0, US=1, Zellen 3000 bis 3004); fruehere Erwartung 2404 war aus einer aelteren Fassung
            self.assertTrue(wahr, '\n'.join(map(str, zeilen)))
            self.assertEqual((octs(m.BZ, 4), octs(m.AC, 11)), ('3002', '00000000000'))
        finally:
            stop.set(); r.abbrechen(); tr.schliessen(); shutil.rmtree(d, ignore_errors=True)


class HwCheck(unittest.TestCase):
    """HW-Check-Fenster (--HWCHECK): Formatierung ohne Tkinter, Einblick in die Trommel, Fenster mit Ersatzmodul."""
    def test_gruppen4(self):
        from grafik_hwcheck import gruppen4
        self.assertEqual(gruppen4(0o22060635124, 11), '2206 0635 124')      # von LINKS: 4 + 4 + 3 (HW-003)
        self.assertEqual(gruppen4(0, 11), '0000 0000 000')
        self.assertEqual(gruppen4(0o77777777777, 11), '7777 7777 777')
        self.assertEqual(gruppen4(0o17, 4), '0017')
    def test_zeilen(self):
        from grafik_hwcheck import hwcheck_zeilen
        tr = types.SimpleNamespace(einblick=lambda a: {0o1234: 0o12345670123}.get(a))
        m = types.SimpleNamespace(BZ=0o2404, adr=0o10, OR=0o25, AC=0o22060635124, AR=0o1234, trommel=tr)
        z = hwcheck_zeilen(m)
        self.assertEqual([n for n, w in z][:4], ['BZ', 'BR', 'Spur Sektor', 'AC'])
        self.assertEqual(len(z), 6); self.assertEqual(z[5], ('Haltzeit', '     ---.- ms'))      # HW-004: sechste Zeile, ohne Messung (kein m.haltuhr)
        self.assertEqual(z[0][1], '2404'); self.assertEqual(z[1][1], '0010 025')
        self.assertEqual(z[2][1], '024 34')                      # AR=1234 oktal: Spur 024 (=AR>>5), Sektor 34 (=AR&037)
        self.assertEqual(z[3][1], '2206 0635 124')
        self.assertTrue(z[4][0].startswith('<<AR>>')); self.assertIn('AR=1234', z[4][0]); self.assertEqual(z[4][1], '1234 5670 123')
        for ar in (0, 0o37, 0o40, 0o7777):                       # Randwerte: 0 00 / 0 37 / 1 00 / 177 37
            m.AR = ar; self.assertEqual(hwcheck_zeilen(m)[2][1], f'{ar >> 5:03o} {ar & 0o37:02o}')
        self.assertEqual(hwcheck_zeilen(m)[2][1], '177 37')
        m.trommel = types.SimpleNamespace()                      # kein Einblick: Platzhalter, kein Fehler
        self.assertEqual(hwcheck_zeilen(m)[4][1], '---- ---- ---')
    def test_einblick_ohne_nebenwirkung(self):
        try:
            from grafik_trommel import GrafikTrommel
        except Exception as e:
            self.skipTest(f'Kern nicht ladbar: {e}')
        import shutil, tempfile
        d = tempfile.mkdtemp(); kopie = os.path.join(d, 'trommel.txt')
        shutil.copy(os.path.join(PROJ, 'Trommel', 'trommel.txt'), kopie)
        tr = GrafikTrommel(kopie)
        try:
            erwartet = {}
            for z in open(kopie, encoding='utf-8'):
                if ':' in z and not z.startswith('#'):
                    a, w = z.split(':')[:2]; erwartet[int(a, 8)] = int(w.split()[0], 8)
            vorher = tr.statistik()
            for a in (0, 1, 0o1000, 0o7777): self.assertEqual(tr.einblick(a), erwartet.get(a, 0), oct(a))
            nachher = tr.statistik()
            self.assertEqual((vorher['rd_wr_zugriffe'], vorher['wartezeit_summe_ticks_aufrufer']), (nachher['rd_wr_zugriffe'], nachher['wartezeit_summe_ticks_aufrufer']))
        finally:
            tr.schliessen(); shutil.rmtree(d, ignore_errors=True)
        self.assertIsNone(tr.einblick(0))                       # nach dem Schliessen: kein Zugriff
    def test_rueckfall_ohne_einblick(self):
        """grafik_trommel.py ohne einblick() (aelterer Stand): der HW-Check liest ueber trommel.T.lesen (HW-003)."""
        import grafik_hwcheck as H
        T = types.SimpleNamespace(lesen=lambda a: {0o1234: 0o12345670123}.get(a, 0))
        tr = types.SimpleNamespace(T=T, eingeschaltet=True)                     # keine Methode einblick
        m = types.SimpleNamespace(BZ=0, adr=0, OR=0, AC=0, AR=0o1234, trommel=tr)
        z = H.hwcheck_zeilen(m)
        self.assertEqual(z[4][1], '1234 5670 123'); self.assertIsNone(H.LETZTER_FEHLER)
        tr.eingeschaltet = False                                                # geschlossen: Platzhalter, Grund gemerkt
        self.assertEqual(H.hwcheck_zeilen(m)[4][1], '---- ---- ---'); self.assertIn('nicht eingeschaltet', H.LETZTER_FEHLER)
        tr2 = types.SimpleNamespace(einblick=lambda a: 1 / 0)                   # Ausnahme: Platzhalter, Grund gemerkt
        m.trommel = tr2
        self.assertEqual(H.hwcheck_zeilen(m)[4][1], '---- ---- ---'); self.assertIn('ZeroDivisionError', H.LETZTER_FEHLER)
    def test_haltzeit_zeile_und_messung(self):
        """HW-004 / HZ-001: ms zwischen Start (R) und Halt bzw. zwischen zwei Halts; Art aus dem Haltgrund, wenn beim Halt noch offen."""
        import grafik_haltzeit as HZ
        from grafik_hwcheck import hwcheck_zeilen
        t = [10.0]
        u = HZ.HaltZeit(zeit=lambda: t[0]); g = ['']; u.grund_fn = lambda: g[0]
        m = types.SimpleNamespace(BZ=0, adr=0, OR=0, AC=0, AR=0, trommel=types.SimpleNamespace(), haltuhr=u)
        self.assertEqual(hwcheck_zeilen(m)[5][1], '     ---.- ms')
        u.halt(HZ.EA)                                              # Halt ohne Start: keine Zeit, aber Bezug fuer den naechsten
        self.assertIsNone(u.lesen())
        u.start(); t[0] = 10.2505; u.halt(HZ.EA)                    # Start -> E/A-Halt
        self.assertEqual(hwcheck_zeilen(m)[5][1], '     250.5 ms  R -> E/A-Halt')
        u.weiter(); t[0] = 10.3005; g[0] = 'Unbedingter Stop (US:=1)'; u.halt(None)    # Halt -> Halt (Wartezeit zaehlt mit)
        self.assertEqual(hwcheck_zeilen(m)[5][1], '      50.0 ms  E/A-Halt -> Stopp')
        self.assertAlmostEqual(u.lesen()[3], 50.0, places=6)                             # reine Laufzeit seit der Fortsetzung (hier gleich)
        u.start(); t[0] = 11.3005; g[0] = 'Fehler bei Eingabe (FE): gerade Zahl'; u.halt(None)
        self.assertEqual(hwcheck_zeilen(m)[5][1], '    1000.0 ms  R -> Fehler')
        u.start(); t[0] = 11.4005; g[0] = 'Halt wegen Ueberlauf (FUE bereits 1)'; u.halt(None)
        self.assertEqual(hwcheck_zeilen(m)[5][1], '     100.0 ms  R -> Fehler')
    def test_haltzeit_nur_rechnerzeit(self):
        """HZ-003: die Anzeige zeigt die reine Rechnerzeit seit der Fortsetzung, nicht die Wartezeit im Halt; nur_lauf=False gibt die Zeit mit Wartezeit."""
        import grafik_haltzeit as HZ
        t = [20.0]
        u = HZ.HaltZeit(zeit=lambda: t[0]); u.grund_fn = lambda: ''
        u.start(); t[0] = 20.1; u.halt(HZ.EA)
        self.assertEqual(HZ.zeile(u.lesen()), '     100.0 ms  R -> E/A-Halt')
        t[0] = 20.5; u.weiter(); t[0] = 20.585; u.halt(HZ.EA)                             # 485 ms Halt -> Halt, davon 85 ms Rechnen
        self.assertEqual(HZ.zeile(u.lesen()), '      85.0 ms  E/A-Halt -> E/A-Halt')
        self.assertEqual(HZ.zeile(u.lesen(), nur_lauf=False), '     485.0 ms  E/A-Halt -> E/A-Halt')
    def test_haltzeit_einzelschritt(self):
        """HZ-004: ein Einzelschritt (E) wird gemessen: 'E -> Halt'; endet er im Stopp, steht dort 'E -> Stopp'; R misst weiter ab dem Start."""
        import grafik_haltzeit as HZ
        t = [30.0]
        u = HZ.HaltZeit(zeit=lambda: t[0]); g = ['']; u.grund_fn = lambda: g[0]
        self.assertEqual(HZ.zeile(u.lesen()), '     ---.- ms')
        u.start(HZ.SCHRITT); t[0] = 30.0005; u.halt(HZ.SCHRITT_ENDE)
        self.assertEqual(HZ.zeile(u.lesen()), '       0.5 ms  E -> Halt')
        u.start(HZ.SCHRITT); t[0] = 30.002; g[0] = 'Unbedingter Stop (US:=1)'; u.halt(None)
        self.assertEqual(HZ.zeile(u.lesen()), '       1.5 ms  E -> Stopp')
        u.start(); t[0] = 30.102; u.halt(HZ.EA)
        self.assertEqual(HZ.zeile(u.lesen()), '     100.0 ms  R -> E/A-Halt')
    def test_haltzeit_im_rechner(self):
        """Der echte Rechner meldet Start (R) und Halt (m.halted von False auf True) der HaltZeit; ein erneutes Setzen zaehlt nicht."""
        import c8205_grafik as G
        from grafik_trommel import GrafikTrommel
        r = G.Rechner({}, types.SimpleNamespace(), pult_modus=True)
        self.assertIs(r.m.haltuhr, r.haltuhr)
        r.haltuhr.zeit = lambda: 5.0; r._taste('R', [])
        r.haltuhr.zeit = lambda: 5.5; r.m.halt_grund = 'Bedingter Stop (BS:=1)'; r.m.halted = True
        self.assertEqual(r.haltuhr.lesen()[:3], (500.0, 'R', 'Stopp')); n = r.haltuhr.anzahl
        r.m.halted = True; self.assertEqual(r.haltuhr.anzahl, n)       # schon gehalten: kein zweiter Halt
        r.m.halted = False; r.haltuhr.zeit = lambda: 6.0; r.m.halt_art = G.FEHLER; r.m.halted = True
        self.assertEqual(r.haltuhr.lesen()[:3], (500.0, 'Stopp', 'Fehler'))
    def test_haltzeit_ea_halt_der_k0_warteschlange(self):
        import threading, time as _t
        from grafik_k0 import K0Warteschlange
        k = K0Warteschlange(types.SimpleNamespace(fl={'SW': 1}), takt=0.01); ereignis = []
        k.bei_halt = lambda: ereignis.append('halt'); k.bei_weiter = lambda: ereignis.append('weiter')
        th = threading.Thread(target=lambda: ereignis.append(k.naechstes()), daemon=True); th.start()
        _t.sleep(0.1); k.einspeisen('a', 'SW'); th.join(2)
        self.assertEqual(ereignis, ['halt', 'weiter', 'a'])             # genau ein Halt je Eingabebefehl, danach Fortsetzung
        k.einspeisen('b', 'SW'); self.assertEqual(k.naechstes(), 'b')   # Zeichen schon da: kein E/A-Halt
        self.assertEqual(ereignis, ['halt', 'weiter', 'a'])
    def test_fenster(self):
        from grafik_hwcheck import HwCheckFenster
        class W:
            def __init__(s, *a, **k): s.cfg = dict(k); s.bound = {}
            def title(s, x): s.titel = x
            def resizable(s, *a): pass
            def protocol(s, n, f): s.bound[n] = f
            def geometry(s, g): s.geo = g
            def grid(s, **k): pass
            def configure(s, **k): s.cfg.update(k)
        tk = types.SimpleNamespace(Toplevel=lambda root: W(), Label=lambda win, **k: W(**k))
        tr = types.SimpleNamespace(einblick=lambda a: 5)
        m = types.SimpleNamespace(BZ=1, adr=2, OR=3, AC=4, AR=5, trommel=tr)
        f = HwCheckFenster(object(), m, tk=tk)
        self.assertEqual(f.win.bound['WM_DELETE_WINDOW'](), None)           # X wirkt nicht
        self.assertEqual(f._werte[0].cfg['text'], '0001'); self.assertEqual(f._werte[2].cfg['text'], '000 05'); self.assertEqual(f._werte[4].cfg['text'], '0000 0000 005')
        self.assertEqual(len(f._werte), 6); self.assertEqual(f._werte[5].cfg['text'], '     ---.- ms')      # HW-004
        m.BZ = 0o2404; f.aktualisieren(); self.assertEqual(f._werte[0].cfg['text'], '2404')


class EUnterM(unittest.TestCase):
    """E unter gehaltenem M erhoeht BZ und AR gemeinsam; die Lampenreihe AR (= Adressteil des BR, m.adr) zeigt das erhoehte AR
    (Handbuch; Interpreter 0.03-015, GRAFIK G2-011). Gilt in beiden Betriebsarten (pult_modus True/False, damit TEST und GRAFIK gleich bleiben)."""
    def _rechner(self, pult_modus):
        try:
            import c8205_grafik as G
            from grafik_trommel import GrafikTrommel
        except Exception as e:
            self.skipTest(f'Kern nicht ladbar: {e}')
        import shutil, tempfile
        d = tempfile.mkdtemp(); kopie = os.path.join(d, 'trommel.txt')
        shutil.copy(os.path.join(PROJ, 'Trommel', 'trommel.txt'), kopie)
        tr = GrafikTrommel(kopie)
        self.addCleanup(lambda: (tr.schliessen(), shutil.rmtree(d, ignore_errors=True)))
        return G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), tr, pult_modus=pult_modus)

    def _pruefe(self, pult_modus):
        r = self._rechner(pult_modus); m = r.m
        for t in ('H', 'G', 'M+'):
            r.taste(t)
        r.taste('E')                                   # erstes E nach G: BZ := 1, AR := 1
        self.assertEqual((m.BZ, m.AR, m.adr), (1, 1, 1))
        r.taste('E')
        self.assertEqual((m.BZ, m.AR, m.adr), (2, 2, 2))
        r.taste('E')
        self.assertEqual((m.BZ, m.AR, m.adr), (3, 3, 3))
        self.assertEqual(m.AC, 0o4 << 9)               # BZ+1 im Adressfeld des AC
        r.taste('M-')
        self.assertEqual((m.BZ, m.AR, m.adr), (3, 3, 3))   # Loslassen von M aendert die Anzeige nicht

    def test_pult_modus(self):
        self._pruefe(True)

    def test_test_modus(self):
        self._pruefe(False)

    def test_lampenreihe(self):
        """PultSteuerung.lampen() liefert den Adressteil des BR (Lampenreihe AR) = erhoehtes AR."""
        r = self._rechner(True)
        s = PultSteuerung(PULT, r, hochlauf_s=0.0, auslauf_s=0.0, tastenzeit_s=0.0)
        s.netz_klick(0.0); s.tick(1.0)
        self.assertEqual(s.netz, BETRIEB)
        for t in ('H', 'G', 'M+', 'E', 'E'):
            r.taste(t)
        self.assertEqual(s.lampen()[1], 2)


def _zellen(zellen):
    """Trommeldatei mit den angegebenen Zellen {Adresse: Wort} (alle anderen 0); Rueckgabe (Ordner, Pfad). Wort: Adresse << 9 | Operation (3 Oktalstellen)."""
    import tempfile
    d = tempfile.mkdtemp(); p = os.path.join(d, 'trommel.txt')
    with open(p, 'w') as f:
        for a in range(4096):
            f.write(f'{a:04o}: {zellen.get(a, 0):011o}\n')
    return d, p


def _z(adr, op):
    return (adr << 9) | op


# kleines Programm: Transport 0100 -> AC, Transport 0101 -> AC, Sprung 0003, Transport AC -> 0100, Sprung 0000
PROGRAMM = {0o0000: _z(0o0100, 0o211), 0o0001: _z(0o0101, 0o211), 0o0002: _z(0o0003, 0o000), 0o0003: _z(0o0100, 0o240),
            0o0004: _z(0o0000, 0o000), 0o0100: 0o1234, 0o0101: 0o4321}


class EGetrennt(unittest.TestCase):
    """Niederdruecken (E+: Phase IV und I, Halt vor Phase II = Knoten 8) und Loslassen (E-: Phase II und III, Halt vor Knoten 19) sind getrennt
    (Handbuch, Taste E; GRAFIK G2-012). Das Token 'E' (kurzer Anschlag) bleibt gleich E+ und sofort E-."""
    def _rechner(self, pult_modus=True, zellen=None):
        try:
            import c8205_grafik as G
            from grafik_trommel import GrafikTrommel
        except Exception as e:
            self.skipTest(f'Kern nicht ladbar: {e}')
        import shutil
        d, p = _zellen(PROGRAMM if zellen is None else zellen)
        tr = GrafikTrommel(p)
        self.addCleanup(lambda: (tr.schliessen(), shutil.rmtree(d, ignore_errors=True)))
        r = G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), tr, pult_modus=pult_modus)
        r._tr = tr
        return r

    @staticmethod
    def _zu(r):
        """Trommel schliessen: das C-Modul kennt nur EINE eingeschaltete Trommel, zwei Rechner gleichzeitig gehen nicht."""
        r._tr.schliessen()

    @staticmethod
    def _zustand(r):
        m = r.m
        return (m.BZ, m.AR, m.AC, m.OR, m.adr, tuple(sorted(m.fl.items())), m.vor_phase2, m.br_aufgestellt, r.e_gedrueckt)

    @staticmethod
    def _folge(r, tokens):
        for t in tokens:
            r.taste(t)

    def test_getrennt_gleich_ganzer_schritt(self):
        """E+ gefolgt von E- ergibt nach jedem Schritt genau den Zustand des ganzen Schritts 'E' (12 Schritte, ueber Spruenge hinweg)."""
        def verlauf(pm, tokens):
            r = self._rechner(pm); self._folge(r, ['H', 'G']); z = []
            for i in range(12):
                self._folge(r, tokens); z.append(self._zustand(r))
            self.assertIn(0o4321, {x[2] for x in z})              # das Programm hat wirklich gerechnet (AC aus Zelle 0101)
            self._zu(r)
            return z
        for pm in (True, False):
            self.assertEqual(verlauf(pm, ['E']), verlauf(pm, ['E+', 'E-']), f'pult_modus={pm}')

    def test_zwischenzustand_nach_niederdruecken(self):
        """Nach E+ steht der Automat vor Phase II: im BR noch der alte Befehl, dessen Operation (Phase IV) ist ausgefuehrt; erst E- holt den naechsten Befehl."""
        r = self._rechner(); m = r.m
        self._folge(r, ['H', 'G', 'E'])                          # Schritt 1: BR = 0100 211 (Transport 0100 -> AC), noch nicht ausgefuehrt
        self.assertEqual((m.adr, m.OR, m.AC), (0o0100, 0o211, 0))
        r.taste('E+')
        self.assertTrue(m.vor_phase2); self.assertTrue(r.e_gedrueckt)
        self.assertEqual((m.adr, m.OR), (0o0100, 0o211))        # BR noch der alte Befehl
        self.assertEqual(m.AC, 0o1234)                          # Phase IV: seine Operation ist ausgefuehrt
        r.taste('E-')
        self.assertFalse(m.vor_phase2); self.assertFalse(r.e_gedrueckt)
        self.assertEqual((m.adr, m.OR), (0o0101, 0o211))        # Phase II: naechster Befehl im BR (Transport 0101 -> AC)
        self.assertEqual(m.BZ, 2)

    def test_unter_M(self):
        """Unter gehaltenem M: E+ erhoeht BZ und AR (und die Lampenreihe AR), E- bleibt ohne Wirkung; danach wie bisher."""
        a = self._rechner()
        self._folge(a, ['H', 'G', 'M+', 'E', 'E', 'E', 'M-', 'E'])
        z_a = self._zustand(a); self._zu(a)
        b = self._rechner()
        self._folge(b, ['H', 'G', 'M+', 'E+'])
        self.assertEqual((b.m.BZ, b.m.AR, b.m.adr), (1, 1, 1))
        vor = self._zustand(b); b.taste('E-')
        self.assertEqual(self._zustand(b)[:5], vor[:5]); self.assertFalse(b.e_gedrueckt)   # Loslassen unter M: keine Wirkung
        self._folge(b, ['E+', 'E-', 'E+', 'E-', 'M-', 'E+', 'E-'])
        self.assertEqual(z_a, self._zustand(b))

    def test_G_bei_gehaltenem_E(self):
        """G bei niedergedrueckter Taste E loescht wie bisher; das Loslassen fuehrt dann keinen Schritt mehr aus."""
        r = self._rechner(); m = r.m
        self._folge(r, ['H', 'G', 'E', 'E+', 'G'])
        self.assertEqual((m.adr, m.OR, m.AR), (0, 0, 0))
        vor = self._zustand(r)[:5]
        zeile = r.taste('E-')
        self.assertEqual(self._zustand(r)[:5], vor); self.assertFalse(r.e_gedrueckt)
        self.assertIn('kein Schritt offen', zeile)

    def test_unzulaessige_folgen(self):
        r = self._rechner(); self._folge(r, ['H', 'G'])
        vor = self._zustand(r)
        eff = []; self.assertFalse(r._taste('E-', eff)); self.assertEqual(self._zustand(r), vor)      # E- ohne E+
        self.assertTrue(r._taste('E+', []))
        eff = []; self.assertFalse(r._taste('E+', eff)); self.assertTrue(r.e_gedrueckt)               # E+ bei gedrueckter Taste
        self.assertTrue(r._taste('E-', []))
        ok, eff = r.folge(['G', 'E+'])
        self.assertFalse(ok); self.assertTrue(any('gedrueckter Taste E' in z for z in eff))

    def test_ohne_schalter_H(self):
        r = self._rechner()                                      # H noch nicht gesetzt
        vor = self._zustand(r)
        self.assertIn('nur bei Schalter H', r.taste('E+'))
        r.taste('E-')
        self.assertEqual(self._zustand(r)[:5], vor[:5]); self.assertFalse(r.e_gedrueckt)

    def test_lampenreihe_waehrend_E_gehalten(self):
        """Pult mit echtem Rechner: Beim Halten von E zeigt die Lampenreihe AR/OR den alten Befehl, nach dem Loslassen den neuen."""
        r = self._rechner()
        s = PultSteuerung(PULT, r, hochlauf_s=0.0, auslauf_s=0.0, tastenzeit_s=0.0)
        s.netz_klick(0.0); s.tick(1.0)
        self.assertEqual(s.netz, BETRIEB)
        self._folge(r, ['H', 'G', 'E'])
        self.assertEqual(s.lampen()[1], 0o0100)
        s.klick('E', 2.0)                                       # Niederdruecken
        self.assertEqual(s.lampen()[1], 0o0100); self.assertEqual(r.m.AC, 0o1234)
        s.loslassen('E', 3.0)                                   # Loslassen
        self.assertEqual(s.lampen()[1], 0o0101)


class DebugLog(unittest.TestCase):
    """--DEBUGLOG: Protokolldatei mit Klicks, Tokens und Rechnerzustand; ohne Start wirkungslos."""
    def test_log(self):
        import tempfile, shutil, grafik_debuglog as DL
        DL.log('X', 'ohne Start: kein Fehler')
        d = tempfile.mkdtemp(); pfad = os.path.join(d, 'x.log')
        try:
            import c8205_grafik as G
            from grafik_pult import PultSteuerung, BETRIEB
            DL.starten(pfad)
            r = G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), types.SimpleNamespace(rd=lambda a: 0, wr=lambda a, w: None), pult_modus=True)
            s = PultSteuerung(os.path.join(PROJ, 'pult'), r, hochlauf_s=0.01, auslauf_s=0.01)
            s.klick_log = lambda z: DL.log('KLICK', z)
            s.netz_klick(time.monotonic()); s.tick(time.monotonic() + 1)
            self.assertEqual(s.netz, BETRIEB)
            r.taste('H'); s.klick('G', time.monotonic())
            DL._L.f.flush()
            txt = open(pfad, encoding='utf-8').read()
            self.assertIn('KLICK', txt); self.assertIn('Pult-Klick G', txt); self.assertIn('TOKEN', txt); self.assertIn('an den Rechner: G', txt)
            self.assertIn('RECHNER', txt); self.assertIn('BZ=0000', txt)
        finally:
            if DL._L: DL._L.f.close()
            DL._L = None; shutil.rmtree(d, ignore_errors=True)


class Klickspur(unittest.TestCase):
    """Klickspur: Aufzeichnung der Pult-Klicks und Wiedergabe im selben Zeitabstand (grafik_debuglog.Aufzeichnung / Wiedergabe)."""
    FOLGE = [(100.0, 'klick', 'K1', False), (100.2, 'klick', 'E', False), (100.35, 'los', 'E', False),
             (100.5, 'klick', 'M', True), (101.0, 'klick', 'M', True), (101.2, 'klick', 'R', False), (101.3, 'klick', 'E', False)]

    def _aufnehmen(self, pfad):
        import grafik_debuglog as DL
        s, r = betrieb()
        s.aufzeichnung = DL.Aufzeichnung(pfad, kopf={'trommel_md5': 'abc'})
        for t, art, taste, um in self.FOLGE:
            if art == 'klick': s.klick(taste, t, umschalt=um)
            else: s.loslassen(taste, t)
        s.aufzeichnung.schliessen()
        return s, r

    def test_aufzeichnen_laden_wiedergeben(self):
        import tempfile, shutil, grafik_debuglog as DL
        d = tempfile.mkdtemp(); pfad = os.path.join(d, 'spur.txt')
        try:
            s1, r1 = self._aufnehmen(pfad)
            txt = open(pfad, encoding='utf-8').read().splitlines()
            self.assertEqual(txt[0], '# C8205-Klickspur 1'); self.assertIn('# trommel_md5: abc', txt)
            daten = [z for z in txt if not z.startswith('#')]
            self.assertEqual(len(daten), 7)                              # alle Klicks, auch der ohne Wirkung (E bei R)
            self.assertIn('0.000 klick K1 wirkt=1', daten[0]); self.assertIn('0.350 los E', daten[2])
            self.assertIn('klick M umschalt wirkt=1', daten[3]); self.assertIn('1.300 klick E wirkt=0', daten[6])
            kopf, ev = DL.lade_klickspur(pfad)
            self.assertEqual(kopf['trommel_md5'], 'abc'); self.assertEqual(len(ev), 7)
            s2, r2 = betrieb()
            w = DL.Wiedergabe(s2, ev); self.assertIsNone(w.bis_naechster(0)); w.starten(500.0)
            self.assertEqual(w.bis_naechster(500.0), 0.0)
            self.assertEqual(w.faellige(500.1), 1); self.assertEqual(r2.tokens, ['K1'])         # nur t=0 ist faellig
            self.assertAlmostEqual(w.bis_naechster(500.1), 0.1, places=6)
            self.assertEqual(w.faellige(500.25), 1)                                            # E bei 0.2
            self.assertEqual(w.faellige(503.0), 5); self.assertTrue(w.fertig); self.assertIsNone(w.bis_naechster(503.0))
            self.assertEqual(r2.tokens, r1.tokens); self.assertEqual(w.abweichungen, 0)
            self.assertEqual((sorted(s2.rastet), sorted(s2.halter)), (sorted(s1.rastet), sorted(s1.halter)))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_abweichung_wird_gezaehlt(self):
        import tempfile, shutil, grafik_debuglog as DL
        d = tempfile.mkdtemp(); pfad = os.path.join(d, 'spur.txt')
        try:
            self._aufnehmen(pfad); kopf, ev = DL.lade_klickspur(pfad)
            s2, r2 = betrieb(); s2.klick('R', 1.0)                       # Startzustand anders: Stellung R, E ist gesperrt
            w = DL.Wiedergabe(s2, ev); w.starten(0.0); w.faellige(10.0)
            self.assertGreaterEqual(w.abweichungen, 1)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_ohne_aufzeichnung_keine_wirkung(self):
        s, r = betrieb(); self.assertIsNone(s.aufzeichnung); self.assertTrue(s.klick('K1', 1.0))

    def test_formatfehler(self):
        import tempfile, shutil, grafik_debuglog as DL
        d = tempfile.mkdtemp()
        def schreibe(inhalt):
            p = os.path.join(d, 'x.txt'); 
            with open(p, 'w', encoding='utf-8') as fh: fh.write(inhalt)
            return p
        try:
            with self.assertRaises(ValueError): DL.lade_klickspur(os.path.join(d, 'gibt_es_nicht.txt'))
            with self.assertRaises(ValueError): DL.lade_klickspur(schreibe('irgendwas\n'))
            with self.assertRaises(ValueError) as c: DL.lade_klickspur(schreibe('# C8205-Klickspur 1\n0.0 klick E\n1.0 tanz X\n'))
            self.assertIn('Zeile 3', str(c.exception))
            with self.assertRaises(ValueError): DL.lade_klickspur(schreibe('# C8205-Klickspur 1\n2.0 klick E\n1.0 klick E\n'))
            kopf, ev = DL.lade_klickspur(schreibe('# C8205-Klickspur 1\n# frei: Kommentar\n\n0.5 klick G\n'))
            self.assertEqual(ev, [(0.5, 'klick', 'G', False, None)])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_schalter_fehler(self):
        import tempfile, shutil, c8205_grafik as G
        d = tempfile.mkdtemp()
        try:
            self.assertEqual(G.hauptprogramm(['--WIEDERGABE', os.path.join(d, 'fehlt.txt')]), G.RC_START)
            p = os.path.join(d, 's.txt')
            with open(p, 'w') as fh: fh.write('# C8205-Klickspur 1\n')
            self.assertEqual(G.hauptprogramm(['--WIEDERGABE', p, '--AUFZEICHNUNG', p]), G.RC_START)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_echter_rechner_gleicher_ablauf(self):
        """Dieselbe Klickfolge (G, R) am echten Rechner aufzeichnen und an einem frischen Rechner abspielen: gleicher Endzustand."""
        try:
            import c8205_grafik as G
            from grafik_trommel import GrafikTrommel
        except Exception as e:
            self.skipTest(f'Kern nicht ladbar: {e}')
        import shutil, tempfile, threading, time, grafik_debuglog as DL
        d = tempfile.mkdtemp(); graph = G.lade_graph(os.path.join(PROJ, 'markdown-dateien'))
        troms = os.path.join(PROJ, 'Trommel', 'trommel.txt')
        def lauf_start():
            os.makedirs(os.path.join(d, str(len(geraete))), exist_ok=True)
            kopie = os.path.join(d, str(len(geraete)), 'trommel.txt'); shutil.copy(troms, kopie)
            tr = GrafikTrommel(kopie); r = G.Rechner(graph, tr, pult_modus=True)
            s = PultSteuerung(PULT, r, hochlauf_s=0.01, auslauf_s=0.01); stop = threading.Event()
            threading.Thread(target=lambda: G.rechner_schleife(r, stop), name='rechner', daemon=True).start()
            s.bei_betrieb = lambda: (r.taste('H'), r.taste('SW=0'), setattr(r, 'thread_modus', True))
            s.netz_klick(0.0); s.tick(1.0); time.sleep(0.05)
            return s, r, tr, stop
        def warte(r):
            for _ in range(300):
                time.sleep(0.01)
                if r.m.k0.erwartet('T') or (not r.laeuft and not r._ereignisse and not r._schritt and not r.start_gewuenscht): break
            time.sleep(0.1)
        pfad = os.path.join(d, 'spur.txt'); geraete = []
        try:
            geraete.append(None); s1, r1, tr1, stop1 = lauf_start(); geraete[-1] = (r1, tr1, stop1)
            s1.aufzeichnung = DL.Aufzeichnung(pfad)
            t = time.monotonic(); s1.klick('G', t); time.sleep(0.1); s1.klick('R', time.monotonic()); warte(r1)
            s1.aufzeichnung.schliessen()
            ende1 = (r1.m.BZ, r1.m.AC, r1.m.AR, r1.m.fl['H'])
            kopf, ev = DL.lade_klickspur(pfad); self.assertEqual([e[2] for e in ev], ['G', 'R'])
            stop1.set(); r1.abbrechen(); tr1.schliessen(); geraete.clear(); time.sleep(0.05)        # es gibt nur eine Trommel zur Zeit
            geraete.append(None); s2, r2, tr2, stop2 = lauf_start(); geraete[-1] = (r2, tr2, stop2)
            w = DL.Wiedergabe(s2, ev); w.starten(time.monotonic())
            while not w.fertig:
                time.sleep(max(0.0, w.bis_naechster(time.monotonic()) or 0)); w.faellige(time.monotonic())
            warte(r2)
            self.assertEqual((r2.m.BZ, r2.m.AC, r2.m.AR, r2.m.fl['H']), ende1); self.assertEqual(w.abweichungen, 0)
        finally:
            for g in geraete:
                if g: g[2].set(); g[0].abbrechen(); g[1].schliessen()
            shutil.rmtree(d, ignore_errors=True)


def tk_after(fenster):
    return fenster.root.after_f


class BsLampe(unittest.TestCase):
    """Lampe BS leuchtet erst, wenn ein bedingter Stopp (06Z) bei eingerastetem Schalter BS wirksam wird - nicht schon beim Einrasten."""
    def test_lampe_bs(self):
        try:
            import c8205_grafik as G
            from grafik_trommel import GrafikTrommel
        except Exception as e:
            self.skipTest(f'Kern nicht ladbar: {e}')
        import shutil, tempfile
        d = tempfile.mkdtemp(); kopie = os.path.join(d, 'trommel.txt')
        shutil.copy(os.path.join(PROJ, 'Trommel', 'trommel.txt'), kopie)
        tr = GrafikTrommel(kopie)
        try:
            r = G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), tr, pult_modus=True)
            tr.wr(0, 0o60)                                   # Zelle 0000: bedingter Stopp (060)
            s = PultSteuerung(PULT, r, hochlauf_s=0.01, auslauf_s=0.01)
            s.netz_klick(0.0); s.tick(1.0); r.taste('H'); r.taste('SW=0')
            bs = lambda: s.lampen()[0]['BS']
            self.assertEqual(bs(), 'dunkel')
            self.assertIn('verriegelt', r.taste('ST'))       # BS-Schalter noch nicht gesetzt, kein Stopp: ST wirkungslos
            self.assertTrue(s.klick('G', 2.0)); self.assertTrue(s.klick('BS', 2.1))
            self.assertEqual((r.m.bs_schalter, r.m.fl['BS']), (1, 0))      # Schalterstellung 1, Flag BS (= Lampe) noch 0
            self.assertEqual(bs(), 'dunkel')                 # Einrasten allein laesst die Lampe NICHT leuchten
            self.assertTrue(s.klick('R', 3.0)); r.lauf_wenn_gewuenscht()
            self.assertTrue(r.m.halted); self.assertIn('Bedingter Stop', r.m.halt_grund)
            self.assertEqual(bs(), 'hell')                   # bedingter Stopp wirksam UND Schalter gesetzt
            self.assertTrue(s.klick('H', 4.0)); self.assertTrue(s.klick('ST', 4.1))
            self.assertEqual(bs(), 'dunkel')                 # ST beseitigt den Stopp
            self.assertEqual((r.m.bs_schalter, r.m.fl['BS']), (1, 0))      # Schalter bleibt eingerastet, Flag geloescht
            s.klick('BS', 5.0); self.assertEqual(bs(), 'dunkel')
        finally:
            tr.schliessen(); shutil.rmtree(d, ignore_errors=True)


class FensterMitErsatzmodul(unittest.TestCase):
    """Tk-Schicht gegen ein Ersatzmodul (KEIN echtes Tkinter): prueft nur Verdrahtung und Aufrufe, nicht das Aussehen."""
    def _fake_tk(self):
        class W:
            def __init__(s, *a, **k): s.cfg = {}; s.bound = {}
            def pack(s, *a, **k): pass
            def title(s, *a): pass
            def resizable(s, *a): pass
            def protocol(s, n, f): s.bound[n] = f
            def bind(s, ev, f): s.bound[ev] = f
            def focus_set(s): s.fokus = True
            def focus_get(s): return s.cv
            def create_image(s, *a, **k): s.n = getattr(s, 'n', 0) + 1; return s.n
            def itemconfigure(s, *a, **k): pass
            def coords(s, *a): pass
            def after(s, ms, f): s.after_f = f
            def mainloop(s): pass
            def destroy(s): s.zerstoert = True
        t = types.SimpleNamespace()
        t.Tk = W
        def Canvas(root, **k):
            c = W(); root.cv = c; return c
        t.Canvas = Canvas
        t.PhotoImage = lambda **k: object()
        return t
    def test_verdrahtung(self):
        from grafik_pult_fenster import PultFenster
        r = FakeRechner(); s = PultSteuerung(PULT, r, hochlauf_s=0.0)
        tk = self._fake_tk(); f = PultFenster(s, PULT, tk=tk); f.zeichnen()
        sc = s.m['schluessel']; ev = types.SimpleNamespace(x=sc['cx'], y=sc['cy'], state=0)
        f._maus_druecken(ev); self.assertEqual(s.netz, HOCHLAUF)
        import time; s.tick(time.monotonic() + 1); self.assertEqual(s.netz, BETRIEB)
        g = s.m['tasten']['G']; ev = types.SimpleNamespace(x=g['x'] + 3, y=g['y'] + 3, state=0)
        f._maus_druecken(ev); self.assertIn('G', r.tokens)
        f.zeichnen(); f._schliessen(); self.assertEqual(s.netz, ENDE)
    def test_wiedergabe(self):
        """Fenster mit Klickspur: Ereignisse kommen ueber after() zur Zeit, Maus/Tastatur sind gesperrt, bis alles abgespielt ist."""
        import grafik_debuglog as DL
        from grafik_pult_fenster import PultFenster
        r = FakeRechner(); s = PultSteuerung(PULT, r, hochlauf_s=0.0)
        tk = self._fake_tk(); f = PultFenster(s, PULT, tk=tk)
        ev = [(0.0, 'klick', 'NETZ', False, True), (0.0, 'klick', 'G', False, False)]
        f.wiedergabe_einhaengen(DL.Wiedergabe(s, ev)); f.wiedergabe.starten(time.monotonic()); f._wiedergabe_planen()
        sc = s.m['schluessel']; ev_m = types.SimpleNamespace(x=sc['cx'], y=sc['cy'], state=0, char='1', keysym='1')
        f._maus_druecken(ev_m); self.assertEqual(s.netz, AUS)                  # gesperrt
        f._taste(ev_m); self.assertEqual(r.m.k0.got, [])
        self.assertTrue(callable(tk_after(f)))
        tk_after(f)()                                                           # after-Rueckruf: NETZ-Klick und G (G noch gesperrt: Hochlauf)
        self.assertEqual(s.netz, HOCHLAUF); self.assertTrue(f.wiedergabe.fertig)
        f._maus_druecken(ev_m); self.assertEqual(s.netz, AUSLAUF)              # nach der Wiedergabe wirkt die Maus wieder

if __name__ == '__main__':
    unittest.main(verbosity=1)
