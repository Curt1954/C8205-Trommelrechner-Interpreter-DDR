# SW-Ton und LS-Ton

Version: 0.01-005

Geräusche von Schreibwerk und Lochstreifenleser für den C 8205-Interpreter: Anforderungen, Ergebnisse, Diskussion

Stand: 19.10.2026 (Nachführung Stufe 4: Schreibwerkzeit 80 ms, Zeichenklang 100 ms, ein TAB-Klang; Teil D Rechner- und Stanzertöne vom 15.10.2026) · Programm: `sw_ton.py` · Klänge: Ordner `sw_toene/`

> **Stand Stufe 4 (19.10.2026).** Die Abschnitte 7, 11 und 16 beschreiben `sw_ton.py` nach den Entscheidungen vom 16. und 18.10.2026: **Schreibwerkzeit 80 ms (70 bis 90 ms, gleichverteilt), Zeichenklang 100 ms, TAB nur noch `tab_400.wav` (400 ms), WRZL 360 ms.** Wo die Teile B bis D noch „120 ms ±10 %“, `tab_kurz`/`tab_lang` oder „Einbau später“ nennen, ist das der Stand vom 14./15.10.2026 (Messwerte der Aufnahmen bleiben gültig) und durch dieses Feld überholt. In GRAFIK spielt `grafik_schreibwerk.py` diese Zeiten über den Mischer `tonmisch` (`C8205-Interpreter-GRAFIK_Beschreibung.md` §6); `sw_ton.py` bleibt der selbständige Testrahmen für die Klänge. Die Hörprüfung (S4-16) steht noch aus.
>
> **Nachführung 21.10.2026 (Abgleich OP-30 (b)).** Teil D (Abschnitte 17 bis 21) trägt den Stand vom 15.10.2026. Seitdem gilt: Die Töne des Rechners, des Schreibwerks, des Lesers und des Stanzers sind in GRAFIK eingebaut (Rechnertöne Stufe 2, 17.10.2026; Rest Stufe 4, 19.10.2026) und laufen über den Mischer `tonmisch`; alle Klänge liegen als WAV vor (Ordner `ton/` und `ton/toene_rechner_stanzer/`), die Umwandlung aus MP3 ist erfolgt; die Hörprüfung 2 am 19.10.2026 ist als „ok“ gemeldet. Damit sind in Abschnitt 21.2 D-1, D-10, D-11 und D-12 beantwortet (je mit Zusatz vermerkt). Der Abschnitt 19 „Wartezeit = 0“ gilt für den Modus TEST; in GRAFIK gilt das Stanztempo von etwa 50 Zeichen/s. Maßgeblich ist `C8205-Interpreter-GRAFIK_Beschreibung.md` §6. **Aus dem Abgleich (erledigt 21.10.2026, OP-42):** Der Testrahmen spielte für `WR` den WRZL-Klang, GRAFIK den Zeichenklang. Entschieden: WR hat einen eigenen kurzen Klang, `sw_toene/wr.wav` (120 ms, erste Hälfte des WRZL-Klangs vor dem markanten Ton); der Testrahmen und GRAFIK spielen ihn für `<WR>` (§7.1, §7.2, §14.1).

## 1 Zweck und Abgrenzung

Wenn der Interpreter auf das Schreibwerk (SW) ausgibt oder vom Lochstreifenleser (Kanal K1 = Leser 1, K2 = Leser 2) liest, soll dazu das Geräusch des jeweiligen Geräts zu hören sein. Dieses Dokument beschreibt

- **Teil A:** die Anforderungen,
- **Teil B:** das Ergebnis (Programm, Klänge, Messwerte, Prüfung) und
- **Teil C:** die Diskussion der Ergebnisse mit Bewertung, Entscheidungen und offenen Punkten und
- **Teil D (Ergänzung 15.10.2026):** die Töne des Rechners beim Netz ein und aus sowie die Töne des Lochbandstanzers. Teil D ist noch **nicht** in `sw_ton.py` umgesetzt.

Es ist keine Projektdokumentation des Interpreters. **Es ist nichts in den Interpreter eingebaut.** Das Ergebnis ist ein selbständiges Python-Programm `sw_ton.py` (nur Standardbibliothek) mit

1. der Funktion `sw_ton(zeichen)` für das Schreibwerk,
2. der Funktion `ls_ton()` für den Lochstreifenleser und
3. einem Testrahmen, der einen String oder ein Leser-Szenario als Tonfolge ausgibt.

Der Dateiname blieb `sw_ton.py`, damit bestehende Verweise gültig bleiben.

## Teil A – Anforderungen

## 2 Ausgangslage

Als Vorgabe lagen fünf Aufnahmen vor, dazu der Interpreter mit der Datei `Kodetabellen.md`:

| Aufnahme | Inhalt |
|---|---|
| `SW-WRZL.mp3` | Geräusch beim Ausführen der SW-Ausgabe eines WRZL (0,78 s) |
| `SW-Dauerprint-01.mp3` | mehrfache Zeichenausgabe, dann eine kleine Pause (= TAB), das wiederholt sich, am Zeilenende ein WRZL (24,4 s) |
| `LS-Einzelschritt-1.mp3` | Lesen eines einzelnen Zeichens (0,16 s) |
| `LS-Dauerlesen-2_5s.mp3` | Lesen mehrerer Zeichen hintereinander ohne Pause (2,55 s) |
| `Kodetabellen.md` | R 300-Code, Tabelle 1: Zuordnung der Zeichen |

## 3 Anforderungen Schreibwerk

| Nr. | Anforderung |
|---|---|
| A-SW-1 | Eine Funktion gibt zu einem Zeichen das Schreibwerk-Geräusch aus. Das Zeichen wird gemäß R 300-Code, Tabelle 1 übergeben. |
| A-SW-2 | Es gibt drei Klangarten: WRZL, TAB und allgemeines Zeichen (für den Rest des Codes). *(Seit 21.10.2026 vier: dazu WR, siehe §14.1.)* |
| A-SW-3 | Die Rückkehr der Funktion wird um die Ausgabedauer verzögert. Der Interpreter „steht" für die Dauer der Tonausgabe. |
| A-SW-4 | Für allgemeine Zeichen wird zufällig ein Ton aus mehreren, sich leicht unterscheidenden Tönen gewählt. Diese werden dem Dauerprint entnommen. |
| A-SW-5 | Die Tondauer einfacher Zeichen wird zufällig um ±10 % verändert. |
| A-SW-6 | Die Dauern von WRZL, Einzelzeichen und TAB werden aus den Aufnahmen bestimmt. |
| A-SW-7 | Ein Testrahmen nimmt einen String als Aufrufparameter (in Anführungszeichen, darf CR = WRZL enthalten) und setzt ihn in eine Tonfolge um. |

## 4 Anforderungen Lochstreifenleser

| Nr. | Anforderung |
|---|---|
| A-LS-1 | Eine zweite Funktion bildet das Geräusch eines Lochstreifenlesers nach. Sie wird später bei jedem Eingabe-Halt von Kanal K1 oder K2 aufgerufen. |
| A-LS-2 | Aus den Aufnahmen werden der Einzelschritt (ein Zeichen) und das Dauerlesen (mehrere Zeichen ohne Pause) verwendet. |
| A-LS-3 | Bei 130 Zeichen/s sind einzelne Töne nicht mehr unterscheidbar. Die Funktion muss deshalb auf die Leseranforderung reagieren. |
| A-LS-4 | Das erste Zeichen nach einer längeren Pause ist immer ein Einzelton. Kommt eine zweite Eingabe innerhalb einer kurzen Zeit, darf kein Einzelton mehr ausgegeben werden, sondern das Dauergeräusch läuft endlos, bis die Eingaben länger unterbrochen werden. Die drei Zeiten (Pause, kurze Zeit, Unterbrechung) sind festzulegen. |
| A-LS-5 | Die Verarbeitung des Interpreters darf durch die Tonausgabe nicht länger unterbrochen werden, als die Lesegeschwindigkeit nötig macht. Dies kollidiert mit der Hörbarkeit der Töne und ist abzuwägen. |

