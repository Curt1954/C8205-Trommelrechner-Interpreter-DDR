#!/usr/bin/env python3
"""migrate_doku.py - Migration der Dokumentation (Schritt 2) nach migrate_virtuelle_geraete.sh (Schritt 1).

Aufruf im Projektverzeichnis (dort, wo c8205_interp.py liegt):
    python3 migrate_doku.py -n      Trockenlauf: zeigt je Datei die Zahl der Aenderungen, schreibt nichts
    python3 migrate_doku.py         ausfuehren (Sicherungskopien *.vor_migration liegen NICHT an; vorher sichern oder git benutzen)
    python3 migrate_doku.py -d      zusaetzlich die Aenderungen als unified diff ausgeben

Bearbeitet werden: markdown-dateien/*.md, README.md, README.en.md.   Nicht bearbeitet: CSV/, PDF/ (werden aus diesen Quellen
bzw. vom Projektinhaber neu erzeugt), Test-Protokolle/.

Regeln
  1. virtuelle_Geraete/Trommelvorlagen -> Trommel/Trommelvorlagen;   virtuelle_Geraete/Trommel -> Trommel     (gemeinsam fuer TEST und GRAFIK)
  2. Dokumente, die den TEST-Interpreter beschreiben (*eines_Tests.md, *Python_Interpreter.md, *Lochstreifenleser.md):
        jedes uebrige virtuelle_Geraete/ -> Test-virtuelleGeraete/
  3. alle anderen Dokumente: nur SW-Ausgabe, T-SW-Eingabe, Leser1_02 -> Test-virtuelleGeraete/ ; Leser1, Leser2, Stanzer1 bleiben
        unter virtuelle_Geraete/ (das sind jetzt die Ordner des GRAFIK-Interpreters)
  4. Handarbeit (feste Textstellen): Strukturtabellen in Projektstruktur, Einstieg, README, README.en; Testband-Pfad des Tests
        k1_leser_stanzer; neue Zeile im Entscheidungsregister von GRAFIK_Beschreibung
Jede Handarbeitsstelle wird nur ersetzt, wenn der erwartete Text genau einmal vorkommt; sonst Meldung "NICHT GEFUNDEN" (nichts geaendert).
"""
import difflib
import glob
import os
import re
import sys

TROCKEN = '-n' in sys.argv
ZEIGE_DIFF = '-d' in sys.argv

if not (os.path.isfile('c8205_interp.py') and os.path.isdir('Test-virtuelleGeraete') and os.path.isdir('Trommel')):
    sys.exit('FEHLER: bitte im Projektverzeichnis starten, nachdem Schritt 1 (migrate_virtuelle_geraete.sh) gelaufen ist.')

dateien = sorted(glob.glob('markdown-dateien/*.md')) + [f for f in ('README.md', 'README.en.md') if os.path.isfile(f)]
if any('Verzeichnisse der Geräte neu geordnet' in open(f, encoding='utf-8').read() for f in dateien if f.endswith('GRAFIK_Beschreibung.md')):
    sys.exit('Die Dokumentation ist offenbar schon migriert (Registerzeile vom 20.10.2026 vorhanden) - nichts getan.')
TEST_DOKUS = ('eines_Tests.md', 'Python_Interpreter.md', 'Lochstreifenleser.md')
meldungen = []


def ersetze_einmal(text, alt, neu, name):
    """Handarbeitsstelle: alt muss genau einmal vorkommen."""
    n = text.count(alt)
    if n != 1:
        meldungen.append(f'NICHT GEFUNDEN ({n}x statt 1x) in {name}: {alt[:70]!r}...')
        return text
    return text.replace(alt, neu)


def regeln(name, text):
    text = text.replace('virtuelle_Geraete/Trommelvorlagen', 'Trommel/Trommelvorlagen')
    text = text.replace('virtuelle_Geraete/Trommel', 'Trommel')
    if name.endswith(TEST_DOKUS):
        text = text.replace('virtuelle_Geraete/', 'Test-virtuelleGeraete/')
    else:
        text = re.sub(r'virtuelle_Geraete/(SW-Ausgabe|T-SW-Eingabe|Leser1_02)', r'Test-virtuelleGeraete/\1', text)
    return text


