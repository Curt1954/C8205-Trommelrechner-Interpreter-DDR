# C 8205 – Karte für Claude (zuerst lesen)

Version: 0.01-054
Geprüft am 23.10.2026 gegen Zip 0.95.1 Claude unter Python 3.11, 3.12 und 3.13: Selbsttest, Minimalbeispiel, alle hier genannten Dateien vorhanden, alle Tests in rund 12 s ohne Fehler.

**Projekt:** Simulator des DDR-Kleinrechners Cellatron C 8205 (1968): Python-Interpreter `c8205_interp.py`, Assembler `c82ass` (C, Quelltext in `Assembler/Sourcecode/`), Einadreßmaschine mit Magnettrommel (4096 Worte zu 33 Bit). Dokumentation und Antworten sind deutsch; die Dokumentation ist maßgeblich.

## Zuerst

- **Standardweg für jedes Assemblerprogramm:** `Assembler/asm_und_test.sh <ordner> <n>` (assembliert, ergänzt die `.test`, testet, in einem Aufruf). Die Sollwerte stehen im `.asm` zwischen `;#PRUEFE-START` und `;#PRUEFE-ENDE` (Vorlage `Assembler/Claude/mini/mini.asm`). Nicht Assembler und Interpreter einzeln von Hand aufrufen, nicht `.test` von Hand ergänzen.
- **Zips nie mit `unzip` entpacken, sondern mit Python-`zipfile`** (`unzip` macht in der POSIX-Locale aus Umlauten `#U00e4` und bricht den Interpreter, Falle 3). Das Zip **nicht** vollständig auflisten (über tausend Einträge, meist erzeugt). Diese Karte lesen: `python3 -I -c "import zipfile,sys;sys.stdout.buffer.write(zipfile.ZipFile(sys.argv[1]).read('CLAUDE.md'))" <zip>`. Gezielt suchen oder eine Datei lesen: `python3 -I testscripte/zip_entpacken.py -l <zip> <teilname>` und `-p <zip> <pfad>` (nach dem Entpacken; vorher dieselben zwei Zeilen mit `zipfile.ZipFile(...).namelist()` / `.read(...)`). Sonst entpacken (Schnellstart) und mit `grep`/`find` suchen.
- Vom Handbuch `C8205-Programmierhandbuch_fuer_Claude.md` nur den Abschnitt lesen, den die Aufgabe braucht (Tabelle unten). Begriffe (AC, BZ, V1/V2, KEP, BIS …): Handbuch Abschnitt 10 (Suchkarte).

## Umgebung (Claude-Sitzung in der Cloud)

- Eigener, privater Linux-Arbeitsbereich; Python 3 (3.11, 3.12 und 3.13 geprüft; der Inhaber nutzt 3.11, also nichts verwenden, was erst ab 3.12 geht), keine Pakete nötig, kein Netz nötig. `gcc`/`make` nur zum Neubau des Assemblers. Befehle laufen nur dort, nie auf dem Rechner des Nutzers. Windows-Bau (MinGW-w64, `bau_trommel_mingw.bat`, `bau_ztmodul_mingw.bat`) und Windows-Test des C-Moduls laufen beim Inhaber, nie in der Cloud-Sitzung; Windows-Angaben in der Doku stammen aus seinen Meldungen (Beschreibung §9.2).
- Das Zip liegt dort, wo die Aufgabe es nennt (meist `/mnt/user-data/attachments/<id>/` oder `/mnt/user-data/uploads/`). Diesen Pfad überall einsetzen, wo unten `<zip>` steht. In einem **neuen, leeren Ordner im Arbeitsverzeichnis** entpacken, nicht neben dem Zip.
- Ergebnisse kommen nach `/mnt/user-data/outputs/` und werden mit dem Sendewerkzeug der Sitzung an den Nutzer geschickt (`SendUserFile` oder `present_files`, je nachdem, was vorhanden ist).
- Vorbereitung und Selbstprüfung (im Projektstamm des entpackten Zips):
```
export LC_ALL=C.UTF-8            # vor jedem Lauf (Falle 3); entpackt wird mit Python-zipfile, nie mit unzip
python3 -V; test -x Assembler/_Linux/c82ass && echo asm-ok
python3 -I c8205_interp.py --MODUS=TEST Tests/trommel-001_leer.txt   # endet mit „Test wahr“
```

