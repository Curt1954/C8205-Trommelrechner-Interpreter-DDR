# Checkpoint 4: Gesamtstand Zeitmessung Pult-Anzeige, HW-Check, Lampenabtastung und Haltzeit-Zeile (C 8205, Modus GRAFIK)

Stand: 20.10.2026. Dieses Dokument ist in sich geschlossen und ersetzt CP1 (`CHECKPOINT_Zeitmessung_Pult_HWCheck.md`), CP2 und CP3 als Einstieg. Neu gegenüber CP3: Auswertung der maximalen Verspätung (Abschnitt 8a), Haltzeit-Patch HZ-004 für den Einzelschritt (Abschnitt 13), aktualisierte offene Punkte. Grundlage: `projekt_C8205.zip`, `grafik_zeit_messung.py` (ZM-001), Messausgaben des Projektinhabers.
Kennzeichnung: *gelesen* (im Code gesehen), *gemessen*, *vermutet/Wissen* (nicht belegt).

---

## 1. Fragen des Projektinhabers
1. Sind Bedienpult-Anzeige und HW-Check-Fenster per Background-Thread realisiert?
2. Beeinflussen sie die Befehlsausführungszeit?
3. Kann der Lampenabtast-Thread so in den Hintergrund, dass er die Rechenzeit nicht beeinflusst? Übersprungene Anzeigezustände sind akzeptabel (beim echten Rechner auch).
4. Originalrechner: Befehlsausführung **0,2 bis 0,4 ms** (2 bis 4 Wortzeiten zu 104 µs).
5. Verhalten bei Ringpuffer-Vorschlag im Einzelschritt (E) und E/A-Halt, muss das exakt sein?
6. Würde "Lösung 3" (Anzeige in eigenem Prozess) alles umgehen?
7. Messskript → geliefert (ZM-001), Messungen liegen jetzt vor.
8. Zwischenfrage: Bis zu welcher Hardware "herunter" bleibt die Befehlszeit noch in etwa echt?

## 2. Ergebnis in Kurzform (Stand 20.10.2026)
- **Die Lampenabtastung stört die Befehlsausführung auf der Zielmaschine nicht messbar** (−0,5 % Zugriffe/s bei 5 Läufen à 10 s, innerhalb der Streuung der Grundlinie).
- **Pult-Takt, Tk und HW-Check kosten wenig:** −0,7 % (Tk-Aufbauten) bis −1,4 % (`tk_hw`) auf dem 24-Kern-Rechner ohne Pinning, mittlere Verspätung des Trommel-Threads unverändert ca. 5 µs.
- **Auf einem einzelnen Kern** (Prüfstand mit `taskset`, ungünstigster Fall) kostet `tk_hw` bis **−9,8 %** Zugriffe/s. Die mittlere Verspätung bleibt bei höchstens 11,5 µs, weit unter den ca. 50 µs, ab denen ein Zugriff eine Umdrehung verliert. **Kein Einbruch gefunden.**
- **Maximale Verspätung ungepinnt (5 × 10 s, alle Aufbauten): höchstens 1,3 ms, `tk`/`tk_hw` nicht höher als die Grundlinie** (Abschnitt 8a). Keine Ausreißer.
- Nach der Entscheidungsregel: **kein Umbau der Lampenabtastung nötig** (Weg 1, 2, C-Abtaster, Prozess-Lösung nicht erforderlich).
- **Haltzeit-Zeile:** im Einzelschritt (E) zeigte sie nur `---.- ms`; behoben mit HZ-004 (Abschnitt 13). Gemessene Schritte des Projektinhabers: 0,7 bis 2,9 ms bei Ausgabe-/Halt-Befehlen (Anzeige enthält die Trommelwartezeit, so gewünscht).

