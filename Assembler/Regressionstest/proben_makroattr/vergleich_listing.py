#!/usr/bin/env python3
# vergleich_listing.py <asm> <listing>: Sollwerte aus den "; E=a,b,c"-Marken der .asm (in Reihenfolge) gegen die aufgeloesten dw-Zeilen im Listing
# des Assemblers (Standardausgabe von c82ass). Fuer Proben, die der Assembler ablehnt (rc 16) und von denen deshalb keine .dmp entsteht.
# Aufruf: (cd Assembler && ./_Linux/c82ass --no-color -p <ordner> -s <n>.asm > /tmp/l.txt 2>&1); python3 vergleich_listing.py <ordner>/<n>.asm /tmp/l.txt
import re, sys
asm, lst = sys.argv[1], sys.argv[2]
soll = []   # (zeilennr, text, wert)
for n, z in enumerate(open(asm, encoding='utf-8'), 1):
    m = re.search(r';\s*E=([0-9,]+)\s*$', z.rstrip('\n'))
    if m and not z.lstrip().startswith(';'):
        for w in m.group(1).split(','):
            soll.append((n, z.split(';')[0].strip(), int(w)))
ist = []
for z in open(lst, encoding='utf-8'):
    m = re.match(r'^\s+dw\s+(\d+)\s', z)       # nur aufgeloeste dw-Zeilen (die Makrodefinition steht mit $CALC im Text)
    if m: ist.append(int(m.group(1)))
fehler = 0
for k, (n, t, w) in enumerate(soll):
    i = ist[k] if k < len(ist) else None
    if i != w:
        fehler += 1
        print(f'ABWEICHUNG Nr. {k+1} Zeile {n} "{t}": soll {w}, ist {i}')
if len(ist) != len(soll):
    fehler += 1
    print(f'ABWEICHUNG Anzahl: {len(soll)} Sollwerte, {len(ist)} dw-Zeilen im Listing')
print(f'{len(soll)} Sollwerte, {fehler} Abweichungen')
