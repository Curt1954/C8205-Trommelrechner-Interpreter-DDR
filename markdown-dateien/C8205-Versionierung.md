** Versionierung (Wurzeldokument für Versionsnummern) **

Version: 0.97-017

Dieses Dokument legt fest, wie die Dateien des Projekts C 8205 versioniert werden: wie eine Versionsnummer aufgebaut
ist, welche Dateien eine tragen, wo sie steht und wann sie sich ändert. Es beschreibt keine Inhalte der Dateien,
sondern nur ihre Kennzeichnung. Der Ausgangsstand wurde am 09.10.2026 vom Projektinhaber auf
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
> Einzelheiten: Abschnitt 3; Text für Projektanweisungen: Abschnitt 7.


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
| die Hilfsprogramme `c8205_lochstreifen_anzeige.py`, `c8205_lochstreifen_eingabe.py` und `c8205_lochstreifen_umwandlung.py` | eigene Programmversion (Konstante `VERSION`, Abfrage mit `--version`), **nicht** im Schema `y.xx-zzz`; sie wird in `C8205-Interpreter-Lochstreifen-Hilfsprogramme.md` geführt. Die zugehörige `.md`-Datei trägt dagegen die Nummer `y.xx-zzz` |
| die Assemblerdokumentation `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md` (maßgeblich) | ja, `y.xx-zzz`, wie jede `.md`-Datei in der Zeile `Version:` im Kopf. Das PDF `C8205-Assemblerdokumentation_A4.pdf` wird wie die übrigen PDFs aus der `.md` erzeugt; es trägt keine eigene Nummer, sein Deckblatt nennt die Version der `.md` |
| die GRAFIK-Module (`c8205_grafik.py`, `grafik-interpreter-module/*.py`) | **eigene Zählung** je Modul im Schema `Gn-nnn` (n = Stufe, nnn = Zähler), bei einzelnen Modulen mit eigener Kennung (`DL-`, `FL-`, `HZ-`, `HW-`, `TP-`); **nicht** im Schema `y.xx-zzz`. Die Kennung steht nur in der Konstante `VERSION_*` im Code (Entscheidung des Projektinhabers 21.10.2026; die Zeile `Version:` im Kopf der Module entfällt seit 10.11.2026, damit die Kennung nur an einer Stelle steht). Ohne Kennung: `grafik_stufe4_tests.py`. Bei jeder Änderung eines Moduls steigt seine Kennung um 1; die Stufenkennung ist die Stufe, in der die Änderung entstand |
| das Assemblerprogramm `c82ass` (Binary und Quellcode `Assembler/Sourcecode/ca82_version.h`) | eigene Programmversion `y.xx-zzz`; Quelle ist die Konstante `ASM_VERSION` |
| einzelne weitere Python- und Shell-Dateien, die im Kopf eine Zeile `Version: y.xx-zzz` tragen (Fundstellen: Abschnitt 6) | ja, eigene Nummer; Build +1 je Änderung wie bei den übrigen Dateien. Skripte ohne diese Zeile tragen keine Nummer |
| alles andere (PDFs, Tests, Skripte ohne Versionszeile, Trommeldatei) | nein. Die PDFs tragen keine eigene Nummer, nennen aber auf dem Deckblatt die Version der Quelldatei(en) zum Zeitpunkt der Erzeugung und den Stand (Erzeugungsdatum); so ist erkennbar, ob ein PDF noch zur Quelle passt (`C8205-Interpreter-PDF.md`, Abschnitt 4.6; entschieden am 11.10.2026). Das Erzeugen eines PDFs bricht ab, wenn der Quelldatei die Versionszeile fehlt |

- **Jede Datei hat ihre eigene Nummer.** Die Nummern verschiedener Dateien sind voneinander unabhängig: Ändert sich
  eine Datei, ändert sich nur ihre Nummer.
