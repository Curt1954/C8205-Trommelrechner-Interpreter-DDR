# Einstieg in das C 8205-Projekt

Version: 0.95-004

**Zweck:** Orientierung für Leser, die das Projekt zum ersten Mal sehen: was es enthält, wie man es startet, in welcher Reihenfolge die Dokumentation zu lesen ist und wo zu einer Frage die Antwort steht. Die technischen Einzelheiten des Rechners stehen in den Fachdokumenten. Wer das Projekt kennt, kann dieses Dokument überspringen. Die README (`README.md`, englisch `README.en.md`) fasst das Projekt auf einer Seite zusammen; dieses Dokument setzt dort an.

## 1. Was ist das Projekt?

Das Projekt rekonstruiert und simuliert den Kleinrechner **Cellatron C 8205** (1968, DDR): eine Einadreßmaschine mit **Magnettrommel** als Speicher (128 Spuren × 32 Sektoren, 4096 Worte zu 33 Bit), bedient über Bedienpult, Lochstreifen und Schreibwerk. Zahlen und Adressen werden oktal geschrieben.

Die historische Befehlsverarbeitung wird nicht vereinfacht nachprogrammiert, sondern möglichst genau nachgebildet. Aus den verfügbaren Unterlagen wurde ein **Regelwerk** rekonstruiert: die Knoten des Befehlsablaufs, ihre Ein- und Ausgänge, die Anweisungen an den Knoten, die Wirkung von Registern und Recheneinheiten und die Einbindung der Peripherie. Der Python-Interpreter führt dieses Regelwerk aus.

```text
historische Unterlagen
        │
        ▼
rekonstruiertes Regelwerk (.md-Dateien in markdown-dateien/)
        │  Knotengraph und Variablentabelle T2 werden bei jedem Start gelesen
        ▼
Python-Interpreter
        │
        ▼
Testlauf → Testprotokoll
```

### 1.1 Das Regelwerk ist ausführbar

Zwei Dateien in `markdown-dateien/` sind Dokumentation und zugleich Eingabe des Interpreters:

| Datei | Inhalt | Wird gelesen als |
|---|---|---|
| `C8205-Interpreter-Eingänge_der_Knoten.md` | Knoten, Typen, Ein- und Ausgänge, Verzweigungen | Knotengraph |
| `C8205-Interpreter-Beschreibung_der_Knoten.md` | Bedeutung jeder ANWEISUNG-nnn | Variablentabelle T2 |

Den Ordner bestimmt der Schalter `--mdverz` (Vorgabe: `markdown-dateien/` neben `c8205_interp.py`). Von Hand als Python-Funktion hinterlegt ist nur die **Wirkung** jeder einzelnen ANWEISUNG. Fehlt eine Funktion, meldet der Interpreter einen **Stub**, statt zu raten. Daraus folgt:

- Eine Änderung an diesen beiden Dateien ändert das Verhalten der Simulation, ohne dass Python-Code geändert wird.
- Die Ursache eines unerwarteten Testergebnisses liegt nicht automatisch im Python-Code (siehe Abschnitt 8).

### 1.2 Zwei Wege: Python-Interpreter und Claude-Interpreter

Dasselbe Testformat lässt sich auf zwei Wegen ausführen. Der **Python-Interpreter** (`c8205_interp.py`) arbeitet den Knotengraphen automatisch und reproduzierbar ab. Beim **Claude-Interpreter** erhält eine KI das komplette Regelwerk und dieselbe Testdatei und arbeitet den Graphen Knoten für Knoten von Hand ab; er dient als unabhängige Gegenprobe. Dieses Dokument behandelt den Python-Interpreter. Zum Claude-Interpreter: `C8205-Interpreter-Projektueberblick.md`, Abschnitt 2, und `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 1b.

## 2. Die Teilbereiche

### 2.1 Interpreter

Der Interpreter liegt im Wurzelverzeichnis: `c8205_interp.py` (Einstieg), Beschreibung in `markdown-dateien/C8205-Interpreter-Python_Interpreter.md`. Er ist **nicht** die historische Software des C 8205, sondern das heutige Simulationswerkzeug für die rekonstruierte Hardware.

Zwei Betriebsarten:

- **TEST**: läuft ohne Fenster und prüft Programme automatisch.
- **GRAFIK** (`c8205_grafik.py`): zeigt Bedienpult und Schreibwerk als Fenster, spielt Töne und bildet die Trommel nach. Beschreibung: `C8205-Interpreter-GRAFIK_Beschreibung.md`.

### 2.2 Assembler

`Assembler/` enthält den in C geschriebenen Assembler `c82ass`. Er übersetzt Assembler-Quelltext (`.asm`) und erzeugt unter anderem:

- eine `.test`-Datei (Testauftrag für den Python-Interpreter),
- eine `.obj`-Datei (binär codierter Lochstreifen mit Objektcode zur Eingabe mit Kennzeichen, Format des Minimalprogramms),
- mit dem Schalter `--ABSPR` statt der `.obj` eine `.kep`-Datei (Lochstreifen für das Kleine Eingabeprogramm, KEP).

```text
Assembler-Quelltext (.asm)
       │
       ▼
     c82ass
       │
       ├── .test ───────► Python-Interpreter (Testauftrag)
       └── .obj / .kep ─► Lochstreifen für Leser, Minimalprogramm bzw. KEP
