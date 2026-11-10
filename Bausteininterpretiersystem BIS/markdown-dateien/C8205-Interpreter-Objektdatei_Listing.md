** Objektdatei-Ausdrucke der Beispielprogramme (Vorgabebilder) **

Version: 0.03-004

Dieses Dokument erklärt, wie die in den Büchern abgedruckten Beispielprogramme zu lesen sind und wie man daraus
einen Testauftrag macht. Es wiederholt nichts aus den Teildokumenten, sondern verweist auf sie (Assemblerdokumentation,
"C8205-Interpreter-Durchführung_eines_Tests.md", "C8205-Interpreter-BIS.md").
Quellen: Erläuterung des Projektinhabers (07.10.2026), Assemblerdokumentation Abschnitte 3.1, 3.3.7 bis 3.3.9, 3.3.12 und 5.2
(die `.odt` ist maßgeblich), BIS-Dokumentation Abschnitte BIS-2.2.2 bis BIS-2.2.5, Beispiel "Ermittlung des Maximums von drei
Zahlen" mit den daraus entstandenen Tests. Was nicht belegt ist, steht unter "Offene Punkte" (Abschnitt 6).


## 1. Was ein Vorgabebild ist (und was nicht)

Die Beispielprogramme der Bücher sind als **Ausdruck einer Programm-Objektdatei** abgebildet, die die Eingabe mit Kennzeichen des
BIS-Minimalprogramms liest (Ansprung 0262, "C8205-Programmierhandbuch-Anhang_B_BIS_Anschluss.md"). Das Kleine Eingabeprogramm
(KEP) ist dafür nicht zuständig: Es liest nur Dualziffern (Assemblerdokumentation 3.1). Der Ausdruck ist **kein Speicherabzug**.
Welche Adressen im Trommelspeicher tatsächlich belegt werden, berechnet erst die Eingabe mit Kennzeichen aus den Angaben der Datei
und aus den Leitadressen, die beim Laden gelten. Wer die Zahlen als Trommeladressen liest, liest falsch.

Dasselbe Format erzeugt der Assembler `c82ass` in seiner `.obj`-Datei ("K1K2-ladefähiger Objektcode", Assemblerdokumentation 5.2).
Ein Vorgabebild lässt sich daher mit demselben Wissen lesen wie eine `.obj`-Datei. Der Unterschied liegt nur in der Darstellung:
Das Vorgabebild ist ein Textausdruck mit Spalten, die `.obj` ist ein **binär codierter R300-Lochstreifen** (je Zeichen eine
Lochbildzeile aus acht Ziffern 0/1) ohne Adressspalte, ohne Leerzeichen und ohne Zeilenende (Abschnitt 2).


## 2. Spalten einer Befehlszeile

Beispielzeile: `0003  02 1 211.   b   M := b`

| Spalte | Beispiel | Bedeutung |
|---|---|---|
| 1 | `0003` | relative Adresse der Zelle, oktal. Die endgültige Zelle ist Hauptleitadresse + Spalte 1 |
| 2 | `02` | Kennzeichen K1K2 (Abschnitt 3): sagt der Eingabe, was sie zum Adreßteil addiert |
| 3 | `1` | Adreßteil des Befehls, oktal, im Ausdruck ohne führende Nullen gedruckt (`1` = 0001, `7776` = 7776) |
| 4 | `211.` | Operationsteil BAZ, oktal; der Punkt ist die Wortmarke und schließt das Wort ab |
| 5 | `b` | Inhalt des AC nach dem Befehl, `<AC>` (`"` heißt: unverändert), nur Erläuterung |
| 6 | `M := b` | Bemerkung, nur Erläuterung |

Die Spalten 5 und 6 gehören nicht zur Objektdatei und gehen nicht in den Test ein. Spalte 5 ist aber eine gute
Kontrolle für die Prüfwerte (z. B. `AC=0` nach einem Stopp mit Löschen).

