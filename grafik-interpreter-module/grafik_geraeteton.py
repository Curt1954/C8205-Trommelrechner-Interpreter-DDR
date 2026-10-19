# -*- coding: utf-8 -*-
"""
grafik_geraeteton.py - Toene von Lochstreifenleser und Lochbandstanzer fuer GRAFIK (Stufe 4, GRAFIK_Beschreibung §6 (alt: Dok. 10) S4-09, S4-10).
Version: G4-002.  Nur Standardbibliothek.

Beides sind Zustandsautomaten mit ersetzbarer Uhr (`uhr`) und ersetzbarem Warten (`schlafe`), damit die Pruefungen ohne Audiogeraet
und ohne Echtzeit laufen.  Zeitgeber: tick() wird vom Mischer nach jedem Block (alle 10 ms) aufgerufen (mischer.takt_haken).

LeserTon (S4-09; ton/SW_Ton_Beschreibung.md Abschnitt 9):
  zeichen() bei jedem Zeichen, das ein Leser tatsaechlich liefert.  Lesetempo 130 Zeichen/s: ein Zeichen fruehestens 1/130 s nach dem
  vorigen (Rechenzeit wird angerechnet); die Tonlaenge verzoegert nichts.  Eine Schwelle LS_PAUSE_S = 100 ms:
    erstes Zeichen nach mehr als 100 ms Pause -> Einzelschritt (ls_einzel.wav, 148 ms);
    naechstes Zeichen hoechstens 100 ms spaeter -> Einzelschritt abgebrochen, Dauergeraeusch (ls_dauer.wav, Schleife);
    mehr als 100 ms ohne Zeichen waehrend Dauergeraeusch -> Ende mit 60 ms Auslaufen (ls_ende.wav); danach wieder Einzelschritt.

StanzerTon (S4-10; GRAFIK_Beschreibung §6 (alt: Dok. 03) Nr. 21, 23): Zustaende Aus / Geraeusch (ls_motor.wav, Schleife) / Dauerstanzen (ls_dauerstanzen.wav, Schleife);
  nie zwei Geraeusche zugleich.  Das erste Zeichen schaltet Aus -> Geraeusch.  Das zweite Zeichen mit weniger als 50 ms Abstand zum
  Vorgaenger schaltet auf Dauerstanzen; 50 ms nach dem letzten Zeichen faellt es auf Geraeusch zurueck; 5 s ohne Zeichen schalten ab.
  Bei gedrueckter Taste LS laeuft nur ls_motor.wav, dauernd (nie Dauerstanzen, nie abschalten).  Kein Einzelschritt-Ton.
  V (nicht gefragt): Beim Loesen von LS beginnt die 5-s-Frist neu.
  G4-003 (Antwort F-62 Nr. 4): Stanzertempo ungefaehr 50 Zeichen/s: ein Zeichen fruehestens 1/50 s nach dem vorigen (wie das Lesetempo des
  Lesers; Rechenzeit wird angerechnet, die Tonlaenge verzoegert nichts).  Ohne Ton (--STUMM) gilt das Tempo ebenso; im Modus TEST nicht.
"""
import threading
import time

import grafik_tonmisch as TM

VERSION_GERAETETON = 'G4-004'
LS_PAUSE_S = 0.100          # Schwelle des Lesers (S4-09), nach der Hoerpruefung nachzustellen (S4-16)
LESETEMPO = 130.0           # Zeichen je Sekunde
STANZTEMPO = 50.0           # Zeichen je Sekunde (Antwort F-62 Nr. 4: ungefaehr so; Mindestabstand 20 ms, Rechenzeit angerechnet)
STANZ_DAUER_S = 0.050       # Abstand zweier Zeichen, unter dem Dauerstanzen beginnt, und Frist bis zum Ende von Dauerstanzen (S4-10)
STANZ_AUS_S = 5.0           # Abschalten des Geraeuschs ohne Zeichen (S4-10)
PEGEL = 1.0

