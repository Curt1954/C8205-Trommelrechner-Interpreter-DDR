# Python-Interpreter für den C 8205 (`c8205_interp.py`)

Stand: 28.09.2026. Diese Datei beschreibt den Python-Interpreter, seine Bedienung und alles, was zur Erzeugung
einer menschenzentrierten Bedienungsanleitung (PDF) erforderlich ist. Die Regeln des Rechners selbst stehen
**nicht** hier, sondern in den übrigen Regelwerk-Dateien; hier wird nur auf sie verwiesen (Abschnitt 12).

## Inhaltsverzeichnis

1. Zweck und Einordnung
2. Aufbau des Interpreters
3. Voraussetzungen und Installation
4. Schnellstart
5. Aufruf und Schalter
6. Die Testdatei
7. Die Tastenfolge
8. Geräte und Kanäle (Ein-/Ausgabe)
9. Ausgaben, Protokoll und Endzustand
10. Fehlermeldungen und Abhilfe
11. Abweichungen, Erweiterungen und offene Punkte
12. Bezug zu den Regelwerk-Dateien
13. Beispiele
14. Vorgaben für die PDF-Bedienungsanleitung

---

## 1. Zweck und Einordnung

Der Interpreter führt Programme des Rechners C 8205 **interpretativ** aus: Er läuft den Knotengraphen des
Befehlsablaufs (Phasen I bis IV) ab und bildet Register, Flags, Trommelspeicher und Peripherie nach. Alle
Zeiten (Wortzeit, Wartezeit auf die Trommel) sind 0; die Trommeldrehung wird nicht nachgebildet.

Er dient dazu,
- Testprogramme des C 8205 nachvollziehbar durchzurechnen (Protokoll Knoten für Knoten),
- das Verhalten des Regelwerks zu prüfen,
- Ein-/Ausgabe (Schreibwerk, Lochbandleser, Stanzer, Pult-Tastatur) an einem Terminal zu erproben.


Grundsatz (aus der Datei `C8205-Interpreter-Durchführung_eines_Tests.md`): Der Graph wird wortlautgetreu
abgelaufen. Unklares wird als **Stub** gemeldet (Abbruch mit Meldung) und nie stillschweigend „repariert“.

## 2. Aufbau des Interpreters

Der Interpreter wird **nicht** aus den Regelwerk-Dateien erzeugt, sondern liest sie zur Laufzeit:

| Baustein | Herkunft | Inhalt |
|---|---|---|
| Knotengraph | `C8205-Interpreter-Eingänge_der_Knoten.md` (Schalter `--graph`) | Knoten, Typen, Ein-/Ausgänge, Verzweigungen |
| Variablentabelle T2 | `C8205-Interpreter-Beschreibung_der_Knoten.md` (Schalter `--t2`) | Bedeutung der ANWEISUNG-nnn |
| Funktionen je ANWEISUNG | handgeschrieben in `c8205_interp.py` (`a001`, `a021`, `t002` …) | Wirkung auf Register, Flags, Speicher |
| Kodetabelle (Tabelle 1) | **in das Skript eingebettet** (`TABELLE1`), erzeugt aus `C8205-Interpreter-Kodetabellen.md`, Abschnitt 1.4 | Zeichen, Lochbilder, Ein-/Ausgabe-Adressen |
| Geräte | handgeschrieben (`Leser`, `Stanzer`, `K0Quelle`, `sw_schreibe`) | Peripherie |

Die Funktionen tragen die Nummer der ANWEISUNG (`a` = Anweisung, `t` = Test). Ändert sich der Graph oder T2, muss
nur das Skript angepasst werden, wenn eine ANWEISUNG neu ist oder anders wirkt. Fehlt zu einer ANWEISUNG eine
Funktion, meldet der Interpreter einen Stub.

Ablauf eines Tests: Testdatei einlesen → **formale Prüfung** → Tastenfolge auswerten (Ausgangszustand) →
Knotengraph ab Konnektor B ablaufen → Ergebnis ausgeben.

## 3. Voraussetzungen und Installation

- **Python 3** (nur Standardbibliothek, nichts zu installieren). `--k0 tastatur` funktioniert plattformübergreifend:
  unter Linux/macOS über das Modul `termios`, unter Windows über das Modul `msvcrt` (beide Standardbibliothek,
  die Auswahl erfolgt automatisch anhand des laufenden Betriebssystems).
- **Dateien im selben Ordner** wie `c8205_interp.py`: `C8205-Interpreter-Eingänge_der_Knoten.md` und
  `C8205-Interpreter-Beschreibung_der_Knoten.md` (Vorgaben für `--graph` und `--t2`).
- Optional der Wrapper `c8205_interpreter.sh` (Abschnitt 5.2), der ebenfalls im Ordner des Skripts liegen muss,
  weil er `python3 c8205_interp.py` relativ aufruft.
- Ein Terminal mit ANSI-Farben (für Gelb und Rot; ohne Terminal oder mit gesetztem `NO_COLOR` erscheint reiner Text).

Der Dateiname der Eingänge-Datei enthält ein „ä“. Findet der Interpreter sie nicht, kann der Pfad mit `--graph`
angegeben werden.

## 4. Schnellstart

```
python3 c8205_interp.py Tests/0015-030.txt
```

Das führt den Test aus, gibt die Zeichen der Ausgabebefehle auf dem Terminal aus (dunkelgelb) und zeigt die
Endzeile (`Ende: …`). Mit Wrapper und Protokolldatei:

```
./c8205_interpreter.sh 0015-030.txt        # schreibt Protokolle/0015-030.log
```

Erwartet wird für den Test `0015-030` die Ausgabe `Jahr 1972` (Abschnitt 13.1).

## 5. Aufruf und Schalter

### 5.1 Kommandozeile

```
python3 c8205_interp.py [--graph DATEI] [--t2 DATEI] [--out VERZ|DATEI.log]
        [--leser1 PFAD] [--leser2 PFAD] [--stanzer1 PFAD]
        [--k0 tastatur|datei=PFAD] [--knotentest]  TEST.txt [TEST2.txt ...]
```

