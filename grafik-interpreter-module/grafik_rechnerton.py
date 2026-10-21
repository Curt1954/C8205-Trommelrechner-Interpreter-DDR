# -*- coding: utf-8 -*-
"""
grafik_rechnerton.py - Rechnertoene fuer GRAFIK ueber den Mischer (Stufe 4, GRAFIK_Beschreibung §6 (alt: Dok. 10) S4-11, S4-12).
Version: G4-004.  Nur Standardbibliothek.  Loest grafik_ton.RechnerTon (Stufe 2, je Klang ein Abspielprozess) ab; gleiche Schnittstelle
(fade_in, grund_an, fade_out, alles_aus, fade_laeuft, dauer_fade_in, dauer_fade_out, verfuegbar), damit PultSteuerung unveraendert bleibt.

  * fade_in:   Einzelklang 'rechner' (Schluessel 'fade'), volle Laenge (11,3 s).
  * grund_an:  Grundgeraeusch als Schleife (Schluessel 'grund'), Pegel 0,8 (Projektinhaber 17.10.2026).  Die Schleife laeuft im Mischer
               ohne Neustart (Stufe 2: Neustart einer 60-s-Datei mit moeglicher Luecke).
  * fade_out:  beginnt mit dem Klick; fade_in und Grundgeraeusch enden, fade_out (2 s) klingt; die Tore der anderen Kanaele
               (Schreibwerk, Leser, Stanzer) werden geschlossen (V: nach Netz aus klingt nur noch fade_out).
  * alles_aus: Strg+C, X, Fenster zu, Ende: alle Toene sofort aus (kein fade_out).
Der Mischer wird erst spaeter gesetzt (ton.mischer = ...); ohne Mischer sind alle Aufrufe ohne Wirkung.
"""
import os

import grafik_tonmisch as TM

VERSION_RECHNERTON = 'G4-004'
GRUND_PEGEL = 0.8
FADE_IN = 'netz_ein_fade_in.wav'
FADE_OUT = 'netz_aus_fade_out.wav'
GRUND = 'rechner_grundgeraeusch.wav'


class MischerRechnerTon:
    def __init__(self, ordner, mischer=None, klaenge=None, grund_pegel=GRUND_PEGEL, faktor=1.0):
        """ordner: Ordner `ton`. klaenge: Woerterbuch {'fade_in', 'fade_out', 'grund'} (array 'h') fuer Tests, sonst aus den Dateien."""
        self.mischer = mischer
        self.faktor = faktor                      # --TON (Gruppe Pult): Lautstaerke von fade_in, Grundgeraeusch, fade_out; 1,0 = Pegel der Hoerpruefung 1
        self.grund_pegel = grund_pegel * faktor
        self.ist_mischer = True
        if klaenge is None:
            klaenge = {'fade_in': TM.lade_klang(os.path.join(ordner, FADE_IN)),
                       'fade_out': TM.lade_klang(os.path.join(ordner, FADE_OUT)),
                       'grund': TM.lade_klang(os.path.join(ordner, GRUND))}
        self.k = klaenge

    @property
    def verfuegbar(self):
        return self.mischer is not None

    def dauer_fade_in(self):
        return len(self.k['fade_in']) / float(TM.RATE)

    def dauer_fade_out(self):
        return len(self.k['fade_out']) / float(TM.RATE)

    def fade_laeuft(self):
        return self.mischer is not None and self.mischer.klingt_schluessel('fade') > 0

    def fade_in(self):
        if self.mischer is not None:
            self.mischer.einzel('rechner', self.k['fade_in'], self.faktor, 'fade')

    def grund_an(self):
        if self.mischer is not None:
            self.mischer.dauer_an('rechner', 'grund', self.k['grund'], self.grund_pegel)

    def fade_out(self):
        m = self.mischer
        if m is None:
            return
        m.dauer_aus('grund')
        m.dauer_aus('fade')                                  # fade_in bricht ab: es klingt immer nur einer der Klaenge
        for kanal in ('schreibwerk', 'leser', 'stanzer'):    # nach Netz aus nur noch fade_out (V, S4-12)
            m.tor(kanal, False)
        m.einzel('rechner', self.k['fade_out'], self.faktor, 'fade')

    def alles_aus(self):
        if self.mischer is not None:
            self.mischer.alles_aus()
