# -*- coding: utf-8 -*-
"""
grafik_trommel.py - Trommel des Modus GRAFIK (Stufe 1): gleiche Schnittstelle wie die Klasse Trommel des Interpreters
(rd, wr, schliessen), aber ueber das C-Modul c8205_trommel (echte Trommel mit Koinzidenz, Hintergrund-Thread).

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


class GrafikTrommel:
    """Magnettrommel ueber das C-Modul. Schnittstelle wie I.Trommel: rd(adresse), wr(adresse, wert), schliessen()."""

    def __init__(self, pfad, basp=None, start_index=-1, modul=None):
        """pfad: Trommeldatei (4096 Zeilen). basp: None oder sechs Zeichen 0/1 (--BASP); None = Stellung aus der Schalterdatei
        neben der Trommel (wird mit 000000 angelegt, wenn sie fehlt). start_index: nur fuer reproduzierbare Pruefungen
        (PERM-Index 0..31); im Betrieb -1 = beliebige Lage wie am echten Geraet (kein Schalter dafuer in GRAFIK)."""
        self.pfad = pfad
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

    # --- Schnittstelle des Knotengraphen --------------------------------------------------------------------------
    def rd(self, adresse):
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
