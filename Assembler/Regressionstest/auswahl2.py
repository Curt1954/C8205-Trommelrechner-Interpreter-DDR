#!/usr/bin/env python3
"""Gemeinsame Auswahl (Programme + Negativtests): Phase 1 volle Zaehlerabdeckung, Phase 2 auffuellen auf die Haelfte.
Aufruf: auswahl2.py <datenverz> <ausgabeverz>"""
import os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from gcda import lies_verz
daten, aus = sys.argv[1], sys.argv[2]
os.makedirs(aus, exist_ok=True)
tests = {d: lies_verz(os.path.join(daten, d))[0] for d in sorted(os.listdir(daten))}
union = set().union(*tests.values())
freq = collections.Counter()
for t in tests.values(): freq.update(t)
ziel = (len(tests) + 1) // 2
unb = set(union); g = []
while unb:
    b = max((n for n in tests if n not in g), key=lambda n: (sum(1.0 / freq[c] for c in tests[n] & unb), len(tests[n])))
    g.append(b); unb -= tests[b]
p1 = len(g)
cnt = collections.Counter()
for n in g: cnt.update(tests[n])
while len(g) < ziel:
    b = max((n for n in tests if n not in g), key=lambda n: (sum(1.0 / (1 + cnt[c]) ** 2 for c in tests[n]), len(tests[n])))
    g.append(b); cnt.update(tests[b])
abd = set().union(*(tests[n] for n in g))
print(f'Tests {len(tests)}, Ziel {ziel}, Phase 1 {p1}, gewaehlt {len(g)} (prog {sum(n.startswith("prog_") for n in g)}, neg {sum(n.startswith("neg_") for n in g)}); Zaehler {len(abd)} von {len(union)}')
for art in ('neg', 'prog'):
    gw = sorted(n[len(art) + 1:] for n in g if n.startswith(art + '_'))
    al = sorted(n[len(art) + 1:] for n in tests if n.startswith(art + '_'))
    open(os.path.join(aus, art + '_gewaehlt.txt'), 'w').write('\n'.join(gw) + '\n')
    open(os.path.join(aus, art + '_alle.txt'), 'w').write('\n'.join(al) + '\n')
    open(os.path.join(aus, art + '_entfallen.txt'), 'w').write('\n'.join(x for x in al if x not in set(gw)) + '\n')
