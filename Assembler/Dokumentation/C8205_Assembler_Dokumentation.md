** Assemblerdokumentation (durchsuchbare Ableitung) **

Diese Datei ist eine Textableitung von `C8205_Assembler_Dokumentation.odt` (per `extract-text`), gedacht
zum Durchsuchen und Zitieren. **Maßgeblich bleibt die .odt** (siehe `C8205-Projektstruktur.md`,
Abschnitte 1 und 3); bei Widersprüchen gilt die .odt. Diese Ableitung wird nicht automatisch
aktualisiert, wenn die .odt sich ändert.

Stand 09.10.2026: Die Abschnitte 1 bis 5 dieser Ableitung wurden an das tatsächliche Verhalten des Assemblers `c82ass`
(Version 0.2, einschließlich der in Abschnitt 6.3 beschriebenen Korrekturen im Quellcode) angepasst. Was gegenüber der
.odt geändert wurde und warum, steht in Abschnitt 6 am Ende dieser Datei. Die .odt wurde am 09.10.2026 entsprechend angepasst.

Hinweis zur Nummerierung: Die Original-Gliederung springt nach Abschnitt "3.2 Sprachdefinition" erneut
bei "3." ein (Abschnitt "Assembleranweisungen"), obwohl bereits eine übergeordnete Ebene "3. Der
Assembler c82ass" existiert. Das ist keine Übertragungsfehler dieser Ableitung, sondern so in der Quelle
vorgefunden und hier unverändert übernommen (analog zur Praxis in `C8205-Projektstruktur.md`, Abschnitt 4,
Unstimmigkeiten zu vermerken statt sie eigenmächtig zu bereinigen).


# Cross-Assembler für C8205 / C8205Z – Version 0.03-001

Die gesamte Software läuft sowohl unter Linux als auch Windows 10. Sie ist in C (gcc) programmiert; die
grafische Oberfläche benutzt node.js.


## 1. Installation

Zum Zweck der Installation ist die Datei `C8205.zip` in einem geeigneten Verzeichnis zu entpacken. Beim
Entpacken wird ein Unterverzeichnis angelegt, in dem sich sowohl Windows- als auch Linux-Binaries
befinden.

### 1.1 Verzeichnisstruktur

Der Assembler liegt im Unterverzeichnis `Assembler` des Gesamtprojekts C8205. Struktur (Beispielprojekte
gekürzt), Ausgabe von `ls -1R`:

```
./Assembler:
c82ass.sh                      # Ausführen des Assemblers
asm_alle.sh                    # assembliert alle .asm-Dateien unterhalb eines Verzeichnisses (meldet nur Fehler)
asm_aufraeumen.sh              # entfernt .log, .mqo, .obj und .sym (Trockenlauf; --loeschen löscht)
Dokumentation                  # diese Dokumentation
_Linux                         # Linux-Binary des Assemblers
make_c82ass.bat                # Batch-Datei zum Erzeugen des Assemblers unter Windows (Pendant zu make_c82ass.sh)
make_c82ass.sh                 # Skript zum Erzeugen des Assemblers unter Linux
projekdetails                  # zuletzt benutzte Aufrufparameter
projekdetails.<Projekt>        # gesicherte Aufrufparameter je Projekt (`/` im Projektnamen wird zu `_`)
Projekt_1                      # Projektverzeichnis (Beispiel, mit Unterverzeichnissen)
Proj_FeldSortieren             # Projektverzeichnis (Beispiel, ohne Unterverzeichnisse)
Projekt_2                      # Projektverzeichnis (Beispiel, ohne Unterverzeichnisse)
Claude                         # weitere Beispielprojekte (ohne Unterverzeichnisse)
Claude_bsp_reassemblierung     # weitere Beispielprojekte, je Programm ein Unterverzeichnis
Sourcecode                     # C-Quellcode des Assemblers selbst
_Windows                       # Windows-Binary des Assemblers

./Assembler/Dokumentation:
C8205_Assembler_Dokumentation.md   C8205_Assembler_Dokumentation.odt   C8205_Assembler_Dokumentation.pdf

./Assembler/_Linux:
c82ass

./Assembler/Projekt_1:
bsp_5.15
bsp_5.16
bsp_seite_39
bsp_seite_40
bsp_seite_42
deepseek-test
dt_test
ziffern

./Assembler/Projekt_1/bsp_5.16:
bsp_5_16.asm  bsp_5_16.dmp  bsp_5_16.log  bsp_5_16.mqo  bsp_5_16.obj  bsp_5_16.sym  bsp_5_16.test

./Assembler/Proj_FeldSortieren:
code.asm  code_wdhl_bef.asm  code.log  code.mqo  code.obj  code.sym  code.test

./Assembler/Sourcecode:
c8205_op_codes.c  c82_austausch.c  c82_austausch.h  ca82ass.c
ca82_protokoll.c  ca82_protokoll.h  ca82_standards.c  ca82_standards.h
c82ass.makros

./Assembler/_Windows:
```

Projektverzeichnisse können beliebig benannt sein, auch Unterverzeichnisse enthalten. In ihnen steht der
Quelltext, die erzeugte Objektdatei (die K1K2-ladefähige Textdatei) und weitere Hilfsdateien. Die
Programme `c82ass`, `c82load`, `c82dump`, `c82simi` erwarten ihre Dateien immer in einem
Projektunterverzeichnis, das im gleichen Pfad wie sie selbst liegen muss.

