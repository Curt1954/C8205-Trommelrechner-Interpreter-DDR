#!/usr/bin/env python3
"""hschl_voll_gen.py -- erzeugt hschl_voll.asm: genau 16 Eingaben = 32 Worte (Spur voll), danach /. Aufruf vom Projektstamm (asm_und_test.sh tut es selbst)."""
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'hschl', 'gen'))
from hschl_variante import *

w = modell(''.join(E_HAUPT[:16]) + '/')
assert len(w) == 32
SOLL = """; Sollwerte von Hand hergeleitet: Streifen hschl_voll.txt = die ersten 16 Eingaben des Streifens hschl.txt (Beschreibung dort) und /; 16 Eingaben = 32 Worte fuellen den Spurpuffer genau.
; Die volle Spur wird sofort geschrieben (Puffer voll), danach bleibt der Zeiger am Anfang des Puffers: das Streifenende / findet einen leeren Puffer und schreibt KEINE zweite (leere) Spur.
; Es wird GENAU EINE Spur geschrieben (ZT 0 Spur 127 = Zellen 07740 bis 07777); ZT 1 Spur 0 bleibt 0. Sektoranzahl R2 = 32 = 040. Wort 0 und 1 = Eingabe 1 (71234567012 / 02000), Wort 30 und 31 = Eingabe 16 (Kz 3 4, Ziffern 2 0 7 2 0)."""
assert [o11(x) for x in (w[0], w[1], w[30], w[31])] == ['71234567012', '00000002000', '00000020720', '00000000304']
P = ['US=1', '0001: 00000000000   # dif1: R1 unveraendert', '0002: 00000000000   # dif3: R3 unveraendert', '0003: 00000000000   # fehlart: kein Fehler', '7776: 00000000040   # R2: Sektoranzahl 32', '7775: 00000000001   # KBGB unveraendert 1',
     'ZT-Zellen-Pruefung:']
P += ['0-7740: %s   # Wort 0' % o11(w[0]), '0-7741: %s   # Wort 1' % o11(w[1]), '0-7776: %s   # Wort 30' % o11(w[30]), '0-7777: %s   # Wort 31' % o11(w[31]),
      '1-0000: 00000000000   # keine zweite Spur (Spur voll und Ende zugleich: nur eine Ausgabe)', '0-7677: 00000000000   # Spur davor nicht beschrieben']
erzeuge('hschl_voll', '16 Eingaben, Spur genau voll', '16 Eingaben = 32 Worte: eine Spur, keine zweite', 'hschl_voll.txt', SOLL, P, os.path.join(hier, '..'))
