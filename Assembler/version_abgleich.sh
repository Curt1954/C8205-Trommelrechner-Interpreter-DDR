#!/bin/bash
# version_abgleich.sh -- prueft, ob alle Stellen der Handliste (markdown-dateien/C8205-Versionierung.md,
# Abschnitt 4, "Assemblerstand: alle Stellen einer Hochzaehlung") zu ASM_VERSION in ca82_version.h passen.
#
# Aufruf (von ueberall; das Skript liegt in Assembler/):
#   bash Assembler/version_abgleich.sh [-v] [--binary] [--regr <Ordner|Regressionstest.zip>]
#
# Optionen:
#   -v            je Quelltext-Datei mit Nummer eine Zeile (sonst nur Zusammenfassung)
#   --binary      zusaetzlich: Assembler/_Linux/c82ass --version gegen ASM_VERSION pruefen (das Binary
#                 baut der Inhaber; bis dahin meldet diese Zeile eine Abweichung, das ist erwartet)
#   --regr <Pfad> Regressionstest an anderer Stelle: Ordner mit negativ/ und LIESMICH.md oder ein
#                 Regressionstest.zip (Vorgabe: Assembler/Regressionstest/, sonst Regressionstest.zip im Projektstamm)
#   -h            diese Hilfe
#
# Geprueft wird (je Stelle eine Zeile OK, HINWEIS oder ABWEICHUNG):
#   1. ca82_version.h: ASM_VERSION hat die Form y.xx-zzz
#   2. Quelltext-Kopfzeilen "Version y.xx-zzz (siehe ca82_version.h)": keine Nummer ist neuer als ASM_VERSION
#      (ungeaenderte Dateien behalten ihre aeltere Nummer; ob eine Datei haette nachgezogen werden muessen, laesst sich
#      ohne Vergleichsstand nicht entscheiden: HINWEIS, wenn keine Kopfzeile die aktuelle Nummer traegt)
#   3. .md (Assemblerdokumentation, massgeblich): Zeile "Version:" und die drei Texte "C82aas Version ..."
#   4. Regressionstest: negativ/version.erwartet und negativ/pass0_version.erwartet (ohne Nummer oder mit ASM_VERSION),
#      LIESMICH.md (Kopfzeile = neuester Eintrag, dessen c82ass-Nummer = ASM_VERSION)
#   5. nur mit --binary: Ausgabe von c82ass --version
# Rueckgabe: 0 alles in Ordnung (Hinweise zaehlen nicht), 1 mindestens eine ABWEICHUNG, 2 Aufruf falsch oder Datei fehlt.
# Nur lesend; schreibt nichts.

stamm=$(cd "$(dirname "$0")/.." && pwd) || exit 2
exec python3 -I - "$stamm" "$@" <<'PY'
import os, re, subprocess, sys, zipfile

stamm, args = sys.argv[1], sys.argv[2:]
verbose = False
mit_binary = False
regr = None
i = 0
while i < len(args):
    a = args[i]
    if a == '-v':
        verbose = True
    elif a == '--binary':
        mit_binary = True
    elif a == '--regr' and i + 1 < len(args):
        i += 1
        regr = args[i]
    elif a in ('-h', '--help'):
        with open(os.path.join(stamm, 'Assembler', 'version_abgleich.sh'), encoding='utf-8') as f:
            for z in f.read().split('\n')[1:]:
                if not z.startswith('#'):
                    break
                print(z[2:] if z.startswith('# ') else z[1:])
        sys.exit(0)
    else:
        print('version_abgleich.sh: unbekannte Option oder Parameter fehlt: %s (Hilfe: -h)' % a, file=sys.stderr)
        sys.exit(2)
    i += 1

NUM = r'\d\.\d\d-\d{3}'
anzahl_abw = 0

def ok(stelle, wert):
    print('  OK         %s: %s' % (stelle, wert))

def hinweis(stelle, text):
    print('  HINWEIS    %s: %s' % (stelle, text))

def abw(stelle, text):
    global anzahl_abw
    anzahl_abw += 1
    print('  ABWEICHUNG %s: %s' % (stelle, text))

