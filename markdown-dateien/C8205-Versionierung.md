** Versionierung (Wurzeldokument für Versionsnummern) **

Version: 0.95-049

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
| das Assemblerprogramm `c82ass` (Binary und Quellcode `Assembler/Sourcecode/ca82_version.h`) | eigene Programmversion `y.xx-zzz` (seit 1.00-010 mit Build; Stand 21.10.2026: `1.00-026`; Quelle ist die Konstante `ASM_VERSION`), s. Abschnitt 4 |
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
| `c82ass` (Programm) | Konstante in der Funktion `greetings()` in `Assembler/Sourcecode/ca82_version.h`; das Programm gibt beim Start und bei `-h` die Zeile `C8205 Assembler C82aas Version y.xx-zzz` aus. Die `.odt` und die `.md` der Assemblerdokumentation nennen dieselbe Nummer in den Beispielausgaben; die `.md` auch im Kopf (`Version: y.xx-zzz`) |

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

Version des Assemblers, so wie das Programm sie kennt (muss der Konstante in `Assembler/Sourcecode/ca82_version.h` und den Angaben der
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
- **GRAFIK-Module (Stand 21.10.2026, erledigt mit 0.95-003):** Maßgeblich ist die **Konstante `VERSION_*` im Code**; die Zeile `Version:` im Kopfkommentar trägt dieselbe Kennung (Entscheidung des Projektinhabers 21.10.2026). Beim Angleichen wurden neun Abweichungen beseitigt (`c8205_grafik.py` G2-004 → G4-004, `grafik_geraete.py` G1-002 → G4-002, `grafik_geraeteton.py` und `grafik_rechnerton.py` G4-002 → G4-004, `grafik_pult.py` G2-001 → G2-010, `grafik_pult_fenster.py` G2-001 → G4-008, `grafik_ton.py` G2-002 → G2-003, `grafik_tonmisch.py` G4-001 → G4-004, `grafik_tonmisch_c.py` G4-003 → G4-005); die Kopfzeile ist dabei keine eigene Änderung (Abschnitt 3). `grafik_k0.py` und `grafik_trommel.py` tragen neu die Kennung **G5-001** (Entscheidung des Projektinhabers 21.10.2026; frühere Stände sind im Archiv nicht belegt); sie haben nur die Kopfzeile, keine Konstante. `grafik_tastatur.py` hat ebenfalls nur die Kopfzeile (G4-010), `grafik_pult_tests.py` keine Kennung. Die Regel für die Zählung: Bei jeder Änderung eines GRAFIK-Moduls wird seine Kennung um 1 erhöht, und Kopfzeile und Konstante (soweit vorhanden) werden gemeinsam geändert; die Stufenkennung (G1 bis G5) ist die Stufe, in der die Änderung entstand. Ob jedes Modul seinen Zähler je Änderungsschritt um 1 erhöht hat, ist rückwirkend nicht prüfbar (keine Historie im Archiv).
- **`.md`-Dateien ohne Versionszeile:** Die Prüfung aus Abschnitt 6 (zweiter Befehl) meldet bei G6-017 unter den bleibenden Dateien `ton/SW_Ton_Beschreibung.md` sowie die neuen `C8205-Interpreter-GRAFIK_Beschreibung.md` und `C8205-Interpreter-GRAFIK_Pruefverfahren.md` (inzwischen nachgeführt, siehe unten). **Nachführung G6-018 (S6-08):** `ton/SW_Ton_Beschreibung.md`, `C8205-Interpreter-GRAFIK_Beschreibung.md` und `C8205-Interpreter-GRAFIK_Pruefverfahren.md` tragen jetzt `0.01-001` (Regel „neue Datei“; für `ton/SW_Ton_Beschreibung.md` setzt der Entwickler diese Nummer, solange der Projektinhaber keine andere nennt). Ihre Builds zählen ab jetzt je Änderung. Die zu löschenden Dateien (`C8205-Anforderungspaket-*.md`, `CHECKPOINT_*`, `AENDERUNG_*`, `HWCHECK_HW-003.md`) tragen meist keine; sie entfallen.
- **Builds des Interpreters:** `c8205_interp.py` hat die Builds 0.03-013 bis 0.03-017 lückenlos (je +1; Kopfzeile, Konstante `VERSION` und `--version` stimmen überein, geprüft bei G6-017). Für die `.md`-Dateien ist die Regel „je Änderungsschritt +1“ nicht prüfbar, weil das Archiv keine frühere Fassung enthält.
- **Gesamtversion (entschieden 21.10.2026):** Es gibt eine Gesamtversion, aber nur als Bezeichnung für Releases (Abschnitt 11). Sie steht im Git-Tag und in der Tabelle in Abschnitt 11, nicht in den Dateien. Maßgeblich bleiben die Nummern der einzelnen Dateien.
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
| 0.95-002 | 21.10.2026 | Durchsicht der Einstiegs- und Strukturdokumente: `README.md` und `README.en.md` (0.95-002) auf die Ordner `Hilfsprogramme/` und `testscripte/` umgestellt, Schnellstart und PDF-Tabelle berichtigt, veralteten Änderungsabschnitt gestrichen; `Projektstruktur` (0.95-003): Abschnitt 1a (Liste der Skripte in `testscripte/`) neu, Angaben zu `pdflib`, `_Windows/`, Assembler-Aufruf und Namensfamilien berichtigt, Abschnitte 5 und 6 gestrichen, `ton/aufnahmen/` (Ordner entfernt) herausgenommen; `Interpreter-PDF` (0.95-002): Zeilen für `C8205-PDF_Gestaltungsrichtlinie_A4.pdf` und `C8205-Testuebersicht_A4.pdf` in Abschnitt 4.6, `Testuebersicht` in Abschnitt 8; `GRAFIK_Beschreibung` (0.95-002): Hinweis zu den MP3-Quellen berichtigt (Ordner `ton/aufnahmen/` entfernt). Außerdem `Hilfsprogramme/c8205_befehlssweep.py` (nicht versioniert) an die Schnittstellen `Machine(trommel)` und `K0Quelle` angepasst; alle 512 Operationscodes laufen wieder durch. |
| 0.95-003 | 21.10.2026 | Offener Punkt OP-38 der `GRAFIK_Beschreibung` erledigt: Abschnitt 8 (GRAFIK-Module) und Abschnitt 10.3 nachgeführt (Konstante im Code maßgeblich; neun Kopfzeilen angeglichen; `grafik_k0.py` und `grafik_trommel.py` erhalten G5-001). `GRAFIK_Beschreibung` (0.95-003): OP-38 nach „Als erledigt belegt“ verschoben, Modulübersicht in Abschnitt 11 neu. |
| 0.95-004 | 21.10.2026 | Offener Punkt OP-18 der `GRAFIK_Beschreibung` erledigt: `Tests/sw_eingabe_leser_stanzer.test` (unfertige Ableitung, Endlosschleife) mit den Assemblerdateien und dem Protokoll entfernt. `GRAFIK_Beschreibung` (0.95-004): OP-18 nach „Als erledigt belegt“; `GRAFIK_Pruefverfahren` (0.95-002): Befund B-1 erledigt; `CSV/test_tabelle.md` (0.95-002) und `test_tabelle.csv`: Zeile des Tests entfernt (sonst nicht neu erzeugt); `Assembler/projekdetails.Projekt_1_sw_eingabe` auf `sw_eingabe_lage.asm`; `PDF/pdf-layout-scripte/build_testhandbuch.py` (nicht versioniert): Nennung im Text der Familie `sw_` gestrichen. |
| 0.95-005 | 21.10.2026 | Offener Punkt OP-34 der `GRAFIK_Beschreibung` untersucht: Verhalten bei gleichnamiger Datei im `LOCHSTREIFENKORB` gemessen (Datei im Korb wird unter Linux ohne Meldung überschrieben); als Befund mit Entscheidungsvorschlag (a) bis (c) eingetragen, Punkt bleibt offen. `GRAFIK_Beschreibung` (0.95-005). Kein Code geändert. |
| 0.95-006 | 21.10.2026 | Offener Punkt OP-32 der `GRAFIK_Beschreibung` teilweise erledigt: Testlücke der Fokus-Entprellung (0,4 s) geschlossen, drei neue Tests in `testscripte/grafik_sw_tests.py` (81 von 81 grün; Gegenprobe mit geänderter Schwelle rot). Der Teil „Fensterlage und Fokus am echten Fenster“ bleibt offen. `GRAFIK_Beschreibung` (0.95-006), `GRAFIK_Pruefverfahren` (0.95-003, Prüfungszahl in §3 berichtigt). Ausführbarer Code der Module unverändert. |
| 0.95-007 | 21.10.2026 | Offener Punkt OP-37 der `GRAFIK_Beschreibung` bearbeitet: Werte der Lampenmittelung im Code gegen §3.5 geprüft (stimmen); sechs neue Tests in `testscripte/grafik_pult_tests.py` (75 von 75 grün, fünf Gegenproben rot); Handprüfung H-12 und Handliste §7.5 im Prüfverfahren ergänzt. Punkt bleibt offen (Handprüfung und Bestätigung durch den Projektinhaber). `GRAFIK_Beschreibung` (0.95-007), `GRAFIK_Pruefverfahren` (0.95-004). Ausführbarer Code der Module unverändert. |
| 0.95-008 | 21.10.2026 | Offene Punkte OP-34 und OP-37 der `GRAFIK_Beschreibung` erledigt: OP-34 vom Projektinhaber entschieden (Variante a: gleichnamige Datei im `LOCHSTREIFENKORB` wird überschrieben), Verhalten durch neuen Test `test_gleicher_name_im_korb_wird_ueberschrieben` in `testscripte/grafik_geraete_tests.py` festgehalten (19 von 19 grün); OP-37 (Werte der Lampenmittelung) bestätigt. Beide Punkte nach „Als erledigt belegt“ (§10.5) verschoben, Kennungen §10.7 angepasst, `--leser`-Zeile in §2 ergänzt. `GRAFIK_Beschreibung` (0.95-008), `GRAFIK_Pruefverfahren` (0.95-005, H-12 nachgeführt). Ausführbarer Code der Module unverändert. |
| 0.95-009 | 21.10.2026 | Offene Punkte OP-10, OP-11 und OP-36 der `GRAFIK_Beschreibung` untersucht: OP-10 und OP-11 mit Befund (gemessen und gegen `Bedienpult_mit_Schaltern.md` und `Eingänge_der_Knoten.md` gelesen) und Entscheidungsvorschlag eingetragen, beide bleiben offen; OP-36 als nicht beschaffbar geschlossen (nach §10.5). `GRAFIK_Beschreibung` (0.95-009), `GRAFIK_Pruefverfahren` (0.95-006, H-8 nachgeführt). Kein Code geändert. |
| 0.95-010 | 21.10.2026 | Offene Punkte OP-10 und OP-11 der `GRAFIK_Beschreibung` entschieden (Projektinhaber) und umgesetzt: `E+` ohne M zeigt BZ in den AR-Lampen, G bei gehaltenem E löscht nur den Überlauf; `c8205_grafik.py` G4-005, `grafik_pult.py` G2-011, sieben neue Tests in `testscripte/grafik_pult_tests.py` (82 von 82; drei Gegenproben); Gleichwertigkeit TEST/GRAFIK 199 von 199 gleich. OP-41 neu (Fortsetzung nach G im Überlaufhalt, zur Bestätigung). `GRAFIK_Beschreibung` (0.95-010), `GRAFIK_Pruefverfahren` (0.95-007). Zwei vorbestehende Testfehler standen hier zunächst als nicht behoben, siehe 0.95-011. |
| 0.95-011 | 21.10.2026 | OP-41 vom Projektinhaber bestätigt. Die zwei vorbestehenden Testfehler behoben: `testscripte/grafik_stufe5_tests.py` prüft die Version des Interpreters jetzt gegen das Schema `y.xx-zzz` statt gegen `0.03-` (der Interpreter meldet seit 0.95-001 eine andere Unterversion); `testscripte/grafik_sw_ende_zu_ende.py`, `test_in_beiden_zeichenlagen` (SW auf GB): die Ziffer bleibt im Puffer, weil `ziffern_2` nach dem Umschaltzeichen endet und kein zweites 011 erreicht; erwartet wird jetzt `zweite == []`, Puffer `['2']`, keine Anzeige (die alte Erwartung galt vor dem Puffer, G4-009). Beide Blöcke 15 von 15 bzw. 7 von 7 grün; Gegenprobe schlägt an. `GRAFIK_Beschreibung` (0.95-011), `GRAFIK_Pruefverfahren` (0.95-008). |
| 0.95-012 | 21.10.2026 | Schritt 6 der offenen Punkte der `GRAFIK_Beschreibung`: OP-30 (b) erledigt (`ton/SW_Ton_Beschreibung.md` gegen §6, Code, WAV-Dateien und einen Lauf von `sw_ton.py` abgeglichen; Dok. 03 lag nicht vor; Teil D nachgeführt, Version 0.01-004) und OP-21 erledigt (Handbücher auf Töne durchgesehen, keine Änderung nötig). Zwei Berichtigungen in §6 (`ffplay` in der Liste der Abspielprogramme, Grundgeräusch 5,9 s). Neu: OP-42 (Klang für `WR`, zu entscheiden). `GRAFIK_Beschreibung` (0.95-012), `GRAFIK_Pruefverfahren` (0.95-009). Kein Code geändert. |
| 0.95-013 | 21.10.2026 | Offener Punkt OP-42 der `GRAFIK_Beschreibung` entschieden (Projektinhaber: für WR die erste Hälfte des WRZL-Klangs vor dem markanten Ton, 120 ms) und umgesetzt: neue Klangart `wr` in `grafik-interpreter-module/grafik_schreibwerk.py` (G4-001 → G4-002), neue Datei `ton/sw_toene/wr.wav` und Skript `ton/erzeuge_wr_klang.py`, `ton/sw_ton.py` kennt `<WR>`; fünf neue Tests in `testscripte/grafik_stufe4_tests.py` (85 von 85, Python- und C-Mischer; zwei Gegenproben rot). `GRAFIK_Beschreibung` (0.95-013): OP-42 nach „Als erledigt belegt“, §6.2, §6.9, §6.10 Nr. 6 nachgeführt, neu OP-43; `GRAFIK_Pruefverfahren` (0.95-010, Hörzeile für WR, Prüfungszahl 85); `SW_Ton_Beschreibung.md` (0.01-005); `README.md` und `README.en.md` (0.95-003); `Projektstruktur` (0.95-004). **Befund OP-43:** im Archiv liegen `c8205_grafik.py` G4-005 und `grafik_pult.py` G2-011 nur in `testscripte/`; die Pult-Tests sind damit im Archivstand rot (Näheres: Beschreibung §10.4). Die PDFs wurden nicht neu erzeugt (`make_all_pdf.sh`). |
| 0.95-014 | 21.10.2026 | Offener Punkt OP-43 der `GRAFIK_Beschreibung` erledigt (Projektinhaber: „mach was du denkst“, Empfehlung (a)): `c8205_grafik.py` (G4-005) und `grafik-interpreter-module/grafik_pult.py` (G2-011) an ihren Plätzen; lose Kopien in `testscripte/` und die ältere Pult-Testdatei im Modulordner entfernt; `test_haltzeit_einzelschritt` in `testscripte/grafik_pult_tests.py` übernommen (83 Tests, 83 von 83 grün; Sammellauf `--schnell` 16 von 16 Blöcken grün). Kein Code geändert, nur Dateien verschoben und ein Test übernommen. `GRAFIK_Beschreibung` (0.95-014): OP-43 nach „Als erledigt belegt“. Die PDFs wurden nicht neu erzeugt (`make_all_pdf.sh`). |
| 0.95-015 | 21.10.2026 | Offener Punkt OP-40 der `GRAFIK_Beschreibung` untersucht und erledigt: neues Messskript `testscripte/grafik_sw_zeit_messung.py` (ändert nichts, kein Teil des Sammellaufs). Ergebnis: Im Sammellauf wirkt die Schreibwerkzeit nicht (Tests benutzen `Rechner` ohne Schreibwerk); 33 von 199 Tests schreiben auf das Schreibwerk, 1233 Zeichen, rund 110 s berechnete Schreibwerkzeit. Kein Code und keine Tests geändert. `GRAFIK_Beschreibung` (0.95-015): OP-40 nach „Als erledigt belegt“; `GRAFIK_Pruefverfahren` (0.95-011): Zeile zum Messskript; `Projektstruktur` (0.95-005): Zeile zum Messskript. Die PDFs wurden nicht neu erzeugt (`make_all_pdf.sh`). |
| 0.95-016 | 21.10.2026 | Offener Punkt OP-39 der `GRAFIK_Beschreibung` erprobt und erledigt: H und Abbruch werden durch die Schreibwerkzeit (höchstens 400 ms je Ausgabebefehl) nicht blockiert. Vier neue Tests in `testscripte/grafik_stufe4_tests.py` (Klasse `SchreibwerkzeitUndH`; 89 von 89, Python- und C-Mischer; Gegenprobe schlägt an). Kein Code geändert. `GRAFIK_Beschreibung` (0.95-016): OP-39 nach „Als erledigt belegt“, Prüfungszahl 89; `GRAFIK_Pruefverfahren` (0.95-012): Prüfungszahl 89. Die PDFs wurden nicht neu erzeugt (`make_all_pdf.sh`). |
| 0.95-017 | 21.10.2026 | Offener Punkt OP-20 der `GRAFIK_Beschreibung` untersucht: Befund, dass die Taste E nach einem Abbruch des E-Schritts im Eingabe-Halt durch H dauerhaft wirkungslos bleibt (`e_gedrueckt` wird nicht zurückgesetzt) und dass K0 nach H weiter „wartet“ (`_wartet_auf`). Entscheidung des Projektinhabers offen (beheben oder so lassen). Neue Probe `testscripte/grafik_e_im_eingabe_halt_probe.py` (nicht Teil des Sammellaufs, ändert nichts im Projekt). Kein Code geändert. `GRAFIK_Beschreibung` (0.95-017): OP-20 neu gefasst; `Projektstruktur` (0.95-006): Zeile zur Probe. Die PDFs wurden nicht neu erzeugt (`make_all_pdf.sh`). |
| 0.95-018 | 21.10.2026 | Offener Punkt OP-20 der `GRAFIK_Beschreibung` behoben (Entscheidung des Projektinhabers „ok, mach weiter“, gelesen als Variante (a)): `c8205_grafik.py` G4-005 → G4-006 (`leerlauf` setzt nach `HUnterbrechung`/`Wiederaufsetzen` einer E-Taste `e_gedrueckt` und `e_nieder_unter_m` zurück), `grafik-interpreter-module/grafik_k0.py` G5-001 → G5-002 (`naechstes` löscht `_wartet_auf`, wenn das Warten durch eine Ausnahme verlassen wird). Acht neue Tests in `testscripte/grafik_pult_tests.py` (Klassen `K0AbbruchBeimWarten`, `EImEingabeHaltAbgebrochen`; 91 von 91, vorher 83); Gegenproben: alter Kern allein zwei, altes `grafik_k0.py` allein sechs Tests rot. Sammellauf `--schnell` 16 von 16 Blöcken grün; Gleichwertigkeitsläufe nicht gestartet. Die Probe `testscripte/grafik_e_im_eingabe_halt_probe.py` zeigt den behobenen Zustand (Kopfkommentar nachgeführt). `GRAFIK_Beschreibung` (0.95-018): OP-20 nach „Als erledigt belegt“, neu §3.8 Nr. 8; `Projektstruktur` (0.95-007). Die PDFs wurden nicht neu erzeugt (`make_all_pdf.sh`). |
| 0.95-019 | 21.10.2026 | Offener Punkt OP-19 der `GRAFIK_Beschreibung` untersucht (Prüfsumme von `Trommel/trommel.txt` vor und nach den Läufen): Sammellauf `--schnell` lässt die Datei unverändert, ein Einzeltest im Modus TEST verändert sie (gewollt), ein GRAFIK-Lauf ohne Fenster ließ sie unverändert. Entscheidung des Projektinhabers offen ((a) so lassen, (b) Wächter im Sammellauf, (c) Kopie als Vorgabe). Kein Code geändert. `GRAFIK_Beschreibung` (0.95-019): OP-19 neu gefasst. Die PDFs wurden nicht neu erzeugt (`make_all_pdf.sh`). |
| 0.95-020 | 21.10.2026 | Offener Punkt OP-19 der `GRAFIK_Beschreibung` umgesetzt (Entscheidung des Projektinhabers: Variante (b), Wächter im Sammellauf): neu `testscripte/grafik_trommel_waechter.py` und `testscripte/grafik_trommel_waechter_tests.py` (elf Tests mit Gegenproben); `testscripte/grafik_alle_tests.sh` merkt vor dem ersten Block die Prüfsummen von `Trommel/trommel.txt` und `trommel.basp` und vergleicht sie im letzten Block (jetzt 18 Blöcke mit `--schnell`, 20 voll; Sammellauf `--schnell` 18 von 18, Trommeldateien unverändert; Gegenprobe am Skript: schreibender Block macht den Wächter rot, Rückgabewert 1). Kein Programmcode des Interpreters geändert. `GRAFIK_Beschreibung` (0.95-020): OP-19 nach „Als erledigt belegt“; `GRAFIK_Pruefverfahren` (0.95-013): §3.1, §3.2 (Blöcke 19 und 20), B-2; `Projektstruktur` (0.95-008). Der volle Lauf mit den Gleichwertigkeitsläufen und die PDFs (`make_all_pdf.sh`) wurden nicht neu erzeugt. |
| 0.95-021 | 21.10.2026 | Offener Punkt OP-09 der `GRAFIK_Beschreibung` untersucht (Eingabeklang beim ersten Zeichen): Klangweg über Schreibwerk und Mischer (Python und C) ohne Fehler; Besonderheit des ersten Zeichens nach dem Einschalten ist das Paar aus Umschaltzeichen und Zeichen (Klang erst beim Loslassen). Zwei neue Tests `test_op09_*` in `testscripte/grafik_sw_tests.py` (83 von 83 grün, Gegenprobe schlägt an). Kein Programmcode geändert; Ursache nicht belegt, OP-09 bleibt offen (Gegenprobe am Fenster mit `--DEBUGLOG`). `GRAFIK_Beschreibung` (0.95-021): §6.10 Nr. 3, §10.2 OP-09; `GRAFIK_Pruefverfahren` (0.95-014): §3.1 Zeile 6 (83 Prüfungen), H-7. `Projektstruktur` unverändert (keine neue Datei). Die PDFs wurden nicht neu erzeugt. |
| 0.95-022 | 21.10.2026 | Zu OP-09: neues Skript `testscripte/op09_eingabeklang.sh` (Handprüfung H-7): lädt den Abschnitt `Trommeldatei:` von `Tests/sw_zwei_ziffern.test` (oder eines anderen Tests) auf eine frische leere Trommelkopie und startet GRAFIK mit Fenster, Ton und `--DEBUGLOG`. Geprüft an einer Kopie mit angeglichenen Umlautnamen: Vorbereitung ok, Probelauf ohne Fenster liefert die erwartete SW-Ausgabe (`Erste: 2`, `Zweite: 3`), `Trommel/trommel.txt` unverändert (gleiche Prüfsumme). **Nicht geprüft:** der Start mit Fenster und Ton (kein Tk, kein Bildschirm). `GRAFIK_Beschreibung` (0.95-022), `GRAFIK_Pruefverfahren` (0.95-015, H-7), `Projektstruktur` (0.95-009). PDFs nicht neu erzeugt. |
| 0.95-023 | 21.10.2026 | Zu OP-09: Log des Projektinhabers vom Lauf mit `op09_eingabeklang.sh` ausgewertet (erstes Zeichen: Eingabeklang 1,8 s nach dem Tastendruck angefordert, nicht verloren; Folgezeichen ohne Verzug; Zeile „beim Loslassen“ fehlt). `grafik_sw_fenster.py` G4-008 → G4-009: nur Debug-Log erweitert (`011 aktiv` je Taste, `Taste los … nichts geliefert`, `Stimmen im Mischer danach`), Verhalten unverändert. Tests: `grafik_sw_tests` 83 von 83, `grafik_stufe4_tests` 89 von 89, `grafik_sw_pult_test` grün (an einer Kopie mit angeglichenen Umlautnamen; im Archiv selbst schlägt `test_ohne_spieler_code_16` wegen der `#U00e4`-Namen fehl, OP-43). `GRAFIK_Beschreibung` (0.95-023), `GRAFIK_Pruefverfahren` (0.95-016). OP-09 bleibt offen (zweiter Lauf mit dem erweiterten Log). PDFs nicht neu erzeugt. |
| 0.95-024 | 21.10.2026 | (a) OP-09: zweiter Lauf des Projektinhabers mit `op09_eingabeklang.sh` ausgewertet (noch alte `grafik_sw_fenster.py`): Verzug des ersten Klangs 1,73 s, wiederholbar. (b) OP-13 untersucht: neue Probe `testscripte/grafik_op13_probe.py` belegt die Annahmen (1) bis (3) am GRAFIK-Kern (Halt bleibt, H und R heben ihn auf; H im Lauf nach 2 ms an der Befehlsgrenze; H im Eingabe-Halt sofort, R wiederholt den Befehl; K1 im Lauf und SW=1 im Eingabe-Halt wirken wie angenommen). Kein Programmcode geändert. `GRAFIK_Beschreibung` (0.95-024): §6.10 Nr. 3, §10.3 OP-13; `Projektstruktur` (0.95-010). OP-13 bleibt Standardannahme bis zur Bestätigung. PDFs nicht neu erzeugt. |
| 0.95-025 | 21.10.2026 | OP-09: dritter Lauf des Projektinhabers (Verzug 1,76 s) und neue Probe `testscripte/grafik_op09_rechnerzeit_probe.py`: Der Rechner gibt nach dem Umschaltzeichen die Aufforderung des Testprogramms erneut aus (1,70 s Schreibwerkzeit); der Klang des ersten Zeichens kommt erst mit der Annahme. Ursache gefunden, Verhalten nicht geändert, Entscheidung (a) so lassen / (b) Klang beim Tastendruck beim Projektinhaber. `GRAFIK_Beschreibung` (0.95-025), `GRAFIK_Pruefverfahren` (0.95-017), `Projektstruktur` (0.95-011). PDFs nicht neu erzeugt. |
| 0.95-026 | 21.10.2026 | **OP-09 entschieden und umgesetzt (Projektinhaber: Variante (b), Klang beim Tastendruck).** `grafik_sw.py` G4-007 → G4-008: neuer Aufruf `klick` an `SwEingabe`, aufgerufen in `tippen()`, sobald das Zeichen im Puffer ist; `echo` bleibt die Anzeige bei der Annahme. `grafik_sw_fenster.py` G4-009 → G4-010: `_klick_eingabe` (Klang, Schreibwerk, auch bei Selektor SW) und `_echo_eingabe` (nur Anzeige). **Dateistand bereinigt:** die Fassung G4-009 lag nur lose in `testscripte/`, im Modulordner stand noch G4-008; jetzt gilt allein die Datei im Modulordner (G4-010), die lose Kopie ist entfernt (wie bei OP-43). Tests: `grafik_sw_tests.py` 83 → 89 (sechs neue `test_op09_*`), `grafik_stufe4_tests.py` 89 → 90 (Fenstertest ersetzt und ergänzt), `grafik_sw_abstand_tests.py`: die Attrappe `Rec` kennt jetzt `erwartet` (die G4-009-Fassung des Fensters rief es im Debug-Log auf, 5 Fehler, vorher unbemerkt). Geprüft an einer Kopie mit angeglichenen Umlautnamen: `grafik_sw_tests` 89, `grafik_stufe4_tests` 90, `grafik_sw_ende_zu_ende` 15, `grafik_sw_pult_test` 5, `grafik_sw_abstand_tests` 6, `grafik_pult_tests` 91, `grafik_stufe5_tests` 7, jeweils alle grün; Gegenproben: ohne den Aufruf in `tippen()` fünf, mit dem Klang erst bei der Annahme vier der sechs neuen Tests rot. Nicht gestartet: Sammellauf, Gleichwertigkeitsläufe; `grafik_sw_vormerkung_s3_13.py` (nicht im Sammellauf) hat auch im unveränderten Archiv zwei Fehler. `GRAFIK_Beschreibung` 0.95-026 (OP-09 nach §10.5, OP-44 in §10.2, §5.5, §6.2, §6.10 Nr. 3, Register), `GRAFIK_Pruefverfahren` 0.95-018 (H-7, Prüfungszahlen). PDFs nicht neu erzeugt. |
| 0.95-027 | 21.10.2026 | Zu OP-09, Berichtigung: Die in 0.95-026 als OP-44 geführte Frage „Puffer ein Tastendruck oder acht Eingaben“ entfällt. Der Projektinhaber stellte klar, dass sich sein Satz („Puffer voll, weitere Taste geht nicht“) auf den elektronischen Ein-Zeichen-Puffer des echten C 8205 bezieht und nichts mit dem Software-Puffer zu tun hat; der Software-Puffer (8 Eingaben) bleibt. Kein Code geändert. `GRAFIK_Beschreibung` 0.95-027 (OP-44 aus §10.2 gestrichen, Klarstellung in §6.10 Nr. 3, §10.5 und Register). PDFs nicht neu erzeugt. |
| 0.95-028 | 21.10.2026 | **OP-14 bearbeitet** (Standardannahmen S3-06, S3-07, S3-15; „mach weiter“, Reihenfolge nach OP-13). Code und Tests gegengelesen: WR, TAB, nicht darstellbare Zeichen und die Vorgabelage rechts unten stehen so im Code und sind durch Tests festgehalten. Neuer Test `test_op14_benannte_zeichen_die_das_schreibwerk_wirklich_ausgibt` in `testscripte/grafik_sw_tests.py` (89 → 90 von 90, Gegenprobe schlägt an): die Rechnerausgabe kann von den in S3-07 genannten Zeichen nur Irrung Satz, ≈, ≋ und △ liefern, ZV, BM, Irrung Zeichen und Transport nicht. Kein Programmcode geändert. `GRAFIK_Beschreibung` 0.95-028 (OP-14 mit Beleg und Befund, §5.1 S3-07, Stand-Absatz: Puffer-Annahmen als bestätigt, wie schon OP-07 in §10.5), `GRAFIK_Pruefverfahren` 0.95-019 (Prüfungszahl). Bestätigung des Projektinhabers zu OP-14 steht aus, ebenso zu OP-13. PDFs nicht neu erzeugt. |
| 0.95-029 | 21.10.2026 | OP-14 vom Projektinhaber bestätigt („OP-14 ja“). `GRAFIK_Beschreibung` 0.95-029: OP-14 aus §10.3 nach §10.5 verschoben, die Vermerke „Standardannahme, ohne Einzelbestätigung“ zu S3-06, S3-07 und S3-15 in §5.1 und im Stand-Absatz auf „bestätigt“ gesetzt, Zuordnung S3-06/07/15 auf §10.5. Kein Code, keine Tests geändert. OP-13 bleibt offen. PDFs nicht neu erzeugt. |
| 0.95-030 bis 0.95-033 | 21.10.2026 | **Nachtrag, Einzelheiten nicht überliefert.** `GRAFIK_Beschreibung` trug im Archiv `projekt_C8205.zip` schon die Nummer 0.95-033, während dieses Protokoll bei 0.95-029 endete; die vier Änderungsschritte dazwischen wurden hier nicht eingetragen. Aus dem Inhalt der Beschreibung ablesbar (nicht aus einer Historie): OP-13 bestätigt (Projektinhaber: „OP-13 alle ja“) und nach §10.5 verschoben; OP-15 (HW-Check, Annahmen b, c, d, f) bestätigt, mit neuem Test `test_op15_anzeige_vor_dem_einschalten` (`grafik_pult_tests.py`, 92 von 92). Welche Nummer zu welchem Schritt gehört, lässt sich nicht sagen. |
| 0.95-034 | 21.10.2026 | **OP-13 abgeschlossen im Code und in der Beschreibung.** `c8205_grafik.py` G4-006 → G4-007: Kopfkommentar nennt die Standardannahmen (1) bis (3) als bestätigt (vorher „nicht ausdrücklich bestätigt“); nur Kommentar, kein Verhalten. `GRAFIK_Beschreibung` 0.95-034: der Hinweis im OP-13-Eintrag (§10.5), der Kommentar sei noch nicht geändert, ist berichtigt. Dieses Protokoll nachgetragen (0.95-030 bis -033) und auf 0.95-034 gebracht. PDFs nicht neu erzeugt. |
| 0.95-035 | 21.10.2026 | **OP-16, Teil 1 (M-28) umgesetzt (Projektinhaber: „ja“).** `grafik_pult_fenster.py` G4-008 → G4-009: gehaltene Computertasten wiederholen im Pult-Fenster nicht (Merken je `keysym`, Wiederholung als Paar Loslassen/Drücken unter 0,03 s erkannt, Freigabe beim Fokusverlust). `testscripte/grafik_pult_tests.py`: fünf neue Tests `test_m28_*` in `Op16Maus` (99 → 104 von 104, an einer Kopie mit angeglichenen Umlautnamen); Gegenprobe (Sperre abgeschaltet) macht zwei Tests rot. `GRAFIK_Beschreibung` 0.95-035 (§4.5, OP-16 in §10.3). M-16 (Nachleuchten von M) bleibt offen. Nicht geprüft: Verhalten am echten Fenster. PDFs nicht neu erzeugt. |
| 0.95-036 | 21.10.2026 | **OP-16, Teil 2 (M-16) umgesetzt (Projektinhaber: „das Weiterleuchten entfernen, also der Beschreibung folgen“).** `grafik_pult.py` G2-011 → G2-012: `loslassen` ruft für M kein `_blinken` mehr auf; M gilt wie E sofort als losgelassen. `testscripte/grafik_pult_tests.py`: neuer Test `test_m16_m_leuchtet_nach_dem_loslassen_nicht_weiter` (104 → 105 von 105, an einer Kopie mit angeglichenen Umlautnamen); Gegenprobe macht ihn rot. `GRAFIK_Beschreibung` 0.95-036 (§4.3, OP-16 in §10.3). Nicht geprüft: Verhalten am echten Fenster. PDFs nicht neu erzeugt. |
| 0.95-037 | 21.10.2026 | **OP-31 bestätigt (Projektinhaber: „OP-31 alles JA“).** Kein Programmcode geändert. `testscripte/grafik_sw_tests.py`: neuer Test `test_op31_kein_klang_bei_ruecktaste` (90 → 91 von 91, an einer Kopie mit angeglichenen Umlautnamen); Gegenprobe (Klang in `ruecktaste()`) macht ihn rot. `GRAFIK_Beschreibung` 0.95-037: OP-31 aus §10.3 nach §10.5 verschoben, Vermerk in §5.6, Zuordnung in §10.7. PDFs nicht neu erzeugt. |
| 0.95-038 | 21.10.2026 | **OP-35 (a) bestätigt (Projektinhaber: „OP-35 nein, das ist so richtig“, mit Erläuterung).** Kein Programmcode geändert. `testscripte/grafik_pult_tests.py`: neuer Test `test_op35a_kanal_per_befehl_aendert_die_rastung_nicht` (105 → 106 von 106, an einer Kopie mit angeglichenen Umlautnamen); Gegenprobe macht ihn und `test_kanaltasten_genau_eine_rastet` rot. `GRAFIK_Beschreibung` 0.95-038: Satz in §4.1 auf „bestätigt“ mit Wortlaut, OP-35 in §10.3 auf (b) gekürzt, (a) nach §10.5, Zuordnung in §10.7. (b) bleibt offen. PDFs nicht neu erzeugt. |
| 0.95-039 | 21.10.2026 | **OP-35 (b) bestätigt (Projektinhaber: „ja, wirkt sofort“); OP-35 damit abgeschlossen.** Kein Programmcode geändert. `testscripte/grafik_pult_tests.py`: neuer Test `test_op35b_r_wirkt_sofort_nach_kurzem_klick_auf_m` (106 → 107 von 107, an einer Kopie mit angeglichenen Umlautnamen); Gegenprobe macht sechs Tests rot. `GRAFIK_Beschreibung` 0.95-039: OP-35 aus §10.3 nach §10.5 verschoben, Vermerk in §4.1, Zuordnung in §10.7. PDFs nicht neu erzeugt. |
| 0.95-040 | 21.10.2026 | **OP-17 bestätigt (Projektinhaber: „OP-17 ja“).** Kein Programmcode, keine Tests geändert. `GRAFIK_Beschreibung` 0.95-040: OP-17 aus §10.3 nach §10.5 verschoben, mit dem Vermerk, dass die 50 ms eine Entwurfsangabe sind und bei laufender Schreibwerkzeit bis 400 ms dauern können (OP-39); Zuordnung in §10.7. PDFs nicht neu erzeugt. |
| 0.95-041 | 21.10.2026 | **OP-30 (a) verglichen (Projektinhaber: „ja vergleiche“).** Kein Programmcode, keine Tests geändert. `grafik_gleichwertigkeit.py` mit `acbz-003_AC_Ue_E_Transport`, `bsp_5_6_vordere_bits_als_adresse` und `pj2-bis_minimalprogramm`, dreimal: je GLEICH (TEST gegen GRAFIK); `Trommel/trommel.txt` und `trommel.basp` unverändert. Grenze: kein alter Interpreter zum Vergleich, andere Trommelstände nicht probiert. `GRAFIK_Beschreibung` 0.95-041 (OP-30 (a) in §10.4). OP-30 (c) bleibt offen. PDFs nicht neu erzeugt. |
| 0.95-042 | 21.10.2026 | **OP-30 (c) als nicht beschaffbar geschlossen (Projektinhaber).** Kein Programmcode, keine Tests geändert. `GRAFIK_Beschreibung` 0.95-042 (OP-30 in §10.4). Damit ist OP-30 insgesamt erledigt und von §10.4 nach §10.5 verschoben, Zuordnung in §10.7. PDFs nicht neu erzeugt. |
| 0.95-043 | 21.10.2026 | **OP-44 (neu): `LayoutError` bei der PDF-Erzeugung der `GRAFIK_Beschreibung` behoben (Projektinhaber: „los gehts“).** Kein Programmcode des Interpreters, keine Tests geändert. Ursache: `NOSPLIT` auf den letzten beiden Tabellenzeilen in `table_block` (`md2pdf.py`); die Zeilen OP-20 und OP-19 in §10.5 sind zusammen höher als die Satzfläche. Änderung: `NOSPLIT` nur, wenn Kopfzeile und die zwei letzten Zeilen höchstens 80 % der Satzfläche brauchen. Geändert (Skripte, nicht versioniert): `PDF/pdf-layout-scripte/md2pdf.py`, `erzeuge_grafik_beschreibung_pdf.py`, `erzeuge_grafik_pruefverfahren_pdf.py`. Beide GRAFIK-Erzeuger laufen an den aktuellen Quellen ohne Fehler; `make_all_pdf.sh` als Ganzes nicht gelaufen. `GRAFIK_Beschreibung` 0.95-043 (OP-44 in §10.5, §10.7). `C8205-GRAFIK_Beschreibung_A4.pdf` neu erzeugt (Stand 21.10.2026, 69 Seiten); alle übrigen PDFs weiterhin nicht neu erzeugt. |
| 0.95-044 | 21.10.2026 | **OP-45 (neu): Bezeichnung ZV/ZL in den Kodetabellen angeglichen (Projektinhaber: „ja, mache deinen Vorschlag“); Rest von OP-23 gestrichen („entferne“).** Kein Programmcode, keine Tests geändert. `Kodetabellen` 0.95-001 → 0.95-002 (nur Text an drei Stellen: Abkürzungszeile unter Tabelle 1, Absatz „ZV und BM“ in 1.4, Lesehilfe zu Tabelle 2; keine Tabellenzelle geändert). `GRAFIK_Beschreibung` 0.95-044 (OP-45 in §10.5, OP-14 und OP-23 nachgeführt, §10.7). `C8205-Kodetabellen_A4.pdf` (10 Seiten) und `C8205-GRAFIK_Beschreibung_A4.pdf` neu erzeugt (Stand 21.10.2026); alle übrigen PDFs weiterhin nicht neu erzeugt. |
| 0.95-045 | 21.10.2026 | **OP-46 (neu): Code im Archiv hinter der Dokumentation zurückgeführt (Schritt 1 der Abarbeitung, Projektinhaber: „los gehts“).** Befund: Das Archiv `projekt_C8205.zip` enthielt `grafik_pult_fenster.py` noch mit G4-008 und `grafik_pult.py` mit G2-011, obwohl Versionierung (0.95-035, 0.95-036) und `GRAFIK_Beschreibung` (§4.3, §4.5) G4-009 und G2-012 als umgesetzt führen; die Tests dazu (`test_m28_*`, `test_m16_m_leuchtet_*`) waren im Archiv, vier davon schlugen an. **Änderung:** `grafik_pult.py` G2-011 → G2-012 (`loslassen` ruft für M kein `_blinken` mehr auf); `grafik_pult_fenster.py` G4-008 → G4-009 (Sperre für gehaltene Computertasten: Merken je `keysym`, Paar Loslassen/Drücken unter 0,03 s gilt als Wiederholung, Freigabe beim Fokusverlust über `_fokus_aus`). **Ehrlicher Vorbehalt:** Die ursprüngliche Fassung G4-009 lag nicht vor; die Sperre ist nach der Beschreibung (§4.5) und den Tests neu geschrieben, Einzelheiten können vom verlorenen Original abweichen. **Belegt:** `testscripte/grafik_pult_tests.py` 107 von 107 grün (vorher 3 Fehlschläge, 1 Fehler), an einer Kopie mit angeglichenen Umlautnamen. **Nicht geprüft:** Verhalten am echten Tk-Fenster; Sammellauf `grafik_alle_tests.sh`. `GRAFIK_Beschreibung` 0.95-045 (OP-46 in §10.5). PDFs nicht neu erzeugt. |
| 0.95-046 | 21.10.2026 | **OP-47 (neu): Pult-Tasten über die Buchstabentasten des Rechners (Schritt 2 der Abarbeitung).** H, R, E, G, M, T, S sowie Umschalt+E und Umschalt+M wirken wie die Pult-Tasten, mit allen Sperren (Anforderung des Projektinhabers: nur wenn die Taste klickbar wäre). `grafik_pult.py` G2-012 → G2-013 (`TASTATUR_PULT`, `tastatur(…, umschalt)`, `tastatur_los`); `grafik_pult_fenster.py` G4-009 → G4-010 (Umschalt, Strg/Alt ignoriert, Loslassen von E und M, Haltesperre ohne Unterschied der Schreibweise). `testscripte/grafik_pult_tests.py`: neue Klasse `Op47Buchstaben` (17 Tests), alter Test `test_computertastatur` auf `q` umgestellt; 124 von 124 grün; Gegenproben (12 und 5 Tests rot); `grafik_alle_tests.sh --schnell` 18 von 18 Blöcken (Kopie mit angeglichenen Umlautnamen). `GRAFIK_Beschreibung` 0.95-046 (§4.5, OP-47 in §10.5, **neu OP-48 offen:** Vorrang der SW-Eingabe bei Kanal SW). Nicht geprüft: Verhalten am echten Tk-Fenster. PDFs nicht neu erzeugt. |
| 0.95-047 | 21.10.2026 | **Gesamtversion für Releases eingeführt (Projektinhaber); in einer parallelen Sitzung als 0.95-043 vergeben, hier mit der nächsten freien Nummer 0.95-047 eingeordnet (Zusammenführung 21.10.2026).** Abschnitt 8 (Punkt „Gesamtversion“) und neuer Abschnitt 11 (Regeln und Tabelle der Releases, erster Eintrag `v0.95.1`). Angaben zum Assembler berichtigt: Programmversion hat seit 1.00-010 einen Build (Abschnitt 2, 4, 10.3), Stand `1.00-026`. `Projektstruktur` 0.95-013 (Assembler-Abschnitt nachgeführt). Kein Programmcode geändert. |
| 0.95-048 | 21.10.2026 | **OP-48 behoben (Rückmeldung des Projektinhabers: nach `S` wirkte `R` nicht, es klang wie SW-Eingabe).** Bei angewähltem Kanal SW hat eine Pult-Buchstabentaste am Pult-Fenster jetzt Vorrang, wenn sie als Pult-Taste wirken würde und das SW keine Eingabe erwartet (kein 011, Puffer leer); sonst bleibt sie SW-Eingabe. `grafik_pult.py` G2-013 → G2-014 (neu `taste_klickbar`, reine Prüfung); `grafik_pult_fenster.py` G4-010 → G4-011 (`_pult_vorrang`, Loslassen und Wiederholung gehaltener Pult-Tasten gehen nicht an das SW). `grafik_pult_tests.py`: neun Tests `test_op48_*` (124 → 133 von 133); Gegenprobe macht fünf rot; `grafik_alle_tests.sh --schnell` 18 von 18 (Kopie mit angeglichenen Umlautnamen). `GRAFIK_Beschreibung` 0.95-047 (§4.5, OP-48 nach §10.5). Nebenwirkung: ein `h` zwischen zwei Eingabeaufforderungen im Lauf hält an. Nicht geprüft: Verhalten am echten Tk-Fenster. PDFs nicht neu erzeugt. |
| 0.95-049 | 21.10.2026 | **Klarstellung zu OP-47 (Projektinhaber): „E gedrückt halten“ bedeutet Umschalt+E (ebenso M), nicht den Finger auf `e` lassen.** Nur Text: `GRAFIK_Beschreibung` 0.95-048 (neuer Absatz in §4.5 mit Gegenüberstellung Maus und Tastatur, Verweis in §4.3, Halte-Regel M-21). Kein Programmcode, keine Tests geändert. PDFs nicht neu erzeugt. |


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

### 10.3 GRAFIK-Module (eigene Zählung, Kopfzeile `Version:`, Stand 21.10.2026)

| Modul | Version | Modul | Version |
|---|---|---|---|
| `c8205_grafik.py` | G4-007 (Kopf und `VERSION_GRAFIK`; neu 21.10.2026, OP-13, nur Kommentar) | `grafik_pult.py` | G2-014 (neu 21.10.2026, OP-48; davor G2-013 OP-47, G2-012 OP-16 / M-16) |
| `grafik_pult_fenster.py` | G4-011 (neu 21.10.2026, OP-48; davor G4-010 OP-47, G4-009 OP-16 / M-28) | `grafik_ton.py` | G2-003 |
| `grafik_geraete.py` | G4-002 | `grafik_geraeteton.py`, `grafik_rechnerton.py` | G4-004 |
| `grafik_schreibwerk.py` | G4-002 (neu 21.10.2026, Klang für WR, OP-42) | `grafik_tonmisch.py` | G4-004 |
| `grafik_tonmisch_c.py` | G4-005 | `grafik_sw.py` | G4-008 (neu 21.10.2026, OP-09) |
| `grafik_sw_fenster.py` | G4-010 (neu 21.10.2026, OP-09) | `grafik_tastatur.py` | G4-010 (nur Kopfzeile) |
| `grafik_hwcheck.py` | HW-004 | `grafik_haltzeit.py` | HZ-004 |
| `grafik_debuglog.py` | DL-003 | `grafik_fensterlage.py` | FL-001 |
| `grafik_k0.py` | G5-002 (neu 21.10.2026, OP-20, nur Kopfzeile) | `grafik_trommel.py` | G5-001 (nur Kopfzeile) |
| `grafik_pult_tests.py` | keine Kennung (Prüfmodul) | | |

Hilfsprogramme: `c8205_lochstreifen_anzeige.py` und `c8205_lochstreifen_eingabe.py` 1.9, `c8205_lochstreifen_umwandlung.py` 1.1 (eigene Programmversion, Abschnitt 2); Assembler `c82ass` 1.00-026 (Stand 21.10.2026).


## 11. Releases (Gesamtversion)

Eine **Gesamtversion** bezeichnet einen Stand des ganzen Projekts bei einem Release auf GitHub. Sie ist nur ein Etikett:

- Form `V.M.P` (z. B. `0.95.1`), als Git-Tag mit vorangestelltem `v` (`v0.95.1`). `V.M` entspricht Hauptversion und Unterversion der Dateien (Abschnitt 1); `P` zählt die Releases innerhalb dieser Unterversion und beginnt bei 1.
- Jedes Release erhöht `P` um 1. `V` und `M` ändern sich nur, wenn der Projektinhaber die Haupt- oder Unterversion der Dateien ausdrücklich erhöht; dann beginnt `P` wieder bei 1.
- Die Gesamtversion steht **nur** im Git-Tag, im Titel des Releases und in der Tabelle unten, nicht in den Dateien selbst. Dadurch gibt es nichts zu synchronisieren, und die Dateinummern (Abschnitte 1 bis 3) bleiben unverändert maßgeblich.
- Mit jedem Release wird hier eine Zeile ergänzt: Tag, Datum und die Nummern der Dateien, die für das Release wichtig sind.

| Gesamtversion | Datum | Enthaltene Stände | Bemerkung |
|---|---|---|---|
| `v0.95.1` | 21.10.2026 | Interpreter `c8205_interp.py` 0.95-001; Assembler `c82ass` 1.00-026; Assemblerdokumentation `.md` 1.00-026 (die `.odt` und das PDF sind nicht nachgeführt); `Projektstruktur` 0.95-013; `Versionierung` 0.95-043 | erstes Release mit Gesamtversion; `_Windows/` enthält noch kein Binary |
