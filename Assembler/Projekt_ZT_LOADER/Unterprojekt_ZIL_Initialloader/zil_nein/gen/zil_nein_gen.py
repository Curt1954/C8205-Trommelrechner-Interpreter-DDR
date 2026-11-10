#!/usr/bin/env python3
"""zil_nein_gen.py -- erzeugt zil_nein.asm aus zil/zil.asm: Repository vorhanden, Antwort N (Weg 2). Aufruf vom Projektstamm (asm_und_test.sh tut es selbst)."""
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'zil', 'gen'))
from zil_variante import erzeuge

SOLL = """; Sollwerte von Hand hergeleitet (Weg 2: Repository vorhanden, Antwort N):
; Eingabe (Datei zil_nein.txt): Um. KB (nach der Frage steht KBGB = 1), j (KB, uebergangen), Um. GB, n (= N, Nein). Um. GB setzt KBGB := 1, N setzt R2 := 0.
; Ausgabe auf SW: zuerst eine Zeilenschaltung (leere erste Zeile), dann UP Repository pruefen / Repository gefunden / Zusatztrommel loeschen [J/N] / (leere Zeile, 7b: Zeilenschaltung nach der Antwort N) / Programmende; ztinit wird nicht aufgerufen.
; Zellen und Register nach dem Lauf: status = 2 (Zelle 0001), KBGB = 0 (Zelle 7775: nach der Antwort 1, \\"Programmende\\" beginnt mit Um. KB und endet in KB), R2 = 0 (letzte Antwort N)."""
erzeuge('zil_nein', os.path.join(hier, '..'),
        'zil (Dummy): Repository vorhanden, Antwort N (nach kleinem j): Programmende, Weg 2',
        1, 'zil_nein.txt', SOLL,
        ['0001: 00000000002   # status: Weg 2 (Nein)', '7775: 00000000000   # KBGB: Ausschrift Programmende endet in KB',
         '7776: 00000000000   # R2: Antwort N',
         'ZT-Zellen-Pruefung:', '0-0000: 00000000000   # ZT 0 Spur 0 Zelle 0: ztinit wurde nicht aufgerufen (Marke #ZTROMMEL=LEER)'],
        'Variante: Antwort N.')
