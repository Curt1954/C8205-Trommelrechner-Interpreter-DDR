# ZIL (Urlader der Zusatztrommeln): Prüfung der Realisierbarkeit des Ablaufs ohne Fehlerrückgaben

Version: 0.01-008
Stand: 31.10.2026
Grundlage: Zip 0.95.7-074 mit den Lieferungen dieser Sitzung; gelesen wurden `ZT-Repository_Aufgabenstellung.md` 0.01-044 (Abschnitte 5a, 6, 6b, 8), das Flussdiagramm (`mk_dot.py`), `zil.asm`, `macro_zt_loader.macro` und Handbuch 5.3 (Parameterübergabe).
**Nichts programmiert, nichts geändert.** Dieses Dokument ist das Prüfergebnis; es ist keine Spezifikation.
**Nachtrag 01.11.2026 (historisches Dokument, Text unten nicht nachgeführt):** `hschl` legt den Streifen inzwischen nicht mehr als `kat4` ab, sondern als **Typ 10** (liest mit `TYP10EINGABE`, `/` beendet über einen Endeausgang); den Fehler „Ziffer 8 oder 9“ und die Meldung „lochstreifen fehlerhaft“ gibt es nicht mehr, übrig bleibt „lochstreifen zu lang“ (2048 Eingaben). Maßgeblich ist `ZT-Repository_Aufgabenstellung.md` (6c, 7a).
**Nachtrag 09.11.2026 (historisches Dokument, Text unten nicht nachgeführt):** Der Programmname im Verzeichnis ist seit der Umstellung auf `kat5` ein Wort; der Eintrag hat 2 Zellen (Name in Wort 1, Bitwort in Wort 2), das Verzeichnis liegt in den Spuren 1 bis 32, die erste Programmspur ist 33, Zelle 19 = 040, SPUF-PN fasst ID 1 bis 32. Angaben wie „Wort 3“, „Spur 49“, „ID 1 bis 21“ oder „3 Zellen“ im Text unten gelten für den Stand davor. Maßgeblich ist `ZT-Repository_Aufgabenstellung.md` (0.01-061).

## 1. Vorgabe des Inhabers

Es gibt **nirgends Fehlerrückgaben**. Ein Unterprogramm (UP) liefert höchstens ein **Ergebnis** (`repo`: R2 = 1/0, `jneingabe`: R2 = 1/0, `hschl`: R2 = Sektoranzahl), aber nie eine Fehlerart an das aufrufende Programm.

## 2. Ergebnis

Der Ablauf (Elemente 1a bis 18) ist **realisierbar**, wenn ein Fehler im Lochstreifen **im UP selbst** behandelt wird: das UP gibt die Meldung aus und hält an. Die Elemente 15a und 15b im Hauptprogramm entfallen dann, ebenso die Zelle `lsfehl`. Alle anderen UP kommen ohne Fehlerrückgabe aus und sind (bis auf `hschl`) programmiert und getestet.

Die Zelle `lsfehl` samt 15a/15b ist von mir als **Annahme** eingeführt worden (steht in `zil.asm` und md 8 Punkt 2 als Annahme); sie widerspricht der Vorgabe und ist zu entfernen.

## 3. Prüfung UP für UP

