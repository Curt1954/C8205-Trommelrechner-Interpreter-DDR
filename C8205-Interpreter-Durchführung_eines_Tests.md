** Durchführung eines Tests **

## 1. Einordnung und Testvoraussetzungen

Das Gesamtdokument (mit all seinen Teilen) beschreibt zwei unterschiedliche Aspekte:

1. Die Hardware und die in der Elektronik angelegten Beziehungen (Knotenautomat).
2. Davon abweichend/ergänzend die Annahmen für eine interpretative Abarbeitung eines Befehls.

Punkt 2 beschreibt damit die Voraussetzung jedes Tests. Insbesondere basiert er auf der Annahme,
dass alle Zeiten = 0 sind, d. h. zeitliche Abhängigkeiten werden zwar in ihrer Reihenfolge betrachtet,
führen aber nicht zu "Wartezeiten".

Jeder Test nimmt an, dass der Rechner eingeschaltet ist.

Der Vor-Zustand vom Einschalten bis zum Beginn der Interpretation der Befehlsschleife am Konnektor B
wird definiert durch:
- die Interpretation der betätigten Tasten und Schalter, sowie
- den Trommelinhalt.

## 1a. Zwei Ausführende: Python-Interpreter und Claude-Interpreter

Ein Test nach diesem Format kann auf zwei Arten durchgeführt werden:

- **Python-Interpreter** (`c8205_interp.py`): führt den Knotengraphen deterministisch und automatisiert
  aus. Schneller, reproduzierbar, aber ohne Rückfragemöglichkeit bei unklaren Stellen.
- **Claude-Interpreter**: Eine KI erhält das komplette Regelwerk als Kontext sowie eine Testdatei
  (hochgeladen oder im Prompt) und arbeitet den Knotengraphen manuell, Knoten für Knoten, ab. Langsamer
  und nicht deterministisch reproduzierbar (abhängig von Modell und Sitzung), erlaubt dafür aber
  Rückfragen und Erläuterungen während der Abarbeitung.

**Aktuelle Rolle (während der Entwicklung des Python-Interpreters):** Der Claude-Interpreter dient als
unabhängige Gegenprobe. Weichen Python-Ergebnis und Claude-Ergebnis bei einem Test voneinander ab,
liegt ein Fehler in einem der beiden vor (oder eine unklare Stelle im Regelwerk selbst) – diese Rolle
endet, sobald der Python-Interpreter vollständig und stubfrei ist.

**Rolle im Normalbetrieb (danach):** Der Python-Interpreter ist die Standardmethode für Testläufe. Der
Claude-Interpreter wird eingesetzt, wenn im Einzelfall Rückfragen zu einer Ableitung oder Unklarheit
gestellt werden sollen.

**Rolle bei künftigen Erweiterungen des Regelwerks:** Neue oder geänderte Befehle/Anweisungen werden
zunächst mit dem Claude-Interpreter durchgespielt, bevor sie in `c8205_interp.py` übernommen werden.

**Einschränkung:** Der Claude-Interpreter ist nicht deterministisch reproduzierbar. Bei unklaren
Regelwerk-Stellen kann die ausführende KI Rückfragen stellen, statt eigenmächtig zu entscheiden (vgl.
Abschnitt 5, "laut scheitern"-Prinzip) – abhängig vom verwendeten Modell mit unterschiedlich vielen
Rückfragen. Diese Festlegung gilt modellneutral für jede interpretierende KI, nicht nur für Claude.

## 2. Schritt 1 jedes Tests: die Trommeldatei

Der Trommelinhalt wird, zum Zwecke der Interpretation, vor Beginn jedes Tests als .txt-Datei mit
festem Aufbau übermittelt. Das ist der erste Schritt jedes Tests.

Der Trommelinhalt ist nur ein Ausschnitt (adreßweise) der Gesamttrommel.

**Zeilenformat:**
```
Adresse: Wert [# Bemerkung]
```
- Adresse genügt der Definition von ADR (bzw. a): 4 Oktalstellen (12 Bit).
- Wert genügt der Definition Maschinenwort: 11 Oktalstellen (33 Bit), mit Vornullen ergänzt.
- Alle Zahlen werden als Oktalzahlen dargestellt.
- Leerzeilen sind möglich und werden übergangen.
- Kommentarzeilen beginnen mit `#`.
- Ein Kommentar beginnt mit `#` und reicht bis zum Zeilenende. Er kann entweder als eigene Zeile stehen
  oder – durch mindestens ein Leerzeichen getrennt – an eine Adresse:Wert-Zeile angehängt werden; in
  letzterem Fall gilt für das Parsen alles ab dem `#` bis Zeilenende als Kommentar und wird ignoriert.

**Beispiel:**
```
# Beginn Programmbefehle
0000: 00003000211
0001: 00003001210
0002: 00000000020
# Beginn Datenbereich
3000: 00000000100 # Startwert der Schleife
3001: 00000000045
```

**Testmarken `#DOK-xxxx` und `#SPEI-xxxx` (von der Hardware abweichend, nur für die Testdurchführung):**

Zusätzlich zu den oben beschriebenen Adresse:Wert-Zeilen kann die Trommeldatei Anweisungszeilen der
Form

```
#DOK-xxxx <Text>
```

enthalten. `xxxx` ist dabei eine Oktalzahl; 
 `<Text>` ist ein freier, dem Test zugeordneter Kommentartext. Diese Zeilen sind, obwohl sie wie die übrigen
Kommentarzeilen mit `#` beginnen, keine gewöhnlichen, folgenlosen Kommentare, sondern Testmarken mit
eigener Wirkung bei der Interpretation (s. Abschnitt 7).

#DOK-xxxx darf mehrfach mit derselben Nummer xxxx vorkommen (Ausgabe aller zugehörigen Texte in Dateireihenfolge).
#SPEI-xxxx darf mehrfach mit derselben Nummer xxxx vorkommen und wird – falls vorhanden – im Anschluss an die Textzeile(n) gleicher Nummer ausgegeben.


```
#SPEI-xxxx ssss-eeee
```

gegeben werden. Sie definiert für dasselbe `xxxx` einen Speicherbereich des Trommelspeichers, `ssss` als
Startadresse und `eeee` als Endadresse, beide oktal.

(Hinweis: Die Vorgabe zur Testmarke `#SPEI-xxxx` verlangt wörtlich `ssss>=eeee`; da `ssss` als
Start- und `eeee` als Endadresse benannt sind, ist damit vermutlich `ssss<=eeee` gemeint — vgl. den
analog behandelten mutmaßlichen Tippfehler in Abschnitt 3.2. Festzuhalten ist in jedem Fall die
Forderung: Vor Beginn des Tests ist zu prüfen, dass `ssss` und `eeee` eine gültige Adressspanne bilden;
ein Test mit einer nicht gültigen Spanne darf nicht gestartet werden.)

**Ergänzung 29.09.2026 – Testmarke `#SPUR-xxxx aaaa`:**

```
#SPUR-xxxx aaaa
```

