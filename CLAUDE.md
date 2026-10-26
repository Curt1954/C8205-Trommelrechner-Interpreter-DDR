# C 8205 – Karte für Claude (zuerst lesen)

Version: 0.01-020
Geprüft am 23.10.2026 gegen Zip 0.95.1 Claude unter Python 3.11, 3.12 und 3.13: Selbsttest, Minimalbeispiel, alle hier genannten Dateien vorhanden, alle Tests in rund 12 s ohne Fehler.

**Projekt:** Simulator des DDR-Kleinrechners Cellatron C 8205 (1968): Python-Interpreter `c8205_interp.py`, Assembler `c82ass` (C, Quelltext in `Assembler/Sourcecode/`), Einadreßmaschine mit Magnettrommel (4096 Worte zu 33 Bit). Dokumentation und Antworten sind deutsch; die Dokumentation ist maßgeblich.

## Zuerst

- Das Zip **nicht** mit `unzip -l` auflisten (über tausend Einträge, meist erzeugt). Diese Karte: `unzip -p <zip> CLAUDE.md`. Gezielt suchen: `unzip -Z1 <zip> '*muster*'`; eine Datei lesen: `unzip -p <zip> <pfad>`. Sonst entpacken (Schnellstart) und mit `grep`/`find` suchen.
- Vom Handbuch `C8205-Programmierhandbuch_fuer_Claude.md` nur den Abschnitt lesen, den die Aufgabe braucht (Tabelle unten). Begriffe (AC, BZ, V1/V2, KEP, BIS …): Handbuch Abschnitt 10 (Suchkarte).

## Umgebung (Claude-Sitzung in der Cloud)

- Eigener, privater Linux-Arbeitsbereich; Python 3 (3.11, 3.12 und 3.13 geprüft; der Inhaber nutzt 3.11, also nichts verwenden, was erst ab 3.12 geht), keine Pakete nötig, kein Netz nötig. `gcc`/`make` nur zum Neubau des Assemblers. Befehle laufen nur dort, nie auf dem Rechner des Nutzers. Windows-Bau (MinGW-w64, `bau_trommel_mingw.bat`, `bau_ztmodul_mingw.bat`) und Windows-Test des C-Moduls laufen beim Inhaber, nie in der Cloud-Sitzung; Windows-Angaben in der Doku stammen aus seinen Meldungen (Beschreibung §9.2).
- Das Zip liegt dort, wo die Aufgabe es nennt (meist `/mnt/user-data/attachments/<id>/` oder `/mnt/user-data/uploads/`). Diesen Pfad überall einsetzen, wo unten `<zip>` steht. In einem **neuen, leeren Ordner im Arbeitsverzeichnis** entpacken, nicht neben dem Zip.
- Ergebnisse kommen nach `/mnt/user-data/outputs/` und werden mit dem Sendewerkzeug der Sitzung an den Nutzer geschickt (`SendUserFile` oder `present_files`, je nachdem, was vorhanden ist).
- Vorbereitung und Selbstprüfung (im Projektstamm des entpackten Zips):
```
export LC_ALL=C.UTF-8            # vor jedem unzip und jedem Lauf (Falle 3)
python3 -V; test -x Assembler/_Linux/c82ass && echo asm-ok
python3 -I c8205_interp.py --MODUS=TEST Tests/trommel-001_leer.txt   # endet mit „Test wahr“
```

## Zip-Stamm

`CLAUDE.md`, Handbuch `C8205-Programmierhandbuch_fuer_Claude.md`, `README.md`, `Regressionstest.zip` · `c8205_interp.py` Interpreter, `c8205_grafik.py` + `grafik-interpreter-module/` + `c-module/` GRAFIK · `Assembler/` (`_Linux/c82ass` fertiges Binary, `Sourcecode/`, `Dokumentation/` mit der maßgeblichen `.odt`, Vorlagen in `Claude/`, `Claude_bsp_reassemblierung/`) · `Tests/` (über 150 fertige Tests), `Test-Ergebnisvergleiche/`, `Test-virtuelleGeraete/` (nicht löschen), `Trommel/trommel.txt` · `markdown-dateien/` (Doku, Anhänge A und B, Versionierung), `testscripte/`, `Testausfuehrungen/` (Skripte `testwahl.sh`, `kep_test.sh`, `interpreter_test.sh`, `bis_test.sh`; sie wechseln selbst in den Projektstamm), `Hilfsprogramme/`, `Bausteininterpretiersystem BIS/`. Vollständig: `markdown-dateien/C8205-Projektstruktur.md`.

