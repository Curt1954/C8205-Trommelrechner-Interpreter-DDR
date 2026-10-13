** Versionierung (Wurzeldokument für Versionsnummern) **

Version: 0.03-007

Dieses Dokument legt fest, wie die Dateien des Projekts C 8205 versioniert werden: wie eine Versionsnummer aufgebaut
ist, welche Dateien eine tragen, wo sie steht und wann sie sich ändert. Es beschreibt keine Inhalte der Dateien,
sondern nur ihre Kennzeichnung. Der Ausgangsstand (Abschnitt 5) wurde am 09.10.2026 vom Projektinhaber auf
**0.03-001** gesetzt.

> **Arbeitsregel für alle, die an diesen Dateien mitarbeiten (auch KI-Sitzungen anderer Konten):**
>
> 1. **Jede Änderung** an einer versionierten Datei erhöht ihren **Build** (`zzz`) um 1. Die geänderte Datei wird mit der
>    neuen Nummer übergeben; unveränderte Dateien behalten ihre Nummer.
> 2. **Hauptversion** (`y`) und **Unterversion** (`xx`) werden **nur auf ausdrückliche Aufforderung** des Projektinhabers
>    erhöht, nie von selbst, auch nicht bei großen Änderungen.
> 3. Mit **jeder neuen Unterversion oder Hauptversion beginnt der Build wieder bei 001** (bei einer neuen Hauptversion
>    beginnt außerdem die Unterversion wieder bei 00).
>
> Einzelheiten: Abschnitt 3. Weitergabe der Regel und Text für Projektanweisungen: Abschnitt 7.


## 1. Aufbau der Versionsnummer

Eine Versionsnummer hat die Form `y.xx-zzz`:

| Teil | Name | Stellen | Wertebereich | Bedeutung |
|---|---|---|---|---|
| `y` | Hauptversion | beliebig viele Ziffern, ohne führende Null | 0, 1, 2, … | Entwicklungsabschnitt. `0` heißt: im Aufbau, noch nicht freigegeben |
| `xx` | Unterversion | genau 2 Ziffern | 00 bis 99 | Stand innerhalb der Hauptversion; wird vom Projektinhaber gesetzt |
| `zzz` | Build | genau 3 Ziffern | 001 bis 999 | laufende Nummer der Änderungen innerhalb der Unterversion; jede Änderung zählt 1; beginnt mit jeder neuen Unterversion oder Hauptversion wieder bei 001 |

Zwischen Hauptversion und Unterversion steht ein Punkt, vor dem Build ein Bindestrich. Das Muster als regulärer
Ausdruck: `[0-9]+\.[0-9]{2}-[0-9]{3}`.

Beispiele: `0.03-001` (erster Build der Unterversion 0.03), `0.03-002` (nächster Build), `0.04-001` (neue Unterversion),
`1.00-001` (erste Fassung der Hauptversion 1).

**Reihenfolge:** Die drei Teile werden einzeln als ganze Zahlen von links nach rechts verglichen. `0.03-012` ist neuer
als `0.03-009` und älter als `0.04-001`. Der Build `000` wird nicht vergeben.


## 2. Was eine Versionsnummer trägt

| Gegenstand | Versionsnummer |
|---|---|
| jede `.md`-Datei des Projekts, in allen Ordnern (auch `README.md`, `README.en.md` und die BIS-Dokumentation) | ja |
| der Python-Interpreter `c8205_interp.py` | ja |
| die Hilfsprogramme `c8205_lochstreifen_anzeige.py` und `c8205_lochstreifen_eingabe.py` | eigene Programmversion (Konstante `VERSION`, Abfrage mit `--version`), **nicht** im Schema `y.xx-zzz`; sie wird in `C8205-Interpreter-Lochstreifen-Hilfsprogramme.md` geführt. Die zugehörige `.md`-Datei trägt dagegen die Nummer `y.xx-zzz` |
| die Assemblerdokumentation `Assembler/Dokumentation/C8205_Assembler_Dokumentation.odt` (maßgeblich) | ja, `y.xx-zzz` (Stand 11.10.2026: `1.00-001`). Die zugehörige `.md` trägt als `.md`-Datei ebenfalls eine eigene Nummer und nennt im Kopf die Version der `.odt`, von der sie abgeleitet ist. Das PDF `C8205-Assemblerdokumentation_A4.pdf` wird wie die übrigen PDFs aus der `.md` erzeugt (PDF-Richtlinie, `C8205-Interpreter-PDF.md`, Abschnitt 4.6 und 8); es trägt keine eigene Nummer, sein Deckblatt nennt die Version der `.md` |
| das Assemblerprogramm `c82ass` (Binary und Quellcode `Assembler/Sourcecode/ca82ass.c`) | eigene Programmversion `y.xx` ohne Build (Stand 11.10.2026: `1.00`), s. Abschnitt 4 |
| alles andere (PDFs, Tests, übrige Skripte, Trommeldatei) | derzeit nein, s. Abschnitt 8. Die PDFs tragen keine eigene Nummer, nennen aber auf dem Deckblatt die Version ihrer Quelle(n) |