`aaaa` ist eine Oktaladresse. Die Testmarke bezieht sich, anders als `#SPEI-xxxx`, nicht auf eine
Adressspanne, sondern auf die **Spur (Bahn)**, in der `aaaa` liegt (Bahn-Nr. = `aaaa` ohne die unteren
5 Bit, s. Datei "C8205-Interpreter-Magnettrommel.md", Abschnitt Speicherorganisation); welcher der 32
Sektoren von `aaaa` konkret adressiert wird, spielt dabei keine Rolle. Ausgegeben werden alle 32 Zellen
dieser Spur, und zwar in der **physischen Zugriffsreihenfolge** der Trommel (nicht in aufsteigender
logischer Adresse), wie in der Datei "C8205-Interpreter-Magnettrommel.md", Abschnitt
"Speichernumerierung / Interleaving" tabelliert. `#SPUR-xxxx` darf wie `#SPEI-xxxx` mehrfach mit
derselben Nummer xxxx vorkommen und wird, falls vorhanden, im Anschluss an eine etwaige
`#SPEI-xxxx`-Ausgabe angehängt (Reihenfolge: erst alle `#SPEI-xxxx`, danach alle `#SPUR-xxxx`, jeweils
in Dateireihenfolge). Das Zeilenformat je Zelle ist dasselbe wie bei `#SPEI-xxxx` ("Adresse: Wert").

Diese drei Testmarken sind eine von der realen Hardware abweichende Ergänzung, die ausschließlich der
besseren Durchführung von Tests mit dem Interpreter dient; sie haben keine Entsprechung in der
physischen Elektronik des C 8205.

**Testmarke `#PROT STUFE=n`, n ∈ {0,1,2} (Protokollierungsstufe):**

Zusätzlich zu `#DOK-xxxx` und `#SPEI-xxxx` kann die Trommeldatei eine Anweisungszeile

```
#PROT STUFE=n
```

enthalten. Anders als `#DOK-xxxx` und `#SPEI-xxxx` bezieht sie sich nicht auf eine einzelne Adresse,
sondern gilt test-weit; sie legt fest, wie ausführlich der Durchlauf durch den Knotenautomaten
(Abschnitt 8) protokolliert wird — nützlich vor allem bei Programmen mit vielen Durchläufen (z. B.
Schleifen über Gruppen-/Wiederholungsbefehle), bei denen ein Protokoll jedes einzelnen durchlaufenen
Knotens unübersichtlich lang würde.

- **STUFE=0:** Es wird kein ausführliches Protokoll des Knotenautomaten-Durchlaufs erstellt, weder auf
  dem Bildschirm noch in einer Datei. Die Diagnoseausgaben zu Befehl 164 (Abschnitt 7) bleiben davon
  unberührt: sie erscheinen unabhängig von der Protokollierungsstufe stets auf dem Bildschirm.
- **STUFE=1:** Zusätzlich zu den stets erscheinenden Diagnoseausgaben (Abschnitt 7) wird das
  ausführliche Protokoll des Knotenautomaten-Durchlaufs auf dem Bildschirm ausgegeben (s. Abschnitt
  8.2). Es entsteht dabei keine Protokolldatei.
- **STUFE=2:** Zusätzlich zu den stets erscheinenden Diagnoseausgaben (Abschnitt 7) wird das
  ausführliche Protokoll des Knotenautomaten-Durchlaufs statt auf dem Bildschirm in die
  Protokolldatei ("protokoll.txt", s. Abschnitt 8) geschrieben, die am Testende zum Download
  bereitgestellt wird.

Die Marke darf innerhalb eines Tests höchstens einmal vorkommen. Fehlt sie, gilt STUFE=1 als
Standardwert (entspricht der bislang unbedingt geltenden Protokollierung vor Einführung dieser Marke).

Wie `#DOK-xxxx` und `#SPEI-xxxx` ist auch `#PROT STUFE=n` eine von der realen Hardware abweichende,
zusätzliche Definition, die ausschließlich der besseren Durchführung von Tests mit dem Interpreter
dient und keine Entsprechung in der physischen Elektronik des C 8205 hat.

## 2a. Testauftrag aus einem Assemblerlauf (Ergänzung 01.10.2026)

Eine Testdatei (Testauftrag) lässt sich von Hand schreiben, ist wegen der oktalen Adressen aber mühsam.
Für Programme in Assemblersprache übernimmt das der Assembler `c82ass` (Projektstruktur, Abschnitt 3):
Er wandelt ein mit symbolischen Adressen geschriebenes Programm in Oktalbefehle um. Von den dabei
erzeugten Dateien wird nur `<name>.test` benötigt. Sie enthält die Trommeldatei im Zeilenformat von
Abschnitt 2, jede Zeile mit der zugehörigen Quelltextzeile als Bemerkung:

```
2007: 00002006241 # beginn: 241 i ; I:=0
2010: 00002003210 # schleife: 210 azv ; ac:=(azv+i)
```

Vorgehen:
1. Im Assembler-Quelltext an der Stelle, an der ausgewertet werden soll, einen Leerbefehl 164 mit einer
   vierstelligen Debug-Nummer als Adresse vorsehen (Abschnitt 7), z. B. `halt: 164 0001`. Die Nummer
   muss mit den Testmarken `#DOK-`/`#SPEI-`/`#SPUR-` des Testauftrags übereinstimmen.
2. `c82ass.sh -p <Projekt> -s <name>` aufrufen.
3. Den Testauftrag `Tests/asm_NNNN_<name>.txt` anlegen: Zeile `Trommeldatei:`, die Testmarken (`#DOK`,
   `#SPEI`, `#PROT STUFE=n`), der Inhalt von `<name>.test`, dann `Tastenfolge:` mit der Tastenfolge
   (im Beispiel `H G R`: Start bei Adresse 0000, dort steht ein Sprung zum Programmanfang) und
   optional der Abschnitt `Prüfungen:` (Abschnitt 3a).

Von Hand ergänzt werden also nur die Debug-Anweisungen (Testmarken), die Startbedingungen (Tastenfolge)
und ggf. die Prüfungen. Der Code selbst stammt unverändert aus dem Assemblerlauf.

Beispiel (gekürzt; Quelltext `Assembler/Projekt_1/bsp_5.16/bsp_5_16.asm`, Test `Tests/asm_0001_bsp_5_16.txt`):

```
Trommeldatei:
#DOK-0001 Test eines mit Assembler assemblierten Programmes
#SPEI-0001 2027-2033
#SPEI-0001 2100-2104
#PROT STUFE=2

0000: 00002000000 # 000 go
2000: 00002007000 # go: 000 beginn
...                                  (weitere Zeilen unverändert aus bsp_5_16.test)
2025: 00000001164 # halt: 164 0001 ;DEBUG Nr. 0001 aktivieren
2026: 00000000020 # 020 0 ;halt
...

Tastenfolge:
H G R
```

## 3. Schritt 2 jedes Tests: die Tastenfolge zur Definition des Ausgangszustands

Nach Übernahme einer korrekten Trommeldatei wird eine Tastenfolge angegeben, die auf die Ebene von
Registern (mit ihren Bits) und Flags (mit ihren Werten 0/1) herunterzubrechen ist. Dadurch wird der
Ausgangszustand des Rechners vor Eintritt in Konnektor B vollständig definiert.

### 3.1 Beispiel A — Ansprung des Speicherplatzes 0000 (direkt)

Trommeldatei wie in Abschnitt 2.

Tastenfolge: `H` `G` `R`

| Schritt | Aktion | Wirkung auf Register/Flags |
|---|---|---|
| 1 | Schalter H-R → "H" | Flag H := 1 |
| 2 | Taste "G" | alle Flags außer H, T, BS und SP werden gelöscht, danach US := 1 (s. Fall 1); BR wird auf "0000 000" gesetzt (unbedingter Sprung nach Speicherplatz 0000); K0 wird angewählt, Schalter "SW" ist nicht gedrückt → Flag T := 1; `<BZ>:=0` — dies ist nicht der unmittelbare Effekt von "G" selbst (G hat laut Dokument "keinen Einfluss auf ... Befehlszählerinhalt"), sondern das vorweggenommene Ergebnis der durch G geladenen Sprunginstruktion (ANWEISUNG-007, `<BZ>:=a`, hier a=0000) |
| 3 | Schalter H-R → "R" | Flag H := 0, US := 0; Interpretation setzt bei Konnektor B fort, mit BZ=0000 |

