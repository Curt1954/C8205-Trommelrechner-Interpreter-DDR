# C 8205 – ZT-Makros aus `macro_zt_loader.macro`

Version: 0.01-002

Stand: 09.11.2026 · Quelle: `Assembler/Projekt_ZT_LOADER/macro_zt_loader.macro` (7 Makros, jedes mit `$SPEC`-Zeile; Assembler c82ass 1.03-004)
Art: Übersicht, abgeleitet aus den `#`-Kommentaren der Makrodatei, aufgebaut wie `C8205_Standardmakros_c82ass.md`. Die ZT-Makros sind nur hier und in diesen Kommentaren beschrieben. Diese Übersicht sagt, **was ein Makro tut und wie man es aufruft**. Zellenlisten, Bitfelder und Arbeitszellen stehen nur im `#`-Kommentar der Makrodatei; bei Abweichung gilt dieser Kommentar.
Alle Zahlen sind oktal, wie in der Quelle, außer wo „dezimal“ dabeisteht. PDF: siehe Abschnitt 7.

## 0. Gemeinsame Regeln

- **Einbinden:** Im Quelltext `;#MACRODATEI1=<Pfad>` (Pfad relativ zur Quelldatei). Programme in den Unterprojekten von `Assembler/Projekt_ZT_LOADER/` schreiben `;#MACRODATEI1=../../macro_zt_loader.macro`.
- **Aufruf eines Unterprogramm-Makros (UP):** Das Makro erzeugt nur den Rumpf; der Ablauf läuft nicht hinein. Die Marke vor dem Makro ist der Einsprung. Man trägt die Register ein (R1 = Zelle 7773, R2 = 7776, R3 = 7774, z. B. `211 radr`, `240 07773`) und ruft mit `025 <marke>` auf. Nach der Rückkehr steht im AC ein Rückkehrwort, das man nicht auswerten soll.
- **KB/GB-Zelle:** Die ZT-Makros führen KB/GB nicht über R3, sondern über die eine globale Zelle **KBGB = 7775** (0 = Kleinbuchstaben, 1 = Großbuchstaben).
- **Nur mit `--C8205Z`:** ZTINIT, NEUANL und HSCHL sprechen die Zusatztrommeln an und laufen nur mit diesem Schalter des Interpreters.
- **Arbeitsspur 7640:** Makros, die intern schieben, überschreiben die Zellen der Spur 7640. Dort darf nichts stehen, was erhalten bleiben soll.
- **Fehlerprüfung:** Die UP-Makros prüfen ihre Eingaben nicht (z. B. Trommel größer 3) und melden keine Fehler, außer HSCHL bei zu langem Streifen.
- **Mehrfachaufruf:** Ein UP-Makro erzeugt bei jedem Aufruf einen eigenen Rumpf mit eigener Marke. Ausnahmen (Rumpf nur einmal): ZTKONST und NEUANL; bei NEUANL stehen spätere Aufrufe ohne Marke, alle `025` zeigen auf die Marke des ersten Aufrufs.
- **Das Verzeichnis der Zusatztrommel in drei Sätzen:** Jedes Programm hat einen Eintrag aus 2 Zellen (Programmname, dazu Typ, ID, Trommel, Spur). Das Verzeichnis liegt auf ZT 0, Spuren 1 bis 32, und fasst bis zu 511 Programme; die erste Programmspur ist 33 (dezimal). Spur 0 von ZT 0 ist der Kopf mit dem Zähler der zuletzt vergebenen ID.
- **Version der Makrodatei:** Sie hat keine eigene Versionsnummer; maßgeblich ist der Assemblerstand (c82ass 1.03-004).

## 1. Übersicht

| Thema | Makros | Zweck in einem Satz |
|---|---|---|
| Konstanten | ZTKONST | Benannte Zahlen für das Verzeichnis, ohne Code. |
| Eingabe vom Lochstreifen | TYP10EINGABE | Liest eine Eingabe (Kennzeichen und Zahl) und legt sie als 2 Worte ab. |
| Textausgabe | KAT4AUSGABE_G | Gibt einen gepackten Text aus und führt Klein-/Großbuchstaben mit. |
| Verwaltung der Zusatztrommel | ZTINIT, PNAME, NEUANL | Trommeln löschen, Programmnamen eintragen, Verzeichnis schreiben. |
| Programm laden | HSCHL | Liest einen Lochstreifen und schreibt ihn auf die Zusatztrommel. |

## 2. Konstanten

