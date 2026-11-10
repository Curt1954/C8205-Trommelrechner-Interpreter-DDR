** Versionierung (Wurzeldokument für Versionsnummern) **

Version: 0.97-012

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
| `c82ass` (Programm) | Konstante `ASM_VERSION` in `Assembler/Sourcecode/ca82_version.h` (einzige maßgebliche Stelle; `greetings()` in `ca82_berichte.c` gibt sie aus); das Programm gibt beim Start und bei `-h` die Zeile `C8205 Assembler C82aas Version y.xx-zzz` aus. Dieselbe Nummer steht an weiteren Stellen (Quelltext-Kopfzeilen, `.odt`, `.md`, Regressionstest): vollständige Liste unter der Tabelle |

- Dateinamen und Titelzeilen tragen die Nummer nicht (Dateinamen stehen in vielen Verweisen).
- **Abfrage beim Interpreter:** `python3 c8205_interp.py --version` gibt `c8205_interp.py y.xx-zzz` aus und endet mit
  Rückkehrcode 0, ohne einen Test auszuführen. Die Wrapper `c8205_interpreter.sh` und `.bat` sind für Testläufe gedacht
  (Testdatei als erstes Argument); die Version wird direkt mit `python3` abgefragt.
- Die Ausgaben und Protokolle des Interpreters nennen die Version nicht (s. Abschnitt 8).

**Assemblerstand: alle Stellen einer Hochzählung (Handliste).** Stand `c82ass` 1.03-009, am 10.11.2026 mit `Assembler/version_abgleich.sh` gegen Zip 0.96.1-071 und `Regressionstest.zip` abgeglichen (ermittelt am 06.11.2026 mit `grep` bei 1.01-029, seither ohne neue Stelle in der Liste). Zusätzlich nennen `C8205_Standardmakros_c82ass.md` (Kopfzeile „Stand“ und Absatz „Version der Makrodatei“) und Abschnitt 5.6 der Assemblerdokumentation („Stand …“) den Assemblerstand; sie werden von Hand nachgezogen, `version_abgleich.sh` prüft sie nicht. Wird `ASM_VERSION` hochgezählt, müssen alle Zeilen der Liste nachgezogen werden. Vergisst man eine, meldet das nur `Assembler/version_abgleich.sh` (siehe unter der Tabelle) oder ein späterer Leser; so fehlten in einer früheren Lieferung die drei Versionstexte in der `.odt` (`aufgabe`, Checkpoint 9: Lieferung 008 überholt, Lieferung 009 richtig).

| Ort | Stelle | Wert |
|---|---|---|
| `Assembler/Sourcecode/ca82_version.h` | `#define ASM_VERSION` | neue Nummer |
| jede **geänderte** `.c`/`.h` in `Assembler/Sourcecode/`, die in der ersten Zeile eine Nummer trägt (`Version y.xx-zzz (siehe ca82_version.h)`; derzeit `ca82_berichte`, `ca82_fluss`, `ca82_makros`, `ca82_standards`, `ca82_symbole`, `ca82_typen` und einzelne zugehörige `.h`) | Kopfzeile | neue Nummer; ungeänderte Dateien behalten ihre ältere Nummer; Dateien ohne Nummer in der Kopfzeile (z. B. `ca82_main.c`, `ca82_opsym.c`, `ca82_quelle.c`) bleiben so |
| `Assembler/Dokumentation/C8205_Assembler_Dokumentation.odt` (`content.xml`, maßgeblich) | Titelzeile `Cross-Assembler für C8205 / C8205Z Version …` | eigener Build der `.odt`, +1 |
| dieselbe `.odt` | die drei Texte „C8205 Assembler C82aas Version …“: Usage-Beispiel, Satz zu `--version`, Beispielausgabe | neue Nummer von `ASM_VERSION` |
| `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md` | Zeile `Version:` im Kopf | eigener Build der `.md`, +1 |
| dieselbe `.md` | Kopfsatz „Textableitung … in der Version …“ und Titelzeile `# Cross-Assembler für C8205 / C8205Z – Version …` | Nummer der `.odt`-Titelzeile |
| dieselbe `.md` | die drei Texte „C82aas Version …“ (ein Änderungsprotokoll gibt es seit 1.03-011 nicht mehr) | Nummern von `.odt`, `.md` und `ASM_VERSION` |
| `Assembler/Regressionstest/negativ/version.erwartet` und `pass0_version.erwartet` (nur im `Regressionstest.zip`) | Zeile `stdout C8205 Assembler C82aas Version` | **ohne Nummer** (seit Checkpoint 31): bei einer Hochzählung ist hier nichts nachzuziehen, und die beiden Negativtests melden vor dem Bau des Binarys keine Abweichung mehr; die Nummer prüft `version_abgleich.sh` |
| `Assembler/Regressionstest/LIESMICH.md` (nur im `Regressionstest.zip`) | Zeile `Version:` und ein neuer Eintrag | eigener Build, +1 |
| `Assembler/_Linux/c82ass` (Binary) | wird nicht geliefert | der Inhaber baut es aus dem Quelltext |

