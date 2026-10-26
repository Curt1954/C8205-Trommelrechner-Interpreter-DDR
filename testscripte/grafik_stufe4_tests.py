# -*- coding: utf-8 -*-
"""Pruefungen Stufe 4 (Toene): Mischer, Schreibwerkzeit, Klangwahl, Selektor SW, angezeigte Eingabe, Ausfall (Code 16).
Ohne Audiogeraet und ohne Echtzeit (Zeitgeber und Zufall sind ersetzt). Aufruf: python3 -I testscripte/grafik_stufe4_tests.py"""
import os, sys, time, threading, array, random, unittest
HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
import grafik_tonmisch as TM
# G4-003: Umgebungsvariable C8205_MISCHER=C laesst DIESELBEN Pruefungen gegen den Mischer im C-Modul laufen (grafik_tonmisch_c.CMischer);
# ohne sie laufen sie gegen den Python-Mischer.  Beide muessen alle Pruefungen bestehen (grafik_alle_tests.sh macht beides).
MISCHER_ART = 'Python'
if os.environ.get('C8205_MISCHER') == 'C':
    import grafik_tonmisch_c as TC
    if TC.lade_ton_modul() is None:
        raise SystemExit('C8205_MISCHER=C, aber das C-Modul tonmisch ist nicht gebaut (c-module/python: python3 setup.py build_ext --inplace)')
    TM.Mischer, TM.ListenSenke, TM.ProzessSenke = TC.CMischer, TC.CListenSenke, TC.CProzessSenke
    MISCHER_ART = 'C'
from grafik_schreibwerk import Schreibwerk, zeichen_aus_text, _art
from c8205_grafik import SwSenke


def klang(n, wert=1000):
    return array.array('h', [wert] * n)


def samples(b):
    a = array.array('h'); a.frombytes(b); return a


class Mischer(unittest.TestCase):
    def test_block_ist_10_ms_und_bei_ruhe_stille(self):
        m = TM.Mischer(); b = m.block()
        self.assertEqual(len(b), 882); self.assertEqual(set(samples(b)), {0})

    def test_einzelklang_beginnt_im_naechsten_block_und_endet(self):
        m = TM.Mischer(); m.einzel('schreibwerk', klang(1000, 500))
        s = samples(m.block()); self.assertEqual(s[0], 500)                    # Beginn: erster Block nach dem Ereignis (<= 10 ms)
        m.block(); s3 = samples(m.block())
        self.assertEqual(list(s3[:118]), [500] * 118); self.assertEqual(list(s3[118:]), [0] * (441 - 118))
        self.assertEqual(m.klingt(), 0)

    def test_ueberlappung_summiert_und_begrenzt(self):
        m = TM.Mischer(); m.einzel('schreibwerk', klang(441, 400))
        m.einzel('schreibwerk', klang(441, 300)); self.assertEqual(samples(m.block())[0], 700)
        m.einzel('schreibwerk', klang(441, 30000)); m.einzel('schreibwerk', klang(441, 30000))
        self.assertEqual(samples(m.block())[0], 32767)

    def test_tor_zu_verwirft_einzelklaenge_des_kanals(self):
        m = TM.Mischer(); m.einzel('leser', klang(441, 100)); m.einzel('schreibwerk', klang(441, 200))
        m.tor('leser', False); self.assertEqual(samples(m.block())[0], 200)
        m.einzel('leser', klang(441, 100)); self.assertEqual(samples(m.block())[0], 0)
        m.tor('leser', True); m.einzel('leser', klang(441, 100)); self.assertEqual(samples(m.block())[0], 100)

    def test_dauergeraeusch_schleife_pegel_und_aus(self):
        m = TM.Mischer(); d = array.array('h', list(range(1, 11)))
        m.dauer_an('rechner', 'grund', d, 1.0)
        self.assertEqual(list(samples(m.block())[:12]), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2])
        m.dauer_pegel('grund', 0.0); self.assertEqual(set(samples(m.block())), {0})
        m.dauer_pegel('grund', 0.5); self.assertGreater(samples(m.block())[3], 0)
        m.dauer_aus('grund'); self.assertEqual(set(samples(m.block())), {0})

    def test_alles_aus_sofort(self):
        m = TM.Mischer(); m.einzel('schreibwerk', klang(44100, 9)); m.dauer_an('rechner', 'g', klang(100, 5)); m.alles_aus()
        self.assertEqual(set(samples(m.block())), {0}); self.assertEqual(m.klingt(), 0)

    def test_strom_laeuft_dauernd_im_takt_mit_vorlauf(self):
        senke = TM.ListenSenke(); m = TM.Mischer(senke); m.starten(); time.sleep(0.25); m.schliessen()
        n = len(senke.bloecke)
        self.assertGreaterEqual(n, 22); self.assertLessEqual(n, 29)             # 250 ms = 25 Bloecke plus Vorlauf von 3, nie weiter voraus (S4-03)

    def test_ausfall_der_senke_wird_gemeldet(self):
        gemeldet = []; ev = threading.Event()
        def melde(t): gemeldet.append(t); ev.set()
        s = TM.ProzessSenke(['true']); m = TM.Mischer(s, bei_ausfall=melde); m.starten()
        self.assertTrue(ev.wait(3.0)); self.assertTrue(m.ausfall); m.schliessen()

    def test_prozess_nicht_startbar(self):
        with self.assertRaises(TM.SenkeAusfall):                    # Python-Mischer: schon beim Anlegen der Senke; C-Modul: beim Oeffnen
            TM.Mischer(TM.ProzessSenke(['/gibt/es/nicht']))

    def test_kein_abspielprogramm(self):
        self.assertIsNone(TM.finde_spieler(pfad='/gibt/es/nicht'))

    def test_begrenzen_auf_100_ms_original_unveraendert(self):
        d = klang(5292, 1000); b = TM.begrenze(d, 100, 10)
        self.assertEqual(len(b), 4410); self.assertEqual(len(d), 5292); self.assertEqual(d[5000], 1000)
        self.assertEqual(b[0], 1000); self.assertLess(abs(b[-1]), 100)          # Ende ausgeblendet
        k = klang(100); self.assertIs(TM.begrenze(k, 100), k)                     # kuerzer: unveraendert zurueck

    def test_echte_dateien_laden_24_zeichen_tab_wrzl_wr(self):
        sw = Schreibwerk.laden(os.path.join(PROJ, 'ton'), None)
        self.assertEqual(len(sw.zeichen_klaenge), 24)
        self.assertTrue(all(len(k) <= 4410 for k in sw.zeichen_klaenge))
        self.assertEqual(len(sw.tab), 17640); self.assertEqual(len(sw.wrzl), 15876)
        self.assertEqual(len(sw.wr), 5292)                                         # OP-42: 120 ms

    def test_wr_klang_ist_der_anfang_des_wrzl_klangs_vor_dem_markanten_ton(self):
        """OP-42 (Entscheidung 21.10.2026): wr.wav = erste 120 ms von wrzl.wav, letzte 5 ms ausgeblendet; der laute Schlag (ab etwa 126 ms) fehlt."""
        sw = Schreibwerk.laden(os.path.join(PROJ, 'ton'), None)
        n, aus = 5292, 220                                                          # 120 ms, 5 ms Ausblendung
        self.assertEqual(list(sw.wr[:n - aus]), list(sw.wrzl[:n - aus]))           # davor unveraendert
        self.assertNotEqual(list(sw.wr[n - aus:]), list(sw.wrzl[n - aus:n]))       # Ausblendung vorhanden
        self.assertLess(abs(sw.wr[-1]), 50)                                         # endet leise, kein Knacken
        self.assertLess(max(abs(v) for v in sw.wr), 12000)                          # der Schlag mit Spitze 12941 (ab etwa 126 ms) ist nicht darin
        self.assertGreater(max(abs(v) for v in sw.wrzl[5292:5800]), 12000)         # (Gegenprobe: im WRZL-Klang liegt er gleich dahinter)