- Eine **Kopie** einer Datei ist kein eigener Gegenstand; sie trägt
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
| `.md`-Datei | eine eigene Zeile `Version: y.xx-zzz` unmittelbar unter der Titelzeile (der ersten Zeile der Datei), mit einer Leerzeile davor; danach darf eine weitere Kopfzeile (`Stand:`, `Status:`) unmittelbar folgen |
| `.md`-Datei, die der Interpreter oder ein anderes Werkzeug zeilenweise mit `#` als Kommentarzeichen liest (`C8205-Interpreter-Eingänge_der_Knoten.md`, `C8205-Interpreter-Beschreibung_der_Knoten.md`) | dieselbe Stelle, aber als Kommentarzeile `# Version: y.xx-zzz`, getrennt durch je eine `#`-Zeile; so bleibt die Datei für das Werkzeug unverändert lesbar |
| `c8205_interp.py` | Zeile `Version: y.xx-zzz` im Kopfkommentar unter der ersten Zeile **und** die Konstante `VERSION` am Programmanfang; beide müssen übereinstimmen |
| `c82ass` (Programm) | Konstante `ASM_VERSION` in `Assembler/Sourcecode/ca82_version.h` (einzige maßgebliche Stelle; `greetings()` in `ca82_berichte.c` gibt sie aus); das Programm gibt beim Start und bei `-h` die Zeile `C8205 Assembler C82aas Version y.xx-zzz` aus. Dieselbe Nummer steht an weiteren Stellen (Quelltext-Kopfzeilen, `.md`, Regressionstest): vollständige Liste unter der Tabelle |

- Dateinamen tragen die Nummer nicht (sie stehen in vielen Verweisen), ebenso wenig die Titelzeile einer `.md`-Datei.
- **Abfrage beim Interpreter:** `python3 c8205_interp.py --version` gibt `c8205_interp.py y.xx-zzz` aus und endet mit
  Rückkehrcode 0, ohne einen Test auszuführen. Die Wrapper `c8205_interpreter.sh` und `.bat` sind für Testläufe gedacht
  (Testdatei als erstes Argument); die Version wird direkt mit `python3` abgefragt.
- Das Protokoll des Interpreters nennt die Version in seiner ersten Zeile (`C8205-Interpreter-Version: y.xx-zzz`); die übrigen Ausgaben nennen sie nicht.

**Assemblerstand: alle Stellen einer Hochzählung (Handliste).** Wird `ASM_VERSION` hochgezählt, müssen alle Zeilen der Liste nachgezogen werden. Vergisst man eine, meldet das nur `Assembler/version_abgleich.sh` (siehe unter der Tabelle) oder ein späterer Leser. Die Angaben „Stand …“ in `C8205_Standardmakros_c82ass.md` nennen den Assemblerstand, gegen den der Text zuletzt geprüft wurde; sie gehören nicht zur Handliste und werden nur nachgezogen, wenn der Text neu geprüft wurde.

| Ort | Stelle | Wert |
|---|---|---|
| `Assembler/Sourcecode/ca82_version.h` | `#define ASM_VERSION` | neue Nummer |
| jede **geänderte** `.c`/`.h` in `Assembler/Sourcecode/`, die in der ersten Zeile eine Nummer trägt (`Version y.xx-zzz (siehe ca82_version.h)`; derzeit `ca82_berichte`, `ca82_fluss`, `ca82_makros`, `ca82_standards`, `ca82_symbole`, `ca82_typen` und einzelne zugehörige `.h`) | Kopfzeile | neue Nummer; ungeänderte Dateien behalten ihre ältere Nummer; Dateien ohne Nummer in der Kopfzeile (z. B. `ca82_main.c`, `ca82_opsym.c`, `ca82_quelle.c`) bleiben so |
| `Assembler/Dokumentation/C8205_Assembler_Dokumentation.md` | Zeile `Version:` im Kopf | eigener Build der `.md`, +1 |
| dieselbe `.md` | die drei Texte „C8205 Assembler C82aas Version …“: Usage-Beispiel, Satz zu `--version`, Beispielausgabe (ein Änderungsprotokoll gibt es seit 1.03-011 nicht mehr) | neue Nummer von `ASM_VERSION` |
| `Assembler/Regressionstest/negativ/version.erwartet` und `pass0_version.erwartet` (nur im `Regressionstest.zip`) | Zeile `stdout C8205 Assembler C82aas Version` | **ohne Nummer** (seit Checkpoint 31): bei einer Hochzählung ist hier nichts nachzuziehen, und die beiden Negativtests melden vor dem Bau des Binarys keine Abweichung mehr; die Nummer prüft `version_abgleich.sh` |
| `Assembler/Regressionstest/LIESMICH.md` (nur im `Regressionstest.zip`) | Zeile `Version:` und ein neuer Eintrag | eigener Build, +1 |
| `Assembler/_Linux/c82ass` (Binary) | wird nicht geliefert | der Inhaber baut es aus dem Quelltext |

