# -*- coding: utf-8 -*-
"""
grafik_pultton.py - Tastengeraeusche des Bedienpults fuer GRAFIK (Stufe 4, GRAFIK_Beschreibung §6.7).
Version: G4-003.  Nur Standardbibliothek.

Drei Klaenge fuer die drei mechanischen Tastentypen (Tastentypen: aufgabe 27.10.2026; Klaenge in ton/pult_toene/, Hoerpruefung des
Projektinhabers 27.10.2026: "die 3 sind gut"):
  impuls   = impuls_druck.wav   Typ 3 Impulstaste (Taster, kein Rasten): G, Ue, ST, die Eingabetasten, E und M (beim Druecken).
  einrast  = einrast_aus.wav    Typ 2 Ein-Tasten-Einrastschalter und Kanaltasten K0 bis K3: SP, BS, LS, Selektor SW, K0 bis K3.
                                (V: derselbe Klang beim Einrasten und beim Loesen, weil einrast_ein.wav nicht bestaetigt wurde.)
  radio    = radio_wechsel.wav  Typ 1 Radiotasten H-R und T-SW (ein Klang fuer beide Richtungen).
Es gibt keinen Loslass-Ton (Entscheidung des Projektinhabers 27.10.2026): weder beim Loslassen einer Impulstaste noch bei E- und M-.
Wirkungslose Klicks (gesperrte Taste, Klick auf eine schon eingerastete Taste, Pult nicht im Betrieb) sind stumm (M-25: kein Ton);
dafuer sorgt PultSteuerung: sie ruft taste(art) nur auf, wenn der Klick gewirkt hat.

Lautstaerke: Gruppe Pult des Mischers (--TON, erste Ziffer). Die Klicks werden mit KLICK_PEGEL (1,76; bis 27.10.2026 1,6, dann auf Wunsch des Projektinhabers 10 % lauter) mal dem Gruppenfaktor gespielt, damit sie
sich gegen das Rechner-Grundgeraeusch (GRUND_PEGEL 0,68 seit 27.10.2026, vorher 0,8) durchsetzen: gemessen mit ton/pult_toene/pruefe_hoerbarkeit.py, +12 bis +17 dB im Band
2,5 bis 5 kHz gegen das lauteste 10-ms-Fenster des Grundgeraeusches. Spitze 0,35 * 1,76 = 0,62; mit der Grundgeraeusch-Spitze 0,25 unter 1,0.
Der Faktor steht hier und nicht in den WAV-Dateien, damit --TON wirkt (Grundgeraeusch und Klicks wachsen gemeinsam).
"""
import os

import grafik_tonmisch as TM

VERSION_PULTTON = 'G4-003'
KLICK_PEGEL = 1.76
IMPULS_FAKTOR = 1.4                                 # G4-003: Impulstasten (G, Ue, ST, E, M, Eingabetasten) 1,4-fach (+2,9 dB): der Tick ist nur 9 ms lang, Energie wie einrast; Hoerprobe 27.10.2026 'zu leise'
KANAL = 'rechner'                                   # Gruppe Pult des Mischers
ORDNER = 'pult_toene'                               # unter ton/
DATEIEN = {'impuls': 'impuls_druck.wav', 'einrast': 'einrast_aus.wav', 'radio': 'radio_wechsel.wav'}


def lade_pultklaenge(ton_ordner):
    """Laedt die drei Klaenge aus <ton_ordner>/pult_toene (mono, 16 bit, 44,1 kHz; sonst ValueError, fehlende Datei OSError)."""
    return {art: TM.lade_klang(os.path.join(ton_ordner, ORDNER, name)) for art, name in DATEIEN.items()}


class PultTastenTon:
    def __init__(self, mischer=None, klaenge=None, faktor=1.0, klick_pegel=KLICK_PEGEL):
        """faktor: Gruppenfaktor Pult aus --TON (Faktor = Basis * Ziffer / 5). klaenge: {'impuls', 'einrast', 'radio'} (array 'h')."""
        self.mischer, self.k, self.faktor, self.klick_pegel = mischer, klaenge, faktor, klick_pegel
        self.log = []                               # (art) je gespieltem Klick, nur die letzten 200 (Pruefungen)

    def _mischer_ein(self, m):
        self.mischer = m

    def taste(self, art):
        """Spielt den Klang der Art ('impuls', 'einrast', 'radio'); ohne Mischer oder bei Pegel 0 (--TON Ziffer 0) lautlos."""
        self.log.append(art)
        del self.log[:-200]
        if self.mischer is None or self.k is None:
            return
        pegel = self.klick_pegel * self.faktor * (IMPULS_FAKTOR if art == 'impuls' else 1.0)
        if pegel > 0:
            self.mischer.einzel(KANAL, self.k[art], pegel)
