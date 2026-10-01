** Bedienpult mit Schaltern **

Im physischen Bedienpult des Rechners C8205 sind sowohl Schalter, Eingabetasten und Lampen,
die die Flag-Zustände anzeigen, lokalisiert.
Im Rechner werden die Schalterzustände in gleichnamigen Flags gespeichert als 0/1-Werte.


## Netzschalter

Der Netzschalter schaltet die Stromversorgung des Rechners ein. Das ist Voraussetzung für den Betrieb.


## Schalter "H-R" (Halt – Rechnen)

Schalter mit zwei gegeneinander verriegelten Tasten "H" und "R" (immer nur eine der beiden gedrückt).
In Stellung "H" geht der Rechner in den Halt- (Stopp-)Zustand über.

"H" und "R" sind gegeneinander verriegelt. Die Tasten "E", "M", "G", "Ü" und der Schalter "SW" lassen
sich nur bei Stellung "H" betätigen. Die Taste "ST" ist elektronisch verriegelt.
Durch Einrasten von "H" kann die Befehlsabwicklung unterbrochen werden; unabhängig vom Zeitpunkt des
Eingriffs im Phasenablauf wird erst nach der nächsten Phase III gestoppt.
Durch Drücken von "R" wird diese Sperre aufgehoben, die Abarbeitung eines Programms wird fortgesetzt.


## Tasten E, G, M, Ü, SW, ST

Diese Tasten/Schalter sind – bis auf "ST" – nur bei Schalter "H-R" in Stellung "H" wirksam.

- **Taste "E" – Einzelschritt**
  Mit "E" kann eine Befehlsfolge in Einzelschritten abgearbeitet werden. Beim Niederdrücken werden
  entsprechend dem Phasenablauf die Phase IV und die Phase I freigegeben; solange "E" gedrückt bleibt,
  steht der Automat vor Phase II. Bei verkürzten Gruppen- bzw. Wiederholungsbefehlen mit X-Abbruch wird
  bei gedrückter "E"-Taste das Einschalten von Phase II nicht verhindert.
  Beim Loslassen von "E" werden Phase II und Phase III durchlaufen; danach stoppt die Abarbeitung wieder.
  Erneutes Anschlagen löst den nächsten Schritt aus.

- **Taste "G" – Generallöschen**
  Beseitigt einen programmierten Stopp sowie einen eventuellen Überlauf und löscht das Befehlsregister
  (Einstellung "0000 000" = unbedingter Sprung nach Speicherplatz Null). Wählt zusätzlich Kanal K0 an.
  Kein Einfluss auf Akkumulator- und Befehlszählerinhalt.

- **Taste "M" – Manuell**
  (Für den Interpreter hat M nur die zwei Stellungen "gedrückt" und "losgelassen"; das Antippen "M" in einer
  Tastenfolge ist gleichbedeutend mit M gedrückt und sofort losgelassen, z. B. Fall 4 unter 4.1: H, M, R.)
  Verknüpft den Inhalt des Operationsregisters disjunktiv mit der Operation "025" (Sprung mit
  Rückkehrabsicht). Nach vorherigem "G" ergibt sich damit "0000 025". Bei gedrückter "M"-Taste und
  Betätigung von "E" wird die Befehlsentnahme in Phase II verhindert.

- **Taste "Ü" – Übertrag**
  (Nur bei Schalter H-R in Stellung "H" wirksam, sonst ohne Wirkung.)
  Stellt im Adressregister die Adresse "7777" (oktal) ein und verknüpft den Inhalt des
  Operationsregisters disjunktiv mit der Operation "240" (Transport).

- **Schalter "SW" (Stellungen "T"/"SW", daher auch als "T-SW" bezeichnet) – Tastatureingabe/Schreibwerkeingabe**
  Unterscheidet beim Anwahlkanal K0 zwischen Tastatur- und Schreibwerkeingabe. Drücken von "SW" setzt
  Flag SW; Lösen (Stellung "T") löscht Flag SW und setzt stattdessen Flag T – "T" und "SW" sind
  alternativ. Bei Benutzung des Schreibwerks muss "SW" gedrückt sein, Tastatureingabe nur bei Stellung
  "T". Der Schalter selbst hat keinen Einfluss auf die Anwahl eines peripheren Gerätes.
  ⚠ Dieselbe Schalterstellung "SW" hat einen weiteren Effekt, der erst im Abschnitt „Schalter LS und SW"
  beschrieben wird (Sperre der Schreibwerkausgabe) – siehe dort.

