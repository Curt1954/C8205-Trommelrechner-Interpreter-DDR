** Objektdatei-Ausdrucke der Beispielprogramme (Vorgabebilder) **

Version: 0.03-002

Entwurf vom 07.10.2026 (ergänzt nach dem Assemblerlauf), noch nicht geprüft. Dieses Dokument erklärt, wie die in den Büchern abgedruckten
Beispielprogramme zu lesen sind und wie man daraus einen Testauftrag macht. Es wiederholt nichts aus den
Teildokumenten, sondern verweist auf sie (Assemblerdokumentation, "C8205-Interpreter-Durchführung_eines_Tests.md").
Quellen: Erläuterung des Projektinhabers (07.10.2026), Assemblerdokumentation Abschnitte 3.3.7 bis 3.3.9 und 5.2,
Beispiel "Ermittlung des Maximums von drei Zahlen" mit den daraus entstandenen Tests. Was nicht belegt ist, steht
unter "Offene Punkte" (Abschnitt 6).


## 1. Was ein Vorgabebild ist (und was nicht)

Die Beispielprogramme der Bücher sind als **Ausdruck einer Programm-Objektdatei** abgebildet, die ein Lader
(`c82load`, "Kleines Eingabeprogramm") liest. Der Ausdruck ist **kein Speicherabzug**. Welche Adressen im
Trommelspeicher tatsächlich belegt werden, berechnet erst der Lader aus den Angaben der Datei und aus den
Ladeadressen, die beim Laden gelten. Wer die Zahlen als Trommeladressen liest, liest falsch.

Dasselbe Format erzeugt der Assembler `c82ass` in seiner `.obj`-Datei ("K1K2-ladefähiger Objektcode",
Assemblerdokumentation 5.2). Ein Vorgabebild lässt sich daher mit demselben Wissen lesen wie eine `.obj`-Datei.


## 2. Spalten einer Befehlszeile

Beispielzeile: `0003  02 1 211.   b   M := b`

| Spalte | Beispiel | Bedeutung |
|---|---|---|
| 1 | `0003` | relative Adresse der Zelle, oktal. Die endgültige Zelle ist Programmladeadresse + Spalte 1 |
| 2 | `02` | Relokationskennung K1K2 (Abschnitt 3): sagt dem Lader, was er zum Adreßteil addiert |
| 3 | `1` | Adreßteil des Befehls, oktal, ohne führende Nullen gedruckt (`1` = 0001, `7776` = 7776) |
| 4 | `211.` | Operationsteil BAZ, oktal; der Punkt schließt die Zeile ab |
| 5 | `b` | Inhalt des AC nach dem Befehl, `<AC>` (`"` heißt: unverändert), nur Erläuterung |
| 6 | `M := b` | Bemerkung, nur Erläuterung |

Die Spalten 5 und 6 gehören nicht zur Objektdatei und gehen nicht in den Test ein. Spalte 5 ist aber eine gute
Kontrolle für die Prüfwerte (z. B. `AC=0` nach einem Stopp mit Löschen).


## 3. Relokationskennung (Spalte 2, K1K2)

| K1K2 | Wirkung beim Laden | Beleg |
|---|---|---|
| `00` | keine Änderung: Adreßteil gilt absolut (z. B. Register R2 = 7776, feste Stoppnummer) | Projektinhaber; Assemblerdoku 3.3.9 (`abs`-Symbole: K1K2=00); `dw`-Datenworte ebenfalls 00 |
| `01` | Programmladeadresse wird zum Adreßteil addiert (Sprungziele, Adressen im Programm) | Projektinhaber; Assemblerdoku 3.3.3/3.3.4 ("1. Hauptleitadresse") |
| `02` | eine zweite Ladeadresse (Datenladeadresse) wird zum Adreßteil addiert; ab ihr liegen die Daten, im Beispiel a, b, c | Projektinhaber |
| `20` | Kennzeichen "Relativadresse setzen" (aus `equ`), keine Befehlszeile | Assemblerdoku 3.3.8 (KZ=20) |