- **Jede Datei hat ihre eigene Nummer.** Die Nummern verschiedener Dateien sind voneinander unabhängig: Ändert sich
  eine Datei, ändert sich nur ihre Nummer.
- Eine **Kopie** einer Datei (z. B. in `Bausteininterpretiersystem BIS/`) ist kein eigener Gegenstand; sie trägt
  dieselbe Nummer wie das Original und wird mit ihm zusammen nachgeführt.
- Die Versionsnummer ersetzt weder das Datum noch den Vermerk „Stand:“ in den Dateien, die einen haben. Beide
  stehen nebeneinander.


## 3. Wann sich die Nummer ändert

| Teil | Wird erhöht | Wirkung auf die Nummer |
|---|---|---|
| Build | bei **jeder Änderung** an der Datei, ohne Aufforderung und ohne Ausnahme für kleine Änderungen (Tippfehler, Umformulierung, Layout) | `zzz` + 1 |
| Unterversion | **nur auf ausdrückliche Aufforderung** des Projektinhabers | `xx` + 1, `zzz` := 001 |
| Hauptversion | **nur auf ausdrückliche Aufforderung** des Projektinhabers | `y` + 1, `xx` := 00, `zzz` := 001 |

Hauptversion und Unterversion bleiben also stehen, auch wenn eine Änderung groß ist oder bestehende Tests unbrauchbar
macht. Ob und wann sie steigen, entscheidet allein der Projektinhaber.

Weitere Regeln:

- **Eine Änderung** ist ein Änderungsschritt: alle Bearbeitungen einer Datei, die zusammen als neuer Stand übergeben
  werden (z. B. eine Lieferung am Ende einer Sitzung oder ein Commit). Sie erhöhen den Build einmal um 1. Wird dieselbe
  Datei später erneut geändert, steigt der Build erneut.
- **Jede Datei für sich:** Betrifft ein Vorhaben mehrere Dateien (z. B. ein neuer Schalter im Interpreter und seine
  Beschreibung in `C8205-Interpreter-Python_Interpreter.md`), erhöht sich der Build jeder geänderten Datei um 1.
  Unveränderte Dateien behalten ihre Nummer.
- **Zurücksetzen:** Erhöht der Projektinhaber auf Aufforderung einen Teil, beginnen die Teile rechts davon neu (Build 001,
  bei der Hauptversion zusätzlich Unterversion 00).
- **Überlauf:** Ist Build 999 oder Unterversion 99 erreicht, wird nichts von selbst erhöht. Vor der nächsten Änderung
  fragt man den Projektinhaber, wie es weitergehen soll.
- **Nur vorwärts:** Eine Nummer wird nie zurückgezählt und nie ein zweites Mal vergeben. Eine Nummer bezeichnet genau
  einen Stand der Datei.
- **Die Versionszeile** im Zuge einer Änderung anzupassen ist keine eigene Änderung; sie zählt nicht zusätzlich.
- **Neue Datei:** Sie beginnt mit `0.01-001`, sofern der Projektinhaber nichts anderes vorgibt.
- **Änderungsvermerke** (z. B. „Aenderung …“ im Kopf von `c8205_interp.py`) nennen die Nummer, die durch die
  Änderung entsteht, z. B. „Aenderung 09.10.2026 (Version 0.03-002)“.


## 4. Wo die Nummer steht

| Gegenstand | Ort |
|---|---|
| `.md`-Datei | eine eigene Zeile `Version: y.xx-zzz` unmittelbar unter der Titelzeile (der ersten Zeile der Datei), mit je einer Leerzeile davor und danach |
| `.md`-Datei, die der Interpreter oder ein anderes Werkzeug zeilenweise mit `#` als Kommentarzeichen liest (`C8205-Interpreter-Eingänge_der_Knoten.md`, `C8205-Interpreter-Beschreibung_der_Knoten.md`) | dieselbe Stelle, aber als Kommentarzeile `# Version: y.xx-zzz`, getrennt durch je eine `#`-Zeile; so bleibt die Datei für das Werkzeug unverändert lesbar |
| `c8205_interp.py` | Zeile `Version: y.xx-zzz` im Kopfkommentar unter der ersten Zeile **und** die Konstante `VERSION` am Programmanfang; beide müssen übereinstimmen |
| `C8205_Assembler_Dokumentation.odt` | Titelzeile (erste Zeile): `Cross-Assembler für C8205 / C8205Z Version y.xx-zzz` |
| `c82ass` (Programm) | Konstante in der Funktion `greetings()` in `Assembler/Sourcecode/ca82ass.c`; das Programm gibt beim Start und bei `-h` die Zeile `C8205 Assembler C82aas Version y.xx` aus. Die `.odt` und die `.md` der Assemblerdokumentation nennen dieselbe Nummer in den Beispielausgaben und im Kopf von Abschnitt 3 (`Version: y.xx`) |