## 3. Threads (gelesen)
| Komponente | Thread | Fundstelle |
|---|---|---|
| Bedienpult-Anzeige (`PultFenster`) | **Tk-Hauptthread**, `root.after(LAMPENTAKT_S)` = 40 ms, `root.mainloop()` | `grafik_pult_fenster.py`: `takt()`, `starten()` |
| HW-Check (`HwCheckFenster`) | **gleicher Tk-Thread**, `tk.Toplevel(root)`, kein eigener Timer; Aktualisierung über `fenster.zusatz` aus `takt()` | `grafik_hwcheck.py`; Einhängen in `c8205_grafik.py` (`pult_betrieb`, `--HWCHECK`) |
| Rechner | Thread `rechner` (daemon), startet in `bei_betrieb()`, Rumpf `rechner_schleife()` (5 ms Pause) | `c8205_grafik.py` |
| Lampenabtastung | Thread `lampenabtastung` (daemon), alle `ABTAST_S` = 2 ms, Start in `PultSteuerung.tick()` beim Übergang nach BETRIEB (`starte_abtastung()`) | `grafik_pult.py` |
| Trommel | C-Thread im C-Modul, Sektorwechsel alle 104 µs, Takt aus Monotonic-Uhr | `c-module/trommel.h`, `trommel.c` |
| Wache | Thread `wache`, nur mit `--DEBUGLOG` | `c8205_grafik.py` |

`daemon=True` betrifft nur das Beenden, nicht die Priorität. Python hat keine Thread-Prioritäten (*Wissen über CPython*).

## 4. Wie die Zeit beeinflusst werden kann
- Jeder Trommelzugriff blockiert in Echtzeit bis der Sektor unter dem Kopf ist (0 bis 31 Wortzeiten). Kommt eine Anforderung zu spät, wartet sie bis zu eine Umdrehung (ca. 3,2 ms = 8 bis 16 Befehlszeiten) (*gelesen/abgeleitet*).
- Trommelaufrufe geben die GIL beim Warten frei (`Py_BEGIN_ALLOW_THREADS`). Pult-Takt, HW-Check und Abtast-Thread brauchen im selben Prozess dieselbe GIL wie der Rechner-Thread.
- Beeinflusst wird nur die Echtzeit, nicht das Rechenergebnis. Die Haltzeit-Anzeige (`grafik_haltzeit.py`, `time.monotonic()`) enthält den Einfluss.
- `sys.setswitchinterval` wird im Projekt nirgends gesetzt (Voreinstellung 5 ms): nach jedem Trommelzugriff kann der Rechner-Thread bis zu 5 ms auf die GIL warten, wenn ein anderer Thread Python-Code ausführt (*Wissen, hier nicht gemessen*).
- HW-Check liest `m.BZ`, `m.AC`, `m.AR`, `m.adr`, `m.OR` und den Trommelinhalt (`einblick()`, ohne Koinzidenz) **ohne Lock** (laut Docstring Absicht). Im Dauerlauf können Zeilenwerte aus leicht verschiedenen Momenten stammen, im Halt ist der Stand exakt.
- Kosten der Abtastung (*Schätzung, nicht gemessen*): `PultSteuerung._werte()` baut je Abtastung ein Dict mit ca. 35 Einträgen (viele f-Strings), `Mittelung.probe()` läuft unter Lock; bis zu etwa 500-mal pro Sekunde; im Halt ruft der Thread alle 2 ms unnötig `sofort()` auf. `MITTEL_FENSTER_S = 0.04`, `MITTEL_AN = 0.60`, `MITTEL_AUS = 0.40`.
- Korrektur einer früheren Aussage: Tcl-Aufrufe über `_tkinter` geben die GIL frei, nur der Python-Anteil des Takts hält sie.