## 5 Übergreifende Anforderungen

| Nr. | Anforderung |
|---|---|
| A-ALL-1 | Zuerst ein selbständiges Python-Programm mit Testrahmen. Die Funktionen sollen später in den Interpreter eingebaut werden können, nicht jetzt. |
| A-ALL-2 | Das Programm muss unter Linux und unter Windows nutzbar sein. Die Versionen ändern sich und sind unbestimmt, es darf also nicht von bestimmten Versionen abhängen. |
| A-ALL-3 | Die Dokumentation umfasst Anforderungsbeschreibung, Ergebnisbeschreibung und Diskussion der Ergebnisse. Die spätere Projektdokumentation ist davon getrennt. |

## Teil B – Ergebnisse

## 6 Lieferumfang

| Datei | Inhalt |
|---|---|
| `sw_ton.py` | Funktionen `sw_ton()` und `ls_ton()`, Testrahmen |
| `sw_toene/zeichen_01.wav` … `zeichen_24.wav` | 24 leicht unterschiedliche Anschläge für allgemeine Zeichen (je 120 ms) |
| `sw_toene/tab_kurz.wav` | Tabulator kurz (120 ms) |
| `sw_toene/tab_lang.wav` | Tabulator lang (325 ms) |
| `sw_toene/tab_400.wav` | Tabulator, **der einzige gespielte TAB-Klang seit Stufe 4** (400 ms, aus `tab_lang.wav` gedehnt) |
| `sw_toene/wrzl.wav` | Wagenrücklauf (360 ms) |
| `sw_toene/wr.wav` | Wagenrücklauf ohne Zeilenschaltung (120 ms, neu 21.10.2026; erzeugt mit `erzeuge_wr_klang.py` aus den ersten 120 ms von `wrzl.wav`, letzte 5 ms ausgeblendet) |
| `sw_toene/ls_einzel.wav` | Leser: Einzelschritt (148 ms) |
| `sw_toene/ls_dauer.wav` | Leser: Dauergeräusch, nahtlose Schleifeneinheit (1,25 s) |
| `sw_toene/ls_ende.wav` | Leser: Auslaufen nach dem Dauergeräusch (60 ms) |
| `SW_Ton_Beschreibung.md` / `.pdf` | dieses Dokument |

`sw_toene/` muss neben `sw_ton.py` liegen (Konstante `KLANGORDNER`). Alle WAV-Dateien haben dasselbe Format: 44,1 kHz, mono, 16 bit. Das Programm prüft das beim Laden. Wer Klänge austauschen will, ersetzt nur die Dateien. Zusätzliche `zeichen_*.wav` werden automatisch in die Zufallsauswahl aufgenommen.

## 7 Schreibwerk: die Funktion `sw_ton()`

```python
sw_ton(zeichen) -> float
```

Die Funktion gibt den Klang zum Zeichen aus und **kehrt erst nach der Schreibwerkzeit zurück**. Der Interpreter steht also so lange. Rückgabewert ist die Schreibwerkzeit in Sekunden (0.0, wenn nichts ausgegeben wurde); der Klang kann länger dauern (Zeichen: 100 ms). Der Parameter `tab_lang` ist entfallen.

### 7.1 Eingabe und Zuordnung (R 300-Code, Tabelle 1)

Übergeben wird ein Zeichen so, wie `sw_zeichen()` im Interpreter es liefert, oder ein ASCII-Wert.

| Eingabe | Klangart |
|---|---|
| `'\t'` (ASCII 9), `<TAB>`, `<Tabulator>`, Zahl `9` | **TAB** |
| `'\n'` (ASCII 10 = WRZL), `'\r'` (ASCII 13, nach Vorgabe CR = WRZL), `<WRZL>`, `<SatzMarke>`, Zahlen `10`, `13` | **WRZL** |
| `<WR>` (Wagenrücklauf ohne Zeilenschaltung, so liefert es der Interpreter) | **WR** (seit 21.10.2026, OP-42) |
| jedes andere einzelne Zeichen, auch Leerzeichen | **ZEICHEN** |
| jeder andere Name in `<>` (z. B. `<Um. KB>`, `<Nr.7>`) | **ZEICHEN** |
| leerer String `''` | keine Ausgabe, Rückgabe 0.0 |
| mehrere Zeichen ohne `<>` (z. B. `'ab'`) | `ValueError` |

Namen in `<>` werden ohne Leerzeichen und Punkte und ohne Beachtung der Groß-/Kleinschreibung verglichen.

### 7.2 Klangarten, Schreibwerkzeit und Klanglänge

| Klangart | Klang | Schreibwerkzeit (Rückkehr der Funktion) | Klanglänge |
|---|---|---|---|
| ZEICHEN | zufällig eine der 24 Dateien `zeichen_*.wav` | **80 ms, je Zeichen zufällig um ±10 ms**, also 70 bis 90 ms (gleichverteilt) | **100 ms**: die Dateien (120 ms) werden gekürzt, die letzten 10 ms ausgeblendet |
| TAB | `tab_400.wav` (ein Klang für jeden Tabulatorweg) | 400 ms | 400 ms |
| WRZL | `wrzl.wav` | 360 ms | 360 ms |
| WR | `wr.wav` | 120 ms | 120 ms |

- Bei ZEICHEN wird nie zweimal hintereinander derselbe Klang gewählt.
- Schreibwerkzeit und Klanglänge sind getrennt (S4-17). Bei Zeichen ist der Klang (100 ms) länger als die Schreibwerkzeit (70 bis 90 ms). Der Überstand **überlappt** mit dem Klang des folgenden Zeichens (O4-7); `--wav` mischt die Klänge deshalb übereinander (Summe auf 16 bit begrenzt).
- Der Anschlag selbst dauert etwa 60 ms und wird durch das Kürzen auf 100 ms nicht abgeschnitten.
- Die gekürzten Zeichenklänge liegen als temporäre Dateien vor (der Abspieler braucht einen Pfad); sie werden beim Beenden gelöscht. Die Dateien in `sw_toene/` bleiben unverändert.
- `tab_kurz.wav` und `tab_lang.wav` liegen als Quelle von `tab_400.wav` im Ordner, werden aber nicht mehr gespielt. Die Funktion kennt keine Spalte und kann den Tabulatorweg nicht selbst bestimmen; den braucht sie auch nicht.

### 7.3 Konstanten im Programm

| Konstante | Vorgabe | Bedeutung |
|---|---|---|
| `KLANGORDNER` | `sw_toene/` neben dem Programm | Ort der WAV-Dateien |
| `STUMM` | `False` | `True`: nur warten, keinen Ton ausgeben |
| `SCHREIBWERKZEIT_S` | `0.080` | Schreibwerkzeit allgemeiner Zeichen |
| `SCHREIBWERKZEIT_STREUUNG_S` | `0.010` | Schwankung der Schreibwerkzeit je Zeichen, ±10 ms (0 = aus) |
| `ZEICHENKLANG_S` | `0.100` | Länge des Zeichenklangs (Dateien werden gekürzt) |
| `ZEICHEN_AUSBLENDUNG_S` | `0.010` | Ausblendung am Ende des gekürzten Zeichenklangs |
| `LS_ZEICHEN_PRO_S` | `130` | Lesegeschwindigkeit des Lochstreifenlesers |
| `LS_PAUSE_S` | `0.100` | Schwelle für Einzel- und Dauergeräusch beim Leser |
| `LS_TEMPO` | `True` | Leser hält die Lesegeschwindigkeit ein |

