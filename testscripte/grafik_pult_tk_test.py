#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_pult_tk_test.py - Test der Pult-TASTENBEDIENUNG des GRAFIK-Interpreters MIT echtem Tkinter-Fenster.
Version: PTK-001 (Pilotversuch des Verfahrens)

VERFAHREN (je Testfall):
  1. TEST-Anforderung: Das Skript schreibt eine Testdatei fuer den TEST-Interpreter (#TROMMEL=LEER, Zellen, Tastenfolge, Pruefungen).
  2. TEST-Lauf: c8205_interp.py fuehrt sie aus. Nur wenn die Pruefungen stimmen (Rueckgabewert 0), gilt die Trommel als geeignet
     initialisiert und das Soll als richtig. (Sonst wird der Fall NICHT im GRAFIK-Interpreter versucht.)
  3. Das Skript schreibt die Anfangs-Trommel (alle 4096 Zellen) und eine KLICKSPUR (Dateiformat "C8205-Klickspur 1"):
     Netzschalter ein, die Tastenfolge als Pult-Klicks mit Zeitabstaenden, Netzschalter aus.
  4. GRAFIK-Lauf: c8205_grafik.py --WIEDERGABE SPUR --DEBUGLOG LOG --trommel KOPIE ... Das Pult-Fenster oeffnet sich, spielt die
     Klickspur selbst ab (wie Mausklicks, ohne Tk-Mausereignis) und endet mit dem Netzschalter-Aus von selbst. Zeitgrenze: Spurdauer + 40 s.
  5. AUSWERTUNG nach dem Ende des Interpreters, aus dem Debug-Log: Wiedergabe vollstaendig und ohne Abweichung der Wirkung, die
     Tokens an den Rechner, der letzte Rechnerzustand (BZ, AC, AR, Flags) gegen das Soll des TEST-Laufs, keine FEHLER/WATCHDOG-Zeilen;
     danach die Trommeldatei (Speicherzellen) gegen das Soll.
  Ergebnis: Bericht (bericht.txt) und ein ZIP des ganzen Ergebnisordners zum Zurueckschicken.

Das Fenster nicht anfassen, solange der Test laeuft (die Wiedergabe ignoriert Maus und Tastatur ohnehin).
Aufruf (aus dem Projektordner):
  python3 testscripte/grafik_pult_tk_test.py                  alle Faelle
  python3 testscripte/grafik_pult_tk_test.py --faelle pk-001,pk-004
  python3 testscripte/grafik_pult_tk_test.py --xvfb           Linux ohne Bildschirm: Fenster auf einem virtuellen Display (xvfb-run)
  python3 testscripte/grafik_pult_tk_test.py --langsam 2      alle Zeitabstaende der Klickspur verdoppeln (langsamer Rechner)
  python3 testscripte/grafik_pult_tk_test.py --ohne-tk        TROCKENLAUF: dieselbe Wiedergabe im selben Prozess OHNE Fenster
                                                              (prueft das Skript und das Pult-Modell, NICHT Tkinter)
  python3 testscripte/grafik_pult_tk_test.py --nur-test       nur Schritt 1 und 2
Rueckgabewert 0 nur, wenn alle gewaehlten Faelle bestanden haben.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime

VERSION_PTK = 'PTK-001'
PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------------------------------------------------------------------------------------------------------------
# Testfaelle. Jeder Fall: Name, Beschreibung, Speicherzellen (Anfangsbelegung, sonst 0), Tastenfolge (wie in TEST-Testdateien),
# Soll (Zeile der Pruefungen) und Soll-Speicherzellen. Die Faelle pk-001 bis pk-008 sind aus den TEST-Tests tk-001 bis tk-008 abgeleitet (pk-007 mit Aenderung, siehe dort).
# ----------------------------------------------------------------------------------------------------------------------
SOLL_STOPP5 = 'BZ=0001 AC=00000000000 AR=0005 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0'
FAELLE = [
    dict(name='pk-001_H_G_M_R', text='Tastenfolge H G M R: M ergibt BR = 0000 025, R fuehrt aus; Stopp 020 in Zelle 0000.',
         zellen={0o0000: '00000005020'}, folge='H G M R', soll=SOLL_STOPP5, speicher={0o0000: '00000005020'}),
    dict(name='pk-002_H_G_Mplus_E_Mminus_M_R', text='H G M+ E M- M R: E unter M, danach M, R (AC linksverschoben).',
         zellen={0o0001: '00000010020'}, folge='H G M+ E M- M R',
         soll='BZ=0002 AC=00000004000 AR=0010 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0', speicher={0o0001: '00000010020'}),
    dict(name='pk-003_H_G_UE_R', text='H G Ue R: Transport AC nach 7777, danach Stopp aus Zelle 0000.',
         zellen={0o0000: '00000005020', 0o7777: '00000000555'}, folge='H G Ü R', soll=SOLL_STOPP5,
         speicher={0o0000: '00000005020', 0o7777: '00000000000'}),
    dict(name='pk-004_H_G_Mplus_E_Mminus_UE_R', text='H G M+ E M- Ue R: E unter M, Ue stellt 7777 240 ein, R transportiert AC nach 7777.',
         zellen={0o0001: '00000010020', 0o7777: '00000000555'}, folge='H G M+ E M- Ü R',
         soll='BZ=0002 AC=00000002000 AR=0010 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0',
         speicher={0o0001: '00000010020', 0o7777: '00000002000'}),
    dict(name='pk-005_H_G_Mplus_E_Mminus_ST_R', text='H G M+ E M- ST R: ST nimmt die Stopp-Wirkung zurueck, der Lauf geht bis zum zweiten Stopp.',
         zellen={0o0001: '00000010020', 0o0002: '00000020020'}, folge='H G M+ E M- ST R',
         soll='BZ=0003 AC=00000002000 AR=0020 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0',
         speicher={0o0001: '00000002000', 0o0002: '00000020020'}),
    dict(name='pk-006_ST_R_ohne_Stopp', text='ST R ohne vorherigen Stopp: ST ist wirkungslos.',
         zellen={0o0000: '00000005020'}, folge='ST R', soll=SOLL_STOPP5, speicher={0o0000: '00000005020'}),
    dict(name='pk-007_R_UE_Rollensperre', text='R Ue: In Stellung R ist Ue mechanisch gesperrt (Rollensperre); 7777 bleibt unveraendert. '
                                              '(Im Pult steht H beim Einschalten, deshalb nicht dasselbe wie tk-007.)',
         ohne_test='Rollensperre ist eine Pult-Eigenschaft; der TEST-Interpreter kann "R Ü" nicht ausdruecken (Tastenfolge nicht gueltig). Soll von Hand: wie pk-006.',
         zellen={0o0000: '00000005020', 0o7777: '00000000555'}, folge='R Ü', soll=SOLL_STOPP5,
         speicher={0o0000: '00000005020', 0o7777: '00000000555'}),
    dict(name='pk-008_H_G_UE_E', text='H G Ue E: Einzelschritt, haelt vor Knoten 19; 7777 wird mit AC = 0 beschrieben.',
         zellen={0o0000: '00000005020', 0o7777: '00000000555'}, folge='H G Ü E', soll=SOLL_STOPP5,
         speicher={0o0000: '00000005020', 0o7777: '00000000000'}),
]

# Zeitabstaende der Klickspur (Sekunden, mit --langsam multipliziert). Hochlauf und Auslauf dauern mit --STUMM --netz-schnell je 0,3 s.
T_START = 1.0        # erster Tastenklick nach dem Netzschalter
T_TASTE = 0.6        # nach einer Taste
T_E = 1.0            # nach E (Einzelschritt im Rechner-Thread)
T_R = 2.5            # nach R (Lauf bis zum Halt)
T_LOS = 0.15         # Klick auf M oder E bis zum Loslassen
T_NETZ_AUS = 0.8     # letzte Taste bis Netzschalter aus
ROLLENGESPERRT = {'E', 'M', 'G', 'UE', 'T', 'SW'}      # wie grafik_pult.ROLLENGESPERRT (nur zur Vorhersage der Wirkung)


# ----------------------------------------------------------------------------------------------------------------------
# Hilfen: Dateien
# ----------------------------------------------------------------------------------------------------------------------
def trommel_text(zellen):
    return ''.join(f'{a:04o}: {zellen.get(a, "00000000000")}\n' for a in range(4096))


def trommel_lesen(pfad):
    out = {}
    with open(pfad, encoding='utf-8') as f:
        for z in f:
            m = re.match(r'^([0-7]{4}):\s*([0-7]{11})', z)
            if m:
                out[int(m.group(1), 8)] = m.group(2)
    return out


def testdatei_text(fall):
    z = ['Trommeldatei:', f'#DOK-0001 {fall["text"]}', '#PROT STUFE=2', '#TROMMEL=LEER']
    z += [f'{a:04o}: {w}' for a, w in sorted(fall['zellen'].items())]
    z += ['', 'Tastenfolge:', fall['folge'], '', 'Prüfungen:', fall['soll']]
    z += [f'{a:04o}: {w}' for a, w in sorted(fall['speicher'].items())]
    return '\n'.join(z) + '\n'


def md5(pfad):
    with open(pfad, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


# ----------------------------------------------------------------------------------------------------------------------
# Klickspur und erwartete Tokens
# ----------------------------------------------------------------------------------------------------------------------
def baue_spur(folge, faktor=1.0):
    """Tastenfolge (TEST-Schreibweise) -> (Ereignisse, erwartete Tokens an den Rechner).
    Ereignis: (t, art, taste, umschalt, wirkt). Die Wirkung (wirkt) wird aus einem kleinen Modell vorhergesagt; die Wiedergabe meldet
    jede Abweichung im Log (ABWEICHUNG). Beim Start ist H eingerastet (Startstellung)."""
    f = faktor
    t = T_START * f
    ev = [(0.0, 'klick', 'NETZ', False, True)]
    tokens = []
    stellung, halter = 'H', set()

    def klick(taste, umschalt, wirkt, nach):
        nonlocal t
        ev.append((t, 'klick', taste, umschalt, wirkt))
        return nach

    for tok in folge.split():
        u = tok.upper().replace('Ü', 'UE')
        gesperrt = stellung == 'R' and u in ROLLENGESPERRT
        if u == 'H':
            w = stellung != 'H'
            klick('H', False, w, T_TASTE)
            if w:
                stellung = 'H'
                tokens.append('H')
            t += T_TASTE * f
        elif u == 'R':
            w = stellung != 'R' and not halter
            klick('R', False, w, T_R)
            if w:
                stellung = 'R'
                tokens.append('R')
            t += T_R * f
        elif u in ('M', 'E'):                       # Klick und Loslassen: u+ und u-
            w = not gesperrt and u not in halter
            klick(u, False, w, 0)
            if w:
                ev.append((t + T_LOS * f, 'los', u, False, None))
                tokens += [u + '+', u + '-']
            t += (T_E if u == 'E' else T_TASTE) * f
        elif u in ('M+', 'M-'):                     # Halter: Umschalt+Klick
            taste = u[0]
            w = not gesperrt
            klick(taste, True, w, T_TASTE)
            if w:
                if taste in halter:
                    halter.discard(taste)
                    tokens.append(taste + '-')
                else:
                    halter.add(taste)
                    tokens.append(taste + '+')
            t += T_TASTE * f
        elif u in ('G', 'UE', 'ST', 'K0', 'K1', 'K2', 'K3'):
            w = not gesperrt
            klick(u, False, w, T_TASTE)
            if w:
                tokens.append(u)
            t += T_TASTE * f
        else:
            raise ValueError(f'Taste {tok!r} wird von diesem Skript noch nicht in Klicks umgesetzt')
    t += (T_NETZ_AUS - T_TASTE) * f
    ev.append((t, 'klick', 'NETZ', False, True))
    return ev, tokens


def spur_schreiben(pfad, ev, kopf):
    with open(pfad, 'w', encoding='utf-8') as f:
        f.write('# C8205-Klickspur 1\n')
        for k, v in kopf.items():
            f.write(f'# {k}: {v}\n')
        for t, art, taste, umschalt, wirkt in ev:
            if art == 'klick':
                f.write(f'{t:9.3f} klick {taste}{" umschalt" if umschalt else ""} wirkt={int(bool(wirkt))}\n')
            else:
                f.write(f'{t:9.3f} los {taste}\n')


# ----------------------------------------------------------------------------------------------------------------------
# Laeufe
# ----------------------------------------------------------------------------------------------------------------------
def umgebung():
    env = dict(os.environ)
    env['PYTHONWARNINGS'] = 'ignore::ResourceWarning'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def test_lauf(testdatei, ordner):
    """TEST-Interpreter auf einer eigenen Trommelkopie. Rueckgabe (rc, Ausgabetext)."""
    cmd = [sys.executable, os.path.join(PROJEKT, 'c8205_interp.py'), '--MODUS=TEST',
           '--trommel', os.path.join(ordner, 'test_trommel.txt'), '--out', os.path.join(ordner, 'test_protokoll'), testdatei]
    p = subprocess.run(cmd, cwd=PROJEKT, env=umgebung(), capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def grafik_lauf(ordner, spur, dauer, xvfb):
    """GRAFIK-Interpreter mit Fenster, Wiedergabe und Debug-Log. Rueckgabe (rc oder None bei Zeitgrenze, Dauer in s)."""
    for d in ('Leser1', 'Leser2', 'Stanzer1'):
        os.makedirs(os.path.join(ordner, d), exist_ok=True)
    cmd = [sys.executable, os.path.join(PROJEKT, 'c8205_grafik.py'), '--STUMM', '--netz-schnell', '--BASP', '000000',
           '--trommel', os.path.join(ordner, 'trommel.txt'),
           '--leser1', os.path.join(ordner, 'Leser1'), '--leser2', os.path.join(ordner, 'Leser2'), '--stanzer1', os.path.join(ordner, 'Stanzer1'),
           '--WIEDERGABE', spur, '--DEBUGLOG', os.path.join(ordner, 'debug.log')]
    if xvfb:
        cmd = ['xvfb-run', '-a'] + cmd
    grenze = dauer + 40.0
    t0 = time.monotonic()
    with open(os.path.join(ordner, 'grafik_stdout.txt'), 'w', encoding='utf-8') as so, \
            open(os.path.join(ordner, 'grafik_stderr.txt'), 'w', encoding='utf-8') as se:
        p = subprocess.Popen(cmd, cwd=PROJEKT, env=umgebung(), stdout=so, stderr=se)
        try:
            rc = p.wait(timeout=grenze)
        except subprocess.TimeoutExpired:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
            rc = None
    return rc, time.monotonic() - t0


def grafik_lauf_ohne_tk(ordner, spur, dauer):
    """TROCKENLAUF: dieselbe Wiedergabe im selben Prozess, ohne Fenster (Takt und Wiedergabe von Hand getrieben). NICHT Tkinter."""
    sys.path.insert(0, PROJEKT); sys.path.insert(0, os.path.join(PROJEKT, 'grafik-interpreter-module'))
    import grafik_debuglog as DL
    import c8205_grafik as G
    from grafik_trommel import GrafikTrommel
    from grafik_pult import PultSteuerung, ENDE
    for d in ('Leser1', 'Leser2', 'Stanzer1'):
        os.makedirs(os.path.join(ordner, d), exist_ok=True)
    DL.starten(os.path.join(ordner, 'debug.log'))
    DL.log('START', f'TROCKENLAUF ohne Tk (grafik_pult_tk_test.py {VERSION_PTK})')
    tr = GrafikTrommel(os.path.join(ordner, 'trommel.txt'), basp='000000')
    r = G.Rechner(G.lade_graph(os.path.join(PROJEKT, 'markdown-dateien')), tr, pult_modus=True)
    G.richte_geraete_ein(r, os.path.join(ordner, 'Leser1'), os.path.join(ordner, 'Leser2'), os.path.join(ordner, 'Stanzer1'))
    stop = threading.Event()

    def bei_betrieb():
        r.taste('H')
        r.taste('SW=0')
        r.thread_modus = True
        threading.Thread(target=G.rechner_schleife, args=(r, stop), name='rechner', daemon=True).start()

    def bei_ende():
        stop.set()
        r.abbrechen()

    s = PultSteuerung(os.path.join(PROJEKT, 'pult'), r, hochlauf_s=0.3, auslauf_s=0.3, bei_betrieb=bei_betrieb, bei_ende=bei_ende)
    s.klick_log = lambda z: DL.log('KLICK', z)
    kopf, ev = DL.lade_klickspur(spur)
    w = DL.Wiedergabe(s, ev)
    t0 = time.monotonic()
    w.starten(t0)
    rc = 0
    try:
        while True:
            jetzt = time.monotonic()
            w.faellige(jetzt)
            if s.tick(jetzt) == ENDE:
                break
            if jetzt - t0 > dauer + 40.0:
                rc = None
                stop.set()
                r.abbrechen()
                break
            time.sleep(0.005)
    finally:
        tr.schliessen()
        DL._L.f.close()
        DL._L = None
    return rc, time.monotonic() - t0


# ----------------------------------------------------------------------------------------------------------------------
# Auswertung des Debug-Logs
# ----------------------------------------------------------------------------------------------------------------------
ZEILE = re.compile(r'^\s*(\d+\.\d+) \[(.{12})\] (\S+)\s+(.*)$')


def log_lesen(pfad):
    out = []
    with open(pfad, encoding='utf-8', errors='replace') as f:
        for z in f:
            m = ZEILE.match(z.rstrip('\n'))
            if m:
                out.append((float(m.group(1)), m.group(3), m.group(4)))
    return out


def zustand_parsen(text):
    teil = text.split(' | ', 1)[1] if ' | ' in text else text
    return dict(re.findall(r'(\w+)=(\S+)', teil))


def auswerten(fall, ev, tokens_soll, ordner, rc, dauer):
    """Rueckgabe (Liste (ok, Text) der Einzelpruefungen)."""
    erg = []

    def pr(ok, text):
        erg.append((bool(ok), text))

    pr(rc == 0, f'Interpreter beendet sich selbst, Rueckgabewert 0 (ist: {"Zeitgrenze" if rc is None else rc}, Dauer {dauer:.1f} s)')
    logpfad = os.path.join(ordner, 'debug.log')
    if not os.path.isfile(logpfad):
        pr(False, 'Debug-Log fehlt')
        return erg
    zeilen = log_lesen(logpfad)
    pr(any(k == 'START' for _, k, _ in zeilen), 'Debug-Log beginnt mit START')

    # Wiedergabe vollstaendig, ohne Abweichung der Wirkung
    beginn = [x for _, k, x in zeilen if k == 'WIEDERGABE' and x.startswith('beginnt')]
    ende = [x for _, k, x in zeilen if k == 'WIEDERGABE' and x.startswith('Ende:')]
    n = len(ev)
    pr(beginn and f'{n} Ereignisse' in beginn[0], f'Wiedergabe beginnt mit {n} Ereignissen ({beginn[0] if beginn else "fehlt"})')
    pr(ende and f'Ende: {n} Ereignisse, 0 Abweichung(en)' in ende[0], f'Wiedergabe endet mit 0 Abweichungen der Wirkung ({ende[0] if ende else "Ende fehlt"})')
    abw = [x for _, k, x in zeilen if k == 'WIEDERGABE' and 'ABWEICHUNG' in x and not x.startswith('Ende:')]
    pr(not abw, 'keine Zeile mit ABWEICHUNG' + (': ' + abw[0] if abw else ''))

    # Tokens an den Rechner
    ist_tokens = [re.sub(r'^an den Rechner: ', '', x) for _, k, x in zeilen if k == 'TOKEN']
    pr(ist_tokens == tokens_soll, f'Tokens an den Rechner: soll {" ".join(tokens_soll)} | ist {" ".join(ist_tokens)}')

    # Fehler, Watchdog
    schlecht = [(k, x) for _, k, x in zeilen if k in ('FEHLER', 'WATCHDOG')]
    pr(not schlecht, 'keine FEHLER- und WATCHDOG-Zeilen' + (f': {schlecht[0][0]} {schlecht[0][1][:200]}' if schlecht else ''))
    langsam = [x for _, k, x in zeilen if k == 'LANGSAM']
    if langsam:
        pr(True, f'Hinweis: {len(langsam)} LANGSAM-Zeile(n), z. B. {langsam[0][:100]}')

    # Lauf nach R
    if 'R' in tokens_soll:
        pr(any(k == 'RECHNER' and x.startswith('Lauf endet') for _, k, x in zeilen), 'Lauf nach R hat geendet (Zeile "Lauf endet")')

    # letzter Rechnerzustand vor dem letzten Netzschalter-Klick
    letzter_netz = max((i for i, (_, k, x) in enumerate(zeilen) if k == 'WIEDERGABE' and 'klick NETZ' in x), default=len(zeilen))
    letzter = None
    for _, k, x in zeilen[:letzter_netz]:
        if k == 'RECHNER' and re.match(r'(Ausfuehrung Taste \S+ endet|Lauf endet|Taste \S+ abgebrochen)', x):
            letzter = x
    if letzter is None:
        pr(False, 'kein Rechnerzustand nach einer ausgefuehrten Taste im Log')
    else:
        ist = zustand_parsen(letzter)
        soll = dict(re.findall(r'(\w+)=(\S+)', fall['soll']))
        for k in ('BZ', 'AC', 'AR', 'FE', 'FUE', 'BS', 'US', 'E', 'A'):
            pr(ist.get(k) == soll.get(k), f'Zustand {k}: soll {soll.get(k)} | ist {ist.get(k)}')
        pr(True, 'Hinweis: V1 und V2 stehen nicht im Debug-Log und werden nicht geprueft')

    # Speicher nach dem Lauf (Trommeldatei)
    try:
        zellen = trommel_lesen(os.path.join(ordner, 'trommel.txt'))
        for a, w in sorted(fall['speicher'].items()):
            pr(zellen.get(a) == w, f'Trommel {a:04o}: soll {w} | ist {zellen.get(a)}')
    except OSError as e:
        pr(False, f'Trommeldatei nicht lesbar: {e}')

    # stderr
    try:
        err = open(os.path.join(ordner, 'grafik_stderr.txt'), encoding='utf-8', errors='replace').read()
        if 'Traceback' in err or 'FEHLER' in err:
            pr(False, 'grafik_stderr.txt enthaelt FEHLER/Traceback: ' + err.strip().splitlines()[-1][:200])
    except OSError:
        pass
    return erg


# ----------------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description='Pult-Tastentest GRAFIK (Klickspur + Debug-Log + Auswertung)')
    ap.add_argument('--faelle', help='kommagetrennt, z. B. pk-001,pk-004 (Namensanfang genuegt); Standard: alle')
    ap.add_argument('--ausgabe', help='Ergebnisordner (Standard: Test-Protokolle/pult_tk/<Zeitstempel>)')
    ap.add_argument('--langsam', type=float, default=1.0, help='Faktor fuer alle Zeitabstaende der Klickspur (Standard 1)')
    ap.add_argument('--xvfb', action='store_true', help='Linux: GRAFIK ueber xvfb-run auf einem virtuellen Display starten')
    ap.add_argument('--ohne-tk', action='store_true', help='Trockenlauf im selben Prozess ohne Fenster (kein Tkinter-Test)')
    ap.add_argument('--nur-test', action='store_true', help='nur TEST-Anforderung schreiben und mit dem TEST-Interpreter pruefen')
    args = ap.parse_args(argv)

    auswahl = FAELLE
    if args.faelle:
        wunsch = [x.strip() for x in args.faelle.split(',') if x.strip()]
        auswahl = [f for f in FAELLE if any(f['name'].startswith(w) for w in wunsch)]
        if not auswahl:
            print('FEHLER: kein Fall passt zu', args.faelle, '| vorhanden:', ', '.join(f['name'] for f in FAELLE))
            return 2
    zeit = datetime.now().strftime('%Y%m%d_%H%M%S')
    wurzel = os.path.abspath(args.ausgabe) if args.ausgabe else os.path.join(PROJEKT, 'Test-Protokolle', 'pult_tk', zeit)
    os.makedirs(wurzel, exist_ok=True)
    modus = 'nur TEST-Interpreter' if args.nur_test else ('TROCKENLAUF ohne Tk (kein Tkinter-Test)' if args.ohne_tk else 'GRAFIK mit Tkinter-Fenster')
    kopf = [f'Pult-Tastentest GRAFIK {VERSION_PTK}, {zeit}, {modus}, Python {sys.version.split()[0]}, {sys.platform}',
            f'Projekt: {PROJEKT}', f'Faelle: {len(auswahl)}, Zeitfaktor {args.langsam}']
    bericht = list(kopf)
    print('\n'.join(kopf))
    ergebnis = []
    for fall in auswahl:
        name = fall['name']
        ordner = os.path.join(wurzel, name)
        os.makedirs(ordner, exist_ok=True)
        zeilen = [f'\n=== {name}: {fall["text"]}', f'    Tastenfolge: {fall["folge"]}']
        status = 'FEHLER'
        try:
            # 1. TEST-Anforderung, 2. TEST-Lauf
            if fall.get('ohne_test'):
                zeilen.append('  HINWEIS TEST-Interpreter entfaellt fuer diesen Fall (Soll von Hand): ' + fall['ohne_test'])
            else:
                tdatei = os.path.join(ordner, name + '.test')
                with open(tdatei, 'w', encoding='utf-8') as f:
                    f.write(testdatei_text(fall))
                rc, text = test_lauf(tdatei, ordner)
                with open(os.path.join(ordner, 'test_ausgabe.txt'), 'w', encoding='utf-8') as f:
                    f.write(text)
                if rc != 0:
                    zeilen.append(f'  FEHLER  TEST-Interpreter: Pruefung nicht bestanden oder Lauf fehlerhaft (Rueckgabewert {rc}); '
                                  f'der Fall wird im GRAFIK-Interpreter NICHT versucht. Siehe test_ausgabe.txt')
                    raise StopIteration
                zeilen.append('  OK      TEST-Interpreter: Anforderung bestanden (Trommel geeignet, Soll bestaetigt)')
            if args.nur_test:
                status = 'OK'
                raise StopIteration
            # 3. Anfangs-Trommel und Klickspur
            with open(os.path.join(ordner, 'trommel.txt'), 'w', encoding='utf-8') as f:
                f.write(trommel_text(fall['zellen']))
            shutil.copy(os.path.join(ordner, 'trommel.txt'), os.path.join(ordner, 'trommel_anfang.txt'))
            ev, tokens = baue_spur(fall['folge'], args.langsam)
            spur = os.path.join(ordner, 'klickspur.txt')
            spur_schreiben(spur, ev, {'fall': name, 'trommel_md5': md5(os.path.join(ordner, 'trommel.txt')), 'erzeugt von': f'grafik_pult_tk_test.py {VERSION_PTK}'})
            dauer = ev[-1][0]
            # 4. GRAFIK-Lauf
            print(f'  {name}: GRAFIK-Lauf, Klickspur {dauer:.1f} s ...', flush=True)
            rc, gedauert = grafik_lauf_ohne_tk(ordner, spur, dauer) if args.ohne_tk else grafik_lauf(ordner, spur, dauer, args.xvfb)
            # 5. Auswertung
            pruef = auswerten(fall, ev, tokens, ordner, rc, gedauert)
            for ok, t in pruef:
                zeilen.append(f'  {"OK     " if ok else "FEHLER "} {t}')
            status = 'OK' if all(ok for ok, _ in pruef) else 'FEHLER'
        except StopIteration:
            pass
        except Exception as e:                    # ein Fehler im Skript soll die anderen Faelle nicht verhindern
            import traceback
            zeilen.append(f'  FEHLER  Skriptfehler: {type(e).__name__}: {e}')
            with open(os.path.join(ordner, 'skriptfehler.txt'), 'w', encoding='utf-8') as f:
                f.write(traceback.format_exc())
        zeilen.append(f'  ==> {name}: {status}')
        ergebnis.append((name, status))
        bericht += zeilen
        print('\n'.join(zeilen), flush=True)

    ok_n = sum(1 for _, s in ergebnis if s == 'OK')
    summe = f'\nSUMME: {ok_n} von {len(ergebnis)} Faellen bestanden' + (' - ALLE OK' if ok_n == len(ergebnis) else ' - FEHLER, siehe oben')
    bericht.append(summe)
    print(summe)
    with open(os.path.join(wurzel, 'bericht.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(bericht) + '\n')
    zip_pfad = shutil.make_archive(wurzel, 'zip', os.path.dirname(wurzel), os.path.basename(wurzel))
    print(f'Ergebnisordner: {wurzel}\nZum Zurueckschicken:  {zip_pfad}')
    return 0 if ok_n == len(ergebnis) else 1


if __name__ == '__main__':
    sys.exit(main())
