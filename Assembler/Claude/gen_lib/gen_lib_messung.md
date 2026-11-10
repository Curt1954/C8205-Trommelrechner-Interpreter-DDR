# c82gen – Messung und Regeln für den Einsatz

Version: 0.01-002

Zweck: belegt, was die Bibliothek `c82gen.py` (0.01-004) gegenüber 0.01-002 und gegenüber von Hand geschriebenen `.asm` spart, und sagt, wann sie sich lohnt. Gemessen am 30.10.2026 im Zip 0.95.7-061 mit `asm_und_test.sh` und dem Abnahmetest des Archivprogramms; alle Zahlen stammen aus Läufen, nicht aus Schätzungen. Einzelheiten zum Archivprogramm (Namen, Ursachenreihe) stehen in `gen_lib_messung_archiv.txt` (keine `.md`).

## Ziel

Die erzeugte `.asm` soll nach den Festlegungen (Handbuch 5.8) nicht länger sein als eine von Hand geschriebene, fehlerfrei laufen, und der Aufwand für Claude (Text, den Claude schreiben muss, Fehlersuche, Testzeit) soll deutlich sinken.

## Was 0.01-003 und 0.01-004 ändern

| Ursache für Mehrzellen in 0.01-002 | Maßnahme seit 0.01-003 | Festlegung |
|---|---|---|
| Nullspur (63 Zellen) für Mehrfachverschiebungen | `schiebe_links/_rechts` über W-Transport 646/644/642 auf Spur 7640; im Archivmodus weiter Nullspur (siehe unten) | 026 |
| eigene Rückkehrzelle plus `000 rueck` je UP | Rückkehrsprung steht am UP-Ende, keine Datenzelle | 010 |
| Konstanten und Adressen als benannte Zellen | Literale `#wert`, `@name` (Assembler führt gleiche zusammen) | 003 |
| `dbn`-Füllung bei Ausrichtung | `db`, außer im Archivmodus; Einzelzellen füllen Lücken zuerst | 023 |
| zwei Eingabetafeln mit Laufzeitwahl | eine Tafel mit festem `011`; zwei Tafeln nur im Archivmodus | 011 |
| Kopfkommentar von Hand | Start-/Ausrichtungskommentar entsteht selbst | 001 |
| Felder ohne `begin/bend` | Felder und Tafeln in `begin/bend` | 027 |

Für Claude: Kommentar ist optional (Standardtext), Kurzidiome `kopiere`, `setze`, `wenn_*`, `unterprogramm` als with-Block, `pragma(zeile)` für Zeilen des Testrahmens, `;#TESTBASIS` bei Archivprogrammen (`schreibe(..., testbasis=adr)`), Warnung bei Arbeitszellen, die gelesen, aber nie gespeichert werden (Falle: im Test steht dort der Trommelstand).

## Schiebespur: Fund beim Abnahmetest (0.01-004)

`Prog(..., schiebespur=…)`: `'w7640'` (Vorgabe im Normalmodus) schiebt mit dem W-Transport auf der Arbeitsspur 7640 nach Festlegung 026, ohne Zellen im Programm. `'nullspur'` (Vorgabe im Archivmodus) schiebt wie 0.01-002 mit 612/616 über eine Spur aus 32 Nullzellen im Programm.

Grund: Ein Archivprogramm läuft unter einem Lader, der die Spur 7640 beim Start löscht und danach selbst mit der W-Addition (616) rechnet, also Nullen dort voraussetzt. Der W-Transport füllt die Spur. Mit `'w7640'` im Archivprogramm brach das Laden (Kommando M) im Abnahmetest mit Unbedingtem Stop im Lader ab, AC = 5 (4 Fehler in 114 Prüfungen); mit eigener Nullspur ist der Test wahr. `'w7640'` im Archiv also nur, wenn der Lader es verträgt. Für BIS-Hilfen, die Nullen auf 7640 voraussetzen, ist das nicht geprüft.