## 5. Exaktheit bei Einzelschritt und E/A-Halt (gelesen, relevant nur falls umgebaut wird)
- `lampen()` benutzt gemittelte Werte nur, wenn `netz == BETRIEB` und `r.laeuft` wahr ist (`laeuft` wird nur in `lauf()` gesetzt).
- **Einzelschritt (E):** `leerlauf()` setzt nur `_schritt=True`, `laeuft` bleibt `False` → Anzeige liest `adr`, `OR`, Flags direkt aus `m` (exakt), unabhängig von der Abtastung.
- **Stopp, Fehler, H:** `lauf()` endet, `laeuft=False` im `finally` → exakt.
- **E/A-Halt im Dauerlauf:** Rechner wartet innerhalb von `lauf()`, `laeuft` bleibt `True` → Anzeige nutzt die Mittelung weiter. Bei Abtastung nur an Befehlsgrenzen gäbe es dort veraltete Werte. Lösung: Haken `m.k0.bei_halt`/`m.leser[k].bei_halt` = `_ea_halt` und `bei_weiter` (= `haltuhr.weiter`; `c8205_grafik.py`, ca. Zeilen 137 und 783): Markierung `ea_wartet` setzen/löschen; ist sie gesetzt, liest die Anzeige direkt aus `m`; Ringpuffer bei Start von `lauf()` leeren.
- **Nicht geprüft:** andere blockierende Wartestellen im Dauerlauf (Schreibwerk, Stanzer).

## 6. Lösungsvorschläge (derzeit nicht erforderlich)
| Weg | Inhalt | Aufwand/Risiko |
|---|---|---|
| 1 | Abtast-Thread bleibt, schreibt nur Rohwert `(m.adr, m.OR, dict(m.fl))` in Ringpuffer (ohne f-Strings, ohne Lock); Bit-Auszählung und Hysterese im Tk-Takt (40 ms); `ABTAST_S` 4 bis 5 ms; im Halt nicht abtasten | klein |
| 2 | Kein Abtast-Thread; Schnappschuss alle *n* Befehle an der Befehlsgrenze (`grenz_hook`, "vor Knoten 2"), ca. 1 bis 2 µs; Helligkeit = Befehlsanteil statt Wandzeit; `ea_wartet` nötig | klein bis mittel |
| C-Abtaster | Rechner schreibt je Befehl `adr`, `OR`, Flags in eine C-Struktur; C-Thread ohne GIL tastet alle 2 ms ab, zählt Treffer; Tk liest Zähler. Echte Zeitabtastung, keine GIL-Konkurrenz durch Abtastung; Aufwand in `trommel.c`; Kosten ca. 1 µs je Befehl (*Schätzung*) | mittel |
| Prozess-Lösung | Anzeige in eigenem Prozess (Shared Memory); einziger Weg ohne GIL-Konkurrenz zu Pult/HW-Check; Tasten, HW-Check, Ton, SW-Fenster, Hochlauf, Abbruch, Fensterlage müssten über die Prozessgrenze; Windows-Zweig (`spawn`) | hoch, Regressionsrisiko |
| zusätzlich | `sys.setswitchinterval(0.0001)` beim Start (ungetestet auf Zielmaschine; Option `--sw` im Messskript) | sehr klein |
| nicht empfohlen | nur im 40-ms-Takt abtasten ohne Zwischenwerte (Lampen flackern zufällig) | – |

Grenze aller Abtast-Wege: Pult-Takt und HW-Check bleiben im selben Prozess und konkurrieren um die GIL. Nur die Prozess-Lösung beseitigt das.

## 7. Messskript `grafik_zeit_messung.py` (ZM-001) und Messungen

Aufruf aus dem Projektordner (Skript liegt in `testscripte/`):
```
python3 testscripte/grafik_zeit_messung.py                          # alle Aufbauten, 5 s, 3 Wiederholungen
python3 testscripte/grafik_zeit_messung.py --dauer 10 --wiederholungen 5
python3 testscripte/grafik_zeit_messung.py --dauer 10 --sw 0.0001   # zusätzlich Switch-Intervall 0,1 ms
python3 testscripte/grafik_zeit_messung.py --varianten rechner,tk_hw
python3 testscripte/grafik_zeit_messung.py --liste
```
Aufbauten: `rechner` (Grundlinie) · `abtastung` · `takt_python` · `tk_ohne_abt` · `tk` · `tk_hw`. Jede Messung in eigenem Prozess (`-I`). Ergebnis als Tabelle und `testscripte/zeit_messung_ergebnis.csv`.

