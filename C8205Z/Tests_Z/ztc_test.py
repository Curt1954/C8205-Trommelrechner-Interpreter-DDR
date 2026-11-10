# -*- coding: utf-8 -*-
"""ztc_test.py - Test von ZTC (Assembler/Claude/ztc/ztc.asm) im Interpreter mit --C8205Z gegen die Referenz zt_repo.py.
Ablauf je Fall: ztc.asm assemblieren, ZTC ueber das BIS (Stummel aus ztl_probe_3000.test) auf 3000 laden und starten, Eingaben von der Tastatur (K0-Datei),
ZTD (Ersatzprogramm mit L Worten) von Leser 1; danach die Zusatztrommeln Wort fuer Wort mit dem Ergebnis von zt_repo.py (anlegen + programm_hinzufuegen) vergleichen.
Aufruf (von ueberall): python3 C8205Z/Tests_Z/ztc_test.py     Rueckgabe 0 = alles ok. Alle Dateien liegen in einem Wegwerf-Ordner.
"""
import os, random, re, shutil, subprocess, sys, tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
STAMM = os.path.dirname(os.path.dirname(HIER))
sys.path.insert(0, os.path.join(STAMM, 'C8205Z', 'zt'))
import zt_repo as Z

fehler = 0
pruefungen = 0


def pruefe(bed, text):
    global fehler, pruefungen
    pruefungen += 1
    if not bed:
        fehler += 1
        print('FEHLER:', text)


LOCH = dict(Z.ZEICHEN_LOCH)
LOCH[':'] = 0o015


def obj_schreiben(worte, kz):
    """Worte und Kennzeichen -> .obj als Lochstreifen (Zeilen aus acht Ziffern 0/1): K1 K2, elf Oktalziffern, Punkt; am Ende /."""
    text = ''.join(f'{k1}{k2}{w:011o}.' for w, (k1, k2) in zip(worte, kz)) + '/'
    return ''.join(f'{LOCH[c]:08b}\n' for c in text)


def obj_woerter(daten):
    """.obj (Lochstreifen) -> Liste (K1, K2, Wert); K1 = 2: Adressangabe (K2 = 1 Hauptleitadresse, K2 = 0 Relativadresse); '0.' = Wort 0."""
    umkehr = {v: k for k, v in LOCH.items()}
    text = ''.join(umkehr[int(x, 2)] for x in daten.split())
    erg = []
    for w in text.split('.'):
        if w == '' or w.startswith('/'):
            break
        w = w.split('/')[0]
        if len(w) == 1:
            erg.append((int(w), 0, 0))
        else:
            erg.append((int(w[0]), int(w[1]), int(w[2:] or '0', 8)))
    return erg


def band_text(s):
    return ''.join(f'{LOCH[c]:08b}\n' for c in s)


def assemblieren():
    r = subprocess.run(['./c82ass.sh', '-p', 'Claude/ztc', '-s', 'ztc.asm', '--no-color'], cwd=os.path.join(STAMM, 'Assembler'),
                       capture_output=True, text=True, env=dict(os.environ, LC_ALL='C.UTF-8'))
    pruefe(r.returncode == 0, 'ztc.asm assemblieren: ' + r.stdout[-300:] + r.stderr[-300:])
    with open(os.path.join(STAMM, 'Assembler', 'Claude', 'ztc', 'ztc.obj'), encoding='ascii') as f:
        return f.read()


def lade_obj(obj_text, hla):
    """Wie das BIS: .obj (Lochbild-Zeilen) auf Haupttrommelzellen abbilden. K1 = 0 speichern (K2 = 1: plus Hauptleitadresse), K1 = 2 Adresse."""
    zeichen = obj_woerter(obj_text)
    zellen, ra = {}, 0
    for k1, k2, v in zeichen:
        if k1 == 2:
            if k2 == 1:
                ra = 0
            elif k2 == 0:
                ra = v
        elif k1 == 0:
            zellen[hla + ra] = (v + (hla << 9 if k2 == 1 else 0)) & Z.WORT
            ra += 1
    return [f'{a:04o}: {w:011o} # ZTC' for a, w in sorted(zellen.items())]


