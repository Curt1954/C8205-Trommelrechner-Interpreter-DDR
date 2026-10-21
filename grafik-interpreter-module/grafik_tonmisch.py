# -*- coding: utf-8 -*-
"""
grafik_tonmisch.py - Mischer fuer die Toene des Modus GRAFIK (Stufe 4, GRAFIK_Beschreibung §6 (alt: Dok. 10) S4-01 bis S4-03, S4-12).
Version: G4-004.  Nur Standardbibliothek.

STAND (G4-003): Der Mischer der Stufe 4 ist das C-Modul `tonmisch` (c-module/tonmisch.c, statisch in c8205_trommel eingebunden; Python-Huelle
grafik_tonmisch_c.CMischer).  DIESE Datei bleibt (a) als Rueckfall, wenn das Erweiterungsmodul nicht gebaut ist (c8205_grafik meldet das beim Start),
(b) als Bezug fuer die Pruefungen (grafik_tonmisch_c_tests: Block fuer Block gleiche Ausgabe wie das C-Modul) und (c) fuer Senken und
Hilfen (finde_spieler, lade_klang, begrenze), die beide Mischer benutzen.  Schnittstelle: einzel, dauer_an, dauer_pegel, dauer_aus, tor,
alles_aus, klingt_schluessel, starten, schliessen, bei_ausfall, takt_haken.  Windows (winmm) im C-Modul geschrieben, nicht uebersetzt, nicht getestet.

Aufbau: 44,1 kHz, mono, 16 bit, Bloecke zu 10 ms (441 Samples).  Ein Strom laeuft vom Start bis zum Ende dauernd (bei Ruhe Stille).
Einzelklaenge werden in den naechsten Block eingemischt (Beginn hoechstens ein Block = 10 ms nach dem Ereignis, plus Vorlauf der
Senke), sie ueberlappen sich (Summe, begrenzt auf 16 bit).  Dauergeraeusche sind Schleifen mit Pegel 0 bis 1.  Je Tonkanal
(rechner, schreibwerk, leser, stanzer) gibt es ein Tor; geschlossen = stumm, Einzelklaenge des Kanals werden verworfen.
"""
import array
import os
import shutil
import subprocess
import sys
import threading
import time
import wave

VERSION_TONMISCH = 'G4-004'
RATE = 44100
BLOCK = 441                      # 10 ms
VORLAUF_BLOECKE = 2              # der Erzeuger liegt hoechstens 2 Bloecke (20 ms) vor der Wiedergabe; G4-004 (Hoerpruefung 1: Ton kam zu spaet): vorher 3.
                                 # Hoechstens 3 (Ring aus 4 Bloecken, GRAFIK_Beschreibung §6 (alt: Dok. 03) Nr. 12, S4-03); mehr Vorlauf = sicherer gegen Knacken, weniger = frueher
KANAELE = ('rechner', 'schreibwerk', 'leser', 'stanzer')

SPIELER_LATENZ_MS = 20            # Puffer des Abspielprogramms (G4-004; vorher 40 ms, pw-cat Standard 100 ms). Zu klein: Knacken. Hier aendern, kein Neubau noetig.

# Abspielprogramme mit Roh-Audio (s16le, 44100 Hz, mono) ueber die Standardeingabe; Reihenfolge = Vorrang
SPIELER_ROH = (
    ['paplay', '--raw', '--rate=44100', '--channels=1', '--format=s16le', f'--latency-msec={SPIELER_LATENZ_MS}'],
    ['pw-cat', '--playback', '--raw', '--rate', '44100', '--channels', '1', '--format', 's16', '--latency', f'{SPIELER_LATENZ_MS}ms', '-'],
    ['aplay', '-q', '-t', 'raw', '-f', 'S16_LE', '-r', '44100', '-c', '1', f'--buffer-time={SPIELER_LATENZ_MS * 1000}'],
    ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', '-f', 's16le', '-ar', '44100', '-ac', '1', '-i', 'pipe:0'],
)


# --- Lautstaerke je Gruppe: --TON=pppp (G4-004, Hoerpruefung 1, 19.10.2026) -----------------------------------------------------------
# Vier Ziffern 0 bis 9 in der Reihenfolge Pult, SW, LL, LS (V: Reihenfolge vom Entwickler, Vorschlag des Projektinhabers):
#   Pult = Rechnertoene (fade_in, Grundgeraeusch, fade_out), SW = Schreibwerk (Tastenanschlag, auch angezeigte Eingabe),
#   LL = Lochstreifenleser, LS = Lochbandstanzer.  Ziffer 5 ist die Voreinstellung, 0 stumm; Faktor = BASIS * Ziffer / 5.
# BASIS: Pult, LL, LS 1,0 (Pegel der Hoerpruefung 1: "Lautstaerke gut"), SW 2,0 (Hoerpruefung 1: Tastenanschlag doppelt so laut).
# Hinweis: die Zeichenklaenge erreichen 0,4 des Vollausschlags; ab Faktor 2,5 (SW: Ziffer 6) uebersteuert ein einzelner Klick.
TON_STANDARD = '5555'
TON_BASIS = (1.0, 2.0, 1.3, 1.0)                  # Pult, SW, LL, LS; LL 1,3 statt 1,0: Hoerpruefung 19.10.2026 "Leser einen Tick lauter" (G4-012)
TON_NAMEN = ('Pult', 'SW', 'LL', 'LS')


