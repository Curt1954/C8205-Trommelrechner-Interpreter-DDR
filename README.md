# C 8205 – Simulation eines DDR-Kleinrechners von 1968

Version: 0.95-012

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
| `CLAUDE.md`, `C8205-Programmierhandbuch_fuer_Claude.md` | Einstieg für KI-Sitzungen: Karte (kurz, zuerst lesen; mit Skriptliste) und Handbuch zum Programmieren in Assembler |
| `c8205_grafik.py`, `c8205_grafik.sh`/`.bat`, `grafik-interpreter-module/grafik_*.py` | Modus GRAFIK: Pult-Fenster, Schreibwerk-Fenster, Töne (Mischer, Schreibwerk, Leser, Stanzer, Rechner) |
| `c-module/` | C-Module: Trommel, Bahnsperre, Unterbrechung, Tonmischer `tonmisch`; Erweiterungsmodul in `c-module/python/` |
| `C8205Z/` | **Experimenteller Prototyp** der vier Zusatztrommeln des C 8205Z (einziger Zusatzpfad): Zeitmodell `zt/`, C-Modul `zt_modul/`, Tests `Tests_Z/`, Pultzeichnung `pult_z/`; wirkt nur mit dem Schalter `--C8205Z` |
| `ton/` | Klänge (`sw_toene/`, `toene_rechner_stanzer/`, `pult_toene/` Tastengeräusche des Pults, Netzgeräusche), Testrahmen `sw_ton.py`, `SW_Ton_Beschreibung.md` |
| `testscripte/` | Prüfungen und Testskripte, u. a. `grafik_alle_tests.sh`, `grafik_stufe4_tests.py` |
| `Hilfsprogramme/` | `c8205_lochstreifen_anzeige.py` (virtuellen Lochstreifen als Klartext in einem Fenster ausschreiben), `c8205_lochstreifen_eingabe.py` (virtuellen Lochstreifen aus Tastatureingaben erzeugen), `c8205_lochstreifen_umwandlung.py` (Textdatei in binär kodierten R300-Lochstreifen umwandeln und zurück) |
| `testscripte/` | Testskripte; jedes wechselt selbst ins Projektverzeichnis und darf von überall gestartet werden: `compute_all_tests.sh` (alle Testdefinitionen in `Tests/`), `c8205_bis_test.sh` (Tests künftiger BIS-Bausteine: lädt zuerst das Minimalprogramm `Tests/pj2-bis_minimalprogramm_v6.test` mit `--LOADONLY`, dann die angegebene Testdatei; die Tests des Minimalprogramms selbst, `Tests/pj2-bis_v6_*.test`, tragen ihr Abbild und laufen über `compute_all_tests.sh`), `c8205_befehlssweep.py` (Vollständigkeitstest über alle 512 Operationscodes; Aufruf aus dem Projektordner mit `--interp c8205_interp.py` bzw. aus `testscripte/` mit `--interp ../c8205_interp.py`), `erzeuge_leere_trommel.py` (erzeugt die leere Trommeldatei `Trommel/trommel.txt`, setzt auch eine benutzte Trommel zurück) |
| `pult/` | Bilder und Manifest des Bedienpult-Fensters (Modus GRAFIK) |
| `make_pdf.sh`, `make_all_pdf.sh` | Aufrufhilfen zum Erzeugen der PDFs (Skripte in den Ordnern `pdf-layout-scripte/`) |
| `markdown-dateien/` | Regelwerk und Projektbeschreibung (.md); der Interpreter liest den Knotengraphen von hier |
| `PDF/` | Lesefassungen der Dokumente (A4) |
| `Tests/` | Testaufträge (meist `.txt`; die Endung ist frei, der Assembler erzeugt `.test`) |
| `Test-Ergebnisvergleiche/` | Soll-Dateien der Dateiprüfungen (Namen auf `-ausgabe.txt` oder `_erwartet.txt`) |
| `Test-Protokolle/` | Protokolle (`.log`) der Läufe |
| `Test-virtuelleGeraete/` | Virtuelle Geräte des TEST-Interpreters (Lochstreifenleser, Stanzer, Schreibwerk-Ausgabe, Tastatureingabe) |
| `virtuelle_Geraete/` | Virtuelle Geräte des GRAFIK-Interpreters (`Leser1/`, `Leser2/`, `Stanzer1/`) |
| `Lochstreifen/` | Fertige Lochstreifen- und Ladedateien, nach Format geordnet (`im_KEP-Format/`, `im_BIS-Format/`, `das_KEP_im_TEST-Format/`, `Datenformat/`) |
| `Trommel/` | Die Trommeldatei `trommel.txt`, gemeinsam für beide Interpreter |
| `Testausfuehrungen/` | Test ausführen und Tests überblicken: `testwahl.sh` (Test aus der Liste wählen und ausführen), `kep_test.sh`, `interpreter_test.sh` und `bis_test.sh` (Vorführläufe mit KEP, TEST-Interpreter und BIS); dazu die Übersichtstabelle aller Tests (`test_tabelle.py` erzeugt `.csv`, `.md`, `.xlsx`; `test_tabelle_csv_anzeigen.sh` öffnet sie in LibreOffice Calc) |
| `Bausteininterpretiersystem BIS/` | Teilprojekt BIS (derzeit nur Dokumentation) |
| `Assembler/` | Assembler `c82ass` mit Quellcode, Linux-Binary, Beispielen und Dokumentation |