**Zeile in der `.obj`:** Von der Beispielzeile bleiben nur Kennzeichen, Adreßteil, BAZ und Punkt, ohne Leerzeichen und mit vierstelligem
Adreßteil: `020001211.`. Die Wörter folgen ohne Zeilenende unmittelbar aufeinander, das letzte Zeichen der Datei ist `/`
(Assemblerdokumentation 3.1; SatzMarke/WRZL würde das Minimalprogramm v6 als zusätzliches Wort 0 speichern). Jedes Zeichen steht als
Lochbild in der Kodetabelle 1 (Klbuch). Zurück in Text wandelt `Hilfsprogramme/c8205_lochstreifen_umwandlung.py` mit `--IN-TXT`.

Formen der Zeile (Beispiele aus Assemblerdokumentation 5.2): `01 0007 000.` (Kennzeichen, Adreßteil, BAZ),
`00 00000005000.` (ganzes Maschinenwort ohne Adreßänderung, z. B. `dw`-Daten) und `01 26000.` (ganzes
Maschinenwort mit Adresse in den Adreßstellen, vom Lader verschoben; entsteht bei `da`; führende Nullen sind weggelassen, BIS-2.2.1).
Ein Nullwort wird als `0.` ausgegeben.


## 3. Kennzeichen K1K2 (Spalte 2)

K1 sagt, was das Wort ist, K2 steuert die Adressenänderung (BIS-2.2.2).

| K1K2 | Wirkung beim Laden | Beleg |
|---|---|---|
| `00` | keine Änderung: Adreßteil gilt absolut (z. B. Register R2 = 7776, feste Stoppnummer) | BIS-2.2.3; Assemblerdoku 3.3.9 (`abs`-Symbole: K1K2=00); `dw`-Datenworte ebenfalls 00 |
| `01` | Hauptleitadresse (= 1. Leitadresse, im Vorgabebild "Programmladeadresse") wird zum Adreßteil addiert (Sprungziele, Adressen im Programm) | BIS-2.2.3; Assemblerdoku 3.3.3/3.3.4 |
| `02` | die 2. Leitadresse (im Vorgabebild "Datenladeadresse") wird zum Adreßteil addiert; ab ihr liegen die Daten, im Beispiel a, b, c | BIS-2.2.3 (K2 = 2 … 9: 2. … 9. Leitadresse); Projektinhaber |
| `03` … `09` | 3. … 9. Leitadresse wird addiert | BIS-2.2.3 |
| `20` | Relativadresse setzen (aus `equ`, auch bei `db`), keine Befehlszeile; Form `20 0000 aaaa.` (`equ`) oder kurz `20 aaaa.` (z. B. bei `db`) | BIS-2.2.5 (K1 = 2, K2 = 0); Assemblerdoku 3.3.8 und 5.2 |
| `21` | Hauptleitadresse setzen (Leitbefehl aus `start <zahl>`): `21 0000 zahl.` | BIS-2.2.5 (K2 = 1); Assemblerdoku 3.3.7 |

Der Assembler erzeugt `00`, `01`, `20` und `21` (nur bei `start` mit Operand). Die Kennzeichen `02` bis `09` erzeugt er nur über
das Pragma `;#; LEITADRESSE xx` (Assemblerdoku 3.3.12); es ersetzt dann in **allen** Zeilen das Kennzeichen 01. Das Vorgabebild des
Beispiels mischt dagegen `01` und `02`.

**Wichtig beim Nachbauen mit dem Assembler:** Ein Zahlenoperand (z. B. `240 07776`) ergibt K1K2=**01**, nicht 00, und
würde beim Laden um die Hauptleitadresse verschoben. Ein Befehl mit K1K2=**00** (feste Adresse wie R2 = 7776 oder
eine Stoppnummer) entsteht in unserem Assembler **nur über ein `abs`-Symbol** (Assemblerdokumentation 3.3.9):
`r2: abs 07776` und dann `240 r2` ergibt `00 7776 240.`. Die `abs`-Definitionen stehen hinter `end`.


## 4. Vom Vorgabebild zum Testauftrag

1. **Zwei Ladeadressen wählen**: Hauptleitadresse P (Programmladeadresse, gesetzt mit `2 1 P .`) und, falls Kennzeichen `02` vorkommt,
   die 2. Leitadresse D (Datenladeadresse, gesetzt mit `2 2 D .`). Beide frei, aber so, dass sich nichts überdeckt (Beispiel: P = 3000, D = 3020).
