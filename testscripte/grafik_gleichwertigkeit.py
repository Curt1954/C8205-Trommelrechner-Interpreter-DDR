#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_gleichwertigkeit.py - Abnahmewerkzeug Stufe 1 (Kern und Trommel):
Spielt vorhandene Tests aus Tests/ zweimal ab und vergleicht die Ergebnisse:
  (A) mit dem bisherigen TEST-Verfahren (c8205_interp.lauf, rechnerische Trommel, alle Zeiten 0),
  (B) mit dem GRAFIK-Kern (c8205_grafik.Rechner, echte Trommel ueber das C-Modul), Tasten einzeln, K0-Zeichen ueber die Warteschlange.
  (C) mit --neue-geraete: wie (B), aber Leser und Stanzer sind die NEUEN Klassen (grafik_geraete.GrafikLeser/GrafikStanzer, Checkpoint 4);
      nur Tests, die Leser oder Stanzer benutzen. Der Leser wartet am Bandende aktiv (Review F-11) statt zu enden: das Werkzeug bricht
      dieses Warten nach 1,5 s ab und meldet es als "ABWEICHUNG GEWOLLT" (nur dort, wo TEST am Bandende mit Meldung endet).
Verglichen werden: Register und Flags, Trommelinhalt (Datei, Byte fuer Byte), Schreibwerk-Ausgabe, Stanzerdatei, Ergebnis der
Pruefungen der Testdatei. Ausgenommen sind die Zeiten (GRAFIK_Beschreibung §1 (alt: Dok. 00 Abschnitt 3.6)).
Jeder Lauf geschieht in einem eigenen Arbeitsordner mit eigener Kopie der Trommeldatei (die gemeinsame trommel.txt bleibt unberuehrt).

Aufruf:  python3 testscripte/grafik_gleichwertigkeit.py [--alle | TEST ...] [--zeit SEK] [--bericht DATEI] [--neue-geraete]
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

HIER = os.path.dirname(os.path.abspath(__file__))
PROJEKT = os.path.dirname(HIER)


def finde_tests():
    d = os.path.join(PROJEKT, 'Tests')
    return sorted(f for f in os.listdir(d) if f.endswith(('.txt', '.test')))


def nutzt_geraete(name):
    with open(os.path.join(PROJEKT, 'Tests', name), encoding='utf-8') as fh:
        return any(z.startswith(('--leser', '--stanzer', '--pruefe-stanzer')) for z in fh)


def neuer_leser(pfad, arbeitsverz, k):
    """GrafikLeser fuer einen Pfad aus einer Testdatei. Eine Datei (oder die Dateien eines Ordners) werden in einen eigenen Ordner
    kopiert, weil der neue Leser gelesene Dateien in den LOCHSTREIFENKORB verschiebt. Der Leser wartet am Bandende; nach 1,5 s Warten
    bricht der Haken ab (GrafikAbbruch), damit das Werkzeug nicht haengt."""
    from grafik_geraete import GrafikLeser
    from grafik_trommel import GrafikAbbruch
    ziel = os.path.join(arbeitsverz, f'leser_neu_{k}')
    os.makedirs(ziel)
    if os.path.isdir(pfad):
        quellen = [os.path.join(pfad, n) for n in sorted(os.listdir(pfad)) if os.path.isfile(os.path.join(pfad, n))]
    else:
        quellen = [pfad]
    for i, q in enumerate(quellen):
        shutil.copyfile(q, os.path.join(ziel, f'{i:04d}_{os.path.basename(q)}'))
    frist = [None]

    def haken():
        if frist[0] is None:
            frist[0] = time.time() + 1.5
        elif time.time() > frist[0]:
            raise GrafikAbbruch('Leser wartet am Bandende')
    return GrafikLeser(ziel, nr=k, aufruf_beim_warten=haken)