def stummel():
    """BIS-Minimalprogramm v6 (Zellen aus Tests/pj2-bis_minimalprogramm_v6.test) plus Start ab 1000: Kanal K1, 025 0262 (Eingabe Wort mit Kennzeichen), Sprung 3000."""
    zl = []
    with open(os.path.join(STAMM, 'Tests', 'pj2-bis_minimalprogramm_v6.test'), encoding='utf-8') as f:
        for z in f:
            if len(z) > 5 and z[4] == ':' and all(c in '01234567' for c in z[:4]):
                zl.append(z.rstrip('\n'))
    zl += ['1000: 00004600030 # 030 4600: Kanal K1 (Leser 1)', '1001: 00000262025 # 025 0262: Eingabe Wort mit Kennzeichen',
           f'1002: {0o3000 << 9:011o} # 000 3000: ZTC starten']
    return zl


def fall(name, t, tasten, worte, kz, nn=0o100, zt_vorher=None, soll_text=None, soll_status=0, band_extra=None, bis=False):
    """tasten: Liste der K0-Zeichen; worte/kz: ZTD-Ersatz; zt_vorher: dict t -> Liste (4096 Worte) oder None (alle 0)."""
    obj = assemblieren()
    tmp = tempfile.mkdtemp(prefix='ztc_')
    ztv = os.path.join(tmp, 'zt')
    os.makedirs(ztv)
    z = Z.ZtSatz(ztv)
    if zt_vorher:
        for tt, inhalt in zt_vorher.items():
            z.mem[tt] = list(inhalt)
    z.speichern()
    # Referenz
    ref = Z.ZtSatz(ztv)
    a = Z.Archiv(ref)
    erwartet_ok = soll_status == 0
    if erwartet_ok:
        if not ref.formatiert(t):
            a.formatieren(t)
        a.anlegen(t, nn)
        a.programm_hinzufuegen('ZTD', worte, kz)
    # Band: BIS-Ladeband (2 1 3000 . obj :) dann ZTD-.obj (binaer)
    obj_zeilen = [x for x in obj.split() if x]
    vor = band_text('213000.')
    tail = band_text(':')
    ztd = obj_schreiben(worte, kz) if band_extra is None else band_extra
    band = os.path.join(tmp, 'leser1.txt')
    with open(band, 'w') as f:
        f.write(vor + '\n'.join(obj_zeilen) + '\n' + tail + ztd if bis else ztd)
    k0 = os.path.join(tmp, 'k0.txt')
    with open(k0, 'w') as f:
        f.write('\n'.join(list(tasten) + ['\u00e4']) + '\n')   # Endemarke: unbekanntes Zeichen beendet den Lauf, wenn ZTC nach 0000 erneut anlaeuft
    swo = os.path.join(tmp, 'sw')
    kopf = ['Trommeldatei:', f'#DOK-0001 ZTC-Test {name}', '#PROT STUFE=2', '#TROMMEL=KEEP'] + (['#STARTE 1000'] if bis else []) + [
            f'--leser1 {band}', f'--k0 datei={k0}', f'--sw-ausgabe {swo}']
    zellen = stummel() if bis else lade_obj(obj, 0o3000)
    if not bis:
        zellen.append('0000: 00003000000 # 000 3000: Start von ZTC; beim Sprung 0000 000 am Ende laeuft ZTC erneut an und haelt an der leeren K0-Eingabe (E=1)')
    pruef = ['', 'Prüfungen:', 'US=0'] if bis else ['', 'Tastenfolge:', 'H SW=1 G R', '', 'Prüfungen:', 'US=0']
    ht = os.path.join(tmp, 'trommel.txt')
    with open(ht, 'w') as f:
        f.write(''.join(f'{i:04o}: 00000000000\n' for i in range(4096)))
    tf = os.path.join(tmp, name + '.test')
    with open(tf, 'w', encoding='utf-8') as f:
        f.write('\n'.join(kopf + zellen + pruef) + '\n')
    r = subprocess.run([sys.executable, '-I', 'c8205_interp.py', '--MODUS=TEST', '--max-knoten', '40000000', f'--C8205Z={ztv}', '--trommel', ht, '--out', os.path.join(tmp, 'prot'), tf],
                       cwd=STAMM, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=1500)
    ausgabe = ''
    p = os.path.join(swo, 'sw-ausgabe.txt')
    if os.path.isfile(p):
        ausgabe = open(p, encoding='utf-8').read()
    return tmp, ztv, ref, r, ausgabe


