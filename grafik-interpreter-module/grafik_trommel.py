# -*- coding: utf-8 -*-
"""
grafik_trommel.py - Trommel des Modus GRAFIK (Stufe 1): gleiche Schnittstelle wie die Klasse Trommel des Interpreters
(rd, wr, schliessen), aber ueber das C-Modul c8205_trommel (echte Trommel mit Koinzidenz, Hintergrund-Thread).
Version: G5-001  (Kennung neu eingefuehrt; fruehere Staende sind im Archiv nicht belegt)

Regeln (GRAFIK_Beschreibung §7 (alt: Dok. 02 Abschnitt 6), GRAFIK_Beschreibung §7 (alt: Dok. 04 Abschnitt 4)):
  * Nur das C-Modul greift auf die Trommeldatei zu; es gibt keinen Zwischenspeicher (kein "mem").
  * Jeder Zugriff blockiert, bis die Zelle unter dem Kopf ist (0 bis 31 Wortzeiten zu 104 Mikrosekunden).
  * Die Bahnsperrenschalter werden als ERSTES, vor dem ersten Trommelzugriff, uebernommen (--BASP bzw. Schalterdatei
    neben der Trommeldatei, GRAFIK_Beschreibung §7 (alt: Dok. 02 Abschnitt 6), Entwurf 86/87). Ein gesperrter Schreibzugriff verbraucht seine
    Wartezeit und aendert die Zelle nicht; der Befehlsablauf bleibt unbeeinflusst.
  * Keine Vorbelegung und kein Eingriff des Interpreters in die Trommeldatei: was in der Datei steht, ist die Startbelegung.
  * Ist das C-Modul nicht ladbar oder die Trommel nicht einschaltbar: KonfigFehler (der Treiber meldet und beendet mit Code 16).
  * Strg+C: Python behandelt es; schliessen() gehoert in das finally des Aufrufers und beendet das C-Modul.
"""
import os
import sys
import time

import c8205_interp as I

MASK12 = I.MASK12
MASK33 = I.MASK33

_HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    # Projektordner (die Module liegen in grafik-interpreter-module/)
# Das uebersetzte Erweiterungsmodul liegt im Projekt unter c-module/python/ (mit den Quellen und den Tests).
MODULVERZ = os.path.join(_HIER, 'c-module', 'python')


class GrafikAbbruch(Exception):
    """Ein wartender Zugriff oder eine wartende Eingabe wurde abgebrochen (X im Fenster, Netz-Aus, warten_abbrechen())."""


def lade_modul():
    """Importiert c8205_trommel. Nicht ladbar: KonfigFehler mit Bauanleitung (Rueckkehrcode 16 beim Aufrufer)."""
    if MODULVERZ not in sys.path:
        sys.path.insert(0, MODULVERZ)
    try:
        import c8205_trommel
    except ImportError as e:
        raise I.KonfigFehler(
            'das C-Modul "c8205_trommel" (echte Trommel) ist nicht ladbar: ' + str(e) + '\n'
            '  Bauen: im Ordner c-module/python  "python3 setup.py build_ext --inplace" '
            '(Windows: "python setup.py build_ext --inplace"; braucht einen C-Compiler und die Python-Entwicklungsdateien).')
    return c8205_trommel


PERM = (0o00, 0o15, 0o32, 0o07, 0o24, 0o01, 0o16, 0o33, 0o10, 0o25, 0o02, 0o17, 0o34, 0o11, 0o26, 0o03,
        0o20, 0o35, 0o12, 0o27, 0o04, 0o21, 0o36, 0o13, 0o30, 0o05, 0o22, 0o37, 0o14, 0o31, 0o06, 0o23)    # Sektorfolge wie c-module/trommel.c
TICK_S = 104e-6                  # eine Wortzeit
ZEITMODELLE = ('echt', 'schnell', 'alt')


