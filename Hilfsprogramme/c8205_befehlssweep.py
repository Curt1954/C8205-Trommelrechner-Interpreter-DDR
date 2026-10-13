#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
c8205_befehlssweep.py - Vollstaendigkeitstest fuer c8205_interp.py

Prueft systematisch alle 512 moeglichen Operationsteil-Codes (000-777 oktal, B-A-Z)
gegen den Knotengraphen von c8205_interp.py: fuer jeden Code wird ein Minimalprogramm
gebaut und direkt ueber die interne Knotengraph-Engine (dieselben FUNCS/graph-Strukturen
wie c8205_interp.py) ausgefuehrt. Das prueft NICHT die numerische Korrektheit jeder
Formel (dafuer bitte die regulaeren Tests ueber c8205_interpreter.sh/.bat verwenden),
sondern nur, ob fuer jeden Code ueberhaupt eine ANWEISUNG-Implementierung vorhanden ist
und der Knotenautomat sauber terminiert (kein Stub, kein Sackgassen-Knoten, keine
erkennbare Endlosschleife).

Aufbau je Testfall:
  Adresse 0000: der zu testende Befehl, Adressteil zeigt auf Adresse 0001
                (bei Organisationsbefehlen B<=1, wo der Adressteil als Sprungziel/
                Eingabe-Verschluesselung dient) bzw. auf Adresse 0040 in einer ANDEREN
                Spur (bei Einzel-/Gruppenbefehlen B>=2, wo der Adressteil ein
                Speicheroperand ist, der auch BESCHRIEBEN werden kann - z.B. Transport,
                Konjunktion im Speicher, Vorzeichenbefehl - und bei Gruppen-/
                Wiederholungsbefehlen sogar die GANZE Spur ueberschreibt).
  Adresse 0001: "020" (Unbedingter Stop 1. Art) als definierter Endpunkt.
  Eingabebefehle bekommen ein simuliertes Eingabegeraet (liefert einmal "1", dann Ende),
  damit auch diese Codes ohne --leser/--k0 vollstaendig durchlaufen.

Zusaetzlich (Ergaenzung 02.10.2026): der bedingte Sprung mit Rueckkehrabsicht (064-067,
B=0/A=6/Z>=4, Bedingung Schalter SP) wird fuer SP=0 und SP=1 mit einem von der Folgeadresse
verschiedenen Sprungziel (0010) gesondert geprueft: SP=0 -> kein Sprung (Stop bei 0001, BZ=0002),
SP=1 -> Sprung (Stop bei 0010, BZ=0011). Abweichungen zaehlen als Fehler ('sonst').

Zusaetzlich (Ergaenzung 02.10.2026): Zahlentest fuer den Sprung mit Rueckkehrabsicht (024-027, 124-127 und,
bei SP=1, 064-067). Hier wird NICHT nur der Durchlauf, sondern der AC-Wert geprueft, und zwar gegen eine vom
Interpreter unabhaengige Rechnung nach Befehlsliste/Spezialgrafik: <AC> := <AC> v Vr<BZ> (Loeschen vorher bei
L=1, <BZ> = r+1 steht in z12-z23, Vr schiebt das untere BZ-Bit nach z24), danach Resultatbehandlung R=2 (Vl) bzw.
R=3 (zyklisch). Geprueft wird mit geradem und ungeradem r+1 und mit gesetztem/nicht gesetztem z0 im AC; der
Fehler "unterstes BZ-Bit geht verloren" (ungerades r+1) wird dadurch erkannt.

Aufruf:
  python3 c8205_befehlssweep.py                  # alle 512 Codes, Kurzbericht
  python3 c8205_befehlssweep.py --verbose         # jeden Code einzeln auflisten
  python3 c8205_befehlssweep.py --code 251        # nur einen Code (oktal) im Detail
  python3 c8205_befehlssweep.py --mdverz VERZ     # anderer Ordner mit den Knoten-.md-Dateien
  python3 c8205_befehlssweep.py --graph PFAD --t2 PFAD --interp PFAD
