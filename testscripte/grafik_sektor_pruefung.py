#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_sektor_pruefung.py - Prueft, ob die Befehlsschleife des GRAFIK-Interpreters schnell genug ist, damit zeitoptimal
programmierter Code seinen Sektor findet (Magnettrommel-Dokumentation: Sprung 4 Wortzeiten, Einzelbefehl 5 Wortzeiten).
Version: SP-003 (SP-002: Befehlsart waehlbar: sprung, einzel, gruppe; SP-003: Fehlgriff bei gruppe = Abweichung vom festen Zyklusmuster)

Verfahren (Abstandskarte): Ein Prueflauf besteht aus einer Kette von 32 Sprungbefehlen (000 <Ziel>) auf den Zellen 0000 bis 0037.
Der Sprung auf der physischen Position p fuehrt zur Zelle auf der Position p+d (d = Abstand in Wortzeiten, Wortzeit 104 us).
Je Sprung wird ein Trommelzugriff (Befehlsabruf am Ziel) ausgefuehrt. Zwischen dem Ende eines Zugriffs und der naechsten Anforderung
vergeht die Rechenzeit c der Befehlsschleife. Ist c < d, wartet der Zugriff d - c Wortzeiten (Treffer); ist c > d, ist der Sektor
vorbei und der Zugriff wartet d - c + 32 Wortzeiten (Fehlgriff, bis zu eine Umdrehung = 3,3 ms laenger).
Je Abstand d (Voreinstellung 1 bis 8) wird gemessen:
  fehlgriffe   Anteil der Zugriffe mit Wartezeit > d Wortzeiten (der Sektor war vorbei)
  c_grob       daraus geschaetzte Rechenzeit der Schleife je Sprung in us: (d - mittlere Wartezeit der Treffer) * 104 us; die Wartezeit
               wird in ganzen Ticks gezaehlt, der Wert ist daher nur auf etwa 104 us genau
  c_mittel, c_p99, c_max   Rechenzeit in us zwischen Rueckkehr eines Zugriffs und der naechsten Anforderung (Uhr im Python-Prozess,
               enthaelt Rechnen und Warten auf die Python-Sperre, nicht das Aufwachen des Threads nach dem Zuschlag)
               Zum Vergleich: Sprung 4 Wortzeiten = 416 us, Einzelbefehl 5 Wortzeiten = 520 us
Die kleinste Entfernung d, bei der es (fast) keine Fehlgriffe gibt, ist die Grenze der Schleife. Das Soll laut Dokumentation: d = 4.
Optional (--last N): N Rechenprozesse als Hintergrundlast.

Aufruf (aus dem Projektordner):
  python3 testscripte/grafik_sektor_pruefung.py                        d = 1 bis 8, 2 s je Abstand
  python3 testscripte/grafik_sektor_pruefung.py --dauer 5 --d-bis 12
  python3 testscripte/grafik_sektor_pruefung.py --last 1               mit einem Last-Prozess
  python3 testscripte/grafik_sektor_pruefung.py --mdverz ORDNER        Ordner mit den Knoten-Dokumenten (Umlaute in den Dateinamen!)
