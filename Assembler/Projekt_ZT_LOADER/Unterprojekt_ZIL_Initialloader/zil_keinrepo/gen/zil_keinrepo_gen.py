#!/usr/bin/env python3
"""zil_keinrepo_gen.py -- erzeugt zil_keinrepo.asm aus zil/zil.asm: Platzhalter meldet kein Repository (Weg 1). Aufruf vom Projektstamm (asm_und_test.sh tut es selbst)."""
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'zil', 'gen'))
from zil_variante import erzeuge

SOLL = """; Sollwerte von Hand hergeleitet (Weg 1: kein Repository):
; Der Platzhalter repo liefert d_repo = 0 (R2 = 0); es wird nichts gelesen (keine Eingabedatei, KBGB bleibt 0 (vom Hauptprogramm nach dem Start auf KB gesetzt)).
; Ausgabe auf SW: zuerst eine Zeilenschaltung (leere erste Zeile), dann UP Repository pruefen / Kein Repository gefunden; danach Halt, keine Frage.
; Zellen und Register nach dem Lauf: status = 1 (Zelle 0001), KBGB = 0 (Zelle 7775), R2 = 0."""
erzeuge('zil_keinrepo', os.path.join(hier, '..'),
        'zil (Dummy): kein Repository: Ausschrift und Halt, Weg 1',
        0, None, SOLL,
        ['0001: 00000000001   # status: Weg 1 (kein Repository)', '7775: 00000000000   # KBGB: unveraendert KB',
         '7776: 00000000000   # R2: kein Repository',
         'ZT-Zellen-Pruefung:', '0-0000: 00000000000   # ZT 0 Spur 0 Zelle 0: ztinit wurde nicht aufgerufen (Marke #ZTROMMEL=LEER)'],
        'Variante: kein Repository.')