def parse_ton(text):
    """'5555' -> (5, 5, 5, 5); sonst ValueError (genau vier Ziffern 0 bis 9)."""
    t = str(text).strip()
    if len(t) != 4 or not all(c in '0123456789' for c in t):
        raise ValueError(f'--TON erwartet vier Ziffern 0 bis 9 (Pult SW LL LS), z. B. --TON={TON_STANDARD}; gegeben: {text!r}')
    return tuple(int(c) for c in t)


def ton_faktoren(ziffern):
    """(Pult, SW, LL, LS) -> Faktoren (Pegel) je Gruppe."""
    return tuple(b * z / 5.0 for b, z in zip(TON_BASIS, ziffern))


class SenkeAusfall(Exception):
    """Die Senke (Abspielprogramm, Audiogeraet) ist ausgefallen."""


def finde_spieler(pfad=None):
    """Erstes vorhandene Abspielprogramm (Liste Befehl + Argumente) oder None.  pfad: Suchpfad (fuer Tests)."""
    for b in SPIELER_ROH:
        if shutil.which(b[0], path=pfad):
            return list(b)
    return None


def lade_klang(pfad):
    """WAV (mono, 16 bit, 44,1 kHz) als array('h'); andere Formate werden abgewiesen (kein stilles Umrechnen)."""
    with wave.open(pfad) as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, RATE):
            raise ValueError(f'{pfad}: erwartet mono, 16 bit, {RATE} Hz, gefunden {w.getnchannels()} Kanal, '
                             f'{8 * w.getsampwidth()} bit, {w.getframerate()} Hz')
        a = array.array('h')
        a.frombytes(w.readframes(w.getnframes()))
    if sys.byteorder == 'big':
        a.byteswap()
    return a


def begrenze(daten, ms, ausblendung_ms=10):
    """Klang auf hoechstens `ms` Millisekunden kuerzen; die letzten `ausblendung_ms` werden linear ausgeblendet (O4-8).
    Das Original bleibt unveraendert; ist der Klang kuerzer, kommt er unveraendert zurueck."""
    n = int(RATE * ms / 1000)
    if len(daten) <= n:
        return daten
    a = array.array('h', daten[:n])
    f = max(1, int(RATE * ausblendung_ms / 1000))
    for i in range(f):
        a[n - f + i] = int(a[n - f + i] * (1.0 - (i + 1) / f))
    return a


class _Stimme:
    __slots__ = ('daten', 'pos', 'pegel', 'kanal', 'schleife', 'schluessel')

    def __init__(self, daten, pegel, kanal, schleife=False, schluessel=None):
        self.daten, self.pos, self.pegel, self.kanal, self.schleife, self.schluessel = daten, 0, pegel, kanal, schleife, schluessel


class ListenSenke:
    """Ersatz-Senke fuer Tests und ohne Audiogeraet: sammelt die Bloecke."""
    def __init__(self):
        self.bloecke = []
    def schreibe(self, b):
        self.bloecke.append(b)
    def schliessen(self):
        pass