| Makro | Parameter | Kurzbeschreibung | Mehrfachaufruf |
|---|---|---|---|
| `ZTKONST` | keine, ohne Marke | Legt drei benannte Zahlen an und erzeugt keinen Code: `ZT_EINTRAGSZELLEN` = 2 (Zellen je Verzeichniseintrag), `ZT_VERZSPUREN` = 32 (Spuren des Verzeichnisses), `ZT_PROGSPUR1` = 33 (erste Programmspur). Man schreibt sie im Operanden, z. B. `#ZT_PROGSPUR1`. ZTINIT ruft ZTKONST selbst auf. | Ja, wirkt nur einmal |

Grenze: PNAME und die Puffergröße sind fest auf 2 Zellen je Eintrag gebaut. Wer `ZT_EINTRAGSZELLEN` ändert, muss auch PNAME und die Puffer ändern.

## 3. Eingabe vom Lochstreifen

Aufruf: `eingabe: TYP10EINGABE [ende]`. Vorher den Eingabekanal anwählen (z. B. K1 = Lochbandleser 1), R1 eintragen, mit `025` aufrufen.

| Makro | Parameter | Kurzbeschreibung | Mehrfachaufruf |
|---|---|---|---|
| `TYP10EINGABE` | Makroparameter `ende` (wahlfrei): Marke im aufrufenden Programm, die beim Zeichen `/` angesprungen wird. R1 = Adresse eines Bereichs aus 2 Zellen | Liest **eine Eingabe** und legt sie in 2 Worten ab. Eine Eingabe besteht aus zwei Kennzeichen (Zeichen 0 bis 9 und +), dann Ziffern, dann `.` oder `:` als Ende. **Wort 1** = der Zahlenwert aus den Ziffern 0 bis 7 (die letzten 11 Ziffern zählen). **Wort 2** = die beiden Kennzeichen. Alle anderen Zeichen (Leertaste, Wagenrücklauf, Buchstaben, Irrung) werden überlesen. Mit Parameter `ende` beendet `/` den Streifen: eine angefangene Eingabe wird verworfen. | Nein |

## 4. Textausgabe

| Makro | Parameter | Kurzbeschreibung | Mehrfachaufruf |
|---|---|---|---|
| `KAT4AUSGABE_G` | R1 = Adresse des Textes; Kanal vorher anwählen (z. B. `ANWAHL K2`) | Gibt einen kat4-Text aus (4 Zeichen je Wort). Wie das Standardmakro `KAT4AUSGABE`, nur dass der Zustand Klein-/Großbuchstaben in der globalen Zelle KBGB steht statt in R3. Steht das Gerät auf Großbuchstaben, schaltet das UP vor dem ersten Zeichen auf Kleinbuchstaben um; Umschaltzeichen im Text werden mitgeführt. | Nein |

## 5. Verwaltung der Zusatztrommel

Alle drei sind UP-Makros ohne Makroparameter. Aufruf: `name: MAKRO`, Register füllen, `025 name`. Keine Ausschrift, KBGB bleibt unberührt.

| Makro | Parameter | Kurzbeschreibung | Mehrfachaufruf |
|---|---|---|---|
| `ZTINIT` | R1 = Adresse des Puffers SPUF-00 (auf Spurgrenze) | **Initialisiert die Zusatztrommeln:** löscht alle vier (je 128 Spuren) und legt Spur 0 von ZT 0 mit dem Kopf des Verzeichnisses neu an. Danach steht der Kopf auch in SPUF-00, ZT 0 ist angewählt. Dauert im Zeitmodell rund 44 Sekunden (513 Ausgaben); im TEST-Interpreter ist die Zeit 0. | Nein |
| `PNAME` | R1 = Adresse des Puffers SPUF-PN (2 Spuren, auf Spurgrenze); R2 = Adresse der Zelle mit dem Programmnamen (kat5, 1 bis 5 Zeichen); R3 = Adresse von SPUF-00 | **Trägt einen Programmnamen ins Verzeichnis ein:** vergibt die nächste freie ID, schreibt Name, Typ, ID, Trommel und Spur des neuen Programms in den Eintrag im Puffer SPUF-PN und erhöht den ID-Zähler im Kopf (SPUF-00). Die Trommel wird nicht berührt, es ändern sich nur die Puffer. Nicht geprüft: doppelte Namen, ID größer 32, Trommel größer 3. | Nein |
| `NEUANL` | R1 = Adresse des Puffers SPUF-PN; R2 = Trommelnummer d (0 bis 3, als Zahl); R3 = Spurnummer s (0 bis 126, als Zahl) | **Schreibt den Puffer SPUF-PN auf die Trommel:** wählt Trommel d an und schreibt die 64 Zellen auf die zwei aufeinanderfolgenden Spuren s und s + 1. Der Puffer bleibt unverändert. Für das Verzeichnis: Trommel 0, Spur 1. Nicht geprüft: d größer 3, s größer 126. | Ja, Rumpf nur einmal |