## Regeln des Projektinhabers

- **Assembler-Binary** liegt fertig in `Assembler/_Linux/c82ass`. Neubau nur nach einer Änderung am C-Quelltext (`cd Assembler && ./make_c82ass.sh`) und für eigene Tests; **nie zum Download stellen** (der Inhaber baut selbst).
- **Skripte** (`.sh`, `.bat`, `.py`) darf ich anpassen oder neu schreiben; jedes neue oder geänderte **immer in die Lieferung**.
- **Nachfragen, nicht raten:** bei unleserlicher Vorlage, bei Widerspruch zwischen Quellen, bei Build-Überlauf (999) und wenn Haupt- oder Unterversion steigen müsste (die erhöht nur der Inhaber). Sonst ohne Rückfrage arbeiten und Annahmen in einer Zeile nennen. Für den Assembler gilt die `.odt` vor jeder `.md`.
- **Versionen:** Jede geänderte versionierte Datei (alle `.md`, `c8205_interp.py`, Assembler-`.odt`, `c82ass`) erhöht ihren **Build** (`zzz` in `y.xx-zzz`) einmal je Lieferung um 1, in der Zeile `Version:` im Kopf; unveränderte Dateien behalten ihre Nummer. Einzelheiten: `markdown-dateien/C8205-Versionierung.md`, Abschnitte 2 und 3. Die Zip-Version steht im Dateinamen.
- **Abgabe** (auch jeder Checkpoint nach etwa 10 Minuten): immer **eine Zip-Datei** mit Projektpfaden (z. B. `Assembler/Claude/mini/mini.asm`). Packen im Projektstamm: `bash lieferung_packen.sh --seit <zip>` (mit `bash`, das Skript ist im Zip nicht ausführbar; nimmt alles Neue und Geänderte; ohne `--seit` mit Dateiliste). **Erst `-l`** (zeigt nur an) und Ungewolltes vorher löschen: der Packer nimmt auch erzeugte `.dmp` mit. Ist ein anderes Skript „Permission denied“, ebenfalls mit `bash` aufrufen. Ergebnis `C8205_Lieferung_NNN.zip` in `/mnt/user-data/outputs/`; nur die neueste senden, keine Einzeldateien daneben. Inhalt: `.asm`, `.test` (mit Prüfung), Soll-Dateien, neue oder geänderte Skripte und versionierte Dateien. Binaries verweigert das Skript.
- **Fertig heißt:** Test wahr (Rückgabecode 0), Lieferungs-Zip gesendet, Annahmen in einer Zeile genannt.
- **Dateiformat:** `.asm` und `.test` sind UTF-8 mit LF, Kommentar in jeder Zeile (deutsch), Zahlen oktal.

## Schnellstart (neuer, leerer Ordner)

```
export LC_ALL=C.UTF-8; unzip -q <zip>
Assembler/asm_und_test.sh <ordner_mit_asm> <n> [AAAA=WERT ...]   # assemblieren, .test ergänzen, testen (von überall)
# oder einzeln:
cd Assembler && ./c82ass.sh -p <ordner_mit_asm> -s <n>.asm --WARN=ALLE --no-color   # nur aus Assembler/; rc 0 = fehlerfrei
cd ..        && python3 -I c8205_interp.py --MODUS=TEST <ordner_mit_asm>/<n>.test    # aus dem Projektstamm
```
Rückgabecodes Interpreter: 0 Test wahr · 4 ohne Prüfung · 6 Test falsch · 8 Laufzeitfehler · 16 formale Prüfung negativ · 2 Aufruf falsch. Assembler: 0 fehlerfrei, 16 Fehler.
Alle Tests: `testscripte/compute_all_tests.sh` (rund 10 s).

**Minimalbeispiel** (geprüft, Quelltext in `Assembler/Claude/mini/mini.asm`; kopiert Zelle 0001 nach 0002):
`Assembler/asm_und_test.sh Claude/mini mini 0001=00000000017 0002=00000000017` → „Test wahr“, rc 0 (die Warnung „Symbol 'ende' … nie verwendet“ ist normal). Sollwerte (Adresse 4, Wert 11 Oktalziffern) vorher von Hand herleiten.

**Bei rc 6 oder 16:** zuerst die von Hand hergeleiteten Sollwerte und den Befehlscode prüfen (Falle 4), erst danach den Interpreter verdächtigen.

## Vier Fallen