Zum Abhaken, nachdem alles nachgezogen ist: `bash Assembler/version_abgleich.sh` (von überall; je Stelle eine Zeile OK, HINWEIS oder ABWEICHUNG, Rückgabecode 0 = alles in Ordnung, 1 = Abweichung, 2 = Aufruf falsch oder Datei fehlt; nur lesend; nur für die Claude-Sitzung und Linux). Es liest `ASM_VERSION` und prüft die Quelltext-Kopfzeilen (keine Nummer neuer als `ASM_VERSION`), in der `.md` die Zeile `Version:` und die drei Texte, im Regressionstest die beiden Erwartungsdateien und `LIESMICH.md` (aus `Assembler/Regressionstest/`, sonst aus `Regressionstest.zip` im Projektstamm; `--regr <Pfad>` nennt einen anderen Ort). Mit `--binary` prüft es zusätzlich `c82ass --version` (bis der Inhaber das Binary gebaut hat, ist diese Abweichung erwartet), mit `-v` zeigt es jede Kopfzeile. Nicht entscheidbar ohne Vergleichsstand: ob eine geänderte Quelltext-Datei ihre Kopfzeile bekommen hat; dafür gibt es nur den HINWEIS, wenn keine Kopfzeile die aktuelle Nummer trägt. Von Hand dasselbe (Projektstamm; zeigt alle Fundstellen im Quelltext und in der `.md` sowie die drei Texte):

```
V=$(sed -n 's/.*ASM_VERSION "\(.*\)".*/\1/p' Assembler/Sourcecode/ca82_version.h)
grep -rn "$V" Assembler/Sourcecode Assembler/Dokumentation/C8205_Assembler_Dokumentation.md | cut -c1-105
grep -o "C82aas Version [0-9.]*-[0-9]*" Assembler/Dokumentation/C8205_Assembler_Dokumentation.md
```


## 5. Ausgangsstand

Am 09.10.2026 wurde die Versionierung eingeführt. Alle `.md`-Dateien des Projektarchivs `projekt_c8205.zip` (einschließlich
dieser Datei) und `c8205_interp.py` erhielten die Nummer **0.03-001**; der Wert wurde vom Projektinhaber festgelegt. Ab dem
nächsten Änderungsschritt gelten die Regeln aus Abschnitt 3. Die Unterversion wurde am 20.10.2026 auf Aufforderung des
Projektinhabers auf 0.95 und am 27.10.2026 auf Aufforderung des Projektinhabers auf 0.97 gesetzt (Build danach wieder ab 001);
der Ausgangsstand 0.03-001 bleibt als Geschichte stehen.


## 6. Prüfung

Alle Versionszeilen anzeigen (Linux/macOS; unter Windows z. B. in Git Bash):

```
grep -rHE '^(# )?Version: [0-9]+\.[0-9]{2}-[0-9]{3}$' --include='*.md' --include='c8205_interp.py' .
```

Dateien finden, denen die Versionszeile fehlt (keine Ausgabe = alle Dateien haben eine):

```
grep -rLE '^(# )?Version: [0-9]+\.[0-9]{2}-[0-9]{3}$' --include='*.md' .
```

Python- und Shell-Dateien mit Versionszeile (Fundstellen der Tabellenzeile in Abschnitt 2):

