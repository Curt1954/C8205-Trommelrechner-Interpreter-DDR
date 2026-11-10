#!/usr/bin/env python3
"""gen_lib_test_archiv_gen.py -- Pruefprogramm der Bibliothek c82gen im Archivmodus (benannte Konstanten, dbn, zwei Eingabetafeln mit eingabe_init, Schieben ueber die Nullspur im Programm).
Aufruf (vom Projektstamm): python3 -I Assembler/Claude/gen_lib_test_archiv/gen/gen_lib_test_archiv_gen.py   (asm_und_test.sh ruft ihn selbst auf)
Aufbau und Sollwerte: Assembler/Claude/gen_lib_test/gen/testprogramm.py."""
import os
import sys

hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'gen_lib_test', 'gen'))
from testprogramm import bauen   # noqa: E402

P, soll, name = bauen(archiv=True)
P.schreibe(os.path.join(hier, '..', name + '.asm'), pruefe=soll, gen_name='Assembler/Claude/gen_lib_test_archiv/gen/gen_lib_test_archiv_gen.py')
