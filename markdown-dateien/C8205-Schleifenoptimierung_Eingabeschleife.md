** Schleifenoptimierung der Ziffern-Eingabeschleife (Lage auf der Trommel) **

Version: 0.01-002

Stand 08.11.2026. Gehört zum Taktprotokoll (`C8205-Interpreter-GRAFIK_Beschreibung.md` §7.11) und zum Auswertungsskript
`testscripte/grafik_takt_schleife.py`. Untersucht wird die Ziffernschleife des BIS-Minimalprogramms
`Assembler/Projekt_2/pj2-bis_minimalprogramm_v6.asm` (Anker 0064, Befehle `kz_dl` bis `kz_zn`, Adressen 0064 bis 0076).
**Nur Dokumentation:** Es wurde kein Programm und keine `.asm` geändert; die Ergebnisse sind gerechnet, noch nicht am
umgebauten Programm gemessen.

## 1 Ausgangslage

Messwert aus `taktfile.log` (FS751, `--trommelzeit schnell`, Anker 0064): Die Ziffernvariante V1 (11 Befehle) braucht in
allen 2391 Durchläufen genau **352 Takte**. Davon sind 76 Takte feste Phasenzeiten, **276 Takte Wartezeit** auf die Trommel.
Das Protokoll hat insgesamt 1 325 855 Takte (ab Start gerechnet).

## 2 Zeitmodell (aus `grafik_trommel.py` und dem Protokoll abgelesen)

- Zeit in Wortzeiten (Takten, 104 µs). Jede Phase kostet 1 Takt. Ein Trommelzugriff wartet, bis der Sektor der Adresse
  (untere 5 Bit) unter dem Kopf liegt; der Zugriff selbst kostet nichts. Sektorfolge `PERM` (physisch, oktal):
  `00 15 32 07 24 01 16 33 10 25 02 17 34 11 26 03 20 35 12 27 04 21 36 13 30 05 22 37 14 31 06 23`.
  **Aufeinanderfolgende Adressen liegen 5 Takte auseinander**, physisch benachbarte Sektoren 1 Takt.
- Ablauf je Befehlsart (aus den Zeilen des Protokolls): Laden, Speichern, Addieren, `011`: Holen (Wartezeit), III 1, IV 1,
  Operandzugriff (Wartezeit), I 1, II 1. `616` (Schieben über `nz_3`): wie vorher, dazu 2 Takte für die weiteren
  Schiebeschritte (Wartezeit 1 je Schritt auf den Folgesektor). `311`: III 1, erster Zugriff, IV 1, zweiter Zugriff auf
  dieselbe Zelle (dafür immer **31 Takte Wartezeit**, weil ein Takt vergangen ist), I 1, II 1. `170` nicht genommen:
  III 1, I 1, II 1. Sprung (`004`, `000`): III 1, IV 1, Knoten 63 1, II 1 (4 Takte, Phase I entfällt).
- **Prüfung des Modells:** Das Nachspiel aller 247 770 Zeilen des Protokolls mit diesen Regeln und der Sektorfolge ergibt
  an jeder Zeile genau die protokollierte Zeit (0 Abweichungen); der V1-Durchlauf ergibt 352.

## 3 Was verschiebbar ist

Fest: Operand von `011` (Tabelle `kz_tab` 0300, Sektor 00), Operand von `616` (`nz_3` 7671, Sektor 031: legt 3 Schiebeschritte
fest), die Zeit der `311` (31 Takte zweiter Zugriff). Frei wählbar sind die Sektoren der Befehle (nur aufeinanderfolgend,
solange kein Sprung dazwischen liegt; `004` und `000` springen ohnehin) und die Zellen `kz_a` (7634), `kz_d` (7635), `kz_z`
(7636). Ein eingefügter Sprung (`000`, 4 Takte) macht die Folgeadresse frei. Alle Zugriffe der anderen Varianten (V2 bis V12)
wurden in die Bewertung einbezogen (Gesamtzeit des Protokolls nachgespielt; bei B und C mit dem Eintrittssprung auf der
Zelle 0064, weil die Schleife ihre Stelle verlässt: 312 Eintritte über `kz_i`; bei A entfällt er).

## 4 Ergebnis

| Lage | V1 je Durchlauf | Protokoll gesamt | Änderung |
|---|---|---|---|
| Ausgangslage (0064 bis 0076, Zellen 7634 bis 7636) | 352 | 1 325 855 | – |
| **A** Befehle bleiben, nur drei Datenzellen versetzt | **256** | 1 079 072 | −18,6 % |
| **B** Befehle umgelagert, kein Sprung | 224 | 1 056 192 | −20,3 % |
| **C** Befehle umgelagert, ein Sprung hinter `211 kz_a` (0066) | 160 | 900 384 | −32,1 % |

Mehr als ein eingefügter Sprung bringt in der Rechnung nichts (weiter 160; die `311` mit ihren 31 Takten und die festen
Operandsektoren von `011` und `616` bestimmen den Rest).

**Lage A (ohne fremde Zellen zu berühren, empfohlen als erster Schritt):** Befehle bleiben auf 0064 bis 0076. Nur die Zellen
wandern (gerechnet in dieser Zuordnung): `kz_d` auf **0122**, `kz_a` auf **0123**, `kz_z` auf **0264**. Gleichwertig (gleiche
Zeit, gleiche Gesamtzeit): `kz_d` auf 0137 oder 0234, `kz_a` auf 0140, `kz_z` auf 7607. Alle genannten Zellen sind in
der Speicherbelegung (`.dmp`) des Programms frei. Nach der Rechnung bleiben von den 352 Takten 256: 76 feste Takte, 180
Wartetakte.