Prinzip: Tastenfolgen werden nicht nur als Rohschalterzustände, sondern bis zur Wirkung der dadurch
geladenen/ausgelösten Instruktion vorausinterpretiert, damit der Automat ab Konnektor B im regulären
4-Phasen-Zyklus weiterlaufen kann, ohne dass der manuelle Eingriff selbst als Sonderfall im
Knotengraphen behandelt werden müsste.

### 3.2 Beispiel B — Ansprung eines beliebigen Speicherplatzes (hier: 0004)

Trommeldatei (abweichende Belegung):
```
# Beginn Programmbefehle
0004: 00003000211
0005: 00003001210
0002: 00000004020
# Beginn Datenbereich
3000: 00000000100
3001: 00000000045
```

Tastenfolge: `H` `G` `M`-gedrückt-halten `E` `E` `E` `E` `M`-loslassen `R`

(Entspricht Dokument "C8205-Interpreter-Bedienpult_mit_Schaltern.md", Abschnitt 4.4, Punkt 2 — "Ansprung eines beliebigen Speicherplatzes n",
hier n=4. Anmerkung: Im Originaltext steht bei diesem Fall als Schritt a) "Schalter H-R → R"; das ist im
Kontext, da G/M/E nur bei Stellung "H" wirksam sind, vermutlich ein Tippfehler und müsste "→ H" heißen,
wie in der hier verwendeten Tastenfolge auch tatsächlich benutzt.)

| Schritt | Aktion | Wirkung auf Register/Flags |
|---|---|---|
| 1 | H-R → "H" | Flag H := 1 |
| 2 | Taste "G" | alle Flags außer H, T, BS, SP := 0; BR := "0000 000"; K0 angewählt, T := 1 |
| 3 | "M" gedrückt halten | OR := OR OR 025 → BR := "0000 025" (Sprung mit Rückkehrabsicht, Adresse 0000) |
| 4 | 1. "E" | Befehlsentnahme (Phase II) durch gehaltenes M verhindert; BZ := 0001, AR := 0001; ⟨AC⟩ := 0000 0002 000 (Rücksprungadresse BZ+1 im Adressfeld) |
| 5 | 2. "E" | BZ := 0002, AR := 0002; ⟨AC⟩ := 0000 0003 000 |
| 6 | 3. "E" | BZ := 0003, AR := 0003; ⟨AC⟩ := 0000 0004 000 |
| 7 | 4. "E" | BZ := 0004, AR := 0004; ⟨AC⟩ := 0000 0005 000 (= 0000 0004 000 + 0000 0001 000) |
| 8 | "M" loslassen | OR-Verknüpfung mit 025 entfällt für Folgeschritte |
| 9 | H-R → "R" | Flag H := 0; Interpretation geht bei Konnektor B weiter, mit BZ = 0004 → nächster Befehl wird aus Adresse 0004 entnommen |

### 3.3 Festlegungen zu den Tasten M, Ü und E (Stand 29.09.2026)

(Die Schreibweise der Token einer Tastenfolge steht im Dokument "C8205-Interpreter-Bedienpult_mit_Schaltern.md",
Abschnitt "Tastenfolge-Token".)

**E unter gehaltenem M (Vorgabe des Autors):** Jedes E führt Phase IV (BR = ⟨AR⟩ 025, Sprung mit Rückkehrabsicht
mit Löschen) und Phase I aus; Phase II ist gesperrt. Wirkung nach dem n-ten E (Start mit BZ = b): `BZ := b+n`,
`AR := BZ`, und der AC enthält im Adressfeld (z₁₂–z₂₃) den Wert BZ+1, übrige Stellen 0 (das Löschbit von 025
ersetzt den AC, es wird nicht aufsummiert). Beispiel B (b=0, n=4): `⟨AC⟩ = 0000 0005 000`. Danach steht der Automat
vor Phase II: ein nächstes `E` (nach Loslassen von M) beginnt bei Phase II (Knoten 8), ein `R` bei Konnektor B.

**M hat nur zwei Stellungen: "M gedrückt" (`M+`) und "M losgelassen" (`M-`).** Das Token `M` allein (Antippen)
ist gleichbedeutend mit `M+` und sofort danach `M-`. Gedrücktes M muss innerhalb der Tastenfolge wieder
losgelassen werden. Ungültig sind daher `M-` ohne vorheriges `M+`, ein zweites `M+` bei noch gedrücktem M, ein
`R` bei noch gedrücktem M und eine Tastenfolge, die mit gedrücktem M endet. Wirkung: bei `M+` gilt
`OR := OR ∨ 025`. Beim Loslassen gilt: Wurde unter gehaltenem M kein `E` betätigt (also beim Antippen `M`),
bleibt BR = "⟨AR⟩ 025" aufgestellt und wird erst durch `E` oder `R` ausgeführt (Fall 4). Wurde unter M
mindestens ein `E` betätigt (Beispiel B, Fall 6), entfällt der Beitrag von 025 beim Loslassen (übrige Anteile
im OR, z. B. von Ü, bleiben).

**Ü** ist nur bei gesetztem Schalter H wirksam (wie alle Tasten außer ST). Bei nicht gesetztem H hat die
Taste keine Wirkung. Bei gesetztem H gilt: `AR := 7777` (oktal, überschreibt unbedingt) und
`OR := OR ∨ 240` (Transport); damit steht BR = "7777 240" (wenn OR vorher 000 war), aufgestellt und noch nicht
ausgeführt. Ausgeführt wird BR erst durch `E` oder durch `R` (beides beginnt bei Knoten 19, Ende der
Phase-III-Arbeit).

**ST** ist die einzige Taste, die nicht an Schalter H gebunden ist, dafür aber elektronisch verriegelt: sie ist
nur wirksam, wenn der Rechner im "Bedingten Stopp" (Flag BS) oder "Unbedingten Stopp" (Flag US) steht, sonst
ohne Wirkung. Wirkung: `OR := OR ∨ 240`; AR bleibt unverändert; damit ist BR = "⟨AR⟩ (⟨OR⟩ ∨ 240)" aufgestellt
und noch nicht ausgeführt (Ausführung durch `E` oder `R`, Start bei Knoten 19); US wird dabei gelöscht. US
entsteht in einer Tastenfolge durch `G` (Fall 1: `G` setzt US := 1) und wird durch `ST` oder `R` wieder
gelöscht; ohne vorheriges `G` steht der Rechner zu Beginn einer Tastenfolge nicht im Stopp.

**BS und SP** sind einrastende Schalter. Die Token `BS=1` / `SP=1` (Schalter gedrückt und eingerastet) setzen das
gleichnamige Flag auf 1, `BS=0` / `SP=0` (Schalter gelöst) setzen es auf 0; mehr geschieht nicht. Da die Schalter
mechanisch einrasten, kann `G` sie nicht lösen: `G` lässt die Flags BS und SP unverändert (wie H). Nur ein
`BS=0` bzw. `SP=0` in der Tastenfolge löst sie wieder. Die Schalter sind nicht an H gebunden und in jeder
Reihenfolge zu den anderen Tasten zulässig.

