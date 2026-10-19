#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sw_ton.py - Geraeusche des Schreibwerks (SW) und des Lochstreifenlesers (LS) fuer den C 8205-Interpreter

Selbstaendiges Programm (nur Standardbibliothek) mit
  1. der Funktion  sw_ton(zeichen)  - Schreibwerk, spaeter in den Interpreter einbaubar,
  2. der Funktion  ls_ton()         - Lochstreifenleser, bei jedem Eingabe-Halt K1/K2 aufzurufen, und
  3. einem Testrahmen, der einen String bzw. ein Leser-Szenario als Tonfolge ausgibt.

Die Funktion
------------
    sw_ton(zeichen) -> float

  Uebergeben wird ein auszugebendes Zeichen im Sinne von R 300-Code, Tabelle 1
  (Kodetabellen.md), genau so, wie sw_zeichen() im Interpreter es liefert:
    - ein einzelnes Zeichen als str:   '\\t' (Ascii 9) = Tabulator,
                                       '\\n' (Ascii 10) = WRZL,
                                       '\\r' (Ascii 13) = WRZL bzw. WR  (beide: WRZL-Klang),
                                       jedes andere Zeichen = allgemeines Zeichen
    - ein Name in spitzen Klammern:    '<WRZL>', '<WR>', '<TAB>', '<Tabulator>' wie oben,
                                       jeder andere Name ('<Um. KB>', ...) = allgemeines Zeichen
    - der Ascii-Wert als int:          9 = TAB, 10 und 13 = WRZL, alles andere = Zeichen
  Es gibt drei Klangarten (Stand Stufe 4, 19.10.2026):
    WRZL     Wagenruecklauf: Schreibwerkzeit und Klang 360 ms (wrzl.wav)
    TAB      Tabulator: nur noch ein Klang, tab_400.wav, 400 ms, gleich fuer jeden Tabulatorweg
    ZEICHEN  allgemeines Zeichen: Schreibwerkzeit SCHREIBWERKZEIT_S = 80 ms, je Zeichen zufaellig
             um +-SCHREIBWERKZEIT_STREUUNG_S (10 ms) veraendert, also 70 bis 90 ms (gleichverteilt).
             Der Zeichenklang ist davon unabhaengig ZEICHENKLANG_S = 100 ms lang (die Dateien
             zeichen_*.wav dauern 120 ms und werden auf 100 ms gekuerzt, die letzten
             ZEICHEN_AUSBLENDUNG_S = 10 ms ausgeblendet). Der Ueberstand (Klang laenger als die
             Schreibwerkzeit) UEBERLAPPT mit dem Klang des naechsten Zeichens. Bei jedem Aufruf
             wird zufaellig einer von mehreren, leicht unterschiedlichen Anschlaegen gewaehlt
             (nie zweimal derselbe hintereinander).

  Die Funktion gibt den Klang aus und kehrt erst nach der Schreibwerkzeit zurueck
  (der Interpreter "steht" so lange). Rueckgabewert: die Schreibwerkzeit in Sekunden
  (0.0, wenn nichts ausgegeben wurde, z. B. bei leerem String).

  Schreibwerkzeit und Klanglaenge sind getrennt: Bei TAB und WRZL sind beide gleich (400 bzw.
  360 ms, Laenge der WAV-Datei), bei Zeichen ist die Schreibwerkzeit 70 bis 90 ms, der Klang 100 ms.
  Wer die Klaenge austauschen will, ersetzt nur die Dateien im Ordner sw_toene/ (zeichen_*.wav
  beliebig viele, tab_400.wav, wrzl.wav; alle im selben WAV-Format). tab_kurz.wav und tab_lang.wav
  liegen als Quelle von tab_400.wav dort, werden aber nicht mehr gespielt.
  In GRAFIK spielt grafik_schreibwerk.py dieselben Zeiten ueber den Mischer (tonmisch); dieses Programm
  bleibt der selbstaendige Testrahmen fuer die Klaenge.

Lochstreifenleser: ls_ton()
---------------------------
    ls_ton() -> float

  Wird bei jedem Eingabe-Halt (Kanal K1 = Leser 1 oder K2 = Leser 2) einmal aufgerufen, ohne Parameter.
  Bei 130 Zeichen/s (7,7 ms je Zeichen) waeren Einzeltoene nicht mehr unterscheidbar, deshalb richtet
  sich der Klang nach dem Abstand der Aufrufe (Schwelle LS_PAUSE_S = 100 ms):
    - erstes Zeichen nach mehr als 100 ms Pause   -> Einzelschritt (ca. 150 ms Geraeusch)
    - naechstes Zeichen innerhalb von 100 ms      -> Einzelschritt wird abgebrochen, das Dauergeraeusch
                                                     (nahtlose Schleife) laeuft endlos
    - danach mehr als 100 ms keine Eingabe        -> Dauergeraeusch endet (60 ms Auslaufen); das naechste
                                                     Zeichen ist wieder ein Einzelschritt
  Der Ton laeuft im Hintergrund und haelt den Interpreter nicht auf. Die Funktion verzoegert nur so weit,
  wie die Lesegeschwindigkeit es verlangt (7,7 ms je Zeichen; Rechenzeit des Interpreters zwischen zwei
  Aufrufen wird angerechnet). Ein Hintergrundfaden beendet das Dauergeraeusch nach der Pause.
  Klaenge: sw_toene/ls_einzel.wav, ls_dauer.wav (Schleifeneinheit), ls_ende.wav.
  Konstanten: LS_ZEICHEN_PRO_S (130), LS_PAUSE_S (0.100), LS_TEMPO (True), STUMM.

