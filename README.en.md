# C 8205 – Simulation of a 1968 East German Small Computer

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
| `c8205_befehlssweep.py` | Completeness test over all 512 operation codes |
| `c8205_interpreter.sh`, `c8205_interpreter.bat` | Wrappers: run a test and write the log to `Test-Protokolle/` |
| `markdown-dateien/` | Rule set and project description (.md); the interpreter reads the node graph from here |
| `PDF/` | Readable versions of the documents (A4) |
| `Tests/` | Test orders (`.txt`) |
| `Test-Protokolle/` | Logs (`.log`) of the runs |
| `virtuelle_Geraete/` | Storage for virtual devices (punched tape reader, punch, typewriter unit, keyboard input) |
| `Assembler/` | Assembler `c82ass` with source code, binaries, examples and documentation |

Abridged overview (subfolders of the logs and of the example projects are not listed individually):

```
C8205/
├── c8205_interp.py                 Python interpreter
├── c8205_befehlssweep.py           Completeness test (512 operation codes)
├── c8205_interpreter.sh / .bat     Wrappers with log file
├── markdown-dateien/               Rule set and project description (.md)
├── PDF/                            Readable versions (A4)
├── Tests/                          Test orders (.txt)
├── Test-Protokolle/                Logs of the runs (.log)
├── virtuelle_Geraete/
│   ├── Leser1/, Leser2/            Punched tape input
│   ├── Stanzer1/                   Punch output
│   ├── SW-Ausgabe/                 Typewriter unit output
│   └── T-SW-Eingabe/               Keyboard / typewriter unit input (channel K0)
└── Assembler/
    ├── Sourcecode/                 C source code and macro file
    ├── _Linux/, _Windows/          Binaries
    ├── Dokumentation/              .odt (authoritative), .md, .pdf
    ├── Projekt_1/, Proj_FeldSortieren/   Example projects
    └── Claude_bsp_reassemblierung/ many example and test projects, one folder each
```

<!-- Please check: the line on Claude_bsp_reassemblierung is a cautious description. The folder
     Assembler/Claude is deliberately not listed. Both are still missing from C8205-Projektstruktur.md. -->

The complete directory description is in `markdown-dateien/C8205-Projektstruktur.md` (German).

## Quick start: interpreter

Python 3 is required. No additional packages are needed.

```
python3 c8205_interp.py Tests/0015-030.txt
```

The test runs the program, prints the characters of the output instructions to the terminal (expected:
`Jahr 1972`) and shows a final line at the end. With wrapper and log file:

```
./c8205_interpreter.sh 0015-030.txt      # Linux/macOS, writes Test-Protokolle/0015-030.log
c8205_interpreter.bat 0015-030.txt       # Windows
```

All switches (devices, log depth, file checks) and error messages are described in
`markdown-dateien/C8205-Interpreter-Python_Interpreter.md` (German).

## Quick start: assembler

The assembler runs on Linux and Windows 10. Call on Linux:

```
Assembler/c82ass.sh -p Projekt_1 -s bsp_5_16
```

Among other files, the assembler produces the object code (`.obj`), a memory listing (`.dmp`) and a `.test` file.
The latter contains the drum file in the interpreter's test format and, once the test markers and the key
sequence have been added, can be used as a test order in `Tests/`. Language, directives and macros are described
in `Assembler/Dokumentation/` (the `.odt` is authoritative; German).

## Where to start reading

1. `PDF/C8205-Projektueberblick_A4.pdf` or `markdown-dateien/C8205-Interpreter-Projektueberblick.md`: what the
   project is and how the documents relate (including a document map).
2. `markdown-dateien/C8205-Interpreter-Überblick_und_Gesamtaufbau.md`: root of the rule set (device structure,
   the four phases of instruction processing).
3. Then by interest: hardware (`Magnettrommel`, `Bedienpult_mit_Schaltern`, `Lochstreifenleser`), control logic
   (`Eingänge_der_Knoten`, `Beschreibung_der_Knoten`, `Befehlsliste`), practice (`Python_Interpreter`,
   `Durchführung_eines_Tests`).

The PDFs are finished reading versions and are not updated automatically. The `.md` files are authoritative.

## Status

<!-- Please check and update: the project overview describes the Python interpreter as not yet complete and
     stub-free, and its section 8 "Stand und offene Punkte" (status and open issues) is empty. -->
The project is under development. The interpreter reports instructions that are not yet implemented as stubs.
`c8205_befehlssweep.py` checks over all 512 operation codes whether everything is in place for each instruction.

## License

<!-- To be decided. -->
Not yet specified.

## Sources and background

The rule set was reconstructed from original documentation of the machine (among others the programming manual and
the original documentation). The documents cite them section by section.