## Zip-Stamm

`CLAUDE.md`, Handbuch `C8205-Programmierhandbuch_fuer_Claude.md`, `README.md`, `Regressionstest.zip` · `c8205_interp.py` Interpreter, `c8205_grafik.py` + `grafik-interpreter-module/` + `c-module/` GRAFIK · `Assembler/` (`_Linux/c82ass` fertiges Binary, `Sourcecode/`, `Dokumentation/` mit der maßgeblichen `.odt`, Vorlagen in `Claude/`, `Claude_bsp_reassemblierung/`) · `Tests/` (über 150 fertige Tests), `Test-Ergebnisvergleiche/`, `Test-virtuelleGeraete/` (nicht löschen), `Trommel/trommel.txt` · `markdown-dateien/` (Doku, Anhänge A und B, Versionierung), `testscripte/`, `Testausfuehrungen/` (Skripte `testwahl.sh`, `kep_test.sh`, `interpreter_test.sh`, `bis_test.sh`; sie wechseln selbst in den Projektstamm), `Hilfsprogramme/`, `Bausteininterpretiersystem BIS/`. Vollständig: `markdown-dateien/C8205-Projektstruktur.md`.

## Regeln des Projektinhabers

- **Assembler-Binary** liegt fertig in `Assembler/_Linux/c82ass`. Neubau nur nach einer Änderung am C-Quelltext (`cd Assembler && ./make_c82ass.sh`) und für eigene Tests; **nie zum Download stellen** (der Inhaber baut selbst).
- **Skripte** (`.sh`, `.bat`, `.py`) darf ich anpassen oder neu schreiben; jedes neue oder geänderte **immer in die Lieferung**.
- **Nachfragen, nicht raten:** bei unleserlicher Vorlage, bei Widerspruch zwischen Quellen, bei Build-Überlauf (999) und wenn Haupt- oder Unterversion steigen müsste (die erhöht nur der Inhaber). Sonst ohne Rückfrage arbeiten und Annahmen in einer Zeile nennen. Für den Assembler gilt die `.odt` vor jeder `.md`.
- **Versionen:** Jede geänderte versionierte Datei (alle `.md`, `c8205_interp.py`, Assembler-`.odt`, `c82ass`) erhöht ihren **Build** (`zzz` in `y.xx-zzz`) einmal je Lieferung um 1, in der Zeile `Version:` im Kopf; unveränderte Dateien behalten ihre Nummer. Einzelheiten: `markdown-dateien/C8205-Versionierung.md`, Abschnitte 2 und 3. Die Zip-Version steht im Dateinamen. **Der Assemblerstand (`ca82_version.h`) steht an mehreren Stellen** (Quelltext-Kopfzeilen, `.odt`, `.md`, Regressionstest): jede Hochzählung nach der Liste in `C8205-Versionierung.md`, Abschnitt 4, abarbeiten; fehlt eine Stelle, meldet das meist erst der Regressionstest oder ein späterer Leser.
- **Anforderungs- und Entwurfsdateien** (vom Inhaber hochgeladen, meist nicht im Zip, z. B. `Anforderungen_Schluesselwortparameter.md`): Unter dem Kopf steht die Zeile `Status: offen` oder `Status: umgesetzt in c82ass <Version>, Doku <Abschnitt>` (Beispiel: `Status: umgesetzt in c82ass 1.01-025, Doku 4.30`). **Zuerst diese Zeile lesen und gegen diese Karte und `c82ass --version` prüfen, dann erst bauen:** ein Satz „nicht umgesetzt“ im Text kann überholt sein. Fehlt die Zeile, den Stand in Karte, Doku und Quelltext (`grep`) feststellen, nicht neu bauen, und die Zeile in der Lieferung nachtragen (Build der Datei +1). Wer eine Anforderung umsetzt, trägt die Zeile im selben Schritt nach und liefert die Datei mit.
- **Abgabe** (auch jeder Checkpoint nach etwa 10 Minuten): immer **eine Zip-Datei** mit Projektpfaden (z. B. `Assembler/Claude/mini/mini.asm`). Packen im Projektstamm: `bash lieferung_packen.sh --seit <zip>` (mit `bash` aufrufen, falls das Skript im Zip noch ohne X-Bit ankommt; nimmt alles Neue und Geänderte; ohne `--seit` mit Dateiliste). **Erst `-l`** (zeigt nur an) und Ungewolltes vorher löschen: der Packer nimmt auch erzeugte `.dmp` mit. Ist ein anderes Skript „Permission denied“, ebenfalls mit `bash` aufrufen. **Rechte:** Der Packer packt jede `.sh` mit 0755 (auch ohne X-Bit im Arbeitsbereich), eine `.py` nur, wenn sie dort ausführbar ist, alles andere mit 0644; eine reine Rechteänderung (Inhalt gleich, aber im Vergleichs-Zip ohne X-Bit) listet er als „Rechte“. `c8205_zip_packen.sh` setzt nach dem Packen alle `.sh` im Zip auf 0755. Beim Entpacken (Schnellstart) übernimmt `chmod` die Rechte aus dem Zip. Ergebnis `C8205_Lieferung_NNN.zip` in `/mnt/user-data/outputs/`; nur die neueste senden, keine Einzeldateien daneben. Inhalt: `.asm`, `.test` (mit Prüfung), Soll-Dateien, neue oder geänderte Skripte und versionierte Dateien. Binaries verweigert das Skript. Mit `--seit` nimmt es `.obj` unter `virtuelle_Geraete/` und `Lochstreifen/` mit (das sind Bänder, keine Assembler-Ausgabe); gelöschte Dateien zeigt es nur an („gelöscht“), denn im Zip lassen sie sich nicht ausdrücken: dem Inhaber in einer Zeile nennen.
- **Fertig heißt:** Test wahr (Rückgabecode 0), Lieferungs-Zip gesendet, Annahmen in einer Zeile genannt.
- **Python als Makrosprache (nur für Claude, Handbuch 5.7):** Bibliothek `Assembler/Claude/gen_lib/c82gen.py` (0.01-006, maßgeblich ist die Zeile `Version:` am Dateianfang; seit 0.01-005 `makro()` für parameterlose Makros und `schreibe(..., ztpruefe=[...])` für den Abschnitt ZT-Zellen-Pruefung; Pilot für beides: `Assembler/Projekt_ZT_LOADER/Unterprojekt_Allgemein/ztinit/gen/`; Messung und Einsatzregel `gen_lib_messung.md`: ab etwa 30 Zellen mit Schleife, Feld, UP oder Ein-/Ausgabe), Pilot `Assembler/Claude/feldmax/`, Prüfprogramme `Assembler/Claude/gen_lib_test*`; `asm_und_test.sh` führt einen vorhandenen Generator `<ordner>/gen/<n>_gen.py` selbst zuerst aus, alle Generatoren: `bash testscripte/gen_alle_tests.sh`. Wird ein Assemblerprogramm mit einem Python-Generator erzeugt, liegt dieser im Unterordner `gen/` des Programmordners (z. B. `Assembler/Claude/<programm>/gen/`), die gemeinsame Hilfsbibliothek zentral in `Assembler/Claude/gen_lib/`. Generatoren liegen im ganzen Baum `Assembler/`, auch unter `Assembler/Projekt_ZT_LOADER/`, nicht nur unter `Assembler/Claude/`; suchen mit `find Assembler -path '*/gen/*_gen.py'`. **Nicht jeder Generator nutzt `c82gen`:** nur wo `from c82gen import` steht, gelten die Idiome aus Handbuch 5.7; `typ10ein`, `hschl*` und `zil_*` sind reine Python-Generatoren (die `zil_*` leiten Varianten aus dem handgeschriebenen `zil/zil.asm` ab: dieses ändern, nicht die Variante). Vor dem Ändern eines Generators die Importzeilen lesen. Die erzeugte `.asm` bleibt maßgeblich und lesbar; Änderungen laufen über den Generator, und `.py` und `.asm` kommen zusammen in die Lieferung. Läuft ein erzeugtes Programm nur über einen Lader (nicht allein), liegt neben dem Generator ein `<n>_test.sh`, das `gen_alle_tests.sh` statt `asm_und_test.sh` aufruft.
- **Projektspezifische Makrodateien (c82ass 1.00-049):** `;#MACRODATEI1=<Pfad>` bis `;#MACRODATEI9=<Pfad>` im `.asm`; Suchreihenfolge Quelltext, Datei 1 bis 9, `c82ass.makros`. Vorhanden: `Assembler/Projekt_ZT_LOADER/macro_zt_loader.macro` (Makros `TYP10EINGABE` (optionaler Parameter = Endeausgang für `/`), `KAT4AUSGABE_G`, `ZTINIT`, `PNAME`, `NEUANL`, `ZTKONST` (erzeugt keine Zelle, nur die abs-Konstanten `ZT_EINTRAGSZELLEN` = 2, `ZT_VERZSPUREN` = 32, `ZT_PROGSPUR1` = 33 des ZT-Verzeichnisses; einmal aufrufen, `ZTINIT` tut es selbst), `HSCHL` (legt den ZTD-Streifen seit 01.11.2026 als Typ 10 ab, liest mit `TYP10EINGABE`; Aufruf `hschl: HSCHL fe_lang eingabe ende`); Struktur des Projekts ZT-Loader: Unterprojekte `Unterprojekt_Allgemein`, `_ZIL_Initialloader`, `_ZTD_Dialogmodul`, `_ZTL_Kernmodul`; Programme darin erreichen die Makrodatei mit `;#MACRODATEI1=../../macro_zt_loader.macro`). Beschreibung der ZT-Makros (aufgebaut wie die Standardmakros-Datei): `Assembler/Dokumentation/C8205_ZT_Makros_Uebersicht.md`; PDF daraus: Skript `Assembler/Dokumentation/pdf-layout-scripte/erzeuge_zt_makros_pdf.py` (über `make_pdf.sh`; reportlab nötig, Hilfe im Kopf des Skripts). Der Regressionstest kopiert alle `*.macro` mit. `c82ass ... --makros` gibt die Makroliste (Aufrufe, Herkunft) aus.
- **Namen für Operationscodes (OPSYM, umgesetzt ab c82ass 1.00-061; Doku Assemblerdokumentation 3.3.17):** gilt nur, wenn `cd Assembler && ./_Linux/c82ass --opsyms` mit Rückgabecode 0 endet (**aus `Assembler/` aufrufen**, das gelingt mit jedem Binary ab 1.00-061; ab 1.00-066 geht es auch aus jedem anderen Verzeichnis. Meldet ein Binary bis 1.00-065 aus dem Projektstamm die Standardtabelle als nicht gefunden (Rückgabecode 16), ist das nur das falsche Verzeichnis, kein altes Binary; meldet es die Option als unbekannt (Rückgabecode 16, etwa 1.00-058), weiter Oktalcodes mit Kommentar. Das Binary im Zip baut der Inhaber, Neubau nur zum eigenen Test). Dann vor dem Schreiben von Assembler-Quelltext die Liste lesen und Namen mit vorangestelltem Punkt schreiben (`.LD`, nur im Operationscode-Feld). Hat das Projekt eine Namensdatei (`;#OPSYM=<Pfad>`), diese ebenfalls lesen; neue Projektnamen dort mit `; Nr. <n>` (Nummer der Einzelbefehlsübersicht) anlegen und in der Lieferung nennen; Einzelfälle auch mit `NAME: opsym <code>` im Quelltext. Die Standardtabelle `c82ass.opsym` (23 Namen) ändert nur der Inhaber; Änderungen nur vorschlagen. Tabellentest: `python3 testscripte/opsym_tabelle.py [Namensdatei]`.
- **Dateiformat:** `.asm` und `.test` sind UTF-8 mit LF, Kommentar in jeder Zeile (deutsch), Zahlen oktal.