def handarbeit(name, text):
    if name.endswith('Projektstruktur.md'):
        # Tabellenzeile -> drei Zeilen
        m = re.search(r'^\| `virtuelle_Geraete/` \| Ablage der virtuellen Geräte für den Interpreter.*\n', text, re.M)
        if not m:
            meldungen.append('NICHT GEFUNDEN: Tabellenzeile virtuelle_Geraete/ in ' + name)
        else:
            zellen = m.group(0).strip().strip('|').split(' | ')
            verweis = zellen[2].strip() if len(zellen) >= 3 else ''
            neu = (
                '| `Test-virtuelleGeraete/` | Ablage der virtuellen Geräte für den **TEST-Interpreter** (`c8205_interp.py --MODUS=TEST`), je Gerät ein Unterordner: '
                '`Leser1/`, `Leser1_02/`, `Leser2/` (Lochstreifen für Leser 1 und 2), `Stanzer1/` (Ausgabe des Stanzers 1), `SW-Ausgabe/` (Schreibwerk-Ausgabe), '
                '`T-SW-Eingabe/` (Eingabe über Tastatur/Schreibwerk, Kanal K0); siehe Abschnitt 2 | ' + verweis + ' |\n'
                '| `virtuelle_Geraete/` | Ablage der virtuellen Geräte für den **GRAFIK-Interpreter** (`c8205_grafik.py`), Standardordner der Schalter `--leser1`, `--leser2`, '
                '`--stanzer1`: `Leser1/`, `Leser2/`, `Stanzer1/` (zunächst leer) | `C8205-Interpreter-GRAFIK_Beschreibung.md` |\n'
                '| `Trommel/` | die **gemeinsame Trommel** für TEST und GRAFIK: Trommeldatei `trommel.txt`, Schalterdatei der Bahnsperren `trommel.basp`, '
                '`trommel_r300_eingabe.txt` (der persistente Speicher des Rechners); siehe Abschnitt 2 | Trommel: `C8205-Interpreter-Python_Interpreter.md`, 8.5, und '
                '`C8205-Interpreter-Durchführung_eines_Tests.md`, 2c |\n')
            text = text.replace(m.group(0), neu)
        text = ersetze_einmal(text, 'Verzeichnisse `virtuelle_Geraete/Leser1/`, `…/Leser2/`, `…/Stanzer1/`, `…/SW-Ausgabe/` und `…/T-SW-Eingabe/`',
                              'Verzeichnisse `Test-virtuelleGeraete/Leser1/`, `…/Leser2/`, `…/Stanzer1/`, `…/SW-Ausgabe/` und `…/T-SW-Eingabe/`', name)
        text = ersetze_einmal(text, '`--leser1 virtuelle_Geraete/Leser1` oder', '`--leser1 Test-virtuelleGeraete/Leser1` oder', name)
        text = ersetze_einmal(text, '`--k0 datei=Test-virtuelleGeraete/T-SW-Eingabe`.',
                              '`--k0 datei=Test-virtuelleGeraete/T-SW-Eingabe`. Für den Interpreter GRAFIK gelten die Standardordner `virtuelle_Geraete/Leser1/`, '
                              '`…/Leser2/` und `…/Stanzer1/` (eigene, anfangs leere Ordner); die Trommel `Trommel/trommel.txt` benutzen beide Interpreter gemeinsam.', name)
        text = ersetze_einmal(text, 'Testband `virtuelle_Geraete/Leser1/lb_kopie_quelle.txt`', 'Testband `Test-virtuelleGeraete/Leser1_02/lb_kopie_quelle.txt`', name)
    elif name.endswith('Einstieg_fuer_Neueinsteiger.md'):
        text = ersetze_einmal(text, '`Test-Protokolle/` und `virtuelle_Geraete/`?', '`Test-Protokolle/`, `Test-virtuelleGeraete/`, `virtuelle_Geraete/` und `Trommel/`?', name)
        text = ersetze_einmal(
            text,
            '| `virtuelle_Geraete/` | die virtuellen Geräte, je ein Unterordner: `Leser1/`, `Leser2/`, `Stanzer1/`, `SW-Ausgabe/`, `T-SW-Eingabe/`, `Trommel/` |',
            '| `Test-virtuelleGeraete/` | die virtuellen Geräte des TEST-Interpreters, je ein Unterordner: `Leser1/`, `Leser1_02/`, `Leser2/`, `Stanzer1/`, `SW-Ausgabe/`, `T-SW-Eingabe/` |\n'
            '| `virtuelle_Geraete/` | die virtuellen Geräte des GRAFIK-Interpreters: `Leser1/`, `Leser2/`, `Stanzer1/` |\n'
            '| `Trommel/` | die gemeinsame Trommel (`trommel.txt`) für TEST und GRAFIK |', name)
    elif name.startswith('README'):
        en = name.endswith('.en.md')
        if en:
            alt = '| `virtuelle_Geraete/` | Storage for virtual devices (punched tape reader, punch, typewriter unit, keyboard input, drum) |'
            neu = ('| `Test-virtuelleGeraete/` | Virtual devices of the TEST interpreter (punched tape readers, punch, typewriter unit output, keyboard input) |\n'
                   '| `virtuelle_Geraete/` | Virtual devices of the GRAFIK interpreter (`Leser1/`, `Leser2/`, `Stanzer1/`) |\n'
                   '| `Trommel/` | The drum file `trommel.txt`, shared by both interpreters |')
            baum_alt = ('├── virtuelle_Geraete/\n│   ├── Leser1/, Leser2/            Punched tape input\n│   ├── Stanzer1/                   Punch output\n'
                        '│   ├── SW-Ausgabe/                 Typewriter unit output\n│   ├── T-SW-Eingabe/               Keyboard / typewriter unit input (channel K0)\n'
                        '│   └── Trommel/                    Drum file trommel.txt\n')
            baum_neu = ('├── Trommel/                        Drum file trommel.txt (shared by TEST and GRAFIK)\n'
                        '├── Test-virtuelleGeraete/          virtual devices of the TEST interpreter\n│   ├── Leser1/, Leser1_02/, Leser2/   Punched tape input\n'
                        '│   ├── Stanzer1/                   Punch output\n│   ├── SW-Ausgabe/                 Typewriter unit output\n'
                        '│   └── T-SW-Eingabe/               Keyboard / typewriter unit input (channel K0)\n'
                        '├── virtuelle_Geraete/              virtual devices of the GRAFIK interpreter\n│   ├── Leser1/, Leser2/            Punched tape input\n'
                        '│   └── Stanzer1/                   Punch output\n')
        else:
            alt = '| `virtuelle_Geraete/` | Ablage für virtuelle Geräte (Lochstreifenleser, Stanzer, Schreibwerk, Tastatureingabe, Trommel) |'
            neu = ('| `Test-virtuelleGeraete/` | Virtuelle Geräte des TEST-Interpreters (Lochstreifenleser, Stanzer, Schreibwerk-Ausgabe, Tastatureingabe) |\n'
                   '| `virtuelle_Geraete/` | Virtuelle Geräte des GRAFIK-Interpreters (`Leser1/`, `Leser2/`, `Stanzer1/`) |\n'
                   '| `Trommel/` | Die Trommeldatei `trommel.txt`, gemeinsam für beide Interpreter |')
            baum_alt = ('├── virtuelle_Geraete/\n│   ├── Leser1/, Leser2/            Lochstreifen-Eingabe\n│   ├── Stanzer1/                   Stanzer-Ausgabe\n'
                        '│   ├── SW-Ausgabe/                 Schreibwerk-Ausgabe\n│   ├── T-SW-Eingabe/               Tastatur-/Schreibwerk-Eingabe (Kanal K0)\n'
                        '│   └── Trommel/                    Trommeldatei trommel.txt\n')
            baum_neu = ('├── Trommel/                        Trommeldatei trommel.txt (gemeinsam für TEST und GRAFIK)\n'
                        '├── Test-virtuelleGeraete/          virtuelle Geräte des TEST-Interpreters\n│   ├── Leser1/, Leser1_02/, Leser2/   Lochstreifen-Eingabe\n'
                        '│   ├── Stanzer1/                   Stanzer-Ausgabe\n│   ├── SW-Ausgabe/                 Schreibwerk-Ausgabe\n'
                        '│   └── T-SW-Eingabe/               Tastatur-/Schreibwerk-Eingabe (Kanal K0)\n'
                        '├── virtuelle_Geraete/              virtuelle Geräte des GRAFIK-Interpreters\n│   ├── Leser1/, Leser2/            Lochstreifen-Eingabe\n'
                        '│   └── Stanzer1/                   Stanzer-Ausgabe\n')
        text = ersetze_einmal(text, alt, neu, name)
        text = ersetze_einmal(text, baum_alt, baum_neu, name)
        # GRAFIK-Beispielaufruf: der Testlochstreifen liegt im TEST-Ordner (Leser1_02), die Stanzer-Ausgabe geht in den GRAFIK-Ordner
        text = ersetze_einmal(text, '--leser1 virtuelle_Geraete/Leser1/lb_kopie_quelle.txt --stanzer1 virtuelle_Geraete/Stanzer1/lb_kopie_ausgabe.txt',
                              '--leser1 Test-virtuelleGeraete/Leser1_02/lb_kopie_quelle.txt --stanzer1 virtuelle_Geraete/Stanzer1/lb_kopie_ausgabe.txt', name)
    elif name.endswith('GRAFIK_Beschreibung.md'):
        zeilen = text.split('\n')
        idx = next((i for i, z in enumerate(zeilen) if z.startswith('| 15.10.2026 | **Gemeinsame Trommeldatei:**')), None)
        if idx is None:
            meldungen.append('NICHT GEFUNDEN: Entscheidungsregister in ' + name)
        else:
            ende = idx                       # letzte datierte Registerzeile (Form "| tt.mm.jjjj | ...") hinter dem Eintrag vom 15.10.2026
            for i in range(idx, len(zeilen)):
                if '<!-- REGISTER-ENDE -->' in zeilen[i]:
                    break
                if re.match(r'\| \d\d\.\d\d\.\d{4} \|', zeilen[i]):
                    ende = i
            zeile = ('| 20.10.2026 | **Verzeichnisse der Geräte neu geordnet:** `virtuelle_Geraete/` heißt jetzt `Test-virtuelleGeraete/` und gehört nur dem TEST-Interpreter '
                     '(`Leser1/`, `Leser1_02/`, `Leser2/`, `Stanzer1/`, `SW-Ausgabe/`, `T-SW-Eingabe/`). Neu ist ein leeres `virtuelle_Geraete/` mit `Leser1/`, `Leser2/`, `Stanzer1/` '
                     'als Standardordner von GRAFIK. Die Trommel liegt in `Trommel/` (`trommel.txt`, `trommel.basp`, `trommel_r300_eingabe.txt`) und ist für beide Interpreter gemeinsam; '
                     'die Einträge vom 15.10.2026 gelten mit dem neuen Pfad `Trommel/trommel.txt` | Projektstruktur |')
            zeilen.insert(ende + 1, zeile)
            text = '\n'.join(zeilen)
    return text