In der vorliegenden Projektstruktur ist nur `c82ass` enthalten. Die Programme `c82load`, `c82dump`, `c82simi`
und der `C8205Simulator` sind nicht Teil dieses Projekts und liegen nicht bei; sie werden in dieser Dokumentation
nur erwähnt, weil `c82ass` Dateien für sie erzeugt (`.mqo` und `.obj` für `c82load`, `.mqo` für `c82simi`, `.sym`
für `c82dump`). Für die Prüfung von Assemblerergebnissen im Interpreter dient stattdessen die Datei `.test`
(s. `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2a).

`make_c82ass.sh` ist ein Shell-Script zum Erzeugen des Assemblers. Die Datei `make_c82ass.bat` leistet das Gleiche für den
MinGW-w64-Crosscompiler unter Windows. Der Pfad `_Linux` enthält alle Linux-Binaries und Libraries, der
Pfad `_Windows` die Pendants für Windows 10. `Sourcecode` enthält ausschließlich den C-Quellcode.

`asm_alle.sh [Basisverzeichnis]` assembliert alle `.asm`-Dateien unterhalb eines Verzeichnisses (Vorgabe: `./`) mit `c82ass.sh`. Bei fehlerfreiem Lauf erscheint keine Meldung; bei einem Fehler wird die Datei mit den Fehlerzeilen des Assemblers gemeldet. Rückgabewert: 0 = alles fehlerfrei, 1 = Fehler. `asm_aufraeumen.sh` entfernt die erzeugten Dateien `.log`, `.mqo`, `.obj` und `.sym` unterhalb von `Assembler` (nicht in `Dokumentation`, `Sourcecode`, `_Linux`, `_Windows`); ohne Parameter wird nur angezeigt, was gelöscht würde (Trockenlauf), mit `--loeschen` wird tatsächlich gelöscht. Beide Skripte gehören in das Verzeichnis `Assembler`.


## 2. Überblick

Sowohl das Programm `c82ass.sh` (Linux) als auch das Windows-Binary `_Windows\c82ass.exe` (die Datei `make_c82ass.bat` erzeugt es nur) werden über Aufrufparameter versorgt.
Bei jedem Start eines der Programme werden die jeweils letztbenutzten Parameter automatisch in der Datei
`projekdetails` abgelegt, sodass ein Folgestart ohne Angabe von Parametern gelingt. Zur Änderung müssen
die Parameter einfach mit veränderten Werten wieder angegeben werden.

```
$ c82ass.sh -h
C8205 Assembler C82aas Version 0.2
Usage: ./_Linux/c82ass -p Projektverzeichnis -s Quellcode-Datei
```

Im Usage-Text steht der Aufrufname (`argv[0]`); über `c82ass.sh` erscheint daher `./_Linux/c82ass`. `c82ass.sh` ruft
`./_Linux/c82ass` relativ auf und muss deshalb aus dem Verzeichnis `Assembler` gestartet werden; dort werden auch
`projekdetails` und (zuerst) `c82ass.makros` gesucht.

- `-p` nennt das Verzeichnis, in dem die `.asm`-Datei **direkt** liegt (z. B. `Projekt_1/bsp_5.16`). Unterverzeichnisse
  werden nicht durchsucht; ein Pfadanteil bei `-s` wird abgeschnitten.
- Hat der Name bei `-s` keine Endung aus genau drei Zeichen, wird `.asm` angehängt (`bsp_5_16` wird zu `bsp_5_16.asm`).
- `projekdetails` enthält die Zeilen `-p <Verzeichnis>` und `-s <Datei>`; fehlt einer der Parameter im Aufruf, wird der
  gespeicherte Wert benutzt. Beim Wechsel des Projektverzeichnisses wird die bisherige Datei als
  `projekdetails.<altes Projekt>` gesichert (Schrägstriche im Namen werden zu `_`, z. B. `projekdetails.Projekt_1_bsp_5.16`)
  und die gesicherte Datei des neuen Projekts, falls vorhanden, zurückgeholt.
- Rückgabecode: 0 = fehlerfrei, 16 = Fehler (jede Art von Abbruch). Parameter ab einem Argument, das mit `>` beginnt,
  werden ignoriert.
- Unbekannte Optionen (z. B. `-x`) werden ohne Meldung ignoriert; der Lauf verwendet dann die gespeicherten Parameter.


## 3. Der Assembler c82ass

Version: 0.2

### 3.1 Programmstart

Der Assembler `c82ass` erwartet eine Eingabedatei mit `<quelltext>` unter einem Dateinamen `.asm`.

- **Pass 0:** liest die Makrodatei `c82ass.makros` (fester Name; gesucht zuerst im Arbeitsverzeichnis des Aufrufs, sonst in `Sourcecode/`),
  sammelt die im Quelltext definierten Makros (Abschnitt 4.1), prüft die Makrodefinitionen und löst die Makroaufrufe im Quelltext auf (Abschnitt 4).
- **Pass 1:** ermittelt die Literaltabelle, ausgegeben im Logfile `.log`.
- **Pass 2:** ermittelt die Symboltabelle, ausgegeben im Logfile `.log`, und schreibt die Symboldatei `.sym`.
- **Pass 3:** erzeugt aus dem aufgelösten Quelltext (Literale und Symbole eingesetzt) die Kennzeichenbefehle
  für das „Kleine Eingabeprogramm", ausgegeben im Objektfile `.obj`. Im selben Pass entstehen die Hilfsdatei
  `.mqo`, die formatierte Speicherbelegung `.dmp` und die Trommeldatei `.test` für den Interpreter.

Auf STDOUT gibt der Assembler den formatierten Quelltext (einschließlich der aufgelösten Literale) aus. Meldungen mit `Fehler:`,
`Warnung:` und `Abbruch` sowie die Statuszeilen `Projektverzeichnis:`, `Benutze für -s die Datei:` und `Startadresse:` gehen auf STDERR
(farbig hervorgehoben). Fehler werden je nach Pass in unterschiedlicher Form gemeldet (siehe die folgende Tabelle); jeder Fehler beendet
den Lauf mit Rückgabecode 16. Bei Fehlern können `.obj`, `.mqo` und `.dmp` trotzdem teilweise entstehen und sind dann nicht verwendbar.

**Fehlerausgaben**

| Fehlerart | Ausgabe auf STDOUT (Listing) | Ausgabe auf STDERR | Ablauf danach |
|---|---|---|---|
| Makrodefinition fehlerhaft (Pass 0) | – | `Fehler: Makrodefinition …`, `Fehler: N fehlerhafte Makrodefinition(en) …` | Abbruch nach Pass 0, keine Ausgabedateien |
| Makroaufruf fehlerhaft (Pass 0), z. B. Parameteranzahl oder -typ | `;*** Fehler: erwartet 2 Parameter, aber 1 wurden übergeben!` bzw. `;*** Fehler $1 Parameter $1: Wert "123" …` | `Warnung: Compilierung endete mit FEHLERn.` | Abbruch nach Pass 0, keine Ausgabedateien |
| Syntaxfehler in Pass 1 (z. B. `#` am Anfang eines `dt`-Textes) | `;*** 1 Fehler: …` | `Fehler: bei Operand: … in Zeile: …`, `Fehler: Abbruch wegen Syntaxfehler.` | Pass 2 läuft noch (`.log`, `.sym`), Pass 3 entfällt |
| Fehler in Pass 2 (z. B. Symbol doppelt, Programmzählerüberlauf über 7777) | `;*** (2) Fehler: …` | `Fehler: Abbruch wegen Syntaxfehler.` | Pass 3 entfällt |
| Fehler in Pass 3 (Operand oder Operationscode ungültig) | Zeile `<adresse>: EE …` mit darunter stehender Meldungszeile `bei Operand: … ungültig` | `Fehler: Abbruch.` | alle Pässe gelaufen, `.obj`, `.mqo`, `.dmp`, `.test` unvollständig |
| Belegungsfehler in Pass 3 | `;*** 3 Fehler: Adresse … doppelt belegt: …` | `Fehler: Adresse … doppelt belegt: …`, `Fehler: Abbruch.` | wie Fehler in Pass 3 |

**Belegungsprüfung (Pass 3):** Jedes Wort der Trommel darf nur von einer Anweisung beschrieben werden. Geprüft werden Maschinenbefehle,
`dw`, `da`, `dbn`, `dt`, `dto`, `dtm`, `dz` und die automatisch erzeugten Literale. Überschneidet sich die fortlaufende Speicherbelegung mit
einem früher belegten Bereich, zum Beispiel weil ein `equ` zurückspringt oder das Programm in einen mit `equ` weiter hinten angelegten
Datenbereich hineinläuft, meldet der Assembler `Adresse <oktal> doppelt belegt: "<neue Zeile>" ueberschneidet sich mit "<frühere Zeile>".`
und der Lauf endet mit Rückgabecode 16. Pro Zeile wird höchstens ein Konflikt gemeldet. Nicht geprüft werden `db` (reserviert nur
Speicherplätze), `equ`, `start`, `abs` und `end`.

Aufrufbeispiel:

```

**Auswertung von Ausdrücken** (`<werteausdruck>` und `<adressausdruck>`): `*` und `/` binden stärker als `+` und `-`;
Operatoren gleichen Ranges werden von links nach rechts ausgewertet (`2+3*4` ergibt 14, `10-2-3` ergibt 5). `/` ist eine
ganzzahlige Division, deren Ergebnis zur Null hin abgeschnitten wird (`7/2` ergibt 3, `-7/2` ergibt -3); eine Division durch 0 ist
ein Fehler. Ein Vorzeichen ist nur am Anfang des Ausdrucks zulässig (`-7/2`, `+5`, nicht `7/-2` oder `--5`). Klammern und
Leerzeichen innerhalb eines Ausdrucks sind nicht zulässig.

**Mnemonische Operationscodes (unvollendet):** Der Assembler enthält den Ansatz einer Tabelle mnemonischer Operationscodes (Datei `c8205_op_codes.c`). Zurzeit kennt er, ausschließlich in Kleinbuchstaben, `add` (Code 003), `sub` (004), `ld` (005), `jmp` (006), `stopp` (007) und `nop` (000). Der Operand wird wie bei dreistelligen Operationscodes behandelt und darf entfallen. Die Werte sind vorläufige Platzhalter und entsprechen nicht dem Befehlssatz des C8205; die Tabelle ist unvollständig, und die Mnemonics sollten in Programmen nicht verwendet werden. Maßgeblich bleibt der dreistellige Oktalcode. Die Tabelle ist als Grundlage für eine spätere Erweiterung um vollständige Mnemonics gedacht.
$ c82ass.sh -p PzBeispiele_4 -s bsp_5.17_Oktaldruck.asm
```

Die `<adresse>` der Befehle im Objektfile beginnt immer bei 0000. Ein Operand von `start` ändert die Adressen
nicht; der Wert steht nur in der Kennzeichenzeile `21 0000 <zahl>` (siehe 3.7).

Der Assembler erzeugt bzw. bearbeitet folgende Dateien im Verzeichnis der `.asm`-Datei (Beispiel
`Projekt_1/bsp_5.16/`):

| Endung | Inhalt |
|---|---|
| `.asm` | Quelltext (Eingabe) |
| `.dmp` | formatierte Speicherbelegung (Listing): je Zeile Adresse mit Maschinenwort (`<adresse>: <K1> [<K2>] [<Wert>]`), Label, Mnemonic, Operand und Kommentar in Spalten. Es ist dasselbe Listing, das der Assembler auf STDOUT ausgibt (Meldung „Ausgabe der formatierten Speicherbelegung nach: …“), jedoch ohne die Farbcodes der Fehlermeldungen |
| `.log` | Abschnitte, soweit vorhanden: Literaltabelle, EQU-Definitionen, ABS-Definitionen, Symboltabelle (Symbol, RelAddr, Adresse, original Operation) und Adresstabelle (nach Adresse sortiert) |
| `.mqo` | aufbereiteter Quelltext für `c82load` (kombiniert ihn mit dem Maschinencode); auch für `c82simi`, das ggf. bei der Einzelschrittverarbeitung die Kommentare einblendet. Gegenüber dem Quelltext fehlen `start`, `end`, Makrodefinitionen, reine Kommentarzeilen und `abs`-Anweisungen; Makroaufrufe sind durch ihre Ersetzung ersetzt, `equ`-Operanden aufgelöst, und die Literale stehen am Ende als `dw`-Zeilen (`l0001 dw 5`) |
| `.obj` | mit `c82load` ladefähiger Objektcode K1K2 |
| `.sym` | Symboldatei; wird von `c82dump` benutzt, um zum Trommeldump Symbole zuzuordnen. Je Zeile `<symbol>,<adresse>` (vierstellig oktal, in Quelltextreihenfolge, einschließlich Literalsymbolen wie `l0001`) |
| `.test` | Trommeldatei im Format des Interpreters (`Adresse: Wert # Quelltextzeile`) mit Kopf (`Trommeldatei:`, `#DOK-0001`, `#SPEI-0001 0000-0000`, `#PROT STUFE=2`) und Fuß (`Tastenfolge:`, `H G R`), die für den jeweiligen Fall ergänzt bzw. erweitert werden müssen. Zeilen gibt es nur für Wörter mit K1=00 oder 01 (Befehle, `dw`, `da`, `dz`, `dt`, `dto`, `dtm`, Nullwort); `db`, `equ`, `start` und `abs` erzeugen keine Zeile; Grundlage für Testaufträge, s. `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2a |

Vor jedem Lauf löscht der Assembler die Dateien `.log`, `.obj`, `.mqo`, `.sym`, `.test` und `.dmp` des
Projekts und erzeugt sie neu. Die früher in dieser Dokumentation genannten Endungen `.mqt` (modifizierter
Quelltext) und `.l82` (Objektcode für den `C8205Simulator`) erzeugt der aktuelle Assembler nicht mehr; sie sind
hier gestrichen. Dasselbe gilt für `.mac`: Der Quellcode legt keine solche Datei an (im Kommentar zu Pass 1 steht
nur ein Rest davon).

### 3.2 Sprachdefinition

```
<zahl>              ::= <oktalzahl> | <dezimalzahl>
<oktalzahl>          ::= oktalziffer==0 [ oktalziffer [ oktalziffer … ]]
<oktalziffer>        ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7
<vorzeichen>         ::= -
<dezimalziffer>      ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
<dezimalzahl>        ::= [<vorzeichen>] dezimalziffer<>0 [ dezimalziffer [ dezimalziffer … ]]
<alphazeichen>       ::= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
<sonderzeichen>      ::= % : + - / ` , . < " [ > ' ~ ] # * ( = ; ) ? !
<wert>               ::= <oktalzahl> | <dezimalzahl> | <symbol>
<rechenzeichen>      ::= + | - | * | /
<speicherplatz>      ::= Speicherstelle auf dem Trommelspeicher, fortlaufend nummeriert durch
                          eine Oktalzahl mit dem Wertebereich 00000 bis 07777.
<symbol>             ::= <adresssymbol> | <literalsymbol> | (leer)
<adresssymbol>       ::= Zeichenfolge aus 1 bis 32 Zeichen:
                          <alphazeichen> [ <alphazeichen> | <dezimalziffer> [ … ]],
                          abgeschlossen durch Doppelpunkt.
                          Sie wird vom Programmierer frei definiert. Der Unterstrich `_` wird ebenfalls akzeptiert.
                          Das erste Zeichen ist ein Buchstabe oder `_`, keine Ziffer. Erlaubt sind nur die ASCII-Buchstaben
                          `a`–`z`, `A`–`Z`, die Ziffern `0`–`9` und `_`; Zeichen wie `-`, `.` oder `ä` sind unzulässig.
                          Doppelt definierte Symbole, Symbole über 32 Zeichen und unzulässige Symbole sind Fehler.
<literalsymbol>      ::= 'l' (kleines L) gefolgt von einer Oktalziffernfolge von genau 4
                          Oktalziffern, abgeschlossen durch Doppelpunkt.
                          Sie wird vom Assembler automatisch aus dem Inhalt des Literalzählers vergeben.
<ausdruck>           ::= <werteausdruck> | <literal>
<operand>            ::= <werteausdruck> | <literal> | (leer)
<adressausdruck>     ::= <wert><rechenzeichen>[<wert><rechenzeichen> … ]
                          Einschränkungen: kein negatives Vorzeichen;
                          Wertebereich nur von 00000 … 07777;
                          nur maximal ein Symbol erlaubt.
                          Ein Vorzeichen am Anfang (auch `+`) ist nicht zulässig.
                          Verstöße meldet der Assembler als Fehler in Pass 3.
<werteausdruck>      ::= <wert><rechenzeichen>[<wert><rechenzeichen> … ]
                          Einschränkung: Bei `dw` und in `#`-Literalen sind keine Symbole zulässig (auch keine
                          `abs`-Symbole), dort nur Zahlen; Wertebereich -2^32 … 2^33-1. Adressen werden mit `da` oder
                          `@`-Literalen geschrieben.
