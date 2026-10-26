#!/bin/bash
# lieferung_packen.sh -- packt eine Lieferung (Checkpoint) als Zip, jede Datei mit ihrem Projektpfad.
# Das Zip lässt sich im Projektstamm entpacken; die Dateien landen an der richtigen Stelle.
#
# Aufruf (von überall; das Skript liegt im Projektstamm):
#   lieferung_packen.sh [Optionen] Datei [Datei ...]     genau diese Dateien packen (Pfade ab Projektstamm)
#   lieferung_packen.sh [Optionen] --seit <Original.zip> alles packen, was gegenüber dem Original-Zip neu
#                                                        oder geändert ist (Checkpoint nach jeder Änderung)
#
# Optionen:
#   --seit <zip>   Vergleichsstand (das hochgeladene Zip). Erzeugte Dateien werden übergangen:
#                  Test-Protokolle/, Trommel/trommel.txt, Assembler/projekdetails, .log .mqo .obj .sym,
#                  __pycache__, frühere Lieferungen. Zusätzlich zu --seit dürfen Dateien genannt werden.
#   -d <Ordner>    Zielordner (Vorgabe: /mnt/user-data/outputs, sonst der aktuelle Ordner)
#   -o <Name.zip>  Dateiname (Vorgabe: C8205_Lieferung_NNN.zip, NNN = nächste freie Nummer im Zielordner)
#   -l             nur anzeigen, was gepackt würde (kein Zip)
#   -h             diese Hilfe
#
# Regeln: Keine Binaries (nichts unter Assembler/_Linux/ und _Windows/, keine ELF-/EXE-Dateien).
#         Fehlt eine genannte Datei, wird nichts gepackt. Ausführbare .sh-Dateien bleiben ausführbar.
# Rückgabe: 0 Zip erzeugt (oder -l), 1 nichts zu packen, 2 Aufruf falsch oder Datei fehlt, 3 Binary verweigert.
# Nach dem Packen nur die neueste Lieferung an den Nutzer senden.

stamm=$(cd "$(dirname "$0")" && pwd) || exit 2
exec python3 -I - "$stamm" "$@" <<'PY'
import os, re, sys, zipfile

stamm, args = sys.argv[1], sys.argv[2:]

def hilfe():
    with open(os.path.join(stamm, 'lieferung_packen.sh'), encoding='utf-8') as f:
        for z in f.read().split('\n')[1:]:
            if not z.startswith('#'):
                break
            print(z[2:] if z.startswith('# ') else z[1:])

seit = ziel = name = None
nur_liste = False
dateien = []
i = 0
while i < len(args):
    a = args[i]
    if a in ('-h', '--hilfe', '--help'):
        hilfe(); sys.exit(0)
    elif a in ('--seit', '-d', '-o'):
        if i + 1 >= len(args):
            print('Option %s braucht einen Wert.' % a); sys.exit(2)
        v = args[i + 1]; i += 1
        if a == '--seit': seit = v
        elif a == '-d': ziel = v
        else: name = v
    elif a == '-l':
        nur_liste = True
    elif a.startswith('-') and len(a) > 1:
        print('Unbekannte Option %s (Hilfe: -h).' % a); sys.exit(2)
    else:
        dateien.append(a)
    i += 1

if not dateien and not seit:
    hilfe(); sys.exit(2)

ERZEUGT_VERZ = ('Test-Protokolle/', '__pycache__/')
ERZEUGT_DATEI = ('Trommel/trommel.txt', 'Assembler/projekdetails')
ERZEUGT_ENDUNG = ('.log', '.mqo', '.obj', '.sym', '.pyc')

def erzeugt(rel):
    if any(rel.startswith(v) or ('/' + v) in rel for v in ERZEUGT_VERZ): return True
    if rel in ERZEUGT_DATEI or rel.startswith('Assembler/projekdetails'): return True
    if rel.endswith(ERZEUGT_ENDUNG) and not rel.startswith('Assembler/Regressionstest/'): return True
    if re.match(r'(C8205_Lieferung.*|C8205 Simulator.*)\.zip$', os.path.basename(rel)): return True
    return False