**Last:** trommeloptimale Endlosschleife aus 32 Befehlen auf 0000 bis 0037 (Sektor = `adresse & 0o37`; Trommel schaltet je Wortzeit um 13 Sektoren weiter, im Code "je +15 oktal"). Abwechselnd `211` (laden) und `240` (speichern), Operanden `0o3000 + ((i + 26) % 32)`, am Ende `000 0000` (Sprung). Operand 2 Wortzeiten nach dem Befehl, nächster Befehl 5 Wortzeiten danach. Trommel-Startlage fest (PERM-Index 0). Eine Verzögerung ab ca. 50 µs kostet 31 Wortzeiten, die Last ist empfindlich. Trommeldatei: `aaaa: ttttttttttt` (4096 Zeilen).
**Kennzahlen:** Zugriffe/s, Ø Wartezeit je Zugriff (Ticks = Wortzeiten), Ø Verspätung des Trommel-Threads (µs), max. Verspätung (nur in der CSV, noch nicht ausgewertet).
**Lesen:** weniger Zugriffe/s und mehr Wartezeit gegenüber `rechner` = Störung der Echtzeit.

### 7.1 Entwicklungsumgebung (1 Kern, Python 3.12, Linux x86_64, ohne Tk), gemessen
| Aufbau | Zugriffe/s | vs. Grund | Wartezeit |
|---|---|---|---|
| rechner (3719,9 / 3720,0 / 3707,5) | 3719,9 | – | 2,549 |
| abtastung | 3679,0 | −1,1 % | 2,571 |
| takt_python | 3707,5 | −0,3 % | 2,565 |
`--sw 0.0001` (je 2 Wiederholungen): Abweichungen ebenfalls unter 1 %. Nicht repräsentativ für Mehrkernrechner.

### 7.2 Zielmaschine des Projektinhabers
Hardware: **Intel i9-13900HX, 24 Kerne / 32 Threads** (laut `lscpu -e`): CPU 0 bis 15 = 8 P-Kerne mit Hyperthreading (CORE 0 bis 7, CPU-Paare 0/1, 2/3 … 14/15, bis 5,2 bzw. 5,4 GHz); CPU 16 bis 31 = 16 E-Kerne ohne Hyperthreading (CORE 8 bis 23, bis 3,9 GHz). Im Leerlauf takten viele Kerne bei 800 bis 2400 MHz. (Der Projektinhaber nannte "16 Kerne"; `lscpu` zeigt 24.) Python 3.11.4, Switch-Intervall 5 ms. Tk-Fenster sichtbar, Lampen zeigten das vom echten Rechner bekannte Wechseln.

**A) Alle Aufbauten, ungepinnt, 3 × 5 s:** rechner 3725,5 (Median) · abtastung −0,1 % · takt_python −0,3 % · tk_ohne_abt −0,3 % · tk −0,7 % · tk_hw −0,7 %; Verspätung überall ca. 5 µs.

**B) Alle Aufbauten, ungepinnt, 5 × 10 s (belastbarste Reihe):**
| Aufbau | Zugriffe/s (Median) | vs. Grund | Wartezeit (Ticks) | vs. Grund | Verspätung µs |
|---|---|---|---|---|---|
| rechner (Einzelwerte 3714 bis 3742) | 3737,0 | – | 2,516 | – | 5,1 |
| abtastung | 3719,2 | −0,5 % | 2,511 | −0,2 % | 4,9 |
| takt_python | 3737,2 | 0,0 % | 2,515 | −0,1 % | 5,1 |
| tk_ohne_abt | 3710,4 | −0,7 % | 2,497 | −0,8 % | 5,1 |
| tk | 3709,2 | −0,7 % | 2,496 | −0,8 % | 5,2 |
| tk_hw | 3686,4 | −1,4 % | 2,501 | −0,6 % | 5,2 |
Rückgang `tk_hw` gegen Grundlinie ca. 4 µs je Zugriff; Wartezeit steigt nicht. Die Tk-Aufbauten liegen meist knapp unter dem tiefsten Grundlinienwert → kleiner, wahrscheinlich echter Effekt (Tk bzw. HW-Check).

