# -*- coding: utf-8 -*-
"""
grafik_schreibwerk.py - Schreibwerkzeit und Klangwahl des Schreibwerks fuer GRAFIK (Stufe 4, GRAFIK_Beschreibung §6 (alt: Dok. 10) S4-05 bis S4-08, S4-17).
Version: G4-001.  Nur Standardbibliothek.

Entschieden (Projektinhaber 18.10.2026):
  * Schreibwerkzeit je ausgegebenem Zeichen 80 ms, zufaellig 70 bis 90 ms (gleichverteilt), unabhaengig von der Tonlaenge (O4-1).
  * Zeichenklang 100 ms: die Dateien zeichen_*.wav (120 ms) bleiben unveraendert, bei der Wiedergabe auf 100 ms begrenzt (O4-8);
    der Ueberstand ueber die Schreibwerkzeit hinaus UEBERLAPPT mit dem naechsten Zeichen (O4-7).
  * TAB 400 ms und WRZL 360 ms gelten als Schreibwerkzeit; die Schreibwerkzeit gilt auch bei --STUMM, im Modus TEST nicht (O4-9).
  * Selektor SW (unterdruecken): keine Ausgabe, keine Schreibwerkzeit, kein Klang; er wirkt NUR auf die Ausgabe (O4-3, O4-10).
  * Angezeigte Eingabe: derselbe Klang, KEINE Schreibwerkzeit, keine Sperre; Umschaltzeichen nie (O4-2, O4-3, O4-6).
  * Ein Schreibwerk: eine Folge, nie zweimal derselbe Zeichenklang hintereinander, fuer Ausgabe und Eingabe gemeinsam (S4-05).
Zeitgeber, Zufall und Klaenge sind ersetzbar (schlafe, zufall, mischer), damit die Pruefungen ohne Audiogeraet und ohne Echtzeit laufen.
"""
import glob
import os
import random
import time

import grafik_tonmisch as TM

VERSION_SCHREIBWERK = 'G4-001'
SCHREIBWERKZEIT_MS = 80.0
SCHREIBWERKZEIT_STREUUNG_MS = 10.0          # 70 bis 90 ms
ZEICHENKLANG_MS = 100.0
ZEICHEN_AUSBLENDUNG_MS = 10.0               # Konstante fuer die Hoerpruefung (S4-16)
TAB_MS = 400.0
WRZL_MS = 360.0
PEGEL = 2.0                                 # G4-004: doppelt so laut wie vorher (Hoerpruefung 1); --TON stellt je Gruppe nach (grafik_tonmisch.TON_BASIS)


def _art(s):
    """Klangart eines Aufrufs: 'tab', 'wrzl' oder 'zeichen' (ZR und benannte Zeichen <Name> klingen wie jedes Zeichen)."""
    if s == '\t':
        return 'tab'
    if s == '\n':
        return 'wrzl'
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
    def __init__(self, mischer=None, klaenge=None, schlafe=time.sleep, zufall=None):
        """mischer: grafik_tonmisch.Mischer oder None (--STUMM: keine Toene, die Schreibwerkzeit bleibt).
        klaenge: Wörterbuch {'zeichen': [array,...], 'tab': array, 'wrzl': array}; sonst aus dem Ordner (laden())."""
        self.mischer = mischer
        self.pegel = PEGEL                      # --TON (Gruppe SW) setzt ihn von aussen
        self.schlafe = schlafe
        self.zufall = zufall if zufall is not None else random.Random()
        self.zeichen_klaenge = []
        self.tab = None
        self.wrzl = None
        self._letzter = None                    # Index des letzten Zeichenklangs (nie zweimal derselbe)
        if klaenge:
            self.zeichen_klaenge = [TM.begrenze(k, ZEICHENKLANG_MS, ZEICHEN_AUSBLENDUNG_MS) for k in klaenge['zeichen']]
            self.tab, self.wrzl = klaenge.get('tab'), klaenge.get('wrzl')
        self.letzte_zeiten = []                 # Schreibwerkzeiten in Sekunden (fuer Pruefungen; nur die letzten 200)

    @classmethod
    def laden(cls, ordner, mischer, **kw):
        sw = os.path.join(ordner, 'sw_toene')
        zeichen = [TM.lade_klang(p) for p in sorted(glob.glob(os.path.join(sw, 'zeichen_*.wav')))]
        if not zeichen:
            raise FileNotFoundError(f'keine zeichen_*.wav in {sw}')
        k = {'zeichen': zeichen, 'tab': TM.lade_klang(os.path.join(sw, 'tab_400.wav')), 'wrzl': TM.lade_klang(os.path.join(sw, 'wrzl.wav'))}
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
        return self._zeichenklang()

    def _spiele(self, art):
        k = self._klang(art)
        if self.mischer is not None and k is not None:
            self.mischer.einzel('schreibwerk', k, self.pegel)

    # --- Ausgabe des Rechners ------------------------------------------------------------------------------------
    def zeit(self, art):
        """Schreibwerkzeit in Sekunden: Zeichen 70 bis 90 ms, TAB 400 ms, WRZL 360 ms (O4-1, O4-9)."""
        if art == 'tab':
            return TAB_MS / 1000.0
        if art == 'wrzl':
            return WRZL_MS / 1000.0
        return self.zufall.uniform(SCHREIBWERKZEIT_MS - SCHREIBWERKZEIT_STREUUNG_MS,
                                   SCHREIBWERKZEIT_MS + SCHREIBWERKZEIT_STREUUNG_MS) / 1000.0

    def ausgabe(self, text):
        """Ausgabe des Rechners: je Zeichen Klang und Schreibwerkzeit; kehrt nach der Schreibwerkzeit zurueck."""
        for z in zeichen_aus_text(text):
            art = _art(z)
            self._spiele(art)
            t = self.zeit(art)
            self.letzte_zeiten.append(t)
            del self.letzte_zeiten[:-200]
            self.schlafe(t)

    # --- Angezeigte Eingabe (U-9) --------------------------------------------------------------------------------
    def eingabe(self, text):
        """Eingabe aus dem SW-Fenster: derselbe Klang, keine Schreibwerkzeit, keine Sperre, kehrt sofort zurueck."""
        for z in zeichen_aus_text(text):
            self._spiele(_art(z))
