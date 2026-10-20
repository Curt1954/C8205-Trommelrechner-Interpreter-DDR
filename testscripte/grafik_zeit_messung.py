# -*- coding: utf-8 -*-
"""
grafik_zeit_messung.py - Misst, wie stark Pult-Fenster, Lampenabtastung und HW-Check-Fenster die Echtzeit der Befehlsausfuehrung stoeren.
Version: ZM-001

Idee: Die Trommel (C-Modul) dreht sich in Echtzeit (Wortzeit 104 us). Jeder Trommelzugriff des Rechner-Threads wartet auf seinen Sektor.
Kommt eine Anforderung wegen einer Verzoegerung im Python-Prozess (GIL-Wechsel, Abtast-Thread, Tk-Takt) zu spaet, verpasst sie ihren Sektor
und wartet bis zu eine Umdrehung (31 Wortzeiten, 3,2 ms). Gemessen wird deshalb dasselbe Endlosprogramm (Last) in mehreren Aufbauten:

  rechner       nur Rechner + Trommel (Grundlinie, kein Pult, kein Tk)
  abtastung     + PultSteuerung mit Lampen-Abtast-Thread (alle 2 ms), Hauptthread schlaeft
  takt_python   + Pult-Takt (tick() und zeichenliste() alle 40 ms im Hauptthread) ohne Abtastung, ohne Tk
  tk_ohne_abt   + echtes Tk-Pult-Fenster, aber ohne Abtast-Thread               (braucht Tkinter und eine Anzeige)
  tk            + echtes Tk-Pult-Fenster mit Abtast-Thread                      (wie der normale Betrieb)
  tk_hw         + echtes Tk-Pult-Fenster, Abtast-Thread und HW-Check-Fenster    (wie --HWCHECK)

Jeder Aufbau laeuft mit der Voreinstellung des Switch-Intervalls (5 ms) und optional mit einem kleineren (--sw), jeweils --wiederholungen mal.
Jede Messung laeuft in einem eigenen Python-Prozess (kein Einfluss von Lauf zu Lauf).

Last: trommeloptimale Endlosschleife aus 32 Befehlen auf den Adressen 0000 bis 0037 (Sektor = Adresse & 037): abwechselnd 211 (laden) und
240 (speichern) mit Operanden im Bereich 3000 bis 3037, am Ende 000 0000 (Sprung nach 0000). Die Trommel schaltet je Wortzeit um 13 Sektoren
weiter; der Operand liegt zwei Wortzeiten nach dem Befehl, der naechste Befehl (Adresse + 1) fuenf Wortzeiten nach dem Befehl, so dass
jeder Zugriff ohne Umdrehung bedient wird (ungestoert ca. 2,5 Wortzeiten Wartezeit je Zugriff, ca. 3700 Zugriffe/s, ca. 0,5 ms je Befehl).
Verzoegert sich der Rechner-Thread auch nur um einen halben Schlitz (ca. 50 us), verpasst er den Sektor und wartet 31 Wortzeiten (3,2 ms):
genau das macht die Last empfindlich fuer Stoerungen. Die Trommel startet mit fester Lage (PERM-Index 0).

Kennzahlen je Messfenster (Mittel ueber --dauer Sekunden nach --warm Sekunden Einlauf):
  zugriffe/s   Trommelzugriffe pro Sekunde (Durchsatz; kleiner = langsamer)
  wartetick    mittlere Wartezeit je Zugriff in Wortzeiten (groesser = mehr verpasste Sektoren)
  verspaetung  mittlere Verspaetung, mit der der Trommel-Thread (C) aufwacht, in us (Mass fuer die allgemeine Systemlast)
  max_verspaetung_us  groesste Verspaetung seit Programmstart (nicht nur im Messfenster)

Aufruf (aus dem Projektordner):
  python3 testscripte/grafik_zeit_messung.py                         alle Aufbauten, 5 s, 3 Wiederholungen
  python3 testscripte/grafik_zeit_messung.py --dauer 10 --sw 0.0001  Switch-Intervall 0,1 ms zusaetzlich zur Voreinstellung
  python3 testscripte/grafik_zeit_messung.py --varianten rechner,abtastung
  python3 testscripte/grafik_zeit_messung.py --liste
Ergebnis: Tabelle auf dem Bildschirm und testscripte/zeit_messung_ergebnis.csv.
Tk-Aufbauten ohne Tkinter oder ohne Anzeige werden uebersprungen (in der Entwicklungsumgebung gab es kein Tkinter: diese Aufbauten sind dort NICHT gelaufen).
Hinweis: Fuer vergleichbare Werte nichts anderes auf dem Rechner laufen lassen und alle Aufbauten in einem Aufruf messen.
"""
import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time

HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)
VERSION_MESSUNG = 'ZM-001'

#             Pult   Abtastung  Takt(py)  Tk     HW-Check
VARIANTEN = {
    'rechner':     dict(pult=False, abt=False, takt=False, tk=False, hw=False),
    'abtastung':   dict(pult=True,  abt=True,  takt=False, tk=False, hw=False),
    'takt_python': dict(pult=True,  abt=False, takt=True,  tk=False, hw=False),
    'tk_ohne_abt': dict(pult=True,  abt=False, takt=True,  tk=True,  hw=False),
    'tk':          dict(pult=True,  abt=True,  takt=True,  tk=True,  hw=False),
    'tk_hw':       dict(pult=True,  abt=True,  takt=True,  tk=True,  hw=True),
}

WORTZEITEN_BIS_OPERAND = 2      # Operand liegt 2 Wortzeiten (je +13 Sektoren) nach dem Befehl; der naechste Befehl (+1 Sektor) dann 5 Wortzeiten nach dem Befehl


def programm(j1=WORTZEITEN_BIS_OPERAND):
    """Trommelzeilen {Adresse: 11 Oktalstellen} der Endlosschleife (Format wie Trommel/trommel.txt: 4 Stellen zweite Adresse, 4 Stellen Adresse, 3 Stellen Operation)."""
    p = {}
    for i in range(32):
        if i == 31:
            p[i] = '00000000000'                                     # 000 0000: Sprung nach 0000 (Sektor 0 = Sektor 31 + 1)
        else:
            operand = 0o3000 + ((i + 13 * j1) % 32)
            p[i] = f'0000{operand:04o}' + ('211' if i % 2 == 0 else '240')
    return p


# ----------------------------------------------------------------------------------------------------------------------------
# Kindprozess: eine Messung
# ----------------------------------------------------------------------------------------------------------------------------
def trommel_kopie(ordner):
    """Kopie der Projekt-Trommeldatei mit dem Endlosprogramm."""
    quelle = os.path.join(PROJ, 'Trommel', 'trommel.txt')
    ziel = os.path.join(ordner, 'trommel.txt')
    with open(quelle, encoding='utf-8') as f:
        zeilen = f.read().split('\n')
    prog = programm()
    for i, z in enumerate(zeilen):
        if len(z) >= 5 and z[4] == ':':
            adr = int(z[:4], 8)
            if adr in prog:
                zeilen[i] = f'{adr:04o}: {prog[adr]}'
    with open(ziel, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(zeilen))
    return ziel