| UP / Element | Parameter | Fehlerrückgabe? | Realisierbar? | Stand |
|---|---|---|---|---|
| `repo` (2) | R1 = SPUF-00; Ergebnis R2 = 1/0 | nein (R2 ist die Antwort „Repository ja/nein“, kein Fehler) | ja | Platzhalter |
| `jneingabe` (5) | K0 angewählt, KBGB global; Ergebnis R2 | nein | ja | programmiert, getestet |
| `MELDUNG` / `KAT4AUSGABE_G` | Text, KBGB global | nein | ja | programmiert, getestet |
| `ztinit` (10) | R1 = SPUF-00 | nein | ja | Makro `ZTINIT`, getestet |
| `pname` (13) | R1 = SPUF-PN, R2 = Namenszellen, R3 = SPUF-00 | nein (prüft ID > 21 und Trommel > 3 nicht, wie vorgegeben: Vermerk) | ja | Makro `PNAME`, getestet |
| `neuanl` (14) | R1 = SPUF-PN, R2 = Trommel, R3 = Spur | nein | ja | Makro `NEUANL`, getestet |
| `hschl` (15) | R1 = Puffer Programmcode, R2 = Trommel, R3 = Spur; Ergebnis R2 = Sektoranzahl | **muss im UP behandelt werden** (siehe 4) | ja, mit den Punkten in 5 | Makro `HSCHL`, getestet (31.10.2026) |
| 16 (Länge eintragen, SPUF-PN nochmals schreiben) | Hauptprogramm: Wort 3 ergänzen, dann `NEUANL` mit R1 bis R3 neu gesetzt | nein | ja, reiner Hauptprogramm-Code mit vorhandenem Makro | Platzhalter-Meldung |
| 17 (SPUF-00 auf ZT 0 Spur 0 schreiben) | R1 = SPUF-00; Trommel 0 und Spur 0 fest | nein | ja: Anwahl `05100030`, eine Ausgabe `R1 + 601` (Spur 0), wie in `ZTINIT` | Platzhalter-Meldung |

## 4. Folge für `hschl` und das Hauptprogramm

- `hschl` meldet **Ziffer 8 oder 9** („lochstreifen fehlerhaft“) und **mehr als 4095 Sektoren** („lochstreifen zu lang“) selbst über `MELDUNG` und hält an. Das Hauptprogramm setzt danach nie fort; „ohne Verzeichnis und Spur 0 zu schreiben“ (md Abschnitt 6, Fehler) bleibt von selbst richtig, denn 16 und 17 stehen hinter dem Aufruf.
- Es entfallen: Elemente **15a** (Verzweigung) und **15b** (Ausschrift) im Hauptprogramm, die Zelle `lsfehl`, der Platzhalterwert `d_fehler` als Rückgabe, die Prüfung `lsfehl` im Prüfblock.
- Die Meldungstexte bleiben, ebenso die Tests `zil_lsziffer` und `zil_lszulang` (der Platzhalter `hschl` gibt dann den Text selbst aus und hält an; die erwartete SW-Ausgabe ändert sich nicht, die Sollwerte nach dem Halt sind neu herzuleiten).
- Im Graph ändert sich das Kästchen von `hschl` („Fehler im Lochstreifen: UP meldet selbst und hält an, keine Rückgabe“); die Nummern 15a und 15b entfallen, die übrigen Nummern bleiben.

## 5. Was bei der Realisierung von `hschl` zu beachten ist

1. **Parameterübergabe nur für die unterste UP-Ebene.** Handbuch 5.3 (Festlegung 031): R1 bis R3 sind nur für UP gedacht, die kein weiteres UP aufrufen. `hschl` hätte `MELDUNG` (UP `ausgabe`) aufgerufen, das R1 überschreibt. **Umgesetzt (31.10.2026):** `hschl` ruft kein UP auf, sondern springt bei einem Fehler auf zwei Fehlerausgänge des Hauptprogramms (Parameter des Makros `HSCHL`), die `MELDUNG` aufrufen und halten; R1 bis R3 müssen deshalb nicht gerettet werden und bleiben im Normalweg unverändert. `PNAME` und `NEUANL` rufen kein UP auf und halten R1 bis R3 unverändert.
2. **Kanal:** `5k00 030` lässt die Kanalflags unverändert (md Abschnitt 6): K1 bleibt beim Schreiben der Spuren angewählt. Beim Fehler wählt `MELDUNG` K2 an; da danach gehalten wird, ist der Verlust von K1 ohne Folge.
3. **Schreiben der Spuren:** je 32 Zellen eine Ausgabe `Spur · 2^26 + Puffer + 601` mit Trommelanwahl, wie in `NEUANL`; Übertrag von Spur 127 auf die nächste Trommel wie in `PNAME` (`p = 128 · Trommel + Spur`). Das ist mit vorhandenen Bausteinen machbar.
4. **Zählen:** Länge in Sektoren = Zellen; Grenze 4095, dann Meldung „lochstreifen zu lang“.