**Lage B und C (Sektorangaben, noch ohne Adressen):** Der erste Befehl `011 kz_tab` muss auf **Sektor 031** liegen
(Adresse xx31), die Befehle bis `004` aufeinanderfolgend (B: neun Zellen xx31 bis xx41; C: drei Zellen `011`, `240`, `211` auf
xx31 bis xx33, dahinter der Sprung auf xx34, dann `616` bis `004` als sechs Zellen auf Sektor 014 bis 021 oder 031 bis 036),
`240 kz_z` und `000 kz_dl` auf zwei aufeinanderfolgenden Sektoren (C: 002/003, 017/020, 025/026 oder 034/035). Datenzellen
(C): `kz_d` Sektor 024, `kz_a` Sektor 025, `kz_z` Sektor 026 oder 034; (B): `kz_d` 024 oder 027, `kz_a` 025 oder 005, `kz_z`
mehrere Sektoren (u. a. 006, 026, 027, 034, 035, 036). Der Eintritt von außen (Durchfall aus `kz_i` 0063) geht über einen
Sprung `000 kz_dl` auf der Zelle 0064 (4 Takte je Eintritt, in der Gesamtzeit enthalten).

**Warum B und C noch keine Adressen haben:** Das Programm belegt 0040 bis 0377 fast lückenlos (20 freie Zellen). B und C
brauchen 9 bis 12 zusammenhängende Zellen auf bestimmten Sektoren; mit den freien Zellen und den frei werdenden Zellen 0064 bis
0076 ist das nicht zu erfüllen. Die Datenzellen von B und C liegen auf Sektoren, deren Zellen der Spur 7600 im ZT-Loader
(7622 bis 7626) belegt sind. Für B und C muss anderer Code verschoben oder eine freie Spur benutzt werden: Entscheidung
des Inhabers.

## 5 Grenzen

- Das Ergebnis gilt für die Eingabe aus `taktfile.log` (FS751, schnell). Die Wartezeit auf das Zeichen im Eingabe-Halt ist nicht
  enthalten (virtuelle Zeit steht dort still).
- Gegenprobe gelaufen (siehe Abschnitt 6): Das umgebaute Programm v7 braucht je Ziffer 256 Takte, wie gerechnet.
- Frei in der `.dmp` heißt nicht frei auf der Trommel: Lücken (`spa`, `equ`) lassen den Trommelinhalt unberührt; ob geladene
  Bausteine dort Daten haben, ist zu prüfen.
- Die Zellen 7634 bis 7636 standen im Kopf des Programms und in den Kommentaren; in v7 sind Kopf und Kommentare angepasst (Abschnitt 6).
- Nicht untersucht: ein anderer Befehl statt `311 kz_z` mit `170` (er kostet allein mindestens 35 Takte).

## 6 Umsetzung in v7 und Gegenprobe (08.11.2026)

**Umsetzung.** `Assembler/Projekt_2/pj2-bis_minimalprogramm_v7.asm` ist v6 mit versetzten Arbeitszellen (Lage A, gleichwertige Zellen):
`kz_z` 7607 (Sektor 007), `kz_a` 7763 (Sektor 023), `kz_d` 7634 (Sektor 034). Die Befehle auf 0064 bis 0076 und alle Ansprungzellen
sind unverändert. Alle drei Zellen sind laut Abschnitt „Freie Zellen“ in `C8205-Interpreter-BIS.md` unbenutzt (7605 bis 7607, 7761 bis 7772);
7635 und 7636 werden frei. Die 35 Tests `Tests/pj2-bis_v7_*.test` laufen wie die 35 Tests von v6 fehlerfrei (Rückgabecode 0).

**Gegenprobe mit `--taktprotokoll`** (GRAFIK, `--trommelzeit schnell`, gleiches Lochband für v6 und v7: `0 0` und acht Ziffern `1 2 3 4 5 6 7 0`,
`.`, `:`; Auswertung `grafik_takt_schleife.py --befehl 0064 --takte`):

| Programm | Takte je Ziffernzyklus (V1, 11 Befehle) | Zyklen | vt am Ende des Bandes |
|---|---|---|---|
| v6 (Zellen 7634 bis 7636) | 352 | 8 | 4747 |
| **v7** (Zellen 7607, 7763, 7634) | **256** | 8 | 3947 |

Je Ziffer sind das 96 Takte weniger (−27 %). Die Rechnung aus Abschnitt 4 (256 für Lage A) ist damit bestätigt. Die Zahl −18,6 % in Abschnitt 4
bezieht sich auf das gesamte Protokoll `taktfile.log`, nicht auf die einzelne Ziffer.

**Nicht geprüft:** die Skripte `bis_test.sh`, `kep_test.sh`, `testwahl.sh` und `c8205_bis_test.sh` sowie die Lochstreifen (`.kep`) und die Ablage
unter `Lochstreifen/` nennen weiter v6; ob sie auf v7 umgestellt werden, entscheidet der Inhaber. Nicht auf Windows geprüft.