```

Der Assembler ist ein eigenständiges Teilprojekt. Für den Simulator allein ist seine Dokumentation nicht als Erstes nötig. Einstieg: `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md` (maßgeblich ist die `.odt` im selben Ordner).

### 2.3 Bausteininterpretiersystem BIS

`Bausteininterpretiersystem BIS/` enthält die Dokumentation des historischen BIS: ein Unterprogrammsystem, das auf dem C 8205 selbst abläuft (Eingabe-, Rechen- und Ausgabebausteine, KEP, Minimalprogramm). Das BIS ist **kein Bestandteil des Python-Interpreters**. Wer zunächst die Funktionsweise des simulierten Rechners verstehen will, kann es überspringen.

## 3. Drei Ebenen

Die Dokumentation behandelt drei Ebenen, die nicht verwechselt werden sollen:

| Ebene | Gegenstand |
|---|---|
| A: der historische Rechner | Rechenwerk, Leitwerk, Register, Magnettrommel, Bedienpult, Lochstreifen, Schreibwerk, Befehle |
| B: die Rekonstruktion | wie aus den Unterlagen ein ausführbares Regelwerk entstand: Knotengraph mit Variablentabelle T2 |
| C: die heutige Simulation | Python, Dateien, Testskripte, virtuelle Geräte |

## 4. Ausprobieren

Voraussetzung: Python 3 (geprüft mit 3.11 bis 3.13), keine zusätzlichen Pakete. Ein C-Compiler (`gcc`, `make`) wird nur zum Neubau des Assemblers gebraucht; das fertige Binary liegt in `Assembler/_Linux/c82ass`. Unter Linux vor jedem Aufruf `export LC_ALL=C.UTF-8` setzen (sonst entstehen beim Entpacken falsche Dateinamen mit Umlauten).

**Test ausführen** (aus dem Projektstamm):

```
python3 -I c8205_interp.py --MODUS=TEST Tests/trommel-001_leer.txt
```

Mit Wrapper (im Gesamt-Zip, nicht in der Claude-Variante; Testdatei an beliebiger Stelle der Argumente, Protokoll nach `Test-Protokolle/`): `./c8205_interpreter.sh Tests/trommel-001_leer.txt` (Linux/macOS) bzw. `c8205_interpreter.bat Tests\trommel-001_leer.txt` (Windows).

Erwartet: Ausgabe endet mit `Test wahr`. Rückgabecodes: 0 Test wahr, 4 ohne Prüfung, 6 Test falsch, 8 Laufzeitfehler, 16 formale Prüfung negativ, 2 Aufruf falsch. Das Protokoll liegt unter `Test-Protokolle/<Testname>/protokoll.txt`. Die Trommeldatei `Trommel/trommel.txt` wird bei jedem Lauf verändert; Tests setzen dafür `#TROMMEL=LEER`.

**Alle Tests** (rund 10 Sekunden): `testscripte/compute_all_tests.sh`.

**Assemblieren** (aus dem Ordner `Assembler/`):

```
./c82ass.sh -p Claude/mini -s mini --WARN=ALLE --no-color
```

Rückgabecode 0 bedeutet fehlerfrei. Erzeugt werden `.obj .mqo .sym .dmp .log .test` im Projektordner. Das Skript `Assembler/asm_und_test.sh` assembliert und führt den Test in einem Schritt aus.

**GRAFIK** (aus dem Projektstamm):

