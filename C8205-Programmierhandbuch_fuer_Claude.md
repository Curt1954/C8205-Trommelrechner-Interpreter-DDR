# C 8205 – Programmierhandbuch für Claude

Version: 0.95-020

Zweck: Nachschlagewerk zur Karte `CLAUDE.md`, die zuerst gelesen wird. Hier steht das Kurzwissen, mit dem Claude in einer neuen Sitzung ohne Einlesen von über 1 MB Dokumentation Assemblerprogramme für den C 8205 schreibt, assembliert und im Interpreter prüft. Schnellstart, Rückgabecodes und Selbsttest stehen in der Karte. Zwei Anhänge liegen als eigene Dateien in `markdown-dateien/` und werden nur bei Bedarf gelesen: Anhang A (Trommelzeit, GRAFIK-Interpreter) und Anhang B (BIS-Minimalprogramm).
Maßgeblich bleiben die Quellen; bei Abweichung gilt die Quelle (Assembler: die `.odt`).
Kennzeichen: **[geprüft]** = in der Arbeitsumgebung ausgeführt, **[Beispiel]** = nur aus einem Beispielkommentar.

## 0. Von der `.test` des Assemblers zum Test

Kurzform: `Assembler/asm_und_test.sh <ordner> <name> [AAAA=WERT ...]` assembliert, ergänzt die `.test` wie unten beschrieben und startet den Interpreter (von überall aufrufbar **[geprüft]**). Die folgenden Schritte sind das, was das Skript tut.

**Die vom Assembler erzeugte `.test` enthält keine Prüfung** (Lauf endet mit Rückgabecode 4, nicht 0) **[geprüft]**. Vor dem Lauf ergänzen: `#TROMMEL=LEER` unter `#PROT STUFE=2` einfügen, `#SPEI-0001 0000-0000` auf die Ergebniszellen setzen (z. B. `0001-0002`) und ans Ende anhängen:
```
Prüfungen:
US=1
0001: 00000000017      (Ergebniszelle: vorher von Hand herleiten, Abschnitt 7)
```

## 1. Arbeitsregeln (vom Projektinhaber)

Die Regeln stehen nur in der Karte `CLAUDE.md` („Regeln des Projektinhabers“) und gelten unverändert.

## 2. Arbeitsumgebung (alles **[geprüft]**)

| Thema | Regel |
|---|---|
| Entpacken | `LC_ALL=C.UTF-8 unzip -q Datei.zip`. In der POSIX-Locale entstehen Namen wie `C8205-Interpreter-Eing#U00e4nge_der_Knoten.md` statt `…Eingänge…`, und der Interpreter bricht ab mit „Knotengraph nicht gefunden". Reparatur: `#UXXXX` im Dateinamen durch das Unicode-Zeichen ersetzen. Bei einem Zip, dessen Namen in CP437 gespeichert sind (ältere Zips), hilft stattdessen `unzip -O CP437 Datei.zip`. |
| Entpackte Archive | Untrusted: in ein neues leeres Verzeichnis, Python mit `-I` starten. |
| Assembler | **Immer aus dem Ordner `Assembler/` starten** (`./c82ass.sh …`). Von anderswo: „./_Linux/c82ass: not found". Linux-Binary liegt in `Assembler/_Linux/`. Absoluter Pfad bei `-p` funktioniert. |
| Interpreter | Aus dem Projektstamm: `python3 -I c8205_interp.py --MODUS=TEST <Testdatei>`. Python 3 genügt, keine Pakete. |
| Laufzeiten | Assemblieren < 10 ms, ein Test rund 70 ms. Rechne also großzügig mit vielen kurzen Läufen. |
| Nebenwirkungen | Der Assembler schreibt `Assembler/projekdetails` (letzte `-p`/`-s`, Rest der letzten Sitzung). Der Interpreter schreibt `Test-Protokolle/<test>/protokoll.txt` und **ändert `Trommel/trommel.txt` dauerhaft**. |
| `--NO-TERMOUT` | Unterdrückt auch die Endzeile und die Ergebnisprüfung auf dem Terminal. Nur den Rückgabecode sieht man dann. Zum Lesen weglassen. |

Den Aufruf zeigt die Karte `CLAUDE.md`. `--WARN=ALLE` meldet unbenutzte Symbole, Sprünge auf Datenworte und toten Code. Das sind Hinweise, keine Fehler. Selbstmodifizierender Code löst sie zu Recht aus.
Erzeugt werden `.obj .mqo .sym .dmp .log .test` im Projektordner. Bei `--ABSPR` zusätzlich ein binärer Lochstreifen `.kep`.

