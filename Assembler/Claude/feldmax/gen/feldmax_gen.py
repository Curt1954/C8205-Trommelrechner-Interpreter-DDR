#!/usr/bin/env python3
"""feldmax_gen.py -- Generator fuer feldmax.asm (Pilot der Python-Makrosprache).

Aufgabe: Summe, Maximum und Anzahl der Zellen eines Feldes aus 8 Zahlen (mit negativen Werten).
Aufruf (vom Projektstamm): python3 -I Assembler/Claude/feldmax/gen/feldmax_gen.py
"""
import os
import sys

hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'gen_lib'))
from c82gen import Prog

WERTE = [7, -3, 12, 5, -9, 12, 0, 4]       # Eingabefeld

P = Prog('feldmax -- Summe und Maximum eines Feldes aus 8 Zahlen', grenze=0o200)
P.nullen('summe'); P.nullen('i')
P.feld_lesen('feld', 'i'); P.speichere('max')
P.lab('schl')
P.feld_lesen('feld', 'i'); P.speichere('wert')
P.addiere('summe'); P.speichere('summe')
P.wenn_kleiner_gleich('wert', 'max', 'weiter', 'wert <= max: max bleibt')
P.speichere('max', 'max := wert')
P.lab('weiter')
P.erhoehe('i', P.ae(1))
P.wenn_gleich('i', P.ae(len(WERTE)), 'fertig', 'i = n (in Adresseneinheiten): fertig')
P.sprung('schl')
P.lab('fertig')
P.diag(1)
P.halt('Halt: Ergebnis in summe und max')
P.feld('feld', WERTE, 'feld')
for v in ('summe', 'max', 'i', 'wert'):
    P.arbeit(v, 'Arbeitszelle ' + v)
P.schreibe(os.path.join(hier, '..', 'feldmax.asm'), pruefe={'summe': sum(WERTE), 'max': max(WERTE)},
           gen_name='Assembler/Claude/feldmax/gen/feldmax_gen.py')
