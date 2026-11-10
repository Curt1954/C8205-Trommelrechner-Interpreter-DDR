#!/usr/bin/env python3
"""hschl_gen.py -- erzeugt hschl.asm (Hauptfall: 17 Eingaben, 34 Worte, zwei Spuren mit Trommeluebertrag). Aufruf vom Projektstamm (asm_und_test.sh tut es selbst)."""
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, hier)
from hschl_variante import *

w = modell(haupt_text())
assert len(w) == 34
# Handrechnung (7a): Beispiele 1 bis 3, Eingabe 4 bis 8 und 9
hand = ['71234567012', '00000002000', '00000000123', '00000002000', '00000000000', '00000000200', '00000000005', '00000000201',
        '00000000000', '00000000303', '00000000000', '00000000700', '00000000000', '00000001011', '77777777777', '00000000000', '00000011711', '00000000304']
assert [o11(x) for x in w[:18]] == hand, [o11(x) for x in w[:18]]

SOLL = """; Sollwerte von Hand hergeleitet (Python-Modell in gen/hschl_variante.py nach 7a; die ersten 9 Eingaben unten von Hand nachgerechnet). Ablage als Typ 10: je Eingabe 2 Zellen, Wort 1 = Datenwert (11 Oktalziffern), Wort 2 = Kennzeichen (Kz 1 in z21 bis z26, Kz 2 in z27 bis z32, je Eingabeadresse).
; Streifen hschl.txt (Leser 1) = 17 Eingaben, dann WRZL und /:
;   1  + 0 7 7 1 2 3 4 5 6 7 0 1 2 :   Kz + (20) und 0 (00): Wort 2 = 20 * 2^6 + 00 = 02000; 12 Ziffern, die letzten 11 bleiben: Wort 1 = 71234567012
;   2  + 0 1 2 3 :                    Wort 1 = 123, Wort 2 = 02000
;   3  2 .                            Kz 2 (02) und 0 ergaenzt: Wort 2 = 02 * 2^6 = 0200, Wort 1 = 0
;   4  2 Leertaste 1 a 8 WRZL 9 + 5 : Kz 2 (02) und 1 (01): Wort 2 = 0201; Leertaste, a, 8, WRZL, 9 und + im Ziffernteil werden uebergangen, Ziffer 5: Wort 1 = 5
;   5  Um. GB 3 3 .                    Um. GB wird nur nach KBGB gefuehrt (nicht gespeichert); Kz 3 und 3: Wort 2 = 03 * 2^6 + 03 = 0303, Wort 1 = 0
;   6  Um. KB 7 .                      ein einzelnes Kz 7 (07): Wort 2 = 07 * 2^6 = 0700, Wort 1 = 0
;   7  8 9 .                           8 (Eingabeadresse 010) und 9 (011) sind als Kz gueltig: Wort 2 = 010 * 2^6 + 011 = 01011, Wort 1 = 0
;   8  0 0 und elf Siebenen :          Wort 1 = 77777777777 (z0 gesetzt), Wort 2 = 0
;   9 bis 17: 3 4 k 7 k . mit k = 011 bis 021 (zweimal k in Oktalziffern): Kz 3 und 4: Wort 2 = 03 * 2^6 + 04 = 0304; Eingabe 9: Ziffern 1 1 7 1 1 = Wort 1 = 11711.
; 17 Eingaben = 34 Sektoren: die ersten 16 Eingaben (32 Worte) fuellen die erste Spur und gehen auf Trommel 0, Spur 127 = ZT-Zellen 127 * 32 = 4064 dez = 07740 bis 07777; die Zaehlung geht dann auf Trommel 1, Spur 0 (Zellen 0000 bis 0037) ueber:
; dort liegt die 17. Eingabe (Worte 32 und 33). Die zweite Spur wird mit dem Puffer geschrieben, der vorher mit 441 geloescht wurde: Zellen 0002 bis 0037 sind 0. Sektoranzahl R2 = 34 = 042.
; R1 (Adresse spufpc), R3 (127) und KBGB (vor dem Aufruf 1, der Streifen enthaelt Um. GB und Um. KB) bleiben unveraendert.
"""
P = ['US=1', '0001: 00000000000   # dif1: R1 unveraendert', '0002: 00000000000   # dif3: R3 unveraendert', '0003: 00000000000   # fehlart: kein Fehler',
     '7776: 00000000042   # R2: Sektoranzahl 34', '7775: 00000000001   # KBGB unveraendert 1']
P += ['ZT-Zellen-Pruefung:']
P += zt_spur(0, 127, w[:32], 0, 'ZT 0 Spur 127: Wort')
P += zt_spur(1, 0, w[32:], 32, 'ZT 1 Spur 0 (Uebertrag der Trommel): Wort')
P += ['1-0002: 00000000000   # Rest der zweiten Spur: 0 (Puffer vorher geloescht)', '1-0037: 00000000000   # letzte Zelle der zweiten Spur: 0',
      '1-0040: 00000000000   # Spur 1 der Trommel 1 nicht beschrieben', '0-7677: 00000000000   # Spur 126 der Trommel 0 (davor) nicht beschrieben', '0-0000: 00000000000   # Spur 0 der Trommel 0 nicht beschrieben']
erzeuge('hschl', '17 Eingaben, 34 Worte, Trommeluebertrag', '17 Eingaben (Typ 10), 34 Worte, zwei Spuren, Uebertrag Spur 127 -> Trommel 1 Spur 0, R1, R3 und KBGB unveraendert', 'hschl.txt', SOLL, P,
        os.path.join(hier, '..'))
