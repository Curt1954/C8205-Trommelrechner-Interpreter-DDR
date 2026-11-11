# C 8205 – Programmierhandbuch für Claude, Anhang A: Trommelzeit und GRAFIK-Interpreter

Version: 0.01-003

Gehört zu `C8205-Programmierhandbuch_fuer_Claude.md` (Wurzel des Projekts). Nur lesen, wenn Geschwindigkeit zählt. Kennzeichen **[geprüft]** wie dort.

Die logischen Sektoren liegen **nicht** nacheinander auf der Trommel. Die Zugriffsfolge ist
`00 15 32 07 24 01 16 33 10 25 02 17 34 11 26 03 20 35 12 27 04 21 36 13 30 05 22 37 14 31 06 23` (oktal, physisch).
Zeitoptimale Folgeadresse (Sektor, mod 040): Einzelbefehl `A+32` oder `A+07`, Gruppenbefehl auch `A+24`, Sprung `A+24`. Spurwechsel kostet nichts.
**Der TEST-Interpreter (`--MODUS=TEST`, mein Standardwerkzeug) rechnet alle Zeiten mit 0.** Dort kann ich Trommeloptimierung nicht messen, nur nachrechnen.
Der **GRAFIK-Interpreter** (`c8205_grafik.py`) bildet alle Geräte mit nahezu echten Zeiten nach . **Ich kann ihn ohne Fenster und ohne Ton starten** **[geprüft]**; `tkinter` fehlt in meiner Arbeitsumgebung, wird mit `--ohne-fenster` aber nicht gebraucht:

```
cd <Projektstamm>           # ohne -I, sonst findet er c8205_interp nicht
python3 c8205_grafik.py --ohne-fenster --STUMM --trommelzeit echt \
        --trommel <eigene_trommel.txt> --entwickler-tasten "H G R"
```

- `--trommel` nimmt eine vollständige Trommeldatei (4096 Zeilen `aaaa: ttttttttttt`). Aus der `.test` des Assemblers erzeuge ich sie mit einem kleinen Skript (nicht die Standardtrommel überschreiben).
- `--entwickler-tasten "H G R"` bedient das Pult (mit `--ohne-fenster` ohne Fenster, wie hier; ohne diesen Schalter öffnet sich seit G4-026 das Pult-Fenster, und die Tasten folgen nach dem Hochlauf), `--entwickler-k0 DATEI` legt K0-Zeichen in die Warteschlange, `--leser1`, `--leser2`, `--stanzer1` wie im TEST-Interpreter. Weitere Schalter: `--AUFZEICHNUNG`, `--WIEDERGABE` (Klickspur, wirken nur mit Pult-Fenster), `--DEBUGLOG`, `--pult-protokoll`, `--netz-schnell`.
- `--trommelzeit`: `schnell` = virtuelle Zeit ohne Warten, `echt` = virtuelle Zeit mit Wortzeit 104 µs je Phase und Echtzeit-Anpassung, `alt` = Wartezeiten nach der Wanduhr (Standard). Alle drei sind wählbare Zeitmodelle (`markdown-dateien/C8205-Interpreter-GRAFIK_Beschreibung.md`, „Zeitmodelle und Zähler der Trommelstatistik“).
- Die Endzeile entspricht der des TEST-Interpreters. Danach folgt eine Trommelstatistik; die Bedeutung der Zähler steht in derselben GRAFIK-Beschreibung (Abschnitt „Zeitmodelle und Zähler der Trommelstatistik“). Beim Summenprogramm (Handbuch, Abschnitt 5.2) ergab `echt` 1549 Takte, davon `wartezeit_summe_ticks_aufrufer` 1358 **[geprüft]** (die Werte streuen leicht von Lauf zu Lauf).
- Der Lauf prüft **nichts** selbst (keine `Prüfungen:`). Ergebniszellen lese ich danach aus der Trommeldatei.

- **Takte einer Schleife messen** (Beschreibung §7.11, Prüfverfahren §7.9): Mit `--trommelzeit echt|schnell` und `--taktprotokoll takt.tsv` schreibt GRAFIK jede Zeitfortschreibung in eine Textdatei (ohne den Schalter ändert sich nichts; mit `alt` Rückkehrcode 16). Danach `python3 testscripte/grafik_takt_schleife.py takt.tsv --liste` (Anker finden) und `--befehl <Adresse> --takte` (Takte je Zyklus; ein Befehl zählt von Phase III bis Phase III des Folgebefehls, Wartezeit eingeschlossen). Eingabe-Halt zählt nicht mit. Messwert und gerechnete Lage der Ziffernschleife: `markdown-dateien/C8205-Schleifenoptimierung_Eingabeschleife.md`. Auf einer Trommelkopie arbeiten.
Einzelheiten: `markdown-dateien/C8205-Interpreter-GRAFIK_Beschreibung.md` (bei Bedarf gezielt lesen).
Die Zahl „23" und „00" beim W-Befehl widersprechen sich in `markdown-dateien/C8205-Interpreter-Befehlsliste.md` nur scheinbar: Logischer Sektor 23 ist der physisch letzte, danach folgt wieder 00.