## Schnellstart (neuer, leerer Ordner)

```
export LC_ALL=C.UTF-8
python3 -I -c "import zipfile,sys,os;z=zipfile.ZipFile(sys.argv[1]);z.extractall(sys.argv[2]);[os.chmod(os.path.join(sys.argv[2],i.filename),(i.external_attr>>16)&0o777) for i in z.infolist() if not i.is_dir() and (i.external_attr>>16)&0o777]" <zip> <neuer_ordner>
# gleichwertig, wenn das Skript schon da ist: python3 -I testscripte/zip_entpacken.py <zip> <neuer_ordner>
Assembler/asm_und_test.sh <ordner_mit_asm> <n>                   # assemblieren, .test ergänzen, testen (von überall); Sollwerte aus dem ;#PRUEFE-Block des .asm
Assembler/asm_und_test.sh <ordner_mit_asm> <n> AAAA=WERT ...      # nur wenn das .asm keinen ;#PRUEFE-Block hat
# oder einzeln:
cd Assembler && ./c82ass.sh -p <ordner_mit_asm> -s <n>.asm --WARN=ALLE --no-color   # nur aus Assembler/; rc 0 = fehlerfrei
cd ..        && python3 -I c8205_interp.py --MODUS=TEST <ordner_mit_asm>/<n>.test    # aus dem Projektstamm
```
Rückgabecodes Interpreter: 0 Test wahr · 4 ohne Prüfung · 6 Test falsch · 8 Laufzeitfehler · 16 formale Prüfung negativ · 2 Aufruf falsch. Assembler: 0 fehlerfrei, 16 Fehler.
Alle Tests: `testscripte/compute_all_tests.sh` (rund 17 s; Ausgabe nur eine Zeile „compute_all_tests: N Laeufe, M Abweichungen“ plus je Abweichung höchstens 4 Zeilen; rc 0 = keine Abweichung, 1 = Abweichungen, 3 = Abbruch wegen Umgebungsfehler, z. B. Zip ohne `LC_ALL` entpackt). **Nicht nach jeder Änderung**, sondern nach der Regel im Abschnitt „Tests nach Art der Änderung“.