def messung(var, sw, dauer, warm):
    """Eine Messung in diesem Prozess; Rueckgabe dict (oder dict mit 'uebersprungen')."""
    sys.path.insert(0, PROJ)
    sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
    spec = VARIANTEN[var]
    if sw:
        sys.setswitchinterval(sw)
    if spec['tk']:
        try:
            import tkinter
            wurzel = tkinter.Tk()
            wurzel.destroy()
        except Exception as e:
            return {'uebersprungen': f'Tkinter/Anzeige nicht verfuegbar: {type(e).__name__}: {e}'}
    import c8205_grafik as G
    from grafik_trommel import GrafikTrommel
    import grafik_pult as P

    d = tempfile.mkdtemp()
    tr = r = s = None
    stop = threading.Event()
    try:
        tr = GrafikTrommel(trommel_kopie(d), start_index=0)
        r = G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), tr, pult_modus=True)

        def rechner_starten():
            r.taste('H')
            r.taste('SW=0')
            r.thread_modus = True
            threading.Thread(target=G.rechner_schleife, args=(r, stop), name='rechner', daemon=True).start()

        if spec['pult']:
            s = P.PultSteuerung(os.path.join(PROJ, 'pult'), r, hochlauf_s=0.05, auslauf_s=0.05, tastenzeit_s=0.05)
            if not spec['abt']:
                s.starte_abtastung = lambda: None
            s.bei_betrieb = rechner_starten
            s.bei_ende = lambda: (stop.set(), r.abbrechen())
            jetzt = time.monotonic()
            s.netz_klick(jetzt)
            if not spec['tk']:
                s.tick(jetzt + 1)                    # Hochlauf vorbei: BETRIEB, Abtastung und Rechner-Thread starten
        else:
            rechner_starten()

        ergebnis = {}

        def stat():
            return dict(tr.T.statistik())

        def start_lauf():
            for t in ('H', 'G', 'R'):
                r.pult_taste(t)

        def auswerten(s0, t0, s1, t1):
            dt = t1 - t0
            dz = s1['zugriffe'] - s0['zugriffe']
            dw = s1['wartezeit_summe_ticks'] - s0['wartezeit_summe_ticks']
            da = s1['aufwachen'] - s0['aufwachen']
            dv = s1['verspaetung_summe_ns'] - s0['verspaetung_summe_ns']
            return dict(dauer_s=round(dt, 3), zugriffe_s=round(dz / dt, 1), wartetick=round(dw / dz, 4) if dz else None,
                        verspaetung_us=round(dv / da / 1000, 2) if da else None, ticks_s=round((s1['ticks'] - s0['ticks']) / dt, 1),
                        max_verspaetung_us=round(s1['verspaetung_max_ns'] / 1000, 1))

        if spec['tk']:
            ergebnis = messung_tk(G, r, s, tr, spec, warm, dauer, start_lauf, stat, auswerten)
        else:
            if spec['pult']:
                while s.netz != P.BETRIEB:
                    time.sleep(0.01)
            time.sleep(0.2)
            start_lauf()
            t_frist = time.monotonic() + 5
            while not getattr(r, 'laeuft', False) and time.monotonic() < t_frist:
                time.sleep(0.01)
            if not getattr(r, 'laeuft', False):
                return {'fehler': 'Rechner lief nach R nicht an'}
            t_lauf = time.monotonic()
            s0 = None
            while True:
                jetzt = time.monotonic()
                if s0 is None and jetzt - t_lauf >= warm:
                    s0, t0 = stat(), jetzt
                if s0 is not None and jetzt - t0 >= dauer:
                    s1, t1 = stat(), jetzt
                    break
                if spec['takt']:
                    s.tick(jetzt)
                    s.zeichenliste()
                    time.sleep(max(0.0, P.LAMPENTAKT_S - (time.monotonic() - jetzt)))
                else:
                    time.sleep(0.01)
            ergebnis = auswerten(s0, t0, s1, t1)
            ergebnis['laeuft_am_ende'] = bool(r.laeuft)
        return ergebnis
    finally:
        stop.set()
        try:
            if s is not None:
                s.netz = P.ENDE                  # beendet den Abtast-Thread
            if r is not None:
                r.abbrechen()
            if tr is not None:
                tr.schliessen()
        except Exception:
            pass
        shutil.rmtree(d, ignore_errors=True)


