# C 8205 – Simulation eines DDR-Kleinrechners von 1968

Version: 0.03-006

**Deutsch** | [English](README.en.md)

Dieses Projekt rekonstruiert und simuliert die Befehlsverarbeitung des **Cellatron C 8205**, eines 1968
in der DDR gebauten Kleinrechenautomaten. Es besteht aus zwei eigenständigen Werkzeugen:

- einem **Interpreter** (Python), der Maschinencode gegen ein aus Originalunterlagen rekonstruiertes Regelwerk
  ausführt, und
- einem **Assembler** `c82ass` (C), der lesbaren Assembler-Quelltext in genau diesen Maschinencode übersetzt.

> **Sprache:** Die Dokumentation ist auf Deutsch geschrieben und maßgeblich. Eine englische Fassung dieser
> README steht in [README.en.md](README.en.md).

## Der Rechner

Der C 8205 ist ein Einadreßautomat mit geringem technischem Aufwand (rund 400 Transistoren und 2000 Dioden in der
Zentraleinheit). Statt eines RAM nutzt er eine **Magnettrommel** (128 Spuren × 32 Sektoren, 4096 Maschinenworte
zu 33 Bit): Die Zugriffszeit hängt davon ab, wann die gewünschte Stelle unter dem Lese-/Schreibkopf ansteht.
Bedient wird der Rechner über ein Bedienpult mit Tasten, Schaltern und Lampen; Programme und Daten gelangen über
Lochstreifen, ein Schreibwerk und die Tastatur hinein und heraus.

## Wie die Simulation arbeitet

Die Elektronik des Befehlsablaufs (die vier Phasen der Befehlsabarbeitung) ist als **Knotenautomat** mit rund
80 Knoten beschrieben. Der Interpreter führt diesen Knotengraphen **wortlautgetreu** aus:

- Der Graph und die Bedeutung jeder Anweisung werden zur Laufzeit direkt aus den Regelwerk-Dateien
  (`markdown-dateien/`) gelesen, nicht fest einprogrammiert.
- Unklare Stellen werden als offener Punkt gemeldet („Stub“), statt stillschweigend „repariert“ zu werden.
- Alle Zeiten der echten Hardware (Wortzeit, Wartezeit der Trommel) sind in der Simulation 0. Die Reihenfolge der
  Ereignisse bleibt erhalten.

Ein Testlauf besteht aus einer **Trommeldatei** (Speicherinhalt, oktal), einer **Tastenfolge** (Ausgangszustand,
z. B. `H G R`), **Testmarken** für Diagnoseausgaben und optionalen **Prüfungen** mit Sollwerten. Dadurch lassen
sich Läufe als Regressionstests wiederholen.

## Verzeichnisse

| Pfad | Inhalt |
|---|---|
| `c8205_interp.py` | Python-Interpreter |
| `c8205_befehlssweep.py` | Vollständigkeitstest über alle 512 Operationscodes |
| `c8205_interpreter.sh`, `c8205_interpreter.bat` | Wrapper: starten einen Test und schreiben das Protokoll nach `Test-Protokolle/` |
| `compute_all_tests.sh` | führt den Interpreter für alle Testdefinitionen in `Tests/` aus |
| `c8205_bis_test.sh` | Wrapper für Tests der BIS-Bausteine: lädt zuerst das Minimalprogramm (`Tests/pj2-bis_minimalprogramm.test`), dann die angegebene Testdatei |
| `test_bis.sh` | führt alle BIS-Tests nacheinander aus (leere Trommel, Minimalprogramm, dann jeder Test `pj2-bis_*`) |
| `test.sh` | ältere Fassung von `test_bis.sh` (ohne den Test `pj2-bis_druck_bz_ac`) |
| `erzeuge_leere_trommel.py` | erzeugt die leere Trommeldatei `virtuelle_Geraete/Trommel/trommel.txt` (setzt auch eine benutzte Trommel zurück) |
| `c8205_lochstreifen_anzeige.py` | Hilfsprogramm: schreibt einen virtuellen Lochstreifen als Klartext in einem Fenster aus |
| `c8205_lochstreifen_eingabe.py` | Hilfsprogramm: erzeugt einen virtuellen Lochstreifen aus Tastatureingaben in einem Fenster |
| `markdown-dateien/` | Regelwerk und Projektbeschreibung (.md); der Interpreter liest den Knotengraphen von hier |
| `PDF/` | Lesefassungen der Dokumente (A4) |
| `Tests/` | Testaufträge (meist `.txt`; die Endung ist frei, der Assembler erzeugt `.test`) |
| `Test-Ergebnisvergleiche/` | Soll-Dateien der Dateiprüfungen (Namen auf `-ausgabe.txt` oder `_erwartet.txt`) |
| `Test-Protokolle/` | Protokolle (`.log`) der Läufe |
| `virtuelle_Geraete/` | Ablage für virtuelle Geräte (Lochstreifenleser, Stanzer, Schreibwerk, Tastatureingabe, Trommel) |
| `CSV/` | Übersichtstabelle aller Tests (`test_tabelle.py` erzeugt `.csv`, `.md`, `.xlsx`; `test_tabelle_csv_anzeigen.sh` öffnet sie in LibreOffice Calc) |
| `Bausteininterpretiersystem BIS/` | Teilprojekt BIS (derzeit nur Dokumentation) |
| `Assembler/` | Assembler `c82ass` mit Quellcode, Binaries, Beispielen und Dokumentation |