```
python3 c8205_grafik.py --STUMM        # Pult- und Schreibwerk-Fenster, ohne Töne
python3 c8205_grafik.py                # mit Tönen (Linux: paplay, pw-cat, aplay oder ffplay nötig)
./c8205_grafik.sh --STUMM              # Wrapper, aus jedem Ordner; Windows: c8205_grafik.bat
```

Alle Schalter und die Geräteordner beschreibt die `README.md` (Schnellstart GRAFIK).

## 5. Begriffe

| Begriff | Bedeutung |
|---|---|
| AC, BZ, AR | Akkumulator (33 Bit), Befehlszähler (12 Bit), Adreßregister (12 Bit); weitere Register und Flags (V1, V2, US, BS, FE …): `C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md` |
| Knoten, Knotengraph | Schritt des Befehlsablaufs und der Graph aller Schritte (rund 80 Knoten); ANWEISUNG-nnn ist eine Operation an einem Knoten |
| Variablentabelle T2 | Zuordnung der ANWEISUNGen zu ihrer Bedeutung |
| Stub | vom Interpreter gemeldete, noch nicht gesicherte Stelle des Regelwerks |
| Testauftrag | Eingabe eines Testlaufs: Trommeldatei (Speicherinhalt, oktal), Tastenfolge als Ausgangszustand (z. B. `H G R`), Testmarken für Diagnoseausgaben, optional Prüfungen mit Sollwerten |
| KEP | Kleines Eingabeprogramm auf Spur 0 (Adressen 0000 bis 0037); verarbeitet nur die Zeichen 0, 1, Punkt, Doppelpunkt und Zwischenraum |
| Minimalprogramm | Grundbaustein des BIS; liest Befehle, Adressen und Konstanten über die Eingabekennzeichen K1 und K2 |
| K1K2 | Kennzeichen am Anfang einer Eingabezeile; bestimmen die Aufbereitung (z. B. 00 absolut, 01 bezogen auf die 1. Leitadresse, 20 Relativadresse setzen) |
| BIS | Bausteininterpretiersystem (Abschnitt 2.3) |

## 6. Empfohlene Lesereihenfolge

Nicht alphabetisch lesen. Alle Dateien außer diesem Dokument liegen in `markdown-dateien/`.

| Schritt | Lesen | Ergebnis |
|---|---|---|
| 1 | dieses Dokument | Überblick über die Teile des Projekts |
| 2 | `C8205-Interpreter-Projektueberblick.md` | Gesamtidee, Verweise auf die Fachdokumente |
| 3 | `C8205-Interpreter-Überblick_und_Gesamtaufbau.md` | technischer Aufbau des C 8205 |
| 4 | `C8205-Projektstruktur.md` | welche Datei wo liegt (Landkarte, kein Lehrbuch) |
| 5 | `C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md` | Register und Datenstrukturen |
| 6 | `C8205-Interpreter-Befehlsliste.md` | Befehle des Rechners |
| 7 | `C8205-Interpreter-Eingänge_der_Knoten.md` und `C8205-Interpreter-Beschreibung_der_Knoten.md` | Kern der Rekonstruktion: vom Maschinenbefehl zum Ablauf |
| 8 | `C8205-Interpreter-Python_Interpreter.md` | Ausführung des Regelwerks in Python |
| 9 | `C8205-Interpreter-Durchführung_eines_Tests.md` | Testläufe nachvollziehen |

Beim ersten Durchgang entbehrlich, als Nachschlagewerk später nötig: `C8205-Interpreter-PDF.md`, `C8205-Versionierung.md` (außer vor Änderungen an Dateien), `C8205-Interpreter-Lochstreifen-Hilfsprogramme.md`, `C8205-Interpreter-Kodetabellen.md`, `C8205-Interpreter-Magnettrommel.md`, `C8205-Interpreter-Lochstreifenleser.md`, `baz-wirkungstabelle.md` (Zwischenspeicher des Claude-Interpreters), die Assembler-Dokumentation und die BIS-Dokumentation. Verweise wie „siehe Datenstruktur und Verarbeitungseinheiten“ führen auf die nächste Ebene; die Dokumentation ist ein Nachschlagewerk mit Querverweisen, kein einzelnes Lehrbuch.

## 7. Wo steht was?

Die vollständige Dokumentenlandkarte steht in `C8205-Interpreter-Projektueberblick.md`, Abschnitt 6. Alle Dateien liegen in `markdown-dateien/`, sofern kein anderer Pfad angegeben ist.