Verkürzte Übersicht (Unterordner der Protokolle und der Beispielprojekte sind nicht einzeln aufgeführt):

```
C8205/
├── c8205_interp.py                 Python-Interpreter
├── c8205_grafik.py / .sh / .bat    Modus GRAFIK (Pult-Fenster, Schreibwerk-Fenster, Töne)
├── grafik-interpreter-module/      Module des Modus GRAFIK (grafik_*.py)
├── c-module/                       C-Module (Trommel, Bahnsperre, Unterbrechung, Tonmischer)
├── ton/                            Klänge und Ton-Testrahmen
├── pult/                           Bilder und Manifest des Pult-Fensters
├── Hilfsprogramme/                 Lochstreifen-Hilfsprogramme
├── testscripte/                    Testskripte (compute_all_tests.sh, BIS-Tests, GRAFIK-Prüfungen,
│                                   erzeuge_leere_trommel.py)
├── make_pdf.sh, make_all_pdf.sh    PDF-Erzeugung
├── c8205_zip_packen.sh             Gesamt-Zip "C8205 Simulator V.M.P.zip" packen (mit den Sub-Zips Test-Protokolle.zip und Regressionstest.zip); mit `--claude` die schlanke Variante ohne PDFs, Klänge und Pult-Bilder
├── lieferung_packen.sh             Lieferung (Checkpoint) als Zip mit Projektpfaden packen (für KI-Sitzungen)
├── markdown-dateien/               Regelwerk und Projektbeschreibung (.md)
├── PDF/                            Lesefassungen (A4)
├── Tests/                          Testaufträge (.txt oder .test)
├── Test-Ergebnisvergleiche/        Soll-Dateien der Dateiprüfungen
├── Test-Protokolle/                Protokolle der Läufe (.log); im Gesamt-Zip nur als Test-Protokolle.zip (im Projektstamm entpacken, wird sonst vom Interpreter neu angelegt)
├── Testausfuehrungen/              Testausführung (testwahl.sh u. a.) und Übersichtstabelle aller Tests (test_tabelle.py)
├── Bausteininterpretiersystem BIS/ Teilprojekt BIS (derzeit nur Dokumentation)
├── Lochstreifen/                   fertige Lochstreifen- und Ladedateien, nach Format geordnet
├── Trommel/                        Trommeldatei trommel.txt (gemeinsam für TEST und GRAFIK)
├── Test-virtuelleGeraete/          virtuelle Geräte des TEST-Interpreters
│   ├── Leser1/, Leser1_02/, Leser2/   Lochstreifen-Eingabe
│   ├── Stanzer1/                   Stanzer-Ausgabe
│   ├── SW-Ausgabe/                 Schreibwerk-Ausgabe
│   └── T-SW-Eingabe/               Tastatur-/Schreibwerk-Eingabe (Kanal K0)
├── virtuelle_Geraete/              virtuelle Geräte des GRAFIK-Interpreters
│   ├── Leser1/, Leser2/            Lochstreifen-Eingabe
│   └── Stanzer1/                   Stanzer-Ausgabe
├── CLAUDE.md                       Karte für KI-Sitzungen (zuerst lesen)
├── C8205-Programmierhandbuch_fuer_Claude.md   Handbuch dazu
├── README.md, README.en.md, LICENSE
└── Assembler/
    ├── c82ass.sh                   Assembler ausführen
    ├── asm_alle.sh                 alle .asm-Dateien unter einem Ordner assemblieren (meldet nur Fehler)
    ├── asm_und_test.sh             assemblieren, .test um Prüfung ergänzen und im Interpreter testen (ein Aufruf)
    ├── asm_aufraeumen.sh           nicht benötigte Dateien (.log, .mqo, .obj, .sym) löschen
    ├── make_c82ass.sh / .bat       Assembler bauen (Linux / Windows)
    ├── Sourcecode/                 C-Quellcode und Makrodatei
    ├── _Linux/                     Binary (Windows: `_Windows/c82ass.exe` liegt bei, selbst bauen mit `make_c82ass.bat`)
    ├── Dokumentation/              .odt (maßgeblich), .md, .pdf
    ├── Regressionstest/            Prüfung des Assemblers; im Gesamt-Zip nur als Regressionstest.zip (im Projektstamm entpacken, Pfade darin: Assembler/Regressionstest/...)
    ├── Projekt_1/, Projekt_2/, Proj_FeldSortieren/, Claude/   Projektordner (beliebig viele, beliebig benannt); Claude/mini/ ist das kleinste geprüfte Beispiel
    └── Claude_bsp_reassemblierung/ Projektordner: u. a. die Quelltexte der Tests aus Tests/
```


