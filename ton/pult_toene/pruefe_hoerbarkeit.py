#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft, wie weit die Pult-Klicks ueber dem Rechner-Grundgeraeusch liegen (nur Messung, kein Hoeren).
Je Band: lautester 10-ms-Abschnitt des Klicks gegen Median und Maximum der 10-ms-Abschnitte des Grundgeraeusches
(Bandleistung, Hann-Fenster). Sollwert: im Band 2,5 bis 5 kHz mindestens +10 dB gegen das Maximum (bei Klickpegel 1,76).
Aufruf:  python3 pruefe_hoerbarkeit.py [--grund ../rechner_grundgeraeusch.wav] [--grund-pegel 0.68] [--klick-pegel 1.76]
Braucht numpy. Rueckgabecode 0 = alle ueber dem Sollwert, 1 = mindestens ein Klick darunter."""
import argparse, os, struct, sys, wave
import numpy as np
HIER = os.path.dirname(os.path.abspath(__file__))
KLICKS = ('impuls_druck.wav', 'einrast_aus.wav', 'radio_wechsel.wav')
BAENDER = ((500, 1500), (1500, 2500), (2500, 5000), (5000, 9000))
SOLL_DB = 10.0

def lade(pfad):
    w = wave.open(pfad)
    return np.array(struct.unpack('<%dh' % w.getnframes(), w.readframes(w.getnframes()))) / 32768.0, w.getframerate()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--grund', default=os.path.join(HIER, '..', 'rechner_grundgeraeusch.wav'))
    ap.add_argument('--grund-pegel', type=float, default=0.68)  # GRUND_PEGEL in grafik_rechnerton.py (bis 27.10.2026 0,8)
    ap.add_argument('--klick-pegel', type=float, default=1.76)  # KLICK_PEGEL: Pegel, mit dem der Mischer den Klick spielen soll (Einbau noch offen)
    a = ap.parse_args()
    g, sr = lade(a.grund); g = g * a.grund_pegel
    N = int(0.010 * sr); f = np.fft.rfftfreq(N, 1 / sr); fen = np.hanning(N)
    def bp(x, b): return (abs(np.fft.rfft(x * fen)) ** 2)[(f >= b[0]) & (f < b[1])].sum()
    rausch = {b: np.array([bp(g[s:s + N], b) for s in range(0, len(g) - N, N // 2)]) for b in BAENDER}
    schlecht = False
    print('Grund RMS %.4f; Sollwert %+.0f dB im Band 2500-5000 gegen das lauteste Grund-Fenster' % (g.std(), SOLL_DB))
    for nm in KLICKS:
        c, _ = lade(os.path.join(HIER, nm)); c = c * a.klick_pegel
        zeile = []
        for b in BAENDER:
            pk = max(bp(c[s:s + N], b) for s in range(0, len(c) - N, N // 4))
            med, mx = (10 * np.log10(pk / np.median(rausch[b])), 10 * np.log10(pk / rausch[b].max()))
            zeile.append('%d-%d: %+.1f/%+.1f' % (b[0], b[1], med, mx))
            if b == (2500, 5000) and mx < SOLL_DB: schlecht = True
        print('%-16s Spitze %.2f  (dB gegen Median/Maximum)  %s' % (nm, abs(c).max(), '  '.join(zeile)))
    print('UNTER dem Sollwert' if schlecht else 'alle ueber dem Sollwert')
    return 1 if schlecht else 0

if __name__ == '__main__':
    sys.exit(main())
