# -*- coding: utf-8 -*-
"""
grafik_ton.py - Rechnertoene fuer GRAFIK (vorgezogener Anfang von Stufe 4): fade_in (Hochlauf), Grundgeraeusch (Betrieb), fade_out (Ausschalten).
Version: G2-003. Nur Standardbibliothek. Schreibwerk, Leser und Stanzer folgen in Stufe 4 (Mischer: GRAFIK_Beschreibung §6 (alt: Dok. 03)).

Abspielen: Windows winsound (nur ein Klang gleichzeitig, also Grundgeraeusch und andere Toene noch NICHT gemischt); sonst ein
Kommandozeilenspieler (paplay, pw-play, aplay, play, ffplay), je Klang ein eigener Prozess. Ohne Spieler: Meldung auf stderr, kein Ton, kein Fehler.
Das Grundgeraeusch (5,94 s) laeuft als Endlosschleife aus einer zusammenkopierten 60-s-Datei (Neustart bei Ende; hoerbare Luecke
von einigen 10 ms beim Neustart moeglich).
"""
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import wave
import array

VERSION_TON = 'G2-003'
GRUND_PEGEL = 0.8       # Grundgeraeusch 20 % leiser (Projektinhaber 17.10.2026)
SPIELER = (['paplay'], ['pw-play'], ['aplay', '-q'], ['play', '-q'], ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet'])


def dauer(pfad):
    """Laenge einer WAV-Datei in Sekunden."""
    with wave.open(pfad) as w:
        return w.getnframes() / float(w.getframerate())


class NullTon:
    def fade_laeuft(self): return False
    def fade_in(self): pass
    def grund_an(self): pass
    def fade_out(self): pass
    def alles_aus(self): pass


class RechnerTon:
    def __init__(self, ordner, spieler=None, meldung=True):
        self.ordner = ordner
        self.befehl = None
        self.winsound = None
        self._proz = {}
        self._lock = threading.Lock()
        self._grund_laeuft = False
        self._tmp = None
        if spieler is not None:
            self.befehl = spieler
        elif os.name == 'nt':
            try:
                import winsound
                self.winsound = winsound
            except ImportError:
                pass
        else:
            for b in SPIELER:
                if shutil.which(b[0]):
                    self.befehl = b
                    break
        if self.befehl is None and self.winsound is None and meldung:
            print('Ton: kein Abspielprogramm gefunden (paplay, pw-play, aplay, play, ffplay) - Rechner laeuft ohne Ton.', file=sys.stderr)

    @property
    def verfuegbar(self):
        return self.befehl is not None or self.winsound is not None

    def dauer_fade_in(self):
        return dauer(self._pfad('netz_ein_fade_in.wav'))

    def dauer_fade_out(self):
        return dauer(self._pfad('netz_aus_fade_out.wav'))

    def fade_laeuft(self):
        """True, solange ein fade_in/fade_out noch abgespielt wird (nur mit Kommandozeilenspieler feststellbar; sonst False)."""
        with self._lock:
            p = self._proz.get('fade')
        return p is not None and p.poll() is None

    def _pfad(self, name):
        return os.path.join(self.ordner, name)

    def _spiele(self, schluessel, pfad):
        if self.winsound is not None:
            self.winsound.PlaySound(pfad, self.winsound.SND_FILENAME | self.winsound.SND_ASYNC)
            return None
        if self.befehl is None:
            return None
        try:
            p = subprocess.Popen(self.befehl + [pfad], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            return None
        with self._lock:
            self._proz[schluessel] = p
        return p

    def _stoppe(self, schluessel):
        with self._lock:
            p = self._proz.pop(schluessel, None)
        if p is not None and p.poll() is None:
            p.terminate()
            try:
                p.wait(0.5)
            except subprocess.TimeoutExpired:
                p.kill()

    def fade_in(self):
        self._spiele('fade', self._pfad('netz_ein_fade_in.wav'))

    def fade_out(self):
        """Beginnt mit dem Klick: fade_in bricht ab, das Grundgeraeusch endet (es laeuft immer nur einer der Klaenge)."""
        self._grund_laeuft = False
        self._stoppe('grund')
        self._stoppe('fade')
        self._spiele('fade', self._pfad('netz_aus_fade_out.wav'))

    def grund_an(self):
        if self._grund_laeuft or not self.verfuegbar:
            return
        self._grund_laeuft = True
        threading.Thread(target=self._schleife, name='grundgeraeusch', daemon=True).start()

    def _lang_datei(self):
        if self._tmp is None:
            self._tmp = tempfile.mkdtemp(prefix='c8205_ton_')
        ziel = os.path.join(self._tmp, 'grund_60s.wav')
        if not os.path.isfile(ziel):
            with wave.open(self._pfad('rechner_grundgeraeusch.wav')) as w:
                par, daten = w.getparams(), w.readframes(w.getnframes())
            if par.sampwidth == 2:                         # 16 bit: Pegel auf GRUND_PEGEL
                a = array.array('h')
                a.frombytes(daten)
                if sys.byteorder == 'big':
                    a.byteswap()
                a = array.array('h', (int(x * GRUND_PEGEL) for x in a))
                if sys.byteorder == 'big':
                    a.byteswap()
                daten = a.tobytes()
            with wave.open(ziel, 'wb') as o:
                o.setparams(par)
                for _ in range(10):
                    o.writeframes(daten)
        return ziel

    def _schleife(self):
        pfad = self._lang_datei()
        while self._grund_laeuft:
            if self.winsound is not None:
                self.winsound.PlaySound(pfad, self.winsound.SND_FILENAME | self.winsound.SND_ASYNC)
                for _ in range(600):
                    if not self._grund_laeuft:
                        return
                    time.sleep(0.1)
                continue
            p = self._spiele('grund', pfad)
            if p is None:
                return
            while self._grund_laeuft and p.poll() is None:
                time.sleep(0.05)

    def alles_aus(self):
        self._grund_laeuft = False
        self._stoppe('grund')
        self._stoppe('fade')
        if self.winsound is not None:
            self.winsound.PlaySound(None, self.winsound.SND_PURGE)
        if self._tmp:
            shutil.rmtree(self._tmp, ignore_errors=True)
            self._tmp = None