LS_EINZEL, LS_DAUER, LS_ENDE = 'ls_einzel.wav', 'ls_dauer.wav', 'ls_ende.wav'
ST_MOTOR, ST_DAUER = 'ls_motor.wav', 'ls_dauerstanzen.wav'


def lade_leserklaenge(ordner):
    import os
    sw = os.path.join(ordner, 'sw_toene')
    return {'einzel': TM.lade_klang(os.path.join(sw, LS_EINZEL)), 'dauer': TM.lade_klang(os.path.join(sw, LS_DAUER)),
            'ende': TM.lade_klang(os.path.join(sw, LS_ENDE))}


def lade_stanzerklaenge(ordner):
    import os
    d = os.path.join(ordner, 'toene_rechner_stanzer')
    return {'motor': TM.lade_klang(os.path.join(d, ST_MOTOR)), 'dauer': TM.lade_klang(os.path.join(d, ST_DAUER))}


class LeserTon:
    AUS, EINZEL, DAUER = 'aus', 'einzel', 'dauer'

    def __init__(self, mischer=None, klaenge=None, uhr=time.monotonic, schlafe=time.sleep, tempo=LESETEMPO, pegel=PEGEL):
        """tempo: Zeichen/s oder 0/None = kein Lesetempo (nur Ton).  pegel: Lautstaerke (--TON, Gruppe LL)."""
        self.mischer, self.k, self.uhr, self.schlafe, self.tempo, self.pegel = mischer, klaenge, uhr, schlafe, tempo, pegel
        self.zustand = self.AUS
        self._letzt = None
        self._lock = threading.Lock()
        self.verzoegerungen = []                # Wartezeiten des Lesetempos (Pruefungen; nur die letzten 200)

    def _mischer_ein(self, m):
        self.mischer = m
        m.takt_haken.append(self.tick)

    def zeichen(self):
        """Aufruf bei jedem gelieferten Zeichen.  Rueckgabe: die Verzoegerung dieses Aufrufs in Sekunden (Lesetempo)."""
        warte = 0.0
        if self.tempo and self._letzt is not None:
            frei = self._letzt + 1.0 / self.tempo
            warte = frei - self.uhr()
            if warte > 0:
                self.schlafe(warte)
            else:
                warte = 0.0
        self.verzoegerungen.append(warte)
        del self.verzoegerungen[:-200]
        with self._lock:
            t = self.uhr()
            self._tick(t)                       # ein abgelaufenes Dauergeraeusch zuerst beenden (der Zeitgeber kann noch nicht gelaufen sein)
            m = self.mischer
            if self._letzt is not None and t - self._letzt <= LS_PAUSE_S:
                if self.zustand != self.DAUER:
                    self.zustand = self.DAUER
                    if m is not None and self.k:
                        m.dauer_aus('ls_einzel')                            # Einzelschritt abbrechen
                        m.dauer_an('leser', 'ls_dauer', self.k['dauer'], self.pegel)
            else:
                self.zustand = self.EINZEL
                if m is not None and self.k:
                    m.einzel('leser', self.k['einzel'], self.pegel, 'ls_einzel')
            self._letzt = t
        return warte

    def _tick(self, t):
        if self._letzt is None or t - self._letzt <= LS_PAUSE_S:
            return
        if self.zustand == self.DAUER:
            m = self.mischer
            if m is not None and self.k:
                m.dauer_aus('ls_dauer')
                m.einzel('leser', self.k['ende'], self.pegel, 'ls_ende')         # 60 ms Auslaufen
        if self.zustand != self.AUS:
            self.zustand = self.AUS

    def tick(self):
        with self._lock:
            self._tick(self.uhr())

    def stop(self):
        with self._lock:
            self.zustand = self.AUS
            self._letzt = None