- **Taste "ST" – Start**
  (Für den Interpreter: nicht an Stellung H gebunden; ohne US/BS ohne Wirkung; Wirkung OR := OR ∨ 240, AR bleibt,
  US wird gelöscht; BR ist danach aufgestellt und wird durch E oder R ausgeführt.)
  Verknüpft den Inhalt des Operationsregisters disjunktiv mit der Operation "240". Elektronisch
  verriegelt: nur wirksam, wenn der Rechner im Zustand "Bedingter Stopp" oder "Unbedingter Stopp" steht.


## Eingabetasten

Umfassen die Zeichen 0…9, +, −, „,", „.", „:", B, D, ZR, WM, IS, IB.
Betätigbar nur, wenn:
  - Kanal K0 angewählt ist,
  - Schalter "SW" in Stellung "T" steht,
  - ein Eingabe-Halt-Befehl im Befehlsregister steht.

**Wirkung:** Ist ein Eingabebefehl aufgestellt, stoppt der Automat nach Phase III. Beim Anschlagen wird
die dem Zeichen zugeordnete Eingabeverschlüsselung (gemäß FS- bzw. R300-Code) disjunktiv mit dem Inhalt
des Adressregisters verknüpft; danach wird die Sperre durch Umstellung des Eingabebefehls aufgehoben.
Die Verschlüsselung der einzelnen Tasten steht in den (später zu besprechenden) Codetabellen.
"IB" und "WM" sind beim Arbeiten im Fernschreibcode wirkungslos.

Sonderbedeutung einzelner Tasten:
  - **ZR** – Zwischenraum, identisch mit Leerzeichen
  - **WM** – Wortmarke, identisch mit dem Code für Tabulator (TAB)
  - **IS** – Irrung Satz (gemäß Codetabelle)
  - **IB** – Irrung Block (gemäß Codetabelle)
  - **B** (nicht der Buchstabe B) – Sondertaste für Programmbaustein-Ansprung des BIS, nicht weiter benötigt
  - **D** (nicht der Buchstabe D) – Sondertaste für Programmbaustein-Ansprung des BIS, nicht weiter benötigt


## Kanalauswahltasten

Jede Kanalauswahltaste wählt einen Kanal gleichzeitig für Ein- und Ausgabe aus, wobei Eingabe- und
Ausgabegerät unterschiedlich sein können; ob der Eingabe- oder der Ausgabeaspekt genutzt wird,
bestimmt der abgearbeitete Befehl. Maßgebend ist der Moment des Drückens: Das entsprechende Flag wird
auf 1 gesetzt, die Flags der anderen drei Kanäle auf 0.

Besonderheit K0: Diese Taste hat kein eigenes Flag, sondern die zwei Subflags "T" (Tastatur) und "SW"
(Schreibwerk statt Tastatur) sind ihr zugeordnet. Beim Drücken von K0 ist der Zustand des Schalters "SW"
(s. o., Stellungen T/SW) maßgeblich: ist "SW" gedrückt, wird beim Drücken von K0 Flag SW gesetzt, sonst
Flag T. Anstelle der Tasten kann die Kanalanwahl auch per Befehl erfolgen; er berücksichtigt den
Schalterstatus SW analog.

| Taste | Anwahlverschlüsselung (programmiert) | Gerät |
|-------|---------------------------------------|-------|
| K0    | 4700 030 | Tastatureingabe* / Schreibwerkeingabe* |
| K1    | 4600 030 | Leser 1 / Lochbandstanzer |
| K2    | 4500 030 | Leser 2 / Schreibwerkausgabe |
| K3    | 4400 030 | frei |


## Selektoren: Schalter "SP" und "BS"