## 6. Stand der Lücken vor der Programmierung von `hschl`

Diese Punkte sind keine Fehlerrückgaben.

1. **Format des Streifens und Abbildung auf `kat4` (festgelegt, Antwort des Inhabers 31.10.2026).** Der Streifen enthält dieselben Zeichen wie die BIS-Eingabe mit Kennzeichen. Jedes gelesene Zeichen wird als `kat4`-Zeichen abgelegt (Code = Ausgabeadresse der Kodetabelle R 300 ohne das werthöchste Bit, md Abschnitt 1), vier je Wort, das erste rechts; im letzten Wort ist z0 = 1. Das Lochstreifenende `/` wird mitgespeichert, Ziffer 8 oder 9 ist ein Fehler (Abschnitt 4). **Zuordnungstabelle hergeleitet (Doku 31.10.2026): `ZT-Repository_Aufgabenstellung.md` 0.01-046, Abschnitt 6c (Entwurf, offene Punkte dort).** Ursprünglicher Text: die Zuordnungstabelle Eingabeadresse → `kat4`-Zeichen (64 Zellen auf einer 0100-Grenze wie bei `jneingabe`; der Inhalt ist aus der Kodetabelle R 300 herleitbar). Zeichen mit Sprung-Umstellung (`.`, `:`, Leertaste, WRZL, Um. KB, Um. GB, Tabulator, `-`, `,`, BM u. a.) führen ihre Tabellenzelle als Befehl aus und brauchen je einen kleinen Behandler; ZV und BM haben dieselbe Eingabeadresse 72 (Kodetabellen 1.3).
2. **Typ (gestrichen, Inhaber 31.10.2026).** ZTD hat keinen Typ; der Typ ist nur ein Feld im Verzeichniseintrag. Der in Version 0.01-001 geführte Widerspruch „Typ 10 des Eintrags gegen die Speicherung als `kat4` mit z0 = 1 im letzten Wort“ besteht nicht. Er war schon erledigt und wurde von mir fälschlich erneut als offen geführt.
3. **Zellen 18/19 in SPUF-00 nach dem Laden** (md Abschnitt 8 Punkt 4): Das Hauptprogramm schreibt SPUF-00 in 17 mit den ursprünglichen Werten 0 und 48 zurück. Ein später abgelegtes Programm bekäme damit wieder Spur 49 und überschriebe ZTD. Für den Urlader selbst unerheblich, für das Repository nicht.

## 6a. Stand der Streichungen (31.10.2026, Doku)

In der Doku sind 15a, 15b und `lsfehl` gestrichen: `ZT-Repository_Aufgabenstellung.md` 0.01-045 (Abschnitte 1, 6, 8 Punkt 2) und Flussdiagramm (`mk_dot.py`, `ZIL_Ablauf.pdf` neu erzeugt). **Noch offen (Code, auf Freigabe):** `zil.asm` und die Tests `zil_lsziffer`/`zil_lszulang`. Die Datei `ZT-Repository_Aufgabenstellung.pdf` ist noch der alte Stand und wird beim Inhaber neu erzeugt.

## 7. Zusammenfassung

Realisierbar: ja. Nötig sind (a) die Behandlung der beiden Lochstreifenfehler **innerhalb** von `hschl` statt einer Rückgabe, mit den daraus folgenden Streichungen in Graph, md und `zil.asm`/Tests (Abschnitt 4) und (b) die Zuordnungstabelle zu 6.1 (das Format ist festgelegt, 6.2 ist gestrichen) und die Entscheidung zu 6.3 (für den Urlader selbst unerheblich). Auf Freigabe zum Programmieren warten die Streichungen (Doku und Code getrennt) und `hschl`.