- Dateinamen und Titelzeilen tragen die Nummer nicht (Dateinamen stehen in vielen Verweisen).
- **Abfrage beim Interpreter:** `python3 c8205_interp.py --version` gibt `c8205_interp.py y.xx-zzz` aus und endet mit
  Rückkehrcode 0, ohne einen Test auszuführen. Die Wrapper `c8205_interpreter.sh` und `.bat` sind für Testläufe gedacht
  (Testdatei als erstes Argument); die Version wird direkt mit `python3` abgefragt.
- Die Ausgaben und Protokolle des Interpreters nennen die Version nicht (s. Abschnitt 8).


## 5. Ausgangsstand

Am 09.10.2026 wurde die Versionierung eingeführt. Alle `.md`-Dateien des Projektarchivs `projekt_c8205.zip` (einschließlich
dieser Datei) und `c8205_interp.py` erhielten die Nummer **0.03-001**; der Wert wurde vom Projektinhaber festgelegt. Zum
Ausgangsstand gehören auch die zugehörigen Anpassungen: der Schalter `--version`, die Verweise auf dieses Dokument
(`C8205-Projektstruktur.md`, `C8205-Interpreter-Projektueberblick.md`, `C8205-Interpreter-Überblick_und_Gesamtaufbau.md`,
`C8205-Interpreter-Python_Interpreter.md`, `README.md`, `README.en.md`) und die Aufnahme dieser Datei in die Liste der
Dateien, die der Claude-Interpreter nicht braucht (`C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 1b.1). Sie erhöhen
keine Nummer. Ab dem nächsten Änderungsschritt gelten die Regeln aus Abschnitt 3.


## 6. Prüfung

Alle Versionszeilen anzeigen (Linux/macOS; unter Windows z. B. in Git Bash):

```
grep -rHE '^(# )?Version: [0-9]+\.[0-9]{2}-[0-9]{3}$' --include='*.md' --include='c8205_interp.py' .
```

Dateien finden, denen die Versionszeile fehlt (keine Ausgabe = alle Dateien haben eine):

```
grep -rLE '^(# )?Version: [0-9]+\.[0-9]{2}-[0-9]{3}$' --include='*.md' .
```

Version des Interpreters, so wie das Programm sie kennt (muss der Zeile `Version:` im Kopfkommentar entsprechen):

```
python3 c8205_interp.py --version
```

Version des Assemblers, so wie das Programm sie kennt (muss der Konstante in `Assembler/Sourcecode/ca82ass.c` und den Angaben der
Assemblerdokumentation entsprechen; das Skript `c82ass.sh` muss aus dem Verzeichnis `Assembler` gestartet werden):

```
cd Assembler && ./c82ass.sh -h
```


## 7. Weitergabe der Regel

Die Arbeitsregel (Kasten am Anfang) muss jeder kennen, der Dateien dieses Projekts ändert, auch Mitarbeiter und
KI-Sitzungen anderer Konten. Eine KI-Sitzung weiß nichts von früheren Gesprächen oder anderen Konten; verlässlich ist nur,
was in den Dateien steht. Deshalb steht die Regel in diesem Dokument, in `README.md`, `README.en.md`,
`C8205-Interpreter-Projektueberblick.md`, im Kopf von `baz-wirkungstabelle.md` (die KI-Sitzungen des Claude-Interpreters
laufend ergänzen) und im Kopfkommentar von `c8205_interp.py`.

Zum Einfügen in die Projektanweisungen oder persönlichen Einstellungen eines Claude-Kontos (die Sitzung kennt die Regel
dann auch ohne hochgeladene Dateien):

```
Versionierung im Projekt C 8205 (Aufbau y.xx-zzz, Definition: C8205-Versionierung.md):
Jede Änderung an einer versionierten Datei (alle .md-Dateien und c8205_interp.py) erhöht deren Build (zzz) um 1.
Die geänderte Datei wird mit der neuen Nummer übergeben. Hauptversion (y) und Unterversion (xx) werden nur auf
ausdrückliche Aufforderung des Projektinhabers erhöht, nie von selbst. Bei jeder neuen Unterversion oder Hauptversion
beginnt der Build wieder bei 001 (bei einer neuen Hauptversion auch die Unterversion bei 00).
```


## 8. Offene Punkte

- **Nicht versionierte Dateien:** PDFs, Tests, Skripte (`.sh`, `.bat`, `c8205_befehlssweep.py`, `erzeuge_leere_trommel.py`; die beiden Lochstreifen-Hilfsprogramme haben eine eigene Programmversion, s. Abschnitt 2)
  und Trommeldatei tragen keine Nummer; der Assembler `c82ass` hat seit dem 11.10.2026 eine Programmversion (Abschnitt 2). **PDFs:** Sie tragen keine eigene Nummer, aber ihr
  Deckblatt nennt die Version der Quelldatei(en) zum Zeitpunkt der Erzeugung und den Stand (Erzeugungsdatum); so ist
  erkennbar, ob ein PDF noch zur Quelle passt (`C8205-Interpreter-PDF.md`, Abschnitt 4.2 und 4.3; entschieden am
  11.10.2026). Das Erzeugen eines PDFs bricht ab, wenn der Quelldatei die Versionszeile fehlt.
- **Assemblerdokumentation:** Seit dem 11.10.2026 tragen die `.odt` und die `.md` die Nummer `1.00-001` (auf Anweisung des
  Projektinhabers, Abschnitt 9). Jede der beiden Dateien zählt ihren Build selbst (Abschnitt 3); die `.md` nennt im Kopf die Version
  der `.odt`, von der sie abgeleitet ist. Das PDF trägt keine eigene Nummer; sein Deckblatt nennt wie bei allen PDFs die Version der `.md`, aus der es erzeugt wird.
- **Gesamtversion:** Eine Nummer für das ganze Projekt gibt es nicht; es zählen nur die Nummern der einzelnen Dateien.
- **BAZ-Wirkungstabelle:** `baz-wirkungstabelle.md` gilt laut ihrem Kopf nur, solange sich die zugrunde liegenden Dokumente
  nicht ändern. Mit Versionsnummern ließe sich festhalten, für welche Nummern von `Eingänge_der_Knoten`,
  `Beschreibung_der_Knoten` und `Befehlsliste` sie gilt. Nicht umgesetzt.
- **Protokolle:** Die Protokolle des Interpreters nennen dessen Version nicht. Ob sie es sollen, ist nicht entschieden.


## 9. Änderungsprotokoll

| Version | Datum | Änderung |
|---|---|---|
| 0.03-001 | 09.10.2026 | Versionierung eingeführt (Ausgangsstand, vom Projektinhaber festgelegt). |
| 0.03-002 | 09.10.2026 | Regeln zum Hochzählen auf Anweisung des Projektinhabers geändert: jede Änderung erhöht den Build um 1, Hauptversion und Unterversion nur auf Aufforderung (Abschnitt 3). Arbeitsregel am Anfang, Abschnitt 7 (Weitergabe der Regel) und dieses Protokoll neu. |
| 0.03-003 | 09.10.2026 | Auf Anweisung des Projektinhabers: Der Build beginnt mit jeder neuen Unterversion oder Hauptversion wieder bei 001. Die Regel stand schon in Abschnitt 3; sie steht jetzt auch im Kasten am Anfang, in der Tabelle von Abschnitt 1 und im Text für Projektanweisungen (Abschnitt 7). |
| 0.03-004 | 10.10.2026 | Aufnahme der Lochstreifen-Hilfsprogramme: eigene Programmversion (Abschnitt 2) und Hinweis in Abschnitt 8. |
| 0.03-005 | 11.10.2026 | PDFs: Die Version der Quelldatei(en) steht auf dem Deckblatt (Entscheidung zur PDF-Gestaltungsrichtlinie, Abschnitt 4); der offene Punkt in Abschnitt 8 ist damit erledigt, Abschnitt 2 (Tabelle) und Abschnitt 8 angepasst. |
| 0.03-006 | 11.10.2026 | Assemblerdokumentation und Assemblerprogramm erhalten Versionsnummern: Auf Anweisung des Projektinhabers Version 1.00 (`.odt` und `.md` als `1.00-001`, Programm `c82ass` als `1.00`). Abschnitte 2, 4, 6 und 8 angepasst. |
| 0.03-007 | 11.10.2026 | Das Assembler-PDF wird regulär aus der `.md` erzeugt, nicht mehr aus der `.odt` exportiert (PDF-Richtlinie, Abschnitt 4.6 und 8); Abschnitt 2 (Tabelle) und Abschnitt 8 angepasst. |
