# -*- coding: utf-8 -*-
"""
grafik_geraeteton.py - Toene von Lochstreifenleser und Lochbandstanzer fuer GRAFIK (Stufe 4, GRAFIK_Beschreibung §6 (alt: Dok. 10) S4-09, S4-10).
Version: G4-005.  Nur Standardbibliothek.

Beides sind Zustandsautomaten mit ersetzbarer Uhr (`uhr`) und ersetzbarem Warten (`schlafe`), damit die Pruefungen ohne Audiogeraet
und ohne Echtzeit laufen.  Zeitgeber: tick() wird vom Mischer nach jedem Block (alle 10 ms) aufgerufen (mischer.takt_haken).

LeserTon (S4-09, neu G4-005 am 22.10.2026): zeichen() bei jedem Zeichen, das ein Leser tatsaechlich liefert (echtes Benutzen, nicht das Warten im Eingabe-Halt).
  Laeuft kein Ton: Einzelton (ls_einzel.wav, 148 ms), Befehlsschleife nach 1/10 s frei.  Laeuft er noch beim naechsten Zugriff: abgebrochen, Dauerton
  (ls_dauer.wav, Schleife) ab jetzt, Freigabe je Zeichen nach 1/130 s.  LS_AUS_S ohne Zugriff: Ton aus (60 ms Auslaufen, ls_ende.wav), Ablauf zurueck.

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

VERSION_GERAETETON = 'G4-005'
LS_PAUSE_S = 0.100          # (bis G4-004: Schwelle des Lesers; ab G4-005 ersetzt durch EINZEL_FREIGABE_S und LS_AUS_S)
EINZEL_FREIGABE_S = 0.100   # G4-005: Befehlsschleife nach dem Einzelton-Beginn nach 1/10 s wieder frei
LS_EINZEL_S = 0.148         # Laenge von ls_einzel.wav, wenn der Klang nicht bekannt ist
LS_AUS_S = 3.0              # G4-005: so lange ohne Zugriff auf den Leser -> Ton aus, Ablauf zurueckgesetzt (Wert geschaetzt, nachzustellen)
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
    """G4-005 (Wunsch des Projektinhabers 22.10.2026): Einzelton, Dauerton und Abschalten haengen am tatsaechlichen BENUTZEN des Lesers
    (zeichen() = ein Eingabebefehl hat ein Zeichen von K1/K2 geholt), nicht am Warten im Eingabe-Halt.
    Ablauf: Der erste Zugriff, wenn kein Ton laeuft, schaltet den Einzelton ein; er laeuft bis zu seinem Ende.  Parallel dazu wird die
    Befehlsschleife nach EINZEL_FREIGABE_S (1/10 s) wieder freigegeben.  Kommt dann ein neuer Zugriff und der Einzelton laeuft noch, wird er
    abgebrochen und durch den Dauerton ersetzt, der ab diesem Moment neu laeuft; die Befehlsschleife wird danach jeweils nach 1/130 s frei.
    Laeuft der Einzelton nicht mehr, beginnt wieder ein Einzelton.  Folgt LS_AUS_S lang kein Zugriff, geht der Ton aus (Dauerton mit 60 ms
    Auslaufen) und der Ablauf beginnt von vorn.  Die Freigabezeit wird vor dem naechsten Zugriff abgewartet; Rechenzeit dazwischen zaehlt mit."""
    AUS, EINZEL, DAUER = 'aus', 'einzel', 'dauer'

    def __init__(self, mischer=None, klaenge=None, uhr=time.monotonic, schlafe=time.sleep, tempo=LESETEMPO, pegel=PEGEL):
        """tempo: Zeichen/s oder 0/None = kein Lesetempo (nur Ton).  pegel: Lautstaerke (--TON, Gruppe LL)."""
        self.mischer, self.k, self.uhr, self.schlafe, self.tempo, self.pegel = mischer, klaenge, uhr, schlafe, tempo, pegel
        self.zustand = self.AUS
        self._letzt = None                      # Zeit des letzten Zugriffs (Beginn der Aus-Frist)
        self._frei = None                       # Zeitpunkt, ab dem die Befehlsschleife nach dem letzten Zugriff wieder frei ist
        self._einzel_ende = 0.0                 # Zeitpunkt, an dem der laufende Einzelton endet
        self._lock = threading.Lock()
        self.verzoegerungen = []                # Wartezeiten des Lesetempos (Pruefungen; nur die letzten 200)
        n = len(klaenge['einzel']) if klaenge else 0
        self.einzel_s = n / 44100.0 if n else LS_EINZEL_S

    def _mischer_ein(self, m):
        self.mischer = m
        m.takt_haken.append(self.tick)

    def zeichen(self):
        """Aufruf bei jedem Zeichen, das ein Leser tatsaechlich liefert.  Rueckgabe: die Verzoegerung dieses Aufrufs in Sekunden."""
        warte = 0.0
        if self.tempo and self._frei is not None:
            warte = self._frei - self.uhr()
            if warte > 0:
                self.schlafe(warte)             # die Befehlsschleife ist erst nach der Freigabezeit des vorigen Zugriffs wieder frei
            else:
                warte = 0.0
        self.verzoegerungen.append(warte)
        del self.verzoegerungen[:-200]
        with self._lock:
            t = self.uhr()
            self._tick(t)                       # eine abgelaufene Aus-Frist zuerst behandeln (der Zeitgeber kann noch nicht gelaufen sein)
            m = self.mischer
            if self.zustand == self.DAUER:
                frei = 1.0 / self.tempo if self.tempo else 0.0               # Dauerton laeuft weiter
            elif self.zustand == self.EINZEL and t < self._einzel_ende:
                self.zustand = self.DAUER                                    # Einzelton laeuft noch: abbrechen, Dauerton ab jetzt
                if m is not None and self.k:
                    m.dauer_aus('ls_einzel')
                    m.dauer_an('leser', 'ls_dauer', self.k['dauer'], self.pegel)
                frei = 1.0 / self.tempo if self.tempo else 0.0
            else:                                                            # kein Ton laeuft: Einzelton
                self.zustand = self.EINZEL
                self._einzel_ende = t + self.einzel_s
                if m is not None and self.k:
                    m.einzel('leser', self.k['einzel'], self.pegel, 'ls_einzel')
                frei = EINZEL_FREIGABE_S if self.tempo else 0.0
            self._letzt = t
            self._frei = t + frei
        return warte

    def _tick(self, t):
        """Aus-Frist: LS_AUS_S ohne Zugriff -> Ton aus, Ablauf zurueckgesetzt (Aufruf unter der Sperre)."""
        if self._letzt is None or t - self._letzt < LS_AUS_S:
            return
        if self.zustand == self.DAUER:
            m = self.mischer
            if m is not None and self.k:
                m.dauer_aus('ls_dauer')
                m.einzel('leser', self.k['ende'], self.pegel, 'ls_ende')         # 60 ms Auslaufen
        self.zustand = self.AUS
        self._letzt = None
        self._frei = None

    def tick(self):
        with self._lock:
            self._tick(self.uhr())

    def stop(self):
        with self._lock:
            m = self.mischer
            if m is not None:
                m.dauer_aus('ls_dauer'); m.dauer_aus('ls_einzel')
            self.zustand = self.AUS
            self._letzt = None
            self._frei = None


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
