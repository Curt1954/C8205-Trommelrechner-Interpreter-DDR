** Versionierung (Wurzeldokument für Versionsnummern) **

Version: 0.95-001

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
| die Assemblerdokumentation `Assembler/Dokumentation/C8205_Assembler_Dokumentation.odt` (maßgeblich) | ja, `y.xx-zzz` (Stand 11.10.2026: `1.00-001`; Stand 19.10.2026: Titelzeile der `.odt` `1.00-005`, `.md` `1.00-008`, Abschnitt 8). Die zugehörige `.md` trägt als `.md`-Datei ebenfalls eine eigene Nummer und nennt im Kopf die Version der `.odt`, von der sie abgeleitet ist. Das PDF `C8205-Assemblerdokumentation_A4.pdf` wird wie die übrigen PDFs aus der `.md` erzeugt (PDF-Richtlinie, `C8205-Interpreter-PDF.md`, Abschnitt 4.6 und 8); es trägt keine eigene Nummer, sein Deckblatt nennt die Version der `.md` |
| die GRAFIK-Module (`c8205_grafik.py`, `grafik-interpreter-module/*.py`) | **eigene Zählung** je Modul im Schema `Gn-nnn` (n = Stufe, nnn = Zähler), bei einzelnen Modulen mit eigener Kennung (`DL-`, `FL-`, `HZ-`, `HW-`); **nicht** im Schema `y.xx-zzz`. Sie steht im Kopf des Moduls (Zeile `Version:`); `c8205_grafik.py` meldet sie zusätzlich über die Konstante `VERSION_GRAFIK`. Stand 19.10.2026: Abschnitt 10 |
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
keine Nummer. Ab dem nächsten Änderungsschritt gelten die Regeln aus Abschnitt 3. Die Unterversion wurde am 20.10.2026 auf Aufforderung des Projektinhabers auf 0.95 gesetzt (Abschnitt 9); der Ausgangsstand 0.03-001 bleibt als Geschichte stehen.


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
- **GRAFIK-Module (Stand 19.10.2026, geprüft bei G6-017):** (a) `c8205_grafik.py` trägt im Kopf noch `Version: G2-004` und den Satz „`c8205_interp.py` bleibt … 0.03-013“, die Konstante `VERSION_GRAFIK` lautet `G4-003`; beide stimmen nicht überein, und der Kopf ist veraltet (die AENDERUNG-Notizen nennen G2-011 und G3-003, im Text des Moduls kommen G2-012 und G4-008 vor). Eine Regel, welche der Angaben maßgeblich ist, gibt es nicht. (b) `grafik_k0.py` und `grafik_trommel.py` tragen keine `Version:`-Zeile. (c) Ob jedes Modul seinen Zähler je Änderungsschritt um 1 erhöht hat, ist nicht prüfbar (keine Historie im Archiv). **Stufe 6 ändert keinen Programmcode;** die Kopfzeilen bleiben, wie sie sind. Zu entscheiden: Kopfzeile von `c8205_grafik.py` bei der nächsten Code-Änderung auf `VERSION_GRAFIK` angleichen.
- **`.md`-Dateien ohne Versionszeile:** Die Prüfung aus Abschnitt 6 (zweiter Befehl) meldet bei G6-017 unter den bleibenden Dateien `ton/SW_Ton_Beschreibung.md` sowie die neuen `C8205-Interpreter-GRAFIK_Beschreibung.md` und `C8205-Interpreter-GRAFIK_Pruefverfahren.md` (inzwischen nachgeführt, siehe unten). **Nachführung G6-018 (S6-08):** `ton/SW_Ton_Beschreibung.md`, `C8205-Interpreter-GRAFIK_Beschreibung.md` und `C8205-Interpreter-GRAFIK_Pruefverfahren.md` tragen jetzt `0.01-001` (Regel „neue Datei“; für `ton/SW_Ton_Beschreibung.md` setzt der Entwickler diese Nummer, solange der Projektinhaber keine andere nennt). Ihre Builds zählen ab jetzt je Änderung. Die zu löschenden Dateien (`C8205-Anforderungspaket-*.md`, `CHECKPOINT_*`, `AENDERUNG_*`, `HWCHECK_HW-003.md`) tragen meist keine; sie entfallen.
- **Builds des Interpreters:** `c8205_interp.py` hat die Builds 0.03-013 bis 0.03-017 lückenlos (je +1; Kopfzeile, Konstante `VERSION` und `--version` stimmen überein, geprüft bei G6-017). Für die `.md`-Dateien ist die Regel „je Änderungsschritt +1“ nicht prüfbar, weil das Archiv keine frühere Fassung enthält.
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
| 0.03-013 | 19.10.2026 | Stufe 6 (S6-04): Triage-Liste `TRIAGE_S6-04_Stichprobe_A6-6.md` angelegt; `GRAFIK_Beschreibung` 0.01-003 (OP-39 und OP-40 neu, Zeile U-3/U-4/U-6 in §10.5, §10.7); `GRAFIK_Pruefverfahren` 0.01-003 (Hinweis zur eingegliederten Datei aktualisiert); drei Kommentare in `c-module/tonmisch.c`, `tonmisch.h` und `python/c8205_ton_methoden.h` (Verweis „Dokument 10“ → GRAFIK_Beschreibung Abschnitt 6, alt: Dok. 10; S6-07, von der Suche in G6-020 nicht erfasst). Ausführbarer Code unverändert: nach Entfernen der Kommentare (`gcc -x c -fpreprocessed -dD -E -P`) ist der Inhalt aller drei Dateien identisch. |
| 0.03-012 | 19.10.2026 | Stufe 6 (S6-07, Teil 2): Verweise auf `AENDERUNG_K0_…`, `Dokument 10`, `Dokument 01, 06` und `CHECKPOINT_Stufe2.md` umgestellt in `Python_Interpreter` (0.03-014), `Bedienpult_mit_Schaltern` (0.03-010), `Lochstreifenleser` (0.03-007), `Projektstruktur` (0.03-013), `README.md` und `README.en.md` (0.03-011), `ton/SW_Ton_Beschreibung.md` (0.01-003) und einen Docstring in `grafik_pult.py`; `GRAFIK_Beschreibung` 0.01-002 (Ausnahme für S6-12, §10.6). Kein ausführbarer Code geändert. |
| 0.03-011 | 19.10.2026 | Stufe 6 (S6-07, Teil 1): Verweise auf die Anforderungsdokumente umgestellt: `README.md` (0.03-010), `README.en.md` (0.03-010), `Projektstruktur` (0.03-012), `ton/SW_Ton_Beschreibung.md` (0.01-002), `GRAFIK_Pruefverfahren` (0.01-002); in 16 Python-Dateien (52 Kommentar- und Docstring-Stellen) als „GRAFIK_Beschreibung §n (alt: Dok. nn …)“. Kein ausführbarer Code geändert (AST ohne Docstrings gleich, alle Dateien kompilieren). Die GRAFIK-Modulzähler (OP-38) bleiben unverändert. |
| 0.03-010 | 19.10.2026 | Stufe 6 (S6-08): Versionszeilen `0.01-001` für `ton/SW_Ton_Beschreibung.md` und die zwei GRAFIK-Dokumente; Abschnitt 8 nachgeführt. Die Bestandsdokumente `Python_Interpreter` (0.03-013), `Bedienpult_mit_Schaltern` (0.03-009), `Magnettrommel` (0.03-003), `Lochstreifenleser` (0.03-006), `Projektstruktur` (0.03-011), `Projektueberblick` (0.03-007), `Einstieg_fuer_Neueinsteiger` (0.01-003), `Überblick_und_Gesamtaufbau` (0.03-004) und `Durchführung_eines_Tests` (0.03-014) haben einen kurzen GRAFIK-Absatz erhalten. |
| 0.03-009 | 19.10.2026 | Stufe 6 (S6-03): Builds 0.03-014 bis 0.03-017 des Interpreters mit Inhalt und Prüfung in Abschnitt 10 aufgenommen, darunter 0.03-015 und 0.03-016 aus den Notizen `AENDERUNG_E_unter_M_…` und `AENDERUNG_K0_Anwahl_Schalter_SW_…`, die damit gelöscht werden können; GRAFIK-Module mit eigener Zählung (Abschnitt 2, 8, 10); Stand der Assemblerdokumentation (Abschnitt 2); drei neue offene Punkte in Abschnitt 8. |
| 0.03-008 | 19.10.2026 | Stand Interpreter nachgeführt: `c8205_interp.py` steht auf **0.03-017** (Stufe 5, Schalter `--MODUS TEST\|GRAFIK`, Standard GRAFIK; Testläufe brauchen `--MODUS=TEST`). Die Builds 0.03-013 bis 0.03-017 sind im Kopf von `c8205_interp.py` (Zeilen „Aenderung …“) beschrieben, nicht in diesem Dokument. Die Wrapper `c8205_interpreter.sh`/`.bat` tragen keine eigene Nummer. |
| 0.95-001 | 20.10.2026 | Auf Aufforderung des Projektinhabers: Unterversion **0.95** für alle Dateien, die eine Nummer im Schema `y.xx-zzz` tragen, Build jeweils wieder **001** (alle `.md`-Dateien einschließlich dieser Datei und `c8205_interp.py`). Ausgenommen: die Assemblerdokumentation (`C8205_Assembler_Dokumentation.md` bleibt `1.00-009`, `.odt` und `c82ass` unverändert), `C8205-Interpreter-BIS.md` (0.03-003) und `C8205-Interpreter-Objektdatei_Listing.md` (0.03-002) sowie die Dateien mit eigener Zählung (Hilfsprogramme, GRAFIK-Module). Die Verweise im Fließtext auf frühere Nummern (z. B. 0.03-016) bleiben als Historie stehen. |