class Werk(unittest.TestCase):
    def neu(self, mit_mischer=True, seed=1):
        self.zeiten = []
        self.uhr = Uhr()                                      # G4-003: ersetzbare Uhr, schlafe() rueckt sie vor und merkt die Wartezeit
        self.m = TM.Mischer() if mit_mischer else None
        k = {'zeichen': [klang(5292, 100 + i) for i in range(24)], 'tab': klang(17640, 7), 'wrzl': klang(15876, 8), 'wr': klang(5292, 9)}
        return Schreibwerk(self.m, k, schlafe=self._schlafe, zufall=random.Random(seed), uhr=self.uhr)

    def _schlafe(self, dt):
        self.zeiten.append(round(dt, 9)); self.uhr.schlafe(dt)

    def test_schreibwerkzeit_75_bis_90_ms_gleichverteilt(self):
        w = self.neu(); w.ausgabe('x' * 2000); w.warte_bis_frei()            # das letzte Zeichen wird erst beim Auslaufen gezaehlt
        self.assertEqual(len(self.zeiten), 2000)
        self.assertGreaterEqual(min(self.zeiten), 0.075); self.assertLessEqual(max(self.zeiten), 0.090)
        mittel = sum(self.zeiten) / 2000
        self.assertAlmostEqual(mittel, 0.0825, delta=0.001)
        self.assertGreater(len(set(round(z, 5) for z in self.zeiten)), 500)       # je Zeichen verschieden

    def test_tab_400_wrzl_360_zeichen_zr_benannt(self):
        w = self.neu(); w.ausgabe('\t'); w.ausgabe('\n'); w.ausgabe(' '); w.ausgabe('<Nr.5>'); w.warte_bis_frei()
        self.assertEqual(self.zeiten[0], 0.4); self.assertEqual(self.zeiten[1], 0.36)
        self.assertTrue(0.075 <= self.zeiten[2] <= 0.09); self.assertEqual(len(self.zeiten), 4)       # <Nr.5> = ein Zeichen

    def test_wr_120_ms_eigener_klang_nicht_wrzl(self):
        """OP-42: <WR> (Wagenruecklauf ohne Zeilenschaltung) hat Klang und Schreibwerkzeit 120 ms; WRZL bleibt 360 ms, jedes andere benannte Zeichen ein Zeichen."""
        self.assertEqual(_art('<WR>'), 'wr'); self.assertEqual(_art('\n'), 'wrzl'); self.assertEqual(_art('<WRZL>'), 'zeichen')
        self.assertEqual(_art('<Nr.5>'), 'zeichen'); self.assertEqual(_art('\t'), 'tab')
        w = self.neu(); w.ausgabe('<WR>'); w.warte_bis_frei()
        self.assertEqual(self.zeiten, [0.12]); self.assertEqual(self.m.klingt(), 1)
        self.assertEqual(samples(self.m.block())[0], int(9 * w.pegel))               # Kennung 9 des WR-Klangs mal Pegel (nicht 8 = WRZL, nicht 100+i = Zeichen)
        w.ausgabe('a<WR>\nb'); w.warte_bis_frei()                                      # Zeichen, WR, WRZL, Zeichen
        self.assertEqual([round(z, 3) for z in self.zeiten[2:4]], [0.12, 0.36]); self.assertEqual(len(self.zeiten), 5)

    def test_wr_ohne_klangdatei_still_aber_mit_schreibwerkzeit(self):
        k = {'zeichen': [klang(5292)] * 3, 'tab': klang(10), 'wrzl': klang(10)}       # 'wr' fehlt: kein Absturz, kein Klang, Zeit bleibt
        zeiten = []; u = Uhr(); m = TM.Mischer(); w = Schreibwerk(m, k, schlafe=lambda dt: (zeiten.append(round(dt, 9)), u.schlafe(dt)), uhr=u); w.ausgabe('<WR>'); w.warte_bis_frei()
        self.assertEqual(zeiten, [0.12]); self.assertEqual(m.klingt(), 0)

    def test_wr_stumm_schreibwerkzeit_ja(self):
        w = self.neu(mit_mischer=False); w.ausgabe('<WR>'); w.warte_bis_frei(); self.assertEqual(self.zeiten, [0.12])

    def test_wr_als_angezeigte_eingabe_klingt_ohne_schreibwerkzeit(self):
        w = self.neu(); w.eingabe('<WR>'); self.assertEqual(self.zeiten, []); self.assertEqual(self.m.klingt(), 1)
        self.assertEqual(samples(self.m.block())[0], int(9 * w.pegel))

    def test_zeichenklang_100_ms_nie_zweimal_derselbe(self):
        w = self.neu(); letzter = None
        for i in range(3000):
            w.ausgabe('a'); s = samples(self.m.block())[0]                         # Kennung: 100+i je Datei
            self.assertNotEqual(s, letzter); letzter = s
            while self.m.klingt(): self.m.block()
        self.assertTrue(all(len(k) == 4410 for k in w.zeichen_klaenge))

    def test_ueberstand_ueberlappt_mit_dem_folgezeichen(self):
        w = self.neu(); w.ausgabe('a')
        for _ in range(8): self.m.block()                                           # 80 ms vergangen: Klang 1 laeuft noch 20 ms
        self.assertEqual(self.m.klingt(), 1); w.ausgabe('b')
        self.assertEqual(self.m.klingt(), 2)                                        # beide klingen, nichts abgeschnitten
        s = samples(self.m.block()); self.assertGreater(s[0], 200)                   # Summe beider Klaenge

    def test_stumm_schreibwerkzeit_ja_ton_nein(self):
        w = self.neu(mit_mischer=False); w.ausgabe('abc'); w.warte_bis_frei(); self.assertEqual(len(self.zeiten), 3)

    def test_eingabe_klingt_ohne_schreibwerkzeit(self):
        w = self.neu(); w.eingabe('a'); w.eingabe('\t'); w.eingabe('\n')
        self.assertEqual(self.zeiten, []); self.assertEqual(self.m.klingt(), 3)
        self.assertEqual(list(zeichen_aus_text('a<Um. KB>b')), ['a', '<Um. KB>', 'b'])

    def test_eine_klangfolge_fuer_ausgabe_und_eingabe(self):
        w = self.neu(); gesehen = []
        for i in range(500):
            (w.ausgabe if i % 2 else w.eingabe)('z'); gesehen.append(samples(self.m.block())[0])
            while self.m.klingt(): self.m.block()
        self.assertTrue(all(a != b for a, b in zip(gesehen, gesehen[1:])))

    def test_abwechselnd_ein_und_ausgabe_laufen_ineinander(self):
        w = self.neu(); w.ausgabe('a'); w.eingabe('b'); w.ausgabe('c')
        self.assertEqual(self.m.klingt(), 3)


