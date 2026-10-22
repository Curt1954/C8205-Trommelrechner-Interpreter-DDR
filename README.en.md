# C 8205 – Simulation of a 1968 East German Small Computer

Version: 0.95-003

[Deutsch](README.md) | **English**

This project reconstructs and simulates the instruction processing of the **Cellatron C 8205**, a small
computing automaton built in the GDR (East Germany) in 1968. It consists of two independent tools:

- an **interpreter** (Python) that executes machine code against a rule set reconstructed from original
  documentation, and
- an **assembler** `c82ass` (C) that translates readable assembly source into exactly this machine code.

> **Language:** The documentation is written in German, and the German version is authoritative. This README is
> a translation. File and directory names, technical terms and the contents of the `markdown-dateien/` folder
> are German; key terms are given in English here with the German term in parentheses where useful.

## The machine

The C 8205 is a single-address machine built with little technical effort (about 400 transistors and 2000 diodes
in the central unit). Instead of RAM it uses a **magnetic drum** (*Magnettrommel*; 128 tracks × 32 sectors,
4096 machine words of 33 bits each): access time depends on when the desired location passes under the
read/write head. The machine is operated from a control panel (*Bedienpult*) with keys, switches and lamps.
Programs and data enter and leave through punched tape, a typewriter unit (*Schreibwerk*) and the keyboard.

## How the simulation works

The electronics of the instruction cycle (the four phases of instruction processing) are described as a **node
automaton** with about 80 nodes. The interpreter executes this node graph **to the letter**:

- The graph and the meaning of every instruction are read at run time directly from the rule-set files
  (`markdown-dateien/`), not hard-coded.
- Unclear points are reported as open issues ("stubs") instead of being silently "repaired".
- All timing of the real hardware (word time, drum wait time) is 0 in the simulation. The order of events is
  preserved.

A test run consists of a **drum file** (memory contents, octal), a **key sequence** (initial state, e.g. `H G R`),
**test markers** for diagnostic output, and optional **checks** with expected values. This makes runs repeatable
as regression tests.

## Directories

| Path | Contents |
|---|---|
| `c8205_interp.py` | Python interpreter |
| `c8205_grafik.py`, `c8205_grafik.sh`/`.bat`, `grafik_*.py` | GRAFIK mode: panel window, typewriter window, sounds (mixer, typewriter, reader, punch, computer) |
| `c-module/` | C modules: drum, track lock, interrupt, sound mixer `tonmisch`; extension module in `c-module/python/` |
| `ton/` | sounds (`sw_toene/`, `toene_rechner_stanzer/`, power sounds), test harness `sw_ton.py`, `SW_Ton_Beschreibung.md` |
| `testscripte/` | checks and test scripts, e.g. `grafik_alle_tests.sh`, `grafik_stufe4_tests.py` |
| `Hilfsprogramme/` | helper programs: `c8205_befehlssweep.py` (completeness test over all 512 operation codes; run from the project folder with `--interp c8205_interp.py`, or from `Hilfsprogramme/` with `--interp ../c8205_interp.py`), `c8205_lochstreifen_anzeige.py` (shows a virtual punched tape as plain text in a window), `c8205_lochstreifen_eingabe.py` (creates a virtual punched tape from keyboard input), `c8205_lochstreifen_umwandlung.py` (converts a text file to a binary-coded R300 punched tape and back) |
| `testscripte/` | test scripts; each one changes to the project directory itself and can be started from anywhere: `compute_all_tests.sh` (all test definitions in `Tests/`), `c8205_bis_test.sh` (BIS tests: first loads the minimal program `Tests/pj2-bis_minimalprogramm.test`, then the given test file), `test_bis.sh`, `test2_bis.sh`, `test3_bis.sh` (BIS tests one after another: empty drum, minimal program, then the `pj2-bis_*` tests; each a larger set), `test.sh` (older version of `test_bis.sh`), `erzeuge_leere_trommel.py` (creates the empty drum file `Trommel/trommel.txt`, also resets a used drum) |
| `pult/` | images and manifest of the control-panel window (GRAFIK mode) |
| `make_pdf.sh`, `make_all_pdf.sh` | helpers for generating the PDFs (scripts in the `pdf-layout-scripte/` folders) |
| `markdown-dateien/` | Rule set and project description (.md); the interpreter reads the node graph from here |
| `PDF/` | Readable versions of the documents (A4) |
| `Tests/` | Test orders (mostly `.txt`; the extension is free, the assembler produces `.test`) |
| `Test-Ergebnisvergleiche/` | Expected-result files for file checks (names ending in `-ausgabe.txt` or `_erwartet.txt`) |
| `Test-Protokolle/` | Logs (`.log`) of the runs |
| `Test-virtuelleGeraete/` | Virtual devices of the TEST interpreter (punched tape readers, punch, typewriter unit output, keyboard input) |
| `virtuelle_Geraete/` | Virtual devices of the GRAFIK interpreter (`Leser1/`, `Leser2/`, `Stanzer1/`) |
| `Trommel/` | The drum file `trommel.txt`, shared by both interpreters |
| `CSV/` | Overview table of all tests (`test_tabelle.py` produces `.csv`, `.md`, `.xlsx`; `test_tabelle_csv_anzeigen.sh` opens it in LibreOffice Calc) |
| `Bausteininterpretiersystem BIS/` | Sub-project BIS (documentation only for now) |
| `Assembler/` | Assembler `c82ass` with source code, Linux binary, examples and documentation |