## 10. Versionsstand des Interpreters (Builds 0.03-013 bis 0.03-017) und der GRAFIK-Module

Quelle: die Zeilen „Aenderung …“ im Kopfkommentar von `c8205_interp.py` und die Notizen `AENDERUNG_*` (übernommen bei G6-017; die Notizen sind danach entbehrlich). Alle Builds sind **Zwischenstand, vom Projektinhaber mit den Stufen abgenommen** (Stufe 2 bis 5, 17. bis 19.10.2026).

### 10.1 Interpreter `c8205_interp.py`

| Build | Datum | Änderung | GRAFIK-Pendant |
|---|---|---|---|
| 0.03-013 | 14.10.2026 | Neuer Aufrufparameter `--BASP=abcdef` (sechs Bahnsperrenschalter, Vorgabe `000000`); zunächst nur der Parameter, die Wirkung (Schreibsperre) kam später über das C-Modul | – |
| 0.03-014 | 17.10.2026 | Schalter BS und Flag BS getrennt: `BS+`/`BS=1` und `BS-`/`BS=0` setzen nur die Schalterstellung (`Machine.bs_schalter`); das Flag BS wird erst durch den wirksamen bedingten Stopp 1 und durch G, ST und R wieder 0; ST wirkt nur bei US oder Flag BS. Folge: nach `BS+` ohne wirksamen bedingten Stopp steht BS=0; keine Testdatei war betroffen | – |
| **0.03-015** | 17.10.2026 | **E unter gehaltenem M:** Nach jedem E gilt `m.adr := m.AR`; die Lampenreihe AR (Adressteil des BR) zeigt das erhöhte AR. Entscheidung des Auftraggebers: die BR-Zeile im Test-Interpreter wird dem Pult angeglichen. Ändert nur Protokolltext (BR-Zeilen von 12 Protokollen: `0015-030`, `acbz-002_BZ_vorbelegt_M_E`, `asm_druck_tastenfolge`, `st-001` bis `st-005` mit `st-004_…_neu`, `tk-002`, `tk-004`, `tk-005`), **kein Testergebnis** | `c8205_grafik.py` G2-011 (ohne Bedingung `pult_modus`, damit TEST und GRAFIK dasselbe tun) |
| **0.03-016** | 18.10.2026 | **Anwahlbefehl K0 wertet den Schalter SW aus:** neuer dauerhafter Zustand `m.sw_schalter`; K0 wählt T oder SW nach der Schalterstellung im Moment der Anwahl (vorher nach dem Flag SW, das K1, K2, K3 löschen); K1, K2, K3 löschen weiter die Flags, nicht den Schalter; `tastenfolge()` führt den Schalter bei `SW=1`/`SW=0` mit. Entscheidung 18.10.2026 (Befund B-1, Checkpoint 22: bei `ziffern` bekam das SW-Fenster nie Eingabe). Neu: Programmbeispiel `Assembler/Projekt_1/sw_zwei_ziffern`, `Tests/sw_zwei_ziffern.test`. Verändert das Verhalten keines vorhandenen Testprogramms | `c8205_grafik.py` G3-003 (`Rechner.sw_gedrueckt` als Property auf `m.sw_schalter`) |
| 0.03-014 | 19.10.2026 | Stufe 6 (A6-5): Die zwei GRAFIK-PDFs (`C8205-GRAFIK_Beschreibung_A4.pdf`, `C8205-GRAFIK_Pruefverfahren_A4.pdf`) stehen in `make_all_pdf.sh` (neue Skripte `erzeuge_grafik_beschreibung_pdf.py` und `erzeuge_grafik_pruefverfahren_pdf.py`); der Satz „nicht in `make_all_pdf.sh` eingetragen“ in den zwei Quellen ist entfallen; Zeilen in `PDF.md` (4.6, Abschnitt 8), den PDF-Tabellen von `README.md`, `README.en.md` und `Projektueberblick` ergänzt. Neue Versionen: `GRAFIK_Beschreibung` 0.01-004; `GRAFIK_Pruefverfahren` 0.01-004; `PDF` 0.03-013; `README.md` 0.03-012; `README.en.md` 0.03-012; `Projektueberblick` 0.03-008. Kein Code geändert. |
| 0.03-015 | 19.10.2026 | Stufe 6 (A6-5): Projektstruktur gegen den tree-Auszug vom 19.10.2026 abgeglichen und nachgeführt (`Projektstruktur` 0.03-014): Zeilen zu `ton/` (die drei Rechnerklänge liegen im Hauptordner, `toene_rechner_stanzer/` enthält die Stanzerklänge), `pult/` (`bild/`, `grafiken/`), `c-module/` (`c8205_api.h`, `plattform.h`, `build_msvc.bat`) und `testscripte/` (`k0_schatten_haken.py`, `r300_eingabe_*`). Kein Code geändert. |
| 0.03-017 | 19.10.2026 | **Schalter `--MODUS TEST\|GRAFIK`** (Standard GRAFIK); GRAFIK übergibt die Kommandozeile an `c8205_grafik.hauptprogramm`, TEST ist das bisherige Verhalten; Testläufe brauchen `--MODUS=TEST` (Wrapper `c8205_interpreter.sh`/`.bat` setzen es); unbekannter Modus: Meldung und Code 2 | `c8205_grafik.py` |