## 8 Schreibwerk: Herkunft der Klänge und Messwerte

Gemessen wurde nur in den sauber periodischen Abschnitten des Dauerprints (0–6 s und 21–24 s).

| Größe | Messwert |
|---|---|
| Zeichentakt | 120,0 ms im Mittel (σ 4,4 ms; die Abstände wechseln zwischen ca. 115 und 125 ms), ≈ 8,3 Zeichen/s |
| Einzelzeichen | Anstieg ca. 2 ms, kräftiger Teil 10–12 ms, hörbares Ausklingen ca. 40 ms (bis ca. 55 ms im Rauschen) |
| TAB kurz | Abstand von Anschlag zu Anschlag 239 ms (±0,6; n = 9), also ca. 120 ms mehr als ein normaler Takt |
| TAB lang | Abstand von Anschlag zu Anschlag 445 ms (±8; n = 5), also ca. 325 ms mehr |
| WRZL | Klang von 242 bis 603 ms, **ca. 360 ms** (340–360 ms je nach Schwelle); die Datei dauert 777 ms mit 242 ms Vorlauf und 175 ms Nachlauf |

Das Druckmuster im Dauerprint wiederholt sich im Zyklus von ca. 1,9 s: 4 Zeichen, TAB kurz, 4 Zeichen, TAB kurz, 3 Zeichen, TAB lang.

Der TAB hat kaum eigenen Klang. Beim kurzen TAB gibt es in 8 von 9 Fällen ein schwaches Ticken ca. 100 ms nach dem letzten Anschlag. Beim langen TAB liegen mehrere schwache Ticks bei ca. 120, 235 und 340 ms.

### 8.1 Herstellung der Klangdateien

- **Zeichen (24 Stück):** Aus den Anschlägen des Dauerprints, die mindestens 85 ms Abstand zu den Nachbaranschlägen haben, wurden die 24 mit dem besten Signal-Rausch-Abstand gewählt. Jeder Ausschnitt reicht von 6 ms vor bis 54 ms nach dem Spitzenwert, mit kurzen Ein- und Ausblendungen (2 ms und 6 ms). Die Spitze ist auf 0,4 normiert, das ist etwa die Lautstärke des WRZL. Die Ausschnitte sind mit Stille auf 120 ms aufgefüllt. Sie ähneln sich im Feinverlauf kaum (mittlere Paar-Korrelation 0,05).
- **TAB kurz:** 120 ms aus einer Lücke von 239 ms, beginnend 88 ms nach dem vorherigen Anschlag, sodass das Ticken am Anfang liegt.
- **TAB lang:** 325 ms aus einer Lücke von 455 ms, beginnend 115 ms nach dem vorherigen Anschlag.
- **WRZL:** 360 ms aus `SW-WRZL.mp3`, beginnend bei 241 ms.

Die Dauern sind so festgelegt, dass eine Folge die gemessene Zeit zwischen zwei Anschlägen ergibt: Zeichen 120 ms + TAB kurz 120 ms = ca. 240 ms (gemessen 239 ms).

## 9 Lochstreifenleser: die Funktion `ls_ton()`

```python
ls_ton() -> float
```

Die Funktion wird **bei jedem Eingabe-Halt von Kanal K1 oder K2** einmal aufgerufen, ohne Parameter. Bei 130 Zeichen/s (7,7 ms je Zeichen) wären einzelne Töne nicht mehr unterscheidbar. Deshalb richtet sich der Klang nach dem **Abstand der Aufrufe**, und der Ton läuft im Hintergrund.

> **Nachführung 22.10.2026 (G4-005, Wunsch des Projektinhabers; ersetzt die Tabelle 9.1 und die Schwelle von 100 ms in GRAFIK):** Der Ton hängt am tatsächlichen Benutzen des Lesers (ein Zeichen wird geliefert), nicht am Warten im Eingabe-Halt. Läuft kein Ton, startet der Einzelton (148 ms bis zu seinem Ende); die Befehlsschleife ist nach 1/10 s wieder frei. Kommt dann der nächste Zugriff und der Einzelton läuft noch, wird er abgebrochen und durch den Dauerton ersetzt, der ab diesem Moment läuft; die Befehlsschleife ist danach je Zeichen nach 1/130 s frei. Läuft der Einzelton nicht mehr, beginnt wieder ein Einzelton. Folgt `LS_AUS_S` (3 s, geschätzt, nachzustellen) lang kein Zugriff, geht der Ton aus (Dauerton mit 60 ms Auslaufen) und der Ablauf beginnt von vorn. Umgesetzt in `grafik_geraeteton.LeserTon`; `sw_ton.py` ist unverändert.

### 9.1 Verhalten

| Lage | Klang |
|---|---|
| erstes Zeichen nach mehr als 100 ms ohne Eingabe | **Einzelschritt** (Geräusch ca. 150 ms) |
| nächstes Zeichen höchstens 100 ms nach dem vorigen | der Einzelschritt wird abgebrochen, das **Dauergeräusch** läuft endlos |
| Dauergeräusch läuft, Eingaben bleiben mehr als 100 ms aus | Dauergeräusch endet mit 60 ms **Auslaufen** |
| nächstes Zeichen nach einem Dauergeräusch und mehr als 100 ms Pause | wieder ein **Einzelschritt** |

Es gibt nur eine Schwelle (`LS_PAUSE_S`, 100 ms). Sie gilt für alle drei Entscheidungen: Einzel oder Dauer, Dauer weiter, Dauer vorbei. So entstehen keine Zwischenzustände.

### 9.2 Verzögerung des Interpreters

- Die Funktion verzögert nur **so weit, wie die Lesegeschwindigkeit es verlangt**: ein Zeichen frühestens 1/130 s nach dem vorigen. Rechenzeit des Interpreters zwischen zwei Aufrufen wird angerechnet. Braucht der Interpreter ohnehin 7,7 ms oder länger je Zeichen, wird nichts zusätzlich gewartet.
- Die **Tonlänge verzögert den Interpreter nicht**. Der Ton läuft im Hintergrund. Je Zeichen kostet der Aufruf nur das Anmelden der Eingabe, ein Prozess für den Ton wird nur beim Wechsel zwischen Einzelschritt, Dauergeräusch und Auslaufen gestartet.
- Ein Hintergrundfaden beendet das Dauergeräusch, wenn die Eingaben aussetzen. Er läuft als Daemon und endet mit dem Programm. Beim Beenden wird der Ton gestoppt.
- `LS_TEMPO = False` schaltet die Verzögerung ganz ab.
- Rückgabewert: die Verzögerung dieses Aufrufs in Sekunden.

### 9.3 Klänge und Herkunft

| Datei | Herkunft |
|---|---|
| `ls_einzel.wav` (148 ms) | `LS-Einzelschritt-1.mp3`, Ausschnitt von 8 bis 156 ms (3 ms Vorlauf vor dem ersten Ereignis) |
| `ls_dauer.wav` (1,25 s) | `LS-Dauerlesen-2_5s.mp3`, stationärer Teil von 0,40 bis 1,80 s, Naht mit 150 ms Überblendung gleicher Leistung glattgezogen |
| `ls_ende.wav` (60 ms) | Ausschnitt der Schleife mit 60 ms Ausblendung |

