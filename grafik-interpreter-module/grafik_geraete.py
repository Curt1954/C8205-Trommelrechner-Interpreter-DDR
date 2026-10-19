#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_geraete.py - Lochbandleser und Lochbandstanzer fuer den Modus GRAFIK (Stufe 1, Checkpoint 3).
Version: G1-002

Regeln (GRAFIK_Beschreibung §11 (alt: Dok. 04 Abschnitt 2.5), GRAFIK_Beschreibung Anhang A (alt: Dok. 05) F-11 und F-12, entschieden 15./16.10.2026):

Leser
  * Ein Pfad je Leser, und der ist ein ORDNER. Dateien mit Punkt am Anfang und Unterordner bleiben unbeachtet.
  * Reihenfolge der Dateien nach AENDERUNGSZEIT (aelteste zuerst). Bei gleicher Zeit nach Dateiname (Standardannahme,
    vom Projektinhaber nicht bestaetigt).
  * Im Eingabe-Halt auf dem Leserkanal wartet der Leser AKTIV auf eine Datei (Lampe E leuchtet; das Flag E setzt a032).
    Er blockiert dabei, ruft aber alle `takt` Sekunden den Warte-Haken auf (Pult-Ereignisse, H, Kanalwechsel, Abbruch).
    "Ende bedeutet Leser leer" entfaellt: naechste() liefert nie None.
  * Ist eine Datei komplett gelesen, wird sie in den Unterordner LOCHSTREIFENKORB verschoben (bei Bedarf angelegt) und,
    solange der Eingabe-Halt noch aktiv ist, die naechste Datei genommen. Eine nicht ganz gelesene Datei bleibt stehen.
  * Netz-Aus: eine teilgelesene Datei bleibt im Ordner und wird beim naechsten Start von vorn gelesen.
  * Fehler (ungueltige Zeile, Ordner fehlt, Korb nicht benutzbar) sind KonfigFehler: der Rechner haelt mit Meldung
    (GRAFIK_Beschreibung §11 (alt: Dok. 04 Punkt 14)).
  * Zwei Leser auf demselben Ordner sind ein Startfehler: pruefe_verschieden().

Stanzer
  * --stanzer1 ist ein Ordner, die Datei heisst stanzer.ls. Sie wird angelegt, wenn sie beim ersten Stanzen nach dem
    Start fehlt, sonst FORTGESCHRIEBEN (angehaengt), nie ueberschrieben.

Standardannahmen dieser Datei (zur Abnahme, nicht ausdruecklich bestaetigt):
  (a) Die Datei wird verschoben, sobald das letzte Lochbild (die letzte nichtleere Zeile) geliefert wird, nicht erst beim
      naechsten Lesen. Sonst bliebe eine vollstaendig gelesene Datei nach Netz-Aus liegen und wuerde erneut gelesen.
      Schlaegt das Verschieben fehl, endet naechste() mit KonfigFehler und das letzte Lochbild wird nicht geliefert.
      Die Datei bleibt dann liegen und wird beim naechsten Start von vorn gelesen.
  (b) Fehlt der Leserordner oder ist der Pfad eine Datei, ist das erst beim Lesen ein KonfigFehler (wie im
      bisherigen Interpreter), nicht beim Start.
