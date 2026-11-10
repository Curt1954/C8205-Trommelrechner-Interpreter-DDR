# -*- coding: utf-8 -*-
"""
zt_repo_test.py - Test des Hilfsprogramms C8205Z/zt/zt_repo.py gegen ZT-Repository_Aufgabenstellung.md.

Version: 0.01-002 (Neufassung; die Fassung 0.01-001 mit rund 175 Pruefungen ging verloren)
Aufruf (von ueberall):  python3 C8205Z/Tests_Z/zt_repo_test.py       Ausgabe je Fehler eine Zeile, am Ende "Test wahr", rc 0.
Die Sollwerte sind von Hand aus dem Format hergeleitet (Kommentar je Pruefung), nicht aus dem Programm abgelesen.
"""
import os
import sys
import tempfile
import shutil

STAMM = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(STAMM, 'C8205Z', 'zt'))
import zt_repo as z   # noqa: E402

anzahl = 0
fehler = 0


def pruefe(name, ist, soll):
    global anzahl, fehler
    anzahl += 1
    if ist != soll:
        fehler += 1
        print(f'FEHLER {name}: soll {soll!r}, ist {ist!r}')


def wirft(name, status, f, *a):
    global anzahl, fehler
    anzahl += 1
    try:
        f(*a)
    except z.ZtFehler as x:
        if x.status != status:
            fehler += 1
            print(f'FEHLER {name}: Status {x.status:o} statt {status:o}')
        return
    fehler += 1
    print(f'FEHLER {name}: keine Ausnahme')


def neu():
    d = tempfile.mkdtemp(prefix='ztrepo_')
    s = z.ZtSatz(d)
    return d, s, z.Archiv(s)


def oktal(w):
    return f'{w:011o}'