Einbau: in GRAFIK nicht ueber dieses Programm, sondern ueber grafik_schreibwerk.py (SwSenke, Mischer).

Testrahmen
----------
    python3 sw_ton.py "Hallo<TAB>Welt"        (Beispiel unten)
    python3 sw_ton.py "AB\\tCD\\r"
    python3 sw_ton.py --wav probe.wav "AB\\tCD\\r"     (nur in Datei rechnen, ohne Wiedergabe)

  Der String steht in Anfuehrungszeichen. Steuerzeichen koennen echt im String stehen
  oder als Escape geschrieben werden: \\t = TAB, \\r oder \\n = WRZL, \\\\ = Backslash
  (mit --roh werden keine Escapes ausgewertet). CR+LF direkt hintereinander zaehlt als
  ein WRZL. Jedes Zeichen wird der Reihe nach als Klang ausgegeben.

  Leser:    python3 sw_ton.py --ls "1 p300 1 p80 1 1 1 p500 100 p300 1"
            Szenario = Folge von Aufrufen von ls_ton(): n = n Zeichen im Lesertakt (130/s),
            n@ms = n Zeichen im Abstand ms, pms = Pause: naechstes Zeichen kommt ms nach dem letzten.
            Mit --wav DATEI wird die Tonfolge nur berechnet, sonst in Echtzeit gespielt.
            --pause MS aendert die Schwelle (Vorgabe 100).

  Optionen: --stumm  nur Zeiten, kein Ton            --seed N  Zufallsfolge festlegen
            --wav D  Tonfolge in WAV-Datei D (Klaenge ueberlappen wie in GRAFIK)
            --zeit MS      Schreibwerkzeit allgemeiner Zeichen in ms (80)
            --streuung MS  Schwankung der Schreibwerkzeit in ms (10; 0 = aus)