## 3. Das Maschinenmodell in Kurzform

Quellen: `markdown-dateien/C8205-Interpreter-Magnettrommel.md`, `markdown-dateien/C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md`.

- Einadreßmaschine, **Akkumulator AC** (33 Bit), Befehlszähler BZ, Adreßregister AR. Kein Indexregister, kein indirekter Sprung.
- Speicher: Magnettrommel, **4096 Worte zu 33 Bit**, Adressen 0000 bis 7777 oktal. Eine Adresse besteht aus Spur (7 Bit) und Sektor (5 Bit):
  **Spur = Adresse ÷ 040 (oktal), Sektor = Adresse mod 040.** Beispiel: 0040 ist Spur 1, Sektor 0.
- Wort = 11 Oktalziffern: `0000 aaaa BAZ`. Die Adresse `aaaa` steht in den Ziffern 7 bis 4, der Operationscode `BAZ` in den letzten drei.
  `00000007065` ist also der Befehl `065` mit Adresse 0007.
- **Adresseneinheit** (1°) im Wort: `01000` (oktal). Wer eine Adresse im AC um 1 erhöht, addiert `dw 01000`, nicht `1`.
- Zahlen: Festkomma, negative Werte im Zweierkomplement (`dw -5` ergibt `77777777773`).
- Beim Halt (`020`) steht BZ **auf Adresse des Stopps + 1** **[geprüft]**.
- Die Zellen 0002 bis 0037 belegt das KEP (Kleines Eingabeprogramm). Laden dorthin warnt der Assembler bei `--ABSPR`. 0000 und 0001 sind erlaubt (dort trägt das geladene Programm seinen Sprung zur Startadresse ein).
  Quelle: `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md`, „Schalter `--ABSPR`".
- Der Arbeitsbereich des BIS liegt auf 7600 bis 7777 (siehe Anhang B, `markdown-dateien/C8205-Programmierhandbuch-Anhang_B_BIS_Anschluss.md`).

## 4. Befehlscodes lesen und die gebräuchlichen Codes

Quelle: `markdown-dateien/C8205-Interpreter-Befehlsliste.md`, Abschnitte „generische Befehlszusammenfassung" und „Einzelbefehlsübersicht" (bei Widerspruch gilt die Einzelbefehlsübersicht).
Alle 512 Codes 000 bis 777 sind definiert (siehe Sweep `testscripte/c8205_befehlssweep.py`).

**Code = B A Z (drei Oktalziffern).**

- **B** Befehlstyp: 0 Organisation 1. Art · 1 Organisation 2. Art · 2 Einzelbefehl · 3 markierter Einzelbefehl (setzt zusätzlich den Vergleicher) · 4 Gruppenbefehl G · 5 verkürzter G (GX) · 6 Wiederholung W · 7 verkürzter W (WX).
- **A** Operationsart (je nach B anders gedeutet, siehe Tabellen unten).
- **Z** Zusatz: `Z = 0` nichts · `1` AC vorher **löschen** · `2` Ergebnis rechts schieben · `3` löschen + rechts · `4` links · `5` löschen + links · `6` zyklisch links · `7` löschen + zyklisch links.
  Das Löschen wirkt **vor** der Operation (Phase III). `211` ist daher „Laden", `241` „Zelle := 0 und AC := 0".

### 4.1 Die Codes, die ich ständig brauche

