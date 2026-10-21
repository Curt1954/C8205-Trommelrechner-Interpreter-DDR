#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_sw_zeit_messung.py - Messung zu OP-40 (GRAFIK_Beschreibung §10.4): Wie viel Schreibwerkzeit kaeme zur Laufzeit der Tests aus Tests/ hinzu?
Verfahren: jeder Test laeuft mit dem GRAFIK-Kern (wie grafik_gleichwertigkeit.py, ohne Schreibwerk, also ohne Schreibwerkzeit); aus der Schreibwerk-Ausgabe
(sw) wird die Schreibwerkzeit berechnet, die der echte Treiber (c8205_grafik.py, Schreibwerk nach S4-17, auch bei --STUMM) abwarten wuerde:
Zeichen im Mittel 80 ms, TAB 400 ms, WRZL 360 ms, WR 120 ms (grafik_schreibwerk.py). Die Rechnung nimmt die Mittelwerte, keine Zufallswerte.
Aufruf:  python3 testscripte/grafik_sw_zeit_messung.py [--zeit SEK] [--bericht DATEI]
Es wird nichts veraendert; jeder Lauf hat einen eigenen Arbeitsordner.
"""
import argparse, os, sys, time
HIER = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HIER)
sys.path.insert(0, HIER); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
import grafik_gleichwertigkeit as GW
import grafik_schreibwerk as SW

MITTEL_MS = {'tab': SW.TAB_MS, 'wrzl': SW.WRZL_MS, 'wr': SW.WR_MS}


def schreibwerkzeit_s(text):
    """Berechnete Schreibwerkzeit in Sekunden fuer einen Ausgabetext (Mittelwerte)."""
    summe = 0.0; n = 0
    for z in SW.zeichen_aus_text(text):
        summe += MITTEL_MS.get(SW._art(z), SW.SCHREIBWERKZEIT_MS); n += 1
    return summe / 1000.0, n


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--zeit', type=float, default=60.0); ap.add_argument('--bericht')
    a = ap.parse_args()
    zeilen = []; gesamt_s = 0.0; gesamt_z = 0; lauf_gesamt = 0.0
    for name in GW.finde_tests():
        t0 = time.time(); r = GW.starte_kind('grafik', name, a.zeit); dt = time.time() - t0
        lauf_gesamt += dt
        if 'sw' not in r:
            zeilen.append((name, None, 0, dt)); continue
        s, n = schreibwerkzeit_s(r['sw']); gesamt_s += s; gesamt_z += n
        zeilen.append((name, s, n, dt))
    mit = [z for z in zeilen if z[2] > 0]
    out = ['Tests: %d, davon mit Schreibwerk-Ausgabe: %d, ohne Ergebnis (uebersprungen/Absturz/Zeit): %d' % (len(zeilen), len(mit), sum(1 for z in zeilen if z[1] is None)),
           'Zeichen gesamt: %d, berechnete Schreibwerkzeit gesamt: %.1f s, Laufzeit der Kinder (ohne Schreibwerkzeit) gesamt: %.1f s' % (gesamt_z, gesamt_s, lauf_gesamt),
           'Die zehn Tests mit der laengsten Schreibwerkzeit:']
    for name, s, n, dt in sorted(mit, key=lambda z: -z[1])[:10]:
        out.append('  %-60s %6d Zeichen  %7.1f s  (Lauf ohne Schreibwerkzeit %.1f s)' % (name, n, s, dt))
    txt = '\n'.join(out); print(txt)
    if a.bericht:
        open(a.bericht, 'w', encoding='utf-8').write(txt + '\n')


if __name__ == '__main__':
    main()