Abridged overview (subfolders of the logs and of the example projects are not listed individually):

```
C8205/
├── c8205_interp.py                 Python interpreter
├── c8205_grafik.py / .sh / .bat    GRAFIK mode (panel window, typewriter window, sounds)
├── grafik-interpreter-module/      Modules of GRAFIK mode (grafik_*.py)
├── c-module/                       C modules (drum, track lock, interrupt, sound mixer)
├── ton/                            Sounds and sound test harness
├── pult/                           Images and manifest of the panel window
├── Hilfsprogramme/                 Instruction sweep (512 operation codes), punched-tape helper programs
├── testscripte/                    Test scripts (compute_all_tests.sh, BIS tests, GRAFIK checks,
│                                   erzeuge_leere_trommel.py)
├── make_pdf.sh, make_all_pdf.sh    PDF generation
├── markdown-dateien/               Rule set and project description (.md)
├── PDF/                            Readable versions (A4)
├── Tests/                          Test orders (.txt or .test)
├── Test-Ergebnisvergleiche/        Expected-result files for file checks
├── Test-Protokolle/                Logs of the runs (.log)
├── CSV/                            Overview table of all tests (test_tabelle.py)
├── Bausteininterpretiersystem BIS/ Sub-project BIS (documentation only for now)
├── Trommel/                        Drum file trommel.txt (shared by TEST and GRAFIK)
├── Test-virtuelleGeraete/          virtual devices of the TEST interpreter
│   ├── Leser1/, Leser1_02/, Leser2/   Punched tape input
│   ├── Stanzer1/                   Punch output
│   ├── SW-Ausgabe/                 Typewriter unit output
│   └── T-SW-Eingabe/               Keyboard / typewriter unit input (channel K0)
├── virtuelle_Geraete/              virtual devices of the GRAFIK interpreter
│   ├── Leser1/, Leser2/            Punched tape input
│   └── Stanzer1/                   Punch output
├── README.md, README.en.md, LICENSE
└── Assembler/
    ├── c82ass.sh                   Run the assembler
    ├── asm_alle.sh                 assemble all .asm files under a folder (reports errors only)
    ├── asm_aufraeumen.sh           delete unneeded files (.log, .mqo, .obj, .sym)
    ├── make_c82ass.sh / .bat       Build the assembler (Linux / Windows)
    ├── Sourcecode/                 C source code and macro file
    ├── _Linux/                     Binary (build it yourself for Windows; _Windows/ currently holds none)
    ├── Dokumentation/              .odt (authoritative), .md, .pdf
    ├── Projekt_1/, Projekt_2/, Proj_FeldSortieren/, Claude/   Project folders (any number, any name)
    └── Claude_bsp_reassemblierung/ Project folders: among others the source code of the tests in Tests/
```


The complete directory description is in `markdown-dateien/C8205-Projektstruktur.md` (German).

## Quick start: interpreter

Python 3 is required. No additional packages are needed.

```
python3 c8205_interp.py --MODUS=TEST Tests/0015-030.txt
```

The test runs the program, prints the characters of the output instructions to the terminal (expected:
`Jahr 1972`) and shows a final line at the end. With wrapper and log file:

```
./c8205_interpreter.sh 0015-030.txt      # Linux/macOS, writes Test-Protokolle/0015-030.log
c8205_interpreter.bat 0015-030.txt       # Windows
```

Run all test definitions in `Tests/` at once:

```
testscripte/compute_all_tests.sh
```

All switches (devices, log depth, file checks) and error messages are described in
`markdown-dateien/C8205-Interpreter-Python_Interpreter.md` (German).

