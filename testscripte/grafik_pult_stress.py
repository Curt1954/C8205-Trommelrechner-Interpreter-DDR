# -*- coding: utf-8 -*-
"""Stresstest Pult <-> Rechner (ohne Fenster): ein 'Tk-Thread' (Hauptthread) klickt zufaellig auf alle Tasten und ruft tick() auf,
der Rechner-Thread laeuft wie im echten Betrieb. Haengt ein Klick laenger als 3 s, werden alle Threads ausgegeben (Exit 1).
Aufruf: python3 -I testscripte/grafik_pult_stress.py [Sekunden] [Seed]"""
import os, sys, random, shutil, tempfile, threading, time, faulthandler
HIER = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HIER); sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
import c8205_grafik as G
from grafik_trommel import GrafikTrommel
from grafik_pult import PultSteuerung, BETRIEB

def main(dauer=20, seed=1):
    rnd = random.Random(seed)
    d = tempfile.mkdtemp(); kopie = os.path.join(d, 'trommel.txt')
    shutil.copy(os.path.join(PROJ, 'Trommel', 'trommel.txt'), kopie)
    tr = GrafikTrommel(kopie); r = G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), tr, pult_modus=True)
    s = PultSteuerung(os.path.join(PROJ, 'pult'), r, hochlauf_s=0.01, auslauf_s=0.01, tastenzeit_s=0.05)
    stop = threading.Event()
    s.bei_betrieb = lambda: (r.taste('H'), r.taste('SW=0'), setattr(r, 'thread_modus', True), threading.Thread(target=G.rechner_schleife, args=(r, stop), daemon=True).start())
    s.bei_ende = lambda: (stop.set(), r.abbrechen())
    tasten = ['H','R','H','R','E','M','G','UE','ST','K0','K1','K2','K3','T','SW','SP','BS','LS','SW_umschalt',
              '0','1','2','3','4','5','6','7','8','9','PLUS','MINUS','KOMMA','PUNKT','DOPPELPUNKT','ZR','B','D']
    s.netz_klick(time.monotonic()); s.tick(time.monotonic() + 1)
    assert s.netz == BETRIEB
    t_ende = time.time() + dauer; n = 0; fehler = {}
    while time.time() < t_ende:
        t = rnd.choice(tasten); jetzt = time.monotonic()
        faulthandler.dump_traceback_later(3, exit=True)          # haengt dieser Schritt > 3 s: alle Threads ausgeben, Ende
        try:
            s.klick(t, jetzt, umschalt=rnd.random() < 0.15)
        except Exception as e:                                  # Tk meldet Ausnahmen in Rrueckrufen und macht weiter
            fehler[type(e).__name__] = fehler.get(type(e).__name__, 0) + 1
        if rnd.random() < 0.5: s.loslassen(rnd.choice('EM'), time.monotonic())
        s.tick(time.monotonic()); s.zeichenliste()
        faulthandler.cancel_dump_traceback_later()
        n += 1; time.sleep(rnd.choice([0, 0.001, 0.005, 0.02, 0.05]))
    print(f'OK: {n} Klicks in {dauer} s ohne Haenger (Seed {seed}); Rechner laeuft={r.laeuft}; Ausnahmen im Klick: {fehler}')
    stop.set(); r.abbrechen(); tr.schliessen(); shutil.rmtree(d, ignore_errors=True)

if __name__ == '__main__':
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 20, int(sys.argv[2]) if len(sys.argv) > 2 else 1)
