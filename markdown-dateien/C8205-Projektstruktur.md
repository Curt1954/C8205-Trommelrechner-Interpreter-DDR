** Projektstruktur (Wurzeldokument für die Verzeichnisstruktur) **

Dieses Dokument erläutert die Verzeichnisstruktur des Gesamtprojekts C 8205: welches Verzeichnis welchen
Zweck hat und in welchem Dokument die Einzelheiten stehen. Es wiederholt keine Details aus den
Teildokumenten, sondern verweist nur auf sie (wie "C8205-Interpreter-Überblick_und_Gesamtaufbau.md").
Erzeugte Dateien werden nur nach Endung beschrieben, nicht einzeln aufgezählt.

Das Projekt hat zwei Teilprojekte: den **Interpreter** (Python, Wurzel des Projektverzeichnisses) und den
**Assembler** (C, Unterverzeichnis `Assembler/`).


## 1. Oberste Ebene

| Pfad | Zweck | Maßgebliches Dokument |
|---|---|---|
| `c8205_interp.py` | Python-Interpreter (Knotenautomat) | `C8205-Interpreter-Python_Interpreter.md` |
| `c8205_befehlssweep.py` | Vollständigkeitstest über alle 512 Operationscodes | Kopfkommentar der Datei |
| `c8205_interpreter.sh`, `c8205_interpreter.bat` | Wrapper: starten `c8205_interp.py` für eine Testdatei und schreiben das Protokoll nach `Test-Protokolle/<Testname>.log` | `C8205-Interpreter-Python_Interpreter.md`, Abschnitt 5.2 |
| `markdown-dateien/` | Unterordner mit den .md-Dateien des Projekts (Projektbeschreibung und Regelwerk, Quelle für Interpreter und PDFs): alle `C8205-Interpreter-*.md`-Dateien (darunter `C8205-Interpreter-PDF.md`, die Gestaltungsrichtlinie für alle PDF-Ausgaben), `baz-wirkungstabelle.md` und dieses Dokument (`C8205-Projektstruktur.md`) selbst. Die Rolle jeder Datei steht in der Dokumentenlandkarte von `C8205-Interpreter-Projektueberblick.md` (Abschnitt 6). Nicht hier liegt die Assemblerdokumentation (`Assembler/Dokumentation/`, s. Abschnitt 3). Jede .md-Datei existiert nur einmal. Der Interpreter liest den Ordner über den Schalter `--mdverz` (Vorgabe: `markdown-dateien/` neben `c8205_interp.py`). | Wurzel: `C8205-Interpreter-Überblick_und_Gesamtaufbau.md`; PDF-Richtlinie: `C8205-Interpreter-PDF.md` (selbst) |
| `PDF/` | Erzeugte PDFs (A4), je Dokument eine Datei `C8205-<Inhalt>_A4.pdf`; hier nicht einzeln aufgezählt. Das Assembler-PDF liegt dagegen in `Assembler/Dokumentation/` (s. Abschnitt 3). Außerdem liegt hier das Skript `erzeuge_knoten_pdfs.py`, das `C8205-Knotengraph_A4.pdf` und `C8205-Knotentabellen_A4.pdf` aus den beiden Knoten-.md-Dateien erzeugt. | Liste, Quellen und Namensschema: `C8205-Interpreter-PDF.md`, Abschnitt 8; Skript (Aufruf, Voraussetzungen): Abschnitt 7 |
| `Tests/` | Testaufträge für den Interpreter (`.txt`) | `C8205-Interpreter-Durchführung_eines_Tests.md` |
| `Test-Protokolle/` | Protokolle (`.log`) der Interpreterläufe | `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 8 |
| `virtuelle_Geraete/` | Ablage der virtuellen Geräte für den Interpreter, je Gerät ein Unterordner: `Leser1/`, `Leser2/` (Lochstreifen für Leser 1 und 2), `Stanzer1/` (Ausgabe des Stanzers 1), `SW-Ausgabe/` (Schreibwerk-Ausgabe), `T-SW-Eingabe/` (Eingabe über Tastatur/Schreibwerk, Kanal K0); siehe Abschnitt 2 | Mechanismus: `C8205-Interpreter-Durchführung_eines_Tests.md`, 6.2 und 6.3.2; Schalter: `C8205-Interpreter-Python_Interpreter.md`, 8.2 und 8.3 |
| `Assembler/` | Teilprojekt Assembler | Abschnitt 3; Doku: `Assembler/Dokumentation/C8205_Assembler_Dokumentation.odt` (maßgeblich), `.md` (durchsuchbare Ableitung) und `.pdf` (Export), gleicher Pfad |


## 2. Konventionen für Tests, Protokolle und virtuelle Geräte

- **Testname:** `NNNN-<Operationscodes>.txt` in `Tests/` (z. B. `0004-210_544_020.txt`). Testaufträge aus Assemblerläufen heißen `asm_NNNN_<Programmname>.txt` (z. B. `asm_0001_bsp_5_16.txt`). Das Protokoll trägt
  denselben Namen mit der Endung `.log` in `Test-Protokolle/`. Der Wrapper findet die Testdatei über den Namen.
- **Virtuelle Geräte:** Der Interpreter kennt die Geräte nur über die Schalter `--leser1`, `--leser2`,
  `--stanzer1`, `--sw-ausgabe` und `--k0`. Diese nehmen einen Pfad (Datei oder Ordner) entgegen. Die
  Verzeichnisse `virtuelle_Geraete/Leser1/`, `…/Leser2/`, `…/Stanzer1/`, `…/SW-Ausgabe/` und `…/T-SW-Eingabe/`
  sind die dafür vorgesehene Ablage; **die Wrapper übergeben sie nicht**; die Testdatei darf die Zuordnung aber selbst als Zeile enthalten (`C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2b). Sie wirken nur, wenn der Schalter
  beim Aufruf angegeben wird, z. B. `--leser1 virtuelle_Geraete/Leser1` oder
  `--k0 datei=virtuelle_Geraete/T-SW-Eingabe`.