<literal>            ::= #<werteausdruck> | @<adressausdruck>
                          Literal bedeutet, dass der numerische Wert von <werteausdruck> oder
                          <adressausdruck> auf einem vom Assembler selbst festgelegten
                          <speicherplatz> gespeichert wird. Diesem Speicherplatz wird vom
                          Assembler ein <literalsymbol> zugeordnet.
<adresse>            ::= numerischer Wert eines <symbol>, der einen <speicherplatz> adressiert.
<kommentar>          ::= ; (Semikolon) gefolgt von ASCII-Zeichen. | (leer)
                          Innerhalb der \-Zeichen von dt wird ; nicht als Kommentar betrachtet.
<trenner>            ::= Tabulator[<trenner>[...]] | Leertaste<trenner>[...]]
<befehl>             ::= [<symbol>] <trenner><operationscode> [<trenner><operand>]
                          [<trenner><kommentar>]
                          Alle Befehle müssen auf einer Zeile stehen; eine Zeile darf höchstens 255 Zeichen lang sein.
<operationscode>     ::= <maschinenbefehl> | <assembleranweisung>
<assembleranweisung> ::= start | end | db | dbn | dw | da | dt | dto | dtm | dz | equ | equ10 | equ40 | equ100 | abs
<maschinenbefehl>    ::= <oktalziffer><oktalziffer><oktalziffer>
<quelltext>          ::= <befehl>[<befehl> [ … ]]
```


## 3. Assembleranweisungen

(Nummerierung wie im Original: startet hier erneut bei "3.", s. Hinweis zur Nummerierung oben.)

### 3.1 Definiere Bereich

```
[<symbol>]  db  <zahl>
```
Hält `<zahl>` Speicherplätze frei, ohne ihren Inhalt zu definieren.
`<zahl>` muss eine Oktalzahl (führende 0) oder eine Dezimalzahl sein, höchstens 010000. Negative Zahlen, Ausdrücke
(z. B. `3+1`), Symbole und ein fehlender Operand sind Fehler.

### 3.2 Definiere Bereich auf Null

```
[<symbol>]  dbn  <zahl>
```
Hält `<zahl>` Speicherplätze frei, setzt ihren Inhalt auf 0.
Für `<zahl>` gilt dasselbe wie bei `db`. Je Speicherplatz erzeugt `dbn` in der Objektdatei die Zeile `00 0.`.

### 3.3 Definiere Wert

```
[<symbol>]  dw  <werteausdruck>
```
- Speichert den numerischen Wert von `<werteausdruck>` auf dem `<speicherplatz>`. Zulässig ist der Bereich -2^32 bis
  2^33-1 (33-Bit-Wort), sonst meldet der Assembler `Operand ist ungültig`. Negative Werte werden im Zweierkomplement
  gespeichert (`dw -5` ergibt `77777777773`). Symbole sind im `<werteausdruck>` von `dw` nicht zulässig; Adressen
  schreibt man mit `da`.
- Es wird keine Hauptleitadresse addiert.
- In der Objektdatei steht ein Datenwort als `00 <elf Oktalziffern>.`; nur der Wert 0 wird kurz als `<adresse>: 0.` ausgegeben
  (Nullwort ohne Kennzeichen).

```
[<symbol>]  dw  <literal>
```
- Erzeugt am Programmende automatisch aus `<literal>` eine Definition der Art
  `<literalsymbol> DW <werteausdruck>`.
- Speichert die `<adresse>` von `<literalsymbol>` auf dem aktuellen `<speicherplatz>`.
- Es wird keine Hauptleitadresse addiert.

### 3.4 Definiere Adresse

```
[<symbol>]  da  <adressausdruck>
```
Speichert den numerischen Wert von `<adressausdruck>` auf dem `<speicherplatz>`, verschoben um «9 in den
Adressstellen. Zum `<adressausdruck>` wird die 1. Hauptleitadresse addiert.

```
[<symbol>]  da  <literal>
```
- Erzeugt am Programmende automatisch aus `<literal>` eine Definition der Art
  `<literalsymbol> da <adressausdruck>`.
- Zum `<adressausdruck>` wird die 1. Hauptleitadresse addiert.
- Nimmt stattdessen die `<adresse>` von `<literalsymbol>` in den Befehl, der das `<literal>` enthält.

### 3.5 Definiere Text zur Ausgabe von Zeichen

```
[<symbol>]  dt[o|m]  \<alphazeichen> | <leerzeichen> | <dezimalziffer>
             <sonderzeichen> [ <alphazeichen> | <leerzeichen> | <dezimalziffer> | <sonderzeichen>[...]]\
```
- Gespeichert wird ein Code gemäß R300-Code Ausgabeadresse C8205 (siehe R300-code.pdf). Die
  Abspeicherung erfolgt als Folge von Speicherplatzinhalten in der Form (oktal): `0000 xxxx 030`, wobei
  `xxxx` die Ausgabeadresse ist.
- Die Zeichen „\" am Anfang und Ende sind erforderlich, wenn der Text mit `#` beginnt, ein `;` enthält (sonst beginnt dort der
  Kommentar) oder führende bzw. abschließende Leerzeichen enthalten soll. Leerzeichen innerhalb des Textes (`dt a b`) sind auch ohne
  „\" zulässig; sonst werden führende und abschließende Leerzeichen entfernt.
  Ein führendes `#` kennzeichnet ein Literal (`#<werteausdruck>`), keinen Text; `dt #ab` und `dto #x` meldet der
  Assembler als Fehler. Richtig ist `dt \#ab\` bzw. `dto \#x\`. Ein `#` innerhalb des Textes (`dt a#b`) ist zulässig.
- `dt` ist für längere, zusammenhängende Textausgaben gedacht. Sein Vorteil: Der Text lässt sich ohne
  ausgeschriebene Umschaltzeichen definieren, der Quelltext bleibt gut lesbar. Für verstreute Einzelzeichen
  ist `dt` nicht geeignet, dafür nimmt man `dz` (3.6) und schreibt alle Umschaltzeichen explizit.
- Der Assembler setzt `dt` zur Assemblerzeit in Maschinenbefehle um und kennt den Zustand KB/GB zur
  Laufzeit nicht. Er führt den Zustand nur in der Reihenfolge des Quelltexts weiter. Beim allerersten `dt`
  des Quelltexts nimmt er KB an. Jedes weitere `dt` setzt den Zustand des vorangehenden `dt` fort und fügt
  nur dort ein Umschaltzeichen ein, wo sich der Zustand innerhalb des Textes ändert.
- Daraus folgt: Vor jeder zusammengehörenden Folge von `dt`-Anweisungen muss ein Umschaltbefehl
  durchlaufen werden, der exakt auf den Zustand des ersten Zeichens dieser Folge schaltet (`dz $inkb`,
  `dz $ingb` oder `dtm` als erste Anweisung der Folge). Das gilt für jede Folge neu. Es kann dabei ein
  eigentlich unnötiger Umschaltbefehl entstehen. Der ist beabsichtigt, weil sich Assemblerzeit und
  Laufzeit nicht synchronisieren lassen. Umschaltzeichen mit `dz` zwischen zusammengehörenden
  `dt`-Anweisungen sind nicht zulässig, sie bringen den Zustand des Assemblers durcheinander.
- Praktischer Hinweis dazu: `dtm` fügt immer vor dem ersten Zeichen ein Umschaltzeichen passend zum ersten
  Buchstaben ein. Damit ist es die natürliche erste Anweisung einer `dt`-Folge. Es ersetzt das von Hand
  gesetzte `dz $inkb` oder `dz $ingb` davor.
- `dto` verhält sich wie `dt`, außer dass generell KEINE Umschaltzeichen automatisch eingefügt werden.
  Das bedeutet, in einer `dto`-Anweisung kann man KEINE gemischte Groß- und Kleinschreibung definieren
  (auch keine Zahlen und Großbuchstaben usw.).
- `dtm` verhält sich wie `dt`, außer dass vor dem ersten Zeichen generell ein Umschaltzeichen, dem ersten
  Buchstaben entsprechend, automatisch eingefügt wird.

### 3.6 Definiere Zeichen (spezielle Sonderzeichen)

```
[<symbol>]  dz  $wrzl | $sm | $inkb | $ingb | $irrz | $irrs | $trans | $bm | $vorl |
                $irrb | $wr | $tab | $zr | % | : | + | ` | / | , | . | -
