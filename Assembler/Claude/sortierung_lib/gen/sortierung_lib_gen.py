#!/usr/bin/env python3
"""sortierung_lib_gen.py -- Vergleichsprogramm zu Assembler/Claude/sortierung.asm (handgeschrieben, Programmbeispiel 8 der Anleitung):
dieselbe Sortierung von 4 Namen (je 6 Zeichen zu 5 Bit) mit demselben Verfahren (Befehle 240 zur Laufzeit bauen, R-Lesebefehl 251),
aber mit der Bibliothek c82gen geschrieben. Dient dem Vergleich von Zellenzahl und Erzeugungsaufwand (gen_lib_messung.md).
Aufruf (vom Projektstamm): python3 -I Assembler/Claude/sortierung_lib/gen/sortierung_lib_gen.py   (asm_und_test.sh ruft ihn selbst auf)."""
import os
import sys

hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'gen_lib'))
from c82gen import Prog

NAMEN = [0o10021054460, 0o13371052070, 0o13300654600, 0o11206050000]   # HABERL KOREHN KLAUS IHLE
P = Prog('sortierung -- 4 Namen aufsteigend ordnen (UP sort, Parameter sn und sla)', grenze=0o100)
# Hauptprogramm
P.laden('#04000'); P.speichere('sn')                    # n = 4 Adresseneinheiten
P.laden('@feld'); P.speichere('sla')                    # Anfangsadresse des Feldes
P.aufruf('sort')
P.halt('Halt: Feld ist sortiert')
# Unterprogramm sort
P.up_beginn('sort')
P.op('001', 'sinit', 'AC := 0, weiter')
P.lab('sinit'); P.speichere('si', 'i := 0')
P.addiere('#01000', 'AC := i + 1')
P.lab('skset'); P.speichere('sk', 'k := i + 1')
P.addiere('sla'); P.addiere('#0240', 'Befehl 240 a(k+1) bauen')
P.speichere('sb1'); P.op('251', 0, 'AC := a(k+1)'); P.speichere('sh', 'H := a(k+1)')
P.laden('si'); P.addiere('sla'); P.addiere('#0240', 'Befehl 240 a(i+1) bauen')
P.speichere('sb2'); P.op('251', 0, 'AC := a(i+1)')
P.vergleiche('sh'); P.sprung_kleiner_gleich('sknext', 'a(i+1) <= H: nicht tauschen')
P.lab('sb1'); P.op('db', 1, 'zur Laufzeit 240 a(k+1)')
P.laden('sh')
P.lab('sb2'); P.op('db', 1, 'zur Laufzeit 240 a(i+1)')
P.lab('sknext'); P.laden('sk'); P.addiere('#01000'); P.vergleiche('sn')
P.sprung_gleich('sinext', 'k + 1 = n: innere Schleife fertig'); P.sprung('skset')
P.lab('sinext'); P.laden('si'); P.addiere('#02000', 'AC := i + 2'); P.vergleiche('sn')
P.sprung_gleich('rueck_sort', 'i + 2 = n: Rueckkehr')
P.subtrahiere('#01000', 'AC := i + 1'); P.sprung('sinit')
P.up_ende('sort')
for v in ('sn', 'sla', 'si', 'sk', 'sh'):
    P.arbeit(v, 'Zelle ' + v)
P.feld('feld', NAMEN, 'Name')
soll = {'feld+%d' % i: w for i, w in enumerate(sorted(NAMEN))}
P.schreibe(os.path.join(hier, '..', 'sortierung_lib.asm'), pruefe=soll, gen_name='Assembler/Claude/sortierung_lib/gen/sortierung_lib_gen.py')