Verkürzte Übersicht (Unterordner der Protokolle und der Beispielprojekte sind nicht einzeln aufgeführt):

```
C8205/
├── c8205_interp.py                 Python-Interpreter
├── c8205_befehlssweep.py           Vollständigkeitstest (512 Operationscodes)
├── c8205_interpreter.sh / .bat     Wrapper mit Protokolldatei
├── compute_all_tests.sh            alle Testdefinitionen in Tests/ ausführen
├── c8205_bis_test.sh               Wrapper für BIS-Tests (lädt zuerst das Minimalprogramm)
├── test_bis.sh                     alle BIS-Tests nacheinander ausführen
├── test.sh                         ältere Fassung von test_bis.sh
├── erzeuge_leere_trommel.py        leere Trommeldatei erzeugen
├── c8205_lochstreifen_anzeige.py   Lochstreifen als Klartext anzeigen (Hilfsprogramm)
├── c8205_lochstreifen_eingabe.py   Lochstreifen aus Tastatureingaben erzeugen (Hilfsprogramm)
├── markdown-dateien/               Regelwerk und Projektbeschreibung (.md)
├── PDF/                            Lesefassungen (A4)
├── Tests/                          Testaufträge (.txt oder .test)
├── Test-Ergebnisvergleiche/        Soll-Dateien der Dateiprüfungen
├── Test-Protokolle/                Protokolle der Läufe (.log)
├── CSV/                            Übersichtstabelle aller Tests (test_tabelle.py)
├── Bausteininterpretiersystem BIS/ Teilprojekt BIS (derzeit nur Dokumentation)
├── virtuelle_Geraete/
│   ├── Leser1/, Leser2/            Lochstreifen-Eingabe
│   ├── Stanzer1/                   Stanzer-Ausgabe
│   ├── SW-Ausgabe/                 Schreibwerk-Ausgabe
│   ├── T-SW-Eingabe/               Tastatur-/Schreibwerk-Eingabe (Kanal K0)
│   └── Trommel/                    Trommeldatei trommel.txt
└── Assembler/
    ├── c82ass.sh                   Assembler ausführen
    ├── asm_alle.sh                 alle .asm-Dateien unter einem Ordner assemblieren (meldet nur Fehler)
    ├── asm_aufraeumen.sh           nicht benötigte Dateien (.log, .mqo, .obj, .sym) löschen
    ├── make_c82ass.sh / .bat       Assembler bauen (Linux / Windows)
    ├── Sourcecode/                 C-Quellcode und Makrodatei
    ├── _Linux/, _Windows/          Binaries
    ├── Dokumentation/              .odt (maßgeblich), .md, .pdf
    ├── Projekt_1/, Projekt_2/, Proj_FeldSortieren/, Claude/   Projektordner (beliebig viele, beliebig benannt)
    └── Claude_bsp_reassemblierung/ Projektordner: u. a. die Quelltexte der Tests aus Tests/
```