def fehlt(was):
    print('version_abgleich.sh: %s nicht gefunden' % was, file=sys.stderr)
    sys.exit(2)

def lies(pfad):
    if not os.path.isfile(pfad):
        fehlt(pfad)
    with open(pfad, encoding='utf-8') as f:
        return f.read()

def schluessel(v):
    y, rest = v.split('.', 1)
    xx, zzz = rest.split('-')
    return (int(y), int(xx), int(zzz))

# 1. ASM_VERSION
kopf = lies(os.path.join(stamm, 'Assembler', 'Sourcecode', 'ca82_version.h'))
m = re.search(r'#define\s+ASM_VERSION\s+"([^"]*)"', kopf)
if not m:
    fehlt('#define ASM_VERSION in ca82_version.h')
asm = m.group(1)
print('c82ass ASM_VERSION (ca82_version.h): %s' % asm)
if re.fullmatch(NUM, asm):
    ok('ca82_version.h', 'ASM_VERSION %s hat die Form y.xx-zzz' % asm)
else:
    abw('ca82_version.h', 'ASM_VERSION "%s" hat nicht die Form y.xx-zzz; weitere Pruefung abgebrochen' % asm)
    sys.exit(1)

# 2. Quelltext-Kopfzeilen
quell = os.path.join(stamm, 'Assembler', 'Sourcecode')
mit_nr = []
for n in sorted(os.listdir(quell)):
    if not n.endswith(('.c', '.h')):
        continue
    with open(os.path.join(quell, n), encoding='utf-8', errors='replace') as f:
        z1 = f.readline()
    mm = re.search(r'Version (%s) \(siehe ca82_version\.h\)' % NUM, z1)
    if mm:
        mit_nr.append((n, mm.group(1)))
neuer = [(n, v) for n, v in mit_nr if schluessel(v) > schluessel(asm)]
aktuell = [n for n, v in mit_nr if v == asm]
if verbose:
    for n, v in mit_nr:
        print('             %-22s %s%s' % (n, v, '  (aktuell)' if v == asm else ''))
for n, v in neuer:
    abw('Kopfzeile %s' % n, '%s ist neuer als ASM_VERSION %s' % (v, asm))
if not neuer:
    ok('Quelltext-Kopfzeilen', '%d Dateien mit Nummer, keine neuer als ASM_VERSION; %d tragen die aktuelle Nummer' % (len(mit_nr), len(aktuell)))
if not aktuell:
    hinweis('Quelltext-Kopfzeilen', 'keine Kopfzeile traegt %s; pruefen, ob die geaenderte Datei nachgezogen ist (Dateien ohne Nummer in der Kopfzeile bleiben so)' % asm)

# 3. .md
dok = os.path.join(stamm, 'Assembler', 'Dokumentation')
md = lies(os.path.join(dok, 'C8205_Assembler_Dokumentation.md'))
mv = re.search(r'^Version: (%s)$' % NUM, md, re.M)
md_v = mv.group(1) if mv else None
if md_v:
    ok('.md Zeile "Version:"', md_v)
else:
    abw('.md Zeile "Version:"', 'nicht gefunden oder falsche Form')
drei_md = re.findall(r'C82aas Version (%s)' % NUM, md)
if len(drei_md) == 3 and all(v == asm for v in drei_md):
    ok('.md drei Texte "C82aas Version"', asm)
else:
    abw('.md drei Texte "C82aas Version"', 'gefunden %s, erwartet dreimal %s' % (drei_md, asm))