**Minimalbeispiel** (geprüft, Quelltext in `Assembler/Claude/mini/mini.asm`; kopiert Zelle 0001 nach 0002):
`Assembler/asm_und_test.sh Claude/mini mini` → „Test wahr“, rc 0 (die Sollwerte stehen im `;#PRUEFE`-Block von `mini.asm`; Argumente wie `0002=00000000017` wären dort überflüssig) (die Warnung „Symbol 'ende' … nie verwendet“ ist normal). Sollwerte (Adresse 4, Wert 11 Oktalziffern) vorher von Hand herleiten.

**Bei rc 6, 8 oder 16** gibt `asm_und_test.sh` selbst eine Fehlersuche-Hilfe aus (die letzten 25 ausgeführten Befehle mit Quelltextzeile, Symbolzellen mit Anfangs- und Endwert; abschaltbar mit `ASM_FEHLERHILFE=0`): erst diese lesen, nicht von Hand nachlaufen. **Bei rc 6 oder 16:** zuerst die von Hand hergeleiteten Sollwerte und den Befehlscode prüfen (Falle 4), erst danach den Interpreter verdächtigen.

## Vier Fallen

1. Die vom Assembler erzeugte `.test` enthält **nur dann eine Prüfung**, wenn im `.asm` ein Block `;#PRUEFE-START … ;#PRUEFE-ENDE` steht (sonst rc 4). `asm_und_test.sh` ergänzt fehlende Teile (`#TROMMEL=LEER`, `US=1`, Zellen aus Argumenten) und meldet, was geprüft wird; von Hand nach Handbuch Abschnitt 0.
2. Die Trommel ist persistent, `Trommel/trommel.txt` wird bei jedem Lauf verändert: im Test `#TROMMEL=LEER` setzen (Handbuch Abschnitt 7).
3. `unzip` erzeugt in der POSIX-Locale Dateinamen wie `…#U00e4…`, und der Interpreter bricht mit „Knotengraph nicht gefunden“ ab (Handbuch Abschnitt 2). Deshalb **nie `unzip`, immer Python-`zipfile`** (Schnellstart, `testscripte/zip_entpacken.py`); `LC_ALL=C.UTF-8` bleibt trotzdem für die Läufe gesetzt.
4. **Nie raten:** Befehlscodes erst in Handbuch Abschnitt 4.1 nachsehen (häufig verwechselt: `211` lädt, `210` addiert, `240` speichert, `020` hält); Registerwerte (BZ, AR, V1/V2) nicht schätzen, sondern `US=1` plus Ergebniszellen prüfen (Abschnitte 7 und 8). Ein Test fängt Vertauschungen nur, wenn die Sollwerte vorher von Hand hergeleitet wurden.