1. Die vom Assembler erzeugte `.test` enthält **keine Prüfung** (rc 4). `asm_und_test.sh` ergänzt sie; von Hand nach Handbuch Abschnitt 0.
2. Die Trommel ist persistent, `Trommel/trommel.txt` wird bei jedem Lauf verändert: im Test `#TROMMEL=LEER` setzen (Handbuch Abschnitt 7).
3. Ohne `LC_ALL=C.UTF-8` entstehen Dateinamen wie `…#U00e4…`, und der Interpreter bricht mit „Knotengraph nicht gefunden“ ab (Handbuch Abschnitt 2).
4. **Nie raten:** Befehlscodes erst in Handbuch Abschnitt 4.1 nachsehen (häufig verwechselt: `211` lädt, `210` addiert, `240` speichert, `020` hält); Registerwerte (BZ, AR, V1/V2) nicht schätzen, sondern `US=1` plus Ergebniszellen prüfen (Abschnitte 7 und 8). Ein Test fängt Vertauschungen nur, wenn die Sollwerte vorher von Hand hergeleitet wurden.

## Welche Aufgabe, was lesen?

| Aufgabe | Lesen |
|---|---|
| Assemblerprogramm schreiben und testen | Handbuch Abschnitte 3 bis 9 **ganz lesen** (das Handbuch ist nur rund 3400 Wörter lang; Abschnitt 9 sind die bekannten offenen Punkte); Vorlagen in `Tests/`, `Assembler/Claude/`, `Assembler/Claude_bsp_reassemblierung/` |
| Wirkung eines Befehlscodes klären | `markdown-dateien/C8205-Interpreter-Befehlsliste.md`, „Einzelbefehlsübersicht“ |
| Assembler (C-Quelltext) ändern | `Assembler/Sourcecode/`; danach Regressionstest (Handbuch Abschnitt 8, Schritt 7) |
| Interpreter (Python) ändern | `markdown-dateien/C8205-Interpreter-Python_Interpreter.md`; danach `testscripte/compute_all_tests.sh` |
| BIS (Minimalprogramm, Kennzeichen) | `markdown-dateien/C8205-Programmierhandbuch-Anhang_B_BIS_Anschluss.md` |
| Laufzeit, Trommelzeit, GRAFIK zur Zeitmessung | `markdown-dateien/C8205-Programmierhandbuch-Anhang_A_Trommelzeit_GRAFIK.md`; GRAFIK immer mit `--ohne-fenster --STUMM` |
| GRAFIK-Fenster, Pult oder Ton ändern | `markdown-dateien/C8205-Interpreter-GRAFIK_Beschreibung.md` (mit `grep -n`); dafür das **Gesamt-Zip anfordern** |
| Unbekannte Datei oder Begriff | Handbuch Abschnitt 10 (Suchkarte) |

## Die wichtigsten Skripte (Aufruf steht im Kopfkommentar)

`Assembler/asm_und_test.sh` assemblieren + testen · `Assembler/c82ass.sh` Assembler starten (nur aus `Assembler/`) · `Assembler/asm_alle.sh [Ordner]` alle `.asm` darunter, meldet nur Fehler · `Assembler/asm_aufraeumen.sh [--loeschen]` Erzeugtes entfernen (ohne Schalter nur Anzeige) · `bash lieferung_packen.sh` Lieferung packen · `c8205_zip_packen.sh` baut die Zips des Inhabers, **nie** für Lieferungen · `c8205_interpreter.sh` Interpreter-Wrapper · `testscripte/compute_all_tests.sh` alle Tests · `testscripte/c8205_befehlssweep.py` alle 512 Befehlscodes · `Assembler/Regressionstest/` (nach `unzip Regressionstest.zip`). Alles weitere, auch `.bat`: Handbuch Abschnitt 10.

## Zip-Fassungen und Arbeitsstand

Es gibt das Gesamt-Zip und die schlanke Claude-Variante (Name endet auf „Claude“). Was sie weglässt (PDFs, `README.en.md`, `pult/`, `ton/` …), steht in Handbuch Abschnitt 11 und ist kein Mangel: vor „fehlt“ dort nachsehen; wird eine weggelassene Datei gebraucht, beim Inhaber anfordern.
Der Arbeitsstand steht nur in der Aufgabe des Inhabers und in der letzten Lieferung; fehlt beides, nachfragen. Die Datei `aufgabe` im Zip-Stamm (`unzip -p <zip> aufgabe`) hält Notizen zum Arbeitsstand beim Packen (mit Datum); eine neuere Nachricht oder hochgeladene `aufgabe` geht vor, bei Widerspruch nachfragen. `Assembler/projekdetails` wird bei jedem Lauf überschrieben und zählt nicht.
