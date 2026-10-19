# -*- coding: utf-8 -*-
"""
grafik_debuglog.py - Fehlersuch-Protokoll des Modus GRAFIK (Schalter --DEBUGLOG [DATEI]). Nur Standardbibliothek.
Version: DL-003
Schreibt zeitgestempelt (Sekunden seit Start, Threadname) in eine Textdatei, jede Zeile sofort geschrieben (auch bei Absturz lesbar):
  MAUS/TASTE/FOKUS  rohe Ereignisse des Fensters (Position, Umschalt, welches Element hat den Fokus, welches Ziel getroffen wurde)
  KLICK/TOKEN       Entscheidung der Pult-Steuerung und was an den Rechner weitergegeben wird
  RECHNER           Taste vorgemerkt, Ausfuehrung beginnt/endet, jeweils mit dem Rechnerzustand
  STATUS            jede Sekunde: Alter des letzten Fenster-Taktes, Rechner-Thread, Zustand
  WATCHDOG          steht der Fenster-Takt > 1,5 s oder haengt ein Einzelschritt > 3 s: Stacks aller Threads
  FEHLER/LANGSAM    Ausnahmen in Tk-Rueckrufen und im Takt; Takt/HW-Check-Aktualisierung > 0,15 s
Ohne --DEBUGLOG ist log() wirkungslos.

Klickspur (ab DL-002): Aufzeichnung und Wiedergabe der Pult-Bedienung (Schalter --AUFZEICHNUNG [DATEI], --WIEDERGABE [DATEI]).
  Aufzeichnung  schreibt jeden Klick auf eine Pult-Taste (auch die ohne Wirkung) und jedes Loslassen von E/M mit der Zeit seit dem
                ersten Ereignis in eine Textdatei (je Zeile sofort geschrieben). Mit --DEBUGLOG wird automatisch mitgeschrieben.
  Wiedergabe    liest die Datei und fuehrt die Ereignisse im selben zeitlichen Abstand wieder aus (Aufruf der PultSteuerung,
                also genau wie ein Mausklick, aber ohne Tk-Ereignis: Fokus und Trefferpruefung des Fensters sind nicht dabei).
                Nur im Debug-Modus (--WIEDERGABE schaltet --DEBUGLOG ein). Abweichungen der Wirkung gegen die Aufzeichnung stehen im Log.
Dateiformat (Textdatei, von Hand aenderbar; Zeilen mit # sind Kopf/Kommentar):
  # C8205-Klickspur 1
  0.000 klick NETZ wirkt=1
  12.431 klick E umschalt wirkt=1
  12.700 los E
  Ab DL-003 (RE-001): zusaetzliche Ereignisart "tipp <keysym>" = eine Taste der Computertastatur im SW-FENSTER (Tk-keysym, z. B. a, A, percent,
  Tab, Return, space, adiaeresis); das Format bleibt "C8205-Klickspur 1". Die Wiedergabe erzeugt dafuer ein echtes Tk-Tastenereignis im SW-Fenster
  (SwFenster.tipp_wiedergabe), das durch dieselbe Bindung <Key> laeuft wie eine echte Taste. Ohne SW-Fenster (kein tipper) wird die Zeile gemeldet.
"""
import faulthandler
import threading
import time
from datetime import datetime

VERSION_DEBUGLOG = 'DL-003'
FORMAT_KLICKSPUR = 'C8205-Klickspur 1'
_L = None


class _Log:
    def __init__(self, pfad):
        self.pfad = pfad
        self.f = open(pfad, 'w', encoding='utf-8', buffering=1)
        self.t0 = time.monotonic()
        self.sperre = threading.Lock()

    def zeile(self, kat, text):
        z = f'{time.monotonic() - self.t0:9.3f} [{threading.current_thread().name[:12]:12}] {kat:8} {text}\n'
        with self.sperre:
            self.f.write(z)
            self.f.flush()

    def threads(self):
        with self.sperre:
            faulthandler.dump_traceback(file=self.f, all_threads=True)
            self.f.flush()


def starten(pfad):
    global _L
    _L = _Log(pfad)
    return _L


def aktiv():
    return _L is not None


def log(kat, text=''):
    if _L is None:
        return
    try:
        _L.zeile(kat, str(text))
    except Exception:
        pass


def threads_ausgeben(grund):
    log('WATCHDOG', grund)
    if _L is not None:
        try:
            _L.threads()
        except Exception:
            pass


# ----------------------------------------------------------------------------------------------------------------------
# Klickspur: Aufzeichnung und Wiedergabe der Pult-Bedienung
# ----------------------------------------------------------------------------------------------------------------------
class Aufzeichnung:
    """Schreibt jeden Pult-Klick und jedes Loslassen von E/M in eine Textdatei (Zeit in Sekunden seit dem ersten Ereignis).
    Wird von PultSteuerung.klick() und .loslassen() aufgerufen (Attribut PultSteuerung.aufzeichnung); thread-sicher."""

    def __init__(self, pfad, kopf=None):
        self.pfad = pfad
        self.f = open(pfad, 'w', encoding='utf-8', buffering=1)
        self.sperre = threading.Lock()
        self.t0 = None
        self.anzahl = 0
        self.f.write(f'# {FORMAT_KLICKSPUR}\n# erzeugt: {datetime.now().isoformat(timespec="seconds")}\n')
        for k, v in (kopf or {}).items():
            self.f.write(f'# {k}: {v}\n')
        self.f.flush()

    def _zeile(self, jetzt, text):
        with self.sperre:
            if self.f is None:
                return
            if self.t0 is None:
                self.t0 = jetzt
            self.f.write(f'{max(0.0, jetzt - self.t0):9.3f} {text}\n')
            self.f.flush()
            self.anzahl += 1

    def klick(self, taste, jetzt, umschalt=False, wirkt=None):
        w = '?' if wirkt is None else int(bool(wirkt))
        self._zeile(jetzt, f'klick {taste}{" umschalt" if umschalt else ""} wirkt={w}')

    def loslassen(self, taste, jetzt):
        self._zeile(jetzt, f'los {taste}')

    def schliessen(self):
        with self.sperre:
            if self.f is not None:
                try:
                    self.f.close()
                finally:
                    self.f = None


