#!/usr/bin/env python3
# vergleich.py <asm> <dmp>: Sollwerte aus den "; E=a,b,c"-Marken der .asm (in Reihenfolge, ab Zelle 1) gegen die Woerter der .dmp
import re, sys
asm, dmp = sys.argv[1], sys.argv[2]
soll = []   # (zeilennr, text, wert)
for n, z in enumerate(open(asm, encoding='utf-8'), 1):
    m = re.search(r';\s*E=([0-9,]+)\s*$', z.rstrip('\n'))
    if m and not z.lstrip().startswith(';'):
        for w in m.group(1).split(','):
            soll.append((n, z.split(';')[0].strip(), int(w)))
ist = {}
for z in open(dmp, encoding='utf-8'):
    m = re.match(r'^([0-7]{4}): (?:00 ([0-7]{11})|0\s)', z)
    if m: ist[int(m.group(1), 8)] = int(m.group(2), 8) if m.group(2) else 0
fehler = 0
for k, (n, t, w) in enumerate(soll, 1):
    i = ist.get(k)
    if i != w:
        fehler += 1
        print(f'ABWEICHUNG Zelle {k:04o} (dez {k}) Zeile {n} "{t}": soll {w}, ist {i}')
print(f'{len(soll)} Sollwerte, {fehler} Abweichungen')