## Quick start: GRAFIK mode with panel, typewriter window and sounds

Besides batch mode (`c8205_interp.py`, no windows, no sound) there is GRAFIK mode: control-panel window, typewriter (SW)
window and all sounds (computer, typewriter, paper-tape reader, tape punch).

```
python3 c8205_grafik.py                    # with sound (Linux: needs paplay, pw-cat, aplay or ffplay)
python3 c8205_grafik.py --STUMM            # no sound, no start-up delay
python3 c8205_grafik.py --TON=5955         # volume per group: panel, SW, reader, punch (0 = mute, 5 = default, i.e. 5555)
python3 c8205_grafik.py --leser1 Test-virtuelleGeraete/Leser1_02/lb_kopie_quelle.txt --stanzer1 virtuelle_Geraete/Stanzer1/lb_kopie_ausgabe.txt
```

- Typewriter: **82.5 ms writing time per character (75 to 90 ms), character sound 100 ms**, tab 400 ms, carriage return with line feed (WRZL) 360 ms, carriage return without line feed (WR) 120 ms (first half of the WRZL sound).
  With the SW selector latched there is no output, no sound and no waiting.
- Punch: about 50 characters per second; continuous punching below 50 ms spacing, off after 5 s without a character.
- Without a playback program, start-up without `--STUMM` ends with return code 16.
- The mixer is the C module `c-module/tonmisch.c` (linked into the extension module `c8205_trommel`; build with
  `cd c-module/python && python3 setup.py build_ext --inplace`). Without the built module the Python mixer is used.
- **Status:** On Linux the logic tests and the listening test (19 Oct 2026) have been done; Windows (`winmm`) is untested. Details and open points (German): `markdown-dateien/C8205-Interpreter-GRAFIK_Beschreibung.md` (description) and `markdown-dateien/C8205-Interpreter-GRAFIK_Pruefverfahren.md` (testing, hand checklists).
- `ton/sw_ton.py` stays as a stand-alone test harness for the sounds (`ton/SW_Ton_Beschreibung.md`, German).

Copy-tape example: `Assembler/Projekt_1/sw_eingabe/k1_leser_stanzer.asm` reads from reader 1 (`ANWAHL LSL1`) and punches to punch 1
(`ANWAHL LSS1`); `:` in KB (code 15) ends the input and is not punched. Batch test: `python3 c8205_interp.py --MODUS=TEST Tests/k1_leser_stanzer.test`.

## Quick start: Claude interpreter (without Python)

A test can also be run without Python: an AI works through the node graph by hand. To do so, upload the rule set
(`markdown-dateien/`, without `Python_Interpreter`, `PDF`, `Projektstruktur`, `Projektueberblick`, `Versionierung` and the assembler
documentation) and the test file, and give a start instruction. The steps, the choice of files and a suggested start
instruction are described in `markdown-dateien/C8205-Interpreter-Durchführung_eines_Tests.md` (German), section 1b
(as a PDF: `PDF/C8205-Testhandbuch_A4.pdf`, "Kurzanleitung: Test starten").

## Quick start: assembler

The assembler runs on Linux and Windows 10; the Linux binary is included (`Assembler/_Linux/`), on Windows you build it
yourself (see below). Call on Linux, **from the `Assembler/` folder**:

```
cd Assembler
./c82ass.sh -p Projekt_1/bsp_5.16 -s bsp_5_16
```

Assemble all `.asm` files below a folder at once (only errors are reported; exit code 0 = no errors,
1 = errors):

```
Assembler/asm_alle.sh [base directory]   # default: Assembler/; can be started from anywhere
```

To build it from the source code: `Assembler/make_c82ass.sh` (Linux) or `Assembler/make_c82ass.bat`
(Windows, MinGW-w64).

Among other files, the assembler produces the object code (`.obj`), a memory listing (`.dmp`) and a `.test` file.
The latter contains the drum file in the interpreter's test format and, once the test markers and the key
sequence have been added, can be used as a test order in `Tests/`. Language, directives and macros are described
in `Assembler/Dokumentation/` (the `.odt` is authoritative; German).

## Where to start reading

**First time here?** Start with `markdown-dateien/C8205-Einstieg_fuer_Neueinsteiger.md` (in German): it explains what
the project contains (interpreter, assembler, BIS), in which order to read the documents, and what can be skipped at
first.

**Already know the project, or want a compact overall overview?** Continue here:

1. `PDF/C8205-Projektueberblick_A4.pdf` or `markdown-dateien/C8205-Interpreter-Projektueberblick.md`: what the
   project is and how the documents relate (including a document map).