"""
import os
import re
import shutil
import time

from c8205_interp import KonfigFehler
from grafik_trommel import GrafikAbbruch

VERSION_GERAETE = 'G4-002'
KORB = 'LOCHSTREIFENKORB'
STANZER_DATEI = 'stanzer.ls'
_LOCHBILD = re.compile(r'[01]{8}')


def pruefe_verschieden(pfad1, pfad2):
    """Startfehler (KonfigFehler), wenn Leser 1 und Leser 2 auf denselben Ordner zeigen (Review F-11 (f))."""
    if pfad1 and pfad2:
        a, b = os.path.realpath(pfad1), os.path.realpath(pfad2)
        if a == b or (os.path.exists(a) and os.path.exists(b) and os.path.samefile(a, b)):
            raise KonfigFehler(f'--leser1 und --leser2 zeigen auf denselben Ordner: {pfad1}')


class GrafikLeser:
    def __init__(self, ordner, nr=1, aufruf_beim_warten=None, takt=0.05):
        self.ordner = ordner
        self.nr = nr
        self.aufruf_beim_warten = aufruf_beim_warten
        self.takt = takt
        self.datei = None            # Pfad der gerade geoeffneten Datei
        self.zeilen = None           # deren Lochbilder (nur nichtleere Zeilen)
        self.pos = 0
        self.wartet = False          # True solange der Leser auf eine Datei wartet (Stufe 2: Lesestatus am Pult)
        self._abbruch = False
        self.bei_halt = None         # HZ-001: Aufruf ohne Argument, wenn der Leser zu warten beginnt (E/A-Halt: keine Lochbanddatei)
        self.bei_weiter = None       # HZ-001: Aufruf ohne Argument, wenn er danach ein Zeichen liefert
        self.bei_zeichen = None      # Stufe 4 (S4-09): Aufruf ohne Argument bei jedem gelieferten Zeichen (Ton, Lesetempo); sonst None

    # --- Dateisuche -----------------------------------------------------------------------------------------------
    def _kandidaten(self):
        if not os.path.isdir(self.ordner):
            raise KonfigFehler(f'Leserordner nicht gefunden (oder keine Ordner): {self.ordner}')
        liste = []
        for name in os.listdir(self.ordner):
            p = os.path.join(self.ordner, name)
            if name.startswith('.') or not os.path.isfile(p):
                continue
            try:
                liste.append((os.stat(p).st_mtime_ns, name, p))
            except OSError:
                continue             # Datei verschwand zwischen Auflisten und Abfrage
        liste.sort()
        return [p for _, _, p in liste]

    def _oeffne_naechste(self):
        for p in self._kandidaten():
            try:
                with open(p, encoding='utf-8') as fh:
                    roh = [x.strip() for x in fh]
            except OSError:
                continue
            zeilen = [z for z in roh if z]
            for z in zeilen:
                if not _LOCHBILD.fullmatch(z):
                    raise KonfigFehler(f'Lochstreifen {p}: ungueltige Zeile {z!r}')
            self.datei, self.zeilen, self.pos = p, zeilen, 0
            return True
        return False

    def _in_den_korb(self):
        korb = os.path.join(self.ordner, KORB)
        try:
            os.makedirs(korb, exist_ok=True)
            shutil.move(self.datei, os.path.join(korb, os.path.basename(self.datei)))
        except OSError as e:
            raise KonfigFehler(f'Datei {self.datei} kann nicht nach {KORB} verschoben werden: {e}')
        self.datei, self.zeilen, self.pos = None, None, 0

    # --- Seite des Interpreters -----------------------------------------------------------------------------------
    def naechste(self):
        """Das naechste Lochbild (acht Zeichen 0/1). Wartet, bis eines da ist; liefert nie None."""
        try:
            while True:
                if self._abbruch:
                    raise GrafikAbbruch('Lochbandleser: Warten abgebrochen')
                if self.zeilen is None and not self._oeffne_naechste():
                    if not self.wartet and self.bei_halt is not None:
                        self.bei_halt()
                    self.wartet = True
                    time.sleep(self.takt)
                    if self.aufruf_beim_warten is not None:
                        self.aufruf_beim_warten()     # kann HUnterbrechung/Wiederaufsetzen ausloesen: Zustand bleibt heil
                    continue
                if self.wartet and self.bei_weiter is not None:
                    self.bei_weiter()
                self.wartet = False
                if self.pos >= len(self.zeilen):      # leere Datei: gleich weiter
                    self._in_den_korb()
                    continue
                z = self.zeilen[self.pos]
                if self.pos + 1 >= len(self.zeilen):  # letztes Lochbild: Datei ist damit komplett gelesen (Annahme a)
                    self._in_den_korb()
                else:
                    self.pos += 1
                if self.bei_zeichen is not None:
                    self.bei_zeichen()                    # genau ein Zeichen je Zugriff (S4-09); bremst nur so weit, wie das Lesetempo verlangt
                return z
        finally:
            self.wartet = False

    def abbrechen(self):
        self._abbruch = True


class GrafikStanzer:
    def __init__(self, ordner):
        self.ordner = ordner
        self.pfad = os.path.join(ordner, STANZER_DATEI)
        self.bei_zeichen = None      # Stufe 4 (S4-10): Aufruf ohne Argument nach jedem gestanzten Zeichen (Ton); sonst None

    def stanze(self, lb):
        if os.path.isfile(self.ordner):
            raise KonfigFehler(f'Lochbandstanzer 1: --stanzer1 muss ein Ordner sein, ist aber eine Datei: {self.ordner}')
        try:
            os.makedirs(self.ordner, exist_ok=True)
            with open(self.pfad, 'a', encoding='utf-8') as fh:      # immer anhaengen, nie ueberschreiben
                fh.write(format(lb, '08b') + '\n')
        except OSError as e:
            raise KonfigFehler(f'Lochbandstanzer 1: {self.pfad} nicht beschreibbar: {e}')
        if self.bei_zeichen is not None:
            self.bei_zeichen()