def binary(rel, pfad):
    if rel.startswith(('Assembler/_Linux/', 'Assembler/_Windows/')): return True
    try:
        with open(pfad, 'rb') as f: kopf = f.read(4)
    except OSError:
        return False
    return kopf[:4] == b'\x7fELF' or kopf[:2] == b'MZ' or kopf in (b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe')

def rel_von(d):
    p = os.path.normpath(d)
    if os.path.isabs(p):
        p = os.path.relpath(p, stamm)
    return p.replace(os.sep, '/')

liste = {}   # rel -> Kennzeichen
fehlend, verweigert = [], []

for d in dateien:
    rel = rel_von(d)
    pfad = os.path.join(stamm, rel)
    if rel.startswith('../') or not os.path.isfile(pfad):
        fehlend.append(d); continue
    if binary(rel, pfad):
        verweigert.append(rel); continue
    liste[rel] = 'genannt'

if seit:
    try:
        zf = zipfile.ZipFile(seit)
    except (OSError, zipfile.BadZipFile) as e:
        print('Vergleichs-Zip nicht lesbar: %s (%s)' % (seit, e)); sys.exit(2)
    alt = {}
    for zi in zf.infolist():
        if zi.is_dir(): continue
        n = zi.filename
        if not (zi.flag_bits & 0x800):
            try: n = n.encode('cp437').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError): pass
        alt[n] = zi
    for wurzel, verz, fs in os.walk(stamm):
        verz[:] = [v for v in verz if v not in ('.git', '__pycache__')]
        for fn in fs:
            pfad = os.path.join(wurzel, fn)
            rel = os.path.relpath(pfad, stamm).replace(os.sep, '/')
            if erzeugt(rel) or rel in liste: continue
            if rel not in alt:
                kz = 'neu'
            else:
                with open(pfad, 'rb') as f: neu = f.read()
                if neu == zf.read(alt[rel]): continue
                kz = 'geändert'
            if binary(rel, pfad):
                if kz == 'geändert' or rel.startswith(('Assembler/_Linux/', 'Assembler/_Windows/')):
                    verweigert.append(rel + ' (' + kz + ')')
                continue
            liste[rel] = kz

if fehlend:
    print('Datei nicht gefunden, nichts gepackt:')
    for d in fehlend: print('  ' + d)
    sys.exit(2)
if verweigert:
    print('Binaries werden nie geliefert, nichts gepackt:')
    for r in verweigert: print('  ' + r)
    sys.exit(3)
if not liste:
    print('Nichts zu packen: keine Änderung gegenüber dem Vergleichsstand.')
    sys.exit(1)

for rel in sorted(liste):
    print('  %-9s %s' % (liste[rel], rel))

if nur_liste:
    print('%d Dateien (nur Anzeige, kein Zip).' % len(liste)); sys.exit(0)

if ziel is None:
    ziel = '/mnt/user-data/outputs' if os.path.isdir('/mnt/user-data/outputs') else os.getcwd()
os.makedirs(ziel, exist_ok=True)
if name is None:
    nr = [int(m.group(1)) for f in os.listdir(ziel) for m in [re.match(r'C8205_Lieferung_(\d{3})\.zip$', f)] if m]
    name = 'C8205_Lieferung_%03d.zip' % (max(nr) + 1 if nr else 1)
ziel_zip = os.path.join(ziel, name)

with zipfile.ZipFile(ziel_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    for rel in sorted(liste):
        pfad = os.path.join(stamm, rel)
        zi = zipfile.ZipInfo.from_file(pfad, rel)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = (0o755 if os.access(pfad, os.X_OK) and rel.endswith(('.sh', '.py')) else 0o644) << 16
        with open(pfad, 'rb') as f: z.writestr(zi, f.read())
print('Zip: %s (%d Dateien)' % (ziel_zip, len(liste)))
PY