**E (ohne M)** ist definiert (s. 4.2, Fall 5): Phase IV und Phase I, dann Phase II und III, danach Halt
(Halt-Punkt HP3 = Eintritt in Knoten 19). E ist nur bei gesetztem Schalter H wirksam. Eine Tastenfolge darf
ohne `R` enden; dann bleibt der Rechner im Halt und das Ergebnis der Sequenz ist der Zustand nach dem letzten
Schritt. E unter gehaltenem M: s. 4.3 (Fall 6).

## 3a. Schritt 3 jedes Tests (optional): Ergebnisprüfung (`Prüfungen:`)

**Ergänzung 30.09.2026.**

Nach der Tastenfolge (Abschnitt 3) kann eine Testdatei zusätzlich einen dritten Abschnitt

```
Prüfungen:
```

enthalten. Er ist **optional**: fehlt er, endet der Test wie bisher ohne automatisierte
Ergebnisprüfung. Ist er vorhanden, prüft der ausführende Interpreter (Python- wie Claude-Interpreter,
s. Abschnitt 1a) nach Abschluss der interpretativen Abarbeitung den erreichten Endzustand gegen die hier
angegebenen Soll-Werte und vermerkt im Protokoll `Test wahr` oder `Test falsch`.

### 3a.1 Aufbau

Der Abschnitt `Prüfungen:` besteht aus höchstens zwei Teilen, in dieser Reihenfolge:

1. **Höchstens eine** Register-/Flag-Zeile. Sie enthält, durch Leerzeichen getrennt und in beliebiger
   Reihenfolge, eine oder mehrere Zuweisungen der Form `SCHLÜSSEL=WERT`. Zulässige Schlüssel sind
   ausschließlich die Register `BZ`, `AC`, `AR` sowie die Flags `FE`, `FÜ` (Schreibweise im Test: `FUE`),
   `BS`, `US`, `E`, `A`, `V1`, `V2` — also genau die Teilmenge, die auch in der abschließenden
   Zustandszeile des Interpreters ausgegeben wird (vgl. Abschnitt 8). Andere Register (z. B. OR) oder
   Flags (z. B. H, SP, T, SW, K1–K3) sind hier nicht vorgesehen. Die Zeile muss nicht vollständig sein:
   jeder der genannten Schlüssel darf, muss aber nicht angegeben werden; jeder darf höchstens einmal
   vorkommen.
   - `BZ=` und `AR=` je 4 Oktalstellen (Adressbreite, wie in Abschnitt 2 für Adressen festgelegt).
   - `AC=` 11 Oktalstellen (Maschinenwortbreite, wie in Abschnitt 2 für den Wert festgelegt).
   - Flag-Werte sind je genau eine Oktalstelle mit dem Wert `0` oder `1` (kein anderer Oktalwert
     zulässig).
2. **Beliebig viele** Speicherprüfzeilen, danach folgend, je eine pro Zeile, im selben Format wie die
   Adresse:Wert-Zeilen der Trommeldatei (Abschnitt 2): `Adresse: Wert` (Adresse 4, Wert 11 Oktalstellen).
   Sie legen fest, welchen Inhalt bestimmte Trommeladressen nach Testende haben müssen. Dieselbe Adresse
   darf nicht mehrfach mit widersprüchlichem Sollwert auftreten (wie bei den Trommeldatei-Zeilen selbst,
   s. Abschnitt 2/5).

Fehlt die Register-/Flag-Zeile (weil keine Register/Flags geprüft werden sollen), beginnt der Abschnitt
unmittelbar mit Speicherprüfzeilen. Sind weder eine Register-/Flag-Zeile noch Speicherprüfzeilen
angegeben (leerer `Prüfungen:`-Abschnitt), gilt das wie ein fehlender Abschnitt: keine Ergebnisprüfung.

**Beispiel** (wie oben skizziert):

```
Trommeldatei:
#DOK-0001 Test Ladebefehl und Addition
#PROT STUFE=2
0000: 00003000211
0001: 00003001210
0002: 00000001164
0003: 00000000020
# Beginn Datenbereich
3000: 00000000100
3001: 00000000045

Tastenfolge:
H G R

Prüfungen:
BZ=0003 AC=00000000045 AR=0003 FE=0 FUE=0 BS=0 US=1  E=0 A=0 V1=0 V2=0
0000: 00003000211
3000: 00000000100
3001: 00000000045
```

### 3a.2 Auswertung

Die Ergebnisprüfung wird erst nach Abschluss der interpretativen Abarbeitung der Tastenfolge und des
sich ggf. anschließenden Knotenautomaten-Durchlaufs vorgenommen, also gegen den dann erreichten
Endzustand (Register, Flags, Trommelinhalt).

Jede angegebene Register-/Flag-Zuweisung und jede angegebene Speicherprüfzeile wird einzeln mit dem
tatsächlich erreichten Wert verglichen. Das Gesamtergebnis ist:

- **Test wahr:** ausschließlich dann, wenn **alle** angegebenen Einzelprüfungen (Register, Flags,
  Speicherzellen) mit dem tatsächlichen Endzustand übereinstimmen.
- **Test falsch:** sobald **mindestens eine** der angegebenen Einzelprüfungen nicht übereinstimmt.

Im Protokoll (bzw. auf dem Bildschirm, s. 3a.3) wird zu jeder angegebenen Einzelprüfung sowohl der
Soll- als auch der Ist-Wert vermerkt, nicht nur das Gesamtergebnis — damit im Fehlerfall sofort
erkennbar ist, welche Einzelprüfung(en) abweichen.

**Test ohne ordnungsgemäßes Ende:** Bricht die Abarbeitung vor Erreichen eines regulären Endzustands ab
(Stub, Laufzeitfehler, Knotenlimit — s. Abschnitt 5, Grundsatz "laut scheitern"), wird keine
Ergebnisprüfung vorgenommen; ein in diesem Fall dennoch vorhandener `Prüfungen:`-Abschnitt bleibt ohne
Wirkung, es wird stattdessen vermerkt, dass die Ergebnisprüfung deswegen entfällt. Insbesondere gilt ein
solcher Fall nicht automatisch als `Test falsch`.

### 3a.3 Ausgabe

Die Ergebnisprüfung wird, unabhängig von der Protokollierungsstufe `#PROT STUFE=n` (Abschnitt 2,
analog zur `#DOK`-Diagnose in Abschnitt 7), stets zusätzlich auf dem Bildschirm ausgegeben. Bei
`#PROT STUFE=2` wird sie außerdem am Ende der Protokolldatei (Abschnitt 8) vermerkt, im Anschluss an die
dortige Endzustandszeile.

### 3a.4 Formale Gültigkeitsprüfung

Der `Prüfungen:`-Abschnitt unterliegt, wie Trommeldatei und Tastenfolge, der formalen
Gültigkeitsprüfung vor Testbeginn (s. Abschnitt 5): unbekannte Schlüssel in der Register-/Flag-Zeile,
ein Schlüssel mit falscher Stellenzahl oder unzulässigem Wert, ein mehrfach angegebener Schlüssel, eine
Speicherprüfzeile außerhalb des Adresse:Wert-Formats sowie eine widersprüchlich mehrfach belegte
Prüfadresse führen dazu, dass der Test **nicht startet** (Grundsatz "laut scheitern", keine
eigenmächtige Korrektur).

## 4. Weitere typische Tastensequenzen (zur Illustration, nicht Teil des Test-Starts)

