# -*- coding: utf-8 -*-
"""Pruefungen Stufe 3: SW-Fenster (Logik ohne Tkinter, Anbindung an die K0-Warteschlange, Tk-Schicht mit Ersatzmodul).
Aufruf: python3 -I testscripte/grafik_sw_tests.py"""
import os, sys, threading, time, types, unittest
HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
from grafik_sw import SwAnzeige, SwEingabe, abbilden, BREITE
from grafik_k0 import K0Warteschlange


class Anzeige(unittest.TestCase):
    def test_normal_und_zeilenschaltung(self):
        a = SwAnzeige(); a.schreibe('abc\nde')
        self.assertEqual(a.text(), 'abc\nde'); self.assertEqual(a.pos, 2)

    def test_tab_stopp_alle_12(self):
        a = SwAnzeige(); a.schreibe('\n' + 'Alle Vö' + '\t')          # Beispiel des Projektinhabers: 7 Zeichen, TAB = 5 Leerschritte
        self.assertEqual(a.pos, 12); self.assertEqual(a.zeile_text(1), 'Alle Vö' + ' ' * 5)
        a = SwAnzeige(); a.schreibe('\t12\t')                          # Position 14 -> 24: 10 Leerschritte
        self.assertEqual(a.zeile_text(0), ' ' * 12 + '12' + ' ' * 10); self.assertEqual(a.pos, 24)

    def test_tab_auf_dem_stopp_geht_zum_naechsten(self):
        a = SwAnzeige(); a.schreibe('\t'); self.assertEqual(a.pos, 12); a.schreibe('\t'); self.assertEqual(a.pos, 24)

    def test_tab_ab_120_bis_130(self):
        a = SwAnzeige(); a.schreibe('x' * 125 + '\t')
        self.assertEqual(a.pos, 130); self.assertEqual(len(a.zeile_text(0)), 130)
        a.schreibe('\t'); self.assertEqual(a.pos, 130)                 # keine Bewegung mehr

    def test_rechter_anschlag_ueberdruck_ohne_umbruch(self):
        a = SwAnzeige(); a.schreibe('a' * 130)
        self.assertEqual(a.pos, 130); self.assertEqual(len(a.zeilen), 1)
        a.schreibe('Z')
        self.assertEqual(len(a.zeilen), 1); self.assertEqual(a.pos, 130)           # kein Umbruch, Position bleibt
        self.assertEqual(a.zeile_text(0), 'a' * 129 + 'Z')                         # letztes Zeichen ueberdruckt
        a.schreibe('Y'); self.assertEqual(a.zeile_text(0), 'a' * 129 + 'Y')

    def test_wr_und_wrzl_setzen_position_null(self):
        a = SwAnzeige(); a.schreibe('abcdef\rXY')
        self.assertEqual(a.zeile_text(0), 'XYcdef'); self.assertEqual(a.pos, 2)   # WR: Ueberdruck derselben Zeile
        a.schreibe('\n'); self.assertEqual(a.pos, 0); self.assertEqual(len(a.zeilen), 2)

    def test_benannte_zeichen_nur_ausgefuehrt(self):
        a = SwAnzeige()
        for z in ('a', '<ZV>', '<BM>', '<Irrung Zeichen>', '<Irrung Satz>', '<Transport (Relikt)>', '<\u2248>', '<\u224b>', '<\u25b3>', 'b'):
            a.schreibe(z)
        self.assertEqual(a.zeile_text(0), 'ab'); self.assertEqual(a.pos, 2)        # nichts angezeigt, Position unveraendert

    def test_op14_benannte_zeichen_die_das_schreibwerk_wirklich_ausgibt(self):
        """OP-14 (S3-07, 21.10.2026): Welche benannten Zeichen kann die Rechnerausgabe ans SW ueberhaupt liefern? Nicht ZV, BM, Irrung Zeichen und
        Transport (sie stehen nicht in SW_ZEILE, Kodetabellen 1.4: das Schreibwerk gibt sie nicht aus), sondern nur Irrung Satz, die Umschaltzeichen,
        WR und die drei Zeichen ohne Bildschirmdarstellung. Alle ausser WR bewegen die Schreibposition nicht; WR setzt sie auf 0."""
        import types
        import c8205_interp as I
        benannt = set()
        for lage in ('KB', 'GB'):
            m = types.SimpleNamespace(sw_lage=lage)
            for zeile in I.SW_ZEILE.values():
                t = I.sw_zeichen(m, zeile)
                if len(t) > 1:
                    benannt.add(t)
        self.assertEqual(benannt, {'<Irrung Satz>', '<Um. GB>', '<Um. KB>', '<WR>', '<\u2248>', '<\u224b>', '<\u25b3>'})
        for t in sorted(benannt - {'<WR>'}):
            a = SwAnzeige(); a.schreibe('abc'); a.schreibe(t); a.schreibe('d')
            self.assertEqual((a.zeile_text(0), a.pos), ('abcd', 4), t)          # keine Anzeige, keine Bewegung
        a = SwAnzeige(); a.schreibe('abc'); a.schreibe('<WR>'); self.assertEqual(a.pos, 0)

    def test_wr_als_benanntes_zeichen_wird_ausgefuehrt(self):
        a = SwAnzeige()
        for z in 'abcdef':
            a.schreibe(z)
        a.schreibe('<WR>'); self.assertEqual(a.pos, 0); self.assertEqual(a.zeile_text(0), 'abcdef')   # nicht angezeigt, aber ausgefuehrt
        a.schreibe('X'); self.assertEqual(a.zeile_text(0), 'Xbcdef')

    def test_alle_zeichen_der_tabelle_1(self):
        """Alles, was sw_zeichen() fuer Tabelle 1 liefert: benannte Zeichen erscheinen nie; sichtbare immer."""
        import c8205_interp as I
        for lage in ('KB', 'GB'):
            m = types.SimpleNamespace(sw_lage=lage)
            for r in I.TABELLE1:
                s = I.sw_zeichen(m, r); a = SwAnzeige(); a.schreibe(s)
                if len(s) > 2 and s[0] == '<' and s[-1] == '>':
                    self.assertNotIn('<', a.text(), s)
                elif s not in ('\t', '\n'):
                    self.assertEqual(a.text(), s)

    def test_benanntes_zeichen_am_anschlag_und_vor_tab(self):
        a = SwAnzeige(); a.schreibe('x' * 130); a.schreibe('<ZV>')
        self.assertEqual(a.zeile_text(0), 'x' * 130); self.assertEqual(a.pos, 130)
        a = SwAnzeige(); a.schreibe('ab'); a.schreibe('<BM>'); a.schreibe('\t')
        self.assertEqual(a.pos, 12)

    def test_einzelne_spitze_klammern_sind_zeichen(self):
        a = SwAnzeige()
        for z in '<ab>':
            a.schreibe(z)
        self.assertEqual(a.zeile_text(0), '<ab>'); self.assertEqual(a.pos, 4)

    def test_geaenderte_zeilen(self):
        a = SwAnzeige(); a.schreibe('a\nb')
        self.assertEqual(a.hole_geaenderte(), [0, 1]); self.assertEqual(a.hole_geaenderte(), [])
        a.schreibe('c'); self.assertEqual(a.hole_geaenderte(), [1])

    def test_paketgrenzen_egal(self):
        a = SwAnzeige()
        for z in 'ab\tc\nd':
            a.schreibe(z)
        b = SwAnzeige(); b.schreibe('ab\tc\nd')
        self.assertEqual(a.text(), b.text())


class Abbildung(unittest.TestCase):
    def test_gleiche_lage(self):
        self.assertEqual(abbilden('a', 'KB'), ['a']); self.assertEqual(abbilden('A', 'GB'), ['A'])
        self.assertEqual(abbilden('3', 'KB'), ['3'])

    def test_umschaltzeichen_vorangestellt(self):
        self.assertEqual(abbilden('A', 'KB'), ['Um. GB', 'A']); self.assertEqual(abbilden('a', 'GB'), ['Um. KB', 'a'])
        self.assertEqual(abbilden('(', 'KB'), ['Um. GB', '(']); self.assertEqual(abbilden('3', 'GB'), ['Um. KB', '3'])

    def test_sondertasten(self):
        self.assertEqual(abbilden('\r', 'KB'), ['WRZL']); self.assertEqual(abbilden('\t', 'GB'), ['TAB'])
        self.assertEqual(abbilden(' ', 'GB'), ['ZR'])

    def test_nicht_angenommen(self):
        for z in ('ä', 'ö', 'ß', '@', '{', '}', '\\', '|', '€', '\x01', '\x1b'):
            self.assertIsNone(abbilden(z, 'KB'), z)

    def test_angenommene_zeichen_des_dokuments(self):
        for z in '%:+/,.-;()?!<>"\'[]~#*=':
            self.assertIsNotNone(abbilden(z, 'KB'), z)
        for z in 'azAZ09`':
            if z != '`':
                self.assertIsNotNone(abbilden(z, 'KB'), z)


def ein_tastendruck(fn):
    """G4-008-Mechanik (Einstellung True; seit G4-009 ist die Vorgabe False)."""
    import functools
    @functools.wraps(fn)
    def lauf(*a, **k):
        alt = SwEingabe.EIN_TASTENDRUCK
        SwEingabe.EIN_TASTENDRUCK = True
        try:
            return fn(*a, **k)
        finally:
            SwEingabe.EIN_TASTENDRUCK = alt
    return lauf