## 6. Programm laden

| Makro | Parameter | Kurzbeschreibung | Mehrfachaufruf |
|---|---|---|---|
| `HSCHL` | Drei Makroparameter: `fehlerzulang` = Marke des Fehlerausgangs im aufrufenden Programm; `eingabeup` = Marke des UP `TYP10EINGABE`; `namensteil` = Namensteil der Marke `hs_<namensteil>`. Register: R1 = Adresse des Spurpuffers (1 Spur = 32 Zellen, auf Spurgrenze); R2 = Trommelnummer d; R3 = Spurnummer s der ersten Zielspur. K1 (Lochbandleser 1) vorher anwählen | **Liest einen Lochstreifen und schreibt ihn auf die Zusatztrommel.** Jede Eingabe des Streifens (zwei Kennzeichen, Ziffern, Ende) ergibt 2 Zellen im Spurpuffer. Sind 16 Eingaben beisammen, wird die Spur auf die Trommel geschrieben und die nächste Spur begonnen. Das Zeichen `/` beendet den Streifen; die letzte, teilvolle Spur wird dann ebenfalls geschrieben. Bei der Rückkehr steht in R2 die Anzahl der geschriebenen Sektoren (2 je Eingabe). Wird der Streifen zu lang (mehr als 2048 Eingaben), springt HSCHL zu `fehlerzulang` und kehrt nicht zurück. Aufruf: `hschl: HSCHL fe_lang eingabe ende`; das aufrufende Programm enthält zusätzlich `eingabe: TYP10EINGABE hs_ende`. | Nein |

## 7. PDF-Ausgabe

Das Layoutskript `Assembler/Dokumentation/pdf-layout-scripte/erzeuge_zt_makros_pdf.py` erzeugt aus dieser Datei `Assembler/Dokumentation/C8205-ZT_Makros_A4.pdf`. Aufruf im Projektstamm: `./make_pdf.sh erzeuge_zt_makros_pdf.py [--stand TT.MM.JJJJ]`; `./make_all_pdf.sh` erzeugt es mit allen anderen PDF. Das Skript ist wie `erzeuge_standardmakros_pdf.py` aufgebaut und nutzt `md2pdf.py` aus `PDF/pdf-layout-scripte/`.

## 8. Spezifikationszeile (`$SPEC`) der ZT-Makros

Jedes Makro trägt als zweite Zeile hinter `MACRO` eine Spezifikationszeile (Assemblerdokumentation 4.32; c82ass wertet sie seit 1.03-002 aus, `TYP=E` seit 1.03-004).

- **`TYP=E` (Eingebettet):** Assembler-Hilfskonstrukt zur Verringerung der Komplexität des Quelltexts, kein wirklich mehrfach verwendetes Makro. Keine Prüfung der Einmalerzeugung, keine Warnung.
- **`TYP=M` mit `CLASS=ZTLOADER`:** Das Makro erzeugt seinen Rumpf nur einmal und setzt dafür einen globalen Merker (`$GLOBAL`); ohne Merker und ohne `$BLOCK` warnt der Assembler.

| Makro | Thema | Zeile in der Makrodatei | TYP | CLASS | ACTION | Merker (Einmalerzeugung) |
|---|---|---|---|---|---|---|
| `ZTKONST` | Konstanten | ja: `$SPEC TYP=E ACTION=None` | E | – (keine Klasse) | None | – (Rumpf trotzdem nur einmal über `zt_konst_da`) |
| `TYP10EINGABE` | Eingabe Typ 10 | ja: `$SPEC TYP=E ACTION=None` | E | – (keine Klasse) | None | – (jeder Aufruf erzeugt Code) |
| `KAT4AUSGABE_G` | Textausgabe | ja: `$SPEC TYP=E ACTION=None` | E | – (keine Klasse) | None | – (jeder Aufruf erzeugt Code) |
| `ZTINIT` | ZT-Verwaltung | ja: `$SPEC TYP=E ACTION=None` | E | – (keine Klasse) | None | – (jeder Aufruf erzeugt Code) |
| `PNAME` | ZT-Verwaltung | ja: `$SPEC TYP=E ACTION=None` | E | – (keine Klasse) | None | – (jeder Aufruf erzeugt Code) |
| `NEUANL` | ZT-Verwaltung | ja: `$SPEC TYP=M CLASS=ZTLOADER ACTION=None` | M | ZTLOADER | None | `neuanl_da` |
| `HSCHL` | Hauptschleife | ja: `$SPEC TYP=E ACTION=None` | E | – (keine Klasse) | None | – (jeder Aufruf erzeugt Code) |