def messung_tk(G, r, s, tr, spec, warm, dauer, start_lauf, stat, auswerten):
    """Aufbau mit echtem Tk-Fenster: Tk-Hauptschleife im Hauptthread; Start und Ende der Messung per after()."""
    from grafik_pult_fenster import PultFenster
    from grafik_pult import BETRIEB
    f = PultFenster(s, os.path.join(PROJ, 'pult'))
    if spec['hw']:
        from grafik_hwcheck import HwCheckFenster
        f.zusatz.append(HwCheckFenster(f.root, r.m))
    z = {}

    def r_starten():
        start_lauf()
        f.root.after(int(warm * 1000), s_start)

    def s_start():
        z['s0'], z['t0'] = stat(), time.monotonic()
        z['laeuft0'] = bool(r.laeuft)
        f.root.after(int(dauer * 1000), s_ende)

    def s_ende():
        z['s1'], z['t1'] = stat(), time.monotonic()
        z['laeuft1'] = bool(r.laeuft)
        f.beenden()

    def pruefe_betrieb():
        if s.netz == BETRIEB and r.thread_modus:
            f.root.after(200, r_starten)
        else:
            f.root.after(50, pruefe_betrieb)

    f.root.after(100, pruefe_betrieb)
    f.starten()                                   # blockiert bis f.beenden()
    if 's1' not in z:
        return {'fehler': 'Tk-Messung wurde nicht abgeschlossen (Fenster vorzeitig beendet?)'}
    erg = auswerten(z['s0'], z['t0'], z['s1'], z['t1'])
    erg['laeuft_am_ende'] = z['laeuft1']
    if not z['laeuft0']:
        erg['warnung'] = 'Rechner lief zu Beginn des Messfensters noch nicht'
    return erg


# ----------------------------------------------------------------------------------------------------------------------------
# Elternprozess: Messreihe
# ----------------------------------------------------------------------------------------------------------------------------
def kind_aufrufen(var, sw, dauer, warm):
    cmd = [sys.executable, '-I', os.path.abspath(__file__), '--einzel', var, '--dauer', str(dauer), '--warm', str(warm)]
    if sw:
        cmd += ['--sw', str(sw)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=dauer + warm + 60)
    except subprocess.TimeoutExpired:
        return {'fehler': 'Zeitueberschreitung'}
    for zeile in reversed(p.stdout.splitlines()):
        if zeile.startswith('ERGEBNIS '):
            return json.loads(zeile[9:])
    return {'fehler': f'keine Ausgabe (Rueckgabecode {p.returncode}): ' + (p.stderr.strip().splitlines() or ['?'])[-1]}


def median(werte):
    w = [x for x in werte if x is not None]
    return statistics.median(w) if w else None


