#!/usr/bin/env python3
"""hschl_rand_gen.py -- erzeugt hschl_rand.asm: 16 Eingaben, dann eine 17. Eingabe, die vor ihrem Ende von / abgebrochen wird (verworfen). Aufruf vom Projektstamm (asm_und_test.sh tut es selbst)."""
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'hschl', 'gen'))
from hschl_variante import *

w = modell(''.join(E_HAUPT[:16]) + '215/')
assert w == modell(''.join(E_HAUPT[:16]) + '/') and len(w) == 32
SOLL = """; Sollwerte von Hand hergeleitet: Streifen hschl_rand.txt = die ersten 16 Eingaben von hschl.txt, dann 2 1 5 und / (eine 17. Eingabe ohne Punkt, vom Streifenende abgebrochen).
; Die begonnene 17. Eingabe wird verworfen (nichts in den Puffer geschrieben, nicht gezaehlt): Sektoranzahl R2 = 32 = 040, genau eine Spur (ZT 0 Spur 127), keine zweite Spur; ZT 1 Spur 0 bleibt 0. Inhalt der Spur wie bei hschl_voll."""
P = ['US=1', '0001: 00000000000   # dif1: R1 unveraendert', '0002: 00000000000   # dif3: R3 unveraendert', '0003: 00000000000   # fehlart: kein Fehler', '7776: 00000000040   # R2: Sektoranzahl 32 (die 17. Eingabe zaehlt nicht)', '7775: 00000000001   # KBGB unveraendert 1',
     'ZT-Zellen-Pruefung:']
P += ['0-7740: %s   # Wort 0' % o11(w[0]), '0-7777: %s   # Wort 31' % o11(w[31]),
      '1-0000: 00000000000   # keine zweite Spur: die abgebrochene Eingabe wird verworfen', '1-0001: 00000000000   # Zelle 1 der zweiten Spur: 0']
erzeuge('hschl_rand', '/ bricht eine Eingabe ab', '16 Eingaben, die 17. von / abgebrochen: verworfen, eine Spur, R2 = 32', 'hschl_rand.txt', SOLL, P, os.path.join(hier, '..'))
