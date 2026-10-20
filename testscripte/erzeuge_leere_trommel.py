#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
erzeuge_leere_trommel.py -- erzeugt eine Trommeldatei mit 4096 Zeilen,
alle Zellen auf 00000000000.

Format je Zeile: 'aaaa: ttttttttttt\n' (4 Oktalziffern Adresse, ': ', 11 Oktalziffern Wert).

Aufruf:
    python3 testscripte/erzeuge_leere_trommel.py
    python3 testscripte/erzeuge_leere_trommel.py --aus Trommel/trommel.txt

Ohne Schalter gilt die Vorgabe:
    --aus Trommel/trommel.txt   (im Projektverzeichnis, eine Ebene ueber testscripte/)
"""
import argparse
import os


ADR_MAX = 0o7777          # letzte Adresse (4095 dezimal); 4096 Zellen insgesamt


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Projektverzeichnis; das Skript liegt in testscripte/
    ap = argparse.ArgumentParser(description='Trommeldatei mit Nullen erzeugen (4096 Zeilen).')
    ap.add_argument('--aus', default=os.path.join(here, 'Trommel', 'trommel.txt'),
                    help='Zieldatei; Vorgabe: Trommel/trommel.txt im Projektverzeichnis')
    args = ap.parse_args()

    zielordner = os.path.dirname(os.path.abspath(args.aus))
    if zielordner:
        os.makedirs(zielordner, exist_ok=True)

    # newline='' : '\n' bleibt unter Windows ein einzelnes LF (sonst CRLF = 19 statt 18 Byte je Zeile)
    with open(args.aus, 'w', encoding='utf-8', newline='') as fh:
        for adr in range(ADR_MAX + 1):
            fh.write(f'{adr:04o}: 00000000000\n')

#    print(f'{ADR_MAX + 1} Zeilen geschrieben nach: {args.aus}')
#    print(f'Alle Zellen auf 00000000000 (Adressen 0000 bis {ADR_MAX:04o}).')


if __name__ == '__main__':
    main()