SP und BS sind einrastende Schalter: Gedrückt bleiben sie eingerastet, bis ein Mensch sie löst; das gleichnamige
Flag ist 1, solange der Schalter eingerastet ist, und 0, wenn er gelöst ist. Die Taste "G" kann eingerastete
Schalter mechanisch nicht bedienen und ändert deshalb die Flags SP und BS nicht (ebenso wenig H). Zur Definition
einer Tastenfolge genügt: Schalter gedrückt → Flag := 1, Schalter gelöst → Flag := 0.

Die Selektoren umfassen die Schalter "SP" und "BS". Ihre Stellungen werden als Bedingungen für die
Befehle "Bedingter Sprung mit Rückkehrabsicht" (SP) und "Bedingter Stopp" (BS) interpretiert; die
Bedingung ist erfüllt, wenn der entsprechende Schalter gesetzt ist.
Bei ausgeführtem "Bedingten Stopp" bleibt der Automat nach Phase III stehen; durch Lösen des Schalters
"BS" kann die Sperre aufgehoben werden.


## Schalter "LS" und Stellung "SW" (Lochbandstanzer / zusätzlicher Effekt des Schalters SW)

"LS" ist nur für den physischen Rechner C8205 von Bedeutung; bei der interpretativen Nachbildung der
Befehlsverarbeitung spielt er keine Rolle. Bei gesetztem "LS" läuft der Motor des Lochbandstanzers
ständig (sinnvoll bei Stanzvorgängen in kurzen Abständen unterhalb der 3-Sekunden-Abschaltverzögerung);
bei nicht gesetztem "LS" läuft der Motor nicht, ein Stanzvorgang beginnt dann erst nach Ablauf der
Einschaltverzögerung (Hochlauf).

"SW" bezeichnet hier keinen zweiten Schalter, sondern die bereits oben beschriebene Stellung "SW" des
Schalters "SW"/"T-SW". Auf die Schreibwerk**ausgabe** über Kanal K2 hat die Stellung dieses Schalters
KEINEN Einfluss; die Ausgabe über K2 ist unabhängig davon jederzeit möglich. Die Stellung "SW" betrifft
ausschließlich die Eingabeseite (Zeicheneingabe über das Schreibwerk an Kanal K0) – siehe dazu Datei
"C8205-Interpreter-Lochstreifenleser.md", Abschnitt A5.


## Bahnsperrenschalter

Räumlich und bedientechnisch am Bedienpult angesiedelt (rückseitig an der Tastatur-Anzeige-Einheit),
inhaltlich aber von der Magnettrommel ausgewertet – daher vollständig im Dokument zur Magnettrommel
beschrieben (Abschnitt "Bahnsperrenschalter" in C8205-Interpreter-Magnettrommel.md).


## Tastenfolge-Token (Schreibweise der Bedienhandlungen in einer Testdefinition)

Eine Tastenfolge beschreibt die Bedienhandlungen am Pult, die den Ausgangszustand vor dem Eintritt in den
Befehlsablauf festlegen (Dokument "C8205-Interpreter-Durchführung_eines_Tests.md", Abschnitt 3). Sie besteht aus
Token, die durch Leerzeichen getrennt in einer oder mehreren Zeilen stehen; `#` beginnt einen Kommentar bis zum
Zeilenende. Groß-/Kleinschreibung ist gleichgültig. Die Wirkungen sind die der oben beschriebenen Tasten und Schalter.

