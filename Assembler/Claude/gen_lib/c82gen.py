#!/usr/bin/env python3
"""c82gen.py -- Python als Makrosprache fuer C-8205-Assembler (nur fuer Claude).

Version: 0.01-006

Ein Generator (Python-Skript im Unterordner gen/ eines Programmordners) beschreibt das Programm Befehl fuer
Befehl mit den Idiomen dieser Bibliothek; die Bibliothek legt Zellen und Adressen fest, prueft die Speichergrenze
und schreibt den Assemblerquelltext (.asm) samt ;#PRUEFE-Block. Es wird nichts uebersetzt: jede Idiom-Methode
erzeugt genau die dokumentierte Befehlsfolge. Die erzeugte .asm bleibt massgeblich und lesbar.
Ziel (seit 0.01-003): die erzeugte .asm ist nicht laenger als ein von Hand nach den Programmierfestlegungen (Handbuch 5.8)
geschriebenes Programm, der Generator aber deutlich kuerzer als die .asm.

Aufruf eines Generators (vom Projektstamm): python3 -I Assembler/Claude/<programm>/gen/<n>_gen.py
(asm_und_test.sh ruft <ordner>/gen/<n>_gen.py selbst auf, wenn es existiert.)

Aufbau eines Generators:
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'gen_lib'))
    from c82gen import Prog
    P = Prog('titel', grenze=0o0400)          # grenze = hoechste erlaubte Zellenzahl
    P.lab('haupt')                             # Marke fuer die naechste Zeile
    P.laden('x')                               # 211 x   (Kommentar 'AC := x' entsteht selbst; eigener Kommentar als 2. Argument)
    P.var('x', 5, 'Eingabewert')               # Datenzelle (dw)
    P.schreibe(pfad, pruefe={'summe': wert})   # .asm schreiben, Sollwerte aus dem Python-Modell
Operanden: Symbolnamen (Zeichenketten), Zahlen (Adresse, oktal mit fuehrender 0 geschrieben) oder wie im Assembler
'#wert' (Konstante, Zahl mit fuehrender 0 = oktal, sonst dezimal) und '@name' (Adresse von name). In den Kurzidiomen
(setze, wenn_*) sind Zahlen Konstanten. Zellenaufbau: erst Code (in der Reihenfolge der Aufrufe), dann Daten.

Neu in 0.01-006 (30.10.2026): zt_anw waehlt mit Befehlswort 05100030 + t * 0100000 an (5100 030 = ZT0 ... 5400 030 = ZT3), vorher 05000030; sonst unveraendert.

Neu in 0.01-005 (Wunsch des Projektinhabers 30.10.2026, Tests mit Zusatztrommeln):
    makro(name, zellen=None, makrodatei=None, k=None)   Aufruf eines Makros ohne Parameter aus einer Makrodatei (Zeile 'NAME' im Code, Marke wie bei op: vorher lab());
                          die Zellenzahl des Makros gibt der Aufrufer an oder (zellen=None) die Bibliothek misst sie mit dem Assembler (makrodatei = Pfad der .macro-Datei,
                          absolut oder relativ zum Aktuellen Verzeichnis). Die Makrodatei selbst steht per pragma('#MACRODATEI1=<Pfad relativ zur .asm>') im Kopf.
    schreibe(..., ztpruefe=[(o, adresse, wert), ...])   Abschnitt 'ZT-Zellen-Pruefung:' im ;#PRUEFE-Block (Interpreter mit --C8205Z, Durchfuehrung_eines_Tests.md 3a.6):
                          o = Zusatztrommel 0 bis 3, adresse = ZT-Zelladresse (Spur * 040 + Sektor), wert = Sollwert aus dem Python-Modell; optional als 4. Element ein Kommentar.
                          Die Marke der Trommelvorlage setzt man mit pragma('#ZTROMMEL=LEER') (schreibt '; #ZTROMMEL=LEER', der Assembler erkennt sie wie ';#...').

Neu in 0.01-004 (gegenueber der ersten Fassung 0.01-003):
    schiebespur           Prog(..., schiebespur='w7640' | 'nullspur'); Vorgabe 'w7640' im Normalmodus (Festlegung 026), 'nullspur' bei archiv=True
                          (eigene Spur aus 32 Nullzellen, 612/616 wie 0.01-002; Begruendung beim Schiebe-Idiom unten). nullspur() hat nur dort Wirkung.
    Zusatztrommel         Anwahl 5k00 030 mit k = d + 1 = 1 bis 4 (5100 = ZT0 ... 5400 = ZT3; Interpreter ab 0.95-017); zt_lies/zt_schreibe(k=None).
    Vertraeglichkeit      der Generator des Archivprogramms (Schnittstelle 0.01-002, archiv=True) laeuft unveraendert.

Neu in 0.01-003 (Festlegungen aus Handbuch 5.8; Messungen in Assembler/Claude/gen_lib/gen_lib_messung.md):
    Kommentar optional    Jede Methode erzeugt ohne Kommentarargument einen sachlichen Standardkommentar (Dateiformat: Kommentar
                          in jeder Zeile); eigene Kommentare nur, wo sie etwas erklaeren.
    Kurzidiome            kopiere(von, nach), setze(nach, wert), wenn_gleich/_kleiner_gleich/_groesser_gleich(a, b, ziel),
                          wenn_negativ/_nichtnegativ(x, ziel), unterprogramm(name) als with-Block.
    Festlegung 026        schiebe_links/_rechts(n): W-Transport 646/642 auf der Arbeitsspur 7640, keine Nullspur (spart 63 Zellen).
                          Prog(..., schiebespur='nullspur') schiebt wie 0.01-002 mit 612/616 ueber eine eigene Nullspur im Programm; das ist
                          Vorgabe bei archiv=True, weil ein Lader (ZTL) die Spur 7640 beim Start loescht und danach mit Nullen rechnet; der
                          W-Transport fuellt sie (Abnahmetest ZTD: M-Kommando brach ab). 'w7640' im Archiv nur, wenn der Lader es vertraegt.
    Festlegung 010        Die Rueckkehrzelle eines Unterprogramms liegt am Ende des UP (letzter up_ende-Aufruf); kein eigener
                          Rueckkehrsprung, keine Datenzelle (spart eine Zelle je UP).
    Festlegung 003        Konstanten und Adressen als Literale '#wert' und '@name' (Assembler legt sie ab); Archivprogramme
                          (nur lueckenfreie .obj) behalten benannte Zellen.
    Festlegung 023        Ausrichtungsfuellung mit db (nicht dbn); nur Archivprogramme brauchen dbn.
    Luckenfuellung        Einzelzellen (var, arbeit, benannte Konstanten) fuellen Ausrichtungsluecken, bevor Fuellzellen entstehen.
    Festlegung 001        Kopfkommentar mit kleinster und groesster Startzelle und Ausrichtung entsteht selbst (nicht bei archiv).
    Festlegung 027        Felder und Tafeln stehen in begin/bend.
    Eingabetafel          ausserhalb von Archivprogrammen nur eine Tafel (Lage 0 modulo 0100) und feste 011-Befehle, kein eingabe_init-UP.
    pragma(zeile)         Zeile fuer den Testrahmen (z. B. '--sw-ausgabe <Ordner>', '--pruefe-sw-ausgabe <Datei>', '#SPEI-0001 a-b').

Aus 0.01-002 (ZTD, Dialogprogramm im ZT-Archiv):
    archiv=True      Programm fuer das ZT-Archiv: Zelle 0000 = Sprung zum Hauptprogramm, nur dbn (kein db: db erzeugt in der .obj
                     eine Adressmarke K1 = 2, ZTC weist sie ab; Archivprogramme muessen luecken-frei sein), Ausrichtung durch dbn-Fuellung
    ausrichten(mod, rest, k)   Fuellung bis Adresse = rest (mod mod); die Bibliothek rechnet die Adressen selbst
    text(s, k)       Textausgabe auf K2: Anwahl 030 04500, dtm, Zeilenschaltung; Zellenzahl wird vom Assembler gemessen
    anwahl(kanal, k) 030 04700 / 04600 / 04500 / 04400 (K0 bis K3)
    schiebe_links/schiebe_rechts(n, k)   Mehrfachverschiebung (Handbuch 4.2)
    ziffer_ausgeben(var, k), zahl_ausgeben(var, stellen, k)   Oktalziffern im Kleinbuchstabenzustand (Handbuch 5.5)
    eingabetafel(name, belegung), eingabe_init(name, k), zeichen_lesen(name, k)   Eingabebefehl 011 mit 64-Zellen-Tafel (Archivmodus: zwei
                     gleiche Tafeln, die nach der Ladeadresse (Vielfaches von 040, nicht von 0100) die passende waehlen)
    puffer(name), zt_lies(t, spur, k), zt_schreibe(t, spur, k)   Zusatztrommel-Spur (Anwahl 5k00 030, k = d + 1 = 1 bis 4, ab Interpreter 0.95-017; 601/661) ueber eine Pufferspur
"""
import os
import sys
from contextlib import contextmanager

