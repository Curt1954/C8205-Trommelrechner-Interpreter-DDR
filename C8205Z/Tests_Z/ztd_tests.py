# -*- coding: utf-8 -*-
"""
ztd_tests.py - Tests von ZTD (Assembler/Claude/ztd/ztd.asm) ueber die echte Kette: BIS -> ZTL -> ZTD.

Version: 0.01-001
Aufruf (von ueberall):  python3 C8205Z/Tests_Z/ztd_tests.py [-v] [Fallname ...]     Ausgabe je Fall "ok" oder "FEHLER", am Ende "Test wahr", rc 0.
Je Fall: ZT-Dateien in einem Wegwerf-Ordner mit zt_repo.py bauen (ZTD als Eintrag 0), ZTL und ZTD assemblieren, ZTL ueber das BIS vom
Leser 1 laden (Band: 2 1 aaaa . + ztl.obj + : + .obj-Dateien fuer a), ZTL startet ZTD; Tastatureingabe aus einer K0-Datei (eine Zeile
je Zeichen); Ende ueber g 6000 . auf ein Halt-Stueck (US=1). Gegenprobe: dieselbe Aenderung mit zt_repo.py (Archiv) auf einer Kopie
des Ausgangs; die ZT-Dateien beider muessen Zelle fuer Zelle gleich sein; dazu die Schreibwerk-Ausgabe (Sollwerte aus Format 11.3
und der Ausgabetabelle von Hand hergeleitet, nicht aus dem Lauf).
"""
import copy
import os
import shutil
import subprocess
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import ztl_tests as zl   # noqa: E402
import ztc_test as zc    # noqa: E402  (nur fall() und formatiert(); haupt() von ztc_test laeuft hier nicht)
z = zl.z
STAMM = zl.STAMM
VERBOSE = '-v' in sys.argv
ZTL_ADR = 0o1200          # ZTL wird tief geladen, damit ZTD (rund 4200 Worte oktal) unter 7540 bleibt


def k0_zeilen(text):
    """Kurzschrift -> Zeilen der K0-Datei: Zeichen einzeln, '_' = WRZL, ' ' = ZR."""
    aus = []
    for c in text:
        aus.append('WRZL' if c == '_' else ('ZR' if c == ' ' else c))
    return aus