class GrafikTrommel:
    """Magnettrommel ueber das C-Modul. Schnittstelle wie I.Trommel: rd(adresse), wr(adresse, wert), schliessen()."""

    def __init__(self, pfad, basp=None, start_index=-1, modul=None, zeitmodell='alt'):
        """pfad: Trommeldatei (4096 Zeilen). basp: None oder sechs Zeichen 0/1 (--BASP); None = Stellung aus der Schalterdatei
        neben der Trommel (wird mit 000000 angelegt, wenn sie fehlt). start_index: nur fuer reproduzierbare Pruefungen
        (PERM-Index 0..31); im Betrieb -1 = beliebige Lage wie am echten Geraet (kein Schalter dafuer in GRAFIK)."""
        self.pfad = pfad
        self.zeitmodell = zeitmodell
        self.vt = 0                  # G4-009: virtuelle Zeit in Wortzeiten (Modell 'echt' und 'schnell')
        self._w0 = self._v0 = None   # Bezug der Echtzeit-Anpassung
        self.T = modul or lade_modul()
        self.eingeschaltet = False
        self.zugriffe = 0
        self.gesperrte_schreibzugriffe = 0
        self.wartezeit_summe = 0
        self.basp_stellung = None
        fehler = I.pruefe_trommeldatei(pfad)
        if fehler:
            raise I.KonfigFehler('Trommeldatei formal fehlerhaft:\n  - ' + '\n  - '.join(fehler[:50])
                                 + (f'\n  ... {len(fehler) - 50} weitere Fehler' if len(fehler) > 50 else ''))
        try:
            self.basp_stellung = self.T.einschalten(pfad, start_index, basp)
        except self.T.TrommelFehler as e:
            raise I.KonfigFehler(f'Trommel nicht einschaltbar: {e}')
        self.eingeschaltet = True
        if self.zeitmodell != 'alt':
            self.vt = PERM.index(self.T.aktueller_sektor() & 0o37)      # die Lage der Trommel beim Einschalten ist der Beginn der virtuellen Zeit

    # --- Schnittstelle des Knotengraphen --------------------------------------------------------------------------
    # --- virtuelle Zeit (G4-009): die Trommel dreht nach dem Tick-Zaehler des Modells, nicht nach der Wanduhr -----------------------
    def _warte_ticks(self, adresse):
        """Wortzeiten bis der Sektor der Adresse unter dem Kopf liegt (0 = jetzt), und Fortschreiben der Zeit."""
        soll = adresse & 0o37
        w = 0
        while PERM[(self.vt + w) & 31] != soll:
            w += 1
        self.vt += w
        self._pace()
        return w

    def tick(self, n=1):
        """Eine (oder n) Wortzeit(en) vergehen (Phasen der Befehlsschleife)."""
        if self.zeitmodell != 'alt':
            self.vt += n
            self._pace()

    def _pace(self):
        """Echtzeit-Anpassung: das Modell laeuft nie schneller als die Hardware (eine Wortzeit = 104 us); hinkt der Rechner hinterher,
        wird nichts aufgeholt, nach einer Pause (Halt, Eingabe-Halt) beginnt der Bezug neu."""
        if self.zeitmodell != 'echt':
            return
        jetzt = time.monotonic()
        if self._w0 is None:
            self._w0, self._v0 = jetzt, self.vt
            return
        d = self._w0 + (self.vt - self._v0) * TICK_S - jetzt
        if d > 0.002:
            time.sleep(d)
        elif d < -0.02:
            self._w0, self._v0 = jetzt, self.vt

    def rd(self, adresse):
        if self.zeitmodell != 'alt':
            wz = self._warte_ticks(adresse)
            self.zugriffe += 1
            self.wartezeit_summe += wz
            return self.T.lesen(adresse & MASK12) & MASK33
        try:
            wert, wz = self.T.lesen_warten(adresse & MASK12)
        except self.T.TrommelAbbruch:
            raise GrafikAbbruch('Trommelzugriff abgebrochen')
        except self.T.TrommelFehler as e:
            raise I.KonfigFehler(f'Trommel nicht lesbar: {self.pfad} ({e})')
        self.zugriffe += 1
        self.wartezeit_summe += wz
        return wert

    def wr(self, adresse, wert):
        if self.zeitmodell != 'alt':
            wz = self._warte_ticks(adresse)
            gesperrt = self.T.schreiben(adresse & MASK12, wert & MASK33)
            self.zugriffe += 1
            self.wartezeit_summe += wz
            if gesperrt:
                self.gesperrte_schreibzugriffe += 1
            return
        try:
            gesperrt, wz = self.T.schreiben_warten(adresse & MASK12, wert & MASK33)
        except self.T.TrommelAbbruch:
            raise GrafikAbbruch('Trommelzugriff abgebrochen')
        except self.T.TrommelFehler as e:
            raise I.KonfigFehler(f'Trommel nicht beschreibbar: {self.pfad} ({e})')
        self.zugriffe += 1
        self.wartezeit_summe += wz
        if gesperrt:
            self.gesperrte_schreibzugriffe += 1

    def einblick(self, adresse):
        """Speicherinhalt OHNE Koinzidenz lesen (kein Warten, keine Statistik): nur fuer das HW-Check-Fenster."""
        if not self.eingeschaltet:
            return None
        return self.T.lesen(adresse & MASK12) & MASK33

    # --- Steuerung --------------------------------------------------------------------------------------------------
    def abbrechen(self):
        """Aus einem anderen Thread: beendet einen wartenden Zugriff (er wirft GrafikAbbruch)."""
        if self.eingeschaltet:
            self.T.warten_abbrechen()

    def aktueller_sektor(self):
        return self.T.aktueller_sektor()

    def statistik(self):
        s = dict(self.T.statistik()) if self.eingeschaltet else {}
        s.update(rd_wr_zugriffe=self.zugriffe, gesperrte_schreibzugriffe=self.gesperrte_schreibzugriffe,
                 wartezeit_summe_ticks_aufrufer=self.wartezeit_summe)
        return s

    def schliessen(self):
        if self.eingeschaltet:
            self.eingeschaltet = False
            try:
                self.T.ausschalten()
            except Exception:
                pass
