"""Tests des Python-Moduls c8205_trommel (vorher: python3 setup.py build_ext --inplace).
   python3 -m unittest -v test_c8205_trommel"""
import os, re, signal, subprocess, sys, tempfile, textwrap, time, unittest

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
try:
    import c8205_trommel as T
except ImportError as e:
    raise SystemExit('c8205_trommel nicht gebaut: "python3 setup.py build_ext --inplace" im Ordner python/ ausfuehren (' + str(e) + ')')

ZEILE = re.compile(r'^[0-7]{4}: [0-7]{11}\n$')


def muster(a): return (a * 0o123 + 0o45) & 0x1FFFFFFFF


def lege_trommel_an(pfad):
    with open(pfad, 'w', encoding='utf-8', newline='') as f:
        for a in range(4096): f.write('%04o: %011o\n' % (a, muster(a)))


def datei_ok(pfad):
    with open(pfad, encoding='utf-8', newline='') as f: zeilen = f.readlines()
    return len(zeilen) == 4096 and all(ZEILE.match(z) for z in zeilen)


class Grundfunktionen(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.pfad = os.path.join(self.tmp.name, 'trommel.txt'); lege_trommel_an(self.pfad)
        T.einschalten(self.pfad, 0)

    def tearDown(self):
        T.bahnsperre_setzen(0, 0, 0, 0, 0, 0); T.ausschalten(); self.tmp.cleanup()

    def test_lesen_und_wartezeit(self):
        for a in (0, 5, 0o1234, 0o7777):
            wert, wz = T.lesen_warten(a)
            self.assertEqual(wert, muster(a)); self.assertTrue(0 <= wz <= 31)

    def test_schreiben_und_ruecklesen(self):
        gesperrt, wz = T.schreiben_warten(0o1234, 0o12345670123)
        self.assertFalse(gesperrt); self.assertEqual(T.lesen_warten(0o1234)[0], 0o12345670123)
        T.schreiben_warten(0o1235, 2 ** 40 + 5)                      # auf 33 Bit begrenzt
        self.assertEqual(T.lesen(0o1235), (2 ** 40 + 5) & 0x1FFFFFFFF)
        T.ausschalten(); self.assertTrue(datei_ok(self.pfad))

    def test_bahnsperre(self):
        T.bahnsperre_setzen(1, 0, 0, 0, 0, 0)
        gesperrt, wz = T.schreiben_warten(5, 1)                       # Bahn 0 gesperrt
        self.assertTrue(gesperrt); self.assertEqual(T.lesen(5), muster(5)); self.assertTrue(0 <= wz <= 31)
        self.assertFalse(T.schreiben_warten(0o45, 1)[0])              # Bahn 1 offen

    def test_fehler(self):
        with self.assertRaises(T.TrommelFehler): T.lesen_warten(0o10000)
        self.assertTrue(issubclass(T.TrommelAbbruch, T.TrommelFehler))

    def test_abbrechen(self):
        T.warten_abbrechen()
        with self.assertRaises(T.TrommelAbbruch): T.lesen_warten(0o100)
        self.assertEqual(T.lesen_warten(0o100)[0], muster(0o100))     # Abbruch-Flag verbraucht

    def test_sektor_und_statistik(self):
        self.assertTrue(0 <= T.aktueller_sektor() <= 0o37)
        T.lesen_warten(7); s = T.statistik()
        self.assertEqual(set(s), {'ticks', 'aufwachen', 'nachgeholte_ticks', 'verspaetung_summe_ns', 'verspaetung_max_ns', 'zugriffe', 'wartezeit_summe_ticks'})
        self.assertGreaterEqual(s['zugriffe'], 1)

    def test_falsche_datei(self):
        T.ausschalten(); schlecht = os.path.join(self.tmp.name, 'alt.txt')
        with open(schlecht, 'w', newline='') as f:
            for a in range(4096): f.write('%04o %011o\n' % (a, 0))
        with self.assertRaises(T.TrommelFehler): T.einschalten(schlecht)

    def test_pfad_mit_umlaut(self):
        T.ausschalten(); ordner = os.path.join(self.tmp.name, 'Eingänge'); os.makedirs(ordner)
        p = os.path.join(ordner, 'trommel.txt'); lege_trommel_an(p)
        T.einschalten(p, 3); self.assertEqual(T.lesen_warten(9)[0], muster(9))


@unittest.skipIf(sys.platform.startswith('win'), 'SIGINT-Test nur unter POSIX (unter Windows anders zu senden)')
class StrgC(unittest.TestCase):
    def test_strg_c_beendet_auch_das_c_modul(self):
        with tempfile.TemporaryDirectory() as tmp:
            pfad = os.path.join(tmp, 'trommel.txt'); lege_trommel_an(pfad)
            skript = textwrap.dedent('''
                import sys, signal; sys.path.insert(0, %r)
                signal.signal(signal.SIGINT, signal.default_int_handler)    # unabhaengig vom Start (Hintergrundstart setzt SIGINT auf 'ignorieren')
                import c8205_trommel as T
                T.einschalten(%r, 0)
                rc = 0
                try:
                    print('BEREIT', flush=True)
                    while True:
                        T.schreiben_warten(0o1234, 0o77); T.lesen_warten(0o1234); T.lesen_warten(0o1235)
                except KeyboardInterrupt:
                    print('KI', flush=True); rc = 8
                finally:
                    T.ausschalten(); print('AUS', flush=True)
                sys.exit(rc)
            ''' % (HIER, pfad))
            p = subprocess.Popen([sys.executable, '-c', skript], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(p.stdout.readline().strip(), 'BEREIT')
            time.sleep(0.5); p.send_signal(signal.SIGINT)
            try: aus, err = p.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill(); self.fail('Prozess endet nach Strg+C nicht (haengt im C-Modul?)')
            self.assertEqual(p.returncode, 8, err); self.assertIn('KI', aus); self.assertIn('AUS', aus)
            self.assertNotIn('Traceback', err); self.assertTrue(datei_ok(pfad), 'Trommeldatei beschaedigt')


class Lader(unittest.TestCase):
    def test_nicht_ladbar_meldung_und_ende(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(HIER, 'trommel_lader.py'), encoding='utf-8') as f: quelle = f.read()
            with open(os.path.join(tmp, 'trommel_lader.py'), 'w', encoding='utf-8') as f: f.write(quelle)   # ohne das Modul daneben
            r = subprocess.run([sys.executable, '-c', 'import trommel_lader; trommel_lader.lade_trommelmodul()'], cwd=tmp,
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 16); self.assertIn('nicht ladbar', r.stdout); self.assertIn('Es startet kein Test', r.stdout)

    def test_ladbar(self):
        import trommel_lader
        self.assertIs(trommel_lader.lade_trommelmodul(), T)


class Schalterdatei(unittest.TestCase):
    """Bahnsperrenschalter: --BASP und Schalterdatei neben der Trommel (Entwurf 86/87)."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pfad = os.path.join(self.tmp.name, 'trommel.txt'); lege_trommel_an(self.pfad)
        self.basp = os.path.join(self.tmp.name, 'trommel.basp')

    def tearDown(self):
        T.bahnsperre_setzen(0, 0, 0, 0, 0, 0); T.ausschalten(); self.tmp.cleanup()

    def lies(self):
        with open(self.basp, 'rb') as f: return f.read()

    def test_ohne_datei_wird_000000_angelegt(self):
        self.assertFalse(os.path.exists(self.basp))
        self.assertEqual(T.einschalten(self.pfad, 0), '000000')
        self.assertEqual(self.lies(), b'000000\n')
        self.assertFalse(T.schreiben_warten(0o100, 5)[0])     # Bahn 2: offen

    def test_angabe_wird_uebernommen_und_gespeichert(self):
        self.assertEqual(T.einschalten(self.pfad, 0, basp='100000'), '100000')
        self.assertEqual(self.lies(), b'100000\n')
        self.assertTrue(T.schreiben_warten(0, 7)[0])          # Spur 0 gesperrt
        self.assertEqual(T.lesen_warten(0)[0], muster(0))      # unveraendert

    def test_ohne_angabe_aus_datei(self):
        T.einschalten(self.pfad, 0, basp='110000'); T.ausschalten()
        self.assertEqual(T.einschalten(self.pfad, 0), '110000')
        self.assertEqual(self.lies(), b'110000\n')

    def test_gleiche_angabe_wird_trotzdem_geschrieben(self):
        T.einschalten(self.pfad, 0, basp='100000'); T.ausschalten()
        os.utime(self.basp, (1, 1))
        T.einschalten(self.pfad, 0, basp='100000')
        self.assertGreater(os.path.getmtime(self.basp), 1000)

    def test_fehlerhafte_datei_wird_nicht_ueberschrieben(self):
        for inhalt in (b'10x000\n', b'1000000\n', b'100000', b'100000\r\n', b''):
            with open(self.basp, 'wb') as f: f.write(inhalt)
            with self.assertRaises(T.TrommelFehler): T.einschalten(self.pfad, 0)
            self.assertEqual(self.lies(), inhalt)
        # Trommel wurde dabei nicht eingeschaltet
        with self.assertRaises(T.TrommelFehler): T.lesen_warten(0)

    def test_ungueltige_angabe(self):
        for a in ('10000', '1000000', '10200a', ''):
            with self.assertRaises(T.TrommelFehler): T.einschalten(self.pfad, 0, basp=a)
        self.assertFalse(os.path.exists(self.basp))

    def test_dateiname_ohne_endung(self):
        p2 = os.path.join(self.tmp.name, 'meine.trommel'); lege_trommel_an(p2)
        T.einschalten(p2, 0)
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, 'meine.basp')))

    def test_pfad_mit_umlaut(self):
        d = os.path.join(self.tmp.name, 'Tr\u00f6mmel'); os.mkdir(d)
        p = os.path.join(d, 'trommel.txt'); lege_trommel_an(p)
        T.einschalten(p, 0, basp='000001')
        self.assertTrue(os.path.exists(os.path.join(d, 'trommel.basp')))

    def test_datei_nicht_schreibbar(self):
        os.mkdir(self.basp)                                    # Verzeichnis statt Datei: weder lesbar noch schreibbar
        with self.assertRaises(T.TrommelFehler): T.einschalten(self.pfad, 0)
        with self.assertRaises(T.TrommelFehler): T.einschalten(self.pfad, 0, basp='000000')


class Referenzzaehler(unittest.TestCase):
    """G4-005: Aufrufe, die None (oder True/False) liefern, duerfen deren Referenzzaehler nicht veraendern.
    Auslöser des Absturzes "none_dealloc: deallocating None" auf Python 3.11 (Modul mit 3.12-Headern gebaut, Py_RETURN_NONE ohne Zaehler).
    Ab Python 3.12 ist None unsterblich: der Test kann dort den Fehler nicht zeigen (er ist dann trivial gruen); auf 3.8 bis 3.11 faengt er ihn."""

    def test_none_zaehler_bleibt(self):
        h = T.ton_neu()
        T.ton_senke(h, 'speicher')
        vorher = sys.getrefcount(None)
        for _ in range(20000):
            T.ton_ausfall(h)                      # liefert None
            T.ton_tor(h, 1, 1)                    # liefert None
            T.ton_dauer_pegel(h, 'x', 0.5)        # liefert None
            T.ton_alles_aus(h)                    # liefert None
            T.warten_abbrechen()                  # liefert None
        T.ton_schliessen(h)
        nachher = sys.getrefcount(None)
        self.assertGreaterEqual(nachher, vorher - 2, f'Referenzzaehler von None gesunken: {vorher} -> {nachher}')

    def test_bool_zaehler_leckt_nicht(self):
        T.bahnsperre_setzen(0, 0, 0, 0, 0, 0)
        w = sys.getrefcount(True) + sys.getrefcount(False)
        for _ in range(20000):
            T.ton_klingt(T.ton_neu())
        self.assertLess(abs(sys.getrefcount(True) + sys.getrefcount(False) - w), 100)

    def test_ton_grundablauf(self):
        h = T.ton_neu()
        T.ton_senke(h, 'speicher')
        k = T.ton_klang(h, b'\x10\x00' * 441)
        self.assertEqual(T.ton_einzel(h, 1, k, 1.0, None), 0)
        T.ton_schritt(h, 3)
        self.assertEqual(len(T.ton_speicher(h)), 3 * 882)
        self.assertIsNone(T.ton_ausfall(h))
        T.ton_schliessen(h)


if __name__ == '__main__': unittest.main()
