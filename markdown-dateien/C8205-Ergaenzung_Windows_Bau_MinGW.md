# Ergänzung für die Gesamtdokumentation: Windows-Bau mit MinGW-w64

Stand: 26.10.2026. Zum Einfügen durch Claude; die Datei selbst gehört nicht ins Zip.

## Hinweis zum Einfügen

| Ziel | Was tun |
|---|---|
| `GRAFIK_Beschreibung` §9.2 | Die Sätze „Alles, was Windows betrifft, ist ungebaut und ungetestet …“ und „Compiler: … Offen sind `-static` …“ durch Abschnitt 1 und 2 unten ersetzen. Abschnitt 3 bis 5 als neue Unterabschnitte 9.2.1 bis 9.2.3 anfügen. |
| `GRAFIK_Beschreibung` §7.4 | Im letzten Absatz „Alles ungebaut und ungetestet“ durch den Satz aus Abschnitt 6 ersetzen. |
| `GRAFIK_Beschreibung` §10.1 und Tabelle OP-01 | Status laut Abschnitt 6 nachführen. |
| `GRAFIK_Pruefverfahren` §9 | Abschnitt 1 als belegtes Ergebnis aufnehmen, Abschnitt 5 als offene Punkte. |
| `CLAUDE.md`, Umgebung | Ein Satz: Windows-Bau und Windows-Test des Moduls laufen beim Inhaber, nie in der Cloud-Sitzung. |

Nach den Projektregeln erhöht jede geänderte versionierte `.md` ihren Build um 1. Die Dateien `plattform.h`, `bau_trommel_mingw.bat`, `bau_ztmodul_mingw.bat`, `c8205_grafik.py`, `grafik-interpreter-module/grafik_tonmisch_c.py` und `testscripte/grafik_stufe4_tests.py` kommen in die Lieferung (Skripte und Quelltext, die geändert wurden).

## 1 Ergebnis (26.10.2026, Rechner des Projektinhabers)

