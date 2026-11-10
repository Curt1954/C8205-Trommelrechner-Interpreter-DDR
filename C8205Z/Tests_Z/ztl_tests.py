# -*- coding: utf-8 -*-
"""
ztl_tests.py - Tests von ZTL (Assembler/Claude/ztl/ztl.asm) mit dem Pruefling ztd_stub.asm (Assembler/Claude/ztl_test/).

Version: 0.01-001
Aufruf (von ueberall):  python3 C8205Z/Tests_Z/ztl_tests.py [-v]     Ausgabe je Fall "ok" oder "FEHLER", am Ende "Test wahr", rc 0.
Was geschieht je Fall: ZT-Dateien in einem Wegwerf-Ordner mit zt_repo.py anlegen (Format-Gegenprobe), ZTL und den Pruefling
assemblieren (in einem Wegwerf-Ordner, der Projektbaum bleibt unveraendert), Band (2 1 3000 . + ztl.obj + :) und .test schreiben,
Interpreter mit --C8205Z und eigener leerer Haupttrommel (--trommel, #TROMMEL=KEEP: LEER wuerde auch die ZT leeren) starten. ZTL wird wie jedes Programm ueber das BIS (Abbild aus Tests/pj2-bis_minimalprogramm_v6.test) von
Leser 1 auf 3000 geladen und durch Sprung auf 3000 gestartet. Sollwerte: aus den Woertern der .obj-Dateien nach der Regel
"Wort + Leitadresse(K2)" (K2 = 0: keine Aenderung, 1: Hauptleitadresse, 2 bis 9: Leitadressen 7612 bis 7621) hergeleitet,
nicht aus dem Lauf abgelesen.
Faelle: nominal (ZT1 unformatiert, Repository auf ZT2, Segmentkette ueber ZT2 und ZT3, Grenzen, Ueberschneidung, Lage 0);
Startfehler 2 (kein Repository, Blockkennung falsch), 3 (Formatversion), 4 (ZTD geloescht), 5 (ZTD zu gross).
"""
import os
import random
import shutil
import subprocess
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
STAMM = os.path.abspath(os.path.join(HIER, '..', '..'))
sys.path.insert(0, os.path.join(STAMM, 'C8205Z', 'zt'))
import zt_repo as z   # noqa: E402

VERBOSE = '-v' in sys.argv
WORT = (1 << 33) - 1
ZTL_LADEADRESSE = 0o3000
SW_VERZ = 'sw'


def lochbild(text):
    """Text -> Lochstreifen (Zeilen aus acht Ziffern); Ziffern, '.', '/' aus zt_repo, ':' = 0o015."""
    aus = []
    for c in text:
        if c == ':':
            aus.append('00001101')
        else:
            aus.append(f'{z.ZEICHEN_LOCH[c]:08b}')
    return '\n'.join(aus) + '\n'


def assembliere(asm, arbeit):
    """asm (Pfad) in ein Wegwerf-Unterverzeichnis kopieren und assemblieren; liefert den Inhalt der .obj (bytes)."""
    name = os.path.splitext(os.path.basename(asm))[0]
    d = os.path.join(arbeit, 'asm_' + name)
    os.makedirs(d, exist_ok=True)
    shutil.copy(asm, os.path.join(d, name + '.asm'))
    r = subprocess.run(['./c82ass.sh', '-p', d, '-s', name + '.asm', '--no-color'], cwd=os.path.join(STAMM, 'Assembler'),
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f'Assembler rc={r.returncode} fuer {asm}\n{r.stdout}\n{r.stderr}')
    with open(os.path.join(d, name + '.obj'), 'rb') as f:
        return f.read()


def bis_zellen():
    """Zellenzeilen (aaaa: wert # kommentar) des BIS-Minimalprogramms v6."""
    zeilen = []
    with open(os.path.join(STAMM, 'Tests', 'pj2-bis_minimalprogramm_v6.test'), encoding='utf-8') as f:
        for ln in f:
            if len(ln) > 5 and ln[4] == ':' and all(c in '01234567' for c in ln[:4]):
                zeilen.append(ln.rstrip('\n'))
    return zeilen


def oktal(w, n=11):
    return f'{w & WORT:0{n}o}'


def leitadresse(k, hla):
    """Leitadresse Nummer k als Wort: 0 -> 0; 1 -> Hauptleitadresse; 2..9 -> (0100 * k) im Adressteil (Vorgabe der Tests)."""
    if k == 0:
        return 0
    if k == 1:
        return hla << 9
    return (0o100 * k) << 9


def lade_soll(worte, kz, hla):
    return [(w + leitadresse(k2, hla)) & WORT for w, (k1, k2) in zip(worte, kz)]