Zum Abhaken, nachdem alles nachgezogen ist: `bash Assembler/version_abgleich.sh` (von überall; je Stelle eine Zeile OK, HINWEIS oder ABWEICHUNG, Rückgabecode 0 = alles in Ordnung, 1 = Abweichung, 2 = Aufruf falsch oder Datei fehlt; nur lesend). Es liest `ASM_VERSION` und prüft die Quelltext-Kopfzeilen (keine Nummer neuer als `ASM_VERSION`), in der `.odt` die Titelzeile und die drei Texte, in der `.md` die Zeile `Version:`, Kopfsatz, Titelzeile, die drei Texte, im Regressionstest die beiden Erwartungsdateien und `LIESMICH.md` (aus `Assembler/Regressionstest/`, sonst aus `Regressionstest.zip` im Projektstamm; `--regr <Pfad>` nennt einen anderen Ort). Mit `--binary` prüft es zusätzlich `c82ass --version` (bis der Inhaber das Binary gebaut hat, ist diese Abweichung erwartet), mit `-v` zeigt es jede Kopfzeile. Nicht entscheidbar ohne Vergleichsstand: ob eine geänderte Quelltext-Datei ihre Kopfzeile bekommen hat; dafür gibt es nur den HINWEIS, wenn keine Kopfzeile die aktuelle Nummer trägt. Von Hand dasselbe (Projektstamm; zeigt alle Fundstellen im Quelltext und in der `.md` sowie die drei Texte der `.odt`):

```
V=$(sed -n 's/.*ASM_VERSION "\(.*\)".*/\1/p' Assembler/Sourcecode/ca82_version.h)
grep -rn "$V" Assembler/Sourcecode Assembler/Dokumentation/C8205_Assembler_Dokumentation.md | cut -c1-105
unzip -p Assembler/Dokumentation/C8205_Assembler_Dokumentation.odt content.xml | grep -o "C82aas Version [0-9.]*-[0-9]*"
```


## 5. Ausgangsstand