| Schalter | Wirkung | Vorgabe |
|---|---|---|
| `TEST.txt` | Testdatei(en) (Abschnitt 6). Ist der Pfad nicht vorhanden, wird der Dateiname unterhalb des aktuellen Ordners und des Skript-Ordners gesucht (Groß-/Kleinschreibung egal). Bei mehreren Treffern werden sie aufgelistet und der Test startet nicht. | – |
| `--graph DATEI` | Knotengraph | `C8205-Interpreter-Eingänge_der_Knoten.md` im Skript-Ordner |
| `--t2 DATEI` | Variablentabelle T2 | `C8205-Interpreter-Beschreibung_der_Knoten.md` im Skript-Ordner |
| `--out …` | Mit Dateiendung (z. B. `Protokolle/t1.log`): Protokoll genau in diese Datei (Ordner werden angelegt; nur mit **einem** Test). Ohne Endung: Ordner, Protokoll dann in `ORDNER/<Testname>/protokoll.txt`. | `ergebnis/` im Skript-Ordner |
| `--leser1 PFAD`, `--leser2 PFAD` | Lochstreifen für Leser 1 (Kanal K1) bzw. 2 (K2): Datei oder Ordner | nicht angegeben |
| `--stanzer1 PFAD` | Ausgabedatei des Stanzers 1 (Kanal K1) | nicht angegeben |
| `--k0 QUELLE` | Eingabequelle für Kanal K0: `tastatur` oder `datei=PFAD` | nicht angegeben |
| `--knotentest` | Nimmt die Zeilen der durchlaufenen Knoten (`Kxxx KON/PHA/ANW/TST …`) ins Knotenprotokoll auf (Bildschirm bei STUFE=1, Protokolldatei bei STUFE=2). Ohne den Schalter entfallen diese Zeilen; erhalten bleiben die `BR=`-Zeilen (vor Knoten 2 und 7), die Diagnose sowie Fehler- und Stub-Meldungen. Der Schalter ändert weder den Ablauf noch die `Knoten:`-Zahl der Endzeile. | aus (false) |

Die langen Bezeichnungen `--lochbandleser1`, `--lochbandleser2` und `--lochbandstanzer1` sind gleichwertig.
Ein **nicht angegebenes** Gerät ist kein Fehler, solange das Programm es nicht benutzt. Benutzt es das Programm
doch, erscheint eine **rote Fehlermeldung** und der Test endet (Abschnitt 10).

### 5.2 Wrapper `c8205_interpreter.sh`

```sh
file="$1"
if [ -z "$file" ]; then
   echo "Test-Datei fehlt."
   exit 1
fi
# Dateiname ohne Pfad, Endung durch .log ersetzen
prot_file="$(basename "$file")"
prot_file="${prot_file%.*}.log"
python3 c8205_interp.py --out "Protokolle/$prot_file" "$file"
```

Der Wrapper reicht nur die Testdatei durch. Sollen Geräte angegeben werden, ruft man `python3 c8205_interp.py`
direkt auf oder ergänzt den Wrapper so, dass er weitere Argumente weitergibt (`shift` und `"$@"` am Ende).

## 6. Die Testdatei

Eine Testdatei besteht aus zwei Teilen, eingeleitet durch die Zeilen `Trommeldatei:` und `Tastenfolge:`.

**Trommeldatei** (Anfangsinhalt der Trommel, nur ein Ausschnitt; nicht genannte Zellen sind 0):

```
Adresse: Wert [# Bemerkung]        Adresse = 4 Oktalstellen, Wert = 11 Oktalstellen
```

Ein Wert besteht aus 4 Oktalstellen „beliebig“ und 7 Stellen Befehl (4 Adresse + 3 Operation), z. B.
`00004500030` = Adresse `4500`, Operation `030`. Leerzeilen und Zeilen mit `#` werden übergangen.

**Testmarken** (nur für die Testdurchführung, ohne Entsprechung in der Hardware):

| Marke | Wirkung |
|---|---|
| `#DOK-xxxx Text` | Kommentar zum Test (`xxxx` oktal). Beim Befehl 164 („Leerbefehl“) mit der Adresse `xxxx` wird der Text als Diagnose auf dem Bildschirm ausgegeben, unabhängig von der Protokollstufe. Es folgt keine automatische Zustandszeile. Mehrfach zulässig. |
| `#SPEI-xxxx ssss-eeee` | Speicherbereich, der beim Befehl 164 mit der Adresse `xxxx` ausgegeben wird. Unabhängig von `#DOK`, auch einzeln und mehrfach zulässig; `ssss ≤ eeee`. |
| `#SPUR-xxxx aaaa` | Ganze Spur (Bahn) mit der Adresse `aaaa`, ausgegeben beim Befehl 164 mit der Adresse `xxxx` (Abschnitt 13.6). Unabhängig von `#DOK`, auch einzeln und mehrfach zulässig. |
| `#PROT STUFE=n` | Protokollstufe des Tests (höchstens einmal): 0 = kein Knotenprotokoll, 1 = Knotenzeilen auf dem Bildschirm, 2 = Knotenzeilen nur in der Protokolldatei. Fehlt die Marke, gilt 1. |

**Formale Prüfung.** Vor dem Start wird geprüft: Zeilenformat, keine Adresse mit widersprüchlichem Wert,
`#SPEI` mit gültiger Spanne (`#SPEI`/`#SPUR` brauchen kein `#DOK`), gültige `#PROT`-Stufe, vorhandene Tastenfolge. Bei einer Unstimmigkeit startet
der Test **nicht** und wird nicht eigenmächtig korrigiert.

## 7. Die Tastenfolge

Die Tastenfolge (Zeile(n) hinter `Tastenfolge:`, Tokens durch Leerzeichen getrennt) legt den Ausgangszustand
vor Konnektor B fest. Sie **endet mit `R`** (dann ist `H` am Ende gelöst) **oder im Halt** (`H` bleibt gesetzt, z. B. `H G Ü E`); beides
ist definiert. Endet sie weder mit `R` noch im Halt, gilt sie als nicht definiert und der Test startet nicht.

Definition der Token: Dokument `C8205-Interpreter-Bedienpult_mit_Schaltern.md`, Abschnitt „Tastenfolge-Token“. Die Tabelle gibt
die Umsetzung im Interpreter wieder.

