#!/usr/bin/env python3
"""kat5_sort1_gen.py -- erzeugt kat5_sort1.asm: Hauptprogramm (im Test ab 02000, ;#TESTBASIS) mit einem Feld von 20 (festen, pseudozufaelligen)
kat5-Texten, das UP kat5_sort1 (Zelle 0000, Makro KAT5SORT aus c82ass.makros) sortiert das Feld aufsteigend in sich auf denselben Zellen; danach druckt das Hauptprogramm
mit dem Makro KAT5AUSGABE jeden Text auf dem Schreibwerk (Kanal 2), je Text eine Zeile (Zeilenschaltung dahinter).
Reiner Python-Generator (kein c82gen). Aufruf vom Projektstamm: python3 -I Assembler/Claude/kat5_sort1/gen/kat5_sort1_gen.py
(asm_und_test.sh ruft ihn selbst auf). Die Sollwerte kommen aus einem eigenen Python-Modell (sorted), nicht aus dem Assemblerlauf."""
import os
import random

hier = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(hier, '..', 'kat5_sort1.asm')
SOLLDRUCK = os.path.join(hier, '..', '..', '..', '..', 'Test-Ergebnisvergleiche', 'kat5_sort1-sw-ausgabe.txt')
N = 20                      # Anzahl der Texte
BASIS = 0o2000              # Ladeadresse im Test (;#TESTBASIS 02000), das Programm selbst ist relativ zu 0000


def code(z):
    """kat5-Code eines Zeichens (Doku 3.3.15): 0-9 = 07..020, a-z = 021..052."""
    if z.isdigit():
        return 0o7 + int(z)
    return 0o21 + ord(z) - ord('a')


def wort(text):
    """kat5-Wort: erstes Zeichen links in z3..z8, 6 Bit je Zeichen, Fuellung 00 rechts, z0 = 0."""
    w = 0
    for i in range(5):
        w = (w << 6) | (code(text[i]) if i < len(text) else 0)
    return w


def text(w):
    """Rueckrechnung: kat5-Wort -> Zeichenkette (nur 0-9 und a-z kommen vor)."""
    r = ''
    for i in range(5):
        c = (w >> (6 * (4 - i))) & 0o77
        if c == 0:
            break
        r += chr(ord('0') + c - 0o7) if c <= 0o20 else chr(ord('a') + c - 0o21)
    return r


zufall = random.Random(8205)
zeichen = 'abcdefghijklmnopqrstuvwxyz0123456789'
texte = []
while len(texte) < N:
    t = ''.join(zufall.choice(zeichen) for _ in range(zufall.randint(1, 5)))
    if t not in texte:
        texte.append(t)
soll = sorted(wort(t) for t in texte)

z = []
zellen = [0]                # Zahl der bisher belegten Zellen (Zaehlerstand relativ zu 0000)
lage = {}                   # Marke -> relative Zelle


def zeile(marke, op, operand, kommentar):
    if marke:
        lage[marke] = zellen[0]
    if op not in ('start', 'end'):
        zellen[0] += 1
    z.append('%-16s%-8s%-14s; %s' % (marke + (':' if marke else ''), op, operand, kommentar))