## Zellen

| Programm | von Hand | 0.01-002 | 0.01-004 | Bemerkung |
|---|---|---|---|---|
| sortierung (Vergleichsprogramm) | 54 | – | **52** | Code 38, Daten 9, Literale 5; Test wahr |
| feldmax | – | 38 | **38** | Code 23, Daten 12, Literale 3; Test wahr |
| Archivprogramm Fassung A (Generator) | 2195 (Fassung B) | 2257 | **2120** | Abnahmetest wahr, 114 Prüfungen; mit `'w7640'` 2063, aber Test falsch |
| gen_lib_test (Normalmodus) | – | – | 546 | 91 von 91 Sollwerten, Test wahr |
| gen_lib_test_archiv (Archivmodus, Nullspur) | – | – | 680 | 91 von 91 |
| gen_lib_test_archiv040 (Archivmodus, W-Transport, Ladeadresse 0140) | – | – | 630 | 91 von 91, zweite Tafel |

## Text, den Claude schreiben muss (Erzeugungsaufwand)

| Programm | von Hand (`.asm`) | Generator 0.01-002 | Generator 0.01-004 | erzeugte `.asm` |
|---|---|---|---|---|
| sortierung | 4385 B, 76 Zeilen | – | **2516 B**, 44 Zeilen (−43 % gegenüber Hand) | 3649 B |
| feldmax | – | 1925 B, 54 Zeilen | **1361 B**, 35 Zeilen (−29 %) | 2927 B (vorher 2953 B) |
| Archivprogramm Fassung A | 67692 B | 46560 B (alte Schnittstelle, unverändert) | – | 116594 B (vorher 117581 B) |

Der Generator ist damit rund halb so lang wie die erzeugte `.asm`. Das ist die eigentliche Ersparnis: Claude schreibt den Generator; Kommentar in jeder Zeile (Dateiformat), Adressen, Rückkehrzellen und Prüfblock erzeugt die Bibliothek.

## Laufzeiten

| Schritt | Zeit |
|---|---|
| Generator (Python) sortierung, feldmax | 0,02 bis 0,03 s |
| Generator Archivprogramm | rund 0,25 s |
| `asm_und_test.sh` gen_lib_test (Generator, Assembler, Interpreter, 91 Sollwerte) | 0,9 s |
| Abnahmetest Archivprogramm (16 Fälle) | 33 s mit alter wie neuer Bibliothek |

Die Testlaufzeit bestimmt der Interpreter, nicht die Bibliothek. Eine Verkürzung der Testzeit ist von der Bibliothek nicht zu erwarten; sie spart Schreibaufwand und Fehlersuche.

## Nicht geprüft

- Das Archivprogramm ist mit der alten Schnittstelle (`ztd_py_gen.py`) unverändert geblieben; es nutzt Literale und `begin/bend` nicht (Archivmodus). Eine Umstellung auf die Kurzidiome ist nicht gemessen.
- Parameterzellen im UP (Festlegung 30.10.2026, Handbuch 5.5) kennt die Bibliothek noch nicht; sie entstehen mit `op`.

## Wann lohnt sich der Generator

- Ab etwa 30 Zellen mit Schleife, Feld, Unterprogramm oder Ein-/Ausgabe: Ja. Adressen, Rückkehrzellen, Ausrichtung und `;#PRUEFE`-Block entstehen fehlerfrei aus dem Python-Modell.
- Programme unter etwa 20 Zellen ohne Unterprogramme: `.asm` von Hand ist gleich kurz; kein Generator.
- Abweichungen von den Festlegungen: Ausrichtung im Normalmodus mit `db n` statt `equ` (002), damit die Prüfadressen der Bibliothek feststehen; Archivmodus mit benannten Konstanten statt Literalen (003, lückenfreie `.obj`) und mit eigener Nullspur statt 026.