**C) Reservestufen `rechner,tk_hw`, je 3 × 10 s, mit `taskset` auf einen Kern** (ungünstigster Fall: der ganze Prozess auf einem Kern). Zuordnung der Stufen 2 bis 4 aus der Reihenfolge der Ausgabe (aus Konsolenausgabe abgeleitet; Stufe 1: nur die Kommentarzeile "# 1. Referenz: ein P-Kern-Thread" wurde mitgeschickt, vermutlich `taskset -c 0`).
| Stufe | Aufbau | rechner Zugriffe/s | tk_hw Zugriffe/s | vs. Grund | Wartezeit rechner / tk_hw | Verspätung µs rechner / tk_hw |
|---|---|---|---|---|---|---|
| 1: P-Kern CPU 0, Partner frei | | 3715,5 | 3476,2 | **−6,4 %** | 2,573 / 2,701 (+5,0 %) | 4,6 / 8,4 |
| 2: P-Kern CPU 0, Partner CPU 1 mit Lastprozess | | 3786,0 | 3745,7 | −1,1 % | 2,540 / 2,554 (+0,6 %) | 1,6 / 2,6 |
| 3: E-Kern CPU 16 allein | | 3784,9 | 3414,4 | **−9,8 %** | 2,538 / 2,633 (+3,7 %) | 5,5 / 11,5 |
| 4: E-Kern CPU 16 mit Lastprozess | | 3786,0 | 3626,0 | −4,2 % | 2,540 / 2,632 (+3,6 %) | 2,1 / 3,5 |

## 8. Auswertung
- **Abtastung:** kein messbarer Einfluss auf der Zielmaschine (−0,5 %, innerhalb der Grundlinienstreuung von ca. 1 %).
- **Tk/HW-Check:** auf dem Mehrkernrechner −0,7 bis −1,4 %; gepinnt auf einen Kern −1,1 bis −9,8 %. Größter Wert (E-Kern allein) ca. 29 µs mehr je Zugriff (264 → 293 µs), davon ca. 0,1 Wortzeiten längere mittlere Wartezeit, Rest zusätzliche Rechenzeit durch Tk/HW-Check.
- **Kein Einbruch:** die mittlere Verspätung des Trommel-Threads bleibt in allen Stufen ≤ 11,5 µs, deutlich unter der Verlustgrenze (ca. 50 µs). Wartezeit je Zugriff steigt höchstens um 5 %. Die Befehlszeit bleibt in der Größenordnung 0,2 bis 0,4 ms.
- **Auffällig, Ursache nicht belegt:** Stufen 2 und 4 (mit Lastprozess auf demselben bzw. Partnerkern) sind *besser* als 1 und 3, obwohl mehr Last läuft; die Grundlinie ist dort mit 3786,0 Zugriffe/s in allen Läufen praktisch identisch, die Verspätung kleiner. **Vermutung** (*nicht gemessen*): Die Lastprozesse halten den Kern wach und hoch getaktet; ohne sie taktet der Kern im fast wartenden Rechner-Thread herunter und muss hochschalten. Prüfung: Governor `performance` (`sudo cpupower frequency-set -g performance`, danach zurücksetzen) und Stufe 1 und 3 wiederholen.
- Hinweis: Eine frühere Erwartung ("Stufe 2 bis 4 werden schlechter") hat sich nicht bestätigt.

## 8a. Maximale Verspätung des Trommel-Threads (CSV-Auswertung, gemessen)

`max_verspaetung_us` ist die größte Verspätung **seit Programmstart** (inklusive Anlauf und 1 s Einlauf), nicht nur im Messfenster. Das Skript überschreibt die CSV bei jedem Aufruf: nach dem Lauf sichern (`cp testscripte/zeit_messung_ergebnis.csv testscripte/zeit_messung_ungepinnt.csv`).