def alter_puffer(fn):
    """G4-007-Mechanik (Puffer bis PUFFER_MAX Eingaben): seit G4-008 gilt vorgabemaessig EIN Tastendruck (SwEingabe.EIN_TASTENDRUCK); diese Pruefungen
    laufen mit der Einstellung False weiter, damit die Mechanik des Puffers (Reihenfolge, Paar, Kanalwechsel, Ruecktaste) geprueft bleibt."""
    import functools
    @functools.wraps(fn)
    def lauf(*a, **k):
        alt = SwEingabe.EIN_TASTENDRUCK
        SwEingabe.EIN_TASTENDRUCK = False
        try:
            return fn(*a, **k)
        finally:
            SwEingabe.EIN_TASTENDRUCK = alt
    return lauf


class Ruecktaste(unittest.TestCase):
    """G4-006: Rücktaste = Löschwirkung in der Anzeige, kein Name, kein Wert für den Rechner."""
    def test_loescht_letztes_zeichen(self):
        a = SwAnzeige(); a.schreibe('abc'); a.schreibe('\b')
        self.assertEqual(a.text(), 'ab'); self.assertEqual(a.pos, 2)
        a.schreibe('\b\b'); self.assertEqual(a.text(), ''); self.assertEqual(a.pos, 0)
    def test_am_zeilenanfang_ohne_wirkung_und_ohne_zeilenverschmelzung(self):
        a = SwAnzeige(); a.schreibe('ab\n'); a.schreibe('\b')
        self.assertEqual(a.text(), 'ab\n'); self.assertEqual(a.pos, 0)
    def test_keine_anzeige_eines_namens(self):
        a = SwAnzeige(); a.schreibe('x'); a.schreibe('\b')
        self.assertNotIn('<', a.text()); self.assertNotIn('\x08', a.text())
    def test_mitten_in_der_zeile_ersetzt_durch_leerzeichen(self):
        a = SwAnzeige(); a.schreibe('abcd\r'); a.schreibe('xy'); a.schreibe('\b')       # 'xycd', Position 2 -> y wird zum Leerzeichen, Position 1
        self.assertEqual(a.text(), 'x cd'); self.assertEqual(a.pos, 1)
    def test_am_rechten_anschlag(self):
        a = SwAnzeige(); a.schreibe('a' * 130); a.schreibe('\b')
        self.assertEqual(len(a.text()), 129); self.assertEqual(a.pos, 129)
    def test_nach_tab_loescht_leerschritt(self):
        a = SwAnzeige(); a.schreibe('a\t'); a.schreibe('\b'); self.assertEqual(a.pos, 11); self.assertEqual(len(a.text()), 11)
    def test_wirkt_ohne_aktiven_011_und_sendet_nichts(self):
        m = FakeMaschine(); m.fl['SW'] = 0; k0 = K0Warteschlange(m); aus = []
        e = SwEingabe(k0, m, echo=lambda t: aus.append(('echo', t)), abstand=0.1, rueck=lambda: aus.append('rueck'))
        self.assertEqual(e.ruecktaste(), 'geloescht')
        self.assertEqual(aus, ['rueck']); self.assertEqual(e.puffer, []); self.assertEqual(list(k0._q['SW']), [])
    def test_op31_kein_klang_bei_ruecktaste(self):
        """OP-31 (5. Annahme 'kein Ton', 21.10.2026 bestaetigt): weder beim Loeschen in der Anzeige noch beim Zuruecknehmen eines vorgemerkten Zeichens klingt etwas."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); aus = []
        e = SwEingabe(k0, m, echo=lambda t: aus.append(('echo', t)), klick=lambda t: aus.append(('klick', t)), abstand=0.1, rueck=lambda: aus.append('rueck'))
        e.lage = 'KB'
        self.assertEqual(e.tippen('A'), 'vorgemerkt'); self.assertEqual(aus, [('klick', 'A')])      # der Tastendruck klingt (OP-09), die Ruecktaste nicht
        self.assertEqual(e.ruecktaste(), 'zurueckgenommen'); self.assertEqual(e.ruecktaste(), 'geloescht')
        self.assertEqual(aus, [('klick', 'A'), 'rueck'])
    def test_nimmt_zuerst_ein_vorgemerktes_zeichen_zurueck(self):
        """G4-007: Ein vorgemerktes Zeichen hat den Rechner nie erreicht und war nie angezeigt: die Rücktaste nimmt es (samt Umschaltzeichen) zurück,
        statt in der Anzeige etwas zu löschen. Erst ohne Vorgemerktes löscht sie in der Anzeige."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); aus = []
        e = SwEingabe(k0, m, echo=lambda t: aus.append(('echo', t)), abstand=0.1, rueck=lambda: aus.append('rueck'))
        e.lage = 'KB'
        self.assertEqual(e.tippen('A'), 'vorgemerkt'); self.assertEqual([x[0] for x in e.puffer], ['Um. GB', 'A'])   # kein 011 aktiv
        self.assertEqual(e.ruecktaste(), 'zurueckgenommen'); self.assertEqual(e.puffer, []); self.assertEqual(aus, [])
        self.assertEqual(e.ruecktaste(), 'geloescht'); self.assertEqual(aus, ['rueck'])
        self.assertEqual(list(k0._q['SW']), [])                                   # an den Rechner ging nie etwas
    @alter_puffer
    def test_nimmt_nur_das_letzte_zeichen_zurueck(self):
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.0); e.lage = 'KB'
        e.tippen('a'); e.tippen('B'); e.tippen('c')                                # kein 011: alle vorgemerkt, Lage: KB, GB, KB
        self.assertEqual([x[0] for x in e.puffer], ['a', 'Um. GB', 'B', 'Um. KB', 'c'])
        e.ruecktaste(); self.assertEqual([x[0] for x in e.puffer], ['a', 'Um. GB', 'B'])
        e.ruecktaste(); self.assertEqual([x[0] for x in e.puffer], ['a'])
        self.assertEqual(e._lage_vorschau(), 'KB')


class FakeMaschine:
    def __init__(self):
        self.fl = {'SW': 1, 'T': 0, 'K1': 0, 'K2': 0, 'K3': 0}; self.zeichenlage = 'KB'


