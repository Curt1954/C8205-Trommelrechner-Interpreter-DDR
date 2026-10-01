** Überblick und Gesamtaufbau (Wurzeldokument für Rechner und Regelwerk) **

Dieses Dokument fasst die allgemeinen, einführenden Angaben zum C 8205 zusammen, wie sie in den
Übersichtsgrafiken (upload_c8205-1 … upload_c8205-6) enthalten sind, und ordnet die Teilprojekte
(Interpreter, Assembler) ein. Details, die in Teildokumenten ausführlich beschrieben sind, werden hier
nicht wiederholt, sondern nur referenziert (Abschnitt 7).

Die Verzeichnisstruktur des Gesamtprojekts (welcher Pfad was enthält) steht nicht hier, sondern im
Wurzeldokument "C8205-Projektstruktur.md".

Das Projekt hat zwei Teilprojekte:
- den **Interpreter** (Python): führt Programme des C 8205 interpretativ nach dem Knotengraphen aus
  (Abschnitt 6.1),
- den **Assembler** `c82ass` (C): übersetzt Assembler-Quelltext in Objektcode für den C 8205
  (Abschnitt 6.2).


## 1. Einordnung und Leistungsdaten

Der C 8205 ist ein **Einadreßautomat**. Bei zeitoptimaler Programmierung lassen sich etwa 2000
verdrahtete Operationen je Sekunde ausführen.

Als Vorzüge werden genannt:
- geringer technischer Aufwand der Zentraleinheit (nur ca. 400 Transistoren und 2000 Dioden),
- die Magnettrommel als vergleichsweise billiges Speichermedium mit relativ kleiner Zugriffszeit,
- für einen Kleinrechner hohe Operationsgeschwindigkeit,
- Programmierhilfen in Form sogenannter Interpretersysteme, die den Programmieraufwand wesentlich
  verringern.

Damit ist der C 8205 ein für die eingesetzte Technik leistungsstarker Kleinrechenautomat, einsetzbar
- für wissenschaftlich-technische Berechnungen,
- für mathematisch-ökonomische Berechnungen,
- zur Datenverarbeitung in begrenztem Umfang,
- als Hilfs- oder Satellitenrechner im Rahmen eines Systems von Rechnern oder Datenverarbeitungsanlagen.

(Der Begriff "Interpretersystem" in dieser historischen Aufzählung meint Programmiersysteme auf dem C 8205
selbst; er ist nicht zu verwechseln mit dem Python-Interpreter dieses Projekts, Abschnitt 6.1.)


## 2. Geräteaufbau

Der Rechner besteht aus:

- der **Stromversorgungseinheit** (Anschlussspannung 220 V ± 10 %, 50 ± 1 Hz, Leistungsaufnahme rund
  1500 VA),
- der **Zentraleinheit**, bestehend aus Rechenwerk und Leitwerk.

Zur unmittelbar zugeordneten (1.) Peripherie gehören:
- der Magnettrommelspeicher (Organisation und Kapazität: siehe Dokument "C8205-Interpreter-Magnettrommel.md"),
- Tastatur, Lampenfeld und Bahnsperrenschalter (Bedienelemente: siehe Dokument "C8205-Interpreter-Bedienpult_mit_Schaltern.md"),
- 2 Lochbandleser (Leser 1 an Kanal K1, Leser 2 an Kanal K2; Eingabegeschwindigkeit des Standardlesers
  130 Zeichen/s, laut Übersichtsgrafik je nach Programm bis 150 Zeichen/s, s. Abschnitt 8; Zeichen im
  8-Kanal- oder 5-Kanal-Kode; Details: "C8205-Interpreter-Lochstreifenleser.md"),
- 1 Lochbandstanzer (maximale Stanzgeschwindigkeit 50 Zeichen/s, Kanal K1),
- 1 Schreibwerk für alphanumerische Ein- und Ausgabe (maximale Schreibgeschwindigkeit 10 Zeichen/s;
  Eingabe über Kanal K0, Ausgabe über Kanal K2).

