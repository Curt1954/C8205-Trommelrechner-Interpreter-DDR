#!/usr/bin/env python3
"""zil_lsziffer_gen.py -- erzeugt zil_lsziffer.asm aus zil/zil.asm: Ja-Weg, die Ziffern 8 und 9 im Streifen (Leser 1) sind seit Typ 10 KEIN Fehler mehr (Kennzeichen gueltig, im Ziffernteil uebergangen); ZTD wird normal geladen. Aufruf vom Projektstamm (asm_und_test.sh tut es selbst)."""
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'zil', 'gen'))
from zil_variante import erzeuge

SOLL = """; Sollwerte von Hand hergeleitet (Ja-Weg, Streifen mit den Ziffern 8 und 9; der frueher gemeldete Fehler "lochstreifen fehlerhaft" entfaellt seit der Ablage als Typ 10, 01.11.2026):
; Eingabe wie zil (Datei zil.txt). Leser 1: Streifen hschl_ziffer.txt = 3 Eingaben 8 9 . / 0 8 9 8 Leertaste 9 7 . / + 8 . und / (Beschreibung bei hschl_ziffer): Worte 0, 01011, 7, 010, 0, 02010 = 6 Sektoren.
; Der Lauf ist der Ja-Weg von zil bis "ZTD geladen mit Programm-ID 1" (Ausgabe wie zil). Zellen: status = 3, KBGB = 0, R2 = 0 und R3 = 1 (Endwerte wie zil), SPUF-PN Zelle 1 = 20010410000 + 6 = 20010410006 (Wort 2 mit Laenge 6, auch auf ZT 0 Spur 1; Name kat5 ztd = 05244240000 in Zelle 0),
;   Puffer Programmcode (1440): Zellen 0 bis 5 = 0, 01011, 7, 010, 0, 02010, Zelle 6 = 0 (vorher mit 441 geloescht); ZT 0 Spur 33 (Zellen 02040 bis 02045) dieselben sechs Worte, Rest der Spur 0.""" 
W = ['00000000000', '00000001011', '00000000007', '00000000010', '00000000000', '00000002010']
P = ['0001: 00000000003   # status: Weg 3 (Ja)', '7775: 00000000000   # KBGB: letzte Ausschrift endet in KB', '7776: 00000000000   # R2: 0 (Trommelnummer, von Element 16 fuer neuanl gesetzt)', '7774: 00000000001   # R3: Spurnummer 1 (Element 16)',
     '1340: 05244240000   # SPUF-PN Zelle 0: Wort 1 = Name ztd (kat5, PNAME)', '1341: 20010410006   # SPUF-PN Zelle 1: Wort 2 mit Laenge 6', '1342: 00000000000   # SPUF-PN Zelle 2: Wort 1 von ID 2, nie beschrieben',
     '1300: 52525252525   # SPUF-00 Zelle 0: Repository-Kennzeichen (ztinit)', '1320: 00000000001   # SPUF-00 Zelle 16: Repository-Kopf', '1321: 00000000001   # SPUF-00 Zelle 17: Zaehler 1 (PNAME)', '1323: 00000000040   # SPUF-00 Zelle 19: letzte belegte Spur (32 dezimal)']
P += ['%04o: %s   # Puffer Programmcode Zelle %d' % (0o1440 + i, W[i], i) for i in range(6)] + ['1446: 00000000000   # Puffer Programmcode Zelle 6: Rest 0 (vorher geloescht)']
P += ['ZT-Zellen-Pruefung:', '0-0000: 52525252525   # ZT 0 Spur 0 Zelle 0', '0-0020: 00000000001   # Zelle 16', '0-0021: 00000000001   # Zelle 17', '0-0022: 00000000000   # Zelle 18', '0-0023: 00000000040   # Zelle 19 (32 dezimal)',
      '0-0040: 05244240000   # Verzeichnis Spur 1 Zelle 0: Wort 1 = Name ztd (kat5)', '0-0041: 20010410006   # Verzeichnis Spur 1 Zelle 1: Wort 2 mit Laenge 6', '0-0042: 00000000000   # Verzeichnis Spur 1 Zelle 2: Wort 1 von ID 2', '0-0100: 00000000000   # Spur 2 Zelle 0']
P += ['0-%04o: %s   # ZT 0 Spur 33 Zelle %d' % (0o2040 + i, W[i], i) for i in range(6)] + ['0-2046: 00000000000   # Rest der Spur 33: 0', '0-2077: 00000000000   # letzte Zelle der Spur 33: 0', '0-2100: 00000000000   # Spur 34 nicht beschrieben']
erzeuge('zil_lsziffer', os.path.join(hier, '..'),
        'zil (Prototyp): Ja-Weg, Ziffern 8 und 9 im Streifen sind kein Fehler: ZTD wird geladen',
        1, 'zil.txt', SOLL, P, 'Variante: Streifen mit den Ziffern 8 und 9 (Typ 10).', leser1='hschl_ziffer.txt')