Die vollständige Verzeichnisbeschreibung steht in `markdown-dateien/C8205-Projektstruktur.md`.

## Schnellstart: Interpreter

Voraussetzung ist Python 3. Zusätzliche Pakete werden nicht benötigt.

```
python3 c8205_interp.py Tests/0015-030.txt
```

Der Test führt das Programm aus, gibt die Zeichen der Ausgabebefehle auf dem Terminal aus (erwartet:
`Jahr 1972`) und zeigt am Ende die Endzeile. Mit Wrapper und Protokolldatei:

```
./c8205_interpreter.sh 0015-030.txt      # Linux/macOS, schreibt Test-Protokolle/0015-030.log
c8205_interpreter.bat 0015-030.txt       # Windows
```

Alle Testdefinitionen in `Tests/` auf einmal ausführen:

```
./compute_all_tests.sh
```

Alle Schalter (Geräte, Protokolltiefe, Dateiprüfungen) und Fehlermeldungen beschreibt
`markdown-dateien/C8205-Interpreter-Python_Interpreter.md`.

## Schnellstart: Claude-Interpreter (ohne Python)

Ein Test lässt sich auch ohne Python ausführen: Eine KI arbeitet den Knotengraphen von Hand ab. Dazu lädt man das
Regelwerk (`markdown-dateien/`, ohne `Python_Interpreter`, `PDF`, `Projektstruktur`, `Projektueberblick`, `Versionierung` und die
Assembler-Dokumentation) und die Testdatei hoch und gibt eine Startanweisung. Die Schritte, die Dateiauswahl und einen
Vorschlag für die Startanweisung beschreibt `markdown-dateien/C8205-Interpreter-Durchführung_eines_Tests.md`,
Abschnitt 1b (als PDF: `PDF/C8205-Testhandbuch_A4.pdf`, „Kurzanleitung: Test starten“).

## Schnellstart: Assembler

Der Assembler läuft unter Linux und Windows 10. Aufruf unter Linux:

```
Assembler/c82ass.sh -p Projekt_1/bsp_16 -s bsp_5_16
```

Alle `.asm`-Dateien unterhalb eines Ordners auf einmal assemblieren (nur Fehler werden gemeldet; Rückgabewert 0 =
alles fehlerfrei, 1 = Fehler):

```
Assembler/asm_alle.sh [Basisverzeichnis]
```

Zum Selbstbauen aus dem Quellcode: `Assembler/make_c82ass.sh` (Linux) bzw. `Assembler/make_c82ass.bat`
(Windows, MinGW-w64).

Der Assembler erzeugt unter anderem den Objektcode (`.obj`), eine Speicherbelegung (`.dmp`) und eine `.test`-Datei.
Diese enthält die Trommeldatei im Testformat des Interpreters und lässt sich nach Ergänzung der Testmarken und der
Tastenfolge als Testauftrag in `Tests/` verwenden. Sprache, Anweisungen und Makros stehen in
`Assembler/Dokumentation/` (die `.odt` ist maßgeblich).

## Wo anfangen zu lesen?

**Zum ersten Mal hier?** Mit `markdown-dateien/C8205-Einstieg_fuer_Neueinsteiger.md` beginnen: Es erklärt, was das
Projekt enthält (Interpreter, Assembler, BIS), in welcher Reihenfolge man die Dokumente liest und was man zunächst
überspringen kann.

**Projekt schon bekannt oder kompakter Gesamtüberblick gewünscht?** Dann hier weiter:

1. `PDF/C8205-Projektueberblick_A4.pdf` bzw. `markdown-dateien/C8205-Interpreter-Projektueberblick.md`: was das
   Projekt ist und wie die Dokumente zusammenhängen (mit Dokumentenlandkarte).
2. `markdown-dateien/C8205-Interpreter-Überblick_und_Gesamtaufbau.md`: Wurzel des Regelwerks (Geräteaufbau, die vier
   Phasen der Befehlsabarbeitung). Als PDF: `PDF/C8205-Rechnerbeschreibung_A4.pdf`.