```
grep -rlE '^(# )?Version:? [0-9]+\.[0-9]{2}-[0-9]{3}' --include='*.py' --include='*.sh' .
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
was in den Dateien steht. Deshalb steht die Regel in diesem Dokument, in der Karte `CLAUDE.md`, in `README.md`, `README.en.md`,
`C8205-Interpreter-Projektueberblick.md`, `C8205-Einstieg_fuer_Neueinsteiger.md`, im Kopf von `baz-wirkungstabelle.md` (die KI-Sitzungen des Claude-Interpreters
laufend ergänzen) und im Kopfkommentar von `c8205_interp.py`.

Zum Einfügen in die Projektanweisungen oder persönlichen Einstellungen eines Claude-Kontos (die Sitzung kennt die Regel
dann auch ohne hochgeladene Dateien):

```
Versionierung im Projekt C 8205 (Aufbau y.xx-zzz, Definition: C8205-Versionierung.md):
Jede Änderung an einer versionierten Datei (alle .md-Dateien, c8205_interp.py und c82ass) erhöht deren Build (zzz) um 1.
Die geänderte Datei wird mit der neuen Nummer übergeben. Hauptversion (y) und Unterversion (xx) werden nur auf
ausdrückliche Aufforderung des Projektinhabers erhöht, nie von selbst. Bei jeder neuen Unterversion oder Hauptversion
beginnt der Build wieder bei 001 (bei einer neuen Hauptversion auch die Unterversion bei 00).
```


## 8. Releases (Gesamtversion)

Eine **Gesamtversion** bezeichnet einen Stand des ganzen Projekts bei einem Release auf GitHub. Sie ist nur ein Etikett:

- Form `V.M.P` (z. B. `0.95.1`), als Git-Tag mit vorangestelltem `v` (`v0.95.1`). `V.M` entspricht Hauptversion und Unterversion der Dateien; `P` zählt die Releases innerhalb dieser Unterversion und beginnt bei 1; bis zum ersten Release einer neuen Unterversion steht `P` auf 0 (so im Zip `0.97.0-001`).
- Jedes Release erhöht `P` um 1. `V` und `M` ändern sich nur, wenn der Projektinhaber die Haupt- oder Unterversion der Dateien ausdrücklich erhöht; dann beginnt `P` wieder bei 1.
- Die Gesamtversion steht im Git-Tag, im Titel des Releases, in der Tabelle unten, im Namen des Zips und in der Anzeigezeile `Letzter Build` am Ende dieser Datei (Abschnitt 9), in keiner anderen Datei. Dadurch gibt es nichts zu synchronisieren, und die Dateinummern bleiben unverändert maßgeblich.
- Mit jedem Release wird hier eine Zeile ergänzt: Tag, Datum und die Nummern der Dateien, die für das Release wichtig sind.

| Gesamtversion | Datum | Enthaltene Stände | Bemerkung |
|---|---|---|---|
| `v0.95.1` | 21.10.2026 | Interpreter `c8205_interp.py` 0.95-001; Assembler `c82ass` 1.00-026; Assemblerdokumentation `.md` 1.00-026 (die `.odt` und das PDF sind nicht nachgeführt); `Projektstruktur` 0.95-013; `Versionierung` 0.95-043 | erstes Release mit Gesamtversion; `_Windows/` enthält noch kein Binary |
| `v0.95.6` | 23.10.2026 | Interpreter `c8205_interp.py` 0.95-002; Assembler `c82ass` 1.00-034; Assemblerdokumentation `.odt` und `.md` 1.00-033 (das PDF ist nicht nachgeführt); `Projektstruktur` 0.95-017; `Regressionstest/LIESMICH.md` 1.00-034; `Versionierung` 0.95-081 | Etikett auf Anweisung des Projektinhabers von 0.95.1 auf 0.95.6 angehoben; die Zwischenstände 0.95.2 bis 0.95.5 stehen nicht in dieser Tabelle |

## 9. Zip packen und Programmierhandbuch pflegen

**Zip packen:** `./c8205_zip_packen.sh` im Projektstamm (Schalter und Einzelheiten im Kopfkommentar des Skripts). Gesamtversion `V.M.P` und Build-Nummer `NNN` kommen aus der Zähldatei `.build-nummer` im Projektstamm (eine Zeile `V.M.P-NNN`; nicht aus der Release-Tabelle); daraus entsteht der Name `C8205 Simulator V.M.P-NNN.zip`. Mit Parameter (`./c8205_zip_packen.sh 0.95.5`) gilt die genannte Version; weicht sie von der Zähldatei ab, beginnt die Build-Nummer bei 001. Vor dem Packen trägt das Skript die Nummer in die Zeile `**Letzter Build:**` am Ende dieser Datei ein (nur eine Anzeige); nach einem erfolgreichen Lauf zählt es die Nummer in `.build-nummer` um 1 hoch. Die Zähldatei kommt in kein Zip. Das Skript packt außerdem `Test-Protokolle/` nach `Test-Protokolle.zip` und `Assembler/Regressionstest/` nach `Regressionstest.zip`; beide Ordner selbst kommen nicht ins Gesamt-Zip, die Sub-Zips schon. Mit `--claude` (`./c8205_zip_packen.sh --claude`, auch mit Version) entsteht stattdessen `C8205 Simulator V.M.P-NNN Claude.zip`: ohne PDFs (außer unter `C8205Z/`) und ihre Erzeugungsskripte, ohne die Testtabelle `Testausfuehrungen/test_tabelle*`, `pult/`, `ton/`, `README.en.md`, `Test-Protokolle.zip` und die vom Assembler erzeugten `.log .mqo .obj .sym`; `virtuelle_Geraete/` und `C8205Z/` bleiben dabei. In keinem der beiden Zips liegt `C8205Z/zt_modul/python/build/` (Bau-Zwischenstand). Für Arbeiten am GRAFIK-Fenster oder an den Klängen taugt nur das Gesamt-Zip.

**Programmierhandbuch pflegen:** `CLAUDE.md` (die Karte), `C8205-Programmierhandbuch_fuer_Claude.md` und die beiden Anhänge in `markdown-dateien/` sind versionierte `.md`-Dateien; jede Änderung erhöht ihren Build. Quellverweise in diesen Texten: Dateiname plus Überschrift, ohne Gliederungsnummern der Quelle. Schnellstart, Rückgabecodes, Fallen und Arbeitsregeln stehen nur in der Karte, Erklärungen nur im Handbuch; die Karte bleibt kurz (Richtwert: höchstens etwa 120 Zeilen). Die Wortzahlen in der Lesetabelle der Karte („Welche Aufgabe, was lesen?“) gelten für die dort genannte Handbuchversion; ändert sich die Länge eines Abschnitts spürbar, nachzählen (Wörter je Abschnitt einschließlich Überschrift): `awk '/^##+ /{if(n)print w,n;n=$0;w=NF;next}{w+=NF}END{print w,n}' C8205-Programmierhandbuch_fuer_Claude.md`.

**Start einer Claude-Sitzung:** Das Auflisten des Zips (über tausend Einträge) füllt den Kontext, und die Sitzung kann damit beginnen, bevor sie eine mitgeschickte Datei wie `aufgabe` gelesen hat (so geschehen in einer claude.ai-Sitzung am 23.10.2026). Der folgende Satz gehört deshalb in die erste Nachricht oder in die Projektanweisungen des Claude-Kontos, nicht nur in eine Datei; alles Weitere steht in der Karte:

```
Projekt C 8205: Das Zip nicht auflisten und nie mit unzip entpacken (Python-zipfile). Zuerst nur die Karte lesen:
python3 -I -c "import zipfile,sys;sys.stdout.buffer.write(zipfile.ZipFile(sys.argv[1]).read('CLAUDE.md'))" <zip>
Alles Weitere (Entpacken, Selbsttest, Lieferung) steht dort.
```

**Letzter Build:** 0.98.1-002
