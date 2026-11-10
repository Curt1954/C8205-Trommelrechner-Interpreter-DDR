# -*- coding: utf-8 -*-
"""
ztd_py_tests.py - Abnahmetest von ZTD (Dialog im ZT-Archiv) nach der frueheren ZT-Repository_Format.md (aus dem Projekt entfernt), gegen das Referenzmodell zt_repo.py.

Version: 0.01-001
Aufruf (von ueberall):  python3 C8205Z/Tests_Z/ztd_py_tests.py [-v] [--ztd PFAD_ZUR.asm] [--behalten]   Ausgabe je Fall "ok" oder "FEHLER", am Ende "Test wahr", rc 0.

Prueft Zustand der Zusatztrommeln (Wort fuer Wort gegen zt_repo.py oder logisch) und die Schreibwerk-Ausgabe (nur das Wesentliche: Namen, Zahlen,
Fehlertext, nicht Zeilenumbruch und Zwischenraeume). Dialog-Syntax der Fassung A: Kommando und Angaben in einer Zeile ('M NAME ADRESSE', 'G ADRESSE',
'D NAME', 'A NAME'). Die handgeschriebene Fassung B (Assembler/Claude/ztd/ztd.asm) fragt dagegen zeilenweise nach (frueheres Format 11.6) und hat einen eigenen
Test (ztd_tests.py); mit --ztd PFAD laeuft hier nur eine Fassung mit der Syntax von A.
Ablauf je Fall: ZT-Dateien in einem Wegwerf-Ordner mit zt_repo.py aufbauen (ZTD aus der .asm assemblieren, als Eintrag 0 ablegen), ZTL ueber das BIS
von Leser 1 auf ZTL_ADR (Vorgabe 0400) laden und starten (Hilfen aus ztl_tests.py), Eingaben aus einer K0-Datei, Ausgabe aus sw-ausgabe.txt. ZTL startet ZTD selbst.
Das Ende eines Falls ist das Ende der K0-Eingabe (ZTD wartet am Prompt, Interpreter meldet rc 8 "K0-Eingabe").
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import ztl_tests as L            # noqa: E402  (Hilfen: assembliere, bis_zellen, lochbild, STAMM, ZTL_LADEADRESSE, z)

z = L.z
ZTL_ADR = int(os.environ.get('ZTD_ZTL_ADR', '400'), 8)   # ZTL liegt tief, damit ZTD (hinter ZTL, bis 07540) Platz hat; ZTL ist lageunabhaengig; mit anderer Adresse (Vielfaches von 040) wechselt die Ladeadresse von ZTD zwischen 0 und 040 modulo 0100
PROG_ADR = 0o6000        # Ladeadresse des Testprogramms, hinter ZTD
STAMM = L.STAMM
VERBOSE = '-v' in sys.argv
ZTD_ASM = os.path.join(STAMM, 'Assembler', 'Claude', 'ztd_py', 'ztd_py.asm')
if '--ztd' in sys.argv:
    ZTD_ASM = os.path.abspath(sys.argv[sys.argv.index('--ztd') + 1])

fehler = 0
pruefungen = 0


def pruefe(bed, text):
    global fehler, pruefungen
    pruefungen += 1
    if not bed:
        fehler += 1
        print('FEHLER:', text)


def tasten_von(text):
    """Text -> K0-Zeichen: Buchstaben und Ziffern einzeln, '_' = ZR (Zwischenraum), '\\n' = WRZL (Zeilenschaltung)."""
    erg = []
    for c in text:
        erg.append('WRZL' if c == '\n' else 'ZR' if c == '_' else c)
    return erg


def lauf(name, arbeit, ztd_obj, bauen, eingabe, ztl_obj, leser_extra='', pruef=('US=0',)):
    """Ein Fall. Liefert (Schreibwerk-Ausgabe, ZT-Satz nach dem Lauf, Rueckgabecode, Interpreter-Text)."""
    d = os.path.join(arbeit, name)
    ztv = os.path.join(d, 'zt')
    os.makedirs(ztv, exist_ok=True)
    zt = z.ZtSatz(ztv)
    bauen(zt)
    zt.speichern()
    bp = os.path.join(d, 'band.txt')                 # Leser 1: nur das, was ein Kommando einlesen soll (a)
    with open(bp, 'w', encoding='ascii') as f:
        f.write(leser_extra)
    k0 = os.path.join(d, 'k0.txt')
    with open(k0, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tasten_von(eingabe) + ['\u00e4']) + '\n')   # Endemarke: unbekanntes Zeichen beendet den Lauf (rc 8)
    swo = os.path.join(d, 'sw')
    zeilen = ['Trommeldatei:', f'#DOK-0001 ZTD-Test {name}', '#PROT STUFE=2', '#TROMMEL=KEEP',
              f'--leser1 {bp}', f'--k0 datei={k0}', f'--sw-ausgabe {swo}']
    zeilen += [x for x in L.bis_zellen() if not x.startswith('0000:')]            # BIS-Abbild ohne den Sprung in Zelle 0000
    zw_ztl, zk_ztl = z.obj_lesen(ztl_obj)
    for i, w in enumerate(L.lade_soll(zw_ztl, zk_ztl, ZTL_ADR)):
        zeilen.append(f'{ZTL_ADR + i:04o}: {w:011o} # ZTL')
    zeilen += [f'0000: {ZTL_ADR << 9:011o} # 000 ZTL: ZTL starten (auch nach q: ZTL und ZTD laufen neu an)']
    zeilen += ['', 'Tastenfolge:', 'H SW=1 G R', '', 'Prüfungen:'] + list(pruef)
    tf = os.path.join(d, name + '.test')
    with open(tf, 'w', encoding='utf-8') as f:
        f.write('\n'.join(zeilen) + '\n')
    ht = os.path.join(d, 'trommel.txt')
    with open(ht, 'w', encoding='ascii') as f:
        f.write(''.join(f'{a:04o}: 00000000000\n' for a in range(4096)))
    r = subprocess.run([sys.executable, '-I', 'c8205_interp.py', '--MODUS=TEST', '--max-knoten', os.environ.get('ZTD_KNOTEN', '60000000'), f'--C8205Z={ztv}', '--trommel', ht,
                        '--out', os.path.join(d, 'prot'), tf], cwd=STAMM, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=int(os.environ.get('ZTD_ZEIT', '90')))
    aus = ''
    p = os.path.join(swo, 'sw-ausgabe.txt')
    if os.path.isfile(p):
        aus = open(p, encoding='utf-8').read()
    return aus, z.ZtSatz(ztv), r.returncode, r.stdout + r.stderr


def norm(s):
    return ' '.join(s.split())


def vergleiche_zt(name, ist, ref):
    for t in range(4):
        if ist.mem[t] != ref.mem[t]:
            dd = [i for i in range(z.GROESSE) if ist.mem[t][i] != ref.mem[t][i]]
            pruefe(False, f'{name}: ZT{t + 1} weicht ab, {len(dd)} Worte, erstes bei {dd[0]:04o}: ist {ist.mem[t][dd[0]]:011o}, soll {ref.mem[t][dd[0]]:011o}')
        else:
            pruefe(True, '')


def objtext(worte, kz, schluss=True):
    """.obj als Text: je Wort K1 K2 Ziffern und Punkt, am Ende Schraegstrich (Lochstreifen wird daraus mit lochbild gebildet)."""
    return ''.join(f'{k1}{k2}{w:o}.' for w, (k1, k2) in zip(worte, kz)) + ('/' if schluss else '')


def vergleiche_logisch(name, ist, ref, namen):
    """Verzeichnis und Programminhalte gleich, Repository in sich stimmig (pruefen() ohne Fehler und ohne fremd belegte Spuren),
    gleiche Zahl belegter Spuren je Trommel. Lage und Reihenfolge der Segmente muessen nicht gleich sein (Format legt sie nicht fest)."""
    ai, ar = z.Archiv(ist), z.Archiv(ref)
    fehler, hinweise = ai.pruefen()
    pruefe(not fehler and not hinweise, f'{name}: Repository nicht stimmig: {fehler} {hinweise}')
    ei = [(e.name, e.laenge) for e in ai.eintraege()]
    er = [(e.name, e.laenge) for e in ar.eintraege()]
    pruefe(sorted(ei) == sorted(er), f'{name}: Verzeichnis {ei} statt {er}')
    for n in namen:
        try:
            pruefe(ai.holen(n) == ar.holen(n), f'{name}: Inhalt von {n} weicht ab')
        except Exception as x:                                       # noqa: BLE001
            pruefe(False, f'{name}: {n} nicht lesbar: {x}')
    for t in range(4):
        bi = sum(ist.belegt(t, sp) for sp in range(z.SPUREN))
        br = sum(ref.belegt(t, sp) for sp in range(z.SPUREN))
        pruefe(bi == br, f'{name}: ZT{t + 1}: {bi} Spuren belegt statt {br}')


def programm(n, samen):
    import random
    r = random.Random(samen)
    worte, kz = [], []
    for i in range(n):
        k2 = r.randrange(10)
        w = r.randrange(1 << 33) if k2 == 0 else (r.randrange(0o1000) << 9) | r.randrange(0o1000)
        worte.append(w)
        kz.append((0, k2))
    return worte, kz


def main():
    arbeit = tempfile.mkdtemp(prefix='ztd_test_')
    try:
        os.chdir(STAMM)
        ztl_obj = L.assembliere(os.path.join(STAMM, 'Assembler', 'Claude', 'ztl', 'ztl.asm'), arbeit)
        ztd_obj = L.assembliere(ZTD_ASM, arbeit)
        zw, zk = z.obj_lesen(ztd_obj)
        pruefe(all(k[0] == 0 for k in zk), 'ZTD-.obj enthaelt Kennzeichen K1 ungleich 0 (Luecke durch db/equ): im Archiv nicht ladbar')
        if VERBOSE:
            print(f'ZTD: {len(zw):o} Worte ({len(zw)} dezimal)')
        pw1, pk1 = programm(0o60, 1)
        pw2, pk2 = programm(0o31 * 3, 2)

        def ref_bau(zt, t=1, extra=True):
            a = z.Archiv(zt)
            a.formatieren(t)
            a.anlegen(t)
            a.formatieren((t + 1) % 4)                  # ZTD hat sechs Segmente: eine zweite Trommel nimmt den Rest
            a.programm_hinzufuegen('ZTD', zw, zk)
            if extra:
                a.programm_hinzufuegen('PROG1', pw1, pk1)
                a.programm_hinzufuegen('SORT2', pw2, pk2)
                a.programm_hinzufuegen('ABC9', pw1[:5], pk1[:5])
            return a
            return a

        def fall(name, eingabe, bau=None, ref=None, soll_text=None, soll_enthalten=(), leser='', pruef=('US=0',), rc_soll=8, logisch=None):
            if os.environ.get('ZTD_FALL') and os.environ['ZTD_FALL'] not in name:
                return ''                       # Hilfe beim Suchen: nur diesen Fall laufen lassen
            bau = bau or (lambda zt: ref_bau(zt))
            aus, ist, rc, text = lauf(name, arbeit, ztd_obj, bau, eingabe, ztl_obj, leser, pruef)
            pruefe(rc == rc_soll and (rc_soll != 8 or 'K0-Eingabe' in text), f'{name}: rc {rc} (erwartet {rc_soll}): {text[-400:]}')
            if soll_text is not None:
                pruefe(norm(aus) == norm(soll_text), f'{name}: Ausgabe {norm(aus)!r}, soll {norm(soll_text)!r}')
            for s in soll_enthalten:
                pruefe(s in norm(aus), f'{name}: Ausgabe enthaelt nicht {s!r}: {norm(aus)!r}')
            if ref is not None:
                zr = z.ZtSatz(tempfile.mkdtemp(dir=arbeit))
                ar = bau(zr)
                ref(ar)
                vergleiche_zt(name, ist, zr)
            if logisch is not None:
                zr = z.ZtSatz(tempfile.mkdtemp(dir=arbeit))
                ar = bau(zr)
                logisch[0](ar)
                vergleiche_logisch(name, ist, zr, logisch[1])
            return aus

        # f01: Start, leere Zeile, unbekanntes Kommando, Hilfe
        h = fall('f01_start_hilfe', '\nX\nH\n', soll_enthalten=['ZTD >', '> ?', 'L LISTE', 'Q ENDE', 'H HILFE'])
        # f02: l listet die Eintraege (ZTD, PROG1, SORT2, ABC9) mit L und Lagewort
        def ersatz_liste():
            zt = z.ZtSatz(tempfile.mkdtemp(dir=arbeit))
            a = ref_bau(zt)
            return [(e.name.strip(), e.laenge, e.lage) for e in a.eintraege()]
        soll = ersatz_liste()
        ausg = fall('f02_liste', 'L\n')
        for n, ln, lage in soll:
            m = re.search(re.escape(n) + r' (\d{4}) (\d{3})', norm(ausg))
            pruefe(m is not None and int(m.group(1), 8) == ln and int(m.group(2), 8) == lage,
                   f'f02: Eintrag {n} L={ln:04o} Lage={lage:03o} nicht in der Ausgabe: {norm(ausg)!r}')
        # f03: Repository auf ZT3 (ZT1, ZT2 unformatiert): l findet es, Kommando klein/gross gleich
        fall('f03_zt3', 'L\n', bau=lambda zt: ref_bau(zt, t=2), soll_enthalten=['ZTD', 'PROG1', 'SORT2', 'ABC9'])
        # f04: m laedt nach 4000, g startet dort; das Programm schreibt eine Konstante und haelt (020)
        tw = [(3 << 9) | 0o211, (4 << 9) | 0o240, 0o20, 0o1234567, 0]
        tk = [(0, 1), (0, 1), (0, 0), (0, 0), (0, 0)]
        def bau_t(zt):
            a = ref_bau(zt, extra=False)                # ZTD ist gross (4 Segmente): wenige Programme, sonst ist die Trommel voll
            a.programm_hinzufuegen('PROG1', pw1, pk1)
            a.programm_hinzufuegen('TESTPROG', tw, tk)
            return a
        soll_mem = [f'{PROG_ADR + i:04o}: {w:011o}' for i, w in enumerate(L.lade_soll(tw, tk, PROG_ADR))]
        soll_mem[4] = f'{PROG_ADR + 4:04o}: {0o1234567:011o}'        # nach dem Lauf: Ergebnis der Konstante
        fall('f04_m_g', 'M_TESTPROG_6000\nG_6000\n', bau=bau_t, rc_soll=0, pruef=['US=1'] + soll_mem,
             soll_enthalten=['GELADEN'])
        # f05: m mit unbekanntem Namen, m ueber die Obergrenze 7540 (Status 5): nichts geladen, Meldungen
        fall('f05_m_fehler', 'M_NIX_6000\nM_TESTPROG_7537\n', bau=bau_t, soll_enthalten=['NAME UNBEKANNT', 'PLATZ REICHT NICHT'],
             pruef=['US=0', f'{0o7537:04o}: 00000000000'])
        # f06: fehlende und fehlerhafte Angaben, Kleinbuchstaben gleich Grossbuchstaben (hier nur Zeichen aus der Kodetabelle)
        fall('f06_angaben', 'M\nM_TESTPROG\nG\nG_89\nM_TESTPROG_6000_UEBER\n', bau=bau_t, soll_enthalten=['> ?', 'GELADEN'])
        # f07: q springt nach 0000: ZTL und ZTD laufen neu an (Meldung zweimal)
        a7 = fall('f07_q', 'Q\n')
        pruefe(norm(a7).count('ZTD >') == 2, f'f07: q: ZTD muesste zweimal anlaufen: {norm(a7)!r}')
        # f08: d loescht PROG1 (Eintrag frei, Belegungsbits frei, belegt - 1); danach zeigt l den Eintrag nicht mehr
        a8 = fall('f08_d', 'D_PROG1\nL\n', ref=lambda a: a.loeschen('PROG1'), soll_enthalten=['GELOESCHT', 'ZTD', 'SORT2', 'ABC9'])
        pruefe('PROG1' not in a8.replace('D_PROG1', ''), f'f08: PROG1 steht nach d noch in der Liste: {norm(a8)!r}')
        # f09: Programm mit drei Segmenten ueber ZT2 und ZT3 loeschen (Kette folgen), unbekannter Name aendert nichts
        bigw, bigk = programm(801, 12345)

        def bau_big(zt):
            a = z.Archiv(zt)
            a.formatieren(1)
            a.anlegen(1)
            a.programm_hinzufuegen('ZTD', zw, zk)
            a.formatieren(2)
            a.programm_hinzufuegen('BIG', bigw, bigk)             # erstes Segment auf ZT2, die weiteren auf ZT3: Kette ueber die Trommeln
            a.programm_hinzufuegen('KLEIN', pw1, pk1)
            return a
        fall('f09_d_kette', 'D_BIG\nD_NIX\nL\n', bau=bau_big, ref=lambda a: a.loeschen('BIG'), soll_enthalten=['GELOESCHT', 'NAME UNBEKANNT', 'KLEIN'])
        # f10: letzter belegter Eintrag (ZTD selbst) bleibt, d ohne Namen ist fehlerhaft
        fall('f10_d_ohne_name', 'D\n', soll_enthalten=['> ?'], ref=lambda a: None)
        # f11: a liest ein Programm vom Leser 1 ein (ein Segment); f12: drei Segmente ueber ZT2 und ZT3; Vergleich logisch mit dem Referenzmodell
        nw, nk = programm(0o50, 777)
        fall('f11_a', 'A_NEUPROG\nL\n', leser=L.lochbild(objtext(nw, nk)), logisch=(lambda a: a.programm_hinzufuegen('NEUPROG', nw, nk), ['NEUPROG', 'PROG1', 'ZTD']),
             soll_enthalten=['EINGELESEN', 'NEUPROG 0050'])
        gw, gk = programm(801, 4242)
        fall('f12_a_gross', 'A_GROSS\n', bau=bau_big, leser=L.lochbild(objtext(gw, gk)),
             logisch=(lambda a: a.programm_hinzufuegen('GROSS', gw, gk), ['GROSS', 'BIG', 'KLEIN', 'ZTD']), soll_enthalten=['EINGELESEN'])
        # f13: Name vorhanden (Status 10): Trommeln unveraendert; f14: K1 ungleich 0 (Status 7); f15: leerer Lochstreifen; je ohne Spuren im Repository
        fall('f13_a_name', 'A_PROG1\n', leser=L.lochbild(objtext(nw, nk)), ref=lambda a: None, soll_enthalten=['NAME VORHANDEN'])
        fall('f14_a_k1', 'A_NEU\nL\n', leser=L.lochbild(objtext(nw[:3], [(0, 1), (1, 0), (0, 0)])),
             logisch=(lambda a: None, ['PROG1', 'ZTD']), soll_enthalten=['KENNZEICHEN UNZULAESSIG', 'PROG1'])
        fall('f15_a_leer', 'A_NEU\n', leser=L.lochbild('/'), logisch=(lambda a: None, ['PROG1', 'ZTD']), soll_enthalten=['LOCHSTREIFEN FEHLERHAFT'])
        # f16: Namensverzeichnis voll (nn = 2): a legt einen zweiten Namensblock an
        def bau_nn2(zt):
            a = z.Archiv(zt)
            a.formatieren(1)
            a.anlegen(1, nn=2)
            a.formatieren(2)
            a.programm_hinzufuegen('ZTD', zw, zk)
            a.programm_hinzufuegen('PROG1', pw1, pk1)
            return a
        fall('f16_a_neuer_block', 'A_DRITTES\nL\n', bau=bau_nn2, leser=L.lochbild(objtext(nw, nk)),
             logisch=(lambda a: a.programm_hinzufuegen('DRITTES', nw, nk), ['DRITTES', 'PROG1', 'ZTD']), soll_enthalten=['EINGELESEN', 'DRITTES 0050'])
    finally:
        if '--behalten' in sys.argv:
            print('Arbeitsordner:', arbeit)
        else:
            shutil.rmtree(arbeit, ignore_errors=True)
    print(f'{pruefungen} Pruefungen')
    print('Test wahr' if fehler == 0 else f'Test falsch ({fehler} Fehler)')
    return 0 if fehler == 0 else 6


if __name__ == '__main__':
    sys.exit(main())