def programm_prog1():
    """Kleines Programm: alle zehn K2, auch negative Zahlen, 3 Gruppen ueber eine Spur hinaus (L = 60 oktal = 48 dezimal)."""
    worte, kz = [], []
    for i in range(0o60):
        k2 = i % 10
        if i % 7 == 3:
            w = (-(i + 1)) & WORT if k2 == 0 else (((0o10 + i) << 9) | 0o211)
        else:
            w = ((0o10 + i) << 9) | 0o211
        worte.append(w)
        kz.append((0, k2))
    return worte, kz


def programm_gross(n, samen):
    """n Worte mit Zufallsinhalt (fester Startwert), Adressteil klein, damit Leitadressen nie ueberlaufen."""
    r = random.Random(samen)
    worte, kz = [], []
    for i in range(n):
        k2 = r.randrange(10)
        if k2 == 0:
            w = r.randrange(1 << 33)
        else:
            w = (r.randrange(0o1000) << 9) | r.randrange(0o1000)
        worte.append(w)
        kz.append((0, k2))
    return worte, kz


def neuer_satz(verz):
    return z.ZtSatz(verz)


def fall(name, arbeit, ztl_obj, stub_obj, bauen, soll_sw=None, jobs=None, erwartet=None, leit=None, c7610=None):
    """Einen Fall bauen und laufen lassen; liefert (ok, Text)."""
    d = os.path.join(arbeit, name)
    ztv = os.path.join(d, 'zt')
    os.makedirs(ztv, exist_ok=True)
    zt = z.ZtSatz(ztv)
    info = bauen(zt, stub_obj) or {}
    zt.speichern()
    # Band: Hauptleitadresse 3000, ztl.obj, Rueckkehr
    worte, kzs = z.obj_lesen(ztl_obj)
    band = lochbild('213000.') + ztl_obj.decode('ascii') + lochbild(':')
    bandpfad = os.path.join(d, 'band.txt')
    with open(bandpfad, 'w', encoding='ascii') as f:
        f.write(band)
    zeilen = ['Trommeldatei:', f'#DOK-0001 ZTL-Test {name}', '#PROT STUFE=2', '#TROMMEL=KEEP', '#STARTE 1000',
              f'--leser1 {bandpfad}', f'--sw-ausgabe {os.path.join(d, SW_VERZ)}']
    zeilen += bis_zellen()
    zeilen += ['1000: 00004600030 # 030 4600: Kanal K1 (Leser 1)', '1001: 00000262025 # 025 0262: Eingabe Wort mit Kennzeichen',
               f'1002: {ZTL_LADEADRESSE << 9:011o} # 000 3000: ZTL starten']
    if jobs is not None:
        # Pruefling (ZTD-Ersatz) und Auftragstabelle werden vom Fall ueber 'info' geliefert
        for i, j in enumerate(jobs):
            basis = 0o1100 + 8 * i
            vals = [j['lage'], j['laenge'], j['hla'] << 9, j.get('grenze', 0), 0, 0, 0, 1]
            for k, v in enumerate(vals):
                zeilen.append(f'{basis + k:04o}: {oktal(v)} # Auftrag {i} Zelle {k}')
        for k in range(2, 10):
            zeilen.append(f'{0o1300 + k - 2:04o}: {oktal(leitadresse(k, 0))} # Leitadresse {k}')
    if c7610 is not None:
        zeilen.append(f'7610: {oktal(c7610)} # 0. Leitadresse verfaelscht (ZTL muss sie auf 0 setzen)')
    zeilen += ['', 'Prüfungen:'] + (erwartet or ['US=1'])
    testpfad = os.path.join(d, name + '.test')
    with open(testpfad, 'w', encoding='utf-8') as f:
        f.write('\n'.join(zeilen) + '\n')
    htpfad = os.path.join(d, 'trommel.txt')           # leere Haupttrommel; KEEP, weil LEER auch die ZT leeren wuerde
    with open(htpfad, 'w', encoding='ascii') as f:
        f.write(''.join(f'{a:04o}: 00000000000\n' for a in range(4096)))
    r = subprocess.run([sys.executable, '-I', 'c8205_interp.py', '--MODUS=TEST', f'--C8205Z={ztv}', '--trommel', htpfad, '--out', os.path.join(d, 'prot'),
                        testpfad], cwd=STAMM, capture_output=True, text=True)
    text = r.stdout + r.stderr
    ok = r.returncode == 0
    if ok and soll_sw is not None:
        p = os.path.join(d, SW_VERZ, 'sw-ausgabe.txt')
        ist = open(p, encoding='utf-8').read() if os.path.exists(p) else '(keine Datei)'
        if ist.split() != soll_sw.split():
            ok = False
            text += f'\nSW-Ausgabe: soll {soll_sw!r}, ist {ist!r}'
    return ok, text


