#!/usr/bin/env python3
"""hschl_leer_gen.py -- erzeugt hschl_leer.asm: ein Streifen ohne Eingabe (nur /). Aufruf vom Projektstamm (asm_und_test.sh tut es selbst)."""
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'hschl', 'gen'))
from hschl_variante import *

assert modell('/') == []
SOLL = """; Sollwerte von Hand hergeleitet: Streifen hschl_leer.txt = nur / (keine Eingabe). hschl schreibt nichts auf die ZT und liefert Sektoranzahl R2 = 0 (Festlegung dieser Fassung: keine Fehlermeldung); R1, R3 und KBGB bleiben unveraendert.
; Der Spurpuffer bleibt 0 (mit 441 geloescht), auf ZT 0 Spur 127 (Zellen 07740 bis 07777) und ZT 1 Spur 0 steht nichts."""
P = ['US=1', '0001: 00000000000   # dif1: R1 unveraendert', '0002: 00000000000   # dif3: R3 unveraendert', '0003: 00000000000   # fehlart: kein Fehler', '7776: 00000000000   # R2: Sektoranzahl 0', '7775: 00000000001   # KBGB unveraendert 1',
     'ZT-Zellen-Pruefung:', '0-7740: 00000000000   # Spur 127 der Trommel 0: nichts geschrieben', '0-7777: 00000000000   # letzte Zelle der Spur 127: nichts geschrieben', '1-0000: 00000000000   # Trommel 1 Spur 0: nichts geschrieben']
erzeuge('hschl_leer', 'keine Eingabe', 'nur /: keine Eingabe, nichts geschrieben, R2 = 0', 'hschl_leer.txt', SOLL, P, os.path.join(hier, '..'))