Ergebnis: Tabelle auf dem Bildschirm und testscripte/sektor_pruefung_ergebnis.csv.
Es wird nichts im Projekt veraendert (Arbeitskopie der Trommel in einem Temp-Ordner).
"""
import argparse
import multiprocessing
import os
import shutil
import sys
import tempfile
import threading
import time

HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ)
sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
VERSION_PRUEFUNG = 'SP-003'
TICK_US = 104.0
ZYKLUS_GRUPPE = 34           # Zugriffe je Durchlauf der Gruppenkette (gemessen: 6, 27, 0, dann 31 mal 1)


def _last():
    x = 0
    while True:
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF


def programm(art, d, perm):
    """{Adresse: 11 Oktalstellen} der Pruefkette (nur die Zellen 0000 bis 0037).
    sprung: Sprung von Position p nach Position p+d.
    einzel: 31 Lade-/Speicherbefehle (211/240) hintereinander (Folgebefehl wie ueblich 5 Wortzeiten spaeter), Operand d Wortzeiten
            nach dem Befehl (Spur 3000), Zelle 0037 springt nach 0000; Dokumentation: Operand fruehestens nach 2 Wortzeiten.
    gruppe: Zelle 0000 Gruppenbefehl 411 (laden, alle 32 Zellen der Spur 3000, Phase IV 32 mal), Zelle 0001 Sprung nach 0000."""
    pos = {s: i for i, s in enumerate(perm)}
    if art == 'sprung':
        return {s: '0000%04o000' % perm[(pos[s] + d) % 32] for s in range(32)}
    if art == 'einzel':
        p = {}
        for i in range(32):
            if i == 31:
                p[i] = '00000000000'
            else:
                operand = 0o3000 + perm[(pos[i] + d) % 32]
                p[i] = '0000%04o' % operand + ('211' if i % 2 == 0 else '240')
        return p
    if art == 'gruppe':
        return {0: '0000%04o411' % 0o3000, 1: '00000000000'}
    raise ValueError(art)


def trommel_kopie(ordner, prog):
    quelle = os.path.join(PROJ, 'Trommel', 'trommel.txt')
    ziel = os.path.join(ordner, 'trommel.txt')
    with open(quelle, encoding='utf-8') as f:
        zeilen = f.read().split('\n')
    for i, z in enumerate(zeilen):
        if len(z) >= 5 and z[4] == ':':
            adr = int(z[:4], 8)
            if adr in prog:
                zeilen[i] = f'{adr:04o}: {prog[adr]}'
    with open(ziel, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(zeilen))
    return ziel


class Mitschnitt:
    """Stellvertreter des C-Moduls: reicht alles durch und merkt sich die Wartezeit jedes Zugriffs (Wortzeiten)."""
    def __init__(self, modul):
        self._m = modul
        self.waits = []
        self.luecken = []          # Rechenzeit in us zwischen Rueckkehr eines Zugriffs und der naechsten Anforderung
        self.sammeln = False
        self._ret = None

    def _vor(self):
        if self.sammeln and self._ret is not None:
            self.luecken.append((time.perf_counter() - self._ret) * 1e6)

    def _nach(self, wz):
        self._ret = time.perf_counter()
        if self.sammeln:
            self.waits.append(wz)

    def __getattr__(self, name):
        return getattr(self._m, name)

    def lesen_warten(self, adr):
        self._vor()
        wert, wz = self._m.lesen_warten(adr)
        self._nach(wz)
        return wert, wz

    def schreiben_warten(self, adr, wert):
        self._vor()
        gesperrt, wz = self._m.schreiben_warten(adr, wert)
        self._nach(wz)
        return gesperrt, wz


def messen(art, d, dauer, warm, mdverz):
    import c8205_grafik as G
    from grafik_trommel import GrafikTrommel, PERM, lade_modul
    tmp = tempfile.mkdtemp()
    stop = threading.Event()
    tr = r = None
    try:
        mit = Mitschnitt(lade_modul())
        tr = GrafikTrommel(trommel_kopie(tmp, programm(art, d, PERM)), start_index=0, modul=mit)
        r = G.Rechner(G.lade_graph(mdverz), tr, pult_modus=True)
        r.taste('H')
        r.taste('SW=0')
        r.thread_modus = True
        threading.Thread(target=G.rechner_schleife, args=(r, stop), name='rechner', daemon=True).start()
        time.sleep(0.2)
        for t in ('H', 'G', 'R'):
            r.pult_taste(t)
        frist = time.monotonic() + 5
        while not getattr(r, 'laeuft', False) and time.monotonic() < frist:
            time.sleep(0.01)
        if not getattr(r, 'laeuft', False):
            return {'fehler': 'Rechner lief nach R nicht an'}
        time.sleep(warm)
        mit.sammeln = True
        t0 = time.monotonic()
        time.sleep(dauer)
        mit.sammeln = False
        dt = time.monotonic() - t0
        w = list(mit.waits)
        lk = sorted(mit.luecken)
        if not w:
            return {'fehler': 'keine Zugriffe gemessen'}
        if art == 'gruppe':
            # Der Zyklus (Gruppenbefehl, Phase IV 32 mal, Sprung zurueck) hat feste Wartezeiten, darunter lange Waits ohne Fehlgriff
            # (Ruecksprung 0001 nach 0000: 27 Wortzeiten laut Sektorfolge). Fehlgriff = Abweichung vom haeufigsten Wert der Zyklusstelle
            # (ein verpasster Sektor kostet eine Umdrehung zusaetzlich, die Folgezugriffe bleiben gleich).
            L = ZYKLUS_GRUPPE
            lang = max(w[:L * 2]) if len(w) >= L * 2 else max(w)
            start = w.index(lang)
            w = w[start:]
            w = w[:len(w) // L * L]
            if not w:
                return {'fehler': 'zu wenige Zugriffe fuer einen Zyklus'}
            muster = []
            for k in range(L):
                spalte = [w[i] for i in range(k, len(w), L)]
                muster.append(max(set(spalte), key=spalte.count))
            fehl = sum(1 for i, x in enumerate(w) if x != muster[i % L])
            treffer = [x for i, x in enumerate(w) if x == muster[i % L]]
        else:
            grenze = d if art == 'sprung' else 15          # Fehlgriff: Wartezeit > d (Sprung) bzw. >= 16 (einzel: ein Sektor war vorbei)
            treffer = [x for x in w if x <= grenze]
            fehl = len(w) - len(treffer)
        mw = sum(treffer) / len(treffer) if treffer else None
        return dict(art=art, d=d, wz_je_zugriff=round(1e6 / (len(w) / dt) / TICK_US, 2), zugriffe=len(w), zugriffe_s=round(len(w) / dt), fehlgriffe=round(fehl / len(w), 4),
                    wartezeit_treffer=None if mw is None else round(mw, 2),
                    c_grob_us=None if mw is None else round((d - mw) * TICK_US, 1),
                    c_mittel_us=round(sum(lk) / len(lk), 1) if lk else None,
                    c_p99_us=round(lk[int(len(lk) * 0.99)], 1) if lk else None,
                    c_max_us=round(lk[-1], 1) if lk else None,
                    laeuft_am_ende=bool(r.laeuft))
    finally:
        stop.set()
        try:
            if r is not None:
                r.abbrechen()
            if tr is not None:
                tr.schliessen()
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description='Abstandskarte: findet die Befehlsschleife ihren Sektor?')
    ap.add_argument('--art', choices=('sprung', 'einzel', 'gruppe'), default='sprung', help='Befehlsart der Pruefkette (sprung)')
    ap.add_argument('--dauer', type=float, default=2.0, help='Messdauer je Abstand in s (2)')
    ap.add_argument('--warm', type=float, default=0.5, help='Einlauf in s (0,5)')
    ap.add_argument('--d-von', type=int, default=1)
    ap.add_argument('--d-bis', type=int, default=8)
    ap.add_argument('--last', type=int, default=0, help='Anzahl Hintergrund-Rechenprozesse (0)')
    ap.add_argument('--mdverz', default=os.path.join(PROJ, 'markdown-dateien'))
    ap.add_argument('--csv', default=os.path.join(HIER, 'sektor_pruefung_ergebnis.csv'))
    a = ap.parse_args()
    lastprozesse = [multiprocessing.Process(target=_last, daemon=True) for _ in range(a.last)]
    for p in lastprozesse:
        p.start()
    print(f'Sektorpruefung {VERSION_PRUEFUNG}: Art {a.art}, CPU-Kerne {os.cpu_count()}, Python {sys.version.split()[0]}, Last-Prozesse {a.last}, {a.dauer} s je Abstand')
    print('   d  WZ/zugr  zugriffe/s  fehlgriffe  wartezeit_treffer  c_grob  c_mittel  c_p99  c_max  (us; Soll laut Dokumentation: Sprung d=4 = 416 us)')
    zeilen = []
    for d in (range(a.d_von, a.d_bis + 1) if a.art != 'gruppe' else (0,)):
        e = messen(a.art, d, a.dauer, a.warm, a.mdverz)
        if 'fehler' in e:
            print(f'{d:4d}  FEHLER: {e["fehler"]}')
            continue
        zeilen.append(e)
        print(f'{d:4d}  {e["wz_je_zugriff"]:7.2f}  {e["zugriffe_s"]:9d}  {e["fehlgriffe"]*100:8.2f} %  {str(e["wartezeit_treffer"]):>16}  {str(e["c_grob_us"]):>6}  {str(e["c_mittel_us"]):>8}  {str(e["c_p99_us"]):>5}  {str(e["c_max_us"]):>5}')
    for p in lastprozesse:
        p.terminate()
    with open(a.csv, 'w', encoding='utf-8') as f:
        f.write('d;zugriffe;zugriffe_s;fehlgriffe;wartezeit_treffer;c_grob_us;c_mittel_us;c_p99_us;c_max_us;last\n')
        for e in zeilen:
            f.write(f'{e["d"]};{e["zugriffe"]};{e["zugriffe_s"]};{e["fehlgriffe"]};{e["wartezeit_treffer"]};{e["c_grob_us"]};{e["c_mittel_us"]};{e["c_p99_us"]};{e["c_max_us"]};{a.last}\n')
    print('CSV:', a.csv)


if __name__ == '__main__':
    main()