class SchreibwerkAsynchron(unittest.TestCase):
    """G4-003 (Projektinhaber 22.10.2026): die Befehlsschleife wartet nicht auf das Ende des Zeichens; erst der naechste Ausgabebefehl wartet,
    falls das Schreibwerk noch beschaeftigt ist; dieses Warten ist ein E/A-Halt (nicht Rechnerzeit)."""

    def werk(self):
        self.u = Uhr(); self.ereignisse = []; self.waits = []
        def schlafe(dt): self.waits.append(round(dt, 9)); self.u.schlafe(dt)
        w = Schreibwerk(None, None, schlafe=schlafe, zufall=random.Random(3), uhr=self.u)
        w.bei_halt = lambda: self.ereignisse.append('halt'); w.bei_weiter = lambda: self.ereignisse.append('weiter')
        return w

    def test_erstes_zeichen_kehrt_sofort_zurueck(self):
        w = self.werk(); w.ausgabe('a')
        self.assertEqual((self.waits, self.ereignisse), ([], []))
        self.assertGreater(w.frei_ab, self.u.t)

    def test_naechster_befehl_wartet_genau_bis_frei(self):
        w = self.werk(); w.ausgabe('a'); t_a = w.letzte_zeiten[-1]
        self.u.t += 0.030                                                # der Rechner rechnet 30 ms
        w.ausgabe('b')
        self.assertEqual(len(self.waits), 1); self.assertAlmostEqual(self.waits[0], t_a - 0.030, places=9)
        self.assertEqual(self.ereignisse, ['halt', 'weiter'])            # E/A-Halt nur fuer die Restzeit

    def test_kein_warten_wenn_schreibwerk_schon_frei(self):
        w = self.werk(); w.ausgabe('a'); self.u.t += 0.5; w.ausgabe('b')
        self.assertEqual((self.waits, self.ereignisse), ([], []))

    def test_text_aus_mehreren_zeichen_wartet_je_folgezeichen(self):
        w = self.werk(); w.ausgabe('abc')
        self.assertEqual(len(self.waits), 2); self.assertEqual(self.ereignisse, ['halt', 'weiter'] * 2)

    def test_tab_blockiert_erst_den_folgebefehl(self):
        w = self.werk(); w.ausgabe('\t'); self.assertEqual(self.waits, [])
        w.ausgabe('x'); self.assertEqual(self.waits, [0.4])

    def test_haltzeit_zaehlt_das_warten_nicht_zur_rechnerzeit(self):
        """Mit dem Rechner verdrahtet: das Warten auf das Schreibwerk ist ein E/A-Halt der Haltuhr."""
        import types
        import c8205_grafik as G
        r = G.Rechner({}, types.SimpleNamespace(), pult_modus=True)
        w = Schreibwerk(None, None, schlafe=lambda dt: None, zufall=random.Random(1), uhr=lambda: 0.0)
        r.sw.schreibwerk = w
        r.haltuhr.start(); r.sw.schreibe('a'); n0 = r.haltuhr.anzahl; r.sw.schreibe('b')
        self.assertEqual(r.haltuhr.anzahl, n0 + 1)                       # ein Halt (E/A-Halt) wegen des Wartens auf 'a'
        self.assertEqual(r.haltuhr.lesen()[2], 'E/A-Halt') if r.haltuhr.lesen() else None


class SchreibwerkzeitUndH(unittest.TestCase):
    """OP-40/OP-39: Hängt der Rechner-Thread in der Schreibwerkzeit, blockiert das weder die Pult-Taste H noch das Beenden.
    Echtzeit (einmal 0,4 s, TAB ist die längste Schreibwerkzeit eines Ausgabebefehls)."""

    def test_ein_ausgabebefehl_ist_ein_zeichen(self):
        """Aufrufstelle c8205_interp.py: sw_schreibe(m, sw_zeichen(m, z)) je Befehl, also genau ein Zeichen oder ein <Name>."""
        for text in ('a', '\t', '\n', '<WR>', '<WRZL>', '<Nr.7>'):
            self.assertEqual(len(list(zeichen_aus_text(text))), 1, text)

    def test_ein_befehl_hoechstens_400_ms(self):
        w = Schreibwerk(None, None, schlafe=lambda t: None, zufall=random.Random(1))
        langste = max(w.zeit(a) for a in ('tab', 'wrzl', 'wr', 'zeichen'))
        self.assertLessEqual(langste, 0.4)

    def test_pult_taste_h_blockiert_nicht_in_der_schreibwerkzeit(self):
        import types
        import c8205_grafik as G
        r = G.Rechner({}, types.SimpleNamespace(), pult_modus=True)
        r.thread_modus = True
        r.sw.schreibwerk = Schreibwerk(None, None)            # echtes time.sleep
        im_werk = threading.Event(); fertig = threading.Event()

        def rechner():
            im_werk.set(); r.sw.schreibe('\t'); r.sw.schreibe('x'); fertig.set()    # TAB startet sofort; das naechste Zeichen wartet 400 ms (G4-003)
        th = threading.Thread(target=rechner, daemon=True); th.start()
        self.assertTrue(im_werk.wait(1))
        time.sleep(0.05)
        self.assertFalse(fertig.is_set())                     # der Rechner-Thread steckt in der Schreibwerkzeit
        t0 = time.monotonic(); r.pult_taste('H'); dauer = time.monotonic() - t0
        self.assertLess(dauer, 0.05)                          # die Pult-Taste kehrt sofort zurueck (nur vorgemerkt)
        self.assertTrue(r._h_angefordert.is_set())            # und H ist angefordert: wirkt an der naechsten Befehlsgrenze
        self.assertFalse(fertig.is_set())
        th.join(2); self.assertTrue(fertig.is_set())

    def test_abbrechen_blockiert_nicht_in_der_schreibwerkzeit(self):
        import types
        import c8205_grafik as G
        r = G.Rechner({}, types.SimpleNamespace(), pult_modus=True)
        r.thread_modus = True
        r.sw.schreibwerk = Schreibwerk(None, None)
        im_werk = threading.Event()
        th = threading.Thread(target=lambda: (im_werk.set(), r.sw.schreibe('\t'), r.sw.schreibe('x')), daemon=True); th.start()
        self.assertTrue(im_werk.wait(1)); time.sleep(0.05)
        t0 = time.monotonic(); r.abbrechen(); dauer = time.monotonic() - t0
        self.assertLess(dauer, 0.05)
        th.join(2)