## 3. Teilprojekt Assembler

Der Assembler `c82ass` übersetzt Assembler-Quelltext (`.asm`) in Objektcode für das "Kleine Eingabeprogramm".
Aufruf, Sprache, Makros und Beispiele stehen in der Assemblerdokumentation; hier nur die Struktur.

| Pfad (unter `Assembler/`) | Zweck |
|---|---|
| `c82ass` | Batch-Datei zum Erzeugen des Assemblers |
| `c82ass.sh` | Ausführen des Assemblers |
| `c82ass.bat` | Windows-Pendant zu `c82ass` (erzeugt `_Windows/c82ass.exe`; kein Wrapper zum Ausführen) |
| `Dokumentation/` | Assemblerdokumentation `C8205_Assembler_Dokumentation`: `.odt` (maßgeblich), `.md` (durchsuchbare Ableitung daraus, kein eigenes Regelwerk), `.pdf` (Export aus der .odt) |
| `Sourcecode/` | C-Quellcode des Assemblers selbst; enthält außerdem die Makrodatei `c82ass.makros` (der Assembler sucht sie unter diesem festen Namen zuerst im Arbeitsverzeichnis des Aufrufs, sonst in `Sourcecode/`; hier liegt sie richtig) |
| `_Linux/`, `_Windows/` | Binaries des Assemblers je Betriebssystem |
| `projekdetails`, `projekdetails.<Projekt>` | Arbeitsdateien: zuletzt benutzte Aufrufparameter, bzw. für ein bestimmtes Projekt gesicherte |
| `Projekt_1/`, `Proj_FeldSortieren/` | Projektverzeichnisse (Beispiele); dürfen beliebig benannt sein und Unterverzeichnisse enthalten |

**Vom Assembler erzeugte Dateien** (im Verzeichnis der `.asm`-Datei, Namensstamm wie die Quelle; der Assembler
löscht `.log`, `.obj`, `.mqo`, `.sym`, `.test` und `.dmp` vor jedem Lauf und erzeugt sie neu):

| Endung | Inhalt |
|---|---|
| `.asm` | Quelltext (Eingabe, keine erzeugte Datei) |
| `.log` | Literaltabelle, Symboltabelle, Tabelle der absoluten Symbole |
| `.obj` | ladefähiger Objektcode (K1K2) |
| `.mqo` | aufbereiteter Quelltext, kombiniert mit dem Maschinencode (Hilfsdatei, Pass 3) |
| `.sym` | Symboldatei (ordnet Symbole zu Trommeladressen zu) |
| `.dmp` | formatierte Speicherbelegung (Listing mit Adresse, Maschinenwort, Label, Mnemonic, Operand, Kommentar); entsteht in Pass 3 |
| `.test` | Trommeldatei im Format des Interpreters (`Adresse: Wert # Quelltextzeile`) mit Platzhalter-Definitionen für Testmarken und Tastenfolge sowie ggf. dem Leerbefehl 164, die für den jeweiligen Fall ergänzt werden müssen; Grundlage für Testaufträge, s. `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2a |


## 4. Offene Punkte

Keine offenen Punkte.

**Erledigt:**

- **Assemblerdokumentation (.odt):** Änderungen (Passbeschreibung, Dateiliste, Streichung `.mqt`/`.l82`, `.dmp`,
  `.test`, Makrodatei, Beispiellauf, Aussage zu `c82ass.bat`) in die `.odt` übernommen. Das `.pdf` wurde daraus neu
  exportiert.
- **Vorhandene `.mac`-Dateien:** vom Projektinhaber entfernt.
- **Ablageort der Makrodatei:** kein Problem. `erzeugeMacroArray` sucht `c82ass.makros` zuerst im Arbeitsverzeichnis und
  weicht auf `Sourcecode/` aus; die Ablage in `Assembler/Sourcecode/` ist damit richtig.
- **`c82ass.sh`/`c82ass.bat`:** geprüft; `.sh` startet nur das Binary, `.bat` erzeugt nur `c82ass.exe`.
- **Endungen `.dmp`, `.mac`, `.test`:** `.dmp` ist die formatierte Speicherbelegung (Pass 3), `.test` die
  Trommeldatei für den Interpreter (Abschnitt 3, Tabelle; ebenso in der Assemblerdokumentation), `.mac` wird nicht
  erzeugt.
- **`.mqt`, `.l82`:** vom aktuellen Assembler nicht mehr erzeugt, in der Assemblerdokumentation gestrichen.
- **`c82load`, `c82dump`, `c82simi`, `C8205Simulator`:** Diese Programme gehören nicht zum Projekt. Die
  Assemblerdokumentation (Abschnitt 1) erwähnt sie nur als Abnehmer von Assemblerdateien.