# ------------------------------------------------------------------------------------------------------------------
# Kindprozess: ein Test in einer Betriebsart
# ------------------------------------------------------------------------------------------------------------------
def kind(art, testname, arbeitsverz, ausgabe):
    sys.path.insert(0, PROJEKT); sys.path.insert(0, os.path.join(PROJEKT, 'grafik-interpreter-module'))
    import random
    random.seed(20261017)      # Machine() waehlt die Anfangs-Zeichenlage des Schreibwerks zufaellig (KB/GB); fuer den Vergleich festhalten
    import c8205_interp as I
    os.chdir(arbeitsverz)
    here = PROJEKT
    pfad = os.path.join(PROJEKT, 'Tests', testname)
    t = I.Test(pfad)
    trommel_pfad = os.path.join(arbeitsverz, 'trommel.txt')
    ergebnis = dict(art=art, test=testname)
    if t.fehler:
        ergebnis.update(uebersprungen='Formfehler der Testdatei: ' + '; '.join(t.fehler[:3]))
        json.dump(ergebnis, open(ausgabe, 'w', encoding='utf-8'))
        return
    I.GERAETE.update(leser1=None, leser2=None, stanzer1=None, sw_ausgabe=None, k0=None, pruefe_stanzer1=None, pruefe_sw_ausgabe=None)
    for k in ('leser1', 'leser2', 'stanzer1', 'sw_ausgabe', 'k0'):
        I.GERAETE[k] = t.geraete.get(k)
    if I.dateipruefungen(t).get('pruefe_stanzer1') and not I.GERAETE['stanzer1']:
        I.GERAETE['stanzer1'] = os.path.join(arbeitsverz, 'virtuelle_Geraete', 'Stanzer1')    # Ersatz fuer das fehlende --stanzer1
    vorab = list(I.vorab_geraete(t)) + list(I.vorab_trommel(t))
    if vorab:
        ergebnis.update(uebersprungen='Vorab-Pruefung negativ: ' + '; '.join(vorab[:3]))
        json.dump(ergebnis, open(ausgabe, 'w', encoding='utf-8'))
        return
    mdverz = os.path.join(PROJEKT, 'markdown-dateien')
    graph = I.load_graph(os.path.join(mdverz, 'C8205-Interpreter-Eingänge_der_Knoten.md'))
    I.load_t2(os.path.join(mdverz, 'C8205-Interpreter-Beschreibung_der_Knoten.md'))

    sw_capture = []
    stanzer_neu = [None]

    class Senke:
        unterdruecken = False

        def schreibe(self, s):
            sw_capture.append(s)

    if art == 'test':
        I.sw_schreibe = lambda m, s: sw_capture.append(s)
        trommel = I.Trommel(trommel_pfad)
        r = I.lauf(t, graph, None, '/dev/null', trommel)
        m = r['m']
        ok, grund = r['ok'], r['grund']
        pruef = I.pruefe_ergebnis(t, m)
        trommel_inhalt = lambda: open(trommel_pfad, 'rb').read()
        trommel.schliessen()
    else:
        import c8205_grafik as G
        from grafik_trommel import GrafikTrommel
        # Ausgangszustand der Trommel wie lauf(): #TROMMEL=LEER, danach die Zeilen der Testdatei (direkt in die Datei, vor dem Einschalten)
        if t.trommel_vor == 'LEER':
            I.schreibe_leere_trommeldatei(trommel_pfad)
        mem = {}
        with open(trommel_pfad, encoding='utf-8', newline='') as fh:
            for z in fh:
                mm = I.TROMMEL_ZEILE_RE.match(z)
                mem[int(mm.group(1), 8)] = int(mm.group(2), 8)
        mem.update({a & I.MASK12: w & I.MASK33 for a, w in t.mem.items()})
        with open(trommel_pfad, 'w', encoding='utf-8', newline='') as fh:
            fh.write(''.join(f'{a:04o}: {mem.get(a, 0):011o}\n' for a in range(4096)))
        trommel = GrafikTrommel(trommel_pfad)
        rech = G.Rechner(graph, trommel, pult_modus=False)
        m = rech.m
        rech.sw = Senke()
        m.sw_datei = rech.sw
        if t.ac_init is not None:
            m.AC = t.ac_init
        if t.bz_init is not None:
            m.BZ = t.bz_init
        for k, key in ((1, 'leser1'), (2, 'leser2')):
            if I.GERAETE[key]:
                m.leser[k] = neuer_leser(I.GERAETE[key], arbeitsverz, k) if art == 'grafik2' else I.Leser(I.GERAETE[key])
        if I.GERAETE['stanzer1']:
            if art == 'grafik2':
                from grafik_geraete import GrafikStanzer
                stanzer_neu[0] = os.path.join(arbeitsverz, 'stanzer_neu')
                m.stanzer = GrafikStanzer(stanzer_neu[0])
            else:
                m.stanzer = I.Stanzer(I.GERAETE['stanzer1'])
        # K0-Zeichen: Zeilen der K0-Datei(en) in der Reihenfolge von K0Quelle, ueber die Warteschlange eingespeist; kein Dateiende-Warten
        k0 = m.k0
        k0.ende_wenn_leer = True
        if I.GERAETE['k0']:
            st = I._Stapel(I.GERAETE['k0'], 'K0-Eingabe-Pfad nicht gefunden')
            for datei in st._scan():
                for z in open(datei, encoding='utf-8'):
                    z = z.rstrip('\r\n')
                    if z == '' or z.startswith('#'):
                        continue
                    k0.einspeisen(z if len(z) == 1 else z.strip())
        from grafik_trommel import GrafikAbbruch
        try:
            ok_tasten, eff = rech.folge(t.tasten)
            if not ok_tasten:
                ok, grund, pruef = False, 'Tastenfolge nicht gueltig/definiert', None
            elif m.halted or m.fl['H']:
                ok = True
                grund = m.halt_grund if m.halted else 'Halt (Schalter H): Tastenfolge endet ohne R'
                pruef = I.pruefe_ergebnis(t, m)
            else:
                ir_tab = {ir['nach']: ir for ir in t.interrupts}
                zustand = {'cur': None}

                def hook(rr):
                    if not ir_tab:
                        return None
                    cur = zustand['cur']
                    if cur is not None and cur in ir_tab and m.BZ == ((cur + 1) & I.MASK12):
                        ir = ir_tab[cur]
                        zustand['cur'] = None
                        m.br_aufgestellt = m.br_tasten_m = m.vor_phase2 = m.bz_g = False
                        m.vor_phase1 = True
                        try:
                            ok_i, eff_i = rr.folge(ir['tokens'])
                        except I.LaufFehler as e:
                            return ('fehler', str(e))
                        m.vor_phase1 = False
                        letzte = ir['tokens'][-1].upper()
                        if not ok_i:
                            return ('fehler', f'Tastenfolge nicht gueltig (INTERRUPT Testzeile {ir["nr"]})')
                        if m.halted:
                            return ('ende', m.halt_grund)
                        if letzte == 'ST':
                            m.fl['H'] = 0
                        if letzte in ('R', 'ST'):
                            node = I.eintritt_br(m) if m.br_aufgestellt else 1
                            m.br_aufgestellt = False
                            return ('neu', node)
                        return ('ende', f'Halt (Schalter H): INTERRUPT nach Befehl {I.octs(cur, 4)} endet ohne R/ST')
                    zustand['cur'] = m.BZ
                    return None

                res = rech.lauf(grenz_hook=hook)
                ok, grund = res['ok'], res['grund']
                pruef = I.pruefe_ergebnis(t, m)
        except GrafikAbbruch as e:
            ok, grund, pruef = False, 'LESER-WARTET: ' + str(e), None
        trommel_inhalt = lambda: open(trommel_pfad, 'rb').read()
        ergebnis['trommel_statistik'] = trommel.statistik()
        trommel.schliessen()

    def datei(p):
        return open(p, 'rb').read().decode('utf-8', 'replace') if p and os.path.isfile(p) else None
    stanzer = None
    if I.GERAETE['stanzer1']:
        if stanzer_neu[0]:
            stanzer = datei(os.path.join(stanzer_neu[0], 'stanzer.ls'))
        else:
            sp = I.GERAETE['stanzer1']
            sp = os.path.join(sp, 'stanzer-ausgabe.txt') if os.path.isdir(sp) or sp.endswith(('/', '\\')) else sp
            stanzer = datei(sp)
    ergebnis.update(
        ok=ok, grund=grund,
        regs=dict(BZ=m.BZ, AC=m.AC, AR=m.AR, OR=m.OR, adr=m.adr, fl=dict(m.fl)),
        trommel_sha=hashlib.sha256(trommel_inhalt()).hexdigest(),
        sw=''.join(sw_capture), stanzer=stanzer,
        pruefung=None if pruef is None else dict(wahr=pruef[0], zeilen=pruef[1]),
    )
    json.dump(ergebnis, open(ausgabe, 'w', encoding='utf-8'), ensure_ascii=False)


