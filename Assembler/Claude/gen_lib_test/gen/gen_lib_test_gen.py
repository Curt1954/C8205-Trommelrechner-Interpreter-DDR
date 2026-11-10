#!/usr/bin/env python3
"""gen_lib_test_gen.py -- Pruefprogramm der Bibliothek c82gen im Normalmodus (Literale, Rueckkehrzelle am UP-Ende, eine Eingabetafel).
Aufruf (vom Projektstamm): python3 -I Assembler/Claude/gen_lib_test/gen/gen_lib_test_gen.py   (asm_und_test.sh ruft ihn selbst auf)
Aufbau und Sollwerte: testprogramm.py (gleicher Ordner)."""
import os
import sys

hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, hier)
from testprogramm import bauen   # noqa: E402

P, soll, name = bauen(archiv=False)
P.schreibe(os.path.join(hier, '..', name + '.asm'), pruefe=soll, gen_name='Assembler/Claude/gen_lib_test/gen/gen_lib_test_gen.py')