## Tests nach Art der Änderung (Limit sparen)

Die Läufe selbst sind billig (je 17 bis 23 s, wenige Ausgabezeilen); Limit kosten viele Aufrufe und ungefilterte Ausgabe. Deshalb **nur prüfen, was von der Änderung berührt wird**:

| Geändert | Prüfen (und sonst nichts) |
|---|---|
| ein Assemblerprogramm (`.asm`, `.test`, `gen/`-Generator) | nur dieses Programm: `Assembler/asm_und_test.sh <ordner> <n>` |
| Projektmakro (`macro_zt_loader.macro`) | `asm_und_test.sh` der Programme, die das Makro aufrufen (`grep -l <MAKRONAME> -r Assembler --include=*.asm`); **nicht** `compute_all_tests.sh` (prüft nur den Interpreter über `Tests/`) |
| `Assembler/Claude/gen_lib/c82gen.py` | `bash testscripte/gen_alle_tests.sh` |
| `c8205_interp.py`, `Tests/`, `Test-virtuelleGeraete/` | `bash testscripte/compute_all_tests.sh` |
| `Assembler/Sourcecode/` (C-Quelltext) | `Assembler/Regressionstest/pruefe_alles.sh --ohne-asan` bei Zwischenständen; mit ASAN (ohne `--ohne-asan`) **einmal** vor der Lieferung (Handbuch Abschnitt 8, Schritt 7); wird `ASM_VERSION` hochgezählt, danach `bash Assembler/version_abgleich.sh` (alle Versionsstellen, Handliste in Versionierung.md Abschnitt 4) |
| GRAFIK-Module | `bash testscripte/grafik_alle_tests.sh --schnell`; ohne `--schnell` nur vor der Lieferung |
| Zusatztrommeln (`C8205Z/`) | `bash C8205Z/Tests_Z/zt_tests.sh` ohne Zusatzargument; `ztc`, `ztd`, `ztdpy` (mehrere Minuten) nur auf ausdrückliche Anforderung des Inhabers |
| nur Doku (`.md`) | kein Testlauf |