### 10.2 Prüfung der Builds 0.03-015 und 0.03-016 (aus den Notizen übernommen, nicht neu gelaufen)

| Build | Geprüft (Linux) | Nicht geprüft |
|---|---|---|
| 0.03-015 | `compute_all_tests.sh`: alle Testdateien wie erwartet (Rückkehrcode 0 bzw. 4), Unterschied nur in den 12 Protokollen; `grafik_gleichwertigkeit.py --alle`: **191 von 191** gleich (TEST 0.03-015 gegen GRAFIK G2-011); `grafik_pult_tests.py` 55 von 55 (neue Klasse `EUnterM`, 3 Tests; `test_test_modus` schlug vor der Änderung fehl); `grafik_kern_tests` 7, `grafik_geraete_tests` 18, `grafik_checkpoint4_tests` 8, `grafik_checkpoint5_tests` 9 (1 übersprungen) | echtes Tk-Fenster; `grafik_alle_tests.sh` als Ganzes; **drei Protokolle** hängen vom Trommelzustand ab (`acbz-003_AC_Ue_E_Transport`, `bsp_5_6_vordere_bits_als_adresse`, `pj2-bis_minimalprogramm`) und wurden nicht mit dem alten Interpreter verglichen |
| 0.03-016 | `grafik_gleichwertigkeit.py --alle`: **193 von 193** gleich (192 vorhandene Tests plus `sw_zwei_ziffern.test`); `--neue-geraete`: **58 von 58**; `compute_all_tests.sh` ohne Meldung; Ende-zu-Ende 15 von 15, SW-Fenster-Logik 32 von 32. Messung mit einer Schattenkopie: alte und neue Regel entscheiden nur bei `sw_zwei_ziffern.test` verschieden (BZ=24 und BZ=109) | **kein Lauf mit dem Original 0.03-015** (die „alte Regel“ ist nachgebildet), echtes Tk-Fenster, `--HWCHECK`, PDFs |