| Code | Wirkung | Anmerkung |
|---|---|---|
| `000` | Sprung nach a | `001` löscht dabei den AC |
| `025` | Sprung mit Rückkehrabsicht | AC := Rückkehrwort `0000 <Adresse hinter dem 025> 000`, siehe 5.3 **[geprüft]** |
| `065` | wie `025`, aber nur wenn Schalter SP gesetzt | sonst AC := 0 und kein Sprung **[Beispiel]** (`Assembler/Claude/bedsprung.asm`) |
| `020` | Stopp | `060`: nur wenn Schalter BS gesetzt |
| `040` / `050` | Sprung, wenn AC < 0 / AC ≥ 0 | bei nicht erfüllter Bedingung keine Verschiebung |
| `070` | Sprung bei Überlauf | löscht den Überlauf |
| `211` | AC := ⟨a⟩ (laden) | `210` AC := AC + ⟨a⟩ · `220` AC := AC − ⟨a⟩ · `221` AC := −⟨a⟩ |
| `240` | ⟨a⟩ := AC (speichern) | `241` ⟨a⟩ := 0, AC := 0 |
| `200` | AC := AC ∧ ⟨a⟩ (Ausblenden von Bits) | `250` ⟨a⟩ := AC ∧ ⟨a⟩ · `260` ⟨a⟩ := ¬AC ∧ ⟨a⟩ |
| `251` | **R-Lesebefehl**: AC := ⟨Adresse aus dem Adreßfeld des AC⟩ | Operand meist `0`. `271` liefert das Negative. Das ersetzt den fehlenden Indexregister. |
| `330` | Vergleich AC mit ⟨a⟩, **keine Operation** | setzt Vergleicher: AC < a → V1, AC > a → V2, AC = a → V1 und V2 |
| `140` | Sprung, wenn V1 oder „V3" (V3 = V1 und V2 gesetzt) | nach `330`: AC ≤ a |
| `150` | Sprung, wenn V2 oder „V3" | nach `330`: AC ≥ a |
| `170` | Sprung, wenn „V3" | nach `330`: AC = a |
| `311` | AC := ⟨a⟩ und Vergleicher setzen | nach dem Löschen steht 0 im AC, also V3 genau bei ⟨a⟩ = 0 **[Beispiel]** (`pj2-bis_minimalprogramm_v3.asm`, Kommentar) |
| `010` / `011` | Eingabe eines Zeichens (ohne / mit Löschen) | siehe 5.6 |
| `030` / `031` | Ausgabe eines Zeichens bzw. **Anwahl** eines Kanals | Operand `04700` K0, `04600` K1, `04500` K2 (Schreibwerk), `04400` K3. Im Quelltext `ANWAHL K2`. |
| `164` | Leerbefehl | Im Interpreter löst `164 nnnn` die Diagnoseausgabe `#DOK-nnnn` aus (Abschnitt 7) |

