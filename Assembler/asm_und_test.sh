#!/bin/bash
# asm_und_test.sh -- assembliert ein Programm, ergänzt die vom Assembler erzeugte .test um eine
# Prüfung und startet den TEST-Interpreter. Alles in einem Aufruf; von überall startbar.
#
# Aufruf:  Assembler/asm_und_test.sh <ordner_mit_asm> <name>[.asm] [AAAA=WERT ...]
#
#   <ordner_mit_asm>  Projektordner, relativ zu Assembler/ (wie bei c82ass.sh -p) oder absolut
#   <name>            Quelltext ohne oder mit .asm
#   AAAA=WERT         erwartete Ergebniszellen, Adresse 4 und Wert 11 Oktalziffern,
#                     z. B. 0001=00000000017 0002=00000000005
#                     (die erwarteten Werte vorher von Hand herleiten, nicht aus einem Lauf abschreiben)
#
# Bevorzugter Weg: Die Sollwerte stehen im .asm zwischen ;#PRUEFE-START und ;#PRUEFE-ENDE (Vorlage:
# Assembler/Claude/mini/mini.asm, Assemblerdokumentation 3.1c). Der Assembler übernimmt sie als Abschnitt
# "Prüfungen:" in die .test (auch BZ, AC, AR, V1, V2 usw.). Dann genügt: asm_und_test.sh <ordner> <n>.
# Ist so ein Abschnitt schon da, werden AAAA=WERT-Argumente NICHT zusätzlich geprüft (das Skript meldet es).
#
# Ergänzt in <ordner>/<name>.test (wird bei jedem Assemblerlauf neu erzeugt):
#   - #TROMMEL=LEER unter #PROT STUFE=2 (falls noch keine #TROMMEL=-Zeile da ist),
#   - #SPEI-0001 auf den Bereich der genannten Ergebniszellen (statt 0000-0000),
#   - am Ende "Prüfungen:" mit US=1 und den genannten Zellen (falls noch kein Prüfungen:-Abschnitt da ist).
# Ohne PRUEFE-Block und ohne Ergebniszellen wird nur US=1 geprüft (das Skript meldet es).
#
# Tastenfolge: Eine Zeile ;#TASTENFOLGE H SW=1 G R im .asm ersetzt die vom Assembler erzeugte Tastenfolge H G R in der .test.
#
# Dateiprüfung: Zeile ";--pruefe-sw-ausgabe DATEI" (oder --pruefe-stanzer1) im .asm wird in den Abschnitt Prüfungen: der .test übernommen.
#
# Zusatztrommeln (C 8205Z): Steht im .asm die Testmarke ";#ZTROMMEL=LEER" (oder KEEP) im Vorspann und/oder im ;#PRUEFE-Block der Unterabschnitt
#   ";ZT-Zellen-Pruefung:" mit Zeilen ";o-aaaa: ttttttttttt" (o = 0 bis 3, alles oktal; Durchfuehrung_eines_Tests.md 2g.1 und 3a.6), startet das
#   Skript den Interpreter mit --C8205Z (Zusatztrommel-Ordner: Trommel/ZT/, abweichend ASM_ZTVERZ=<Ordner>). Gibt es ZT-Zeilen, aber keine Marke
#   #ZTROMMEL=, ergänzt das Skript #ZTROMMEL=LEER (wie #TROMMEL=LEER). Ohne beides läuft der Test wie bisher ohne Zusatztrommeln.
#
# Generator: Liegt <ordner>/gen/<n>_gen.py vor, wird er zuerst ausgeführt (erzeugt <n>.asm, Assembler/Claude/gen_lib).
#
# Rückgabe: Rückgabecode des Assemblers, wenn dieser fehlschlägt (16), sonst der des Interpreters
#           (0 Test wahr, 4 ohne Prüfung, 6 Test falsch, 8 Laufzeitfehler, 16 formale Prüfung negativ, 2 Aufruf falsch);
#           2 bei falschem Aufruf dieses Skripts.
# Bei Test falsch (6), Laufzeitfehler (8) und formaler Prüfung negativ (16) folgt automatisch eine Fehlersuche-Hilfe:
#   die letzten 25 ausgeführten Befehle (mit Quelltextzeile) und die Zellen am Ende des Laufs (Symbole, Anfangs-/Endwert).
#   Abschalten: ASM_FEHLERHILFE=0.
#   ASM_OPTIONEN="..." zusätzliche Optionen für den Assembler, z. B. ASM_OPTIONEN="--no-opt" (Wörter durch Leerzeichen getrennt,
#                     keine Leerzeichen innerhalb eines Wertes); Vorgabe leer. Dasselbe steht dauerhaft im .asm als Zeile
#                     ";#ASMOPTIONEN --no-opt" (beides zusammen wird angewendet).
# Laufgrenzen des Interpreters (Endlosschleifen-Schutz):
#   ASM_MAX_KNOTEN=N  Obergrenze der Knoten je Lauf (Vorgabe 30000000, etwa 1,3 Mio. Befehle, rund 1 Minute);
#                     der Interpreter selbst hat 2000000 (etwa 87000 Befehle, schon nach 3 s erreicht).
#   ASM_TIMEOUT=S     Obergrenze der Laufzeit in Sekunden (Vorgabe 100, unter dem 120-s-Limit der Sitzung);
#                     bei Überschreitung Meldung und Rückgabecode 8.
# Nebenwirkung: Der Assembler schreibt Assembler/projekdetails, der Interpreter ändert Trommel/trommel.txt
#               (mit #TROMMEL=LEER wird sie zuvor geleert) und schreibt Test-Protokolle/<test>/.

