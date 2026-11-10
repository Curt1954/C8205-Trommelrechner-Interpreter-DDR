# -*- coding: utf-8 -*-
"""
grafik_takt_tests.py - Prueft die abschaltbare Taktmitschrift (--taktprotokoll, grafik_takt.py TP-001, GRAFIK G4-025, grafik_trommel.py G5-002).
Version: TT-001 (08.11.2026)

Arbeitet auf einer Kopie der Trommel im Temp-Ordner (Trommel/trommel.txt bleibt unveraendert). Kleines Programm: Sprung, laden (211), speichern (240),
Diagnose (164), Halt (020); feste Startlage (PERM-Index 5), damit die virtuelle Zeit genau gleich bleibt.

Prueft:
  1. Mit und ohne Mitschrift sind vt, Wartezeitsumme, Zugriffe, BZ und AC gleich (die Mitschrift veraendert nichts).
  2. Stetigkeit: vt der naechsten Zeile = vt + n der Zeile davor; erste Zeile = vt am Anfang; Kopf und Endzeile vorhanden.
  3. Summe der Wartezeiten (L und S) und Zahl der Zugriffe stimmen mit der Trommelstatistik ueberein; Phase I steht nur bei Knoten 2.
  4. Zwei Laeufe mit gleicher Startlage ergeben byte-gleiche Dateien.
  5. --takt-max: Mitschrift endet nach N Zeilen mit '# ABGEBROCHEN', die Uhr laeuft unveraendert weiter.
  6. Fehlerfall: --taktprotokoll mit --trommelzeit alt endet mit Rueckkehrcode 16 und legt keine Datei an.
  7. Ende zu Ende ueber die Kommandozeile (hauptprogramm), Rueckkehrcode 0, Datei stetig.
Aufruf (aus dem Projektstamm):  python3 testscripte/grafik_takt_tests.py     Ende: 'grafik_takt_tests: N Pruefungen, M Fehler', Rueckkehrcode 0 = in Ordnung.
"""
import contextlib, io, os, shutil, sys, tempfile

HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [HIER, os.path.join(HIER, 'grafik-interpreter-module'), os.path.join(HIER, 'c-module', 'python')]
import c8205_grafik as G
import grafik_takt as TP
import grafik_trommel as GT

PROGRAMM = {0o0000: 0o00000003000, 0o0001: 0o17, 0o0002: 0, 0o0003: 0o1211, 0o0004: 0o2240, 0o0005: 0o1164, 0o0006: 0o20}
FEHLER = []
ANZAHL = 0


def pruefe(bedingung, text):
    global ANZAHL
    ANZAHL += 1
    if not bedingung:
        FEHLER.append(text)
        print('FEHLER:', text)


def schreibe_trommel(pfad):
    with open(pfad, 'w', newline='\n') as f:
        for a in range(4096):
            f.write('%04o: %011o\n' % (a, PROGRAMM.get(a, 0)))


def lauf(ordner, name, takt_pfad=None, maximum=TP.STANDARD_MAX, start=5):
    kopie = os.path.join(ordner, name + '.txt')
    schreibe_trommel(kopie)
    t = GT.GrafikTrommel(kopie, basp='000000', start_index=start, zeitmodell='schnell')
    prot = None
    try:
        graph = G.lade_graph(os.path.join(HIER, 'markdown-dateien'))
        r = G.Rechner(graph, t, pult_modus=True)
        G.richte_geraete_ein(r, None, None, None)
        if takt_pfad:
            prot = TP.TaktProtokoll(takt_pfad, maximum=maximum, zeitmodell='schnell', vt0=t.vt)
            r.takt_einhaengen(prot)
        for taste in 'H G R'.split():
            r.taste(taste)
            r.lauf_wenn_gewuenscht()
        erg = dict(vt=t.vt, summe=t.wartezeit_summe, zugriffe=t.zugriffe, BZ=r.m.BZ, AC=r.m.AC, grund=r.letzter_grund)
        if prot:
            prot.schliessen()
        return erg
    finally:
        t.schliessen()


def lies(pfad):
    kopf, zeilen, ende = [], [], []
    for z in open(pfad, encoding='utf-8'):
        z = z.rstrip('\n')
        if z.startswith('# lfd') or z.startswith('# C8205'):
            kopf.append(z)
        elif z.startswith('#'):
            ende.append(z)
        else:
            zeilen.append(z.split('\t'))
    return kopf, zeilen, ende


def stetig(zeilen, vt0):
    erwartet = vt0
    for i, z in enumerate(zeilen):
        if int(z[0]) != i + 1 or int(z[1]) != erwartet:
            return False
        erwartet = int(z[1]) + int(z[9])
    return True


