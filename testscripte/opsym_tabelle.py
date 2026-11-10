#!/usr/bin/env python3
# opsym_tabelle.py - prueft die Namenstabelle fuer Operationscodes (OPSYM) gegen die Einzelbefehlsuebersicht
# Version 0.01-001
#
# Aufruf (von ueberall):  python3 -I testscripte/opsym_tabelle.py [Namensdatei]
#   ohne Argument: Standardtabelle Assembler/Sourcecode/c82ass.opsym
#   mit Argument:  eine Namensdatei eines Projekts (;#OPSYM=...)
# Je Eintrag "NAME code ; Nr. <n> ..." wird geprueft, dass die Nummer <n> in der Einzelbefehlsuebersicht der
# Befehlsliste (markdown-dateien/C8205-Interpreter-Befehlsliste.md) vorkommt und den Code des Namens enthaelt.
# Ein Eintrag ohne "Nr. <n>" im Kommentar ist nicht pruefbar und wird gemeldet.
# Rueckgabe: 0 = alle pruefbaren Eintraege stimmen, 1 = mindestens ein Eintrag stimmt nicht, 2 = Aufruf- oder Dateifehler.
import os, re, sys

stamm = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
liste = os.path.join(stamm, "markdown-dateien", "C8205-Interpreter-Befehlsliste.md")
datei = sys.argv[1] if len(sys.argv) > 1 else os.path.join(stamm, "Assembler", "Sourcecode", "c82ass.opsym")
try:
    text = open(liste, encoding="utf-8").read()
    zeilen = open(datei, encoding="utf-8").read().splitlines()
except OSError as e:
    print("Dateifehler:", e); sys.exit(2)

# Einzelbefehlsuebersicht: Tabelle "| Nr. | Code(s) ... | Original-Beschreibung |"; Nummer -> Menge der Codes
nr_codes = {}
ein = False
for z in text.splitlines():
    if z.startswith("| Nr. | Code(s)"):
        ein = True; continue
    if ein:
        m = re.match(r"^\|\s*(\d+)\s*\|\s*([0-7, ]+?)\s*\|", z)
        if m:
            nr_codes.setdefault(int(m.group(1)), set()).update(c.strip() for c in m.group(2).split(",") if c.strip())
        elif not z.startswith("|"):
            if nr_codes: ein = False
if not nr_codes:
    print("Einzelbefehlsuebersicht nicht gefunden in", liste); sys.exit(2)

falsch = nicht_pruefbar = ok = 0
for i, z in enumerate(zeilen, 1):
    kopf, _, kom = z.partition(";")
    w = kopf.split()
    if not w:
        continue
    if len(w) != 2:
        print(f"{datei}:{i}: Zeile nicht lesbar: {z}"); falsch += 1; continue
    name, code = w
    m = re.match(r"\s*Nr\.\s*(\d+)", kom)
    if not m:
        print(f"{datei}:{i}: {name} {code}: nicht pruefbar (kein 'Nr. <n>' im Kommentar)"); nicht_pruefbar += 1; continue
    n = int(m.group(1))
    if n not in nr_codes:
        print(f"{datei}:{i}: {name} {code}: Nr. {n} gibt es in der Einzelbefehlsuebersicht nicht"); falsch += 1
    elif code not in nr_codes[n]:
        print(f"{datei}:{i}: {name} {code}: Code gehoert nicht zu Nr. {n} (dort: {', '.join(sorted(nr_codes[n]))})"); falsch += 1
    else:
        ok += 1
print(f"{datei}: {ok} Eintraege stimmen, {falsch} falsch, {nicht_pruefbar} nicht pruefbar")
sys.exit(1 if falsch else 0)