| Frage | Dokument |
|---|---|
| Gesamtprojekt | `C8205-Interpreter-Projektueberblick.md` |
| Aufbau, Ordner (`Tests/`, `Test-Protokolle/`, `Trommel/` …), Skripte | `C8205-Projektstruktur.md` |
| Wie funktioniert der Rechner grundsätzlich? | `C8205-Interpreter-Überblick_und_Gesamtaufbau.md` |
| Register | `C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md` |
| Befehle | `C8205-Interpreter-Befehlsliste.md` |
| Aufbau der Knoten / Eingänge der Knoten | `C8205-Interpreter-Beschreibung_der_Knoten.md` / `C8205-Interpreter-Eingänge_der_Knoten.md` |
| Python-Interpreter | `C8205-Interpreter-Python_Interpreter.md` |
| Claude-Interpreter | `C8205-Interpreter-Projektueberblick.md`, Abschnitt 2 |
| Test ausführen oder schreiben | `C8205-Interpreter-Durchführung_eines_Tests.md` |
| Magnettrommel, Lochstreifenleser, Zeichenkodes | `C8205-Interpreter-Magnettrommel.md`, `C8205-Interpreter-Lochstreifenleser.md`, `C8205-Interpreter-Kodetabellen.md` |
| Lochstreifen-Hilfsprogramme | `C8205-Interpreter-Lochstreifen-Hilfsprogramme.md` |
| Bedienpult | `C8205-Interpreter-Bedienpult_mit_Schaltern.md` |
| GRAFIK-Modus | `C8205-Interpreter-GRAFIK_Beschreibung.md` |
| Laufzeit, Trommelzeit | `C8205-Programmierhandbuch-Anhang_A_Trommelzeit_GRAFIK.md` |
| Assembler | `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md` |
| Assemblerprogramme schreiben (auch mit KI) | `C8205-Programmierhandbuch_fuer_Claude.md` (Wurzelverzeichnis), Karte `CLAUDE.md` |
| BIS, Objektcode | `Bausteininterpretiersystem BIS/markdown-dateien/C8205-Interpreter-BIS.md` und `C8205-Interpreter-Objektdatei_Listing.md` |

Weitere Ordner: `Hilfsprogramme/` (Lochstreifen-Hilfsprogramme), `testscripte/` (Testskripte, Prüfungen), `Testausfuehrungen/` (Skripte `testwahl.sh`, `kep_test.sh`, `interpreter_test.sh`, `bis_test.sh`, Testtabelle). Das Gesamt-Zip enthält zusätzlich PDFs und weitere Dateien, die in der schlanken Claude-Variante (Name endet auf „Claude“) fehlen, darunter die Wrapper-Skripte `c8205_interpreter.sh/.bat` und `c8205_grafik.sh/.bat`; Einzelheiten: Handbuch für Claude, Abschnitt 11.

## 8. Technischer Zusammenhang, Befehle und Tests lesen

```text
C-8205-Programm
      │
      ▼
   Testauftrag (Trommelinhalt, Tastenfolge, …)
      │
      ▼
 Python-Interpreter
      │
      ▼
 Befehlsverarbeitung → Knotengraph (Knoten, Eingänge, Anweisungen, Übergänge)
      │
      ▼
 Register / Speicher / Geräte → Ergebnis
```

Der Knotengraph ist der zentrale Punkt. Der Interpreter führt nicht abstrakt `ADD → AC = AC + Speicher` aus, sondern vollzieht die rekonstruierte Befehlsverarbeitung nach dem Regelwerk nach. Alle Zeiten der echten Hardware (Wortzeit, Wartezeit der Trommel) sind in der Simulation 0; die Reihenfolge der Ereignisse bleibt erhalten. Läufe lassen sich dadurch als Regressionstests wiederholen.

**Einen einzelnen Befehl nachvollziehen:** nicht im Python-Quelltext beginnen, sondern in dieser Reihenfolge: Befehlsliste → Beschreibung des Befehls → relevante Knoten → Knoteneingänge → Register und Datenstrukturen → Python-Implementierung der Anweisungen → Test.

