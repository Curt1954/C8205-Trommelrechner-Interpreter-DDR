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
| `c8205_interpreter.sh`, `c8205_interpreter.bat` | Wrapper: starten `c8205_interp.py` für eine Testdatei und schreiben das Protokoll nach `Protokolle/<Testname>.log` | `C8205-Interpreter-Python_Interpreter.md`, Abschnitt 5.2 |
| `C8205-Interpreter-*.md`, `baz-wirkungstabelle.md` | Projektbeschreibung und Regelwerk (Quelle für Interpreter und PDFs) | Wurzel: `C8205-Interpreter-Überblick_und_Gesamtaufbau.md` |
| `C8205-Interpreter-PDF.md` | Gestaltungsrichtlinie für alle PDF-Ausgaben | selbst |
| `PDF/` | Aus den .md-Quellen erzeugte PDFs (`C8205-Knotengraph_A4.pdf`, `C8205-Einzelbefehlsliste_A4.pdf`, `C8205-Kodetabellen_A4.pdf`) | Namensschema: PDF-Richtlinie, Abschnitt 8 |
| `Tests/` | Testaufträge für den Interpreter (`.txt`) | `C8205-Interpreter-Durchführung_eines_Tests.md` |
| `Protokolle/` | Protokolle (`.log`) der Interpreterläufe | `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 8 |
| `Leser1/`, `Leser2/`, `Stanzer1/` | Ablage der virtuellen Geräte für den Interpreter (Lochstreifen für Leser 1 und 2, Ausgabe des Stanzers 1); siehe Abschnitt 2 | Mechanismus: `C8205-Interpreter-Durchführung_eines_Tests.md`, 6.2 und 6.3.2; Schalter: `C8205-Interpreter-Python_Interpreter.md`, 8.2 und 8.3 |
| `Assembler/` | Teilprojekt Assembler | Abschnitt 3; Doku: `Assembler/Dokumentation/C8205_Assembler_Dokumentation.odt` (maßgeblich), `.md` (durchsuchbare Ableitung, gleicher Pfad) |


## 2. Konventionen für Tests, Protokolle und virtuelle Geräte

- **Testname:** `NNNN-<Operationscodes>.txt` in `Tests/` (z. B. `0004-210_544_020.txt`). Testaufträge aus Assemblerläufen heißen `asm_NNNN_<Programmname>.txt` (z. B. `asm_0001_bsp_5_16.txt`). Das Protokoll trägt
  denselben Namen mit der Endung `.log` in `Protokolle/`. Der Wrapper findet die Testdatei über den Namen.
- **Virtuelle Geräte:** Der Interpreter kennt die Geräte nur über die Schalter `--leser1`, `--leser2` und
  `--stanzer1`. Diese nehmen einen Pfad (Datei oder Ordner) entgegen. Die Verzeichnisse `Leser1/`, `Leser2/`
  und `Stanzer1/` sind die dafür vorgesehene Ablage; **die Wrapper übergeben sie nicht**. Sie wirken nur,
  wenn der Schalter beim Aufruf angegeben wird, z. B. `--leser1 Leser1`.


## 3. Teilprojekt Assembler

Der Assembler `c82ass` übersetzt Assembler-Quelltext (`.asm`) in Objektcode für das "Kleine Eingabeprogramm".
Aufruf, Sprache, Makros und Beispiele stehen in der Assemblerdokumentation; hier nur die Struktur.

| Pfad (unter `Assembler/`) | Zweck |
|---|---|
| `c82ass` | Batch-Datei zum Erzeugen des Assemblers |
| `c82ass.sh` | Ausführen des Assemblers |
| `Dokumentation/` | Assemblerdokumentation: `.odt` (maßgeblich), `.md` (durchsuchbare Ableitung daraus, kein eigenes Regelwerk) |
| `Sourcecode/` | C-Quellcode des Assemblers selbst |
| `_Linux/`, `_Windows/` | Binaries des Assemblers je Betriebssystem |
| `projekdetails`, `projekdetails.<Projekt>` | Arbeitsdateien: zuletzt benutzte Aufrufparameter, bzw. für ein bestimmtes Projekt gesicherte |
| `Projekt_1/`, `Proj_FeldSortieren/` | Projektverzeichnisse (Beispiele); dürfen beliebig benannt sein und Unterverzeichnisse enthalten |

**Vom Assembler erzeugte Dateien** (im Verzeichnis der `.asm`-Datei, Namensstamm wie die Quelle):

| Endung | Inhalt |
|---|---|
| `.asm` | Quelltext (Eingabe, keine erzeugte Datei) |
| `.log` | Literaltabelle, Symboltabelle, Tabelle der absoluten Symbole |
| `.obj` | ladefähiger Objektcode (K1K2) |
| `.mqo` | aufbereiteter Quelltext, kombiniert mit dem Maschinencode |
| `.sym` | Symboldatei (ordnet Symbole zu Trommeladressen zu) |
| `.dmp` | erzeugt beim Assemblieren; Zweck in der Assemblerdokumentation nicht beschrieben |
| `.mac` | erzeugt beim Assemblieren (nur bei manchen Quelltexten beobachtet); Zweck nicht beschrieben |
| `.test` | Trommeldatei im Format des Interpreters (`Adresse: Wert # Quelltextzeile`); Grundlage für Testaufträge, s. `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2a |


## 4. Offene Punkte

- **Endungen `.dmp`, `.mac`:** Zweck und erzeugende Bedingung klären und in Abschnitt 3 sowie in der
  Assemblerdokumentation nachtragen; dort auch `.test` (Zweck: Abschnitt 3, Tabelle) ergänzen.
- **Assemblerdokumentation nennt `.mqt` und `.l82`:** In den vorhandenen Projektverzeichnissen entstehen diese
  Endungen nicht. Prüfen, ob sie entfallen sind (dann in der Dokumentation streichen) oder nur bei bestimmten
  Läufen entstehen.
- **`c82load`, `c82dump`, `c82simi`, `C8205Simulator`:** In der Assemblerdokumentation erwähnt, im Projektbaum
  nicht vorhanden.