| Token (Groß-/Kleinschreibung egal) | Wirkung |
|---|---|
| `H` | Schalter H-R auf „H“: Flag H := 1 |
| `G` | Generallöschen: alle Flags außer H, T, BS, SP := 0, danach US := 1; AR, OR, BZ := 0; Kanal K0 angewählt (T := 1, bei gedrücktem SW: SW := 1) |
| `M+`, `M-drücken`, `M-gedrückt-halten` (Schreibweisen mit `drueck…` oder `halt…`) | M gedrückt halten: OR := OR ODER 025 |
| `M-`, `M-loslassen` | M loslassen: der Beitrag 025 im OR entfällt (übrige Anteile, z. B. von Ü, bleiben) |
| `M` | Antippen = `M+` und sofort `M-` (Fall 4): OR := OR ODER 025, BR bleibt aufgestellt, `R` startet bei Knoten 19 |
| `E` (mit gehaltenem M) | BZ := BZ + 1, AR := BZ, AC := (BZ+1) im Adressfeld (Beispiel B nach 4×E: `00000005000`); Befehlsentnahme gesperrt, Automat steht danach vor Phase II |
| `E` (ohne M) | nur bei H: Einzelschritt über den Knotengraphen ab Knoten 19 (Phase IV, I, II, III), Halt vor erneutem Eintritt in Knoten 19 |
| `BS=1`, `SP=1` (auch `BS+`, `SP+`) | Schalter gedrückt/eingerastet: Flag BS bzw. SP := 1 |
| `BS=0`, `SP=0` (auch `BS-`, `SP-`) | Schalter gelöst: Flag := 0. `G` löst die Schalter nicht (mechanisch eingerastet) |
| `ST` | nicht an H gebunden, nur bei US oder BS wirksam (sonst keine Wirkung): OR := OR ODER 240, AR unverändert, US := 0; BR aufgestellt, `R` startet bei Knoten 19 |
| `Ü` (`UE`) | nur bei H: AR := 7777, OR := OR ODER 240 (BR aufgestellt); ohne H keine Wirkung |
| `SW=1`, `SW+`, `SW-drücken` | Schalter SW gedrückt: Flag SW := 1, T := 0 |
| `SW=0`, `SW-`, `SW-loslassen` | Schalter SW gelöst: Flag SW := 0, T := 1 |
| `R` | Schalter H-R auf „R“: Flag H := 0, US := 0; Interpretation beginnt bei Konnektor B (bei aufgestelltem BR bei Knoten 19) |

`SW` muss **vor** `G` gesetzt werden, weil `G` daraus T oder SW für K0 ableitet.
Typisches Muster „Sprung nach Speicherplatz n“: `H G M-drücken E … E M-loslassen R` (n mal `E`).

Nach `Ü`, `ST` oder `E` (ohne M) ist BR aufgestellt: folgt `R`, beginnt der Ablauf bei Knoten 19 statt bei Konnektor B.
Ungültig (der Test startet nicht): `M-` ohne `M+`, `M+` bei gedrücktem M, `R` oder Ende bei gedrücktem M.

**Nicht implementiert** (Meldung „nicht definiert“, der Test startet nicht): Kanaltasten `K0`–`K3`. Die Eingabetasten
(0…9, `+` usw.) gehören nicht in die Tastenfolge, sie werden als K0-Eingabe bedient (Abschnitt 8.4).

## 8. Geräte und Kanäle (Ein-/Ausgabe)

Ein Kanal wird durch einen **Anwahlbefehl** ausgewählt, der im Testprogramm steht:

| Anwahlbefehl | Kanal | Eingabe | Ausgabe |
|---|---|---|---|
| `4700 030` | K0 | Pult-Tastatur (T) oder Schreibwerk (SW) | keine |
| `4600 030` | K1 | Lochbandleser 1 | Lochbandstanzer 1 |
| `4500 030` | K2 | Lochbandleser 2 | Schreibwerk (Terminal) |
| `4400 030` | K3 | frei | frei |

Ein Ausgabe-Halt-Befehl (`a 030`) mit `a1 ≤ 3` gibt das Zeichen aus, dessen Ausgabe-Adresse (erste drei
Oktalstellen von `a`, Tabelle 1) zur Adresse passt. Während der Ausgabe ist Flag A = 1.

### 8.1 Schreibwerk-Ausgabe (K2) auf dem Terminal

- Jedes Zeichen erscheint **sofort** auf dem Terminal, in **Dunkelgelb** (ANSI 33).
- Die Zeichenlage KB/GB des Schreibwerks wird beim Start **zufällig** gesetzt. `Um. KB` (Ausgabe-Adresse `117x`)
  und `Um. GB` (`057x`) stellen sie um; sie wirken, geben aber selbst **nichts** aus.
  Ohne Umschaltzeichen im Programm ist die Groß-/Kleinschreibung also zufällig.
- Zeichen ohne sichtbare Darstellung erscheinen als `<Name>` (z. B. `<Irrung Zeichen>`); `SatzMarke` (`272x`) ist ein Zeilenumbruch.
- Ist eine Ausgabe-Adresse nicht in Tabelle 1, erscheint nichts (Hinweis im Protokoll).
- Bei `STUFE=1` erscheinen die Knotenzeilen (mit `--knotentest`) erst nach dem Lauf; die Schreibwerk-Ausgabe steht davor.
- Die Stellung des Schalters SW hat auf die Ausgabe keinen Einfluss.

### 8.2 Lochbandleser (K1, K2)

`--leser1` / `--leser2` nehmen eine **Datei** (ein Streifen) oder einen **Ordner** (Streifen in Namensreihenfolge).
Pro Eingabebefehl wird **eine Zeile** gelesen: acht Zeichen `0`/`1` für die Spuren `w v u p 8 4 2 1`
(Transportspur nicht dargestellt). Leerzeilen sind Vorspann und werden übergangen.

- **Ungerade** Zahl gelochter Spuren = gültig; **gerade** (auch „Irrung Zeichen“) = Fehler bei Eingabe: FE := 1, der Lauf hält.
- Die Eingabeadresse ist `(Lochbild & 0x0F) | ((Lochbild >> 1) & 0x30)` und muss in Tabelle 1 vorkommen.
- Sie wird mit dem Adressregister ODER-verknüpft. Danach wird der Befehl umgestellt: bei **Sprung-Umstellung „ja“**
  (z. B. `:`, `.`, `,`, Tabulator, `Um. KB`, `Um. GB`) zu einem unbedingten Sprung an die Adresse `a ODER Eingabeadresse`,
  bei „nein“ (z. B. Ziffern, Buchstaben) zu einem Lesebefehl, der die Eingabeadresse zum AC addiert.