Die folgenden Sequenzen sind **unabhängig voneinander**: jede führt nur die Wirkung ihrer eigenen,
tatsächlich aufgeführten Tasten aus. Es gibt **keinen** gemeinsamen oder anderweitig spezifizierten
Vor-Zustand — nicht genannte Register/Flags bleiben von der jeweiligen Sequenz unberührt und werden mit
ihrem (unspezifizierten) Vorwert notiert (z. B. ⟨AR⟩, ⟨OR⟩, ⟨BZ⟩, ⟨AC⟩).

### 4.1 Beseitigen der Betriebszustände US, BS, FÜ und FE

**Fall 1 — H, G**

| Aktion | Wirkung |
|---|---|
| H | H:=1 |
| G | alle Flags außer H, T, BS, SP := 0 (damit u. a. auch FÜ:=0, FE:=0, falls zuvor gesetzt; BS und SP sind eingerastete Schalter und bleiben unverändert, s. 3.3); zusätzlich wird **US:=1** gesetzt (Voraussetzung für "G" ist der Halt-Zustand, und "G" stellt BR auf "0000 000"); BR:="0000 000" (AR:=0000, OR:=000); K0 angewählt, T:=1; BZ unverändert |

*(Anmerkung: Ob die Hardware nach "H, G" tatsächlich US=1 anzeigt – etwa weil der zuvor programmierte
Stopp-Befehl formal noch nicht abgearbeitet ist – oder ob G stattdessen auch US auf 0 setzt, ist in der
Originaldokumentation nicht ausdrücklich belegt und bleibt offen. Wirkungslos ist es in jedem Fall: Der
Automat steht durch H, und "R" überwindet US unabhängig von seinem Wert.)*

Kein R in der Sequenz → Automat bleibt in H stehen. Programm ist unterbrochen.

**Fall 2 — ST**

| Aktion | Wirkung |
|---|---|
| ST | nur wirksam, wenn Zustand "Bedingter Stopp" oder "Unbedingter Stopp" vorliegt (elektronische Verriegelung); dann: OR := ⟨OR⟩ OR 240 → BR := ⟨AR⟩ (⟨OR⟩ OR 240); AR bleibt unverändert; US := 0; BR aufgestellt, noch nicht ausgeführt (Start bei Knoten 19 durch E oder R) |

H wird durch ST nicht beeinflusst (ST ist die einzige der hier genannten Tasten, die nicht an Stellung H
gebunden ist).

**Fall 3 — H, Ü, R**

| Aktion | Wirkung |
|---|---|
| H | H:=1 |
| Ü | nur wirksam, weil H gesetzt ist (ohne H: keine Wirkung); AR:="7777" (überschreibt unbedingt); OR := ⟨OR⟩ OR 240 → BR:="7777 (⟨OR⟩ OR 240)" |
| R | H:=0; Interpretation setzt bei Phase IV fort → Ausführung von BR |

**Fall 4 — H, M, R** (M ist hier gleichbedeutend mit M gedrückt und sofort M losgelassen, s. 3.3)

| Aktion | Wirkung |
|---|---|
| H | H:=1 |
| M | AR bleibt unverändert (⟨AR⟩); OR := ⟨OR⟩ OR 025 → BR:="⟨AR⟩ (⟨OR⟩ OR 025)"; kein E unter M, daher bleibt BR aufgestellt |
| R | H:=0; Interpretation setzt bei Phase IV fort (Knoten 19) → Ausführung von BR |

Die Zuordnung zu "US/BS wird übergangen" (Dokumenttext) ist keine aus der Tastenfolge selbst
ableitbare Tatsache, sondern gilt nur unter der Zusatzannahme des jeweiligen Anwendungsfalls, dass
AR/OR zufällig gerade den US-Befehl enthalten. Das gehört zur Anwendung, nicht zur Definition der
Sequenzen.

Übertragung auf BS, FÜ, FE (lt. Dokument "C8205-Interpreter-Bedienpult_mit_Schaltern.md"):
- **BS**: verhält sich wie US, alle vier Fälle anwendbar; zusätzlich muss der Schalter "BS" gelöst
  werden; bei Fall 4 zusätzlich: der nächste Befehl wird abgearbeitet.
- **FÜ**: nur Fall 1 (H, G) anwendbar; zusätzlich ein eigener Fall "H; E gedrückt halten; G; E
  loslassen", der nur den Überlauf löscht statt aller Flags/BR.
- **FE**: nur durch G aufhebbar (entspricht Fall 1, H, G).

### 4.2 Transport des Akkumulatorinhaltes nach Speicherplatz 7777

**Fall 5 — H, G, Ü, E** (E ist hier ein einzelner Tipp, E ohne M; Ü wirkt, weil H gesetzt ist)

| Aktion | Wirkung |
|---|---|
| H | H:=1 |
| G | alle Flags außer H,T,BS,SP := 0, danach US:=1; BR:="0000 000" (AR:=0000, OR:=000); K0 angewählt, T:=1; BZ unverändert (⟨BZ⟩) |
| Ü | AR:="7777"; OR := 000 OR 240 = 240 → BR:="7777 240" |
| E (einzelner Tipp) | Phase IV: Ausführung von BR="7777 240" → `<7777>:=<AC>`. Danach Phase I: `<AR>:=<BZ>` (=⟨BZ⟩). Danach Phase II: `<BZ>:=ADR; <OR>:=OP` (Inhalt der Zelle ⟨BZ⟩). Danach Phase III: `<AR>:=<BZ>=ADR`, gleichzeitig `<BZ>:=<AR>+1`. Automat stoppt danach wieder (H bleibt =1) |

Ergebnis: `<7777> := <AC>`, danach Stopp mit neu geladenem BR aus Zelle ⟨BZ⟩.

### 4.3 Transport des Befehlszählerinhaltes nach dem Akkumulator

**Fall 6 — H, G, M-gedrückt-halten, E, M-loslassen, E**

| Aktion | Wirkung |
|---|---|
| H | H:=1 |
| G | alle Flags außer H,T,BS,SP := 0, danach US:=1; BR:="0000 000" (AR:=0000, OR:=000); K0 angewählt, T:=1; BZ und AC bleiben unverändert (⟨BZ⟩, ⟨AC⟩ — G hat keinen Einfluss auf Akkumulator- und Befehlszählerinhalt) |
| M gedrückt halten | OR := 000 OR 025 = 025 → BR:="0000 025" (Sprung mit Rückkehrabsicht); solange M gehalten wird, verhindert ein nachfolgendes E die Befehlsentnahme in Phase II |
| 1. E (unter gehaltenem M) | Phase IV wird ausgeführt: BR="0000 025" → `<AC>` erhält die um 2 erhöhte Adresse ⟨BZ⟩+2 des nächsten abzuarbeitenden Befehls (im Adressfeld, s. 3.3); BZ := ⟨BZ⟩+1, AR := BZ; Phase II bleibt wegen gehaltenem M gesperrt, Automat steht vor Phase II |
| M loslassen | Sperre der Phase-II-Verhinderung entfällt |
| 2. E (einzelner Tipp) | Phase II und Phase III werden durchlaufen; danach stoppt die Abarbeitung wieder (kein R in der Sequenz, H bleibt =1) |

Ergebnis: `<AC> := ⟨BZ⟩+2`.

**Zusatzregel:** Schlägt man statt eines einzigen 1. E's dieses mehrfach an (weiterhin bei gehaltenem M,
vor dem M-Loslassen), erhöht sich die im AC abgelegte Adresse bei jedem zusätzlichen Anschlag um
weitere 1 — z. B. bei zweimaligem 1. E: `<AC> := ⟨BZ⟩+3`, und Speicherplatz 0002 wird als nächster
Befehl aufgestellt. Das 2. E (nach M-Loslassen) ist davon nicht betroffen; es ist ein einzelner,
separater Schritt zum Abschluss von Phase II/III.