class Senke(unittest.TestCase):
    def test_selektor_sw_keine_ausgabe_kein_ton_aber_schreibwerkzeit(self):
        """G4-004: Selektor SW: kein Text, kein Klang, nichts nachgeholt; die Schreibwerkzeit laeuft still weiter (der Rest eines Textes ist beim Loesen nicht verbraucht)."""
        zeiten = []; m = TM.Mischer(); uhr = [0.0]
        k = {'zeichen': [klang(5292)] * 3, 'tab': klang(10), 'wrzl': klang(10)}
        def schlafe(t): zeiten.append(t); uhr[0] += t
        s = SwSenke(Schreibwerk(m, k, schlafe=schlafe, uhr=lambda: uhr[0])); gehoert = []; s.hoere(gehoert.append)
        s.unterdruecken = True; s.schreibe('abc'); s.schreibe('\t')
        self.assertEqual((s.alles(), gehoert, m.klingt()), ('', [], 0))
        self.assertEqual(len(zeiten), 3)                                                                           # 'b', 'c' und TAB warten je auf das vorige Zeichen
        s.unterdruecken = False; s.schreibe('d'); s.schreibwerk.warte_bis_frei()                                   # danach wieder, nichts wird nachgeholt
        self.assertEqual((s.alles(), gehoert, m.klingt()), ('d', ['d'], 1))

    def test_selektor_sw_mitten_im_text_loesen_der_rest_erscheint(self):
        """G4-004: Text von 30 Zeichen, Selektor rastet nach 5 Zeichen ein und wird nach 0,5 s geloest: der Rest NACH dem Loesen erscheint (vorher ging er in Millisekunden verloren)."""
        uhr = [0.0]; m = TM.Mischer(); k = {'zeichen': [klang(5292)] * 3, 'tab': klang(10), 'wrzl': klang(10)}
        s = SwSenke(Schreibwerk(m, k, schlafe=lambda t: uhr.__setitem__(0, uhr[0] + t), uhr=lambda: uhr[0]))
        for i in range(30):
            if i == 5:
                s.unterdruecken = True; t_ein = uhr[0]
            if s.unterdruecken and uhr[0] - t_ein >= 0.5:
                s.unterdruecken = False
            s.schreibe(chr(ord('a') + i % 26))
        ausgegeben = s.alles()
        self.assertEqual(ausgegeben[:5], 'abcde')
        self.assertGreater(len(ausgegeben), 10)                    # nach dem Loesen geht es weiter
        self.assertLess(len(ausgegeben), 25)                       # ein Stueck ging waehrend der Sperre verloren

    def test_ohne_schreibwerk_wie_bisher(self):
        s = SwSenke(); s.schreibe('xy'); self.assertEqual(s.alles(), 'xy')

    def test_text_erscheint_zu_beginn_der_schreibwerkzeit(self):
        reihenfolge = []
        class W:
            def ausgabe(self, t): reihenfolge.append('werk')
        s = SwSenke(W()); s.hoere(lambda t: reihenfolge.append('anzeige')); s.schreibe('a')
        self.assertEqual(reihenfolge, ['anzeige', 'werk'])


class Fenster(unittest.TestCase):
    def test_eingabe_klick_klingt_auch_bei_selektor_sw(self):
        """OP-09 (21.10.2026): der Klang der Eingabe kommt aus _klick_eingabe (beim Tastendruck), der Selektor SW wirkt nicht auf ihn."""
        import types, grafik_sw_fenster as F
        gespielt = []
        w = types.SimpleNamespace(senke=types.SimpleNamespace(schreibwerk=types.SimpleNamespace(eingabe=gespielt.append),
                                                              unterdruecken=True), q=__import__('queue').Queue())
        F.SwFenster._klick_eingabe(w, 'a')
        self.assertEqual(gespielt, ['a']); self.assertTrue(w.q.empty())      # Klang ja, Anzeige noch nicht

    def test_eingabe_echo_zeigt_nur_an(self):
        """OP-09: _echo_eingabe (Annahme durch den Rechner) zeigt nur an und klingt nicht noch einmal."""
        import types, grafik_sw_fenster as F
        gespielt = []
        w = types.SimpleNamespace(senke=types.SimpleNamespace(schreibwerk=types.SimpleNamespace(eingabe=gespielt.append),
                                                              unterdruecken=False), q=__import__('queue').Queue())
        F.SwFenster._echo_eingabe(w, 'a')
        self.assertEqual(gespielt, []); self.assertEqual(w.q.get_nowait(), 'a')


# ===================================================================================================================
# Checkpoint 54: Rechnertoene ueber den Mischer, Leser (S4-09), Stanzer (S4-10), Haken, Verdrahtung
# ===================================================================================================================
import grafik_geraeteton as GT
from grafik_rechnerton import MischerRechnerTon


class Uhr:
    """Ersetzbare Uhr: schlafe() rueckt sie vor."""
    def __init__(self): self.t = 100.0
    def __call__(self): return self.t
    def schlafe(self, dt): self.t += dt


def lauf(m, uhr, sekunden, schritt=0.010):
    """Mischer-Takt nachbilden: jeder Block 10 ms Uhr weiter, dann der Zeitgeber (wie _lauf)."""
    for _ in range(int(round(sekunden / schritt))):
        uhr.t += schritt; m.block(); m.haken_aufrufen()


class MischerSchluessel(unittest.TestCase):
    def test_einzel_mit_schluessel_laesst_sich_abbrechen(self):
        m = TM.Mischer(); m.einzel('rechner', klang(10000, 5), 1.0, 'fade'); self.assertEqual(m.klingt_schluessel('fade'), 1)
        m.dauer_aus('fade'); self.assertEqual(m.klingt(), 0)

    def test_haken_nach_jedem_block_fehler_stoppen_den_strom_nicht(self):
        senke = TM.ListenSenke(); m = TM.Mischer(senke); n = []
        m.takt_haken.append(lambda: n.append(1)); m.takt_haken.append(lambda: 1 / 0)
        m.starten(); time.sleep(0.15); m.schliessen()
        self.assertGreaterEqual(len(n), 10); self.assertIsNone(m.ausfall); self.assertTrue(m.haken_fehler)