Der Assembler erzeugt nur `00`, `01` und `20`. Ein Kennzeichen `02` kommt nur in den Vorgabebildern vor
(Abschnitt 6, Punkt 2).

**Wichtig beim Nachbauen mit dem Assembler:** Ein Zahlenoperand (z. B. `240 07776`) ergibt K1K2=**01**, nicht 00, und
würde beim Laden um die Programmladeadresse verschoben. Ein Befehl mit K1K2=**00** (feste Adresse wie R2 = 7776 oder
eine Stoppnummer) entsteht in unserem Assembler **nur über ein `abs`-Symbol** (Assemblerdokumentation 3.3.9):
`r2: abs 07776` und dann `240 r2` ergibt `00 7776 240.`. Die `abs`-Definitionen stehen hinter `end`.

Formen der Zeile (Beispiele aus Assemblerdokumentation 5.2): `01 0007 000.` (Kennzeichen, Adreßteil, BAZ),
`00 00000005000.` (ganzes Maschinenwort ohne Adreßänderung, z. B. `dw`-Daten) und `01 26000.` (ganzes
Maschinenwort mit Adresse in den Adreßstellen, vom Lader verschoben; entsteht bei `da`).


## 4. Vom Vorgabebild zum Testauftrag

1. **Zwei Ladeadressen wählen**: Programmladeadresse P und, falls Kennzeichen `02` vorkommt, Datenladeadresse D.
   Beide frei, aber so, dass sich nichts überdeckt (Beispiel: P = 3000, D = 3020).
2. **Zelle bestimmen**: Befehlszelle = P + Spalte 1.
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


## 5. Beispiel: Ermittlung des Maximums von drei Zahlen

P = 3000, D = 3020, Daten a = 3020, b = 3021, c = 3022, Ergebnis M nach R2 (7776).

| Zelle rel. | K1K2 | Adreß­teil | BAZ | Zelle endgültig | Maschinenwort | Bemerkung |
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
AC ≥ Operand. Dazu gehören die Testaufträge `pj2-bsp_maximum_3_zahlen_*` (b, a, c als Maximum und
alle drei gleich) und der Quelltext `pj2_maximum_3_zahlen.asm` (Ausschnitt der Kennzeichen-00-Zeilen: `r2: abs 07776`
und `stoppnr: abs 01111` hinter `end`). Alle vier Tests laufen im Python-Interpreter mit `Test wahr`.


## 6. Offene Punkte

1. **Name "BIS":** Die Objektdatei wird im Projekt als "BIS-Objektdatei" bezeichnet. Die Bedienpult-Datei erwähnt
   das BIS nur als Sondertasten-Hinweis. Die Bedeutung der Abkürzung ist hier nicht belegt und nicht erfunden.
2. **Kennzeichen 02:** Die Datenladeadresse und der Weg, auf dem sie festgelegt wird, sind nur durch die Erläuterung
   des Projektinhabers belegt, nicht durch die Assemblerdokumentation. Ebenso, ob Zellen mit Kennzeichen 02
   in Spalte 1 relativ zu P oder zu D zählen (im Beispiel stehen nur Befehlszellen, alle relativ zu P).
3. **Druckform:** Die genaue Form der Zeilen mit Kennzeichen `20` und der Zeilen ohne Spalte 1 (Ende der Datei in
   Assemblerdokumentation 5.2) ist nicht geklärt.
4. **Bedeutung des Punktes** am Zeilenende (Abschluss der Lochstreifenzeile?) ist nicht belegt.
5. **Einordnung ins Projekt:** Bei Übernahme gehört die Datei in `markdown-dateien/`, braucht einen Eintrag in der
   Dokumentenlandkarte (`C8205-Interpreter-Projektueberblick.md`, Abschnitt 6) und, falls ein PDF entstehen soll,
   einen Eintrag in `C8205-Interpreter-PDF.md`, Abschnitt 8. Beides habe ich nicht geändert.