if [ $# -lt 2 ]; then
    sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//' | head -12
    exit 2
fi

stamm=$(cd "$(dirname "$0")/.." && pwd) || exit 2
ordner="$1"; name="${2%.asm}"; shift 2

for z in "$@"; do
    echo "$z" | grep -qE '^[0-7]{4}=[0-7]{11}$' || { echo "Ungültige Ergebniszelle '$z' (erwartet AAAA=WERT mit 4 und 11 Oktalziffern)"; exit 2; }
done

# 0. Gibt es einen Python-Generator <ordner>/gen/<n>_gen.py, erzeugt er zuerst die .asm (gen_lib, siehe Handbuch 5.7)
cd "$stamm/Assembler" || exit 2
gen_dir="$(cd "$ordner" 2>/dev/null && pwd)/gen"
if [ -f "$gen_dir/${name}_gen.py" ]; then
    echo "Generator: gen/${name}_gen.py"
    (cd "$stamm" && python3 -I "$gen_dir/${name}_gen.py") || { echo "Generator fehlgeschlagen, kein Test."; exit 2; }
fi

# 0b. Testbasis: Steht im .asm eine Zeile ";#TESTBASIS <adr>" (oktal mit fuehrender 0), wird fuer den Lauf eine Testkopie
#     <name>_tb.asm erzeugt, in der hinter der Zeile "start" (ohne Operand) die Zelle 0000 mit "000 <adr>" (Sprung zum Programm, der
#     Start H G R beginnt bei 0000) und danach "equ <adr>" steht. Das Programm bleibt im Quelltext relativ zu
#     0000 geschrieben (Lader mit Leitadresse), laeuft im Test aber ab <adr>, z. B. neben dem BIS-Minimalprogramm (#TROMMEL=MP).
#     Optional steht hinter <adr> eine Marke: ";#TESTBASIS 02000 haupt" (fuer Programme, deren Zelle 0000 ein UP beginnt und
#     die das BIS mit 10 <Adresse> 000 am Hauptprogramm startet): Zelle 0000 enthaelt dann "000 haupt" statt "000 <adr>".
#     Alle Zellen- und BZ-Sollwerte im ;#PRUEFE-Block und in ;#SPEI gelten dann fuer die Lage ab <adr>. Nach dem Lauf bleibt nur
#     <name>.test (aus <name>_tb.test); die uebrigen Dateien <name>_tb.* werden geloescht (ASM_TB_BEHALTEN=1 behaelt sie).
orig_name=""
tb_adr=$(sed -n 's/^;[[:space:]]*#TESTBASIS[[:space:]]\{1,\}\(0[0-7]*\).*/\1/p' "$ordner/$name.asm" 2>/dev/null | head -1)
tb_start=$(sed -n 's/^;[[:space:]]*#TESTBASIS[[:space:]]\{1,\}0[0-7]*[[:space:]]\{1,\}\([A-Za-z_][A-Za-z0-9_]*\).*/\1/p' "$ordner/$name.asm" 2>/dev/null | head -1)
if [ -n "$tb_adr" ]; then
    orig_name="$name"; name="${name}_tb"
    python3 - "$ordner/$orig_name.asm" "$ordner/$name.asm" "$tb_adr" "$tb_start" <<'PY'
import re, sys
q, z, adr = sys.argv[1:4]
ziel = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else adr   # Sprungziel in Zelle 0000: Startmarke oder Testbasis
zeilen = open(q, encoding='utf-8').read().split('\n')
aus, gesetzt = [], False
for l in zeilen:
    aus.append(l)
    if not gesetzt and re.match(r'^[ \t]+start[ \t]*(;.*)?$', l):
        aus.append('                000     %s                   ; Zelle 0000: Sprung auf die Testbasis bzw. Startmarke (der Start H G R beginnt bei 0000)' % ziel)
        aus.append('                equ     %s                   ; Testbasis (;#TESTBASIS): Lage des Programms im Test' % adr)
        gesetzt = True
if not gesetzt:
    print('Fehler: ;#TESTBASIS, aber keine Zeile "start" ohne Operand gefunden.'); sys.exit(2)
open(z, 'w', encoding='utf-8').write('\n'.join(aus))
print('Testbasis %s: Testkopie %s' % (adr, z))
PY
    [ $? -eq 0 ] || exit 2
fi

# 1. Assemblieren (immer aus Assembler/ starten)
# Optionen: Umgebungsvariable ASM_OPTIONEN und/oder eine Zeile ";#ASMOPTIONEN <optionen>" im .asm (z. B. ";#ASMOPTIONEN --no-opt")
asm_opt=$(sed -n 's/^;[[:space:]]*#ASMOPTIONEN[[:space:]]\{1,\}\([^;]*[^;[:space:]]\).*/\1/p' "$ordner/$name.asm" 2>/dev/null | head -1)
[ -n "$asm_opt" ] && echo "Assembleroptionen aus dem .asm: $asm_opt"
./c82ass.sh -p "$ordner" -s "$name.asm" --WARN=ALLE --no-color $asm_opt $ASM_OPTIONEN
rc=$?
if [ $rc -ne 0 ]; then echo "Assembler: Rückgabecode $rc, kein Test."; exit $rc; fi

test_datei="$(cd "$ordner" && pwd)/$name.test"
[ -f "$test_datei" ] || { echo "Keine .test erzeugt: $test_datei"; exit 2; }

# 2. .test ergänzen
python3 - "$test_datei" "$@" <<'PY'
import re, sys
pfad, zellen = sys.argv[1], sys.argv[2:]
t = open(pfad, encoding='utf-8').read()
hat_pruefung = bool(re.search(r'^Prüfungen:', t, re.M))
if hat_pruefung and zellen:
    print('Hinweis: Die .test enthält schon Prüfungen (aus ;#PRUEFE-START im .asm); die Argumente AAAA=WERT werden nicht ergänzt.')
elif hat_pruefung:
    print('Hinweis: Prüfungen aus ;#PRUEFE-START im .asm übernommen.')
elif not zellen:
    print('Hinweis: weder ;#PRUEFE-START im .asm noch AAAA=WERT angegeben: geprüft wird nur US=1.')
# Tastenfolge aus dem Quelltext: Zeile ";#TASTENFOLGE H SW=1 G R" ersetzt das vom Assembler erzeugte "H G R"
# (noetig, wenn Buchstaben ueber K0/SW eingegeben werden: der Schalter SW muss vor dem Anwaehlen von K0 gesetzt sein).
asm_pfad = re.sub(r'\.test$', '.asm', pfad)
try:
    q = open(asm_pfad, encoding='utf-8').read()
except OSError:
    q = ''
m = re.search(r'^;\s*#TASTENFOLGE[ \t]+(\S.*?)\s*$', q, re.M)
if m and re.search(r'^Tastenfolge:\n', t, re.M):
    t = re.sub(r'(^Tastenfolge:\n)[^\n]*\n', lambda x: x.group(1) + m.group(1) + '\n', t, count=1, flags=re.M)
    print('Hinweis: Tastenfolge aus dem Quelltext uebernommen: ' + m.group(1))
if not re.search(r'^#TROMMEL=', t, re.M):
    t = re.sub(r'^(#PROT STUFE=\d+[^\n]*\n)', r'\1#TROMMEL=LEER\n', t, count=1, flags=re.M)
    if '#TROMMEL=LEER' not in t:
        t = t.replace('Trommeldatei:\n', 'Trommeldatei:\n#TROMMEL=LEER\n', 1)
# Zusatztrommeln: ZT-Zellen-Pruefung ohne Marke #ZTROMMEL= -> #ZTROMMEL=LEER hinter der #TROMMEL=-Zeile ergaenzen
if re.search(r'^ZT-Zellen-Pr(ue|ü)fung:', t, re.M) and not re.search(r'^#ZTROMMEL=', t, re.M):
    t = re.sub(r'^(#TROMMEL=[^\n]*\n)', r'\1#ZTROMMEL=LEER\n', t, count=1, flags=re.M)
    print('Hinweis: ZT-Zellen-Pruefung ohne #ZTROMMEL=: #ZTROMMEL=LEER ergänzt.')
if zellen:
    adr = sorted(int(z.split('=')[0], 8) for z in zellen)
    t = re.sub(r'^#SPEI-0001 [0-7]{4}-[0-7]{4}', '#SPEI-0001 %04o-%04o' % (adr[0], adr[-1]), t, count=1, flags=re.M)
if not re.search(r'^Prüfungen:', t, re.M):
    t = t.rstrip('\n') + '\n\nPrüfungen:\nUS=1\n' + ''.join('%s: %s\n' % tuple(z.split('=')) for z in zellen)
# Dateiprüfung: Zeile ";--pruefe-sw-ausgabe DATEI" bzw. ";--pruefe-stanzer1 DATEI" im .asm kommt in den Abschnitt Prüfungen:
for schalter in ('pruefe-sw-ausgabe', 'pruefe-stanzer1'):
    m = re.search(r'^;\s*--' + schalter + r'[ \t]+(\S.*?)\s*$', q, re.M)
    if m and not re.search(r'^--' + schalter + r'\b', t, re.M):
        t = t.rstrip('\n') + '\n--' + schalter + ' ' + m.group(1) + '\n'
        print('Hinweis: Dateiprüfung aus dem Quelltext uebernommen: --' + schalter + ' ' + m.group(1))
open(pfad, 'w', encoding='utf-8').write(t)
PY
[ $? -eq 0 ] || { echo "Ergänzen der .test fehlgeschlagen"; exit 2; }

# 3. Interpreter (aus dem Projektstamm, ohne Benutzer-Site-Pakete)
cd "$stamm" || exit 2
ztarg=""
if grep -qE '^(#ZTROMMEL=|ZT-Zellen-Pr(ue|ü)fung:)' "$test_datei"; then
    ztarg="--C8205Z=${ASM_ZTVERZ:-$stamm/Trommel/ZT}"
    echo "Hinweis: Zusatztrommeln eingeschaltet ($ztarg)."
fi
timeout "${ASM_TIMEOUT:-100}" python3 -I c8205_interp.py --MODUS=TEST $ztarg --max-knoten "${ASM_MAX_KNOTEN:-30000000}" "$test_datei"
rc=$?
if [ $rc -eq 124 ]; then
    echo "Zeitgrenze von ${ASM_TIMEOUT:-100} s überschritten (ASM_TIMEOUT): Endlosschleife oder zu langer Lauf; Rückgabecode 8"
    rc=8
fi

# 4. Fehlersuche-Hilfe bei Test falsch (6), Laufzeitfehler (8) oder formaler Prüfung negativ (16)
#    (abschaltbar mit ASM_FEHLERHILFE=0)
if [ "${ASM_FEHLERHILFE:-1}" != "0" ] && { [ $rc -eq 6 ] || [ $rc -eq 8 ] || [ $rc -eq 16 ]; }; then
python3 -I - "$stamm" "$test_datei" "$name" "$rc" <<'PY'
import os, re, sys
stamm, test, name, rc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
basis = os.path.splitext(test)[0]
def lies(pfad):
    try:
        with open(pfad, encoding='utf-8') as f: return f.read().split('\n')
    except OSError:
        return []
# Anfangswerte und Kommentare aus der .test (nur der Trommelabschnitt)
anf, text = {}, {}
for z in lies(test):
    if z.startswith('Tastenfolge:'): break
    m = re.match(r'^([0-7]{4}): ([0-7]{11})\s*(?:#\s*(.*))?$', z)
    if m:
        anf[int(m.group(1), 8)] = int(m.group(2), 8)
        text[int(m.group(1), 8)] = (m.group(3) or '').strip()
sym = {}
for z in lies(basis + '.sym'):
    m = re.match(r'^(\S+),([0-7]{4})$', z.strip())
    if m: sym[int(m.group(2), 8)] = m.group(1)
endst = {}
for z in lies(os.path.join(stamm, 'Trommel', 'trommel.txt')):
    m = re.match(r'^([0-7]{4}): ([0-7]{11})$', z.strip())
    if m: endst[int(m.group(1), 8)] = int(m.group(2), 8)
prot = os.path.join(stamm, 'Test-Protokolle', name, 'protokoll.txt')
br = []
for z in lies(prot):
    m = re.match(r'^\s*BR=([0-7]{4}) ([0-7]{3})\s+\(vor Knoten \d+\)\s+BZ=([0-7]{4}) AC=([0-7]{11}) .*?V1=(\d) V2=(\d) V3=(\d)', z)
    if m: br.append((int(m.group(1), 8), m.group(2), int(m.group(3), 8), m.group(4), m.group(5) + m.group(6) + m.group(7)))
print()
print('=== Fehlersuche-Hilfe (Rückgabecode %s; abschaltbar mit ASM_FEHLERHILFE=0) ===' % rc)
N = 25
if br:
    print('Ausgeführte Befehle: %d. Die letzten %d (Befehlsadresse = BZ-1; Text aus der .test, \'?\' = Code passt nicht zur Zelle):' % (len(br), min(N, len(br))))
    print('  adr   code   AC (laut Protokoll)  V1V2V3  Befehlszeile')
    for ar, orc, bz, ac, v in br[-N:]:
        if bz == 0 and ar == 0:
            print('  Start (vor dem ersten Befehl)  AC %s' % ac); continue
        adr = (bz - 1) & 0o7777
        t = text.get(adr)
        if t is not None and (anf.get(adr, 0) & 0o777) == int(orc, 8):
            kz, zeile = ' ', t[:60]
        else:
            kz, zeile = '?', ''
        print('  %04o  %04o %s %s  %s     %s %s%s' % (adr, ar, orc, ac, v, kz, '', zeile))
    if len(br) > N: print('  ... %d frühere Befehle ausgelassen; vollständig: %s' % (len(br) - N, prot))
else:
    print('Kein Befehlsverlauf im Protokoll gefunden: %s' % prot)
print()
print('Zellen am Ende des Laufs (* = gegenüber dem Anfangswert in der .test geändert):')
gezeigt = set()
zeilen = []
for a in sorted(set(sym) | set(endst) | set(anf)):
    e, i = endst.get(a, 0), anf.get(a, 0)
    geaendert = e != i
    if a in sym or geaendert:
        zeilen.append('  %04o  %-14s anfangs %011o  am Ende %011o %s' % (a, sym.get(a, ''), i, e, '*' if geaendert else ''))
M = 70
for z in zeilen[:M]: print(z)
if len(zeilen) > M: print('  ... %d weitere Zellen ausgelassen (Trommel/trommel.txt)' % (len(zeilen) - M))
if not any(l.strip().startswith('#TROMMEL=LEER') for l in lies(test)):
    print('Hinweis: #TROMMEL=LEER fehlt, Anfangswerte außerhalb der .test sind unbekannt (angenommen 0).')
PY
fi
if [ -n "$orig_name" ] && [ "${ASM_TB_BEHALTEN:-0}" != "1" ]; then
    # Testkopie aufraeumen: die .test der Testbasis wird zur .test des Programms, alles andere von <name>_tb.* geloescht
    cd "$stamm/Assembler" && d="$(cd "$ordner" && pwd)" && mv -f "$d/$name.test" "$d/$orig_name.test" \
        && for e in asm obj mqo sym dmp log kep; do rm -f "$d/$name.$e"; done
fi
exit $rc