Der Informationsfluss zwischen diesen Baueinheiten: Pult-Tastatur sowie die beiden Lochbandleser
speisen (jeweils über einen Puffer) das Leitwerk/Rechenwerk, das seinerseits mit dem Trommelspeicher
verbunden ist; vom Leitwerk/Rechenwerk führt der Weg über einen weiteren Puffer zu Schreibwerk und
Lochbandstanzer.

Als **2. Peripherie** (wechselnd anschließbar) kommen lochbanderzeugende bzw. lochbandverarbeitende
Geräte in einem beliebigen 5-Kanal- oder 8-Kanal-Kode in Frage (beim 8-Kanal-Kode mit
Paritätslochung im 5. Kanal). Programmsysteme werden meist im 8-Kanal-R300-Kode oder im
5-Kanal-CCITT-2-Kode (auch Telegraphenalphabet Nr. 2 genannt) geliefert. Die Zeichenkode-Tabellen stehen
in "C8205-Interpreter-Kodetabellen.md".


## 3. Rechen- und Leitwerk

Das **Leitwerk** besitzt den Befehlszähler (BZ), das Adreßregister (AR) und das Befehlsregister (BR).
Das Befehlsregister (21 Bit) besteht aus dem Adreßteil a (12 Bit) und dem Operationsregister OR (9 Bit);
das Adreßregister AR (12 Bit) ist davon getrennt der Zellenwähler für den Trommelzugriff. (Bit-Breiten und
Feldaufteilung: siehe Dokument "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md".)

Zum **Rechenwerk** gehören der Akkumulator (AC) und das Rechenwerk im engeren Sinn; dieses kann außer
Addition und Subtraktion auch die logische UND-Verknüpfung (Konjunktion) ausführen.

Die Register unterscheiden sich in ihrer Bauart:

- **BZ und AC sind Umlaufregister**, die sich technisch auf der Trommel befinden (Umlaufspeicherprinzip):
  Ein Lesekopf (H) erfasst die Bit-Belegung eines Platzes, ein Umformer (U) bereitet darauf ein
  erneutes Aufsprechen über einen Sprechkopf (S) vor, ein Löschkopf (L) löscht die Plätze (setzt sie auf
  0). Die zentrale Taktsteuerung sorgt dafür, dass der Informationszustand eines solchen Umlaufregisters
  zu Beginn jeder Wortzeit stets derselbe ist.
- **OR (9 Dualstellen) und AR (12 Stellen) sind dagegen statische Register**, als Schiebekette
  aufgebaut: Die Information wird seriell ein- und herausgeschoben; der Zustand jeder Stelle ist zu
  jedem Zeitpunkt abgreifbar. Im AR geschieht dies für die Spur- und die Sektor-kennzeichnenden Stellen
  getrennt.

Zugriffsrichtung zum Trommelspeicher: Eine **Entnahme** gespeicherter Information ist zum Rechenwerk,
zum Befehlszähler und zum Operationsregister hin möglich. Eine **Abspeicherung** von Information im
Speicher ist dagegen nur vom Akkumulator her möglich.

## 4. Ablauf der Befehlsabarbeitung – die vier Phasen

Charakteristisch für den Einadreßautomaten C 8205 ist, dass als Zellenwähler in jedem Fall das
Adreßregister AR benutzt wird, und dass bei Entnahmen aus dem Speicher – wegen der Verwendung einer
Magnettrommel als Speicher – im Allgemeinen Wartezeiten auftreten, da der gewünschte Sektor erst unter
die Lese-Schreib-Einrichtung gedreht werden muss.

BZ enthält dabei die Adresse BADR des nächstabzuarbeitenden Befehls.

Der Befehlszyklus gliedert sich in vier Phasen, zwischen denen jeweils eine Koinzidenz-Wartezeit liegt.
Die folgende Tabelle beschreibt einen **vergröberten Prinzip-Ablauf**: Sie benennt je Phase nur die
dafür charakteristische Hauptwirkung. Einzelne, hier nicht gesondert aufgeführte Nebeneffekte (z. B.
weitere, in der Elektronik gleichzeitig ablaufende Registerbelegungen) können davon abweichend auch an
anderer Stelle im Zyklus auftreten; das ist keine Inkonsistenz, sondern Folge dieser vereinfachten
Darstellungstiefe.