class Rechnerton(unittest.TestCase):
    def neu(self):
        self.m = TM.Mischer()
        k = {'fade_in': klang(441 * 20, 11), 'fade_out': klang(441 * 10, 22), 'grund': klang(441 * 7, 33)}
        return MischerRechnerTon(None, self.m, k)

    def test_dauern_aus_den_klaengen(self):
        t = self.neu(); self.assertAlmostEqual(t.dauer_fade_in(), 0.2); self.assertAlmostEqual(t.dauer_fade_out(), 0.1)

    def test_echte_dateien(self):
        t = MischerRechnerTon(os.path.join(PROJ, 'ton'))
        self.assertAlmostEqual(t.dauer_fade_in(), 11.294, delta=0.01); self.assertAlmostEqual(t.dauer_fade_out(), 1.951, delta=0.01)
        self.assertAlmostEqual(len(t.k['grund']) / 44100.0, 5.943, delta=0.01)

    def test_fade_in_laeuft_und_endet(self):
        t = self.neu(); self.assertFalse(t.fade_laeuft()); t.fade_in(); self.assertTrue(t.fade_laeuft())
        for _ in range(20): self.m.block()
        self.assertFalse(t.fade_laeuft())

    def test_grundgeraeusch_pegel_0_8_als_schleife(self):
        t = self.neu(); t.grund_an()
        for _ in range(30): s = samples(self.m.block())                              # laenger als die Datei: Schleife ohne Neustart-Luecke
        self.assertEqual(set(s), {int(33 * 0.8)}); self.assertEqual(self.m.klingt(), 1)

    def test_grund_an_zweimal_bleibt_eine_schleife(self):
        t = self.neu(); t.grund_an(); t.grund_an(); self.assertEqual(self.m.klingt(), 1)

    def test_fade_out_beendet_fade_in_und_grund_und_schliesst_tore(self):
        t = self.neu(); t.fade_in(); t.grund_an(); self.m.einzel('leser', klang(5000, 1)); self.m.dauer_an('stanzer', 'st', klang(10, 1))
        t.fade_out()
        self.assertEqual(self.m.klingt(), 1); self.assertEqual(self.m.klingt_schluessel('fade'), 1)
        self.assertEqual(samples(self.m.block())[0], 22)                              # nur fade_out klingt
        self.m.einzel('schreibwerk', klang(10, 1)); self.m.einzel('leser', klang(10, 1))
        self.assertEqual(self.m.klingt(), 1)                                          # Tore zu

    def test_alles_aus_sofort_ohne_fade_out(self):
        t = self.neu(); t.fade_in(); t.grund_an(); t.alles_aus(); self.assertEqual(self.m.klingt(), 0)

    def test_ohne_mischer_ohne_wirkung(self):
        t = MischerRechnerTon(None, None, {'fade_in': klang(10), 'fade_out': klang(10), 'grund': klang(10)})
        t.fade_in(); t.grund_an(); t.fade_out(); t.alles_aus(); self.assertFalse(t.fade_laeuft()); self.assertFalse(t.verfuegbar)

    def test_pult_netzablauf_mit_mischer(self):
        import grafik_pult as P
        t = self.neu(); st = P.PultSteuerung(os.path.join(PROJ, 'pult'), None, hochlauf_s=t.dauer_fade_in(), auslauf_s=t.dauer_fade_out() + 0.05, ton=t)
        st.netz_klick(0.0); self.assertEqual(self.m.klingt_schluessel('fade'), 1)
        for _ in range(21): self.m.block()
        st.tick(0.21); self.assertEqual(st.netz, P.BETRIEB); self.assertEqual(self.m.klingt_schluessel('grund'), 1)
        st.netz_klick(1.0); self.assertEqual(st.netz, P.AUSLAUF); self.assertEqual(self.m.klingt_schluessel('grund'), 0)
        self.assertIsNone(st.tick(1.05)); st.fenster_schliessen(1.06); self.assertEqual(self.m.klingt(), 0)       # X: alles sofort aus


