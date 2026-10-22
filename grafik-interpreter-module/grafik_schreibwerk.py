# -*- coding: utf-8 -*-
"""
grafik_schreibwerk.py - Schreibwerkzeit und Klangwahl des Schreibwerks fuer GRAFIK (Stufe 4, GRAFIK_Beschreibung §6 (alt: Dok. 10) S4-05 bis S4-08, S4-17).
Version: G4-004.  Nur Standardbibliothek.
G4-004 (22.10.2026, Projektinhaber: 'bei gedrueckt gehaltenem Selektor SW geht die Ausgabe verloren, muss aber nach dem Loesen wieder beginnen'): Selektor SW
unterdrueckt Anzeige und Klang, NICHT mehr die Schreibwerkzeit: ausgabe(text, stumm=True) laesst das Schreibwerk je Zeichen still durchlaufen (gleiche
Zeiten, gleiches Warten als E/A-Halt). Sonst waere der Rest eines laufenden Textes in Millisekunden verbraucht und beim Loesen nichts mehr da.
Schalter SELEKTOR_MIT_ZEIT = False stellt das alte Verhalten (G4-003: keine Schreibwerkzeit) wieder her.
G4-003 (22.10.2026, Projektinhaber): Die Befehlsschleife wartet NICHT, bis das Schreibwerk mit dem Zeichen fertig ist. ausgabe() stoesst Klang und
Zeichen an, merkt sich 'frei ab' (Uhr + Schreibwerkzeit) und kehrt sofort zurueck. Erst der naechste Ausgabebefehl (auch das naechste Zeichen
eines Textes) wartet, falls das Schreibwerk noch nicht frei ist, genau bis 'frei ab'. Dieses Warten ist ein E/A-Halt (Haken bei_halt/bei_weiter,
wie bei K0 und Leser): es zaehlt nicht zur Rechnerzeit der Haltzeit-Zeile.

Entschieden (Projektinhaber 18.10.2026):
  * Schreibwerkzeit je ausgegebenem Zeichen im Mittel 82,5 ms, zufaellig 75 bis 90 ms (gleichverteilt), unabhaengig von der Tonlaenge (O4-1).
    Geaendert 22.10.2026 (Projektinhaber, G4-003): vorher 70 bis 90 ms; 'namen_raten' lief merklich zu schnell.
  * Zeichenklang 100 ms: die Dateien zeichen_*.wav (120 ms) bleiben unveraendert, bei der Wiedergabe auf 100 ms begrenzt (O4-8);
    der Ueberstand ueber die Schreibwerkzeit hinaus UEBERLAPPT mit dem naechsten Zeichen (O4-7).
  * TAB 400 ms und WRZL 360 ms gelten als Schreibwerkzeit; die Schreibwerkzeit gilt auch bei --STUMM, im Modus TEST nicht (O4-9).
  * WR (Wagenruecklauf ohne Zeilenschaltung, kommt als <WR>): eigener Klang wr.wav = die ersten 120 ms des WRZL-Klangs, vor dem markanten
    Ton; Klang und Schreibwerkzeit je 120 ms (Entscheidung des Projektinhabers 21.10.2026, OP-42; Erzeugung: ton/erzeuge_wr_klang.py).
  * Selektor SW (unterdruecken): keine Ausgabe, kein Klang; er wirkt NUR auf die Ausgabe (O4-3, O4-10). Seit G4-004 laeuft die Schreibwerkzeit still weiter.
  * Angezeigte Eingabe: derselbe Klang, KEINE Schreibwerkzeit, keine Sperre; Umschaltzeichen nie (O4-2, O4-3, O4-6).
  * Ein Schreibwerk: eine Folge, nie zweimal derselbe Zeichenklang hintereinander, fuer Ausgabe und Eingabe gemeinsam (S4-05).
Zeitgeber, Zufall und Klaenge sind ersetzbar (schlafe, zufall, mischer), damit die Pruefungen ohne Audiogeraet und ohne Echtzeit laufen.
"""
import glob
import os
import random
import time