## 5. Formale Gültigkeitsprüfung vor Testbeginn

Vor jedem Test sind die zum Test angegebenen Ausgangsbedingungen (Trommeldatei gemäß Abschnitt 2,
Tastenfolge gemäß Abschnitt 3) sowie die Debug-Anforderungen (Testmarken `#DOK-xxxx`, `#SPEI-xxxx` und `#SPUR-xxxx`,
s. Abschnitt 2) formal auf Gültigkeit zu prüfen. Der Test startet nur, wenn diese Prüfung insgesamt
positiv verläuft; andernfalls startet der Test nicht.

Zu prüfen ist dabei insbesondere:

- **Trommeldatei:** Einhaltung des in Abschnitt 2 festgelegten Zeilenformats (Adresse 4 Oktalstellen,
  Wert 11 Oktalstellen, ausschließlich Oktalzahlen, zulässige Kommentar- und Leerzeilen); zusätzlich:
  keine Adresse ist mehrfach mit widersprüchlichem Wert belegt (jede Adresse hat innerhalb eines Tests
  genau einen definierten Speicherinhalt).
- **Testmarken `#SPEI-xxxx`:** Eine solche Testmarke ist nur zu einem im selben Test bereits
  definierten `#DOK-xxxx` mit gleichem `xxxx` zulässig; die angegebene Adressspanne `ssss-eeee` muss
  eine gültige Spanne bilden (s. dazu den Hinweis in Abschnitt 2 zum dortigen mutmaßlichen Tippfehler).
- **Testmarke `#PROT STUFE=n`:** `n` ist eine der Ziffern 0, 1 oder 2; die Marke kommt höchstens
  einmal vor. Fehlt sie, ist das gültig (Standardwert STUFE=1).
- **Tastenfolge:** Sie definiert, wie in Abschnitt 3 beschrieben, den Ausgangszustand des Rechners vor
  Eintritt in Konnektor B vollständig; eine Tastenfolge, aus der sich kein vollständig definierter
  Ausgangszustand ergibt, ist nicht gültig. Ungültig sind insbesondere (s. 3.3): M losgelassen ohne vorheriges M gedrückt, M gedrückt bei bereits
  gedrücktem M, R oder Ende der Tastenfolge bei noch gedrücktem M, unbekannte Tasten sowie ein Ende weder
  mit `R` noch im Halt (H gesetzt). Ü und E bei nicht gesetztem H sind gültig, aber ohne Wirkung.
- **Abschnitt `Prüfungen:` (optional, s. Abschnitt 3a):** sofern vorhanden, müssen die Register-/
  Flag-Zeile (zulässige Schlüssel, Stellenzahl, Flag-Wert 0/1, keine Mehrfachnennung eines Schlüssels)
  und die Speicherprüfzeilen (Adresse:Wert-Format, keine widersprüchlich mehrfach belegte Prüfadresse)
  den in Abschnitt 3a.1/3a.4 festgelegten Vorgaben entsprechen.

Ergibt die formale Prüfung eine Unstimmigkeit – sei es beim Zeilenformat, bei einer widersprüchlich
mehrfach belegten Adresse, einer ungültigen
`#SPEI-xxxx`-Spanne oder einer unvollständig definierenden Tastenfolge –, so darf der Test **nicht
eigenmächtig korrigiert und gestartet werden**. Die Durchführung wartet in diesem Fall auf eine
Klärung mit dem Auftraggeber; erst nach dieser Klärung (ggf. mit korrigierten Ausgangsdaten) kann der
Test regulär gestartet werden.

> **Grundsatz "laut scheitern":** Ergibt sich bei der Durchführung eines Tests – sei es bei der
> formalen Prüfung (s. o.) oder später bei der Abarbeitung des Knotengraphen – eine Unklarheit, ein
> Widerspruch oder eine fehlende Festlegung, wird dies **laut gemeldet und der Test angehalten**, statt
> eigenmächtig eine Annahme zu treffen und stillschweigend fortzufahren. Dieser Grundsatz gilt
> unabhängig davon, ob der Test durch den Python-Interpreter oder durch eine interpretierende KI
> (s. Abschnitt 1a) durchgeführt wird.

## 6. Interaktive Zeichenein- und -ausgabe während der interpretativen Abarbeitung

### 6.1 Kanal K0 (Flag T oder SW): Eingabe über die Host-Tastatur

#### 6.1.1 Trigger und Abgrenzung

Erreicht die interpretative Abarbeitung des Knotenautomaten einen Eingabebefehl ("Eingabe-Halt", vgl.
Flag E, Definition Datei "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md"), bei dem Kanal K0 angewählt ist
und dabei entweder Flag T oder Flag SW gesetzt ist (Tastatur- bzw. Schreibwerkeingabe, s. Dateien
"C8205-Interpreter-Bedienpult_mit_Schaltern.md", Abschnitt "Schalter 'SW'", und "C8205-Interpreter-Lochstreifenleser.md", Abschnitt A5, zu K0),
so wird die Eingabe – anders als bei den Lochstreifenlesern (Kanäle K1/K2, dort Eingabe aus der
jeweiligen, in Abschnitt 2 beschriebenen Trommel-/Quelldatei) – nicht aus einer Datei entnommen,
sondern über die Tastatur des Host-Systems angefordert und entgegengenommen.

Diese Regelung betrifft ausschließlich Eingabebefehle mit K0 + (T oder SW); Eingabebefehle auf K1/K2
sind hiervon nicht berührt und bleiben wie bisher definiert.

#### 6.1.2 Ablauf

1. Der Interpreter stellt beim Erreichen des Eingabebefehls fest, dass K0 angewählt und Flag T oder
   Flag SW gesetzt ist.
2. Die den Test durchführende KI (Claude bzw. die jeweils interpretierende KI) fordert daraufhin auf
   dem Host-Bildschirm die Eingabe eines Zeichens an und stellt diese Anforderung dar.
3. Das über die Host-Tastatur eingegebene Zeichen wird entgegengenommen und gemäß der geltenden
   Zeichenkode-Tabelle (Datei "C8205-Interpreter-Kodetabellen.md") in die entsprechende Eingabeverschlüsselung umgesetzt –
   analog zur Behandlung der physischen Eingabetasten (s. Datei "C8205-Interpreter-Bedienpult_mit_Schaltern.md", Abschnitt
   "Eingabetasten": disjunktive Verknüpfung mit dem Adressregister, danach Aufhebung der Sperre durch
   Umstellung des Eingabebefehls).
4. Die Eingabe erfolgt zeichenweise: Pro zu interpretierendem Eingabebefehl wird genau eine
   Host-Tastatur-Eingabe angefordert und entgegengenommen – nicht etwa eine ganze Zeile oder mehrere
   Zeichen auf einmal. Die Anzahl der Anforderungen im Testablauf ergibt sich damit unmittelbar aus der
   Anzahl der tatsächlich zu interpretierenden Eingabebefehle mit K0 + (T oder SW).

#### 6.1.3 Einordnung

Diese Festlegung gilt für die interpretative Abarbeitung des Knotenautomaten (s. Abschnitt 1, Punkt 2)
und ersetzt dort die physische Eingabe über Tastatur bzw. Schreibwerk durch die Host-Tastatur der
jeweils ausführenden KI.