3. Danach nach Interesse: Hardware (`Magnettrommel`, `Bedienpult_mit_Schaltern`, `Lochstreifenleser`), Ablauflogik
   (`Eingänge_der_Knoten`, `Beschreibung_der_Knoten`, `Befehlsliste`), Praxis (`Python_Interpreter`,
   `Durchführung_eines_Tests`).

## PDF-Dokumente

Im Ordner `PDF/` liegen Lesefassungen im Format A4, gestaltet nach der Richtlinie
`markdown-dateien/C8205-Interpreter-PDF.md`. Sie werden nicht automatisch aus den `.md`-Dateien nachgeführt und
können deshalb einen älteren Stand haben (der Stand steht im Dokument). Maßgeblich sind die `.md`-Dateien.

| PDF | Inhalt |
|---|---|
| `C8205-Projektueberblick_A4.pdf` | Überblick: Ziel, Architektur, Assembler, virtuelle Hardware, Testkonzept, Dokumentenlandkarte |
| `C8205-Rechnerbeschreibung_A4.pdf` | Aufbau, Register, Maschinenwort, Magnettrommel, Befehlszyklus und Befehlsarten |
| `C8205-Bedienpult_und_Peripherie_A4.pdf` | Tasten, Schalter, Lampen, Kanäle, Lochstreifenleser, Stanzer, Schreibwerk |
| `C8205-Bedienungsanleitung_Interpreter_A4.pdf` | Bedienung von `c8205_interp.py`: Aufruf, Schalter, Geräte |
| `C8205-Testhandbuch_A4.pdf` | Kurzanleitung „Test starten“ (Claude- und Python-Interpreter), Tests schreiben und Protokolle lesen |
| `C8205-Durchfuehrung_eines_Tests_A4.pdf` | Das Testformat im Wortlaut der Quelle |
| `C8205-Knotengraph_A4.pdf` | Der Knotengraph als Diagramm, auf A4-Kacheln aufgeteilt |
| `C8205-Knotentabellen_A4.pdf` | Knotentabelle und Variablentabelle T2 im Wortlaut der Quellen |
| `C8205-Einzelbefehlsliste_A4.pdf` | Generische Befehlsbeschreibung und Übersicht aller 512 Operationscodes |
| `C8205-Kodetabellen_A4.pdf` | Zeichenkodetabelle (R 300-Lochstreifenkode) |
| `Assembler/Dokumentation/C8205_Assembler_Dokumentation.pdf` | Assembler `c82ass`: Aufruf, Sprache, Makros, Beispiel |

## Stand

Der Interpreter meldet jede Stelle, bei der das Regelwerk unklar ist oder zu der noch keine Umsetzung vorliegt,
bewusst als **Stub** und bricht mit einer Meldung ab, statt zu raten („laut scheitern“). Das ist gewollt und kein
Fehler. Ob für jeden der 512 Operationscodes eine Umsetzung vorhanden ist, prüft `c8205_befehlssweep.py`.

## Versionsnummern

Jede `.md`-Datei und der Interpreter tragen eine eigene Versionsnummer der Form `y.xx-zzz` (Hauptversion,
Unterversion, Build), bei den Dokumenten als Zeile `Version:` unter dem Titel. Die Nummer des Interpreters zeigt
`python3 c8205_interp.py --version`. Aufbau und Regeln: `markdown-dateien/C8205-Versionierung.md`.

**Regel für alle, die mitarbeiten (auch KI-Sitzungen):** Jede Änderung an einer dieser Dateien erhöht ihren Build (`zzz`)
um 1. Hauptversion und Unterversion werden nur auf ausdrückliche Aufforderung des Projektinhabers erhöht.

## Lizenz

MIT-Lizenz, siehe [LICENSE](LICENSE). Sie gilt für den Interpreter, den Assembler, die Tests und die selbst
verfassten Dokumente. Rechte an den Originalunterlagen des C 8205, aus denen das Regelwerk rekonstruiert wurde,
bleiben bei ihren jeweiligen Inhabern.

## Quellen und Hintergrund

Das Regelwerk wurde aus Originalunterlagen des Rechners (u. a. Programmieranleitung und Originaldokumentation)
rekonstruiert. Die Dokumente zitieren sie abschnittsweise.
