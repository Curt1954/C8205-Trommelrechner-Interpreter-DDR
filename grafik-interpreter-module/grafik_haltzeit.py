# -*- coding: utf-8 -*-
"""
grafik_haltzeit.py - Zeitmessung Start -> Halt und Halt -> Halt fuer die Zeile "Haltzeit" des HW-Check-Fensters (--HWCHECK). Kein Tkinter.
Version: HZ-003 (19.10.2026; HZ-001 Wunsch des Projektinhabers; HZ-003: Anzeige zeigt nur die reine Rechnerzeit, ohne Wartezeit im Halt)

Gemessen wird die Zeit in Millisekunden
  * zwischen dem Start (Taste R wirkt) und dem folgenden Halt, und
  * zwischen zwei aufeinanderfolgenden Halts (Zeitpunkt des vorigen Halts bis Zeitpunkt dieses Halts; die Wartezeit im Halt zaehlt mit).
Als Halt zaehlt:
  'Stopp'    unbedingter oder bedingter Stopp, Halt wegen Ueberlauf (Rechner steht, m.halted wird True)
  'Fehler'   Fehler bei Eingabe (FE), Geraetefehler, Fehler im Knotenablauf (m.halted wird True)
  'E/A-Halt' der Rechner wartet an einem Eingabebefehl auf ein Zeichen (K0-Warteschlange) oder auf eine Lochbanddatei (Leser)
Nicht als Halt zaehlt die Taste H (Unterbrechung durch das Pult).
Zusaetzlich wird die reine Laufzeit gefuehrt (vom letzten Start oder von der letzten Fortsetzung nach einem E/A-Halt bis zum Halt):
Feld ms_lauf, im Debug-Log (Marke HALT) und fuer eine spaetere Anzeige; das Fenster zeigt die Zeit zwischen den Halts.

Faeden: start()/halt()/weiter() kommen aus dem Rechner-Thread, lesen() aus dem Fenster-Thread; der Stand wird als ein Tupel ersetzt.
"""
import threading
import time

from grafik_debuglog import log

VERSION_HALTZEIT = 'HZ-003'
NUR_LAUF = True        # HZ-003 (Projektinhaber 19.10.2026): die Anzeige nennt nur die reine Rechnerzeit seit Start bzw. Fortsetzung; False: Zeit zwischen den Halts mit Wartezeit (HZ-001)
STOPP, FEHLER, EA = 'Stopp', 'Fehler', 'E/A-Halt'
START = 'R'


def art_aus_grund(grund):
    """Art eines Halts (m.halted) aus dem Haltgrund: 'Fehler' oder 'Stopp'. Wird erst beim Lesen bestimmt, weil der Grund an manchen
    Stellen erst NACH dem Setzen von halted eingetragen wird."""
    g = (grund or '')
    if g.startswith('Fehler') or g.startswith('FEHLER') or 'Ueberlauf' in g:
        return FEHLER
    return STOPP


class HaltZeit:
    def __init__(self, zeit=time.monotonic):
        self.zeit = zeit
        self._lock = threading.Lock()
        self._bezug = None            # (Zeitpunkt, Name) des Starts R oder des letzten Halts
        self._lauf_ab = None          # Zeitpunkt des Starts bzw. der letzten Fortsetzung (der Rechner rechnet seitdem)
        self.stand = None             # (ms, von, bis, ms_lauf, nummer): der letzte Halt mit Bezug; bis None = Art noch aus m.halt_grund
        self.anzahl = 0
        self.grund_fn = None          # Aufruf ohne Argument: m.halt_grund (bestimmt die Art eines Halts 'None', siehe _aufloesen)

    def _aufloesen(self):
        """Die Art eines Halts, die beim Halt noch offen war (m.halted wurde gesetzt, der Grund steht erst danach), jetzt aus m.halt_grund bestimmen.
        Aufruf unter der Sperre. Beim Start (R) und beim Lesen ist der Grund des letzten Halts noch unveraendert."""
        offen_bezug = self._bezug is not None and self._bezug[1] is None
        offen_stand = self.stand is not None and (self.stand[1] is None or self.stand[2] is None)
        if not (offen_bezug or offen_stand):
            return
        try:
            art = art_aus_grund(self.grund_fn() if self.grund_fn is not None else '')
        except Exception:
            art = STOPP
        if offen_bezug:
            self._bezug = (self._bezug[0], art)
        if offen_stand:
            ms, von, bis, ms_lauf, nr = self.stand
            self.stand = (ms, von if von is not None else art, bis if bis is not None else art, ms_lauf, nr)

    def start(self):
        """Taste R wirkt: neuer Bezugspunkt."""
        t = self.zeit()
        with self._lock:
            self._aufloesen()
            self._bezug = (t, START)
            self._lauf_ab = t

    def weiter(self):
        """Der Rechner rechnet nach einem E/A-Halt weiter (Zeichen angenommen): Beginn der reinen Laufzeit."""
        t = self.zeit()
        with self._lock:
            self._lauf_ab = t

    def halt(self, art=None):
        """Ein Halt beginnt. art: 'Stopp' | 'Fehler' | 'E/A-Halt' | None (= aus m.halt_grund beim Lesen). Gibt die Millisekunden zurueck (None ohne Bezug)."""
        t = self.zeit()
        with self._lock:
            self._aufloesen()
            self.anzahl += 1
            bezug, lauf_ab = self._bezug, self._lauf_ab
            ms = ms_lauf = None
            if bezug is not None:
                ms = (t - bezug[0]) * 1000.0
                self.stand = (ms, bezug[1], art, (t - lauf_ab) * 1000.0 if lauf_ab is not None else None, self.anzahl)
                ms_lauf = self.stand[3]
            self._bezug = (t, art)        # None: die Art wird beim Lesen aus dem Haltgrund bestimmt; bis dahin Name None
            self._lauf_ab = None
            n = self.anzahl
        if ms is None:
            log('HALT', f'Halt {n} ({art}): ohne vorherigen Start, keine Zeit')
        else:
            log('HALT', f'Halt {n} ({art}): {ms:.1f} ms seit {bezug[1]}' + (f', Laufzeit {ms_lauf:.1f} ms' if ms_lauf is not None else ''))
        return ms

    def lesen(self):
        """Stand fuer die Anzeige: None (noch kein Halt mit Bezug) oder (ms, von, bis, ms_lauf, nummer) mit den Namen von/bis."""
        with self._lock:
            self._aufloesen()
            return self.stand


def zeile(stand, nur_lauf=None):
    """Anzeigetext: '    85.0 ms  E/A-Halt -> E/A-Halt'. HZ-003 (NUR_LAUF): die Millisekunden sind die reine Rechnerzeit seit dem Start bzw. seit der
    Fortsetzung nach einem E/A-Halt; die Wartezeit im Halt zaehlt nicht. Mit nur_lauf=False die Zeit zwischen den Halts mit Wartezeit (HZ-001).
    Ohne Messung '   ---.- ms'."""
    if stand is None:
        return '     ---.- ms'
    ms, von, bis = stand[0], stand[1], stand[2]
    lauf = stand[3] if len(stand) > 3 else None
    if (NUR_LAUF if nur_lauf is None else nur_lauf) and lauf is not None:
        ms = lauf
    return f'{ms:10.1f} ms  {von} -> {bis}'