MASKE33 = (1 << 33) - 1
AE = 0o1000          # eine Adresseneinheit im Wort (Handbuch Abschnitt 3)
ARBEITSSPUR = 0o7640  # Festlegung 026: Spur fuer W-Transport-Verschiebungen (kein Wert darf dort stehen bleiben, Festlegung 025)
ZEIT_OPS = ('db', 'dw', 'dbn', 'da', 'dz', 'dtm', 'dto', 'dt', 'PAD', 'begin', 'bend')


def wort(n):
    """Wert als 11 Oktalziffern, negativ im Zweierkomplement (33 Bit)."""
    return '%011o' % (n & MASKE33)


def _zahl(v):
    if isinstance(v, int):
        return ('-0%o' % -v) if v < 0 else ('0%o' % v if v else '0')
    return str(v)


def _wert(text):
    """Zahl in Assemblerschreibweise (fuehrende 0 = oktal, sonst dezimal, optional Minus) -> int."""
    t = text.strip()
    neg = t.startswith('-')
    t = t.lstrip('+-')
    w = int(t, 8) if (len(t) > 1 and t.startswith('0')) else int(t)
    return -w if neg else w


class Prog:
    def __init__(self, titel, grenze=0o7600, sprung_zum_start=False, archiv=False, literale=None,
                 start_min=0o40, start_max=0o7600, kopf_auto=None, schiebespur=None):
        self.titel = titel
        # Schieben: 'w7640' = W-Transport auf der Arbeitsspur 7640 (Festlegung 026, keine Zellen im Programm); 'nullspur' = eigene Spur aus 32 Nullzellen
        # und W-Addition 612/616 (Archivprogramme: ZTL loescht die Spur 7640 beim Start und rechnet danach mit Nullen, der W-Transport wuerde sie fuellen).
        self.schiebespur = schiebespur or ('nullspur' if archiv else 'w7640')
        assert self.schiebespur in ('w7640', 'nullspur'), 'schiebespur: w7640 oder nullspur'
        self.grenze = grenze
        self.kopf = []                              # zusaetzliche Kopfkommentarzeilen
        self.optimiere = True                       # Regeln 019 (kein Laden nach Speichern) und 021 (Sprung auf Sprung)
        self.eingespart = 0
        self.archiv = archiv                        # True: Archivprogramm (nur dbn, Zelle 0000 = Sprung)
        self.literale = (not archiv) if literale is None else literale   # Festlegung 003: '#wert' und '@name' statt benannter Zellen
        self.kopf_auto = (not archiv) if kopf_auto is None else kopf_auto
        self.start_min, self.start_max = start_min, start_max
        self._start_sprung = sprung_zum_start or archiv   # True: Zelle 0000 = "000 haupt" wie im Handbuch-Geruest
        self.code = []                      # Eintraege (label, code, operand, kommentar, zellen)
        self.daten = []
        self._lab = None
        self._konst = {}
        self._adrz = {}
        self._halt = None
        self._zaehler = 0
        self._namen = set()
        self._ups = {}
        self._exits = {}                    # UP -> Indizes seiner Rueckkehrspruenge in self.code
        self._spaeter = []                  # Bausteine, die erst beim Schreiben entstehen (Unterprogramme, Tafeln)
        self._hat = set()
        self._tafeln = {}
        self._text_cache = {}
        self._lits = set()                  # Literale ('#..', '@..'), vom Assembler hinter end abgelegt (je Text eine Zelle)
        self._bew = set()                   # Namen verlegbarer Einzelzellen (fuellen Ausrichtungsluecken)
        self._pragmas = []
        self._fertig_ok = False

    def _leer(self):
        """Reservierung einer Zelle: db (ohne Inhalt) oder im Archiv dbn (mit 0; db haette eine Adressmarke in der .obj)."""
        return 'dbn' if self.archiv else 'db'

    # ---- Operanden und Kommentare --------------------------------------------------------------------
    def _opd(self, x):
        """'#wert' -> Konstante, '@name' -> Adresse von name; alles andere unveraendert."""
        if isinstance(x, str):
            if x.startswith('#'):
                return self.konst(_wert(x[1:]))
            if x.startswith('@'):
                return self.adresse_von(x[1:])
        return x

    def _wertop(self, x):
        """Operand eines Kurzidioms: Zahl = Konstante, Zeichenkette = Symbol bzw. '#..'/'@..'."""
        if isinstance(x, int):
            return self.konst(x)
        return self._opd(x)

    @staticmethod
    def _anz(x):
        """Operand fuer Standardkommentare."""
        s = str(x)
        if s.startswith('#'):
            return s[1:]
        if s.startswith('@'):
            return 'Adresse ' + s[1:]
        return s

    @staticmethod
    def _k(k, standard):
        return k if k else standard

    def neu(self, stamm):
        """Eindeutige Marke (stamm_1, stamm_2, ...)."""
        self._zaehler += 1
        return '%s_%d' % (stamm, self._zaehler)

    def pragma(self, zeile):
        """Zeile fuer den Testrahmen (Kopfkommentar, z. B. '--sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/x')."""
        self._pragmas.append(zeile)

    # ---- Grundbausteine -------------------------------------------------------------------------
    def lab(self, name):
        """Marke fuer die naechste Codezeile."""
        assert self._lab is None, 'zwei Marken hintereinander: %s, %s' % (self._lab, name)
        self._def(name)
        self._lab = name

    def _def(self, name):
        assert name not in self._namen, 'Symbol doppelt: ' + name
        self._namen.add(name)

    def op(self, code, operand, kommentar=None, zellen=1):
        assert code in ZEIT_OPS or (len(code) == 3 and all(c in '01234567' for c in code)), 'Operationscode %r' % code
        if len(code) == 3 and code not in ZEIT_OPS:
            operand = self._opd(operand)
        if not kommentar:
            kommentar = '%s %s' % (code, self._anz(operand))
        self.code.append((self._lab, code, _zahl(operand), kommentar, zellen))
        self._lab = None

    def makro(self, name, zellen=None, makrodatei=None, k=None):
        """Aufruf eines parameterlosen Makros (Zeile 'NAME'). Die Zellenzahl braucht die Bibliothek fuer die Adressen: angegeben oder vom Assembler gemessen."""
        if zellen is None:
            assert makrodatei, 'makro(%s): zellen oder makrodatei angeben' % name
            zellen = self._makro_zellen(name, makrodatei)
        self.code.append((self._lab, name, '', k or ('Makro ' + name), zellen))
        self._lab = None

    def _makro_zellen(self, name, makrodatei):
        """Zellenzahl eines Makros, vom Assembler gemessen (wie _text_zellen)."""
        import subprocess, tempfile, shutil
        stamm = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))   # .../Assembler
        d = tempfile.mkdtemp(prefix='c82gen_')
        try:
            shutil.copy(makrodatei, os.path.join(d, 'm.macro'))
            with open(os.path.join(d, 'm.asm'), 'w', encoding='utf-8', newline='\n') as f:
                f.write(';#MACRODATEI1=m.macro\n                start\n                %s\nende:           164     0\n                end\n' % name)
            r = subprocess.run(['bash', './c82ass.sh', '-p', d, '-s', 'm.asm', '--no-color'], cwd=stamm, capture_output=True, text=True)
            assert r.returncode == 0, 'Assembler (Makromessung) rc %d: %s' % (r.returncode, r.stdout[-300:])
            n = None
            for z in open(os.path.join(d, 'm.sym'), encoding='utf-8'):
                if z.startswith('ende,'):
                    n = int(z.strip().split(',')[1], 8)
            assert n is not None
        finally:
            shutil.rmtree(d, ignore_errors=True)
        return n

    def _datum(self, name, code, operand, kommentar, zellen=1, bewegbar=False):
        assert kommentar, 'Kommentar ist Pflicht'
        if name:
            self._def(name)
            if bewegbar:
                self._bew.add(name)
        self.daten.append((name, code, _zahl(operand), kommentar, zellen))

    # ---- Daten ----------------------------------------------------------------------------------
    def var(self, name, wert, kommentar):
        """Datenzelle mit Anfangswert (dw)."""
        self._datum(name, 'dw', wert, kommentar, bewegbar=True)
        return name

    def feld(self, name, werte, kommentar):
        """Feld aus aufeinanderfolgenden Zellen (je ein dw), in begin/bend (Festlegung 027)."""
        if len(werte) > 1:
            self.daten.append((None, 'begin', '', 'Feld ' + name + ' (zusammengehoerige Worte)', 0))
        for i, w in enumerate(werte):
            self._datum(name if i == 0 else None, 'dw', w, '%s[%d] = %d' % (kommentar, i, w))
        if len(werte) > 1:
            self.daten.append((None, 'bend', '', 'Ende Feld ' + name, 0))
        return name

    def arbeit(self, name, kommentar):
        """Arbeitszelle ohne Anfangswert (db 1; im .test ohne Wert, vor dem Lesen setzen!)."""
        self._datum(name, self._leer(), 1, kommentar, bewegbar=True)
        return name

    def konst(self, wert, kommentar=None):
        """Konstante: Literal '#wert' (Festlegung 003), im Archivprogramm benannte Zelle k_<oktal>; je Wert einmal."""
        if self.literale:
            t = '#' + _zahl(wert)
            self._lits.add(t)
            return t
        if wert not in self._konst:
            n = 'k_%o' % wert if wert >= 0 else 'k_m%o' % -wert
            self._konst[wert] = n
            self._datum(n, 'dw', wert, kommentar or 'Konstante %d' % wert, bewegbar=True)
        return self._konst[wert]

    def ae(self, n):
        """Konstante n Adresseneinheiten (n * 01000)."""
        if self.literale:
            return self.konst(n * AE)
        w = n * AE
        if w not in self._konst:
            self._konst[w] = 'ae_%d' % n
            self._datum('ae_%d' % n, 'dw', w, '%d Adresseneinheit(en)' % n, bewegbar=True)
        return self._konst[w]

    def adresse_von(self, feld):
        """Adresse eines Feldes: Literal '@feld' (Festlegung 003), im Archivprogramm Zelle a_<feld> (da); je Feld einmal."""
        if self.literale:
            t = '@' + feld
            self._lits.add(t)
            return t
        if feld not in self._adrz:
            n = 'a_' + feld
            self._adrz[feld] = n
            self._datum(n, 'da', feld, 'Anfangsadresse von ' + feld, bewegbar=True)
        return self._adrz[feld]

    # ---- Einzelbefehle (Handbuch Abschnitt 4.1) --------------------------------------------------
    def laden(self, x, k=None):
        """AC := x. Regel 019: steht davor 240 x oder 241 x (und keine Marke dazwischen), hat der AC den Wert schon: kein Befehl."""
        x = self._opd(x)
        if self.optimiere and self._lab is None and self.code and self.code[-1][1] in ('240', '241') and self.code[-1][2] == _zahl(x):
            self.eingespart += 1
            return
        self.op('211', x, self._k(k, 'AC := ' + self._anz(x)))

    def addiere(self, x, k=None):
        self.op('210', x, self._k(k, 'AC := AC + ' + self._anz(self._opd(x))))

    def subtrahiere(self, x, k=None):
        self.op('220', x, self._k(k, 'AC := AC - ' + self._anz(self._opd(x))))

    def speichere(self, x, k=None):
        self.op('240', x, self._k(k, '%s := AC' % self._anz(x)))

    def nullen(self, x, k=None):
        self.op('241', x, self._k(k, '%s := 0, AC := 0' % self._anz(x)))

    def vergleiche(self, x, k=None):
        """330: setzt V1/V2, keine Operation."""
        self.op('330', x, self._k(k, 'AC mit %s vergleichen' % self._anz(self._opd(x))))

    def sprung(self, z, k=None):
        self.op('000', z, self._k(k, 'weiter bei ' + str(z)))

    def sprung_gleich(self, z, k=None):
        self.op('170', z, self._k(k, 'gleich: weiter bei ' + str(z)))             # nach 330: AC = a

    def sprung_kleiner_gleich(self, z, k=None):
        self.op('140', z, self._k(k, 'kleiner oder gleich: weiter bei ' + str(z)))   # nach 330: AC <= a

    def sprung_groesser_gleich(self, z, k=None):
        self.op('150', z, self._k(k, 'groesser oder gleich: weiter bei ' + str(z)))  # nach 330: AC >= a

    def sprung_negativ(self, z, k=None):
        self.op('040', z, self._k(k, 'AC < 0: weiter bei ' + str(z)))

    def sprung_nichtnegativ(self, z, k=None):
        self.op('050', z, self._k(k, 'AC >= 0: weiter bei ' + str(z)))

    def diag(self, nr, k='Diagnoseausgabe (nur im Test)'):
        self.op('164', '%04o' % nr if isinstance(nr, int) else nr, k)

    def halt(self, k='Halt'):
        """020; merkt die Adresse: BZ steht danach auf Haltadresse + 1."""
        self._halt = (len(self.code), self._lab)
        self.op('020', 0, k)

    # ---- Kurzidiome (0.01-003) ---------------------------------------------------------------------
    def kopiere(self, von, nach, k=None):
        """nach := von (211 + 240; das Laden entfaellt, wenn der AC den Wert schon hat)."""
        self.laden(von, k)
        self.speichere(nach, k)

    def setze(self, nach, wert, k=None):
        """nach := wert (Zahl = Konstante); Wert 0 mit 241 (eine Zelle)."""
        if wert == 0 or wert == '#0':
            self.nullen(nach, k)
        else:
            self.laden(self._wertop(wert), k)
            self.speichere(nach, k)

    def wenn_gleich(self, a, b, ziel, k=None):
        """a = b: weiter bei ziel (211 a, 330 b, 170 ziel)."""
        self.laden(a, k)
        self.vergleiche(self._wertop(b), k)
        self.sprung_gleich(ziel, k)

    def wenn_kleiner_gleich(self, a, b, ziel, k=None):
        self.laden(a, k)
        self.vergleiche(self._wertop(b), k)
        self.sprung_kleiner_gleich(ziel, k)

    def wenn_groesser_gleich(self, a, b, ziel, k=None):
        self.laden(a, k)
        self.vergleiche(self._wertop(b), k)
        self.sprung_groesser_gleich(ziel, k)

    def wenn_negativ(self, x, ziel, k=None):
        self.laden(x, k)
        self.sprung_negativ(ziel, k)

    def wenn_nichtnegativ(self, x, ziel, k=None):
        self.laden(x, k)
        self.sprung_nichtnegativ(ziel, k)

    # ---- Idiome -----------------------------------------------------------------------------------
    def erhoehe(self, var, schritt, k=None):
        """var := var + schritt (schritt = Konstante '#..', P.ae(n) oder Name)."""
        schritt = self._wertop(schritt)
        k0 = (k + ': ') if k else ''
        self.laden(var, k0 + 'AC := ' + var)
        self.addiere(schritt, k0 + 'AC := AC + ' + self._anz(schritt))
        self.speichere(var, k0 + var + ' := AC')

    def feld_lesen(self, feld, idx, k=None):
        """AC := feld[idx]; idx in Adresseneinheiten (Handbuch 5.4, R-Lesebefehl 251)."""
        k0 = (k + ': ') if k else ''
        self.laden(idx, k0 + 'AC := Index ' + str(idx))
        self.addiere(self.adresse_von(feld), k0 + 'AC := Index + Anfangsadresse ' + feld)
        self.op('251', 0, k0 + 'AC := ' + feld + '[Index] (R-Lesebefehl)')

    def feld_schreiben(self, feld, idx, wert, k=None):
        """feld[idx] := wert (Befehl 240 zur Laufzeit bauen und ausfuehren, Handbuch 5.4)."""
        k0 = (k + ': ') if k else ''
        z = self.neu('fs')
        self.laden(idx, k0 + 'AC := Index ' + str(idx))
        self.addiere(self.adresse_von(feld), k0 + 'AC := Index + Anfangsadresse ' + feld)
        self.addiere(self.konst(0o240), k0 + 'AC := Befehl 240 ' + feld + '[Index]')
        self.speichere(z, k0 + 'Befehl auf Zelle ' + z + ' ablegen')
        self.laden(wert, k0 + 'AC := ' + str(wert))
        self.lab(z)
        self.op(self._leer(), 1, k0 + 'zur Laufzeit 240 ' + feld + '[Index]')
        # db/dbn steht im Code: eine Zelle ohne Inhalt, die zur Laufzeit den Befehl erhaelt

    def up_beginn(self, name, k=None):
        """Unterprogramm: Marke, dann Rueckkehrwort (AC nach 025) in die Rueckkehrzelle rueck_<name> sichern.
        Die Rueckkehrzelle liegt am UP-Ende (Festlegung 010): der letzte up_ende-Aufruf wird zu dieser Zelle,
        die ohnehin sequentiell durchlaufen wird; die uebrigen Ausgaenge springen auf sie."""
        rn = 'rueck_' + name
        self._ups[name] = rn
        self._exits.setdefault(name, [])
        self.lab(name)
        self.speichere(rn, 'Rueckkehrwort sichern' + ((': ' + k) if k else ''))
        self._def(rn)

    def up_ende(self, name, k=None):
        """Ausgang des Unterprogramms (der letzte Aufruf je UP wird zur Rueckkehrzelle, siehe up_beginn)."""
        self._exits[name].append(len(self.code))
        self.sprung('rueck_' + name, (k or 'Rueckkehr') + ' aus ' + name)

    @contextmanager
    def unterprogramm(self, name, k=None):
        """with P.unterprogramm('name'): ... -- up_beginn und am Ende up_ende (entfaellt, wenn der Rumpf schon mit up_ende endet)."""
        self.up_beginn(name, k)
        yield
        if not (self.code and self._exits[name] and self._exits[name][-1] == len(self.code) - 1):
            self.up_ende(name)

    def aufruf(self, name, k=None):
        self.op('025', name, (k + ': ' if k else '') + 'Aufruf ' + name)

    def absolut(self, name, adresse, k):
        """Symbol mit fester Adresse (abs): belegt keine Zelle, z. B. Zellen des BIS (07626)."""
        self._datum(name, 'abs', '0%o' % adresse, k, zellen=0)

    # ---- Ausrichtung, Text, Kanal ---------------------------------------------------------------------
    def ausrichten(self, mod, rest, k):
        """Daten: Fuellung bis Adresse = rest (mod mod), relativ zum Programmanfang. Einzelzellen (var, arbeit, benannte Konstanten)
        fuellen die Luecke zuerst; der Rest wird db (Archivprogramme: dbn)."""
        self.daten.append((None, 'PAD', (mod, rest), k, 0))

    def _hole(self, name, bauer):
        """bauer() einmal beim Schreiben aufrufen (Unterprogramme und Tafeln, die erst am Ende entstehen)."""
        if name not in self._hat:
            self._hat.add(name)
            self._spaeter.append(bauer)

    def anwahl(self, kanal, k=None):
        """Kanalanwahl 030: K0 Tastatur 04700, K1 Leser 1 04600, K2 Schreibwerk 04500, K3 04400."""
        self.op('030', '0%o' % {0: 0o4700, 1: 0o4600, 2: 0o4500, 3: 0o4400}[kanal],
                (k + ': ' if k else '') + 'Kanal K%d anwaehlen' % kanal)

    def _text_zellen(self, t):
        """Zellenzahl von dtm <t>, vom Assembler gemessen (Umschaltzeichen je nach Text)."""
        if t in self._text_cache:
            return self._text_cache[t]
        import subprocess, tempfile
        stamm = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))   # .../Assembler
        d = tempfile.mkdtemp(prefix='c82gen_')
        try:
            with open(os.path.join(d, 'm.asm'), 'w', encoding='utf-8', newline='\n') as f:
                f.write('                start\n                dtm     %s\nende:           164     0\n                end\n' % self._roh(t))
            r = subprocess.run(['bash', './c82ass.sh', '-p', d, '-s', 'm.asm', '--no-color'], cwd=stamm, capture_output=True, text=True)
            assert r.returncode == 0, 'Assembler (Textmessung) rc %d: %s' % (r.returncode, r.stdout[-300:])
            n = None
            for z in open(os.path.join(d, 'm.sym'), encoding='utf-8'):
                if z.startswith('ende,'):
                    n = int(z.strip().split(',')[1], 8)
            assert n is not None
        finally:
            import shutil
            shutil.rmtree(d, ignore_errors=True)
        self._text_cache[t] = n
        return n

    @staticmethod
    def _roh(t):
        assert '\\' not in t, 'Text mit Gegenschraegstrich nicht vorgesehen'
        if t != t.strip() or ';' in t or t.startswith('#'):
            return '\\' + t + '\\'
        return t

    def text(self, t, k=None, zeile=True, kanal=True):
        """Text auf dem Schreibwerk: Anwahl K2, dtm (Umschaltzeichen selbst), Zeilenschaltung. zeile=False: ohne Zeilenschaltung."""
        if kanal:
            self.anwahl(2, k)
        self.op('dtm', self._roh(t), (k + ': ' if k else '') + 'Text ' + repr(t), zellen=self._text_zellen(t))
        if zeile:
            self.op('dz', '$wrzl', (k + ': ' if k else '') + 'Zeilenschaltung')

    def zeichen(self, dz, k=None):
        """Einzelzeichen ($zr, $wrzl, $inkb, $ingb ...): dz."""
        self.op('dz', dz, k or ('Zeichen ' + dz))

    # ---- Schieben (Festlegung 026) -----------------------------------------------------------------
    @staticmethod
    def _sektor(n):
        """Sektor (oktal), ab dem die Wiederholung n Zellen bis zum Spurende zaehlt: Position p = 32 - n, Sektor = 13 p mod 32 (HT-Folge 00 15 32 07 ...)."""
        assert 1 <= n <= 32
        return (13 * (32 - n)) % 32

    def _schiebe_op(self, n):
        if self.schiebespur == 'w7640':
            return '0%o' % (ARBEITSSPUR + self._sektor(n))
        s = self._sektor(n)
        return 'nz' if s == 0 else 'nz+0%o' % s

    def nullspur(self):
        """Spur aus 32 Nullzellen (nz) auf Spurgrenze fuer 612/616; nur bei schiebespur='nullspur', sonst ohne Wirkung."""
        if self.schiebespur != 'nullspur':
            return

        def bau():
            self.ausrichten(32, 0, 'Nullspur auf Spurgrenze')
            self._datum('nz', 'dbn', 32, 'Nullspur nz: 32 Zellen 0 (Operanden der Schiebebefehle 612 und 616)', zellen=32)
        self._hole('nz', bau)

    def schiebe_links(self, n, k=None, zyklisch=True):
        """AC um n Bit nach links: w7640 646 (zyklisch) bzw. 644, Operand 7640 + Sektor (Festlegung 026); nullspur 616 bzw. 614 ueber nz."""
        self.nullspur()
        code = ('646' if zyklisch else '644') if self.schiebespur == 'w7640' else ('616' if zyklisch else '614')
        self.op(code, self._schiebe_op(n), (k + ': ' if k else '') + 'AC um %d Bit %slinks' % (n, 'zyklisch ' if zyklisch else ''))

    def schiebe_rechts(self, n, k=None):
        """AC um n Bit nach rechts: w7640 642 (W-Transport auf 7640), nullspur 612 ueber nz."""
        self.nullspur()
        self.op('642' if self.schiebespur == 'w7640' else '612', self._schiebe_op(n),
                (k + ': ' if k else '') + 'AC um %d Bit nach rechts' % n)

    # ---- Ziffernausgabe (Kleinbuchstabenzustand, Handbuch 5.5) -----------------------------------------
    def _zelle(self, name, kom):
        if name not in self._namen:
            self.arbeit(name, kom)
        return name

    def _ziffer_up(self):
        self._zelle('pz_wert', 'auszugebende Ziffer')
        tab = 'pz_tab'
        self.up_beginn('prt_ziff', 'Ziffer ausgeben')
        self.laden('pz_wert', 'AC := Ziffer')
        self.schiebe_links(9, 'mal 01000 (Adresseneinheiten)')
        self.addiere(self.adresse_von(tab), 'plus Anfang der Ausgabebefehle')
        self.op('251', 0, 'AC := Ausgabebefehl der Ziffer (R-Lesebefehl)')
        self.speichere('pz_x', 'Befehl ablegen')
        self.lab('pz_x')
        self.op(self._leer(), 1, 'hier steht der Ausgabebefehl 030 xxxx')
        self.up_ende('prt_ziff')
        for i in range(8):
            self._datum(tab if i == 0 else None, 'dto', str(i), 'Ausgabebefehl Ziffer %d' % i)

    def ziffer_ausgeben(self, var, k=None):
        """Oktalziffer 0 bis 7 aus var ausgeben (Zustand KB und Kanal K2 muessen gesetzt sein: dz $inkb, anwahl(2))."""
        k0 = (k + ': ') if k else ''
        self._hole('prt_ziff', self._ziffer_up)
        self.laden(var, k0 + 'AC := Ziffer')
        self.speichere(self._zelle('pz_wert', 'auszugebende Ziffer'), k0 + 'Parameter pz_wert')
        self.aufruf('prt_ziff', k)

    def zahl_ausgeben(self, var, stellen, k=None):
        """Zahl aus var mit 'stellen' Oktalziffern (fuehrende Nullen) ausgeben; setzt selbst K2 und den Zustand KB."""
        name = 'prt_okt%d' % stellen
        k0 = (k + ': ') if k else ''

        def bau():
            po = self._zelle('po_wert', 'auszugebende Zahl')
            self.up_beginn(name, 'Zahl mit %d Oktalziffern ausgeben' % stellen)
            for i in range(stellen):
                sh = 3 * (stellen - 1 - i)
                self.laden(po, 'AC := Zahl')
                if sh:
                    self.schiebe_rechts(sh, 'Ziffer %d nach unten' % (i + 1))
                self.op('200', self.konst(7), 'Ziffer %d ausblenden (Maske 7)' % (i + 1))
                self.speichere('pz_wert', 'Ziffer %d' % (i + 1))
                self.aufruf('prt_ziff', 'Ziffer %d' % (i + 1))
            self.up_ende(name)
        self._hole('prt_ziff', self._ziffer_up)
        self._hole(name, bau)
        self.laden(var, k0 + 'AC := Zahl')
        self.speichere(self._zelle('po_wert', 'auszugebende Zahl'), k0 + 'Parameter po_wert')
        self.anwahl(2, k)
        self.zeichen('$inkb', k0 + 'Kleinbuchstabenzustand fuer Ziffern')
        self.aufruf(name, k)

    # ---- Eingabe ueber Tafel (Handbuch 5.6) -------------------------------------------------------------
    def eingabetafel(self, name, belegung, standard=0o77, namen=None, k='Eingabetafel'):
        """64-Zellen-Tafel fuer den Eingabebefehl 011 (Zelle = Eingabeadresse des Zeichens).
        belegung: Code 0..63 -> int (Wert, kommt in den AC) oder str (Sprungmarke, Zelle ist dann 000 <marke>); sonst 'standard'.
        Der Eingabebefehl verodert die Eingabeadresse mit dem Adressteil; die Tafel muss daher auf Vielfachem von 0100 liegen
        (der Kopfkommentar nennt die Ausrichtung). Ausserhalb von Archivprogrammen eine Tafel mit der Marke 'name'; zeichen_lesen
        erzeugt feste Befehle 011 name.
        Archivprogramme werden auf Vielfache von 040 geladen (ZTL), nicht von 0100: die Bibliothek legt deshalb zwei gleiche Tafeln
        an (Lage 0 und Lage 040 modulo 0100); eingabe_init waehlt zur Laufzeit die passende (Marken name_a und name_b)."""
        assert name not in self._tafeln, 'Tafel doppelt: ' + name
        self._tafeln[name] = {'sites': []}
        namen = namen or {}
        lagen = (('a', 0), ('b', 0o40)) if self.archiv else (('', 0),)
        for lage, rest in lagen:
            self.ausrichten(0o100, rest, 'Eingabetafel %s%s' % (name, (' Lage ' + lage.upper()) if lage else ''))
            self.daten.append((None, 'begin', '', 'Eingabetafel %s' % name, 0))
            for c in range(64):
                v = belegung.get(c, standard)
                bez = '%02o %s' % (c, namen.get(c, ''))
                lab = (('%s_%s' % (name, lage)) if lage else name) if c == 0 else None
                if isinstance(v, str):
                    self._datum(lab, '000', v, bez + ': Sprung')
                else:
                    self._datum(lab, 'dw', v, bez + ': Wert')
            self.daten.append((None, 'bend', '', 'Ende Eingabetafel %s' % name, 0))

    def zeichen_lesen(self, name, k=None):
        """Ein Zeichen von der Tastatur/vom Leser lesen (Eingabebefehl 011 mit Tafel name): AC := Tafelwert oder Sprung.
        Ausserhalb von Archivprogrammen ein fester Befehl 011 name (Kanal vorher anwaehlen); im Archivprogramm eine Zelle, die von
        eingabe_init mit dem Befehl 011 <Tafel> belegt wird."""
        k = k or ('Zeichen lesen (Tafel %s)' % name)
        if not self.archiv:
            self.op('011', name, k)
            return
        if self._lab is not None:          # vorher gesetzte Marke gehoert zur Eingabestelle selbst (Sprungziel einer Leseschleife)
            z = self._lab
        else:
            z = self.neu('ein')
            self.lab(z)
        self.op(self._leer(), 1, k + ': zur Laufzeit 011 <Tafel %s>' % name)
        self._tafeln[name]['sites'].append(z)

    def eingabe_init(self, name, k=None):
        """Archivprogramm: Tafel waehlen und alle Eingabestellen dieser Tafel mit dem Befehl 011 belegen (einmal vor dem ersten Lesen).
        Sonst ohne Wirkung (feste Befehle)."""
        if not self.archiv:
            return
        up = 'eing_init_' + name

        def bau():
            t = self._tafeln[name]
            a_a, a_b = self.adresse_von(name + '_a'), self.adresse_von(name + '_b')
            k11 = self.konst(0o11)
            wa, sp = self.neu('wa'), self.neu('sp')
            self.up_beginn(up, 'Eingabetafel ' + name + ' waehlen')
            self.laden(a_a, 'AC := Adresse Tafel A')
            self.op('200', self.konst(0o40000), 'Adressbit 040 von Tafel A (Ladeadresse ist Vielfaches von 040)')
            self.vergleiche(self.konst(0), 'Bit 0 ?')
            self.sprung_gleich(wa, 'ja: Tafel A liegt auf Vielfachem von 0100 (Ladeadresse ist Vielfaches von 0100)')
            self.laden(a_b, 'nein: AC := Adresse Tafel B')
            self.addiere(k11, 'plus Operationscode 011')
            self.sprung(sp, 'weiter')
            self.lab(wa)
            self.laden(a_a, 'AC := Adresse Tafel A')
            self.addiere(k11, 'plus Operationscode 011')
            first = True
            for z in t['sites']:
                if first:
                    self.lab(sp)
                    first = False
                self.speichere(z, 'Eingabebefehl auf Stelle ' + z)
            assert not first, 'Tafel ohne Eingabestelle: ' + name
            self.up_ende(up)
        self._hole(up, bau)
        self.aufruf(up, k or ('Eingabetafel ' + name + ' waehlen'))

    # ---- Zusatztrommeln (Handbuch 4.2) -----------------------------------------
    def puffer(self, name, k='Pufferspur'):
        """32 Zellen auf Spurgrenze (fuer 601/661 und Gruppenbefehle)."""
        self.ausrichten(32, 0, k + ' ' + name + ' auf Spurgrenze')
        self._datum(name, 'dbn', 32, k + ' ' + name + ': 32 Zellen', zellen=32)

    def _zt_up(self):
        for n, kom in (('zt_t', 'Trommel 0 bis 3 (ZT0 bis ZT3)'), ('zc_spur', 'Spur fuer 601/661'), ('zc_op', 'Operationscode 0601/0661'), ('zc_adr', 'Adresse der Pufferspur')):
            self._zelle(n, kom)
        self.up_beginn('zt_anw', 'Zusatztrommel zt_t anwaehlen (5k00 030, k = t + 1; 5100 = ZT0 bis 5400 = ZT3)')
        self.laden('zt_t', 'AC := t')
        self.schiebe_links(15, 'um 15 Bit nach links')
        self.addiere(self.konst(0o5100030, 'Befehl 5100 030 (Anwahl ZT0)'), 'plus Befehl 5100 030')
        self.speichere('zw_x', 'Befehl ablegen')
        self.lab('zw_x')
        self.op(self._leer(), 1, 'hier steht 5k00 030')
        self.up_ende('zt_anw')
        self.up_beginn('zt_ausf', 'Befehl zzz0 bbbb 601/661 aus zc_spur, zc_adr und zc_op bilden und ausfuehren')
        self.laden('zc_spur', 'AC := Spur')
        self.schiebe_links(26, 'um 26 Bit nach links (zzz0)')
        self.addiere('zc_adr', 'plus Adresse der Pufferspur')
        self.addiere('zc_op', 'plus Operationscode')
        self.speichere('za_x', 'Befehl ablegen')
        self.lab('za_x')
        self.op(self._leer(), 1, 'hier steht der ZT-Befehl')
        self.up_ende('zt_ausf')

    def _zt(self, op, t, spur, puf, k, kom):
        k = k or ('ZT ' + kom)
        self._hole('zt', self._zt_up)
        self._zelle('zt_t', 'Trommel')
        self._zelle('zc_spur', 'Spur')
        self._zelle('zc_op', 'Operationscode')
        self.laden(self.adresse_von(puf), k + ': AC := Adresse der Pufferspur ' + puf)
        self.speichere('zc_adr', k + ': Pufferspur merken')
        self.laden(t, k + ': AC := Trommel t')
        self.speichere('zt_t', k + ': Trommel merken')
        self.aufruf('zt_anw', k + ': ZT anwaehlen')
        self.laden(spur, k + ': AC := Spur')
        self.speichere('zc_spur', k + ': Spur merken')
        self.laden(self.konst(op), k + ': AC := Operationscode ' + kom)
        self.speichere('zc_op', k + ': Operationscode merken')
        self.aufruf('zt_ausf', k + ': Spur uebertragen')

    def zt_lies(self, t, spur, puf, k=None):
        """Spur 'spur' der Zusatztrommel t (Variable, 0 bis 3) in die Pufferspur puf lesen (661)."""
        self._zt(0o661, t, spur, puf, k, '661 (ZT -> HT)')

    def zt_schreibe(self, t, spur, puf, k=None):
        """Pufferspur puf auf Spur 'spur' der Zusatztrommel t (Variable, 0 bis 3) schreiben (601)."""
        self._zt(0o601, t, spur, puf, k, '601 (HT -> ZT)')

    # ---- Layout und Ausgabe ------------------------------------------------------------------------
    @staticmethod
    def _labels(lab):
        return lab if isinstance(lab, tuple) else ((lab,) if lab else ())

    def _bewegbar(self, e):
        return e[0] in self._bew and e[4] == 1 and e[1] in ('dw', 'db', 'dbn', 'da')

    def _layout(self):
        """Liste (Adresse, Eintrag). Fuellungen (PAD) nehmen zuerst verlegbare Einzelzellen der folgenden Daten auf, der Rest wird db (dbn im Archiv)."""
        self._fertig()
        code = []
        if self._start_sprung:
            code.append(('', '000', 'haupt', 'Zelle 0000: Sprung zum Hauptprogramm', 1))
        code += self.code
        res, a = [], 0
        for e in code:
            res.append((a, e))
            a += e[4]
        daten = list(self.daten)
        verlegt = set()
        for i, e in enumerate(daten):
            if i in verlegt:
                continue
            lab, cd, opd, kom, zel = e
            if cd == 'PAD':
                mod, rest = opd
                n = (rest - a) % mod
                j = i + 1
                while n and j < len(daten):
                    if j not in verlegt and self._bewegbar(daten[j]):
                        verlegt.add(j)
                        res.append((a, daten[j]))
                        a += 1
                        n -= 1
                    j += 1
                if n:
                    res.append((a, (lab, self._leer(), _zahl(n), kom, n)))
                    a += n
                continue
            res.append((a, e))
            a += zel
        return res

    def _fertig(self):
        """Bausteine, die erst beim Schreiben entstehen (Unterprogramme, Tafeln), einmal anfuegen; Optimierungen 021 und 010."""
        if self._fertig_ok:
            return
        self._fertig_ok = True
        while self._spaeter:
            f = self._spaeter.pop(0)
            f()
        if self.optimiere:
            self._sprung_auf_sprung()
        self._rueck_am_ende()

    def _sprung_auf_sprung(self):
        """Regel 021: Sprung auf eine Zelle, die selbst nur '000 b' enthaelt, geht gleich nach b."""
        spruenge = ('000', '040', '050', '140', '150', '170')
        ziel = {e[0]: e for e in self.code if e[0] and isinstance(e[0], str) and e[1] == '000' and isinstance(e[2], str)}
        neu = []
        for e in self.code:
            if e[1] in spruenge and isinstance(e[2], str):
                t, gesehen = e[2], set()
                while t in ziel and t not in gesehen:
                    gesehen.add(t)
                    t = ziel[t][2]
                if t != e[2]:
                    self.eingespart_21 = getattr(self, 'eingespart_21', 0) + 1
                    e = (e[0], e[1], t, e[3], e[4])
            neu.append(e)
        self.code[:] = neu

    def _rueck_am_ende(self):
        """Festlegung 010: der letzte Ausgang jedes UP wird zur Rueckkehrzelle (db), die vorherige Datenzelle entfaellt.
        Ein UP ohne Ausgang behaelt eine Datenzelle."""
        for name, rn in self._ups.items():
            ex = self._exits.get(name, [])
            if not ex:
                self.daten.append((rn, self._leer(), _zahl(1), 'Rueckkehrwort von %s (zur Laufzeit 000 <Rueckkehradresse>)' % name, 1))
                self._bew.add(rn)
                continue
            i = ex[-1]
            lab, cd, opd, kom, zel = self.code[i]
            assert cd == '000' and opd == rn, 'Ausgang %s: unerwarteter Eintrag %r' % (name, self.code[i])
            labs = self._labels(lab) + (rn,)
            self.code[i] = (labs if len(labs) > 1 else rn, self._leer(), _zahl(1),
                            'Rueckkehrzelle von %s: zur Laufzeit 000 <Rueckkehradresse> (Festlegung 010)' % name, 1)
            self.eingespart_10 = getattr(self, 'eingespart_10', 0) + 1

    def _alle(self):
        return [e for _, e in self._layout()]

    def zellen(self):
        return sum(z[4] for z in self._alle()) + len(self._lits)

    def adressen(self):
        adr = {}
        for a, z in self._layout():
            if z[1] != 'abs' or z[0]:
                for l in self._labels(z[0]):
                    if z[1] != 'abs':
                        adr[l] = a
        return adr

    def _lint(self):
        """Warnung, wenn eine Arbeitszelle (db ohne Anfangswert) gelesen, aber nirgends gespeichert wird (Falle 1 im Handbuch: im Test steht dort der Trommelstand)."""
        arb = {e[0] for e in self.daten if e[0] in self._bew and e[1] in ('db', 'dbn')}
        schreib, lies = set(), set()
        for lab, cd, opd, kom, zel in self.code:
            if len(cd) == 3 and cd[0] in '2345' and isinstance(opd, str):
                (schreib if cd[1:] in ('40', '41', '50', '60') else lies).add(opd)
        for n in sorted(arb & lies - schreib):
            print('Warnung (c82gen): Arbeitszelle %s wird gelesen, aber nirgends gespeichert; im Test hat sie keinen Wert.' % n, file=sys.stderr)

    def _ausrichtung(self):
        """Groesste verlangte Ausrichtung (Zellen) mit Rest 0."""
        m = 1
        for e in self.daten:
            if e[1] == 'PAD' and e[2][1] == 0:
                m = max(m, e[2][0])
        return m

    def _kopf_001(self, n):
        al = self._ausrichtung()
        gr = {1: 'egal', 8: '010', 32: '040', 64: '0100'}.get(al)
        if gr is None:
            gr = '%o' % al
        hoechst = self.start_max - n
        if al > 1:
            hoechst -= hoechst % al
        return ['Empfehlung (001): kleinste Startzelle %04o (0002 bis 0037 gehoeren dem KEP), groesste Startzelle %04o (%04o minus %d Zellen%s), Ausrichtung %s%s.'
                % (self.start_min, hoechst, self.start_max, n, ', abgerundet' if al > 1 else '',
                   'auf eine ' + gr + '-Grenze' if al > 1 else gr, '' if al == 1 else ' (Tafeln und Spuren liegen relativ zum Start)')]

    def _zeile(self, labs, code, opd, kom):
        zs = []
        labs = self._labels(labs)
        for l in labs[:-1]:
            zs.append(l + ':')
        zs.append('%-16s%-8s%-14s ; %s' % ((labs[-1] + ':') if labs else '', code, opd, kom))
        return zs

    def schreibe(self, pfad, pruefe=None, bz=None, gen_name=None, testbasis=None, ztpruefe=None):
        """Quelltext schreiben. pruefe = {Symbol: Sollwert (int)}: Sollwerte aus dem Python-Modell.
        testbasis = Ladeadresse fuer den Test (Zeile ;#TESTBASIS, Handbuch 0): Zellen- und BZ-Sollwerte werden um sie verschoben.
        ztpruefe = [(o, ZT-Adresse, Sollwert[, Kommentar]), ...]: Abschnitt 'ZT-Zellen-Pruefung:' hinter den Zellen (nur mit --C8205Z wirksam)."""
        self._fertig()
        n = self.zellen()
        assert n <= self.grenze, 'Speichergrenze ueberschritten: %d > %d Zellen' % (n, self.grenze)
        self._lint()
        adr = self.adressen()
        code_z = sum(z[4] for z in self.code) + (1 if self._start_sprung else 0)
        zeilen = ['; %s' % self.titel,
                  '; ERZEUGT von %s -- nicht von Hand aendern, Aenderungen im Generator.' % (gen_name or 'gen/'),
                  '; Belegung: %d Zellen (Code %d, Daten %d, Literale %d), Grenze %d.' % (
                      n, code_z, n - code_z - len(self._lits), len(self._lits), self.grenze)]
        if self.kopf_auto:
            zeilen += ['; ' + k for k in self._kopf_001(n)]
        zeilen += ['; ' + k for k in self.kopf]
        zeilen += ['; ' + p for p in self._pragmas]
        if testbasis:
            zeilen.append(';#TESTBASIS 0%o' % testbasis)
        off = testbasis or 0
        zeilen.append('                start                ; Zaehlung beginnt bei 0000')
        for lab, code, opd, kom, zel in self._alle():
            zeilen += self._zeile(lab, code, opd, kom)
        zeilen.append('                end                  ; Programmende')
        zeilen.append('')
        if pruefe is not None or self._halt is not None or ztpruefe:
            zeilen.append('; Sollwerte aus dem Python-Modell des Generators (unabhaengig vom Assemblerprogramm).')
            zeilen.append(';#PRUEFE-START')
            kopf = []
            if self._halt is not None:
                idx, lab = self._halt
                # Adresse des Halts: Zellen vor dem Halt zaehlen
                a = (1 if self._start_sprung else 0) + sum(z[4] for z in self.code[:idx])
                kopf.append('BZ=%04o' % (a + 1 + off))
            kopf.append('US=1')
            zeilen.append('; ' + ' '.join(kopf))
            def aadr(sym):          # 'name' oder 'name+n' (n-te Zelle ab name, n dezimal; Felder)
                b, _, o = sym.partition('+')
                return adr[b] + (int(o) if o else 0) + off
            for sym, wert in sorted((pruefe or {}).items(), key=lambda p: aadr(p[0])):
                zeilen.append('; %04o: %s   # %s' % (aadr(sym), wort(wert), sym))
            if ztpruefe:
                zeilen.append('; ZT-Zellen-Pruefung:')
                for e in ztpruefe:
                    o, a, w = e[0], e[1], e[2]
                    assert 0 <= o <= 3 and 0 <= a <= 0o7777, 'ZT-Pruefzeile %r' % (e,)
                    zeilen.append('; %d-%04o: %s' % (o, a, wort(w)) + (('   # ' + e[3]) if len(e) > 3 else ''))
            zeilen.append(';#PRUEFE-ENDE')
        with open(pfad, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(zeilen) + '\n')
        print('%s: %d Zellen (Grenze %d) -> %s' % (self.titel, n, self.grenze, pfad))
        return adr