- **Ein Checkpoint nach 10 Minuten löst keinen Gesamtlauf aus.** Ein Gesamtlauf (die zur Änderung gehörenden Zeilen der Tabelle) gehört nur zur abschließenden Lieferung einer Aufgabe, und nur, wenn ein gemeinsam genutzter Teil (Interpreter, Assembler, Makrodatei, `gen_lib`) geändert wurde.
- **Ausgabe immer begrenzen:** Testläufe mit `2>&1 | tail -n 20` aufrufen (`compute_all_tests.sh` tut das selbst). Protokolle (`Test-Protokolle/`, `.dmp`) nur gezielt mit `grep -n` oder `head` lesen, nie ganz. Bei Abbruch rc 3 die Ursache beheben, nicht wiederholen.
- Was geprüft wurde und was bewusst nicht, steht in der Lieferung in einer Zeile.

## Welche Aufgabe, was lesen?

**Vor dem Schreiben eines Assemblerprogramms** (vier Punkte; Einzelheiten an den genannten Stellen):
1. Vorlage ansehen: `Assembler/Claude/mini/mini.asm` (Aufbau, `;#PRUEFE`-Block).
2. Namen für Operationscodes: `cd Assembler && ./_Linux/c82ass --opsyms` lesen, nur bei Rückgabecode 0, dazu die Namensdatei des Projekts (`;#OPSYM=`); Regel im Absatz „Namen für Operationscodes“ (Regeln des Projektinhabers).
3. Makros: Namen mit `grep -iE '^[A-Za-z0-9_]+: *MACRO' Assembler/Sourcecode/c82ass.makros` und in der Makrodatei des Programms (`;#MACRODATEI1=`) ansehen; passt eines, dieses aufrufen (Beschreibung: `Assembler/Dokumentation/C8205_Standardmakros_c82ass.md`), Neues nur nach den Festlegungen 017 und 018 (5.8).
4. Generator: ab etwa 30 Zellen mit Schleife, Feld, UP oder Ein-/Ausgabe einen Python-Generator schreiben (Handbuch 5.7; Einsatzregel im Absatz „Python als Makrosprache“).