2. `markdown-dateien/C8205-Interpreter-Überblick_und_Gesamtaufbau.md`: root of the rule set (device structure,
   the four phases of instruction processing). As a PDF: `PDF/C8205-Rechnerbeschreibung_A4.pdf`.
3. Then by interest: hardware (`Magnettrommel`, `Bedienpult_mit_Schaltern`, `Lochstreifenleser`), control logic
   (`Eingänge_der_Knoten`, `Beschreibung_der_Knoten`, `Befehlsliste`), practice (`Python_Interpreter`,
   `Durchführung_eines_Tests`).

## PDF documents

The `PDF/` folder contains reading versions in A4 format, designed according to the guideline
`markdown-dateien/C8205-Interpreter-PDF.md`. They are not updated automatically from the `.md` files and may
therefore be older than their source (the date is shown in the document). The `.md` files are authoritative.
All PDFs are in German.

| PDF | Contents |
|---|---|
| `C8205-Projektueberblick_A4.pdf` | Overview: goal, architecture, assembler, virtual hardware, test concept, document map |
| `C8205-Rechnerbeschreibung_A4.pdf` | Structure, registers, machine word, magnetic drum, instruction cycle and instruction types |
| `C8205-Bedienpult_und_Peripherie_A4.pdf` | Keys, switches, lamps, channels, punched tape reader, punch, typewriter unit |
| `C8205-Bedienungsanleitung_Interpreter_A4.pdf` | Operating `c8205_interp.py`: call, switches, devices |
| `C8205-Testhandbuch_A4.pdf` | Quick guide "Test starten" (Claude and Python interpreter), writing tests and reading logs |
| `C8205-Durchfuehrung_eines_Tests_A4.pdf` | The test format in the wording of the source |
| `C8205-GRAFIK_Beschreibung_A4.pdf` | The GRAFIK interpreter: purpose, windows, devices, sounds, call, limits (in the wording of the source) |
| `C8205-GRAFIK_Pruefverfahren_A4.pdf` | Test procedure for the GRAFIK interpreter: runs, tests, acceptance |
| `C8205-Knotengraph_A4.pdf` | The node graph as a diagram, split into A4 tiles |
| `C8205-Knotentabellen_A4.pdf` | Node table and variable table T2 in the wording of the sources |
| `C8205-Einzelbefehlsliste_A4.pdf` | Generic instruction description and overview of all 512 operation codes |
| `C8205-Kodetabellen_A4.pdf` | Character code table (R 300 punched tape code) |
| `C8205-Einstieg_fuer_Neueinsteiger_A4.pdf` | Orientation for newcomers: what the project contains, reading order |
| `C8205-Lochstreifen-Hilfsprogramme_A4.pdf` | The punched-tape helper programs in `Hilfsprogramme/` |
| `C8205-Projektstruktur_A4.pdf` | Directory structure of the whole project |
| `C8205-PDF_Gestaltungsrichtlinie_A4.pdf` | Design guideline for all PDF output |
| `CSV/C8205-Testuebersicht_A4.pdf` | Overview of all tests |
| `Bausteininterpretiersystem BIS/markdown-dateien/C8205-BIS_A4.pdf` | The building-block interpreter system BIS |
| `Assembler/Dokumentation/C8205-Assemblerdokumentation_A4.pdf` | Assembler `c82ass`: call, language, macros, example |

## Status

The interpreter deliberately reports every point where the rule set is unclear or where no implementation exists
yet as a **stub** and stops with a message instead of guessing ("fail loudly"). This is intended and not a defect.
`Hilfsprogramme/c8205_befehlssweep.py` checks whether an implementation exists for each of the 512 operation codes.

## Version numbers

Every `.md` file and the interpreter carry their own version number of the form `y.xx-zzz` (major version, minor
version, build); in the documents it is the line `Version:` below the title. The interpreter's number is shown by
`python3 c8205_interp.py --version`. Structure and rules: `markdown-dateien/C8205-Versionierung.md` (German).

**Rule for everyone who contributes (including AI sessions):** every change to one of these files raises its build
(`zzz`) by 1. The major and minor version are raised only when the project owner explicitly asks for it.

## License

MIT License, see [LICENSE](LICENSE). It covers the interpreter, the assembler, the tests and the documents written
for this project. Rights to the original documentation of the C 8205, from which the rule set was reconstructed,
remain with their respective owners.

## Sources and background

The rule set was reconstructed from original documentation of the machine (among others the programming manual and
the original documentation). The documents cite them section by section.