Die vollständige Verzeichnisbeschreibung steht in `markdown-dateien/C8205-Projektstruktur.md`.

## Schnellstart: Interpreter

Voraussetzung ist Python 3. Zusätzliche Pakete werden nicht benötigt.

```
python3 c8205_interp.py --MODUS=TEST Tests/0015-030.txt
```

Der Test führt das Programm aus, gibt die Zeichen der Ausgabebefehle auf dem Terminal aus (erwartet:
`Jahr 1972`) und zeigt am Ende die Endzeile. Mit Wrapper und Protokolldatei:

```
./c8205_interpreter.sh 0015-030.txt      # Linux/macOS, schreibt Test-Protokolle/0015-030.log
c8205_interpreter.bat 0015-030.txt       # Windows
```

Alle Testdefinitionen in `Tests/` auf einmal ausführen:

```
testscripte/compute_all_tests.sh
```

Alle Schalter (Geräte, Protokolltiefe, Dateiprüfungen) und Fehlermeldungen beschreibt
`markdown-dateien/C8205-Interpreter-Python_Interpreter.md`.

## Schnellstart: Modus GRAFIK mit Pult, Schreibwerk-Fenster und Tönen

Neben dem Stapelbetrieb (`c8205_interp.py`, ohne Fenster und ohne Töne) gibt es den Modus GRAFIK: Bedienpult-Fenster,
Schreibwerk-Fenster und alle Töne (Rechner, Schreibwerk, Lochstreifenleser, Lochbandstanzer).

```
python3 c8205_grafik.py                    # mit Tönen (Linux: braucht paplay, pw-cat, aplay oder ffplay)
python3 c8205_grafik.py --STUMM            # ohne Töne und ohne Hochlaufwartezeit
python3 c8205_grafik.py --TON=5955         # Lautstärke je Gruppe: Pult SW LL LS (0 = stumm, 5 = Voreinstellung 5555)
python3 c8205_grafik.py --leser1 Test-virtuelleGeraete/Leser1_02/lb_kopie_quelle.txt --stanzer1 virtuelle_Geraete/Stanzer1/lb_kopie_ausgabe.txt
```

- Schreibwerk: **82,5 ms Schreibwerkzeit je Zeichen (75 bis 90 ms), Zeichenklang 100 ms**, Tabulator 400 ms, Wagenrücklauf mit Zeilenschaltung (WRZL) 360 ms, Wagenrücklauf ohne Zeilenschaltung (WR) 120 ms (erste Hälfte des WRZL-Klangs).
  Bei eingerastetem Selektor SW gibt es keine Ausgabe, keinen Ton und kein Warten.
