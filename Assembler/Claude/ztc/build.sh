#!/bin/bash
# build.sh - ztc.asm aus teil1.asm, teil2.asm, den Tabellen (gen_ztc_tabellen.py) und teil3.asm zusammensetzen (nur Entwicklung; ztc.asm ist das Ergebnis)
cd "$(dirname "$0")/../../.." || exit 1
python3 -I Assembler/Claude/ztc/gen_ztc_tabellen.py > /tmp/ztc_tab.inc || exit 1
cat Assembler/Claude/ztc/teil1.asm Assembler/Claude/ztc/teil2.asm /tmp/ztc_tab.inc Assembler/Claude/ztc/teil3.asm > Assembler/Claude/ztc/ztc.asm
