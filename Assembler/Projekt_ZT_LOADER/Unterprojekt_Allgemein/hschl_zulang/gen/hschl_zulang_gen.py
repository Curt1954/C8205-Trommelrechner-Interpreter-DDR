#!/usr/bin/env python3
"""hschl_zulang_gen.py -- erzeugt hschl_zulang.asm: 2048 Eingaben = 4096 Sektoren (mehr als 4095) fuehren in den Fehlerausgang fe_lang. Aufruf vom Projektstamm (asm_und_test.sh tut es selbst)."""
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'hschl', 'gen'))
from hschl_variante import *

SOLL = """; Sollwerte von Hand hergeleitet: Streifen hschl_zulang.txt = 2048 Eingaben 1 2 <k oktal> . (k = 1 bis 2048) und /. Eingabe k: Kz 1 und 2: Wort 2 = 01 * 2^6 + 02 = 0102, Wort 1 = k (die Ziffern von k oktal als Oktalziffern gelesen ergeben k).
; Nach der 2048. Eingabe zaehlt der Sektorzaehler 4096: 4096 - 4096 >= 0 fuehrt in fe_lang (Parameter 1), fehlart := 2, Halt, keine Rueckgabe (R2 bleibt 0).
; Geschrieben sind bis dahin 127 volle Spuren (127 * 16 = 2032 Eingaben): die Zielspuren zaehlen von p = 127 (Trommel 0, Spur 127) bis p = 253 (Trommel 1, Spur 125): Trommel 0 Spur 127 = Zellen 07740 bis 07777, Trommel 1 Spur 0 bis 125 = Zellen 0000 bis 07677.
; Erste Spur: Zelle 0 = Wort 1 von Eingabe 1 = 1, Zelle 1 = 0102, Zelle 30 = Wort 1 von Eingabe 16 = 16 = 020, Zelle 31 = 0102. Letzte geschriebene Spur (Trommel 1 Spur 125 = Zellen 07640 bis 07677): Eingaben 2017 bis 2032, Zelle 0 = 2017 = 03741 (3 * 512 + 7 * 64 + 4 * 8 + 1), Zelle 30 = 2032 = 03760, Zelle 31 = 0102.
; Die 128. Spur (p = 254 = Trommel 1, Spur 126 = Zellen 07700 bis 07777) wird nicht mehr geschrieben: die Eingaben 2033 bis 2048 stehen nur im Puffer."""
assert 2017 == 0o3741 and 2032 == 0o3760
P = ['US=1', '0001: 00000000000   # dif1: nie berechnet', '0002: 00000000000   # dif3: nie berechnet', '0003: 00000000002   # fehlart: 2 = mehr als 4095 Sektoren', '7776: 00000000000   # R2: unveraendert (kehrt nicht zurueck)',
     'ZT-Zellen-Pruefung:', '0-7677: 00000000000   # Spur 126 der Trommel 0 (davor): nicht beschrieben']
for a, v, t in (('0-7740', 1, 'erste geschriebene Spur: Zelle 0 (Wort 1 der Eingabe 1)'), ('0-7741', 0o102, 'Zelle 1 (Wort 2 der Eingabe 1)'), ('0-7776', 16, 'Zelle 30 (Wort 1 der Eingabe 16)'), ('0-7777', 0o102, 'letzte Zelle der ersten Spur'),
                ('1-0000', 17, 'Trommel 1 Spur 0 (Uebertrag): Wort 1 der Eingabe 17'), ('1-7640', 2017, 'Trommel 1 Spur 125 (letzte geschriebene Spur): Zelle 0 (Eingabe 2017)'),
                ('1-7676', 2032, 'Trommel 1 Spur 125: Zelle 30 (Eingabe 2032)'), ('1-7677', 0o102, 'Trommel 1 Spur 125: letzte Zelle')):
    P.append('%s: %s   # %s' % (a, o11(v), t))
P += ['1-7700: 00000000000   # Trommel 1 Spur 126: nicht mehr geschrieben', '1-7777: 00000000000   # Trommel 1 Spur 127: nicht geschrieben']
erzeuge('hschl_zulang', '2048 Eingaben', '2048 Eingaben = 4096 Sektoren (mehr als 4095): Fehlerausgang fe_lang nach 127 geschriebenen Spuren, Halt, keine Rueckgabe', 'hschl_zulang.txt', SOLL, P, os.path.join(hier, '..'))