Messwerte der Aufnahmen: Der Einzelschritt besteht aus mehreren mechanischen Einzelereignissen bei 11, 55, 70, 94, 103 und 149 ms (Klang von 11 bis 149 ms, Aufnahme 158 ms), die kräftigen liegen bis ca. 105 ms. `LS-Dauerlesen-2_5s.mp3` ist ein gleichmäßiges Rauschen ohne eigenen Start- und Stoppklang. Der Pegel sinkt über die Aufnahme langsam (RMS von ca. 0,045 auf ca. 0,030), und der 7,7-ms-Lesertakt ist darin nicht als Periodizität erkennbar. Deshalb wurde der stationäre mittlere Teil als Schleife genommen. Ihr Pegel schwankt über 100-ms-Fenster zwischen 0,035 und 0,048 und zeigt an der Naht keinen Einbruch.

## 10 Wiedergabe, Timing und Plattformen

| System | Wiedergabe |
|---|---|
| Windows | `winsound` (Standardbibliothek), asynchron aus der Datei. Das Leser-Dauergeräusch läuft mit `SND_LOOP` endlos. |
| Linux | erstes gefundene Programm aus `paplay`, `pw-play`, `aplay -q`, `play -q`, `ffplay` |
| macOS | `afplay` (danach dieselbe Liste) |
| kein Player gefunden | einmalige Warnung auf stderr, das Programm wartet nur ohne Ton |

- **Schreibwerk:** Das Programm startet den Player, ohne auf dessen Ende zu warten, und wartet dann selbst bis zum Ende der Ausgabedauer. Die Startzeit des Players liegt damit innerhalb der Ausgabedauer und verlängert sie nicht.
- **Leser unter Linux/macOS:** Die Kommandozeilenspieler wiederholen nicht endlos. Deshalb wird die Schleifeneinheit beim ersten Gebrauch ca. 30 Mal hintereinander in eine temporäre WAV-Datei geschrieben (rund 2,6 MB, wird beim Beenden gelöscht). Läuft sie ab, startet `ls_ton()` sie bei der nächsten Eingabe neu. Beim Wechsel wird der Prozess des alten Klangs beendet.
- **Zeitgenauigkeit:** Gewartet wird bis zu einem festen Zielzeitpunkt (`time.perf_counter()`): grob mit `time.sleep`, die letzten 3 ms aktiv.
- **Windows:** Beim ersten Ton wird der Systemtakt über `timeBeginPeriod(1)` auf 1 ms gestellt und beim Beenden freigegeben. Das macht den Takt unabhängig von der Python- und Windows-Version. Gelingt es nicht, wird stattdessen 18 ms vor dem Ziel aktiv gewartet.
- **Mindestversion:** Python 3.6 (f-Strings). Weitere Pakete werden nicht gebraucht.

## 11 Testrahmen

### 11.1 Schreibwerk

```text
python3 sw_ton.py "AB\tCD\r"
python3 sw_ton.py --wav probe.wav "Hallo\tWelt\r"
python3 sw_ton.py --stumm --seed 1 "Test"
```

Der String steht in Anführungszeichen. Steuerzeichen können echt im String stehen oder als Escape: `\t` = TAB, `\r` oder `\n` = WRZL, `\\` = Backslash. **CR+LF direkt hintereinander zählt als ein WRZL.** Jedes Zeichen wird der Reihe nach als Klang ausgegeben. Der Rahmen zeigt je Zeichen die Art, den gewählten Klang und die Dauer, am Ende Sollzeit und gemessene Zeit.

### 11.2 Lochstreifenleser

```text
python3 sw_ton.py --ls "1 p300 1 p80 1 1 1 p500 100 p300 1"
python3 sw_ton.py --ls "1 p300 1 p80 1 1 1 p500 100" --wav leser.wav
python3 sw_ton.py --ls "20@40" --pause 60
```

Ein Szenario ist eine Folge von Aufrufen von `ls_ton()`, Einträge durch Leerzeichen oder Komma getrennt:

| Eintrag | Bedeutung |
|---|---|
| `n` | n Zeichen im Lesertakt (130/s) hintereinander |
| `n@ms` | n Zeichen im Abstand von ms Millisekunden (der Interpreter braucht so lange je Zeichen) |
| `pms` | Pause: das nächste Zeichen kommt ms Millisekunden nach dem letzten |

Der Rahmen zeigt die Aktionen mit Zeit (`EINZEL`, `DAUER_AN`, `DAUER_AUS`). Ohne `--wav` wird in Echtzeit gespielt und die Dauer des Szenarios gemessen, mit `--wav DATEI` wird die Tonfolge nur berechnet, ohne Wiedergabe und ohne Warten. Beispiel `1 p300 1 p80 1 1 1 p500 100 p300 1 p150 1 p150 1`: Einzelschritt (0,000 s), Einzelschritt (0,300 s), Dauer ab 0,380 s bis 0,495 s, Einzelschritt (0,895 s), Dauer ab 0,903 s bis 1,757 s, dann drei Einzelschritte im Abstand von 150 ms.

### 11.3 Optionen

| Option | Wirkung |
|---|---|
| `--roh` | keine Escapes auswerten |
| `--stumm` | keinen Ton ausgeben, nur die Zeiten einhalten |
| `--seed N` | Zufallsfolge (Klangwahl und Schreibwerkzeit) reproduzierbar machen |
| `--zeit MS` | Schreibwerkzeit allgemeiner Zeichen in ms (Vorgabe 80) |
| `--streuung MS` | Schwankung der Schreibwerkzeit in ms (Vorgabe 10 = 70 bis 90 ms, 0 = aus) |
| `--ls SZENARIO` | Leser-Szenario statt eines Strings |
| `--pause MS` | Leser: Schwelle in ms (Vorgabe 100) |
| `--wav DATEI` | Tonfolge nur in diese WAV-Datei rechnen, ohne Wiedergabe und ohne Warten |

## 12 Prüfung

Alle Prüfungen liefen unter Python 3.12 auf Linux ohne Tonausgabe. Dabei wurden Platzhalter-Player und ein simuliertes `winsound` benutzt.

| Prüfung | Ergebnis |
|---|---|
| Zuordnung Zeichen → Klangart (18 Eingaben: Zeichen, Namen, ASCII-Zahlen, leer, ungültig) | wie in 7.1 beschrieben |
| Zufallsauswahl, 2000 Aufrufe | alle 24 Klänge benutzt, keine direkte Wiederholung |
| Dauerstreuung, 20 000 Aufrufe | 108,0 bis 132,0 ms, Mittel 119,94 ms |
| Verzögerung Schreibwerk, 10 Zeichen | Summe der Rückgaben 1177,3 ms, real 1177,6 ms. Bei weiteren Läufen mit 11 Zeichen wich die reale Zeit um 0,7 bis 8 ms von der Sollzeit ab |
| Rendern in WAV, 8 Zeichen | Datei 1181,7 ms, Summe der Dauern 1,182 s |
| Player-Aufrufe Linux (Platzhalter) | Aufrufe im 120-ms-Raster |
| Windows-Zweig (simuliertes `winsound`) | 3 Aufrufe (Zeichen, TAB, WRZL) in 0,601 s, erwartet 0,600 s |
| Leser-Zeitlogik, Szenario mit 108 Aufrufen | Aktionen und Zeiten wie in 11.2; gerendertes Signal: Einzelschritt wird sauber vom Dauergeräusch abgelöst, Auslaufen am Ende |
| Leser-Lesetempo, Echtzeit, 130 Zeichen | 0,992 s |
| Leser mit Rechenzeit des Interpreters, 130 Zeichen | 3 ms je Zeichen: 0,995 s; 10 ms je Zeichen: 1,301 s, keine zusätzliche Verzögerung |
| Leser: Player und Wächter-Faden (Linux, Platzhalter) | Einzelschritt, Schleife (30-s-Datei), Auslaufen und Beenden der Prozesse in der richtigen Reihenfolge; Gesamtzeit 1,793 s bei Soll 1,792 s |
| Leser: Windows-Zweig (simuliertes `winsound`) | Aufrufe Einzel (Flags 3), Schleife (Flags 11 mit `SND_LOOP`), Auslaufen (Flags 3) |
| Regression Schreibwerk nach Erweiterung um den Leser | unverändert |

