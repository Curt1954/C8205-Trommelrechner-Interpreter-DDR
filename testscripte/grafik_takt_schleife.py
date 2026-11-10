#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_takt_schleife.py - Auswertung des Taktprotokolls, Teil 1: Auswahl der Schleife um einen Befehl (nur Auswahl, noch keine Taktsummen).
Version: TS-002 (08.11.2026: --takte, Teil 2; TS-001: Teil 1, Auftrag des Inhabers: aus dem Taktprotokoll alle Befehle heraussuchen, die mit einem durch seine Adresse
         angegebenen Befehl eine Schleife bilden)

Eingabe: Datei von  c8205_grafik.py --trommelzeit echt|schnell --taktprotokoll DATEI  (GRAFIK_Beschreibung §7.11, Format TP-001).

Wie ein Befehl im Protokoll erkannt wird
  * Jeder Befehl hat genau EINE Zeile art=L mit knoten=9 (Phase II, Befehl holen). Ihre Spalte 'adresse' ist die BEFEHLSADRESSE.
    BZ taugt dafuer nicht: nach einem Sprung (Knoten 63) steht in BZ die Rueckkehradresse, nicht die Adresse des geholten Befehls.
  * OR und BR (Operationscode, Operandadresse) stehen in der ersten Zeile T mit knoten=15 (Phase III) danach. Die Zeile des Befehls
    selbst (z. B. 011, Eingabe) hat in 'adresse' nur '-': der Befehl hat keinen eigenen Trommelzugriff mit seiner Adresse; die Adresse steht
    in der L-Zeile davor. (Beim 011 wird OR waehrend des Befehls zu 211, der Operandzugriff folgt danach mit anderer Adresse.)
  * Ein Befehl umfasst (fuer Teil 2 vorgemerkt) die Zeit von Beginn seiner Phase III bis zum Beginn der Phase III des Folgebefehls,
    also einschliesslich der Wartezeit auf den Folgebefehl. Hier werden diese Zeiten nur in die TSV-Datei mitgeschrieben, nicht summiert.

Schleife (Festlegung fuer Teil 1)
  Anker = Befehl A (Adresse). Ausfuehrungen von A in der Reihenfolge des Protokolls: e1, e2, ... Ein ZYKLUS ist die Folge aller Befehle von
  e(i) (einschliesslich) bis e(i+1) (ausschliesslich). Die Schleife ist die Menge der Befehlsadressen aller Zyklen; verschiedene Wege durch
  die Schleife (z. B. Ziffer / Punkt, Zahl der Durchlaeufe einer inneren Schleife) ergeben VARIANTEN (gleiche Adressfolge). Unterprogramme
  und innere Schleifen, die zwischen zwei Ausfuehrungen von A laufen, gehoeren zum Zyklus (Teil 2 entscheidet, ob ihre Zeit zaehlt).
  Nicht erfasst: Befehle vor der ersten und nach der letzten Ausfuehrung von A (kein vollstaendiger Zyklus); ihre Zahl wird gemeldet.

Teil 2 (--takte): Takte je Zyklus = vt(Phase III der naechsten Ausfuehrung des Ankers) - vt(Phase III dieser Ausfuehrung); je Befehl
  = vt(Phase III des Folgebefehls) - vt(Phase III des Befehls), die Wartezeit auf den Folgebefehl gehoert also zum Befehl (bestaetigt 08.11.2026).
  Eingabe-Halt steht nicht im Protokoll (vt steht still), die Wartezeit auf das Zeichen selbst ist deshalb nicht enthalten. 1 Takt = 1 Wortzeit = 104 us.
  Ausgabe je Variante: Zyklen, Befehle, Takte kleinste/groesste/Mittel; ueber alle Zyklen: Summe und Mittel je Zyklus.

