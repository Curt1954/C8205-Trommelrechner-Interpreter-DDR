# C 8205 – Simulation eines DDR-Kleinrechners von 1968

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
| `markdown-dateien/` | Regelwerk und Projektbeschreibung (.md); der Interpreter liest den Knotengraphen von hier |
| `PDF/` | Lesefassungen der Dokumente (A4) |
| `Tests/` | Testaufträge (`.txt`) |
| `Test-Protokolle/` | Protokolle (`.log`) der Läufe |
| `virtuelle_Geraete/` | Ablage für virtuelle Geräte (Lochstreifenleser, Stanzer, Schreibwerk, Tastatureingabe) |
| `Assembler/` | Assembler `c82ass` mit Quellcode, Binaries, Beispielen und Dokumentation |

Verkürzte Übersicht (Unterordner der Protokolle und der Beispielprojekte sind nicht einzeln aufgeführt):

```
C8205/
├── c8205_interp.py                 Python-Interpreter
├── c8205_befehlssweep.py           Vollständigkeitstest (512 Operationscodes)
├── c8205_interpreter.sh / .bat     Wrapper mit Protokolldatei
├── markdown-dateien/               Regelwerk und Projektbeschreibung (.md)
├── PDF/                            Lesefassungen (A4)
├── Tests/                          Testaufträge (.txt)
├── Test-Protokolle/                Protokolle der Läufe (.log)
├── virtuelle_Geraete/
│   ├── Leser1/, Leser2/            Lochstreifen-Eingabe
│   ├── Stanzer1/                   Stanzer-Ausgabe
│   ├── SW-Ausgabe/                 Schreibwerk-Ausgabe
│   └── T-SW-Eingabe/               Tastatur-/Schreibwerk-Eingabe (Kanal K0)
└── Assembler/
    ├── Sourcecode/                 C-Quellcode und Makrodatei
    ├── _Linux/, _Windows/          Binaries
    ├── Dokumentation/              .odt (maßgeblich), .md, .pdf
    ├── Projekt_1/, Proj_FeldSortieren/   Beispielprojekte
    └── Claude_bsp_reassemblierung/ viele Beispiel- und Testprojekte, je ein Ordner
```

<!-- Bitte prüfen: Die Zeile zu Claude_bsp_reassemblierung ist eine vorsichtige Beschreibung. Der Ordner
     Assembler/Claude ist bewusst nicht aufgeführt. Beide fehlen noch in C8205-Projektstruktur.md. -->

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

Alle Schalter (Geräte, Protokolltiefe, Dateiprüfungen) und Fehlermeldungen beschreibt
`markdown-dateien/C8205-Interpreter-Python_Interpreter.md`.

## Schnellstart: Assembler

Der Assembler läuft unter Linux und Windows 10. Aufruf unter Linux:

```
Assembler/c82ass.sh -p Projekt_1 -s bsp_5_16
```

Der Assembler erzeugt unter anderem den Objektcode (`.obj`), eine Speicherbelegung (`.dmp`) und eine `.test`-Datei.
Diese enthält die Trommeldatei im Testformat des Interpreters und lässt sich nach Ergänzung der Testmarken und der
Tastenfolge als Testauftrag in `Tests/` verwenden. Sprache, Anweisungen und Makros stehen in
`Assembler/Dokumentation/` (die `.odt` ist maßgeblich).

## Wo anfangen zu lesen?

1. `PDF/C8205-Projektueberblick_A4.pdf` bzw. `markdown-dateien/C8205-Interpreter-Projektueberblick.md`: was das
   Projekt ist und wie die Dokumente zusammenhängen (mit Dokumentenlandkarte).
2. `markdown-dateien/C8205-Interpreter-Überblick_und_Gesamtaufbau.md`: Wurzel des Regelwerks (Geräteaufbau, die vier
   Phasen der Befehlsabarbeitung).
3. Danach nach Interesse: Hardware (`Magnettrommel`, `Bedienpult_mit_Schaltern`, `Lochstreifenleser`), Ablauflogik
   (`Eingänge_der_Knoten`, `Beschreibung_der_Knoten`, `Befehlsliste`), Praxis (`Python_Interpreter`,
   `Durchführung_eines_Tests`).

Die PDFs sind fertige Lesefassungen und werden nicht automatisch nachgeführt. Maßgeblich sind die `.md`-Dateien.

## Stand

<!-- Bitte prüfen und aktualisieren: Der Projektüberblick nennt den Python-Interpreter als noch nicht vollständig
     und stubfrei und hat bei "Stand und offene Punkte" (Abschnitt 8) keinen Inhalt. -->
Das Projekt ist in Entwicklung. Der Interpreter meldet noch nicht umgesetzte Anweisungen als Stub. Ob für einen
Befehl alles vorhanden ist, prüft `c8205_befehlssweep.py` über alle 512 Operationscodes.

## Lizenz

<!-- Noch festzulegen. -->
Noch nicht festgelegt.

## Quellen und Hintergrund

Das Regelwerk wurde aus Originalunterlagen des Rechners (u. a. Programmieranleitung und Originaldokumentation)
rekonstruiert. Die Dokumente zitieren sie abschnittsweise.