# ------------------------------------------------------------------------------------------------------------------
# Elternprozess
# ------------------------------------------------------------------------------------------------------------------
KINDER = set()                       # laufende Kindprozesse (eigene Sitzung): bei Strg+C werden sie alle beendet (G4-018)
_MINIMAL = {'pfad': None}
_MINIMAL_LOCK = threading.Lock()


def braucht_minimalprogramm(name):
    """Tests, die das Minimalprogramm auf der Trommel voraussetzen (Kopfzeile). Sie laufen sonst ueber das Bandende hinaus und warten dort
    (der Leser wartet aktiv auf das naechste Band) bis zur Zeitgrenze: 2 x 120 s je Test (G4-018)."""
    with open(os.path.join(PROJEKT, 'Tests', name), encoding='utf-8') as fh:
        return any('Voraussetzung: Minimalprogramm auf der Trommel' in z for z in fh)


def minimal_trommel():
    """Einmal je Werkzeuglauf: Startdatei mit geladenem Minimalprogramm, erzeugt wie Schritt 1 von c8205_bis_test.sh (TEST-Interpreter,
    Tests/pj2-bis_minimalprogramm.test) auf einer Kopie der gemeinsamen trommel.txt. Gibt den Pfad der Datei zurueck (None bei Fehler)."""
    with _MINIMAL_LOCK:
        if _MINIMAL['pfad'] is None:
            d = tempfile.mkdtemp(prefix='c8205_minimal_')
            shutil.copyfile(os.path.join(PROJEKT, 'virtuelle_Geraete', 'Trommel', 'trommel.txt'), os.path.join(d, 'trommel.txt'))
            os.symlink(os.path.join(PROJEKT, 'Tests'), os.path.join(d, 'Tests'))
            shutil.copytree(os.path.join(PROJEKT, 'virtuelle_Geraete'), os.path.join(d, 'virtuelle_Geraete'))
            try:                                       # derselbe Kindprozess wie ein Test (schreibt keine Protokolle ins Projekt)
                subprocess.run([sys.executable, '-I', os.path.abspath(__file__), '--kind', 'test', 'pj2-bis_minimalprogramm.test', d,
                                os.path.join(d, 'ergebnis.json')],
                               cwd=d, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
            except Exception:
                _MINIMAL['pfad'] = ''
                return None
            _MINIMAL['pfad'] = os.path.join(d, 'trommel.txt')
    return _MINIMAL['pfad'] or None


def alle_kinder_beenden():
    for p in list(KINDER):
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass


def starte_kind(art, testname, zeit):
    arbeit = tempfile.mkdtemp(prefix=f'c8205_{art}_')
    try:
        shutil.copytree(os.path.join(PROJEKT, 'virtuelle_Geraete'), os.path.join(arbeit, 'virtuelle_Geraete'))
        os.symlink(os.path.join(PROJEKT, 'Tests'), os.path.join(arbeit, 'Tests'))
        start = minimal_trommel() if braucht_minimalprogramm(testname) else None
        shutil.copyfile(start or os.path.join(PROJEKT, 'virtuelle_Geraete', 'Trommel', 'trommel.txt'), os.path.join(arbeit, 'trommel.txt'))
        out = os.path.join(arbeit, 'ergebnis.json')
        print(f'  ... starte {art:6s} {testname}', file=sys.stderr, flush=True)
        # Ausgabe in Dateien statt Pipes und eigene Prozessgruppe: bei Zeitueberschreitung wird die ganze Gruppe beendet; ein Enkelprozess,
        # der Pipes offen haelt, kann den Elternprozess so nicht mehr blockieren.
        fo = open(os.path.join(arbeit, 'kind.out'), 'wb'); fe = open(os.path.join(arbeit, 'kind.err'), 'wb')
        p = subprocess.Popen([sys.executable, '-I', os.path.abspath(__file__), '--kind', art, testname, arbeit, out],
                             stdout=fo, stderr=fe, cwd=arbeit, stdin=subprocess.DEVNULL, start_new_session=True)
        KINDER.add(p)
        try:
            p.wait(timeout=zeit)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except Exception:
                p.kill()
            try:
                p.wait(timeout=10)
            except Exception:
                pass
            return dict(art=art, test=testname, zeitueberschreitung=zeit)
        finally:
            KINDER.discard(p)
            fo.close(); fe.close()
        if not os.path.isfile(out):
            rest = (open(os.path.join(arbeit, 'kind.err'), errors='replace').read() or open(os.path.join(arbeit, 'kind.out'), errors='replace').read())
            return dict(art=art, test=testname, absturz=rest[-1500:])
        return json.load(open(out, encoding='utf-8'))
    finally:
        shutil.rmtree(arbeit, ignore_errors=True)


def vergleiche(a, b):
    if 'uebersprungen' in a or 'uebersprungen' in b:
        return 'UEBERSPRUNGEN', [a.get('uebersprungen') or b.get('uebersprungen')]
    for x in (a, b):
        if 'absturz' in x:
            return 'ABSTURZ', [f'{x["art"]}: {x["absturz"]}']
        if 'zeitueberschreitung' in x:
            return 'ZEIT', [f'{x["art"]}: Zeitueberschreitung {x["zeitueberschreitung"]} s']
    if str(b.get('grund') or '').startswith('LESER-WARTET'):
        return 'ABWEICHUNG GEWOLLT (Leser wartet am Bandende)', [f'TEST: ok={a.get("ok")} grund={a.get("grund")!r:.150}']
    diffs = []
    for k in ('ok', 'regs', 'trommel_sha', 'sw', 'stanzer', 'pruefung'):
        if a.get(k) != b.get(k):
            diffs.append(f'{k}: TEST={a.get(k)!r:.200} GRAFIK={b.get(k)!r:.200}')
    if a.get('grund') != b.get('grund'):
        diffs.append(f'grund (Hinweis): TEST={a.get("grund")!r:.120} GRAFIK={b.get("grund")!r:.120}')
        if len(diffs) == 1:
            return 'GLEICH (Haltgrund-Text abweichend)', diffs
    return ('GLEICH' if not diffs else 'UNGLEICH'), diffs


def lauf_test(name, zeit, art_b='grafik'):
    a = starte_kind('test', name, zeit)
    b = starte_kind(art_b, name, zeit)
    status, diffs = vergleiche(a, b)
    return name, status, diffs, a, b


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == '--kind':
        kind(*sys.argv[2:6])
        return 0
    ap = argparse.ArgumentParser()
    ap.add_argument('tests', nargs='*')
    ap.add_argument('--alle', action='store_true')
    ap.add_argument('--zeit', type=float, default=120.0, help='Zeitgrenze je Lauf in Sekunden')
    ap.add_argument('--parallel', type=int, default=2)
    ap.add_argument('--bericht')
    ap.add_argument('--neue-geraete', action='store_true', help='nur Tests mit Leser/Stanzer, Leser und Stanzer als neue Klassen (GrafikLeser, GrafikStanzer)')
    args = ap.parse_args()
    namen = finde_tests() if args.alle or not args.tests else [os.path.basename(t) for t in args.tests]
    art_b = 'grafik'
    if args.neue_geraete:
        art_b = 'grafik2'
        namen = [n for n in namen if nutzt_geraete(n)]
    zaehler = {}
    zeilen = []
    ex = concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel)
    try:
        for name, status, diffs, a, b in ex.map(lambda n: lauf_test(n, args.zeit, art_b), namen):
            zaehler[status] = zaehler.get(status, 0) + 1
            z = f'{status:38s} {name}'
            print(z, flush=True)
            zeilen.append(z)
            if status != 'GLEICH':
                for d in diffs:
                    print('      ', d, flush=True)
                    zeilen.append('      ' + d)
    except KeyboardInterrupt:
        alle_kinder_beenden()                                  # Kinder laufen in eigener Sitzung und bekaemen Strg+C sonst nicht
        ex.shutdown(wait=False, cancel_futures=True)
        print('\nAbgebrochen (Strg+C); laufende Kindprozesse beendet.', file=sys.stderr)
        return 130
    finally:
        alle_kinder_beenden()
        ex.shutdown(wait=False, cancel_futures=True)
    print('\nZusammenfassung:', ', '.join(f'{k}: {v}' for k, v in sorted(zaehler.items())), f'(von {len(namen)})')
    if args.bericht:
        with open(args.bericht, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(zeilen) + '\n\nZusammenfassung: ' + ', '.join(f'{k}: {v}' for k, v in sorted(zaehler.items())) + '\n')
    return 0 if all(k in ('GLEICH', 'GLEICH (Haltgrund-Text abweichend)', 'UEBERSPRUNGEN') or k.startswith('ABWEICHUNG GEWOLLT') for k in zaehler) else 1


if __name__ == '__main__':
    sys.exit(main())