### 6.2 Kanäle K1/K2 (Lochstreifenleser): Eingabe über virtuelle Lochstreifen-Dateien

#### 6.2.1 Trigger und Abgrenzung

Erreicht die interpretative Abarbeitung des Knotenautomaten einen Eingabebefehl ("Eingabe-Halt"), bei
dem über die aktive Kanalanwahl ein Lochstreifenleser angefordert wird (Kanal K1 = Leser 1, Kanal K2 =
Leser 2, s. Datei "C8205-Interpreter-Lochstreifenleser.md", Abschnitt A5), so wird die Eingabe nicht über die Host-Tastatur
(s. 6.1) angefordert, sondern aus einer für den jeweiligen Leser angeforderten Textdatei entnommen, die
den "virtuellen Lochstreifen" dieses Lesers repräsentiert.

Für Leser 1 (K1) und Leser 2 (K2) sind stets getrennte Lochstreifendateien zu verwenden; eine für einen
der beiden Leser angeforderte Datei wird nicht für den jeweils anderen Leser herangezogen.

#### 6.2.2 Zeichenentnahme und Nachfordern neuer Dateien

Aus der für den jeweiligen Leser aktuell geladenen Lochstreifendatei wird für jeden von diesem Leser zu
interpretierenden Eingabebefehl jeweils ein Zeichen (eine Zeile gemäß 6.2.4) entnommen, fortlaufend in
der in der Datei vorliegenden Reihenfolge.

Ist die für einen Leser aktuell geladene Datei zu Ende (keine weitere Zeile mehr vorhanden) und tritt für
denselben Leser ein weiterer Eingabebefehl auf, wird für diesen Leser eine neue Lochstreifendatei
angefordert.

#### 6.2.3 Wiederverwendung nicht verbrauchter Dateien

Wird eine für einen Leser angeforderte Lochstreifendatei durch die im bisherigen Testverlauf
tatsächlich aufgetretenen Eingabebefehle dieses Lesers nicht vollständig "verbraucht" (es sind also noch
nicht entnommene Zeilen vorhanden), so bleibt diese Datei für den Leser geladen und wird bei einem im
weiteren Testverlauf folgenden Eingabebefehl desselben Lesers weiterverwendet – die Entnahme setzt dabei
an der zuletzt entnommenen Stelle fort (s. 6.2.2) –, bis die Datei ihrerseits zu Ende ist oder die
Interpretation endet (s. 6.2.5).

#### 6.2.4 Format der virtuellen Lochstreifendateien

Das Format der virtuellen Lochstreifendateien ist binär und an die Datenspuren-Spalten "w v u p 8 Tr 4 2
1" der Tabelle 1 (Datei "C8205-Interpreter-Kodetabellen.md", Abschnitt 1) angelehnt, dargestellt mit den Zeichen "0"/"1"
("1" = Lochung vorhanden, "0" = keine Lochung). Die Transportlochung Tr (ohne Information, s. Datei
"C8205-Interpreter-Lochstreifenleser.md", Abschnitt A4) wird dabei nicht dargestellt. Eine Zeile der Datei besteht somit aus
den acht 0/1-Werten der Datenspuren w v u p 8 4 2 1 (in dieser Reihenfolge) und repräsentiert jeweils
eine Lochungszeile (ein Zeichen) des virtuellen Lochstreifens.

#### 6.2.5 Ende der Interpretation

Geht der Rechner in den Halt-Zustand über (Stopp-Befehl, Fehler-Halt oder auf sonstige Weise), werden
alle für den betreffenden Test ggf. geladenen bzw. angebrochenen Lochstreifendateien – für Leser 1 und
Leser 2 gleichermaßen – beendet und entfernt.

Eine neue Interpretation eines Tests fordert ihre eigenen Lochstreifendateien für Leser 1 und Leser 2
unabhängig neu an; eine Wiederverwendung von Dateien über das Ende einer Testinterpretation hinaus
findet nicht statt.

### 6.3 Ausgabebefehle

#### 6.3.1 Kanal K0 (Schalter/Flag SW): Ausgabe in die Datei "sw-ausgabe.txt"

**Trigger und Wartebedingung**

Wird bei der interpretativen Abarbeitung ein Ausgabebefehl ("Ausgabe-Halt", Flag A, vgl. Datei
"C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md") gestellt, der Kanal K0 und dabei den Schalter/Flag SW
betrifft, so wartet dieser Ausgabebefehl, bis der Schalter SW auf "EIN" (gedrückt) steht.

(Hinweis: Die Kanaltabelle in Datei "C8205-Interpreter-Bedienpult_mit_Schaltern.md" weist die programmierte
Schreibwerkausgabe Kanal K2 zu; die hier beschriebene Wartebedingung und Dateiausgabe betreffen die
Kopplung des Schalters SW mit der Schreibwerkausgabe, s. dort Abschnitt "Schalter 'LS' und Stellung
'SW'". Die genaue Klärung dieses Zusammenspiels bleibt – analog zu anderen an dieser Stelle im
Dokument bereits vermerkten offenen Punkten – ausstehend; für die vorliegende Festlegung maßgeblich
ist allein der Zustand des Schalters SW.)

Sobald die Wartebedingung erfüllt ist, erfolgt die Ausgabe in eine Datei "sw-ausgabe.txt".

**Anlegen und Fortführen der Datei**

Die Datei "sw-ausgabe.txt" wird für einen Test höchstens einmal angelegt. Sie wird nicht angelegt, wenn
der betreffende Test keine Ausgabe auf SW vornimmt. Erfolgen im Testverlauf mehrere Ausgaben auf SW,
wird stets dieselbe, bereits angelegte Datei fortgeführt (Ausgabe wird angehängt, nicht überschrieben).

**Zeichenweise Ausgabe und Zeilenende**

Die Ausgabe erfolgt zeichenweise. Das Zeichen WRZL (Wagenrücklauf Zeilenvorschub) kennzeichnet dabei das
Erreichen des Zeilenendes: Bei Ausgabe von WRZL wird die aktuelle Zeile der Datei abgeschlossen, ggf.
nachfolgende Ausgaben beginnen auf einer neuen Zeile. Mehrere unmittelbar aufeinanderfolgende
WRZL-Ausgaben erzeugen entsprechend mehrere Leerzeilen.

**Bereitstellung am Testende**

Eine im Testverlauf ggf. erzeugte Datei "sw-ausgabe.txt" wird am Ende des Tests zum Download
bereitgestellt.

#### 6.3.2 Kanal K1 (Lochstreifenstanzer): Ausgabe in die Datei "stanzer-ausgabe.txt"

Für Ausgabebefehle auf Kanal K1 (Lochstreifenstanzer, s. Datei "C8205-Interpreter-Lochstreifenleser.md", Abschnitt B5) gilt
Abschnitt 6.3.1 sinngemäß entsprechend: höchstens eine Datei je Test, Anlegen nur bei tatsächlich
erfolgter Ausgabe, Fortführung derselben Datei bei mehreren Ausgaben, Bereitstellung zum Download am
Testende. Eine Wartebedingung wie beim Schalter SW ist hier nicht vorgesehen.