## Teil C – Diskussion der Ergebnisse

## 13 Bewertung der Anforderungen

| Nr. | Erfüllung | Anmerkung |
|---|---|---|
| A-SW-1 | erfüllt | Zeichenübergabe nach Tabelle 1 (7.1) |
| A-SW-2 | erfüllt | WRZL, TAB, ZEICHEN; seit 21.10.2026 auch WR (`<WR>`, eigener Klang), siehe 14.1. Der Code ASCII 13 / `\r` spielt weiter WRZL |
| A-SW-3 | erfüllt | geprüft: Abweichung der Wartezeit 0,3 bis 8 ms je Folge von 10 bis 11 Zeichen |
| A-SW-4 | erfüllt | 24 Klänge, nie derselbe zweimal hintereinander |
| A-SW-5 | erfüllt | 108 bis 132 ms, Mittel 119,94 ms |
| A-SW-6 | erfüllt | WRZL ca. 360 ms, Zeichen ca. 40 ms Klang bei 120 ms Takt, TAB kurz 120 ms und lang 325 ms (Stichprobe klein, siehe 14.3) |
| A-SW-7 | erfüllt | Testrahmen mit Escapes für TAB und CR |
| A-LS-1 | erfüllt, nicht eingebaut | Funktion fertig, Aufrufstelle im Interpreter noch nicht untersucht |
| A-LS-2 | erfüllt | beide Aufnahmen verwendet (9.3) |
| A-LS-3 | erfüllt | Klang richtet sich nach dem Abstand der Aufrufe |
| A-LS-4 | erfüllt, Zeiten offen | alle drei Zeiten sind eine Schwelle von 100 ms, im echten Lauf zu prüfen (14.2) |
| A-LS-5 | erfüllt | Verzögerung nur für das Lesetempo, Ton im Hintergrund |
| A-ALL-1 | erfüllt | selbständig, nicht eingebaut |
| A-ALL-2 | teilweise geprüft | Logik und Aufrufe getestet, echte Tonausgabe unter Linux und Windows nicht |
| A-ALL-3 | erfüllt | dieses Dokument |

## 14 Diskussion der Entscheidungen

### 14.1 WRZL und WR

Laut Tabelle 1 ist WRZL ASCII 10 und WR (Wagenrücklauf ohne Zeilenschaltung, Zeile 55) ASCII 13. Nach Vorgabe gilt CR = WRZL, deshalb spielten bisher beide Codes den WRZL-Klang. Der Interpreter gibt ein WRZL als `chr(10)` aus. **Seit 21.10.2026 (OP-42, Entscheidung des Projektinhabers)** hat WR einen eigenen Klang: nur die erste Hälfte des WRZL-Klangs, vor dem markanten Ton, 120 ms lang (`sw_toene/wr.wav`, Schreibwerkzeit ebenfalls 120 ms). Der Klang entsteht mit `erzeuge_wr_klang.py`: die ersten 120 ms von `wrzl.wav`, die letzten 5 ms ausgeblendet; als markanter Ton gilt der laute Schlag bei etwa 126 ms (Auslegung, nicht gehört; `--ende MS` stellt den Schnitt nach). Der Testrahmen erkennt WR nur am Namen `<WR>` (im Aufrufstring die vier Zeichen `<WR>`); `'\r'`, ASCII 13 und `<WRZL>` bleiben WRZL, damit die Vorgabe „CR = WRZL“ weiter gilt. GRAFIK: `grafik_schreibwerk.py` G4-002.

„Um. KB" und „Um. GB" machen im Interpreter keinen Ton, denn `a017` stellt dort nur die Zeichenlage um und ruft `sw_schreibe` nicht auf. Würden sie doch übergeben, wären sie allgemeine Zeichen.

### 14.2 Die Schwelle von 100 ms beim Leser

Die Werte sind nicht gemessen, sondern aus den Aufnahmen und dem Lesertakt abgeleitet.

- **Lesertakt:** Bei fortlaufendem Lesen liegen die Eingaben 7,7 ms plus die Rechenzeit des Interpreters auseinander. 100 ms sind 13 Lesertakte und fangen auch längere Rechenpausen ab, ohne dass das Dauergeräusch zerhackt wird.
- **Einzelschritt:** Er besteht aus mehreren Ereignissen bis ca. 150 ms, die kräftigen bis ca. 105 ms. Zwei Einzelschritte sind deshalb erst ab ca. 100 ms Abstand getrennt hörbar. Kommt das nächste Zeichen früher, würden sich die Geräusche überlagern, und es gilt das Dauergeräusch.
- **Kompromiss beim Ende (A-LS-5 gegen Hörbarkeit):** Das Dauergeräusch klingt nach dem letzten Zeichen noch 100 ms (ca. 13 Zeichen) nach und läuft dann 60 ms aus. Eine kürzere Schwelle lässt es schneller enden, riskiert aber, dass Rechenpausen es unterbrechen. Eine längere Schwelle lässt es länger nachklingen.
- **Eine Schwelle statt drei:** Mit getrennten Zeiten für „zweite Eingabe" und „Ende" entstünde bei Abständen dazwischen ein Wechsel aus Einzelschritten und kurzen Dauergeräuschen. Eine Schwelle vermeidet das.

Die Schwelle lässt sich über `LS_PAUSE_S` bzw. `--pause` verändern. Ob 100 ms für den Interpreter passt, zeigt sich erst im echten Lauf, vor allem wegen der Rechenzeit je Zeichen.

### 14.3 Messgrundlage und TAB

Die Messwerte stammen aus je einer Aufnahme je Gerät. TAB kurz beruht auf 9, TAB lang auf 5 Lücken. Der Tabulatorweg zu den beiden Längen ist unbekannt, deshalb gibt es nur zwei Messpunkte. Ob die Länge proportional zum Weg ist, ist offen, bis die Tabulatorabstände des aufgenommenen Testdrucks bekannt sind. Die Funktion kennt keine Spalte. Der Aufrufer wählt über `tab_lang`.

Der TAB hat kaum eigenen Klang. Die TAB-Clips sind nur wenig lauter als das Aufnahmerauschen, als Ton zählen vor allem das Timing und das schwache Ticken.

Im Dauerprint selbst ließ sich das WRZL nicht eindeutig wiederfinden. Der Mittelteil von 6 bis 19 s ist unregelmäßig, bei 19,6 bis 20,2 s ist die Aufnahme geschnitten. Die Dauer stammt deshalb aus `SW-WRZL.mp3`.

### 14.4 ±10 % auf den Takt, nicht auf den Klang

Die Zufallsdauer ändert die Zeit bis zum nächsten Zeichen, nicht den Anschlag. Das entspricht dem natürlichen Schwanken der Abstände in der Aufnahme (ca. 113 bis 125 ms) und erhält den Klang des Anschlags. Eine Dehnung des Klangs selbst würde bei einem Impulsgeräusch die Tonhöhe verändern oder künstlich klingen.

### 14.5 WAV-Dateien statt eingebetteter Arrays

Die Klänge liegen als WAV-Dateien, nicht als Arrays im Programm.

