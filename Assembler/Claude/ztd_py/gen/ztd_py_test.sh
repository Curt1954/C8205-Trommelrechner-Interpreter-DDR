#!/bin/bash
# ztd_py_test.sh -- erzeugt ztd_py.asm und prueft ZTD (Fassung A, Generator) mit dem Abnahmetest ztd_py_tests.py
# (ZTD laeuft nur ueber ZTL, nicht allein: asm_und_test.sh passt nicht). Aufruf: bash Assembler/Claude/ztd_py/gen/ztd_py_test.sh   Rueckgabe 0 = Test wahr.
export LC_ALL=C.UTF-8
stamm=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd) || exit 2
cd "$stamm" || exit 2
python3 -I Assembler/Claude/ztd_py/gen/ztd_py_gen.py || exit 2
python3 -I C8205Z/Tests_Z/ztd_py_tests.py