2. **Zelle bestimmen**: Befehlszelle = P + Spalte 1. Die Abspeicherung läuft immer über Hauptleitadresse und Relativadresse; die
   Leitadressen 2 bis 9 verändern nur den Adreßteil des Wortes (BIS-2.2.5). Spalte 1 zählt deshalb auch bei Kennzeichen `02` relativ zu P.
3. **Adreßteil bestimmen**: `00` unverändert, `01` plus P, `02` plus D.
4. **Maschinenwort schreiben**: `0000` + 4 Oktalstellen Adreßteil + BAZ (11 Oktalstellen, "Datenstruktur …",
   Abschnitt Maschinenwort).
5. **Einstieg**: Auf Zelle 0000 steht ein unbedingter Sprung auf P (`000 P`), Tastenfolge `H G R`.
6. **Daten und Werte**: Die Datenzellen (hier a, b, c) stehen nicht im Ausdruck. Werte wählt der Test, am besten
   einen Test je Weg durch das Programm.
7. **Prüfungen**: Nach dem Stopp ist `BZ` = Befehlsadresse + 1 und `AR` = Adreßteil des Stoppbefehls
   (Phase III setzt AR := a, "C8205-Interpreter-Eingänge_der_Knoten.md"). Der AC folgt der Löschung des
   Stoppbefehls. Die Vergleicherstände V1/V2 entstehen aus dem letzten Vergleich (Befehlsliste 4.1.4).
8. **Name**: Testaufträge aus den neuen Büchern erhalten das Präfix `pj2-`.
9. **Bemerkung je Zeile**: Die Originalzeile gehört als Kommentar hinter jede Adresse:Wert-Zeile
   (z. B. `3002: 00003004150 # 0002 01 4 150. ; M>=b ?`), damit der Abgleich mit dem Vorgabebild möglich bleibt.

Ein Beispielprogramm lässt sich auch mit dem Assembler nachbauen (`equ` legt Programm und Daten auf die
Testadressen; Zeilen mit Kennzeichen 00 über `abs`-Symbole, s. Abschnitt 3). Dann entstehen die Zeilen des
Testauftrags aus der `.test`-Datei ("Durchführung eines Tests", 2a). Beim Maximum-Beispiel ist das geprüft: Die
`.test` enthält dieselben Trommelzeilen wie der von Hand geschriebene Testauftrag.

Das Laden einer `.obj` durch das Minimalprogramm v6 zeigt der Test `Tests/pj2-bis_v6_obj_laden.test` (Band
`Test-virtuelleGeraete/Leser1/pj2-bis_v6_obj_laden.txt`). Das Setzen und Addieren der 2. Leitadresse (Band `2 1 3000 . 2 2 100 . 0 2 5 . :`)
prüft `Tests/pj2-bis_v6_ps_adressaenderung_k2.test`; beide laufen mit `Test wahr`.


## 5. Beispiel: Ermittlung des Maximums von drei Zahlen

P = 3000, D = 3020, Daten a = 3020, b = 3021, c = 3022, Ergebnis M nach R2 (7776).

| Zelle rel. | K1K2 | Adreßteil | BAZ | Zelle endgültig | Maschinenwort | Bemerkung |
|---|---|---|---|---|---|---|
| 0000 | 02 | 0 | 211 | 3000 | `00003020211` | M := a |
| 0001 | 02 | 1 | 330 | 3001 | `00003021330` | M ≥ b ? (Vergleicher setzen) |
| 0002 | 01 | 4 | 150 | 3002 | `00003004150` | Sprung nach rel. 0004, wenn M ≥ b |
| 0003 | 02 | 1 | 211 | 3003 | `00003021211` | M := b |
| 0004 | 02 | 2 | 330 | 3004 | `00003022330` | M ≥ c ? |
| 0005 | 01 | 7 | 150 | 3005 | `00003007150` | Sprung nach rel. 0007, wenn M ≥ c |
| 0006 | 02 | 2 | 211 | 3006 | `00003022211` | M := c |
| 0007 | 00 | 7776 | 240 | 3007 | `00007776240` | M → R2 |
| 0010 | 00 | 1111 | 021 | 3010 | `00001111021` | Stopp mit Löschen |