- **Dafür:** Die Player brauchen ohnehin eine Datei (`winsound` mit `SND_ASYNC` kann nicht aus dem Speicher spielen, die Kommandozeilenspieler bekommen einen Pfad). Klänge sind austauschbar, ohne Code zu ändern. Das Programm bleibt lesbar.
- **Dagegen:** Mit Arrays wäre es eine einzige Datei. Das lohnt sich vor allem bei Weitergabe als Einzeldatei. Ein Abspielen direkt aus Arrays ginge nur mit Zusatzbibliotheken wie `sounddevice`, die NumPy und unter Linux oft PortAudio brauchen.
- **Empfehlung:** Ordner `sw_toene/` im Projekt neben `c8205_interp.py` ablegen. Eine Einzeldatei-Fassung kann später entstehen (eingebetteter Block, der beim ersten Aufruf in ein Temp-Verzeichnis entpackt wird).

### 14.6 Klangqualität

- Die Klänge enthalten das Grundrauschen der Aufnahme und sind nicht entrauscht. Zwischen den Zeichen herrscht digitale Stille, das kann minimal anders klingen als die Originalaufnahme.
- Alle allgemeinen Zeichen (Leerzeichen, Ziffern, Buchstaben, Sonderzeichen) klingen gleich, denn die Aufnahme belegt keine Unterschiede nach Zeichenart. Die 24 Klänge ähneln sich im Feinverlauf kaum, das ist die geforderte leichte Variation.
- Das Leser-Dauergeräusch ist eine Schleife von 1,25 s aus einem Rauschen. Das fällt kaum auf, bei sehr langem Lesen kann ein Muster hörbar werden. Eine längere Schleife bräuchte eine längere Aufnahme.

## 15 Grenzen und offene Punkte

| Punkt | Beschreibung |
|---|---|
| Keine echte Tonausgabe geprüft | Logik, Timing und Aufrufe der Player wurden mit Platzhaltern getestet. Hören und Rhythmus unter Linux und Windows sollten einmal geprüft werden. |
| Windows spielt nur einen Klang gleichzeitig | `winsound` unterbricht den laufenden Klang. Schreibwerk- und Leserton können sich dort also gegenseitig abschneiden, falls beides gleichzeitig läuft. |
| Schwelle 100 ms | im echten Lauf prüfen und ggf. anpassen (14.2) |
| TAB-Weg unbekannt | nur zwei Messpunkte, Abhängigkeit vom Tabulatorweg offen (14.3) |
| Kleine Stichprobe | je Gerät eine Aufnahme, TAB aus 9 bzw. 5 Lücken |
| Aufrufstelle des Lesers | *Entschieden 16.10.2026 (Entwurf 63):* bei jedem vom Leser K1/K2 gelieferten Zeichen (genau eins je Zugriff, vom Projektinhaber bestätigt); die Stelle im Interpreter ist beim Einbau noch zu benennen |

## 16 Hinweise zum späteren Einbau

**Stand Stufe 4 (19.10.2026):** `sw_ton.py` ist weiterhin nicht in den Interpreter eingebaut. In GRAFIK laufen die Töne ohne Eingriff in den Interpreter: Schreibwerk über `SwSenke` und `grafik_schreibwerk.py` (Schreibwerkzeit, Klangwahl, Selektor SW), Leser über `GrafikLeser.bei_zeichen` und `grafik_geraeteton.LeserTon`, Stanzer über `GrafikStanzer.bei_zeichen` und `StanzerTon`, Rechner über `grafik_rechnerton.py`; alle über den Mischer `tonmisch` (`c-module/tonmisch.c`; `C8205-Interpreter-GRAFIK_Beschreibung.md` §6). Die Lautstärke je Gruppe stellt `--TON=pppp` (Pult, SW, LL, LS; Vorgabe 5555). Der folgende Text ist der ursprüngliche Einbauvorschlag.

Ursprünglich vorgesehen: Der Ort für das Schreibwerk ist `sw_schreibe(m, s)` in `c8205_interp.py`. Sie wird für jedes Zeichen aufgerufen, das auf das Schreibwerk geht, und `s` ist dort genau ein Zeichen oder ein Name, wie `sw_zeichen()` ihn liefert. Der Aufruf wäre `sw_ton(s)`. Für den Leser gehört `ls_ton()` an die Stelle, an der ein Zeichen von Kanal K1 oder K2 geholt wird.

Zu klären wäre beim Einbau:

- Wie wird der Ton **abschaltbar** gemacht (etwa ein Schalter in der Art von `--SW-TERMINAL`)? Mit Ton wird jeder Testlauf um die Ausgabedauer langsamer, für Regressionstests wäre `STUMM = True` nötig.
- ~~Soll auch das **Echo von Eingaben** über K0 einen Ton machen?~~ *Erledigt 16.10.2026 (Entwurf 88): In GRAFIK gibt es kein Echo, also auch keinen Ton dafür.*
- ~~Soll der TAB kurz oder lang klingen?~~ *Erledigt 16.10.2026 (Entwurf 61): ein TAB-Ton, 400 ms (`tab_400.wav`), GRAFIK_Beschreibung §6 (früher Dokument 03 §5 Nr. 17).*
- ~~Sollen alle Leserzugriffe einen Aufruf von `ls_ton()` bekommen?~~ *Erledigt 16.10.2026 (Entwurf 63): ja, je gelieferten Zeichen; GRAFIK_Beschreibung §6 (früher Dokument 03 §5 Nr. 18).*

## Teil D – Rechner- und Stanzertöne (Ergänzung 15.10.2026)

Dieser Teil ergänzt (Anforderungen jetzt in `C8205-Interpreter-GRAFIK_Beschreibung.md` §6, früher Dokument 03) die Geräusche von Schreibwerk und Leser um das Grundgeräusch des Rechners (Netz ein und aus) und um die Geräusche des Lochbandstanzers. Er hält fest, welche Töne vorliegen, was entschieden ist und was offen bleibt. **Weder `sw_ton.py` noch der Ordner `sw_toene/` enthalten diese Töne bisher.** Die Dateien liegen als MP3 vor. *(Stand 15.10.2026; seit 17.10.2026 liegen sie als WAV in `ton/` und `ton/toene_rechner_stanzer/`, `sw_ton.py` spielt sie weiterhin nicht, in GRAFIK spielen sie `grafik_rechnerton.py` und `grafik_geraeteton.py`.)*

## 17 Vorliegende Aufnahmen

Die Werte sind gemessen (Dauer, mittlerer Pegel als RMS bei Vollaussteuerung 1,0). Die Aufnahmen wurden bisher nicht angehört; die Zuordnung beruht auf den Dateinamen. Die Dateien wurden am 15.10.2026 vom Projektinhaber unter neuen, aussagekräftigeren Namen geliefert; der Inhalt ist bitgleich (Prüfsummen verglichen). Frühere Namen: `Cellatron_8205-Grundgeräusch.mp3` (jetzt `Rechner-arbeitet`), `…-Grundgeräusch-fade_in.mp3` (jetzt `Netzschalter-Ein`), `…-Grundgeräusch-fade_out.mp3` (jetzt `Netzschalter-Aus`), `LS_Motor_läuft.mp3` (jetzt `…-ohne-stanzen`). **Die Töne sind weder in `sw_ton.py` noch in das Pult-Fenster oder den Interpreter eingebaut.** *(Stand 15.10.2026; überholt, siehe Nachführung oben.)*

| Datei | Dauer | Format | Messbefund |
|---|---|---|---|
| `Cellatron_8205-Rechner-arbeitet-Grundgeräusch.mp3` | 5,9 s | MP3, 44,1 kHz, Stereo | gleichmäßiger Pegel (RMS ca. 0,05), als Schleife vorgesehen |
| `Cellatron_8205-Netzschalter-Ein-Grundgeräusch-fade_in.mp3` | 11,3 s | wie oben | Pegel steigt über ca. 6 s von 0 auf ca. 0,058, danach ungefähr gleichmäßig |
| `Cellatron_8205-Netzschalter-Aus-Grundgeräusch-fade_out.mp3` | 2,0 s | wie oben | Pegel fällt von ca. 0,045 auf 0 |
| `LS_Motor_läuft-ohne-stanzen.mp3` | 5,0 s | wie oben | Pegel sinkt in den ersten 2 s von ca. 0,09 auf ca. 0,07, danach gleichmäßig |
| `LS-Stanzer-Dauerstanzen.mp3` | 18,1 s | wie oben | gleichmäßig, Pegel ca. 0,15 (etwa dreimal so laut wie das Grundgeräusch) |