Ohne Angaben liest das Skript die Knoten-.md-Dateien aus markdown-dateien/ neben c8205_interp.py.
"""
import argparse
import importlib.util
import os
import sys
from collections import Counter

STOP_WORT = 0o020          # Unbedingter Stop 1. Art, ohne Loeschen/Resultatbehandlung


class FakeK0:
    """Simuliertes K0-Eingabegeraet: liefert genau ein Zeichen ('1'), danach Ende."""
    def __init__(self):
        self.n = 0

    def naechstes(self):
        self.n += 1
        return '1' if self.n == 1 else None


def lade_ci(interp_pfad):
    """Laedt c8205_interp.py als Modul, unabhaengig vom aktuellen Arbeitsverzeichnis."""
    here = os.path.dirname(os.path.abspath(interp_pfad))
    if here not in sys.path:
        sys.path.insert(0, here)
    spec = importlib.util.spec_from_file_location('c8205_interp', interp_pfad)
    ci = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ci)
    return ci


def baue_maschine(ci, code, sp=0, ziel=None, start=None, ac0=None):
    """Baut fuer einen 9-Bit-Code (0-511) eine frische Machine mit Testprogramm."""
    B = (code >> 6) & 7
    # B<=1 (Organisationsbefehle): Adressteil ist Sprungziel/Verschluesselungs-Adresse,
    #     wird selbst nie beschrieben -> Adresse 0001 (unser Stop) ist sicher.
    # B>=2 (Einzel-/markierte/Gruppenbefehle): Adressteil ist ein Speicheroperand, der
    #     auch geschrieben werden kann (Transport usw.) bzw. bei Gruppen-/
    #     Wiederholungsbefehlen wird die GANZE Spur des Adressteils ueberschrieben ->
    #     dafuer eine andere Spur (0o40) als Schreib-Spielwiese benutzen, die mit
    #     Adresse 0000/0001 (Testbefehl/Stop) nichts zu tun hat.
    a_feld = 1 if B <= 1 else 0o40
    if ziel is not None:
        a_feld = ziel
    instr = (a_feld << 9) | code
    if start is None:
        mem = {0: instr, 1: STOP_WORT}
    else:
        mem = {start: instr}               # Befehl an Adresse 'start' (bestimmt r+1, auch ungerade/gerade)
    if ziel is not None:
        mem[ziel] = STOP_WORT
    m = ci.Machine(mem)
    if start is not None:
        m.BZ = start                       # Programm beginnt bei 'start' (Phase I: AR := BZ)
    if ac0 is not None:
        m.AC = ac0
    m.fl['SP'] = sp                # Schalter SP (nur fuer den bedingten Sprung mit Rueckkehrabsicht relevant)
    m.fl['T'] = 1                  # K0/Tastatur angewaehlt (Standardzustand nach Netz-Ein/G)
    m.k0 = FakeK0()
    m.log = lambda s: None
    m.diag_hook = lambda mm: None
    return m


def fuehre_code_aus(ci, graph, code, max_knoten, sp=0, ziel=None, start=None, ac0=None):
    """Fuehrt einen Code ueber den Knotengraphen aus. Rueckgabe: (status, meldung, schritte, m)."""
    m = baue_maschine(ci, code, sp, ziel, start, ac0)
    node = 1
    schritte = 0
    try:
        while not m.halted:
            schritte += 1
            if schritte > max_knoten:
                return 'limit', f'Knotenlimit ({max_knoten}) erreicht - vermutlich Endlosschleife', schritte, m
            n = graph[node]
            typ = n['typ']
            if typ == 'Konnektor':
                bez = n['text']
                ziel = n['out']
                if ziel is None:
                    for k, o in graph.items():
                        if o['typ'] == 'Konnektor' and o['text'] == bez and o['out'] is not None and k != node:
                            ziel = o['out']
                            break
                nxt = ziel
            elif typ == 'Phasenzuordnung':
                if 'Phase IV' in n['text']:
                    m.zaehler = 0
                    m.start_sek = ci.sektor(m.AR)
                nxt = n['out']
            elif typ == 'Anweisung':
                f = ci.FUNCS.get(n['anw'])
                if f is None:
                    raise ci.Stub(f'ANWEISUNG-{n["anw"]:03d} unbekannt (kein FUNCS-Eintrag)')
                f(m)
                nxt = n['out']
            elif typ == 'Test':
                f = ci.FUNCS.get(n['anw'])
                if f is None:
                    raise ci.Stub(f'ANWEISUNG-{n["anw"]:03d} unbekannt (kein FUNCS-Eintrag)')
                r = f(m)
                nxt = n['wahr'] if r else n['falsch']
            else:
                raise ci.Stub(f'Knotentyp {typ!r} unbekannt')
            if n.get('end'):
                break
            if nxt is None:
                return 'sonst', f'Knoten {node} hat keinen Ausgang', schritte, m
            m.came_from = node
            node = nxt
    except ci.KonfigFehler as e:
        return 'konfig', str(e), schritte, m
    except ci.Stub as e:
        return 'stub', str(e), schritte, m
    except Exception as e:
        return 'sonst', f'{type(e).__name__}: {e}', schritte, m
    return 'ok', m.halt_grund, schritte, m


def pruefe_sp_familie(ci, graph, max_knoten):
    """Bedingter Sprung mit Rueckkehrabsicht (064-067): SP=0 kein Sprung, SP=1 Sprung. Rueckgabe: Liste (code, sp, meldung) der Abweichungen."""
    fehler = []
    for code in (0o064, 0o065, 0o066, 0o067):
        for sp, erw_bz in ((0, 0o2), (1, 0o11)):
            status, msg, schritte, m = fuehre_code_aus(ci, graph, code, max_knoten, sp=sp, ziel=0o10)
            if status != 'ok':
                fehler.append((code, sp, f'{status}: {msg}'))
            elif m.BZ != erw_bz:
                fehler.append((code, sp, f'SP={sp}: BZ={ci.octs(m.BZ,4)} statt {ci.octs(erw_bz,4)} ({"Sprung ausgefuehrt" if sp == 0 else "Sprung fehlt"})'))
    return fehler


M33 = (1 << 33) - 1


def erwarteter_ac(code, ac0, r):
    """Erwarteter AC nach Sprung mit Rueckkehrabsicht, unabhaengig vom Interpreter gerechnet.
    code: B=0/1, A=2 (oder B=0, A=6 bei SP=1), Z=4..7; ac0: AC vorher; r: Adresse des Sprungbefehls."""
    Z = code & 7
    R, L = (Z >> 1) & 3, Z & 1
    ac = 0 if L else ac0                    # Loeschen in Phase III (L=1)
    ac |= (r + 1) << 8                      # Vr<BZ>: BZ (12 Bit) steht in z12-z23 (Bits 9..20), nach Vr in Bits 8..19
    if R == 2:
        ac = (ac << 1) & M33                # Vl
    elif R == 3:
        ac = ((ac << 1) & M33) | ((ac >> 32) & 1)   # zyklische Linksverschiebung
    return ac


def pruefe_rueckkehr_zahlen(ci, graph, max_knoten):
    """Zahlentest 024-027, 124-127 (immer) und 064-067 (SP=1): AC-Wert und BZ nach dem Sprung.
    Rueckgabe: Liste (code, r, ac0, meldung) der Abweichungen; Anzahl der Faelle."""
    fehler = []
    faelle = 0
    ziel = 0o40
    codes = [(c, 0) for c in (0o024, 0o025, 0o026, 0o027, 0o124, 0o125, 0o126, 0o127)]
    codes += [(c, 1) for c in (0o064, 0o065, 0o066, 0o067)]
    for code, sp in codes:
        for r in (0o10, 0o11):                         # r+1 = 0011 (ungerade) bzw. 0012 (gerade)
            for ac0 in (0o40000000005, 0o00000002000):  # z0 gesetzt + niedrige Bits / nur Adressfeld
                faelle += 1
                status, msg, schritte, m = fuehre_code_aus(ci, graph, code, max_knoten, sp=sp,
                                                           ziel=ziel, start=r, ac0=ac0)
                if status != 'ok':
                    fehler.append((code, r, ac0, f'{status}: {msg}'))
                    continue
                soll = erwarteter_ac(code, ac0, r)
                if m.AC != soll or m.BZ != ziel + 1:
                    fehler.append((code, r, ac0,
                                   f'AC={ci.octs(m.AC,11)} statt {ci.octs(soll,11)}, '
                                   f'BZ={ci.octs(m.BZ,4)} statt {ci.octs(ziel+1,4)}'))
    return fehler, faelle


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--interp', default=os.path.join(here, 'c8205_interp.py'),
                     help='Pfad zu c8205_interp.py (Standard: gleiches Verzeichnis)')
    ap.add_argument('--mdverz', default=None, metavar='VERZ',
                     help='Ordner mit den Knoten-.md-Dateien '
                          '(Standard: markdown-dateien/ neben c8205_interp.py, wie bei c8205_interp.py)')
    ap.add_argument('--graph', default=None,
                     help='Pfad zur Knoten-Datei (Standard: Datei im Ordner --mdverz)')
    ap.add_argument('--t2', default=None,
                     help='Pfad zur Variablentabelle T2 (Standard: Datei im Ordner --mdverz)')
    ap.add_argument('--max-knoten', type=int, default=5000,
                     help='Sicherheitslimit an Knotenschritten je Code (Standard: 5000)')
    ap.add_argument('--verbose', action='store_true',
                     help='Jeden der 512 Codes einzeln auflisten, nicht nur die Auffaelligkeiten')
    ap.add_argument('--code', default=None,
                     help='Nur einen einzelnen Code testen (oktal, z.B. 251) und Endzustand zeigen')
    args = ap.parse_args()

    if not os.path.isfile(args.interp):
        ap.error(f'c8205_interp.py nicht gefunden: {args.interp} (--interp angeben)')
    ci = lade_ci(args.interp)

    interp_dir = os.path.dirname(os.path.abspath(args.interp))
    md_dir = args.mdverz or os.path.join(interp_dir, 'markdown-dateien')
    graph_pfad = args.graph or os.path.join(md_dir, 'C8205-Interpreter-Eingänge_der_Knoten.md')
    t2_pfad = args.t2 or os.path.join(md_dir, 'C8205-Interpreter-Beschreibung_der_Knoten.md')
    if not os.path.isfile(graph_pfad):
        ap.error(f'Knoten-Datei nicht gefunden: {graph_pfad} (--graph angeben)')
    if not os.path.isfile(t2_pfad):
        ap.error(f'T2-Datei nicht gefunden: {t2_pfad} (--t2 angeben)')

    graph = ci.load_graph(graph_pfad)
    t2 = ci.load_t2(t2_pfad)

    # Konsistenzpruefung wie in c8205_interp.py main(): fehlende T2-/FUNCS-Eintraege
    # fuer tatsaechlich im Graphen benutzte ANWEISUNG-Nummern.
    fehlend_t2 = sorted({n['anw'] for n in graph.values() if n['anw'] and n['anw'] not in t2})
    fehlend_funcs = sorted(n for n in {x['anw'] for x in graph.values() if x['anw']} if n not in ci.FUNCS)
    print('=== Konsistenz Knotengraph <-> T2/FUNCS ===')
    print('Im Graph referenziert, aber in T2 fehlend:      ', fehlend_t2 or '(keine)')
    print('Im Graph referenziert, aber nicht implementiert:', fehlend_funcs or '(keine)')
    print()

    if args.code is not None:
        code = int(args.code, 8)
        if not 0 <= code <= 0o777:
            ap.error('--code muss zwischen 000 und 777 (oktal) liegen')
        status, msg, schritte, m = fuehre_code_aus(ci, graph, code, args.max_knoten)
        B, A, Z = (code >> 6) & 7, (code >> 3) & 7, code & 7
        print(f'Code {code:03o} (B={B} A={A} Z={Z}): {status}')
        print(f'  Meldung : {msg}')
        print(f'  Schritte: {schritte}')
        print(f'  AC={ci.octs(m.AC,11)}  BZ={ci.octs(m.BZ,4)}  AR={ci.octs(m.AR,4)}')
        return

    ergebnisse = {}
    for code in range(512):
        status, msg, schritte, m = fuehre_code_aus(ci, graph, code, args.max_knoten)
        ergebnisse[code] = (status, msg, schritte)
        if args.verbose:
            B, A, Z = (code >> 6) & 7, (code >> 3) & 7, code & 7
            print(f'  {code:03o} (B={B} A={A} Z={Z}): {status:6s} {msg}  [{schritte} Schritte]')

    cnt = Counter(v[0] for v in ergebnisse.values())
    print('=== Zusammenfassung ===')
    print(f'Getestete Codes gesamt: 512')
    for status in ('ok', 'stub', 'konfig', 'sonst', 'limit'):
        print(f'  {status:6s}: {cnt.get(status, 0)}')
    print()

    for status_kind in ('stub', 'sonst', 'limit', 'konfig'):
        zeilen = [(c, ergebnisse[c][1], ergebnisse[c][2]) for c in range(512) if ergebnisse[c][0] == status_kind]
        if zeilen:
            titel = {'stub': 'NICHT IMPLEMENTIERT (Stub)',
                      'sonst': 'SONSTIGER FEHLER',
                      'limit': 'KNOTENLIMIT (moegliche Endlosschleife)',
                      'konfig': 'GERAET FEHLT (kein Implementierungsfehler, nur Hinweis)'}[status_kind]
            print(f'--- {titel} ({len(zeilen)} Codes) ---')
            for c, msg, schritte in zeilen:
                B, A, Z = (c >> 6) & 7, (c >> 3) & 7, c & 7
                print(f'  {c:03o} (B={B} A={A} Z={Z}): {msg}  [{schritte} Schritte]')
            print()

    sp_fehler = pruefe_sp_familie(ci, graph, args.max_knoten)
    print('=== Bedingter Sprung mit Rueckkehrabsicht (064-067, SP=0/1) ===')
    if sp_fehler:
        for c, sp, msg in sp_fehler:
            print(f'  {c:03o} SP={sp}: {msg}')
    else:
        print('  8 Faelle (4 Codes x SP=0/1): SP=0 kein Sprung, SP=1 Sprung - OK')
    print()

    zahl_fehler, zahl_faelle = pruefe_rueckkehr_zahlen(ci, graph, args.max_knoten)
    print('=== Zahlentest Sprung mit Rueckkehrabsicht (024-027, 124-127, 064-067 mit SP=1) ===')
    if zahl_fehler:
        for c, r, ac0, msg in zahl_fehler:
            print(f'  {c:03o} r={r:04o} AC0={ci.octs(ac0,11)}: {msg}')
    else:
        print(f'  {zahl_faelle} Faelle (12 Codes x r+1 ungerade/gerade x 2 AC-Anfangswerte): AC-Wert und BZ wie erwartet - OK')
    print()

    fehlerhaft = (cnt.get('stub', 0) + cnt.get('sonst', 0) + cnt.get('limit', 0) + len(sp_fehler)
                  + len(zahl_fehler))
    if fehlerhaft == 0:
        print('ERGEBNIS: Alle 512 Operationscodes laufen ohne Implementierungsluecke durch.')
    else:
        print(f'ERGEBNIS: {fehlerhaft} von 512 Codes zeigen eine Implementierungsluecke oder Endlosschleife.')
    sys.exit(1 if fehlerhaft else 0)


if __name__ == '__main__':
    main()