| Aufgabe | Lesen |
|---|---|
| Assemblerprogramm schreiben und testen (Aufruf: `Assembler/asm_und_test.sh`, Sollwerte im `;#PRUEFE`-Block) | Handbuch **nie ganz lesen** (Stand 0.95-135: 14.819 Wörter, allein 5.4 hat 4.923). Immer: Abschnitte 0, 3, 4 mit 4.1, 5.1 bis 5.3, 5.8, 5.9, 6, 7, 8 und 9 (zusammen rund 6.300 Wörter; 5.9 ist die Übersicht zum Speichersparen mit Blöcken, Literalen und Makros; Abschnitt 9 sind die bekannten offenen Punkte). Vorlagen in `Tests/`, `Assembler/Claude/`, `Assembler/Claude_bsp_reassemblierung/`; vorher die vier Punkte oben |
| … dazu nur, was das Programm braucht (Wörter in Klammern) | Gruppen-, Wiederholungs- und Schiebebefehle: 4.2 (253) · Text auf dem Schreibwerk: 5.5 (534) · Eingabe: 5.6 (199) und in 5.8 der Block „Zeicheneingabe mit Sprungumstellung (007)“ · Feldzugriff, Befehl zur Laufzeit bauen: 5.4 nur bis vor den Punkt „Projektspezifische Makrodateien“ (108) · Standardmakros (Namen, Aufruf, Zellen): `Assembler/Dokumentation/C8205_Standardmakros_c82ass.md` · Makroprozessor: der Rest von 5.4 (4.815) ist eine Liste mit einem Punkt je Merkmal, jeder Punkt nennt den Abschnitt der Assemblerdokumentation; mit `grep -n` den Punkt zum gesuchten Merkmal finden und nur ihn lesen · Python-Generator: 5.7 (831) |
| Wirkung eines Befehlscodes klären | `markdown-dateien/C8205-Interpreter-Befehlsliste.md`, „Einzelbefehlsübersicht“ |
| Assembler (C-Quelltext) ändern | `Assembler/Sourcecode/`; danach Regressionstest (Handbuch Abschnitt 8, Schritt 7) |
| Interpreter (Python) ändern | `markdown-dateien/C8205-Interpreter-Python_Interpreter.md`; danach `testscripte/compute_all_tests.sh` |
| BIS (Minimalprogramm, Kennzeichen) | `markdown-dateien/C8205-Programmierhandbuch-Anhang_B_BIS_Anschluss.md` |
| Laufzeit, Trommelzeit, GRAFIK zur Zeitmessung | `markdown-dateien/C8205-Programmierhandbuch-Anhang_A_Trommelzeit_GRAFIK.md`; GRAFIK immer mit `--ohne-fenster --STUMM` |
| GRAFIK-Fenster, Pult oder Ton ändern | `markdown-dateien/C8205-Interpreter-GRAFIK_Beschreibung.md` (mit `grep -n`); dafür das **Gesamt-Zip anfordern** |
| Unbekannte Datei oder Begriff | Handbuch Abschnitt 10 (Suchkarte) |