| Phase | Bezeichnung | Wirkung |
|---|---|---|
| I | Befehlszähleraufstellung | Füllen des Zellenwählers AR mit BADR: `<AR> := <BZ> = BADR` |
| (K) | — Wartezeit | Trommel dreht sich bis zum Sektor, der durch `<AR> = BADR` vorgegeben ist |
| II | Befehlsentnahme und Operationsaufstellung | Entnahme des Befehls ADR OP: `<BZ> := ADR; <OR> := OP` |
| III | Befehlsadressenaufstellung | Füllen des Zellenwählers AR mit ADR, gleichzeitig Rücktransport von BADR nach BZ und Erhöhung um 1: `<AR> := <BZ> = ADR`, gleichzeitig `<BZ> := <AR>+1 = BADR+1` |
| (K) | — Wartezeit | Trommel dreht sich bis zum Sektor, der durch `<AR> = ADR` vorgegeben ist |
| IV | Operationsausführung | Ausführung entsprechend `<OR> = OP` |

Zwischen Phase III und Phase IV kann von außen eingegriffen werden (AC-Löschung, Stop, Start) – die
Bedeutung der zugehörigen Tasten (E, G, M, Ü, ST) und des Schalters H-R ist im Dokument
"C8205-Interpreter-Bedienpult_mit_Schaltern.md" beschrieben.

Eine Phase benötigt 104 µs, d. h. eine Wortzeit.

Diese vier Phasen entsprechen den "Phasenzuordnung"-Knoten der Ablaufbeschreibung (Knoten 2, 8, 15 und
31/61/67 für Beginn Phase I–IV, siehe Dokument "C8205-Interpreter-Eingänge_der_Knoten.md").

**Interpretative Abarbeitung:** Der Python-Interpreter (Abschnitt 6.1) rechnet mit Wortzeit und Wartezeit
= 0; die Trommeldrehung wird nicht nachgebildet. Die Zeitangaben dieses Abschnitts und des Abschnitts 5
beschreiben die Hardware, nicht den Interpreter.


## 5. Speicher-Timing und Leistungswerte

- Umdrehungsgeschwindigkeit der Trommel: 18 000 min⁻¹ = 300 s⁻¹
- Schreibdichte: 32 Wörter à 33 Bit je Spur
- daraus resultierende Arbeitsfrequenz der seriellen Verarbeitung: rund 316 kHz
- Wortzeit: 33 : 316 kHz ≈ 104 µs ≈ 0,1 ms (deckt sich mit der Phasendauer oben; entspricht zugleich der
  Zeit, in der ein gespeichertes Wort unter dem Lesekopf durchläuft)
- mittlere Zugriffszeit des Trommelspeichers: 1,67 ms (maximale Zugriffszeit: 3,33 ms)
- Adressierung: 12 Bit Adressteil des Befehlswortes → 2¹² = 4096 adressierbare Speicherzellen; 9 Bit
  Operationsteil → 2⁹ = 512 mögliche Bitkombinationen für Operationen

Gesamtzeit je Befehlsabarbeitung (inklusive Stellen des Befehlszählers, Befehlsentnahme, Entschlüsselung
der Operation, Aufstellen der Befehlsadresse und ggf. Wartezeiten):

| Befehlsart | min. Zeit | max. Op/s |
|---|---|---|
| Einzelbefehle | 0,5 ms | 1900 |
| Organisationsbefehle | 0,4 ms | 2400 |
| Gruppen-/Wiederholungsbefehle | — | bis ca. 9000 |

Aufgrund des halbanalytischen Aufbaus des Befehlskodes ist nicht jede der 512 möglichen Bitkombinationen
sinnvoll belegt bzw. es gibt Kombinationen mit gleicher Wirkung; dadurch reduziert sich die Befehlsliste
auf etwa 370 sinnvolle, in ihrer Wirkung voneinander verschiedene Befehle. Diese wiederum stellen
Kombinationen von nur rund 20 Grundoperationen dar. (Die Befehle samt Formeln stehen in
"C8205-Interpreter-Befehlsliste-Zwischenstand.md": generische Zusammenfassung nach Befehlsarten B=0…7 und
Einzelbefehlsübersicht aller 512 Oktalcodes.)