gesamt = 0
for pfad in dateien:
    with open(pfad, encoding='utf-8', newline='') as f:
        alt = f.read()
    crlf = '\r\n' in alt
    text = alt.replace('\r\n', '\n') if crlf else alt
    neu = handarbeit(pfad, regeln(pfad, text))
    if neu == text:
        continue
    gesamt += 1
    n = sum(1 for a, b in zip(text.split('\n'), neu.split('\n')) if a != b) + abs(len(neu.split('\n')) - len(text.split('\n')))
    print(f'{"[Trockenlauf] " if TROCKEN else ""}geändert: {pfad}  (~{n} Zeilen)')
    if ZEIGE_DIFF:
        sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), neu.splitlines(True), pfad, pfad + ' (neu)', n=0))
    if not TROCKEN:
        with open(pfad, 'w', encoding='utf-8', newline='') as f:
            f.write(neu.replace('\n', '\r\n') if crlf else neu)

print(f'\n{gesamt} Dateien {"würden geändert" if TROCKEN else "geändert"}.')
for m in meldungen:
    print(m)

if TROCKEN:
    print('\n(Trockenlauf: Die Liste der verbliebenen Fundstellen gibt es erst nach dem echten Lauf, weil jetzt nichts geschrieben wurde.)')
    sys.exit(1 if meldungen else 0)
print('\nVerbliebene Fundstellen "virtuelle_Geraete" (zur Durchsicht; erwartet: nur GRAFIK-Standardordner Leser1/Leser2/Stanzer1 und Hilfsprogramm-Beispiele):')
for pfad in dateien:
    with open(pfad, encoding='utf-8') as f:
        for i, z in enumerate(f, 1):
            if 'virtuelle_Geraete' in z:
                print(f'  {pfad}:{i}: {z.strip()[:150]}')
sys.exit(1 if meldungen else 0)

