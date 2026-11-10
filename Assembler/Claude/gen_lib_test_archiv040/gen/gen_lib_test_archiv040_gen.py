#!/usr/bin/env python3
"""gen_lib_test_archiv040_gen.py -- wie gen_lib_test_archiv, aber mit Ladeadresse 0140 im Test (;#TESTBASIS, 040 modulo 0100):
die Tafel A liegt dann nicht auf einem Vielfachen von 0100, eingabe_init muss die Tafel B waehlen (so laedt der Lader Archivprogramme); Schieben hier mit W-Transport auf 7640.
Aufruf (vom Projektstamm): python3 -I Assembler/Claude/gen_lib_test_archiv040/gen/gen_lib_test_archiv040_gen.py   (asm_und_test.sh ruft ihn selbst auf)."""
import os
import sys

hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'gen_lib_test', 'gen'))
from testprogramm import bauen   # noqa: E402

BASIS = 0o140
P, soll, name = bauen(archiv=True, basis=BASIS, schiebespur='w7640')   # deckt Archivmodus mit W-Transport ab (Vorgabe im Archiv: Nullspur)
P.schreibe(os.path.join(hier, '..', name + '.asm'), pruefe=soll, testbasis=BASIS,
           gen_name='Assembler/Claude/gen_lib_test_archiv040/gen/gen_lib_test_archiv040_gen.py')