Aufruf (aus dem Projektstamm)
  python3 testscripte/grafik_takt_schleife.py LOG --liste                  alle Befehlsadressen mit OR, BR, Haeufigkeit (Anker finden)
  python3 testscripte/grafik_takt_schleife.py LOG --befehl 0265            Schleife um den Befehl auf Adresse 0265 (oktal; mehrfach moeglich)
  python3 testscripte/grafik_takt_schleife.py LOG --op 011                 Anker = alle Adressen, an denen ein Befehl mit OR 011 steht
  python3 testscripte/grafik_takt_schleife.py LOG --befehl 0064 --takte   dazu die Takte (Teil 2)
  Weiter:  --voll (Befehle je Variante einzeln)  --varianten N (Zahl der gezeigten Varianten, Standard 8)  --tsv DATEI (je Zyklus und Befehl
           eine Zeile: anker zyklus variante pos adresse OR BR vt_holen wz_holen vt_III takte)
Rueckkehrcode: 0 in Ordnung · 2 Aufruf oder Datei falsch · 4 Anker nicht gefunden oder weniger als zwei Ausfuehrungen (keine Schleife)
"""
import argparse
import collections
import sys

VERSION_SCHLEIFE = 'TS-002'
KOPF_FORMAT = 'TP-001'
WORTZEIT_US = 104                 # eine Wortzeit (ein Takt) in Mikrosekunden


# ---------------------------------------------------------------------------------------------------------------------------------
# Einlesen
# ---------------------------------------------------------------------------------------------------------------------------------
class Befehl:
    """Ein ausgefuehrter Befehl: Adresse, OR, BR, vt beim Holen, Wartezeit beim Holen, vt am Beginn der Phase III."""
    __slots__ = ('adr', 'op', 'br', 'vt_holen', 'wz_holen', 'vt3')

    def __init__(self, adr, vt, n):
        self.adr = adr
        self.op = None
        self.br = None
        self.vt_holen = vt
        self.wz_holen = n
        self.vt3 = None


def lese_protokoll(pfad):
    """Liefert (befehle, info). info: Zeilen, ende (Text der Endzeile oder None), abgebrochen, ohne_phase3 (Zahl Befehle ohne OR/BR)."""
    befehle = []
    aktuell = None
    info = {'zeilen': 0, 'ende': None, 'abgebrochen': False, 'kopf_ok': False, 'ohne_phase3': 0}
    with open(pfad, encoding='utf-8') as f:
        for nr, zeile in enumerate(f, 1):
            if zeile.startswith('#'):
                if nr == 1 and KOPF_FORMAT in zeile:
                    info['kopf_ok'] = True
                if zeile.startswith('# Ende'):
                    info['ende'] = zeile[2:].strip()
                elif zeile.startswith('# ABGEBROCHEN'):
                    info['abgebrochen'] = True
                    info['ende'] = zeile[2:].strip()
                continue
            zeile = zeile.rstrip('\r\n')
            if not zeile:
                continue
            feld = zeile.split('\t')
            if len(feld) < 11:
                raise ValueError(f'Zeile {nr}: {len(feld)} Spalten statt 11 (kein Taktprotokoll {KOPF_FORMAT}?)')
            info['zeilen'] += 1
            art, knoten = feld[2], feld[3]
            if art == 'L' and knoten == '9':
                if aktuell is not None and aktuell.op is None:
                    info['ohne_phase3'] += 1
                aktuell = Befehl(int(feld[10], 8), int(feld[1]), int(feld[9]))
                befehle.append(aktuell)
            elif art == 'T' and knoten == '15' and aktuell is not None and aktuell.op is None:
                aktuell.op = feld[7]
                aktuell.br = int(feld[6], 8)
                aktuell.vt3 = int(feld[1])
    if aktuell is not None and aktuell.op is None:
        info['ohne_phase3'] += 1
    return befehle, info


# ---------------------------------------------------------------------------------------------------------------------------------
# Auswertung
# ---------------------------------------------------------------------------------------------------------------------------------
def okt4(x):
    return format(x, 'o').zfill(4)


def bereiche(adressen):
    """Fasst eine Adressfolge zu Bereichen +1 zusammen und fasst unmittelbar wiederholte gleiche Bereiche mit 'xK' zusammen."""
    teile = []
    for a in adressen:
        if teile and a == teile[-1][1] + 1:
            teile[-1][1] = a
        else:
            teile.append([a, a])
    erg = []                      # [(von, bis, anzahl)]
    for von, bis in teile:
        if erg and erg[-1][0] == von and erg[-1][1] == bis:
            erg[-1][2] += 1
        else:
            erg.append([von, bis, 1])
    text = []
    for von, bis, k in erg:
        s = okt4(von) if von == bis else f'{okt4(von)}-{okt4(bis)}'
        text.append(s + (f'x{k}' if k > 1 else ''))
    return ' '.join(text)


def op_je_adresse(befehle):
    """adresse -> Counter((OR, BR)) ueber alle Ausfuehrungen."""
    d = collections.defaultdict(collections.Counter)
    for b in befehle:
        d[b.adr][(b.op or '???', b.br if b.br is not None else -1)] += 1
    return d


def op_br_text(zaehler):
    (op, br), n = zaehler.most_common(1)[0]
    s = f'{op}  {okt4(br) if br >= 0 else "????"}'
    if len(zaehler) > 1:
        s += f'  (wechselt: {len(zaehler)} Werte, haeufigster {n}x)'
    return s


def zyklen_um(befehle, anker):
    """Liste der Zyklen (je Zyklus eine Liste von Befehlen) und Zahl der Befehle davor / danach."""
    pos = [i for i, b in enumerate(befehle) if b.adr == anker]
    zyklen = [befehle[a:b] for a, b in zip(pos, pos[1:])]
    davor = pos[0] if pos else 0
    danach = (len(befehle) - pos[-1] - 1) if pos else 0
    return pos, zyklen, davor, danach


def takte_je_zyklus(befehle, pos):
    """Je Zyklus (Index wie zyklen) eine Liste der Takte je Befehl; None, wenn ein vt_III fehlt. Summe = Takte des Zyklus."""
    erg = []
    for a, b in zip(pos, pos[1:]):
        v = [x.vt3 for x in befehle[a:b + 1]]
        erg.append(None if None in v else [y - x for x, y in zip(v, v[1:])])
    return erg


def varianten(zyklen):
    """Gruppiert die Zyklen nach der Adressfolge. Liefert Liste (schluessel, [zyklusnummern ab 1]) nach Haeufigkeit absteigend."""
    gruppen = collections.OrderedDict()
    for k, z in enumerate(zyklen, 1):
        gruppen.setdefault(tuple(b.adr for b in z), []).append(k)
    return sorted(gruppen.items(), key=lambda kv: (-len(kv[1]), kv[1][0]))


def melde_anker(anker, befehle, je_adresse, args, tsv):
    out = []
    pos, zyklen, davor, danach = zyklen_um(befehle, anker)
    if anker not in je_adresse:
        out.append(f'Befehl {okt4(anker)}: im Protokoll nicht vorhanden (keine Zeile L / Knoten 9 mit dieser Adresse).')
        return out, 4
    out.append(f'=== Anker: Befehl auf Adresse {okt4(anker)}   OR/BR: {op_br_text(je_adresse[anker])}')
    out.append(f'    Ausfuehrungen: {len(pos)}   vollstaendige Zyklen: {len(zyklen)}   '
               f'Befehle davor: {davor}   Befehle nach der letzten Ausfuehrung (kein Zyklus): {danach}')
    if len(pos) < 2:
        out.append('    Keine Schleife: der Befehl wird weniger als zweimal ausgefuehrt.')
        return out, 4
    var = varianten(zyklen)
    tk = takte_je_zyklus(befehle, pos)
    laengen = [len(z) for z in zyklen]
    out.append(f'    Varianten (verschiedene Adressfolgen): {len(var)}   Zyklenlaenge in Befehlen: kleinste {min(laengen)}, groesste {max(laengen)}')
    out.append('')
    out.append('  Varianten (haeufigste zuerst; "xK" = derselbe Adressbereich K-mal hintereinander):')
    for nr, (schluessel, nummern) in enumerate(var[:args.varianten], 1):
        out.append(f'  V{nr}: {len(nummern)}x, {len(schluessel)} Befehle, erster Zyklus Nr. {nummern[0]}')
        out.append(f'      {bereiche(schluessel)}')
        if args.takte:
            sm = [sum(tk[k - 1]) for k in nummern if tk[k - 1] is not None]
            if sm:
                out.append(f'      Takte je Zyklus: kleinste {min(sm)}, groesste {max(sm)}, Mittel {sum(sm) / len(sm):.2f}'
                           f'  ({len(sm)} Zyklen, Summe {sum(sm)}, = {sum(sm) / len(sm) * WORTZEIT_US / 1000:.3f} ms je Zyklus)'
                           + ('' if min(sm) == max(sm) else '  <- schwankt'))
        if args.voll:
            z = zyklen[nummern[0] - 1]
            t0 = tk[nummern[0] - 1]
            for p, b in enumerate(z):
                out.append(f'        {p:3d}  {okt4(b.adr)}  {b.op or "???"}  {okt4(b.br) if b.br is not None else "????"}'
                           + (f'  {t0[p]:4d} Takte' if args.takte and t0 else ''))
    if len(var) > args.varianten:
        rest = var[args.varianten:]
        out.append(f'  ... {len(rest)} weitere Varianten mit zusammen {sum(len(n) for _, n in rest)} Zyklen (mit --varianten N alle zeigen)')
    if args.takte:
        alle = [sum(t) for t in tk if t is not None]
        out.append('')
        if alle:
            out.append(f'  Takte ueber alle {len(alle)} Zyklen: Summe {sum(alle)}, Mittel je Zyklus {sum(alle) / len(alle):.3f}, '
                       f'kleinste {min(alle)}, groesste {max(alle)}; Mittel je Befehl {sum(alle) / sum(len(z) for z, t in zip(zyklen, tk) if t is not None):.3f}'
                       f' ({sum(alle) / len(alle) * WORTZEIT_US / 1000:.3f} ms je Zyklus)')
        if len(alle) < len(zyklen):
            out.append(f'  Achtung: {len(zyklen) - len(alle)} Zyklen ohne vt_III, nicht gezaehlt.')
        out.append('  (ohne Wartezeit auf das Zeichen im Eingabe-Halt: dort steht vt still)')
    # Vereinigungsmenge
    zaehl_zyklen = collections.Counter()
    zaehl_ausf = collections.Counter()
    for z in zyklen:
        for a in set(b.adr for b in z):
            zaehl_zyklen[a] += 1
        for b in z:
            zaehl_ausf[b.adr] += 1
    out.append('')
    out.append(f'  Schleifenbefehle (Vereinigung aller Zyklen): {len(zaehl_ausf)} Adressen')
    out.append('    Adresse  OR   BR    in Zyklen  Ausfuehrungen')
    for a in sorted(zaehl_ausf):
        (op, br), _ = je_adresse[a].most_common(1)[0]
        marke = '  <- Anker' if a == anker else ''
        wechsel = '  (OR/BR wechselt)' if len(je_adresse[a]) > 1 else ''
        out.append(f'    {okt4(a)}     {op}  {okt4(br) if br >= 0 else "????"}  {zaehl_zyklen[a]:9d}  {zaehl_ausf[a]:13d}{marke}{wechsel}')
    # nur im Kern: Adressen, die in jedem Zyklus vorkommen
    kern = sorted(a for a, k in zaehl_zyklen.items() if k == len(zyklen))
    out.append('')
    out.append(f'  In jedem Zyklus enthalten (Kern): {bereiche(kern)}')
    if tsv is not None:
        for nr, (schluessel, nummern) in enumerate(var, 1):
            for k in nummern:
                for p, b in enumerate(zyklen[k - 1]):
                    tc = tk[k - 1][p] if tk[k - 1] is not None else ''
                    tsv.write(f'{okt4(anker)}\t{k}\tV{nr}\t{p}\t{okt4(b.adr)}\t{b.op or "???"}\t'
                              f'{okt4(b.br) if b.br is not None else "????"}\t{b.vt_holen}\t{b.wz_holen}\t{b.vt3 if b.vt3 is not None else ""}\t{tc}\n')
    return out, 0


def hauptprogramm(argv=None):
    ap = argparse.ArgumentParser(description='Taktprotokoll auswerten, Teil 1: Schleife um einen Befehl auswaehlen.')
    ap.add_argument('log', help='Taktprotokoll (--taktprotokoll DATEI von c8205_grafik.py)')
    ap.add_argument('--befehl', action='append', default=[], metavar='ADR', help='Befehlsadresse des Ankers (oktal), mehrfach moeglich')
    ap.add_argument('--op', action='append', default=[], metavar='OC', help='Anker = alle Adressen mit diesem Operationscode (oktal, z. B. 011)')
    ap.add_argument('--liste', action='store_true', help='alle Befehlsadressen mit OR, BR und Haeufigkeit auflisten')
    ap.add_argument('--voll', action='store_true', help='je Variante die Befehle einzeln auflisten')
    ap.add_argument('--varianten', type=int, default=8, help='Zahl der gezeigten Varianten (Standard 8)')
    ap.add_argument('--takte', action='store_true', help='Takte je Zyklus und Variante bestimmen (Teil 2)')
    ap.add_argument('--tsv', metavar='DATEI', help='je Zyklus und Befehl eine Zeile in DATEI schreiben (fuer Teil 2)')
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    anker = []
    try:
        for s in args.befehl:
            anker.append(int(s, 8))
    except ValueError:
        print('grafik_takt_schleife: --befehl erwartet eine oktale Adresse (z. B. 0265).', file=sys.stderr)
        return 2
    for s in args.op:
        if len(s) != 3 or any(c not in '01234567' for c in s):
            print('grafik_takt_schleife: --op erwartet einen dreistelligen oktalen Operationscode (z. B. 011).', file=sys.stderr)
            return 2
    if not (anker or args.op or args.liste):
        print('grafik_takt_schleife: nichts zu tun: --liste, --befehl ADR oder --op OC angeben.', file=sys.stderr)
        return 2
    try:
        befehle, info = lese_protokoll(args.log)
    except (OSError, ValueError) as e:
        print(f'grafik_takt_schleife: {e}', file=sys.stderr)
        return 2
    je_adresse = op_je_adresse(befehle)
    print(f'grafik_takt_schleife {VERSION_SCHLEIFE}: {args.log}: {info["zeilen"]} Zeilen, {len(befehle)} Befehle auf {len(je_adresse)} Adressen')
    if not info['kopf_ok']:
        print(f'  Hinweis: Kopfzeile nennt nicht {KOPF_FORMAT}; Spaltenfolge wird trotzdem wie {KOPF_FORMAT} gelesen.')
    if info['abgebrochen']:
        print('  Achtung: Protokoll ist abgebrochen (--takt-max); die Auswertung sieht nur den Anfang des Laufs.')
    elif info['ende'] is None:
        print('  Achtung: keine Endzeile im Protokoll (Lauf vorzeitig beendet?).')
    if info['ohne_phase3']:
        print(f'  Achtung: {info["ohne_phase3"]} Befehle ohne Phase III (OR/BR unbekannt, "???").')
    if args.liste:
        print('')
        print('Adresse  OR   BR    Ausfuehrungen')
        for a in sorted(je_adresse):
            print(f'{okt4(a)}     {op_br_text(je_adresse[a])}' +
                  f'  {sum(je_adresse[a].values())}x')
    for oc in args.op:
        adr = sorted(a for a, z in je_adresse.items() if any(op == oc for (op, _br) in z))
        if not adr:
            print(f'\nOR {oc}: kein Befehl mit diesem Operationscode im Protokoll.')
            continue
        print(f'\nOR {oc}: Befehle an den Adressen ' + ', '.join(okt4(a) for a in adr)
              + '   (die Adresse steht in der Zeile L/Knoten 9 vor der Phase III, nicht in der Zeile des Befehls)')
        anker.extend(a for a in adr if a not in anker)
    rc = 0
    tsv = None
    if args.tsv and anker:
        try:
            tsv = open(args.tsv, 'w', encoding='utf-8', newline='\n')
        except OSError as e:
            print(f'grafik_takt_schleife: {e}', file=sys.stderr)
            return 2
        tsv.write('# grafik_takt_schleife ' + VERSION_SCHLEIFE + ': ' + args.log + '\n')
        tsv.write('# anker\tzyklus\tvariante\tpos\tadresse\tOR\tBR\tvt_holen\twz_holen\tvt_III\ttakte\n')
    try:
        for a in anker:
            zeilen, r = melde_anker(a, befehle, je_adresse, args, tsv)
            print('')
            print('\n'.join(zeilen))
            rc = max(rc, r)
    finally:
        if tsv is not None:
            tsv.close()
    if args.op and not anker:
        rc = 4
    return rc


if __name__ == '__main__':
    sys.exit(hauptprogramm())
