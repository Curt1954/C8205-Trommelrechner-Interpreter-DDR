#!/usr/bin/env python3
"""zil_lszulang_gen.py -- erzeugt zil_lszulang.asm aus zil/zil.asm: Ja-Weg, ein Streifen mit 2048 Eingaben = 4096 Sektoren (Leser 1) fuehrt in den Fehlerausgang fe_lang (Element 15b). Aufruf vom Projektstamm (asm_und_test.sh tut es selbst)."""
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'zil', 'gen'))
from zil_variante import erzeuge

SOLL = """; Sollwerte von Hand hergeleitet (Ja-Weg, Fehler im Lochstreifen: mehr als 4095 Sektoren):
; Eingabe wie zil (Datei zil.txt). Leser 1: Streifen hschl_zulang.txt = 2048 Eingaben 1 2 <k oktal> . (k = 1 bis 2048) und /: Eingabe k = Wort 1 k, Wort 2 0102 (Kz 1 und 2: 01 * 2^6 + 02).
; hschl (Makro HSCHL, Typ 10) legt die 2048. Eingabe noch in den Puffer, zaehlt dann 4096 und springt auf fe_lang (15b): Ausschrift "lochstreifen zu lang", Halt. Bis dahin sind 127 volle Spuren geschrieben (127 * 16 = 2032 Eingaben):
;   ZTD beginnt auf Trommel 0 Spur 33, die Spuren 33 bis 127 (95 Spuren, ZT-Zellen 02040 bis 07777) liegen auf ZT 0, danach (Uebertrag) Spur 0 bis 31 auf ZT 1 (32 Spuren, Zellen 0000 bis 01777); zusammen 127 Spuren.
;   Die 128. Spur (ZT 1 Spur 32 = Zellen 02000 bis 02037) wird nicht mehr geschrieben, sie steht nur im Puffer Programmcode (1440 bis 1477): Eingaben 2033 bis 2048, Zelle 0 = 2033 = 03761, Zelle 1 = 0102, Zelle 30 = 2048 = 04000, Zelle 31 = 0102.
;   Letzte Spur auf ZT 0 (Spur 127 = Zellen 07740 bis 07777): Eingaben 1505 bis 1520 (95 Spuren * 16 = 1520), Zelle 30 = 1520 = 02760, Zelle 31 = 0102; ZT 1 Spur 0: Eingabe 1521 = 02761. Letzte geschriebene Spur (ZT 1 Spur 31 = Zellen 01740 bis 01777): Eingaben 2017 bis 2032, Zelle 0 = 03741, Zelle 31 = 0102.
; Ausgabe auf SW: zuerst eine Zeilenschaltung (leere erste Zeile), dann die Ausschriften des Ja-Wegs bis "Lochband mit ZTD in Leser 1 einlegen", dann "lochstreifen zu lang"; danach Halt, kein Eintrag der Laenge in SPUF-PN, kein Schreiben von SPUF-PN.
; Nach der Frage steht eine leere Zeile (7a, Zeilenschaltung nach der Antwort J).
; Zellen und Register nach dem Lauf: status = 3 (Zelle 0001, 15b setzt status nicht), KBGB = 0 (Zelle 7775: die letzte Ausschrift endet in KB), R2 = 0 (hschl kehrt nicht zurueck), R3 = 33 (oktal 41),
;   SPUF-PN (ab 1340, Zellen 0 und 1) enthaelt den Eintrag von PNAME ohne Laenge (Wort 1 = ztd = 05244240000, Wort 2 = 20010410000); der Zaehler in SPUF-00 Zelle 17 (1321) ist 1 (PNAME).
; neuanl (Element 14, vor 15) hat SPUF-PN schon mit Laenge 0 auf ZT 0 Spur 1 und 2 geschrieben: ZT 0040 = 05244240000, 0041 = 20010410000, 0042 = 0, 0100 = 0."""
assert 2033 == 0o3761 and 2048 == 0o4000 and 1520 == 0o2760 and 1521 == 0o2761 and 2017 == 0o3741 and 95 * 16 == 1520
def o11(x):
    return '%011o' % x