- Stanzer: ungefähr 50 Zeichen je Sekunde; Dauerstanzen unter 50 ms Abstand, nach 5 s ohne Zeichen aus.
- Fehlt ein Abspielprogramm, endet der Start ohne `--STUMM` mit Rückkehrcode 16.
- Der Mischer ist das C-Modul `c-module/tonmisch.c` (in das Erweiterungsmodul `c8205_trommel` eingebunden; bauen mit
  `cd c-module/python && python3 setup.py build_ext --inplace`). Ohne gebautes Modul läuft der Python-Mischer.
- **Stand:** Unter Linux sind die Logiktests und die Hörprüfung (19.10.2026) durchgeführt; unter Windows ist das C-Modul mit MinGW-w64 gebaut (26.10.2026), die Haupttrommel getestet und der Mischer (`winmm`) eingeschaltet (Grundgeräusch, Lochbandleser, Stanzer gehört); Schreibwerkton, Dauerbetrieb, Pult-Fenster und andere Python-Versionen sind nicht geprüft. Einzelheiten und offene Punkte: `markdown-dateien/C8205-Interpreter-GRAFIK_Beschreibung.md` (Beschreibung) und `markdown-dateien/C8205-Interpreter-GRAFIK_Pruefverfahren.md` (Prüfung, Handlisten).
- Der Ton-Testrahmen `ton/sw_ton.py` bleibt als selbständiges Programm für die Klänge (`ton/SW_Ton_Beschreibung.md`).

Beispiel Lochband kopieren: `Assembler/Projekt_1/sw_eingabe/k1_leser_stanzer.asm` liest von Leser 1 (`ANWAHL LSL1`) und stanzt auf
Stanzer 1 (`ANWAHL LSS1`); `:` in KB (Code 15) beendet die Eingabe und wird nicht gestanzt. Test im Stapelbetrieb:
`python3 c8205_interp.py --MODUS=TEST Tests/k1_leser_stanzer.test`.

## Zusatztrommeln (experimenteller Prototyp C8205Z)

Der **experimentelle Prototyp C8205Z** (Ordner `C8205Z/`) fügt dem Simulator vier Zusatztrommeln ZT1 bis ZT4 hinzu. Er wirkt nur mit dem Schalter `--C8205Z[=VERZ]`; ohne den Schalter ist alles unverändert.

```
python3 c8205_interp.py --MODUS=TEST --C8205Z C8205Z/Tests_Z/zt-001_hin_zurueck.test   # Stapelbetrieb, Zeit 0
./c8205_grafik.sh --C8205Z                      # GRAFIK, Befehl 601/661 dauert rund 81 bis 86 ms
./c8205_grafik.sh --HWCHECK --C8205Z            # zusammen mit dem HW-Check-Fenster
```

- Befehle: `5k00 030` wählt die Zusatztrommel k (1 bis 4; 5100 = Trommel 0 bis 5400 = Trommel 3), `zzz0 bbbb 601` gibt eine Haupttrommelspur auf die Zusatztrommel aus, `zzz0 bbbb 661` liest sie zurück (je ganze Spur, 32 Worte). Die Trommeln liegen als `zt1.txt` bis `zt4.txt` in `Trommel/ZT/`.
- Für GRAFIK einmal das Erweiterungsmodul bauen: `cd C8205Z/zt_modul/python && python3 setup.py build_ext --inplace` (das C-Modul selbst prüft `cd C8205Z/zt_modul && make test`).
- Tests: `bash C8205Z/Tests_Z/zt_tests.sh` und `bash C8205Z/Tests_Z/zt_grafik_tests.sh` (TEST gegen GRAFIK).
- Einzelheiten: `C8205Z/zt/Zusatztrommel_Zeitmodell.md`, `markdown-dateien/C8205-Interpreter-GRAFIK_Beschreibung.md` §7.10.

## Schnellstart: Claude-Interpreter (ohne Python)

Ein Test lässt sich auch ohne Python ausführen: Eine KI arbeitet den Knotengraphen von Hand ab. Dazu lädt man das
Regelwerk (`markdown-dateien/`, ohne `Python_Interpreter`, `PDF`, `Projektstruktur`, `Projektueberblick`, `Versionierung` und die
Assembler-Dokumentation) und die Testdatei hoch und gibt eine Startanweisung. Die Schritte, die Dateiauswahl und einen
Vorschlag für die Startanweisung beschreibt `markdown-dateien/C8205-Interpreter-Durchführung_eines_Tests.md`,
Abschnitt 1b (als PDF: `PDF/C8205-Testhandbuch_A4.pdf`, „Kurzanleitung: Test starten“).