```
- Gespeichert wird ein Code gemäß R300-Code Ausgabeadresse C8205 (siehe Tabelle 2 unten). Die
  Abspeicherung erfolgt auf einem Speicherplatz in der Form (oktal): `0000 ssss 030`. Eine automatische
  Ergänzung von Umschaltzeichen wie bei `dt` erfolgt hier generell NICHT.
- Findet man z. B. `dz $wrzl` zu kompliziert, kann man das mit einem Makro vereinfachen:
  ```
  WRZL:  MACRO
             dz  $wrzl  ; Zeilenschaltung
         MEND
  ```
  (In der mitgelieferten `c82ass.makros` enthält `WRZL` zusätzlich die Anweisung `ANWAHL 4700`.)

### 3.7 Beginn des Quellcodes

```
start  [<zahl>]
```
- Nur als 1. Anweisung im `<quelltext>` zulässig, und nur einmal; ein Label vor `start` ist ein Fehler. Der Operand
  muss eine Konstante sein. Der Befehlszähler beginnt unabhängig vom Operanden bei 0. Eine Maschinencodeausgabe erfolgt
  nicht; mit Operand wird im Objektcode die Kennzeichenzeile `21 0000 <zahl>` ausgegeben.
- Ist `<zahl>` angegeben, wird die 1. Leitadresse in den „Lochstreifen" ausgegeben. Es wird dann durch
  `c82load` auf diese 1. Leitadresse + Ladeadresse geladen. Die Ladeadresse existiert dabei nur beim
  Laden mit `c82load`.

### 3.8 Definition Relativadresse

```
[<symbol>]  equ  <werteausdruck> | *
```
- Definiert für das `<symbol>` einen `<werteausdruck>`. Der Befehlszähler wird auf diesen Wert gesetzt.
- Ist `*` angegeben, wird dem Symbol stattdessen der aktuelle Befehlszählerstand zugewiesen.
- Eine Maschinencodeausgabe erfolgt nicht. Im Objektcode für das „Kleine Eingabeprogramm" wird der
  Kennzeichenbefehl für das Setzen der Relativadresse ausgegeben (KZ=20).
- Das weitere Laden erfolgt auf 1. Leitadresse + Ladeadresse + Relativadresse. Die Ladeadresse existiert
  dabei nur beim Laden mit `c82load`.
- Die Anweisungen `equ100`, `equ40` und `equ10` runden den Befehlszähler (Operand `*`) oder den numerischen Operanden
  auf das nächste Vielfache von 0100, 040 bzw. 010 (oktal) auf.

### 3.9 Definition Absolutadresse

```
[<symbol>]  abs  <oktalzahl> | <dezimalzahl>
```
- Definiert für das `<symbol>` eine absolute `<adresse>`. Weder Objektcode- noch Maschinencodeausgabe
  erfolgt.
- Beachte: Symbole, die durch `abs` definiert wurden, sind nicht verschieblich. Anweisungen, in denen ein
  solches Symbol im Adressausdruck oder Werteausdruck vorkommt, werden mit K1K2=00 generiert!
- `abs` kann mehrfach mit dem gleichen Wert definiert werden, ohne Fehler zu erzeugen, aber nicht
  mehrfach mit dem gleichen Symbol für unterschiedliche Werte.

### 3.10 Ende des verschieblichen Teils des Quelltextes

```
[<symbol>]  end
```
- Hinter dieser Anweisung sollten nur noch `abs`- oder `equ`-Anweisungen folgen. Sie werden auch dann
  ausgewertet, wenn das Programm Literale enthält. Makrodefinitionen (siehe Abschnitt 4.1) dürfen
  ebenfalls dort stehen. Der Assembler ordnet hinter dem ersten „end" die automatisch erzeugten
  Literaldefinitionen ein, sodass sie noch zum verschieblichen Teil hinzukommen. Ein nachfolgendes
  `equ` käme also HINTER die Literale. Ein weiteres „end" ändert daran nichts.
- Eine Maschinencodeausgabe erfolgt für „end" nicht.
- Code und Daten (Maschinenbefehle, `db`, `dw` usw.) hinter „end" sind nicht vorgesehen. Der Assembler
  lehnt sie nicht ab, sondern übersetzt sie hinter den Literalen (soweit vorhanden) mit.


### Tabelle 2: Sonderzeichen für die dz-Anweisung

Spalte 1: String, der als Operand bei `dz` anzugeben ist. Spalte 2: 4 Oktalziffern, die die 8 Bit des
030-Ausgabecodes enthalten.

| Sonderzeichen-String | Oktalcode (030-Ausgabe) |
|---|---|
| `$wrzl` | 02720 |
| `$sm` | 02720 |
| `$inkb` | 01170 |
| `$ingb` | 0570 |
| `$irrz` | 03770 |
| `$irrs` | 0160 |
| `$trans` | 01770 |
| `$bm` | 03520 |
| `$vorl` | 0 |
| `$irrb` | 0760 |
| `$zr` | 0320 |
| `$tab` | 01550 |
| `$wr` | 01120 |
| `%` | 01740 |
| `:` | 0150 |
| `+` | 0400 |
| `` ` `` | 01600 |
| `/` | 01410 |
| `,` | 01530 |
| `.` | 0730 |
| `-` | 01000 |

(In der Quelle sind `$wrzl` und `$sm` beide mit 02720 gelistet — so übernommen, nicht aufgelöst. Das Zeichen `;` kann bei `dz` nicht angegeben werden, weil es einen Kommentar einleitet; der Operand für den Code 0150 ist `:`, passend zu Tabelle 3.)

### Tabelle 3: Ausgabe-Umschlüsselung außer Sonderzeichen dz

Spalten: ASCII-Kleinbuchstabe, ASCII-Großbuchstabe, Oktalcode (8 Bit des 030-Ausgabecodes),
ASCII-Code Großbuchstabe (dez.), ASCII-Code Kleinbuchstabe (dez.).