def vergleiche(name, ztv, ref):
    ist = Z.ZtSatz(ztv)
    for tt in range(4):
        if ist.mem[tt] != ref.mem[tt]:
            d = [i for i in range(Z.GROESSE) if ist.mem[tt][i] != ref.mem[tt][i]]
            pruefe(False, f'{name}: ZT{tt + 1} weicht ab, {len(d)} Worte, erstes bei {d[0]:04o}: ist {ist.mem[tt][d[0]]:011o}, soll {ref.mem[tt][d[0]]:011o}')
        else:
            pruefe(True, '')
    return ist


def lauf_fall(name, t, tasten, worte, kz, nn=0o100, vorher=None, status=0, text=None, band_extra=None):
    """Ein Fall; text = erwartete Schreibwerk-Ausgabe bis zum erneuten Anlauf (ohne den zweiten Block 'ZTC / TROMMEL (0-3)?')."""
    tmp, ztv, ref, r, aus = fall(name, t, tasten, worte, kz, nn, vorher, soll_status=status, band_extra=band_extra)
    pruefe(r.returncode == 8 and 'K0-Eingabe' in (r.stdout + r.stderr), f'{name}: rc {r.returncode} {r.stdout[-300:]} {r.stderr[-300:]}')
    folge = 'ZTC\nTROMMEL (0-3)?\n'
    pruefe(aus.endswith(folge), f'{name}: Ausgabe endet nicht mit dem Neustart: {aus[-80:]!r}')
    erster = aus[:-len(folge)] if aus.endswith(folge) else aus
    if text is not None:
        pruefe(erster == text, f'{name}: Ausgabe ist {erster!r}, soll {text!r}')
    if status:
        ist = Z.ZtSatz(ztv)
        pruefe(all(ist.mem[x] == ref.mem[x] for x in range(4)), f'{name}: Trommeln muessen unveraendert sein')
    else:
        vergleiche(name, ztv, ref)
    shutil.rmtree(tmp, ignore_errors=True)


def zufall(zuf, n, nur_k2=None):
    worte = [zuf.getrandbits(33) for _ in range(n)]
    kz = [(0, zuf.choice([0, 1, 1, 1, 2, 9]) if nur_k2 is None else nur_k2) for _ in range(n)]
    return worte, kz


def formatiert():
    z = [0] * Z.GROESSE
    z[0] = 0o40000000000
    z[4] = Z.LISTENKENNUNG
    return z


