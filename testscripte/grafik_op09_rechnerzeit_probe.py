#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_op09_rechnerzeit_probe.py - Nachstellung zu OP-09 (GRAFIK_Beschreibung §6.10 Nr. 3): Wie lange braucht der Rechner nach einem Umschaltzeichen
bis zum naechsten 011? Der Test sw_zwei_ziffern (Tests/) wird auf eine leere Trommelkopie im Temp-Ordner geladen; Schreibwerk mit Schreibwerkzeit,
ohne Klang (wie --STUMM); das SW-Fenster wird durch direktes Einspeisen in die K0-Warteschlange ersetzt. Eine Probe mit Ausgabe, kein Test des Sammellaufs.
Aufruf:  python3 -I testscripte/grafik_op09_rechnerzeit_probe.py [TESTNAME]      (Vorgabe sw_zwei_ziffern; Rueckgabewert 0 = Probe lief durch)
"""
import os, re, sys, time, threading, shutil, tempfile
HIER = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
import c8205_grafik as G
from grafik_trommel import GrafikTrommel
from grafik_schreibwerk import Schreibwerk


def trommel_aus_test(test, ziel):
    zellen, innen = {}, False
    for z in open(test, encoding='utf-8'):
        if z.strip() == 'Trommeldatei:':
            innen = True
        elif innen:
            m = re.match(r'^([0-7]{4}):\s*([0-7]{11})\b', z)
            if m: zellen[int(m.group(1), 8)] = m.group(2)
    with open(ziel, 'w', encoding='utf-8', newline='\n') as f:
        f.write(''.join('%04o: %s\n' % (a, zellen.get(a, '0' * 11)) for a in range(4096)))


def warte(f, t=10.0):
    a = time.time()
    while time.time() - a < t:
        if f(): return time.time() - a
        time.sleep(0.002)
    return None


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else 'sw_zwei_ziffern'
    d = tempfile.mkdtemp(); k = os.path.join(d, 'trommel.txt'); trommel_aus_test(os.path.join(PROJ, 'Tests', name + '.test'), k)
    tr = GrafikTrommel(k); r = G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), tr, pult_modus=True)
    r.sw.schreibwerk = Schreibwerk(None, None)
    r.thread_modus = True; stop = threading.Event()
    threading.Thread(target=G.rechner_schleife, args=(r, stop), daemon=True).start()
    r.pult_taste('H'); r.pult_taste('SW=1'); time.sleep(0.1); r.pult_taste('G'); time.sleep(0.1); r.pult_taste('R')
    k0 = r.m.k0
    w = warte(lambda: k0.offen('SW')); print(f'Start (R) bis zum ersten 011: {w:.2f} s' if w else 'kein 011')
    n0 = len(r.sw.text); time.sleep(0.5)
    for tok in ('Um. KB', '2'):
        n = len(r.sw.text); ok = k0.annehmen('SW', tok, nur_offen=True); time.sleep(0.05)
        w = warte(lambda: k0.offen('SW'))
        print(f'Token {tok!r}: angenommen={ok}; bis zum naechsten 011: {w:.3f} s; dabei ausgegeben: {"".join(r.sw.text[n:])!r}')
    stop.set(); r.abbrechen(); tr.schliessen(); shutil.rmtree(d, ignore_errors=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