Am 09.10.2026 wurde die Versionierung eingeführt. Alle `.md`-Dateien des Projektarchivs `projekt_c8205.zip` (einschließlich
dieser Datei) und `c8205_interp.py` erhielten die Nummer **0.03-001**; der Wert wurde vom Projektinhaber festgelegt. Zum
Ausgangsstand gehören auch die zugehörigen Anpassungen: der Schalter `--version`, die Verweise auf dieses Dokument
(`C8205-Projektstruktur.md`, `C8205-Interpreter-Projektueberblick.md`, `C8205-Interpreter-Überblick_und_Gesamtaufbau.md`,
`C8205-Interpreter-Python_Interpreter.md`, `README.md`, `README.en.md`) und die Aufnahme dieser Datei in die Liste der
Dateien, die der Claude-Interpreter nicht braucht (`C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 1b.1). Sie erhöhen
keine Nummer. Ab dem nächsten Änderungsschritt gelten die Regeln aus Abschnitt 3. Die Unterversion wurde am 20.10.2026 auf Aufforderung des Projektinhabers auf 0.95 und am 27.10.2026 auf Aufforderung des Projektinhabers auf 0.97 gesetzt (Build danach wieder ab 001); der Ausgangsstand 0.03-001 bleibt als Geschichte stehen.


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
  Projektinhabers). Jede der beiden Dateien zählt ihren Build selbst (Abschnitt 3); die `.md` nennt im Kopf die Version
  der `.odt`, von der sie abgeleitet ist. Das PDF trägt keine eigene Nummer; sein Deckblatt nennt wie bei allen PDFs die Version der `.md`, aus der es erzeugt wird.
- **GRAFIK-Module:** Maßgeblich ist die **Konstante `VERSION_*` im Code**; die Zeile `Version:` im Kopfkommentar trägt dieselbe Kennung (Entscheidung des Projektinhabers 21.10.2026). `grafik_k0.py` und `grafik_trommel.py` tragen neu die Kennung **G5-001** (Entscheidung des Projektinhabers 21.10.2026; frühere Stände sind im Archiv nicht belegt); sie haben nur die Kopfzeile, keine Konstante. `grafik_tastatur.py` hat ebenfalls nur die Kopfzeile (G4-010), `grafik_pult_tests.py` keine Kennung. Die Regel für die Zählung: Bei jeder Änderung eines GRAFIK-Moduls wird seine Kennung um 1 erhöht, und Kopfzeile und Konstante (soweit vorhanden) werden gemeinsam geändert; die Stufenkennung (G1 bis G5) ist die Stufe, in der die Änderung entstand. Ob jedes Modul seinen Zähler je Änderungsschritt um 1 erhöht hat, ist rückwirkend nicht prüfbar (keine Historie im Archiv).
- **`.md`-Dateien ohne Versionszeile:** Die Prüfung aus Abschnitt 6 (zweiter Befehl) meldet bei G6-017 unter den bleibenden Dateien `ton/SW_Ton_Beschreibung.md` sowie die neuen `C8205-Interpreter-GRAFIK_Beschreibung.md` und `C8205-Interpreter-GRAFIK_Pruefverfahren.md` (inzwischen nachgeführt, siehe unten). **Nachführung G6-018 (S6-08):** `ton/SW_Ton_Beschreibung.md`, `C8205-Interpreter-GRAFIK_Beschreibung.md` und `C8205-Interpreter-GRAFIK_Pruefverfahren.md` tragen jetzt `0.01-001` (Regel „neue Datei“; für `ton/SW_Ton_Beschreibung.md` setzt der Entwickler diese Nummer, solange der Projektinhaber keine andere nennt). Ihre Builds zählen ab jetzt je Änderung. Die zu löschenden Dateien (`C8205-Anforderungspaket-*.md`, `CHECKPOINT_*`, `AENDERUNG_*`, `HWCHECK_HW-003.md`) tragen meist keine; sie entfallen.
- **Builds des Interpreters:** `c8205_interp.py` hat die Builds 0.03-013 bis 0.03-017 lückenlos (je +1; Kopfzeile, Konstante `VERSION` und `--version` stimmen überein, geprüft bei G6-017). Für die `.md`-Dateien ist die Regel „je Änderungsschritt +1“ nicht prüfbar, weil das Archiv keine frühere Fassung enthält.
- **Gesamtversion (entschieden 21.10.2026):** Es gibt eine Gesamtversion, aber nur als Bezeichnung für Releases (Abschnitt 11). Sie steht im Git-Tag und in der Tabelle in Abschnitt 11, nicht in den Dateien. Maßgeblich bleiben die Nummern der einzelnen Dateien.
- **BAZ-Wirkungstabelle:** `baz-wirkungstabelle.md` gilt laut ihrem Kopf nur, solange sich die zugrunde liegenden Dokumente
  nicht ändern. Mit Versionsnummern ließe sich festhalten, für welche Nummern von `Eingänge_der_Knoten`,
  `Beschreibung_der_Knoten` und `Befehlsliste` sie gilt. Nicht umgesetzt.
- **Protokolle:** Die Protokolle des Interpreters nennen dessen Version nicht. Ob sie es sollen, ist nicht entschieden.
- **Abgleich des Assemblerstands (umgesetzt 06.11.2026, Checkpoint 31):** Das Skript `Assembler/version_abgleich.sh` prüft alle Stellen der Handliste in Abschnitt 4 gegen `ASM_VERSION` (Aufruf und Umfang dort). Die Erwartungsdateien `version.erwartet` und `pass0_version.erwartet` enthalten keine Nummer mehr (Variante A, vom Inhaber dem Bearbeiter überlassen: „entscheide selbst“): ein Platzhalter, den `regressionstest.sh` aus `ca82_version.h` einsetzt, hätte die Abweichung vor dem Bau des Binarys nicht beseitigt, und `regressionstest.sh` bleibt unverändert. Der Vergleich Nummer gegen Quelltext liegt allein in `version_abgleich.sh`. Nicht geprüft: Windows (das Skript ist nur für die Claude-Sitzung und Linux gedacht).


## 10. Versionsstand der GRAFIK-Module

Eigene Zählung je Modul (Abschnitt 2), Kopfzeile `Version:`, Stand 21.10.2026.

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
| `v0.95.6` | 23.10.2026 | Interpreter `c8205_interp.py` 0.95-002; Assembler `c82ass` 1.00-034; Assemblerdokumentation `.odt` und `.md` 1.00-033 (das PDF ist nicht nachgeführt); `Projektstruktur` 0.95-017; `Regressionstest/LIESMICH.md` 1.00-034; `Versionierung` 0.95-081 | Etikett auf Anweisung des Projektinhabers von 0.95.1 auf 0.95.6 angehoben; die Zwischenstände 0.95.2 bis 0.95.5 stehen nicht in dieser Tabelle |

## 12. Zip packen und Programmierhandbuch pflegen

**Zip packen:** `./c8205_zip_packen.sh` im Projektstamm. Es bildet den Namen `C8205 Simulator V.M.P.zip` aus der Release-Tabelle (Abschnitt 11) und packt vorher `Test-Protokolle/` nach `Test-Protokolle.zip` und `Assembler/Regressionstest/` nach `Regressionstest.zip`. Beide Ordner selbst kommen nicht ins Gesamt-Zip, die Sub-Zips schon. Mit Parameter (`./c8205_zip_packen.sh 0.95.5`) gilt die genannte Version. Mit `--claude` (`./c8205_zip_packen.sh --claude`, auch mit Version) entsteht stattdessen `C8205 Simulator V.M.P Claude.zip`: ohne PDFs, die Testtabelle `Testausfuehrungen/test_tabelle*`, `pult/`, `ton/`, `virtuelle_Geraete/`, `README.en.md`, `Test-Protokolle.zip` und die vom Assembler erzeugten `.log .mqo .obj .sym`. Für Arbeiten am GRAFIK-Fenster oder an den Klängen taugt nur das Gesamt-Zip.

**Programmierhandbuch pflegen:** `CLAUDE.md` (die Karte), `C8205-Programmierhandbuch_fuer_Claude.md` und die beiden Anhänge in `markdown-dateien/` sind versionierte `.md`-Dateien (Abschnitt 2); jede Änderung erhöht ihren Build (Abschnitt 3). Quellverweise in diesen Texten: Dateiname plus Überschrift, ohne Gliederungsnummern der Quelle. Schnellstart, Rückgabecodes, Fallen und Arbeitsregeln stehen nur in der Karte, Erklärungen nur im Handbuch; die Karte bleibt kurz (Richtwert: höchstens etwa 100 Zeilen). Die Wortzahlen in der Lesetabelle der Karte („Welche Aufgabe, was lesen?“) gelten für die dort genannte Handbuchversion; ändert sich die Länge eines Abschnitts spürbar, nachzählen (Wörter je Abschnitt einschließlich Überschrift): `awk '/^##+ /{if(n)print w,n;n=$0;w=NF;next}{w+=NF}END{print w,n}' C8205-Programmierhandbuch_fuer_Claude.md`.

**Start einer Claude-Sitzung:** Das Auflisten des Zips (über tausend Einträge) füllt den Kontext, und die Sitzung kann damit beginnen, bevor sie eine mitgeschickte Datei wie `aufgabe` gelesen hat (so geschehen in einer claude.ai-Sitzung am 23.10.2026). Der folgende Satz gehört deshalb in die erste Nachricht oder in die Projektanweisungen des Claude-Kontos, nicht nur in eine Datei; alles Weitere steht in der Karte:

```
Projekt C 8205: Das Zip nicht auflisten und nie mit unzip entpacken (Python-zipfile). Zuerst nur die Karte lesen:
python3 -I -c "import zipfile,sys;sys.stdout.buffer.write(zipfile.ZipFile(sys.argv[1]).read('CLAUDE.md'))" <zip>
Alles Weitere (Entpacken, Selbsttest, Lieferung) steht dort.
```

**Letzter Build:** 0.96.1-074