## 6. Teilprojekte

### 6.1 Interpreter

Der Interpreter (`c8205_interp.py`) führt Programme des C 8205 interpretativ aus: Er läuft den
Knotengraphen des Befehlsablaufs (Phasen I bis IV) ab und bildet Register, Flags, Trommelspeicher und
Peripherie nach (alle Zeiten = 0). Testaufträge liegen in `Tests/`, Protokolle in `Protokolle/`. Der
Vollständigkeitstest `c8205_befehlssweep.py` prüft alle 512 Operationscodes gegen den Knotengraphen.
Einzelheiten: "C8205-Interpreter-Python_Interpreter.md" (Bedienung, Schalter, Geräte) und
"C8205-Interpreter-Durchführung_eines_Tests.md" (Testdatei, Tastenfolge, Protokoll).

### 6.2 Assembler

Der Cross-Assembler `c82ass` (Version 0.2, Unterverzeichnis `Assembler/`) übersetzt Assembler-Quelltext
(`.asm`) in ladefähigen Objektcode für den C 8205. Er ist in C (gcc) geschrieben und läuft unter Linux und
Windows 10; die grafische Oberfläche benutzt node.js. Aufruf: `c82ass.sh -p Projektverzeichnis -s Quelldatei`;
die zuletzt benutzten Parameter werden in `projekdetails` abgelegt, sodass ein Folgestart ohne Parameter
möglich ist.

**Arbeitsweise (drei Pässe):**
1. Pass 1 ermittelt die Literaltabelle (Ausgabe im Logfile `.log`).
2. Pass 2 ermittelt die Symboltabelle (ebenfalls `.log`).
3. Pass 3 löst die Literale im Quelltext auf und erzeugt daraus die Kennzeichenbefehle für das "Kleine
   Eingabeprogramm" (Objektdatei `.obj`).

**Sprache:** Eine Zeile je Befehl: `[Symbol] Operationscode [Operand] [; Kommentar]`. Operationscode ist ein
Maschinenbefehl (drei Oktalziffern, d. h. der Operationsteil BAZ aus Abschnitt 5) oder eine
Assembleranweisung (Daten-/Textdefinition: `db`, `dbn`, `dw`, `da`, `dt`/`dto`/`dtm`, `dz`; Adressdefinition:
`equ`, `abs`; Programmrahmen: `start`, `end`). Zahlen sind oktal oder dezimal; Literale (`#wert`, `@adresse`)
legt der Assembler selbst auf Speicherplätzen am Programmende ab. Ein einfacher Makro-Präprozessor
(Makrodatei `ca82ass.makros`, erweiterbar) erzeugt wiederkehrende Befehlsfolgen, z. B. Kanalanwahlen.

**Zusammenhang mit dem Rechner:** Der erzeugte Objektcode ist für das "Kleine Eingabeprogramm" des C 8205
bestimmt (Bedienpult-Dokument, Abschnitt 4.5): ein einfaches Leseprogramm auf Spur 0, das nur die Zeichen
0, 1, Punkt, Doppelpunkt und Zwischenraum verarbeitet. Daher besteht der Objektcode aus Zeilen im
K1K2-Format (Kennzeichen, Adresse, Wort); der Kennzeichenbefehl `20` setzt eine Relativadresse. Die
Textausgabe (`dt`, `dz`) verwendet die Ausgabeadressen des R300-Kodes (Kodetabellen, Tabelle 1).

**Erzeugte Dateien** (im Verzeichnis der `.asm`-Datei): `.log` (Literal-, Symbol- und Absolut-Symbol-
Tabelle), `.obj` (Objektcode), `.mqo` (aufbereiteter Quelltext mit Maschinencode), `.sym` (Symboldatei
zur Zuordnung von Symbolen zu Trommeladressen); `.test` enthält die Trommeldatei im Format des Interpreters; `.dmp` und `.mac` entstehen ebenfalls, ihr Zweck
ist nicht beschrieben.

