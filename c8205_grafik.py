#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
c8205_grafik.py - Treiber des Modus GRAFIK: Stufe 1 "Kern und Trommel", Stufe 2 "Pult-Fenster" und Stufe 3 "SW-Fenster" (ohne Ton des Schreibwerks).
Version: G4-007 (eigene Zaehlung der GRAFIK-Module; die Konstante VERSION_GRAFIK stimmt damit ueberein; c8205_interp.py zaehlt eigen, siehe dessen Kopf)

Aufgaben (GRAFIK_Beschreibung §11 (alt: Dok. 04 Abschnitt 6), Stufe 1):
  * Rechner: Knotenautomat des C 8205 fuer den Dauerbetrieb am Pult. exec_node und run_e sind KOPIEN der verschachtelten
    Funktionen aus lauf() in c8205_interp.py (Entscheidung Punkt 18: erst kopieren, nach bestandenen Tests herausloesen);
    jede Aenderung am Knotenablauf ist in beiden Fassungen nachzuziehen. Die Pult-Tastenlogik (H, G, M, E, R, ST, Ue, SW, BS, SP,
    K0..K3) ist die Logik von tastenfolge(), aber mit dauerhaftem Zustand und je Taste einzeln aufrufbar.
    E ist getrennt in Niederdruecken (Token 'E+': Phase IV und I, Halt vor Phase II = Knoten 8) und Loslassen (Token 'E-': Phase II
    und III, Halt vor Knoten 19), wie im Handbuch (G2-012). Das Token 'E' ist der kurze Anschlag (E+ und sofort E-, wie 'M' = M+ und M-)
    und gleich dem bisherigen Einzelschritt; der Knotenablauf ist dabei unveraendert, nur an Knoten 8 geteilt (run_e_nieder/run_e_los).
  * Trommel: grafik_trommel.GrafikTrommel (C-Modul, echte Wartezeiten). Die rechnerische Wartezeitschleife der Knoten 040/041
    bleibt bestehen (GRAFIK_Beschreibung §11 (alt: Dok. 04, Punkt 13)); die echte Trommel liefert die Daten und die Echtzeit.
  * K0-Eingabe: grafik_k0.K0Warteschlange (T vom Pult, SW vom SW-Fenster).
  * Schreibwerk-Ausgabe: SwSenke (die Fenster der spaeteren Stufen haengen sich dort an; kein Terminal, kein Echo).
  * Gleichwertigkeit mit TEST (GRAFIK_Beschreibung §1 (alt: Dok. 00, Abschnitt 3.6)): gleiche Ergebnisse bei gleichem Programm; ausgenommen die Zeiten.
    Prueffweg: testscripte/grafik_gleichwertigkeit.py.

GRAFIK-Standardannahmen dieser Stufe (vom Projektinhaber am 21.10.2026 bestaetigt, GRAFIK_Beschreibung §10.5, OP-13: "alle ja"):
  (1) Nach einem Halt (m.halted) bleibt der Rechner stehen; die Tasten H und R heben diesen Zustand auf (GRAFIK_Beschreibung §3.6 (alt: Dok. 01 Abschnitt 1.8 Nr. 23)).
  (2) H waehrend des Laufs wirkt an der Befehlsgrenze (Knoten 2), im Eingabe-Halt sofort; R setzt danach den Befehl fort.
  (3) Kanal-/Schalterwechsel waehrend des Laufs wirken an der Befehlsgrenze bzw. im Eingabe-Halt (Wiederaufsetzen des Eingabebefehls).