W2 = o11(0o102)
erzeuge('zil_lszulang', os.path.join(hier, '..'),
        'zil (Prototyp): Ja-Weg, 2048 Eingaben im Streifen: Ausschrift "lochstreifen zu lang", Halt',
        1, 'zil.txt', SOLL,
        ['0001: 00000000003   # status: 3 (15b setzt ihn nicht)',
         '1340: 05244240000   # SPUF-PN Zelle 0: Wort 1 = Name ztd (kat5, PNAME)', '1341: 20010410000   # SPUF-PN Zelle 1: Wort 2 ohne Laenge (PNAME; hschl haelt vor Element 16)', '1342: 00000000000   # SPUF-PN Zelle 2: Wort 1 von ID 2, nie beschrieben', '7775: 00000000000   # KBGB: letzte Ausschrift endet in KB',
         '7776: 00000000000   # R2: unveraendert 0 (hschl kehrt nicht zurueck)', '7774: 00000000041   # R3: Spurnummer 33 (oktal 41) fuer hschl',
         '1300: 52525252525   # SPUF-00 Zelle 0: Repository-Kennzeichen (ztinit)', '1320: 00000000001   # SPUF-00 Zelle 16: Repository-Kopf', '1321: 00000000001   # SPUF-00 Zelle 17: Zaehler 1 (PNAME)', '1323: 00000000040   # SPUF-00 Zelle 19: letzte belegte Spur (32 dezimal)',
         '1440: ' + o11(2033) + '   # Puffer Programmcode Zelle 0: Wort 1 der Eingabe 2033 (128. Spur)', '1441: ' + W2 + '   # Zelle 1: Wort 2', '1476: ' + o11(2048) + '   # Zelle 30: Wort 1 der Eingabe 2048', '1477: ' + W2 + '   # Zelle 31: Wort 2 der Eingabe 2048',
         'ZT-Zellen-Pruefung:', '0-0000: 52525252525   # ZT 0 Spur 0 Zelle 0', '0-0020: 00000000001   # Zelle 16', '0-0021: 00000000000   # Zelle 17', '0-0022: 00000000000   # Zelle 18', '0-0023: 00000000040   # Zelle 19 (32 dezimal)',
         '0-0040: 05244240000   # Verzeichnis Spur 1 Zelle 0: Wort 1 = Name ztd (kat5, Element 14)', '0-0041: 20010410000   # Verzeichnis Spur 1 Zelle 1: Wort 2 mit Laenge 0', '0-0042: 00000000000   # Verzeichnis Spur 1 Zelle 2: Wort 1 von ID 2', '0-0100: 00000000000   # Spur 2 Zelle 0',
         '0-2040: ' + o11(1) + '   # ZT 0 Spur 33 Zelle 0: Wort 1 der Eingabe 1', '0-2041: ' + W2 + '   # Zelle 1: Wort 2 der Eingabe 1', '0-7776: ' + o11(1520) + '   # ZT 0 Spur 127, Zelle 30: Wort 1 der Eingabe 1520', '0-7777: ' + W2 + '   # ZT 0 Spur 127, letzte Zelle',
         '1-0000: ' + o11(1521) + '   # ZT 1 Spur 0 (Uebertrag), erste Zelle: Wort 1 der Eingabe 1521', '1-1740: ' + o11(2017) + '   # ZT 1 Spur 31, Zelle 0 (letzte geschriebene Spur): Eingabe 2017', '1-1777: ' + W2 + '   # ZT 1 Spur 31, letzte Zelle',
         '1-2000: 00000000000   # ZT 1 Spur 32: nicht mehr geschrieben', '1-7777: 00000000000   # ZT 1 Spur 127: nicht geschrieben'],
        'Variante: 2048 Eingaben im Streifen.', leser1='hschl_zulang.txt')