def reihe(args):
    varianten = [v.strip() for v in args.varianten.split(',') if v.strip()]
    for v in varianten:
        if v not in VARIANTEN:
            sys.exit(f'unbekannter Aufbau {v!r}; --liste zeigt die Namen')
    sws = [None] + [float(x) for x in args.sw.split(',') if x.strip()]
    zeilen = []
    print(f'Zeitmessung {VERSION_MESSUNG}: {len(varianten)} Aufbauten x {len(sws)} Switch-Intervalle x {args.wiederholungen} Wiederholungen, je {args.warm:g} s Einlauf + {args.dauer:g} s Messung')
    print(f'Python {sys.version.split()[0]}, Voreinstellung Switch-Intervall {sys.getswitchinterval() * 1000:g} ms\n')
    for sw in sws:
        for v in varianten:
            lauefe = []
            for i in range(args.wiederholungen):
                e = kind_aufrufen(v, sw, args.dauer, args.warm)
                e.update(variante=v, sw_ms=(sw * 1000 if sw else sys.getswitchinterval() * 1000), lauf=i + 1)
                lauefe.append(e)
                zeilen.append(e)
                if 'uebersprungen' in e or 'fehler' in e:
                    print(f'  {v:12s} sw={e["sw_ms"]:g} ms: {e.get("uebersprungen") or e.get("fehler")}')
                    break
                print(f'  {v:12s} sw={e["sw_ms"]:6.3g} ms  Lauf {i + 1}: {e["zugriffe_s"]:9.1f} Zugriffe/s  Warte {e["wartetick"]:.3f} Ticks  Verspaetung {e["verspaetung_us"]:.1f} us')
    # Zusammenfassung
    print('\nZusammenfassung (Median der Wiederholungen); Abweichung gegen die Grundlinie "rechner" mit demselben Switch-Intervall')
    print(f'{"Aufbau":12s} {"sw/ms":>7s} {"Zugriffe/s":>11s} {"vs. Grund":>10s} {"Warte/Tick":>11s} {"vs. Grund":>10s} {"Verspaet./us":>13s}')
    grund = {}
    for e in zeilen:
        if e['variante'] == 'rechner' and 'zugriffe_s' in e:
            grund.setdefault(e['sw_ms'], []).append(e)
    for sw in sws:
        swm = sw * 1000 if sw else sys.getswitchinterval() * 1000
        g = grund.get(swm)
        gz = median([e['zugriffe_s'] for e in g]) if g else None
        gw = median([e['wartetick'] for e in g]) if g else None
        for v in varianten:
            es = [e for e in zeilen if e['variante'] == v and e['sw_ms'] == swm and 'zugriffe_s' in e]
            if not es:
                print(f'{v:12s} {swm:7.3g} {"(keine Messung)":>11s}')
                continue
            z, w, vs = median([e['zugriffe_s'] for e in es]), median([e['wartetick'] for e in es]), median([e['verspaetung_us'] for e in es])
            dz = f'{(z / gz - 1) * 100:+.1f} %' if gz else '-'
            dw = f'{(w / gw - 1) * 100:+.1f} %' if gw else '-'
            print(f'{v:12s} {swm:7.3g} {z:11.1f} {dz:>10s} {w:11.3f} {dw:>10s} {vs:13.1f}')
    pfad = os.path.join(HIER, 'zeit_messung_ergebnis.csv')
    felder = ['variante', 'sw_ms', 'lauf', 'dauer_s', 'zugriffe_s', 'wartetick', 'verspaetung_us', 'max_verspaetung_us', 'ticks_s', 'laeuft_am_ende', 'uebersprungen', 'fehler', 'warnung']
    with open(pfad, 'w', encoding='utf-8') as f:
        f.write(';'.join(felder) + '\n')
        for e in zeilen:
            f.write(';'.join(str(e.get(k, '')) for k in felder) + '\n')
    print(f'\nEinzelwerte: {pfad}')
    print('Lesehilfe: weniger Zugriffe/s und mehr Warte/Tick gegenueber der Grundlinie = der Aufbau stoert die Echtzeit. Schwankt schon die Grundlinie '
          'zwischen den Laeufen stark, sind die Unterschiede nicht belastbar (laenger messen, Rechner ruhig lassen).')


def main():
    ap = argparse.ArgumentParser(description='Misst den Einfluss von Pult, Abtastung und HW-Check auf die Echtzeit der Befehlsausfuehrung.')
    ap.add_argument('--dauer', type=float, default=5.0, help='Messfenster in s (Standard 5)')
    ap.add_argument('--warm', type=float, default=1.0, help='Einlaufzeit nach dem Start in s (Standard 1)')
    ap.add_argument('--wiederholungen', type=int, default=3)
    ap.add_argument('--varianten', default=','.join(VARIANTEN), help='kommagetrennt, Standard: alle')
    ap.add_argument('--sw', default='', help='zusaetzliche Switch-Intervalle in s, kommagetrennt, z. B. 0.0001 (Voreinstellung 0.005 wird immer gemessen)')
    ap.add_argument('--liste', action='store_true', help='Aufbauten auflisten')
    ap.add_argument('--einzel', help='intern: eine Messung in diesem Prozess')
    args = ap.parse_args()
    if args.liste:
        for k, v in VARIANTEN.items():
            print(f'{k:12s} ' + ', '.join(n for n, an in v.items() if an) if any(v.values()) else f'{k:12s} nur Rechner')
        return 0
    if args.einzel:
        sw = float(args.sw) if args.sw else None
        try:
            erg = messung(args.einzel, sw, args.dauer, args.warm)
        except Exception as e:
            import traceback
            traceback.print_exc()
            erg = {'fehler': f'{type(e).__name__}: {e}'}
        print('ERGEBNIS ' + json.dumps(erg), flush=True)
        os._exit(0)                                # Hintergrund-Threads (Trommel, Abtastung) nicht abwarten
    reihe(args)
    return 0


if __name__ == '__main__':
    sys.exit(main())