- Ist der Streifen zu Ende, hält der Lauf mit Flag E = 1 (der reale Leser würde unendlich warten).

### 8.3 Lochbandstanzer (K1)

`--stanzer1 PFAD` ist die Ausgabedatei (bei einem Ordner: `stanzer-ausgabe.txt` darin). Je gestanztem Zeichen
entsteht eine Zeile mit acht Zeichen `0`/`1` für `w v u p 8 4 2 1`. Die Datei wird beim ersten gestanzten
Zeichen eines Laufs **neu angelegt** (nicht angehängt) und nur angelegt, wenn wirklich gestanzt wird.

### 8.4 Pult-Tastatur und Schreibwerk-Eingabe (K0)

`--k0 tastatur` liest einen Tastendruck je Eingabebefehl vom Terminal (ohne Echo, ohne Enter, Strg+C wirkt).
`--k0 datei=PFAD` liest eine Textdatei mit einem Zeichen oder Namen je Zeile (`ZR`, `WM`, `IS`, `IB`, `TAB`,
`WRZL` oder Namen aus Tabelle 1; Zeilen mit `#` sind Kommentar; Dateiende = Halt mit `EINGABE_ENDE`).

*(Plattformhinweis: Unter Linux/macOS wird `termios`/`tty` verwendet, unter Windows `msvcrt.getch()` – beide
liefern das Zeichen sofort und ohne Bildschirm-Echo. Unter Windows ist `msvcrt.getch()` bekannt dafür, dass es
Strg+C in Ausnahmefällen als normales Zeichen statt als Abbruchsignal liefern kann; im Zweifel hilft Strg+Pause
oder das Schließen des Konsolenfensters.)*

Was eingegeben werden darf, hängt vom Schalter SW ab:

| Zustand | Eingebbar |
|---|---|
| SW nicht gedrückt (Flag T, Pult-Tastatur) | **nur** `0`–`9`, `+`, `-`, `,`, `.`, `:`, `ZR`, `WM`, `IS`, `IB` (19 Codes). `B` und `D` haben keinen Code und sind nicht eingebbar. |
| SW gedrückt (Flag SW, Schreibwerk) | **alle** Zeichen der Tabelle 1 |

Ein nicht erlaubtes Zeichen wird bei `datei=` mit roter Meldung abgelehnt (Test endet); bei `tastatur` wird der
Tastendruck ignoriert und auf die nächste gültige Taste gewartet.
Zeichen werden über die Spalten „Ascii KB“/„Ascii GB“ gefunden; die Eingabe-Zeichenlage (Start KB, geändert durch
gelesenes `Um. KB`/`Um. GB`) bestimmt, welche Spalte zuerst durchsucht wird. Auf die Eingabeadresse hat sie keinen Einfluss.

## 9. Ausgaben, Protokoll und Endzustand

**Bildschirm** (je Test): Kopfzeile `=== Test <Name> (#PROT STUFE=n) ===`, gefolgt von Schreibwerk-Zeichen,
Diagnose (`-- Diagnose --`, `#DOK-…`, `#SPEI-…`, `#SPUR-…` bei Befehl 164), bei STUFE=1 (und `--knotentest`) den Knotenzeilen bzw. `BR=`-Zeilen und am Ende der
**Endzeile**:

```
Ende: <Grund> | Knoten: n | BZ=… AC=… AR=… | FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
```

Die Registerwerte sind oktal (BZ, AR vierstellig, AC elfstellig). Flags: FE Fehler bei Eingabe, FUE Überlauf,
BS bedingter Stopp, US unbedingter Stopp, E/A Ein-/Ausgabebefehl aufgestellt, V1/V2 Vergleicher.

**Endgründe** (Auswahl):

| Endgrund | Bedeutung |
|---|---|
| Unbedingter Stop (US:=1) | Programm hat ordnungsgemäß gehalten |
| Überlauf (FÜ) / bedingter Stopp | Halt durch Überlauf bzw. gesetzten Schalter BS |
| Fehler bei Eingabe (FE) | gerade Zahl von Lochungen |
| Lochbandleser n: kein Lochstreifen mehr | Leser leer, Flag E bleibt 1 |
| EINGABE_ENDE | K0-Datei zu Ende |
| Gerät nicht nutzbar | Gerät nicht angegeben oder Datei/Zeichen ungültig (rote Meldung) |
| STUB bei Knoten n | Regelwerk unvollständig (Kanal K3 ist dagegen der definierte Fall „nicht benutzt“, s. Abschnitt 11) |
| Tastenfolge nicht gültig/definiert | Test startete nicht |

**Diagnose (Befehl 164).** Der Leerbefehl wird zuerst abgearbeitet; erst danach erscheint die Diagnose. Die Leer-Befehle 164 und 166
sind laut Befehlsliste (Nr. 66) „Leer-Operation ohne Löschen“, also **ohne Resultatbehandlung**: das Z-Feld erzeugt
hier **keine Verschiebung** (Korrektur 29.09.2026). Die Adresse des Befehls (`a`) wählt die zugehörigen `#DOK`-Texte (alle, in Dateireihenfolge), die `#SPEI`-Bereiche und die
`#SPUR`-Spuren; jede Speicherzelle steht als Zeile `aaaa: wwwwwwwwwww` unter der jeweiligen Markenzeile. Die Marken sind
voneinander unabhängig: passt nur ein `#SPEI` oder nur ein `#SPUR` zur Adresse, wird nur dieses ausgegeben. Eine
automatische Zustandszeile (`BZ=… AC=… FE=…`) nach `#DOK` gibt es nicht (Änderung 29.09.2026); passt keine Marke, entfällt die Diagnose ganz.
Vor der Ausgabe je `#SPEI`- bzw. `#SPUR`-Marke steht die auslösende Testmarke selbst als Zeile (z. B. `#SPEI-0023 4000-4005`,
`#SPUR-0023 4000`), damit im Protokoll erkennbar ist, wozu die folgenden Speicherzeilen gehören.