| Baustein | Bau | Laden | Test |
|---|---|---|---|
| `c8205_trommel.pyd` (Trommel, Bahnsperre, Unterbrechung, Tonmischer) | gebaut mit MinGW-w64 | `import c8205_trommel` ok | `test_c8205_trommel.py`: 23 Tests, OK, 1 übersprungen |
| `c8205_ztmodul.pyd` (Zusatztrommeln, C8205Z) | gebaut mit MinGW-w64 | `import c8205_ztmodul` ok | kein Python-Test vorhanden |
| GRAFIK-Interpreter (`c8205_grafik.bat`, Start aus `neu\`) | – | startet; Startzeile „Hinweis: Toene unter Windows ueber den Mischer (winmm).“ | Töne vom Inhaber **gehört**: Grundgeräusch, Lochbandleser (LL) und Stanzer (LS) über den C-Mischer mit `winmm` |

Umgebung: Python 3.13, 64 Bit (`...\Python313`), `gcc` aus MSYS2 `mingw64` (`gcc -dumpmachine` meldet `x86_64-w64-mingw32`; die gcc-Version wurde nicht festgehalten).

Der übersprungene Test ist der SIGINT-Test (`test_c8205_trommel.py`, Zeile 81); er ist unter Windows absichtlich ausgenommen. Die Meldung `trommel_einschalten: Dateigroesse 69632, erwartet 73728 …` mitten im Lauf gehört zum Test, der eine Datei im alten 17-Byte-Format (4096 × 17 = 69632) anlegt und deren Abweisung prüft (`TrommelFehler`, Zeilen 70 bis 73). Sie erscheint auch unter Linux und ist kein Fehler.

**Ton unter Windows (Beobachtung des Inhabers, 26.10.2026):** Beim Start von `c8205_grafik.bat` erscheint die Zeile „Hinweis: Toene unter Windows noch nicht ueber den Mischer (winmm fehlt): nur Rechnertoene (winsound) und Schreibwerkzeit.“ Die Töne waren hörbar. Sie kommen aber aus dem Stufe-2-Zweig (`os.name == 'nt'` in `c8205_grafik.py`, Klasse `RechnerTon` in `grafik_ton.py`, `winsound`, ein Klang zur Zeit). Der C-Mischer `tonmisch` mit `winmm` wurde damit **nicht benutzt**, weil dieser Zweig ihn umging; Leser- und Stanzerton waren dort aus. Das Hören belegt also `winsound`, nicht den Mischer.

**Änderung danach (26.10.2026):** `c8205_grafik.py` prüft unter Windows zuerst mit `grafik_tonmisch_c.winmm_verfuegbar()`, ob das C-Modul mit `ton_*`-Methoden lädt und `winmm` sich öffnen lässt. Dann läuft derselbe Aufbau wie unter Linux (Pult-, Schreibwerk-, Leser- und Stanzerton über den C-Mischer; Senke `CWinmmSenke`, `neuer_mischer_winmm()`), und die Hinweiszeile entfällt. Sonst gilt der alte `winsound`-Zweig mit der Hinweiszeile. Mit `--STUMM` wird `winmm` nicht geprüft. Fällt `winmm` im Betrieb aus, gilt wie unter Linux Code 16. **Ergebnis:** Der Inhaber hat danach Grundgeräusch, Leser- und Stanzertöne gehört (Mischer mit `winmm` aktiv, Startzeile wie oben). Schreibwerkton, Lücken und Lautstärken (`--TON`) wurden nicht gemeldet und gelten als nicht geprüft.

Linux: Beide Module bauen mit der geänderten `plattform.h` unverändert; `test_c8205_trommel.py` läuft unter Linux mit 23 Tests ohne Auslassung und ohne Fehler (Python 3.12 in der Cloud-Sitzung, Build mit `gcc`, nicht mit `setup.py`). Die Änderungen stehen nur im `_WIN32`-Zweig und in `.bat`-Dateien.

## 2 Bauen unter Windows

Voraussetzungen: ein **64-Bit**-MinGW-w64 (MSYS2 `mingw64` oder gleichwertig) und ein 64-Bit-Python mit der Bibliothek `libs\python3.lib` (Standardinstallation von python.org). Ohne Setuptools:

```
set PATH=C:\Users\<name>\AppData\Local\Programs\Python\Python313;C:\msys64\mingw64\bin;%PATH%
gcc -dumpmachine                                   (muss x86_64-w64-mingw32 ausgeben)
cd <projekt>\c-module\python
bau_trommel_mingw.bat                              (ergibt c8205_trommel.pyd)
cd <projekt>\C8205Z\zt_modul\python
bau_ztmodul_mingw.bat                              (ergibt c8205_ztmodul.pyd)
python -c "import c8205_trommel; print('ok')"
python test_c8205_trommel.py
```

Beide Skripte rufen `gcc` mit `-shared -O2 -std=gnu11 -DPy_LIMITED_API=0x03080000 -D_WIN32_WINNT=0x0601 -DWINVER=0x0601 -static-libgcc`, binden gegen `python3.lib` und `winmm` und lesen den Python-Ordner über `sysconfig` und `sys.base_prefix`. Das `set PATH` gilt nur für das offene Terminalfenster.

## 3 Fehlerbilder und Abhilfe

| Meldung | Ursache | Abhilfe |
|---|---|---|
| `unknown type name 'CONDITION_VARIABLE'`, danach implizite Deklarationen von `InitializeConditionVariable`, `WakeAllConditionVariable`, `SleepConditionVariableCS`, `YieldProcessor` | MinGW setzt sonst eine Windows-Zielversion unter Vista (`_WIN32_WINNT` 0x0502) und `windows.h` blendet diese Deklarationen aus | `-D_WIN32_WINNT=0x0601 -DWINVER=0x0601` im gcc-Aufruf der `.bat` (maßgeblich, weil `Python.h`, `bahnsperre.c` und `unterbrechung.c` `windows.h` selbst einbinden); zusätzlich setzt `plattform.h` die Werte vor `#include <windows.h>` und definiert `YieldProcessor` als `pause`, falls der Header es nicht liefert |
| `Recognised but unhandled machine type (0x8664) in Import Library Format archive` | Der gefundene `gcc` ist der alte 32-Bit-MinGW von mingw.org (`c:/mingw`, Pfad `mingw32/6.3.0`); `python3.lib` ist 64 Bit | 64-Bit-MinGW-w64 vor den alten in `PATH` setzen; `gcc -dumpmachine` prüfen |
| `FEHLER: ...\libs\python3.lib fehlt` mit einem MSYS2-Pfad | Steht der MSYS2-Ordner vor Python im `PATH`, antwortet das Python von MSYS2 auf die Abfrage der `.bat`; es hat kein `libs\python3.lib` | Den Python-Ordner **vor** den MSYS2-Ordner setzen |
| `fatal error: ../tonmisch.h: No such file or directory` | `tonmisch.h` fehlt in `c-module`, oder `c8205_ton_methoden.h` liegt in `c-module` statt in `python` (dann zeigt `../tonmisch.h` eine Ebene zu hoch) | Ablage nach Abschnitt 4 herstellen |
| `fatal error: c8205_ton_methoden.h: No such file or directory` | Die Datei fehlt im Ordner `python` | Dorthin kopieren |

## 4 Dateiablage

```
c-module\
    plattform.h            nur hier (nicht in python\)
    tonmisch.h             hier; c8205_ton_methoden.h bindet "../tonmisch.h" ein
    trommel.h, bahnsperre.h, unterbrechung.h, c8205_api.h, *.c
c-module\python\
    bau_trommel_mingw.bat
    c8205_ton_methoden.h   nur hier (nicht in c-module\)
    c8205_trommel_modul.c, setup.py, trommel_lader.py, test_c8205_trommel.py
C8205Z\zt_modul\python\
    bau_ztmodul_mingw.bat  liest plattform.h und c8205_api.h über ..\..\..\c-module
```

Dateinamen: Windows lädt nur `.pyd`. Die `.abi3.so` im selben Ordner ist der Linux-Build und wird unter Windows ignoriert; beide dürfen nebeneinander liegen.

## 5 Offen (nicht geprüft)

- **Weitere DLLs:** Der Importtest lief in demselben Terminal, in dem der MSYS2-Ordner im `PATH` stand. Fehlende Laufzeit-DLLs aus `C:\msys64\mingw64\bin` wären dadurch nicht aufgefallen. Prüfen: `objdump -p c8205_trommel.pyd | findstr "DLL Name"` und Importtest in einem frischen Fenster ohne MSYS2 im `PATH`.
- **Python-Versionen:** Gebaut und getestet nur mit Python 3.13. Das Modul benutzt die Limited API (`Py_LIMITED_API=0x03080000`) und `python3.lib`; ob dieselbe `.pyd` unter 3.8 bis 3.12 lädt, ist nicht geprüft. Der Inhaber nutzt sonst Python 3.11.
- **Tonmischer unter Windows:** `tonmisch.c` mit `winmm` läuft (gehört: Grundgeräusch, LL, LS). **Nicht geprüft:** Schreibwerkton und Tastenklänge über den Mischer, Lücken und Aussetzer bei längerem Betrieb (Puffer 4 × 10 ms), Lautstärke und `--TON`, Verhalten ohne Audiogerät (Probe `winmm_pruefen()` meldet dann den Grund), Netz aus mit `fade_out`. Unter Linux belegt: die Änderungen stehen nur im Windows-Zweig; `grafik_stufe4_tests.py` besteht mit beiden Mischern (103 Tests), und der Sammellauf `grafik_alle_tests.sh --schnell` ist so wie vorher (siehe nächster Punkt). Ob `test_c8205_trommel.py` den Mischer aufruft, wurde nicht geprüft.
- **Vorhandener Fehlschlag unter Linux (nicht von dieser Änderung):** `testscripte/grafik_sw_ende_zu_ende.py` (Block „Stufe 3 Ende-zu-Ende“) meldet 2 Fehlschläge und 1 Fehler, mit und ohne die Änderung gleich (15 Tests). Ursache nicht untersucht.
- **Zeitverhalten:** Der Test hat 0,43 s gedauert und bestanden; Messwerte der Windows-Uhr (Aufwachverspätung, Zähler `aufwachen`, `nachgeholte_ticks`, §7.8) liegen nicht vor.
- **Zusatztrommel:** nur gebaut und importiert, kein Funktionstest. In `C8205Z/zt_modul` liegt als Test nur `testframe_zt.c` (C-Testrahmen).
- **GRAFIK-Interpreter und Pult unter Windows:** Der Start über `c8205_grafik.bat` läuft bis zur Tonhinweiszeile und die Töne waren hörbar (`winsound`). Ob das Pult-Fenster (Tk) vollständig bedienbar ist, wurde nicht gemeldet und nicht geprüft.
- **`-static`:** Die Skripte benutzen nur `-static-libgcc`; ob mehr nötig ist, hängt vom Ergebnis der DLL-Prüfung ab.

## 6 Textbausteine zum Einsetzen

**Für §7.4, letzter Absatz (statt „Alles ungebaut und ungetestet“):**
„Windows-Zweig seit 26.10.2026 mit MinGW-w64 (64 Bit) gebaut; `test_c8205_trommel.py` besteht unter Windows mit Python 3.13 (23 Tests, 1 übersprungen, der SIGINT-Test). Messwerte zur Windows-Uhr liegen nicht vor (§9.2.3).“

**Für §10.1 (Windows, eigene Abnahme):**
„Teilabnahme am 26.10.2026: Bau von `c8205_trommel.pyd` und `c8205_ztmodul.pyd` mit MinGW-w64, Laden, Test der Haupttrommel bestanden (§9.2). GRAFIK startet unter Windows; Rechnertöne über `winsound` vom Inhaber gehört (O4-18 bestätigt). `winmm`-Mischer eingeschaltet; Grundgeräusch, LL und LS vom Inhaber gehört. Offen: Schreibwerkton und Dauerbetrieb über den Mischer, Pult-Fenster, Zeitmessung, andere Python-Versionen, Zusatztrommel-Funktionstest.“

**Für die Tabelle der offenen Punkte, OP-01 (Bau `tonmisch` mit MinGW-w64):**
„erledigt für Bau und Betrieb am 26.10.2026: übersetzt, gelinkt und im GRAFIK-Interpreter unter Windows eingeschaltet (`winmm_pruefen()`, `neuer_mischer_winmm()`; Rückfall `winsound`); Grundgeräusch, Lochbandleser- und Stanzerton über `winmm` vom Inhaber gehört. Offen: Dauerbetrieb, Schreibwerkton.“

**Für OP-03 (Ton unter Windows bis zum Mischer):**
„am 26.10.2026 unter Windows gehört: erst Rechnertöne über `winsound` (Zweig ohne Mischer), danach über den Mischer mit `winmm` zusätzlich Lochbandleser- und Stanzertöne; die Startzeile nennt den Weg.“

## 7 Änderungsliste (vollständig, Stand 26.10.2026)

Geändert (kommen in die Lieferung):

| Datei | Änderung | Wirkt auf | Belegt durch |
|---|---|---|---|
| `c-module/plattform.h` | Im Windows-Zweig vor `#include <windows.h>`: `_WIN32_WINNT` und `WINVER` auf 0x0601, falls kleiner als 0x0600 oder nicht gesetzt. Nach dem Include: `YieldProcessor` als `pause` (x86) oder leer, falls der Header es nicht definiert | nur Windows (`#ifdef _WIN32`) | Windows-Bau und -Test beim Inhaber; Linux-Bau von `trommel.c`, `tonmisch.c`, `bahnsperre.c`, `unterbrechung.c` und beider Module ohne Warnung |
| `c-module/python/bau_trommel_mingw.bat` | gcc-Aufruf um `-D_WIN32_WINNT=0x0601 -DWINVER=0x0601` ergänzt | nur Windows-Bau | Bau, Import, 23 Tests unter Windows |
| `C8205Z/zt_modul/python/bau_ztmodul_mingw.bat` | dieselbe Ergänzung | nur Windows-Bau | Bau und Import unter Windows |
| `c8205_grafik.py` | Windows-Zweig des Tons: Probe `winmm_pruefen()` (liefert ok und Grund), bei Erfolg Aufbau wie unter Linux mit `neuer_mischer_winmm()` (Variable `winmm`, Bedingungen `spieler is not None or winmm`) und Startzeile „… ueber den Mischer (winmm).“; sonst alter `winsound`-Zweig mit Hinweiszeile und Zeile „Grund: …“ | Linux-Zweig unverändert; neuer Pfad nur bei `os.name == 'nt'` | Linux-Sammellauf; Windows: Grundgeräusch, LL und LS gehört |
| `grafik-interpreter-module/grafik_tonmisch_c.py` | Neu: Klasse `CWinmmSenke`, Funktionen `winmm_pruefen()`, `winmm_verfuegbar()` (Hülle darum) und `neuer_mischer_winmm()` | neuer Code, auf Linux nur über die Tests erreicht | drei neue Tests; unter Windows gehört (siehe oben) |
| `testscripte/grafik_stufe4_tests.py` | Neue Klasse `WinmmSenke` mit drei Tests (Probe liefert unter Nicht-Windows `False`, mit Grund, der „winmm“ nennt; `neuer_mischer_winmm()` wirft `SenkeAusfall` mit „winmm“) | Linux | 103 Tests mit Python- und C-Mischer bestanden |

Unverändert, aber an der richtigen Stelle nötig (Dateien aus dem Archiv, keine Lieferung):

- `c-module/tonmisch.h` muss in `c-module` liegen (Include `../tonmisch.h` aus `python/`).
- `c-module/python/c8205_ton_methoden.h` muss in `python/` liegen, nicht in `c-module/`.
- `plattform.h` nur in `c-module/`, nicht in `python/`.

Ergebnisse in der Reihenfolge der Beobachtung (Windows, Rechner des Projektinhabers):

1. Erster Bau mit altem `plattform.h`: Fehler `unknown type name 'CONDITION_VARIABLE'` (Abschnitt 3).
2. Mit `-D…` in der `.bat`: Compiler läuft durch; `YieldProcessor`-Warnung nur, solange die alte `plattform.h` aktiv war.
3. Linkfehler `unhandled machine type (0x8664)`: 32-Bit-MinGW (mingw.org) gegen 64-Bit-Python.
4. Mit MSYS2 `mingw64` und Python vor MSYS2 im `PATH`: `OK: c8205_trommel.pyd`, Import ok, 23 Tests OK (1 übersprungen).
5. Zusatztrommel: `OK: c8205_ztmodul.pyd`, Import ok.
6. `c8205_grafik.bat` vor der Änderung am Ton: Hinweiszeile „… winmm fehlt …“, Töne hörbar über `winsound`.
7. Nach der Änderung: Startzeile „Hinweis: Toene unter Windows ueber den Mischer (winmm).“; Grundgeräusch, Lochbandleser- und Stanzertöne hörbar.

Nicht von dieser Änderung, aber festgehalten: `testscripte/grafik_sw_ende_zu_ende.py` hat unter Linux 2 Fehlschläge und 1 Fehler, mit und ohne die Änderung; Ursache nicht untersucht.

Die Versionszeilen der geänderten `.py`-Dateien (`VERSION_TONMISCH_C = 'G4-005'`, `VERSION_GRAFIK`) wurden nicht verändert; ob dafür eine neue Kennung zu vergeben ist, entscheidet der Projektinhaber.

### 7.1 Meldung des Inhabers: Leser- und Stanzertöne kommen nicht (26.10.2026)

Leser- und Stanzerton laufen nur über den C-Mischer (`LeserTon`, `StanzerTon`). Im alten `winsound`-Zweig sind sie absichtlich aus. Ob der Mischer überhaupt aktiv war, wurde nicht gemeldet. Deshalb gibt `c8205_grafik.py` unter Windows jetzt beim Start eine Zeile aus: entweder „Hinweis: Toene unter Windows ueber den Mischer (winmm).“ oder die alte Hinweiszeile mit einer zweiten Zeile „Grund: …“ (`grafik_tonmisch_c.winmm_pruefen()` liefert `(ok, Grund)`). Ursache der fehlenden Töne bis zur Rückmeldung des Inhabers **nicht geklärt**. Tests: 103 in `grafik_stufe4_tests.py` mit beiden Mischern bestanden (Linux). **Auflösung (26.10.2026):** Mit der Startzeile „Hinweis: Toene unter Windows ueber den Mischer (winmm).“ meldete der Inhaber, dass Leser- und Stanzertöne zusätzlich zum Grundgeräusch hörbar waren. Warum sie vorher fehlten, ist nicht geklärt; vermutlich lief noch der `winsound`-Zweig (dort sind sie absichtlich aus). Die Diagnosezeilen bleiben im Code.