## 18 Rechner: Grundgeräusch und Netzablauf

### 18.1 Entscheidungen (Projektinhaber)

| Datum | Entscheidung |
|---|---|
| 15.10.2026 | **Der Interpreter läuft erst, wenn Lampe B auf grün schaltet.** |
| 15.10.2026 | **Einschalten:** Klick auf den Netzschalter → B schaltet auf **rot** → `fade_in` läuft → B schaltet auf **grün**. |

### 18.2 Ablauf

| Schritt | Anzeige (Lampe B) | Ton | Interpreter |
|---|---|---|---|
| Klick auf den Netzschalter (Einschalten) | rot | `fade_in` beginnt (11,3 s) | läuft noch nicht |
| `fade_in` ist abgelaufen | wechselt auf grün | Grundgeräusch als Schleife (`Cellatron_8205-Rechner-arbeitet-Grundgeräusch.mp3`) | läuft |
| Betrieb | grün | Grundgeräusch läuft endlos weiter | läuft |
| Klick auf den Netzschalter (Ausschalten) | B sofort dunkel (16.10.2026), Netzschalter rot, `fade_out` 2 s, danach beendet sich das Skript (GRAFIK-Beschreibung §3 (früher Pult-Dokument 01)) | `fade_out` (2,0 s), siehe 20 | Abbruch nach GRAFIK-Beschreibung §3 (früher Pult-Dokument 01) |

Der Zeitpunkt „B grün" ist nach der Reihenfolge der Entscheidung das Ende von `fade_in`. Ob der Wechsel genau am Ende von `fade_in` oder etwas früher erfolgt, ist nicht ausdrücklich festgelegt (siehe 21).

### 18.3 Auswirkung auf die Pult-Beschreibung (GRAFIK_Beschreibung §3, früher Pult-Dokument 01)

Die Pult-Beschreibung (GRAFIK_Beschreibung §3, früher Pult-Dokument 01, Abschnitt 5) legt bisher fest, dass B und N beim Start des Skripts sofort grün sind und ein gestartetes Skript immer einen eingeschalteten Rechner bedeutet. Das gilt nach der Entscheidung vom 15.10.2026 nicht mehr unverändert: Nach dem Einschalten gibt es eine Hochlaufphase mit B rot, in der der Interpreter noch nicht läuft. Der Befund ist im GRAFIK-Beschreibung §3 (früher Pult-Dokument 01) (Abschnitt 5, Hinweis, und offene Entscheidung 12) und im Entscheidungsregister des Hauptdokuments vermerkt. Der Prototyp des Pult-Fensters (`pult-fenster/`) ist **nicht** angepasst; er startet weiter mit B und N grün.

## 19 Lochbandstanzer

Nach der Projektdokumentation (Lochstreifenleser-Doku B3 und B5, Bedienpult-Doku) gilt für den Stanzer:

- Höchstgeschwindigkeit 50 Zeichen/s, ein Zeichen dauert 20 ms.
- Der Motor läuft nicht dauernd. Er läuft an, sobald ein Zeichen ausgegeben werden soll (Einschaltverzögerung, Hochlauf), und schaltet nach 3 s ohne Zeichen ab (Abschaltverzögerung).
- Bei gesetztem Schalter „LS" auf dem Pult läuft der Motor ständig.
- Der Interpreter bildet Puffer und Stanzvorgang zeitlich nicht nach (Wartezeit = 0). *(Gilt für den Modus TEST; in GRAFIK gilt seit Stufe 4 ein Stanztempo von etwa 50 Zeichen/s, Beschreibung §6.4.)*

Vorliegende Töne: `LS_Motor_läuft-ohne-stanzen.mp3` (Motor) und `LS-Stanzer-Dauerstanzen.mp3` (Stanzen fortlaufend). **Wie und wann sie eingesetzt werden, ist nicht festgelegt** (siehe 21). Das gilt auch für die Frage, ob ein Einzelschritt-Ton für ein einzelnes gestanztes Zeichen gebraucht wird; er liegt nicht vor.

## 20 Vorschlag zu `fade_out` (nicht entschieden)

`fade_out` ist 2,0 s lang, das Ausschalten dauert im Pult 2 s, B ist dabei dunkel (GRAFIK-Beschreibung §3 (früher Pult-Dokument 01), Entscheidung 16.10.2026). Vorschlag: `fade_out` beginnt mit dem Klick und läuft parallel zur 2-s-Anzeige, sodass der Ton beim Beenden des Skripts ausgeklungen ist. Das ist **keine Entscheidung** des Projektinhabers.

## 21 Technische Hinweise und offene Punkte

### 21.1 Technische Hinweise

- **Format:** `sw_ton.py` erwartet WAV, 44,1 kHz, mono, 16 bit. Die neuen Dateien sind MP3 in Stereo und müssten vorher umgewandelt werden. `winsound` unter Windows kann kein MP3 abspielen. *(Stand 15.10.2026; die Umwandlung ist erfolgt, alle Klänge liegen als WAV vor.)*
- **Gleichzeitige Töne:** Das Grundgeräusch läuft dauernd unter Schreibwerk-, Leser- und Stanzertönen. Unter Windows spielt `winsound` aber nur einen Klang gleichzeitig (Abschnitt 15). Ein Konzept mit gleichzeitiger Wiedergabe (z. B. Mischen vor der Ausgabe oder ein anderer Player) ist nötig. *(Seit Stufe 4: Mischer `tonmisch`, Beschreibung §6.1; unter Windows nicht übersetzt und nicht getestet.)*
- **Anschluss `fade_in` an die Schleife:** Das Ende von `fade_in` liegt im Pegel höher (ca. 0,073 in den letzten 100 ms) als der Anfang von `Cellatron_8205-Rechner-arbeitet-Grundgeräusch.mp3` (ca. 0,044). Eine Überblendung ist nicht festgelegt und müsste durch Hören geprüft werden.
- **Schleife:** `Cellatron_8205-Rechner-arbeitet-Grundgeräusch.mp3` hat Pegel 0,044 am Anfang und 0,059 am Ende der letzten 100 ms. Ob die Naht hörbar ist, ist nicht geprüft.

### 21.2 Offene Punkte