Abweichend von 6.3.1 werden jedoch ALLE Zeichen jeweils in einer eigenen Zeile im Binärformat
ausgegeben, gemäß den Datenspuren-Spalten "w v u p 8 Tr 4 2 1" der Tabelle 1 (Datei "C8205-Interpreter-Kodetabellen.md",
Abschnitt 1; "1" = Lochung vorhanden, "0" = keine Lochung); die Transportlochung Tr wird dabei, wie
schon bei den virtuellen Lochstreifen-Eingabedateien (s. 6.2.4), nicht dargestellt. Eine Zeile besteht
somit aus den acht 0/1-Werten der Datenspuren w v u p 8 4 2 1 (in dieser Reihenfolge) und repräsentiert
jeweils ein ausgegebenes Zeichen. Das Konzept "Zeilenende durch WRZL" (s. 6.3.1) ist auf diese Datei
nicht anwendbar, da hier ohnehin jedes Zeichen bereits eine eigene Zeile bildet.

## 7. Diagnoseausgabe bei Befehl 164 (Leerbefehl) mit Testmarken `#DOK`/`#SPEI`

Die im Folgenden beschriebene Diagnoseausgabe ist, wie die zugrundeliegenden Testmarken `#DOK-xxxx` und
`#SPEI-xxxx` (s. Abschnitt 2), eine von der realen Hardware abweichende, zusätzliche Definition, die
ausschließlich der besseren Durchführung von Tests mit dem Interpreter dient und keine Entsprechung in
der physischen Elektronik des C 8205 hat.

### 7.1 Auslösebedingung

Tritt bei der Interpretation der im virtuellen Trommelspeicher definierten Befehlsfolge der Befehl 164
(oktal; Leerbefehl, B=1/A=6/Z=4, s. Variablentabelle T2, Kommentar zu ANWEISUNG-008) mit einer Adresse a
auf, für die in der Trommeldatei eine Testmarke `#DOK-xxxx` mit xxxx=a definiert ist, so wird zusätzlich
zur regulären Abarbeitung die im Folgenden beschriebene Diagnoseausgabe vorgenommen.

### 7.2 Ablauf

1. Der Befehl 164 wird zunächst interpretativ genau so abgearbeitet, wie es der Knotenautomat für
   diesen Befehl vorgibt; die Ausführung selbst erfährt keine Sonderbehandlung.
2. Danach wird in die Protokolldatei des Tests (s. Abschnitt 8) geschrieben:
   - die Testmarke `#DOK-xxxx` mit dem in der Trommeldatei zugehörig angegebenen Text,
   - der Inhalt der Register `<BZ>` und `<AC>`,
   - die Werte der Flags FE, FÜ, BS, US, E, A (Ü steht hier für Flag FÜ, s. Flagtabelle in Datei
     "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md").
3. Ist zu demselben xxxx zusätzlich eine Testmarke `#SPEI-xxxx ssss-eeee` in der Trommeldatei definiert,
   werden danach zusätzlich alle virtuellen Trommelinhalte der Adressen ssss bis eeee zeilenweise in die
   Protokolldatei geschrieben, jeweils Adresse und Inhalt in Oktalziffern (Zeilenformat entsprechend
   Abschnitt 2: "Adresse: Wert").
4. Ist zu demselben xxxx zusätzlich eine Testmarke `#SPUR-xxxx aaaa` definiert, werden danach (nach
   allen `#SPEI-xxxx`-Ausgaben) alle 32 Zellen der Spur, in der `aaaa` liegt, zeilenweise ausgegeben, und
   zwar in physischer Zugriffsreihenfolge der Trommel (s. Abschnitt 2); Zeilenformat wie bei `#SPEI-xxxx`.
5. Danach wird die Interpretation gemäß Knotenautomat regulär fortgesetzt.

Diese Bildschirmausgabe der Diagnoseinformationen erfolgt unabhängig von der in `#PROT STUFE=n`
(s. Abschnitt 2) festgelegten Protokollierungsstufe stets zusätzlich auf dem Bildschirm; sie ist von
der in Abschnitt 8 beschriebenen, stufenabhängigen Protokollierung des gesamten
Knotenautomaten-Durchlaufs zu unterscheiden. Bei STUFE=2 wird sie außerdem, wie in Schritt 2 oben
beschrieben, zusätzlich in die Protokolldatei geschrieben.

## 8. Protokolldatei je Test

Bei Protokollierungsstufe STUFE=2 (s. `#PROT STUFE=n`, Abschnitt 2) wird für den Test eine eigene
Protokolldatei ("protokoll.txt") angelegt. Sie ist von den in Abschnitt 6.3 beschriebenen Dateien
"sw-ausgabe.txt" und "stanzer-ausgabe.txt" zu unterscheiden: Während jene nur bei tatsächlich erfolgter
Ausgabe auf dem jeweiligen Kanal angelegt werden, wird die Protokolldatei bei STUFE=2 für den gesamten
Test angelegt, unabhängig davon, ob Ausgabebefehle auftreten. Bei STUFE=0 und STUFE=1 entsteht keine
Protokolldatei.

### 8.1 Inhalt

Bei STUFE=2 enthält die Protokolldatei, in der zeitlichen Reihenfolge ihres Auftretens während des
Tests:

- die Protokollierung der Ausgangsbedingungen: die übernommene Trommeldatei (Abschnitt 2) sowie die
  Tastenfolge zur Definition des Ausgangszustands mit ihrer Wirkung auf Register und Flags
  (Abschnitt 3),
- die Protokollierung der Zustände des Knotenautomaten: die beim Durchlauf des Knotengraphen ab
  Konnektor B (Datei "C8205-Interpreter-Eingänge_der_Knoten.md") jeweils erreichten Knoten in der durchlaufenen Reihenfolge,
- die angeforderten Debug-Ausgaben gemäß Abschnitt 7 (`#DOK-xxxx`-Ausgaben mitsamt Registern und Flags
  sowie ggf. zugehörige `#SPEI-xxxx`- und `#SPUR-xxxx`-Speicherauszüge),
- abschließend, sofern für den Test ein `Prüfungen:`-Abschnitt angegeben ist (Abschnitt 3a), die
  Ergebnisprüfung: je geprüftem Register/Flag bzw. je geprüfter Speicherzelle Soll- und Ist-Wert, sowie
  das Gesamtergebnis `Test wahr` / `Test falsch`.

### 8.2 Bildschirmausgabe der Zustände des Knotenautomaten

Bei STUFE=1 wird die Protokollierung der Zustände des Knotenautomaten auf dem Bildschirm ausgegeben,
in möglichst einzeiliger, knapper Form (z. B. eine Zeile je durchlaufenem Knoten); da bei STUFE=1 keine
Protokolldatei entsteht (s. o.), ist dies dort die einzige Aufzeichnung dieser Zustände. Bei STUFE=2
entfällt diese Bildschirmausgabe; die Zustände werden stattdessen gemäß 8.1 in die Protokolldatei
geschrieben. Bei STUFE=0 entfällt sie ebenfalls, ohne Ersatz durch eine Protokolldatei. Die
Diagnoseausgaben zu Befehl 164 (Abschnitt 7) sind von dieser stufenabhängigen Regelung nicht erfasst;
sie erscheinen stufenunabhängig immer auf dem Bildschirm.

### 8.3 Bereitstellung am Testende

Die Protokolldatei wird, sofern sie angelegt wurde (STUFE=2, s. o.), am Ende des Tests zum Download
bereitgestellt.

## 9. Ausblick

Mit Abschnitt 3 ist das initiale Starten eines in der Trommeldatei definierten Tests vollständig
beschrieben. Abschnitt 4 ergänzt dies um weitere, vom Teststart unabhängige Tastensequenz-Beispiele.
Der eigentliche Durchlauf durch den Knotengraphen ab Konnektor B ist in der Datei
"C8205-Interpreter-Eingänge_der_Knoten.md" beschrieben.