**Protokolldatei** (nur bei `#PROT STUFE=2`): Abschnitte `== 1. Ausgangsbedingungen ==` (übernommene Trommel,
Tastenfolge mit Wirkung je Taste), `== 2. Zustände des Knotenautomaten ==` und `== Ende ==`.
Knotenzeilen erscheinen nur bei Aufruf mit `--knotentest`. Eine Knotenzeile hat die Form
`K009 ANW 005 BZ=0001 AR=0001 AC=00000000000`; Tests tragen zusätzlich `-> wahr` oder `-> falsch`.
Die Zeile `BR=aaaa ooo` mit dem Befehlsregister (Adressteil und Operationsteil des zuletzt geladenen Befehls) steht
**vor Knoten 2** (Beginn Phase I) und **vor Knoten 7** (Sprung über Konnektor 1 aus Knoten 63; Knoten 7 selbst wird als
Konnektor übersprungen, die Zeile steht unmittelbar nach der Zeile von Knoten 63). Sie steht auch ohne `--knotentest`
im Protokoll. Beispiel: `  BR=3000 211  (vor Knoten 002)  BZ=0001 AC=00000000000 FÜ=0 V1=0 V2=0 V3=0`. Am Zeilenende stehen der
Befehlszähler `<BZ>` (vierstellig oktal), der Akkumulator `<AC>` (elfstellig oktal), das Überlauf-Flag FÜ und die Vergleicher V1, V2 sowie der Pseudovergleicher V3
(V3=1 genau dann, wenn V1=1 und V2=1) zum jeweiligen Zeitpunkt. Die frühere Zeile „nach Knoten 009“ entfällt. Bei STUFE=0 oder 1
entsteht keine Protokolldatei; bei angegebenem `--out` erscheint dann ein Hinweis.

## 10. Fehlermeldungen und Abhilfe

Fehler zu Geräten erscheinen **in Rot** auf dem Terminal (Standardfehlerausgabe, nur mit Terminal gefärbt):

| Meldung | Ursache | Abhilfe |
|---|---|---|
| `Eingabe von Lochbandleser n (Kanal Kn) angefordert, aber --lesern nicht angegeben.` | Programm liest von K1/K2, Schalter fehlt | `--leser1`/`--leser2` angeben |
| `Ausgabe auf Lochbandstanzer 1 (Kanal K1) angefordert, aber --stanzer1 nicht angegeben.` | Programm stanzt, Schalter fehlt | `--stanzer1` angeben |
| `Eingabe über K0 (…) angefordert, aber --k0 nicht angegeben …` | Programm liest von K0 | `--k0 tastatur` oder `--k0 datei=PFAD` |
| `Lochbandleser n: Lochstreifen-Pfad nicht gefunden: …` | Pfad falsch | Pfad prüfen |
| `Lochstreifen …: ungültige Zeile …` | Zeile ist nicht acht Zeichen aus `0`/`1` | Streifendatei korrigieren |
| `K0-Eingabe: '…' ist an der Pult-Tastatur (T) nicht eingebbar …` | Zeichen an T nicht erlaubt | `SW=1` vor `G` in die Tastenfolge oder anderes Zeichen |
| `K0-Datei nicht lesbar: …` | Datei fehlt | Pfad prüfen |
| `Testdatei nicht gefunden: …` | Name weder als Pfad noch unterhalb der Suchordner vorhanden | Pfad prüfen, Schreibweise, aktuellen Ordner beachten (wird mit angezeigt) |
| `Testdatei … nicht eindeutig gefunden` | mehrere Dateien gleichen Namens | vollständigen Pfad angeben |
| `--out mit Dateiendung … ist nur mit genau einer Testdatei zulässig` | `--out x.log` mit mehreren Tests | Ordner ohne Endung verwenden oder Tests einzeln starten |
| `Tastenfolge nicht gültig/definiert` | Token unbekannt, weder `R` noch Halt am Ende, M nicht losgelassen, nicht implementierte Taste | Abschnitt 7 |
| `STUB bei Knoten n: …` | vom Programm benutzte Funktion noch nicht umgesetzt | Abschnitt 11 |

## 11. Abweichungen, Erweiterungen und offene Punkte

**Erweiterungen gegenüber dem Regelwerk** (nur für den Interpreter, ohne Entsprechung in der Hardware):
- Testmarken `#DOK`, `#SPEI`, `#PROT STUFE`.
- Schreibwerk-Ausgabe (K2) direkt am Terminal in Dunkelgelb; das Regelwerk sieht dafür die Datei `sw-ausgabe.txt` vor.
- Schalter `--leser1/2`, `--stanzer1`, `--k0`; das Regelwerk (Durchführung eines Tests, 6.2) beschreibt für Leser
  Verzeichnisse, der Interpreter nimmt auch eine einzelne Datei.
- `--out` mit Dateiendung als direkte Protokolldatei; Suche der Testdatei über den Namen.
- Token `SW=1`/`SW=0` in der Tastenfolge.
- Schalter `--knotentest` (Ergänzung 29.09.2026): Knotenzeilen im Protokoll nur auf Wunsch; Vorgabe aus. Der Wrapper
  `c8205_interpreter.sh` ruft ohne diesen Schalter auf; für Knotenzeilen in der `.log`-Datei muss er dort ergänzt werden.

**Auslegung, wo das Regelwerk offen lässt:**
- `B` und `D` (Pult-Tasten) haben keinen Code und sind an T nicht eingebbar.
- `WM` = Tabulator (Eingabe-Adresse 075), `IB` = Eingabe-Adresse 036 (Kodetabellen 3.3).
- Tabellenzeile 52 („Transport“, Relikt) wird nicht benutzt.

**Auslegung A=3/Z=2 (Ergänzung 29.09.2026):** Die Codes `232`, `332`, `432`, `532`, `632`, `732` („bedingte Addition ohne Löschen, mit Rechtsverschiebung“) werden nach Befehlsliste 4.3 (A=3, Z=2,3: „wenn z₃₂=0: AC := Vr AC“) ausgeführt: keine Addition von `<a>`, die Operation selbst ist leer, die Rechtsverschiebung leistet die Resultatbehandlung. Bei `332` wird der Vergleicher wie bei allen markierten Befehlen gesetzt und korrigiert. Zuvor endeten diese Codes mit einem Stub. Damit gibt es für die 512 Operationscodes keinen Stub mehr; K3 wird in dieser Ausbaustufe nicht benutzt (s. unten), Ein-/Ausgabebefehle brauchen die passenden Geräteschalter.

