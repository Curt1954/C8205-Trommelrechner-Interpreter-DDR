#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_trommel_waechter.py - Waechter zu OP-19 (GRAFIK_Beschreibung §10.4/§10.5, entschieden 21.10.2026, Variante b): Die Trommeldatei ist der
Speicher des Rechners; ein Sammellauf darf sie nicht veraendern, sonst sind die Laeufe nicht reproduzierbar.
Aufruf:
  python3 testscripte/grafik_trommel_waechter.py merken  STANDDATEI [PROJEKTORDNER]   Pruefsummen von Trommel/trommel.txt und Trommel/trommel.basp merken
  python3 testscripte/grafik_trommel_waechter.py pruefen STANDDATEI [PROJEKTORDNER]   mit dem gemerkten Stand vergleichen; Rueckgabewert 0 = unveraendert,
                                                                                   1 = veraendert (die Datei wird NICHT zurueckgesetzt), 2 = Aufruf/Stand unlesbar
Eine fehlende Datei zaehlt als eigener Zustand (fehlt vorher und nachher = unveraendert; entsteht oder verschwindet sie = veraendert).
Wird von testscripte/grafik_alle_tests.sh vor dem ersten und nach dem letzten Block aufgerufen; ohne Aenderung am Projekt.
"""
import hashlib, json, os, sys

HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)
DATEIEN = ('Trommel/trommel.txt', 'Trommel/trommel.basp')


def stand(projekt):
    erg = {}
    for rel in DATEIEN:
        p = os.path.join(projekt, *rel.split('/'))
        if os.path.isfile(p):
            with open(p, 'rb') as fh:
                erg[rel] = hashlib.sha256(fh.read()).hexdigest()
        else:
            erg[rel] = None
    return erg


def merken(standdatei, projekt=PROJ):
    with open(standdatei, 'w', encoding='utf-8') as fh:
        json.dump(stand(projekt), fh)
    return 0


def pruefen(standdatei, projekt=PROJ, aus=sys.stdout):
    try:
        with open(standdatei, encoding='utf-8') as fh:
            vorher = json.load(fh)
    except (OSError, ValueError) as e:
        print(f'Waechter: Stand nicht lesbar ({standdatei}): {e}', file=sys.stderr)
        return 2
    jetzt = stand(projekt)
    diff = [rel for rel in DATEIEN if vorher.get(rel) != jetzt[rel]]
    for rel in diff:
        was = 'fehlte' if vorher.get(rel) is None else 'war da'
        jetzt_ = 'fehlt' if jetzt[rel] is None else 'ist da'
        print(f'Waechter: {rel} hat sich waehrend des Laufs veraendert (vorher {was}, jetzt {jetzt_}, Pruefsumme verschieden)', file=aus)
    if not diff:
        print('Waechter: Trommel/trommel.txt und trommel.basp unveraendert', file=aus)
    return 1 if diff else 0


def main(argv):
    if len(argv) < 3 or argv[1] not in ('merken', 'pruefen') or len(argv) > 4:
        print(__doc__, file=sys.stderr)
        return 2
    projekt = argv[3] if len(argv) == 4 else PROJ
    return (merken if argv[1] == 'merken' else pruefen)(argv[2], projekt)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