def haupt():
    zuf = random.Random(8205)
    os.chdir(STAMM)
    kopf = 'ZTC\nTROMMEL (0-3)?\nEINTRAEGE (OKTAL, VORGABE 100)?\nZTD-LOCHSTREIFEN IN LESER 1 LEGEN\n'
    w, k = zufall(zuf, 30)
    ok = lambda t, b, z: f'REPOSITORY ANGELEGT, TROMMEL {t}, BLOCK AB SPUR {b:03o}, ZTD AB SPUR {z:03o}\n'
    lauf_fall('f01_formatiert_t0', 0, ['0', 'WRZL', 'WRZL'], w, k, vorher={0: formatiert()}, text=kopf + ok(0, 1, 0o12))
    # f02: unformatiert, Zufallsinhalt auf ZT3, nn = 100 getippt, J
    zufallsinhalt = [zuf.getrandbits(33) for _ in range(Z.GROESSE)]
    zufallsinhalt[4] = 0
    unf = 'TROMMEL 2 UNFORMATIERT. LISTE ANLEGEN (J/N)?\nACHTUNG: FREMDDATEN GEHEN VERLOREN\n'
    kopf2 = 'ZTC\nTROMMEL (0-3)?\nEINTRAEGE (OKTAL, VORGABE 100)?\n'
    lauf_fall('f02_unformatiert_J', 2, ['2', 'WRZL', '1', '0', '0', 'ZR', 'J', 'WRZL'], w, k, vorher={2: zufallsinhalt},
              text=kopf2 + unf + 'ZTD-LOCHSTREIFEN IN LESER 1 LEGEN\n' + ok(2, 1, 0o12))
    # f03: unformatiert, N -> Abbruch, nichts geaendert
    lauf_fall('f03_unformatiert_N', 1, ['1', 'WRZL', 'WRZL', 'N', 'WRZL'], w, k, vorher={1: zufallsinhalt}, status=0o14,
              text=kopf2 + unf.replace('TROMMEL 2', 'TROMMEL 1') + 'ABGEBROCHEN\n')
    # f04: Repository liegt schon auf ZT2
    fertig = Z.ZtSatz(tempfile.mkdtemp(prefix='ztc_f04_'))
    ar = Z.Archiv(fertig)
    ar.formatieren(1)
    ar.anlegen(1, 0o100)
    ar.programm_hinzufuegen('ZTD', w, k)
    lauf_fall('f04_vorhanden', 0, ['0', 'WRZL', 'WRZL'], w, k, vorher={0: formatiert(), 1: fertig.mem[1]}, status=0o12,
              text=kopf2 + 'REPOSITORY VORHANDEN\n')
    # f05: Laengen an den Grenzen: 1, 25, 26, 400 (ein volles Segment), 401, 850 Worte
    for n in (1, 25, 26, 400, 401, 850):
        w, k = zufall(zuf, n)
        lauf_fall(f'f05_laenge_{n}', 1, ['1', 'WRZL', 'WRZL'], w, k, vorher={1: formatiert()}, text=kopf + ok(1, 1, 0o12))
    # f06: nn = 1 und nn = 777 (Trommel 3; Trommel 4 siehe f13)
    w, k = zufall(zuf, 40)
    lauf_fall('f06_nn1', 2, ['2', 'WRZL', '1', 'WRZL'], w, k, nn=1, vorher={2: formatiert()}, text=kopf + ok(2, 1, 2))
    lauf_fall('f06_nn777', 2, ['2', 'WRZL', '7', '7', '7', 'WRZL'], w, k, nn=0o777, vorher={2: formatiert()}, text=kopf + ok(2, 1, 0o101))
    # f07: Belegungsliste mit Luecken: Spuren 1..4 und 10..13 belegt -> Block (9 Spuren) ab 14, Segment dahinter
    voll = formatiert()
    for sp in list(range(1, 5)) + list(range(0o10, 0o14)):
        voll[sp >> 5] |= 1 << (32 - (sp & 31))
    w, k = zufall(zuf, 70)
    lauf_fall('f07_luecken', 0, ['0', 'WRZL', 'WRZL'], w, k, vorher={0: voll}, text=kopf + ok(0, 0o14, 0o25))
    # f08: Ungueltige Eingaben werden neu erfragt (9, x, 12 -> mehrere Ziffern, dann 1); nn: 0 abgelehnt, dann Vorgabe
    lauf_fall('f08_neu_fragen', 1, ['9', 'WRZL', 'x', 'WRZL', '1', '2', 'WRZL', '1', 'WRZL', '0', 'WRZL', 'WRZL'], w, k, vorher={1: formatiert()},
              text='ZTC\n' + 'TROMMEL (0-3)?\n' * 4 + 'EINTRAEGE (OKTAL, VORGABE 100)?\n' * 2 + 'ZTD-LOCHSTREIFEN IN LESER 1 LEGEN\n' + ok(1, 1, 0o12))
    # f09: Trommel voll (alle Spuren belegt)
    alle = [0] * Z.GROESSE
    alle[4] = Z.LISTENKENNUNG
    alle[0] = alle[1] = alle[2] = alle[3] = 0o77777777776
    alle[0] = 0o77777777776
    lauf_fall('f09_voll', 0, ['0', 'WRZL', 'WRZL'], w, k, vorher={0: alle}, status=6, text=kopf2 + 'TROMMELN VOLL\n')
    # f10: Block passt, kein Platz fuer das Segment (Spuren 12 bis 127 belegt)
    knapp = formatiert()
    for sp in range(0o12, 0o200):
        knapp[sp >> 5] |= 1 << (32 - (sp & 31))
    lauf_fall('f10_segment_voll', 0, ['0', 'WRZL', 'WRZL'], w, k, vorher={0: knapp}, status=6, text=kopf2 + 'TROMMELN VOLL\n')
    # f11: Bandfehler: K1 ungleich 0 (Status 7), leeres Band (11 oktal), unzulaessiges Zeichen (11 oktal)
    tx = lambda s: band_text(s)
    lauf_fall('f11_k1', 0, ['0', 'WRZL', 'WRZL'], w, k, vorher={0: formatiert()}, status=7, band_extra=tx('0100000000005.1100000000007./'),
              text=kopf + 'KENNZEICHEN UNZULAESSIG\n')
    lauf_fall('f11_leer', 0, ['0', 'WRZL', 'WRZL'], w, k, vorher={0: formatiert()}, status=0o11, band_extra=tx('/'), text=kopf + 'LOCHSTREIFEN FEHLERHAFT\n')
    lauf_fall('f11_ziffer8', 0, ['0', 'WRZL', 'WRZL'], w, k, vorher={0: formatiert()}, status=0o11, band_extra=tx('0100000000008./'),
              text=kopf + 'LOCHSTREIFEN FEHLERHAFT\n')
    # f13: Trommel 4 (t = 3, Anwahl 5400 030): formatiert und unformatiert mit J, ZTD ueber zwei Segmente
    w, k = zufall(zuf, 450)
    lauf_fall('f13_t3_formatiert', 3, ['3', 'WRZL', 'WRZL'], w, k, vorher={3: formatiert()}, text=kopf + ok(3, 1, 0o12))
    w, k = zufall(zuf, 30)
    lauf_fall('f13_t3_unformatiert_J', 3, ['3', 'WRZL', 'WRZL', 'J', 'WRZL'], w, k, vorher={3: zufallsinhalt},
              text=kopf2 + unf.replace('TROMMEL 2', 'TROMMEL 3') + 'ZTD-LOCHSTREIFEN IN LESER 1 LEGEN\n' + ok(3, 1, 0o12))
    # f12: ZTC ueber das BIS laden (2 1 3000 ., .obj, :), dann starten (1000); Tastatur nur mit Zeichen der Pult-Tastatur (ZR statt WRZL); am Ende kehrt das BIS zu 1002 zurueck, ZTC laeuft erneut an und liest die Endemarke
    w, k = zufall(zuf, 60)
    tmp, ztv, ref, r, aus = fall('f12_bis', 0, ['0', 'ZR', 'ZR'], w, k, zt_vorher={0: formatiert()}, bis=True)
    pruefe(r.returncode == 8 and 'K0-Eingabe' in (r.stdout + r.stderr), f'f12_bis: rc {r.returncode} {r.stdout[-300:]} {r.stderr[-300:]}')   # danach liest das BIS (Zelle 0000) von K0: Endemarke
    pruefe(aus == kopf + ok(0, 1, 0o12) + 'ZTC\nTROMMEL (0-3)?\n', f'f12_bis: Ausgabe {aus!r}')   # nach 0000 kehrt das BIS zum Aufrufer von 025 0262 (Zelle 1002) zurueck: ZTC laeuft erneut an
    vergleiche('f12_bis', ztv, ref)
    shutil.rmtree(tmp, ignore_errors=True)
    print('Pruefungen', pruefungen, 'Fehler', fehler)
    print('Test wahr' if fehler == 0 else 'Test falsch')
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(haupt())