| Nr. | Frage |
|---|---|
| D-1 | **Startzustand:** GRAFIK-Beschreibung §3 (früher Pult-Dokument 01) lässt B und N beim Skriptstart grün sein. **Startzustand entschieden 16.10.2026:** Das Skript beginnt mit Rechner aus (B dunkel) und wartet auf den Klick auf den Netzschalter. **Offen:** Das Skript beendet sich beim Ausschalten komplett, wie wird es dann wieder eingeschaltet? *(Beantwortet, Beschreibung §6.5: Wiedereinschalten heißt, das Skript neu zu starten.)* |
| D-2 | **Zeitpunkt B grün:** genau am Ende von `fade_in` (11,3 s) oder früher? *(Entschieden 16.10.2026, Dialog F-14: B wird grün am Ende von `fade_in`; `fade_in` läuft in voller Länge, 11,3 s)* |
| D-3 | **Ohne Ton:** Gilt die Wartezeit des Hochlaufs auch, wenn der Ton abgeschaltet ist (`STUMM`)? Für Tests wären 11 s je Start eine erhebliche Verzögerung. |
| D-4 | **Lampe N:** Wann schaltet sie beim Einschalten auf grün, mit B oder schon früher? *(Entschieden 16.10.2026, Dialog zu F-14: N leuchtet schon nach dem Aufblenden grün, vor dem Klick; `C8205-Interpreter-GRAFIK_Beschreibung.md` §3.6, früher Dokument 01 §1.8)* |
| D-5 | **Netz aus:** Beginnt `fade_out` mit dem Klick (Vorschlag 20)? Was geschieht beim Beenden durch Strg+C oder Schließen des Fensters? *(16.10.2026: als geklärt bezeichnet; vorläufig beginnt `fade_out` mit dem Klick, siehe `C8205-Interpreter-GRAFIK_Beschreibung.md` Anhang A, F-02)* |
| D-6 | **Stanzer, Motor:** Wann spielt `LS_Motor_läuft-ohne-stanzen`: bei gesetztem Schalter „LS" dauernd, sonst ab dem ersten Zeichen bis 3 s nach dem letzten? *(Entschieden 16.10.2026, Dialog F-14: bei gesetztem LS immer; sonst endet das Geräusch **5 Sekunden** nach dem letzten Zeichen und beginnt mit dem nächsten Zeichen wieder; der Ton wirkt nicht auf die Stanzerdatei. Abweichung zu den 3 s der Projektdokumentation: **geklärt in Entwurf 53**, die 5 s gelten nur für das Geräusch (3 s sind schlecht hörbar), der Motor schaltet weiter nach 3 s ab.)* |
| D-7 | **Stanzer, Dauerstanzen:** Ab welchem Zeichenabstand gilt Dauerstanzen statt Einzelstanzen? Gilt wie beim Leser eine Schwelle? **Entschieden 16.10.2026 (Entwurf 59, dem Assistenten überlassen):** Zustandsgesteuert; Dauerstanzen ab Zeichenabstand höchstens 40 ms, Ende nach 60 ms ohne Zeichen; GRAFIK_Beschreibung §6 (früher Dokument 03 §5 Nr. 15). **Berichtigt 16.10.2026 (Entwurf 66):** Schwelle 50 ms, Abschalten nach 5 s; GRAFIK_Beschreibung §6 (früher Dokument 03 §5 Nr. 21). |
| D-8 | **Stanzer, Einzelschritt:** Wird ein Ton für ein einzelnes Zeichen gebraucht? Wenn ja, fehlt die Aufnahme. **Entschieden 16.10.2026 (Entwurf 59):** Kein Einzelschritt-Ton; Einzeltöne sind viel länger als die Stanzzeit eines Zeichens. |
| D-9 | **Aufnahmen:** Ist `LS-Stanzer-Dauerstanzen` mit oder ohne Motorgeräusch aufgenommen (ob Motor und Stanzen getrennte Ebenen sind)? Der neue Dateiname des Motortons (`…-ohne-stanzen`) legt nahe, dass er ohne Stanzen aufgenommen ist; für `Dauerstanzen` sagt der Name nichts dazu (nach Dateinamen, nicht angehört). **Standardannahme 16.10.2026 (Entwurf 59):** Dauerstanzen enthält den Motor; Motor-Pegel während Dauerstanzen 0; Hörprüfung steht aus. **Entschieden 16.10.2026 (Entwurf 66):** Motor und Dauerstanzen sind das gleiche Geräusch; GRAFIK_Beschreibung §6 (früher Dokument 03 §5 Nr. 21). |
| D-10 | **Wiedergabe:** Lösung für gleichzeitige Töne und Umwandlung der MP3 in WAV (21.1). *(Erledigt: Mischer `tonmisch` und WAV-Dateien, Beschreibung §6.1.)* |
| D-11 | **Hörprüfung** aller Aufnahmen und ihrer Zuordnung zu den Dateinamen. *(Hörprüfung 2 am 19.10.2026 vom Projektinhaber als „ok“ gemeldet, ohne Einzelbefunde; eine eigene Prüfung der Zuordnung Dateiname zu Klang ist nicht belegt.)* |
| D-12 | **Einbau:** Die fünf Aufnahmen sind noch nirgends eingebaut (Netzschalter-Ein/-Aus, Rechner-arbeitet-Schleife, Stanzer-Motor, Dauerstanzen). Der Einbau folgt nach den Entscheidungen D-1 bis D-11 (Stand 15.10.2026: keine davon getroffen). *(Erledigt: eingebaut, Rechnertöne Stufe 2, Schreibwerk, Leser, Stanzer und Mischer Stufe 4; Windows offen, Beschreibung §6.8.)* |
| D-13 | **Modi (15.10.2026):** `--MODUS=TEST` läuft ohne Töne und ohne Wartezeit des Hochlaufs (vorgegeben, D-3 ist damit für TEST erledigt); Töne gibt es nur im Modus `--MODUS=GRAFIK`. Entschieden 15.10.2026: In GRAFIK schaltet `--STUMM` die Töne ab, dann entfällt auch die Hochlaufwartezeit. Siehe GRAFIK_Beschreibung §1 und §6. |

## 22 Änderungsverzeichnis

| Stand | Änderung |
|---|---|
| 14.10.2026 | Teile A bis C: Schreibwerk und Lochstreifenleser |
| 15.10.2026 | Punkt D-13 ergänzt: Modi `--MODUS=TEST` und `--MODUS=GRAFIK` des Python-Interpreters; Modus TEST ohne Töne und ohne Hochlaufwartezeit (vorgegeben) |
| 15.10.2026 | Aufnahmen unter neuen Dateinamen übernommen (Inhalt unverändert), Punkt D-12 und Anmerkung zu D-9 ergänzt |
| 15.10.2026 | Teil D ergänzt: Rechner- und Stanzertöne, Entscheidungen zum Netzablauf (B rot → `fade_in` → B grün, Interpreter läuft erst bei B grün), offene Punkte |
| 19.10.2026 | Nachführung Stufe 4 (B-8): `sw_ton.py` und Beschreibung auf Schreibwerkzeit 80 ms (70 bis 90 ms), Zeichenklang 100 ms (gekürzt, 10 ms Ausblendung, Überlappung), ein TAB-Klang `tab_400.wav`; `tab_lang`, `TAB_LANG_VORGABE`, `ZEICHEN_STREUUNG` und `--tab-lang` entfallen, neu `--zeit`, `--streuung` in ms; Hinweis auf den Einbau über `grafik_schreibwerk.py` und `--TON`. Hörprüfung offen. Abschnitte 8, 12 bis 15 und Teil D nicht umgeschrieben (Stand der Messungen 14./15.10.2026) |
| 21.10.2026 | Abgleich mit `C8205-Interpreter-GRAFIK_Beschreibung.md` §6, dem Code, den WAV-Dateien und einem Lauf von `sw_ton.py` (OP-30 (b)): Konstanten und Beispiele aus Teil B stimmen; Nachführungsvermerk und Zusätze in Teil D (§17, §19, §21.1, §21.2); neuer Befund zu `WR` (Beschreibung OP-42; am selben Tag entschieden, siehe nächste Zeile). Messwerte und Texte der Teile A bis C unverändert. Dok. 03 lag nicht vor |
| 21.10.2026 | OP-42 entschieden und umgesetzt (0.01-005): vierte Klangart WR (`<WR>`, `sw_toene/wr.wav`, 120 ms, erste Hälfte des WRZL-Klangs vor dem markanten Ton); §7.1, §7.2, §14.1, Tabelle der Dateien und A-SW-2 nachgeführt; `sw_ton.py` und `erzeuge_wr_klang.py` angepasst bzw. neu. Messwerte und Texte der Teile A bis C sonst unverändert |
