# -*- coding: utf-8 -*-
"""
grafik_k0.py - Eingabewarteschlange des Kanals K0 im Modus GRAFIK (Stufe 1).

Ersetzt K0Quelle des Interpreters (Terminal oder Datei): In GRAFIK gibt es weder Terminal noch Datei als Quelle.
Es fuellen zwei Quellen die Warteschlange (GRAFIK_Beschreibung §11 (alt: Dok. 04 Abschnitt 2.4), Punkt 19):
  'T'  - Klicks im Bedienpult (Pult-Tastatur, Schalter T)
  'SW' - Eingabe im SW-Fenster (Schalter SW)
T kommt nur vom Pult, SW nur vom SW-Fenster; ein Zeichen der jeweils anderen Quelle wird ignoriert. Die Warteschlange
hat KEIN Ende: Der Rechner wartet im Eingabe-Halt unbegrenzt (nur Abbruch, Netz-Aus oder Fensterschliessen beenden das Warten).

Schnittstelle zum Interpreter (a032 in c8205_interp.py greift auf m.k0 zu):
  naechstes()  blockiert, bis ein Zeichen der gerade angewaehlten Quelle da ist; liefert das Token (ein Zeichen oder ein Name
               wie ZR, WM, IS, IB, TAB, WRZL - wie die Zeilen einer K0-Datei). Attribute tast und hinweis_gezeigt sind
               gesetzt, damit a032 nicht erlaubte Zeichen an T still ignoriert (kein Fehler, keine Terminalmeldung).
Schnittstelle zu den Fenstern:
  erwartet(quelle)           True, wenn der Rechner JETZT ein Zeichen dieser Quelle erwartet (Eingabe-Halt, K0, T bzw. SW)
  annehmen(quelle, token)    liefert das Zeichen, wenn es jetzt erwartet wird (True), sonst verworfen (False)
  einspeisen(token, quelle)  legt das Zeichen in Vorrat (fuer Pruefungen und fuer Vormerkung); quelle None = fuer jede Quelle
"""
import collections
import threading

from grafik_trommel import GrafikAbbruch
from grafik_debuglog import log


class K0Warteschlange:
    tast = True               # a032: nicht erlaubte Zeichen still ignorieren
    hinweis_gezeigt = True    # a032: kein Terminalhinweis (es gibt in GRAFIK kein Terminal als Quelle)

    def __init__(self, maschine=None, ende_wenn_leer=False, aufruf_beim_warten=None, takt=0.05):
        """maschine: die Machine (liefert fl['SW'], fl['T'] = angewaehlte Quelle). ende_wenn_leer: NUR fuer Pruefungen -
        ist der Vorrat leer, liefert naechstes() None (wie Dateiende einer K0-Datei) statt zu warten.
        aufruf_beim_warten: wird alle takt Sekunden im Wartezustand aufgerufen (Pult-Ereignisse, Abbruchpruefung)."""
        self.m = maschine
        self.ende_wenn_leer = ende_wenn_leer
        self.aufruf_beim_warten = aufruf_beim_warten
        self.takt = takt
        self._q = {'T': collections.deque(), 'SW': collections.deque(), None: collections.deque()}
        self._cv = threading.Condition()
        self._wartet_auf = None        # 'T' oder 'SW' solange der Interpreter im Eingabe-Halt wartet, sonst None
        self._abbruch = False
        self.bei_halt = None           # HZ-001: Aufruf ohne Argument, wenn der Rechner im Eingabebefehl zu warten beginnt (E/A-Halt, einmal je naechstes())
        self.bei_weiter = None         # HZ-001: Aufruf ohne Argument, wenn er danach ein Zeichen uebernimmt (rechnet weiter)

    # --- Seite des Interpreters ---------------------------------------------------------------------------------
    def _quelle(self):
        m = self.m
        return 'SW' if (m is not None and m.fl.get('SW')) else 'T'

    def naechstes(self):
        quelle = self._quelle()
        gewartet = False
        with self._cv:
            while True:
                if self._abbruch:
                    self._wartet_auf = None
                    raise GrafikAbbruch('K0-Eingabe abgebrochen')
                for q in (quelle, None):
                    if self._q[q]:
                        self._wartet_auf = None
                        tok = self._q[q].popleft()
                        log('K0', f'Rechner uebernimmt Token {tok!r} (Quelle {quelle})')
                        if gewartet and self.bei_weiter is not None:
                            self.bei_weiter()
                        return tok
                if self.ende_wenn_leer:
                    self._wartet_auf = None
                    return None
                if not gewartet:
                    gewartet = True
                    if self.bei_halt is not None:
                        self.bei_halt()
                self._wartet_auf = quelle
                self._cv.wait(self.takt)
                hook = self.aufruf_beim_warten
                if hook is not None:
                    self._cv.release()
                    try:
                        hook()
                    finally:
                        self._cv.acquire()
                # Wahl der Quelle kann sich durch ein Pult-Ereignis (Kanaltaste) geaendert haben
                neu = self._quelle()
                if neu != quelle:
                    quelle = neu
                    self._wartet_auf = None

    # --- Seite der Fenster -------------------------------------------------------------------------------------
    def erwartet(self, quelle):
        with self._cv:
            return self._wartet_auf == quelle

    def offen(self, quelle):
        """True, wenn ein 011 dieser Quelle aktiv ist UND noch kein Zeichen fuer ihn bereitliegt (ein 011 bekommt genau ein Zeichen)."""
        with self._cv:
            return self._wartet_auf == quelle and not self._q[quelle]

    def annehmen(self, quelle, token, nur_offen=False):
        """Ein Zeichen aus dem Pult (T) oder dem SW-Fenster (SW): nur angenommen, wenn der Rechner genau diese Quelle erwartet.
        nur_offen (SW-Fenster, G3-005): zusaetzlich nur, wenn fuer den aktiven 011 noch kein Zeichen bereitliegt; sonst waere ein Zeichen
        angezeigt, das den Rechner nicht erreicht (GRAFIK_Beschreibung §5 (alt: Dok. 09) S3-13, S3-14)."""
        with self._cv:
            if self._wartet_auf != quelle or (nur_offen and self._q[quelle]):
                return False
            self._q[quelle].append(token)
            self._cv.notify_all()
            return True

    def einspeisen(self, token, quelle=None):
        with self._cv:
            self._q[quelle].append(token)
            self._cv.notify_all()

    def leeren(self):
        with self._cv:
            for q in self._q.values():
                q.clear()

    def abbrechen(self):
        """Beendet ein laufendes oder kuenftiges Warten mit GrafikAbbruch."""
        with self._cv:
            self._abbruch = True
            self._cv.notify_all()