**Auslegung des Interpreters (bewusst wortlautgetreu nach dem Knotengraphen, nicht nach vereinfachenden Beschreibungen):**
- ANWEISUNG-001 wird in Knoten 3 (Phase I) **und** Knoten 16 (Phase III) jeweils vollständig angewendet
  (`<AR>:=<BZ>` und gleichzeitig `<BZ>:=<AR>+1` mit dem Altwert). Der dabei in Phase I entstehende BZ-Zwischenwert wird
  in Knoten 11 überschrieben, bevor ihn ein Knoten liest; die Phasentabelle der Überblicksdatei ist nur eine Vergröberung.
- Die Resultatbehandlung (ANWEISUNG-022, Z-Feld) wird bei jedem Befehl angewendet, **außer** bei den Leer-Befehlen (B=1, A=6, Z≥4; z. B. 164, 166): diese laufen ohne Resultatbehandlung, auch ohne Verschiebung (Korrektur 29.09.2026).
- Bei den verkürzten Gruppen-/Wiederholungsbefehlen (B=5, 7) ist das Vorzeichenbit R-abhängig: bei R≠1 gilt z₀,
  bei R=1 gilt z₃₂ (ANWEISUNG-042). Der Test wird **nach** ANWEISUNG-022 der jeweiligen Zelle ausgewertet (Beispiele 13.4).
- ANWEISUNG-010 setzt nach T2 „interne Umstellung auf A=0“ (sonst würde ein genommener Sprung wie ein Stopp enden).

**Offene Punkte:**
**Geklärt (28.09.2026):** Test `0021-544` (Autor) hat gezeigt, dass die Zelle, bei der AC negativ wird, noch vollständig
verarbeitet (insbesondere gespeichert) werden muss (Befehlsliste 4.1.6). Der Knotengraph wurde entsprechend um die Knoten
73–78 erweitert (ANWEISUNG-024 nur noch normale Abbruchbedingung, ANWEISUNG-042 an Knoten 73, neue ANWEISUNG-044 setzt den
Merker); s. Beispiel 13.4.
- **Kanal K3** (Anwahl `4400 030`, kein Gerät) wird vom C 8205 in dieser Ausbaustufe **nie benutzt** (Festlegung des Autors, 29.09.2026). Ein Programm, das auf K3 ein- oder ausgibt, liegt außerhalb des definierten Betriebs. Der Interpreter meldet dies mit einem Stub, das ist kein Fehler des Interpreters und kein offener Punkt.
- Schreibwerk-Ausgabe in die Datei `sw-ausgabe.txt` und Stanzer-Ausgabe im Format des Regelwerks (6.3.2) fehlen bzw. weichen ab.
- Kanaltasten `K0`–`K3` in Tastenfolgen.
- Option `--leser-ende halt|warten` und `--k0`-Vorgabe „beides, umschaltbar“ sind nicht umgesetzt.
- Der Interpreter liefert dem Betriebssystem keinen Testergebnis-Code: Der Rückgabewert ist 0, auch wenn ein Test mit Fehler endet
  (nur ungültige Schalter ergeben 2). Das Ergebnis steht in der Endzeile.

## 12. Bezug zu den Regelwerk-Dateien

| Thema | Datei |
|---|---|
| Überblick, Phasen, Leistungsdaten | `C8205-Interpreter-Überblick_und_Gesamtaufbau.md` |
| Flags, Register, Maschinenwort | `C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md` |
| Trommel, Sektoren, Bahnsperre | `C8205-Interpreter-Magnettrommel.md` |
| Tasten, Schalter, Kanäle, Funktionsabläufe | `C8205-Interpreter-Bedienpult_mit_Schaltern.md` |
| Leser, Stanzer, Schreibwerk (Hardware) | `C8205-Interpreter-Lochstreifenleser.md` |
| Zeichenkodes, Tabelle 1 | `C8205-Interpreter-Kodetabellen.md` |
| Befehle und Formeln | `C8205-Interpreter-Befehlsliste-Zwischenstand.md` |
| Knotengraph / Variablentabelle T2 | `C8205-Interpreter-Eingänge_der_Knoten.md`, `C8205-Interpreter-Beschreibung_der_Knoten.md` |
| Testdurchführung, Testdatei, Protokoll | `C8205-Interpreter-Durchführung_eines_Tests.md` |
| Cache der BAZ-Wirkungen (wird vom Python-Interpreter nicht gelesen) | `baz-wirkungstabelle.md` |

## 13. Beispiele

### 13.1 Ausgabe auf dem Schreibwerk (Test `0015-030`)

```
Trommeldatei:
#DOK-0015 Test Ausgabebefehl
#PROT STUFE=2
0001: 00007240000
7240: 00004500030
7241: 00002720030
7242: 00000570030
7243: 00001210030
7244: 00001170030
7245: 00000610030
7246: 00000700030
7247: 00001110030
7250: 00000320030
7251: 00000010030
7252: 00000310030
7253: 00000070030
7254: 00000020030
7255: 00000015164
7256: 00000000020

Tastenfolge:
H G M-drücken E M-loslassen R
```

Ablauf: Die Tastenfolge springt (Muster „Sprung nach n“, n = 1) auf Adresse 0001, dort steht ein Sprung nach 7240.
Das Programm wählt K2 an (`4500 030`), gibt `SatzMarke` (Zeilenumbruch), `Um. GB`, `J`, `Um. KB`, `a`, `h`, `r`,
Leerzeichen, `1`, `9`, `7`, `2` aus und ruft den Leerbefehl 164 (Diagnose) auf.

```
$ ./c8205_interpreter.sh 0015-030.txt
=== Test 0015-030 (#PROT STUFE=2) ===

Jahr 1972
-- Diagnose --
#DOK-0015 Test Ausgabebefehl
Ende: Unbedingter Stop (US:=1) | Knoten: 295 | BZ=7257 AC=00000000000 AR=0000 | FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
Protokolldatei: Protokolle/0015-030.log
```

Die Zeile `Jahr 1972` erscheint in Dunkelgelb. Die Leerzeile davor ist der Zeilenumbruch des Programms.
Der `Knoten:`-Wert kann je nach Fassung des Graphen abweichen und ist kein fester Sollwert.

### 13.2 Ziffer vom Lochstreifen lesen