**Reihe 1 (nur die letzte gepinnte Messung, Stufe 4: E-Kern CPU 16 mit Lastprozess auf demselben Kern):** rechner 13,1 / 17,2 / 14,4 ms; tk_hw 28,3 / 10,6 / 11,2 ms. Grundlinie und `tk_hw` gleich hoch → vermutlich Scheduler-Rauschen durch den Lastprozess auf demselben Kern, nicht Tk (*Vermutung*).

**Reihe 2 (ungepinnt, 5 × 10 s, alle sechs Aufbauten, parallel eine VMware mit SUSE und offenes Chrome; laut Projektinhaber "steht alles still", also vermutlich kaum Last):**
| Aufbau | Zugriffe/s (Median) | max. Verspätung je Lauf (µs) |
|---|---|---|
| rechner | 3731,8 | 1114 / 645 / 1032 / 752 / 636 |
| abtastung | 3736,9 | 631 / 195 / 634 / 1220 / 1294 |
| takt_python | 3732,1 | 651 / 618 / 1116 / 319 / 252 |
| tk_ohne_abt | 3709,1 | 1034 / 391 / 622 / 1042 / 1001 |
| tk | 3694,1 | 635 / 611 / 619 / 625 / 555 |
| tk_hw | 3692,9 | 1073 / 634 / 565 / 148 / 183 |
Keine Fehler, keine Warnungen. Maxima höchstens 1,3 ms (ca. 12 Takte), bei `rechner` so hoch wie bei den Tk-Aufbauten. Zugriffe/s gegen Grundlinie: abtastung +0,1 %, takt_python 0,0 %, tk_ohne_abt −0,6 %, tk −1,0 %, tk_hw −1,0 %.
**Lesart:** keine Ausreißer; ein Wert um 1 ms kann einzeln einmal eine Umdrehung kosten, passt zu den −0,6 bis −1,0 %. Die parallele VM erzeugte vermutlich keine echte Last; für eine belastbare "stört nicht bei Last"-Aussage wäre `--varianten rechner,tk_hw --dauer 10 --wiederholungen 3` unter echter Last (Video, CPU-Last) zu wiederholen (nicht nötig, die Reservestufen haben schon gezeigt, dass selbst ein einzelner langsamer Kern hält).
Mögliche Skripterweiterung (nicht umgesetzt): Maximum nur im Messfenster, Anzahl der Verspätungen über 50 µs (`nachgeholte_ticks`), CSV fortschreiben statt überschreiben.

## 9. Grenzen der Aussage
1. **Mittelwerte verdecken seltene Ausreißer.** Ausgewertet in 8a (höchstens 1,3 ms ungepinnt); die Spalte gilt seit Programmstart, die Anzahl einzelner Verspätungen kennen wir nicht. Erledigt, soweit für die Entscheidung nötig.
2. **Nicht gemessen: Lauf mit Bedienung** (Fenster ziehen, Größe ändern, Tasten, schnell wechselnde Lampen im HW-Check). Die Tk-Fenster waren bei der Messung sichtbar und die Lampen wechselten wie am echten Rechner, aber ohne Bedienung während des Laufs.
3. Die Last ist eine einzelne synthetische Schleife; Befehle mit viel Knotenarbeit und enger Trommelfolge sind kritischer. Die Reserve bei der Rechenzeit der Knoten ist **nicht** direkt gemessen, nur ob die Zugriffe den Sektor treffen. Der Übergang bei zu langsamer Hardware wäre abrupt (Umdrehung ca. 3,2 ms), nicht schleichend.
4. Tk-Aufbauten liefen erst auf dem Rechner des Projektinhabers real (in der Entwicklungsumgebung gab es kein Tkinter).
5. Andere blockierende Wartestellen im Dauerlauf (Schreibwerk, Stanzer) nicht geprüft.
6. **Windows nicht geprüft** (weder Zeitmessung noch Haltzeit-Patch): `spawn`-Zweig, Timer-Auflösung (Standard ca. 15 ms), Trommel-Echtzeit. Zuerst `grafik_zeit_messung.py` dort laufen lassen. Andere Python-Versionen nicht gemessen (Zielmaschine: 3.11.4, Entwicklungsumgebung: 3.12).