def main():
    arbeit = tempfile.mkdtemp(prefix='ztl_test_')
    fehler = 0
    try:
        ztl_obj = assembliere(os.path.join(STAMM, 'Assembler', 'Claude', 'ztl', 'ztl.asm'), arbeit)
        stub_obj = assembliere(os.path.join(STAMM, 'Assembler', 'Claude', 'ztl_test', 'ztd_stub.asm'), arbeit)
        stub_worte, stub_kz = z.obj_lesen(stub_obj)
        ztl_worte, _ = z.obj_lesen(ztl_obj)
        ztl_laenge = len(ztl_worte)
        ende_ztl = ZTL_LADEADRESSE + ztl_laenge          # Adresse hinter ZTL
        puffer = (ende_ztl + 0o37) & ~0o37               # Arbeitsspur
        ztd_adr = puffer + 0o40                          # ZTD wird hinter die Arbeitsspur geladen
        p1w, p1k = programm_prog1()
        bigw, bigk = programm_gross(801, 12345)          # 801 dezimal: drei Segmente (400 + 400 + 1)
        if VERBOSE:
            print(f'ZTL: {ztl_laenge:o} Worte, Ende {ende_ztl:04o}, Arbeitsspur {puffer:04o}, ZTD ab {ztd_adr:04o}')

        # ---------------------------------------------------------------- nominal
        def bau_nominal(zt, stub):
            a = z.Archiv(zt)
            a.formatieren(1)                              # ZT2 tragt das Repository, ZT1 bleibt unformatiert
            a.anlegen(1)
            a.programm_hinzufuegen('ZTD', stub_worte, stub_kz)
            a.programm_hinzufuegen('PROG1', p1w, p1k)
            for s in range(0o52, 0o160):                  # ZT2 bis auf die letzten 16 Spuren belegen: Segmentkette geht auf ZT3 weiter
                zt.setze_belegt(1, s, True)
            a.formatieren(2)
            lagen = a.programm_hinzufuegen('BIG', bigw, bigk)
            ein = {e.name.strip(): e for e in a.eintraege()}
            return {'lagen': lagen, 'eintraege': ein}

        # Lagen der Eintraege kennen wir erst nach dem Bauen; deshalb Eintraege vorab im Wegwerf-Satz bestimmen
        vorab = os.path.join(arbeit, 'vorab')
        os.makedirs(vorab)
        vz = z.ZtSatz(vorab)
        info = bau_nominal(vz, stub_obj)
        eint = {}
        for e in z.Archiv(vz).eintraege():
            eint[e.name.strip()] = e
        def lage_laenge(n):
            e = eint[n]
            return e.lage, e.laenge
        l1, n1 = lage_laenge('PROG1')
        lb, nb = lage_laenge('BIG')
        if VERBOSE:
            print(f'PROG1 Lage {l1:o} L {n1:o}; BIG Lage {lb:o} L {nb:o}; Segmente {[(t, f"{s:o}") for t, s in info["lagen"]]}')
        ende_hla = 0o7540 - n1

        def erwartung(jobs, soll_status, soll_ra, ladungen):
            """Pruefzeilen: Status, ZTL_PUFFER und RA je Auftrag, 7610 = 0, Speicher der geladenen Programme, ZTD hinter der Arbeitsspur."""
            erw = ['US=1']
            for i, (js, sa) in enumerate(zip(soll_status, soll_ra)):
                b = 0o1100 + 8 * i
                erw.append(f'{b + 4:04o}: {oktal(js)}')                    # Status
                erw.append(f'{b + 5:04o}: {oktal(puffer << 9)}')           # ZTL_PUFFER
                erw.append(f'{b + 6:04o}: {oktal(sa << 9)}')               # RA nach dem Laden
            erw.append(f'7610: {oktal(0)}')                                # 0. Leitadresse von ZTL auf 0 gesetzt
            speicher = {}
            for worte, kz, hla in ladungen:
                for w, a in zip(lade_soll(worte, kz, hla), range(hla, hla + len(worte))):
                    speicher[a] = w
            for a in sorted(speicher):
                erw.append(f'{a:04o}: {oktal(speicher[a])}')
            for w, a in zip(lade_soll(stub_worte, stub_kz, ztd_adr), range(ztd_adr, ztd_adr + len(stub_worte))):
                if stub_worte[a - ztd_adr] != 0:                           # Zellen mit Anfangswert 0 beschreibt der Pruefling selbst
                    erw.append(f'{a:04o}: {oktal(w)}')                     # ZTD selbst, von ZTL geladen (K2 = 0 und 1)
            return erw

        jobs = [
            dict(lage=l1, laenge=n1, hla=0o4000),                          # 1 PROG1 nach 4000
            dict(lage=lb, laenge=nb, hla=0o4100, grenze=0o5000 << 9),      # 2 BIG: Ende hinter Grenze 5000: Status 5, nichts geladen
            dict(lage=l1, laenge=n1, hla=0o3100),                          # 3 liegt in ZTL: Status 5
            dict(lage=l1, laenge=n1, hla=puffer),                          # 4 liegt in der Arbeitsspur: Status 5
            dict(lage=0, laenge=n1, hla=0o4400),                           # 5 Lage 0: Status 4
            dict(lage=l1, laenge=n1, hla=ende_hla),                        # 6 endet genau auf der Grenze 7540: in Ordnung
            dict(lage=l1, laenge=n1, hla=ende_hla + 1),                    # 7 ein Wort zu weit: Status 5
            dict(lage=l1, laenge=n1, hla=0o4600, grenze=(0o4600 + n1) << 9),   # 8 eigene Grenze, genau erreicht: in Ordnung
        ]
        erw = erwartung(jobs, [0, 5, 5, 5, 4, 0, 5, 0], [n1, 0, 0, 0, 0, n1, 0, n1],
                        [(p1w, p1k, 0o4000), (p1w, p1k, ende_hla), (p1w, p1k, 0o4600)])
        ok, text = fall('nominal', arbeit, ztl_obj, stub_obj, bau_nominal, jobs=jobs, erwartet=erw, c7610=0o777000)
        meld('nominal', ok, text)
        fehler += 0 if ok else 1
        # BIG allein (Segmentkette ZT2, ZT3, ZT3; das Laden dauert wegen der Knotengrenze des Interpreters einen eigenen Lauf)
        jobs = [dict(lage=lb, laenge=nb, hla=0o4100)]
        erw = erwartung(jobs, [0], [nb], [(bigw, bigk, 0o4100)])
        ok, text = fall('segmentkette', arbeit, ztl_obj, stub_obj, bau_nominal, jobs=jobs, erwartet=erw, c7610=0o777000)
        meld('segmentkette', ok, text)
        fehler += 0 if ok else 1

        # ---------------------------------------------------------------- Startfehler: Meldung der Statusnummer auf dem Schreibwerk
        def leer(zt, stub):
            pass

        def block_kaputt(zt, stub):
            a = z.Archiv(zt)
            a.formatieren(0)
            t, spur = a.anlegen(0)
            a.programm_hinzufuegen('ZTD', stub_worte, stub_kz)
            zt.mem[t][spur * 32] ^= 1                 # Blockkennung beschaedigen

        def version_fremd(zt, stub):
            a = z.Archiv(zt)
            a.formatieren(2)
            a.anlegen(2)
            a.programm_hinzufuegen('ZTD', stub_worte, stub_kz)
            zt.mem[2][6] = 2

        def ztd_geloescht(zt, stub):
            a = z.Archiv(zt)
            a.formatieren(3)
            a.anlegen(3)
            a.programm_hinzufuegen('ZTD', stub_worte, stub_kz)
            a.programm_hinzufuegen('PROG1', p1w, p1k)
            a.loeschen('ZTD')

        def ztd_zu_gross(zt, stub):
            a = z.Archiv(zt)
            a.formatieren(0)
            a.anlegen(0)
            a.programm_hinzufuegen('ZTD', [0] * 0o4230, [(0, 0)] * 0o4230)   # 2200 dezimal: ab 3540 ueber die Grenze 7540

        def ztd_nicht_eintrag0(zt, stub):
            a = z.Archiv(zt)
            a.formatieren(1)
            a.anlegen(1)
            a.programm_hinzufuegen('PROG1', p1w, p1k)                      # Eintrag 0 heisst nicht ZTD

        for n, bau, nr in (('kein_repository', leer, 2), ('blockkennung', block_kaputt, 2), ('formatversion', version_fremd, 3),
                           ('ztd_geloescht', ztd_geloescht, 4), ('ztd_zu_gross', ztd_zu_gross, 5),
                           ('eintrag0_nicht_ztd', ztd_nicht_eintrag0, 4)):
            ok, text = fall(n, arbeit, ztl_obj, stub_obj, bau, soll_sw=f'{nr:04o}', erwartet=['US=1'])
            meld(n, ok, text)
            fehler += 0 if ok else 1
    finally:
        if '--behalten' in sys.argv:
            print('Arbeitsordner:', arbeit)
        else:
            shutil.rmtree(arbeit, ignore_errors=True)
    print('Test wahr' if fehler == 0 else f'Test falsch ({fehler} Fall/Faelle)')
    return 0 if fehler == 0 else 6


def meld(name, ok, text):
    print(f'{name}: {"ok" if ok else "FEHLER"}')
    if not ok or VERBOSE:
        zl = text.splitlines()
        bad = [x for x in zl if 'FEHLER' in x and 'soll=' in x]
        print('\n'.join((bad[:40] if bad else zl[-25:])) if not ok else '')


if __name__ == '__main__':
    sys.exit(main())