Schiebekombinationen: Die Z-Ziffer hängt hinten dran. Beispiel `217` lädt mit zyklischer Linksverschiebung, `212` addiert und schiebt rechts.
Die Multiplikation nutzt die bedingte Addition mit Rechtsverschiebung (`232`, als Gruppenbefehl `432`; Quelle: Befehlsliste, Abschnitt „Vollständige Befehlsübersicht").
Rechnen mit Verschiebung (Multiplikation, Division): Vorlagen in `Tests/bsp_6_1_*` bis `bsp_6_3_*`. Dort nachsehen statt neu herleiten.

### 4.2 Gruppen- und Wiederholungsbefehle (B = 4 bis 7)

- Die Operation von A/Z gilt wie bei B=2, aber für **alle 32 Zellen der Spur** (G) bzw. vom adressierten Sektor bis zum Spurende (W, n = 1 bis 32 Zellen).
- GX/WX brechen zusätzlich ab, sobald der AC negativ wird.
- Nützlich: `440 a` speichert den AC in alle 32 Zellen der Spur, `441 a` füllt die Spur mit 0 (und löscht den AC). Ein Beispiel für `520` (GX-Subtraktion) steht am Ende der Befehlsliste. Beispiel für `616`: ab einer Zelle, die 12 Zellen vor dem Spurende liegt, ergibt es 12 zyklische Linksverschiebungen (Vorlage `Assembler/Projekt_2/pj2-bis_minimalprogramm_v3.asm`, Zelle `nz_12`).
- Zusatztrommeln (**experimenteller Prototyp C8205Z**, nur mit dem Schalter `--C8205Z`): `5k00 030` wählt die Zusatztrommel k (1 bis 4), `zzz0 bbbb 601` gibt eine ganze Spur der Haupttrommel aus, `zzz0 bbbb 661` liest sie zurück. Ohne den Schalter sind `601` und `661` wie bisher Leer-Operationen mit Löschen; für normale Programme ändert sich nichts.
- Gruppenbefehle **lesen oder verändern jede Zelle der Spur**. Eine belegte Zelle im Feld wird zerstört. Quelle: `Bausteininterpretiersystem BIS/markdown-dateien/C8205-Interpreter-BIS.md`, „Arbeitszellen des Minimalprogramms".

## 5. Programmieridiome (die Beispiele sind **[geprüft]**: assembliert, im Interpreter gelaufen, Test wahr)

### 5.1 Programmgerüst

```
                start                ; Zählung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
...Daten und Unterprogramme...
haupt:          ...
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
ende:           end
```

- Zellen mit `db` bekommen **keinen** Wert in der `.test`-Datei (sie stammen aus dem Trommelstand!). Jede Zelle, die ich lese, vorher mit `dw 0` oder `241` initialisieren.
- Ziel „absolut adressiert" (BIS-Minimalprogramm): Pragma `;#; LEITADRESSE 00` **vor** `start`, `start` ohne Operand, mit `equ 0100` usw. an feste Orte springen. Siehe `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md`, „Pragma LEITADRESSE".
- `equ <wert>` setzt den Befehlszähler, `equ *` gibt dem Symbol den Zählerstand, `equ40 / equ100` runden auf das nächste Vielfache, `spa nn` setzt die rechten zwei Oktalziffern (Sektor), `abs nn` definiert eine feste Adresse (nicht verschieblich).

### 5.2 Schleife mit Zähler und Vergleich (Summe 1 bis 5 = 15)

```
                start
                000     haupt
summe:          dw      0
zaehler:        dw      0
eins:           dw      1
fuenf:          dw      5
haupt:          241     summe        ; summe := 0, AC := 0
                241     zaehler      ; zaehler := 0
schleife:       211     zaehler      ; AC := zaehler
                210     eins         ; AC := zaehler + 1
                240     zaehler      ; zaehler := AC
                210     summe        ; AC := summe + zaehler
                240     summe        ; summe := AC
                211     zaehler      ; AC := zaehler
                330     fuenf        ; Vergleich AC mit 5 (keine Operation)
                170     fertig       ; gleich: fertig
                000     schleife
fertig:         164     0001
                020     0
ende:           end
```

Ergebnis: Zelle `0001` = `00000000017`, `0002` = `00000000005`.

### 5.3 Unterprogramm mit Rückkehr

```
rueck:          db      1            ; Laufzeit: hier steht 000 <Rückkehradresse>
haupt:          025     up           ; Aufruf
                025     up
                025     up
                020     0
up:             240     rueck        ; erste Zeile jedes Unterprogramms: Rückkehrwort sichern
                211     zahl         ; ...Arbeit...
                210     eins
                240     zahl
                000     rueck        ; zurück: Sprung auf die Zelle, die selbst ein Sprung ist
```

Ergebnis: `zahl` = 3 nach drei Aufrufen. Das Rückkehrwort ist ein Sprungbefehl `000 <Adresse hinter dem 025>`. Es gibt keinen Rückkehrkeller.
Wegen der **einen** Rückkehrzelle `rueck` ist ein Unterprogramm ohne zusätzliche Sicherung des Rückkehrwortes nicht rekursiv.
Vorlage für Parameter: `Assembler/Claude/sortierung.asm` (Parameter `sn`, `sla` vor dem Aufruf eintragen, `sruck` hat dieselbe Rolle wie `rueck`).
Trick aus derselben Vorlage: `240 sruck` und danach `001 sinit` legt den Rücksprung ab, löscht den AC und springt weiter.

### 5.4 Adreßrechnung (Feldzugriff, Befehl zur Laufzeit bauen)

Weil es keinen Indexregister gibt, baue ich den Befehl im AC und speichere ihn auf eine Zelle, die danach ausgeführt wird:

```
                211     index        ; AC := i  (in Adresseneinheiten, 01000 je Element)
                210     anfang       ; AC := Feldanfang (da feld) + i
                251     0            ; R-Lesebefehl: AC := ⟨Feldanfang + i⟩
```

- Feldanfang mit `da feld` ablegen (Adresse, um 9 Bit verschoben, plus Leitadresse). Konstante Werte mit `dw`.
- Soll statt Lesen ein anderer Befehl ablaufen: `210 sbef` mit `sbef: dw 0240` addiert den Operationscode, dann `240 genbef` speichert den fertigen Befehl `240 <adr>` auf die Zelle `genbef: db 1`, die danach ausgeführt wird (Vorlage: `Assembler/Projekt_1/bsp_5.16/bsp_5_16.asm`).
- Fertige Makros in `Assembler/Sourcecode/c82ass.makros`: `ARRAY_LOAD`, `ARRAY_STORE`, `ARRAY_VGL`, `ARRAY_SWAP`, `MACHE_ADRESSEINHEIT`, `WDHL`.
  Das Makro-Format ist starr (`$PR1 …`, `$IF`, `$1 … $9`). Neue Makros nur nach Muster dieser Datei schreiben, Details in `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md`, „Der Makro-Präprozessor des Assemblers".

### 5.5 Text auf dem Schreibwerk ausgeben

```
haupt:          ANWAHL  K2           ; Kanal 2 = Schreibwerk (Makro, erzeugt 030 04500)
                dtm     Hallo Welt   ; dtm setzt die Umschaltzeichen selbst (erstes Zeichen: Großbuchstabe)
                WRZL                 ; Zeilenschaltung (Makro; wählt danach wieder K0 an)
                020     0
```

Ergebnis in `sw-ausgabe.txt`: `Hallo Welt` + Zeilenende. Regeln (Quelle: `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md`, „Definiere Text zur Ausgabe von Zeichen"):

- Jedes Zeichen ist **ein Ausgabebefehl** `0000 xxxx 030`. Ein Text belegt so viele Zellen wie Zeichen plus Umschaltzeichen.
- `dt` führt den Umschaltzustand (Kleinbuchstaben/Großbuchstaben) nur zur Assemblerzeit. **Vor jede `dt`-Folge `dtm` oder `dz $inkb` / `dz $ingb` setzen.** Nie `dz`-Umschaltzeichen zwischen `dt`-Zeilen mischen.
- `dto` setzt keine Umschaltzeichen. `dz $wrzl | $wr | $tab | $zr | …` für Einzelzeichen.
- Texte mit `;` oder führendem `#` in `\…\` einschließen.
- Ziffern kommen im Zustand „Kleinbuchstabe" (KB), die Zeichen darüber im Zustand „Großbuchstabe" (GB).

### 5.6 Eingabe

Eingabebefehle (`010`, `011`) holen ein Zeichen vom angewählten Kanal. Der Code des Zeichens (die „Eingabeadresse") wird mit dem Adreßteil verodert und führt zur Zelle `Adreßteil ∨ Eingabeadresse`.
Das Zeichen wählt damit eine Tabellenzelle aus (Tabelle `ztab`, 64 Zellen, ein Sprung oder ein fertiger Ausgabebefehl je Zeichen).
Vorlagen: `Assembler/Projekt_1/sw_eingabe/k1_leser_stanzer.asm` **[Beispiel]**, `Bausteininterpretiersystem BIS/markdown-dateien/C8205-Interpreter-BIS.md`, „Eingabeunterprogramme". Eingabecodes: `markdown-dateien/C8205-Interpreter-Kodetabellen.md`.
Die Eingabe für Tests kommt aus einer Datei (`--k0 datei=PFAD`, `--leser1 PFAD`), siehe Abschnitt 7.

## 6. Assembler-Sprache: Stolperfallen

Quelle: `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md`, „Sprachdefinition" und „Assembleranweisungen".

- Zeilenformat: `[symbol:] operationscode [operand] [; kommentar]`. Trenner sind Leerzeichen oder Tabulator. Maximal 255 Zeichen je Zeile.
  Spalte 1 ist für das Symbol da. Befehle beginnen mit Einrückung.
- **Nur dreistellige Oktalcodes.** Keine Mnemonics (`ld`, `add` ergeben „Operationscode ist ungültig").
- Symbole: 1 bis 32 Zeichen, `a-z A-Z 0-9 _`, erstes Zeichen kein Ziffer. Doppelt definierte Symbole sind Fehler.
- Zahlen: führende `0` heißt oktal (`01000`), sonst dezimal. Ausdrücke mit `+ - * /`, ohne Klammern und ohne Leerzeichen. `*` und `/` binden stärker.
- Anweisungen: `start end db dbn dw da dt dto dtm dz equ equ10 equ40 equ100 abs spa`.
- **`dw` kein relatives Ergebnis:** `dw a` ist ein Fehler. Adressen schreibt man mit `da`. Differenzen zweier Marken sind in `dw` erlaubt (`dw ende-anfang`).
- **`da` verlangt eine relative Adresse** (mindestens ein Symbol): `da 5` ist ein Fehler, dafür `dw`.
- Literale: `#wert` legt eine Konstante hinter `end` ab und setzt deren Adresse in den Befehl (`210 #0211`). `@adresse` entsprechend für Adressen.
- Ein Symbol allein auf einer Zeile belegt keinen Platz und erhält die Adresse der nächsten belegenden Zeile.
- Code hinter `end` ist nicht vorgesehen. Nach `end` stehen nur `abs`, `equ` und Makrodefinitionen.
- `db n` reserviert ohne Inhalt, `dbn n` setzt 0. Höchstens 010000.
- Ein falsch geschriebenes Pragma (`LEITADRESS`) wird **nicht gemeldet**, sondern gilt als Kommentar. Kontrolle: Die Statuszeile `Leitadresse: xx` muss erscheinen.
- Die Warnung zu Zellen 0002 bis 0037 beim Lochstreifen-Ausgabeformat (`--ABSPR`): Dort liegt das KEP.

## 7. Tests schreiben und lesen

Quelle: `markdown-dateien/C8205-Interpreter-Durchführung_eines_Tests.md`. Der Assembler schreibt ein Test-Gerüst; ich ergänze es.

```
Trommeldatei:
#DOK-0001
#SPEI-0001 0001-0004           ; Diagnose: diese Zellen am Ende ausgeben (bei 164 0001)
#PROT STUFE=2
#TROMMEL=LEER                  ; ohne diese Zeile erbt der Test den Trommelstand früherer Läufe
--sw-ausgabe <Verzeichnis>     ; Schreibwerk-Ausgabe in <Verzeichnis>/sw-ausgabe.txt
0000: 00000005000 # 000 haupt  ; Adresse: Wert (oktal, 4 und 11 Stellen), Kommentar mit #
...
Tastenfolge:
H G R                          ; H, G, R = Start bei Zelle 0000. Für Start bei n: #STARTE n

Prüfungen:
US=1                           ; höchstens eine Register-/Flag-Zeile
0001: 00000000017              ; beliebig viele Speicherprüfzeilen
--pruefe-sw-ausgabe <Soll-Datei>
```

Regeln für Prüfungen **[geprüft]**:

- **Registerwerte nicht raten.** Nach dem Halt steht BZ auf Stoppadresse + 1, AR kann 0 sein, und der Vergleicher bleibt nach `330` gesetzt. Prüfe daher **`US=1` plus die Ergebniszellen plus ggf. die Schreibwerk-Datei**. BZ/AR/V nur prüfen, wenn sie das Ziel des Tests sind.
- Auch bei `Test falsch` steht in der Ausgabe je Einzelprüfung „soll/ist". Dort liegt der Hinweis auf die Ursache.
- Die Soll-Datei für die Schreibwerk-Prüfung gehört nach `Test-Ergebnisvergleiche/` und heißt `…-ausgabe.txt` oder `…_erwartet.txt`, sonst startet `testscripte/compute_all_tests.sh` sie als Test.
- Trommel ist **persistent** (`Trommel/trommel.txt`, immer 4096 Zeilen `aaaa: ttttttttttt`, a und t oktal). **Leer heißt: alle t = 0.** Der Stand im Zip kann Zellen ungleich 0 enthalten (Rest früherer Läufe). Entweder `#TROMMEL=LEER` setzen oder alle gelesenen Zellen im Test nennen, auch die mit 0. Eine leere Trommeldatei erzeugt `testscripte/erzeuge_leere_trommel.py`.
- `#TROMMEL=` kennt **`LEER`**, **`KEEP`** und **`MP`**. `KEEP` = Trommel unverändert (Stand des Vorläufers) und ist der **Standard**, wenn die Marke fehlt; alle vorhandenen Tests ohne `LEER` tragen es ausdrücklich. Nur `LEER` macht einen Test unabhängig von der Vorgeschichte. `MP` braucht eine Trommelvorlage; `Trommel/Trommelvorlagen/` ist im Zip leer, der Test endet dann mit Rückgabecode 16. Dann das Abbild über `testscripte/c8205_bis_test.sh` laden (lädt `Tests/pj2-bis_minimalprogramm_v6.test` mit `--LOADONLY`).
- Weitere Geräte in der Testdatei: `--leser1 PFAD`, `--leser2 PFAD`, `--stanzer1 PFAD`, `--k0 datei=PFAD`. Je Zeile höchstens einmal, relative Pfade vom Aufrufort.
- Tests, die ein BIS-Unterprogramm prüfen, laden zuerst das Minimalprogramm v6 (`testscripte/c8205_bis_test.sh`, oder `#TROMMEL=MP`, falls die Vorlage vorhanden ist); die Tests des Minimalprogramms selbst (`Tests/pj2-bis_v6_*.test`) tragen ihr Abbild und brauchen das nicht.
- Unterbrechung mitten im Lauf: `#INTERRUPT H <Tasten>`. Debugausgabe stärker: `#PROT STUFE=2` und `#SPUR-nnnn aaaa` (ganze Spur in physischer Reihenfolge).

Fehlersuche in dieser Reihenfolge: (1) Rückgabecode und „soll/ist"-Zeilen, (2) `164 nnnn` an der interessanten Stelle mit `#SPEI`, (3) `Test-Protokolle/<test>/protokoll.txt`, (4) `.dmp` und `.sym` des Assemblers (Adresse ↔ Symbol).

## 8. Ablauf für jede Programmieraufgabe

1. Auftrag lesen. Was steht fest (Zellen, Ansprungadressen), was ist offen? Bei Widerspruch oder unleserlicher Vorlage fragen.
2. Ähnliche Vorlage suchen: `Tests/` (über 150 Tests), `Assembler/Claude_bsp_reassemblierung/` (Quelltexte der Tests), `Assembler/Projekt_*`.
3. `.asm` schreiben, mit Kopfkommentar: Zweck, Parameter, belegte Zellen, Rückkehrzelle. Kommentar in jeder Zeile (die Vorlagen tun das auch).
4. Assemblieren (Abschnitt 2), Rückgabecode 0, Warnungen lesen. `.dmp` ansehen: stimmen die Adressen mit dem Plan überein?
5. Test aus der `.test` ableiten (Abschnitt 7). **Erwartete Werte vorher von Hand herleiten**, nicht aus dem ersten Lauf abschreiben.
6. Interpreter starten, Rückgabecode und „soll/ist" prüfen. Bei Fehlern Abschnitt 7 (Fehlersuche).
7. Regressionstest des Assemblers (`Assembler/Regressionstest/regressionstest.sh`) nur laufen lassen, wenn **Assembler-Quellcode** geändert wurde. Der Ordner fehlt im Gesamt-Zip: vorher im Projektstamm `unzip Regressionstest.zip` (Pfade darin: `Assembler/Regressionstest/...`).
8. Abgabe: als **eine Zip-Datei** mit den Projektpfaden (Regel in `CLAUDE.md`): `.asm`, `.test` (und Soll-Dateien) sowie neue oder geänderte Skripte. Keine Binaries (der Assembler darf zum Testen gebaut werden, wird aber nie geliefert).

## 9. Offene Punkte und Widersprüche in den Quellen (nachfragen, nicht raten)

1. Ob in den Anschlusszellen 204 als einzige freie Zelle Absicht ist (Anhang B).
2. **`.md` gegen `.odt`.** Wo die `.md` vom Assembler abweicht, siehe `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md`, „Abgleich mit dem Assembler c82ass". Im Zweifel gilt `Assembler/Dokumentation/C8205_Assembler_Dokumentation.odt`.
3. Eingabebefehl (`010`, `011`) nur über Beispielkommentare belegt. Vor dem Schreiben von Eingabeprogrammen die Wirkung in `markdown-dateien/C8205-Interpreter-Lochstreifenleser.md` und `markdown-dateien/C8205-Interpreter-Kodetabellen.md` nachlesen und im Test absichern.

## 10. Wo steht was (Suchkarte statt Volltext lesen)

| Frage | Datei, Überschrift |
|---|---|
| Aufbau Rechner, Phasen | `markdown-dateien/C8205-Interpreter-Überblick_und_Gesamtaufbau.md` |
| Maschinenwort, Register, Flags | `markdown-dateien/C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md` |
| Zahlendarstellungen (Dual, ganze Festkommazahl, Gleitkomma, Tetraden) | `markdown-dateien/C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md`, „Übersicht der Zahlendarstellungen"; externe Gleitkommadarstellung und Tetraden des BIS: `Bausteininterpretiersystem BIS/markdown-dateien/C8205-Interpreter-BIS.md`, „Zahlendarstellungen des BIS" |
| Trommel, Sektorfolge, Bahnsperre | `markdown-dateien/C8205-Interpreter-Magnettrommel.md` |
| Befehl X (alle 512 Codes) | `markdown-dateien/C8205-Interpreter-Befehlsliste.md`, „Einzelbefehlsübersicht" |
| Tasten, Schalter | `markdown-dateien/C8205-Interpreter-Bedienpult_mit_Schaltern.md` |
| Zeichencodes (R300) | `markdown-dateien/C8205-Interpreter-Kodetabellen.md` |
| Lochstreifenleser, Stanzer | `markdown-dateien/C8205-Interpreter-Lochstreifenleser.md` |
| Testformat | `markdown-dateien/C8205-Interpreter-Durchführung_eines_Tests.md` |
| Interpreter-Schalter | `markdown-dateien/C8205-Interpreter-Python_Interpreter.md` |
| Zusatztrommeln, Schalter `--C8205Z`, Befehle 601 und 661 (experimenteller Prototyp C8205Z) | `C8205Z/zt/Zusatztrommel_Zeitmodell.md`; Schalterzeile in `markdown-dateien/C8205-Interpreter-Python_Interpreter.md`; GRAFIK: `markdown-dateien/C8205-Interpreter-GRAFIK_Beschreibung.md` §7.10 |
| Assembler-Sprache, Makros, Beispiel (maßgeblich: `.odt` im selben Ordner) | `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md` |
| BIS (Minimalprogramm, Kennzeichen) | `Bausteininterpretiersystem BIS/markdown-dateien/C8205-Interpreter-BIS.md` und `Bausteininterpretiersystem BIS/markdown-dateien/C8205-Interpreter-Objektdatei_Listing.md` |
| Programmbeispiele | `Assembler/Claude/`, `Assembler/Projekt_1/`, `Assembler/Projekt_2/`, `Tests/` |
| Trommelzeit, Zeitmodelle, GRAFIK ohne Fenster | `markdown-dateien/C8205-Programmierhandbuch-Anhang_A_Trommelzeit_GRAFIK.md` |
| BIS: feste Zellen, Anschlusszellen, Kennzeichen | `markdown-dateien/C8205-Programmierhandbuch-Anhang_B_BIS_Anschluss.md` |
| Zip packen, Version, Pflege dieser Texte | `markdown-dateien/C8205-Versionierung.md`, Abschnitt 11 und 12 |

Die großen Dateien (Befehlsliste 65 KB, BIS 90 KB, Testdurchführung 124 KB, GRAFIK-Beschreibung 272 KB) **nicht ganz lesen**. Mit `grep -n` die Überschrift finden und nur den Abschnitt lesen.
Die GRAFIK-Beschreibung brauche ich nur, wenn Fenster, Pult oder Töne das Thema sind.

## 11. Welche Teile des Zips man braucht

Dies ist die einzige ausführliche Beschreibung der Zip-Fassungen; die Karte `CLAUDE.md` verweist nur hierher. Beide Fassungen erzeugt `./c8205_zip_packen.sh` in einem Lauf (`--gesamt` oder `--claude` erzeugen nur eine):

- **Gesamt-Zip** `C8205 Simulator V.M.P.zip`: enthält alles.
- **Claude-Variante** `C8205 Simulator V.M.P Claude.zip`: lässt Entbehrliches weg (rund 40 % weniger Einträge). Mit ihr bestehen alle Tests von `testscripte/compute_all_tests.sh` mit derselben Ausgabe wie mit dem Gesamt-Zip **[geprüft]**.

In beiden Fassungen steht `CLAUDE.md` als erster Eintrag; `unzip -p <zip> CLAUDE.md` liest sie ohne Entpacken.

**Zum Arbeiten genügen:** `Assembler/` (Assembler, `Claude/`, `Projekt_*`, `Dokumentation/`), `Tests/`, `markdown-dateien/`, `testscripte/`, `Trommel/`, `c8205_interp.py`. **Nicht löschen:** `Test-virtuelleGeraete/` (Geräteordner, Ein- und Ausgabedateien von rund 80 Tests) und `Test-Ergebnisvergleiche/` (Soll-Dateien einzelner Tests) **[geprüft]**. Für den GRAFIK-Interpreter zusätzlich `c8205_grafik.py`, `grafik-interpreter-module/` und `c-module/` (darin das gebaute Modul `c8205_trommel`; ohne es endet der Start mit „C-Modul nicht ladbar“).

**In der Claude-Variante fehlen:** alle PDFs samt `pdf-layout-scripte/`, `make_pdf.sh` und `make_all_pdf.sh`, ferner die Testtabelle `Testausfuehrungen/test_tabelle*` (die Skripte in `Testausfuehrungen/` bleiben), `pult/` (Bilder des Pult-Fensters), `ton/` (nur der GRAFIK-Lauf mit Ton; mit `--STUMM` nicht nötig), `README.en.md`, `Test-Protokolle.zip` (Ausgaben früherer Läufe; der Interpreter legt `Test-Protokolle/` beim ersten Lauf selbst neu an) und die vom Assembler erzeugten Dateien `.log .mqo .obj .sym` unter `Assembler/` (`.asm`, `.dmp` und `.test` bleiben maßgeblich). `virtuelle_Geraete/` bleibt dagegen drin: Es wird nur vom GRAFIK-Lauf mit Fenster gebraucht (GRAFIK ohne Fenster läuft ohne **[geprüft]**), liefert aber die Standardpfade für Leser und Stanzer und ist klein. `Regressionstest.zip` liegt in beiden Fassungen; man braucht es nur nach einer Änderung am Assembler-Quellcode (Abschnitt 8, Schritt 7).

**Gesamt-Zip nur wenn nötig:** Den GRAFIK-Interpreter zur Zeitmessung starte ich immer mit `--ohne-fenster --STUMM` (Anhang A); das geht in der Claude-Variante, fehlende Ordner `ton/` und `pult/` sind dann richtig. Das Gesamt-Zip ist nur nötig, wenn GRAFIK-Fenster, Pult oder Ton selbst geändert werden sollen.