| Token | Bedeutung und Wirkung |
|---|---|
| `H` | Schalter H-R auf "H": Flag H := 1 |
| `R` | Schalter H-R auf "R": Flag H := 0; zusätzlich US := 0. Der Befehlsablauf beginnt (Startpunkte: s. unten) |
| `G` | Generallöschen (nur bei H): alle Flags außer H, T, BS und SP := 0 (BS und SP sind eingerastete Schalter, G kann sie mechanisch nicht lösen); AR := 0000, OR := 000 (BR = "0000 000"); K0 wird angewählt (T := 1, bei gedrücktem Schalter SW: SW := 1); BZ und AC bleiben unverändert; danach US := 1 (wird durch ST oder R wieder gelöscht) |
| `M+` (auch `M-drücken`, `M-gedrückt-halten`) | M gedrückt halten (nur bei H): OR := OR ∨ 025 |
| `M-` (auch `M-loslassen`) | M loslassen. Wurde unter gehaltenem M kein E betätigt, bleibt BR = ⟨AR⟩ 025 aufgestellt. Wurde mindestens ein E betätigt, entfällt der Beitrag 025 im OR (übrige Anteile, z. B. von Ü, bleiben) |
| `M` | Antippen, gleichbedeutend mit `M+` und sofort danach `M-` |
| `E` | Einzelschritt (nur bei H). Ohne M: Phase IV und I, dann Phase II und III, danach Halt (Halt-Punkt vor Knoten 19). Steht der Automat nach einem E unter M vor Phase II, beginnt E bei Phase II. Unter gehaltenem M: Phase II entfällt; BZ := BZ+1, AR := BZ, der AC enthält im Adressfeld den Wert BZ+1 (übrige Stellen 0) |
| `Ü` | Übertrag (nur bei H, sonst ohne Wirkung): AR := 7777, OR := OR ∨ 240; BR ist aufgestellt und noch nicht ausgeführt |
| `ST` | Start (nicht an H gebunden, aber nur bei US oder BS wirksam, sonst ohne Wirkung): OR := OR ∨ 240, AR unverändert, US := 0; BR ist aufgestellt und noch nicht ausgeführt |
| `SW=1` (auch `SW+`, `SW-drücken`) | Schalter SW gedrückt: Flag SW := 1, T := 0 |
| `SW=0` (auch `SW-`, `SW-loslassen`) | Schalter SW gelöst: Flag SW := 0, T := 1 |
| `BS=1`, `SP=1` (auch `BS+`, `SP+`) | Selektorschalter gedrückt und eingerastet: gleichnamiges Flag := 1 |
| `BS=0`, `SP=0` (auch `BS-`, `SP-`) | Selektorschalter gelöst: gleichnamiges Flag := 0 |
| `K0` … `K3` | Kanalauswahltaste: Flag des gewählten Kanals := 1, die Flags der anderen drei Kanäle := 0 (K0: T oder SW je nach Schalter SW) |

Hinweise:
- `SW` muss vor `G` gesetzt werden, weil `G` daraus für K0 das Flag T oder SW ableitet.
- Die Eingabetasten (0…9, +, − usw.) gehören nicht in die Tastenfolge; sie werden als K0-Eingabe während des Ablaufs bedient.
- Eine Tastenfolge wird bis zur Wirkung der dadurch aufgestellten Instruktion vorausinterpretiert. Sie muss den
  Ausgangszustand vollständig definieren (Gültigkeitsregeln: Dokument "C8205-Interpreter-Durchführung_eines_Tests.md",
  Abschnitte 3.3 und 5). Sie endet mit `R` oder im Halt (H gesetzt).
- **Startpunkte nach `R`:** Ist keine Instruktion in BR aufgestellt (z. B. nach `H G R` oder `H G M+ E … E M- R`),
  beginnt der Ablauf bei Konnektor B mit dem in BZ stehenden Wert. Ist BR aufgestellt und noch nicht ausgeführt
  (nach `Ü`, `ST`, `M` ohne E oder nach `E` ohne M), beginnt der Ablauf bei Knoten 19 (Ausführung von BR).
  Endet die Tastenfolge ohne `R`, bleibt der Rechner im Halt; das Ergebnis ist der Zustand nach dem letzten Schritt.

## Typische Funktionsabläufe unter Benutzung der Schalter und Tasten (Eingriffsmöglichkeiten)

### 4.1 Beseitigen der Betriebszustände "US", "BS", "FÜ", "FE"

Zustand "Unbedingter Stopp" (US) kann geändert werden durch:
  1. a) Schalter "H-R" → "H"; b) Taste "G"; — Programm wird unterbrochen.
  2. a) Schalter "H-R" → "H"; b) Taste "G"; c) Taste "ST" — US wird übergangen (Sprung zur Adresse des
     US-Befehls).
  3. a) Schalter "H-R" → "H"; b) Taste "Ü"; c) Schalter "H-R" → "R" — US wird übergangen (Speicherplatz
     7777 oktal wird angesprungen/geändert).
  4. a) Schalter "H-R" → "H"; b) Taste "M"; c) Schalter "H-R" → "R" — Sprung zur Adresse des US-Befehls,
     Akkumulatorinhalt wird der Resultatbehandlung unterworfen.

