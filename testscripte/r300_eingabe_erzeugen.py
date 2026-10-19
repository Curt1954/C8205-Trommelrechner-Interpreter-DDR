# -*- coding: utf-8 -*-
"""
r300_eingabe_erzeugen.py - erzeugt das Eingabeprogramm "alle Zeichen des R300-Codes" (Version RE-001, 18.10.2026).

Aus EINER Quelle (c8205_interp.TABELLE1) entstehen:
  Assembler/Projekt_1/r300_eingabe/r300_eingabe.asm   Quelltext (danach: Assembler/c82ass.sh -p Projekt_1/r300_eingabe -s r300_eingabe)
  Tests/r300_eingabe.test                              TEST-Auftrag (Trommel aus der .test des Assemblers + K0-Datei + Pruefungen)
  virtuelle_Geraete/T-SW-Eingabe/r300_eingabe.txt      K0-Eingabedatei fuer den TEST-Interpreter (je Zeile ein Zeichen oder Name)
  Tests/r300_eingabe_klickspur.txt                     Klickspur fuer GRAFIK (--WIEDERGABE): Pult-Klicks UND Tasten im SW-Fenster ("tipp")
  Tests/r300_eingabe_soll.txt                          Sollfolge (Zeichen, Umschaltzeichen, Code, Spur-Wort) zum Vergleich mit dem Debug-Log

Aufruf (aus dem Projektordner):
  python3 -I testscripte/r300_eingabe_erzeugen.py asm        nur den Quelltext schreiben
  python3 -I testscripte/r300_eingabe_erzeugen.py rest       .test (braucht die .test des Assemblers), K0-Datei, Klickspur, Soll

Programm (siehe .asm): 0000 Sprung zum Programmanfang; Schreibwerk (K2) Meldung; dann Schleife: K0 anwaehlen, "011 ztab" (Eingabe-Halt mit
Loeschen: AC := Tabellenwort ztab OR Code), Echo des Zeichens am Schreibwerk, Spur im Speicher (ab SPUR). Zeichen mit Sprung-Umstellung
springen auf ztab OR Code: dort steht ein Sprung auf den Handler des Zeichens. Ende: das Zeichen "Irrung Satz" (hat keine Taste; nur der
TEST-Interpreter sendet es), danach Stopp.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
import c8205_interp as I          # noqa: E402

H16 = 0o153                       # Adresse des Handlers 'Irrung Satz' (Stopp), laut .sym; BZ steht danach auf H16+1
MELDUNG = 'R300 Eingabe, die Anzeige jeder Taste macht das Fenster'
ZTAB = 0o400                      # Tabelle: 64 Worte ZTAB .. ZTAB+077 (Code = Eingabeadresse des Zeichens)
SPUR = 0o3000                     # Spurpuffer: je getipptem Zeichen ein Wort (das Ausgabewort des Zeichens)
ASM_DIR = os.path.join(PROJ, 'Assembler', 'Projekt_1', 'r300_eingabe')
NAME = 'r300_eingabe'

# Tasten der Computertastatur (Zeichen -> Tk-keysym). Nur Zeichen, die die R300-Tabelle kennt UND fuer die es eine Taste gibt.
KEYSYM = {' ': 'space', '\t': 'Tab', '\r': 'Return', '%': 'percent', ':': 'colon', '+': 'plus', '`': 'grave', '/': 'slash',
          ',': 'comma', '.': 'period', '-': 'minus', '<': 'less', '"': 'quotedbl', '[': 'bracketleft', '>': 'greater',
          "'": 'apostrophe', '~': 'asciitilde', ']': 'bracketright', '#': 'numbersign', '*': 'asterisk', '(': 'parenleft',
          '=': 'equal', ';': 'semicolon', ')': 'parenright', '?': 'question', '!': 'exclam'}


def zeilen():
    """Zeilen der Tabelle, die der Rechner ueber K0 bekommt (ohne Transport und Irrung Zeichen)."""
    return [r for r in I.TABELLE1 if r[0] not in (50, 54)]


def code_von(r):
    return r[6]                   # Eingabeadresse (dezimal geschrieben wie die Tabelle, Wert = Code)


def ausgabewort(r):
    """Ausgabebefehl 'dz'-Form: 0000 <Ausgabeadresse 3 Stellen + 0> 030"""
    return int(r[3] + '0', 8) << 9 | 0o030


def okt(w):
    return '0' + format(w, 'o')


def wort_oktal(w):
    return f'{w:011o}'


# Zeichen, die der Benutzer tippen kann (Tastatur), und ihre Lage (KB/GB/None = in beiden Lagen gleich)
def tipp_zeichen():
    """Liste (zeichen, lage, name) aller tippbaren R300-Zeichen in der Reihenfolge der Tabelle: erst alle KB-Zeichen, dann alle GB-Zeichen."""
    kb, gb, beide = [], [], []
    for r in zeilen():
        nr = r[0]
        if nr in (25, 26, 51, 52, 53, 55):         # Umschaltzeichen (macht das Fenster selbst), Irrung Satz, ZV, BM, WR: keine Taste
            continue
        if nr == 12:
            beide.append(('\t', None, 'TAB'))
        elif nr == 38:
            gb.append(('\r', 'GB', 'WRZL'))
        elif nr == 49:
            beide.append((' ', None, 'ZR'))
        else:
            if r[5] and chr(r[5]) == r[1]:
                kb.append((r[1], 'KB', r[1]))
            if r[4] and r[4] < 256 and chr(r[4]) == r[2]:
                gb.append((r[2], 'GB', r[2]))
    return kb, gb, beide


def folge():
    """Die Tippfolge: beginnt in KB (der Vorzustand des SW ist unbestimmt, das erste Zeichen setzt ihn), alle KB-Zeichen, dann GB-Zeichen.
    Rueckgabe Liste (zeichen, name)."""
    kb, gb, beide = tipp_zeichen()
    f = [(z, n) for z, _l, n in kb]
    f += [(z, n) for z, _l, n in beide]
    f += [(z, n) for z, _l, n in gb]
    # noch einmal KB, damit auch der Wechsel GB -> KB vorkommt; dann Zeichen ohne R300-Code (muessen wirkungslos bleiben)
    f += [('a', 'a'), ('1', '1')]
    return f


NICHT_R300 = [('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('ß', 'ss'), ('@', 'at'), ('€', 'euro'), ('§', 'paragraph')]


def k0_tokens():
    """Was der Rechner ueber K0 bekommt (wie SwEingabe.abbilden, Vorzustand unbestimmt) - Liste (token, zeichen_name)."""
    import grafik_sw as S
    lage = None
    out = []
    for z, n in folge():
        tok = S.abbilden(z, lage)
        for t in tok:
            out.append((t, n))
            if t == 'Um. KB':
                lage = 'KB'
            elif t == 'Um. GB':
                lage = 'GB'
            else:
                nd = S.lage_des_zeichens(t)
                if nd:
                    lage = nd
    return out


# ---------------------------------------------------------------------------------------------------------------------
def asm_text():
    L = []
    w = L.append
    w('         start  0')
    w('; r300_eingabe.asm  --  Eingabeprogramm fuer ALLE Zeichen des R300-Codes, die eine Computertaste haben (Version RE-001)')
    w('; ERZEUGT von testscripte/r300_eingabe_erzeugen.py - nicht von Hand aendern, sondern das Skript.')
    w(';')
    w('; Ablauf: Meldung am Schreibwerk (K2); dann K0 anwaehlen (Schalter SW gedrueckt!) und Schleife: Eingabe-Halt 011 ztab,')
    w(';         das Ausgabewort des Zeichens in die Spur (ab 03000) schreiben, weiter. KEIN Echo: das SW-Fenster zeigt jedes angenommene')
    w(';         Zeichen selbst an (S3-04); zwischen zwei 011 wird K2 nie angewaehlt (S3-13: der Rechner ist rechtzeitig wieder bei 011).')
    w('; Tabelle ztab (0400..0477): Wort ztab+Code = Ausgabebefehl des Zeichens (Zeichen ohne Sprung-Umstellung); bei Zeichen MIT')
    w(';         Sprung-Umstellung springt der Eingabebefehl auf ztab+Code und fuehrt dort "000 handler" aus.')
    w('; Ende:  das Zeichen "Irrung Satz" (keine Taste; nur der TEST-Interpreter sendet es) -> Stopp. Sonst laeuft das Programm bis Netz aus.')
    w('; Lage:  Das Programm geht davon aus, dass das Schreibwerk nach der Meldung auf KB steht; das erste getippte Zeichen muss')
    w(';         deshalb eine Ziffer oder ein Kleinbuchstabe sein (das SW schickt vor dem ersten Zeichen kein Umschaltzeichen).')
    w('')
    w('beginn:  000    anfang               ; Zelle 0000: Sprung zum Programmanfang')
    w('anfang:  ANWAHL 4500                 ; K2 = Schreibwerk-Ausgabe')
    w('         dtm    \\' + MELDUNG + '\\')
    w('         dz     $inkb                ; Ausgabelage KB (das erste Eingabezeichen kommt ohne Umschaltzeichen)')
    w('         dz     $wrzl')
    w('         ANWAHL 4700                 ; K0 (liest die Schalterstellung SW)')
    w('')
    w('schleife: 011   ztab                 ; Eingabe-Halt mit Loeschen: AC := Tabellenwort ztab OR Code (Zeichen ohne Sprung)')
    w('gemein:  240    SPURBEGINN           ; Spur: AC (Ausgabewort des Zeichens) -> Spurzelle (Adresse wird je Zeichen um 1 erhoeht)')
    w('         211    gemein               ; AC := der Speicherbefehl (Zelle gemein)')
    w('         210    eins                 ; + 1 in den Adressstellen')
    w('         240    gemein               ; zurueckschreiben')
    w('         000    schleife')
    w('eins:    dw     01000                ; 1 in den Adressstellen (Adresse << 9)')
    w('')
    # Handler fuer Zeichen mit Sprung-Umstellung
    sprung = [r for r in zeilen() if r[7] and r[0] not in (50, 54, 52, 53)]
    for r in sprung:
        c = code_von(r)
        name = f'h{c:02o}'
        if r[0] == 51:                  # Irrung Satz = Ende
            w(f'{name}:     020    0                    ; {r[1]} (Code {c:02o}): Ende (nur im TEST-Lauf)')
        else:
            w(f'{name}:     211    w{c:02o}                  ; {r[1]} / {r[2]} (Code {c:02o}): Ausgabewort laden')
            w(f'         000    gemein')
            w(f'w{c:02o}:     dw     {okt(ausgabewort(r))}')
    w('')
    w(f'; ---- Tabelle ztab ({ZTAB:04o}..{ZTAB + 0o77:04o}) ----')
    w(f'         equ    {ZTAB:04o}                  ; Tabelle auf 0400 (64 Worte, Code = Eingabeadresse)')
    n_vor = len(L)
    by_code = {}
    for r in zeilen():
        by_code.setdefault(code_von(r), []).append(r)
    for c in range(0o100):
        rs = by_code.get(c, [])
        # Code 072: ZV (kein Sprung) und BM (Sprung) teilen ihn: die Zelle gilt fuer BM (Sprung), ZV hat keine Taste
        r = None
        if rs:
            r = next((x for x in rs if x[7]), rs[0])
        if r is None:
            w(f'         dw     0                    ; {c:02o}: unbelegt')
        elif r[7]:
            if r[0] == 53:
                w(f'         dw     0                    ; {c:02o}: BM/ZV: keine Taste, nicht behandelt (Zelle wuerde als Sprung nach 0000 laufen)')
            else:
                w(f'         000    h{c:02o}                 ; {c:02o}: {r[1]} / {r[2]} (Sprung-Umstellung)')
        else:
            w(f'         dw     {okt(ausgabewort(r))}       ; {c:02o}: {r[1]} / {r[2]}')
    L[n_vor] = 'ztab:    ' + L[n_vor][9:]
    w('')
    w(f'SPURBEGINN: abs  0{SPUR:o}')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    wahl = sys.argv[1] if len(sys.argv) > 1 else 'asm'
    if wahl == 'asm':
        os.makedirs(ASM_DIR, exist_ok=True)
        with open(os.path.join(ASM_DIR, NAME + '.asm'), 'w', encoding='utf-8') as f:
            f.write(asm_text())
        print('geschrieben:', os.path.join(ASM_DIR, NAME + '.asm'))


# ---------------------------------------------------------------------------------------------------------------------
def soll_liste():
    """Je K0-Token des Rechners: (token, zeichenname, code, ausgabewort). Ende-Token 'IS' (Irrung Satz) bleibt ohne Spur-Eintrag."""
    lage = 'KB'
    out = []
    for tok, n in k0_tokens():
        r = I.k0_zeile(tok, lage)
        if r[0] == 25:
            lage = 'KB'
        elif r[0] == 26:
            lage = 'GB'
        out.append((tok, n, code_von(r), ausgabewort(r)))
    return out


def schreibe_rest():
    soll_gr = soll_liste()
    # In einer K0-Datei beginnt ein Kommentar mit '#': das Zeichen '#' kann der TEST-Interpreter nicht lesen (Code 00 ist aber derselbe wie bei '0').
    soll = [x for x in soll_gr if x[0] != '#']
    # K0-Datei: ein Token je Zeile; Ende: IS (Irrung Satz) -> Stopp
    p = os.path.join(PROJ, 'virtuelle_Geraete', 'T-SW-Eingabe', NAME + '.txt')
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        for tok, _n, _c, _w in soll:
            f.write(tok + '\n')
        f.write('IS\n')
    # Sollfolge
    p = os.path.join(PROJ, 'Tests', NAME + '_soll.txt')
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Sollfolge des Programms r300_eingabe (RE-001): was der Rechner ueber K0 bekommen muss\n')
        f.write('# Nr  Spur-Adresse  Token        Code  Spur-Wort     getipptes Zeichen\n')
        for i, (tok, n, c, w) in enumerate(soll_gr):
            f.write(f'{i + 1:3d}   {SPUR + i:04o}          {tok:<12} {c:02o}    {wort_oktal(w)}   {n}\n')
    # TEST-Auftrag aus der .test des Assemblers
    quelle = os.path.join(ASM_DIR, NAME + '.test')
    with open(quelle, encoding='utf-8') as f:
        zl = f.read().splitlines()
    kopf = ['Trommeldatei:', '#DOK-0001 R300-Eingabe: alle Zeichen mit Computertaste ueber SW einlesen und als Echo ausgeben (RE-001)',
            '#TROMMEL=LEER',
            f'--sw-ausgabe virtuelle_Geraete/SW-Ausgabe/{NAME}.txt',
            f'--k0 datei=virtuelle_Geraete/T-SW-Eingabe/{NAME}.txt', '#PROT STUFE=2']
    koerper = [z for z in zl if z[:1].isdigit()]
    spur = [f'{SPUR + i:04o}: {wort_oktal(w)} # Spur {i + 1}: {tok} ({n})' for i, (tok, n, _c, w) in enumerate(soll)]
    fuss = ['', 'Tastenfolge:', 'H SW=1 G R', '', 'Prüfungen:',
            f'BZ={H16 + 1:04o} AC=00000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0'] + \
           [f'{SPUR + i:04o}: {wort_oktal(w)}' for i, (_t, _n, _c, w) in enumerate(soll)] + \
           [f'{SPUR + len(soll):04o}: 00000000000', f'--pruefe-sw-ausgabe Test-Ergebnisvergleiche/{NAME}-sw-ausgabe.txt']
    erwartet = MELDUNG + '\n'        # kein Echo des Programms (S3-04: das Fenster zeigt die Eingabe, im TEST-Lauf gibt es kein Fenster)
    with open(os.path.join(PROJ, 'Test-Ergebnisvergleiche', NAME + '-sw-ausgabe.txt'), 'w', encoding='utf-8', newline='') as f:
        f.write(erwartet)
    p = os.path.join(PROJ, 'Tests', NAME + '.test')
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(kopf + koerper + fuss) + '\n')
    print('geschrieben: K0-Datei, Sollfolge, Tests/' + NAME + '.test (Spur-Zeilen im Soll:', len(spur), ')')
    return soll_gr


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'rest':
    schreibe_rest()


# ---------------------------------------------------------------------------------------------------------------------
T_TIPP = 0.45          # Sekunden zwischen zwei getippten Zeichen (der Rechner muss wieder im Eingabe-Halt sein; --langsam im Aufruf-Skript)
T_ERSTE = 4.0          # erstes getipptes Zeichen (nach Netz, SW, G, R und der Meldung am Schreibwerk)


def keysym_von(z):
    if z in KEYSYM:
        return KEYSYM[z]
    if z.isascii() and (z.isalnum()):
        return z
    return {'ä': 'adiaeresis', 'ö': 'odiaeresis', 'ü': 'udiaeresis', 'ß': 'ssharp', '@': 'at', '€': 'EuroSign', '§': 'section'}[z]


def klickspur_text():
    """Klickspur fuer GRAFIK: Netz, Taste SW (Schalter SW gedrueckt), G, R; dann alle Tasten im SW-Fenster; Netz aus."""
    z = ['# C8205-Klickspur 1',
         '# fall: r300_eingabe (RE-001): alle Zeichen des R300-Codes mit Computertaste, getippt im SW-Fenster (Ereignisart tipp, ab DL-003)',
         '# aufruf: siehe testscripte/r300_eingabe_grafik.sh; Trommel: virtuelle_Geraete/Trommel/trommel_r300_eingabe.txt',
         '# erwartet: Sollfolge in Tests/r300_eingabe_soll.txt; Spur im Speicher ab 3000 (Trommeldatei nach dem Lauf)',
         '    0.000 klick NETZ wirkt=1',
         '    1.000 klick SW wirkt=1',
         '    1.600 klick G wirkt=1',
         '    2.200 klick R wirkt=1']
    t = T_ERSTE
    tipps = [(zn, n) for zn, n in folge()] + [(zn, n) for zn, n in NICHT_R300]
    for zn, n in tipps:
        z.append(f'{t:9.3f} tipp {keysym_von(zn)}')
        t += T_TIPP
    z.append(f'{t + 1.0:9.3f} klick NETZ wirkt=1')
    return '\n'.join(z) + '\n'


def trommel_text():
    mem = {}
    with open(os.path.join(PROJ, 'Tests', NAME + '.test'), encoding='utf-8') as f:
        for zl in f:
            if zl[:1].isdigit() and zl[4:6] == ': ':
                mem[int(zl[:4], 8)] = int(zl[6:17], 8)
                if zl.startswith('3000'):
                    break
    # nur Programm und Tabelle, keine Spur (Zellen ab SPUR kommen im .test als Pruefungen nach 'Prüfungen:')
    return ''.join(f'{a:04o}: {mem.get(a, 0):011o}\n' for a in range(4096))


def schreibe_gr():
    with open(os.path.join(PROJ, 'Tests', NAME + '_klickspur.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(klickspur_text())
    # Trommel nur aus dem Programmteil des .test (bis 'Tastenfolge:')
    mem = {}
    with open(os.path.join(PROJ, 'Tests', NAME + '.test'), encoding='utf-8') as f:
        for zl in f:
            if zl.startswith('Tastenfolge'):
                break
            if len(zl) > 17 and zl[:4].isdigit() and zl[4:6] == ': ':
                mem[int(zl[:4], 8)] = int(zl[6:17], 8)
    with open(os.path.join(PROJ, 'virtuelle_Geraete', 'Trommel', 'trommel_' + NAME + '.txt'), 'w', encoding='utf-8', newline='') as f:
        f.write(''.join(f'{a:04o}: {mem.get(a, 0):011o}\n' for a in range(4096)))
    print('geschrieben: Klickspur und Trommel (Programm bei 0000..', f'{max(mem):04o}', ')')


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'rest':
    schreibe_gr()
