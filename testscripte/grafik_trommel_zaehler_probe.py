# -*- coding: utf-8 -*-
"""
grafik_trommel_zaehler_probe.py - Probelauf zu den Zeitmodellen und Zaehlern der Trommelstatistik (GRAFIK_Beschreibung §7.8).
Version: TZ-001

Fuer jedes Zeitmodell (alt, echt, schnell) laeuft dieselbe Zugriffsfolge: je Durchgang tick(2), rd, tick(1), wr
(also 2 Zugriffe, 3 Phasen). Danach werden alle Zaehler von GrafikTrommel.statistik() und die virtuelle Zeit vt ausgegeben.
Optional (--startlagen) wird die Streuung der Wartezeitsumme ueber alle 32 festen Startlagen im Modell 'schnell' gemessen.

Die Trommeldatei des Projekts wird NICHT veraendert: der Lauf arbeitet auf einer Kopie in einem Temp-Ordner
(geschrieben wird nur in die Zellen 3000 bis 3037 der Kopie).
In 'alt' vergehen die Phasen (tick) nicht; die Spalte ist mit den anderen nicht vergleichbar.

Aufruf (aus dem Projektordner):
  python3 testscripte/grafik_trommel_zaehler_probe.py                     400 Durchgaenge, Startlage 5, alle drei Modelle
  python3 testscripte/grafik_trommel_zaehler_probe.py --durchgaenge 1000 --start 0 --modelle schnell,echt
  python3 testscripte/grafik_trommel_zaehler_probe.py --startlagen        zusaetzlich: Streuung ueber Startlage 0..31
  python3 testscripte/grafik_trommel_zaehler_probe.py --trommel PFAD      andere Trommeldatei als Vorlage der Kopie
Dauer: echt und alt brauchen etwa Wortzeit x Wartezeit (rund 1,5 s bei 400 Durchgaengen). Linux; Windows nicht geprueft.
"""
import argparse, os, shutil, statistics, sys, tempfile

HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [HIER, os.path.join(HIER, 'grafik-interpreter-module'), os.path.join(HIER, 'c-module', 'python')]
import grafik_trommel as G


def lauf(kopie, modell, start, n):
    t = G.GrafikTrommel(kopie, basp='000000', start_index=start, zeitmodell=modell)
    try:
        for i in range(n):
            t.tick(2)
            t.rd((i * 7) & 0o7777)
            t.tick(1)
            t.wr(0o3000 | (i & 0o37), i)
        return t.statistik(), t.vt
    finally:
        t.schliessen()


def main():
    ap = argparse.ArgumentParser(description='Zaehler der Trommelstatistik je Zeitmodell (Probelauf)')
    ap.add_argument('--durchgaenge', type=int, default=400)
    ap.add_argument('--start', type=int, default=5, help='feste Startlage (PERM-Index 0..31)')
    ap.add_argument('--modelle', default='schnell,echt,alt')
    ap.add_argument('--startlagen', action='store_true', help='Streuung ueber die Startlagen 0..31 (Modell schnell)')
    ap.add_argument('--trommel', default=os.path.join(HIER, 'Trommel', 'trommel.txt'))
    a = ap.parse_args()
    modelle = [m.strip() for m in a.modelle.split(',') if m.strip()]
    for m in modelle:
        if m not in G.ZEITMODELLE:
            ap.error(f'unbekanntes Modell {m!r}')
    with tempfile.TemporaryDirectory() as tmp:
        kopie = os.path.join(tmp, 'trommel.txt')
        shutil.copyfile(a.trommel, kopie)
        erg = {}
        for m in modelle:
            import time
            t0 = time.monotonic()
            s, vt = lauf(kopie, m, a.start, a.durchgaenge)
            erg[m] = (s, vt, time.monotonic() - t0)
        namen = ['ticks', 'aufwachen', 'nachgeholte_ticks', 'verspaetung_summe_ns', 'verspaetung_max_ns', 'zugriffe',
                 'wartezeit_summe_ticks', 'rd_wr_zugriffe', 'gesperrte_schreibzugriffe', 'wartezeit_summe_ticks_aufrufer']
        print(f'{a.durchgaenge} Durchgaenge (je tick(2), rd, tick(1), wr), Startlage {a.start}\n')
        print(f'{"":34s}' + ''.join(f'{m:>14s}' for m in modelle))
        print(f'{"Dauer des Laufs (Wanduhr, ms)":34s}' + ''.join(f'{erg[m][2] * 1000:14.1f}' for m in modelle))
        for k in namen:
            print(f'{k:34s}' + ''.join(f'{erg[m][0].get(k, 0):14d}' for m in modelle))
        print(f'{"vt am Ende (nicht in statistik)":34s}' + ''.join(f'{erg[m][1] if m != "alt" else "-":>14}' for m in modelle))
        for m in modelle:
            s = erg[m][0]
            print(f'\n{m}: aufwachen + nachgeholte_ticks = {s["aufwachen"] + s["nachgeholte_ticks"]}, ticks = {s["ticks"]}'
                  f' (Rueckstand des Threads {s["ticks"] - s["aufwachen"] - s["nachgeholte_ticks"]})')
        if a.startlagen:
            w = [lauf(kopie, 'schnell', i, a.durchgaenge)[0]['wartezeit_summe_ticks_aufrufer'] for i in range(32)]
            mw = statistics.mean(w)
            print(f'\nStartlage 0..31 (schnell): Summe {min(w)} bis {max(w)}, Spanne {max(w) - min(w)} Wortzeiten = {100 * (max(w) - min(w)) / mw:.2f} %,'
                  f' {len(set(w))} verschiedene Werte')


if __name__ == '__main__':
    main()