def lauf(name, arbeit, ztl_obj, ztd_obj, bauen, eingabe, baender=(), max_knoten=60000000, adr_halt=0o7000, pruef=None, zellen=(), ende_g=True, pruef_us=True):
    """Fall laufen lassen; liefert (rc, text, sw, ZtSatz-Verzeichnis)."""
    d = os.path.join(arbeit, name)
    ztv = os.path.join(d, 'zt')
    os.makedirs(ztv, exist_ok=True)
    zt = z.ZtSatz(ztv)
    bauen(zt)
    zt.speichern()
    band = zl.lochbild(f'21{ZTL_ADR:04o}.') + ztl_obj.decode('ascii') + zl.lochbild(':')
    for b in baender:
        band += b
    bandpfad = os.path.join(d, 'band.txt')
    with open(bandpfad, 'w', encoding='ascii') as f:
        f.write(band)
    k0 = os.path.join(d, 'k0')
    os.makedirs(k0, exist_ok=True)
    with open(os.path.join(k0, 'tasten.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(k0_zeilen(eingabe + (f'g{adr_halt:04o}.' if ende_g else ''))) + '\n')
    zeilen = ['Trommeldatei:', f'#DOK-0001 ZTD-Test {name}', '#PROT STUFE=2', '#TROMMEL=KEEP',
              f'--leser1 {bandpfad}', f'--sw-ausgabe {os.path.join(d, "sw")}', f'--k0 datei={k0}']
    zeilen += zl.bis_zellen()
    zeilen += ['1000: 00004600030 # 030 4600: Kanal K1 (Leser 1)', '1001: 00000262025 # 025 0262: Eingabe Wort mit Kennzeichen',
               f'1002: {ZTL_ADR << 9:011o} # 000 ZTL: ZTL starten', f'{adr_halt:04o}: 00000000020 # Halt-Stueck fuer g']
    zeilen += list(zellen)
    zeilen += ['', 'Tastenfolge:', 'SW+ H G M+ ' + 'E ' * 0o1000 + 'M- R', '', 'Prüfungen:'] + (['US=1'] if pruef_us else ['E=1']) + (pruef or [])
    testpfad = os.path.join(d, name + '.test')
    with open(testpfad, 'w', encoding='utf-8') as f:
        f.write('\n'.join(zeilen) + '\n')
    htpfad = os.path.join(d, 'trommel.txt')
    with open(htpfad, 'w', encoding='ascii') as f:
        f.write(''.join(f'{a:04o}: 00000000000\n' for a in range(4096)))
    r = subprocess.run([sys.executable, '-I', 'c8205_interp.py', '--MODUS=TEST', f'--C8205Z={ztv}', '--trommel', htpfad,
                        '--max-knoten', str(max_knoten), '--out', os.path.join(d, 'prot'), testpfad],
                       cwd=STAMM, capture_output=True, text=True, timeout=int(os.environ.get("ZTD_TIMEOUT", "150")))
    p = os.path.join(d, 'sw', 'sw-ausgabe.txt')
    sw = open(p, encoding='utf-8').read() if os.path.exists(p) else None
    return r.returncode, r.stdout + r.stderr, sw, ztv


def vergleich(ztv, soll_zt):
    """ZT-Dateien gegen den Satz der Gegenprobe: liste der Abweichungen."""
    ist = z.ZtSatz(ztv)
    abw = []
    for t in range(4):
        for a in range(z.GROESSE):
            if ist.mem[t][a] != soll_zt.mem[t][a]:
                abw.append(f'ZT{t + 1} {a:04o}: soll {soll_zt.mem[t][a]:011o} ist {ist.mem[t][a]:011o}')
                if len(abw) > 12:
                    return abw
    return abw


def obj_band(obj):
    return obj.decode('ascii')


def main():
    wahl = [a for a in sys.argv[1:] if not a.startswith('-')]
    arbeit = tempfile.mkdtemp(prefix='ztd_test_')
    fehler = 0
    try:
        ztl_obj = zl.assembliere(os.path.join(STAMM, 'Assembler', 'Claude', 'ztl', 'ztl.asm'), arbeit)
        ztd_obj = zl.assembliere(os.path.join(STAMM, 'Assembler', 'Claude', 'ztd', 'ztd.asm'), arbeit)
        mini_obj = zl.assembliere(os.path.join(STAMM, 'Assembler', 'Claude', 'mini', 'mini.asm'), arbeit)
        ztd_w, ztd_k = z.obj_lesen(ztd_obj)
        mini_w, mini_k = z.obj_lesen(mini_obj)
        p1w, p1k = zl.programm_prog1()

        def basis(zt, mit_prog1=True):
            a = z.Archiv(zt)
            a.formatieren(0)
            a.formatieren(1)
            a.anlegen(0)
            a.programm_hinzufuegen('ZTD', ztd_w, ztd_k)
            if mit_prog1:
                a.programm_hinzufuegen('PROG1', p1w, p1k)
            return a

        def zeile(name, laenge):
            return f'{name:<10s} {laenge:04o}'

        def obj_aus(worte, kz):
            """Worte -> .obj als Lochstreifen (K1 K2 Ziffern Punkt, Ende '/')."""
            text = ''.join(f'{k1}{k2}{w:o}.' for w, (k1, k2) in zip(worte, kz)) + '/'
            return zl.lochbild(text)

        bigw, bigk = zl.programm_gross(801, 12345)          # drei Segmente (400 + 400 + 1)
        faelle = []

        def fall(name, bau, eingabe, enth=(), gegen=None, baender=(), pruef=None, nicht=(), zellen=(), ende_g=True):
            faelle.append((name, bau, eingabe, list(enth), gegen, baender, pruef, list(nicht), zellen, ende_g))

        def klein(zt):                                        # Verzeichnisblock mit nn = 8 Eintraegen, voll
            a = basis(zt, False)
            for i in range(6):
                a.programm_hinzufuegen(f'P{i}', mini_w, mini_k)

        def leer_hinzu(zt, name, w, k):
            z.Archiv(zt).programm_hinzufuegen(name, w, k)

        def loesche(zt, name):
            z.Archiv(zt).loeschen(name)

        L_ZTD = len(ztd_w)
        fall('dialog_liste', basis, 'xhl',
             ['ZTD', '?', 'L  LISTE', 'Q  ENDE', 'H  HILFE', zeile('ZTD', L_ZTD), zeile('PROG1', len(p1w))])
        fall('del', basis, 'dPROG1_l', ['NAME:', 'OK', zeile('ZTD', L_ZTD)], lambda zt: loesche(zt, 'PROG1'), nicht=['PROG1'])
        fall('del_unbekannt', basis, 'dXYZ_', ['NAME UNBEKANNT'], lambda zt: None)
        fall('add_mini', basis, 'aMINI_l', ['OK', zeile('MINI', len(mini_w))], lambda zt: leer_hinzu(zt, 'MINI', mini_w, mini_k),
             baender=(obj_band(mini_obj),))
        fall('add_vorhanden', basis, 'aPROG1_', ['NAME VORHANDEN'], lambda zt: None, baender=(obj_band(mini_obj),))
        fall('add_kennzeichen', basis, 'aBAD_', ['KENNZEICHEN UNZULAESSIG'], lambda zt: None,
             baender=(zl.lochbild('0100.2000.0.'),))
        fall('add_ziffer8', basis, 'aBAD_', ['KENNZEICHEN UNZULAESSIG'], lambda zt: None, baender=(zl.lochbild('0100.0198.0/'),))
        fall('add_gross', basis, 'aBIG_l', ['OK', zeile('BIG', len(bigw))], lambda zt: leer_hinzu(zt, 'BIG', bigw, bigk),
             baender=(obj_aus(bigw, bigk),))
        fall('add_neuer_block', klein, 'aNEU_l', ['OK', zeile('NEU', len(mini_w))], lambda zt: leer_hinzu(zt, 'NEU', mini_w, mini_k),
             baender=(obj_band(mini_obj),))
        fall('add_leer', basis, 'aLEER_l', ['OK', zeile('LEER', 0)], lambda zt: leer_hinzu(zt, 'LEER', [], []),
             baender=(zl.lochbild('/'),))
        fall('del_dann_add', basis, 'dPROG1_aMINI_', ['OK'], lambda zt: (loesche(zt, 'PROG1'), leer_hinzu(zt, 'MINI', mini_w, mini_k)),
             baender=(obj_band(mini_obj),))

        def voll(zt):
            basis(zt)
            for t in range(4):
                if zt.formatiert(t):
                    for s in range(1, 128):
                        zt.setze_belegt(t, s, True)
        # TROMMELN VOLL: alle Spuren belegt, Eintrag aber frei
        fall('add_voll', voll, 'aVOLL_', ['TROMMELN VOLL'], lambda zt: None, baender=(obj_band(mini_obj),))

        def pruef_lade(adr):
            # Wort + Leitadresse(K2): K2 = 0 keine Aenderung, 1 Hauptleitadresse; K2 = 2 bis 9: Inhalt der Zellen 7612 bis 7621
            # (ZTD setzt sie nicht; auf der leeren Haupttrommel 0)
            erw = []
            for i, (w, (k1, k2)) in enumerate(zip(p1w, p1k)):
                soll = (w + ((adr << 9) if k2 == 1 else 0)) & zl.WORT
                erw.append(f'{adr + i:04o}: {soll:011o}')
            return erw
        fall('move', basis, 'mPROG1_6200.', ['OK'], None, pruef=pruef_lade(0o6200))
        fall('move_unbekannt', basis, 'mNIX_', ['NAME UNBEKANNT'], None)
        # g mit Ruecksprung: Stueck bei 7100 sichert das Rueckkehrwort in 7102 und springt dorthin; danach arbeitet ZTD weiter (l)
        fall('go_rueck', basis, 'g7100.l', ['ADRESSE:', zeile('PROG1', len(p1w))], None,
             zellen=['7100: 00007102240 # 240 7102: Rueckkehrwort sichern', '7101: 00007102000 # 000 7102: zurueck (Zelle 7102 enthaelt den Sprung)'])
        # q: Sprung nach Zelle 0000 (BIS); das BIS liest danach das Sofortbefehl-Wort 1 0 7000000 . (Sprung nach 7000, Halt-Stueck)
        fall('quit', basis, 'q' + '10' + '7000000.', ['ZTD', '>'], None, ende_g=False)
        sel = [f for f in faelle if not wahl or f[0] in wahl]
        for (name, bau, eingabe, enth, gegen, baender, pruef, nicht, zellen, ende_g) in sel:
            rc, text, sw, ztv = lauf(name, arbeit, ztl_obj, ztd_obj, bau, eingabe, baender, pruef=pruef, zellen=zellen, ende_g=ende_g)
            ok = rc == 0
            meld = ''
            if sw is None:
                ok = False
                meld += ' keine SW-Ausgabe'
            else:
                for s in enth:
                    if s not in sw:
                        ok = False
                        meld += f' fehlt in SW-Ausgabe: {s!r}'
                rest = sw.split('OK', 1)[-1]          # nach der Erfolgsmeldung darf der Name nicht mehr in der Liste stehen
                for s in nicht:
                    if s in rest:
                        ok = False
                        meld += f' steht noch in der SW-Ausgabe: {s!r}'
            if gegen is not None:
                soll = z.ZtSatz(os.path.join(arbeit, name, 'soll'))
                bau(soll)
                gegen(soll)
                abw = vergleich(ztv, soll)
                if abw:
                    ok = False
                    meld += ' ZT: ' + '; '.join(abw[:6])
            print(f'{name}: {"ok" if ok else "FEHLER"}')
            if not ok or VERBOSE:
                print(meld)
                print('SW-Ausgabe:\n' + (sw or '(keine)'))
                if not ok:
                    zl_ = text.splitlines()
                    print('\n'.join(zl_[-12:]))
            fehler += 0 if ok else 1
        # Kette ZTC - ZTL - ZTD: ZTC legt das Repository mit dem echten ZTD (vom Lochstreifen) an, danach laeuft ZTL - ZTD auf diesem Bild
        if not wahl or 'kette_ztc' in wahl:
            os.chdir(STAMM)
            tmp, ztv_c, ref_c, r_c, aus_c = zc.fall('kette_ztc', 0, ['0', 'WRZL', 'WRZL'], ztd_w, ztd_k, zt_vorher={0: zc.formatiert()})
            ist_c = z.ZtSatz(ztv_c)
            ok = r_c.returncode == 8 and 'REPOSITORY ANGELEGT, TROMMEL 0, BLOCK AB SPUR 001, ZTD AB SPUR 012' in aus_c
            meld = '' if ok else f' ZTC rc {r_c.returncode}: {aus_c[-120:]!r}'
            abw = vergleich(ztv_c, ref_c)
            if abw:
                ok = False
                meld += ' ZTC-Bild: ' + '; '.join(abw[:4])

            def bau_c(zt):
                for t in range(4):
                    zt.mem[t] = list(ist_c.mem[t])
            rc, text, sw, ztv = lauf('kette_ztc', arbeit, ztl_obj, ztd_obj, bau_c, 'l')
            if rc != 0 or sw is None or zeile('ZTD', L_ZTD) not in sw:
                ok = False
                meld += f' ZTL/ZTD rc {rc}, SW {sw!r}'
            shutil.rmtree(tmp, ignore_errors=True)
            print(f'kette_ztc: {"ok" if ok else "FEHLER"}')
            if not ok:
                print(meld)
            fehler += 0 if ok else 1
    finally:
        if '--behalten' in sys.argv:
            print('Arbeitsordner:', arbeit)
        else:
            shutil.rmtree(arbeit, ignore_errors=True)
    print('Test wahr' if fehler == 0 else f'Test falsch ({fehler} Fall/Faelle)')
    return 0 if fehler == 0 else 6


if __name__ == '__main__':
    sys.exit(main())