class ProzessSenke:
    """Senke: Abspielprogramm mit Roh-Audio ueber eine Roehre.  Bricht der Prozess weg, folgt SenkeAusfall."""
    def __init__(self, befehl):
        self.befehl = befehl
        try:
            self.p = subprocess.Popen(befehl, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as e:
            raise SenkeAusfall(f'{befehl[0]} nicht startbar: {e}')

    def schreibe(self, b):
        try:
            self.p.stdin.write(b)
            self.p.stdin.flush()
        except (BrokenPipeError, OSError, ValueError) as e:
            raise SenkeAusfall(f'{self.befehl[0]} beendet ({e.__class__.__name__})')
        if self.p.poll() is not None:
            raise SenkeAusfall(f'{self.befehl[0]} beendet (Code {self.p.returncode})')

    def schliessen(self):
        try:
            self.p.stdin.close()
        except Exception:
            pass
        try:
            self.p.terminate()
            self.p.wait(0.5)
        except Exception:
            try:
                self.p.kill()
            except Exception:
                pass


class Mischer:
    def __init__(self, senke=None, bei_ausfall=None):
        self.senke = senke
        self.bei_ausfall = bei_ausfall          # Aufruf mit dem Fehlertext, aus dem Mischer-Thread
        self._lock = threading.Lock()
        self._stimmen = []
        self._tor = {k: True for k in KANAELE}
        self._thread = None
        self._stop = threading.Event()
        self.ausfall = None                     # Text des Ausfalls, sonst None
        self.bloecke_gesendet = 0
        self.takt_haken = []                    # G4-002: Aufrufe ohne Argument nach jedem Block (Zeitgeber der Zustandsautomaten), im Mischer-Thread
        self.haken_fehler = []                  # Texte von Ausnahmen aus den Haken (der Strom laeuft trotzdem weiter)

    # --- Ereignisse -------------------------------------------------------------------------------------------
    def einzel(self, kanal, daten, pegel=1.0, schluessel=None):
        """Einzelklang: beginnt im naechsten Block; ueberlappt mit allem, was schon klingt.
        schluessel (G4-002): wahlfrei; mit dauer_aus(schluessel) laesst sich der Klang vorzeitig abbrechen (fade_in, Leser-Einzelschritt)."""
        with self._lock:
            if self._tor.get(kanal, True):
                self._stimmen.append(_Stimme(daten, pegel, kanal, False, schluessel))

    def dauer_an(self, kanal, schluessel, daten, pegel=1.0):
        """Dauergeraeusch als Schleife (je Schluessel eines; ein zweites mit demselben Schluessel ersetzt das erste)."""
        with self._lock:
            self._stimmen = [s for s in self._stimmen if s.schluessel != schluessel]
            if self._tor.get(kanal, True):                  # G4-003: Tor zu = stumm, auch fuer Schleifen (wie im C-Modul)
                self._stimmen.append(_Stimme(daten, pegel, kanal, True, schluessel))

    def dauer_pegel(self, schluessel, pegel):
        with self._lock:
            for s in self._stimmen:
                if s.schluessel == schluessel:
                    s.pegel = pegel

    def dauer_aus(self, schluessel):
        with self._lock:
            self._stimmen = [s for s in self._stimmen if s.schluessel != schluessel]

    def tor(self, kanal, offen):
        with self._lock:
            self._tor[kanal] = bool(offen)
            if not offen:
                self._stimmen = [s for s in self._stimmen if s.kanal != kanal]

    def alles_aus(self):
        """Alle Toene sofort aus (Strg+C, X, Fenster schliessen): Stimmen verwerfen, Tore bleiben."""
        with self._lock:
            self._stimmen = []

    def klingt(self):
        with self._lock:
            return len(self._stimmen)

    def klingt_schluessel(self, schluessel):
        """Anzahl der Stimmen (Einzelklaenge und Schleifen) mit diesem Schluessel (G4-002)."""
        with self._lock:
            return sum(1 for s in self._stimmen if s.schluessel == schluessel)

    # --- Mischen -----------------------------------------------------------------------------------------------
    def block(self):
        """Ein Block zu 10 ms (bytes, 882 Byte, little endian)."""
        acc = [0] * BLOCK
        with self._lock:
            rest = []
            for s in self._stimmen:
                d, p = s.daten, s.pos
                if s.schleife:
                    n = len(d)
                    if n == 0:
                        continue
                    seg = [d[(s.pos + i) % n] for i in range(BLOCK)]
                    s.pos = (s.pos + BLOCK) % n
                    rest.append(s)
                else:
                    seg = d[p:p + BLOCK]
                    s.pos = p + BLOCK
                    if s.pos < len(d):
                        rest.append(s)
                g = s.pegel
                if g == 1.0:
                    for i, v in enumerate(seg):
                        acc[i] += v
                elif g > 0.0:
                    for i, v in enumerate(seg):
                        acc[i] += int(v * g)
            self._stimmen = rest
        a = array.array('h', [32767 if v > 32767 else (-32768 if v < -32768 else v) for v in acc])
        if sys.byteorder == 'big':
            a.byteswap()
        return a.tobytes()

    # --- Strom -------------------------------------------------------------------------------------------------
    def haken_aufrufen(self):
        for h in list(self.takt_haken):
            try:
                h()
            except Exception as e:              # ein Fehler im Zeitgeber darf den Tonstrom nicht beenden
                self.haken_fehler.append(f'{e.__class__.__name__}: {e}')
                del self.haken_fehler[:-20]

    def starten(self):
        """Thread starten: erzeugt dauernd Bloecke (bei Ruhe Stille) und liefert sie an die Senke, im Takt der Uhr."""
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._lauf, name='tonmisch', daemon=True)
        self._thread.start()

    def _lauf(self):
        t0 = time.monotonic()
        n = 0
        try:
            while not self._stop.is_set():
                self.senke.schreibe(self.block())
                n += 1
                self.bloecke_gesendet = n
                self.haken_aufrufen()
                # nie weiter als VORLAUF_BLOECKE vor der Uhr (Ring, Verzoegerung <= 50 ms, S4-03)
                warte = t0 + (n - VORLAUF_BLOECKE) * BLOCK / RATE - time.monotonic()
                if warte > 0:
                    self._stop.wait(warte)
        except SenkeAusfall as e:
            self.ausfall = str(e)
            if self.bei_ausfall is not None and not self._stop.is_set():
                self.bei_ausfall(self.ausfall)
        except Exception as e:                  # jeder andere Fehler im Strom gilt ebenso als Ausfall
            self.ausfall = f'{e.__class__.__name__}: {e}'
            if self.bei_ausfall is not None and not self._stop.is_set():
                self.bei_ausfall(self.ausfall)

    def schliessen(self):
        self._stop.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(1.0)
        if self.senke is not None:
            self.senke.schliessen()
