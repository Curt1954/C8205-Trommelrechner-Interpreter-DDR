#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_takt_schleife_tests.py - Prueft das Auswertungsskript grafik_takt_schleife.py (TS-002), Teil 1 (Schleifenauswahl) und Teil 2 (--takte).
Version: TY-002 (08.11.2026; --takte, Teil 2)

Arbeitet mit kleinen, von Hand gebauten Taktprotokollen (Format TP-001) im Temp-Ordner; kein GRAFIK-Lauf, kein Tkinter.
Prueft: Befehlsadresse aus der Zeile L/Knoten 9 (nicht aus BZ), OR/BR aus Phase III, Zyklen und Varianten um einen Anker, Kern, --op,
        Bereichsschreibweise mit xK, TSV-Datei, Rueckkehrcodes 0/2/4, Hinweis bei abgebrochenem Protokoll.
Aufruf (aus dem Projektstamm):  python3 testscripte/grafik_takt_schleife_tests.py     Ende: 'grafik_takt_schleife_tests: N Pruefungen, M Fehler'
"""
import contextlib, io, os, sys, tempfile

HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HIER, 'testscripte'))
import grafik_takt_schleife as S

FEHLER = []
ANZAHL = 0


def pruefe(bedingung, text):
    global ANZAHL
    ANZAHL += 1
    if not bedingung:
        FEHLER.append(text)
        print('FEHLER:', text)


def protokoll(pfad, folge, ende='# Ende: test', op=None):
    """folge: Liste von Befehlsadressen (int); op: Adresse -> (OR, BR). BZ wird absichtlich falsch (0001) geschrieben."""
    op = op or {}
    zeilen = ['# C8205 Taktprotokoll TP-001; Zeitmodell schnell; vt am Anfang 0', '# lfd\tvt\tart\tknoten\tphase\tBZ\tBR\tOR\tAC\tn\tadresse']
    vt, lfd = 0, 0
    for a in folge:
        o, b = op.get(a, ('240', 0o7600))
        for art, kn, ph, n, ad, orr in (('L', '9', 'II', 3, format(a, 'o').zfill(4), '000'), ('T', '15', 'III', 1, '-', o)):
            lfd += 1
            zeilen.append(f'{lfd}\t{vt}\t{art}\t{kn}\t{ph}\t0001\t{format(b, "o").zfill(4)}\t{orr}\t00000000000\t{n}\t{ad}')
            vt += n
        vt += 4                                   # Rest des Befehls (nur Zeitverlauf, fuer die Pruefung unwichtig)
    if ende:
        zeilen.append(ende)
    with open(pfad, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(zeilen) + '\n')


def lauf(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = S.hauptprogramm(argv)
    return rc, out.getvalue(), err.getvalue()


def main():
    with tempfile.TemporaryDirectory() as d:
        log = os.path.join(d, 'a.tsv')
        # Ablauf: Anker 0010; zwei Zyklen ueber 0011, ein Zyklus ueber 0013 (anderer Weg); 0020 ist ein 011-Befehl im Zyklus
        folge = [0o7, 0o10, 0o11, 0o12, 0o10, 0o11, 0o12, 0o10, 0o13, 0o20, 0o12, 0o10, 0o11, 0o12, 0o6]
        protokoll(log, folge, op={0o20: ('011', 0o300), 0o10: ('211', 0o301)})
        befehle, info = S.lese_protokoll(log)
        pruefe(len(befehle) == len(folge), f'Befehlszahl {len(befehle)} statt {len(folge)}')
        pruefe([b.adr for b in befehle] == folge, 'Befehlsadresse kommt aus der Zeile L/Knoten 9 (BZ ist absichtlich falsch)')
        pruefe(befehle[9].op == '011' and befehle[9].br == 0o300, 'OR/BR aus Phase III (Knoten 15)')
        pruefe(info['ende'] == '# Ende: test'.lstrip('# ') or info['ende'].startswith('Ende'), 'Endzeile erkannt')
        pruefe(not info['abgebrochen'] and info['ohne_phase3'] == 0, 'kein Abbruch, alle Befehle mit Phase III')

        pos, zyklen, davor, danach = S.zyklen_um(befehle, 0o10)
        pruefe(len(pos) == 4 and len(zyklen) == 3, f'Anker 0010: {len(pos)} Ausfuehrungen, {len(zyklen)} Zyklen (erwartet 4 und 3)')
        pruefe(davor == 1 and danach == 3, f'davor/danach {davor}/{danach} (erwartet 1/3)')
        var = S.varianten(zyklen)
        pruefe(len(var) == 2 and len(var[0][1]) == 2 and var[0][0] == (0o10, 0o11, 0o12), 'Varianten: haeufigste zuerst 0010 0011 0012 (2x)')
        pruefe(var[1][0] == (0o10, 0o13, 0o20, 0o12) and var[1][1] == [3], 'zweite Variante ueber 0013 und 0020, Zyklus Nr. 3')

        pruefe(S.bereiche([0o64, 0o65, 0o66, 0o64, 0o65, 0o66, 0o64, 0o65, 0o66]) == '0064-0066x3', 'Bereich mit Wiederholung 0064-0066x3')
        pruefe(S.bereiche([0o10, 0o13, 0o14]) == '0010 0013-0014', 'Bereiche getrennt bei Luecke')

        tsv = os.path.join(d, 'z.tsv')
        rc, out, err = lauf([log, '--befehl', '0010', '--tsv', tsv])
        pruefe(rc == 0, f'rc {rc} statt 0 bei --befehl 0010')
        pruefe('Ausfuehrungen: 4' in out and 'vollstaendige Zyklen: 3' in out and 'Varianten (verschiedene Adressfolgen): 2' in out, 'Kopf der Ausgabe')
        pruefe('0010 0011 0012'.replace(' ', '-') not in out and '0010-0012' in out, 'Variante als Bereich 0010-0012')
        pruefe('In jedem Zyklus enthalten (Kern): 0010 0012' in out, 'Kern = Anker und 0012')
        zeilen = [z for z in open(tsv, encoding='utf-8') if not z.startswith('#')]
        pruefe(len(zeilen) == 3 + 3 + 4 and zeilen[0].split('\t')[4] == '0010', f'TSV: {len(zeilen)} Zeilen (erwartet 10)')
        pruefe(all(len(z.rstrip('\n').split('\t')) == 11 for z in zeilen), 'TSV: elf Spalten')

        # Teil 2: im Hilfsprotokoll dauert jeder Befehl genau 8 Wortzeiten (Phase III bis Phase III)
        pruefe(S.takte_je_zyklus(befehle, pos) == [[8, 8, 8], [8, 8, 8], [8, 8, 8, 8]], 'Takte je Befehl und Zyklus aus vt_III')
        rc, out, err = lauf([log, '--befehl', '0010', '--takte', '--tsv', tsv])
        pruefe(rc == 0 and 'Takte je Zyklus: kleinste 24, groesste 24, Mittel 24.00  (2 Zyklen, Summe 48' in out, 'Variante 1: 24 Takte, 2 Zyklen')
        pruefe('kleinste 32, groesste 32, Mittel 32.00  (1 Zyklen' in out, 'Variante 2: 32 Takte')
        pruefe('Takte ueber alle 3 Zyklen: Summe 80, Mittel je Zyklus 26.667' in out, 'Gesamtmittel 80/3 = 26,667')
        zeilen = [z.rstrip('\n').split('\t') for z in open(tsv, encoding='utf-8') if not z.startswith('#')]
        pruefe(all(len(z) == 11 and z[10] == '8' for z in zeilen), 'TSV: elfte Spalte takte, je Befehl 8')
        rc, out, err = lauf([log, '--befehl', '0010'])
        pruefe('Takte ueber' not in out, 'ohne --takte keine Taktzeilen')

        rc, out, err = lauf([log, '--op', '011'])
        pruefe('OR 011: Befehle an den Adressen 0020' in out, '--op 011 nennt die Adresse 0020')
        pruefe(rc == 4 and 'weniger als zweimal' in out, '--op 011: 0020 laeuft nur einmal, keine Schleife, rc 4')
        rc, out, err = lauf([log, '--op', '017'])
        pruefe('kein Befehl mit diesem Operationscode' in out and rc == 4, '--op ohne Treffer: Meldung, rc 4')
        rc, out, err = lauf([log, '--befehl', '0777'])
        pruefe(rc == 4 and 'nicht vorhanden' in out, 'unbekannter Anker: rc 4')
        rc, out, err = lauf([log, '--befehl', '0013'])
        pruefe(rc == 4 and 'weniger als zweimal' in out, 'Anker nur einmal ausgefuehrt: keine Schleife, rc 4')
        rc, out, err = lauf([log, '--liste'])
        pruefe(rc == 0 and '0010     211  0301' in out and '4x' in out, '--liste zeigt 0010 mit OR 211, BR 0301 und 4x')

        rc, out, err = lauf([log])
        pruefe(rc == 2 and 'nichts zu tun' in err, 'ohne Auftrag: rc 2')
        rc, out, err = lauf([log, '--befehl', '09'])
        pruefe(rc == 2, 'keine oktale Adresse: rc 2')
        rc, out, err = lauf([log, '--op', '11'])
        pruefe(rc == 2, 'Operationscode nicht dreistellig: rc 2')
        rc, out, err = lauf([os.path.join(d, 'gibtsnicht.tsv'), '--liste'])
        pruefe(rc == 2, 'Datei fehlt: rc 2')

        kaputt = os.path.join(d, 'k.tsv')
        with open(kaputt, 'w', encoding='utf-8') as f:
            f.write('# x\n1\t2\t3\n')
        rc, out, err = lauf([kaputt, '--liste'])
        pruefe(rc == 2 and 'Spalten' in err, 'falsche Spaltenzahl: rc 2 mit Meldung')

        abg = os.path.join(d, 'b.tsv')
        protokoll(abg, folge, ende='# ABGEBROCHEN nach 10 Zeilen')
        rc, out, err = lauf([abg, '--befehl', '0010'])
        pruefe(rc == 0 and 'abgebrochen' in out, 'abgebrochenes Protokoll: Hinweis in der Ausgabe')
        ohne = os.path.join(d, 'c.tsv')
        protokoll(ohne, folge, ende=None)
        rc, out, err = lauf([ohne, '--befehl', '0010'])
        pruefe('keine Endzeile' in out, 'fehlende Endzeile: Hinweis')

    print(f'grafik_takt_schleife_tests: {ANZAHL} Pruefungen, {len(FEHLER)} Fehler')
    return 1 if FEHLER else 0


if __name__ == '__main__':
    sys.exit(main())