## Die wichtigsten Skripte (Aufruf steht im Kopfkommentar)

**Für Claude vorbereitete Skripte:** `testscripte/*` (darunter `gen_alle_tests.sh`), `Assembler/asm_und_test.sh` und `lieferung_packen.sh`. Sie sind für den Einsatz in der Claude-Sitzung gedacht und werden dort anstelle von Handarbeit benutzt.

`Assembler/asm_und_test.sh` assemblieren + testen · `Assembler/c82ass.sh` Assembler starten (nur aus `Assembler/`) · `Assembler/asm_alle.sh [Ordner]` alle `.asm` darunter, meldet nur Fehler · `Assembler/version_abgleich.sh` prüft alle Versionsstellen des Assemblers gegen `ASM_VERSION` (nur lesend) · `Assembler/asm_aufraeumen.sh [--loeschen]` Erzeugtes entfernen (ohne Schalter nur Anzeige) · `bash lieferung_packen.sh` Lieferung packen · `c8205_zip_packen.sh` baut die Zips des Inhabers, **nie** für Lieferungen · `c8205_interpreter.sh` Interpreter-Wrapper · `testscripte/compute_all_tests.sh` alle Tests · `testscripte/c8205_befehlssweep.py` alle 512 Befehlscodes · `Assembler/Regressionstest/` (nach `unzip Regressionstest.zip`). Alles weitere, auch `.bat`: Handbuch Abschnitt 10.

## Zip-Fassungen und Arbeitsstand

Es gibt das Gesamt-Zip und die schlanke Claude-Variante (Name endet auf „Claude“). Was sie weglässt (PDFs, `README.en.md`, `pult/`, `ton/` …), steht in Handbuch Abschnitt 11 und ist kein Mangel: vor „fehlt“ dort nachsehen; wird eine weggelassene Datei gebraucht, beim Inhaber anfordern.
Der Arbeitsstand steht nur in der Aufgabe des Inhabers und in der letzten Lieferung; fehlt beides, nachfragen. Eine leere `aufgabe` (0 Byte) ist gewollt: Es gibt keinen Altbestand, der Arbeitsstand steht dann nur in der Nachricht des Inhabers. Die Datei `aufgabe` im Zip-Stamm (`python3 -I testscripte/zip_entpacken.py -p <zip> aufgabe`) hält Notizen zum Arbeitsstand beim Packen (mit Datum); eine neuere Nachricht oder hochgeladene `aufgabe` geht vor, bei Widerspruch nachfragen. `Assembler/projekdetails` wird bei jedem Lauf überschrieben und zählt nicht.
