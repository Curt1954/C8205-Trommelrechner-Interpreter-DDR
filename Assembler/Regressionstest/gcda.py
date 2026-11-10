#!/usr/bin/env python3
"""Liest .gcda-Dateien (GCC 13) und liefert die Menge der Zaehler mit Wert > 0.
Schluessel: (Dateiname, Funktionskennung, Zaehlerindex)."""
import os, struct, sys

def lies(pfad):
    d = open(pfad, 'rb').read()
    if d[:4] == b'adcg': e = '<'
    elif d[:4] == b'gcda': e = '>'
    else: raise ValueError('kein gcda: ' + pfad)
    ps = 16
    treffer = set(); alle = 0
    ident = None
    n = len(d)
    while ps + 8 <= n:
        tag, ln = struct.unpack_from(e + 'II', d, ps)
        pl = ps + 8
        if tag == 0x01000000:
            ident = struct.unpack_from(e + 'I', d, pl)[0]
        elif tag == 0x01a10000 and ln >= 0x80000000:
            # alle Zaehler der Funktion sind 0: negative Laenge, keine Nutzdaten
            alle += ((1 << 32) - ln) // 8
            ps = pl
            continue
        elif tag == 0x01a10000:
            anz = ln // 8
            vals = struct.unpack_from(e + '%dQ' % anz, d, pl) if False else None
            for i in range(anz):
                lo, hi = struct.unpack_from(e + 'II', d, pl + 8 * i)
                alle += 1
                if lo or hi: treffer.add((os.path.basename(pfad), ident, i))
        ps = pl + ln
    return treffer, alle

def lies_verz(verz):
    t = set(); a = 0
    for wurzel, _, dateien in os.walk(verz):
        for f in dateien:
            if f.endswith('.gcda'):
                x, y = lies(os.path.join(wurzel, f)); t |= x; a += y
    return t, a

if __name__ == '__main__':
    t, a = lies_verz(sys.argv[1])
    print(len(t), 'von', a, 'Zaehlern > 0')