## 10. Nächste Schritte
1. **Windows:** `grafik_zeit_messung.py` (alle Aufbauten, `--dauer 10 --wiederholungen 5`) und die Pult-Tests dort laufen lassen; Timer-Auflösung und `spawn` prüfen. CSV sichern.
2. Patch HZ-004 (`patch_HZ-004.zip`) in den Projektstand übernehmen, falls noch nicht geschehen (Dateiziele siehe 13).
3. Optional: Governor-Test (Stufe 1 und 3 mit `performance`), Messung mit Bedienung, Skripterweiterung (siehe 8a), Haltzeit mit Intervall (min/max, siehe 13).
4. Nur bei tatsächlichen Einbrüchen auf der Zielhardware: Umbau der Abtastung gemäß Abschnitt 6; Prüfung mit `testscripte/grafik_pult_tests.py` und Vorher/Nachher-Messung; Versionsnummern hochzählen, Dokumentation nachführen.

## 11. Praktische Hinweise
- **Entpacken:** `unzip` verstümmelt Umlaute in Dateinamen (`Eingänge_der_Knoten.md` → `Eing#U00e4nge…`); mit Python entpacken (`zipfile.ZipFile(...).extract(...)`), sonst findet `lade_graph()` die Datei nicht.
- **C-Modul:** `c-module/python/c8205_trommel.abi3.so` lädt unter Linux x86_64 mit Python 3.12 (abi3).
- **Rechner ohne Fenster aufbauen** (Muster `testscripte/grafik_pult_stress.py`): `GrafikTrommel(kopie, start_index=0)`, `G.Rechner(G.lade_graph('markdown-dateien'), tr, pult_modus=True)`, `r.thread_modus=True`, Thread mit `G.rechner_schleife`, Tasten über `r.pult_taste('H'|'G'|'R')`.
- **Messstellen:** `tr.T.statistik()` liefert `ticks`, `aufwachen`, `nachgeholte_ticks`, `verspaetung_summe_ns`, `verspaetung_max_ns`, `zugriffe`, `wartezeit_summe_ticks`; `GrafikTrommel.wartezeit_summe` zählt aufruferseitig.
- **Fundstellen** (Zeilen ungefähr, hochgeladener Stand): `c8205_grafik.py`: `pult_taste` ~541, `leerlauf` ~566, `_ea_halt` ~644, `lauf` ~663, `rechner_schleife` ~788, `pult_betrieb` ~825 (`bei_betrieb` ~840, HW-Check ~954); `grafik_pult.py`: `LAMPENTAKT_S` 29, `MITTEL_*` 31 bis 33, `ABTAST_S` 34, `Mittelung` ~64, `tick()` ~172 (Abtaststart ~181), `_werte` ~349, `starte_abtastung` ~358, `lampen()` ~380; `grafik_pult_fenster.py`: `takt()` ~174; `grafik_hwcheck.py`: `hwcheck_zeilen`, `HwCheckFenster.aktualisieren`.
- `taskset` pinnt den ganzen Prozess (Rechner, Trommel-Thread, Tk, Abtastung) auf einen Kern; härter als ein schwacher Mehrkernrechner.

## 12. Offene Fragen an den Projektinhaber
1. Soll die Haltzeit-Zeile als Intervall (min bis max der letzten Schritte, z. B. `0.7 bis 2.9 ms`) erweitert werden? (Projektinhaber: wichtig ist die Befehlszeit als Ganzes bzw. ein Intervall; bisher Einzelwert.)
2. Falls später umgebaut wird: Helligkeit in Wandzeit oder in Befehlsanteilen (Weg 2)?
3. Weitere längere Wartestellen im Dauerlauf (Schreibwerk, Stanzer) neben K0 und Leser?
4. Ist ein Eingriff in `trommel.c` (C-Abtaster) grundsätzlich erlaubt?
5. Welcher Befehlsmix ist auf dem echten Rechner der kritischste (für eine realistischere Last)?