Die Verzeichnisse und Dateien des Assemblers beschreibt "C8205-Projektstruktur.md", Abschnitt 3.
Maßgebliche Dokumentation (Aufruf, Sprachdefinition, Anweisungen, Makros, Beispiel):
`Assembler/Dokumentation/C8205_Assembler_Dokumentation.odt`; die `.md`-Datei
"C8205_Assembler_Dokumentation.md" ist nur eine durchsuchbare Ableitung.


## 7. Verweise auf die Teildokumente

**Rechner und Regelwerk**
- Trommelorganisation im Detail (128 Spuren/32 Sektoren, Interleaving/logische vs. physische
  Sektoradressen, Bahnwahl, Bahnsperrenschalter): "C8205-Interpreter-Magnettrommel.md".
- Register-, Feld- und Flag-Definitionen im Detail (AC, OR, BZ, AR, BR, Maschinenwortaufbau, Flags E, A,
  T, SW, K1–K3, FE, FÜ, BS, US, V1, V2): "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md".
- Bedienelemente im Detail (Schalter H-R, Tasten E/G/M/Ü/SW/ST, Eingabetasten, Kanalauswahl, Selektoren
  SP/BS, Schalter LS, Kleines Eingabeprogramm): "C8205-Interpreter-Bedienpult_mit_Schaltern.md".
- Lochstreifenleser, Lochstreifenstanzer, Schreibwerk-Ausgabe (Hardware): "C8205-Interpreter-Lochstreifenleser.md".
- Zeichenkodes (Tabelle 1 Lochstreifenkode, Tabelle 2 R 300, Tabelle 3 CCITT-2): "C8205-Interpreter-Kodetabellen.md".
- Befehle und Formeln: "C8205-Interpreter-Befehlsliste-Zwischenstand.md".
- Ablaufdetails der Befehlsverarbeitung als Knoten-/Testgraph: "C8205-Interpreter-Eingänge_der_Knoten.md" und
  "C8205-Interpreter-Beschreibung_der_Knoten.md" (Variablentabelle T2).

**Interpreter und Tests**
- Python-Interpreter (Aufbau, Aufruf, Schalter, Geräte, Protokoll): "C8205-Interpreter-Python_Interpreter.md".
- Testdurchführung (Testdatei, Tastenfolge, Ergebnisprüfung): "C8205-Interpreter-Durchführung_eines_Tests.md".
- Cache der BAZ-Wirkungen (für den Claude-Interpreter; der Python-Interpreter liest ihn nicht): "baz-wirkungstabelle.md".

**Assembler**
- Teilprojekt, Verzeichnisse, erzeugte Dateien: "C8205-Projektstruktur.md", Abschnitt 3.
- Sprache, Anweisungen, Makros, Beispiel: "C8205_Assembler_Dokumentation.odt" (maßgeblich) bzw. ".md" (Ableitung).
- Vom Assemblerergebnis zum Testauftrag des Interpreters: "C8205-Interpreter-Durchführung_eines_Tests.md", Abschnitt 2a.

**Ausgabe**
- Gestaltung der PDF-Ausgaben (Knotengraph, Einzelbefehlsliste, Kodetabellen): "C8205-Interpreter-PDF.md".
- Verzeichnisstruktur des Gesamtprojekts: "C8205-Projektstruktur.md".


## 8. Offene Punkte

- **Lesegeschwindigkeit:** Diese Datei (Übersichtsgrafik) nennt für die Leser "je nach Programm bis 150
  Zeichen/s"; "C8205-Interpreter-Lochstreifenleser.md", Abschnitt A3, nennt 130 Zeichen/s für den
  Standardleser. Beide Angaben sind oben mitgeteilt; zu klären, ob 150 nur für einen anderen Lesertyp bzw.
  Betriebsfall gilt oder ob eine Angabe zu korrigieren ist.