**Fehlersuche bei einem Test:** Reihenfolge der Fragen: Ausgangszustand, Trommelzustand und Registerwerte richtig? Richtiger Befehl geladen? Welcher Knoten wurde zuletzt ausgeführt, welche Anweisung war dort problematisch? War die Regelwerksbeschreibung eindeutig? Erst danach: Fehler im Python-Interpreter. So wird ein Problem nicht vorschnell dem Python-Code zugeschrieben.

Die Teile eines Tests liegen in diesen Ordnern:

| Ordner | Inhalt |
|---|---|
| `Tests/` | Testaufträge (`.test` und `.txt`; der Assembler erzeugt `.test`) |
| `Test-Ergebnisvergleiche/` | Soll-Dateien (Namen meist auf `-ausgabe.txt` oder `_erwartet.txt`), mit denen Tests ihre Ausgabe vergleichen |
| `Test-Protokolle/` | Protokolle der Interpreterläufe; der Ordner entsteht erst beim Lauf und ist im Zip nicht enthalten |
| `Test-virtuelleGeraete/` | virtuelle Geräte des TEST-Interpreters: `Leser1/`, `Leser1_02/`, `Leser2/`, `Stanzer1/`, `SW-Ausgabe/`, `T-SW-Eingabe/` |
| `virtuelle_Geraete/` | virtuelle Geräte des GRAFIK-Interpreters: `Leser1/`, `Leser2/`, `Stanzer1/` |
| `Trommel/` | die gemeinsame Trommel (`trommel.txt`) für TEST und GRAFIK |

## 9. Rekonstruktion und historische Sicherheit

Zu unterscheiden sind: historisch belegt, rekonstruiert, angenommen und technische Implementierung. Ist eine Stelle der Unterlagen nicht eindeutig, darf die Implementierung diese Unsicherheit nicht unbemerkt in einen scheinbar sicheren Fakt verwandeln. Dafür meldet der Interpreter unklare Stellen als offenen Punkt („Stub“), statt sie stillschweigend zu „reparieren“. Für Änderungen und Erweiterungen ist diese Unterscheidung besonders wichtig.

## 10. Einstiegspunkte nach Aufgabe

| Aufgabe | Beginnen mit |
|---|---|
| einen Test ausführen | `C8205-Interpreter-Durchführung_eines_Tests.md`; Assembler- oder BIS-Kenntnisse sind dafür nicht nötig |
| einen Maschinenbefehl verstehen | Vorgehen aus Abschnitt 8 |
| den Python-Interpreter ändern | `C8205-Interpreter-Python_Interpreter.md`, danach die Dokumentation des betroffenen Regelwerks. Das Verhalten des Knotengraphen steht in den beiden Knoten-Dateien (Abschnitt 1.1); in Python liegt nur die Wirkung der einzelnen Anweisungen. |
| einen neuen Test schreiben | `C8205-Interpreter-Durchführung_eines_Tests.md`, danach vorhandene Dateien in `Tests/` |
| Assemblerprogramme schreiben | `Assembler/Dokumentation/`, `C8205-Programmierhandbuch_fuer_Claude.md` und die vorhandenen `.asm`-Beispiele |
| das BIS verstehen | `Bausteininterpretiersystem BIS/`, nicht die Python-Interpreter-Dokumentation |
| eine `.md`-Datei ändern | `C8205-Versionierung.md` lesen. Jede Änderung erhöht den Build (`zzz` in `y.xx-zzz`) um 1; Haupt- und Unterversion erhöht nur der Projektinhaber auf ausdrückliche Aufforderung. |

## 11. Kurzfassung

```text
HISTORISCHER C 8205 → REKONSTRUKTION → REGELWERK → KNOTENGRAPH → PYTHON-INTERPRETER → TESTS
```

Wichtig sind fünf Aussagen:

1. Der C 8205 ist der historische Rechner.
2. Das Regelwerk (die `.md`-Dateien) beschreibt die rekonstruierte Befehlsverarbeitung.
3. Der Knotengraph ist der zentrale Ablauf dieser Befehlsverarbeitung und steht als Datei im Regelwerk.
4. Der Python-Interpreter liest diesen Knotengraphen und führt ihn aus.
5. Tests zeigen, ob die Rekonstruktion und ihre Implementierung wie erwartet funktionieren.

Lesereihenfolge: Projektüberblick → Gesamtaufbau → Projektstruktur → Datenstrukturen → Befehle → Knoten → Interpreter → Tests. Assembler und BIS sind eigene Wege und müssen für das Verständnis des Interpreters nicht gelesen werden.