## 13. Haltzeit-Zeile im HW-Check, Patch HZ-004 (20.10.2026)

**Wunsch:** Die Zeile zeigt die Zeit zwischen zwei Halts: im Einzelschritt (E) einen Durchlauf der Befehlsschleife, bei R (Run) die Zeit vom letzten Halt bis zum nächsten Halt-Befehl, egal welcher. Gemeldet: es erschien nur noch `---.- ms`.
**Ursache (gelesen, nachgestellt):** `haltuhr.start()` wurde nur beim Tastendruck R aufgerufen; E startete keine Messung, und im Einzelschritt entsteht kein `m.halted`-Halt. Ohne Halt mit Bezug bleibt `stand = None` → `---.- ms`.
**Änderung:**
- `grafik_haltzeit.py` (jetzt **HZ-004**): `start(name='R')` mit Namen; Konstanten `SCHRITT = 'E'`, `SCHRITT_ENDE = 'Halt'`.
- `c8205_grafik.py` (`VERSION_GRAFIK` **G4-004**, Kopf bewusst `G2-004` wie in der Versionierung beschrieben): neue Methode `_schritt_start()`; `_e_taste()` startet die Messung vor `run_e_nieder()`/`run_e_los()` (einmal je Tastendruck, bei E beide zusammen) und beendet sie mit `halt(SCHRITT_ENDE)`, wenn der Schritt nicht im Stopp endet (sonst meldet der `halted`-Setter den Halt).
- Anzeige: `0.6 ms  E -> Halt`; Stopp/Fehler im Schritt: `E -> Stopp` / `E -> Fehler`; R weiter `R -> E/A-Halt`, `R -> Stopp`, `R -> Fehler`, `E/A-Halt -> ...`.
- Test `test_haltzeit_einzelschritt` in `testscripte/grafik_pult_tests.py`; 70 Tests laufen OK (Entwicklungsumgebung, ohne Tk).
- Doku: GRAFIK_Beschreibung §8.3 (Absatz Einzelschritt, Änderungskennung HZ-004) und Versionierung (Tabellenzeilen `grafik_haltzeit.py` HZ-004, `VERSION_GRAFIK` G4-004).
- Paket `patch_HZ-004.zip` (`c8205_grafik.py` → Projektordner; `grafik_haltzeit.py` → `grafik-interpreter-module/`; `grafik_pult_tests.py` → `testscripte/`; `C8205-Interpreter-GRAFIK_Beschreibung.md` und `C8205-Versionierung.md` → `markdown-dateien/`).
**Bestätigt vom Projektinhaber:** Anzeige funktioniert; Einzelschritt bei Ausgabe-/Halt-Befehlen 0,7 bis 2,9 ms. Plausibel: die Zeit enthält die Trommelwartezeit (0 bis 31 Wortzeiten, bis ca. 3,2 ms; Mittel rund 1,7 ms); die 0,2 bis 0,4 ms des Originals gelten für trommeloptimal gelegte Befehle. Bei Ausgabebefehlen kann zusätzlich Gerätewartezeit enthalten sein (nicht geprüft). Entscheidung: **Befehlszeit als Ganzes anzeigen**, keine Trennung in Rechen- und Trommelwartezeit (Zähler `GrafikTrommel.wartezeit_summe` gäbe es).
**Unverändert (bewusst):** Taste H zählt nicht als Halt (bei endlosem Programm bleibt die Zeile beim letzten Wert); die Wartezeit im Halt zählt nicht (HZ-003, `NUR_LAUF = True`; `False` gibt die Zeit mit Wartezeit).
**Nicht geprüft:** Verhalten im echten Tk-Fenster außer der Bestätigung des Projektinhabers; Windows.