Programm: `0000: 00004600030` (K1 anwählen), `0001: 00000000011` (Eingabe-Halt mit Löschen), `0002: 00000000020` (Stopp).
Streifendatei `band5.txt` mit den Zeilen `` (leer) und `00010101` (die Ziffer 5: Spuren p, 4, 1).
Aufruf: `python3 c8205_interp.py --leser1 band5.txt test.txt`. Ergebnis: Stopp bei BZ=0003 mit AC=…05.

Mit dem Zeichen `:` (Zeile `00001101`) und Eingabe-Halt `0001: 00000000010` springt das Programm nach 0015.

### 13.3 Zeichen stanzen

Programm: `0000: 00004600030` (K1 anwählen), `0001: 00000250030` (Ausgabe der Ziffer 5, Ausgabe-Adresse `025x`),
`0002: 00000730030` (Ausgabe des Punktes, `073x`), `0003: 00000000020` (Stopp).
Aufruf mit `--stanzer1 out/band.txt` erzeugt eine Datei mit den Zeilen `00010101` und `00111011`.
Ohne `--stanzer1` endet derselbe Test mit der roten Fehlermeldung aus Abschnitt 10.

### 13.4 Vorzeichenbit und X-Abbruch (synthetische Tests, Stand 28.09.2026)

Alle Tests haben `#PROT STUFE=0` und enden mit der Diagnose des Befehls 164 (`#SPEI-… 4000-4037`).

**`s1-R1`** – verkürzter Gruppen-Transport mit Rechtsverschiebung (R=1, Code `542`), AC startet mit `…006`:

```
0000: 00003000211          # AC := <3000>
0001: 00004001542          # GX-Transport nach 4001, Z=2 (R=1, ohne Löschen)
0002: 00000020164          # Leerbefehl, Diagnose #DOK-0020
0003: 00000000020
3000: 00000000006
```

Ergebnis: **zwei** Zellen werden geschrieben, `4001: 00000000006` (Ladewert unverschoben, vor der Verschiebung noch positiv)
und `4016: 00000000003` (die Zelle, bei der AC durch die Rechtsverschiebung negativ wird: z₀ ist bei R=1 stets 0, entscheidend
ist z₃₂, hier 1 nach der ersten Verschiebung). Bei z₀ als Vorzeichen würden alle 32 Zellen geschrieben.

**`s2-R2`** – Linksverschiebung (R=2, Code `544`) und AC = `…003`: z₀ entscheidet. Es werden alle 32 Zellen geschrieben;
die letzte (`4037`) enthält `00060000000` – die durch die Verschiebung negativ gewordene, aber noch abgespeicherte 32. Zelle.

**`s3-neg`** – Sonderfall: AC ist bereits **vor** der ersten Zelle negativ (`3000: 40000000000`, GX-Transport R=2). Auch hier
wird die erste Zelle (`4001`) noch vollständig bearbeitet und mit dem negativen Wert beschrieben, erst danach bricht der Lauf ab.

### 13.5 Referenzläufe (Sollwerte für Regressionsläufe)

**Hinweis (29.09.2026):** Seit der Korrektur „164/166 ohne Resultatbehandlung“ (Abschnitt 9) verschiebt der Leerbefehl den AC nicht mehr. Sollwerte von Tests, die mit 164 enden (z. B. `0014`, `0015-030`), sind neu zu bestimmen, sofern der AC beim Leerbefehl ≠ 0 war.

Alle Tests: Tastenfolge `H G R`, Ende „Unbedingter Stop (US:=1)“, FE=0, FÜ=0, BS=0. Die Knotenzahl ist fassungsabhängig.

| Test | Inhalt | Ergebnis |
|---|---|---|
| `0004` | Ladebefehl, GX-Transport, Linksverschiebung | 26 Zellen ≠ 0; AC am Ende `0`; BZ=0004 |
| `0005` | Gruppen-Transport (`640`), Startsektor 01 bis Sektor 23 | 27 Zellen ≠ 0; AC `…200`; BZ=0004 |
| `0006`, `0007` | WX-/GX-Transport mit Linksverschiebung | je 14 Zellen ≠ 0; AC `0`; BZ=0004 |
| `0010` | Laden, Addieren, Speichern; zwei `#SPEI`-Bereiche | AC `…600`; BZ=3010; 5 Speicherzeilen in der Diagnose |
| `0011` | Subtraktion, `241` löscht AC vor dem Transport | AC `0`; `3020`=`77777777770`, `3021`=`0`; BZ=3011 |
| `0012` | Positiv-Sprung genommen, Befehl `5002` übersprungen | AC `…200`; BZ=5006 |
| `0021` | Ladebefehl, WX-Transport mit Linksverschiebung, X-Abbruch (Autor-Test) | 3 Zellen ≠ 0: `4001`=`10000000000`, `4016`=`20000000000`, `4033`=`40000000000` (letztere jetzt korrekt gespeichert); AC `0`; BZ=0004 |
| `0014` | Sprung, Laden, Vergleichersetzen, Vergleichersprung 2 (zweimal genommen), Transport, Leerbefehl | Diagnose: BZ=3011 AC=`40000000200`; Ende: BZ=3012 AC=`40000000200` V1=0 V2=1; 204 Knoten |

### 13.6 Neue Testmarke `#SPUR-xxxx aaaa` (Ergänzung 29.09.2026)

Analog zu `#SPEI-xxxx ssss-eeee`, aber statt einer Adressspanne wird die **ganze Spur (Bahn)** ausgegeben,
in der `aaaa` liegt — alle 32 Zellen, in der physischen Zugriffsreihenfolge der Trommel (nicht in
aufsteigender logischer Adresse). Erscheint in der Diagnose nach allen `#SPEI-xxxx`-Ausgaben derselben
Adresse und ist von `#DOK` unabhängig; vor den 32 Zellen steht die Marke `#SPUR-xxxx aaaa` als Kopfzeile. Beispiel `s4-spur` (13.5): `#SPUR-0023 4000` gibt beginnend mit `4000` alle 32 Zellen der
Spur `40xx` in physischer Reihenfolge aus (`4000, 4015, 4032, 4007, 4024, 4001, 4016, 4033, …, 4023`).

## 14. Vorgaben für die PDF-Bedienungsanleitung

Dieser Abschnitt legt fest, was für die Erzeugung einer **menschenzentrierten** Bedienungsanleitung (PDF)
erforderlich ist. Die Anleitung erklärt die **Bedienung des Interpreters**, nicht den Rechner C 8205; den Rechner
nur so weit, wie die Bedienung ihn braucht.