"""
import argparse
import os
import sys
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grafik-interpreter-module'))     # die grafik_*-Module
import c8205_interp as I
from c8205_interp import (MASK12, MASK33, KonfigFehler, LaufFehler, Stub, octs, sektor, eintritt_br, FUNCS, Machine)
from grafik_trommel import GrafikTrommel, GrafikAbbruch
from grafik_k0 import K0Warteschlange
from grafik_geraete import GrafikLeser, GrafikStanzer, pruefe_verschieden
from grafik_debuglog import log
from grafik_haltzeit import HaltZeit, FEHLER, EA, SCHRITT, SCHRITT_ENDE

VERSION_GRAFIK = 'G4-007'      # G4-007 (21.10.2026): nur Kopfkommentar, Standardannahmen (1) bis (3) als bestaetigt vermerkt (OP-13), kein Verhalten geaendert; G4-006 (21.10.2026): OP-20 (E nach Abbruch des E-Schritts im Eingabe-Halt wieder wirksam); G4-005: OP-10, OP-11 (AR-Lampen bei E+, G bei gehaltenem E); G4-004: Haltzeit im Einzelschritt (HZ-004)
SPUR_STANDARD = 'c8205_pult_klickspur.txt'
RC_OK, RC_ABBRUCH, RC_START = 0, 8, 16


class Wiederaufsetzen(Exception):
    """Ein Pult-Ereignis hat waehrend eines Eingabe-Halts den Kanal oder Schalter geaendert: der Befehl wird neu ausgefuehrt."""


class HUnterbrechung(Exception):
    """Die Taste H wurde im Eingabe-Halt gedrueckt: der Lauf endet, der Befehl wird nach R neu ausgefuehrt."""


class PultTaste(str):
    """Taste, die vom Pult-Fenster kommt: vor der Ausfuehrung wird (wie am Anfang von tastenfolge()) entschieden, ob eine neue Tastenfolge beginnt."""


_OHNE_NEUE_FOLGE = ('M-', 'E-', 'SW=0', 'SW=1', 'SP+', 'SP-', 'BS+', 'BS-')

# OP-11: Halt wegen Ueberlauf (ANWEISUNG-046) -> der davor liegende Pruefknoten (ANWEISUNG-020) laut Knotengraph
_UEBERLAUF_HALT = {30: 28, 46: 44, 58: 55, 66: 65, 81: 80}


class SwSenke:
    """Ziel der Schreibwerk-Ausgabe (K2). Ersetzt m.sw_datei: a017 -> sw_schreibe() -> senke.schreibe(s) und kehrt zurueck, es
    gibt also weder Terminal- noch Dateiausgabe. Das SW-Fenster (Stufe 3) meldet sich mit hoere() an.
    unterdruecken (Selektor SW, GRAFIK_Beschreibung §3.6 (alt: Dok. 01 Abschnitt 1.8 Nr. 17)): neuer Text wird nicht ausgegeben und nicht nachgeholt; es gibt
    dann weder Klang noch Schreibwerkzeit (Stufe 4, S4-07, O4-10). Der Selektor SW wirkt nur auf die Ausgabe.
    schreibwerk (Stufe 4, grafik_schreibwerk.Schreibwerk): Klang und Schreibwerkzeit je ausgegebenem Zeichen (S4-17); der Text
    erscheint zu Beginn der Schreibwerkzeit, der Aufruf kehrt erst danach zurueck. None = wie bisher (Pruefungen, TEST)."""

    def __init__(self, schreibwerk=None):
        self.text = []
        self.unterdruecken = False
        self.hoerer = []
        self.schreibwerk = schreibwerk

    def schreibe(self, s):
        if self.unterdruecken:
            return
        self.text.append(s)
        for h in list(self.hoerer):
            h(s)
        if self.schreibwerk is not None:
            self.schreibwerk.ausgabe(s)

    def hoere(self, funktion):
        self.hoerer.append(funktion)

    def alles(self):
        return ''.join(self.text)


class HaltMaschine(Machine):
    """Machine mit Halt-Melder (HZ-001): jedes Setzen von halted von False auf True (Stopp, Ueberlauf, Eingabefehler, Fehler im Ablauf) meldet
    der HaltZeit einen Halt. Sonst unveraendert (c8205_interp.py bleibt unberuehrt). halt_art: vor dem Setzen von halted 'Fehler' eintragen,
    wenn der Halt kein Befehl des Programms ist (Geraete- oder Ablauffehler); sonst bestimmt HaltZeit die Art aus halt_grund."""

    @property
    def halted(self):
        return self.__dict__.get('_halted', False)

    @halted.setter
    def halted(self, wert):
        alt = self.__dict__.get('_halted', False)
        self.__dict__['_halted'] = bool(wert)
        if wert and not alt:
            art = self.__dict__.pop('halt_art', None)
            uhr = self.__dict__.get('haltuhr')
            if uhr is not None:
                uhr.halt(art)
        elif not wert:
            self.__dict__.pop('halt_art', None)


class Rechner:
    """Knotenautomat mit Pult-Tastenlogik. Zwei Betriebsweisen:
       pult_modus=True  : GRAFIK (Standardannahmen 1 bis 3 oben).
       pult_modus=False : Verhalten wie lauf()/tastenfolge() in TEST (fuer den Gleichwertigkeitstest)."""

    def __init__(self, graph, trommel, pult_modus=True, knotentest=False, max_knoten=2_000_000, k0=None):
        self.graph = graph
        self.trommel = trommel
        self.pult_modus = pult_modus
        self.knotentest = knotentest
        self.max_knoten = max_knoten
        self.m = HaltMaschine(trommel)
        self.haltuhr = HaltZeit()             # HZ-001: Zeit Start -> Halt und Halt -> Halt (Zeile Haltzeit im HW-Check-Fenster)
        self.haltuhr.grund_fn = lambda: self.m.halt_grund
        self.m.haltuhr = self.haltuhr
        self.zeilen = []                      # Knotenprotokoll (wie in TEST); im Dauerbetrieb nur mit knotentest gefuellt
        self.m.log = lambda s: self.zeilen.append(s)
        self.sw = SwSenke()
        self.m.sw_datei = self.sw
        I.SW_FENSTER = None                   # kein Echo der Eingaben (Entwurf 88), kein Terminal-Fenster
        self.m.k0 = k0 if k0 is not None else K0Warteschlange(self.m, aufruf_beim_warten=self._warte_hook)
        if hasattr(self.m.k0, 'aufruf_beim_warten') and self.m.k0.aufruf_beim_warten is None:
            self.m.k0.aufruf_beim_warten = self._warte_hook
        self.m.k0.bei_halt, self.m.k0.bei_weiter = self._ea_halt, self.haltuhr.weiter      # HZ-001: E/A-Halt im Eingabebefehl
        # dauerhafter Zustand der Pult-Tastenlogik (in TEST: lokale Variablen von tastenfolge)
        self.or_basis = 0
        self.mhalt = False
        self.e_unter_m = 0
        self.e_gedrueckt = False              # Taste E ist niedergedrueckt (E+ ohne E-); bleibt ueber andere Tasten hinweg bestehen
        self.e_nieder_unter_m = False         # M war beim Niederdruecken von E gehalten (dann entfaellt Phase II, das Loslassen bleibt ohne Wirkung)
        self.e_ue_test = None                 # OP-11: Pruefknoten (28, 44, 55, 65, 80), hinter dem E+ im Halt wegen Ueberlauf stehen blieb
        self.e_aufsatz = None                 # OP-11: nach G bei gehaltenem E (Ueberlauf geloescht): Pruefknoten, bei dem E- Phase IV und I fortsetzt
        self.sw_gedrueckt = False             # Property: Schalterstellung SW liegt in m.sw_schalter (a028 liest sie beim Anwahlbefehl K0)
        # Ablaufsteuerung
        self.start_gewuenscht = False
        self.laeuft = False
        self.wiederaufnahme = None            # Knoten, der nach einem H im Eingabe-Halt neu auszufuehren ist
        self.letzter_grund = ''
        self._sperre = threading.RLock()
        self._ereignisse = []
        self._h_angefordert = threading.Event()
        self.thread_modus = False             # True: Tasten werden nur vorgemerkt und im Rechner-Thread ausgefuehrt (nie im Fenster-Thread)
        self._schritt = False                 # True, solange leerlauf() eine vorgemerkte Taste (E) ausfuehrt
        self.beobachter_befehl = None         # Stufe 2: Lampen (wird an der Befehlsgrenze und beim Halt aufgerufen)
        self.beobachter_halt = None

    # ------------------------------------------------------------------------------------------------------------
    # Knotenausfuehrung (KOPIE aus lauf() in c8205_interp.py)
    # ------------------------------------------------------------------------------------------------------------
    def zustandstext(self):
        """Eine Zeile Rechnerzustand fuer das Debug-Log (--DEBUGLOG)."""
        m = self.m
        try:
            erw = m.k0.erwartet('T')
        except Exception:
            erw = '?'
        return (f'BZ={octs(m.BZ,4)} BR={octs(m.adr,4)} {octs(m.OR,3)} AR={octs(m.AR,4)} AC={octs(m.AC,11)} '
                + ' '.join(f'{k}={m.fl.get(k, 0)}' for k in ('H', 'E', 'A', 'T', 'SW', 'K1', 'K2', 'K3', 'US', 'BS', 'FE', 'FUE'))
                + f' BS-Schalter={m.bs_schalter}'
                + f' | laeuft={self.laeuft} schritt={self._schritt} start={self.start_gewuenscht} halted={m.halted} mhalt={self.mhalt}'
                + f' warteschlange={[str(t) for t in self._ereignisse]} eingabe_erwartet={erw}')

    def br_zeile(self, vor):
        m = self.m
        f = m.fl
        self.zeilen.append(f'  BR={octs(m.adr,4)} {octs(m.OR,3)}  (vor Knoten {vor:03d})  '
                           f'BZ={octs(m.BZ,4)} AC={octs(m.AC,11)} FÜ={f["FUE"]} '
                           f'V1={f["V1"]} V2={f["V2"]} V3={f["V1"] & f["V2"]}')

    def exec_node(self, node):
        m, graph = self.m, self.graph
        n = graph[node]
        typ = n['typ']
        zusatz = ''
        br_nach = None
        if node == 2:
            self.br_zeile(2)
        try:
            if typ == 'Konnektor':
                bez = n['text']
                ziel = n['out']
                if ziel is None:
                    for k, o in graph.items():
                        if o['typ'] == 'Konnektor' and o['text'] == bez and o['out'] is not None and k != node:
                            ziel = o['out']
                            if k == 7:
                                br_nach = 7
                            break
                text = f'KON {bez}'
                nxt = ziel
            elif typ == 'Phasenzuordnung':
                text = 'PHA ' + n['text'].replace('Beginn ', '')
                if 'Phase IV' in n['text']:
                    m.zaehler = 0
                    m.start_sek = sektor(m.AR)
                nxt = n['out']
            elif typ == 'Anweisung':
                f = FUNCS.get(n['anw'])
                if f is None:
                    raise Stub(f'ANWEISUNG-{n["anw"]:03d} unbekannt')
                f(m)
                text = f'ANW {n["anw"]:03d}'
                nxt = n['out']
            elif typ == 'Test':
                f = FUNCS.get(n['anw'])
                if f is None:
                    raise Stub(f'ANWEISUNG-{n["anw"]:03d} unbekannt')
                r = f(m)
                text = f'TST {n["anw"]:03d}'
                zusatz = ' -> wahr' if r else ' -> falsch'
                nxt = n['wahr'] if r else n['falsch']
            else:
                raise Stub(f'Knotentyp {typ!r} unbekannt')
        except KonfigFehler as e:
            fe = f'Geraet nicht nutzbar (Knoten {node}): {e}'
            self.zeilen.append(f'K{node:03d} {fe}')
            raise LaufFehler(fe)
        except Stub as e:
            fe = f'STUB bei Knoten {node}: {e}'
            self.zeilen.append(f'K{node:03d} {fe}')
            raise LaufFehler(fe)
        if self.knotentest:
            self.zeilen.append(f'K{node:03d} {text} BZ={octs(m.BZ,4)} AR={octs(m.AR,4)} AC={octs(m.AC,11)}{zusatz}')
        if br_nach:
            self.br_zeile(br_nach)
        if n.get('end'):
            return None
        return nxt

    def ar_lampen(self):
        """Wert der Lampenreihe AR am Pult (OP-10, entschieden 21.10.2026). E+ ohne M, solange E gehalten ist (Phase IV und I sind gelaufen,
        der Automat steht vor Phase II): die Lampen zeigen den Befehlszaehler BZ. Sonst den Adressteil des BR (m.adr); bei E+ mit gehaltenem M
        ist das das erhoehte AR (m.adr := AR beim Niederdruecken)."""
        m = self.m
        if self.e_gedrueckt and not self.e_nieder_unter_m and m.vor_phase2:
            return m.BZ & MASK12
        return m.adr & MASK12

    def _zustand_br(self):
        m = self.m
        return f'BR={octs(m.adr,4)} {octs(m.OR,3)} BZ={octs(m.BZ,4)} AR={octs(m.AR,4)} AC={octs(m.AC,11)}'

    def run_e_nieder(self, ab=None):
        """Taste E niederdruecken (Handbuch, Taste E: Phase IV und Phase I werden freigegeben; solange E gedrueckt bleibt, steht der Automat vor
        Phase II). Laeuft von der Befehlsgrenze bis unmittelbar vor Knoten 8 (Beginn Phase II). Jeder Weg zu Phase II fuehrt ueber Knoten 8, und
        Knoten 19 ist ohne Knoten 8 nicht wieder erreichbar (Graphpruefung). Rueckgabe (gestoppt, Zustandstext); gestoppt=True, wenn der Schritt
        vorher im Stopp endet (m.halt_grund). Steht der Automat schon vor Phase II (nach E unter M), gibt es nichts freizugeben.
        ab (OP-11): Pruefknoten, bei dem ein im Halt wegen Ueberlauf stehen gebliebenes Niederdruecken fortgesetzt wird (nach G bei gehaltenem E)."""
        m = self.m
        if ab is None:
            if m.vor_phase2:
                return False, self._zustand_br()
            if m.vor_phase1 and not m.br_aufgestellt:
                node = 2
            else:
                node = eintritt_br(m)
        else:
            node = ab
        m.vor_phase1 = False
        self.e_ue_test = None
        vorher = None
        schritt = 0
        while node != 8:
            schritt += 1
            if schritt > self.max_knoten:
                raise LaufFehler('Abbruch: Knotenlimit beim Niederdruecken von E erreicht')
            if node == 19 and schritt > 1:
                raise LaufFehler('Knoten 019 ohne Phase II erreicht (Knotengraph?)')
            nxt = self.exec_node(node)
            if m.halted:
                if node in _UEBERLAUF_HALT and vorher == _UEBERLAUF_HALT[node]:
                    self.e_ue_test = vorher       # OP-11: Halt wegen Ueberlauf hinter dem Pruefknoten 'vorher'
                return True, self._zustand_br()
            if nxt is None:
                raise LaufFehler(f'Knoten {node} hat keinen Ausgang')
            m.came_from = node
            vorher = node
            node = nxt
        m.vor_phase2 = True
        m.br_aufgestellt = True
        return False, self._zustand_br()

    def run_e_los(self):
        """Taste E loslassen (Handbuch: Phase II und Phase III werden durchlaufen; danach stoppt die Abarbeitung wieder). Laeuft von Knoten 8 bis
        zum Halt vor Knoten 19. Rueckgabe (gestoppt, Zustandstext) wie run_e_nieder."""
        m = self.m
        m.vor_phase2 = False
        node = 8
        schritt = 0
        while True:
            schritt += 1
            if schritt > self.max_knoten:
                raise LaufFehler('Abbruch: Knotenlimit beim Loslassen von E erreicht')
            if node == 19 and schritt > 1:
                break
            nxt = self.exec_node(node)
            if m.halted:
                return True, self._zustand_br()
            if nxt is None:
                raise LaufFehler(f'Knoten {node} hat keinen Ausgang')
            m.came_from = node
            node = nxt
        m.br_aufgestellt = True
        return False, self._zustand_br()

    def run_e(self):
        """Ganzer Einzelschritt (Phase IV, I, II, III) ohne Pause: Niederdruecken und sofort Loslassen. Wirkungstext wie bisher."""
        m = self.m
        gestoppt, z = self.run_e_nieder()
        if not gestoppt:
            gestoppt, z = self.run_e_los()
        if gestoppt:
            return f'E  : Einzelschritt endet im Stopp: {m.halt_grund}'
        return f'E  : Einzelschritt (Phase IV, I, II, III), Halt vor Knoten 019; {z}'

    def _schritt_start(self, gemessen):
        """HZ-004: Beginn der Zeitmessung eines Einzelschritts (einmal je Tastendruck, auch bei E = E+ und E- zusammen)."""
        if not gemessen:
            self.haltuhr.start(SCHRITT)
        return True

    def _e_taste(self, u, eff):
        """Taste E. 'E+' = Niederdruecken (Phase IV und I), 'E-' = Loslassen (Phase II und III), 'E' = beides sofort (kurzer Anschlag).
        Wirksam nur bei Schalter H. Unter gehaltenem M entfaellt Phase II: das Niederdruecken erhoeht BZ und AR (wie bisher), das Loslassen
        bleibt ohne Wirkung. Rueckgabe False nur bei einer unzulaessigen Folge (E+ bei gedrueckter, E- bei nicht gedrueckter Taste)."""
        m = self.m
        pre = {'E': 'E  :', 'E+': 'E+ :', 'E-': 'E- :'}[u]
        zeile = None
        gem = gest = False                     # HZ-004: Zeitmessung des Einzelschritts laeuft / Schritt endete im Stopp
        if u in ('E', 'E+'):
            if self.e_gedrueckt:
                eff.append('?? : E gedrueckt, obwohl E bereits gedrueckt ist')
                return False
            self.e_gedrueckt = True
            self.e_nieder_unter_m = self.mhalt
            if self.mhalt:
                if m.bz_g:
                    alt = m.BZ
                    m.bz_g = False
                    m.BZ = 1
                    m.AR = 1
                    m.AC = ((alt + 2) & MASK12) << 9
                else:
                    m.BZ = (m.BZ + 1) & MASK12
                    m.AR = m.BZ
                    m.AC = ((m.BZ + 1) & MASK12) << 9
                m.adr = m.AR            # die Lampenreihe AR (= Adressteil des BR, m.adr) zeigt das erhoehte AR (Handbuch: E unter M erhoeht AR); wie TEST seit 0.03-015
                m.vor_phase2 = True
                m.br_tasten_m = False
                self.e_unter_m += 1
                zeile = (f'{pre} (M gehalten) Befehlsentnahme gesperrt, BZ := {octs(m.BZ,4)}, AR := {octs(m.AR,4)}, '
                         f'AC := {octs(m.AC,11)} (BZ+1 im Adressfeld); BR-Adressteil := AR')
            elif not m.fl['H']:
                zeile = f'{pre} nur bei Schalter H wirksam, H nicht gesetzt -> keine Wirkung'
            elif m.halted:
                zeile = f'{pre} Automat steht im Stopp ({m.halt_grund}) -> keine weitere Ausfuehrung'
            else:
                if m.bz_g and m.OR == 0:
                    m.BZ = 0
                    m.bz_g = False
                if m.vor_phase2:
                    zeile = f'{pre} Automat steht schon vor Phase II -> beim Niederdruecken nichts freizugeben'
                else:
                    gem = self._schritt_start(gem)
                    gestoppt, z = self.run_e_nieder()
                    gest = gest or gestoppt
                    zeile = (f'{pre} Einzelschritt endet im Stopp: {m.halt_grund}' if gestoppt
                             else f'{pre} E niedergedrueckt: Phase IV und I, Halt vor Phase II (Knoten 008); {z}')
        if u in ('E', 'E-'):
            if u == 'E-' and not self.e_gedrueckt:
                eff.append('?? : E losgelassen, obwohl E nicht gedrueckt ist')
                return False
            unter_m = self.e_nieder_unter_m
            self.e_gedrueckt = False
            if unter_m:
                if u == 'E-':
                    zeile = f'{pre} (E unter M niedergedrueckt) Phase II entfaellt -> beim Loslassen keine Wirkung'
            elif not m.fl['H']:
                if u == 'E-':
                    zeile = f'{pre} nur bei Schalter H wirksam, H nicht gesetzt -> keine Wirkung'
            elif m.halted:
                if u == 'E-':
                    zeile = f'{pre} Automat steht im Stopp ({m.halt_grund}) -> keine weitere Ausfuehrung'
            elif self.e_aufsatz is not None:
                # OP-11: G bei gehaltenem E hat den Ueberlauf geloescht; das Loslassen setzt Phase IV und I fort und durchlaeuft dann Phase II und III
                ab, self.e_aufsatz = self.e_aufsatz, None
                gem = self._schritt_start(gem)
                gestoppt, z = self.run_e_nieder(ab=ab)
                if not gestoppt:
                    gestoppt, z = self.run_e_los()
                gest = gest or gestoppt
                zeile = (f'{pre} Einzelschritt endet im Stopp: {m.halt_grund}' if gestoppt
                         else f'{pre} E losgelassen nach G (Ueberlauf geloescht): Phase IV und I fortgesetzt, Phase II und III, Halt vor Knoten 019; {z}')
            elif m.vor_phase2:
                gem = self._schritt_start(gem)
                gestoppt, z = self.run_e_los()
                gest = gest or gestoppt
                if gestoppt:
                    zeile = f'{pre} Einzelschritt endet im Stopp: {m.halt_grund}'
                elif u == 'E':
                    zeile = f'{pre} Einzelschritt (Phase IV, I, II, III), Halt vor Knoten 019; {z}'
                else:
                    zeile = f'{pre} E losgelassen: Phase II und III, Halt vor Knoten 019; {z}'
            elif u == 'E-':
                zeile = f'{pre} kein Schritt offen (Phase II steht nicht aus) -> keine Wirkung'
        if gem and not gest:
            self.haltuhr.halt(SCHRITT_ENDE)    # HZ-004: Schritt beendet, der Rechner steht wieder (Halt vor Phase II bzw. vor Knoten 19)
        if zeile is not None:
            eff.append(zeile)
        return True

    # ------------------------------------------------------------------------------------------------------------
    # Pult-Tasten (Logik aus tastenfolge(), je Taste einzeln, Zustand dauerhaft)
    # ------------------------------------------------------------------------------------------------------------
    @property
    def sw_gedrueckt(self):
        """Schalter SW gedrueckt (dauerhafter Zustand; liegt im Rechner, damit der Anwahlbefehl K0 im Programm ihn sieht)."""
        return bool(self.m.sw_schalter)

    @sw_gedrueckt.setter
    def sw_gedrueckt(self, wert):
        self.m.sw_schalter = 1 if wert else 0

    def neue_folge(self, sw_gedrueckt=None):
        """Beginn einer neuen Tastenfolge wie bei jedem Aufruf von tastenfolge() (or_basis := OR, M nicht gehalten)."""
        self.or_basis = self.m.OR
        self.mhalt = False
        self.e_unter_m = 0
        if sw_gedrueckt is not None:
            self.sw_gedrueckt = sw_gedrueckt

    def _or_neu(self):
        self.m.OR = self.or_basis | (0o025 if self.mhalt else 0)

    def _taste(self, t, eff):
        """Verarbeitet EINE Taste; haengt die Wirkungszeile an eff an; Rueckgabe False, wenn die Taste nicht definiert/unzulaessig war."""
        m = self.m
        ok = True
        u = t.upper().replace('Ü', 'UE')
        if u == 'H':
            m.fl['H'] = 1
            if self.pult_modus:
                m.halted = False
            eff.append('H  : Schalter H-R -> "H", Flag H := 1')
        elif u == 'G' and self.e_gedrueckt:
            # OP-11 (entschieden 21.10.2026, Handbuch 4.1 Nr. 2): bei gehaltenem E loescht G NUR den Ueberlauf; BR, AR, BZ, AC, Kanal und
            # die uebrigen Flags bleiben. War E+ im Halt wegen Ueberlauf stehen geblieben, wird dieser Halt aufgehoben; E- setzt dann fort.
            hatte = bool(m.fl['FUE'])
            m.fl['FUE'] = 0
            fortsetzen = (hatte and m.halted and self.e_ue_test is not None
                          and str(m.halt_grund).startswith('Halt wegen Ueberlauf'))
            if fortsetzen:
                m.halted = False
                m.halt_grund = ''
                self.e_aufsatz, self.e_ue_test = self.e_ue_test, None
            eff.append('G  : (E gehalten) nur der Ueberlauf wird geloescht, FUE := 0; BR, AR, BZ, AC und die uebrigen Flags bleiben'
                       + ('; der Halt wegen Ueberlauf ist aufgehoben, E- setzt Phase IV und I fort' if fortsetzen else ''))
        elif u == 'G':
            self.e_aufsatz = self.e_ue_test = None
            for k in m.fl:
                if k not in ('H', 'T', 'SP'):     # das Flag BS (Lampe) wird geloescht, der Schalter BS (m.bs_schalter) bleibt eingerastet
                    m.fl[k] = 0
            m.fl['T'], m.fl['SW'] = (0, 1) if self.sw_gedrueckt else (1, 0)
            m.AR = 0
            m.adr = 0
            self.or_basis = 0
            self._or_neu()
            m.bz_g = True   # BZ bleibt; BZ := 0 erst bei Ausfuehrung des Sprungs nach 0000
            m.br_aufgestellt = False
            m.br_tasten_m = False
            m.vor_phase2 = False
            m.vor_phase1 = False
            m.fl['US'] = 1
            eff.append('G  : alle Flags ausser H,T,BS,SP := 0 (BS, SP: eingerastete Schalter); BR := 0000 000 (AR:=0000, OR:=000); US := 1; K0 angewaehlt, '
                       + ('SW gedrueckt -> SW := 1' if self.sw_gedrueckt else 'SW nicht gedrueckt -> T := 1')
                       + '; BZ bleibt unveraendert (BZ := 0 erst bei Ausfuehrung des Sprungs nach 0000)')
        elif u.startswith('SW') and (u.find('DRUECK') >= 0 or u in ('SW=1', 'SW+')):
            self.sw_gedrueckt = True
            m.fl['SW'], m.fl['T'] = 1, 0
            eff.append('SW gedrueckt: Schalter SW -> Flag SW := 1, T := 0')
        elif u.startswith('SW') and ('LOS' in u or u in ('SW=0', 'SW-')):
            self.sw_gedrueckt = False
            m.fl['SW'], m.fl['T'] = 0, 1
            eff.append('SW geloest (Stellung T): Flag SW := 0, T := 1')
        elif u == 'M' or (u.startswith('M') and (any(w in u for w in ('DRUECK', 'HALT')) or u == 'M+')) \
                or (u.startswith('M') and ('LOS' in u or u == 'M-')):
            press = u == 'M' or u == 'M+' or any(w in u for w in ('DRUECK', 'HALT'))
            release = u == 'M' or not press
            if press:
                if self.mhalt:
                    eff.append('?? : M gedrueckt, obwohl M bereits gedrueckt ist')
                    return False
                self.mhalt = True
                self.e_unter_m = 0
                self.or_basis = m.OR
                self._or_neu()
                eff.append('M gedrueckt halten: OR := OR ODER 025 (BR = AR 025)' if u != 'M'
                           else 'M  : (= M gedrueckt, sofort losgelassen) OR := OR ODER 025 -> BR = AR 025')
            if release:
                if not self.mhalt:
                    eff.append('?? : M losgelassen, obwohl M nicht gedrueckt ist')
                    return False
                self.mhalt = False
                if self.e_unter_m == 0:
                    self.or_basis |= 0o025
                    m.br_aufgestellt = True
                    m.br_tasten_m = True
                    self._or_neu()
                    if u != 'M':
                        eff.append('M loslassen: kein E unter M -> BR = AR 025 bleibt aufgestellt (Ausfuehrung durch E oder R)')
                else:
                    self._or_neu()
                    eff.append('M loslassen: OR-Verknuepfung mit 025 entfaellt fuer Folgeschritte')
        elif u[:2] in ('BS', 'SP') and len(u) > 2 and (u[2:] in ('=1', '+', '=0', '-') or any(w in u for w in ('DRUECK', 'LOS'))):
            name = u[:2]
            press = u[2:] in ('=1', '+') or 'DRUECK' in u
            if name == 'BS':
                m.bs_schalter = 1 if press else 0       # nur die Schalterstellung; das Flag BS (Lampe) wird erst durch einen wirksamen bedingten Stopp 1
                eff.append('BS : Schalter BS ' + ('gedrueckt (eingerastet)' if press else 'geloest') + f' -> Schalterstellung {m.bs_schalter}, Flag BS unveraendert ({m.fl["BS"]})')
            else:
                m.fl[name] = 1 if press else 0
                eff.append(f'{name} : Schalter {name} ' + ('gedrueckt (eingerastet) -> ' if press else 'geloest -> ') + f'Flag {name} := {m.fl[name]}')
        elif u == 'ST':
            if not (m.fl['US'] or m.fl['BS']):
                eff.append('ST : elektronisch verriegelt, Rechner steht weder im bedingten noch im unbedingten Stopp -> keine Wirkung')
            else:
                self.or_basis |= 0o240
                self._or_neu()
                m.fl['US'] = 0
                m.fl['BS'] = 0
                m.br_aufgestellt = True
                eff.append(f'ST : (US oder BS) OR := OR ODER 240 -> BR = {octs(m.adr,4)} {octs(m.OR,3)}, AR unveraendert; US := 0 (aufgestellt, nicht ausgefuehrt)')
        elif u == 'UE':
            if not m.fl['H']:
                eff.append('Ue : nur bei Schalter H wirksam, H nicht gesetzt -> keine Wirkung')
            else:
                m.AR = 0o7777
                m.adr = 0o7777
                self.or_basis |= 0o240
                self._or_neu()
                m.br_aufgestellt = True
                eff.append(f'Ue : AR := 7777; OR := OR ODER 240 -> BR = 7777 {octs(m.OR,3)} (Transport, aufgestellt, nicht ausgefuehrt)')
        elif u in ('E', 'E+', 'E-'):
            ok = self._e_taste(u, eff)
        elif u in ('K0', 'K1', 'K2', 'K3'):
            kn = int(u[1])
            for k in (1, 2, 3):
                m.fl[f'K{k}'] = 1 if k == kn else 0
            if kn == 0:
                m.fl['T'], m.fl['SW'] = (0, 1) if self.sw_gedrueckt else (1, 0)
            else:
                m.fl['T'] = m.fl['SW'] = 0
            eff.append(f'{u} : Kanaltaste (rastend): Kanal K{kn} angewaehlt'
                       + (' ' + ('(SW gedrueckt -> SW := 1)' if self.sw_gedrueckt else '(SW nicht gedrueckt -> T := 1)') if kn == 0 else '')
                       + '; ein im Programm ausgefuehrter Anwahlbefehl uebersteuert diese Einstellung')
        elif u == 'R':
            if self.mhalt:
                ok = False
                eff.append('?? : R bei noch gedruecktem M (M muss vorher losgelassen werden)')
            m.fl['H'] = 0
            m.fl['US'] = 0
            m.fl['BS'] = 0
            self.e_aufsatz = self.e_ue_test = None
            if self.pult_modus:
                m.halted = False
            if not self.mhalt:
                self.haltuhr.start()                  # HZ-001: Bezugspunkt der Haltzeit
            if m.bz_g and m.OR == 0:
                m.BZ = 0
                m.bz_g = False
            self.start_gewuenscht = True
            eff.append('R  : Schalter H-R -> "R", Flag H := 0, US := 0; Interpretation beginnt bei Konnektor B'
                       + (' bzw. bei Knoten 19 (nach M mit Sprung mit Rueckkehrabsicht bei Knoten 54), wenn BR aufgestellt ist' if m.br_aufgestellt else ''))
        else:
            ok = False
            eff.append(f'?? : Taste/Schritt {t!r} ist im Regelwerk (Abschnitt 3) nicht definiert')
        return ok

    def _wirke(self, t, eff):
        """Fuehrt eine Taste aus; vom Pult kommende Tasten (PultTaste) beginnen vorher ggf. eine neue Tastenfolge."""
        if isinstance(t, PultTaste) and t not in _OHNE_NEUE_FOLGE and not self.mhalt and t != 'M+' \
                and not (t.upper() == 'G' and self.e_gedrueckt):          # OP-11: G bei gehaltenem E beginnt keine neue Tastenfolge
            self.neue_folge()
        return self._taste(t, eff)

    def pult_taste(self, t):
        """Taste aus dem Pult-Fenster. Im Thread-Modus (GRAFIK mit Fenster) wird sie nur vorgemerkt: der Rechner-Thread fuehrt sie aus.
        Grund: E kann im Eingabe-Halt auf ein K0-Zeichen warten und darf dabei NICHT den Fenster-Thread blockieren (Checkpoint 13)."""
        t = PultTaste(t)
        log('RECHNER', f'Taste {t} vorgemerkt (thread_modus={self.thread_modus}) | ' + self.zustandstext())
        if self.thread_modus:
            with self._sperre:
                self._ereignisse.append(t)
                if t.upper() == 'H':
                    self._h_angefordert.set()
            return None
        return self.taste(t)

    def taste(self, t):
        """Eine Pult-Taste (aus dem Pult-Thread oder, im Dauerlauf, vorgemerkt fuer die naechste Befehlsgrenze).
        Rueckgabe: Wirkungszeile (str) oder None, wenn die Taste vorgemerkt wurde."""
        with self._sperre:
            if self.laeuft or self._schritt:
                self._ereignisse.append(t)
                if t.upper() == 'H':
                    self._h_angefordert.set()
                return None
            eff = []
            self._wirke(t, eff)
            return eff[-1] if eff else ''

    def leerlauf(self):
        """Im Rechner-Thread aufrufen, wenn nicht gelaufen wird: fuehrt vorgemerkte Pult-Tasten aus. Ein Einzelschritt (E) kann dabei im
        Eingabe-Halt warten; waehrenddessen werden weitere Tasten vorgemerkt und vom Warte-Haken bearbeitet (H bricht den Schritt ab)."""
        with self._sperre:
            if self.laeuft or self._schritt or not self._ereignisse:
                return
            ev, self._ereignisse = self._ereignisse, []
            self._schritt = True
        try:
            while ev:
                t = ev.pop(0)
                log('RECHNER', f'Ausfuehrung Taste {t} beginnt | ' + self.zustandstext())
                try:
                    self._wirke(t, [])
                    log('RECHNER', f'Ausfuehrung Taste {t} endet | ' + self.zustandstext())
                except (HUnterbrechung, Wiederaufsetzen) as e:
                    log('RECHNER', f'Taste {t} abgebrochen durch {type(e).__name__} | ' + self.zustandstext())
                    # Schritt abgebrochen (H bzw. Kanalwechsel im Eingabe-Halt); die Taste selbst ist schon ausgefuehrt.
                    # OP-20 (entschieden 21.10.2026, Variante a): Der Abbruch verlaesst _e_taste, ehe e_gedrueckt zurueckgesetzt wird; ohne
                    # diese Zeilen waere E danach tot. E gilt nach dem Abbruch als losgelassen; der halbe Befehl bleibt fuer R liegen.
                    if str(t).upper() in ('E', 'E+', 'E-'):
                        self.e_gedrueckt = False
                        self.e_nieder_unter_m = False
                except (LaufFehler, Stub, KonfigFehler) as e:
                    print(f'\nFEHLER bei Taste {t}: {e}', file=sys.stderr, flush=True)
                    log('FEHLER', f'bei Taste {t}: {type(e).__name__}: {e}')
                    self.m.halt_art = FEHLER
                    self.m.halted = True
        finally:
            with self._sperre:
                self._schritt = False
                self._ereignisse = ev + self._ereignisse      # nicht ausgefuehrte Tasten (nur bei GrafikAbbruch) nicht verlieren

    def folge(self, tokens, run_e_erlaubt=True):
        """Wie tastenfolge() in TEST: ganze Folge, danach Pruefung auf Ende mit R bzw. im Halt. Rueckgabe (ok, eff)."""
        m = self.m
        self.neue_folge(sw_gedrueckt=False if not self.pult_modus else None)
        self.e_gedrueckt = False
        self.e_aufsatz = self.e_ue_test = None
        eff = []
        ok = True
        toks = list(tokens)
        for t in toks:
            if not self._taste(t, eff):
                ok = False
        if self.mhalt:
            ok = False
            eff.append('?? : Tastenfolge endet mit gedrueckter Taste M (M muss losgelassen werden)')
        if self.e_gedrueckt:
            ok = False
            eff.append('?? : Tastenfolge endet mit gedrueckter Taste E (E muss losgelassen werden)')
        if toks[-1:] and toks[-1].upper() == 'R':
            if m.fl['H'] != 0:
                ok = False
        elif m.fl['H'] != 1:
            ok = False
            eff.append('?? : Tastenfolge endet weder mit R noch im Halt (H) - Ausgangszustand nicht definiert')
        else:
            eff.append('Ende der Tastenfolge ohne R: Rechner bleibt im Halt (H)')
        return ok, eff

    # ------------------------------------------------------------------------------------------------------------
    # Lauf
    # ------------------------------------------------------------------------------------------------------------
    def _ereignisse_abarbeiten(self, im_eingabe_halt=False):
        """Pult-Tasten, die waehrend des Laufs gedrueckt wurden; Aufruf an der Befehlsgrenze und im Eingabe-Halt."""
        with self._sperre:
            if not self._ereignisse:
                return False
            ev, self._ereignisse = self._ereignisse, []
        m = self.m
        vor = tuple(m.fl[k] for k in ('K1', 'K2', 'K3', 'T', 'SW'))
        h = False
        for t in ev:
            if t.upper() == 'H':
                h = True
            eff = []
            self._wirke(t, eff)
        self._h_angefordert.clear()
        if h:
            return 'H'
        nach = tuple(m.fl[k] for k in ('K1', 'K2', 'K3', 'T', 'SW'))
        return 'KANAL' if (im_eingabe_halt and vor != nach) else True

    def _ea_halt(self):
        """HZ-001: der Rechner wartet an einem Eingabebefehl (Zeichen oder Lochbanddatei): E/A-Halt."""
        self.haltuhr.halt(EA)

    def _warte_hook(self):
        """Aus dem Warten auf eine Eingabe (K0-Warteschlange): Pult-Ereignisse verarbeiten."""
        if self._h_angefordert.is_set() or self._ereignisse:
            log('RECHNER', 'Warte-Haken (Eingabe-Halt): Ereignisse ' + str([str(t) for t in self._ereignisse]))
            r = self._ereignisse_abarbeiten(im_eingabe_halt=True)
            if r == 'H':
                raise HUnterbrechung()
            if r == 'KANAL':
                raise Wiederaufsetzen()

    def unterbrechen(self):
        """Aus einem anderen Thread: Taste H (jederzeit, auch waehrend des Laufs)."""
        self.taste('H')

    def lauf(self, grenz_hook=None):
        """Knotenschleife ab dem aufgestellten BR bis zum Halt oder bis zur Unterbrechung durch H.
        grenz_hook(rechner) wird an jeder Befehlsgrenze (vor Knoten 2) aufgerufen (Pruefhilfe, z. B. #INTERRUPT); Rueckgabe
        None = weiter, ('neu', knoten) = dort fortfahren, ('ende', grund) = Lauf beenden, ('fehler', text) = Fehler.
        Rueckgabe: dict(ok, grund, knoten)."""
        m = self.m
        self.start_gewuenscht = False
        with self._sperre:
            self.laeuft = True
        zaehl = 0
        fehler = None
        ende_grund = None
        try:
            if self.wiederaufnahme is not None:
                node = self.wiederaufnahme
                self.wiederaufnahme = None
            else:
                node = eintritt_br(m) if m.br_aufgestellt else 1
                m.br_aufgestellt = False
            while not m.halted:
                zaehl += 1
                if zaehl > self.max_knoten:
                    fehler = 'Abbruch: Knotenlimit erreicht (Endlosschleife?)'
                    break
                # Befehlsgrenze: Knoten 2 (Beginn Phase I nach einer Taste/Folgebefehl) UND der Weg ueber Konnektor 63->7->6
                # (naechster Befehl nach Sprung bzw. Befehlsende, ohne Knoten 2). Ohne den zweiten Fall wird H in einer
                # Endlosschleife aus Sprungbefehlen nie bemerkt.
                if node == 2 or (node == 6 and m.came_from == 63):
                    if self.beobachter_befehl is not None:
                        self.beobachter_befehl(self)
                    if self._h_angefordert.is_set() or self._ereignisse:
                        r = self._ereignisse_abarbeiten()
                        if r == 'H':
                            # Unterbrechung an der Befehlsgrenze (wie #INTERRUPT in TEST): Phase IV des vorigen Befehls ist abgelaufen
                            m.br_aufgestellt = m.br_tasten_m = m.vor_phase2 = m.bz_g = False
                            m.vor_phase1 = True
                            ende_grund = 'Halt (Schalter H): Unterbrechung durch das Pult'
                            break
                    if node == 2 and grenz_hook is not None:      # #INTERRUPT-Pruefhilfe wie in TEST nur an Knoten 2
                        a = grenz_hook(self)
                        if a:
                            if a[0] == 'neu':
                                node = a[1]
                                continue
                            if a[0] == 'ende':
                                ende_grund = a[1]
                                break
                            if a[0] == 'fehler':
                                fehler = a[1]
                                break
                try:
                    nxt = self.exec_node(node)
                except Wiederaufsetzen:
                    continue
                except HUnterbrechung:
                    self.wiederaufnahme = node
                    ende_grund = 'Halt (Schalter H): Unterbrechung im Eingabe-Halt'
                    break
                except LaufFehler as e:
                    fehler = str(e)
                    break
                if m.halted:
                    break
                if nxt is None:
                    fehler = f'Knoten {node} hat keinen Ausgang'
                    break
                m.came_from = node
                node = nxt
        finally:
            with self._sperre:
                self.laeuft = False
                rest, self._ereignisse = self._ereignisse, []
            for t in rest:                       # zwischen Befehlsgrenze und Ende gedrueckte Tasten
                self._wirke(t, [])
        grund = fehler or ende_grund or m.halt_grund
        self.letzter_grund = grund
        if fehler is not None:
            self.haltuhr.halt(FEHLER)                 # HZ-001: Fehler im Knotenablauf beendet den Lauf, ohne dass halted gesetzt wird
        if self.beobachter_halt is not None:
            self.beobachter_halt(self)
        return dict(ok=fehler is None, grund=grund, knoten=zaehl)

    def lauf_wenn_gewuenscht(self, **kw):
        """Fuer den Treiber: laeuft, solange R (neu) gedrueckt wurde; Rueckgabe das Ergebnis des letzten Laufs oder None."""
        r = None
        while self.start_gewuenscht:
            log('RECHNER', 'Lauf beginnt (R) | ' + self.zustandstext())
            r = self.lauf(**kw)
            log('RECHNER', f'Lauf endet: {r.get("grund") if r else None} | ' + self.zustandstext())
        return r

    def abbrechen(self):
        """Aus einem anderen Thread (X im Fenster, Netz-Aus, Strg+C-Ersatz): beendet jedes Warten."""
        k0 = self.m.k0
        if hasattr(k0, 'abbrechen'):
            k0.abbrechen()
        if hasattr(self.trommel, 'abbrechen'):
            self.trommel.abbrechen()


# ------------------------------------------------------------------------------------------------------------------
# Aufbau und Treiber
# ------------------------------------------------------------------------------------------------------------------
def lade_graph(mdverz):
    graph_pfad = os.path.join(mdverz, 'C8205-Interpreter-Eingänge_der_Knoten.md')
    t2_pfad = os.path.join(mdverz, 'C8205-Interpreter-Beschreibung_der_Knoten.md')
    for p in (graph_pfad, t2_pfad):
        if not os.path.isfile(p):
            raise KonfigFehler(f'Knotendokumentation nicht gefunden: {p}')
    graph = I.load_graph(graph_pfad)
    I.load_t2(t2_pfad)
    return graph


def richte_geraete_ein(r, leser1=None, leser2=None, stanzer1=None):
    """Lochbandleser (Ordner, Korb, aktives Warten) und -stanzer (stanzer.ls) an den Rechner haengen (grafik_geraete.py).
    Die Leser rufen beim Warten denselben Haken auf wie die K0-Warteschlange (H, Kanalwechsel, Abbruch)."""
    pruefe_verschieden(leser1, leser2)
    for k, pfad in ((1, leser1), (2, leser2)):
        if pfad:
            r.m.leser[k] = GrafikLeser(pfad, nr=k, aufruf_beim_warten=r._warte_hook)
            r.m.leser[k].bei_halt, r.m.leser[k].bei_weiter = r._ea_halt, r.haltuhr.weiter
    if stanzer1:
        r.m.stanzer = GrafikStanzer(stanzer1)


def rechner_schleife(r, stop):
    """Rumpf des Rechner-Threads im Fenster-Betrieb: Tasten (auch E) werden NUR hier ausgefuehrt; eine Ausnahme beendet den Thread nicht
    (sonst waere das Pult tot)."""
    while not stop.is_set():
        try:
            r.leerlauf()
            r.lauf_wenn_gewuenscht()
        except GrafikAbbruch:
            break
        except Exception as e:
            print(f'\nFEHLER im Rechner-Thread: {type(e).__name__}: {e}', file=sys.stderr, flush=True)
            import traceback
            log('FEHLER', 'Rechner-Thread: ' + traceback.format_exc())
            r.start_gewuenscht = False
            r.m.halt_art = FEHLER
            r.m.halted = True
        time.sleep(0.005)


def _wache(r, st, fenster, stop):
    """Debug: jede Sekunde eine Statuszeile; steht der Fenster-Takt oder haengt ein Einzelschritt, werden die Stacks aller Threads ausgegeben."""
    schritte = 0
    letzter_dump = 0.0
    while not stop.wait(1.0):
        alter = time.monotonic() - fenster.letzter_takt
        rt = [t for t in threading.enumerate() if t.name == 'rechner']
        schritte = schritte + 1 if r._schritt else 0
        log('STATUS', f'takt_alter={alter:.2f}s rechner_thread={"lebt" if rt else "FEHLT/ENDE"} netz={st.netz} rastet={sorted(st.rastet)} '
                      f'halter={sorted(st.halter)} maus_gehalten={sorted(st.maus_gehalten)} | ' + r.zustandstext())
        jetzt = time.monotonic()
        if (alter > 1.5 or schritte >= 3) and jetzt - letzter_dump > 10:
            letzter_dump = jetzt
            from grafik_debuglog import threads_ausgeben
            threads_ausgeben(f'Fenster-Takt steht seit {alter:.1f}s' if alter > 1.5 else f'Einzelschritt haengt seit {schritte}s')


def pult_betrieb(r, args, here):
    """Stufe 2: Pult-Fenster im Hauptthread, Rechner in einem eigenen Thread (laeuft erst nach dem Hochlauf, B gruen)."""
    try:
        import tkinter  # noqa: F401
        from grafik_pult import PultSteuerung, HOCHLAUF_S, AUSLAUF_S, ENDE
        from grafik_pult_fenster import PultFenster
    except ImportError as e:
        print(f'\nFEHLER: Pult-Fenster nicht moeglich (Tkinter fehlt? {e}). '
              'Linux: Paket python3-tk installieren; oder mit --ohne-fenster starten.', file=sys.stderr)
        return RC_START
    stop = threading.Event()
    durch_x = []

    def rechner_thread():
        rechner_schleife(r, stop)

    def bei_betrieb():
        r.taste('H')
        r.taste('SW=0')                             # Startstellung: H und T (GRAFIK_Beschreibung §3.6 (alt: Dok. 01 Abschnitt 1.8 Nr. 3))
        r.thread_modus = True
        threading.Thread(target=rechner_thread, name='rechner', daemon=True).start()

    def bei_ende():
        stop.set()
        r.abbrechen()

    pult_ordner = os.path.join(here, 'pult')
    # Stufe 4: Schreibwerk (Schreibwerkzeit S4-17 gilt auch bei --STUMM, die Toene nicht), Rechnertoene, Leser und Stanzer ueber den Mischer
    # (C-Modul tonmisch ueber grafik_tonmisch_c; Rueckfall: Python-Mischer grafik_tonmisch). Windows: winmm ist noch nicht getestet, dort bleiben die
    # Stufe-2-Rechnertoene (winsound).
    from grafik_schreibwerk import Schreibwerk
    from grafik_geraeteton import LeserTon, StanzerTon, lade_leserklaenge, lade_stanzerklaenge
    import grafik_tonmisch as TM
    f_pult, f_sw, f_ll, f_ls = TM.ton_faktoren(getattr(args, 'TON', None) or TM.parse_ton(TM.TON_STANDARD))         # --TON: Pult SW LL LS (G4-004)
    mischer, spieler, ton_ausfall = None, None, []
    ton_ordner = os.path.join(here, 'ton')
    leser_ton = stanzer_ton = None
    if args.STUMM:
        ton = None
        r.sw.schreibwerk = Schreibwerk(None, None)
        leser_ton = LeserTon(None, None)                    # kein Ton, das Lesetempo (130 Zeichen/s) gilt
        stanzer_ton = StanzerTon(None, None)                # kein Ton, das Stanztempo (ungefaehr 50 Zeichen/s) gilt
    else:
        if os.name == 'nt':
            from grafik_ton import RechnerTon
            print('Hinweis: Toene unter Windows noch nicht ueber den Mischer (winmm fehlt): nur Rechnertoene (winsound) und Schreibwerkzeit.', file=sys.stderr)
            ton = RechnerTon(ton_ordner, meldung=False)
            r.sw.schreibwerk = Schreibwerk(None, None)
            leser_ton = LeserTon(None, None)
            stanzer_ton = StanzerTon(None, None)
        else:
            spieler = TM.finde_spieler()
            if spieler is None:                             # S4-04 (E O4-4): Abbruch vor dem Aufblenden der Fenster
                print('\nFEHLER: Kein Abspielprogramm gefunden (paplay, pw-cat, aplay, ffplay). Ton nicht moeglich; '
                      'mit --STUMM ohne Ton starten.', file=sys.stderr)
                return RC_START
            from grafik_rechnerton import MischerRechnerTon
            try:
                ton = MischerRechnerTon(ton_ordner, faktor=f_pult)
                r.sw.schreibwerk = Schreibwerk.laden(ton_ordner, None)
                r.sw.schreibwerk.pegel = f_sw
                leser_ton = LeserTon(None, lade_leserklaenge(ton_ordner), pegel=f_ll)
                stanzer_ton = StanzerTon(None, lade_stanzerklaenge(ton_ordner), pegel=f_ls)
            except (OSError, ValueError) as e:
                print(f'\nFEHLER: Klaenge nicht ladbar: {e}', file=sys.stderr)
                return RC_START
    for lk, leser in r.m.leser.items():                     # S4-09: Ton und Lesetempo bei jedem gelieferten Zeichen
        if leser is not None and leser_ton is not None:
            leser.bei_zeichen = leser_ton.zeichen
    if stanzer_ton is not None and r.m.stanzer is not None:
        r.m.stanzer.bei_zeichen = stanzer_ton.zeichen       # S4-10
    # Hochlauf = Laenge von fade_in (B rot), Auslauf = Laenge von fade_out; --netz-schnell kuerzt nur zusammen mit --STUMM (sonst B gruen vor Ende des Tons)
    hoch, aus = HOCHLAUF_S, AUSLAUF_S
    if ton is not None:
        hoch, aus = ton.dauer_fade_in(), ton.dauer_fade_out() + 0.05
        if args.netz_schnell:
            print('Hinweis: --netz-schnell wirkt nur zusammen mit --STUMM (Hoch- und Auslauf folgen sonst dem Ton).', file=sys.stderr)
    elif args.netz_schnell:
        hoch = aus = 0.3
    st = PultSteuerung(pult_ordner, r, hochlauf_s=hoch, auslauf_s=aus,
                       bei_betrieb=bei_betrieb, bei_ende=bei_ende, ton=ton,
                       bei_ls=(stanzer_ton.ls_taste if stanzer_ton is not None else None))
    if args.pult_protokoll or args.DEBUGLOG:
        def klicklog(z):
            log('KLICK', z)
            if args.pult_protokoll:
                print(z, file=sys.stderr, flush=True)
        st.klick_log = klicklog
    aufz = None
    if args.aufzeichnung_pfad or args.wiedergabe_ereignisse is not None:
        import grafik_debuglog as DL
        import hashlib
        try:
            with open(args.trommel, 'rb') as f:
                tmd5 = hashlib.md5(f.read()).hexdigest()
        except OSError:
            tmd5 = '?'
        if args.aufzeichnung_pfad:
            try:
                aufz = DL.Aufzeichnung(args.aufzeichnung_pfad, kopf={'grafik': VERSION_GRAFIK, 'trommel_md5': tmd5,
                                                                     'basp': args.basp, 'aufruf': ' '.join(sys.argv)})
            except OSError as e:
                print(f'\nFEHLER: Klickspur kann nicht geschrieben werden: {e}', file=sys.stderr)
                return RC_START
            st.aufzeichnung = aufz
            print(f'Klickspur wird aufgezeichnet: {os.path.abspath(args.aufzeichnung_pfad)}', file=sys.stderr)
        if args.wiedergabe_ereignisse is not None:
            alt_md5 = args.wiedergabe_kopf.get('trommel_md5')
            if alt_md5 and tmd5 != '?' and alt_md5 != tmd5:
                z = ('WARNUNG: Die Trommeldatei ist nicht mehr die der Aufzeichnung (MD5 verschieden); die Wiedergabe kann anders verlaufen. '
                     'Mit der gesicherten Trommel starten: --trommel KOPIE.txt')
                print('\n' + z, file=sys.stderr)
                log('WIEDERGABE', z)
    try:
        fenster = PultFenster(st, pult_ordner, bei_schliessen=lambda: durch_x.append(1))
    except Exception as e:                          # kein DISPLAY o. ae.
        print(f'\nFEHLER: Pult-Fenster konnte nicht geoeffnet werden: {type(e).__name__}: {e}', file=sys.stderr)
        return RC_START
    try:
        from grafik_sw_fenster import SwFenster
        sw_fenster = SwFenster(fenster, r.sw, r.m.k0, r.m, bei_schliessen=fenster._schliessen)
        fenster.sw_weiter = sw_fenster              # G4-008: Tasten, die beim Pult ankommen, gehen bei K0/SW an die SW-Eingabe
        sw_fenster.starten()
    except Exception as e:                          # das SW-Fenster gehoert zu GRAFIK (GRAFIK_Beschreibung §3.1 (alt: Dok. 01 Abschnitt 1.6)): ohne es kein Betrieb
        print(f'\nFEHLER: SW-Fenster konnte nicht geoeffnet werden: {type(e).__name__}: {e}', file=sys.stderr)
        try:
            fenster.beenden()
        except Exception:
            pass
        return RC_START
    if getattr(args, 'HWCHECK', False):
        try:
            from grafik_hwcheck import HwCheckFenster
            fenster.zusatz.append(HwCheckFenster(fenster.root, r.m))
        except Exception as e:                      # das Pult bleibt bedienbar, auch wenn das Zusatzfenster nicht geht
            print(f'\nWARNUNG: HW-Check-Fenster nicht moeglich: {type(e).__name__}: {e}', file=sys.stderr)
    if args.wiedergabe_ereignisse is not None:
        import grafik_debuglog as DL
        fenster.wiedergabe_einhaengen(DL.Wiedergabe(st, args.wiedergabe_ereignisse, tipper=sw_fenster.tipp_wiedergabe))
    if args.DEBUGLOG:
        fenster.debug_einhaengen()
        threading.Thread(target=_wache, args=(r, st, fenster, stop), name='wache', daemon=True).start()
    import signal
    sigint = []

    def bei_strg_c(signum, frame):
        # Tk faengt eine KeyboardInterrupt-Ausnahme in Rueckrufen ab und macht weiter - deshalb ein Signalhandler, der nur ein Flag setzt;
        # das Fenster prueft es im 40-ms-Takt. Zweimal Strg+C: sofortiges Ende (Notausgang, falls doch etwas haengt).
        if sigint:
            print('\nStrg+C zweimal: sofortiges Ende', file=sys.stderr, flush=True)
            os._exit(RC_ABBRUCH)
        sigint.append(1)
        durch_x.append(1)
        fenster.abbruch_anfordern()

    alt = signal.signal(signal.SIGINT, bei_strg_c)
    if spieler is not None:
        def bei_ausfall(text):                      # Strom im Betrieb ausgefallen: Code 16 wie beim Start (S4-04)
            ton_ausfall.append(text)
            durch_x.append(1)
            try:
                fenster.abbruch_anfordern()
            except Exception:
                pass
        try:
            import grafik_tonmisch_c as TC
            mischer, mischer_art = TC.neuer_mischer(spieler, bei_ausfall=bei_ausfall)
            if mischer_art != 'C':
                print('Hinweis: C-Modul tonmisch nicht gebaut (c-module/python: python3 setup.py build_ext --inplace); es laeuft der Python-Mischer.', file=sys.stderr)
            r.sw.schreibwerk.mischer = mischer
            ton.mischer = mischer
            leser_ton._mischer_ein(mischer)
            stanzer_ton._mischer_ein(mischer)
            mischer.starten()
        except TM.SenkeAusfall as e:
            ton_ausfall.append(str(e))
            durch_x.append(1)
    try:
        fenster.starten()
    except KeyboardInterrupt:
        durch_x.append(1)
    finally:
        signal.signal(signal.SIGINT, alt)
        stop.set()
        r.abbrechen()
        if ton is not None:
            ton.alles_aus()
        for gt in (leser_ton, stanzer_ton):
            if gt is not None:
                gt.stop()
        if mischer is not None:
            mischer.alles_aus()
            mischer.schliessen()
        if aufz is not None:
            aufz.schliessen()
    if ton_ausfall:
        print(f'\nFEHLER: Tonausgabe ausgefallen: {ton_ausfall[0]}', file=sys.stderr)
        return RC_START
    if durch_x:
        print('\nABBRUCH durch den Benutzer (Fenster geschlossen oder Strg+C)', file=sys.stderr)
        return RC_ABBRUCH
    return RC_OK


def TM_ton_standard():
    import grafik_tonmisch as TM
    return TM.TON_STANDARD


def _ton_arg(text):
    import grafik_tonmisch as TM
    try:
        return TM.parse_ton(text)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def hauptprogramm(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(prog='c8205_grafik.py', description='C 8205, Modus GRAFIK, Stufe 1 (Kern und Trommel, ohne Fenster und Ton)')
    ap.add_argument('--MODUS', '--modus', dest='modus', default='GRAFIK')
    ap.add_argument('--mdverz', default=os.path.join(here, 'markdown-dateien'))
    ap.add_argument('--trommel', default=os.path.join(here, 'Trommel', 'trommel.txt'))
    ap.add_argument('--leser1')
    ap.add_argument('--leser2')
    ap.add_argument('--stanzer1')
    ap.add_argument('--STUMM', action='store_true')
    ap.add_argument('--TON', '--ton', dest='TON', default=TM_ton_standard(), type=_ton_arg, metavar='pppp',
                    help='Lautstaerke je Gruppe, vier Ziffern 0 bis 9 in der Reihenfolge Pult SW LL LS (Rechnertoene, Schreibwerk, Lochstreifenleser, '
                         'Lochbandstanzer); 5 = Voreinstellung, 0 = stumm. Beispiel: --TON=5955. Wirkungslos mit --STUMM.')
    ap.add_argument('--TASTATUR', '--tastatur', dest='TASTATUR', default='de', metavar='de|en',
                    help='Tastaturbelegung des Rechners (Standard de). Wirkt beim Abspielen einer Klickspur (AltGr-Zeichen unter X11) und im Protokoll; '
                         'beim echten Tippen gilt die Belegung des Betriebssystems.')
    ap.add_argument('--HWCHECK', '--hwcheck', dest='HWCHECK', action='store_true', help='zweites Fenster mit BZ, BR, Spur/Sektor, AC und <<AR>> (oktal), bleibt aufgeblendet')
    ap.add_argument('--BASP', '--basp', dest='basp', default=None, metavar='abcdef')
    # in GRAFIK wirkungslos, ohne Fehler (GRAFIK_Beschreibung §11 (alt: Dok. 04 Abschnitt 2.5), Review F-13)
    for name in ('--out', '--pruefe-stanzer1', '--pruefe-sw-ausgabe', '--k0', '--sw-ausgabe', '--zwischenablage',
                 '--lochbandleser1', '--lochbandleser2', '--lochbandstanzer1'):
        ap.add_argument(name)
    for name in ('--knotentest', '--NO-TERMOUT', '--SW-TERMINAL', '--version'):
        ap.add_argument(name, action='store_true')
    # Gerueste dieser Stufe (entfallen mit dem Pult-Fenster in Stufe 2): Tastenfolge und K0-Zeichen von der Kommandozeile
    ap.add_argument('--entwickler-tasten', metavar='"H G M+ E M- K1 R"', help='Stufe-1-Geruest: Pult-Tasten nacheinander druecken')
    ap.add_argument('--entwickler-k0', metavar='DATEI', help='Stufe-1-Geruest: K0-Zeichen (eines je Zeile) in die Warteschlange legen')
    ap.add_argument('--ohne-fenster', action='store_true', help='Stufe-1-Verhalten ohne Pult-Fenster (wird auch bei --entwickler-tasten/-k0 angenommen)')
    ap.add_argument('--pult-protokoll', action='store_true', help='Entwickler: jeden Pult-Klick mit Ergebnis und Grund auf stderr ausgeben')
    ap.add_argument('--DEBUGLOG', '--debuglog', dest='DEBUGLOG', nargs='?', const='c8205_grafik_debug.log', default=None, metavar='DATEI',
                    help='Fehlersuche: Protokoll aller Mausereignisse, Fokus, Tasten und Rechnerzustaende in DATEI (Standard c8205_grafik_debug.log im aktuellen Ordner)')
    ap.add_argument('--AUFZEICHNUNG', '--aufzeichnung', dest='AUFZEICHNUNG', nargs='?', const=SPUR_STANDARD, default=None, metavar='DATEI',
                    help=f'Klicks auf die Pult-Tasten mit Zeitabstand in DATEI aufzeichnen (Standard {SPUR_STANDARD}); mit --DEBUGLOG automatisch (DEBUGLOGNAME_klickspur.txt)')
    ap.add_argument('--WIEDERGABE', '--wiedergabe', dest='WIEDERGABE', nargs='?', const=SPUR_STANDARD, default=None, metavar='DATEI',
                    help=f'Debug: eine aufgezeichnete Klickspur (Standard {SPUR_STANDARD}) im selben Zeitabstand selbst abspielen; schaltet --DEBUGLOG ein')
    ap.add_argument('--netz-schnell', action='store_true', help='Entwickler: Hochlauf und Auslauf auf 0,3 s verkuerzen (nur fuer Pruefungen)')
    ap.add_argument('tests', nargs='*')            # entfaellt in GRAFIK: ignoriert
    args = ap.parse_args(argv)

    if args.modus.upper() != 'GRAFIK':
        print(f'FEHLER: unbekannter Modus {args.modus!r} (dieses Programm kennt nur GRAFIK)', file=sys.stderr)
        return RC_START
    import grafik_tastatur as TAST
    try:
        args.TASTATUR = TAST.setze(args.TASTATUR)
    except ValueError as e:
        print(f'FEHLER: --TASTATUR: {e}', file=sys.stderr)
        return RC_START
    if args.basp is not None and not (len(args.basp) == 6 and set(args.basp) <= {'0', '1'}):
        print(f'FEHLER: --BASP: sechs Ziffern 0/1 erwartet, erhalten: {args.basp!r}', file=sys.stderr)
        return RC_START

    for attr, ordner in (('leser1', 'Leser1'), ('leser2', 'Leser2'), ('stanzer1', 'Stanzer1')):
        if getattr(args, attr) is None:
            setattr(args, attr, os.path.join(here, 'virtuelle_Geraete', ordner))
    try:
        pruefe_verschieden(args.leser1, args.leser2)
    except KonfigFehler as e:
        print(f'\nFEHLER: {e}', file=sys.stderr)
        return RC_START

    # Klickspur: --WIEDERGABE ist Debug-Modus (schaltet --DEBUGLOG ein); --DEBUGLOG zeichnet automatisch auf, ausser waehrend einer Wiedergabe
    args.wiedergabe_ereignisse, args.wiedergabe_kopf, args.aufzeichnung_pfad = None, {}, args.AUFZEICHNUNG
    if args.WIEDERGABE:
        import grafik_debuglog as DL0
        try:
            args.wiedergabe_kopf, args.wiedergabe_ereignisse = DL0.lade_klickspur(args.WIEDERGABE)
        except ValueError as e:
            print(f'\nFEHLER: {e}', file=sys.stderr)
            return RC_START
        if args.aufzeichnung_pfad and os.path.abspath(args.aufzeichnung_pfad) == os.path.abspath(args.WIEDERGABE):
            print('\nFEHLER: --AUFZEICHNUNG und --WIEDERGABE nennen dieselbe Datei', file=sys.stderr)
            return RC_START
        if not args.DEBUGLOG:
            args.DEBUGLOG = 'c8205_grafik_debug.log'
            print('Hinweis: --WIEDERGABE ist ein Debug-Modus, --DEBUGLOG wurde eingeschaltet.', file=sys.stderr)
    elif args.DEBUGLOG and not args.aufzeichnung_pfad:
        args.aufzeichnung_pfad = os.path.splitext(args.DEBUGLOG)[0] + '_klickspur.txt'
    if args.DEBUGLOG:
        import platform
        import grafik_debuglog as DL
        DL.starten(args.DEBUGLOG)
        log('START', f'Grafik {VERSION_GRAFIK}, Debuglog {DL.VERSION_DEBUGLOG}, Python {sys.version.split()[0]}, {platform.platform()}, Tastatur {args.TASTATUR}, Aufruf: {sys.argv}')
        print(f'Debug-Log wird geschrieben: {os.path.abspath(args.DEBUGLOG)}', file=sys.stderr)
    trommel = None
    r = None
    rc = RC_OK
    try:
        try:
            graph = lade_graph(args.mdverz)
            trommel = GrafikTrommel(args.trommel, basp=args.basp)
        except KonfigFehler as e:
            print(f'\nFEHLER: {e}', file=sys.stderr)
            return RC_START
        r = Rechner(graph, trommel, pult_modus=True)
        richte_geraete_ein(r, args.leser1, args.leser2, args.stanzer1)
        if args.entwickler_k0:
            for z in open(args.entwickler_k0, encoding='utf-8'):
                z = z.rstrip('\r\n')
                if z and not z.startswith('#'):
                    r.m.k0.einspeisen(z if len(z) == 1 else z.strip())
            r.m.k0.ende_wenn_leer = True
        if not (args.ohne_fenster or args.entwickler_tasten or args.entwickler_k0):
            return pult_betrieb(r, args, here)
        if args.WIEDERGABE or args.AUFZEICHNUNG:
            print('Hinweis: --AUFZEICHNUNG/--WIEDERGABE wirken nur mit dem Pult-Fenster.', file=sys.stderr)
        if args.HWCHECK:
            print('Hinweis: --HWCHECK wirkt nur mit dem Pult-Fenster (nicht mit --ohne-fenster, --entwickler-tasten, --entwickler-k0).', file=sys.stderr)       # finally unten schliesst die Trommel
        if args.entwickler_tasten:
            for t in args.entwickler_tasten.split():
                r.taste(t)
                res = r.lauf_wenn_gewuenscht()
                if res is not None and not res['ok']:
                    print('LAUF NICHT ORDNUNGSGEMAESS BEENDET:', res['grund'], file=sys.stderr)
        m = r.m
        print(f'Ende: {r.letzter_grund} | BZ={octs(m.BZ,4)} AC={octs(m.AC,11)} AR={octs(m.AR,4)} | '
              + ' '.join(f'{k}={m.fl[k]}' for k in ('FE', 'FUE', 'BS', 'US', 'E', 'A', 'V1', 'V2')))
        if r.sw.alles():
            print('SW-Ausgabe:', repr(r.sw.alles()))
        print('Trommel:', trommel.statistik())
    except (KeyboardInterrupt, GrafikAbbruch):
        print('\nABBRUCH durch den Benutzer (Strg+C)', file=sys.stderr)
        rc = RC_ABBRUCH
    finally:
        if trommel is not None:
            trommel.schliessen()
    return rc


if __name__ == '__main__':
    sys.exit(hauptprogramm())
