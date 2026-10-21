#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_e_im_eingabe_halt_probe.py - Nachstellung zu OP-20 (GRAFIK_Beschreibung §10.4): Was bleibt stehen, wenn H einen Einzelschritt (E) im
Eingabe-Halt abbricht? Kein Test des Sammellaufs, sondern eine Probe mit Ausgabe. Stand 21.10.2026: OP-20 ist behoben (G4-006, G5-002); die Probe zeigt jetzt den behobenen Zustand (E wirkt nach H wieder, K0 wartet nicht mehr). Die Pruefungen stehen in grafik_pult_tests.py (Klassen K0AbbruchBeimWarten, EImEingabeHaltAbgebrochen).
Aufbau: GRAFIK-Kern mit Rechner-Thread (wie im Fenster-Betrieb), Programm KEP (Tests/bsp_5_18_kep.txt) auf einer Kopie der Trommel; G, dann sechs E-Schritte,
der siebte E-Schritt steht im Eingabe-Halt (Flag E=1, K0 wartet auf T). Dann H und danach E, G+E bzw. R.
Aufruf:  python3 -I testscripte/grafik_e_im_eingabe_halt_probe.py        (Rueckgabewert 0 = Probe lief durch, sagt nichts ueber den Befund)
Es wird nichts im Projekt veraendert (Trommelkopie im Temp-Ordner).
"""
import os, sys, time, threading, shutil, tempfile
HIER = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
import c8205_grafik as G
import c8205_interp as I
from grafik_trommel import GrafikTrommel


def kep_trommel(kopie):
    shutil.copy(os.path.join(PROJ, 'Trommel', 'trommel.txt'), kopie)
    kep = I.Test(os.path.join(PROJ, 'Tests', 'bsp_5_18_kep.txt')); mem = {}
    with open(kopie, encoding='utf-8', newline='') as fh:
        for z in fh:
            mm = I.TROMMEL_ZEILE_RE.match(z); mem[int(mm.group(1), 8)] = int(mm.group(2), 8)
    mem.update({a & I.MASK12: w & I.MASK33 for a, w in kep.mem.items()})
    with open(kopie, 'w', encoding='utf-8', newline='') as fh:
        fh.write(''.join(f'{a:04o}: {mem.get(a, 0):011o}\n' for a in range(4096)))


def neu():
    d = tempfile.mkdtemp(); k = os.path.join(d, 'trommel.txt'); kep_trommel(k)
    tr = GrafikTrommel(k); r = G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), tr, pult_modus=True)
    r.thread_modus = True; stop = threading.Event()
    threading.Thread(target=G.rechner_schleife, args=(r, stop), daemon=True).start()
    r.pult_taste('H'); r.pult_taste('SW=0'); time.sleep(0.1)
    return r, tr, stop, d


def warte(f, t=3.0):
    t0 = time.time()
    while time.time() - t0 < t:
        if f(): return True
        time.sleep(0.01)
    return False


def ende(r, tr, stop, d):
    stop.set(); r.abbrechen(); tr.schliessen(); shutil.rmtree(d, ignore_errors=True)


def innen(r):
    m = r.m
    return (f'BZ={m.BZ:04o} AC={m.AC:011o} H={m.fl["H"]} E={m.fl["E"]} | e_gedrueckt={r.e_gedrueckt} K0 erwartet T={m.k0.erwartet("T")} '
            f'Zeichen im Vorrat={list(m.k0._q["T"])}')


def bis_eingabe_halt(r):
    r.pult_taste('G'); time.sleep(0.1)
    for _ in range(6):
        r.pult_taste('E'); time.sleep(0.12)
    r.pult_taste('E')
    return warte(lambda: r.m.k0.erwartet('T'))


def main():
    print('Referenz ohne H:')
    r, tr, stop, d = neu(); print('  Eingabe-Halt erreicht:', bis_eingabe_halt(r)); print('  ', innen(r))
    r.m.k0.einspeisen('1', 'T'); time.sleep(0.4); print('   nach Zeichen 1:', innen(r)); ende(r, tr, stop, d)
    for name, folge in (('E erneut', ['E']), ('G, dann E', ['G', 'E']), ('R', ['R'])):
        print(f'H im Eingabe-Halt, dann {name}:')
        r, tr, stop, d = neu(); bis_eingabe_halt(r)
        r.pult_taste('H'); time.sleep(0.4); print('   nach H:        ', innen(r))
        for t in folge:
            r.pult_taste(t); time.sleep(0.25)
        print(f'   nach {name}:'.ljust(18), innen(r))
        r.m.k0.einspeisen('1', 'T'); time.sleep(0.4); print('   nach Zeichen 1:', innen(r)); ende(r, tr, stop, d)
    print('H im Eingabe-Halt des R-Laufs (Gegenprobe, Weg ueber lauf()):')
    r, tr, stop, d = neu(); r.pult_taste('G'); time.sleep(0.1); r.pult_taste('R')
    warte(lambda: r.m.k0.erwartet('T'), 5); r.pult_taste('H'); time.sleep(0.5)
    print('   nach H: Rechner laeuft:', r.laeuft, '| K0 erwartet T:', r.m.k0.erwartet('T'), '| Wiederaufnahme-Knoten:', r.wiederaufnahme)
    ende(r, tr, stop, d)
    return 0


if __name__ == '__main__':
    sys.exit(main())