z.append('; kat5_sort1: Sortier-UP (Makro KAT5SORT, Rel 0000) und Hauptprogramm, erzeugt von gen/kat5_sort1_gen.py')
z.append('; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat5_sort1')
z.append('; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat5_sort1-sw-ausgabe.txt')
z.append(';#TESTBASIS 02000 haupt')
z.append('r1:             abs     07773                ; Register 1: Adresse des Wortes fuer KAT5AUSGABE (Adressfeld)')
z.append('r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle fuer KAT5AUSGABE (Adressfeld)')
zeile('', 'start', '', 'Zaehlung beginnt bei 0000')
zeile('kat5_sort1', 'KAT5SORT', '', 'UP KAT5SORT (Rumpf aus c82ass.makros, Zelle 0000 bis 0065); Parameter auf Marke+1 und Marke+2')
zellen[0] = 0o66            # das Makro belegt 66 Zellen (oktal) in einem Stueck, der Generator zaehlt sie nicht einzeln
rel = '%04o' % zellen[0]
z.append('')
z.append('; ==========================================================')
z.append(';   RELATIVE START-ADRESSE DES HAUPTPROGRAMMS:  %s' % rel)
z.append(';   BIS: Leitadresse 21 2000 .   Start: 10 %s 000 .' % ('%04o' % (BASIS + zellen[0])))
z.append('; ==========================================================')
z.append('')
zeile('haupt', '.LD', '@feld', 'AC := Adresse des Feldes')
zeile('', '.STO', 'kat5_sort1+1', 'Parameter 1 eintragen (Zelle Marke+1)')
zeile('', '.LD', '#%s' % oct(N).replace('0o', '0'), 'AC := %d (Anzahl der Texte)' % N)
zeile('', '.STO', 'kat5_sort1+2', 'Parameter 2 eintragen (Zelle Marke+2)')
zeile('', '025', 'kat5_sort1', 'Aufruf des Unterprogramms')
zeile('', '.LD', '@kbaus', 'AC := Adresse der KB/GB-Zelle des Schreibwerks')
zeile('', '.STO', 'r3', 'R3 := Adresse der Zustandszelle (Festlegung 030)')
zeile('', 'ANWAHL', 'K2', 'Kanal 2 = Schreibwerk anwaehlen')
zeile('', '.LD', '@init', 'AC := Adresse des Wortes Zeilenschaltung + Um. KB')
zeile('', '.STO', 'r1', 'R1 := Adresse von init')
zeile('', '025', 'ausgabe', 'neue Zeile und Um. KB drucken (das BIS laesst das Schreibwerk auf GB)')
zeile('', '.LD', '@feld', 'AC := Adresse des (sortierten) Feldes')
zeile('', '.STO', 'pa', 'pa := Adresse des ersten Textes')
zeile('', '.LD', '#%s' % oct(N).replace('0o', '0'), 'AC := %d (Anzahl der Texte)' % N)
zeile('', '.STO', 'pz', 'pz := Zaehler der noch zu druckenden Texte')
zeile('pl', '.LD', 'pa', 'AC := Adresse des aktuellen Textes')
zeile('', '.STO', 'r1', 'R1 := Adresse des Textes')
zeile('', '025', 'ausgabe', 'Text drucken (KAT5AUSGABE)')
zeile('', '.LD', '@zeil', 'AC := Adresse des Wortes Zeilenschaltung')
zeile('', '.STO', 'r1', 'R1 := Adresse von zeil')
zeile('', '025', 'ausgabe', 'Zeilenschaltung drucken')
zeile('', '.LD', 'pa', 'AC := Adresse des aktuellen Textes')
zeile('', '.ADD', '#01000', 'AC := Adresse des naechsten Textes (eine Adresseinheit weiter)')
zeile('', '.STO', 'pa', 'pa := Adresse des naechsten Textes')
zeile('', '.LD', 'pz', 'AC := Zaehler')
zeile('', '.SUB', '#01', 'AC := Zaehler - 1')
zeile('', '.STO', 'pz', 'pz := AC')
zeile('', '.CMP', '#0', 'AC mit 0 vergleichen')
zeile('', '.JVG3', 'halt', 'Zaehler = 0: alle Texte gedruckt, Halt')
zeile('', '.JMP', 'pl', 'sonst naechster Text')
halt = zellen[0]
zeile('halt', '.STOP', '0', 'Halt: Feld ist sortiert und gedruckt')
for i, t in enumerate(texte):
    zeile('feld' if i == 0 else '', 'kat5', t, 'Text[%d] = %s, Wort %011o' % (i, t, wort(t)))
zeile('zeil', 'kat5', '$wrzl', 'Wort Zeilenschaltung (kat5 053), steht hinter dem Feld')
zeile('init', 'kat5', '$wrzl$inkb', 'Wort Zeilenschaltung und Um. KB (kat5 053, 054): Anfang des Drucks')
zeile('kbaus', 'dw', '0', 'KB/GB-Zustand des Schreibwerks (0 = KB, 1 = GB), anfangs KB (Festlegung 030)')
zeile('pa', 'db', '01', 'Arbeitszelle pa: Adresse des aktuellen Textes beim Drucken')
zeile('pz', 'db', '01', 'Arbeitszelle pz: Zaehler beim Drucken')
zeile('ausgabe', 'KAT5AUSGABE', '', 'UP KAT5AUSGABE (Rumpf aus c82ass.makros, Tabelle dahinter)')
zeile('ende', 'end', '', 'Programmende')
z.append('')
z.append(';#PRUEFE-START')
z.append('; BZ=%04o US=1' % (BASIS + halt + 1))
for i, w in enumerate(soll):
    z.append('; %04o: %011o   # feld+%d' % (BASIS + lage['feld'] + i, w, i))
z.append(';#PRUEFE-ENDE')
z = [l.replace('STARTADR', '%04o' % (BASIS + lage['haupt'])) for l in z]
with open(ZIEL, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(z) + '\n')
with open(SOLLDRUCK, 'w', encoding='utf-8', newline='') as f:
    f.write('\n' + ''.join(text(w) + '\n' for w in soll))