d, s, a = neu()
try:
    # Zeichen und Namen. Z = 71, T = 63, D = 24, ZR = 12 (je 6 Bit, z0 links): 111001 110011 010100 001010 001010 000
    pruefe('Name ZTD Wort 1', oktal(z.name_worte('ZTD')[0]), '71632412120')
    pruefe('Name ZTD Wort 2', oktal(z.name_worte('ZTD')[1]), '12121212120')
    pruefe('Name PROG1 Wort 1', oktal(z.name_worte('prog1')[0]), '47514627010')   # P 47, R 51, O 46, G 27, 1 01
    pruefe('Name rueckwaerts', z.worte_name(*z.name_worte('Abc 12')), 'ABC 12')
    pruefe('Lochbild 0', z.ZEICHEN_LOCH['0'], 0o20)
    pruefe('Lochbild 9', z.ZEICHEN_LOCH['9'], 0o31)
    pruefe('Lochbild Punkt', z.ZEICHEN_LOCH['.'], 0o73)
    pruefe('Lochbild Schraegstrich', z.ZEICHEN_LOCH['/'], 0o141)

    # Belegungsliste: Spur s in Wort s >> 5, Bit z(s und 37) mit z0 = Bit 32
    s.setze_belegt(0, 0)
    pruefe('Spur 0', oktal(s.mem[0][0]), '40000000000')
    s.setze_belegt(0, 31)
    pruefe('Spur 37 oktal', oktal(s.mem[0][0]), '40000000002')
    s.setze_belegt(0, 32)
    pruefe('Spur 40 oktal', oktal(s.mem[0][1]), '40000000000')
    s.setze_belegt(0, 127)
    pruefe('Spur 177 oktal', oktal(s.mem[0][3]), '00000000002')
    s.setze_belegt(0, 127, False)
    pruefe('Spur 177 frei', s.mem[0][3], 0)
    pruefe('Luecke nach Spur 0', s.luecke(0, 3), 1)

    # Formatieren: Zellen 0 bis 3 = Liste (nur Spur 0), Zelle 4 = Kennung, 5 bis 7 und 10 bis 37 = 0
    s.mem[1] = [0o77777777777] * z.GROESSE
    a.formatieren(1)
    pruefe('Format Zelle 0', oktal(s.mem[1][0]), '40000000000')
    pruefe('Format Zelle 4', oktal(s.mem[1][4]), '25147361025')
    pruefe('Format Zelle 5 bis 7', s.mem[1][5:8], [0, 0, 0])
    pruefe('Format Zelle 10 bis 37', s.mem[1][8:32], [0] * 24)
    pruefe('Format formatiert', (s.formatiert(0), s.formatiert(1)), (False, True))
    pruefe('Anker ohne Repository', a.anker(), None)
    wirft('Anlegen auf unformatierter Trommel', 1, a.anlegen, 2)

    # Anlegen: Namensblock nn = 100 oktal = 64 dez. -> (4 * 64 + 4) / 32 = 8,125 -> 9 Spuren = Spur 1 bis 9
    pruefe('Anlegen', a.anlegen(1), (1, 1))
    pruefe('Liste nach Anlegen', oktal(s.mem[1][0]), '77740000000')                 # 10 Bits: Spur 0 bis 9
    pruefe('Anker', (oktal(s.mem[1][5]), s.mem[1][6], s.mem[1][7]), ('61350247316', 1, 1))
    pruefe('Block Kennung', oktal(s.mem[1][32]), '34716052613')
    pruefe('Block Folge, nn, belegt', s.mem[1][33:36], [0, 0o100, 0])
    pruefe('Anker gefunden', a.anker(), (1, 1))
    wirft('Zweites Repository', 2, a.anlegen, 1)

    # Programm: 7 Worte, ein Segment ab Spur 10 dez. = 12 oktal; Lagewort = 1 * 200 + 12 = 212
    worte = [0o1111, 0o2222, 0o3333, 0o4444, 0o5555, 0o6666, 0o7777]
    kz = [(0, 1), (0, 0), (0, 2), (0, 9), (0, 5), (0, 0), (0, 3)]
    pruefe('Segment', a.programm_hinzufuegen('ZTD', worte, kz), [(1, 10)])
    pruefe('Liste mit Segment', oktal(s.mem[1][0]), '77777777600')                  # 26 Bits: 10 + 16
    b = 10 * 32
    pruefe('Gruppe 0 Kennungswort', oktal(s.mem[1][b]), oktal((1 << 27) | (2 << 15) | (9 << 9) | (5 << 3)))
    pruefe('Gruppe 0 Wort 0', s.mem[1][b + 1], 0o1111)
    pruefe('Gruppe 0 Wort 4', s.mem[1][b + 5], 0o5555)
    pruefe('Gruppe 1 Wort 5 (Zelle 7)', s.mem[1][b + 7], 0o6666)
    pruefe('Gruppe 1 Wort 6 (Zelle 10)', s.mem[1][b + 8], 0o7777)
    pruefe('Gruppe 1 Kennung', s.mem[1][b + 6], 3 << 21)      # Gruppe 1 = Worte 5 bis 9: Wort 6 (K2 = 3) hat das zweite Kennzeichen, Verschiebung 27 - 6 = 21
    e = a.eintraege()
    pruefe('Eintrag', (len(e), e[0].name, e[0].laenge, e[0].lage), (1, 'ZTD', 7, 0o212))
    pruefe('Eintrag Wort 3 im Block', s.mem[1][32 + 4 + 3], 0o212)
    pruefe('Block belegt', s.mem[1][35], 1)
    pruefe('Holen', a.holen('ztd'), (worte, kz))
    pruefe('Pruefen', a.pruefen(), ([], []))
    wirft('Name vorhanden (Status 10 oktal)', 0o10, a.programm_hinzufuegen, 'zTd', [1], [(0, 0)])
    wirft('K1 ungleich 0', 7, a.programm_hinzufuegen, 'X', [1], [(2, 0)])
    wirft('K2 ueber 9', 7, a.programm_hinzufuegen, 'X', [1], [(0, 10)])
    pruefe('Nach Fehler unveraendert', oktal(s.mem[1][0]), '77777777600')

    # Wortlage: Wort i -> Spur i // 25, Gruppe (i % 25) // 5, Zelle Gruppenanfang + 1 + i % 5 (Anfaenge 0, 6, 12, 18, 24 dez.)
    gross = [i + 1 for i in range(801)]
    gk = [(0, i % 10) for i in range(801)]
    lagen = a.programm_hinzufuegen('BIG', gross, gk)
    pruefe('BIG drei Segmente', len(lagen), 3)
    for i, soll_zelle in ((0, 1), (4, 5), (5, 7), (10, 13), (15, 19), (20, 25), (24, 29), (25, 32 + 1), (399, 15 * 32 + 29 - 0), (400, 1)):
        seg, rest = divmod(i, 400)
        t, sp = lagen[seg]
        spur, j = divmod(rest, 25)
        zelle = z.GRUPPEN[j // 5] + 1 + j % 5
        pruefe(f'Wortlage {i}', s.mem[t][(sp + spur) * 32 + zelle], gross[i])
    t0, s0 = lagen[0]
    pruefe('Verkettung Segment 1 -> 2', s.mem[t0][(s0 + 15) * 32 + 30], z.lagewort(*lagen[1]))   # Zelle 36 oktal = 30 dez.
    pruefe('Verkettung Zelle 37', s.mem[t0][(s0 + 15) * 32 + 31], 0)
    pruefe('Verkettung Segment 3 Ende', s.mem[lagen[2][0]][(lagen[2][1] + 15) * 32 + 30], 0)
    pruefe('Holen BIG', a.holen('BIG'), (gross, gk))
    pruefe('Pruefen mit BIG', a.pruefen(), ([], []))

    # Loeschen: Lagewort 0, Bits frei, belegt - 1, Name bleibt
    liste_vorher = list(s.mem[1][:4])
    a.loeschen('BIG')
    pruefe('Loeschen: Eintrag weg', [x.name for x in a.eintraege()], ['ZTD'])
    pruefe('Loeschen: Bits', oktal(s.mem[1][0]), '77777777600')
    pruefe('Loeschen: belegt', s.mem[1][35], 1)
    wirft('Loeschen unbekannt', 4, a.loeschen, 'BIG')
    wirft('Holen unbekannt', 4, a.holen, 'BIG')

    # Beschaedigungen
    s.mem[1][32] ^= 1
    wirft('Blockkennung falsch', 2, a.bloecke)
    s.mem[1][32] ^= 1
    s.mem[1][6] = 2
    f, h = a.pruefen()
    pruefe('Formatversion fremd erkannt', any('Formatversion' in x for x in f), True)
    s.mem[1][6] = 1
    s.setze_belegt(1, 50)
    f, h = a.pruefen()
    pruefe('Fremdbelegung nur Hinweis', (f, len(h)), ([], 1))
    s.setze_belegt(1, 50, False)

    # Speichern und Laden
    s.speichern()
    s2 = z.ZtSatz(d)
    pruefe('Speichern/Laden', s2.mem == s.mem, True)
    pruefe('Dateiformat', open(os.path.join(d, 'zt2.txt'), encoding='ascii').read().splitlines()[4], '0004: 25147361025')

    # Namensblock voll: kleiner Block nn = 2 -> weiterer Block mit gleicher Groesse
    d2, s_2, a2 = neu()
    a2.formatieren(0)
    a2.anlegen(0, 2)
    for n in ('A', 'B', 'C'):
        a2.programm_hinzufuegen(n, [1, 2, 3], [(0, 0)] * 3)
    pruefe('Zweiter Block', len(a2.bloecke()), 2)
    pruefe('Drei Eintraege', [x.name for x in a2.eintraege()], ['A', 'B', 'C'])
    pruefe('Pruefen zwei Bloecke', a2.pruefen(), ([], []))
    # Trommeln voll: nur ZT1 formatiert, 128 Spuren: Block 1 + (4*2+4)/32 -> 1 Spur, Segmente zu 16
    for i in range(6):
        try:
            a2.programm_hinzufuegen(f'P{i}', [1], [(0, 0)])
        except z.ZtFehler as x:
            pruefe('Trommeln voll Status', x.status, 6)
            break
    else:
        pruefe('Trommeln voll erreicht', True, False)
    shutil.rmtree(d2, ignore_errors=True)

    # .obj lesen: Text und Lochstreifen; Wort = K1 K2 Ziffern '.', '0.' = Wort 0, '/' beendet
    w, k = z.obj_lesen('010003000.0000000000017.0.010000020./')
    pruefe('obj Text Worte', w, [0o3000, 0o17, 0, 0o20])
    pruefe('obj Text Kennzeichen', k, [(0, 1), (0, 0), (0, 0), (0, 1)])
    lochstreifen = ''.join(f'{z.ZEICHEN_LOCH[c]:08b}\n' for c in '010003000.0.2000000000.1020000.')
    w, k = z.obj_lesen(lochstreifen.encode('ascii'))
    pruefe('obj Lochstreifen', (w, k), ([0o3000, 0, 0, 0o20000], [(0, 1), (0, 0), (2, 0), (1, 0)]))
finally:
    shutil.rmtree(d, ignore_errors=True)

print(f'{anzahl} Pruefungen, {fehler} Fehler')
print('Test wahr' if fehler == 0 else 'Test falsch')
sys.exit(0 if fehler == 0 else 6)