class Leser(unittest.TestCase):
    def neu(self, tempo=GT.LESETEMPO):
        self.uhr = Uhr(); self.m = TM.Mischer()
        k = {'einzel': klang(6500, 1), 'dauer': klang(55125, 2), 'ende': klang(2646, 3)}
        lt = GT.LeserTon(self.m, k, uhr=self.uhr, schlafe=self.uhr.schlafe, tempo=tempo); self.m.takt_haken.append(lt.tick); return lt

    def test_erstes_zeichen_einzelschritt(self):
        lt = self.neu(); lt.zeichen(); self.assertEqual(lt.zustand, 'einzel'); self.assertEqual(self.m.klingt_schluessel('ls_einzel'), 1)
        self.assertEqual(self.m.klingt_schluessel('ls_dauer'), 0)

    def test_naechster_zugriff_nach_freigabe_einzel_laeuft_noch_dauerton(self):
        lt = self.neu(); lt.zeichen(); w = lt.zeichen()                                # 2. Zugriff wartet die 1/10 s Freigabe ab
        self.assertAlmostEqual(w, GT.EINZEL_FREIGABE_S, delta=1e-6)
        self.assertEqual(lt.zustand, 'dauer'); self.assertEqual(self.m.klingt_schluessel('ls_dauer'), 1); self.assertEqual(self.m.klingt_schluessel('ls_einzel'), 0)

    def test_dauer_freigabe_je_zeichen_1_130_s(self):
        lt = self.neu(); lt.zeichen(); lt.zeichen(); w = lt.zeichen()
        self.assertAlmostEqual(w, 1 / 130.0, delta=1e-6); self.assertEqual(lt.zustand, 'dauer')

    def test_einzel_beendet_dann_wieder_einzelton(self):
        lt = self.neu(); lt.zeichen(); lauf(self.m, self.uhr, 0.20)                    # Einzelton (148 ms) ist zu Ende, Aus-Frist noch nicht
        self.assertEqual(lt.zustand, 'einzel'); lt.zeichen()
        self.assertEqual(lt.zustand, 'einzel'); self.assertEqual(self.m.klingt_schluessel('ls_einzel'), 1); self.assertEqual(self.m.klingt_schluessel('ls_dauer'), 0)

    def test_dauer_laeuft_solange_zugriffe_kommen_und_endet_nach_aus_frist_mit_auslaufen(self):
        lt = self.neu()
        for _ in range(50): lt.zeichen(); lauf(self.m, self.uhr, 0.010)
        self.assertEqual(lt.zustand, 'dauer'); self.assertEqual(self.m.klingt_schluessel('ls_dauer'), 1)
        lauf(self.m, self.uhr, GT.LS_AUS_S - 0.1)                                      # noch nicht abgelaufen: der Motor laeuft weiter
        self.assertEqual(lt.zustand, 'dauer'); self.assertEqual(self.m.klingt_schluessel('ls_dauer'), 1)
        lauf(self.m, self.uhr, 0.2)
        self.assertEqual(lt.zustand, 'aus'); self.assertEqual(self.m.klingt_schluessel('ls_dauer'), 0)
        lauf(self.m, self.uhr, 0.1); self.assertEqual(self.m.klingt(), 0)

    def test_aus_frist_zaehlt_ab_dem_letzten_zugriff_nicht_ab_dem_eingabe_halt(self):
        lt = self.neu(); lt.zeichen(); lt.zeichen()
        lauf(self.m, self.uhr, GT.LS_AUS_S + 0.05)                                     # Leser wartet (Eingabe-Halt), kein Zugriff: Ton geht aus
        self.assertEqual(lt.zustand, 'aus'); self.assertEqual(self.m.klingt_schluessel('ls_dauer'), 0)

    def test_auslaufen_ist_ein_einzelklang_60_ms(self):
        lt = self.neu(); lt.zeichen(); lt.zeichen()
        self.uhr.t += GT.LS_AUS_S + 0.01; lt.tick()
        self.assertEqual(self.m.klingt_schluessel('ls_ende'), 1); self.assertEqual(self.m.klingt_schluessel('ls_dauer'), 0)

    def test_nach_aus_wieder_einzelschritt(self):
        lt = self.neu(); lt.zeichen(); lt.zeichen(); lauf(self.m, self.uhr, GT.LS_AUS_S + 0.3)
        self.assertEqual(lt.zustand, 'aus'); lt.zeichen(); self.assertEqual(lt.zustand, 'einzel')

    def test_zugriff_ohne_zeitgeber_setzt_abgelaufene_aus_frist_selbst_um(self):
        lt = self.neu(); lt.zeichen(); lt.zeichen(); self.uhr.t += GT.LS_AUS_S + 0.5; lt.zeichen()
        self.assertEqual(lt.zustand, 'einzel'); self.assertEqual(self.m.klingt_schluessel('ls_dauer'), 0)

    def test_lesetempo_im_dauerton_130_zeichen_je_sekunde_rechenzeit_angerechnet(self):
        lt = self.neu(); lt.zeichen(); lt.zeichen(); t0 = self.uhr.t
        for _ in range(130): lt.zeichen()
        self.assertAlmostEqual(self.uhr.t - t0, 1.0, delta=0.002)                      # 130 Zeichen im Dauerton = 1 s
        lt2 = self.neu(); lt2.zeichen(); lt2.zeichen(); self.uhr.t += 0.05             # Interpreter war ohnehin langsamer: nichts zusaetzlich
        self.assertEqual(lt2.zeichen(), 0.0)

    def test_tonlaenge_verzoegert_nicht(self):
        lt = self.neu(tempo=0); t0 = self.uhr.t
        for _ in range(100): lt.zeichen()
        self.assertEqual(self.uhr.t, t0)                                               # ohne Lesetempo kein Warten, Ton laeuft nebenher

    def test_ohne_mischer_nur_tempo(self):
        u = Uhr(); lt = GT.LeserTon(None, None, uhr=u, schlafe=u.schlafe); lt.zeichen(); lt.zeichen(); lt.zeichen(); lt.tick()
        self.assertAlmostEqual(u.t - 100.0, GT.EINZEL_FREIGABE_S + 1 / 130.0, delta=1e-6)

    def test_tor_leser_zu_stumm(self):
        lt = self.neu(); self.m.tor('leser', False); lt.zeichen(); self.assertEqual(self.m.klingt(), 0)

    def test_geraet_ruft_bei_jedem_gelieferten_zeichen(self):
        import tempfile, shutil
        from grafik_geraete import GrafikLeser
        d = tempfile.mkdtemp()
        try:
            with open(os.path.join(d, 'a.ls'), 'w') as f: f.write('10000001\n01000001\n11111111\n')
            g = GrafikLeser(d); n = []; g.bei_zeichen = lambda: n.append(1)
            self.assertEqual([g.naechste() for _ in range(3)], ['10000001', '01000001', '11111111']); self.assertEqual(len(n), 3)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class Stanzer(unittest.TestCase):
    def neu(self, tempo=None):
        """tempo=None: ohne Stanztempo (die Zustandspruefungen dieser Klasse); tempo=50: wie im Betrieb (G4-003)."""
        self.uhr = Uhr(); self.m = TM.Mischer()
        st = GT.StanzerTon(self.m, {'motor': klang(10, 1), 'dauer': klang(10, 2)}, uhr=self.uhr, schlafe=self.uhr.schlafe, tempo=tempo)
        self.m.takt_haken.append(st.tick); return st

    # --- Stanztempo ungefaehr 50 Zeichen/s (Antwort F-62 Nr. 4, G4-003) -------------------------------------------------
    def test_stanztempo_ist_50_zeichen_je_sekunde_vorgabe(self):
        self.assertEqual(GT.STANZTEMPO, 50.0)
        self.assertEqual(GT.StanzerTon().tempo, 50.0)                      # Voreinstellung = Betrieb

    def test_stanztempo_100_zeichen_hintereinander_brauchen_zwei_sekunden(self):
        st = self.neu(50.0); t0 = self.uhr.t
        for _ in range(100): st.zeichen()
        self.assertAlmostEqual(self.uhr.t - t0, 99 * 0.020, places=6)      # das erste Zeichen wartet nie
        self.assertEqual(st.verzoegerungen[0], 0.0); self.assertAlmostEqual(st.verzoegerungen[-1], 0.020, places=6)

    def test_stanztempo_rechenzeit_wird_angerechnet(self):
        st = self.neu(50.0); st.zeichen(); self.uhr.t += 0.012; vor = self.uhr.t
        w = st.zeichen(); self.assertAlmostEqual(w, 0.008, places=6); self.assertAlmostEqual(self.uhr.t - vor, 0.008, places=6)

    def test_stanztempo_langsame_zeichen_werden_nicht_gebremst(self):
        st = self.neu(50.0); st.zeichen(); self.uhr.t += 0.5; vor = self.uhr.t
        self.assertEqual(st.zeichen(), 0.0); self.assertEqual(self.uhr.t, vor)

    def test_stanztempo_schnelles_stanzen_ergibt_dauerstanzen(self):
        st = self.neu(50.0)
        for _ in range(10): st.zeichen()
        self.assertEqual((st.zustand, self.zustand_klingt()), ('dauerstanzen', (0, 1)))     # 20 ms Abstand < 50 ms

    def test_stanztempo_ls_loesen_aendert_die_zeichenzeit_nicht(self):
        st = self.neu(50.0); st.ls_taste(True); st.zeichen(); self.uhr.t += 0.010; st.ls_taste(False)
        w = st.zeichen(); self.assertAlmostEqual(w, 0.010, places=6)       # 10 ms seit dem Zeichen, nicht seit dem Loslassen

    def test_stanztempo_gilt_auch_ohne_ton_stumm(self):
        uhr = Uhr(); st = GT.StanzerTon(None, None, uhr=uhr, schlafe=uhr.schlafe); t0 = uhr.t
        for _ in range(11): st.zeichen()
        self.assertAlmostEqual(uhr.t - t0, 10 * 0.020, places=6)

    def test_stanztempo_ohne_tempo_keine_bremse(self):
        st = self.neu(None); t0 = self.uhr.t
        for _ in range(50): st.zeichen()
        self.assertEqual(self.uhr.t, t0)

    def test_stanztempo_bremst_den_geraetezugriff_nicht_die_datei(self):
        import tempfile, shutil
        from grafik_geraete import GrafikStanzer
        st = self.neu(50.0); d = tempfile.mkdtemp()
        try:
            g = GrafikStanzer(os.path.join(d, 'st')); g.bei_zeichen = st.zeichen
            for i in range(11): g.stanze(i)
            self.assertAlmostEqual(self.uhr.t - 100.0, 10 * 0.020, places=6)
            with open(g.pfad) as f: self.assertEqual(len(f.read().split()), 11)        # alle Zeichen in der Datei, nur langsamer
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def zustand_klingt(self):
        return (self.m.klingt_schluessel('st_motor'), self.m.klingt_schluessel('st_dauer'))

    def test_aus_bis_zum_ersten_zeichen_dann_geraeusch(self):
        st = self.neu(); self.assertEqual((st.zustand, self.zustand_klingt()), ('aus', (0, 0)))
        st.zeichen(); self.assertEqual((st.zustand, self.zustand_klingt()), ('geraeusch', (1, 0)))

    def test_kein_einzelschritt_ton_langsame_zeichen_nur_motor(self):
        st = self.neu()
        for _ in range(5): st.zeichen(); lauf(self.m, self.uhr, 0.2)
        self.assertEqual((st.zustand, self.zustand_klingt()), ('geraeusch', (1, 0)))

    def test_dauerstanzen_beginnt_mit_dem_zweiten_zeichen_unter_50_ms(self):
        st = self.neu(); st.zeichen(); self.uhr.t += 0.020; st.zeichen()
        self.assertEqual((st.zustand, self.zustand_klingt()), ('dauerstanzen', (0, 1)))               # nie zwei Geraeusche zugleich

    def test_ab_50_ms_abstand_kein_dauerstanzen(self):
        st = self.neu(); st.zeichen(); self.uhr.t += 0.051; st.zeichen(); self.assertEqual(st.zustand, 'geraeusch')

    def test_dauerstanzen_laeuft_solange_bedingung_erhalten_bleibt_und_endet_per_zeitgeber(self):
        st = self.neu(); st.zeichen()
        for _ in range(100): self.uhr.t += 0.020; st.zeichen(); self.m.block(); self.m.haken_aufrufen()
        self.assertEqual(st.zustand, 'dauerstanzen')
        lauf(self.m, self.uhr, 0.040); self.assertEqual(st.zustand, 'dauerstanzen')
        lauf(self.m, self.uhr, 0.030); self.assertEqual((st.zustand, self.zustand_klingt()), ('geraeusch', (1, 0)))

    def test_nach_5_s_ohne_zeichen_aus_naechstes_zeichen_startet_wieder(self):
        st = self.neu(); st.zeichen(); lauf(self.m, self.uhr, 4.9); self.assertEqual(st.zustand, 'geraeusch')
        lauf(self.m, self.uhr, 0.2); self.assertEqual((st.zustand, self.zustand_klingt()), ('aus', (0, 0)))
        st.zeichen(); self.assertEqual((st.zustand, self.zustand_klingt()), ('geraeusch', (1, 0)))

    def test_ls_gedrueckt_motor_dauernd_nie_abschalten(self):
        st = self.neu(); st.ls_taste(True); self.assertEqual((st.zustand, self.zustand_klingt()), ('geraeusch', (1, 0)))
        lauf(self.m, self.uhr, 6.0); self.assertEqual((st.zustand, self.zustand_klingt()), ('geraeusch', (1, 0)))

    def test_ls_gedrueckt_nie_dauerstanzen(self):
        st = self.neu(); st.ls_taste(True)
        for _ in range(20): self.uhr.t += 0.010; st.zeichen()
        self.assertEqual((st.zustand, self.zustand_klingt()), ('geraeusch', (1, 0)))

    def test_ls_gedrueckt_waehrend_dauerstanzen_schaltet_auf_motor(self):
        st = self.neu(); st.zeichen(); self.uhr.t += 0.01; st.zeichen(); st.ls_taste(True)
        self.assertEqual((st.zustand, self.zustand_klingt()), ('geraeusch', (1, 0)))

    def test_ls_loesen_5_s_frist_beginnt_neu(self):
        st = self.neu(); st.ls_taste(True); lauf(self.m, self.uhr, 10); st.ls_taste(False)
        lauf(self.m, self.uhr, 4.9); self.assertEqual(st.zustand, 'geraeusch'); lauf(self.m, self.uhr, 0.2); self.assertEqual(st.zustand, 'aus')

    def test_stop(self):
        st = self.neu(); st.zeichen(); st.stop(); self.assertEqual((st.zustand, self.m.klingt()), ('aus', 0))

    def test_tor_stanzer_zu_dauergeraeusch_weg(self):
        st = self.neu(); st.zeichen(); self.m.tor('stanzer', False); self.assertEqual(self.m.klingt(), 0)

    def test_geraet_ruft_nach_dem_stanzen_nicht_bei_fehler(self):
        import tempfile, shutil
        from grafik_geraete import GrafikStanzer
        from c8205_interp import KonfigFehler
        d = tempfile.mkdtemp()
        try:
            g = GrafikStanzer(os.path.join(d, 'st')); n = []; g.bei_zeichen = lambda: n.append(1)
            g.stanze(5); g.stanze(6); self.assertEqual(len(n), 2)
            with open(g.pfad) as f: self.assertEqual(f.read(), '00000101\n00000110\n')              # Ton wirkt nicht auf die Datei
            f = os.path.join(d, 'datei'); open(f, 'w').close(); g2 = GrafikStanzer(f); g2.bei_zeichen = lambda: n.append(1)
            with self.assertRaises(KonfigFehler): g2.stanze(1)
            self.assertEqual(len(n), 2)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class PultLs(unittest.TestCase):
    def test_selektor_ls_ruft_bei_ls_und_aendert_den_rechner_nicht(self):
        import grafik_pult as P
        ereignisse = []
        st = P.PultSteuerung(os.path.join(PROJ, 'pult'), None, bei_ls=ereignisse.append)
        st.netz = P.BETRIEB
        st.klick('LS', 0.0); st.klick('LS', 1.0)
        self.assertEqual(ereignisse, [True, False]); self.assertEqual(st.protokoll[-2:], ['LS+', 'LS-'])