class Anbindung(unittest.TestCase):
    """SwEingabe gegen die echte K0-Warteschlange; ein Faden spielt den Rechner (wie a032: Lage bei Um. KB/Um. GB umstellen)."""
    def _rechner(self, m, k0, erhalten, stop):
        def lauf():
            while not stop.is_set():
                try:
                    t = k0.naechstes()
                except Exception:
                    return
                erhalten.append(t)
                if t == 'Um. GB': m.zeichenlage = 'GB'
                if t == 'Um. KB': m.zeichenlage = 'KB'
        th = threading.Thread(target=lauf, daemon=True); th.start(); return th

    def _warte(self, bed, s=2.0):
        t0 = time.time()
        while time.time() - t0 < s:
            if bed(): return True
            time.sleep(0.005)
        return False

    def test_blockiert_ohne_kanal_sw(self):
        """S3-13: Ist K0/SW nicht angewaehlt, ist die Taste blockiert: keine Eingabe, keine Anzeige, nichts im Puffer."""
        m = FakeMaschine(); m.fl['SW'] = 0; k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append, abstand=0.1)
        self.assertEqual(e.tippen('a'), 'blockiert'); self.assertFalse(e.eingabe_aktiv())
        self.assertEqual(echo, []); self.assertEqual(e.puffer, []); self.assertIsNone(e.lage)      # keine Wirkung, auch nicht auf die Lage
    def test_ohne_aktiven_011_wird_vorgemerkt(self):
        """G4-007: K0/SW ist angewaehlt, der Rechner aber noch nicht bei 011: das Zeichen wartet im Puffer, keine Anzeige, Lage des SW unveraendert."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append, abstand=0.1); e.lage = 'KB'
        self.assertEqual(e.tippen('a'), 'vorgemerkt'); self.assertFalse(e.eingabe_aktiv())
        self.assertEqual(echo, []); self.assertEqual([x[0] for x in e.puffer], ['a']); self.assertEqual(e.lage, 'KB')
        k0._wartet_auf = 'SW'                                                        # jetzt wartet der Rechner
        self.assertEqual(e.liefern(), 'geliefert'); self.assertEqual(echo, ['a']); self.assertEqual(e.puffer, []); self.assertEqual(e.lage, 'KB')
    def test_lieferung_und_zwei_eingaben(self):
        """S3-11: A in der anderen Lage = zwei Eingaben, Um. GB, dann A, im Abstand von etwa 0,1 s; der Rechner durchlaeuft zwei 011."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.1); e.lage = 'KB'; erhalten = []; stop = threading.Event()   # SW steht auf KB (Vorzustand, hier nicht Thema)
        self._rechner(m, k0, erhalten, stop)
        try:
            self.assertTrue(self._warte(e.erwartet)); self.assertTrue(e.eingabe_aktiv())
            self.assertEqual(e.tippen('a'), 'geliefert'); self.assertTrue(self._warte(lambda: erhalten == ['a']))
            self.assertTrue(self._warte(e.erwartet))
            t0 = time.monotonic()
            self.assertEqual(e.tippen('A'), 'folgt')                         # SW auf KB, A braucht GB: zuerst Um. GB
            self.assertTrue(self._warte(lambda: erhalten == ['a', 'Um. GB'] and m.zeichenlage == 'GB'))
            self.assertEqual(e.lage, 'GB')                                   # das SW steht jetzt auf GB
            self.assertEqual(e.liefern(), None)                              # vor Ablauf des Abstands wird nichts gesendet
            self.assertTrue(self._warte(lambda: (e.liefern(), erhalten == ['a', 'Um. GB', 'A'])[1]))    # die zweite Eingabe, ohne erneutes Tippen
            self.assertGreaterEqual(time.monotonic() - t0, 0.1 - 0.005)      # Abstand etwa 0,1 s
            self.assertIsNone(e.zweite)
        finally:
            stop.set(); k0.abbrechen()
    def test_op09_erstes_zeichen_nach_dem_einschalten_klingt_erst_beim_loslassen(self):
        """OP-09 (21.10.2026, Befund aus dem Code, am echten Fenster nicht gehoert): Nach dem Einschalten ist die Lage des SW unbestimmt (None).
        Das erste Zeichen mit bestimmter Lage geht deshalb als Paar (Um. KB, Zeichen) an den Rechner (Regel 18.10.2026, G3-008). Das Umschaltzeichen
        klingt und erscheint nie (O4-6); das Zeichen selbst wird ohne gehaltene Umschalttaste erst beim LOSLASSEN frei (U-11 Fall b) und klingt erst
        dann (Anzeige und Klang haengen an der Annahme durch den Rechner). Beim Druecken bleibt es still."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append); erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            self.assertIsNone(e.lage)
            self.assertTrue(self._warte(e.erwartet))
            self.assertEqual(e.tippen('a'), 'folgt')                         # Druecken: nur das Umschaltzeichen ist beim Rechner
            self.assertTrue(self._warte(lambda: erhalten == ['Um. KB']))
            self.assertEqual(echo, [])                                       # kein Klang, keine Anzeige beim Druecken
            self.assertTrue(self._warte(e.erwartet))
            self.assertIsNone(e.liefern()); self.assertEqual(echo, []); self.assertEqual([x[0] for x in e.puffer], ['a'])   # ohne Loslassen bleibt das Zeichen im Puffer
            self.assertEqual(e.loslassen(), 'geliefert')                     # Loslassen: Zeichen frei, ein 011 ist aktiv
            self.assertEqual(echo, ['a']); self.assertTrue(self._warte(lambda: erhalten == ['Um. KB', 'a']))
            self.assertEqual(e.lage, 'KB')
        finally:
            stop.set(); k0.abbrechen()
    def test_op09_zweiter_zeichen_ohne_zweiten_011_bleibt_im_puffer(self):
        """OP-09: Fragt der Rechner nach dem Umschaltzeichen nicht noch einmal (ein einzelner 011), bleibt das erste Zeichen im Puffer: kein Klang,
        keine Anzeige, auch nach dem Loslassen. Der Puffer haelt es, bis wieder ein 011 aktiv ist."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append)
        k0._wartet_auf = 'SW'                                                # genau ein 011
        self.assertEqual(e.tippen('a'), 'folgt')                             # Um. KB angenommen
        self.assertEqual(k0.naechstes(), 'Um. KB')                           # der Rechner holt das Umschaltzeichen ab und fragt nicht wieder
        k0._wartet_auf = None
        self.assertIsNone(e.loslassen()); self.assertEqual(echo, []); self.assertEqual([x[0] for x in e.puffer], ['a'])
        k0._wartet_auf = 'SW'                                                # spaeter ein neuer 011
        self.assertEqual(e.liefern(), 'geliefert'); self.assertEqual(echo, ['a'])
    # --- OP-09 (Entscheidung 21.10.2026): Klang beim Tastendruck, Anzeige bei Annahme -------------------------------------------------------
    def _mit_klick(self, **kw):
        m = FakeMaschine(); k0 = K0Warteschlange(m); ereignis = []
        e = SwEingabe(k0, m, echo=lambda t: ereignis.append(('anzeige', t)), klick=lambda t: ereignis.append(('klick', t)), **kw)
        return m, k0, e, ereignis
    def test_op09_klick_beim_druecken_anzeige_bei_annahme(self):
        """Der Rechner ist nicht bei einem 011: das Zeichen wartet im Puffer, klingt aber sofort; angezeigt wird es erst bei der Annahme, ohne zweiten Klang."""
        m, k0, e, ereignis = self._mit_klick(abstand=0.1); e.lage = 'KB'
        self.assertEqual(e.tippen('a'), 'vorgemerkt')
        self.assertEqual(ereignis, [('klick', 'a')])                          # Klang sofort, keine Anzeige
        k0._wartet_auf = 'SW'
        self.assertEqual(e.liefern(), 'geliefert')
        self.assertEqual(ereignis, [('klick', 'a'), ('anzeige', 'a')])        # Anzeige bei Annahme, kein zweiter Klang
    def test_op09_direkte_lieferung_ein_klang_eine_anzeige(self):
        m, k0, e, ereignis = self._mit_klick(abstand=0.1); e.lage = 'KB'; k0._wartet_auf = 'SW'
        self.assertEqual(e.tippen('a'), 'geliefert')
        self.assertEqual(ereignis, [('klick', 'a'), ('anzeige', 'a')])
    def test_op09_erstes_zeichen_klingt_beim_druecken_nicht_erst_beim_loslassen(self):
        """Das erste Zeichen nach dem Einschalten geht als Paar (Um. KB, Zeichen). Das Umschaltzeichen klingt nie, das Zeichen klingt beim Druecken;
        die Anzeige kommt erst nach dem Loslassen und der Annahme durch den Rechner."""
        m, k0, e, ereignis = self._mit_klick(); erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            self.assertTrue(self._warte(e.erwartet))
            self.assertEqual(e.tippen('a'), 'folgt')
            self.assertEqual(ereignis, [('klick', 'a')])                      # sofort beim Druecken
            self.assertTrue(self._warte(lambda: erhalten == ['Um. KB']))
            self.assertTrue(self._warte(e.erwartet))
            self.assertEqual(e.loslassen(), 'geliefert')
            self.assertEqual(ereignis, [('klick', 'a'), ('anzeige', 'a')])    # Loslassen: Anzeige, kein zweiter Klang
        finally:
            stop.set(); k0.abbrechen()
    def test_op09_kein_klang_bei_blockiert_voll_verworfen_und_umschaltzeichen(self):
        m, k0, e, ereignis = self._mit_klick(abstand=0.1); m.fl['SW'] = 0
        self.assertEqual(e.tippen('a'), 'blockiert'); self.assertEqual(ereignis, [])          # K0/SW nicht angewaehlt
        m.fl['SW'] = 1; e.lage = 'KB'
        self.assertEqual(e.tippen('\x01'), 'verworfen'); self.assertEqual(ereignis, [])       # nicht im R300-Code
        for _ in range(SwEingabe.PUFFER_MAX): e.tippen('a')
        n = len(ereignis); self.assertEqual(n, SwEingabe.PUFFER_MAX)
        self.assertEqual(e.tippen('a'), 'voll'); self.assertEqual(len(ereignis), n)           # Taste geht verloren: kein Klang
        self.assertTrue(all(x == ('klick', 'a') for x in ereignis))
        m2, k02, e2, ereignis2 = self._mit_klick(abstand=0.1); e2.lage = 'KB'
        e2.tippen('A'); self.assertEqual(ereignis2, [('klick', 'A')])                         # Paar (Um. GB, A): nur das Zeichen klingt
    def test_op09_ruecktaste_im_puffer_macht_keinen_weiteren_klang(self):
        m, k0, e, ereignis = self._mit_klick(abstand=0.1); e.lage = 'KB'
        e.tippen('a'); self.assertEqual(e.ruecktaste(), 'zurueckgenommen')
        self.assertEqual(ereignis, [('klick', 'a')]); self.assertEqual(e.puffer, [])
    def test_op09_ohne_klick_aufruf_bleibt_stumm(self):
        """Ohne klick-Aufruf (Pruefungen) aendert sich nichts: keine Ausnahme, die Anzeige kommt bei der Annahme."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append); e.lage = 'KB'; k0._wartet_auf = 'SW'
        self.assertEqual(e.tippen('a'), 'geliefert'); self.assertEqual(echo, ['a'])
    def test_lage_des_rechners_spielt_keine_rolle(self):
        """Regel 18.10.2026: nur die Lage des SW zaehlt. SW auf KB, Rechner auf GB: eine Ziffer geht allein (ein Eingabezeichen)."""
        m = FakeMaschine(); m.zeichenlage = 'GB'; k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.1); erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            e.lage = 'KB'                                                    # das SW steht auf KB (Vorzustand)
            self.assertTrue(self._warte(e.erwartet))
            self.assertEqual(e.tippen('2'), 'geliefert')                     # nur die Ziffer, kein Umschaltzeichen
            self.assertTrue(self._warte(lambda: erhalten == ['2']))
            self.assertEqual(m.zeichenlage, 'GB'); self.assertEqual(e.lage, 'KB')   # keine der beiden Lagen hat sich geaendert
        finally:
            stop.set(); k0.abbrechen()

    def test_sw_auf_gb_ziffer_braucht_um_kb_und_ziffer(self):
        """SW auf GB, Rechner auf KB: Um. KB und dann die Ziffer, der Rechner bekommt zwei Eingabezeichen; danach steht das SW auf KB."""
        m = FakeMaschine(); m.zeichenlage = 'KB'; k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.1); e.lage = 'GB'
        erhalten = []; stop = threading.Event(); self._rechner(m, k0, erhalten, stop)
        try:
            self.assertTrue(self._warte(e.erwartet))
            self.assertEqual(e.tippen('2'), 'folgt')
            self.assertTrue(self._warte(lambda: erhalten == ['Um. KB'])); self.assertEqual(e.lage, 'KB')
            self.assertTrue(self._warte(lambda: (e.liefern(), erhalten == ['Um. KB', '2'])[1]))
            self.assertIsNone(e.zweite)
        finally:
            stop.set(); k0.abbrechen()
    def test_vorzustand_unbestimmt_erstes_zeichen_sendet_immer_das_umschaltzeichen(self):
        """Regel 18.10.2026 (G3-008): Nach dem Einschalten ist die Lage des SW unbestimmt, das Fenster kennt sie nicht. Fuer das ERSTE Zeichen
        mit bestimmter Lage geht deshalb IMMER das Umschaltzeichen zum Rechner ('A': Um. GB, A; danach steht das SW auf GB). Danach entscheidet
        das vorhergehende Zeichen ('3' nach 'A': Um. KB und 3; '4' nach '3': nur 4)."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.1); erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            self.assertIsNone(e.lage)
            self.assertTrue(self._warte(e.erwartet))
            self.assertEqual(e.tippen('A'), 'folgt')                                        # erstes Zeichen: Um. GB zuerst
            self.assertTrue(self._warte(lambda: erhalten == ['Um. GB'])); self.assertEqual(e.lage, 'GB')
            self.assertTrue(self._warte(lambda: (e.liefern(), erhalten == ['Um. GB', 'A'] and e.erwartet())[1]))
            self.assertEqual(e.tippen('3'), 'folgt')                                        # Ziffer braucht KB: Um. KB, dann 3
            self.assertTrue(self._warte(lambda: erhalten == ['Um. GB', 'A', 'Um. KB'])); self.assertEqual(e.lage, 'KB')
            self.assertTrue(self._warte(lambda: (e.liefern(), erhalten == ['Um. GB', 'A', 'Um. KB', '3'])[1]))
            self.assertTrue(self._warte(e.erwartet))
            self.assertEqual(e.tippen('4'), 'geliefert')                                    # Lage unveraendert: nur das Zeichen
            self.assertTrue(self._warte(lambda: erhalten == ['Um. GB', 'A', 'Um. KB', '3', '4']))
        finally:
            stop.set(); k0.abbrechen()

    def test_vorzustand_unbestimmt_kleinbuchstabe_sendet_um_kb(self):
        """'a' als erstes Zeichen: Um. KB, a; das SW steht danach auf KB (Antwort 18.10.2026)."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.05); erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            self.assertTrue(self._warte(e.erwartet))
            self.assertEqual(e.tippen('a'), 'folgt')
            self.assertTrue(self._warte(lambda: (e.liefern(), erhalten == ['Um. KB', 'a'])[1])); self.assertEqual(e.lage, 'KB')
        finally:
            stop.set(); k0.abbrechen()

    def test_zeichen_mit_gleichem_code_in_beiden_lagen_setzen_die_lage_nicht(self):
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.1); erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            self.assertTrue(self._warte(e.erwartet))
            self.assertEqual(e.tippen(' '), 'geliefert'); self.assertIsNone(e.lage)         # ZR gilt in beiden Lagen
            self.assertTrue(self._warte(lambda: erhalten == ['ZR'] and e.erwartet()))
            self.assertEqual(e.tippen('b'), 'folgt'); self.assertEqual(e.lage, 'KB')            # ZR hat die Lage nicht gesetzt: 'b' als erstes Zeichen mit Lage sendet Um. KB
        finally:
            stop.set(); k0.abbrechen()

    def test_abbilden_ohne_vorzustand(self):
        self.assertEqual(abbilden('A', None), ['Um. GB', 'A']); self.assertEqual(abbilden('3', None), ['Um. KB', '3'])     # erstes Zeichen: immer mit Umschaltzeichen
        self.assertEqual(abbilden('a', None), ['Um. KB', 'a']); self.assertEqual(abbilden(' ', None), ['ZR'])           # ZR, TAB, WRZL: allein
        self.assertEqual(abbilden('A', 'KB'), ['Um. GB', 'A']); self.assertEqual(abbilden('3', 'GB'), ['Um. KB', '3'])
        self.assertEqual(abbilden('3', 'KB'), ['3']); self.assertEqual(abbilden('A', 'GB'), ['A'])
        self.assertIsNone(abbilden('ä', None))

    @alter_puffer
    def test_keine_zeichen_zwischen_den_zwei_eingaben(self):
        """Zeichen zwischen den zwei Eingaben gibt es nicht (18.10.2026): kommt die naechste Taste, ist die ausstehende zweite Eingabe frei und
        geht vor ihr hinaus; mit Puffer (G4-007) geht nichts verloren, die Reihenfolge bleibt."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m); e.lage = 'KB'; erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            self.assertTrue(self._warte(e.erwartet)); self.assertEqual(e.tippen('A'), 'folgt')
            self.assertEqual(e.tippen('b'), 'vorgemerkt')                    # ('A' war ohne Loslassen noch nicht frei: jetzt frei, dann 'Um. KB', 'b')
            self.assertTrue(self._warte(lambda: (e.loslassen(), e.liefern(), erhalten == ['Um. GB', 'A', 'Um. KB', 'b'])[2]))     # 'b' geht beim Loslassen (Fall b)
        finally:
            stop.set(); k0.abbrechen()
    def test_abstand_kommt_von_den_tasten(self):
        """U-11: ohne abstand geht die zweite Eingabe erst beim Loslassen (liefern() sendet nichts); mit gemessenem abstand nach dieser Zeit."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); t = [0.0]; e = SwEingabe(k0, m, zeit=lambda: t[0]); e.lage = 'KB'; erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            self.assertTrue(self._warte(e.erwartet)); self.assertEqual(e.tippen('A'), 'folgt')
            t[0] = 5.0; self.assertIsNone(e.liefern())              # kein fester Abstand: ohne Loslassen kommt nichts
            self.assertTrue(self._warte(e.erwartet)); self.assertEqual(e.loslassen(), 'geliefert')
            self.assertTrue(self._warte(lambda: erhalten == ['Um. GB', 'A']))
            self.assertTrue(self._warte(e.erwartet)); self.assertEqual(e.tippen('3', abstand=0.37), 'folgt')
            t[0] = 5.2; self.assertIsNone(e.liefern()); t[0] = 5.37; self.assertTrue(self._warte(e.erwartet)); self.assertEqual(e.liefern(), 'geliefert')
        finally:
            stop.set(); k0.abbrechen()

    def test_grossbuchstabe_geht_nicht_verloren_wenn_rechner_noch_beim_umschaltzeichen(self):
        """G4-007 (Fehler 19.10.2026: bei Grossbuchstaben fehlten Zeichen): Bearbeitet der Rechner das Umschaltzeichen noch, wenn die zweite Eingabe
        faellig ist, wartet das Zeichen im Puffer und geht an den naechsten 011; es erscheint erst dann."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append, abstand=0.005); e.lage = 'KB'
        erhalten = []; stop = threading.Event()

        def langsamer_rechner():                  # braucht nach dem Umschaltzeichen 0,3 s (kein 011 aktiv), dann wieder 011
            while not stop.is_set():
                try:
                    t = k0.naechstes()
                except Exception:
                    return
                erhalten.append(t)
                if t == 'Um. GB':
                    time.sleep(0.3)
        threading.Thread(target=langsamer_rechner, daemon=True).start()
        try:
            self.assertTrue(self._warte(e.erwartet)); self.assertEqual(e.tippen('A'), 'folgt')
            self.assertTrue(self._warte(lambda: erhalten == ['Um. GB']))
            time.sleep(0.03); self.assertFalse(e.erwartet())                 # der Rechner ist noch nicht wieder bei 011
            self.assertIsNone(e.liefern()); self.assertEqual(echo, [])       # Zeichen wartet, keine Anzeige
            self.assertEqual(e.ausstehend(), 1)
            self.assertTrue(self._warte(lambda: (e.liefern(), echo == ['A'])[1], 2.0))   # ... und kommt beim naechsten 011
            self.assertTrue(self._warte(lambda: erhalten == ['Um. GB', 'A'])); self.assertEqual(e.ausstehend(), 0)
        finally:
            stop.set(); k0.abbrechen()
    def test_ein_011_bekommt_genau_ein_zeichen(self):
        """S3-13/S3-14 (G4-007): Hat der aktive 011 sein Zeichen, aber der Rechner hat es noch nicht geholt, bekommt er kein zweites; das zweite wartet
        im Puffer und wird NICHT angezeigt (sonst stuende ein Zeichen im Fenster, das den Rechner nicht erreicht hat)."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append, abstand=0.1); e.lage = 'KB'
        k0._wartet_auf = 'SW'                                                # ein 011 ist aktiv, der Rechner holt gerade nicht
        self.assertTrue(e.erwartet()); self.assertEqual(e.tippen('a'), 'geliefert')
        self.assertFalse(e.erwartet()); self.assertEqual(e.tippen('b'), 'vorgemerkt')
        self.assertEqual(echo, ['a']); self.assertEqual(list(k0._q['SW']), ['a']); self.assertEqual(e.ausstehend(), 1)
    # --- G4-008: ein Tastendruck im Puffer ---------------------------------------------------------------------------------------
    @ein_tastendruck
    def test_ein_tastendruck_naechste_taste_erst_nach_abholung(self):
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m, echo=lambda t: None, abstand=0.0); e.lage = 'KB'
        self.assertEqual(e.tippen('a'), 'vorgemerkt')                    # Rechner nicht bei 011: ein Zeichen wartet
        self.assertEqual(e.tippen('b'), 'voll')                          # die naechste Taste erst, wenn ein Eingabebefehl 'a' abgeholt hat
        self.assertEqual([x[0] for x in e.puffer], ['a'])
        k0._wartet_auf = 'SW'; self.assertEqual(e.liefern(), 'geliefert')  # 011 holt 'a' ab
        k0._wartet_auf = None; k0._q['SW'].clear()                          # Rechner hat es uebernommen
        self.assertEqual(e.tippen('b'), 'vorgemerkt')                    # jetzt wieder eine Eingabe moeglich

    @ein_tastendruck
    def test_ein_tastendruck_paar_sperrt_bis_beide_abgeholt(self):
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m, echo=lambda t: None, abstand=0.0); e.lage = 'KB'
        self.assertEqual(e.tippen('A'), 'vorgemerkt')                    # Umschalter + Zeichen = EIN Tastendruck (2 Eingaben)
        self.assertEqual([x[0] for x in e.puffer], ['Um. GB', 'A'])
        self.assertEqual(e.tippen('x'), 'voll')
        k0._wartet_auf = 'SW'; e.liefern()                               # 011 holt den Umschalter
        k0._wartet_auf = None; k0._q['SW'].clear()
        self.assertEqual(e.tippen('x'), 'voll')                          # das Zeichen des Paares ist noch nicht abgeholt
        k0._wartet_auf = 'SW'; e.liefern()
        k0._wartet_auf = None; k0._q['SW'].clear()
        self.assertEqual(e.tippen('x'), 'vorgemerkt')

    @ein_tastendruck
    def test_ein_tastendruck_ohne_kanal_sw_weiter_blockiert(self):
        m = FakeMaschine(); m.fl['SW'] = 0; k0 = K0Warteschlange(m); e = SwEingabe(k0, m, echo=lambda t: None)
        self.assertEqual(e.tippen('a'), 'blockiert'); self.assertEqual(e.puffer, [])

    @alter_puffer
    def test_kanalwechsel_verwirft_den_puffer(self):
        """G4-007: Wechselt der Kanal (hier: Schalter SW geloest, Quelle T; oder Zaehler kanal_wechsel), wird der Puffer verworfen; die Taste ist blockiert."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append, abstand=0.1); e.lage = 'KB'
        self.assertEqual(e.tippen('a'), 'vorgemerkt'); self.assertEqual(e.tippen('b'), 'vorgemerkt'); self.assertEqual(e.ausstehend(), 2)
        m.fl['SW'] = 0; m.fl['T'] = 1                                        # Schalter SW geloest
        self.assertEqual(e.liefern(), 'verworfen'); self.assertEqual(e.ausstehend(), 0); self.assertEqual(e.verworfen_zaehler, 2)
        self.assertEqual(e.tippen('a'), 'blockiert'); self.assertEqual(e.tippen('A'), 'blockiert')
        k0._wartet_auf = 'SW'; self.assertIsNone(e.liefern()); self.assertEqual(echo, []); self.assertEqual(list(k0._q['SW']), [])
        m.fl['SW'] = 1; m.fl['T'] = 0                                        # wieder K0/SW
        self.assertEqual(e.tippen('a'), 'geliefert')
    @alter_puffer
    def test_zaehler_kanalwechsel_verwirft_auch_wenn_k0_wieder_angewaehlt(self):
        """Ein Programm, das zwischen zwei Eingaben K2 anwaehlt und K0 wieder (schneller als der Takt): der Puffer von vorher ist trotzdem weg.
        Die erneute Anwahl desselben Kanals (kein Wechsel, Zaehler bleibt) leert ihn nicht."""
        m = FakeMaschine(); m.kanal_wechsel = 0; k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.1); e.lage = 'KB'
        e.tippen('a'); e.tippen('b')
        self.assertIsNone(e.liefern()); self.assertEqual(e.ausstehend(), 2)  # gleicher Kanal: bleibt
        m.kanal_wechsel += 1                                                 # K2 und zurueck: Zaehler weiter, Flags wieder wie vorher
        self.assertEqual(e.liefern(), 'verworfen'); self.assertEqual(e.ausstehend(), 0)
        self.assertEqual(e.tippen('c'), 'vorgemerkt')                        # danach wird wieder vorgemerkt
    @alter_puffer
    def test_zweite_haelfte_eines_paares_ueberlebt_den_kanalwechsel(self):
        """Umschaltzeichen und Zeichen sind EIN Tastendruck: ist das Umschaltzeichen schon beim Rechner und wechselt dann der Kanal (das Programm
        gibt z. B. eine Meldung ueber K2 aus), geht das Zeichen trotzdem noch an den naechsten 011; alles Uebrige im Puffer wird verworfen."""
        m = FakeMaschine(); m.kanal_wechsel = 0; k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append, abstand=0.0); e.lage = 'KB'
        k0._wartet_auf = 'SW'
        self.assertEqual(e.tippen('A'), 'folgt')                              # Um. GB ist beim Rechner, A wartet
        self.assertEqual(e.tippen('b'), 'vorgemerkt'); self.assertEqual(e.ausstehend(), 3)    # A, Um. KB, b
        m.kanal_wechsel += 1
        self.assertEqual(e.liefern(), 'verworfen'); self.assertEqual([x[0] for x in e.puffer], ['A'])
        k0._q['SW'].clear(); k0._wartet_auf = 'SW'
        self.assertEqual(e.liefern(), 'geliefert'); self.assertEqual(echo, ['A']); self.assertEqual(e.ausstehend(), 0)
    def test_paar_wird_mit_seinem_ersten_zusammen_verworfen(self):
        m = FakeMaschine(); m.kanal_wechsel = 0; k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.0); e.lage = 'KB'
        self.assertEqual(e.tippen('A'), 'vorgemerkt')                         # kein 011: Um. GB und A im Puffer
        m.kanal_wechsel += 1
        self.assertEqual(e.liefern(), 'verworfen'); self.assertEqual(e.ausstehend(), 0)
    @alter_puffer
    def test_puffer_voll(self):
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.1); e.lage = 'KB'
        for z in 'abcdefgh':
            self.assertEqual(e.tippen(z), 'vorgemerkt')
        self.assertEqual(e.tippen('i'), 'voll'); self.assertEqual(e.ausstehend(), 8)
        e.ruecktaste(); self.assertEqual(e.tippen('i'), 'vorgemerkt')
    @alter_puffer
    def test_paar_kommt_ganz_oder_gar_nicht_in_den_puffer(self):
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.0); e.lage = 'KB'
        for z in 'abcdefg':
            e.tippen(z)
        self.assertEqual(e.tippen('A'), 'voll'); self.assertEqual(e.ausstehend(), 7)     # Um. GB + A passen nicht mehr (7 + 2 > 8)
        self.assertEqual(e._lage_vorschau(), 'KB')
    @alter_puffer
    def test_puffer_in_reihenfolge_je_011_eine_eingabe(self):
        """Der Rechner ist langsamer als das Tippen: alle Zeichen kommen, in der Reihenfolge, je 011 eines."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append, abstand=0.0); e.lage = 'KB'
        erhalten = []; stop = threading.Event()

        def rechner():
            while not stop.is_set():
                try:
                    t = k0.naechstes()
                except Exception:
                    return
                erhalten.append(t); time.sleep(0.02)
        threading.Thread(target=rechner, daemon=True).start()
        try:
            self.assertTrue(self._warte(e.erwartet))
            for z in 'Hallo':
                e.tippen(z)
            self.assertTrue(self._warte(lambda: (e.liefern(), len(erhalten) == 7)[1], 3.0))     # Um. GB, H, Um. KB, a, l, l, o
            self.assertTrue(self._warte(lambda: echo == list('Hallo')))
            self.assertEqual(e.ausstehend(), 0)
            self.assertEqual(erhalten, ['Um. GB', 'H', 'Um. KB', 'a', 'l', 'l', 'o'])
        finally:
            stop.set(); k0.abbrechen()
    def test_echo_nur_fuer_angenommene_zeichen(self):
        """S3-04 neu: Jedes angenommene Zeichen wird angezeigt (ZR, TAB, WRZL eingeschlossen), nicht angenommene und blockierte nicht,
        Umschaltzeichen nie; bei zwei Eingaben erscheint das Zeichen einmal, erst wenn es angenommen ist."""
        m = FakeMaschine(); k0 = K0Warteschlange(m); echo = []; e = SwEingabe(k0, m, echo=echo.append, abstand=0.02); e.lage = 'KB'; erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            for z, soll in (('a', 'a'), (' ', ' '), ('\t', '\t'), ('\r', '\n'), ('7', '7')):
                self.assertTrue(self._warte(e.erwartet)); n = len(erhalten)
                self.assertEqual(e.tippen(z), 'geliefert'); self.assertTrue(self._warte(lambda: len(erhalten) == n + 1))
                self.assertEqual(echo[-1], soll)
            self.assertEqual(len(echo), 5)
            self.assertTrue(self._warte(e.erwartet)); self.assertEqual(e.tippen('ä'), 'verworfen'); self.assertEqual(len(echo), 5)
            self.assertEqual(e.tippen('A'), 'folgt'); self.assertEqual(len(echo), 5)                  # Um. GB: keine Anzeige
            self.assertTrue(self._warte(lambda: (e.liefern(), echo[-1:] == ['A'])[1]))
            self.assertEqual(echo, ['a', ' ', '\t', '\n', '7', 'A'])
            self.assertEqual([t for t in erhalten if t.startswith('Um.')], ['Um. GB'])
        finally:
            stop.set(); k0.abbrechen()
    def test_nicht_angenommenes_zeichen_still_verworfen(self):
        m = FakeMaschine(); k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.1); erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            self.assertTrue(self._warte(e.erwartet))
            self.assertEqual(e.tippen('ä'), 'verworfen'); time.sleep(0.1)
            self.assertEqual(erhalten, []); self.assertTrue(e.erwartet())     # Rechner wartet weiter
        finally:
            stop.set(); k0.abbrechen()

    def test_t_quelle_wird_nicht_vom_sw_fenster_bedient(self):
        m = FakeMaschine(); m.fl['SW'] = 0; m.fl['T'] = 1
        k0 = K0Warteschlange(m); e = SwEingabe(k0, m, abstand=0.1); erhalten = []; stop = threading.Event()
        self._rechner(m, k0, erhalten, stop)
        try:
            self.assertTrue(self._warte(lambda: k0.erwartet('T')))
            self.assertEqual(e.tippen('a'), 'blockiert'); self.assertFalse(e.eingabe_aktiv())      # Quelle T: das SW-Fenster bedient sie nicht
        finally:
            stop.set(); k0.abbrechen()


def _fake_tk():
    class W:
        def __init__(s, *a, **k):
            s.cfg = dict(k); s.bound = {}; s.titel = None; s.text = '\n'; s.focus = False; s.nach = []; s.geom = None
        def bind(s, f, fn, add=None): s.bound[f] = fn
        def pack(s, *a, **k): pass
        def title(s, t=None):
            if t is not None: s.titel = t
            return s.titel
        def resizable(s, *a): pass
        def update_idletasks(s): pass
        def winfo_reqwidth(s): return 900
        def winfo_reqheight(s): return 600
        def winfo_screenwidth(s): return 1920
        def winfo_screenheight(s): return 1080
        def geometry(s, g): s.geom = g
        def protocol(s, n, fn): s.bound[n] = fn
        def after(s, ms, fn=None): s.nach.append(fn); return len(s.nach)
        def lift(s): s.lifted = True
        def focus_set(s): s.focus = True
        def focus_get(s): return s if s.focus else None
        def configure(s, **k): s.cfg.update(k)
        def destroy(s): s.zerstoert = True
        def index(s, i):
            return '%d.0' % (s.text.count('\n') + 1) if i == 'end-1c' else '1.0'
        def insert(s, pos, txt, *tags):
            if pos == 'end': s.text = s.text[:-1] + txt + '\n'
            else:
                n = int(pos.split('.')[0]); zl = s.text.split('\n'); zl[n - 1] = txt + zl[n - 1]; s.text = '\n'.join(zl)
        def delete(s, a, b):
            n = int(a.split('.')[0]); zl = s.text.split('\n'); zl[n - 1] = ''; s.text = '\n'.join(zl)
        def see(s, i): pass
        def get(s, a, b): raise tk.TclError('nichts markiert')
        def tag_add(s, *a): pass
        def add_command(s, **k): pass
        def tk_popup(s, *a): pass
        def grab_release(s): pass
    tk = types.SimpleNamespace(Toplevel=W, Text=W, Menu=W, TclError=type('TclError', (Exception,), {}))
    return tk


class PultAttrappe:
    def __init__(s):
        s.root = types.SimpleNamespace(lift=lambda: setattr(s, 'pult_lift', True))
        s.cv = types.SimpleNamespace(focus_set=lambda: setattr(s, 'pult_fokus', True))
        s.geschlossen = 0
        s._schliessen = lambda: setattr(s, 'geschlossen', s.geschlossen + 1)


class FensterMitErsatzmodul(unittest.TestCase):
    """Tk-Schicht gegen ein Ersatzmodul (KEIN echtes Tkinter): prueft nur Verdrahtung und Aufrufe, nicht das Aussehen."""
    def _bauen(self):
        from c8205_grafik import SwSenke
        from grafik_sw_fenster import SwFenster
        m = FakeMaschine(); k0 = K0Warteschlange(m); senke = SwSenke(); pult = PultAttrappe()
        f = SwFenster(pult, senke, k0, m, bei_schliessen=pult._schliessen, tk=_fake_tk())
        return f, senke, k0, m, pult

    def test_ausgabe_kommt_an_im_tk_thread(self):
        f, senke, k0, m, pult = self._bauen()
        senke.schreibe('Hallo'); senke.schreibe('\t'); senke.schreibe('x\n')
        f.takt()
        self.assertEqual(f.anzeige.zeile_text(0), 'Hallo' + ' ' * 7 + 'x')
        self.assertIn('Hallo' + ' ' * 7 + 'x', f.txt.text)

    def test_benannte_zeichen_im_fenster_nicht_angezeigt(self):
        f, senke, k0, m, pult = self._bauen()
        for z in ('a', '<ZV>', '<Irrung Satz>', 'b'):
            senke.schreibe(z)
        f.takt()
        self.assertEqual(f.anzeige.zeile_text(0), 'ab'); self.assertNotIn('<', f.txt.text)

    def test_bereits_geschriebener_text_erscheint(self):
        from c8205_grafik import SwSenke
        from grafik_sw_fenster import SwFenster
        m = FakeMaschine(); k0 = K0Warteschlange(m); senke = SwSenke(); senke.schreibe('frueher'); pult = PultAttrappe()
        f = SwFenster(pult, senke, k0, m, tk=_fake_tk()); f.takt()
        self.assertEqual(f.anzeige.zeile_text(0), 'frueher')

    def test_x_ist_wie_strg_c(self):
        f, senke, k0, m, pult = self._bauen()
        f.w.bound['WM_DELETE_WINDOW']()
        self.assertEqual(pult.geschlossen, 1)

    # --- G4-008: Tasten, die beim PULT ankommen (Fokus in der Luecke zwischen zwei Eingabeaufforderungen) ------------------------
    def _ev(self, char, keysym=None, state=0):
        return types.SimpleNamespace(char=char, keysym=keysym or char, state=state)

    def test_taste_am_pult_geht_an_die_sw_eingabe(self):
        """Lauf 19.10.2026: Der Fokus lag nach einem Zeichen kurz beim Pult; die Taste kam dort an (wirkt=False) und war verloren."""
        f, senke, k0, m, pult = self._bauen()
        f.eingabe.lage = 'KB'
        self.assertTrue(f.taste_vom_pult(self._ev('s')))                      # Rechner noch nicht bei 011: Puffer
        self.assertEqual(f.eingabe.ausstehend(), 1)
        k0._wartet_auf = 'SW'; f.takt()                                       # 011 aktiv: der Takt gibt das Zeichen weiter
        self.assertEqual(f.eingabe.ausstehend(), 0); self.assertEqual(list(k0._q['SW']), ['s'])
        f.takt(); self.assertEqual(f.anzeige.zeile_text(0), 's')

    def test_taste_am_pult_ohne_kanal_sw_bleibt_beim_pult(self):
        f, senke, k0, m, pult = self._bauen()
        m.fl['SW'] = 0; m.fl['T'] = 1
        self.assertFalse(f.taste_vom_pult(self._ev('5')))                     # die Pult-Tastatur (T) wertet sie selbst aus
        self.assertEqual(f.eingabe.ausstehend(), 0)

    def test_umschalttaste_am_pult_wird_gemerkt_und_beim_loslassen_vergessen(self):
        f, senke, k0, m, pult = self._bauen()
        m.fl['SW'] = 0; m.fl['T'] = 1                                         # auch ohne K0/SW: Umschalttaste merken, Loslassen raeumt auf
        self.assertTrue(f.taste_vom_pult(self._ev('', 'Shift_L')))
        self.assertIn('Shift_L', f._umschalt)
        f.taste_los_vom_pult(self._ev('', 'Shift_L'))
        self.assertNotIn('Shift_L', f._umschalt)

    def test_grossbuchstabe_am_pult_mit_umschalttaste_am_pult(self):
        f, senke, k0, m, pult = self._bauen()
        f.eingabe.lage = 'KB'
        f.taste_vom_pult(self._ev('', 'Shift_L'))
        f.taste_vom_pult(self._ev('D'))
        self.assertEqual([e[0] for e in f.eingabe.puffer], ['Um. GB', 'D'])    # Paar im Puffer, Reihenfolge bleibt

    def test_groesse_und_lage(self):
        f, *_ = self._bauen()
        self.assertEqual((f.txt.cfg['width'], f.txt.cfg['height'], f.txt.cfg['wrap']), (130, 36, 'none'))
        self.assertEqual(f.w.geom, '+1010+410')                      # rechts unten wie "SW Ausgabe"

    def test_titel_und_fokus_bei_eingabe(self):
        f, senke, k0, m, pult = self._bauen()
        erhalten = []; stop = threading.Event()
        def rechner():
            while not stop.is_set():
                try: erhalten.append(k0.naechstes())
                except Exception: return
        threading.Thread(target=rechner, daemon=True).start()
        try:
            t0 = time.time()
            while not k0.erwartet('SW') and time.time() - t0 < 2: time.sleep(0.005)
            f.takt()
            f.eingabe.lage = 'KB'                                                            # SW steht auf KB (Vorzustand, hier nicht Thema)
            self.assertIn('Eingabe erwartet', f.w.titel); self.assertTrue(f.txt.focus)       # Fokus angefordert
            ev = types.SimpleNamespace(char='a', keysym='a', state=0)
            self.assertEqual(f._taste(ev), 'break')
            t0 = time.time()
            while erhalten != ['a'] and time.time() - t0 < 2: time.sleep(0.005)
            self.assertEqual(erhalten, ['a'])
        finally:
            stop.set(); k0.abbrechen()

    # --- OP-32: Entprellung des Fokus (0,4 s ohne Eingabeaufforderung, GRAFIK_Beschreibung §5.7) ---------------------------------
    def _fokus_vorbereiten(self):
        """SW-Fenster mit steuerbarer Aufforderung (aktiv) und steuerbarer Uhr; liefert (f, pult, uhr, setze_aktiv)."""
        import grafik_sw_fenster
        f, senke, k0, m, pult = self._bauen()
        zustand = {'aktiv': True}; uhr = [100.0]
        f.eingabe.eingabe_aktiv = lambda: zustand['aktiv']
        f.w.focus_get = lambda: f.txt if f.txt.focus else None       # echtes Tk liefert das fokussierte Widget; die Attrappe sonst das Fenster selbst
        orig = grafik_sw_fenster.time.monotonic
        grafik_sw_fenster.time.monotonic = lambda: uhr[0]
        self.addCleanup(setattr, grafik_sw_fenster.time, 'monotonic', orig)
        return f, pult, uhr, lambda a: zustand.__setitem__('aktiv', a)

    def test_fokus_entprellung_bleibt_unter_0_4_s_im_sw_fenster(self):
        f, pult, uhr, setze = self._fokus_vorbereiten()
        f._fokus()                                                   # Aufforderung da: Fokus angefordert
        self.assertTrue(f.txt.focus); self.assertTrue(f._fokus_angefordert)
        setze(False); f._fokus()                                     # Aufforderung weg: Uhr startet
        uhr[0] += 0.375; f._fokus()                                  # 0,375 s: noch nicht zurueck
        self.assertFalse(getattr(pult, 'pult_fokus', False)); self.assertTrue(f._fokus_angefordert)

    def test_fokus_geht_nach_0_4_s_ohne_aufforderung_zum_pult(self):
        f, pult, uhr, setze = self._fokus_vorbereiten()
        f._fokus(); setze(False); f._fokus()
        uhr[0] += 0.5; f._fokus()                                    # Schwelle (0,4 s) ueberschritten
        self.assertTrue(getattr(pult, 'pult_fokus', False)); self.assertTrue(getattr(pult, 'pult_lift', False))
        self.assertFalse(f._fokus_angefordert)

    def test_fokus_neue_aufforderung_setzt_die_uhr_zurueck(self):
        f, pult, uhr, setze = self._fokus_vorbereiten()
        f._fokus(); setze(False); f._fokus()
        uhr[0] += 0.25; f._fokus()                                   # Luecke zwischen zwei Eingabe-Halts
        setze(True); f._fokus()                                      # naechster Eingabe-Halt: Uhr zurueck
        setze(False); f._fokus()                                     # neue Luecke beginnt
        uhr[0] += 0.25; f._fokus()                                   # 0,5 s seit der ersten, aber nur 0,25 s seit der letzten Luecke
        self.assertFalse(getattr(pult, 'pult_fokus', False)); self.assertTrue(f._fokus_angefordert)
        uhr[0] += 0.25; f._fokus()                                   # insgesamt 0,5 s seit Beginn der letzten Luecke
        self.assertTrue(getattr(pult, 'pult_fokus', False))

    def _rechner_faden(self, k0):
        erhalten = []; stop = threading.Event()
        def rechner():
            while not stop.is_set():
                try: erhalten.append(k0.naechstes())
                except Exception: return
        threading.Thread(target=rechner, daemon=True).start()
        return erhalten, stop

    def _warte(self, bed, s=2.0):
        t0 = time.time()
        while time.time() - t0 < s:
            if bed(): return True
            time.sleep(0.005)
        return False

    def test_eingabe_wird_angezeigt_in_der_reihenfolge_mit_der_ausgabe(self):
        """S3-04 neu (U-1, U-2): angenommene Zeichen erscheinen im Fenster, auf derselben Schreibposition wie die Ausgabe des Rechners."""
        f, senke, k0, m, pult = self._bauen(); erhalten, stop = self._rechner_faden(k0)
        ev = lambda c, k=None: types.SimpleNamespace(char=c, keysym=k or c, state=0)
        try:
            self.assertTrue(self._warte(lambda: k0.erwartet('SW'))); f.eingabe.lage = 'KB'      # SW steht auf KB (Vorzustand, hier nicht Thema)
            f._taste(ev('a')); self.assertTrue(self._warte(lambda: erhalten == ['a']))
            senke.schreibe('X')                                           # Ausgabe des Rechners nach der Eingabe
            self.assertTrue(self._warte(lambda: k0.erwartet('SW')))
            f._taste(ev('b')); self.assertTrue(self._warte(lambda: erhalten == ['a', 'b']))
            f.takt()
            self.assertEqual(f.anzeige.zeile_text(0), 'aXb')              # a, X, b: eine Reihenfolge, eine Schreibposition
            self.assertEqual(f.anzeige.pos, 3)
            self.assertTrue(self._warte(lambda: k0.erwartet('SW')))
            f._taste(ev('\r', 'Return')); self.assertTrue(self._warte(lambda: erhalten == ['a', 'b', 'WRZL']))
            f.takt(); self.assertEqual(f.anzeige.zeile_text(1), ''); self.assertEqual(f.anzeige.pos, 0)    # WRZL: neue Zeile
        finally:
            stop.set(); k0.abbrechen()

    def test_blockierte_und_nicht_angenommene_tasten_erscheinen_nicht(self):
        f, senke, k0, m, pult = self._bauen()                              # kein Rechner: kein 011 aktiv
        ev = lambda c, k=None: types.SimpleNamespace(char=c, keysym=k or c, state=0)
        f._taste(ev('a')); f.takt()
        self.assertEqual(f.anzeige.zeile_text(0), ''); self.assertNotIn('a', f.txt.text)       # blockiert: keine Anzeige
        erhalten, stop = self._rechner_faden(k0)
        try:
            self.assertTrue(self._warte(lambda: k0.erwartet('SW')))
            f._taste(ev('\u00e4')); f.takt()                                # ae ist nicht im R300-Code: nicht angenommen, nicht angezeigt
            self.assertEqual(f.anzeige.zeile_text(0), ''); self.assertEqual(erhalten, [])
        finally:
            stop.set(); k0.abbrechen()

    def test_zeichen_in_der_anderen_lage_zwei_eingaben_eine_anzeige(self):
        f, senke, k0, m, pult = self._bauen(); erhalten, stop = self._rechner_faden(k0)
        f.eingabe.abstand = 0.03; f.eingabe.lage = 'KB'
        try:
            self.assertTrue(self._warte(lambda: k0.erwartet('SW')))
            f._taste(types.SimpleNamespace(char='A', keysym='A', state=1))
            self.assertTrue(self._warte(lambda: erhalten == ['Um. GB']))
            f.takt(); self.assertEqual(f.anzeige.zeile_text(0), '')       # Umschaltzeichen: keine Anzeige
            self.assertTrue(self._warte(lambda: (f.takt(), erhalten == ['Um. GB', 'A'])[1]))   # zweite Eingabe im Takt des Fensters
            f.takt(); self.assertEqual(f.anzeige.zeile_text(0), 'A')
        finally:
            stop.set(); k0.abbrechen()

    def test_sondertasten_und_ignorierte_tasten(self):
        f, senke, k0, m, pult = self._bauen()
        e = types.SimpleNamespace
        self.assertIsNone(f._taste(e(char='\x03', keysym='c', state=4)))                  # Strg+C: Kopieren, keine Eingabe
        self.assertEqual(f._taste(e(char='\x08', keysym='BackSpace', state=0)), 'break')   # G4-006: Rücktaste hat Löschwirkung (nicht mehr "ohne Wirkung", S3-10)
        self.assertIsNone(f._taste(e(char='', keysym='F5', state=0)))
        self.assertEqual(f._taste(e(char='\t', keysym='Tab', state=0)), 'break')          # Tab: nicht zum Fokuswechsel verwenden

    def test_ruecktaste_loescht_in_der_anzeige(self):
        """G4-006: Rücktaste im Fenster: letztes angezeigtes Zeichen weg, kein Name, nichts an den Rechner, auch ohne aktiven 011."""
        f, senke, k0, m, pult = self._bauen()
        e = types.SimpleNamespace
        f.q.put('abc'); f.takt(); self.assertEqual(f.anzeige.zeile_text(0), 'abc')
        for _ in range(2):
            self.assertEqual(f._taste(e(char='\x08', keysym='BackSpace', state=0)), 'break')
        f.takt(); self.assertEqual(f.anzeige.zeile_text(0), 'a')
        self.assertEqual(list(k0._q['SW']), []); self.assertEqual(list(k0._q['T']), [])
        self.assertEqual(f._taste(e(char='\x08', keysym='BackSpace', state=4)), None)       # Strg+Rücktaste: ohne Wirkung

    def test_ende_nach_beenden(self):
        f, *_ = self._bauen()
        f.beenden(); self.assertTrue(f.beendet); n = len(f.w.nach); f.takt(); self.assertEqual(len(f.w.nach), n)


class WiedergabeTipp(unittest.TestCase):
    """Ereignisart tipp der Wiedergabe (G3-006, Lauf 18.10.2026): Haltezeit statt Loslassen im selben Augenblick; AltGr unter Linux. Ersatzobjekte, KEIN echtes Tkinter."""
    class _W:
        def __init__(self): self.nach = []
        def focus_get(self): return T_TXT[0]
        def after(self, ms, fn): self.nach.append((ms, fn))
    class _Txt:
        def __init__(self): self.ereignisse = []
        def event_generate(self, ev, **kw): self.ereignisse.append((ev, kw))
        def focus_force(self): pass

    def _fenster(self):
        from grafik_sw_fenster import SwFenster
        f = object.__new__(SwFenster)
        f.w = self._W(); f.txt = self._Txt(); T_TXT[0] = f.txt
        f.eingabe = types.SimpleNamespace(erwartet=lambda: True, zweite=None, puffer=[], lage='KB')
        return f

    def test_loslassen_erst_nach_der_haltezeit(self):
        f = self._fenster()
        self.assertTrue(f.tipp_wiedergabe('less'))
        self.assertEqual([e[0] for e in f.txt.ereignisse], ['<KeyPress>'])          # Loslassen noch nicht
        self.assertEqual(len(f.w.nach), 1)
        ms, fn = f.w.nach[0]
        self.assertGreaterEqual(ms, 100)                                              # echte Haltezeit, nicht 0
        fn()
        self.assertEqual([e[0] for e in f.txt.ereignisse], ['<KeyPress>', '<KeyRelease>'])

    def test_altgr_zustand_unter_linux(self):
        f = self._fenster()
        alt = sys.platform
        try:
            sys.platform = 'linux'
            f.tipp_wiedergabe('bracketleft'); f.tipp_wiedergabe('a')
        finally:
            sys.platform = alt
        self.assertEqual(f.txt.ereignisse[0][1].get('state'), 0x80)                  # AltGr (Mod5)
        self.assertNotIn('state', f.txt.ereignisse[1][1])                            # normale Taste ohne Zusatz
        f.w.nach[0][1]()
        self.assertEqual(f.txt.ereignisse[-1][1].get('state'), 0x80)                  # Loslassen mit demselben Zustand


class Fensterlage(unittest.TestCase):
    """FL-001: Fenster merken ihre letzte Position (grafik_fensterlage.py), ohne echtes Tkinter."""
    class _F:
        def __init__(self, geom='1148x860+30+-5', vroot=(0, 0, 1920, 1080)):
            self.g, self.v, self.gesetzt = geom, vroot, []
        def geometry(self, g=None):
            if g is None: return self.g
            self.gesetzt.append(g); self.g = '1148x860' + g
        def winfo_vrootx(self): return self.v[0]
        def winfo_vrooty(self): return self.v[1]
        def winfo_vrootwidth(self): return self.v[2]
        def winfo_vrootheight(self): return self.v[3]

    def setUp(self):
        import tempfile, os
        import grafik_fensterlage as L
        self.L = L; self.dir = tempfile.mkdtemp(); self.alt = os.environ.get('C8205_FENSTERLAGE')
        os.environ['C8205_FENSTERLAGE'] = os.path.join(self.dir, 'unterordner', 'lage.json')
    def tearDown(self):
        import os, shutil
        if self.alt is None: os.environ.pop('C8205_FENSTERLAGE', None)
        else: os.environ['C8205_FENSTERLAGE'] = self.alt
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_ecke_aus_wm_geometry(self):
        for g, soll in (('1148x860+30+-5', (30, -5)), ('+12+34', (12, 34)), ('1x1-1500+20', (-1500, 20)), ('130x36+0+0', (0, 0))):
            self.assertEqual(self.L.ecke(self._F(g)), soll, g)
        self.assertIsNone(self.L.ecke(self._F('unsinn')))
    def test_speichern_und_laden(self):
        self.assertIsNone(self.L.laden('sw'))                       # nichts da, kein Fehler
        self.assertTrue(self.L.speichern('sw', 100, 200)); self.assertTrue(self.L.speichern('pult', -50, 7))
        self.assertEqual(self.L.laden('sw'), (100, 200)); self.assertEqual(self.L.laden('pult'), (-50, 7))
    def test_kaputte_datei_gilt_als_leer(self):
        import os
        os.makedirs(os.path.dirname(self.L.pfad()))
        with open(self.L.pfad(), 'w') as f: f.write('{kaputt')
        self.assertIsNone(self.L.laden('sw')); self.assertTrue(self.L.speichern('sw', 1, 2)); self.assertEqual(self.L.laden('sw'), (1, 2))
    def test_aus_schaltet_ab(self):
        import os
        os.environ['C8205_FENSTERLAGE'] = 'aus'
        self.assertFalse(self.L.speichern('sw', 1, 2)); self.assertIsNone(self.L.laden('sw'))
    def test_anwenden_nur_wenn_sichtbar(self):
        self.L.speichern('sw', 300, 400)
        f = self._F(); self.assertTrue(self.L.anwenden(f, 'sw', 900, 600)); self.assertEqual(f.gesetzt, ['+300+400'])
        self.L.speichern('sw', 5000, 400)                            # Bildschirm abgesteckt / Aufloesung kleiner: Vorgabe
        f = self._F(); self.assertFalse(self.L.anwenden(f, 'sw', 900, 600)); self.assertEqual(f.gesetzt, [])
        self.L.speichern('sw', 300, 3000); f = self._F(); self.assertFalse(self.L.anwenden(f, 'sw', 900, 600))
        self.L.speichern('sw', -1500, 20)                            # zweiter Bildschirm links: nur gueltig, wenn der virtuelle Bereich ihn einschliesst
        self.assertFalse(self.L.anwenden(self._F(), 'sw', 900, 600))
        self.assertTrue(self.L.anwenden(self._F(vroot=(-1920, 0, 3840, 1080)), 'sw', 900, 600))
        self.assertFalse(self.L.anwenden(self._F(), 'unbekannt', 900, 600))
    def test_merker_schreibt_erst_nach_ruhe_und_beim_beenden(self):
        t = [0.0]; f = self._F('1148x860+10+10'); mk = self.L.Merker(f, 'pult', lambda: t[0])
        self.assertFalse(mk.merken()); self.assertIsNone(self.L.laden('pult'))        # Startlage: nichts schreiben
        f.g = '1148x860+50+60'; self.assertFalse(mk.merken())                          # Lage geaendert, noch in Bewegung
        t[0] = 0.5; f.g = '1148x860+55+60'; self.assertFalse(mk.merken())              # Fenster wird noch gezogen
        t[0] = 1.2; self.assertFalse(mk.merken()); self.assertIsNone(self.L.laden('pult'))
        t[0] = 1.6; self.assertTrue(mk.merken()); self.assertEqual(self.L.laden('pult'), (55, 60))     # 1,1 s ruhig: geschrieben
        self.assertFalse(mk.merken())                                                  # unveraendert: kein erneutes Schreiben
        f.g = '1148x860+70+80'; self.assertTrue(mk.beenden()); self.assertEqual(self.L.laden('pult'), (70, 80))   # beim Schliessen sofort
    def test_sw_fenster_startet_an_der_gespeicherten_lage_und_merkt_sich_die_neue(self):
        from c8205_grafik import SwSenke
        from grafik_sw_fenster import SwFenster
        self.L.speichern('sw', 321, 123)
        m = FakeMaschine(); k0 = K0Warteschlange(m); pult = PultAttrappe()
        f = SwFenster(pult, SwSenke(), k0, m, bei_schliessen=pult._schliessen, tk=_fake_tk())
        self.assertEqual(f.w.geom, '+321+123')                                          # statt rechts unten (1920-900-10, 1080-600-70)
        f.beenden()                                                                      # ohne lesbare Lage (Ersatzfenster): kein Fehler, nichts geschrieben
        self.assertEqual(self.L.laden('sw'), (321, 123))


T_TXT = [None]


if __name__ == '__main__':
    unittest.main(verbosity=1)