## Schnellstart: Assembler

Der Assembler läuft unter Linux und Windows 10; mitgeliefert sind das Linux-Binary (`Assembler/_Linux/`) und das Windows-Binary
(`Assembler/_Windows/c82ass.exe`); Selbstbau: s. u. Aufruf unter Linux, **aus dem Ordner `Assembler/`**:

```
cd Assembler
./c82ass.sh -p Projekt_1/bsp_5.16 -s bsp_5_16
```

Alle `.asm`-Dateien unterhalb eines Ordners auf einmal assemblieren (nur Fehler werden gemeldet; Rückgabewert 0 =
alles fehlerfrei, 1 = Fehler):

```
Assembler/asm_alle.sh [Basisverzeichnis]   # Vorgabe: Assembler/; darf von überall gestartet werden
```

Zum Selbstbauen aus dem Quellcode: `Assembler/make_c82ass.sh` (Linux) bzw. `Assembler/make_c82ass.bat`
(Windows, MinGW-w64).

Der Assembler erzeugt unter anderem den Objektcode (`.obj`, ein binär codierter R300-Lochstreifen, unmittelbar in den Lochbandleser legbar), eine Speicherbelegung (`.dmp`) und eine `.test`-Datei.
Diese enthält die Trommeldatei im Testformat des Interpreters und lässt sich nach Ergänzung der Testmarken und der
Tastenfolge als Testauftrag in `Tests/` verwenden. Sprache, Anweisungen und Makros stehen in
`Assembler/Dokumentation/` (die `.odt` ist maßgeblich).

## Wo anfangen zu lesen?

**KI-Sitzung (Claude) oder schneller Einstieg ins Programmieren?** `CLAUDE.md` in der Wurzel lesen (kurz: Schnellstart, Fallen, Skripte, welche Datei wofür), danach gezielt `C8205-Programmierhandbuch_fuer_Claude.md`.

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
| `C8205-GRAFIK_Beschreibung_A4.pdf` | Der GRAFIK-Interpreter: Zweck, Fenster, Geräte, Töne, Aufruf, Grenzen (Wortlaut der Quelle) |
| `C8205-GRAFIK_Pruefverfahren_A4.pdf` | Prüfverfahren des GRAFIK-Interpreters: Läufe, Tests, Abnahme |
| `C8205-Knotengraph_A4.pdf` | Der Knotengraph als Diagramm, auf A4-Kacheln aufgeteilt |
| `C8205-Knotentabellen_A4.pdf` | Knotentabelle und Variablentabelle T2 im Wortlaut der Quellen |
| `C8205-Einzelbefehlsliste_A4.pdf` | Generische Befehlsbeschreibung und Übersicht aller 512 Operationscodes |
| `C8205-Kodetabellen_A4.pdf` | Zeichenkodetabelle (R 300-Lochstreifenkode) |
| `C8205-Einstieg_fuer_Neueinsteiger_A4.pdf` | Orientierung für neue Leser: Inhalt des Projekts, Lesereihenfolge |
| `C8205-Lochstreifen-Hilfsprogramme_A4.pdf` | Die Lochstreifen-Hilfsprogramme in `Hilfsprogramme/` |
| `C8205-Projektstruktur_A4.pdf` | Verzeichnisstruktur des Gesamtprojekts |
| `C8205-PDF_Gestaltungsrichtlinie_A4.pdf` | Gestaltungsrichtlinie für alle PDF-Ausgaben |
| `Testausfuehrungen/C8205-Testuebersicht_A4.pdf` | Übersicht aller Tests |
| `Bausteininterpretiersystem BIS/markdown-dateien/C8205-BIS_A4.pdf` | Das Bausteininterpretiersystem BIS |
| `Assembler/Dokumentation/C8205-Assemblerdokumentation_A4.pdf` | Assembler `c82ass`: Aufruf, Sprache, Makros, Beispiel |

## Stand

Der Interpreter meldet jede Stelle, bei der das Regelwerk unklar ist oder zu der noch keine Umsetzung vorliegt,
bewusst als **Stub** und bricht mit einer Meldung ab, statt zu raten („laut scheitern“). Das ist gewollt und kein
Fehler. Ob für jeden der 512 Operationscodes eine Umsetzung vorhanden ist, prüft `testscripte/c8205_befehlssweep.py`.

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