Die Sprungziele 4 und 7 sind relativ zum Programm (Kennzeichen 01) und überspringen jeweils den Befehl
"M := b" bzw. "M := c". Der Sprung 150 ist ein Vergleichersprung 2: er springt bei V2 oder V3, also bei
AC ≥ Operand (Handbuch 4.1; Code 330 setzt dazu den Vergleicher). Dazu gehören die Testaufträge `pj2-bsp_maximum_3_zahlen_*` (b, a, c als
Maximum und alle drei gleich) und der Quelltext `Assembler/Projekt_2/pj2_maximum_3_zahlen.asm` (Kennzeichen-00-Zeilen: `r2: abs 07776`
und `stoppnr: abs 01111` hinter `end`; Test `Tests/pj2_maximum_3_zahlen.test`). Alle fünf Tests laufen im Python-Interpreter mit `Test wahr`.

**Die `.obj` des Nachbaus** (Assembler 1.00-038, zurückgewandelt mit `c8205_lochstreifen_umwandlung.py --IN-TXT`, 165 Lochbildzeilen).
In der Datei stehen die Wörter ohne Zeilenwechsel; hier je Wort eine Zeile:

```
013000000.      Zelle 0000: 000 maximum (Sprung nach 3000)
2000003000.     Relativadresse 3000 (equ 03000)
013020211.      3000: 211 a
013021330.      3001: 330 b
013004150.      3002: 150 nachb
013021211.      3003: 211 b
013022330.      3004: 330 c
013007150.      3005: 150 nachc
013022211.      3006: 211 c
007776240.      3007: 240 r2 (Kennzeichen 00)
001111021.      3010: 021 stoppnr (Kennzeichen 00)
2000003020.     Relativadresse 3020 (equ 03020)
0000000000100.  3020: a = 0100 (dw)
0000000000300.  3021: b = 0300
0000000000200.  3022: c = 0200
/               Schluss
```

Der Nachbau legt Programm und Daten mit `equ` auf die Testadressen; die Adreßteile stehen deshalb schon in den Zeilen
(Kennzeichen 01, nicht 02), und es entsteht kein Leitbefehl `21`, weil `start` hier ohne Operand steht. Die Maschinenworte stimmen mit
der Spalte "Maschinenwort" der Tabelle überein.


## 6. Prüfumfang und offene Punkte

**Geprüft** (Assembler `c82ass` 1.00-038): Der Nachbau des Maximum-Beispiels wurde assembliert (rc 0), die binäre `.obj` mit `--IN-TXT`
zurückgewandelt und Wort für Wort mit `.dmp`, `.test` und der Tabelle in Abschnitt 5 verglichen: gleich. Ein kleiner Formtest bestätigte die
Zeilenformen `21 0000 zahl.`, `20 0000 aaaa.` (`equ`), `20 aaaa.` (`db`) und `00 <elf Ziffern>.`. Die fünf Maximum-Tests, `pj2-bis_v6_obj_laden.test`
und `pj2-bis_v6_ps_adressaenderung_k2.test` laufen mit `Test wahr`. Das Minimalprogramm v6 verarbeitet K1 = 2 mit K2 = 1 bis 9
(Quelltext `pj2-bis_minimalprogramm_v6.asm`, Kopfkommentar; Anhang B nennt nur K2 = 0 und 1).

**Offen:**

1. **Lesen am GRAFIK-Fenster:** Das Lesen einer `.obj` mit Kennzeichen über Leser/Eingabe am GRAFIK-Fenster ist nicht geprüft.
2. **Andere Dokumente:** `C8205-Projektstruktur.md` (Zeile 188) und `C8205-Interpreter-Projektueberblick.md` (Zeilen 121 und 127) nennen die
   Objektdatei noch "für das KEP" bzw. "die das KEP liest"; nach Assemblerdokumentation 3.1 ist das die Eingabe mit Kennzeichen des
   Minimalprogramms. Dort nicht geändert.
3. **PDF:** Für diese Datei gibt es keinen Eintrag in `C8205-Interpreter-PDF.md`; ob ein PDF entstehen soll, ist nicht entschieden.