| Klein | Groß | Oktalcode | ASCII Groß (dez) | ASCII Klein (dez) |
|---|---|---|---|---|
| 1 | < | 0010 | 60 | 49 |
| 2 | " | 0020 | 34 | 50 |
| 3 | ≈ | 0230 | 0 | 51 |
| 4 | [ | 0040 | 91 | 52 |
| 5 | > | 0250 | 62 | 53 |
| 6 | ' | 0260 | 39 | 54 |
| 7 | ≋ | 0070 | 0 | 55 |
| 8 | ~ | 0100 | 126 | 56 |
| 9 | ] | 0310 | 93 | 57 |
| 0 | # | 0200 | 35 | 48 |
| % | * | 1740 | 42 | 37 |
| Tabulator | Tabulator | 1550 | 9 | 9 |
| q | Q | 1300 | 81 | 113 |
| w | W | 1660 | 87 | 119 |
| e | E | 0450 | 69 | 101 |
| r | R | 1110 | 82 | 114 |
| t | T | 1630 | 84 | 116 |
| z | Z | 1710 | 90 | 122 |
| u | U | 1440 | 85 | 117 |
| i | I | 0510 | 73 | 105 |
| o | O | 1060 | 79 | 111 |
| p | P | 1270 | 80 | 112 |
| : | ( | 0150 | 40 | 58 |
| + | = | 0400 | 61 | 43 |
| a | A | 0610 | 65 | 97 |
| s | S | 1420 | 83 | 115 |
| d | D | 0640 | 68 | 100 |
| f | F | 0460 | 70 | 102 |
| g | G | 0670 | 71 | 103 |
| h | H | 0700 | 72 | 104 |
| j | J | 1210 | 74 | 106 |
| k | K | 1220 | 75 | 107 |
| l | L | 1030 | 76 | 108 |
| ` | ; | 1600 | 59 | 96 |
| / | ) | 1410 | 41 | 47 |
| SatzMarke | WRZL | 2720 | 10 | 10 |
| y | Y | 1500 | 89 | 121 |
| x | X | 1470 | 88 | 120 |
| c | C | 0430 | 67 | 99 |
| v | V | 1650 | 86 | 118 |
| b | B | 0620 | 66 | 98 |
| n | N | 1050 | 78 | 110 |
| m | M | 1240 | 77 | 109 |
| , | ? | 1530 | 63 | 44 |
| . | ! | 0730 | 33 | 46 |
| - | — | 1000 | — | 45 |
| Leertaste | ZwR | 0320 | 32 | 32 |

(Zeile "i/I" in der Quelle als "I / I" notiert — hier als Klein-/Großbuchstabe interpretiert und so
übernommen. Zeile "-" hat in der Quelle keinen Eintrag in Spalte "ASCII Groß (dez)" — als "—" markiert,
nicht ergänzt.)


## 4. Der Makro-Präprozessor des Assemblers

Der Präprozessor ist sehr einfach gehalten und hat eine starre Syntax. Er prüft, ob eine Operation ein
Makroname ist. Die Prüfung erfolgt in der Textdatei `c82ass.makros`, die erweitert werden darf. Der Assembler sucht sie unter
diesem festen Namen zuerst im Arbeitsverzeichnis des Aufrufs, sonst unter `Sourcecode/c82ass.makros`; fehlt sie
an beiden Orten, bricht er mit einer Fehlermeldung ab. Zusätzlich können Makros direkt im Quelltext definiert werden (Abschnitt 4.1).

- Jedes dort definierte Makro beginnt mit dem Makronamen, unmittelbar gefolgt von einem Doppelpunkt und
  danach (getrennt durch Tab oder Leerzeichen) dem Schlüsselwort `MACRO`.
- Müssen dem Makro Parameter übergeben werden, folgt nach `MACRO`, getrennt durch Leerzeichen, die
  Anzahl der Parameter. Es sind maximal 9 Parameter zulässig.
- Danach kommen die Definitionsanweisungen des Makros. Sie können die formalen Parameter `$x` mit
  x=1..9 enthalten, die durch die Übergabeparameter ggf. mehrfach ersetzt werden.
- Jedes Makro wird durch das Schlüsselwort `MEND` abgeschlossen (Leerraum davor ist beliebig).

Im Definitionsteil kann für jeden Parameter eine Prüfliste angegeben werden. Ist sie angegeben, darf der
betreffende Parameter nur die Werte der Liste annehmen. Eine Prüfliste wird durch `$PRx` mit x=1..9
definiert; sie muss auf einer Zeile für sich stehen.

Statt einer Werteliste kann hinter `$PRx` eine Typangabe stehen (z. B. `$PR1: $TYPADR`). Dann prüft der Assembler
beim Makroaufruf, ob der übergebene Wert zum Typ passt; sonst meldet er einen Fehler
`Parameter $x: Wert "<wert>" …`:

| Typ | Zulässiger Wert beim Aufruf |
|---|---|
| `$TYPADR` | eine symbolische Adresse (ein Label, z. B. `marke`) oder eine Sternadresse (`*`, `*+3`); keine Zahl |
| `$TYPKON` | eine Oktalkonstante: nur Ziffern 0–7, beginnt mit `0` (z. B. `0100`); `100` oder `09` sind Fehler |
| `$TYPABS` | ein Symbol, das im Quelltext mit `abs` definiert ist (z. B. `absx: abs 05`) |

Die Prüfung erfolgt vor der eigentlichen Übersetzung und ist deshalb nur syntaktisch: Bei `$TYPADR` wird nicht
geprüft, ob das Label im Programm vorkommt (das meldet die spätere Symbolauflösung).

Die Definition der zu generierenden Anweisungen kann durch eine `$IF`-`$ELIF`-`$ENDIF`-Struktur gesteuert
werden. Sie kann mehrfach auftreten, darf aber nicht geschachtelt werden. Die Schlüsselworte `$IF`,
`$ELIF`, `$ENDIF` müssen jeweils auf einer Zeile für sich stehen.

Hinter `$IF` und `$ELIF` muss mindestens einer, können bis zu 4 Bedingungsblöcke angegeben werden. Ein
Bedingungsblock besteht aus 3 Strings: `<wert1> <vergleichszeichen> <wert2>`. Als
`<vergleichszeichen>` sind `>`, `<`, `=`, `>=`, `<=` zugelassen. Jeder folgende Bedingungsblock ist durch
`|` (logisch ODER) oder `&` (logisch UND) zu verknüpfen.

Achtung: Die Bedingungsblöcke haben eine implizite Klammerung der Art:

```
(((  <bedingungsblock1> [|&] <bedingungsblock2> ) [|&] <bedingungsblock3> ) [|&] <bedingungsblock4> )
```

Innerhalb eines Definitionsblockes sind Kommentare zugelassen: `#` leitet einen Kommentar ein, der nur in
der Makrodefinition gilt und auf einer eigenen Zeile stehen muss; `;` leitet einen Kommentar ein, der
auch generiert wird — er kann auf einer eigenen Zeile oder in der Anweisung vorkommen.

Beispiel:

```
ANWAHL:  MACRO 1
  $PR1 4000 4100 4200 4300 4400 4500 4600 4700 K0 K1 K2 K3 K4 K5 K6 K7 LSL1 LSL2 LKL1 LKS1 LSS1 SW1I SW1O SW2O KONI
  # Generieren einer Anwahl für Zeichenkanäle
      $IF  $1  =  4000 | $1 = K7
         030 04000  ; 4000 oder K7
      $ELIF  $1  =  4100 | $1 = K6
         030 04100  ; 4100 oder K6
      $ELIF  $1  =  4200 | $1 = K5
         030 04200  ; 4200 oder K5
      $ELIF  $1  =  4300 | $1 = K4 | $1 = LKS1
         030 04300  ; 4300 oder K4 oder LKS1
      $ELIF  $1  =  4400 | $1 = K3 | $1 = LKL1 | $1 = SW2O
         030 04400  ; 4400 oder K3 oder LKL1 oder SW2 Output
      $ELIF  $1  =  4500 | $1 = K2 | $1 = LSL2 | $1 = SW1O
         030 04500  ; 4500 oder K2 oder LSL2 oder SW1 Output
      $ELIF  $1  =  4600 | $1 = K1 | $1 = LSL1 | $1 = LSS1
         030 04600  ; 4600 oder K1 oder LSL1 oder LSS1
      $ELIF  $1  =  4700 | $1 = K0 | $1 = SW1I | $1 = KONI
         030 04700  ; 4700 oder K0 oder SW1 Input oder KON Input
      $ENDIF
         MEND
```

Aufruf: `ANWAHL LSS1` erzeugt: `030  04600  ; 4600 oder K1 oder LSL1 oder LSS1`

Der Makroaufruf im Assemblerprogramm darf ein Label haben, z. B.:

```
input_loop:  ANWAHL  LSL1
             …
```

In einem solchen Fall wird generiert:

```
input_loop:  030  04600  ; 4600 oder K1 oder LSL1 oder LSS1
```

Der Makroaufruf selbst wird nicht als Kommentarzeile (`;   ANWAHL   LSL1`) ausgegeben; er erscheint weder im Listing
noch in `.mqo`, `.dmp` oder `.test`.

Enthält das Makro selbst eine Schleife mit einem Label, z. B.:

```
BSP1:  MACRO
# Makro enthält eine Schleife
ML0001%: 211  …
         …
         000  ML0001%
         MEND
```

so wird bei einem Makroaufruf `loop: BSP1` folgende Anweisungsfolge generiert, wenn die erste zu
generierende Anweisung ein eigenes Label hat:

```
loop      equ  *
ML0001DKR 211  …
          …
          000  ML0001DKR
```

Hat die erste Anweisung kein eigenes Label, entfällt die `equ`-Anweisung und die erste Anweisung erhält
das Label des Makroaufrufs. Ausnahme: Ist die erste Anweisung `equ`, `abs`, `start` oder `end`, bleibt die `equ`-Anweisung
bestehen.

Ein Makro SOLLTE kein „normales" Label der Assemblersprache enthalten, sonst kann es nur einmalig
aufgerufen werden. Stattdessen muss ein generisches Label verwendet werden: genau `ML`, vier Ziffern und `%`, danach der
Doppelpunkt (z. B. `ML0004%:`). Jedes andere Label mit `%` meldet den Fehler `Macrolabel muß mit ML beginnen …`. Bei jedem
Aufruf wird das `%` durch drei Großbuchstaben ersetzt (z. B. `ML0001DKR`), sodass jeder Aufruf ein eigenes Label erhält.

Makro-Aufrufparameter, die exakt 4 Ziffern enthalten und nur diese, werden ggf. als 4-Ziffern-String
geprüft (durch `$PRx`); sie erhalten bei der Benutzung (Ersetzung des formalen Parameters) automatisch
eine Vornull. Beispiel: `ANWAHL 4600` erzeugt:

```
     030    04600  ; 4600 oder K1 oder LSL1 oder LSS1
```

### 4.1 Makros im Quelltext

Makros können nicht nur in der Makrodatei `c82ass.makros`, sondern auch direkt im Quelltext (`.asm`) definiert
werden. Die Definition hat dieselbe Syntax wie in der Makrodatei: Sie beginnt mit dem Makronamen, unmittelbar
gefolgt von einem Doppelpunkt, danach folgt das Schlüsselwort `MACRO` (bei Bedarf mit der Anzahl der Parameter).
Abgeschlossen wird sie durch `MEND` (zulässig sind auch `MACROENDE` und `macroende`). Der Doppelpunkt hinter dem
Makronamen ist im Quelltext Pflicht.

- **Gültigkeit:** Eine Definition darf an beliebiger Stelle im Quelltext stehen, auch vor `start`. Das Makro gilt
  im gesamten Quelltext, auch für Aufrufe, die vor der Definition stehen. Die Definition selbst erzeugt keinen Code.
- **Definitionsteil:** Es gelten alle Regeln dieses Abschnitts (formale Parameter `$x`, Prüflisten `$PRx`,
  `$IF`-`$ELIF`-`$ENDIF`, Kommentare mit `#` und `;`, generische Labels mit `%`). Ein Makro darf andere Makros
  aufrufen, gleichgültig ob sie in der Makrodatei oder im Quelltext definiert sind, aber nicht sich selbst.
- **Gleicher Name wie in der Makrodatei:** Das Makro im Quelltext ersetzt das gleichnamige Makro der Makrodatei,
  jedoch nur für diesen Assemblerlauf; die Makrodatei selbst bleibt unverändert. Der Assembler gibt dazu eine
  Warnung aus. Die Ersetzung wirkt auch dort, wo ein anderes Makro das ersetzte Makro aufruft.
- **Fehler:** Ein Makroname darf im Quelltext nur einmal definiert werden. Weitere Fehler sind eine `MACRO`-Zeile
  ohne Namen, eine Definition innerhalb einer anderen Definition (Schachtelung ist nicht erlaubt), ein fehlendes
  `MEND` und ein `MEND` ohne zugehöriges `MACRO`. Der Assembler meldet den Fehler und bricht nach Pass 0 ab.

Beispiel:

```
ZEILE2:  MACRO
         dz  $wrzl  ; Zeilenschaltung
         dz  $wrzl  ; Zeilenschaltung
         MEND
```

Der Aufruf `ZEILE2` erzeugt die beiden Anweisungen `dz $wrzl`.

Soll das Makro `WRZL` der Makrodatei nur für ein Programm anders arbeiten, wird es im Quelltext neu definiert:

```
WRZL:    MACRO
         dz  $wrzl  ; Zeilenschaltung
         dz  $wrzl  ; Zeilenschaltung
         MEND
```

Der Assembler meldet dazu:

```
Warnung: Makro WRZL aus der Makrodatei wird für diesen Lauf durch die Definition im Quelltext ersetzt.
```


## 5. Compilierungsbeispiel

```
c82ass.sh -p Projekt_1/bsp_5.16 -s bsp_5_16
```

### 5.1 Quelltext bsp_5_16.asm und Assemblerlauf

Hinweis: Die Datei `Projekt_1/bsp_5.16/bsp_5_16.asm` ist eine veränderte Fassung des hier abgedruckten Beispiels: Sie beginnt mit dem Startsprung `000 go` mit `equ 02000` und der Marke `go:`, enthält vor dem Halt den Debug-Befehl `164 0001`, und der Datenbereich beginnt mit `equ 02100` statt `equ 0100`. Ihr Objektcode weicht deshalb von 5.2 ab; der abgedruckte Quelltext ergibt genau den Objektcode in 5.2.

```
Projektverzeichnis: Projekt_1/bsp_5.16
Benutze für -s die Datei: bsp_5_16
Startadresse: 0000
C8205 Assembler C82aas Version 0.2

Pass 0
Verarbeite 'c82ass.makros', Erzeuge Macroersetzungen

Pass 1
Löse Literale auf

Pass 2
Löse Symbole auf nach Projekt_1/bsp_5.16/bsp_5_16.log und Projekt_1/bsp_5.16/bsp_5_16.sym

Pass 3
Erzeuge Kennzeichen-Befehle in Objektdatei Projekt_1/bsp_5.16/bsp_5_16.obj
```

Quelltext (`; C8205 Heft 2 Programmierung in Maschinensprache; Beispiel: 5.16 Umspeichern eines
Vektors`):

```asm
                start
                000     beginn
aqv:            da      qvektor    ; Adresse der ersten Komponente Quellvektor
dqv:            dw      05000      ; Dimension von qvektor gezählt in Adresseinheiten
azv:            da      zvektor    ; Adresse der ersten Komponente Zielvektor
adreinheit:     dw      01000      ; Adresseinheit
spbef:          dw      0240       ; Speicherbefehl
i:              db      1          ; Arbeitszelle für i
beginn:         241     i          ; I:=0
schleife:       210     azv        ; ac:=(azv+i)
                210     spbef      ; ac:=(azv+i)240
                240     genbef     ; Arbeitszelle genbef:= (qzv+i) 240
                211     i          ; ac:=<i>
                210     aqv        ; ac:=qvektor+i
; 251: Laden des Inhaltes einer Speicherstelle, deren Adresse im AC steht, in den AC.
                251     0          ; ac:=<qvektor+i>
genbef:         db      1          ; hier steht der Befehl 240 (qzv+i) Speichern
                211     i          ; ac:=<i>
                210     adreinheit ; ac:=i+1
                240     i          ; i:=ac
                330     dqv        ; vergleicher 3, falls i == <dqv>
                170     halt       ; sprung bei gleich
                000     schleife
halt:           020     0          ; halt
qvektor:        dw      1
                dw      2
                dw      3
                dw      4
                dw      5
                equ     0100
zvektor:        db      5
ende:           end
```

Nach dem Listing meldet der Assembler:

```
Ausgabe als Minimalprogramm-Objektdatei nach: Projekt_1/bsp_5.16/bsp_5_16.obj
Ausgabe der formatierten Speicherbelegung nach: Projekt_1/bsp_5.16/bsp_5_16.dmp
Ausgabe der Testdatei (Spalten 1,3,4,5 fuer K1=00/01) nach: Projekt_1/bsp_5.16/bsp_5_16.test
```

### 5.2 Durch c82ass erzeugter Objektcode (K1K2-Programmcode) für „Kleines Eingabeprogramm"

```
0000: 01 0007 000.
0001: 01 26000.
0002: 00 00000005000.
0003: 01 100000.
0004: 00 00000001000.
0005: 00 00000000240.
0006: 20 0007.
0007: 01 0006 241.
0010: 01 0003 210.
0011: 01 0005 210.
0012: 01 0016 240.
0013: 01 0006 211.
0014: 01 0001 210.
0015: 00 0000 251.
0016: 20 0017.
0017: 01 0006 211.
0020: 01 0004 210.
0021: 01 0006 240.
0022: 01 0002 330.
0023: 01 0025 170.
0024: 01 0010 000.
0025: 01 0000 020.
0026: 00 00000000001.
0027: 00 00000000002.
0030: 00 00000000003.
0031: 00 00000000004.
0032: 00 00000000005.
      20 0000 0100.
0100: 20 0105.
/
```


## 6. Abgleich mit dem Assembler c82ass (Prüfung vom 08.10.2026)

Grundlage der Prüfung: Binary `c82ass` (Version 0.2), Quellcode `ca82ass.c` und `ca82_standards.c`, Makrodatei
`c82ass.makros` sowie Testläufe mit dem Binary. Der Text der geänderten `.odt` stimmt mit den Abschnitten 1 bis 5 dieser
Datei inhaltlich überein (nur Formatierung und Tippfehler unterscheiden sich). Die folgenden Punkte betreffen das Verhalten des Assemblers. Die Abschnitte 1 bis 5
wurden am 09.10.2026 an dieses Verhalten angepasst; Abschnitt 6.1 bleibt als Änderungsprotokoll erhalten (die Spalte
"Dokumentation sagt" nennt den Text der .odt vor der Anpassung).

### 6.1 Abweichungen zwischen Dokumentation und Assembler

| Nr. | Stelle | Dokumentation sagt | c82ass tut |
|---|---|---|---|
| 1 | 3.1, 5 (Aufruf) | `-p Projekt_1 -s bsp_5_16`, Dateien liegen in `Projekt_1/bsp_5.16/` | `-p` muss das Verzeichnis sein, in dem die `.asm` direkt liegt, also `-p Projekt_1/bsp_5.16`. Unterverzeichnisse werden nicht durchsucht. Ein Pfadanteil in `-s` wird abgeschnitten. Sonst: `Fehler: Die Datei … existiert nicht im Projektverzeichnis`, Rückgabecode 16. |
| 2 | 2 | `c82ass.sh -h` meldet `Usage: c82ass.sh -p …` | Meldet den Aufrufnamen aus `argv[0]`, über `c82ass.sh` also `Usage: ./_Linux/c82ass -p Projektverzeichnis -s Quellcode-Datei`. |
| 3 | 5.1 | Ausgabe mit Zeilen `Eingabedatei:`, `Log-Datei:`, `Maschinencode-Datei:`, `Hilfsdatei:`, `Symboltabelle-Datei:`, `Verarbeite Quellcode:` | Gibt tatsächlich aus: `Projektverzeichnis: …`, `Benutze für -s die Datei: …`, `Startadresse: …`, Banner, die Pässe, das Listing und am Ende `Ausgabe als Minimalprogramm-Objektdatei nach: …`, `Ausgabe der formatierten Speicherbelegung nach: …`, `Ausgabe der Testdatei (Spalten 1,3,4,5 fuer K1=00/01) nach: …`. |
| 4 | 3.1 (Fehlermeldungen) | Fehlermeldungen erfolgen innerhalb der STDOUT-Ausgabe | Nur Fehler aus den Pässen stehen im Listing auf STDOUT (Zeile `;*** (n) Fehler: …`). Meldungen mit `Fehler:`, `Warnung:` und `Abbruch` gehen farbig nach STDERR, ebenso die Statuszeilen `Projektverzeichnis:`, `Benutze für -s die Datei:` und `Startadresse:`. |
| 5 | 3.1 (`.log`) | Literaltabelle, Symboltabelle, Tabelle der absoluten Symbole | Abschnitte, sofern vorhanden: `Literaltabelle`, `EQU-Definitionen`, `ABS-Definitionen`, `Symboltabelle` (Spalten Symbol, RelAddr, Adresse, original Operation) und `Adresstabelle` (nach Adresse sortiert). |
| 6 | 3.1 (`.test`) | Platzhalter für Testmarken und Tastenfolge, ggf. Leerbefehl 164 | Der Assembler schreibt keinen Leerbefehl 164. Aufbau: Kopf `Trommeldatei:`, `#DOK-0001`, `#SPEI-0001 0000-0000`, `#PROT STUFE=2`; je Wort mit K1 = 00 oder 01 (Befehle, `dw`, `da`, `dz`, `dt`/`dto`/`dtm`, Nullwort) eine Zeile `<adresse>: <11 Oktalziffern> # <Quelltext>`; Fuß `Tastenfolge:` und `H G R`. `db`, `equ`, `start`, `abs` erzeugen keine Zeile. |
| 7 | 3.1 (`.sym`) | Symboldatei | Format je Zeile `<symbol>,<adresse>` mit vierstelliger Oktaladresse, in Quelltextreihenfolge, einschließlich Literalsymbolen (`l0001`). |
| 8 | 3.2, 3.8 | `<assembleranweisung>` kennt nur `equ`; im Text stehen `equ100`, `equ40`, `equ10` | Die drei Varianten sind echte Operationscodes. Sie runden den Befehlszähler (Operand `*`) oder den numerischen Operanden auf das nächste Vielfache von 0100, 040 bzw. 010 auf. |
| 9 | 3.6, Tabelle 2 | `dz`-Operand `;` mit Code 0150 | `;` ist nicht möglich, weil das Semikolon einen Kommentar einleitet (`dz Operand nicht gültig`). Der Assembler kennt stattdessen `:` mit Code 0150 (passend zu Tabelle 3). `$wrzl` und `$sm` haben beide 02720, wie dokumentiert. |
| 10 | 3.3, 3.2 | `<werteausdruck>` darf Symbole enthalten | Bei `dw` und in `#`-Literalen sind Symbole nicht zulässig, auch keine `abs`-Symbole: `dw a+1`, `dw #a`, `dw x1+1` und `210 #a+2` melden `Operand … ist ungültig`. Adressen schreibt man mit `da` oder mit `@`-Literalen (`da a+1`, `dw @a`). In Maschinenbefehlen sind `abs`-Symbole im Operanden erlaubt (`211 x1+2` erzeugt K1K2=00). |
| 11 | 3.7 | `start` nur als 1. Anweisung | Stimmt, zusätzlich: `start` darf nur einmal vorkommen, der Operand muss eine Konstante sein, ein Label vor `start` ist ein Fehler. Mit Operand schreibt der Assembler die Objektzeile `21 0000 <zahl>`. Der Befehlszähler beginnt unabhängig vom Operand bei 0. |
| 12 | 3.2 | Maschinenbefehl = drei Oktalziffern | **Behoben im Quellcode (Schritt 6):** Früher wurde jede dreistellige Dezimalzahl als Operationscode akzeptiert (`999 0` ergab K1K2=01, Code 999). Jetzt sind nur drei Oktalziffern 0–7 gültig; sonst meldet der Assembler `bei Operand: <code> Operationscode ist ungültig` und endet mit Rückgabecode 16. Die Meldung nennt dabei den Operationscode, früher stand dort fälschlich der Operand. |
| 13 | 3.2 | Symbole: Buchstaben und Ziffern | Der Unterstrich wird akzeptiert (`label_1:`). Das erste Zeichen darf keine Ziffer sein (`1abc:` ist ein Fehler), und außer ASCII-Buchstaben, Ziffern und `_` ist kein Zeichen zulässig (`ab-c:`, `x.y:`, `äb:` sind Fehler). Die Meldung lautet `Label "<name>:" ist unzulaessig: erlaubt sind Buchstaben, Ziffern und _, das erste Zeichen ist keine Ziffer.`, danach endet der Lauf mit `Abbruch wegen Syntaxfehler`. Labels über 32 Zeichen und doppelt definierte Labels sind ebenfalls Fehler. Eine Quelltextzeile darf höchstens 255 Zeichen lang sein. |
| 14 | 4 | Makrodefinition: `MACRO` nach einem Tab, Abschluss `<tab>MEND` | Die Trennung erfolgt durch beliebigen Leerraum, Leerzeichen genügen (so ist `c82ass.makros` geschrieben). |
| 15 | 4 | Generisches Makro-Label: Buchstabe, Buchstaben/Ziffern, `%` vor dem Doppelpunkt; Beispiel `start%:`, erzeugt `start0001` | Erlaubt ist nur `ML` + genau vier Ziffern + `%` + `:`, z. B. `ML0004%:`. Alles andere meldet `Macrolabel muß mit ML beginnen …` (der Hinweistext nannte früher irrtümlich fünf Ziffern, `ML01234%`; behoben in Schritt 3). Das `%` wird durch drei Großbuchstaben ersetzt (z. B. `ML0001DKR`), nicht durch die Aufrufnummer. Das Beispiel `start%:` ist damit nicht lauffähig. |
| 16 | 4 | Makroaufruf mit Label: Hat die erste erzeugte Anweisung kein eigenes Label, entfällt die `equ`-Anweisung | **Behoben im Quellcode (Schritt 5):** Früher wurde die Zeile `<label> equ * ; automatisch generiert` immer erzeugt (im Objektcode als Zeile `20 0000 <adr>`). Jetzt erhält die erste erzeugte Anweisung das Label des Aufrufs, und die `equ`-Zeile entfällt, wie beschrieben. Die `equ`-Zeile bleibt, wenn die erste Anweisung selbst ein Label trägt oder ein `equ`, `abs`, `start` oder `end` ist (dort würde das Label sonst einen anderen Wert als die Adresse bekommen). Kommentarzeilen vor der ersten Anweisung werden übersprungen. Symboltabelle und Maschinencode sind unverändert. |
| 17 | 4 | Beispielmakro `ANWAHL` erzeugt `030 4000` usw. | Die Makrodatei erzeugt `030 04000` (mit führender Null). Das Makro `WRZL` in der Makrodatei enthält zusätzlich `ANWAHL 4700`; das Beispiel in 3.6 zeigt nur `dz $wrzl`. |

### 6.2 Ergänzungen (im Dokument bisher nicht beschrieben)

- **Rückgabecodes:** 0 = fehlerfrei, 16 = Fehler (jede Art von Abbruch). Beim Aufruf werden alle Parameter ab einem Argument,
  das mit `>` beginnt, ignoriert.
- **Fehlerausgaben:** Die Form der Fehlermeldungen hängt vom Pass ab (`;*** Fehler: …` in Pass 0, `;*** 1 Fehler: …` in Pass 1,
  `;*** (2) Fehler: …` in Pass 2, Zeile mit `EE` und Meldungszeile in Pass 3). Früher stand in 3.1 nur die Form `;*** (<Pass>) Fehler: …`.
  Die vollständige Übersicht steht jetzt als Tabelle in Abschnitt 3.1.
- **Belegungsprüfung:** Der Assembler meldet in Pass 3 Adressen, die von mehr als einer Anweisung beschrieben werden
  (`Adresse … doppelt belegt`). Beschrieben jetzt in Abschnitt 3.1.
- **Ausdrücke:** Rangfolge (`*` `/` vor `+` `-`), Auswertung von links nach rechts, ganzzahlige Division zur Null hin, Division durch 0 als Fehler,
  Vorzeichen nur am Anfang, keine Klammern und Leerzeichen. Beschrieben jetzt nach der Grammatik in Abschnitt 2.
- **`dt` und Backslashes:** Früher stand, die Zeichen „\" seien nur bei Leerzeichen im Text oder führendem `#` nötig. Tatsächlich sind Leerzeichen im Text
  auch ohne „\" zulässig; nötig sind sie bei führendem `#`, bei `;` im Text und bei führenden bzw. abschließenden Leerzeichen (3.5).
- **Mnemonische Operationscodes:** `add`, `sub`, `ld`, `jmp`, `stopp` und `nop` werden vom Assembler mit vorläufigen Platzhalter-Codes akzeptiert; als unvollendeter Ansatz
  beschrieben in Abschnitt 2 (nach der Grammatik).
- **Nullwort:** `dw 0` erscheint in der Objektdatei als `<adresse>: 0.`, `dbn` je Wort als `00 0.` (3.2, 3.3).
- **Unbekannte Optionen** (z. B. `-x`) werden ohne Meldung ignoriert (Abschnitt 2).
- **`.mqo`:** Inhalt genauer beschrieben (Abschnitt 3.1, Dateiliste).
- **Verzeichnisübersicht (1.1):** ergänzt um `asm_alle.sh`, `asm_aufraeumen.sh`, `Projekt_2`, `Claude`, `Claude_bsp_reassemblierung` und die weiteren Unterordner von `Projekt_1`; die beiden Skripte sind kurz beschrieben.
- **Beispiel 5.1:** Hinweis, dass die Projektdatei `bsp_5_16.asm` eine veränderte Fassung des abgedruckten Beispiels ist.
- **Arbeitsverzeichnis:** `c82ass.sh` ruft `./_Linux/c82ass` relativ auf. Der Aufruf muss daher aus dem Verzeichnis `Assembler`
  erfolgen. Dort werden auch `projekdetails` und (zuerst) `c82ass.makros` gesucht.
- **`projekdetails`:** enthält die Zeilen `-p <Projektverzeichnis>` und `-s <Datei>` (der Dateiname so, wie angegeben, ohne
  ergänzte Endung). Fehlt `-p` oder `-s` im Aufruf, wird der gespeicherte Wert benutzt. Beim Wechsel des Projektverzeichnisses
  wird die bisherige Datei als `projekdetails.<altes Projekt>` gesichert; Schrägstriche im Projektnamen werden dabei durch `_`
  ersetzt (z. B. `projekdetails.Projekt_1_bsp_5.16`).
- **Dateiendung bei `-s`:** Hat der Name keinen Punkt oder keine Endung mit genau drei Zeichen, wird `.asm` angehängt
  (`bsp_5.17_Oktaldruck` wird zu `bsp_5.17_Oktaldruck.asm`). Eine dreistellige Endung wie in `x.v10` wird dagegen als Endung
  behandelt.
- **Fehlerlisting:** Fehler stehen im Listing als `;*** (<Pass>) Fehler: …`. Danach folgt `Abbruch wegen Syntaxfehler.`. Bei
  Fehlern in Pass 3 können `.obj`, `.mqo` und `.dmp` trotzdem teilweise entstehen und sind dann nicht verwendbar.
- **Objektcode-Kennzeichen:** `start <zahl>` erzeugt `21 0000 <zahl>`, `equ` (auch `equ10/40/100`) und `db` erzeugen `20 …`,
  `dz`, `dt`, `dto`, `dtm` erzeugen `00 <code> 030`; die Objektdatei endet mit einer Zeile `/`.
- **Makroparameter:** Formale Parameter sind `$1` bis `$9`. Mehr als 9 Parameter in der Kopfzeile (Anzahl oder Namensliste) meldet der Assembler als Fehler.
  Ein Makro, das sich selbst aufruft, meldet `Rekursiver Macro-Aufruf von: <name>`. Eine falsche Parameteranzahl beim Aufruf
  ist ein Fehler.
- **Prüftypen für `$PRx`:** `$TYPADR`, `$TYPKON` und `$TYPABS` (Beschreibung in Abschnitt 4). Früher wurde nicht der beim
  Aufruf übergebene Wert geprüft, sondern der Text `$TYPADR` selbst; die Prüfung hatte keine Wirkung, und bei jedem Makro mit
  Typangabe erschienen Debug-Zeilen (`!!!!…  pruefliste …`). Beides ist im Quellcode behoben. Folge: Aufrufe, die bisher
  unbemerkt falsche Werte übergaben, melden jetzt einen Fehler, z. B. `TEST 123` (Zahl statt Label). In `Proj_FeldSortieren/code_wdhl_bef.asm` steht inzwischen
  der gültige Aufruf `TEST i`.
- **Mitgelieferte Makros in `c82ass.makros`:**

| Makro | Parameter | Zweck |
|---|---|---|
| `WRZL` | – | `dz $wrzl` und `ANWAHL 4700` |
| `KB`, `GB` | – | `dz $inkb` bzw. `dz $ingb` (Umschaltung Klein-/Großbuchstaben) |
| `ANWAHL` | 1 (Kanal) | `030 0xxxx` für Zeichenkanäle (4000…4700, K0…K7, LSL1, LSL2, LKL1, LKS1, LSS1, SW1I, SW1O, SW2O, KONI) |
| `TANWAHL` | 1 | `030 05x00` für Zusatztrommeln (5100…5400, ZTR1…ZTR4) |
| `TROUT` | 2 (Haupttrommeladresse, Zusatztrommeladresse) | `032 $2` und `401 $1` |
| `TRIN` | 2 (Zusatztrommeladresse, Haupttrommeladresse) | `032 $1` und `461 $2` |
| `WDHL` | 5 (Löschen JA/NE, Resultatsbehandlung LI/RE/ZL/OHNE, Operation KON/ADD/SUB/BADD, Anzahl 1…32, Adresse) | Wiederholungsbefehl |
| `ARRAY_LOAD`, `ARRAY_STORE`, `ARRAY_VGL` | 3 (Arrayadresse, Indexvariable, Adresse des erzeugten Befehls) | bilden Lade-, Speicher- bzw. Vergleicherbefehl für `array[index]` |
| `ARRAY_SWAP` | 4 (Arrayadresse, Indexvar1, Indexvar2, Arbeitsspeicher) | vertauscht zwei indizierte Arrayelemente |
| `MACHE_ADRESSEINHEIT` | 2 (Werteadresse, Zieladresse) | Wert laden, 9-mal links schieben, speichern |
| `MACHE_ADRESSEINHEIT2` | 3 (Werteadresse, Zieladresse, Anzahl) | wie oben mit Wiederholungsbefehl |
| `TEST` | 1 | Testmakro für die Typprüfung `$TYPADR` |

### 6.3 Auffälligkeiten im Assembler (vermutlich Fehler im Programm, nicht in der Dokumentation)

1. **`dbn` (behoben im Quellcode, Schritt 1):** Die Ausgabeschleife in Pass 3 benutzt als Schleifenvariable wieder `i` und verdeckt damit den Zeilenindex. Folge: Im
   Listing (`.dmp`, STDOUT) und in der `.test` erscheinen zusätzliche, fremde Zeilen (z. B. `start` oder das vorangehende `db`)
   an der Adresse des `dbn`. Außerdem wird der Befehlszähler in der Schleife nicht erhöht, die `.obj` enthält deshalb
   `dbn 3` als dreimal `0010: 00 0.` mit derselben Adresse. Beispiel: `a: db 010` / `b: dbn 3` / `c: dw 1`. Nach der Korrektur erscheinen die Folgeworte als `0011: 00 0.` und `0012: 00 0.` mit aufsteigenden Adressen und ohne fremde Zeilen.
2. **Subtraktion und Vorzeichen bei `dw` (behoben im Quellcode, Schritt 2):** Früher speicherte `dw -5` den Wert 5 und
   `dw 5-7` ebenfalls 5, `dw 0-5` erzeugte eine 22-stellige Oktalzahl. Ursachen: Ein Ausdruck aus Ziffern und `-` wurde als eine
   einzige Zahl gelesen, ein führendes Vorzeichen ging bei der Auswertung verloren, und es wurde mit vorzeichenlosen 64-Bit-Werten
   gerechnet. Jetzt wird vorzeichenbehaftet gerechnet, ein führendes `-` oder `+` gilt als Vorzeichen, und ein Operator ohne
   rechten Operanden (`dw 5-`) meldet `Operand … ist ungültig`. Negative Ergebnisse werden als 33-Bit-Wort (11 Oktalziffern) im
   **Zweierkomplement** ausgegeben: `dw -5` ergibt `77777777773`, `dw 5-7` ergibt `77777777776`. Das entspricht der Darstellung
   der C8205 (negative Zahlen als Zweierkomplement z̃ = 2³³ − z, z₀ = 1; siehe `C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md`).
3. **Absturz bei ungültigem Makro-Label (behoben im Quellcode, Schritt 3):** Früher brach der Assembler bei einem Makro mit
   einem Label im Format `name%:` (z. B. dem Beispiel `start%:`) ohne Label am Aufruf mit `double free or corruption` ab
   (Rückgabecode 134, nicht 16). Ursache: Die Fehlerzeile wurde in einen zu kleinen Zwischenspeicher geschrieben und
   überschrieb außerdem die Folgezeile des Makros. Jetzt wird hinter der fehlerhaften Zeile eine Fehlerzeile eingefügt, alle
   anderen Zeilen bleiben unverändert, und der Lauf endet regulär mit Rückgabecode 16. Der Hinweistext nennt jetzt das richtige
   Format `ML` + vier Ziffern + `%` (z. B. `ML0004%:`) statt `ML01234%`.
4. **`projekdetails` (behoben im Quellcode, Schritt 4, Datei `ca82_standards.c`):** Zwei Fehler, beide im Lauf bestätigt.
   (a) Beim Sichern wurden Schrägstriche im Projektnamen durch `_` ersetzt, beim Zurückholen für das neue Projekt aber nicht.
   Bei Pfaden wie `Projekt_1/bsp_5.16` blieb die gesicherte Datei deshalb ungenutzt, das gespeicherte `-s` ging verloren.
   Jetzt wird der Name in beiden Fällen gleich gebildet. (b) Wurde `-s` aus `projekdetails` gelesen und stand dort ohne
   Endung (z. B. `-s f`), ging die Endung `.asm` verloren, weil der Zeilenumbruch noch davor stand. Der Aufruf ohne Parameter
   endete dann mit `Die Datei …/f für Parameter -s existiert nicht`. Jetzt wird der Zeilenumbruch vorher entfernt. Ein Aufruf
   ohne Parameter benutzt damit wie in Abschnitt 6.2 beschrieben die zuletzt gespeicherten Werte, auch wenn `-s` ohne Endung
   angegeben wurde.
5. **Wertebereich bei `dw` (behoben im Quellcode, Schritt 6):** Früher wurden Werte außerhalb des 33-Bit-Wortes angenommen und
   mit mehr als 11 Oktalziffern ausgegeben (z. B. `dw 0100000000000`, `dw 8589934592`, `dw 99999999999999999999`). Jetzt gilt der
   Bereich −2³² bis 2³³−1 (vorzeichenlos bis `77777777777`, negativ im Zweierkomplement). Alles darüber oder darunter meldet
   `bei Operand: <wert> Operand ist ungültig`.
6. **Ungültige Labels (behoben im Quellcode):** Früher akzeptierte die Prüffunktion `isValidLabel` ein Label mit führender Ziffer
   (`1abc:` stand in der `.sym`). Labels mit unzulässigen Zeichen (`ab-c:`, `x.y:`, `äb:`) wurden beim Anlegen der Symboltabelle
   ohne Meldung übersprungen und fehlten in der `.sym`. Jetzt wird die führende Ziffer abgelehnt, und jedes unzulässige Label
   meldet `Label "<name>:" ist unzulaessig …` mit Zeilennummer im Listing. Geprüft mit `1abc:`, `ab-c:`, `x.y:`, `äb:` (Fehler) und
   `ok_1:` (steht in der `.sym`). Die mitgelieferte Datei `_Linux/c82ass` muss dafür neu aus `Sourcecode/` gebaut werden
   (`make_c82ass.sh`); ein älteres Binary zeigt noch das alte Verhalten.
7. **Zeilen hinter `end` bei vorhandenen Literalen (behoben im Quellcode):** Früher wurden bei einem Programm mit mindestens
   einem Literal (`#…`, `@…`) alle Zeilen hinter `end` ignoriert: `abs`- und `equ`-Definitionen fehlten in `.log`,
   Symboltabelle und `.sym`, und ein dort definiertes `abs`-Symbol führte beim Benutzen zu `Adresse (3) ist ungültig`. Ohne
   Literal wurden diese Zeilen ausgewertet. Außerdem erschien in Läufen mit Fehlern, aber ohne Literal, fälschlich die Warnung
   `end - Anweisung fehlt`. Ursache: Pass 1 setzte die Kennung „end gesehen“ nur innerhalb der Literalschleife und verließ danach die
   Zeilenschleife. Jetzt werden die Literale einmalig beim ersten `end` ausgegeben und die Zeilen dahinter immer ausgewertet
   (Abschnitt 3.10). Die mitgelieferte Datei `_Linux/c82ass` muss dafür neu aus `Sourcecode/` gebaut werden (`make_c82ass.sh`).
8. **Falsche Zahl in der Meldung bei falscher Makro-Parameterzahl (behoben im Quellcode):** Die Meldung
   `erwartet N Parameter, aber M wurden übergeben!` nannte für M statt der übergebenen Parameter einen Zeilenzähler (meist 0).
   Beispiel: Makro mit `MACRO 2`, Aufruf `A2 x` meldete „… aber 0 wurden übergeben“. Jetzt steht dort die tatsächliche Zahl
   (hier 1). Verhalten und Rückgabecode (16) sind unverändert.
9. **Fehlertexte (behoben im Quellcode):** (a) Die Meldungen zu `dt`/`dto`/`dtm` mit `#` am Anfang des Operanden und zu einem
   `#`-Literal in einer Assembleranweisung hatten leere Angaben (`bei Operand:  Operand …` und `in Zeile: ``). Jetzt stehen dort der
   Operand und die Quellzeile. (b) `db -1` und `dbn -1` meldeten „Programmzählerüberlauf über 7777“; jetzt:
   `db: Operand "-1" darf nicht negativ sein.` (c) Bei einem Makro mit mehr als 9 Parametern stand der Doppelpunkt des Makronamens
   doppelt (`Makro A3:: …`). Verhalten und Rückgabecodes sind unverändert.
10. **Operandenprüfung bei `db` und `dbn` (behoben im Quellcode):** Früher wurde ein ungültiger Operand stillschweigend verarbeitet:
    `db abc` reservierte 0 Worte, `db 5x` 5 Worte, `db 3+1` 3 Worte, `db 09` 0 Worte, `db #5` 0 Worte, ein fehlender Operand ebenfalls 0 Worte.
    Alle folgenden Adressen waren damit verschoben, der Lauf endete mit Rückgabecode 0. Jetzt gilt `<zahl>` wie in der Grammatik
    (Oktalzahl mit führender 0 oder Dezimalzahl, höchstens 010000); alles andere meldet z. B.
    `db: Operand "abc" ist keine gültige Zahl (Oktalzahl mit führender 0 oder Dezimalzahl).`, `… ist zu groß …` oder
    `db: Operand fehlt (erwartet wird eine Zahl).` Gültige Operanden verhalten sich unverändert.
11. **Farbcodes in der `.dmp` bei Fehlerläufen (behoben im Quellcode):** Bei Fehlern in Pass 3 (z. B. `dw 5-`, unbekanntes Symbol) enthielt die
    Datei `.dmp` die ANSI-Escape-Sequenzen der Bildschirmfarben (um die Marke `EE` und die Meldungszeile), weil dasselbe Listing auf den
    Bildschirm und in die Datei geschrieben wurde; zusätzlich waren die Spaltenbreiten von diesen unsichtbaren Zeichen verfälscht. Jetzt wird
    die `.dmp` ohne Farbcodes geschrieben und die Spalten werden aus dem sichtbaren Text berechnet. Die Bildschirmausgabe und alle
    fehlerfreien `.dmp`-Dateien sind unverändert.
12. **Prüfungen beim `<adressausdruck>` von `da` und `@`-Literalen (behoben im Quellcode):** Die in der Grammatik genannten Einschränkungen
    wurden nicht geprüft: `da -1` ergab `37777777000`, `da x+y` (zwei Symbole) wurde ausgewertet, `da x-5` und `da 4096` ergaben Adressen außerhalb
    von 00000…07777, und bei einem führenden Vorzeichen oder einem fehlenden Operand (`da 5-`, `da x+*2`) lief die Berechnung mit einem nicht
    gesetzten Wert (Ergebnis unbestimmt). Jetzt meldet Pass 3 diese Fälle als Fehler (Zeile `EE` mit Meldungszeile). Gültige Ausdrücke sind
    unverändert; alle 118 Beispiele ergeben identische Ausgabedateien.
13. **Dezimalzahlen ab 8 bei `da` (behoben im Quellcode):** `da 10` ergab Adresse 12 (dezimal gelesen), `da 100` die Adresse 0220, `da 4095`
    einen Wert außerhalb des Adressbereichs. Ursache: Eine Dezimalzahl wurde zuerst in eine Oktalzeichenkette umgewandelt und dann wieder
    als Dezimalzahl gelesen. Oktalzahlen mit führender 0 und Zahlen unter 8 waren nicht betroffen. Jetzt werden Dezimal- und Oktalzahlen richtig ausgewertet.
14. **`ANWAHL K4` … `K7` wurden abgelehnt (behoben in der Makrodatei):** Das Makro `ANWAHL` in `c82ass.makros` hat Zweige für `K4` bis `K7`
    (Codes 04300, 04200, 04100, 04000), aber die Prüfliste `$PR1` enthielt nur `K0` bis `K3`; `ANWAHL K5` meldete deshalb
    `Wert "K5" steht nicht in der Pruefliste`. Jetzt steht `K0 … K7` in der Prüfliste (Tabelle in 6.2 und Beispiel in Abschnitt 4 entsprechend).
    Der Assembler selbst ist davon nicht betroffen, es genügt die neue `c82ass.makros`.