### 14.1 Zielgruppe und Ton

- **Leser:** Personen, die Testprogramme für den C 8205 schreiben und durchrechnen, ohne den Aufbau des Interpreters zu kennen.
  Kenntnis von Oktalzahlen und Grundbegriffen des Rechners (Register, Flags) wird nicht vorausgesetzt; Begriffe werden im Glossar erklärt.
- **Sprache:** Deutsch, knapp, in der Handlungsform („Starten Sie …“ oder Imperativ, einheitlich). Ein Satz, eine Handlung.
- **Terminologie einheitlich:** „Lochstreifenleser“ (Kürzel Leser), „Lochstreifenstanzer“ (Stanzer), „Schreibwerk“ (SW), „Testdatei“,
  „Tastenfolge“, „Trommeldatei“. Kanäle immer als K0 bis K3.

### 14.2 Gliederung

| Kapitel der Anleitung | Inhalt | Quelle in dieser Datei |
|---|---|---|
| 1 Zu dieser Anleitung | Zweck, Zielgruppe, Symbole, Stand | 1, 14.1 |
| 2 Erste Schritte | Voraussetzungen, Ordner, erster Lauf | 3, 4 |
| 3 Tests schreiben | Aufbau der Testdatei, Marken, Tastenfolge | 6, 7 |
| 4 Interpreter starten | Aufruf, Schalter, Wrapper, Suche der Testdatei | 5 |
| 5 Ein- und Ausgabe | Kanäle, Schreibwerk, Leser, Stanzer, Tastatur | 8 |
| 6 Ergebnisse lesen | Bildschirm, Endzeile, Protokoll | 9 |
| 7 Wenn etwas schiefgeht | Fehlermeldungen mit Abhilfe | 10 |
| 8 Beispiele Schritt für Schritt | drei Beispiele mit Ausgaben | 13 |
| 9 Kurzreferenz | eine Seite: alle Schalter, Tokens, Kanäle | 5, 7, 8 |
| Anhang | Glossar, Grenzen des Interpreters, Verweise auf das Regelwerk | 11, 12 |

### 14.3 Pflichtinhalte und Gestaltung

- **Jede Handlung mit Beispiel:** Jeder Schalter und jedes Token erscheint mindestens einmal in einem lauffähigen Beispiel.
- **Echte Ausgaben:** Terminalausgaben werden aus tatsächlichen Läufen übernommen, nicht von Hand geschrieben. Feste Werte
  (Knotennummern) nur mit Vermerk, dass sie fassungsabhängig sind.
- **Farben erklären und nicht allein tragen lassen:** Dunkelgelb = Ausgabe des Rechners (Schreibwerk), Rot = Fehlermeldung.
  In Schwarz-Weiß-Druck muss die Bedeutung aus dem Text hervorgehen (z. B. Prefix „Fehler:“ bzw. Kennzeichnung im Beispiel).
- **Hinweis- und Warnkästen:** „Hinweis“ für Nützliches, „Achtung“ für Stellen, an denen Tests scheitern (z. B. `SW=1` vor `G`,
  Tastenfolge endet mit `R`, Zufalls-Zeichenlage KB/GB).
- **Codeblöcke** in Festbreitenschrift, Terminalausgaben von Eingaben unterscheidbar (Eingaben nach `$`).
- **Tabellen** für Schalter, Tokens, Kanäle, Fehlermeldungen (Vorlage: Abschnitte 5, 7, 8, 10).
- **Fehlerverzeichnis** alphabetisch oder nach Meldungstext auffindbar; jede Meldung mit Ursache und Abhilfe.
- **Glossar:** Akkumulator (AC), Befehlszähler (BZ), Adressregister (AR), Operationsregister (OR), Flag, Trommel, Sektor, Bahn,
  Oktal, Knoten, Konnektor, Phase I bis IV, Stub, Testmarke, Zeichenlage KB/GB, Kanal K0 bis K3, T/SW, Sprung-Umstellung.
- **Layout:** A4, Seitenzahlen, Inhaltsverzeichnis mit Seitenverweisen, Kopfzeile mit Titel und Stand, Kapitel beginnen auf neuer Seite.
  Die Kurzreferenz passt auf **eine** Seite und ist einzeln druckbar.
- **Stand und Version:** Datum und Fassung des Interpreters auf der Titelseite; die Anleitung gilt für die dort genannte Fassung.

### 14.4 Erzeugung

1. **Quelle:** Die Anleitung wird aus dieser Datei (Abschnitte 1 bis 13) abgeleitet, nicht kopiert; Fachtexte zum Rechner werden
   nur verlinkt oder als Glossareintrag verkürzt. Der Abschnitt 14 selbst gehört nicht in die Anleitung.
2. **Beispiele neu erzeugen:** Vor jeder Ausgabe alle Beispiele des Kapitels 8 mit dem aktuellen `c8205_interp.py` ausführen und die
   Ausgabe übernehmen (Farben in Screenshots oder farbigen Codeblöcken sichtbar machen).
3. **Werkzeug:** Markdown-nach-PDF (z. B. Pandoc mit LaTeX-Vorlage) oder Word-Datei mit anschließender PDF-Ausgabe; die Wahl ist offen.
   Zeichensatz muss `ä ö ü ß`, Oktalzahlen und die Symbole `→ ≤ ≥ …` darstellen.
4. **Abnahmeprüfung** vor Veröffentlichung:
   - jeder Schalter aus `python3 c8205_interp.py --help` kommt in der Anleitung vor,
   - jede Fehlermeldung aus Abschnitt 10 ist im Fehlerverzeichnis,
   - jedes Beispiel wurde mit der genannten Fassung ausgeführt,
   - Verweise auf Dateinamen entsprechen den tatsächlichen Namen (Präfix `C8205-Interpreter-`),
   - Glossar, Inhaltsverzeichnis und Kurzreferenz sind vollständig.

### 14.5 Pflege

Ändert sich der Interpreter (neuer Schalter, neues Token, neue Meldung, umgesetzter offener Punkt), sind in dieser Datei die Abschnitte
5 bis 11 und die Beispiele in 13 zu aktualisieren und die Anleitung neu zu erzeugen. Gelöste Punkte aus Abschnitt 11 werden dort
gestrichen und in 5 bis 9 beschrieben.