"""

import argparse
import atexit
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import wave

KLANGORDNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sw_toene')

STUMM = False                # True: nur warten, keinen Ton ausgeben
SCHREIBWERKZEIT_S = 0.080    # allgemeine Zeichen: Schreibwerkzeit (Stufe 4, S4-17)
SCHREIBWERKZEIT_STREUUNG_S = 0.010   # zufaellig je Zeichen +-10 ms, also 70 bis 90 ms (gleichverteilt; 0 = aus)
ZEICHENKLANG_S = 0.100       # Laenge des Zeichenklangs (S4-05); die Dateien (120 ms) werden gekuerzt
ZEICHEN_AUSBLENDUNG_S = 0.010  # letzte 10 ms des gekuerzten Zeichenklangs ausblenden
LS_ZEICHEN_PRO_S = 130       # Lesegeschwindigkeit des Lochstreifenlesers
LS_PAUSE_S = 0.100           # Eingabeabstand, ab dem es kein fortlaufendes Lesen mehr ist (s. ls_ton)
LS_TEMPO = True              # ls_ton haelt die Lesegeschwindigkeit ein (False: keine Verzoegerung)
LS_PROTOKOLL = None          # Liste (Zeit, Aktion) fuehren lassen, nur fuer den Testrahmen

_rng = random.Random()
_klaenge = None              # wird beim ersten Gebrauch geladen
_letztes_zeichen = None      # Index des zuletzt gewaehlten Zeichenklangs
_letzte_wahl = None          # (Klang, Dauer) des letzten Aufrufs, nur fuer die Anzeige im Testrahmen
_abspieler = None
_spin_s = 0.003             # letzte Sekunden vor dem Ziel aktiv warten (Windows ggf. mehr, s. _timer_genau)


# ---------------------------------------------------------------- Klaenge laden

class _Klang:
    def __init__(self, pfad):
        self.pfad = pfad
        self.name = os.path.splitext(os.path.basename(pfad))[0]
        with wave.open(pfad, 'rb') as w:
            self.format = (w.getnchannels(), w.getsampwidth(), w.getframerate())
            self.frames = w.readframes(w.getnframes())
            self.dauer = w.getnframes() / w.getframerate()


def _lade():
    global _klaenge
    if _klaenge is not None:
        return _klaenge
    if not os.path.isdir(KLANGORDNER):
        raise FileNotFoundError(f'Klangordner fehlt: {KLANGORDNER}')
    k = {'ZEICHEN': [], 'TAB': [], 'WRZL': []}
    for datei in sorted(os.listdir(KLANGORDNER)):
        if not datei.lower().endswith('.wav'):
            continue
        n = datei.lower()
        pfad = os.path.join(KLANGORDNER, datei)
        if n.startswith('zeichen'):
            k['ZEICHEN'].append(_Klang(pfad))
        elif n == 'tab_400.wav':
            k['TAB'].append(_Klang(pfad))
        elif n == 'wrzl.wav':
            k['WRZL'].append(_Klang(pfad))
    fehlt = [a for a, v in k.items() if not v]
    if fehlt:
        raise FileNotFoundError(f'Im Klangordner fehlen Klaenge: {", ".join(fehlt)} ({KLANGORDNER})')
    k['ZEICHEN'] = [_gekuerzt(kl) for kl in k['ZEICHEN']]
    formate = {kl.format for v in k.values() for kl in v}
    if len(formate) != 1:
        raise ValueError(f'Die WAV-Dateien muessen alle dasselbe Format haben, gefunden: {formate}')
    _klaenge = k
    return k


def _gekuerzt(klang):
    """Zeichenklang auf ZEICHENKLANG_S kuerzen, die letzten ZEICHEN_AUSBLENDUNG_S ausblenden (wie grafik_tonmisch.begrenze).
    Das Ergebnis liegt als temporaere WAV-Datei vor (der Abspieler braucht einen Pfad); klang.dauer ist die Klanglaenge."""
    import array
    kan, breite, rate = klang.format
    if breite != 2:
        return klang                                       # nur 16 bit wird gekuerzt (alle mitgelieferten Klaenge)
    n = min(len(klang.frames) // (kan * breite), round(ZEICHENKLANG_S * rate))
    roh = array.array('h')
    roh.frombytes(klang.frames[:n * kan * breite])
    if sys.byteorder == 'big':
        roh.byteswap()
    aus = min(n, round(ZEICHEN_AUSBLENDUNG_S * rate))
    for i in range(aus):                                   # lineares Ausblenden am Ende
        f = (aus - 1 - i) / aus
        for c in range(kan):
            j = (n - aus + i) * kan + c
            roh[j] = int(roh[j] * f)
    if sys.byteorder == 'big':
        roh.byteswap()
    pfad = os.path.join(_tempordner(), os.path.basename(klang.pfad))
    with wave.open(pfad, 'wb') as w:
        w.setnchannels(kan); w.setsampwidth(breite); w.setframerate(rate)
        w.writeframes(roh.tobytes())
    return _Klang(pfad)


_tempdir = None


def _tempordner():
    global _tempdir
    if _tempdir is None:
        _tempdir = tempfile.mkdtemp(prefix='sw_ton_')
        atexit.register(shutil.rmtree, _tempdir, True)
    return _tempdir


_ls_klaenge = None


def _lade_ls():
    """Laedt die drei Leserklaenge (Einzelschritt, Schleifeneinheit, Auslaufen)."""
    global _ls_klaenge
    if _ls_klaenge is None:
        k = {}
        for schluessel, name in (('LS_EINZEL', 'ls_einzel.wav'), ('LS_DAUER', 'ls_dauer.wav'),
                                 ('LS_ENDE', 'ls_ende.wav')):
            pfad = os.path.join(KLANGORDNER, name)
            if not os.path.isfile(pfad):
                raise FileNotFoundError(f'Leserklang fehlt: {pfad}')
            k[schluessel] = [_Klang(pfad)]
        if len({v[0].format for v in k.values()}) != 1:
            raise ValueError('Die Leserklaenge muessen alle dasselbe WAV-Format haben')
        _ls_klaenge = k
    return _ls_klaenge


# ------------------------------------------------------------ Zeichen -> Klangart

_NAMEN_WRZL = {'WRZL', 'WR', 'SATZMARKE'}
_NAMEN_TAB = {'TAB', 'TABULATOR'}


def klangart(zeichen):
    """'WRZL', 'TAB' oder 'ZEICHEN' fuer ein Zeichen nach Tabelle 1; None bei leerem String."""
    if isinstance(zeichen, int):
        if zeichen == 9:
            return 'TAB'
        if zeichen in (10, 13):
            return 'WRZL'
        return 'ZEICHEN'
    if zeichen == '':
        return None
    if len(zeichen) == 1:
        if zeichen == '\t':
            return 'TAB'
        if zeichen in ('\n', '\r'):
            return 'WRZL'
        return 'ZEICHEN'
    if len(zeichen) > 2 and zeichen[0] == '<' and zeichen[-1] == '>':
        name = re.sub(r'[\s.]', '', zeichen[1:-1]).upper()
        if name in _NAMEN_TAB:
            return 'TAB'
        if name in _NAMEN_WRZL:
            return 'WRZL'
        return 'ZEICHEN'
    raise ValueError(f'sw_ton erwartet genau ein Zeichen oder einen Namen in <>, nicht {zeichen!r}')


def _waehle(art):
    """Waehlt Klang und Schreibwerkzeit zur Klangart: (Klang, Schreibwerkzeit in s).

    ZEICHEN: Klang zufaellig (nie zweimal derselbe in Folge), Schreibwerkzeit SCHREIBWERKZEIT_S um zufaellig
    +-SCHREIBWERKZEIT_STREUUNG_S (gleichverteilt), unabhaengig von der Klanglaenge (100 ms).
    TAB und WRZL: Schreibwerkzeit = Dauer des Klangs (400 bzw. 360 ms)."""
    global _letztes_zeichen, _letzte_wahl
    k = _lade()
    if art == 'TAB':
        klang = k['TAB'][0]
        _letzte_wahl = (klang, klang.dauer)
    elif art == 'WRZL':
        klang = k['WRZL'][0]
        _letzte_wahl = (klang, klang.dauer)
    else:
        n = len(k['ZEICHEN'])
        i = _rng.randrange(n)
        if n > 1:
            while i == _letztes_zeichen:
                i = _rng.randrange(n)
        _letztes_zeichen = i
        klang = k['ZEICHEN'][i]
        _letzte_wahl = (klang, SCHREIBWERKZEIT_S + _rng.uniform(-SCHREIBWERKZEIT_STREUUNG_S, SCHREIBWERKZEIT_STREUUNG_S))
    return _letzte_wahl


# ------------------------------------------------------------------ Wiedergabe

class _Abspieler:
    """Startet eine WAV-Datei asynchron (Windows: winsound, sonst ein Kommandozeilenspieler)."""

    def __init__(self):
        self.winsound = None
        self.befehl = None
        self.prozesse = []
        self.ls_proc = None          # Linux/macOS: Prozess des laufenden Leserklangs
        self.ls_schleife = False
        self.ls_schleifenpfad = None
        if sys.platform == 'win32':
            import winsound
            self.winsound = winsound
            _timer_genau()
            return
        kandidaten = ([['afplay']] if sys.platform == 'darwin' else []) + [
            ['paplay'], ['pw-play'], ['aplay', '-q'], ['play', '-q'],
            ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet']]
        for c in kandidaten:
            if shutil.which(c[0]):
                self.befehl = c
                return
        print('sw_ton: kein Audio-Abspielprogramm gefunden (paplay/pw-play/aplay/play/ffplay/afplay) '
              '- es wird nur gewartet, ohne Ton.', file=sys.stderr)

    def spiele(self, pfad):
        if self.winsound:
            self.winsound.PlaySound(pfad, self.winsound.SND_FILENAME | self.winsound.SND_ASYNC)
        elif self.befehl:
            self.prozesse = [p for p in self.prozesse if p.poll() is None]   # beendete abraeumen
            self.prozesse.append(subprocess.Popen(
                self.befehl + [pfad], stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

    # --- Leserklaenge: Einzelschritt, endlose Schleife, Auslaufen
    def _starte(self, pfad):
        self.prozesse = [p for p in self.prozesse if p.poll() is None]
        p = subprocess.Popen(self.befehl + [pfad], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.prozesse.append(p)
        return p

    @staticmethod
    def _stoppe(p):
        if p is not None and p.poll() is None:
            try:
                p.terminate()
            except OSError:
                pass

    def ls_einzel(self, pfad):
        if self.winsound:
            self.spiele(pfad)                       # ersetzt, was gerade klingt
        elif self.befehl:
            alt = self.ls_proc
            self.ls_proc = self._starte(pfad)
            self._stoppe(alt)

    def ls_schleife_an(self, pfad):
        """Dauergeraeusch endlos wiederholen (Windows: SND_LOOP; sonst lange temporaere Datei)."""
        if self.winsound:
            ws = self.winsound
            ws.PlaySound(pfad, ws.SND_FILENAME | ws.SND_ASYNC | ws.SND_LOOP)
        elif self.befehl:
            alt = self.ls_proc
            self.ls_schleifenpfad = _schleifendatei(pfad)
            self.ls_proc = self._starte(self.ls_schleifenpfad)
            self.ls_schleife = True
            self._stoppe(alt)

    def ls_schleife_pruefen(self):
        """Linux/macOS: ist die lange Schleifendatei abgelaufen, sofort neu starten."""
        if self.ls_schleife and self.befehl and self.ls_proc is not None and self.ls_proc.poll() is not None:
            self.ls_proc = self._starte(self.ls_schleifenpfad)

    def ls_aus(self, pfad):
        """Dauergeraeusch beenden und kurz auslaufen lassen."""
        self.ls_schleife = False
        if self.winsound:
            self.winsound.PlaySound(pfad, self.winsound.SND_FILENAME | self.winsound.SND_ASYNC)
        elif self.befehl:
            alt = self.ls_proc
            self.ls_proc = self._starte(pfad)
            self._stoppe(alt)

    def alles_aus(self):
        self.ls_schleife = False
        if self.winsound:
            self.winsound.PlaySound(None, self.winsound.SND_PURGE)
        else:
            for p in self.prozesse:
                self._stoppe(p)


_schleifen_cache = {}


def _schleifendatei(pfad, sekunden=30.0):
    """Kommandozeilenspieler wiederholen nicht endlos: Schleifeneinheit mehrfach hintereinander in eine
    temporaere WAV-Datei (ca. 30 s) schreiben. Laeuft sie ab, startet ls_schleife_pruefen() sie neu."""
    if pfad not in _schleifen_cache:
        with wave.open(pfad, 'rb') as w:
            par = w.getparams()
            frames = w.readframes(w.getnframes())
        n = int(sekunden * par.framerate / par.nframes) + 1
        ordner = tempfile.mkdtemp(prefix='sw_ton_')
        atexit.register(shutil.rmtree, ordner, True)
        ziel = os.path.join(ordner, 'ls_dauer_lang.wav')
        with wave.open(ziel, 'wb') as w:
            w.setparams(par)
            w.writeframes(frames * n)
        _schleifen_cache[pfad] = ziel
    return _schleifen_cache[pfad]


def _timer_genau():
    """Windows: Systemtakt auf 1 ms stellen, damit time.sleep auch bei aelteren Python-/Windows-
    Versionen genau genug ist (Standard dort bis ca. 15 ms). Gelingt das nicht, wird stattdessen
    laenger aktiv gewartet. Auf anderen Systemen nichts zu tun."""
    global _spin_s
    try:
        import ctypes
        winmm = ctypes.windll.winmm
        if winmm.timeBeginPeriod(1) != 0:
            raise OSError('timeBeginPeriod fehlgeschlagen')
        atexit.register(winmm.timeEndPeriod, 1)
    except Exception:
        _spin_s = 0.018


def _warte_bis(ziel):
    """Wartet bis perf_counter() == ziel (grob schlafen, zuletzt kurz aktiv warten)."""
    while True:
        rest = ziel - time.perf_counter()
        if rest <= 0:
            return
        if rest > _spin_s + 0.001:
            time.sleep(rest - _spin_s)


# ------------------------------------------------------------------ Die Funktion

def sw_ton(zeichen):
    """Gibt das Schreibwerk-Geraeusch zu 'zeichen' aus und kehrt nach der Ausgabedauer zurueck.

    zeichen: str (ein Zeichen oder '<Name>') oder int (Ascii-Wert), siehe Modulkopf.
    Rueckgabe: Schreibwerkzeit in Sekunden (0.0 bei leerem String); der Klang kann laenger dauern (Zeichen: 100 ms)."""
    global _abspieler
    art = klangart(zeichen)
    if art is None:
        return 0.0
    klang, dauer = _waehle(art)
    start = time.perf_counter()
    if not STUMM:
        if _abspieler is None:
            _abspieler = _Abspieler()
        _abspieler.spiele(klang.pfad)
    _warte_bis(start + dauer)
    return dauer


# ------------------------------------------------------------------ Lochstreifenleser

class LsLogik:
    """Entscheidet, wann welcher Leserklang gilt. Reine Zeitlogik: keine Uhr, kein Ton.

    Zustaende: RUHE (nichts), EINZEL (ein Einzelschritt wurde gestartet), DAUER (Dauergeraeusch laeuft).
    Regel: Folgt eine Eingabe hoechstens 'pause' Sekunden nach der vorigen, ist es fortlaufendes Lesen,
    sonst ein Einzelschritt. Nach 'pause' ohne Eingabe endet das Dauergeraeusch.
    eingabe(t) und ablauf(t) liefern Aktionen als Liste von (Zeit, Name):
    'EINZEL', 'DAUER_AN', 'DAUER_AUS'."""

    def __init__(self, pause=None):
        self._pause = pause
        self.modus = 'RUHE'
        self.letzte = None

    @property
    def pause(self):
        return LS_PAUSE_S if self._pause is None else self._pause

    def ablauf(self, t):
        """Zeitablauf bis t beruecksichtigen (Pause ueberschritten?)."""
        aktionen = []
        if self.modus != 'RUHE' and t - self.letzte > self.pause:
            if self.modus == 'DAUER':
                aktionen.append((self.letzte + self.pause, 'DAUER_AUS'))
            self.modus = 'RUHE'
        return aktionen

    def eingabe(self, t):
        """Ein Zeichen wird zur Zeit t geliefert."""
        aktionen = self.ablauf(t)
        if self.modus == 'RUHE':
            aktionen.append((t, 'EINZEL'))
            self.modus = 'EINZEL'
        elif self.modus == 'EINZEL':
            aktionen.append((t, 'DAUER_AN'))
            self.modus = 'DAUER'
        self.letzte = t
        return aktionen


_ls = LsLogik()
_ls_cv = threading.Condition()       # schuetzt _ls und den Abspieler, weckt den Waechter
_ls_waechter = None
_ls_lieferung = -1e9                 # Zeitpunkt, zu dem das letzte Zeichen geliefert wurde


def _ls_ausfuehren(aktionen):
    """Aktionen hoerbar machen (Aufruf nur mit gehaltenem _ls_cv)."""
    global _abspieler
    k = _lade_ls()
    for _zeit, name in aktionen:
        if LS_PROTOKOLL is not None:
            LS_PROTOKOLL.append((time.perf_counter(), name))
        if STUMM:
            continue
        if _abspieler is None:
            _abspieler = _Abspieler()
        if name == 'EINZEL':
            _abspieler.ls_einzel(k['LS_EINZEL'][0].pfad)
        elif name == 'DAUER_AN':
            _abspieler.ls_schleife_an(k['LS_DAUER'][0].pfad)
        else:
            _abspieler.ls_aus(k['LS_ENDE'][0].pfad)


def _ls_wache():
    """Hintergrundfaden: beendet das Dauergeraeusch, wenn laenger als LS_PAUSE_S nichts mehr kommt."""
    while True:
        with _ls_cv:
            while _ls.modus != 'DAUER':
                _ls_cv.wait()
            rest = _ls.letzte + _ls.pause - time.perf_counter()
            if rest > 0:
                _ls_cv.wait(rest)               # wird von jeder neuen Eingabe geweckt
                continue
            _ls_ausfuehren(_ls.ablauf(time.perf_counter()))


def _ls_aufraeumen():
    with _ls_cv:
        _ls.modus = 'RUHE'
        if _abspieler is not None:
            _abspieler.alles_aus()


def ls_ton():
    """Geraeusch des Lochstreifenlesers; bei jedem Eingabe-Halt (Kanal 1 oder 2) aufrufen.

    Die Funktion haelt die Lesegeschwindigkeit ein (LS_ZEICHEN_PRO_S = 130 Zeichen/s, also 7,7 ms je
    Zeichen) und kehrt dann sofort zurueck. Der Ton wird im Hintergrund gespielt und haelt den Interpreter
    NICHT auf. Der Klang richtet sich nach dem Abstand der Eingaben (Schwelle LS_PAUSE_S, 100 ms):
      - erstes Zeichen nach mehr als LS_PAUSE_S Pause: Einzelschritt (ca. 150 ms Geraeusch)
      - zweites Zeichen innerhalb LS_PAUSE_S: Einzelschritt wird abgebrochen, Dauergeraeusch laeuft
        endlos, solange die Eingaben nicht laenger als LS_PAUSE_S aussetzen
      - bleibt eine Eingabe laenger als LS_PAUSE_S aus, endet das Dauergeraeusch (kurzes Auslaufen),
        das naechste Zeichen ist wieder ein Einzelschritt.
    Rueckgabe: die Verzoegerung dieses Aufrufs in Sekunden."""
    global _ls_lieferung, _ls_waechter
    _lade_ls()
    jetzt = time.perf_counter()
    ziel = jetzt
    if LS_TEMPO:
        # Der Leser liefert ein Zeichen fruehestens 1/130 s nach dem vorigen. Zeit, die der Interpreter
        # zwischen zwei Aufrufen selbst braucht, wird angerechnet und nicht zusaetzlich gewartet.
        ziel = max(jetzt, _ls_lieferung + 1.0 / LS_ZEICHEN_PRO_S)
    _ls_lieferung = ziel
    with _ls_cv:
        _ls_ausfuehren(_ls.eingabe(ziel))
        if _ls.modus == 'DAUER' and not STUMM and _abspieler is not None:
            _abspieler.ls_schleife_pruefen()
        if _ls_waechter is None:
            _ls_waechter = threading.Thread(target=_ls_wache, name='ls_wache', daemon=True)
            _ls_waechter.start()
            atexit.register(_ls_aufraeumen)
        _ls_cv.notify_all()
    _warte_bis(ziel)
    return max(0.0, ziel - jetzt)


def ls_render(zeiten, pause=None):
    """Rechnet Aufrufzeiten (Sekunden) von ls_ton() ohne Uhr und ohne Ton in eine Tonfolge um.

    Rueckgabe: (Samples als array('h'), Abtastrate, Aktionen [(Zeit, Name)], Lieferzeiten)."""
    from array import array
    k = _lade_ls()

    def daten(schluessel):
        a = array('h')
        a.frombytes(k[schluessel][0].frames)
        return a
    einzel, dauer, ende = daten('LS_EINZEL'), daten('LS_DAUER'), daten('LS_ENDE')
    rate = k['LS_EINZEL'][0].format[2]
    logik = LsLogik(pause)
    aktionen, lieferungen, lief = [], [], -1e9
    for s in zeiten:
        t = max(s, lief + 1.0 / LS_ZEICHEN_PRO_S) if LS_TEMPO else s
        lief = t
        lieferungen.append(t)
        aktionen += logik.eingabe(t)
    aktionen += logik.ablauf(lieferungen[-1] + logik.pause + 1.0)
    n = int((aktionen[-1][0] + 1.0) * rate)
    buf = [0] * n

    def misch(quelle, start, anzahl, ausblenden=0, wiederholen=False):
        for i in range(anzahl):
            j = (i % len(quelle)) if wiederholen else i
            if j >= len(quelle) or start + i >= n:
                break
            v = quelle[j]
            if ausblenden and anzahl - i <= ausblenden:
                v = v * (anzahl - i) // ausblenden
            buf[start + i] += v
    for idx, (t, name) in enumerate(aktionen):
        start = int(t * rate)
        folge = aktionen[idx + 1] if idx + 1 < len(aktionen) else None
        if name == 'EINZEL':
            anzahl = len(einzel)
            if folge and folge[1] == 'DAUER_AN':               # Einzelschritt wird vom Dauergeraeusch abgeloest
                anzahl = min(anzahl, max(1, int(folge[0] * rate) - start))
            misch(einzel, start, anzahl, ausblenden=int(0.003 * rate))
        elif name == 'DAUER_AN':
            aus = next((z for z, nm in aktionen[idx + 1:] if nm == 'DAUER_AUS'), t)
            misch(dauer, start, int(aus * rate) - start, wiederholen=True)
        else:
            misch(ende, start, len(ende))
    out = array('h', (max(-32767, min(32767, v)) for v in buf))
    return out, rate, aktionen, lieferungen


def ls_szenario(text):
    """Testszenario in Aufrufzeiten (Sekunden) umsetzen. Eintraege durch Leerzeichen oder Komma getrennt:
         n        n Zeichen im Lesertakt (130/s) hintereinander
         n@ms     n Zeichen im Abstand von ms Millisekunden (Interpreter braucht so lange je Zeichen)
         pms      Pause: das naechste Zeichen kommt ms Millisekunden nach dem letzten
       Beispiel: '1 p300 1 p80 1 1 1 p500 100 p300 1'"""
    zeiten, t, letzte = [], 0.0, 0.0
    for tok in text.replace(',', ' ').split():
        if tok[0] in 'pP':
            t = letzte + float(tok[1:]) / 1000.0
            continue
        n, _, iv = tok.partition('@')
        schritt = float(iv) / 1000.0 if iv else 1.0 / LS_ZEICHEN_PRO_S
        for _ in range(int(n)):
            zeiten.append(t)
            letzte = t
            t += schritt
    return zeiten


# ------------------------------------------------------------------- Testrahmen

def text_zu_zeichen(text, roh=False):
    """Zerlegt den Testtext in Zeichen. Escapes \\t \\r \\n \\\\ (ausser bei roh); CR+LF = ein WRZL."""
    if not roh:
        text = re.sub(r'\\([rnt\\])', lambda m: {'r': '\r', 'n': '\n', 't': '\t', '\\': '\\'}[m.group(1)], text)
    text = text.replace('\r\n', '\n').replace('\n\r', '\n')
    return list(text)


def _zeigen(nr, ch, art, klang, dauer):
    anzeige = {'\t': '\\t', '\n': 'WRZL(LF)', '\r': 'WRZL(CR)'}.get(ch, ch)
    print(f'{nr:4d}  {anzeige:<9} {art:<8} {klang.name:<11} {dauer * 1000:6.1f} ms')


def main(argv=None):
    global STUMM, SCHREIBWERKZEIT_S, SCHREIBWERKZEIT_STREUUNG_S
    ap = argparse.ArgumentParser(
        description='Testrahmen fuer sw_ton(): setzt einen String in eine Schreibwerk-Tonfolge um.')
    ap.add_argument('text', nargs='?', help='auszugebender String (in Anfuehrungszeichen); darf TAB und CR (= WRZL) enthalten')
    ap.add_argument('--ls', metavar='SZENARIO', help='statt eines Strings: Lochstreifenleser-Szenario, z. B. "1 p300 1 p80 1 1 1 p500 100" '
                    '(n = n Zeichen im Lesertakt, n@ms = n Zeichen im Abstand ms, pms = Pause bis zum naechsten Zeichen)')
    ap.add_argument('--pause', type=float, default=LS_PAUSE_S * 1000, metavar='MS',
                    help='Leser: Eingabeabstand in ms, ab dem es kein fortlaufendes Lesen mehr ist (Vorgabe 100)')
    ap.add_argument('--roh', action='store_true', help='keine Escapes (\\t \\r \\n) auswerten')
    ap.add_argument('--stumm', action='store_true', help='keinen Ton ausgeben, nur die Zeiten einhalten')
    ap.add_argument('--zeit', type=float, default=SCHREIBWERKZEIT_S * 1000, metavar='MS',
                    help='Schreibwerkzeit allgemeiner Zeichen in ms (Vorgabe 80)')
    ap.add_argument('--streuung', type=float, default=SCHREIBWERKZEIT_STREUUNG_S * 1000, metavar='MS',
                    help='zufaellige Schwankung der Schreibwerkzeit in ms (Vorgabe 10 = 70 bis 90 ms, 0 = aus)')
    ap.add_argument('--seed', type=int, help='Startwert der Zufallsauswahl (reproduzierbare Folge)')
    ap.add_argument('--wav', metavar='DATEI', help='Tonfolge nur in diese WAV-Datei schreiben (keine Wiedergabe, kein Warten)')
    a = ap.parse_args(argv)

    if a.seed is not None:
        _rng.seed(a.seed)
    if a.ls is not None:
        return _main_ls(a)
    if a.text is None:
        ap.error('Es fehlt der auszugebende String (oder --ls SZENARIO).')
    STUMM = a.stumm
    SCHREIBWERKZEIT_S = a.zeit / 1000.0
    SCHREIBWERKZEIT_STREUUNG_S = a.streuung / 1000.0
    zeichen = text_zu_zeichen(a.text, a.roh)
    if not zeichen:
        print('leerer String - nichts auszugeben')
        return 0

    print(' Nr  Zeichen   Art      Klang        Dauer')
    soll = 0.0
    if a.wav:
        import array
        fmt, t, stuecke = None, 0.0, []
        for nr, ch in enumerate(zeichen, 1):
            art = klangart(ch)
            klang, dauer = _waehle(art)
            _zeigen(nr, ch, art, klang, dauer)
            fmt = klang.format
            stuecke.append((t, klang))                           # Klang beginnt mit dem Zeichen, die Schreibwerkzeit schiebt den Beginn des naechsten
            t += dauer
            soll += dauer
        kan, breite, rate = fmt
        if breite != 2:
            raise ValueError('--wav mischt nur 16-bit-Klaenge')
        ende = max(round(st * rate) + len(kl.frames) // (kan * breite) for st, kl in stuecke)
        mix = [0] * (ende * kan)
        for st, kl in stuecke:                                   # ueberlappende Klaenge werden addiert (wie der Mischer in GRAFIK)
            roh = array.array('h'); roh.frombytes(kl.frames)
            if sys.byteorder == 'big':
                roh.byteswap()
            o = round(st * rate) * kan
            for i, v in enumerate(roh):
                mix[o + i] += v
        out = array.array('h', (max(-32768, min(32767, v)) for v in mix))
        if sys.byteorder == 'big':
            out.byteswap()
        with wave.open(a.wav, 'wb') as w:
            w.setnchannels(kan); w.setsampwidth(breite); w.setframerate(rate)
            w.writeframes(out.tobytes())
        print(f'\nTonfolge: {len(zeichen)} Zeichen, {soll:.3f} s  ->  {a.wav}')
        return 0

    t0 = time.perf_counter()
    for nr, ch in enumerate(zeichen, 1):
        art = klangart(ch)
        d = sw_ton(ch)                    # die Auswahl trifft sw_ton selbst
        soll += d
        _zeigen(nr, ch, art, _letzte_wahl[0], d)
    ist = time.perf_counter() - t0
    print(f'\nSollzeit {soll:.3f} s, gemessene Zeit {ist:.3f} s, {len(zeichen)} Zeichen')
    return 0


def _main_ls(a):
    """Testrahmen Lochstreifenleser: Szenario als Aufruffolge von ls_ton() abspielen oder in WAV rechnen."""
    global STUMM, LS_PAUSE_S, LS_PROTOKOLL
    STUMM = a.stumm
    LS_PAUSE_S = a.pause / 1000.0
    zeiten = ls_szenario(a.ls)
    if not zeiten:
        print('leeres Szenario - nichts auszugeben')
        return 0
    print(f'Leser {LS_ZEICHEN_PRO_S} Zeichen/s = {1000.0 / LS_ZEICHEN_PRO_S:.2f} ms je Zeichen, '
          f'Pause-Schwelle {LS_PAUSE_S * 1000:.0f} ms, {len(zeiten)} Aufrufe\n')
    print('   Zeit [s]  Aktion')
    if a.wav:
        buf, rate, aktionen, lief = ls_render(zeiten)
        for t, name in aktionen:
            print(f'  {t:8.3f}  {name}')
        with wave.open(a.wav, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
            w.writeframes(buf.tobytes())
        print(f'\n{len(zeiten)} Zeichen gelesen bis {lief[-1]:.3f} s, Tonfolge {len(buf) / rate:.3f} s  ->  {a.wav}')
        return 0
    LS_PROTOKOLL = []
    t0 = time.perf_counter()
    for s in zeiten:
        _warte_bis(t0 + s)
        ls_ton()
    ende_lesen = time.perf_counter() - t0
    _warte_bis(time.perf_counter() + LS_PAUSE_S * 1.3 + 0.2)       # Dauergeraeusch auslaufen lassen
    for t, name in LS_PROTOKOLL:
        print(f'  {t - t0:8.3f}  {name}')
    print(f'\n{len(zeiten)} Zeichen in {ende_lesen:.3f} s gelesen (Szenario-Sollzeit {zeiten[-1]:.3f} s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