def lade_klickspur(pfad):
    """Liest eine Klickspur. Rueckgabe (kopf: dict, ereignisse: Liste (t, art, taste, umschalt, wirkt)); wirkt ist True/False/None.
    Fehler (Datei fehlt, falsches Format, unlesbare Zeile) -> ValueError mit Zeilennummer."""
    kopf, ereignisse, letzte = {}, [], 0.0
    try:
        with open(pfad, encoding='utf-8') as f:
            zeilen = f.read().splitlines()
    except OSError as e:
        raise ValueError(f'Klickspur nicht lesbar: {pfad}: {e}')
    if not zeilen or zeilen[0].strip() != '# ' + FORMAT_KLICKSPUR:
        raise ValueError(f'{pfad}: keine Klickspur (erste Zeile muss "# {FORMAT_KLICKSPUR}" sein)')
    for nr, z in enumerate(zeilen, 1):
        z = z.strip()
        if not z:
            continue
        if z.startswith('#'):
            if ':' in z:
                k, v = z[1:].split(':', 1)
                kopf[k.strip()] = v.strip()
            continue
        teile = z.split()
        try:
            t, art = float(teile[0]), teile[1]
            if art == 'klick':
                taste, rest = teile[2], teile[3:]
                umschalt = 'umschalt' in rest
                wirkt = None
                for x in rest:
                    if x.startswith('wirkt='):
                        wirkt = {'1': True, '0': False}.get(x[6:])
                ereignisse.append((t, art, taste, umschalt, wirkt))
            elif art == 'los':
                ereignisse.append((t, art, teile[2], False, None))
            elif art == 'tipp':
                ereignisse.append((t, art, teile[2], False, None))
            else:
                raise ValueError('unbekannte Art ' + art)
        except (ValueError, IndexError) as e:
            raise ValueError(f'{pfad}, Zeile {nr}: nicht lesbar ({e}): {z!r}')
        if t < letzte:
            raise ValueError(f'{pfad}, Zeile {nr}: Zeit {t} liegt vor der vorigen Zeile ({letzte})')
        letzte = t
    return kopf, ereignisse


class Wiedergabe:
    """Spielt eine Klickspur an einer PultSteuerung ab: je Ereignis derselbe Aufruf wie beim Aufzeichnen (klick bzw. loslassen),
    im aufgezeichneten Zeitabstand. Nicht selbst getaktet: das Fenster (oder ein Test) ruft faellige(jetzt) auf und fragt mit
    bis_naechster(jetzt), wann der naechste Aufruf noetig ist."""

    def __init__(self, steuerung, ereignisse, tipper=None):
        self.s = steuerung
        self.tipper = tipper            # tipper(keysym) -> bool: Taste im SW-Fenster (Ereignisart tipp), gesetzt von c8205_grafik
        self.ev = list(ereignisse)
        self.i = 0
        self.t0 = None
        self.abweichungen = 0

    def starten(self, jetzt):
        self.t0 = jetzt
        log('WIEDERGABE', f'beginnt: {len(self.ev)} Ereignisse, Dauer {self.ev[-1][0] if self.ev else 0:.3f} s')

    @property
    def fertig(self):
        return self.i >= len(self.ev)

    def bis_naechster(self, jetzt):
        """Sekunden bis zum naechsten Ereignis (0, wenn es schon faellig ist); None, wenn alles abgespielt ist."""
        if self.fertig or self.t0 is None:
            return None
        return max(0.0, self.ev[self.i][0] - (jetzt - self.t0))

    def faellige(self, jetzt):
        """Fuehrt alle bis jetzt faelligen Ereignisse der Reihe nach aus. Rueckgabe: Anzahl."""
        n = 0
        while not self.fertig and self.ev[self.i][0] <= jetzt - self.t0 + 1e-9:
            t, art, taste, umschalt, wirkt = self.ev[self.i]
            self.i += 1
            n += 1
            if art == 'klick':
                ok = self.s.klick(taste, jetzt, umschalt=umschalt)
                abw = wirkt is not None and bool(ok) != wirkt
                if abw:
                    self.abweichungen += 1
                log('WIEDERGABE', f'{self.i}/{len(self.ev)} t={t:.3f} klick {taste}{" umschalt" if umschalt else ""}: '
                                  f'wirkt={int(bool(ok))} (aufgezeichnet {"?" if wirkt is None else int(wirkt)})'
                                  + (' ABWEICHUNG' if abw else ''))
            elif art == 'tipp':
                ok = self.tipper(taste) if self.tipper is not None else None
                log('WIEDERGABE', f'{self.i}/{len(self.ev)} t={t:.3f} tipp {taste}: '
                                  + ('kein SW-Fenster, Taste nicht gegeben' if ok is None else f'gegeben={int(bool(ok))}'))
            else:
                self.s.loslassen(taste, jetzt)
                log('WIEDERGABE', f'{self.i}/{len(self.ev)} t={t:.3f} los {taste}')
            if self.fertig:
                log('WIEDERGABE', f'Ende: {len(self.ev)} Ereignisse, {self.abweichungen} Abweichung(en) der Wirkung')
        return n