Später (Stufe 3 bis 5) ist der Gesamtlauf `grafik_alle_tests.sh` mit 18 von 18 Blöcken bestanden (Prüfverfahren §8).

### 10.3 GRAFIK-Module (eigene Zählung, Kopfzeile `Version:`, Stand 19.10.2026)

| Modul | Version | Modul | Version |
|---|---|---|---|
| `c8205_grafik.py` | Kopf `G2-004` (veraltet), Konstante `VERSION_GRAFIK` = `G4-004` (Abschnitt 8) | `grafik_pult.py`, `grafik_pult_fenster.py` | G2-001 |
| `grafik_geraete.py` | G1-002 | `grafik_ton.py` | G2-002 |
| `grafik_geraeteton.py`, `grafik_rechnerton.py` | G4-002 | `grafik_schreibwerk.py`, `grafik_tonmisch.py` | G4-001 |
| `grafik_tonmisch_c.py` | G4-003 | `grafik_sw.py` | G4-007 |
| `grafik_sw_fenster.py` | G4-008 | `grafik_tastatur.py` | G4-010 |
| `grafik_hwcheck.py` | HW-004 | `grafik_haltzeit.py` | HZ-004 |
| `grafik_debuglog.py` | DL-003 | `grafik_fensterlage.py` | FL-001 |
| `grafik_k0.py`, `grafik_trommel.py` | keine `Version:`-Zeile | | |

Hilfsprogramme: `c8205_lochstreifen_anzeige.py` und `c8205_lochstreifen_eingabe.py` 1.9, `c8205_lochstreifen_umwandlung.py` 1.1 (eigene Programmversion, Abschnitt 2); Assembler `c82ass` 1.00.