Zustand "Bedingter Stopp" (BS) verhält sich wie US (gleiche Fälle 1–4), zusätzlich: Lösen des Schalters
"BS"; bei Beseitigung gemäß Fall 4 wird der nächste Befehl abgearbeitet.

Zustand "Überlauf" (FÜ) wird beseitigt durch:
  1. a) Schalter "H-R" → "H"; b) Taste "G" — Programm wird unterbrochen.
  2. a) Schalter "H-R" → "H"; b) Taste "E" gedrückt halten; c) Taste "G"; d) Taste "E" loslassen — nur
     der Überlauf wird gelöscht (Generallöschen bei gedrückter Einzelschritt-Taste).

Zustand "Fehler bei Eingabe" (FE) kann nur durch Generallöschen ("G") aufgehoben werden.

### 4.2 Transport des Akkumulatorinhaltes nach Speicherplatz 7777 (oktal)
a) Schalter "H-R" → "H"; b) Taste "G"; c) Taste "Ü"; d) Taste "E" — der aufgestellte Befehl "7777 240"
wird durch d) ausgeführt, der Akkumulatorinhalt wird nach 7777 (oktal) transportiert.

### 4.3 Transport des Befehlszählerinhaltes nach dem Akkumulator
a) Schalter "H-R" → "H"; b) Taste "G"; c) Taste "M" gedrückt halten; d) Taste "E"; e) Taste "M"
loslassen; f) Schalter "H-R" → "R".
Danach steht im Akkumulator die um 2 Einheiten erhöhte Adresse des nächsten abzuarbeitenden Befehls
(meist ein Sprung in ein Druckprogramm). Wird in Schritt d) "E" zweimal angeschlagen, steht die um 3
Einheiten erhöhte Adresse im Akkumulator, Speicherplatz "0002" wird als nächster Befehl aufgestellt.
Alternativ kann im Haltzustand durch Niederdrücken von "E" (außer bei X-Befehlen) der
Befehlszählerstand im Adressteil des Befehlsregisters sichtbar gemacht werden.

### 4.4 Manueller Ansprung einer Speicherzelle
1. Ansprung des Platzes "0000": a) Schalter "H-R" → "H"; b) Taste "G"; c) Schalter "H-R" → "R".
2. Ansprung eines beliebigen Speicherplatzes n: a) Schalter "H-R" → "R"; b) Taste "G"; c) Taste "M"
   gedrückt halten; d) Taste "E" n-mal anschlagen; e) Taste "M" loslassen; f) Schalter "H-R" → "R".

### 4.5 Hinweise zum "Kleinen Eingabeprogramm"
Ermöglicht die Eingabe von Befehlen, Zahlen und Hilfsadressen über ein einfaches Leseprogramm (liegt auf
Spur 0, wird über Speicherplatz "0002" angesprungen, bei gesetztem Sperrschalter gegen Überschreiben
gesichert; nur über eine Serviceeinheit bei völlig gelöschtem Speicher nutzbar). Verarbeitet nur die
Zeichen "0", "1", Punkt ".", Doppelpunkt ":" und Zwischenraum "ZR". Worte werden entsprechend ihrer
dualen Darstellung eingegeben (Beginn beim ersten von Null verschiedenen Bit möglich) und im
Akkumulator aufgebaut. "." und ":" dienen als Schlusszeichen: ":" speichert die aufgebaute Information
als Befehl auf Speicherplatz "7723" (Leitbefehl); "." führt den Leitbefehl aus (bei Transportbefehl
"a1 a2 a3 a4 240" wird das zuvor aufgebaute Wort nach Zelle a1 a2 a3 a4 abgespeichert) und erhöht
dessen Adresse um 1, sofern kein Sprungbefehl vorliegt. "ZR" löscht die im Akkumulator aufgebaute
Information, solange noch kein Schlusszeichen gegeben wurde.
