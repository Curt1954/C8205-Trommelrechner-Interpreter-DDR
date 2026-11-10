#!/usr/bin/env python3
"""hschl_ziffer_gen.py -- erzeugt hschl_ziffer.asm: die Ziffern 8 und 9 sind kein Fehler mehr (Kennzeichen gueltig, im Ziffernteil uebergangen). Aufruf vom Projektstamm (asm_und_test.sh tut es selbst)."""
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'hschl', 'gen'))
from hschl_variante import *

w = modell(''.join(E_ZIFFER) + '/')
assert [o11(x) for x in w] == ['00000000000', '00000001011', '00000000007', '00000000010', '00000000000', '00000002010']
SOLL = """; Sollwerte von Hand hergeleitet: Streifen hschl_ziffer.txt = 3 Eingaben und /. Der frueher gemeldete Fehler "Ziffer 8 oder 9" gibt es nicht mehr (Typ 10, 7a).
;   1  8 9 .              8 und 9 als Kennzeichen: Wort 2 = 010 * 2^6 + 011 = 01011, Wort 1 = 0
;   2  0 8 9 8 Leertaste 9 7 .   Kz 0 (00) und 8 (010): Wort 2 = 00 * 2^6 + 010 = 010; im Ziffernteil werden 9, 8, Leertaste und 9 uebergangen, Ziffer 7: Wort 1 = 7
;   3  + 8 .              Kz + (020) und 8 (010): Wort 2 = 020 * 2^6 + 010 = 02010, Wort 1 = 0
; Sektoranzahl R2 = 6, kein Fehler (fehlart 0), eine Spur auf Trommel 0 Spur 127 (Zellen 07740 bis 07745), der Rest 0."""
P = ['US=1', '0001: 00000000000   # dif1: R1 unveraendert', '0002: 00000000000   # dif3: R3 unveraendert', '0003: 00000000000   # fehlart: kein Fehler (8 und 9 sind keine Fehler mehr)', '7776: 00000000006   # R2: Sektoranzahl 6', '7775: 00000000001   # KBGB unveraendert 1',
     'ZT-Zellen-Pruefung:']
P += zt_spur(0, 127, w, 0, 'ZT 0 Spur 127: Wort')
P += ['0-7746: 00000000000   # Rest der Spur: 0', '0-7777: 00000000000   # letzte Zelle der Spur: 0', '1-0000: 00000000000   # keine zweite Spur']
erzeuge('hschl_ziffer', 'Ziffern 8 und 9 kein Fehler', 'Ziffern 8 und 9 als Kennzeichen gueltig, im Ziffernteil uebergangen, kein Fehler', 'hschl_ziffer.txt', SOLL, P, os.path.join(hier, '..'))
