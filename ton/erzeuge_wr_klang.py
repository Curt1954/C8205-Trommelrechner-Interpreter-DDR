#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
erzeuge_wr_klang.py - erzeugt sw_toene/wr.wav, den Klang fuer WR (Wagenruecklauf ohne Zeilenschaltung).

Festlegung des Projektinhabers (21.10.2026, OP-42): Fuer WR wird nur die erste Haelfte des WRZL-Klangs
genommen, vor dem markanten Ton, und dieser neue Klang 120 ms lang gespielt.

Verfahren: die ersten 120 ms von sw_toene/wrzl.wav (360 ms); der laute Schlag liegt bei etwa 126 ms
(Spitzenwert 12941, groesster Einzelwert der Datei), er gehoert nicht mehr dazu. Die letzten 5 ms werden
linear ausgeblendet (kein Knacken am Schnitt). Format wie die uebrigen Dateien (44100 Hz, 16 bit, mono).

Aufruf:  python3 erzeuge_wr_klang.py          (aus dem Ordner ton/ oder von ueberall; schreibt sw_toene/wr.wav)
         python3 erzeuge_wr_klang.py --ende 125 --aus 5     (anderer Schnitt in ms, andere Ausblendung in ms)
Nur Standardbibliothek.
"""
import argparse
import array
import os
import sys
import wave

HIER = os.path.dirname(os.path.abspath(__file__))
ORDNER = os.path.join(HIER, 'sw_toene')


def erzeuge(ende_ms=120.0, aus_ms=5.0, quelle=None, ziel=None):
    quelle = quelle or os.path.join(ORDNER, 'wrzl.wav')
    ziel = ziel or os.path.join(ORDNER, 'wr.wav')
    with wave.open(quelle, 'rb') as w:
        kan, breite, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
        if (kan, breite) != (1, 2):
            raise ValueError('erwartet 16-bit mono')
        roh = array.array('h')
        roh.frombytes(w.readframes(w.getnframes()))
    if sys.byteorder == 'big':
        roh.byteswap()
    n = round(rate * ende_ms / 1000.0)
    if n > len(roh):
        raise ValueError(f'Schnitt {ende_ms} ms liegt hinter dem Ende von {quelle}')
    teil = array.array('h', roh[:n])
    m = min(n, round(rate * aus_ms / 1000.0))
    for i in range(m):                                  # lineare Ausblendung der letzten m Samples
        teil[n - m + i] = round(teil[n - m + i] * (m - 1 - i) / m)
    if sys.byteorder == 'big':
        teil.byteswap()
    with wave.open(ziel, 'wb') as w:
        w.setnchannels(kan); w.setsampwidth(breite); w.setframerate(rate)
        w.writeframes(teil.tobytes())
    return ziel, n


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--ende', type=float, default=120.0, metavar='MS', help='Laenge des Ausschnitts ab Beginn von wrzl.wav (Vorgabe 120)')
    ap.add_argument('--aus', type=float, default=5.0, metavar='MS', help='Ausblendung am Ende (Vorgabe 5)')
    a = ap.parse_args()
    z, n = erzeuge(a.ende, a.aus)
    print(f'{z}: {n} Samples = {n / 44.1:.1f} ms')