def main():
    with tempfile.TemporaryDirectory() as tmp:
        ohne = lauf(tmp, 'ohne')
        a = os.path.join(tmp, 'a.tsv')
        b = os.path.join(tmp, 'b.tsv')
        mit = lauf(tmp, 'mit_a', a)
        lauf(tmp, 'mit_b', b)
        pruefe(ohne['grund'] is not None and mit == ohne, f'mit und ohne Mitschrift gleich: {mit} gegen {ohne}')
        kopf, zeilen, ende = lies(a)
        vt0 = int(kopf[0].split('vt am Anfang ')[1].split()[0])
        pruefe(len(kopf) == 2 and len(ende) == 1 and ende[0].startswith('# Ende:'), 'Kopf (2 Zeilen) und Endzeile vorhanden')
        pruefe(len(zeilen) > 20, f'Zeilen vorhanden ({len(zeilen)})')
        pruefe(stetig(zeilen, vt0), 'Stetigkeit: vt = vt + n der Zeile davor, lfd ab 1')
        zug = [z for z in zeilen if z[2] in ('L', 'S')]
        pruefe(sum(int(z[9]) for z in zug) == ohne['summe'], 'Summe der Wartezeiten = Trommelstatistik')
        pruefe(len(zug) == ohne['zugriffe'], 'Zahl der Zugriffe = Trommelstatistik')
        pruefe(any(z[2] == 'S' for z in zug) and any(z[2] == 'L' for z in zug), 'Lese- und Schreibzugriffe getrennt (L, S)')
        pruefe(all(z[3] == '2' for z in zeilen if z[4] == 'I'), 'Phase I nur im Knoten 2')
        pruefe(all(z[10] == '-' for z in zeilen if z[2] == 'T') and all(z[10] != '-' for z in zug), 'Adresse nur bei L und S')
        pruefe(ohne['vt'] == int(ende[0].split('vt am Ende ')[1].split(',')[0]), 'vt am Ende in der Endzeile = vt der Trommel')
        pruefe(open(a, 'rb').read() == open(b, 'rb').read(), 'zwei Laeufe mit gleicher Startlage: byte-gleiche Dateien')
        c = os.path.join(tmp, 'c.tsv')
        klein = lauf(tmp, 'mit_c', c, maximum=5)
        k2, z2, e2 = lies(c)
        pruefe(len(z2) == 5 and len(e2) == 1 and e2[0].startswith('# ABGEBROCHEN'), f'--takt-max 5: 5 Zeilen und ABGEBROCHEN ({len(z2)}, {e2})')
        pruefe(klein == ohne, 'nach dem Abbruch der Mitschrift laeuft die Uhr unveraendert weiter')
        # Luecke (vt ausserhalb von tick und Zugriff fortgeschrieben, z. B. Zusatztrommel): Zeile Z, Zeitfolge bleibt lueckenlos
        g = os.path.join(tmp, 'g.tsv')
        p = TP.TaktProtokoll(g, vt0=10)
        p.knoten, p.phase = 9, 'II'
        p.tick(10, 1)
        p.tick(30, 1)
        p.zugriff('L', 31, 4, 0o1234)
        p.schliessen()
        k4, z4, e4 = lies(g)
        pruefe([z[2] for z in z4] == ['T', 'Z', 'T', 'L'] and z4[1][1] == '11' and z4[1][9] == '19' and stetig(z4, 10), f'Luecke als Z-Zeile: {[z[2] for z in z4]}')
        # Fehlerfall: Zeitmodell alt
        d = os.path.join(tmp, 'd.tsv')
        kopie = os.path.join(tmp, 'fehler.txt')
        schreibe_trommel(kopie)
        with contextlib.redirect_stderr(io.StringIO()) as err:
            rc = G.hauptprogramm(['--ohne-fenster', '--STUMM', '--trommel', kopie, '--taktprotokoll', d])
        pruefe(rc == G.RC_START and not os.path.exists(d) and 'trommelzeit' in err.getvalue(), f'alt: Rueckkehrcode {rc}, keine Datei')
        # Ende zu Ende ueber die Kommandozeile (Startlage zufaellig)
        e = os.path.join(tmp, 'e.tsv')
        kopie2 = os.path.join(tmp, 'cli.txt')
        schreibe_trommel(kopie2)
        aus = io.StringIO()
        with contextlib.redirect_stdout(aus):
            rc = G.hauptprogramm(['--ohne-fenster', '--STUMM', '--trommelzeit', 'schnell', '--trommel', kopie2,
                                  '--entwickler-tasten', 'H G R', '--taktprotokoll', e])
        k3, z3, e3 = lies(e)
        v3 = int(k3[0].split('vt am Anfang ')[1].split()[0])
        pruefe(rc == 0 and 'Taktprotokoll:' in aus.getvalue() and stetig(z3, v3) and e3 and e3[0].startswith('# Ende:'), f'Kommandozeile: rc {rc}, Datei stetig')
    print(f'grafik_takt_tests: {ANZAHL} Pruefungen, {len(FEHLER)} Fehler')
    return 1 if FEHLER else 0


if __name__ == '__main__':
    sys.exit(main())