class StanzerTon:
    AUS, GERAEUSCH, DAUERSTANZEN = 'aus', 'geraeusch', 'dauerstanzen'

    def __init__(self, mischer=None, klaenge=None, uhr=time.monotonic, schlafe=time.sleep, tempo=STANZTEMPO, pegel=PEGEL):
        """tempo: Zeichen/s oder 0/None = kein Stanztempo (nur Ton).  pegel: Lautstaerke (--TON, Gruppe LS)."""
        self.mischer, self.k, self.uhr, self.schlafe, self.tempo, self.pegel = mischer, klaenge, uhr, schlafe, tempo, pegel
        self.zustand = self.AUS
        self.ls = False
        self._letzt = None
        self._letztes_zeichen = None            # Zeit des letzten gestanzten Zeichens (fuer das Stanztempo; LS loesen aendert sie nicht)
        self._lock = threading.Lock()
        self.verzoegerungen = []                # Wartezeiten des Stanztempos (Pruefungen; nur die letzten 200)

    def _mischer_ein(self, m):
        self.mischer = m
        m.takt_haken.append(self.tick)

    # --- Hilfen (unter Sperre) -----------------------------------------------------------------------------------
    def _motor(self):
        m = self.mischer
        if m is not None and self.k:
            m.dauer_aus('st_dauer')
            m.dauer_an('stanzer', 'st_motor', self.k['motor'], self.pegel)
        self.zustand = self.GERAEUSCH

    def _dauerstanzen(self):
        m = self.mischer
        if m is not None and self.k:
            m.dauer_aus('st_motor')
            m.dauer_an('stanzer', 'st_dauer', self.k['dauer'], self.pegel)
        self.zustand = self.DAUERSTANZEN

    def _aus(self):
        m = self.mischer
        if m is not None:
            m.dauer_aus('st_motor')
            m.dauer_aus('st_dauer')
        self.zustand = self.AUS

    # --- Ereignisse ------------------------------------------------------------------------------------------------
    def zeichen(self):
        """Aufruf bei jedem gestanzten Zeichen (nach dem Schreiben in die Datei).  Rueckgabe: die Verzoegerung in Sekunden (Stanztempo).
        Das Stanztempo bremst vor dem Zustandswechsel: das Zeichen zaehlt ab dem Ende der Wartezeit."""
        warte = 0.0
        if self.tempo and self._letztes_zeichen is not None:
            warte = self._letztes_zeichen + 1.0 / self.tempo - self.uhr()
            if warte > 0:
                self.schlafe(warte)
            else:
                warte = 0.0
        self.verzoegerungen.append(warte)
        del self.verzoegerungen[:-200]
        with self._lock:
            t = self.uhr()
            self._letztes_zeichen = t
            self._tick(t)
            if self.zustand == self.AUS:
                self._motor()
            elif (self.zustand == self.GERAEUSCH and not self.ls and self._letzt is not None
                  and t - self._letzt < STANZ_DAUER_S):
                self._dauerstanzen()                    # zweites Zeichen mit weniger als 50 ms Abstand
            self._letzt = t
        return warte

    def ls_taste(self, gedrueckt):
        """Selektor LS (einrastend): gedrueckt = Motor laeuft dauernd, nur ls_motor.wav."""
        with self._lock:
            t = self.uhr()
            self._tick(t)
            gedrueckt = bool(gedrueckt)
            if gedrueckt:
                self.ls = True
                if self.zustand != self.GERAEUSCH:
                    self._motor()
            else:
                self.ls = False
                self._letzt = t                         # V: die 5-s-Frist beginnt beim Loesen neu
                if self.zustand == self.AUS:
                    pass

    def _tick(self, t):
        if self._letzt is None:
            return
        if self.zustand == self.DAUERSTANZEN and t - self._letzt >= STANZ_DAUER_S:
            self._motor()                               # Zeitgeber: 50 ms nach dem letzten Zeichen zurueck zu Geraeusch
        if self.zustand == self.GERAEUSCH and not self.ls and t - self._letzt >= STANZ_AUS_S:
            self._aus()                                 # 5 s ohne Zeichen: abschalten

    def tick(self):
        with self._lock:
            self._tick(self.uhr())

    def stop(self):
        with self._lock:
            self._aus()
            self._letzt = None
            self._letztes_zeichen = None