import grafik_tonmisch as TM

VERSION_SCHREIBWERK = 'G4-004'
SELEKTOR_MIT_ZEIT = True                    # G4-004: Selektor SW unterdrueckt nur Anzeige und Klang, die Schreibwerkzeit laeuft weiter
SCHREIBWERKZEIT_MS = 82.5                   # Mittel (G4-003: 75 bis 90 ms, vorher 70 bis 90 ms)
SCHREIBWERKZEIT_STREUUNG_MS = 7.5           # 75 bis 90 ms
ZEICHENKLANG_MS = 100.0
ZEICHEN_AUSBLENDUNG_MS = 10.0               # Konstante fuer die Hoerpruefung (S4-16)
TAB_MS = 400.0
WRZL_MS = 360.0
WR_MS = 120.0                               # G4-002 (OP-42): Klang und Schreibwerkzeit fuer WR
PEGEL = 2.0                                 # G4-004: doppelt so laut wie vorher (Hoerpruefung 1); --TON stellt je Gruppe nach (grafik_tonmisch.TON_BASIS)


def _art(s):
    """Klangart eines Aufrufs: 'tab', 'wrzl', 'wr' oder 'zeichen' (ZR und die uebrigen benannten Zeichen <Name> klingen wie jedes Zeichen)."""
    if s == '\t':
        return 'tab'
    if s == '\n':
        return 'wrzl'
    if s == '<WR>':
        return 'wr'
    return 'zeichen'


def zeichen_aus_text(text):
    """Zerlegt Schreibwerk-Text in Zeichen; ein benanntes Zeichen <Name> ist ein Zeichen (GRAFIK_Beschreibung §5 (alt: Dok. 09) S3-04)."""
    i, n = 0, len(text)
    while i < n:
        if text[i] == '<':
            j = text.find('>', i)
            if j > i:
                yield text[i:j + 1]
                i = j + 1
                continue
        yield text[i]
        i += 1