# 4. Regressionstest (Ordner oder Zip)
def regr_leser():
    kandidaten = []
    if regr:
        kandidaten.append(regr if os.path.isabs(regr) else os.path.join(os.getcwd(), regr))
    else:
        kandidaten.append(os.path.join(stamm, 'Assembler', 'Regressionstest'))
        kandidaten.append(os.path.join(stamm, 'Regressionstest.zip'))
    for k in kandidaten:
        if os.path.isdir(k):
            def rd(rel, k=k):
                p = os.path.join(k, rel)
                if not os.path.isfile(p):
                    return None
                with open(p, encoding='utf-8') as f:
                    return f.read()
            return rd, k
        if os.path.isfile(k) and k.endswith('.zip'):
            z = zipfile.ZipFile(k)
            namen = set(z.namelist())
            def rd(rel, z=z, namen=namen):
                n = 'Assembler/Regressionstest/' + rel
                return z.read(n).decode('utf-8') if n in namen else None
            return rd, k
    return None, None

rd, quelle = regr_leser()
if rd is None:
    hinweis('Regressionstest', 'weder Assembler/Regressionstest/ noch Regressionstest.zip gefunden; Erwartungsdateien und LIESMICH.md nicht geprueft')
else:
    print('  (Regressionstest aus %s)' % quelle)
    for n in ('negativ/version.erwartet', 'negativ/pass0_version.erwartet'):
        t = rd(n)
        if t is None:
            abw(n, 'Datei fehlt')
            continue
        st = [z for z in t.split('\n') if z.startswith('stdout ')]
        if not st:
            abw(n, 'keine Zeile "stdout <text>"')
            continue
        nummern = re.findall(NUM, ' '.join(st))
        if not nummern:
            ok(n, 'ohne Nummer (%s)' % st[0])
        elif all(v == asm for v in nummern):
            ok(n, 'enthaelt %s' % asm)
        else:
            abw(n, 'enthaelt %s statt %s' % (nummern, asm))
    lm = rd('LIESMICH.md')
    if lm is None:
        abw('LIESMICH.md', 'Datei fehlt')
    else:
        mk = re.search(r'^Version (%s) \(Stand \d\d\.\d\d\.\d{4}\)$' % NUM, lm, re.M)
        eintraege = re.findall(r'^Mit Version (%s) \(c82ass (?:bleibt )?(%s)' % (NUM, NUM), lm, re.M)
        if not mk:
            abw('LIESMICH.md Kopfzeile', '"Version y.xx-zzz (Stand dd.mm.yyyy)" nicht gefunden')
        elif not eintraege:
            abw('LIESMICH.md', 'kein Eintrag "Mit Version ... (c82ass ...)" gefunden')
        else:
            neuester = max(eintraege, key=lambda e: schluessel(e[0]))
            fehler = []
            if neuester[0] != mk.group(1):
                fehler.append('Kopfzeile %s, neuester Eintrag %s' % (mk.group(1), neuester[0]))
            if neuester[1] != asm:
                fehler.append('neuester Eintrag nennt c82ass %s statt %s' % (neuester[1], asm))
            if fehler:
                abw('LIESMICH.md', '; '.join(fehler))
            else:
                ok('LIESMICH.md', 'Version %s, neuester Eintrag nennt c82ass %s' % (mk.group(1), asm))

# 5. Binary
if mit_binary:
    bin_pfad = os.path.join(stamm, 'Assembler', '_Linux', 'c82ass')
    if not os.path.isfile(bin_pfad):
        hinweis('Binary', '%s nicht vorhanden' % bin_pfad)
    else:
        try:
            r = subprocess.run([bin_pfad, '--version'], cwd=os.path.join(stamm, 'Assembler'),
                               capture_output=True, text=True, timeout=30)
            mb = re.search(r'C82aas Version (%s)' % NUM, r.stdout + r.stderr)
            if mb and mb.group(1) == asm:
                ok('Binary c82ass --version', asm)
            else:
                abw('Binary c82ass --version', 'meldet %s statt %s (das Binary baut der Inhaber; bis dahin erwartet)' % (mb.group(1) if mb else 'keine Version', asm))
        except (OSError, subprocess.SubprocessError) as e:
            hinweis('Binary', 'nicht ausfuehrbar: %s' % e)

print('version_abgleich: %s' % ('ALLES IN ORDNUNG' if anzahl_abw == 0 else '%d ABWEICHUNG(EN)' % anzahl_abw))
sys.exit(0 if anzahl_abw == 0 else 1)
PY