# ---------------------------------------------------------------------------------------------------------------------------
# Hoerpruefung 1 (19.10.2026), G4-004: --TON (Lautstaerke je Gruppe), SW doppelt so laut, Vorlauf 2 Bloecke, Spielerlatenz
class TonOption(unittest.TestCase):
    def test_parse_ton_vier_ziffern(self):
        self.assertEqual(TM.parse_ton('5555'), (5, 5, 5, 5)); self.assertEqual(TM.parse_ton('0959'), (0, 9, 5, 9))
        for schlecht in ('555', '55555', '55a5', '', '5 55', '-555', '5.55'):
            with self.assertRaises(ValueError, msg=schlecht): TM.parse_ton(schlecht)

    def test_standard_ist_5555_und_faktoren(self):
        self.assertEqual(TM.TON_STANDARD, '5555')
        self.assertEqual(TM.ton_faktoren((5, 5, 5, 5)), (1.0, 2.0, 1.3, 1.0))          # SW doppelt so laut wie vor der Hoerpruefung
        self.assertEqual(TM.ton_faktoren((0, 0, 0, 0)), (0.0, 0.0, 0.0, 0.0))
        f = TM.ton_faktoren((9, 9, 9, 9)); self.assertAlmostEqual(f[0], 1.8); self.assertAlmostEqual(f[1], 3.6)

    def test_reihenfolge_pult_sw_ll_ls(self):
        self.assertEqual(TM.TON_NAMEN, ('Pult', 'SW', 'LL', 'LS'))
        f = TM.ton_faktoren(TM.parse_ton('5000')); self.assertEqual((f[0], f[1], f[2], f[3]), (1.0, 0.0, 0.0, 0.0))

    def test_schreibwerk_pegel_voreinstellung_2_und_einstellbar(self):
        import grafik_schreibwerk as S
        self.assertEqual(S.PEGEL, 2.0)
        m = TM.Mischer(); sw = Schreibwerk(m, {'zeichen': [klang(441, 1000)] * 3, 'tab': klang(441), 'wrzl': klang(441)}, schlafe=lambda t: None)
        self.assertEqual(sw.pegel, 2.0); sw.ausgabe('A'); b = samples(m.block()); self.assertEqual(b[10], 2000)      # 1000 * 2
        m2 = TM.Mischer(); sw2 = Schreibwerk(m2, {'zeichen': [klang(441, 1000)] * 3, 'tab': klang(441), 'wrzl': klang(441)}, schlafe=lambda t: None)
        sw2.pegel = TM.ton_faktoren((5, 0, 5, 5))[1]; sw2.ausgabe('A'); self.assertEqual(samples(m2.block())[10], 0)   # SW 0 = stumm

    def test_rechnerton_faktor(self):
        m = TM.Mischer(); t = MischerRechnerTon(None, m, {'fade_in': klang(1000, 1000), 'fade_out': klang(1000, 1000), 'grund': klang(1000, 1000)}, faktor=0.6)
        t.fade_in(); self.assertEqual(samples(m.block())[5], 600)
        m.alles_aus(); t.grund_an(); self.assertEqual(samples(m.block())[5], int(1000 * 0.8 * 0.6))
        m.alles_aus(); t.fade_out(); self.assertEqual(samples(m.block())[5], 600)
        t0 = MischerRechnerTon(None, TM.Mischer(), {'fade_in': klang(10), 'fade_out': klang(10), 'grund': klang(10)})
        self.assertEqual((t0.faktor, t0.grund_pegel), (1.0, 0.8))                       # Voreinstellung = Pegel der Hoerpruefung 1

    def test_leser_und_stanzer_pegel(self):
        m = TM.Mischer(); lt = GT.LeserTon(m, {'einzel': klang(441, 1000), 'dauer': klang(441), 'ende': klang(441)}, tempo=None, pegel=0.4)
        lt.zeichen(); self.assertEqual(samples(m.block())[5], 400)
        m = TM.Mischer(); st = GT.StanzerTon(m, {'motor': klang(441, 1000), 'dauer': klang(441)}, tempo=None, pegel=0.0)
        st.zeichen(); self.assertEqual(samples(m.block())[5], 0)
        self.assertEqual((GT.LeserTon().pegel, GT.StanzerTon().pegel), (1.0, 1.0))

    def test_kommandozeile(self):
        import c8205_grafik as G, argparse
        self.assertEqual(G._ton_arg('5955'), (5, 9, 5, 5))
        with self.assertRaises(argparse.ArgumentTypeError): G._ton_arg('12')

    def test_vorlauf_und_spielerlatenz_g4_004(self):
        self.assertEqual(TM.VORLAUF_BLOECKE, 2); self.assertEqual(TM.SPIELER_LATENZ_MS, 20)
        pa = [b for b in TM.SPIELER_ROH if b[0] == 'paplay'][0]; self.assertIn('--latency-msec=20', pa)
        pw = [b for b in TM.SPIELER_ROH if b[0] == 'pw-cat'][0]; self.assertEqual(pw[pw.index('--latency') + 1], '20ms')
        ap = [b for b in TM.SPIELER_ROH if b[0] == 'aplay'][0]; self.assertIn('--buffer-time=20000', ap)

    def test_ton_beginnt_im_naechsten_block_nach_dem_zeichen(self):
        m = TM.Mischer(); m.einzel('schreibwerk', klang(441, 700), 2.0); b = samples(m.block()); self.assertEqual((b[0], b[440]), (1400, 1400))