class Schreibwerk:
    def __init__(self, mischer=None, klaenge=None, schlafe=time.sleep, zufall=None, uhr=time.monotonic):
        """mischer: grafik_tonmisch.Mischer oder None (--STUMM: keine Toene, die Schreibwerkzeit bleibt).
        klaenge: Wörterbuch {'zeichen': [array,...], 'tab': array, 'wrzl': array, 'wr': array}; sonst aus dem Ordner (laden())."""
        self.mischer = mischer
        self.pegel = PEGEL                      # --TON (Gruppe SW) setzt ihn von aussen
        self.schlafe = schlafe
        self.uhr = uhr                          # G4-003: ersetzbar (Pruefungen)
        self.frei_ab = 0.0                      # G4-003: Uhrzeit, ab der das Schreibwerk das letzte Zeichen fertig hat
        self.bei_halt = None                    # G4-003: Aufruf ohne Argument, wenn der Rechner auf das Schreibwerk zu warten beginnt (E/A-Halt)
        self.bei_weiter = None                  # G4-003: Aufruf ohne Argument, wenn das Schreibwerk frei ist und der Rechner weiterrechnet
        self.zufall = zufall if zufall is not None else random.Random()
        self.zeichen_klaenge = []
        self.tab = None
        self.wrzl = None
        self.wr = None
        self._letzter = None                    # Index des letzten Zeichenklangs (nie zweimal derselbe)
        if klaenge:
            self.zeichen_klaenge = [TM.begrenze(k, ZEICHENKLANG_MS, ZEICHEN_AUSBLENDUNG_MS) for k in klaenge['zeichen']]
            self.tab, self.wrzl, self.wr = klaenge.get('tab'), klaenge.get('wrzl'), klaenge.get('wr')
        self.letzte_zeiten = []                 # Schreibwerkzeiten in Sekunden (fuer Pruefungen; nur die letzten 200)

    @classmethod
    def laden(cls, ordner, mischer, **kw):
        sw = os.path.join(ordner, 'sw_toene')
        zeichen = [TM.lade_klang(p) for p in sorted(glob.glob(os.path.join(sw, 'zeichen_*.wav')))]
        if not zeichen:
            raise FileNotFoundError(f'keine zeichen_*.wav in {sw}')
        k = {'zeichen': zeichen, 'tab': TM.lade_klang(os.path.join(sw, 'tab_400.wav')), 'wrzl': TM.lade_klang(os.path.join(sw, 'wrzl.wav')),
             'wr': TM.lade_klang(os.path.join(sw, 'wr.wav'))}
        return cls(mischer, k, **kw)

    # --- Klangwahl -----------------------------------------------------------------------------------------------
    def _zeichenklang(self):
        n = len(self.zeichen_klaenge)
        if n == 0:
            return None
        if n == 1:
            i = 0
        else:
            i = self.zufall.randrange(n - 1)
            if self._letzter is not None and i >= self._letzter:
                i += 1                           # den letzten ausnehmen: nie zweimal derselbe
        self._letzter = i
        return self.zeichen_klaenge[i]

    def _klang(self, art):
        if art == 'tab':
            return self.tab
        if art == 'wrzl':
            return self.wrzl
        if art == 'wr':
            return self.wr
        return self._zeichenklang()

    def _spiele(self, art):
        k = self._klang(art)
        if self.mischer is not None and k is not None:
            self.mischer.einzel('schreibwerk', k, self.pegel)

    # --- Ausgabe des Rechners ------------------------------------------------------------------------------------
    def zeit(self, art):
        """Schreibwerkzeit in Sekunden: Zeichen 75 bis 90 ms, TAB 400 ms, WRZL 360 ms, WR 120 ms (O4-1, O4-9, OP-42)."""
        if art == 'tab':
            return TAB_MS / 1000.0
        if art == 'wrzl':
            return WRZL_MS / 1000.0
        if art == 'wr':
            return WR_MS / 1000.0
        return self.zufall.uniform(SCHREIBWERKZEIT_MS - SCHREIBWERKZEIT_STREUUNG_MS,
                                   SCHREIBWERKZEIT_MS + SCHREIBWERKZEIT_STREUUNG_MS) / 1000.0

    def warte_bis_frei(self):
        """Wartet, bis das Schreibwerk das letzte Zeichen fertig hat (nur wenn es noch beschaeftigt ist). Das Warten ist ein E/A-Halt."""
        rest = self.frei_ab - self.uhr()
        if rest <= 0:
            return
        if self.bei_halt is not None:
            self.bei_halt()
        try:
            self.schlafe(rest)
        finally:
            if self.bei_weiter is not None:
                self.bei_weiter()

    def ausgabe(self, text, stumm=False):
        """stumm=True (Selektor SW, G4-004): wie unten, aber ohne Klang; die Schreibwerkzeit und das Warten bleiben.
        Ausgabe des Rechners (G4-003): je Zeichen zuerst warten, bis das Schreibwerk frei ist (E/A-Halt, nur falls noetig), dann Klang
        und Zeichen anstossen, 'frei ab' = jetzt + Schreibwerkzeit merken und sofort weitermachen (kein Warten auf das Ende des Zeichens)."""
        for z in zeichen_aus_text(text):
            art = _art(z)
            self.warte_bis_frei()
            if not stumm:
                self._spiele(art)
            t = self.zeit(art)
            self.letzte_zeiten.append(t)
            del self.letzte_zeiten[:-200]
            self.frei_ab = self.uhr() + t

    # --- Angezeigte Eingabe (U-9) --------------------------------------------------------------------------------
    def eingabe(self, text):
        """Eingabe aus dem SW-Fenster: derselbe Klang, keine Schreibwerkzeit, keine Sperre, kehrt sofort zurueck."""
        for z in zeichen_aus_text(text):
            self._spiele(_art(z))
