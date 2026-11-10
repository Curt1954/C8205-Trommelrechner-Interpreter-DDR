# C 8205 – Programmierhandbuch für Claude, Anhang B: Das BIS-Minimalprogramm

Version: 0.01-007

Gehört zu `C8205-Programmierhandbuch_fuer_Claude.md` (Wurzel des Projekts). Nur lesen, wenn ein Programm an das BIS-Minimalprogramm anschließt (laufende Arbeiten).

Quelle: Quelltext `Assembler/Projekt_2/pj2-bis_minimalprogramm_v6.asm` (Stand 24.10.2026, 218 Worte, Code in 0040 bis 0377) und `Bausteininterpretiersystem BIS/markdown-dateien/C8205-Interpreter-BIS.md`, Abschnitte BIS-A.4 (Funktionen) und BIS-A.5 (Arbeitszellen). Die Ansprungzellen sind **fest**, der übrige Code darf verschoben werden. Es gibt **kein Hauptprogramm**; Zelle 0000 enthält den Sprung `000 0262` zur Eingabe eines Wortes mit Kennzeichen, Zelle 0001 den Sprung zum Druck von BZ und AC (Änderung 24.10.2026: 0000 war zuvor nicht belegt, das war falsch).

| Zelle | Bedeutung (v6) |
|---|---|
| 0001 | Sprung zum Druck von BZ und AC (`000 0223`); Tastenfolge `H G Ü E G M+ E M- R` |
| 0200 / 0220 / 0240 | Druck: `triadendruck` (11 Triaden), `adressdruck` (4), `befehlsdruck` (7). Aufruf `025 <einstieg>`, **Wort in R1 (7773)**, Kanal K2 vorher angewählt; R1 bleibt unverändert; Rückkehr über `td_rs` (7741) |
| 0262 | Eingabe eines Wortes mit Kennzeichen (springt nach `kz_anf` 0040), Kanal vom Aufrufer angewählt |
| 0263 | Eingabe eines Programmstückes (ebenfalls `kz_anf`) |
| 0316 | Adresseneingabe (`ae_anf` 0044); Ergebnis im AC |
| 7600 / 7601 | Leitbefehl `LB` (240 mit Hauptleitadresse + RA), Folgezelle mit Rücksprung |
| 7602 bis 7604 | `XW`: Sofortbefehl (K1 = 1), Stopp, Rücksprung |
| 7610 | 0. Leitadresse (immer 0); 7611 Hauptleitadresse; 7612 bis 7621 2. bis 9. Leitadresse (K2 = 2 bis 9) |
| 7630 bis 7636 | Arbeitszellen der Kennzeicheneingabe (`kz_rs`, K1, K2, K2s, Zahl, Ziffer, Zähler) |
| v7 (08.11.2026) | Takt-Optimierung der Ziffernschleife (256 statt 352 Takte je Ziffer, Quelltext `pj2-bis_minimalprogramm_v7.asm`, Code und Ansprungzellen wie v6): nur drei Arbeitszellen wandern, `kz_z` (Zähler) nach **7607**, `kz_a` (Zahl) nach **7763**, `kz_d` (Ziffer) nach **7634**; 7635 und 7636 sind damit frei, die Arbeitszellen der Kennzeicheneingabe liegen auf 7630 bis 7634. Alles andere in dieser Tabelle gilt unverändert auch für v7 |
| 7640 bis 7677 | Nullspur (für den Wiederholungsbefehl 616) |
| 7700 bis 7737 | Einsen-Spur des Drucks (wird überschrieben); 7717 Gruppenzähler |
| 7740 / 7741 / 7742 | Rückkehr Adresseneingabe / Rückkehr Druck / Relativadresse RA (Adresse · 01000) |
| 7743 / 7744 | Druck BZ und AC: Fortsetzungsbefehl / gesicherter AC |
| 7760 | Ziffernzähler des Drucks |
| 7773 | R1: Übergabezelle der Druckprogramme (feste Regel in v6) |
| 7777 | Transportzelle für den AC (vom Druck auch als Arbeitskopie benutzt) |
| 0400 bis 0477 | im Minimalprogramm frei (Anschlusszellen 403 bis 410, 430) |
| 7540 bis 7575 | Ansprungzellen Rechen-, Ausgabe- und Satzeingabeprogramme (Tabelle im BIS-Dokument, BIS-A.2) |

Nicht mehr vorhanden: Hauptprogramm (`haupt`/`neu`), `la_tab` ab 7724 mit Relativadresse 7735, `ps_ab` 7761/7762, Sofortbefehl 7705/7706 und `ae_tab` 0700 bis 0777. Die Zellen 7723/7724 gehören nur dem KEP (Leitbefehl, Hauptleitadresse des KEP).

**Anschlusszellen (203 bis 224, 403 bis 430, 7540 bis 7575): das zentrale Prinzip des BIS** (Festlegung des Inhabers 07.11.2026; ausführlich im BIS-Dokument, BIS-1.2). Standalone-Programme und einfache Testprogramme brauchen nur ihren Assemblercode. Im Praxiseinsatz werden vorher ein oder mehrere Bausteine über das Minimalprogramm geladen, zuletzt das zu testende Programm; die Bausteine liegen in gewissen Grenzen frei im Speicher. Damit das Programm die Unterprogramme findet, ohne ihre Lage zu kennen, gibt es Anschlusszellen mit **festen, dauerhaft definierten Adressen** (Tabellen BIS-A.1 und BIS-A.2; sie gelten auch für Bausteine, die noch nicht programmiert sind):

- **Baustein:** schreibt beim Laden in seine Anschlusszelle nur einen unbedingten Sprung auf den Beginn seines Unterprogramms, `000 <UP-Beginn>`.
- **Programm:** ruft das Unterprogramm über die Anschlusszelle auf, `025 <Anschlusszelle>`, nie über die tatsächliche Lage des Bausteins.
- **Baustein nicht geladen:** Die Anschlusszelle ist undefiniert; das koordiniert der Bediener des Rechners, das Programm prüft es nicht.
- Die **Adresse** der Zelle ist fest, ihr **Inhalt** ist ein Eintrag, den der Baustein beim Laden schreibt. Die Belegung durch Minimalprogramm-Code ist deshalb kein Fehler, solange der Baustein nur den Eintrag überschreibt, der ihm gehört.
- Das Minimalprogramm selbst liegt fest und braucht keinen Eintrag: Seine sechs Ansprungzellen sind 0200, 0220, 0240 (dort steht der Beginn des Unterprogramms) und 0262, 0263, 0316 (dort steht ein unbedingter Sprung nach `kz_anf` bzw. `ae_anf`).

Kennzeichen in v6: K1 = 0 Wort speichern · 1 Sofortbefehl · 2 Adresseneingabe (`2 1 aaaa .` Hauptleitadresse, `2 0 aaaa .` und `2 .` Relativadresse) · ZR neues K1 · `/` bedingter Stopp · `:` und BM Rückkehr. K1 = 3 bis 9, `+`, `B`, `D` haben keine Wirkung (Anschlusszellen für Eingabebausteine sind nicht belegt). Beim Pult sind `B` und `D` Tasten, nicht die Buchstaben des Schreibwerks (laut Projektinhaber).