class StartOhneAbspielprogramm(unittest.TestCase):
    """B-5 / S4-04: echter Start von c8205_grafik.py ohne Abspielprogramm bricht mit Code 16 ab, mit --STUMM nicht an dieser Stelle.
    Tkinter wird durch ein leeres Ersatzmodul ersetzt (die Tonpruefung kommt vor dem Aufblenden der Fenster); PATH ist leer."""
    def _start(self, *args):
        import subprocess, tempfile, shutil
        with tempfile.TemporaryDirectory() as t:
            os.mkdir(os.path.join(t, 'stub')); open(os.path.join(t, 'stub', 'tkinter.py'), 'w').close()
            os.mkdir(os.path.join(t, 'leer'))
            tr = os.path.join(t, 'trommel.txt')
            shutil.copy(os.path.join(PROJ, 'Trommel', 'trommel.txt'), tr)
            env = dict(os.environ, PYTHONPATH=os.path.join(t, 'stub'), PATH=os.path.join(t, 'leer'), C8205_FENSTERLAGE='aus', PYTHONDONTWRITEBYTECODE='1')
            p = subprocess.run([sys.executable, os.path.join(PROJ, 'c8205_grafik.py'), '--trommel', tr, *args], env=env, cwd=t,
                               capture_output=True, text=True, timeout=60)
            return p.returncode, p.stderr + p.stdout

    def test_ohne_spieler_code_16(self):
        rc, text = self._start()
        self.assertEqual(rc, 16, text); self.assertIn('Kein Abspielprogramm gefunden', text)

    def test_mit_stumm_keine_spielerpruefung(self):
        rc, text = self._start('--STUMM')
        self.assertNotIn('Kein Abspielprogramm', text)

if __name__ == '__main__':
    print(f'Mischer: {MISCHER_ART}', flush=True)
    unittest.main(verbosity=1)
