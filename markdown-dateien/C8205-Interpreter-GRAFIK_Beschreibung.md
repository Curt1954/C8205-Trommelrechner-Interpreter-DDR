# C 8205 – GRAFIK-Interpreter: Beschreibung

Version: 0.01-004

**Stand: Gerüst, Abschnitte 1 bis 11 geschrieben (§10 mit teilweiser Triage, siehe §10.6); Prüfverfahren §1 bis §10 liegt vor (`C8205-Interpreter-GRAFIK_Pruefverfahren.md`).** Das PDF dazu (`C8205-GRAFIK_Beschreibung_A4.pdf`) wird mit `make_all_pdf.sh` erzeugt. Entstanden in Stufe 6 (Dokumentation konsolidieren); Plan und Anforderungen: Anforderungspaket Dokument 12 (fällt nach Abschluss weg).

Leser: Anwender und Entwickler des GRAFIK-Interpreters. Das Dokument ersetzt nach Abschluss von Stufe 6 die Anforderungsdokumente 00 bis 12. Alte Kennungen (F-13, S4-09 usw.) stehen im Text in Klammern und in Anhang B.

## 1 Zweck, Abgrenzung zu TEST

**Inhalt:** Zwei Modi, `--MODUS`, was in GRAFIK wirkt und was nicht

**Quellen (alt):** Dok. 00 §3.6; Dok. 11 S5-01 bis S5-07

**Zwei Modi.** Der Python-Interpreter `c8205_interp.py` hat zwei Betriebsarten, gewählt mit `--MODUS=TEST` oder `--MODUS=GRAFIK` (Vorgabe 1, 15.10.2026; Umsetzung S5-01). **Ohne Angabe gilt GRAFIK** (Entscheidung 1 zu `--MODUS`, 15.10.2026). Geschrieben werden `--MODUS=X`, `--MODUS X` und `--modus`; der Wert ist unabhängig von Groß- und Kleinschreibung, bei Wiederholung gilt der letzte (S5-02, Vorschlag des Entwicklers, in Stufe 5 umgesetzt).

| Gegenstand | `--MODUS=TEST` | `--MODUS=GRAFIK` |
|---|---|---|
| Ablauf | Stapelbetrieb: Tastenfolge der Testdatei, dann Knotenschleife bis zum Halt; verhält sich wie vor Stufe 5 (S5-04) | Dauerbetrieb am Bedienpult; Start mit ausgeschaltetem Rechner, Netzablauf über den Netzschalter (Klick → B rot → `fade_in` → B grün; der Interpreter läuft erst bei B grün) |
| Fenster | keines; bei `--SW-TERMINAL` das Fenster „SW Ausgabe“ | Bedienpult (fest 1148 × 860) und SW-Fenster (130 × 36 Zeichen), dazu das Terminal; auf 1920 × 1080 nebeneinander, Überlappung erlaubt |
| Töne | keine, keine Wartezeit des Hochlaufs | Schreibwerk, Lochstreifenleser, Rechner, Stanzer (§6); abschaltbar mit `--STUMM` |
| Trommel | persistente Textdatei `trommel.txt`, rechnerisches Modell, alle Zeiten 0, **kein C-Modul** | echte Trommel über das C-Modul (§7), mit Wartezeiten |
| Eingabe K0 | Terminal oder `--k0 datei=PFAD` | Pult (T) und SW-Fenster (SW); `--k0` wirkungslos |
| Testdatei, Makros, Testprotokoll | ja | keine; eine angegebene Testdatei wird ignoriert (S5-06) |
| Programm laden | Trommelbelegung und Tastenfolge der Testdatei | wie am echten Rechner: Objektprogramm-Lochstreifen über Leser 1 oder 2 mit dem Minimalprogramm, danach Sofortbefehl am Pult (Entscheidung 11 zu `--MODUS`) |

**Was gleich bleibt (Gleichwertigkeit, entschieden 16.10.2026, Review F-04).** Bei gleichem Programm liefern TEST und GRAFIK dieselben Ergebnisse (Registerinhalte, Ausgaben). Ausnahmen sind nur die Zeiten (in GRAFIK echte Trommel) und die Befehlsentnahme nach einem X-Abbruch (`Überblick_und_Gesamtaufbau.md`, 4.1). Jede andere Abweichung gilt als Fehler des GRAFIK-Zweigs. Der Prüfweg steht im Prüfverfahren §4.

**TEST bleibt maßgeblich.** Tests, Zeit- und Zyklenvergleiche und die Gegenprobe laufen im Modus TEST. Der Claude-Interpreter arbeitet nach den Regeln von TEST (kein C-Code, keine Fenster, keine Töne, rechnerische Trommel, Zeiten 0) und bleibt die unabhängige Gegenprobe (Entscheidung 7). Das Reproduzierbarkeitsproblem der echten Trommel betrifft nur GRAFIK.

**Fenster schließen.** Ein Klick auf X am Pult oder am SW-Fenster wirkt wie Abbruch mit Strg+C; „Netz aus“ bleibt der Netzschalter im Pult (Entscheidung 12, Review F-05). Das SW-Fenster zeigt jedes angenommene Zeichen selbst an (Dok. 09 S3-04 neu, 18.10.2026); die älteren Fassungen „ohne Echo“ sind damit überholt (Registerzeilen bleiben als Geschichte unverändert).

**Fehlerfälle in GRAFIK.** Fehlen Tkinter oder die grafische Anzeige, oder lässt sich das C-Modul nicht laden, gibt es eine Meldung im Terminal und der Interpreter beendet sich mit Rückkehrcode **16** (Entscheidung 5; S5-09).

**Unbekannter Modus.** Fehlermeldung und Rückkehrcode **2** (`c8205_interp.py` 0.03-017; Dok. 11 S5-03). Entschieden vom Projektinhaber am 19.10.2026: Dieser Wert gilt. Die ältere Registerzeile vom 15.10.2026 (Entscheidung 2 zu `--MODUS`) nennt 16; sie bleibt in Anhang A unverändert stehen und ist in diesem Punkt überholt.


## 2 Start und Schalter

**Inhalt:** `c8205_grafik.sh/.bat`, `python3 c8205_interp.py`, `--leser1/2`, `--stanzer1`, `--trommel`, `--STUMM`, `--BASP`, `--mdverz`, `--HWCHECK`, Rückkehrcodes

**Quellen (alt):** Dok. 05 F-08, F-13; Dok. 11

**Aufruf.**

```
./c8205_grafik.sh [Schalter ...]          (Linux; Windows: c8205_grafik.bat, ungetestet)
python3 c8205_interp.py [Schalter ...]    (gleichwertig; ohne --MODUS startet GRAFIK)
```

`c8205_grafik.sh` reicht alle Schalter unverändert an `c8205_grafik.py` weiter. Der Stapelbetrieb mit Testdatei braucht `--MODUS=TEST`; `c8205_interpreter.sh` und `.bat` setzen das selbst (S5-08). Wer eine Testdatei ohne `--MODUS=TEST` angibt, bekommt auf `stderr` den Hinweis „Testdateien werden im Modus GRAFIK ignoriert; fuer Testlaeufe --MODUS=TEST angeben.“ und der Lauf geht als GRAFIK weiter (S5-06, bestätigt 19.10.2026, O5-1).

**Schalter, die in GRAFIK wirken** (nach `c8205_grafik.py`, `hauptprogramm()`):

| Schalter | Wirkung |
|---|---|
| `--MODUS` | siehe §1 |
| `--leser1 ORDNER`, `--leser2 ORDNER` | Ordner mit nachrückenden Lochstreifendateien; gelesene wandern in `LOCHSTREIFENKORB` (Register 15.10.2026). Standard `virtuelle_Geraete/Leser1` und `/Leser2`; beide müssen verschieden sein, sonst Fehler (16) |
| `--stanzer1 ORDNER` | Ausgabeordner des Stanzers; Standard `virtuelle_Geraete/Stanzer1` |
| `--trommel PFAD` | Trommeldatei (seit 15.10.2026); Standard `virtuelle_Geraete/Trommel/trommel.txt`. Sie ist der Speicher des Rechners, Programme verändern sie; wer die Ausgangsbelegung behalten will, sichert sie oder gibt eine eigene Kopie an. Neben ihr liegt die Schalterdatei der Bahnsperren (`trommel.basp`) |
| `--BASP abcdef` | Bahnsperrenschalter, sechs Ziffern 0/1; wirkt in GRAFIK über das C-Modul (`bahnsperre_setzen`), wird im Pult nicht angezeigt; ohne Angabe gilt die Stellung der Schalterdatei (anlegen mit `000000`) |
| `--STUMM` | schaltet alle Töne ab; damit entfällt auch die Wartezeit des Hochlaufs (Entscheidung 6) |
| `--TON pppp` | Lautstärke je Gruppe (Pult, SW, LL, LS), vier Ziffern 0 bis 9, 5 = Voreinstellung, 0 = stumm; wirkungslos mit `--STUMM` |
| `--TASTATUR de\|en` | Tastaturbelegung beim Abspielen einer Klickspur und im Protokoll; Standard `de` |
| `--HWCHECK` | zweites Fenster mit BZ, BR, Spur/Sektor, AC und <<AR>> (§8) |
| `--mdverz VERZ` | Ordner mit den Dokumenten, aus denen der Knotengraph gelesen wird; Standard `markdown-dateien` |
| `--DEBUGLOG [DATEI]`, `--AUFZEICHNUNG [DATEI]`, `--WIEDERGABE [DATEI]` | Fehlersuche: Protokoll, Aufzeichnung und Wiedergabe einer Klickspur (Prüfverfahren §5) |
| `--pult-protokoll`, `--netz-schnell`, `--ohne-fenster`, `--entwickler-tasten`, `--entwickler-k0` | Entwicklerschalter für Prüfungen, nicht für den Betrieb |

*Herkunft:* `--TON`, `--TASTATUR`, `--DEBUGLOG`, `--AUFZEICHNUNG` und `--WIEDERGABE` wurden im Zuge der Entwicklung vom Projektinhaber beauftragt (Auskunft 19.10.2026); Dok. 11 S5-05 führt sie nicht auf. Einzelheiten stehen bei §6 (`--TON`) und im Prüfverfahren §5 (Klickspur).

**Wirkungslos, ohne Fehler:** `--k0`, `--sw-ausgabe`, `--NO-TERMOUT`, `--zwischenablage`, `--SW-TERMINAL`, `--out`, `--knotentest`, `--lochbandleser1/2`, `--lochbandstanzer1`, `--pruefe-stanzer1`, `--pruefe-sw-ausgabe` und das positionale Argument `tests` (Entscheidung 11 und 3 zu `--MODUS`; Review F-13, entschieden 16.10.2026). `--version` und `-h`/`--help` liefern in jedem Modus die Ausgabe des Interpreters (S5-07, Vorschlag).

**Rückkehrcodes** (`c8205_grafik.py`, `RC_OK, RC_ABBRUCH, RC_START = 0, 8, 16`): **0** normal; **8** Abbruch mit Strg+C oder durch Schließen eines Fensters; **16** Start nicht möglich (fehlendes Tkinter oder Anzeige, C-Modul nicht ladbar, ungültiger Schalterwert wie `--BASP` oder `--TASTATUR`, beide Leser auf demselben Ordner, Fehler in der Klickspur). Ein unbekannter `--MODUS` gibt **2** (siehe §1).


## 3 Bedienpult-Fenster

**Inhalt:** Layout, Lampen, Farben, Netzablauf, Lampentempo, Betriebsmodus, Bedienablauf, Zuordnung T/SW/SP/BS/LS, E unter M

**Quellen (alt):** Dok. 01 §1 bis §6, 08

Das Bedienpult-Fenster (Tkinter) gibt es nur im Modus GRAFIK. Es bildet das Foto des Bedienpults ab (Lampen, Tasten, Schlüsselschalter), zeigt den Zustand des Rechners an und nimmt die Bedienung entgegen. Die Regeln der Tastenbedienung stehen in §4, die Sperren und Verriegelungen in `C8205-Interpreter-Bedienpult_mit_Schaltern.md`; GRAFIK führt dafür nichts Eigenes ein: Sind die Tasten bedienbar, reagieren sie wie im TEST beschrieben (Review F-14, 16.10.2026). Alte Kennungen aus Dokument 01 und 08 stehen in Klammern.

### 3.1 Fenster, Layout, Bildschirm

- **Layout.** Als Vorlage dient das Foto des Bedienpults (Abb. 2) mit Lampenfeld, Tastatur (Abb. 3 und 4), Kanaltasten und Selektoren. Das Fenster ist **fest 1148 × 860 Pixel** groß und wird nicht skaliert (Entscheidungen 13.10. und 16.10.2026; Review F-05). Das Foto ist ein einziges Hintergrundbild und wird nie neu gezeichnet; jede Lampe und jede Taste ist ein eigenes Bildobjekt, dessen Grafik nur bei Zustandsänderung getauscht wird (Dok. 01 §6.2; am laufenden Fenster nicht bestätigt).
- **Teilgrafiken** liefert der Projektinhaber: Tasten (je `-dunkel` und `-hell`), große Lampe (`dunkel`, `hell`, `hell-grün`, `hell-rot`, `dunkel-rot`, 26 × 26 px), kleine Lampe (`Diode-dunkel`, `-hell`, 14 × 14 px), Schlüsselschalter (`schlüssel-ein`, `-aus`, 40 × 41 px). Neun Tasten (0, 2, 4, 6, 8, −, „,“, D, ZR) hat der Entwickler nach Vorbild ergänzt (Näherung); damit hat jede aktive Taste ein Grafikpaar. Lage und Zuordnung stehen im Manifest in `pult/` (Maßstab 860 px).
- **Bedeutung von „hell“** (bestätigt 16.10.2026, Entwurf 81): bei Tasten **gedrückt** (hell beschriftet, helle Umrandung, abgesenkt), bei Lampen **leuchtet**.
- **Entfallen** sind die vier unbeschrifteten unteren Selektortasten unter SP, BS, LS und SW; sie sind nur Teil des Fotos. Das Lösen eines Selektors geschieht durch erneuten Klick. Aktiv sind 38 Tasten.
- **Bildschirm.** Zielbildschirm 1920 × 1080; zu sehen sind drei getrennte Fenster: das Terminal, daneben das Pult, daneben darunter das SW-Fenster (§5). Pult und SW-Fenster dürfen sich überlappen. Auf kleineren Bildschirmen wird das Pult trotzdem in fester Größe geöffnet (Standardannahme, F-05). Die Fensterlage wird gemerkt (FL-001, `grafik_fensterlage.py`); Einzelheiten beim Füllen von §10 zu prüfen.
- **Schließen.** X am Pult ist wie Abbruch mit Strg+C; zweimal Strg+C beendet sofort (§4, §1).

### 3.2 Lampen

Die Konvention des Handbuchs gilt: Die Lampe heißt wie das Flag („Lampe = Anzeige“). **Rot und grün gibt es nur für die Lampen B und N**, alle anderen Lampen kennen hell und dunkel.

| Lampe | Quelle | Anmerkung |
|---|---|---|
| E, A, T, SW, K1, K2, K3, FE, BS, US, H | `m.fl[...]` gleichen Namens | direkt |
| FÜ | `m.fl['FUE']` | anderer Schlüsselname |
| **R** | nicht Flag H | Lampe R leuchtet, wenn der Schalter R gedrückt ist (H und R sind gegeneinander verriegelt; Lampe R = nicht Lampe H), **unabhängig von Haltgründen** (Review F-09, entschieden 16.10.2026, berichtigt in Entwurf 33; ein Haltgrund US, BS, FÜ, FE, E, A ändert daran nichts; es gibt kein eigenes Flag R) |
| **B** | Betriebsanzeige | siehe 3.5; rot nur im Hochlauf |
| **N** | Netz liegt an | leuchtet **immer grün**, solange das Programm am Terminal gestartet und das Pult sichtbar ist: vor dem Einschalten, im Hochlauf, im Betrieb und beim Ausschalten bis zum Schließen (Entwurf 80) |
| AR (12 kleine Lampen) | `m.adr` | **Adreßteil des Befehlsregisters** (Lampenreihe „AR“), nicht das Register `m.AR` (Review F-10, 16.10.2026); Triaden mit den Gewichten 4, 2, 1 |
| OR (9 kleine Lampen) | `m.OR`, Bit 8 … 0 | Triaden B, A, Z |
| V1, V2 | `m.fl['V1']`, `m.fl['V2']` | |

Insgesamt 15 große und 23 kleine Lampen (12 AR, 9 OR, V1, V2). Die Lampen T und SW zeigen die Flags T und SW (Kanal K0, Teilflags). Bei Halt zeigen FE (Fehler Eingabe), FÜ (Überlauf), BS (bedingter Stopp) und US (unbedingter Stopp) den jeweiligen Haltzustand; H und R werden von der Stellung H–R gesteuert (Nr. 21 und 22 des Bedienablaufs, 3.7).

*Hinweis:* Die Datenstruktur-Doku sagt, im Zustand „Rechnen“ dürfe von den Lampen H, R, US, BS, FÜ, FE, E und A nur R leuchten. Das gilt nur, solange kein Haltgrund besteht; maßgeblich ist die Entscheidung F-09 (Register 16.10.2026).

### 3.3 Tasten, Schalter und Selektoren

38 aktive Tasten: Kanal K0 bis K3; Selektoren SP, BS, LS und **Selektor SW** (Manifest-Name `SW_umschalt`, rechts außen, nach dem Foto „SW“); Eingriff H, E, M, T, R, G, Ü, SW (Tastatur) und ST; Eingabe B, +, 1, 3, 5, 7, 9, „.“, „:“, D, −, 0, 2, 4, 6, 8, „,“, ZR, IS, IB, WM. D ist die Sondertaste für den Programmbaustein-Ansprung des BIS.

**Wippe T-SW (Review F-06, entschieden 16.10.2026, Entwurf 50 und 71).** „T-SW“ ist eine mechanisch verbundene Kombination zweier Tasten, T und SW der Tastatur, von denen immer genau eine gedrückt ist (wie H und R). Es gibt keine dritte Bedienstelle. Der **Selektor SW** rechts außen ist davon unabhängig. Die Tastatur hat keine weitere Taste SW. Die Lage von T und SW im Foto ist „geschätzt, Treffer unsicher“ (Manifest).

| Element | Wirkung im Interpreter | Rastverhalten | bei R gesperrt |
|---|---|---|---|
| Taste T | Flag T := 1, Flag SW := 0 (Token `SW=0`) | rastet ein, löst SW | **ja** (Entwurf 71) |
| Taste SW | Flag SW := 1, Flag T := 0 (Token `SW=1`) | rastet ein, löst T | **ja** (Entwurf 71) |
| SP | Flag SP := 1, solange eingerastet | einrastend | nein |
| BS | nur Schalterstellung; Flag BS wird erst 1, wenn ein „Bedingter Stopp“ bei eingerastetem BS wirksam wird | einrastend | nein |
| LS | Stanzermotor läuft ständig; ohne Wirkung auf die Stanzerdatei, nur Ton (3.7) | einrastend | nein |
| Selektor SW | unterdrückt neue SW-Ausgabe (3.7) | einrastend, je für sich | nein |

Die Taste G setzt K0 an und leitet daraus das Flag ab: Schalter SW gedrückt → SW := 1, sonst T := 1. Die Stellung T/SW wirkt auf die **Eingabe**: Stellung SW heißt Eingabe nur im SW-Fenster, Stellung T nur über Klicks im Pult; beides gilt nur bei angewähltem K0 und aufgestelltem Eingabe-Halt (Vorgabe 6 zu `--MODUS`). Sie hat keinen Einfluss auf die Schreibwerk-Ausgabe über K2.

**Startzustand der Tasten** (entschieden 16.10.2026, Review F-14): alle Schalter und Tasten ungedrückt, **außer H und T-SW in Stellung T**; die Taste K0 ist eingerastet und Kanal K0 angewählt (Entwurf 96; ersetzt Entwurf 76). Lampe R ist dunkel (R = nicht H), andere Lampen als N und B sind dunkel, solange der Rechner aus ist.

**Bahnsperrenschalter.** Der rückseitige Bahnsperrenschalter (6 Schalter) gehört zur Trommel (`bahnsperre_setzen`, §7) und wird im Pult **nicht angezeigt** („gar nicht anzeigen“, 16.10.2026, Entwurf 86, O-9; keine Zusatzleiste). Die Stellungen kommen über `--BASP` und die Datei neben der Trommel.

### 3.4 Netzschalter und Netzablauf

Der Netzschalter ist der **Schlüsselschalter unter der Lampe N** (Grafiken `schlüssel-ein` grünlich, `schlüssel-aus` rötlich; „der Netzschalter ist rot“ heißt `schlüssel-aus`). Dok. 01 §3.4 nannte dies „nach meiner Lesart“ mit der Bitte um Bestätigung; **der Projektinhaber hat es am 19.10.2026 bestätigt** („ja“ auf den Vermerk in Checkpoint G6-006). Bestätigt („Ja, so ist es genau“, 16.10.2026) ist, dass „der Netzschalter ist rot“ die Grafik `schlüssel-aus` meint; der Bedienablauf (Review F-14) setzt den Schlüsselschalter als Netzschalter voraus.

| Schritt | Verhalten |
|---|---|
| Start | Im Terminal wird der Interpreter im Modus GRAFIK gestartet; Pult- und SW-Fenster werden aufgeblendet. Rechner **aus**: Schlüsselschalter `aus`, N grün, B dunkel, Tasten wie 3.3; **nur der Netzschalter nimmt Klicks an** (Entscheidung 16.10.2026; ersetzt „gestartetes Skript = eingeschalteter Rechner“) |
| Einschalten (Klick) | Netzschalter sofort grün (`schlüssel-ein`), **B rot**, Ton `fade_in` läuft in voller Länge (**11,3 s**, die Länge der Aufnahme; die frühere Schätzung „5 bis 6 s“ ist überholt). Während des Hochlaufs nehmen die Tasten keine Klicks an |
| Hochlauf zu Ende | am Ende von `fade_in` wird **B grün**; erst jetzt gilt der Rechner als eingeschaltet und läuft der Interpreter. Die Tasten sind im Rahmen ihrer natürlichen Abhängigkeiten bedienbar. Das Grundgeräusch (Schleife) beginnt (§6) |
| Klick im Hochlauf | Netzschalter wieder rot, `fade_in` **bricht ab**, `fade_out` läuft (es läuft immer nur einer von beiden), **B dunkel**; nach Ende von `fade_out` endet das Programm. Seltener Fall (F-02 Nr. 2 und 4, ersetzt die Annahme „wirkungslos“) |
| Ausschalten bei laufendem Rechner (Klick) | `schlüssel-aus`, **B sofort dunkel** (nicht rot; Entwurf 45), N bleibt grün, `fade_out` läuft (rund 2 s); danach endet das Skript **komplett**, Pult- und SW-Fenster werden abgeräumt, Rückkehrcode 0 |

Technik: Das Fenster meldet `NETZ_AUS` über einen Rückkanal; der Interpreter beendet sich kontrolliert an einer Knotengrenze (Dateien schließen, Trommel ausschalten, Stanzer und SW-Datei sauber abschließen). B ist nur beim Einschalten rot. Mit `--STUMM` entfällt die Wartezeit des Hochlaufs; B wird nach dem Klick sofort grün (§2).

### 3.5 Lampentempo und ruhiges Bild

- **Tempo der Befehle** (Review F-07, entschieden und präzisiert 16.10.2026, Entwurf 82): Die Befehle laufen **ungebremst**; verlangsamt werden sie nur dadurch, dass auf Trommel, Stanzer, Leser und SW gewartet werden muss. Keine weitere künstliche Verzögerung, kein Takt-Schalter. Die Zahl „rund 1900 Einzelbefehle/s“ bei zeitoptimaler Lage ist keine Vorgabe, nur die Größenordnung.
- **Anzeigetakt:** Das Fenster fragt alle **40 ms** ab (höchstens 25 Bilder pro Sekunde); kommen mehrere Zustände an, wird nur der letzte gezeichnet. Bei jedem Halt (auch nach einem E-Schritt) wird der Stand **sofort** gemeldet. Der Takt betrifft nur die Anzeige, nicht die Befehle.
- **Ruhiges Bild** (Entwurf 84, Durchgang O-5; Wortlaut des Projektinhabers: „Lass die Lampen so leuchten, dass das Bild ruhig ist.“): Die Lampen springen im Dauerlauf nicht mit jeder Momentaufnahme. Das Wie ist dem Entwickler überlassen. **Standardannahme (nicht bestätigt):** Mittelung statt Momentaufnahme: Die Lampenzustände werden zeitgesteuert abgetastet, das Pult beurteilt jede Lampe über das Fenster der letzten 40 ms; sie leuchtet ab 60 % Anteil „an“, ist dunkel bis 40 %, dazwischen bleibt der bisherige Zustand (Hysterese). Es bleiben zwei Grafiken (hell, dunkel); ein abgestuftes Nachleuchten entfällt. Schwellen und Fenster sind Konstanten und werden bei der Handabnahme am laufenden Fenster geprüft (Prüfverfahren §7).

### 3.6 Bedienablauf: vom Einschalten bis zum Start eines Programms

Der Ablauf wurde mit dem Projektinhaber am 16.10.2026 Schritt für Schritt festgelegt (Review F-14) und dient als Abnahmeszenario (Prüfverfahren §7). Nr. 1 bis 6: siehe 3.4. Weiter:

| Nr. | Schritt | Festlegung |
|---|---|---|
| 7 | Voraussetzung | Programmstart erst, wenn das **Minimalprogramm (MP)** geladen ist |
| 8 | MP laden: Tasten | H ist gedrückt; dann **G, M halten (M+), E, E, M lösen (M−), K1, R**; das **KEP** wird angesprungen. Mit Leser 2 statt Leser 1: **K2** statt K1 |
| 9 | MP laden: Lochstreifen | In Leser 1 (K1), alternativ Leser 2 (K2), liegt als Datei im Leserordner ein **binär kodierter Lochstreifen mit dem BIS-Minimalprogramm**. Das KEP liest ihn und speichert das MP ab Adresse 0040; am Lochstreifenende bleibt es stehen |
| 10 | Sprung in Zelle 0000 | beim Abspeichern trägt das KEP in Zelle 0000 einen Sprung zum MP ein |
| 11 | MP starten | **H, G, R**: G stellt BR auf „0000 000“, R führt ihn aus, der Ablauf springt ins MP |
| 12 | Eingabe eines Befehls mit Kennzeichen | Zuerst können **Leitadressen** gesetzt werden; es sind die verschiedenen Möglichkeiten, eine Leitadresse einzugeben: **20 aaaa** = Relativadresse, **21 aaaa** = 1. Leitadresse, … **29 aaaa** = 9. Leitadresse |
| 13 | Anwenderprogramm laden *(Bedeutung von `01.` gegen das BIS-Dokument nicht geprüft, außerhalb des Umfangs, OP-33)* | Leserkanal wählen (K1 oder K2), dann **`01.`** eingeben (Kennzeichen K₁ = 0, K₂ = 1: fortlaufende Eingabe von Objektkodebefehlen mit Addition der 1. Leitadresse). Die Adressen des Objektkodes werden entsprechend dem Kennzeichen LEITADRESSE (00 bis 09) mit der zuvor eingegebenen Adresse verschoben |
| 14 | Programmstart | **`10 aaaa`** verlässt das MP; `aaaa` ist die **Startadresse im Speicher**. *Beispiel 1:* Programm relativ bei 0000, `21 1200` gegeben → Start mit `10 1200`. *Beispiel 2:* relativ bei 0200, `21 1200` → Start mit `10 1400` (oktal) |

Das KEP gelangt **nicht** über Pult oder GRAFIK auf Spur 0; es muss anderweitig dorthin (z. B. mit einem TEST oder von Hand in die Trommeldatei; Pflege durch den Projektinhaber, F-03). Der Objektkode-Lochstreifen kommt wie das MP als Datei in den Leserordner (Erzeugung: Assembler und `c8205_lochstreifen_umwandlung.py`). Die BIS-Einzelheiten (Kennzeichen, Leitadressen, Befehl `01.`) legt dieses Dokument nicht neu fest; sie stehen in der BIS-Dokumentation (in Dok. 01 nicht geprüft). In den Nr. 14 bis 25 sind einige Standardannahmen nicht ausdrücklich bestätigt (siehe §10).

### 3.7 Bedienung während des Programmlaufs und Ende

Das Pult ist in Teilen **interruptfähig**, also jederzeit bedienbar, auch während die Befehlsverarbeitung läuft (Dialog F-14, 16.10.2026, Entwurf 48):

| Nr. | Element | Festlegung |
|---|---|---|
| 15 | Taste **H** | jederzeit; unterbricht die Befehlsverarbeitung; danach ist das Pult wieder normal bedienbar. Der Interpreter prüft an der Befehlsgrenze (Knoten 2); dass das auch in GRAFIK so ist, ist Standardannahme (ja) |
| 16 | **K0 bis K3** | jederzeit |
| 17 | **Selektor SW** | jederzeit; unterdrückt die SW-Ausgabe, der Rechner macht weiter (unten) |
| 18 | **SP, BS, LS** | jederzeit |
| 19 | **Netzschalter** | jederzeit (3.4) |
| 20 | **Wippe T-SW** | **nicht** im Lauf R: Rollensperre, nur bei H bedienbar (Entwurf 71) |
| 21 | Flags **FE, FÜ, BS, US** | die Lampen zeigen den Haltzustand |
| 22 | Stellung **H–R** | steuert die Lampen H und R |

**Selektor SW (Entwurf 49 bis 52, bestätigt).** Eingerastet bleibt der bestehende Text im SW-Fenster sichtbar, neuer Text wird nicht ausgegeben; der Rechner arbeitet die Ausgabebefehle weiterhin korrekt ab (Register, Flags, Ablauf wie ohne Selektor). **Keine Ausgabe heißt kein Warten:** die Schreibwerkzeit (10 Zeichen/s) entfällt, es gibt weder Tastengeräusch noch Tastenverzögerung. Wird der Selektor gelöst, geben Ausgabebefehle ab diesem Moment wieder aus, mit Geräusch und Verzögerung; unterdrückter Text wird nicht nachgeholt. Der Selektor berührt weder Flags noch die Lampe SW und wirkt **nur auf das Schreibwerk** (Leser, Stanzer und Rechnergeräusch bleiben unberührt). Die Dateiausgabe `--sw-ausgabe` und die Terminalausgabe gibt es in GRAFIK nicht (Standardannahme).

**Stanzer im Lauf (Entwurf 52 und 53).** Der Selektor SW gilt für den Stanzer nicht; der Stanzer hat im Lauf keine eigene Bedienung. Der Schalter LS wirkt nur auf den **Ton**: Ist LS gesetzt, wird das Stanzergeräusch immer gespielt, sonst endet es **5 Sekunden** nach dem letzten Zeichen und beginnt mit dem nächsten wieder. Der Ton hat keine Wirkung auf die Stanzerdatei. Die 5 s gelten nur für das Geräusch (3 s sind schlecht hörbar); der Motor schaltet laut Projektdokumentation weiterhin nach 3 s ab. Diese Aufteilung ist eine Festlegung des Bearbeiters auf Delegation („mach wie du denkst“), nicht der Wortlaut des Projektinhabers (§6).

**Ende des Programmlaufs (Entwurf 54).**

| Nr. | Ende | Festlegung |
|---|---|---|
| 23 | Programm hält selbst | Stopp-Befehl (Lampe US), bedingter Stopp bei eingerastetem BS (Lampe BS) oder Überlauf (Lampe FÜ): das Pult zeigt nur die Lampe und wartet auf ST, Ü, M, E wie im TEST. Nichts Zusätzliches: keine Meldung im Terminal, kein Ton |
| 24 | Eingriff am Pult | z. B. H (Nr. 15) |
| 25 | Netzschalter | Ablauf 3.4, Rückkehrcode 0 |

### 3.8 E und M+ E im Halt

Festlegung des Projektinhabers (18.10.2026): E und M+ E wirken **so, wie es im Interpreter programmiert ist** (TEST: `c8205_interp.py` 0.03-015; GRAFIK: `c8205_grafik.py` G2-012, Pult G2-010). Die erste Fassung vom 17.10.2026 („jedes E erhöht BZ um 1 …“) ist gestrichen. Es gilt nur im Halt; bei Stellung R sind E und M gesperrt.

1. **E ohne M: Einzelschritt, der Befehl im Befehlsregister wird ausgeführt** (Sprünge und Trommelzugriffe eingeschlossen). **Niederdrücken** (`E+`) gibt Phase IV und I frei, der Automat hält vor Phase II (Knoten 8). **Loslassen** (`E-`) durchläuft Phase II und III und hält vor Knoten 19. `E` ist der kurze Anschlag. BZ ändert sich durch die Befehlsentnahme (+1) oder einen Sprung, nicht pauschal um 1. Steht der Automat nach einem E unter M schon vor Phase II, gibt es beim Niederdrücken nichts freizugeben.
2. **M+ E (M gedrückt oder gehalten, dann E): Phase II entfällt.** Schon das Niederdrücken erhöht **BZ um 1 und setzt AR := BZ**. Der AC enthält im Adressfeld BZ+1 (übrige Stellen 0); die Lampenreihe AR (`m.adr`) zeigt das erhöhte AR (seit 0.03-015 / G2-011). Das Loslassen von E unter M ist ohne Wirkung. Nach G gilt das erste E unter M als Sonderfall: BZ := 1, AR := 1.
3. BZ und AR zählen in 12 Bit, nach 7777 (oktal) folgt 0000.
4. Prüfbar im HW-Check-Fenster (§8): Nach n Klicks auf E unter M+ sind BZ und AR um n gestiegen. Der Test `KepUeberPult` endet mit BZ=2404, AC=22060635124 (Pult-Tests 65 von 65 bestanden, Stand G2-012); Bedienablauf 3.6 Nr. 8 gilt unverändert.
5. TEST und GRAFIK verhalten sich gleich (Gleichwertigkeit 191 von 191, Stand G2-011); nur TEST kennt allein den ganzen Anschlag `E`. Die Klick-Zuordnung (`E+`, `E-`) steht in §4.3.

**Offen (nicht entschieden, §10):** (a) Nach `E+` zeigt BR noch den alten Befehl, dessen Operation (Phase IV) schon ausgeführt ist; BZ kann einen Zwischenwert zeigen: Entspricht der Knotenautomat hier der Anlage? (b) G bei gehaltenem E löscht wie bisher, das Loslassen tut danach nichts; Handbuch 4.1 Nr. 2 sieht nur das Löschen des Überlaufs vor, nicht umgesetzt.

### 3.9 Aufbau der Pult-Software und Threads

Das Fenster läuft im Hauptthread, der Rechner in einem eigenen Thread. **Alle Pult-Tasten werden nur vorgemerkt und im Rechner-Thread ausgeführt**: Der Einzelschritt E kann im Eingabe-Halt auf ein K0-Zeichen warten; im Fenster-Thread blockierte er das ganze Fenster (Fehler des Projektinhabers, Strg+C ohne Wirkung). Strg+C setzt nur ein Flag, das Fenster beendet im Takt; **zweimal Strg+C beendet sofort**; eine Ausnahme im Takt oder im Rechner-Thread beendet weder Takt noch Thread.

| Datei | Aufgabe |
|---|---|
| `grafik_pult.py` | Pult-Steuerung ohne Tkinter: Netzablauf, Tastenregeln, Lampen, Zeichenliste, Weitergabe an den Rechner |
| `grafik_pult_fenster.py` | Tk-Schicht: Canvas, Maus, Computertastatur, Schließen; Takt 40 ms |
| `grafik_ton.py`, `ton/` | Töne des Rechners (§6) |
| `grafik_hwcheck.py` | Hardware-Check-Fenster (§8) |
| `pult/` | Manifest, Foto, Teilgrafiken |
| `c8205_grafik.py` | Start öffnet das Pult-Fenster; Entwicklerschalter `--ohne-fenster`, `--netz-schnell`, `--pult-protokoll` (§2) |

Die Zählung der GRAFIK-Module (G1 bis G5) steht in `C8205-Versionierung.md`; die Aufteilung in §11.

*Nicht in §3 übernommen (noch zu verarbeiten, siehe Checkpoint G6-006):* Dok. 01 §4 (Befunde), §7 (offene Entscheidungen), §8 (Erkenntnisse und Risiken), §9 (Plattformen) und §10 (Nächste Schritte); Dok. 08 §4 (offene Einschränkungen der Abnahme Stufe 2). Die Zeichenabbildung des SW-Fensters aus Dok. 01 §1.7 kommt nach §5.


## 4 Bedienung

**Inhalt:** Mausregeln, Computertastatur, Fokus, Touchscreen, Sperren (M-15 bis M-35)

**Quellen (alt):** Dok. 06

Das Bedienpult wird mit der Maus bedient; die Computertastatur wirkt nur auf die Eingabetasten und auf die Umschalttaste. Die Nummern in Klammern sind die alten Kennungen aus Dokument 06 (M-15 bis M-35). Welche Taste wann gesperrt ist, steht in `C8205-Interpreter-Bedienpult_mit_Schaltern.md` (Rollensperre, Entriegelung, Verriegelung H gegen R, Verriegelung von ST) und gilt für Maus und Tastatur gleich (M-17, keine eigene Regel).

### 4.1 Auslösung und Tastenarten

Jede Taste löst **beim Drücken der Maustaste** aus, nicht erst beim Loslassen. Jede Taste hat ihren eigenen Zustand und ihren eigenen Timer; ein zweiter Klick innerhalb der 0,25 s gilt als neuer Tastendruck und startet die 0,25 s neu (M-15). Die Zeit 0,25 s (statt früher 0,4 s) gilt seit dem 17.10.2026 und ist einstellbar.

| Art | Tasten | Verhalten |
|---|---|---|
| Klick-Taste | B, +, 1, 3, 5, 7, 9, ·, :, IS, IB, G, Ü, D, −, 0, 2, 4, 6, 8, „,“, ZR, WM, ST | Klick: 0,25 s die gedrückte Grafik, dann wieder normal; die Maus muss nicht gehalten werden |
| Rastende Paare | H und R, T und SW | je Paar ist immer genau eine Taste eingerastet (dauerhaft hell); einfacher Klick auf die andere rastet sie ein und löst die erste; Klick auf die eingerastete ändert nichts; kein Aufleuchten, kein Umschalt (M-19, M-20) |
| Halte-Tasten | E, M | kurzer Klick: 0,25 s hell; Maustaste gehalten: gedrückt, solange gehalten; Umschalt+Klick ersetzt das Halten (4.3) |
| Kanalwahl und Selektoren | K0 bis K3; SP, BS, LS, Selektor SW | K0 bis K3 rasten ein, immer genau eine (wechselseitig, auch bei R); Start: K0 eingerastet. SP, BS, LS und SW rasten je für sich ein, erneuter Klick löst; kein Aufleuchten (M-34) |

T-SW ist **ein** Schalter mit den Stellungen T und SW (Beschriftung „SW“) und ist von der Rollensperre betroffen: bei Stellung R gesperrt, nur bei H bedienbar, wie E, M, G und Ü (M-18, bestätigt 16.10.2026). Wechselt der Kanal per Befehl im Programm, folgen die Lampen K1 bis K3 bzw. T und SW, die Rastung der Taste nicht (Auslegung, nicht ausdrücklich bestätigt; M-34 Nr. 1).

### 4.2 Sperren bei Stellung R

Gesperrt sind bei R: E, M, G, Ü und der Schalter T-SW. Die acht Tasten K0 bis K3, SP, BS, LS und SW sind bei R **nicht** gesperrt (M-34 Nr. 3). Die 21 Eingabetasten sind bei R nicht mechanisch gesperrt, sondern **nur elektronisch verriegelt** (bestätigt 17.10.2026): Sie lassen sich klicken, wenn der Rechner auf eine K0-Eingabe wartet (Eingabe-Halt, Kanal K0, Stellung T), sonst nicht.

Ein Klick auf eine gesperrte Taste bewirkt **nichts**: kein Aufleuchten (auch nicht 0,25 s), kein Ton, keine Meldung, nichts wird an den Interpreter weitergegeben, kein Flag ändert sich (M-25).

### 4.3 E und M: Halten, Umschalt+Klick, E+ und E-

- **Gehaltene Maustaste (M-16, bestätigt).** Die Taste gilt als losgelassen, sobald die Maustaste losgelassen wird, egal wo der Zeiger steht; wandert der Zeiger bei gehaltener Maustaste weg, bleibt die Taste gedrückt; wurde kürzer als 0,25 s gehalten, bleibt sie trotzdem die vollen 0,25 s hell.
- **Umschalt+Klick (M-21, bestätigt).** Umschalt+Klick auf E oder M hält die Taste dauerhaft gedrückt und hell, wie eine eingerastete Taste; ein weiterer Umschalt+Klick lässt sie los; ein normaler Klick auf eine so gehaltene Taste ändert nichts. E und M können gleichzeitig gehalten werden (z. B. `M+ E … E M-`). Die Rollensperre gilt auch für Umschalt+Klick.
- **R bei gehaltenem E oder M (berichtigt 16.10.2026).** Ein Klick auf R bleibt **wirkungslos** (wie 4.2), solange E oder M gehalten ist, weil R mechanisch die Rollensperre auslöst und das nur bei nicht gedrückten gesperrten Tasten geht. Ein Klick auf R innerhalb der 0,25 s nach einem kurzen Klick auf E oder M **wirkt sofort**; die 0,25 s sind nur die Darstellung eines kurzen Tastendrucks (Entscheidung des Entwicklers, vom Projektinhaber überlassen).
- **Andere Tasten (M-26).** Die Umschalttaste hat bei allen anderen Tasten keine Wirkung; Umschalt+Klick verhält sich dort wie ein einfacher Klick.
- **E+ und E- (M-35).** Niederdrücken und Loslassen von E sind zwei Ereignisse: Maustaste drücken und Umschalt-Klick (Einrasten) senden `E+` (Phase IV und I, Halt vor Phase II); Maustaste loslassen und Umschalt-Klick (Lösen) senden `E-` (Phase II und III, Halt vor Knoten 19). Ein kurzer Klick ist `E+` beim Drücken und `E-` beim Loslassen; die Taste zeigt dabei mindestens 0,25 s die gedrückte Grafik. M verhält sich entsprechend mit `M+` und `M-`. Unter gehaltenem M erhöht `E+` BZ und AR um 1, `E-` ist ohne Wirkung (§3, E unter M). Der TEST-Interpreter kennt nur den ganzen Anschlag `E`.

### 4.4 Darstellung, Touchscreen, Fokus

- **Überfahren (M-24).** Beim Überfahren ändert sich nichts: keine Hervorhebung, auch gesperrte Tasten sehen unverändert aus, der Mauszeiger bleibt der normale Zeiger, kein Hinweistext. „Hell“ heißt damit eindeutig „gedrückt oder eingerastet“.
- **Touchscreen (M-22).** Nicht unterstützt; keine Touch-Gesten (langes Drücken, Doppeltipp).
- **Fensterfokus verloren (M-27, bestätigt).** Eine gerade mit der Maus gehaltene Taste (E oder M) wird sofort losgelassen (bei E sendet das `E-`); eingerastete Tasten (H oder R, T oder SW sowie mit Umschalt+Klick gehaltene E und M) bleiben unverändert; laufende 0,25-s-Timer laufen zu Ende.
- **Fokus des Pult-Fensters (M-30).** Das Pult erhält den Fokus nach dem Programmstart und im laufenden Programm, wenn keine Eingabe im SW-Fenster anliegt; liegt eine an, hat das SW-Fenster Vorrang. Der Fokus bleibt beim Pult. Wird er händisch woandershin gesetzt, ist am Pult keine Eingabe möglich (weder Maus noch Computertastatur). Erst ein Mausklick auf das Pult bringt ihn zurück; dieser Klick dient **nur dem Fokus** und löst auch dann keine Taste aus, wenn er auf einer Taste liegt (bestätigt). Für die Tastenbedienung ist ein weiterer Klick nötig (M-32 verweist darauf).
- **Angefangene Eingabe im SW-Fenster (M-33).** Entfällt: Eine Eingabe im SW-Fenster ist immer nur ein Zeichen und damit abgeschlossen.

### 4.5 Computertastatur

Die ursprüngliche Regel „nur Maus“ (M-23) ist für die Eingabetasten **aufgehoben**. Die Eingabetasten `B + 1 3 5 7 9 · :` und `D − 0 2 4 6 8 , ZR` sind auch über die gleichnamigen Tasten der Computertastatur bedienbar; alle übrigen Pult-Tasten nur mit der Maus. Die Umschalttaste der Computertastatur wird für E und M gebraucht (4.3).

**Zuordnung (M-28, bestätigt).** Ziffern 0 bis 9 und die Zeichen +, −, „,“ und „:“ entsprechen den gleichen Zeichen der Computertastatur (der Doppelpunkt braucht auf deutscher Tastatur Umschalt, das ist für die Pult-Taste unschädlich, M-26); „·“ entspricht dem Punkt „.“; B und D entsprechen b und d unabhängig von Groß- und Kleinschreibung; ZR entspricht der Leertaste; die Ziffern des Ziffernblocks zählen wie die der Hauptreihe. Die Grafik zeigt „ZR“ (Zwischenraum), nicht „ZP“, und „IS, IB“, nicht „JS, JE“; die Dokumente sind entsprechend berichtigt.

**Verhalten (M-28).** Ein Tastendruck wirkt wie ein Mausklick auf die Pult-Taste: Auslösung beim Drücken, Taste 0,25 s hell. Gehaltene Computertasten wiederholen nicht; erst loslassen und erneut drücken löst wieder aus. Die Sperren gelten gleich (bei gesperrten Tasten passiert nichts, 4.2). Die Taste leuchtet auch, wenn die Maus woanders steht; mehrere Computertasten gleichzeitig sind möglich, jede mit eigenem Timer.

**Wann sie wirkt (M-29, M-31).** Nur wenn das Pult-Fenster den Fokus hat **und** der Rechnerzustand die Benutzung erlaubt (z. B. Eingabetasten nur im Eingabe-Halt). Sobald das Pult den Fokus hat, wirkt die Computertastatur sofort; ein weiterer Klick ist dafür nicht nötig. Lässt der Zustand Eingaben nicht zu, passiert nichts (wie M-25). Tastenkürzel für andere Tasten könnten später als Erweiterung ergänzt werden, ohne diese Regeln zu ändern (M-23 Nr. 3). Die Belegung beim Abspielen einer Klickspur wählt `--TASTATUR` (§2).

*Hinweis zur Herkunft:* Dokument 06 wurde am 18.10.2026 auf den Stand von Entwurf 96 und 99 gebracht, ohne dass die Fassung von Entwurf 96 vorlag; Tastenzeit 0,25 s, einrastende Kanaltasten und die Verriegelung der Eingabetasten bei R sind nach dem Register und Dokument 01 §1.7 nachgezogen. Maßgeblich bleibt das Register (Anhang A).


## 5 SW-Fenster

**Inhalt:** K0-Eingabe, Zeichenpuffer, Anfangslage, Eingabe-Regeln (S3-xx)

**Quellen (alt):** Dok. 09 §3, §7a, §10; Dok. 01 §1.7 (Zeichenabbildung); Dok. 10 §12 bis §15 (Puffer, Rücktaste, Weiterleitung vom Pult)

Das SW-Fenster (Tkinter) ist das zweite Fenster des Modus GRAFIK, im selben Prozess wie das Pult, und öffnet nach ihm. Es zeigt die Schreibwerk-Ausgabe des Rechners **und jedes Zeichen, das der Rechner als Eingabe angenommen hat**, nimmt die Tastatureingabe am SW an und führt die Schreibposition. Im Modus TEST gibt es kein SW-Fenster; dort liefert die K0-Datei die Zeichen. Der Ton der SW-Ausgabe und der angezeigten Eingabe steht in §6. Alte Kennungen (S3-xx, U-xx, G3-/G4-xx) stehen in Klammern; die Zuordnung zu den Abschnitten folgt am Ende von §5.

**Begriffe.** *Eingabe-Halt:* Der Rechner wartet im Befehl `011` auf ein Zeichen; die Warteschlange K0 meldet dann „erwartet SW“. *Token:* was der Rechner über K0 bekommt, ein Zeichen oder `Um. KB` / `Um. GB`. *Lage des SW:* KB oder GB, so wie das SW selbst sie führt (nie die Lage des Rechners); nach dem Einschalten unbestimmt. *Schreibposition:* Es gibt nur eine; sie wird entweder durch eine Eingabe oder durch eine Ausgabe mit einem Zeichen belegt und rückt dann weiter. Ein „Echo“ im Sinne eines Rückschreibens durch das Programm gibt es beim C 8205 nicht (Festlegung 18.10.2026); das Fenster zeigt jedes angenommene Zeichen selbst an.

### 5.1 Fenster und Anzeige

- **Größe und Darstellung** (S3-02): 130 Spalten × 36 Zeilen, Schrift mit fester Breite, kein Zeilenumbruch. Der Text ist markierbar; Markieren und Strg+C legen ihn in die Zwischenablage (S3-03).
- **Schreibposition** (S3-05): 0 bis 130; Tabulatorstopp alle 12 Zeichen. Die Position zählt die schon beschriebenen Plätze (0 = vor dem ersten Platz). Hinter Position 130 gibt es keine Bewegung: Jedes weitere Zeichen ersetzt das Zeichen auf dem 130. Platz (Überdruck), kein Zeilenumbruch. Ein Tabulator ab Position 120 geht auf 130, ab 130 bleibt er stehen.
- **Zeilenschaltung und Wagenrücklauf** (S3-06): WRZL beginnt eine neue Zeile. `WR` setzt die Position auf 0, ohne Anzeige und ohne Zeilenvorschub; folgende Zeichen überdrucken. TAB füllt nur fehlende Spalten. *(WRZL: Entscheidung; WR und TAB: Standardannahme, ohne Einzelbestätigung.)*
- **Nicht darstellbare Zeichen** (S3-07): ZV, BM, Irrung Zeichen, Irrung Satz, Transport, ≈, ≋ und △ werden nur ausgeführt, ohne Anzeige und ohne Bewegung der Schreibposition (Entscheidung 18.10.2026; „keine Bewegung“ ist die Auslegung des Entwicklers, ohne Einzelbestätigung).
- **Ausgabe des Rechners:** Jedes Zeichen, das ein Ausgabebefehl sendet, wird angezeigt. Ausgabe und angenommene Eingabe laufen durch **eine** Warteschlange in die Anzeige; die Reihenfolge beider Quellen bleibt erhalten (S3-04, U-1).
- **Schließen** (S3-16): X am SW-Fenster wirkt wie Strg+C (Rückgabecode 8); Netz-Aus beendet mit 0.
- **Lage auf dem Bildschirm:** Das Fenster öffnet an der zuletzt gemerkten Stelle (FL-001, `grafik_fensterlage.py`, 19.10.2026); ohne gemerkte Stelle rechts unten wie das frühere Fenster „SW Ausgabe“ (S3-15, Standardannahme). Einzelheiten zum Merken stehen in §3.1 und werden beim Füllen von §10 geprüft.

### 5.2 Wann eine Eingabe angenommen wird

Eine Taste im SW-Fenster wirkt nur, wenn **K0 angewählt, der Selektor SW am Pult gedrückt** (Stellung SW statt T) **ist** (S3-08). Dazu braucht das Programm nur `011`; ein `030` ist für die Anzeige nicht nötig (Wortlaut des Projektinhabers 18.10.2026: „Wenn im SW ein Zeichen eingegeben wird, DANN MUSS ES DARGESTELLT WERDEN, nur mit dem 011-Befehl“).

| Zustand | Wirkung der Taste |
|---|---|
| K0 und SW angewählt, Rechner bei `011` | Das Zeichen geht an den Rechner und wird sofort angezeigt. |
| K0 und SW angewählt, Rechner noch nicht (wieder) bei `011` | Das Zeichen wartet im Puffer (§5.5) und wird erst angezeigt, wenn der Rechner es geholt hat. |
| Kanal K1 bis K3 angewählt, Schalter SW gelöst (Stellung T) | **Gesperrt:** keine Eingabe, keine Anzeige, kein Ton, keine Meldung, nichts vorgemerkt. |
| Zeichen ohne Gegenstück im R300-Code | Still verworfen (§5.3), ohne Wirkung auf die Lage. |

Es gibt keine Regel „Programmende“ (S3-18); maßgeblich ist allein, ob K0/SW angewählt ist und ein Eingabebefehl die Zeichen abholt. Ein angezeigtes Zeichen, das den Rechner nicht erreicht, kann nicht vorkommen: Anzeige und Eingabe gehören zusammen (Antwort 18.10.2026 07:44). Weil gesperrte Tasten still bleiben, sieht ein Anwender, dessen Selektor SW nicht gerastet ist (stattdessen T), keine Reaktion; das ist kein Fehler (Debug-Log-Befund 19.10.2026, Dok. 10 §15). Ein Hinweis erscheint nicht (bestätigt 19.10.2026, §10.5).

### 5.3 Zeichenabbildung

Ein- und ausgegeben werden können nur Zeichen des R300-Codes (`C8205-Interpreter-Kodetabellen.md`, Tabelle 1; Entscheidung 16.10.2026, F-16).

1. **Abbildung** (S3-09): Ein getipptes Zeichen wird über seinen ASCII-Wert in den Spalten „Ascii KB“ und „Ascii GB“ der Tabelle 1 gefunden. Angenommen werden genau 85 Zeichen: `a`–`z`, `A`–`Z`, `0`–`9`, `% : + / , . - ; ( ) ? ! < > " ' [ ] ~ # * =` und der Gravis. Nicht angenommen werden Umlaute, `ß`, `§`, `€`, `° ´ ² ³ µ`, die AltGr-Zeichen `@ { } \ |` und alles ohne Gegenstück.
2. **Sondertasten** (S3-10): Eingabetaste → WRZL, Leertaste → ZR, Tab → Tabulator. Strg-/Alt-Kombinationen, Entf, Pfeile, Funktionstasten, Esc, Pos1 und Umschalt allein ohne Wirkung. Ausnahme Rücktaste: siehe §5.6.
3. **Nicht eingebbar** über die Computertastatur sind die Zeichen ohne Tastenentsprechung (ZV, BM, Irrung Zeichen, Irrung Satz, Transport, ≈, ≋, △).
4. **Nicht angenommenes Zeichen:** stiller Verwurf wie bei einer gesperrten Taste: keine Anzeige, kein Ton, keine Meldung, nichts an den Rechner; Lage und Puffer bleiben unverändert.
5. **Gravis:** Er kommt am echten Fenster als `grave` an und wird geliefert (Handlauf F-56). Mit der Wiedergabe des Tests (`event_generate`) ist er nicht erzeugbar; die Auswertung führt das als bekannte Eigenschaft (`[BEKANNT]`), nicht als Befund (→ Prüfverfahren §7).

### 5.4 Lage KB/GB und Umschaltzeichen

- **Die Umschalttasten der Computertastatur** (Umschalt, Feststelltaste, AltGr) werden nicht gesondert ausgewertet. Sie bestimmen nur, welches Zeichen getippt wird (`A` statt `a`); das Fenster erkennt am Zeichen, welche Lage es braucht. Das C-8205-Zeichen `Um. KB` oder `Um. GB` tippt der Benutzer nie selbst; **das Fenster erzeugt es** (S3-11; bestätigt 18.10.2026, Checkpoint 45).
- **Die Lage des Rechners spielt für die Eingabe am SW keine Rolle** (Festlegung des Projektinhabers 18.10.2026). Das Fenster führt nur die Lage des SW selbst.
- **Nach dem Einschalten (jedem Programmstart) ist die Lage des SW unbestimmt** (S3-12; Entscheidung 18.10.2026): Der Benutzer tippt frei, mit oder ohne Umschalttaste; weitere Festlegungen gibt es nicht, den Rest erledigt das Fenster. Für das **erste** Zeichen mit bestimmter Lage geht deshalb **immer** das Umschaltzeichen zum Rechner: `A` als erstes Zeichen → `Um. GB`, `A`, das SW steht danach auf GB; `a` → `Um. KB`, `a`, danach KB. Es gibt keinen zufälligen und keinen festen Anfangszustand (beides verworfen).
- **Bei den folgenden Zeichen** entscheidet das vorhergehende: gleiche Lage → nur das Zeichen; andere Lage → Umschaltzeichen und Zeichen, der Rechner bekommt **zwei Eingaben** und muss dafür zwei `011` durchlaufen. Zeichen mit gleichem Code in beiden Lagen (ZR, TAB, WRZL u. a.) gehen allein und ändern die Lage nicht.
- **Abstand der zwei Eingaben** (S3-11, U-11, Z-2; Entscheidung 18.10.2026): kein fester Wert. Maßgebend ist das echte Drücken der Tasten. Ist eine Umschalttaste beteiligt (Umschalt, AltGr), ist der Abstand die Zeit zwischen deren Drücken und dem Drücken der Zeichentaste; sonst geht das Umschaltzeichen beim Drücken der Zeichentaste und das Zeichen beim Loslassen (Abstand = Haltezeit). Das Fenster fügt keine Zeit hinzu. Die „etwa 0,1 s“ vom 18.10.2026 waren ein Beispiel, keine Vorgabe. Zeichen „dazwischen“ gibt es nicht; kommt die nächste Taste, ist eine ausstehende zweite Eingabe frei, nichts wird verworfen (S3-14).
- `Um. KB` und `Um. GB` werden nie angezeigt und bleiben stumm.
- **Eingabeprogramme:** Jedes Programm bekommt als erstes Eingabezeichen ein Umschaltzeichen. Die älteren Testprogramme `ziffern_1`, `ziffern_2` und `sw_zwei_ziffern` kennen keines und bleiben unverändert; ihre Tests setzen die Lage des SW vorab (U-12, entschieden 18.10.2026: „alte Tests, mach wie du denkst“). `r300_eingabe` kennt die Umschaltzeichen.

### 5.5 Puffer (seit 19.10.2026)

Auf Wunsch des Projektinhabers (19.10.2026) gibt es einen kleinen Puffer (G4-007; Anlass: viele Zeichen gingen verloren, Großbuchstaben „immer“, weil Umschaltzeichen und Zeichen fast gleichzeitig kommen). Er **ersetzt** die Fassung vom 18.10.2026 („keine wartenden Zeichen“, S3-13, S3-14, S3-18) und die Vormerkung der Fassung vom 16.10.2026.

| Punkt | Regel |
|---|---|
| Wann gepuffert | K0 mit SW ist angewählt, aber kein `011` aktiv oder der aktive hat sein Zeichen schon. |
| Größe | Höchstens 8 Eingaben (`PUFFER_MAX`); ein Umschaltzeichen zählt mit, ein Zeichen in der anderen Lage braucht 2 und kommt als Paar ganz oder gar nicht hinein. Ist der Puffer voll, geht die Taste verloren. |
| Weitergabe | Der Takt des Fensters (10 ms) gibt je aktivem `011` **eine** Eingabe weiter, in der Reihenfolge des Tippens; Paare frühestens nach dem echten Tastenabstand (§5.4). |
| Anzeige und Ton | Erst wenn der Rechner die Eingabe geholt hat, nicht beim Tippen. Die Anzeige zeigt nur, was den Rechner erreicht hat (S3-04). |
| Kanalwechsel | Anwahl von K1 bis K3 oder Wegfall des Flags SW **verwirft** den Puffer; gezählt wird jeder echte Wechsel, auch ein kurzes K2 und zurück. **Ausnahme:** die zweite Hälfte eines Paares, dessen Umschaltzeichen schon beim Rechner ist, bleibt erhalten, damit das Umschaltzeichen nicht allein steht (z. B. Programme, die nach dem Umschaltzeichen eine Meldung über K2 ausgeben). Ohne K0/SW ist die Taste weiter gesperrt und nichts wird gepuffert. |
| Verfall | Kein zeitlicher Verfall; Zeichen bleiben im Puffer, bis der Rechner wieder bei `011` ist oder der Kanal wechselt. |
| Rücktaste | Nimmt zuerst das zuletzt gepufferte Zeichen zurück (samt seinem Umschaltzeichen, wenn es noch im Puffer steht), siehe §5.6. |

**Stand der Entscheidung.** Gewünscht hat der Projektinhaber: einen kleinen Puffer, der bei Kanalwechsel verworfen wird. Größe 8, die Ausnahme für Paare und das Fehlen eines zeitlichen Verfalls sind Annahmen des Entwicklers, vom Projektinhaber am 19.10.2026 bestätigt (§10.5). Auf die Frage nach einer Taste „dazwischen“ antwortete der Projektinhaber am 19.10.2026: „weiß ich nicht, die Eingabe muss funktionieren!“ Daraufhin steht `SwEingabe.EIN_TASTENDRUCK = False` (G4-009): Es gilt dieser Puffer. Die Alternative `True` (G4-008: der Puffer hält höchstens einen Tastendruck, ein Zeichen oder Umschalter und Zeichen) bleibt wählbar, verliert aber bei schnellem Tippen systembedingt Zeichen. Eine dritte, nicht gebaute Möglichkeit wäre: ein Platz Vormerkung, die Taste danach nicht verwerfen, sondern erst bei Abholung annehmen. Ob 8 reicht, soll der nächste Lauf mit `--DEBUGLOG` zeigen (Zeilen `SW Taste … voll`).

**Wegfall der Vormerkung am 18.10.2026 und ihr Ersatz.** Bis 18.10.2026 wartete ein Zeichen nach dem Umschaltzeichen als „Vormerkung“ bis zum nächsten Eingabe-Halt und verfiel mit der Eingabebedingung oder dem Programmende (O-11). Das entfiel am 18.10.2026 (Antworten 07:44 und 07:56: Sperre statt Warten; `verwerfen()`, B-6 und die Regel „Programmende“ sind entfernt). Der Puffer vom 19.10.2026 ist keine Rückkehr zu dieser Vormerkung: Er verfällt nicht mit dem Programmende, sondern nur mit dem Kanalwechsel, und die Anzeige folgt erst der Abholung.

### 5.6 Rücktaste (seit 19.10.2026)

Die Rücktaste hat **Löschwirkung** (G4-006; Antwort des Projektinhabers 19.10.2026: Löschwirkung ja, Anzeige eines Namens nein; der frühere Stand „ohne Wirkung“ war ein Lesefehler des Entwicklers):

- Gibt es ein gepuffertes Zeichen (§5.5), nimmt sie **zuerst dieses** zurück (das zuletzt gepufferte, samt Umschaltzeichen); es hat den Rechner nie erreicht und war nie angezeigt.
- Sonst löscht sie das zuletzt angezeigte Zeichen links der Schreibposition, auch ein Zeichen der Rechnerausgabe, und die Position geht um eins zurück. Am Zeilenanfang ohne Wirkung, keine Zeilenverschmelzung.
- Keine Anzeige eines Namens (kein `<Rücktaste>`), **nichts an den Rechner** (der R300-Code hat kein Rücktasten-Zeichen; „Irrung Zeichen“ ist ein Lochstreifen-Zeichen und nicht eingebbar), kein Ton.
- Sie wirkt unabhängig davon, ob ein `011` aktiv ist. Strg+Rücktaste und Alt+Rücktaste ohne Wirkung.

### 5.7 Fokus, Titel und Weiterleitung vom Pult

- **Fokus** (S3-15; Entscheidung 16.10.2026, F-16 Teilantwort): Bei einem Eingabe-Halt (und bei gepufferten Zeichen) fordert das SW-Fenster den Fokus an; der Titel nennt dann „Eingabe erwartet“. Sonst hat das Pult den Fokus. Wird der Fokus vom Betriebssystem verweigert, erzwingt das Fenster ihn nicht; ein Mausklick in das Fenster holt ihn (der Klick dient nur dem Fokus). Nach der Eingabe geht der Fokus zum Pult zurück.
- **Weiterleitung vom Pult** (G4-008, 19.10.2026): Nach jedem Zeichen ging der Fokus zurück zum Pult und wurde erst bei der nächsten Aufforderung (rund 0,3 s später) wieder angefordert; Tasten in dieser Lücke erreichten das Pult und gingen verloren (Debug-Log: `TASTE Computertastatur … wirkt=False`). Seitdem reicht das Pult Tasten der Computertastatur an das SW-Fenster weiter, solange K0/SW angewählt ist (Umschalttasten immer, damit der echte Tastenabstand stimmt); sie laufen durch dieselbe Eingabelogik. Ohne K0/SW wertet das Pult die Taste selbst aus (Pult-Tastatur, Stellung T). Ob das die verschluckten Zeichen beseitigt, ist am echten Fenster noch nicht bestätigt (→ §10).
- **Entprellung:** Das SW-Fenster gibt den Fokus erst nach **0,4 s ohne Eingabeaufforderung** an das Pult zurück (`_fokus`, `_inaktiv_seit`; Dok. 10 §14, Schwelle im Code gegengelesen). Liegt der Abstand der Eingabebefehle um diese Schwelle (gemessen 350 bis 450 ms), bleibt der Fokus mal im SW-Fenster und wechselt mal zum Pult; Tasten gehen dabei seit G4-008 nicht mehr verloren (Weiterleitung). Die Schwelle ist nicht geändert.
- **Warnung:** Bei geöffnetem HW-Check-Fenster (§8) kann das SW-Fenster den Fokus nicht halten; das hängt vom Fenstermanager ab und ist als bekannte Eigenschaft akzeptiert (B-5, A-4).

### 5.8 Debug-Log und Spur

- **Debug-Log** (`--DEBUGLOG`, S3-17): je Taste eine Zeile `SW Taste char=… keysym=… -> geliefert | folgt | vorgemerkt | voll | blockiert | verworfen (Puffer: n)`; bei Kanalwechsel `Puffer -> verworfen`; ferner die Annahme beim Rechner („Rechner uebernimmt Token“, `grafik_k0.py`), die Anzeige (`SWAUS`) und je Eingabeklang eine Zeile mit Schreibwerk und Mischer. Die Klickspur kennt die Ereignisart `tipp`. Keine Wirkung auf das Rechnerverhalten.
- **Spur:** Das Programm `r300_eingabe` schreibt je empfangenem Token dessen Ausgabewort ab Zelle 3000 in den Speicher; damit ist prüfbar, was der Rechner wirklich bekam. Die Auswertung `r300_eingabe_log_auswerten.py` vergleicht Anzeige, angenommene Zeichen und Tokens (Verfahren: Prüfverfahren §6).

### 5.9 Überholte Fassungen (zum Lesen der Altdokumente)

| Altdokument sagt | Gilt seit | Ersatz |
|---|---|---|
| Kein Echo, Tastatureingaben nirgends zu sehen (Dok. 00, 01 §1.6, 03 §5, Entwurf 88) | 18.10.2026 | Jedes angenommene Zeichen wird angezeigt (S3-04 neu, U-1 bis U-8) |
| Das erste Zeichen setzt die Lage, ohne dass ein Umschaltzeichen geht (Dok. 01 §1.7 Nr. 2, Dok. 09 vor Checkpoint 45) | 18.10.2026 (Checkpoint 45) | Das erste Zeichen mit bestimmter Lage bekommt immer das Umschaltzeichen (S3-12) |
| Umschaltzeichen aus der Lage des Rechners | 18.10.2026 | Nur die Lage des SW zählt (S3-11) |
| Vormerkung bis zum nächsten Eingabe-Halt, Verfall mit Programmende (Dok. 01 §1.7 Nr. 2, 4, 5; O-11) | 18.10.2026 | Sperre statt Warten (S3-13, S3-18), seit 19.10.2026 der Puffer (§5.5) |
| Fester Abstand 0,1 s der zwei Eingaben (`ABSTAND_ZWEITE`) | 18.10.2026 (Checkpoint 38/39) | Abstand der echten Tasten (U-11) |
| Rücktaste ohne Wirkung (S3-10, Entwurf vor Checkpoint 58) | 19.10.2026 | Löschwirkung (§5.6) |
| Taste im Puffer: höchstens ein Tastendruck (G4-008, `EIN_TASTENDRUCK = True`) | 19.10.2026 (G4-009) | Puffer bis 8 Eingaben (`False`) |

### 5.10 Kennungen, Stand der Festlegungen

| Alte Kennung | Gegenstand | Abschnitt |
|---|---|---|
| S3-01, S3-02, S3-03 | Fenster, Größe, Markieren und Kopieren | 5.1 |
| S3-04, S3-08 | Anzeige jedes angenommenen Zeichens, Bedingungen | 5.1, 5.2 |
| S3-05, S3-06, S3-07 | Schreibposition, Tabulator, WR/WRZL, nicht darstellbare Zeichen | 5.1 |
| S3-09, S3-10 | Zeichenabbildung, Sondertasten | 5.3 |
| S3-11, S3-12, U-11, U-12, Z-1, Z-2 | Lage, Umschaltzeichen, Abstand | 5.4 |
| S3-13, S3-14, S3-18, G4-007, G4-009 | Sperre und Puffer | 5.2, 5.5 |
| G4-006 | Rücktaste | 5.6 |
| S3-15, G4-008, FL-001, B-5 | Fokus, Weiterleitung, Fensterlage | 5.1, 5.7 |
| S3-16 | Schließen | 5.1 |
| S3-17, RE-001, RLA-001 | Debug-Log, Spur, Auswertung | 5.8 |
| U-1 bis U-10, B-1 bis B-9 | Umsetzung und Befunde der Stufe 3 | 5.9, Prüfverfahren §10 |

**Stand.** Entscheidungen des Projektinhabers: S3-01 bis S3-05, S3-08 (die Sperre), S3-09 bis S3-14, S3-16, S3-18, Z-1, Z-2, U-9 (Ton für die angezeigte Eingabe: ja, §6) und die Rücktaste. **Standardannahmen ohne Einzelbestätigung (bei der Abnahme der Stufe 3 am 18.10.2026 nicht beanstandet):** S3-06 (WR und TAB), S3-07 (keine Bewegung bei nicht darstellbaren Zeichen), S3-15 (Lage rechts unten). **Annahmen des Entwicklers seit 19.10.2026, nicht bestätigt:** Puffergröße 8, Ausnahme für Paare, kein Verfall, `EIN_TASTENDRUCK = False`. Dieser Abschnitt ist aus den Dokumenten übernommen; nur die Konstanten (Breite 130, Tabulator 12, `PUFFER_MAX` 8, `EIN_TASTENDRUCK = False`, Takt 10 ms, Fenster 130 × 36, Titel „Eingabe erwartet“, Taste `BackSpace`) habe ich im Code gegengelesen, nicht das Verhalten. Die Puffer-Änderungen vom 19.10.2026 sind am echten Fenster nicht erprobt.

## 6 Töne

**Inhalt:** Schreibwerk, Lochstreifenleser, Rechner-Grundgeräusch, Netzablauf, Stanzer, Haltzeit, Mischer

**Quellen (alt):** Dok. 03, 10 §4; `ton/SW_Ton_Beschreibung.md` bleibt als Teil B bis D

Töne gibt es nur im Modus GRAFIK. Im Modus TEST gibt es keine Töne und keine Hochlaufwartezeit. Dieser Abschnitt beschreibt den **geltenden Stand** der Töne (Stufe 4, am 19.10.2026 vom Projektinhaber abgenommen; offen bleibt Windows). Er ersetzt Dok. 03 (Stand 16.10.2026, in großen Teilen überholt) als Beschreibung. Die Herkunft der Klangdateien, die Messwerte und der Testrahmen `ton/sw_ton.py` stehen weiter in `ton/SW_Ton_Beschreibung.md` (Teil B bis D, nachgeführt am 19.10.2026). Alte Kennungen (S4-xx, O4-xx, Nr. aus Dok. 03 §5, G4-xx) stehen in Klammern.

### 6.1 Aufbau: ein Tonstrom, ein Mischer

- **Tonstrom** (S4-01): In GRAFIK ohne `--STUMM` wird beim Start **ein Ausgabestrom geöffnet, der bis zum Ende dauernd läuft** (bei Ruhe Stille). Es wird kein Abspielprozess je Klang gestartet. *Dauergeräusche* (Rechner-Grundgeräusch, Leser-Dauergeräusch, Stanzer) laufen als Schleife und werden nur über den Pegel (0 oder voll) stumm oder hörbar. *Einzelklänge* (Zeichen, TAB, WRZL, Leser-Einzelschritt, Auslaufen) werden beim Ereignis in den laufenden Strom eingemischt; gleichzeitige Klänge überlappen und werden summiert (auf 16 Bit begrenzt).
- **Mischer** (S4-01, S4-02): das C-Modul `tonmisch` (`c-module/tonmisch.c`), als statische Bibliothek `libtonmisch.a` **fest in das Erweiterungsmodul `c8205_trommel` eingebunden** (eine Datei zusammen mit der Trommel, §7). Blöcke zu 10 ms (441 Werte, 44,1 kHz, mono, 16 Bit), **eigener C-Thread ohne GIL**, höchstens 2 Blöcke Vorlauf (20 ms), bis 128 gleichzeitige Stimmen. Der Python-Mischer `grafik_tonmisch.py` bleibt als Rückfall (ohne gebautes Erweiterungsmodul meldet `c8205_grafik` das beim Start) und als Bezug der Prüfungen.
- **Senke** (S4-02): Linux: ein Abspielprogramm mit Roh-Audio über eine Röhre, vom Modul gestartet; der Mischer nimmt in dieser Reihenfolge das erste vorhandene von `paplay`, `pw-cat`, `aplay`. Windows: `winmm` (`waveOut…`) mit vier Puffern zu 10 ms, im Code, **nicht übersetzt und nicht getestet** (§6.8).
- **Tonkanäle** (S4-12): Rechner, Schreibwerk, Leser, Stanzer; je Kanal ein internes Tor. Die Tore dienen **Netz aus** und dem Auslaufen der Dauergeräusche. **Der Selektor SW schließt kein Tor** (§6.2). Es gibt kein neues Bedienelement.
- **Verzögerung** (S4-03): Ton und Zeichen im SW-Fenster erscheinen im Mittel gleichzeitig; der Ton setzt höchstens 50 ms nach dem Zeichen ein; das Zeichen wird nie wegen des Tons verzögert. In der ersten Hörprüfung war der Tastenklang „bemerkbar“ verzögert (geschätzt 0,1 s); daraufhin wurden Vorlauf (30 → 20 ms) und Puffer des Abspielprogramms (40 → 20 ms; `pw-cat` 100 → 20 ms) gesenkt (G4-004). Gemessen ist das am Gerät nicht; die zweite Hörprüfung war „ok“. Zu kleine Werte können knacken (`SPIELER_LATENZ_MS` in `grafik_tonmisch.py`, ohne Neubau änderbar).
- **Aufrufstellen** (S4-14): Der Interpreter für TEST bleibt unverändert; die Töne hängen im GRAFIK-Pfad an vorhandenen Stellen: Schreibwerk-Ausgabe (`SwSenke`), Leser (`GrafikLeser.bei_zeichen`), Stanzer (`GrafikStanzer.bei_zeichen`, Selektor LS über `PultSteuerung.bei_ls`), Netzablauf (`MischerRechnerTon`).

### 6.2 Schreibwerk

| Gegenstand | Festlegung |
|---|---|
| Klangarten (S4-05) | Zeichen, TAB, WRZL. Zeichen: zufällig eine der 24 Dateien `zeichen_*.wav`, **nie zweimal hintereinander derselbe**; der Anschlag (etwa 60 ms) wird nicht abgeschnitten. WRZL: `wrzl.wav`, 360 ms. TAB: **nur ein Klang**, `tab_400.wav`, 400 ms, gleich für jeden Tabulatorweg (kurz und lang entfallen). |
| Zeichenklang (S4-05; O4-1, O4-8) | **100 ms.** Die 24 Dateien dauern 120 ms und bleiben unverändert; bei der Wiedergabe werden sie auf 100 ms gekürzt, die letzten 10 ms werden ausgeblendet (`ZEICHEN_AUSBLENDUNG_MS`). |
| Schreibwerkzeit (S4-17; O4-1) | Jedes **ausgegebene** Zeichen belegt das Schreibwerk **80 ms, je Zeichen zufällig 70 bis 90 ms** (gleichverteilt); der Ausgabebefehl kehrt erst danach zurück (Tastenverzögerung), der Rechner wartet so lange. Die Schreibwerkzeit ist **nicht** die Tonlänge. TAB (400 ms) und WRZL (360 ms) bleiben Schreibwerkzeit. Das Zeichen erscheint im SW-Fenster zu Beginn der Schreibwerkzeit. |
| Überstand (O4-7) | Der Zeichenklang (100 ms) ist länger als die Schreibwerkzeit (70 bis 90 ms): Der Klang des folgenden Zeichens beginnt zur Schreibwerkzeit, der Rest des vorigen **überlappt** und klingt darunter zu Ende. |
| Rechter Anschlag (S4-06) | Ein Zeichen hinter Position 130 wird angeschlagen (Ton und Zeit wie jedes Zeichen) und im Fenster auf Position 130 überdruckt (§5.1). |
| Selektor SW (S4-07; O4-3, O4-10) | Bei eingerastetem Selektor SW (`SW_umschalt`) gibt es für die **Ausgabe des Rechners** keine Ausgabe, keine Schreibwerkzeit und keinen Klang; der Rechner arbeitet die Ausgabebefehle weiter ab; nach dem Lösen gibt es wieder Ausgabe mit Klang und Schreibwerkzeit; unterdrückter Text wird nicht nachgeholt. **Der Selektor SW wirkt nur auf die Ausgabe**; Leser, Stanzer und Rechnergeräusch und die angezeigte Eingabe bleiben unberührt. Nicht zu verwechseln mit der Wippe T-SW (Eingabequelle, §3.3, §5.2). |
| Angezeigte Eingabe (S4-08; U-9, O4-2, O4-5, O4-6) | Jedes im SW-Fenster angezeigte Eingabezeichen klingt **wie jede Ausgabe** auf das Schreibwerk (Klangwahl gemeinsam, ein Schreibwerk). Es hat **keine Schreibwerkzeit** und **keine Sperre**: der Klang läuft nur nebenher. **Umschaltzeichen haben keinen Ton**, nur die Zeichen. Der Klang beginnt mit dem Zeichen, also nach dem echten Tastenabstand und, bei gepuffertem Zeichen (§5.5), erst bei Annahme durch den Rechner, weil der Ton an der Anzeige hängt. Folgen Ein- und Ausgabe abwechselnd, laufen die Klänge ineinander. Die Eingabe klingt auch bei eingerastetem Selektor SW. |
| `--STUMM` (S4-13; O4-9) | Kein Ton, aber die Schreibwerkzeit gilt auch mit `--STUMM` (im Modus TEST nicht). |

### 6.3 Lochstreifenleser

Der Leserton hängt an `GrafikLeser.bei_zeichen` und wird bei **jedem Zeichen** aufgerufen, das der Leser K1 oder K2 tatsächlich an den Rechner liefert (S4-09; genau ein Zeichen je Zugriff, vom Projektinhaber bestätigt 16.10.2026). Kein Aufruf bei Zeichen von Tastatur oder K0. Es gibt **einen** Leserton für K1 und K2 (O4-12).

- **Lesetempo 130 Zeichen/s**, auch mit `--STUMM`, nicht im Modus TEST (O4-11); Rechenzeit wird angerechnet, die Tonlänge verzögert nichts.
- Das erste Zeichen nach mehr als 100 ms Pause ist ein **Einzelschritt** (`ls_einzel.wav`, etwa 150 ms). Folgt das nächste Zeichen höchstens 100 ms später, läuft das **Dauergeräusch** (Schleife `ls_dauer.wav`, der Einzelschritt wird abgebrochen). Bleiben die Zeichen länger als 100 ms aus, endet es mit dem **Auslaufen** (`ls_ende.wav`, 60 ms). Die Schwelle 100 ms ist eine Konstante, die nach der Hörprüfung nachzustellen ist (S4-16).
- Das Löschzeichen 11111111, das der Interpreter übergeht, zählt als gelieferte Zeichen: es klingt und kostet Lesezeit (O4-13).

### 6.4 Lochbandstanzer

Der Stanzerton hängt an `GrafikStanzer.bei_zeichen` (nach dem Schreiben des Zeichens) und wirkt **nicht** auf die Stanzerdatei. Der Ton hängt vom **Zustand**, nicht vom einzelnen Zeichen: ein Ton je Zeichen würde sich überlagern, weil die Einzeltöne viel länger als die Stanzzeit (20 ms) sind (Dok. 03 §5 Nr. 15).

- **Zustände:** *Aus* (kein Ton) – *Geräusch* (`ls_motor.wav`, Schleife) – *Dauerstanzen* (`ls_dauerstanzen.wav`, Schleife). Es gibt **einen** Geräuschzustand, nie zwei Geräusche gleichzeitig; einen Einzelschritt-Ton gibt es nicht (S4-10; Dok. 03 §5 Nr. 21).
- **Dauerstanzen** beginnt mit dem zweiten Zeichen, das weniger als 50 ms nach seinem Vorgänger ausgegeben wird, und läuft, solange das erhalten bleibt. 50 ms nach dem letzten Zeichen beendet ein Zeitgeber es (zurück zu *Geräusch*). **Kommt nach 5 s kein Zeichen, wird das Geräusch abgeschaltet**; das nächste Zeichen startet es wieder.
- **Selektor LS gedrückt:** Es läuft immer nur `ls_motor.wav`, dauernd und ohne Abschalten; `ls_dauerstanzen.wav` wird dann nie gespielt (Dok. 03 §5 Nr. 23). Das gilt auch ohne `--stanzer1` (O4-15). Beim Lösen von LS beginnt die 5-s-Frist neu (O4-16).
- **Stanztempo** (S4-18): etwa 50 Zeichen/s, ein Zeichen frühestens 20 ms nach dem vorigen (Rechenzeit angerechnet; wer langsamer liefert, wird nicht gebremst); auch mit `--STUMM`, nicht im Modus TEST. Es gilt für den Ausgabebefehl des Rechners, nicht für die Tonlänge. Bei schnellem Lauf entsteht damit Dauerstanzen (20 ms < 50 ms). Eine Streuung wie beim Schreibwerk ist nicht eingebaut.
- **3 s und 5 s:** Der **Motor** des Stanzers schaltet nach der Projektdokumentation weiter **nach 3 s** ohne Zeichen ab; die **5 s** gelten nur für das **Geräusch**, weil 3 s schlecht hörbar sind. Diese Aufteilung ist eine Festlegung des Entwicklers auf die Delegation des Projektinhabers (16.10.2026, „mach wie du denkst“), nicht sein Wortlaut.

### 6.5 Rechner: Grundgeräusch und Netzablauf

Der Ablauf von Netz-Ein bis Netz-Aus steht in §3.4. Die Töne dazu (S4-11; Dok. 03 §1 Nr. 4, 5; §5 Nr. 19, 20):

- **Einschalten:** `fade_in` in voller Länge (11,3 s, Länge der Aufnahme), danach B grün und **Grundgeräusch** als Schleife (Aufnahme 6,0 s, Pegel 0,8, Entscheidung 17.10.2026; kein Neustart wie in Stufe 2). Der Pegel am Ende von `fade_in` (etwa 0,073 RMS) liegt über dem am Schleifenanfang (etwa 0,044); eine Überblendung ist nicht festgelegt und bleibt Gegenstand der Hörprüfung.
- **Ausschalten mit dem Klick:** `fade_out` (2 s) beendet `fade_in` und das Grundgeräusch und schließt die Tore von Schreibwerk, Leser und Stanzer (O4-17); danach Ende mit Code 0.
- **Strg+C, X am Pult oder SW-Fenster, Schließen** (Code 8): alle Töne hören sofort auf (Tore zu, Strom zu), **kein `fade_out`**.
- **Wiedereinschalten** heißt, das Skript neu zu starten; es beginnt wieder mit „Rechner aus“ und wartet auf den Klick auf den Netzschalter. Die Register sind danach weg, die Trommeldatei bleibt erhalten.
- **Haltzeit:** Die Haltzeit-Zeile des Hardware-Checks (HZ-003, nur reine Rechnerzeit) gehört zu §8, nicht zu den Tönen.

### 6.6 Lautstärke und Stummschaltung

- **`--STUMM`** (S4-13): keine Töne, **keine Hochlaufwartezeit** (B grün sofort nach dem Klick), keine Prüfung des Audiogeräts; Schreibwerkzeit, Lesetempo und Stanztempo bleiben.
- **`--TON=pppp`** (S4-19; Entscheidung 19.10.2026 nach der ersten Hörprüfung): vier Ziffern 0 bis 9 in der Reihenfolge **Pult, SW, LL, LS** (Pult = Rechnertöne; SW = Schreibwerk einschließlich der angezeigten Eingabe; LL = Lochstreifenleser; LS = Lochbandstanzer). Voreinstellung 5555; 0 = stumm. Faktor = Basis × Ziffer / 5. **Basis laut Code (`TON_BASIS` in `grafik_tonmisch.py`): Pult 1,0, SW 2,0, LL 1,3, LS 1,0.** SW 2,0, weil der Tastenanschlag doppelt so laut werden sollte (Hörprüfung 1); LL 1,3 seit G4-012 („Leser einen Tick lauter“, Hörprüfung 19.10.2026). Ungültige Angaben (nicht vier Ziffern) beenden den Start mit der argparse-Meldung (Code 2). Mit `--STUMM` wirkungslos; unter Windows wirkt der Wert Pult nicht. Die Zeichenklänge erreichen 0,4 des Vollausschlags; ab Faktor 2,5 (SW: Ziffer 6) übersteuert ein einzelner Klick.

### 6.7 Start und Fehlerfälle

Fehlt in GRAFIK ohne `--STUMM` ein Abspielprogramm oder ein nutzbares Audiogerät, bricht das Skript **vor dem Aufblenden der Fenster** mit der Meldung „Kein Abspielprogramm gefunden“ und **Rückkehrcode 16** ab (S4-04; Entscheidung 16.10.2026, bestätigt als O4-4 am 18.10.2026); es läuft **nicht** ohne Ton weiter. Dasselbe gilt, wenn der Strom **im Betrieb** ausfällt (Abspielprozess endet oder Schreiben schlägt fehl). Der Startfall ist mit leerem PATH und einem Ersatz für tkinter geprüft (G4-019); der Ausfall im Betrieb am echten Gerät ist nicht eigens geprüft.

### 6.8 Plattformen

Linux ist umgesetzt und vom Projektinhaber abgehört (Hörprüfung 2, 19.10.2026: ok). Windows ist weder übersetzt noch getestet: Der Bau von `tonmisch` mit MinGW-w64 und der Mischer mit `winmm` sind offen, bis ein Windows-Tester da ist (B-2; → §9, §10, Prüfverfahren §9). Bis dahin bleibt unter Windows der Stand von Stufe 2: Rechnertöne über `winsound` (nur ein Klang gleichzeitig), Schreibwerkzeit und Lesetempo ja, sonst kein Ton, mit Hinweis beim Start (O4-18). Bekannte funktionierende Linux-Umgebung (Dok. 10 §10): Ubuntu 23.04, Python 3.11.4, gcc 12.3.0, `paplay`; das Erweiterungsmodul ist ein abi3-Modul (nach dem Absturz „deallocating None“ auf Python 3.11, behoben mit G4-005, benutzt es `Py_IncRef`/`Py_DecRef` statt der Makros). Ein Neubau am eigenen Rechner ist der sichere Weg: `cd c-module/python && rm -rf build && python3 setup.py build_ext --inplace`.

### 6.9 Konstanten und ihr Stand

Alle Konstanten sind nach der Hörprüfung nachstellbar (S4-16); der Projektinhaber kann Laufzeiten und Schwellen akustisch nicht stoppen.

| Konstante | Wert | Fundstelle im Code | Stand |
|---|---|---|---|
| Schreibwerkzeit | 80 ms, 70 bis 90 ms | `grafik_schreibwerk.py` | E 18.10.2026 |
| Zeichenklang, Ausblendung | 100 ms, 10 ms | `grafik_schreibwerk.py` | E 18.10.2026 |
| TAB, WRZL | 400 ms, 360 ms | `grafik_schreibwerk.py` | E (Nr. 17); `tab_400.wav` ohne eigene Abnahme |
| Schwelle Leser, Auslaufen | 100 ms, 60 ms | `grafik_geraeteton.py` | E; nachzustellen |
| Lesetempo | 130 Zeichen/s | `grafik_geraeteton.py` | E (O4-11) |
| Dauerstanzen, Ende, Abschalten | 50 ms, 50 ms, 5 s | `grafik_geraeteton.py` | E 16.10.2026 (Nr. 21) |
| Stanztempo | 50 Zeichen/s | `grafik_geraeteton.py` | E 18.10.2026 („ungefähr so“) |
| Grundgeräusch-Pegel | 0,8 | `grafik_rechnerton.py` | E 17.10.2026 |
| Vorlauf, Puffer der Senke | 2 Blöcke (20 ms), 20 ms | `grafik_tonmisch.py` | G4-004, am Gerät nicht gemessen |

### 6.10 Befunde und Hinweise zu den Quellen

1. **Pegel LL:** Dok. 10 S4-19 nennt die Basis 1,0 für Pult, LL und LS; der Code hat für LL seit G4-012 1,3. Eine Beschreibung dieser Änderung liegt in den Dokumenten nicht vor; hier steht der Code-Wert, vom Projektinhaber am 19.10.2026 bestätigt (§10.5).
2. **Dok. 03** beschreibt in Kopf, §2, §3 und im Absatz „Stand 16.10.2026“ noch „nichts eingebaut“, „120 ms ±10 %“ und „Einsatz nicht festgelegt“; maßgeblich sind hier §6 und Dok. 10. Dok. 03 ist nur im Kopf und mit einer Berichtigung zu O4-1 bis O4-6 vermerkt (Dok. 10 B-1, B-8). `tab_kurz.wav` und `tab_lang.wav` liegen als Quelle, werden aber nicht mehr gespielt.
3. **Eingabeklang beim ersten Zeichen:** Der Projektinhaber berichtete (19.10.2026), dass für das erste Zeichen im Fenster kein Klick kam; eine Ursache wurde nicht gefunden (Dok. 10 §11, „Drei Beobachtungen“). Das Debug-Log schreibt dazu je Eingabeklang eine Zeile `SW Eingabeklang …`. Offen.
4. **Nicht an echten Geräten gemessen:** Verzögerung (50 ms), Schreibwerkzeit im Betrieb, Stanztempo. Windows offen (§6.8).
5. **Ungeprüft:** Ob `ton/SW_Ton_Beschreibung.md` (Stand 15.10.2026, nachgeführt 19.10.2026) in allen Punkten mit Dok. 03 §5 Nr. 11 bis 24 übereinstimmt (Dok. 10 §6.3); die übrigen Handbücher sind nicht auf Töne durchgesehen (Dok. 10 B-8).

### 6.11 Kennungen

| Alte Kennung | Gegenstand | Abschnitt |
|---|---|---|
| S4-01, S4-02, S4-03, S4-12, S4-14, G4-001 bis G4-005 | Mischer, Senke, Tore, Verzögerung, Aufrufstellen | 6.1 |
| S4-05 bis S4-08, S4-17, O4-1 bis O4-10, U-9 | Schreibwerk, Selektor SW, angezeigte Eingabe | 6.2 |
| S4-09, O4-11 bis O4-13 | Lochstreifenleser | 6.3 |
| S4-10, S4-18, O4-14 bis O4-16, Dok. 03 §5 Nr. 15, 21, 23 | Lochbandstanzer | 6.4 |
| S4-11, O4-17, Dok. 03 §1 Nr. 4, 5; §5 Nr. 19, 20 | Rechner, Netzablauf | 6.5 |
| S4-13, S4-19, G4-012 | `--STUMM`, `--TON` | 6.6 |
| S4-04, O4-4 | Abbruch mit Code 16 | 6.7 |
| S4-15, S4-16, O4-18, B-2 | Plattformen, Hörprüfung, Konstanten | 6.8, 6.9 |

**Stand der Prüfung.** Aus den Dokumenten übernommen; im Code gegengelesen sind nur die Konstanten der Tabelle in §6.9 und `TON_BASIS`. Logikprüfungen laufen ohne Audiogerät (`grafik_stufe4_tests`, 69 Prüfungen, gegen den Python-Mischer und gegen das C-Modul; Prüfverfahren §3). Hörprüfung 1 und 2 und der Lauf mit Tk-Fenster sind vom Projektinhaber am 19.10.2026 als „ok“ gemeldet, ohne Einzelbefunde.

## 7 Echte Trommel

**Inhalt:** C-Module, Regel „Schlitz ist Schlitz“, Takt, Plattformschicht, Anbindung

**Quellen (alt):** Dok. 02; Dok. 07 (Stufe 1); `C8205-Interpreter-Magnettrommel.md` verweist hierher

Im Modus GRAFIK läuft die Magnettrommel „echt“: Die Zugriffe des Knotengraphen gehen über C-Module, die als Hintergrund-Thread die drehende Trommel nachbilden und Lese- und Schreibaufträge nur bedienen, wenn die angeforderte Zelle gerade unter dem Kopf liegt. Im Modus TEST bleibt es beim rechnerischen Verfahren (alle Zeiten 0) ohne C-Modul; die Klasse `Trommel` des TEST-Interpreters bleibt unverändert (Entscheidung 15.10.2026). Den Aufbau der Trommel (128 Bahnen mit je 32 Sektoren, 4096 Worte zu 33 Bit, Verschränkung der Sektoren) beschreibt `C8205-Interpreter-Magnettrommel.md`; hier steht, wie GRAFIK sie nachbildet. Alte Kennungen (Dok. 02 Nr., O-7 bis O-9, G1-xx) stehen in Klammern.

### 7.1 Bausteine

| Baustein | Aufgabe |
|---|---|
| `c-module/trommel.c/.h` | Hintergrund-Thread dreht die Trommel (Wortzeit **104 µs**, Reihenfolge `PERM` mit 32 Sektoren, `trommel_sektor` = untere 5 Bit der Adresse, `trommel_bahn` = obere 7 Bit); Auftragskanal `trommel_lesen_warten` / `trommel_schreiben_warten` |
| `c-module/bahnsperre.c/.h` | Hauptschalter und fünf Zusatzschalter; die Bahn ist gesperrt, wenn `bahn & ~zusatz == 0`; Bahnen ab 32 sind nie sperrbar. Speichert und lädt die Stellung in einer Datei neben der Trommel (§7.5) |
| `c-module/unterbrechung.c/.h` | Strg+C setzt `abbruch_angefordert` |
| `c-module/plattform.h` | Plattformschicht (§7.4) |
| `c-module/python/` | Python-Erweiterungsmodul `c8205_trommel` (statisch gelinkt, eine Datei `.so`/`.pyd`, Limited API ab CPython 3.8; enthält auch den Mischer `tonmisch`, §6.1) und Lader `trommel_lader.py` |
| `grafik_trommel.py` | Trommel-Klasse für GRAFIK über das C-Modul (`einschalten`, `--BASP`, Schalterdatei) |

Eine **statische Bibliothek** kann zur Laufzeit nicht „geladen“ werden; nicht ladbar kann nur ein Python-Modul oder eine dynamische Bibliothek sein. Um die Absicht des Projektinhabers (eine Datei, bei Fehlen Fehlermeldung und Ende) zu erfüllen, gibt es `libtrommel.a` (`make`) und das **fest eingebundene Erweiterungsmodul** `c8205_trommel`; die dynamische Variante (`libtrommel.so`/`trommel.dll` über `ctypes`) bleibt gebaut, ist aber nicht der vorgesehene Weg. Das C-Modul wird **vorübersetzt mitgeliefert** (`-static` gelinkt; Entscheidung 16.10.2026), ein eigener Bau ist möglich (`cd c-module/python && python3 setup.py build_ext --inplace`; nötig sind ein C-Compiler, die Python-Entwicklungsdateien und `setuptools`).

### 7.2 Regeln der Nachbildung

- **Aktuelle Zelle** (Dok. 02 Nr. 2): Das Modul führt die aktuelle Sektornummer, die alle 104 µs wechselt. Ein Auftrag wird **nur ausgeführt, wenn der Sektor seiner Adresse gerade der aktuelle ist**. Die Wahl der Bahn kostet keine Zeit. `trommel_aktueller_sektor()` liefert den Sektor exakt aus der Uhr; die Variable `trommel_aktuelle_sektornummer` bleibt als reine Beobachtungsvariable lockfrei (formal ein Datenwettlauf; bestätigt 16.10.2026, O-7 Nr. 2).
- **„Schlitz ist Schlitz“** (Nr. 4): Ist eine Sektornummer aktuell, dann für die **ganzen 104 µs**. Trifft eine Anforderung in dieser Zeitspanne ein, wird sie bedient, auch wenn der Sektor schon einen Teil seiner Zeit läuft. Das ist eine bewusst gewählte Gewohnheit (Ungenauigkeit) des Simulators. Folge: Trifft der Auftrag im Schlitz des richtigen Sektors ein, ist die **Wartezeit 0**; sonst wartet er auf den nächsten Tick, in dem sein Sektor aktuell ist, **1 bis 31 Ticks**. Zugriffe auf dieselbe Zelle innerhalb eines Schlitzes (Lesen und Zurückschreiben) kosten keine zusätzliche Zeit. (Das Makro `TROMMEL_ZUGRIFF_AUCH_IM_SCHLITZ=0` würde erst den nächsten Tickbeginn zulassen, 1 bis 32 Ticks; diese Variante ist nicht mehr getestet.)
- **Wartezeit:** `wartezeit` ist die Zahl der Ticks (Wortzeiten) vom Eintreffen bis zur Ausführung, 0 bis 31. Es ist immer nur ein Aufrufer gleichzeitig im Kanal. Die gemessenen Wartezeiten bestätigen unabhängig die Sektorreihenfolge: logisch nächste Adresse (Sektor +1) 5 Ticks, physisch benachbart (+15 oktal) 1 Tick.
- **Gesperrte Schreibzugriffe** verbrauchen ihre Wartezeit (wie nach `bahnsperre.h`; bestätigt 16.10.2026, O-7 Nr. 1).
- **Werte** werden auf 33 Bit begrenzt; eine Adresse über 07777 liefert `TROMMEL_FEHLER`.
- **Abbruch:** `abbruch_angefordert` (Strg+C) oder `trommel_warten_abbrechen()` beendet das Warten mit `TROMMEL_ABGEBROCHEN`; der Aufrufer prüft alle 50 ms. Das Flag wird schon beim Eintreffen jeder Anforderung geprüft und dabei verbraucht.
- **Startlage:** nach dem Einschalten **beliebig (zufällig)**, wie am echten Gerät. In GRAFIK gibt es **keinen Schalter** für eine feste Startlage (O-7 Nr. 3, 16.10.2026); `trommel_einschalten_start(pfad, index)` mit fester Startlage bleibt für Testrahmen.
- **Rückgabecodes** des Kanals: `TROMMEL_OK`, `TROMMEL_SCHREIBEN_GESPERRT`, `TROMMEL_ABGEBROCHEN`, `TROMMEL_FEHLER`.

### 7.3 Takt

Der Takt kommt aus der Monotonic-Uhr (Linux `clock_gettime`, Windows `QueryPerformanceCounter`) mit absoluten Zeitpunkten; die aktuelle Zelle ist eine Funktion der Uhr. Ein verspätet aufwachender Hintergrund-Thread **holt übersprungene Ticks der Reihe nach nach**, sodass kein Sektor ausgelassen wird. Unter Linux ist der Timer-Slack auf 1 ns gesetzt (der Standard von 50 µs wäre fast ein halber Tick). Gemessen unter Linux (ein Kern): mittlere Aufwachverspätung 25 µs, größte 1,9 ms (19 Ticks nachgeholt); die Tickzahl stimmt trotzdem mit der Uhr überein.

### 7.4 Plattformschicht

| Aufgabe | Linux | Windows |
|---|---|---|
| Thread, Mutex, Bedingungsvariable | `pthread` | `CreateThread`, `CRITICAL_SECTION`, `CONDITION_VARIABLE` |
| Uhr | `clock_gettime(CLOCK_MONOTONIC)` | `QueryPerformanceCounter` |
| Schlafen bis zum nächsten Tick | `clock_nanosleep` (absolut), kein Spin | siehe unten |
| Strg+C | `sigaction(SIGINT)` | `signal(SIGINT)` |

**Kein aktives Warten** (entschieden 16.10.2026, O-7 Nr. 4: „alle 20 µs prüfen reicht“; zuerst als 20 ms gelesen, gemeint sind Mikrosekunden): Der Hintergrund-Thread schläft immer; solange ein Auftrag ansteht, prüft er die Uhr in Abständen von höchstens 20 µs. Ein Tickbeginn darf bis etwa 20 µs spät erkannt werden; die Tickzahl und die Wartezeit in Wortzeiten bleiben exakt. Unter Windows arbeitet die Systemuhr nur grob (`timeBeginPeriod(1)` ist gesetzt); dort kann die **Echtzeit-Dauer** eines Zugriffs länger werden, die Wartezeit in Wortzeiten nicht. **Stand Dok. 02 (16.10.2026): Der Windows-Zweig (Parameter `spinnen` in `plattform.h`, Schalter `req_wartet` in `trommel.c`) war noch nicht angepasst; ob das inzwischen geschehen ist, habe ich nicht geprüft.** Bauen unter Windows: MinGW-w64 (Entscheidung 16.10.2026, O-8; kein MSVC, `build_msvc.bat` liegt nur bei); die Bauskripte sollen `-static` bekommen und `--compiler=mingw32` benutzen; mit MinGW-w64 gilt das Modul voraussichtlich nur für die Python-Version, mit der gebaut wurde (die versionsunabhängige `python3.lib` über `#pragma comment` gibt es nur bei MSVC). **Alles ungebaut und ungetestet** (§9, §10; Prüfverfahren §9).

### 7.5 Anbindung an den GRAFIK-Interpreter

Seit Stufe 1 umgesetzt und abgenommen (18.10.2026; Dok. 07). Dok. 02 §6 führt die Anbindung noch als „nicht umgesetzt“; das ist überholt.

- **Eigener Zweig:** GRAFIK benutzt die Wartezeit der echten Trommel, nicht zusätzlich die rechnerische Schleife der Knoten 040/041 (der Knotengraph der Dokumentation bleibt gemeinsam). Alle Zugriffe laufen über `Machine.rd` und `Machine.wr` auf die Klasse in `grafik_trommel.py`; das Modul ist der **einzige** Zugriff auf die Datei (kein Zwischenspeicher `mem`; so verlangt es Dok. 02 §6, im Code nicht gegengelesen; gegengelesen sind nur Wortzeit 104 µs, `PERM` mit 32 Sektoren, `.basp` in `bahnsperre.c` und der Ladeweg mit Code 16 in `grafik_trommel.py`). Besonders zu beachten ist die Befehlsentnahme nach X-Abbruch als einzige Stelle, die von „alle Zeiten 0“ abweicht (`C8205-Interpreter-Überblick_und_Gesamtaufbau.md`, Abschnitt 4.1).
- **Start:** `lade_trommelmodul()`, dann Prüfung der Trommeldatei, dann `einschalten`, **als Erstes**, vor dem ersten Trommelzugriff. Am Ende (`finally`) `ausschalten()`; Strg+C beendet auch das C-Modul. Ist das Modul nicht ladbar oder die Trommel nicht einschaltbar: Fehlermeldung mit Bauanleitung und **Rückkehrcode 16**, wie bei fehlerhafter Trommeldatei (bestätigt 15.10.2026).
- **Trommeldatei:** `virtuelle_Geraete/Trommel/trommel.txt` (4096 Zeilen `aaaa: ttttttttttt` mit LF, 18 Byte je Zeile, 73728 Byte), gemeinsam für TEST und GRAFIK (Entscheidung 15.10.2026); `--trommel PFAD` gilt in beiden Modi. Das Modul prüft Größe sowie erste und letzte Zeile und weist andere Dateien (das alte 17-Byte-Format, CRLF) mit Meldung ab. Pfade mit Umlauten sind unterstützt (UTF-8, unter Windows `_wfopen`).
- **Bahnsperre und `--BASP`** (Entscheidungen 15. und 16.10.2026, Entwurf 86, 87): `--BASP=abcdef` (sechs Ziffern 0/1, von links: Hauptschalter 0001, dann 0040, 0100, 0200, 0400, 1000) wird beim Hochfahren der Trommel an das C-Modul übermittelt, vor dem ersten Zugriff. Das Pult-Fenster stellt die Schalter **nicht** dar (ausdrücklich entschieden, O-9). Das Modul hat dabei drei Aufgaben: (1) wird eine Stellung übermittelt, übernimmt es sie und speichert sie in der **Schalterdatei neben der Trommel** (`trommel.basp`: Pfad der Trommeldatei ohne Endung plus `.basp`; eine Zeile mit sechs Zeichen 0/1 und LF); (2) fehlt `--BASP`, entnimmt es die Stellung aus dieser Datei; (3) existiert sie noch nicht, legt es sie mit `000000` an. Eine vorhandene, aber formal fehlerhafte oder nicht lesbare Datei wird nicht überschrieben (Meldung, Code 16); geschrieben wird bei jeder übermittelten Stellung. Der Kommentar in `bahnsperre.h`, es werde nie eine Konfigurationsdatei geben, ist damit überholt.
- **Startbelegung** (entschieden 15. und 16.10.2026): Die Trommel ist „immer so, wie sie ist“. In GRAFIK gibt es keine Vorbelegung und keinen Eingriff des Interpreters in die Trommeldatei; was darin steht, ist die Startbelegung. Für einen Kaltstart muss die Datei ein lauffähiges Minimalprogramm enthalten (das KEP braucht man nur, um das MP erstmals zu laden). **Den Zustand der Datei pflegt der Projektinhaber selbst;** das Paket liefert weder eine Vorlage `MP.txt` noch ein Zurücksetz-Skript. Wege zum Zurücksetzen (nur TEST oder Hilfsskript): leer mit `testscripte/erzeuge_leere_trommel.py`; auf das Minimalprogramm durch Laden mit `Tests/pj2-bis_minimalprogramm.test` auf leerer Trommel. **Jeder TEST-Lauf verändert die gemeinsame Datei und damit die Startbelegung von GRAFIK;** es gibt keine Warnung bei nicht lauffähiger Trommel und keinen Schutz gegen gleichzeitigen Zugriff.
- **Betriebsart:** Im Modus GRAFIK die echte Trommel; im Modus TEST und beim Claude-Interpreter das rechnerische Verfahren. Die Gegenprobe (Claude-Interpreter) vergleicht Ergebnisse, keine Echtzeit: Registerinhalte und Ausgaben dürfen nicht von der Trommelwartezeit abhängen.

### 7.6 Folgen

- **Tempo:** Jeder Zugriff dauert 0 bis 3,2 ms (0 bis 31 Wortzeiten). Bei zufälligen Adressen liegt die mittlere Wartezeit bei etwa 16 Ticks (rund 1,6 ms), bei nach der Trommelstruktur gewählten Adressen bei 0 bis 5 Ticks. Programme mit vielen Zugriffen laufen damit zum ersten Mal in realistischer Zeit; die Laufzeit hängt von der Programmierung ab. Gemessen ist das nur an den Testfolgen des Moduls.
- **Nicht reproduzierbar:** Die Wartezeit hängt von der Echtzeit ab, zu der der Interpreter einen Auftrag stellt. Läuft der Interpreter in Python langsamer als eine Wortzeit zwischen zwei Aufträgen, verpasst er „optimale“ Folgezellen und wartet bis zum nächsten Auftreten des Sektors. **Zeiten und Zyklenzahlen schwanken von Lauf zu Lauf.** Zeiten sind deshalb von der Gleichwertigkeit TEST/GRAFIK ausgenommen (Register, 16.10.2026); Zeitvergleiche in GRAFIK werden nicht gefordert. Ein virtueller Takt (deterministisch, ohne Thread) wäre eine weitere, nicht gewünschte Änderung.
- **Anzeige:** Ob eine Anzeige die aktuelle Sektornummer zeigen soll, ist nicht festgelegt. Das Lampentempo des Pults ist in §3.5 geregelt.

### 7.7 Prüfstand

Linux (gcc, ein Kern): `make test` mit 8 Prüfgruppen bestanden; 11 Python-Tests des Erweiterungsmoduls bestanden (Lesen mit Wartezeit 0 bis 31, Schreiben mit Begrenzung auf 33 Bit, Bahnsperre, Abbruch, Datei im alten Format, Pfad mit Umlaut, Strg+C mit Rückkehrcode 8, Lader mit Code 16); AddressSanitizer, UndefinedBehaviorSanitizer und ThreadSanitizer ohne Meldung (ein früher Datenwettlauf bei `req_wartet` ist durch atomare Zugriffe behoben); die alten Testrahmen `testframe.c` und `testframe_trommel.c` kompilieren, wurden mit der neuen Fassung nicht ausgeführt. Die Zahlen stammen aus Dok. 02 §5 (Stand 16.10.2026) und sind in dieser Sitzung **nicht neu gelaufen**. Die Meldung des Projektinhabers vom 19.10.2026 (Gesamtlauf `grafik_alle_tests.sh` 18 von 18 Blöcken) schließt die Trommel ein (Prüfverfahren §8).

### 7.8 Kennungen

| Alte Kennung | Gegenstand | Abschnitt |
|---|---|---|
| Dok. 02 Nr. 1, 2, 5, 6, 8, 9, 10 | Vorgaben: echte Trommel, Thread, Modi, Strg+C, Bibliothek | 7.1, 7.2, 7.5 |
| Dok. 02 Nr. 4, O-7 Nr. 1 bis 3 | „Schlitz ist Schlitz“, gesperrte Zugriffe, Beobachtungsvariable, Startlage | 7.2 |
| O-7 Nr. 4, O-8 | kein aktives Warten, MinGW-w64 | 7.4 |
| O-9, Entwurf 86 und 87 | `--BASP`, Schalterdatei `.basp` | 7.5 |
| G1-xx (Stufe 1), Dok. 07 | `grafik_trommel.py`, Treiber | 7.1, 7.5 |

## 8 Hardware-Check

**Inhalt:** `--HWCHECK`, Fenster, Anzeige

**Quellen (alt):** Dok. 01 §1.9; `HWCHECK_HW-003.md`; Dok. 10 §13 bis §15 (Haltzeit)

Mit dem Schalter `--HWCHECK` (nur Modus GRAFIK, nur mit dem Pult-Fenster; Entscheidung 17.10.2026, Entwurf 97, erweitert Entwurf 98, Gruppierung geändert Entwurf 99) blendet das Programm **ein weiteres Fenster** auf, mit dem sich die Wirkung der Pult-Tasten auf die Hardware-Elemente genau ansehen lässt. Das Fenster ändert nichts am Rechner. Mit `--ohne-fenster`, `--entwickler-tasten` und `--entwickler-k0` ist `--HWCHECK` wirkungslos (Hinweis im Terminal). Alte Kennungen (HW-xxx, HZ-xxx, Entwurf-Nummern) stehen in Klammern.

### 8.1 Fenster

- **Größe und Lage:** nur so groß, wie die Anzeige braucht (keine Skalierung), **verschiebbar**; erscheint beim Start neben dem Pult-Fenster.
- **Dauer:** Das Fenster bleibt aufgeblendet, solange der GRAFIK-Interpreter gestartet ist. Es lässt sich **nicht schließen** (X am HW-Check-Fenster ohne Wirkung) und endet mit dem Pult-Fenster (Netz aus, X am Pult, Strg+C). „Aufgeblendet“ heißt nicht „immer im Vordergrund“.
- **Aktualisierung:** im 40-ms-Takt des Pult-Fensters (§3.5). **Keine Rückwirkung** auf den Rechner: Der Speicherinhalt wird ohne Koinzidenz direkt gelesen, ohne Wartezeit und ohne Änderung der Trommelstatistik (§7).
- **Vor dem Einschalten** (Rechner aus) zeigt das Fenster die Registerwerte (alles 0).
- **Nicht Teil der Anforderung:** Schreiben in Register oder Speicher, Haltepunkte, weitere Elemente (Flags, V1/V2); sie lassen sich später ergänzen. Die umlaufende Trommellage (der Sektor unter dem Kopf, wechselt alle 104 µs) wäre im 40-ms-Takt nicht lesbar und ist nicht Teil der Anzeige; sie ließe sich bei Bedarf als eigene Zeile ergänzen.

### 8.2 Anzeige: sechs Zeilen untereinander

Alles oktal, außer der letzten Zeile (`grafik_hwcheck.py`, HW-004).

| Zeile | Inhalt |
|---|---|
| `BZ` | Befehlszähler, 4 Stellen |
| `BR` | **AR-Teil und OR** des Befehlsregisters, 4 und 3 Stellen, wie die Lampenreihen AR und OR am Pult (im Programm `m.adr`, `m.OR`) |
| `Spur Sektor` | Spurnummer (3 Stellen, 000 bis 177) und Sektornummer (2 Stellen, 00 bis 37) der **Adresse im Speicheradressregister AR** (`m.AR`): Spur = AR ÷ 32, Sektor = AR mod 32 (logische Sektornummer wie `sektor()` im Interpreter); Beispiel `054 13` |
| `AC` | Akkumulator, 11 Stellen in Vierergruppen |
| `<<AR>>` | **Speicherinhalt** an der Adresse im Register AR, 11 Stellen in Vierergruppen; der Wert von AR steht zur Kontrolle im Namen (`<<AR>>  AR=0001`) |
| `Haltzeit` | Millisekunden, dezimal (§8.3) |

**Vierergruppen werden von links gebildet:** 11 Stellen = 4 + 4 + 3, z. B. `2206 0635 124`, Null: `0000 0000 000` (geändert in Entwurf 99 nach dem Test des Projektinhabers vom 17.10.2026; die Entwürfe 97 und 98 bildeten sie von rechts, 3 + 4 + 4). Der AR-Teil von BR ist der **Adressteil des Befehlsregisters** (die Pult-Lampenreihe AR); das AR in `<<AR>>` und in `Spur Sektor` ist dagegen das **Speicheradressregister**. Das sind zwei verschiedene Register.

### 8.3 Haltzeit (seit 19.10.2026)

Die sechste Zeile zeigt die **reine Rechnerzeit** in Millisekunden (eine Nachkommastelle) vom Start (Taste R wirkt) bzw. von der Fortsetzung nach einem Halt bis zum nächsten Halt, dazu „von → bis“, z. B. `85.0 ms  E/A-Halt -> E/A-Halt` oder `R -> E/A-Halt`. Ohne Messung steht `---.- ms`.

- **Als Halt gilt:** Stopp (US/BS, Halt wegen Überlauf), Fehler (FE, Geräte- oder Ablauffehler), E/A-Halt (der Rechner wartet an einem Eingabebefehl auf ein Zeichen oder eine Lochbanddatei). Die Taste H zählt nicht.
- **Die Wartezeit im Halt zählt nicht** (Entscheidung des Projektinhabers 19.10.2026, HZ-003; `NUR_LAUF = True` in `grafik_haltzeit.py`; `False` gibt die Zeit mit Wartezeit zurück). Die frühere Fassung zeigte bei Halt → Halt die Zeit mit Wartezeit (HZ-001) und kurz auch beide Zeiten (HZ-002); beides entfällt. Im Debug-Log steht je Halt die Marke `HALT` mit Zeit und, falls bekannt, Laufzeit.
- **Messung:** `grafik_haltzeit.py` (`m.haltuhr`); `c8205_grafik.HaltMaschine` (Unterklasse von `Machine`, `c8205_interp.py` bleibt unberührt) meldet jedes Setzen von `halted` von False auf True; K0-Warteschlange und Lochbandleser haben dafür die Haken `bei_halt` und `bei_weiter`.
- Die Haltzeit dient auch zur Beurteilung der SW-Eingabe: Der Abstand der Eingabebefehle (350 bis 450 ms gemessen, Zeit mit Wartezeit) liegt um die Fokus-Schwelle von 0,4 s (§5.7).

### 8.4 Fokus

Bei geöffnetem HW-Check-Fenster kann das SW-Fenster den Fokus bei einem Eingabe-Halt nicht immer halten; der Tk-Test meldet eine Warnung. Das hängt vom Fenstermanager ab und ist als bekannte Eigenschaft akzeptiert (B-5, A-4; kein Programmfehler). Im echten Lauf holte sich das SW-Fenster den Fokus bei 97 von 97 Tipps; ein HW-Check-Fenster, das während eines Eingabe-Halts erst öffnet, kommt in der Praxis nicht vor.

### 8.5 Stand, Annahmen, Prüfung

- **Abnahme:** Das Aussehen beurteilt der Projektinhaber; bei der Abnahme der Stufe 3 (18.10.2026) wurde keine Beanstandung gemeldet. Der Tk-Test (alle Punkte OK) lief am echten Fenster.
- **Standardannahmen aus Dok. 01 §1.9 Nr. 5, nicht einzeln bestätigt:** (b) die beiden Bedeutungen von AR (§8.2); (c) Anzeige auch vor dem Einschalten; (d) „aufgeblendet“ = nicht schließbar; (f) `Spur Sektor` bezieht sich auf das Speicheradressregister AR, nicht auf die umlaufende Trommellage (Entwurf 98, zur Bestätigung). Die Gruppierung von links (a) ist durch den Test des Projektinhabers vom 17.10.2026 festgelegt.
- **Rückfall beim Lesen** (HW-003): Hat die Trommel-Klasse keine Methode `einblick()` (älterer Stand von `grafik_trommel.py`), liest der HW-Check direkt über das C-Modul (`trommel.T.lesen`, ohne Koinzidenz, ohne Statistik); bei einem Lesefehler bleibt der Platzhalter `---- ---- ---`, der Grund steht in `grafik_hwcheck.LETZTER_FEHLER`. Ein Platzhalter im Fenster weist also auf einen Lesefehler hin.
- **Prüfung:** Die Formatierung (`hwcheck_zeilen`, `gruppen4`) braucht kein Tkinter und ist in `testscripte/grafik_pult_tests.py` (Klasse `HwCheck`, darin `test_rueckfall_ohne_einblick`) geprüft; die Haltzeit-Prüfungen (z. B. `test_haltzeit_nur_rechnerzeit`) stehen nach Dok. 10 ebenfalls dort bzw. im Gesamtlauf (die Fundstelle habe ich nicht einzeln geprüft). Am echten Fenster ist der Hardware-Check mit dem Tk-Test (A-4) und der Hörprüfung 2 gelaufen (`./c8205_grafik.sh --HWCHECK`). Im Code gegengelesen habe ich nur den Kopf von `grafik_hwcheck.py` (HW-004, sechs Zeilen, Gruppierung von links), `NUR_LAUF` in `grafik_haltzeit.py`, die Fokus-Schwelle von 0,4 s in `grafik_sw_fenster.py` und das Vorhandensein der Klasse `HwCheck`.
- **Hinweis zu Dok. 01 §1.9:** Der Text nennt noch fünf Zeilen und keine Haltzeit; maßgeblich ist diese Beschreibung (HW-004, HZ-003).

### 8.6 Kennungen

| Alte Kennung | Gegenstand | Abschnitt |
|---|---|---|
| Entwurf 97, 98, 99; Dok. 01 §1.9 | Fenster, Zeilen, Gruppierung | 8.1, 8.2 |
| HW-003 | Lesen des Speicherinhalts (Rückfall), Gruppierung von links | 8.2, 8.5 |
| HW-004, HZ-001, HZ-002, HZ-003 | Haltzeit | 8.3 |
| B-5, A-4 (Dok. 09) | Fokus bei geöffnetem Fenster | 8.4 |

## 9 Plattformen

**Inhalt:** Linux (getestet), Windows (nicht getestet), Abhängigkeiten (Tk, ALSA/winmm)

**Quellen (alt):** Dok. 00 §3.2; Dok. 01 §9; Dok. 02 §5.3; Dok. 10 §10; Dok. 11 S5-12

Zielsysteme sind **Linux und Windows**, nicht von bestimmten Versionen abhängig. Getestet ist nur Linux; ein Windows-Tester „kommt noch“ (Antwort des Projektinhabers 16.10.2026). Die Abnahme der Stufen 4 und 5 am 19.10.2026 erfolgte **ohne Windows**; Windows ist eine eigene, spätere Abnahme (O5-3, A5-8; Prüfverfahren §9).

### 9.1 Linux

| Gegenstand | Stand |
|---|---|
| Voraussetzungen | Python 3 mit Tkinter (unter Linux oft ein eigenes Paket, z. B. `python3-tk`); für die Töne eines der Abspielprogramme `paplay`, `pw-cat`, `aplay` (der Mischer nimmt das erste vorhandene in dieser Reihenfolge); ohne Abspielprogramm bricht GRAFIK ohne `--STUMM` mit Code 16 ab (§6.7). C-Modul: vorübersetzt mitgeliefert (`c8205_trommel.abi3.so`, statisch gelinkt); ein eigener Bau braucht gcc, `python3-dev` und `setuptools` (§7.1) |
| Start | `./c8205_grafik.sh [Schalter]` (§2) |
| Getestet | Trommel und Mischer in C (Linux, gcc, ein Kern), Logiktests ohne Fenster, Tk-Test am echten Fenster, Hörprüfungen 1 und 2 und echter Lauf mit Tk-Fenster durch den Projektinhaber (19.10.2026); Gesamtlauf `grafik_alle_tests.sh` 18 von 18 Blöcken auf seinem Rechner |
| Bekannte Umgebung | `hp7`, Ubuntu 23.04, Linux 6.2.0-27, Python 3.11.4, gcc 12.3.0, `paplay` (pacat 16.1), `pw-cat` (libpipewire 0.3.65), `aplay` 1.2.8 |
| Python-Version | Das Erweiterungsmodul ist ein abi3-Modul für CPython ab 3.8. Bis Checkpoint 56 wurde es mit 3.12 gebaut und stürzte auf 3.11 ab (`deallocating None`); behoben in G4-005 (§6.8). Die Entwicklungsumgebung hat Python 3.12; der Absturz ließ sich dort nicht nachstellen |
| Bekannte Eigenschaften | Fokus bei geöffnetem HW-Check-Fenster hängt vom Fenstermanager ab (§8.4); der Strg+C-Test des C-Moduls schlägt fehl, wenn `grafik_alle_tests.sh` als Hintergrundauftrag (`&`) startet, weil die Shell dann SIGINT ignoriert; im Vordergrund ist er grün |

### 9.2 Windows (nicht getestet)

- **Stand:** Alles, was Windows betrifft, ist **ungebaut und ungetestet**: der Windows-Zweig der Trommel (Win32-Threads, `QueryPerformanceCounter`; Dok. 02 §5.3), der Mischer `tonmisch` mit `winmm` (`waveOut` mit vier Puffern zu 10 ms), das Startscript `c8205_grafik.bat` (neu angelegt, Entwurf) und `c8205_interpreter.bat`. Eine Syntaxprüfung des Trommelzweigs (`gcc -fsyntax-only -D_WIN32` gegen eigene Platzhalter-Header) fand keine Fehler; sie ersetzt keinen Test. Das Pult-Fenster (Tkinter) ist plattformneutral geschrieben, aber unter Windows nicht gestartet; Tkinter gehört nach bisheriger Kenntnis zur üblichen Python-Installation, geprüft ist das nicht.
- **Compiler:** MinGW-w64 (entschieden 16.10.2026, O-8; der Projektinhaber hat nur diesen installiert), kein MSVC. Bau: `mingw32-make` im Ordner `c-module` und `python setup.py build_ext --inplace --compiler=mingw32` im Ordner `c-module/python`. Offen sind `-static` in Makefile und `setup.py` und die Frage, ob ein mit MinGW-w64 gebautes Modul nur für die Python-Version gilt, mit der gebaut wurde.
- **Auslieferung:** vorübersetzt, eine Datei je System; die Windows-Datei erst, wenn der Tester sie geprüft hat.
- **Töne unter Windows bis zum Mischer:** Rechnertöne über `winsound` (nur ein Klang gleichzeitig), Schreibwerkzeit und Lesetempo ja, sonst kein Ton, mit Hinweis beim Start (O4-18); `--TON` wirkt für Pult nicht (§6.6). Der C-Mischer hat `winmm`-Code; in `c8205_grafik.py` bleibt der Windows-Zweig bis zum Tester unverändert.
- **Trommel:** Die Systemuhr arbeitet unter Windows nur grob; die Wartezeit in Wortzeiten bleibt exakt, die Echtzeit-Dauer eines Zugriffs kann länger werden (§7.4). Die Trommeldatei muss LF-Zeilenenden haben (Werkzeuge im Textmodus würden CRLF schreiben; das Modul weist solche Dateien ab). Strg+C-Test des Erweiterungsmoduls wird unter Windows übersprungen.
- **Gemeinsam relevant:** Zeilenenden, Namen der Bibliotheken (`libtrommel.so`, `trommel.dll`), Pfadtrenner (Pfade mit Umlauten sind über `_wfopen` vorgesehen), Strg+C-Behandlung.
- **Abnahme:** Windows wird gegen das Prüfverfahren abgenommen (O5-3, O6-5; Prüfverfahren §9 mit B-2 und A5-8).

### 9.3 macOS

Nicht Gegenstand der Anforderungen; im Code ist nur das Merken der Fensterlage (FL-001) für macOS vorgesehen (`~/Library/Application Support/C8205/`). Getestet ist nichts.

## 10 Offene Punkte

Dieser Abschnitt führt alles, was bei Abschluss der Stufen 1 bis 5 nicht entschieden, nicht bestätigt oder nicht geprüft war. **Entschiedenes steht nicht hier**, sondern in Anhang A (Register) und in den Abschnitten 1 bis 9. Die Punkte sind nach Art gruppiert; Kennungen in Klammern verweisen auf die alte Fundstelle (Anhang B). Wo ich einen Stand nicht gegengeprüft habe, steht es dabei.

### 10.1 Windows (eigene, spätere Abnahme)

Entschieden 19.10.2026 (O5-3): Stufe 5 wurde ohne Windows abgenommen; Windows ist eine eigene Abnahme, sobald ein Tester da ist (Dok. 00 §4: der Tester „kommt noch“, baut und testet selbst; Compiler MinGW-w64). Bis dahin bleibt der Windows-Zweig ungetestet. Die Abnahmekriterien stehen im Prüfverfahren §9.

| Nr. | Punkt | Stand | Alte Fundstelle |
|---|---|---|---|
| OP-01 | **Bau `tonmisch` mit MinGW-w64** und Mischer mit `winmm` (Mischer-Code für Windows ist geschrieben, nicht übersetzt) | offen | B-2 (Dok. 10), S4-02, S4-15 |
| OP-02 | **Startskripte** `c8205_grafik.bat` und `c8205_interpreter.bat` | angelegt, nicht getestet | S5-12, A5-8 (Dok. 11) |
| OP-03 | **Ton unter Windows:** bis zum Mischer nur Rechnertöne (`winsound`), Schreibwerkzeit und Lesetempo; sonst kein Ton, mit Hinweis beim Start | bestätigt (O4-18, „wenn du meinst. ja“), ungetestet | O4-18 |
| OP-04 | **Trommel, Plattformschicht Windows** (`plattform.h`, Win32): nicht übersetzt, nicht getestet. Ob dort das aktive Warten inzwischen entfernt ist (Dok. 02 §4.4: „noch nicht angepasst“, Stand 16.10.2026), habe ich **nicht geprüft** (→ §7.4) Aus Dok. 02 §5.3 zusätzlich zu prüfen: das Makefile setzt unter Windows kein `-static` (Entscheidung Entwurf 67); ohne `--compiler=mingw32` sucht setuptools nach MSVC (Kenntnisstand des Entwicklers, nie geprüft); der Strg+C-Test wird unter Windows übersprungen; Echtzeit-Prüfungen der Trommel sind dort neu zu bewerten; das Erweiterungsmodul (Limited API) ist unter MinGW-w64 voraussichtlich an die Python-Version gebunden (Dok. 00 §6, Entwurf 85; nie geprüft) | offen | Dok. 02 §4.4, §5.3 |
| OP-05 | **Tk-Verhalten unter Windows und WSL**, Bildschirmgrößen, Zwischenablage, X/Strg+C über die Pipe-Meldung (plattformneutral gewählt, Dok. 04 Nr. 15): nie geprüft | offen | Dok. 01 §8 Nr. 13, Dok. 04 Nr. 15 |
| OP-26 | **Kein Sammellauf unter Windows:** `grafik_alle_tests.sh` ist ein Bash-Skript, eine `.bat`-Entsprechung gibt es nur für `r300_eingabe_*`; ebenso weicht `build_msvc.bat` (MSVC) von S4-02 (MinGW-w64 für `tonmisch`) ab. Welcher Weg unter Windows gilt, ist offen (Prüfverfahren §9, W-2 und W-5). Aufgenommen am 19.10.2026 (Projektinhaber: „mir egal“, daher vom Entwickler eingetragen) | offen | Prüfverfahren §9, §10 |

### 10.2 Zu entscheiden oder zu bestätigen

Diese Punkte sind im Verhalten umgesetzt oder im Code festgelegt, aber vom Projektinhaber nicht ausdrücklich entschieden. OP-06, OP-07, OP-08 und OP-12 wurden am 19.10.2026 bestätigt und stehen in §10.5.

| Nr. | Punkt | Stand | Alte Fundstelle |
|---|---|---|---|
| OP-09 | **Eingabeklang beim ersten Zeichen:** Der Projektinhaber meldete am 19.10.2026, dass für das erste Zeichen im Fenster kein Klick kam; Ursache nicht gefunden. Das Debug-Log schreibt je Eingabeklang eine Zeile `SW Eingabeklang …` (→ §6.10) | offen | Dok. 10 §11 |
| OP-10 | **E+ und BR/BZ:** Nach `E+` zeigt BR noch den alten Befehl, dessen Operation (Phase IV) schon ausgeführt ist; BZ kann einen Zwischenwert zeigen. Entspricht der Knotenautomat hier der Anlage? (→ §3.8) | offen | §3.8 (Dok. 01 §1.7/§1.8, Quelle nicht einzeln geprüft) |
| OP-11 | **G bei gehaltenem E:** löscht wie bisher, das Loslassen tut danach nichts. Handbuch 4.1 Nr. 2 sieht nur das Löschen des Überlaufs vor; nicht umgesetzt (→ §3.8) | offen | §3.8 (Dok. 01 §1.7/§1.8, Quelle nicht einzeln geprüft) |

### 10.3 Standardannahmen ohne Einzelbestätigung

Bei der Abnahme der Stufen nicht beanstandet, aber nie einzeln bestätigt. Sie gelten als Verhalten, bis jemand etwas anderes sagt.

| Nr. | Annahme | Alte Fundstelle |
|---|---|---|
| OP-13 | **Stufe 1, Annahmen (1) bis (3):** (1) nach einem Halt bleibt der Rechner stehen, H und R heben das auf; (2) H im Lauf wirkt an der Befehlsgrenze (Knoten 2), im Eingabe-Halt sofort, R setzt danach den Befehl fort; (3) Kanal- und Schalterwechsel im Lauf wirken an der Befehlsgrenze bzw. im Eingabe-Halt (Wiederaufsetzen des Eingabebefehls) | `c8205_grafik.py` (Kopfkommentar), Dok. 08 §4 |
| OP-14 | **Stufe 3:** S3-06 (WR, TAB), S3-07 (Auslegung a), S3-15 (Lage f) | Dok. 09 §6 |
| OP-15 | **HW-Check:** (b) beide Bedeutungen von AR; (c) Anzeige auch vor dem Einschalten; (d) „aufgeblendet“ heißt nicht schließbar; (f) `Spur Sektor` bezieht sich auf AR, nicht auf die umlaufende Trommellage (→ §8.5) | Dok. 01 §1.9 Nr. 5 |
| OP-16 | **Mausbedienung:** Dok. 06 ist nur so weit umgesetzt, wie Dok. 01 §1.7 es wiederholt | Dok. 08 §4 |
| OP-17 | **Klicks im Dauerlauf R:** Das Pult meldet jeden Klick sofort, der Interpreter fragt an jeder Befehlsgrenze ohne Warten nach, Wirkung spätestens 50 ms. Seit 16.10.2026 „vorläufig entschieden, zu erproben“ (Dok. 01 §7 Nr. 14); ob die Erprobung ausdrücklich belegt ist, habe ich nicht geprüft | F-15 (a) |
| OP-31 | **Rücktaste, Annahmen (1) bis (5)** (§5.6): löscht das Zeichen links der Schreibposition, auch aus der Rechnerausgabe; am Zeilenanfang ohne Wirkung; der Rechner erfährt nichts; kein Ton; wirkt auch ohne aktiven `011`. Entschieden ist nur „Löschwirkung ja, keine Anzeige eines Namens“ (19.10.2026); die fünf Annahmen stehen in Dok. 05 F-64 als „bitte bestätigen“ und wurden nicht einzeln beantwortet | Dok. 05 F-64 (a) |
| OP-34 | **Leserdateien bei gleicher Änderungszeit:** Sortiert wird nach Änderungszeit, bei Gleichstand nach Dateiname. Das ist eine Standardannahme (Dok. 00 §6, Entwurf 35, F-11 (b)); im Code so umgesetzt (`grafik_geraete.py`: Sortierung nach `(st_mtime_ns, name)`), vom Projektinhaber nicht ausdrücklich bestätigt. **Namensgleichheit im `LOCHSTREIFENKORB`:** nichts festgelegt (Entwurf 37); der Code verschiebt mit `shutil.move`, das Verhalten bei gleichem Namen ist nicht geprüft | Dok. 00 §6 (Entwurf 35, 37), Dok. 05 F-11 |
| OP-35 | **Pult-Auslegungen ohne Bestätigung:** (a) Wechselt der Kanal per Befehl im Programm, folgen die Lampen K1 bis K3 bzw. T und SW, die Rastung der Kanaltaste aber nicht (M-34 Nr. 1, im Text als „Auslegung, nicht ausdrücklich bestätigt“ geführt, §4). (b) Dass ein Klick auf R innerhalb der 0,25 s nach einem Klick auf E oder M sofort wirkt, ist eine Entscheidung des Entwicklers auf Delegation des Projektinhabers (M-21 Nr. 5, Entwurf 79), nicht sein Wortlaut | Dok. 06 M-34, M-21 |

### 10.4 Bekannte Einschränkungen und Befunde

| Nr. | Punkt | Stand | Alte Fundstelle |
|---|---|---|---|
| OP-18 | **`sw_eingabe_leser_stanzer.test`** liefert im Gesamtlauf auf zurückgesetzter Trommel den Rückkehrcode 8; Ursache nicht untersucht. Das Testhandbuch nennt die Abweichung im Kasten „Achtung“ | offen | G5-009, Dok. 11 |
| OP-19 | **Trommeldatei wird von Testläufen verändert** (sie ist der Speicher des Rechners); für einen reproduzierbaren Lauf vorher sichern oder mit `--trommel EIGENE_KOPIE` starten | bekannt | Dok. 12 §3.1, `c8205_grafik.sh` |
| OP-20 | **E-Schritt im Eingabe-Halt:** Wird er durch H oder Kanalwechsel abgebrochen, bleibt der halbe Befehl liegen (Randfall) | bekannte Einschränkung | Dok. 08 §4 |
| OP-21 | **Handbücher auf Töne:** Der Fließtext in `erzeuge_bedienungsanleitung_pdf.py` ist außer Befehlen und `--MODUS` nicht durchgesehen; Handbücher nicht auf Töne durchgesehen (S6-05) | offen | G5-003, S6-05 |
| OP-22 | **Pult-Grafiken:** (a) richtige Grafik „BS gedrückt“ fehlt, die gelieferte zeigt ein „E“, im Fenster steht eine synthetische Fassung; (b) fünf Foto-Abgleiche unsicher (Ü, G, H, T, WM: Schätzwert Mittelpunkt + 13 px); (c) Positionen der Schlüsselschalter-Grafiken widersprechen sich um rund 20 px, beide liegen am selben Mittelpunkt; (d) gedrückte Tasten haben an manchen Stellen eine schwache Doppelkante. Blockieren nichts; Abgleich am laufenden Fenster | Hinweis | Dok. 01 §8 Nr. 2, 3, 5, 11, 12 |
| OP-24 | **Überholte Aussagen** in Dok. 01 §1.7 und §1.9, Dok. 02 §6 (§5.9, §7.5, §8.5) und Dok. 03 (§5 Nr. 9 und die Absätze „Stand 16.10.2026“ nennen „nicht eingebaut“; `tab_kurz.wav` und `tab_lang.wav` werden nicht mehr gespielt, Dok. 10 §6.3 B-1, B-2); sie fallen mit Stufe 6 weg | erledigt mit Stufe 6 | Dok. 10 §6.3; ferner Dok. 00 §3 (Zeilen „ohne Echo“, 15.10.2026; seit 18.10.2026 überholt, Dok. 09 S3-04), Stufe-3-Checkpoint U-8 |
| OP-25 | **R300-Eingabe, Klickspur und Sollfolge:** `Tests/r300_eingabe_klickspur.txt` und `Tests/r300_eingabe_soll.txt` liegen nicht im Archiv (am 19.10.2026 gelöscht, weil die Regressionsschleife sie als Tests zählte). Der echte Lauf und die Auswertung starten erst, wenn der Erzeuger sie neu anlegt. **Entschieden 19.10.2026 (Projektinhaber: „lassen“): so lassen; bei Bedarf erzeugen und danach wieder löschen.** Die vier Testskripte bleiben unverändert | entschieden, kein Eingriff | Prüfverfahren §6.5, §10 B-4 |
| OP-27 | **Ausfall des Tonstroms im Betrieb am echten Gerät** (Rückkehrcode 16 mitten im Lauf, S4-04, Dok. 10 B-5): nur der Start ohne Abspielprogramm ist an einem echten Start geprüft; der Ausfall im Betrieb wurde in der Abnahme nicht eigens gemeldet | offen | Dok. 10 B-5 |
| OP-28 | **Zeiten am Gerät nicht gemessen:** Verzögerung des Tons höchstens 50 ms, Schreibwerkzeit 70 bis 90 ms, Lesetempo 130 Zeichen/s, Stanztempo etwa 50 Zeichen/s. Belegt ist nur die Hörprüfung 2 („ok“, 19.10.2026). Ebenso nicht am Gerät geprüft: die Aufrufe von `pw-cat` und `aplay` (am Rechner des Projektinhabers lief ein Abspielprogramm; welches, ist nicht festgehalten) | Hinweis | Dok. 10 §3a (Nicht geprüft), S4-03, S4-18, §6.9 |
| OP-29 | **Bedienablauf am Pult nie durchgespielt:** Dok. 01 §1.8 Nr. 8 bis 14 (Minimalprogramm laden, Leitadressen, `01.`, `10 aaaa`) wurde in Stufe 2 nur am KEP-Beispiel geprüft; ein Beleg für den ganzen Ablauf liegt mir nicht vor. Außerdem offen aus `AENDERUNG_E_unter_M` (0.03-015): der Hinweis „H statt R“ zu Handbuch 4.4 Nr. 2 | offen | CP Stufe 2, AENDERUNG 0.03-015 |
| OP-30 | **Abgleiche, die nie stattfanden:** (a) Die Änderungen 0.03-015 (E unter M) und 0.03-016 (K0 wertet Schalter SW aus) sind nur durch Messungen belegt, nicht durch einen Vergleich der Ausgaben mit dem alten Interpreter; drei Protokolle hängen vom Trommelzustand ab (`acbz-003_AC_Ue_E_Transport`, `bsp_5_6_vordere_bits_als_adresse`, `pj2-bis_minimalprogramm`). (b) `ton/SW_Ton_Beschreibung.md` (§22 Änderungsverzeichnis) ist nicht mit Dok. 03 Nr. 11 bis 24 abgeglichen. (c) `r300_eingabe_trommel_nach_lauf.txt` (73 KB, Echtlauf F-54) wurde nie inhaltlich ausgewertet; die Datei liegt nicht im Archiv | Hinweis | AENDERUNG 0.03-015/-016, CP Stufe 3 |
| OP-32 | **Fensterlage (FL-001) und Fokus-Entprellung am echten Fenster:** Dok. 05 F-65 (b) bat um eine Prüfung unter X11 (Wandern der Position) und mit zwei Bildschirmen; eine Rückmeldung ist nicht belegt. Die Entprellung des Fokus (0,4 s, §5.7) hat in `grafik_sw_tests.py` keinen eigenen Test, den ich gefunden habe (Dok. 05 F-43; Tests für den Puffer gibt es) | Hinweis | Dok. 05 F-43, F-65 (b) |
| OP-33 | **Bedienablauf §3 Nr. 12 bis 14 gegen das BIS-Dokument:** Dok. 01 §1.8 stellte fest, dass die BIS-Dokumentation dem Paket nicht beilag und die Einzelheiten nicht geprüft sind. Sie liegt im Projekt (`Bausteininterpretiersystem BIS/markdown-dateien/C8205-Interpreter-BIS.md`) und wurde bei G6-014 **stichprobenartig** gelesen. Bestätigt: `2 K₂ aaaa` mit K₂ = 0 Relativadresse, 1 Hauptleitadresse, 2 bis 9 die 2. bis 9. Leitadresse (BIS-2.2, Kennzeichentabelle); `1 0 aaaa …` ist ein Sofortbefehl ohne Adressenänderung (BIS-2.2.11: `10 3004 000.`). **Abweichungen, nicht geklärt:** (a) das BIS-Dokument schreibt die Eingaben mit Schlusspunkt und beim Sofortbefehl mit Befehlsteil (`1 K₂ a₁a₂a₃a₄ BAZ .`); §3 Nr. 12 bis 14 und Dok. 01 zeigen die Kurzform `20 aaaa`, `10 aaaa` ohne Punkt; (b) Dok. 01 nennt `01.` einen „Befehl zur fortlaufenden Eingabe von Objektkodebefehlen“; nach BIS-2.2.3 ist `0 K₂ …` ein **einzelnes Maschinenwort** (mit Addition der Leitadresse nach K₂), und die Programmstück-Eingabe des MP wird dort mit `025 eingabeprogst` aufgerufen. Ob `01.` am Pult das Einlesen des Bandes auslöst, habe ich nicht aus dem BIS-Dokument herleiten können. **Entschieden 19.10.2026 (Projektinhaber): Die Prüfung am Pult ist nicht möglich, weil dafür ein vollständiges BIS-Minimalprogramm nötig ist; das ist nicht Gegenstand dieser Anforderung.** §3 Nr. 12 bis 14 bleibt wie in Dok. 01 festgelegt (Kurzform), ungeprüft; die Abweichungen (a) und (b) bleiben als Hinweis stehen und werden bei der BIS-Abnahme geprüft | Hinweis, außerhalb des Umfangs | Dok. 01 §1.8 Nr. 12 bis 14 und „Lesart und Grenzen“ (b) |
| OP-36 | **`CHECKPOINT_Stufe1.md` fehlt im Archiv:** Dok. 07 §4 nennt dort „Annahmen zu Leserdatei und LOCHSTREIFENKORB“. Die Datei liegt nicht vor; die Annahmen sind aus Dok. 00 §6 (Entwurf 23, 35), `grafik_geraete.py` und §7 rekonstruiert, nicht gegen die Datei geprüft | Hinweis | Dok. 07 §4 |
| OP-37 | **Lampenmittelung („ruhiges Bild“):** Fenster 40 ms, leuchtet ab 60 % Anteil „an“, dunkel bis 40 %, dazwischen bleibt der Zustand (Hysterese) ist eine Standardannahme des Entwicklers, vom Projektinhaber nicht bestätigt (§3, Dok. 01 §6.2). Das Prüfverfahren §7 enthält dafür keine Handprüfung am laufenden Fenster, obwohl §3 sie dort ansiedelt | offen | Dok. 00 §6 (Entwurf 84), Dok. 01 §1.5, §6.2 |
| OP-38 | **Versionskennung der GRAFIK-Module:** `c8205_grafik.py` trägt im Kopf `Version: G2-004` (veraltet), die Konstante `VERSION_GRAFIK` lautet `G4-003`; `grafik_k0.py` und `grafik_trommel.py` haben keine `Version:`-Zeile; eine Regel für die Zählung der GRAFIK-Module gibt es nicht (`C8205-Versionierung.md` §8, §10.3). Stufe 6 ändert keinen Code, daher unverändert | offen | Versionierung §8 |
| OP-39 | **Rechner-Thread in der Schreibwerkzeit:** Hängt der Rechner-Thread in der Schreibwerkzeit (bis 0,4 s), reagieren H und der Abbruch erst danach. Nicht erprobt (Stufe-3-Checkpoint, Stand Stufe 4). Aufgenommen bei der Triage S6-04 am 19.10.2026 | offen | CP Stufe 3 (Stufe 4, Schreibwerkzeit) |
| OP-40 | **Schreibwerkzeit und Laufzeit der GRAFIK-Tests:** Wie die Schreibwerkzeit die Laufzeit der vorhandenen GRAFIK-Tests beeinflusst, wurde nie untersucht (Hinweis Dok. 10 §6.3). Belegt ist nur, dass der Gesamtlauf durchläuft (18 von 18 Blöcken, Gleichwertigkeit `--alle` 159 s). Aufgenommen bei der Triage S6-04 am 19.10.2026 | Hinweis | CP Stufe 3, Dok. 10 §6.3 |

### 10.5 Als erledigt belegt

Punkte, die in den Anforderungsdokumenten offen standen und durch spätere Abnahmen erledigt sind. Sie bleiben hier mit Beleg, damit sie nicht als Verlust erscheinen.

| Alter Punkt | Erledigt durch | Beleg |
|---|---|---|
| Töne nicht hörbar geprüft (Stufe 2); Mischung mit späteren Tönen | Mischer `tonmisch` (Stufe 4); Hörprüfung 2 unter Linux am 19.10.2026: ok | Dok. 10 B-6 |
| Grundgeräusch: kurze Lücke beim Schleifenneustart | Grundgeräusch ist im Mischer eine Schleife ohne Neustart (G4-002) | Dok. 10 |
| Tk-Fenster lief nur beim Projektinhaber (Linux) | Tk-Lauf vom Projektinhaber als „läuft“ gemeldet (B-3 bis B-5), Stufe 4 abgenommen | Dok. 10, G5-007 |
| Vormerkung im SW-Fenster, Stau (F-35, F-36, S3-13, S3-14) | ersetzt durch den Puffer (19.10.2026, §5.5); Entscheidung 18.10.2026 07:44: keine wartenden Zeichen, Sperre bei K0 weg | Dok. 09 §6, Dok. 10 §15 |
| Freigabe zum Neuprogrammieren (Dok. 04) | Stufen 1 bis 5 umgesetzt und abgenommen, Stufe 5 am 19.10.2026 ohne Windows | Dok. 11 |
| Hörprüfung und Nachstellen der Konstanten (Dok. 03 §5 Nr. 22) | Hörprüfung 2 unter Linux: ok (B-6); Konstantenstand in §6.9 | Dok. 10 |
| OP-06 Leserpegel LL 1,3 (G4-012) | **Bestätigt 19.10.2026** („ja das ist alles ok“, auf die Frage, ob 1,3 als gewollter Wert gilt); Dok. 10 S4-19 (1,0) ist überholt | Antwort 19.10.2026 |
| OP-07 Puffer im SW-Fenster: 8 Eingaben, Ausnahme für Umschaltzeichen und Zeichen, kein Verfall | **Bestätigt 19.10.2026** (gleiche Antwort); am echten Fenster weiter nicht erprobt, `--DEBUGLOG` zeigt es an Zeilen `SW Taste … voll` | Antwort 19.10.2026 |
| OP-08 Hinweis bei gesperrter Taste (Selektor SW nicht gerastet) | **Bestätigt 19.10.2026: bleibt still, kein Hinweis** (gleiche Antwort; gelesen als „so bleibt es“) | Antwort 19.10.2026 |
| OP-12 C-Modul vorübersetzt mitliefern oder bauen | Antwort „ja das ist alles ok“ auf die Frage mit vier Punkten; eine Wahl zu diesem Punkt wurde nicht genannt. **Gelesen als: der jetzige Stand gilt** (vorübersetzte `c8205_trommel.abi3.so` liegt bei, `c-module/python/setup.py` baut sie; unter Windows ist zu bauen). Bei Widerspruch bitte sagen | Antwort 19.10.2026 |
| Testhandbuch nennt 201 Tests und die beiden r300-Dateien | `r300_eingabe_klickspur.txt` und `r300_eingabe_soll.txt` gelöscht (199 Tests); PDFs über `make_all_pdf.sh` neu erzeugt und bestätigt | Dok. 11, Dok. 04 |
| Gravis ungeprüft (Dok. 09 §5b/§5d, Vorschlag „aus S3-09 streichen“) | Handlauf F-56: am echten Fenster kommt `grave` an und wird geliefert; in der Wiedergabe nicht erzeugbar, daher `[BEKANNT]`. Keine Streichung | Dok. 09 §5d (`gravis.log`), Prüfverfahren §10 B-5 |
| `ziffern_2` bei Um. KB (Dok. 10 §16) | Kein Fehler des Interpreters; die Prüfung `grafik_sw_ende_zu_ende.py` hatte eine falsche Erwartung und wurde berichtigt (15 von 15). `ziffern_*` kennen kein Umschaltzeichen (U-12) und bleiben unverändert | Dok. 10 §16 |
| Vormerkung verfällt nicht bei Programmende (Dok. 09 B-6, `verwerfen()` nie aufgerufen) | Die Vormerkung entfiel am 18.10.2026; seit 19.10.2026 gilt der Puffer, es gibt keine Regel „Programmende“ (§5.5) | Dok. 09 §6, §11 |
| `KepUeberPult.test_kep` rot im Gesamtlauf (Dok. 09 §11 Nr. 6, Dok. 10 §12) | Gesamtlauf am 19.10.2026: 18 von 18 Blöcken bestanden (im Vordergrund; als Hintergrundauftrag scheitert der Strg+C-Test, siehe §8) | Dok. 11 A5-1 |
| `#` im Modus TEST nicht eingebbar (Dok. 09 B-4) | Eigenschaft der K0-Datei (`#` beginnt dort einen Kommentar), keine Änderung; in GRAFIK wird `#` getippt | Dok. 09 §6 |
| Flag BS wird beim Einrasten gesetzt, anders als im Dokument (CP Stufe 2, „Offen im TEST-Modus“) | Interpreter 0.03-014: `BS+` setzt nur die Schalterstellung `bs_schalter`, das Flag BS erst ein wirksamer bedingter Stopp (§3, Tabelle der Schalter) | `c8205_interp.py` Kopf, CP Stufe 2 |
| Handbuch nennt 0.03-016 nicht (A-6; AENDERUNG 0.03-016 „Frage 3 offen“) | `Python_Interpreter.md`, `Bedienpult_mit_Schaltern.md` und beide README nennen 0.03-016; PDFs neu erzeugt (A5-7) | Dok. 11 A5-7 |
| „ohne Echo“ in den Dokumenten berichtigen (U-8) | `Python_Interpreter.md` trägt den Hinweis (Echo nur im Modus TEST, in GRAFIK zeigt das SW-Fenster jedes angenommene Zeichen); Rest in Dok. 00 fällt mit Stufe 6 weg (OP-24) | Dok. 09 §10 |
| E unter M: Niederdrücken und Loslassen von E trennen (AENDERUNG 0.03-015 „Noch offen“) | umgesetzt als `E+` und `E-` (M-35, §4) | Dok. 08, Beschreibung §4 |
| HW-Check zeigt `---- ---- ---` (HW-003), `grafik_trommel.py` G2-007 gegen G2-010 | HW-Check liest über das C-Modul, wenn `einblick()` fehlt; HW-Check in Stufe 2 abgenommen | HWCHECK_HW-003 |
| Auswertung der R300-Eingabe an einem neuen Log nicht erprobt; altes Log passt nicht zur neuen Sollfolge (93 statt 92 Token) | Läufe F-55 bis F-58 mit neuer Sollfolge, Auswertung gelaufen | Dok. 09 §5b bis §5e |
| Dok. 05 Kurzliste F-01 bis F-19 und Durchgang O-1 bis O-13 | im Durchgang 16.10.2026 beantwortet (Entwurf 24 bis 93); die Antworten stehen in Anhang A und in den Abschnitten 1 bis 9 | Dok. 05 §0, §8 |
| F-35 bis F-53 (Vormerkung, Stau, Testlücken F-40, F-43, F-44, Handliste F-46, Wiedergabe F-37) | Vormerkung und Stau entfielen am 18.10.2026 (Sperre, später Puffer); Wiedergabe und Tk-Test berichtigt (SWTK-003); Handliste neu gefasst; Tests für den Puffer vorhanden (`test_puffer_*`) | Dok. 05 §9, Dok. 09 §5d, §7 |
| F-63 (Lautstärke `--TON`, Verzögerung 20 ms, Hörprüfung von Leser, Stanzer, TAB, WRZL, Eingabe) | Hörprüfung 2 unter Linux: ok (19.10.2026); `--TON` am 19.10.2026 entschieden (S4-19) | Dok. 10 §16 |
| F-39 Fokus bei geöffnetem HW-Check-Fenster („zu bestätigen“) | als bekannte Eigenschaft akzeptiert (B-5, A-4, §8.4) | Dok. 09 §6 |
| F-02 Standardannahmen Nr. 1 bis 9 (Netzablauf) | ersetzt oder bestätigt durch den Dialog zu F-14 (Entwurf 42, 43, 54) und die Entscheidungen 16.10.2026; Hochlauf und Klick im Hochlauf stehen in §3 | Dok. 05 F-02 |
| Dok. 02 §8 Nr. 1 bis 10 (gesperrte Schreibzugriffe, Beobachtungsvariable, Startlage, C-Modul mitliefern, Code 16, Startbelegung) | am 14. bis 16.10.2026 entschieden oder bestätigt („nicht widersprochen“); Nr. 6 (aktives Warten, Compiler, Tester) in OP-01 bis OP-04 | Dok. 02 §8, Dok. 05 §8 (O-7, O-8) |
| Dok. 03 §5 Nr. 12 bis 24 (Tonstrom, Ausfall, C-Modul, Stanzer, Hörprüfung) | Nr. 15 und Nr. 21 (Stanzer: 40/60 ms) sind durch 50 ms und 5 s (S4-10) ersetzt; Nr. 22 und Nr. 24 bestätigt („die anderen Punkte sind ok“, 16.10.2026); Hörprüfung 2 ok | Dok. 03 §5 Nr. 24, Dok. 10 S4-10, B-6 |
| Trommel-Testergebnisse (Dok. 02 §5), Lücke aus G6-009 | übernommen in Prüfverfahren §7.4 (Sollwerte, nicht neu gemessen) | Prüfverfahren §7.4 |
| Dok. 07 §5: Beispiellauf `kep_eingabe.txt` (BZ=2404, AC=22060635124) „nicht gegen einen Erwartungswert verglichen“ | Der Pult-Test `KepUeberPult` endet mit denselben Werten (BZ=2404, AC=22060635124), Pult-Tests 65 von 65 | Dok. 01 §1.10 Nr. 6 |
| Dok. 07 §6: Freigabe für Stufe 2 steht aus; Dokumentation für GRAFIK nicht angepasst | Stufen 1 bis 3 am 18.10.2026 abgenommen (Dok. 00 §6, Entwurf 119, 120); Anpassung der Dokumentation ist Stufe 6 selbst | Dok. 00 §6 |
| Dok. 01 §1.8 Nr. 17: `--sw-ausgabe` und Terminalausgabe in GRAFIK (Standardannahme) | Schalterliste F-13 am 16.10.2026 entschieden: `--sw-ausgabe` wirkungslos ohne Fehler (§2) | Dok. 05 F-13 |
| Dok. 01 §1.9 Nr. 5 (a): Vierergruppen von links | Test des Projektinhabers 17.10.2026, Entwurf 99 | Dok. 01 §1.9 |
| Dok. 06 M-15 bis M-35 | alle 21 Nummern kommen in §4 vor (Zählung G6-014); „Noch offen“ in Dok. 06 verweist nur auf Dok. 05 §8, das in dieser Triage gelesen ist | §4 |
| Dok. 00 §6, Vermerke „Offen:“ der Entwürfe 35 bis 140 | alle durch spätere Zeilen erledigt (F-12, F-14, F-15, F-16, F-17, F-18, Stufe 3 bis 5 abgenommen) oder oben als OP-34, OP-35 übernommen; PDFs und Testhandbuch: Dok. 11 A5-7 | Dok. 00 §6 |
| OP-23 Assemblerdokumentation sagt, die Oberfläche benutze `node.js` | **Entschieden 19.10.2026 (Projektinhaber): „aus der .odt ableiten“.** `C8205_Assembler_Dokumentation.md` neu abgeleitet (Version 1.00-008): `node.js`-Satz entfernt, `-WARN=SYS` und `spa` (neuer Abschnitt 3.3.10) übernommen, Abschnitte 3.3.11 und 3.3.12 umnummeriert, Verweise auf das Pragma auf 3.3.12 berichtigt (die .odt verweist selbst noch auf 3.3.11). **Rest:** das PDF `C8205-Assemblerdokumentation_A4.pdf` nennt `node.js` noch (nach Entscheidung 16.10.2026 unverändert); die .odt hat die falschen Verweise 3.3.11 | Dok. 01 §8 Nr. 1, Dok. 00 §6 (Entwurf 90 bis 92) |
| `AENDERUNG_E_unter_M_…0_03-015.md` und `AENDERUNG_K0_…0_03-016.md`: Inhalt nur dort; „Frage 3“ (Handbuch nennt 0.03-016 nicht) | Inhalt, Prüfung und „Nicht geprüft“ stehen in `C8205-Versionierung.md` 0.03-009, Abschnitt 10; „Noch offen: E+/E- trennen“ ist umgesetzt (M-35), „H statt R“ steht in OP-29, die drei trommelabhängigen Protokolle in OP-30 | Versionierung §10 |
| Dok. 01 §2 (Artefakte) und §3 (Element-Zuordnung): „Bitte bestätigen“ zum Netzschalter, Tabelle in §3.5 „abgeleitet, nicht bestätigt“ | Netzschalter = Schlüsselschalter bestätigt (Entwurf 81); T-SW, SP, BS, LS, Selektor SW entschieden (Entwurf 50, 71, 96); `pult-fenster/` aus §2 gibt es als Ordner nicht mehr (Stufe 2 neu programmiert), §2 ist Verlauf | Dok. 00 §6 (Entwurf 50, 71, 81), §4 |
| Dok. 00 §6, Entwurf 34 bis 114: F-11 (a) bis (f), F-12, F-13, O-1 bis O-13 | alle beantwortet; F-11 (c), (d) ohne Anforderung erledigt (Entwurf 36, 37), (e), (f) „JA“ (Entwurf 38); Rest siehe OP-34, OP-37 | Dok. 00 §6 |
| U-3, U-4, U-6 (Stufe 3): `r300_eingabe` ohne Echo, Auswertung und Handliste an die neue Eingabe-Anzeige anpassen | umgesetzt (Checkpoint 40, 41); echte Läufe F-55 und F-58 ohne Befund, Tk-Test SWTK-004: 49 OK, 1 WARNUNG (Fokus, B-5), 0 FEHLER | Dok. 09 §5b bis §5e, §10 |

### 10.6 Arbeitsvermerk Stufe 6 (entfällt nach Abschluss)

**Ausnahme für S6-12 (entschieden 19.10.2026):** `testscripte/r300_eingabe_log_auswerten.py` behält die Verweise „Dok. 09 5b“ (Kommentar und Berichtstext). Ein Berichtstext ändert die Ausgabe des Skripts; Stufe 6 ändert keinen Code. Die Suche unter A6-3 nach „Dok. 09“ meldet dort zwei Treffer, die gewollt sind. Bedeutung: Dok. 09 §5b = Prüfverfahren §6 (R300-Eingabe).

Die Triage nach S6-04 ist mit G6-014 **durchgesehen**. **Vollständig gelesen** sind Dok. 05, 06, 07 §4 bis §6, 09, 10, 11, Dok. 01 §1.8 bis §1.10, Dok. 02 §5 und §8, Dok. 03 §5, `CHECKPOINT_Stufe2.md`, `CHECKPOINT_Stufe3.md`, `CHECKPOINT_G5-001.md`, `AENDERUNG_*` und `HWCHECK_HW-003.md`; ferner durchgesehen Dok. 00 §4, Dok. 01 §4 bis §10, Dok. 04 §2 und §5, Dok. 08 §4 und die Checkpoints G5-002 bis G5-010. **Daraus kamen OP-25 bis OP-36 und die Erledigungen in §10.5.**

**Grenzen (ehrlich):** (1) **Dok. 00 §6** (alle Entwürfe 1 bis 140) und **Dok. 01 §2, §3** sind seit G6-015 vollständig gelesen; daraus kamen OP-23 (erweitert), OP-34 (erweitert) und OP-37. (2) **Dok. 06**: dass alle M-Nummern in §4 vorkommen, ist **gezählt**, nicht Satz für Satz verglichen; die Satzebene gehört zu A6-1 (Stichprobe des Projektinhabers). (3) Das BIS-Dokument wurde nur an den Stellen gelesen, die OP-33 nennt; die Prüfung von `01.` und `10 aaaa` am Pult ist entschieden außerhalb des Umfangs (OP-33). (4) Dok. 01 §4 bis §10 wurden schon früher durchgesehen (nicht in G6-015 wiederholt). (5) Versionierung (S6-03) bei G6-017 geprüft: der Interpreter hat die Builds 0.03-013 bis 0.03-017 lückenlos; für die `.md`-Dateien ist „je Änderungsschritt +1“ nicht prüfbar (keine Historie im Archiv); `projekt_C8205_1.zip` ist nicht untersucht. **„Keine weiteren offenen Punkte“ gilt für die gelesenen Quellen.** Aus Sicht der Triage ist das Löschen (S6-11) freigegeben, **erst nach** Versionierung (S6-03), Verweisen (S6-07) und Sicherung (S6-11).

### 10.7 Kennungen

| Alte Kennung | Gegenstand | Abschnitt |
|---|---|---|
| B-2 (Dok. 10), S4-15, S5-12, A5-8, O4-18 | Windows | 10.1 |
| G4-007, G4-009, G4-012, O4-17 | Puffer, Leserpegel | 10.5 |
| F-15 (a), Dok. 01 §7 Nr. 14 | Klicks im Dauerlauf | 10.3 |
| S3-06, S3-07, S3-15 | Standardannahmen Stufe 3 | 10.3 |
| G5-009, Dok. 11 „Beim Abnehmen festgestellt“ | Testbefunde | 10.4 |
| Dok. 10 B-5, S4-03, S4-18 | Tonstrom im Betrieb, Zeiten am Gerät | 10.4 (OP-27, OP-28) |
| Prüfverfahren §9 (W-2, W-5) | Windows: Bauweg, Sammellauf | 10.1 (OP-26) |
| CP Stufe 2, AENDERUNG 0.03-015/-016, HWCHECK_HW-003 | Bedienablauf, nie durchgeführte Abgleiche | 10.4 (OP-29, OP-30) |
| Dok. 02 §5.3, §8; Dok. 03 §5 | Windows-Zusätze zu OP-04, Erledigungen | 10.1 (OP-04), 10.5 |
| Dok. 05 F-64, F-65, F-43 | Rücktaste-Annahmen, Fensterlage, Fokus-Entprellung | 10.3 (OP-31), 10.4 (OP-32) |
| Dok. 01 §1.8 Nr. 12 bis 14, BIS-Dokument | Schreibweise und Bedeutung von `20 aaaa`, `01.`, `10 aaaa` | 10.4 (OP-33, außerhalb des Umfangs) |
| Dok. 00 §6 (Entwurf 35), Dok. 06 M-21, M-34 | Leser-Gleichstand, Pult-Auslegungen | 10.3 (OP-34, OP-35) |
| Dok. 07 §4 | `CHECKPOINT_Stufe1.md` fehlt | 10.4 (OP-36) |
| Dok. 00 §6 (Entwurf 84), Dok. 01 §6.2 | Lampenmittelung | 10.4 (OP-37) |
| Versionierung §8, §10.3 | Versionskennung der GRAFIK-Module | 10.4 (OP-38) |
| CP Stufe 3 (Schreibwerkzeit), Dok. 10 §6.3 | Rechner-Thread in der Schreibwerkzeit, Testlaufzeit | 10.4 (OP-39, OP-40) |

## 11 Aufbau der GRAFIK-Module

Dieser Abschnitt erklärt kurz, **warum** es neben `c8205_interp.py` den Treiber `c8205_grafik.py`, den Ordner `grafik-interpreter-module/` und den Ordner `c-module/` gibt, und was in welcher Datei steht. Entscheidung O6-4: ein kurzer Abschnitt, kein Parallelkapitel. Die Dateiliste ist aus den Kopfkommentaren der Dateien gelesen; das Verhalten habe ich nicht geprüft.

### 11.1 Warum eine zweite Programmfamilie

`c8205_interp.py` ist ein **Stapelbetrieb**: erst die Tastenfolge einer Testdatei, dann die Knotenschleife bis zum Halt, dann die Ergebnisprüfung (Dok. 04 §2.2). GRAFIK ist **ereignisgesteuert**: Klicks am Pult, ein laufender Rechner, Halt heißt Warten. Das ist kein Austausch einzelner Klassen, sondern ein neuer Treiber. Damit TEST unverändert bleibt, liegt GRAFIK in neuen Dateien, die `c8205_interp.py` als Bibliothek nutzen (`load_graph`, Tabellen, `FUNCS`, `Machine`, `Leser`, `Stanzer`). Die Auswahl trifft allein `--MODUS` (§1, §2); der Interpreter ruft bei `GRAFIK` `c8205_grafik.hauptprogramm()` auf (`c8205_interp.py` 0.03-017).

### 11.2 Schichten

| Schicht | Dateien | Aufgabe |
|---|---|---|
| Interpreter (beide Modi) | `c8205_interp.py` | Knotenautomat für TEST, Tabellen, `Machine`; Modus-Weiche `--MODUS` |
| Treiber GRAFIK | `c8205_grafik.py` | Rechner im Dauerbetrieb, Tastenlogik mit dauerhaftem Zustand, Start der Fenster und Töne, Abbruch |
| Logik ohne Tk | `grafik_pult.py`, `grafik_sw.py`, `grafik_k0.py`, `grafik_haltzeit.py`, `grafik_schreibwerk.py`, `grafik_geraeteton.py`, `grafik_tastatur.py` | testbar ohne Fenster und ohne Audiogerät |
| Tk-Schicht | `grafik_pult_fenster.py`, `grafik_sw_fenster.py`, `grafik_hwcheck.py`, `grafik_fensterlage.py` | Zeichnen, Maus, Computertastatur, Fenster merken; ein Tk-Prozess, zwei Fenster |
| Geräte | `grafik_geraete.py`, `grafik_trommel.py` | Leser und Stanzer als Ordner, Trommel über das C-Modul |
| Töne | `grafik_tonmisch.py` (Rückfall), `grafik_tonmisch_c.py`, `grafik_rechnerton.py`, `grafik_ton.py` (Stufe 2) | Mischer und Rechnertöne |
| Fehlersuche | `grafik_debuglog.py` | `--DEBUGLOG` |
| C-Module | `c-module/` (`trommel.c`, `bahnsperre.c`, `unterbrechung.c`, `tonmisch.c`, `plattform.h`), Erweiterungsmodul `c-module/python/c8205_trommel_modul.c` | echte Trommel mit Koinzidenz, Bahnsperren, Abbruch, Tonmischer; statisch in **ein** Erweiterungsmodul gebunden (abi3) |

Die Trennung „Logik ohne Tk“ und „Tk-Schicht“ gilt, damit die Logik in der Entwicklungsumgebung ohne Anzeige geprüft werden kann (Dok. 09, Dok. 10; Prüfverfahren §2).

### 11.3 Was man wissen muss

- **Kopie statt Herauslösen (Punkt 18):** `exec_node` und `run_e` sind in `c8205_grafik.py` **Kopien** der verschachtelten Funktionen aus `lauf()` in `c8205_interp.py`. Jede Änderung am Knotenablauf ist in beiden Fassungen nachzuziehen; die Gleichwertigkeit von TEST und GRAFIK (ohne Zeiten) prüft `testscripte/grafik_gleichwertigkeit.py` (Prüfverfahren §4). Entschieden war „erst kopieren, nach bestandenen Tests herauslösen“; nach dem Kopfkommentar von `c8205_grafik.py` stehen die Kopien noch.
- **Zwei Zählungen:** `c8205_interp.py` zählt `0.03-0xx`, die GRAFIK-Module zählen je Datei eigene Kennungen (G1-, G2-, … G4-, FL-, HW-, HZ-, DL-). Die Zählung der GRAFIK-Module soll in `C8205-Versionierung.md` ergänzt werden (S6-03, noch nicht geschehen).
- **Rechnerische Wartezeit bleibt:** Die Knoten 040/041 behalten ihre rechnerische Schleife; die echte Trommel liefert Daten und Echtzeit (Punkt 13, Dok. 04).
- **Modulpfad:** `c8205_grafik.py` setzt `grafik-interpreter-module/` selbst in den Suchpfad; Start über `c8205_grafik.sh`/`.bat` oder `python3 c8205_interp.py` (Standard `GRAFIK`).
- **TEST nicht umgebaut:** Nach Dok. 04 §6 blieb TEST bis Stufe 5 unberührt; `--MODUS` kam mit Stufe 5 (0.03-017). Ob die Änderungen 0.03-015 und 0.03-016 den TEST-Zweig berühren, habe ich nicht geprüft.

### 11.4 Kennungen

| Alte Kennung | Gegenstand | Abschnitt |
|---|---|---|
| Dok. 04 §2 bis §4, O6-4 | Modulbefunde, Aufteilung | 11.1, 11.2 |
| Punkte 13, 18 (Dok. 04 §5) | Wartezeit, Kopie von `exec_node`/`run_e` | 11.3 |
| G1-xxx bis G4-xxx, FL-, HW-, HZ-, DL- | Modulversionen | 11.2, 11.3 |

## Anhang A Entscheidungsregister

Die 114 Zeilen aus Dokument 00 §2, **unveränderte Nummern und Daten, unveränderter Wortlaut** (O6-2). Die Spalte „Dokument“ nennt die alten Dokumentnummern; Anhang B.1 ordnet sie den neuen Abschnitten zu.

<!-- REGISTER-ANFANG: 114 Datenzeilen, Kopf und Trenner zählen nicht mit -->
| Datum | Entscheidung | Dokument |
|---|---|---|
| 13.10.2026 | Abb. 3 und 4 als interaktive Grafik in separatem Fenster; als Layout dient das **Foto (Abb. 2)** | 01 |
| 13.10.2026 | Fensterhöhe etwa **860 px**; Grafik vorher auf diese Höhe skalieren (1148 × 860) | 01 |
| 13.10.2026 | Teilgrafiken je Bildelement (gedrückt/losgelassen, hell/dunkel) werden vom Projektinhaber geliefert | 01 |
| 13.10.2026 | Die vier **unbeschrifteten unteren Selektortasten** werden nie gedrückt: entfallen | 01 |
| 13.10.2026 | **Rot/grün nur für Lampen B und N**; gestartetes Skript = Rechner eingeschaltet = grün | 01 |
| 13.10.2026 | Klick auf Netzschalter: **B rot, 2 Sekunden Anzeige, dann beendet sich das Skript komplett** *(B-Farbe ersetzt am 16.10.2026: B wird dunkel, siehe Eintrag „Hochlauf, KEP, Abbruch im Hochlauf“)* | 01 |
| 13.10.2026 | Die **Trommel soll echter werden**: Zugriffe laufen über die hochgeladenen C-Module | 02 |
| 13.10.2026 | Das Modul merkt sich die **aktuelle Zelle** (wechselt alle **104 µs**) und führt Lese-/Schreibanforderungen nur aus, wenn diese Zelle gerade die aktuelle ist; deshalb **selbständiger Hintergrundprozess** (umgesetzt als Hintergrund-Thread im Python-Prozess; falls ein eigener Prozess gemeint war, weicht das ab, Rückfrage offen) | 02 |
| 13.10.2026 | **Dateiformat:** Das Modul wird auf das Format der Interpreter-Trommeldatei (18 Byte je Zeile) umgestellt | 02 |
| 13.10.2026 | **„Schlitz ist Schlitz“:** Ist eine Sektornummer aktuell, dann für die ganzen 104 µs (digital). Trifft in dieser Zeitspanne eine Anforderung ein, wird sie bedient. (Gewohnheit/Ungenauigkeit des Simulators, bewusst so festgelegt.) | 02 |
| 13.10.2026 | **Betriebsart:** Die echte Trommel läuft **immer**, außer beim **Claude-Interpreter**. **Eingeschränkt am 15.10.2026:** nur im Modus `--MODUS=GRAFIK`; im Modus `--MODUS=TEST` gibt es keine echte Trommel und kein C-Modul (siehe 3.6) | 02, 00 (3.1, 3.6) |
| 13.10.2026 | **Zielsysteme: Linux und Windows** | 00 (3.2), 02 |
| 13.10.2026 | Die Frage nach dem **Lampentempo** (Echtzeitausgabe von AR) war zurückgestellt; **aufgehoben 16.10.2026** (Review F-07), Entscheidung siehe Zeile „Tempo in GRAFIK“ weiter unten | 01 (6.2) |
| 14.10.2026 | **Strg+C:** Wird der Interpreter mit Strg+C unterbrochen, wird auch das C-Modul beendet (gilt nur im Modus GRAFIK; im Modus TEST gibt es kein C-Modul) | 02 |
| 14.10.2026 | **Bibliothek:** Eine statische Bibliothek ist denkbar; ist das C-Modul nicht ladbar, gibt es eine **Fehlermeldung und der Interpreter beendet sich** (kein Rückfall). Umsetzung: Python-Erweiterungsmodul mit fest eingebundenen C-Modulen (Dokument 02, Abschnitt 4.5). Gilt nur im Modus GRAFIK | 02 | 
| 13.10.2026 | Die Dokumentation wird **aufgespalten** (Hauptdokument, Trommel, Bedienpult; weitere können folgen) | 00 |
| 15.10.2026 | **Der Interpreter läuft erst, wenn Lampe B auf grün schaltet.** | 03, 01 (5) |
| 15.10.2026 | **Einschalten:** Klick auf den Netzschalter → B rot → `fade_in` läuft → B grün. (Weicht vom bisherigen Start mit B und N grün in Dokument 01 ab.) | 03, 01 (5) |
| 15.10.2026 | **Betriebsmodi:** Der Python-Interpreter soll die zwei Modi **`--MODUS=TEST`** und **`--MODUS=GRAFIK`** haben | 00 (3.6), 01 (1.6), 02, 03 |
| 15.10.2026 | **`--MODUS=TEST`** ist der bisherige Stapelbetrieb **ohne** Pult-Fenster, **ohne** Töne (also auch ohne die Wartezeit des Hochlaufs), **ohne** die C-Module der Trommel und **ohne** das interaktive Eingabefenster für das SW | 00 (3.6), 01, 02, 03 |
| 15.10.2026 | **SW-Fenster:** Das bisherige Fenster „SW Ausgabe“ (`--SW-TERMINAL`) gibt es nur im Modus TEST. Im Modus GRAFIK erscheint ein dazu **analoges Fenster**, das nur SW-Eingaben und -Ausgaben darstellt und **immer auch die SW-Eingabe übernimmt**; es wird aufgeblendet, wenn der Interpreter im Modus GRAFIK am Terminal gestartet wird, und verschwindet, wenn das Programm endet | 00 (3.6), 01 (1.6) |
| 15.10.2026 | **Vorgehen:** Nach einer Prüfung bleibt der bisherige Interpreter für TEST **unverändert**; für GRAFIK werden die betroffenen Module **neu programmiert**, danach wird nur noch umgeschaltet | 00 (3.6), 02 |
| 15.10.2026 | **SW-Fenster in GRAFIK, Aussehen:** genau wie das bisherige Fenster „SW Ausgabe“: 130 × 36 Zeichen, Markieren und Kopieren; **ohne Echo: Tastatureingaben sind nirgends zu sehen, auch nicht in Dunkelgelb** (Berichtigung 16.10.2026, Entwurf 88) **[überholt am 18.10.2026, Entwurf 104: das SW-Fenster zeigt jedes angenommene Zeichen selbst an, Dok. 09 S3-04 neu]** | 00 (3.6), 01 (1.6) |
| 15.10.2026 | **Eingaben in GRAFIK:** SW-Eingaben erfolgen im SW-Fenster, wenn der Rechner im Eingabe-Halt-Befehl steht, **Kanal K0 angewählt** und der Schalter **SW** gedrückt ist (Kanal von „Kanal 2“ auf K0 mit Schalter SW **berichtigt**, 3.6 Punkt 9). **Alle Eingaben des K0 (Pult-Tastatur) erfolgen mit Klicks im interaktiven Bedienpult.** Bei Eingabe-Halt unterscheidet T-SW also zwischen dem interaktiven Bedienpult (T) und dem interaktiven SW-Fenster (SW) | 00 (3.6), 01 (1.6) |
| 15.10.2026 | **Kein Testdokument in GRAFIK:** Es gibt kein Test-Anforderungs-Dokument (Testdatei), daher keine Makros (z. B. `#STARTE`) und kein bisheriges Testprotokoll. Wortlaut des Projektinhabers: „bei TEST“; als GRAFIK gelesen (**bestätigt**, 3.6 Punkt 10) | 00 (3.6) |
| 15.10.2026 | **X am SW-Fenster** (Modus GRAFIK) ist wie **Abbruch mit Strg+C**: der Interpreter und das C-Modul beenden sich (Entscheidung vom 14.10.2026 gilt) | 00 (3.6), 01, 02 |
| 15.10.2026 | **Lage in GRAFIK:** drei getrennte Fenster, nichts eingebettet: das Terminal, daneben das Bedienpult, daneben darunter das SW-Fenster | 00 (3.6), 01 (1.6) |
| 16.10.2026 | **Bildschirm in GRAFIK (Review F-05):** Zielbildschirm **1920 × 1080**; Pult in **fester Größe 1148 × 860 px, nicht skaliert**; Pult- und SW-Fenster dürfen sich **überlappen, wenn der Platz fehlt**. Lage der Fenster sonst wie am 15.10.2026 (keine Pixelvorgabe) | 00 (3.6), 01 (1.6, 8), 05 |
| 15.10.2026 | **`--SW-TERMINAL` im Modus GRAFIK:** wird ohne Fehlermeldung ignoriert (der Schalter kann ohnehin nur beim Aufruf des Interpreters mitgegeben werden) | 00 (3.6) |
| 15.10.2026 | **Geräte-Schalter in GRAFIK:** nur `--leser1`, `--leser2`, `--stanzer1`, je nur ein Pfad (Leser: Ordner mit nachrückenden Lochstreifendateien, gelesene wandern in `LOCHSTREIFENKORB`, siehe Register unten); `--k0`, `--sw-ausgabe`, `--NO-TERMOUT`, `--zwischenablage` wirkungslos ohne Fehler | 00 (3.6) |
| 15.10.2026 | **Programmquelle in GRAFIK:** Objektprogramm-Lochstreifen über Leser 1/2 mit dem Minimalprogramm (Befehlseingabe zur laufenden Speicherung); danach Start durch einen Sofortbefehl am Bedienpult | 00 (3.6), 01 |
| 15.10.2026 | **Terminal in GRAFIK:** zeigt gegebenenfalls nur Fehlermeldungen | 00 (3.6) |
| 15.10.2026 | **Standardmodus:** Ohne `--MODUS` gilt **GRAFIK**; bisherige Stapelaufrufe brauchen künftig `--MODUS=TEST` | 00 (3.6) |
| 15.10.2026 | **Unbekannter Modus** (z. B. `--MODUS=XYZ`): Fehlermeldung, Rückkehrcode 16, kein Start | 00 (3.6) |
| 15.10.2026 | **Fehlerfälle in GRAFIK:** Tkinter oder Anzeige fehlt → Fehlermeldung, Rückkehrcode 16, Beenden; C-Modul nicht ladbar → Rückkehrcode 16 (bestätigt) | 00 (3.6), 01, 02 |
| 15.10.2026 | **Einzelschalter in GRAFIK:** nur `--STUMM` (Töne aus, dann auch keine Hochlaufwartezeit); `--PULT-FENSTER` entfällt (ersetzt durch `--MODUS=GRAFIK`); `--BASP` wirkt in GRAFIK über das C-Modul | 00 (3.6), 01, 02, 03 |
| 15.10.2026 | **Claude-Interpreter:** arbeitet nach den Regeln des Modus TEST | 00 (3.1, 3.6) |
| 15.10.2026 | **Prüfung der betroffenen Module:** durch Claude als nächster Schritt, nur lesend; Prüfbericht als Dokument 04; danach Freigabe durch den Projektinhaber | 00 (3.6), 04 |
| 15.10.2026 | **X** am Pult-Fenster wie am SW-Fenster: Abbruch wie Strg+C (so gelesen; ersetzt für GRAFIK die Annahme „X = Netz-Aus“ des Prototyps) | 00 (3.6), 01 (7, Punkt 4) |
| 15.10.2026 | **Eigener Zweig für GRAFIK:** Für alle betroffenen Teile des Python-Programms wird im Modus GRAFIK ein eigener Zweig angefertigt, wenn eine unveränderte Nutzung nicht möglich ist; TEST bleibt unverändert. Daraus (so gelesen): Punkt 13 des Prüfberichts (rechnerische Wartezeit der Knoten 040/041 gegen die echte Trommel) und Punkt 18 (`exec_node`/`run_e` für GRAFIK kopieren) sind erledigt; der Knotengraph in der Doku bleibt gemeinsam | 04 (5), 00 (3.6) |
| 15.10.2026 | **Trommel in GRAFIK „immer so wie sie ist“:** keine Vorbelegung und kein Eingriff des Interpreters in die Trommeldatei. **Die Trommeldatei wird unverändert übernommen; was darin steht, ist die Startbelegung (Präzisierung 15.10.2026, ersetzt den Nachsatz „das KEP muss schon in der Datei stehen“). Hinweis: Für einen Kaltstart muss die Datei ein lauffähiges Minimalprogramm enthalten; das KEP braucht man nach BIS-2.1 nur, um das MP erstmals zu laden** (Punkt 17 des Prüfberichts erledigt) | 04 (5), 02 |
| 15.10.2026 | **Gemeinsame Trommeldatei:** TEST und GRAFIK nutzen dieselbe `virtuelle_Geraete/Trommel/trommel.txt` (kein eigener Dateiname für GRAFIK). Folge: Jeder TEST-Lauf schreibt in die Datei, die GRAFIK als Startbelegung übernimmt; ein Schutz gegen gleichzeitigen Zugriff von TEST und GRAFIK ist nicht vorgesehen | 02 (8, Punkt 9), 00 (3.6) |
| 15.10.2026 | **Standard von `--BASP` in GRAFIK:** Ohne Angabe gilt `000000` (wie im Interpreter), also ist Spur 0 ungeschützt; geschützt wird nur auf ausdrückliche Angabe von `--BASP`. **Ersetzt 16.10.2026 (Entwurf 86): Ohne Angabe gilt die Stellung aus der Schalterdatei neben der Trommel; fehlt sie, wird sie mit `000000` angelegt (siehe Zeile unten, O-9).** | 02 (6), 00 (3.6) |
| 15.10.2026 | **`--trommel PFAD`** gilt für TEST und GRAFIK; ohne Angabe gilt die gemeinsame `virtuelle_Geraete/Trommel/trommel.txt` | 02, 00 (3.6) |
| 15.10.2026 | **Verhalten der Leser in GRAFIK (entschieden 15.10.2026):** Für Leser 1 und 2 wird je **ein Pfad** angegeben, der nach dieser Beschreibung ein Ordner ist, in dem Lochstreifendateien erscheinen (bestätigt). Liegt ein Eingabe-Halt-Befehl für den Kanal Leser 1 bzw. Leser 2 vor, wartet der Leser **mit leuchtender Lampe E**, bis im Pfad eine Lochstreifendatei vorhanden ist; er prüft das **aktiv**. Ist das Ende einer Datei erreicht und der Eingabe-Halt noch aktiv, wird eine eventuell vorhandene **zweite Datei** (usw.) genommen, andernfalls wird gewartet. Liest der Rechner nicht alle Zeichen einer Datei, bleibt der Leser **an dieser Stelle stehen**; ein späterer Eingabebefehl liest dort weiter. Streifenwechsel im Betrieb ist damit durch Ablegen weiterer Dateien im Pfad möglich. **Reihenfolge und Verbleib (entschieden 15.10.2026):** Mehrere Dateien werden in der **zeitlichen Reihenfolge ihres Zeitstempels** genommen. Gelesene Dateien bleiben **nicht** im Ordner liegen, sie werden in den Unterordner **`LOCHSTREIFENKORB`** verschoben, der bei Bedarf anzulegen ist (bestätigt 15.10.2026: ältester Zeitstempel zuerst, Änderungszeit, Verschieben sobald das Dateiende gelesen ist; eine nicht zu Ende gelesene Datei bleibt liegen) | 00 (3.6, Punkt 11), 04 (2.4) |
| 16.10.2026 | **Leser in GRAFIK, Ergänzung (Review F-11 (e), (f), entschieden 16.10.2026):** Nach Netz-Aus bleibt eine teilgelesene Datei im Leserordner liegen und wird beim nächsten Start von vorn gelesen (entspricht dem Neustart des Rechners). Zeigen `--leser1` und `--leser2` auf denselben Ordner, ist das ein Startfehler (Konfigurationsfehler, Code 16). | 00 (3.6, Punkt 11), 04 (2.4), 05 (F-11) |
| 16.10.2026 | **Stanzer in GRAFIK (Review F-12, entschieden 16.10.2026):** Der Stanzer legt seine Datei an, wenn er nach dem Start des Interpreters zum ersten Mal zu schreiben beginnt und im Stanzerordner noch keine Datei liegt; Standardname **`stanzer.ls`**. Gibt es die Datei bereits, wird sie **fortgeschrieben** (angehängt), nie überschrieben. Der Stanzerpfad `--stanzer1` ist danach ein Ordner (aus der Antwort abgeleitet, nicht gesondert bestätigt). Abweichung vom heutigen Interpreter, der die Datei `stanzer-ausgabe.txt` beim ersten Zeichen jedes Aufrufs überschreibt; in TEST bleibt es beim heutigen Verhalten (Standardannahme). | 00 (3.6, Punkt 11), 04 (2.5), 05 (F-12) |
| 16.10.2026 | **Standardordner der Geräte in GRAFIK (Review F-12, entschieden 16.10.2026):** In GRAFIK sollen `--leser1`, `--leser2` und `--stanzer1` angegeben werden. Fehlt ein Schalter, gilt der Standardordner aus dem Ordner `virtuelle_Geraete/` (Projektstruktur, `C8205-Projektstruktur.md`): `Leser1/`, `Leser2/` bzw. `Stanzer1/`; die Lage dieser Ordner wie bei der Trommel (Vorgabepfad neben dem Skript, aus der Projektstruktur abgeleitet, nicht gesondert bestätigt). Damit gibt es in GRAFIK keinen Stanzbefehl ohne Stanzerordner; die Frage entfällt. | 00 (3.6, Punkt 11), 04 (2.5), 05 (F-12) |
| 16.10.2026 | **Schalterliste in GRAFIK (Review F-13, entschieden 16.10.2026):** Für GRAFIK gelten genau die Schalter `--MODUS`, `--leser1`, `--leser2`, `--stanzer1`, `--trommel`, `--STUMM` und `--BASP`; dazu `--mdverz`, weil der Graph ohne das Verzeichnis der Knotendoku nicht geladen werden kann. Alle anderen Schalter des Interpreters (u. a. `--out`, `--knotentest`, `--pruefe-*`, `--version`, `--k0`, `--sw-ausgabe`, `--NO-TERMOUT`, `--zwischenablage`, `--SW-TERMINAL`) sind in GRAFIK wirkungslos und ohne Fehler; das positionale Argument `tests` entfällt. Die Aliasse `--lochbandleser1/2` und `--lochbandstanzer1` sind in der Vorschlagsliste nicht genannt und damit in GRAFIK wirkungslos (nicht gesondert besprochen). Der entfallene `--PULT-FENSTER`, die Groß-/Kleinschreibung des Modus-Werts und `--STUMM`/`--BASP` in TEST wurden nicht gesondert besprochen; es bleibt beim heutigen Verhalten. | 00 (3.6, Punkt 11), 04, 05 (F-13) |
| 15.10.2026 | **Rollensperre und Entriegelung** (Erklärung des Projektinhabers): Rollensperre bedeutet nur Sperren. Die Taste R löst sie aus, danach ist keine andere Taste der Gruppen mit Rollensperre bedienbar, nur H hebt sie auf; R verriegelt gleichzeitig die Eingabetasten. Nicht betroffen: K0 bis K3, ST, BS, SP, LS. Steht in `C8205-Interpreter-Bedienpult_mit_Schaltern.md` (0.03-007) und im PDF. **Entriegelung entschieden (Antwort B):** Die Eingabetasten werden durch einen aufgestellten Eingabe-Halt-Befehl entriegelt, auch bei R. **T-SW (entschieden 16.10.2026, Entwurf 49):** Der Schalter T-SW (Tasten T und SW, `SW_umschalt`) unterliegt **nicht** der Rollensperre; die Ableitung vom 16.10.2026 (Review F-06, „ja“) ist ersetzt. Nicht betroffen sind damit K0 bis K3, ST, BS, SP, LS, der Selektor SW und T-SW | 01 (1.7, 3.5, Punkt 7) |
| 16.10.2026 | **Schalter T, SW, `SW_umschalt` (Review F-06):** Logisch ein Schalter T-SW mit den Stellungen T und SW; Bedienstellen im Fenster: Tasten T und SW (Tastatur, gegenseitig verriegelt) und `SW_umschalt` oben rechts (wechselt die Stellung). **Berichtigt in Entwurf 50:** T-SW ist eine Wippe aus nur den zwei Tasten T und SW; `SW_umschalt` ist der Selektor SW. Stellung SW → Flag SW := 1, T := 0; Stellung T → SW := 0, T := 1. Aus der Pult-Doku abgeleitet, nicht ausdrücklich bestätigt; Tabelle in Dokument 01, Abschnitt 3.5. **Entwurf 49:** keine Rollensperre für T-SW (entschieden); der **Selektor SW** rechts außen ist ein eigener Selektor (unterdrückt die SW-Ausgabe) | 01 (3.5), 05 |
| 16.10.2026 | **Tempo in GRAFIK (Review F-07, aus den Unterlagen abgeleitet, nicht ausdrücklich bestätigt):** Rückstellung aufgehoben. **Zielwert ist das Originaltempo** des C 8205 (Interpreter-Doku „Überblick und Gesamtaufbau“, Abschnitt 5): Einzelbefehl bei zeitoptimaler Lage 5 Wortzeiten (0,52 ms, rund 1900 Befehle/s), Organisationsbefehl 4 Wortzeiten (0,42 ms, rund 2400/s), Gruppen- und Wiederholungsbefehle bis rund 9000/s. Es wird **nicht künstlich gebremst** und es gibt keinen Takt-Schalter: Das Tempo ergibt sich aus der echten Trommel (Wartezeit 0 bis 31 Wortzeiten zu 104 µs, mittlere Zugriffszeit 1,67 ms) und dem Python-Tempo der Phasen ohne Trommelwartezeit. Die Geräte behalten ihr Originaltempo (Leser 130 Zeichen/s, Stanzer 50 Zeichen/s, Schreibwerk 10 Zeichen/s; Dokument 03; ob das auch bei `--STUMM` gilt, regelt F-17). **Lampen:** Im Dauerlauf R zeigt das Pult höchstens alle 40 ms den jeweils letzten Zustand (Weg 2 aus Dokument 01 Abschnitt 6.2); bei jedem Halt und nach jedem E-Schritt sofort den Stand. Kein abgestuftes Nachleuchten (Weg 3, keine dritte Lampengrafik); **ergänzt in Entwurf 84: ruhiges Lampenbild** (Zeile „Lampenbild ruhig“). **Abnahme (Standardannahme, nicht bestätigt):** Messung auf dem Zielrechner im Dauerlauf R mit einem Programm aus zeitoptimal gelegten Einzelbefehlen; erwartet werden mindestens 90 % von 1900 Befehlen/s. Braucht Python je Phase länger als eine Wortzeit, verlängern sich die Trommelwartezeiten (Dokument 02 §7); das ist hingenommen, es gibt dazu weder Eingriff noch Meldung. | 01 (1.5, 6.2), 02 (7), 05 |
| 16.10.2026 | **Rückkehrcodes und Beenden in GRAFIK (Review F-08, entschieden 16.10.2026 mit „ja“ zum Vorschlag):** **Netz-Aus** (Schlüsselschalter, 2 s Auslauf) → Code **0**. **X** am Pult- oder SW-Fenster und **Strg+C** → Code **8** (wie Strg+C in TEST). Ein **Fehler, bei dem der Rechner hält** (z. B. Stub, nicht nutzbares Gerät) und der danach per X beendet wird → **8**. **Start- und Konfigurationsfehler** (Tkinter oder Anzeige fehlt, C-Modul nicht ladbar, fehlerhafte Trommeldatei, unbekannter Modus, **kein Abspielprogramm oder Audiogerät ohne `--STUMM`**, Entwurf 55) bleiben **16**. Die Codes 0, 4 und 6 der Testauswertung (`Prüfungen:`) entfallen in GRAFIK, weil es dort keine Testdatei gibt. **Aufräumen** bei Netz-Aus, X und Strg+C: Stanzer-, SW- und Trommeldatei werden geschlossen, beide Fensterprozesse und das C-Modul beendet; Netz-Aus endet kontrolliert an einer Knotengrenze, X und Strg+C lösen `KeyboardInterrupt` sofort aus und räumen im `finally` auf (gleiches Aufräumen, anderer Zeitpunkt). Bei **hartem Ende** (kill, Absturz) beenden sich die Fensterprozesse selbst, sobald ihre Verbindung zum Interpreter wegfällt (Standardannahme zu diesem letzten Satz). | 00 (3.6), 01 (7 Nr. 2, 8 Nr. 8), 04 (Punkt 14), 05 |
| 16.10.2026 | **Lampe R und „AR“-Lampen (Review F-09 und F-10, entschieden 16.10.2026):** **Lampe R leuchtet, wenn der Schalter R gedrückt ist** (Flag H = 0; H und R sind gegeneinander verriegelt, es ist immer genau eine der beiden Tasten gedrückt, Lampe R = nicht Lampe H). Ein Haltgrund (US, BS, FÜ, FE, E, A) ändert daran nichts. Es gibt kein eigenes Flag R, die Lampe wird aus `m.fl['H']` abgeleitet. Meine Fassung vom selben Tag („es gibt keine Lampe R“) beruhte auf einem Missverständnis und ist berichtigt; der Vorschlag „leuchtet nur ohne Haltgrund“ bleibt verworfen. **Die unteren Lampen „AR“ zeigen den Adreßteil des Befehlsregisters, `m.adr`** (Schreibweise im Text: „Adreßteil des BR (Lampenreihe ‚AR‘)“, nicht zu verwechseln mit dem Register `m.AR`). Hinweis: Die Datenstruktur-Doku (Abschnitt Anzeige des Arbeitszustands) sagt, im Zustand „Rechnen“ dürfe von den Lampen H, R, US, BS, FÜ, FE, E und A nur R leuchten; das entspricht der Regel nur, solange kein Haltgrund besteht. Maßgeblich ist die Entscheidung des Projektinhabers (Lampe R = Schalter R gedrückt) | 01 (3.1, 3.2, 7 Nr. 5 und 6), 05 |
| 15.10.2026 | **`--BASP` in GRAFIK** wird als Erstes an das Trommelmodul gemeldet (vor dem ersten Zugriff), damit das Modul bei allen Schreibzugriffen des Knotengraphen darauf zurückgreift. Format nach `Magnettrommel.md`: `--BASP=abcdef`, links nach rechts Hauptschalter 0001, 0040, 0100, 0200, 0400, 1000, 1 = EIN. (Im Chat als `--BSP=111000` geschrieben, als Tippfehler gelesen, **bestätigt 15.10.2026: Name `--BASP`**) | 02 (6), 00 (3.6) |
| 15.10.2026 | **Bedienung des Pults per Klick:** Tasten wie 0, 1, + und B, ebenso E, M und G, zeigen nach dem Klick 0,4 s (einstellbar) die gedrückte Grafik und gehen dann in den Ausgangszustand zurück; Schalter (z. B. H, SW, K1) rasten ein und zeigen einen anderen Grafikzustand. Das **Tastenverhalten selbst** (Sperren, Verriegelungen) steht in `C8205-Interpreter-Bedienpult_mit_Schaltern.md` und wird hier **nicht doppelt beschrieben** | 01 (1.7, 7) |
| 15.10.2026 | **Halter für M und E (E bestätigt 15.10.2026):** Umschalt-Klick auf M oder E hält die Taste (Grafik dauerhaft gedrückt, die Maus muss nicht gehalten werden); bei gehaltenem M ist E mehrfach klickbar (je 0,4 s), bei gehaltenem E ist G klickbar („E halten, G drücken“); ein weiterer Umschalt-Klick löst die Taste und die Grafik geht in die Ausgangslage zurück | 01 (1.7) |
| 15.10.2026 | **Prüfbericht Punkt 14 und 19 (Antwort „ja“):** Fehler in GRAFIK (`Stub`, `LaufFehler`, `KonfigFehler`): Der Rechner hält, die Meldung erscheint im Terminal, beendet wird nur durch X, Strg+C oder Netzschalter (14). K0-Quelle: T nur vom Pult, SW nur vom SW-Fenster, die andere Quelle wird ignoriert (19) | 04 (5) |
| 15.10.2026 | **Prüfbericht Punkt 15 und 16 (Ausführung dem Entwickler überlassen):** Vorhanden sind nur das Terminal, zwei Fenster und die C-Module der Trommel als selbständiger Hintergrundprozess. X löst den Abbruch durch eine Meldung vom Fenster an den Interpreter aus, der Interpreter führt den Strg+C-Abbruch selbst aus (plattformneutral); Pult und SW-Fenster laufen in einem gemeinsamen Tk-Prozess mit zwei Fenstern; das SW-Fenster erhält bei erwarteter Eingabe den Fokus | 04 (5), 01 (1.7) |
| 16.10.2026 | **Startzustand in GRAFIK (Review F-01, Schritt 1):** Das Skript startet mit **ausgeschaltetem Rechner**: Schlüsselschalter „aus“, alle Lampen dunkel (auch B und N), das Pult wartet auf den Klick auf den Netzschalter. Danach Hochlauf (B rot → `fade_in` → B grün); der Interpreter läuft erst bei B grün. Ersetzt für GRAFIK die frühere Annahme „gestartetes Skript = eingeschalteter Rechner, B und N grün“ (Dokument 01, 1.3) | 01 (1.3, 5, 7), 03 (3, 5), 05 (F-01) |
| 16.10.2026 | **Zustand des Pults vor dem Einschalten (Review F-14, Dialog, entschieden 16.10.2026):** Terminal: Interpreter gestartet; die Fenster Bedienpult und SW-EA werden aufgeblendet; im Pult sind alle Schalter ungedrückt außer H und T-SW (Stellung T); die Taste K0 ist nicht eingerastet, Kanal K0 ist elektronisch angewählt (berichtigt in Entwurf 76); Lampe N grün, Lampe B dunkel; Netzschalter rot (Schlüsselschalter „aus“); nur der Netzschalter nimmt Klicks an. **Ändert** den Eintrag vom 16.10.2026 zum Startzustand (dort „alle Lampen dunkel, auch B und N“) und die Standardannahme zur Startstellung (F-02 Nr. 8). Der Dialog zum Einschalten und Programmlauf wird fortgeschrieben | 01 (1.3, 1.8, 3.5, 5), 05 (F-14) |
| 16.10.2026 | **Einschalten und Laden des Minimalprogramms (Review F-14, Dialog, entschieden 16.10.2026):** Klick auf den Netzschalter: er wird sofort grün, B rot, `fade_in` läuft (Projektinhaber: ca. 5 bis 6 s); in dieser Zeit nehmen die Tasten keine Klicks an, nur der Netzschalter; ein erneuter Klick macht ihn wieder rot, `fade_out` läuft, danach wird das komplette Interpreterprogramm beendet und beide Fenster werden abgeräumt. Nach `fade_in` wird B grün; ab dann sind die Tasten bedienbar. Das MP wird geladen mit der Tastenfolge G, M halten, E, E, M lösen, K1 (Leser 2: K2), R (H ist schon gedrückt); das KEP wird angesprungen, liest den binär kodierten Lochstreifen mit dem BIS-Minimalprogramm und speichert ihn ab 0040; am Lochstreifenende bleibt es stehen. Der Programmstart ist erst danach möglich. **Ersetzt** F-02 Nr. 2 und Nr. 4. (Dauer und KEP geklärt, siehe nächste Zeile) | 01 (1.3, 1.8, 5), 03 (5), 04 (2.7), 05 (F-14) |
| 16.10.2026 | **Hochlauf, KEP, Abbruch im Hochlauf (Review F-14, Dialog, entschieden 16.10.2026):** Hochlauf: `fade_in` läuft in voller Länge (11,3 s, die Länge der Aufnahme; „solange es läuft“), B wird **am Ende von `fade_in`** grün. Die frühere Angabe „ca. 5 bis 6 s“ war eine Schätzung. KEP: Das Pult-Fenster und der Interpreter in GRAFIK bringen das KEP nicht auf die Spur 0. Es muss **anderweitig** dorthin gelangen, z. B. mit einem TEST oder von Hand in die Trommeldatei (Pflege durch den Projektinhaber, F-03). Der Widerspruch zu Dokument 04 §2.7 ist damit aufgelöst. Klick im Hochlauf: `fade_in` **bricht ab**, `fade_out` läuft (es läuft immer nur einer von beiden), der Netzschalter wird rot, **B wird dunkel**; danach Ende des Programms. Die Tasten bleiben im Hochlauf gesperrt (bestätigt). **Farbe B beim Ausschalten bei laufendem Rechner (entschieden 16.10.2026, Entwurf 45):** B wird **gleich dunkel**, nicht rot; der Netzschalter wird rot, `fade_out` läuft, danach endet das Programm. Ersetzt den Eintrag vom 13.10.2026 („B rot, 2 Sekunden Anzeige“). Offen bleibt der Programmlauf nach dem Laden des MP *(am 16.10.2026 weitergeführt, nächster Eintrag)* | 01 (1.3, 1.8, 5), 03 (5), 04 (2.7), 05 (F-14) |
| 16.10.2026 | **Programmlauf nach dem Laden des MP (Review F-14, Dialog, entschieden 16.10.2026, berichtigt in Entwurf 47):** Das KEP trägt beim Abspeichern des MP in die Zelle 0000 einen Sprung zum Minimalprogramm ein; **H, G, R** startet das MP (Start auf Zelle 0000). Das MP erreicht die Stelle „Eingabe eines Befehls mit Kennzeichen“; dort werden zuerst Leitadressen eingegeben: **20 aaaa** = Relativadresse, **21 aaaa** = 1. Leitadresse, **22 aaaa** = 2. Leitadresse usw. bis **29 aaaa** (die verschiedenen Eingabemöglichkeiten). Dann wird der Leserkanal **K1 oder K2** gewählt und **`01.`** eingegeben (Kennzeicheneingabe K₁K₂; Befehl zur fortlaufenden Eingabe von Objektkodebefehlen mit Addition der 1. Leitadresse); der Objektkode-Lochstreifen wird nach dem Kennzeichen LEITADRESSE (00 bis 09) und der eingegebenen Adresse **ab Speicherplatz aaaa** gespeichert. **Programmstart:** Eingabe **`10 aaaa`** im MP verlässt das MP, die Steuerung geht an das geladene Programm. `aaaa` in `10 aaaa` ist die **Startadresse im Speicher** (Entwurf 48): häufig gleich der (1.) Leitadresse; Beispiel: relativer Start 0200, `21 1200` gegeben → Start mit `10 1400`; Einzelheiten BIS: `C8205-Interpreter-BIS.md` (nicht im Paket) | 01 (1.8 Nr. 10 bis 14), 05 (F-14) |
| 16.10.2026 | **Bedienung während des Programmlaufs (Review F-14, Dialog, entschieden 16.10.2026, Entwurf 48):** Das Pult ist **interruptfähig** bezüglich **H** (jederzeit Unterbrechung der Befehlsverarbeitung, danach wieder normal bedienbar), der **Kanalanwahltasten**, der **Taste SW rechts neben LS** (unterdrückt jederzeit die SW-Ausgabe, der Rechner läuft weiter), **SP, BS, LS**, des **Netzschalters** und – nur bei Stellung H, bei R gesperrt (Entwurf 71) – des **Umschalters T ↔ SW**. Das Pult reagiert auf die Flags **FE, FÜ, BS, US** (Lampen); die Stellung **H–R** steuert die Lampen H und R. **Widerspruch geklärt in Entwurf 49:** Die Taste SW rechts außen ist ein eigener Selektor; T-SW unterliegt nicht der Rollensperre *(in Entwurf 71 ersetzt: bei R gesperrt)* | 01 (1.8 Nr. 15 bis 22, 3.5), 05 (F-14) |
| 16.10.2026 | **Selektor SW, T-SW und Tastenwirkung (Review F-14 und F-06, Dialog, entschieden 16.10.2026, Entwurf 49):** **SW rechts außen ist ein eigener Selektor** (neben SP, BS, LS). **T ↔ SW unterliegt nicht der Rollensperre** *(in Entwurf 71 ersetzt: bei R gesperrt)*. Sind die Tasten bedienbar, **reagieren sie wie im TEST beschrieben** (Pult-Doku, Durchführung eines Tests). Ersetzt die Ableitung zu F-06 (Entwurf 29, „Rollensperre ja“) | 01 (1.8, 3.5, 7), 05 (F-06, F-14) |
| 16.10.2026 | **Wippe T-SW und Selektor SW (Review F-06 und F-14, Dialog, entschieden 16.10.2026, Entwurf 50):** **T-SW ist eine mechanisch verbundene Kombination zweier Tasten** (T und SW) **wie eine Wippe**, immer nur alternativ nach unten zu drücken; die Tastatur hat **keine weitere Taste SW**. Das Manifest-Element **`SW_umschalt` ist der Selektor SW** (rechts außen in der Reihe SP, BS, LS, SW, Abbildung 4 der Pult-Doku) und **rastet ein wie SP, BS und LS**. Ersetzt die Lesart „`SW_umschalt` = dritte Bedienstelle von T-SW“ (Entwurf 29). Abbildung im Paket: `pult-fenster/original-upload/abb4_anwahltasten_selektoren_sperrschalter.png` | 01 (3.3, 3.5, 1.8), 05 (F-06, F-14) |
| 16.10.2026 | **Wirkung des Selektors SW (Review F-14, Dialog, entschieden 16.10.2026, Entwurf 51; ergänzt in Entwurf 52):** Bei eingerastetem Selektor SW bleibt der **bestehende Text im Fenster „SW Ausgabe“ sichtbar**, **neuer Text wird nicht ausgegeben**, der Rechner **arbeitet die Ausgabebefehle weiterhin korrekt ab**, das Schreibwerk macht **keinen Ton**; **keine Ausgabe heißt kein Warten** (keine Schreibwerkzeit). Nach dem Lösen wird wieder ausgegeben (Tastengeräusch, Tastenverzögerung), **unterdrückter Text wird nicht nachgeholt**. Flags und Lampe SW bleiben unberührt; Leser, Stanzer und Rechnergeräusch sind nicht berührt | 01 (1.8 Nr. 17, 3.5), 03 (1), 05 (F-14) |
| 16.10.2026 | **Stanzer im Lauf und Schalter LS (Review F-14, Dialog, entschieden 16.10.2026, Entwurf 52):** Der Selektor SW gilt für den Stanzer nicht; keine eigene Bedienung. Bei gesetztem LS ist das **Stanzergeräusch immer** zu senden, sonst **endet es 5 Sekunden nach dem letzten Zeichen** und beginnt erst mit dem nächsten Zeichen wieder; der Ton hat **keine Wirkung auf die Stanzerdatei**. Abweichung zur Projektdokumentation (3 Sekunden Abschaltverzögerung des Motors) **geklärt in Entwurf 53**: 5 s nur für das Geräusch, weil 3 s schlecht hörbar sind; Motor weiter 3 s; Projektdokumentation unverändert | 01 (1.8, 3.5), 03 (1), 05 (F-14) |
| 16.10.2026 | **Ende des Programmlaufs (Review F-14, Dialog, entschieden 16.10.2026, Entwurf 54):** Das Ende kann **durch Halt des Programms** (US, BS, FÜ), **durch Eingriff am Pult** oder **durch den Netzschalter** erfolgen (alle drei möglich). Nach einem Halt zeigt das Pult **nur die Lampe** und wartet auf die Tasten **ST, Ü, M, E wie im TEST beschrieben**; **nichts Zusätzliches** (keine Terminalmeldung, kein Ton). **Damit ist der Beispielablauf F-14 abgeschlossen** | 01 (1.8 Nr. 23 bis 25), 05 (F-14) |
| 16.10.2026 | **Kein Abspielprogramm oder Audiogerät (Review F-17, Dialog, entschieden 16.10.2026, Entwurf 55):** **Fehlt in GRAFIK (ohne `--STUMM`) ein Abspielprogramm oder ein nutzbares Audiogerät, bricht das Skript mit Fehlermeldung und Rückkehrcode 16 ab** (wie bei fehlendem Tkinter, fehlender Anzeige oder nicht ladbarem C-Modul), und läuft **nicht** ohne Ton weiter. Standardannahmen (nicht gefragt, nicht bestätigt): (1) Mit `--STUMM` wird kein Abspielprogramm gebraucht und nichts geprüft. (2) Die Prüfung erfolgt beim Start, zusammen mit den anderen Startfehlern, vor dem Aufblenden der Fenster. (3) Als „nicht nutzbar“ gilt: kein Abspielprogramm gefunden oder der Probeaufruf beim Start schlägt fehl; ein nicht erkennbares Audiogerät lässt sich nicht sicher feststellen. | 03 (5 Nr. 11), 05 (F-17) |
| 16.10.2026 | **Dauernd laufender Tonstrom (Review F-17, Dialog, Vorschlag des Projektinhabers 16.10.2026, Entwurf 56):** Der Projektinhaber schlägt vor, **alle Töne ständig auszugeben** und nur zwischen **stumm und hörbar** umzuschalten, um die Anlaufverzögerung zu sparen. Daraus abgeleitet, nicht ausdrücklich bestätigt: (1) In GRAFIK ohne `--STUMM` wird beim Start **ein Ausgabestrom geöffnet, der bis zum Ende dauernd läuft** (bei Ruhe Stille); es wird **kein Abspielprozess je Klang** gestartet. Der Probeaufruf aus Nr. 11 ist das Öffnen dieses Stroms. (2) **Dauergeräusche** (Rechner-Grundgeräusch, Motor, Dauerstanzen) laufen als Schleife immer mit und werden nur über den Pegel (0 oder voll) stumm oder hörbar geschaltet; die Schleifenlage beim Einschalten ist beliebig. (3) **Einzelklänge** (Zeichen, TAB, WRZL, Leser) können nicht stumm mitlaufen, weil Beginn und Länge zum Ereignis gehören; sie werden **beim Ereignis in den laufenden Strom eingemischt**. Damit sind auch gleichzeitige Töne (Nr. 7) im Strom lösbar. (4) **Anforderung an die Verzögerung:** Ton und Zeichen im SW-Fenster erscheinen **im Mittel gleichzeitig**; der Ton setzt gegenüber dem Zeichen **höchstens 50 ms** später ein (Standardannahme; Zeichenabstand des Schreibwerks 100 ms). Das Zeichen wird nie wegen des Tons verzögert. Der Puffer des Stroms darf diese Grenze nicht überschreiten. (5) **Stummschaltung im Betrieb:** je Tonkanal (Rechner, Schreibwerk, Leser, Stanzer) ein **internes Tor**; es dient dem Selektor SW, Netz aus und dem Auslaufen der Dauergeräusche. **Kein neues Bedienelement** und keine neue Schalterstellung (Standardannahme; `--STUMM` bleibt Startschalter und öffnet keinen Strom). (6) Ausfall des Stroms im Betrieb und Umsetzung unter Windows: siehe Nr. 13 (Dok. 03 §5). | 03 (5 Nr. 12), 05 (F-17) |
| 16.10.2026 | **Ausfall des Tonstroms im Betrieb und Windows-Umsetzung (Review F-17, Dialog, 16.10.2026, Entwurf 57):** **(a) Fällt der Ausgabestrom in GRAFIK (ohne `--STUMM`) mitten im Lauf aus, bricht das Skript mit Fehlermeldung und Rückkehrcode 16 ab**, wie beim Start (Nr. 11); es läuft nicht ohne Ton weiter. Antwort „ja“ auf den Vorschlag. Standardannahmen (nicht gefragt, nicht bestätigt): Als Ausfall gilt, wenn der Abspielprozess endet oder das Schreiben in den Strom bzw. ein Aufruf der Windows-Tonschnittstelle fehlschlägt; der Abbruch läuft wie jeder andere Abbruch mit Code 16 (Trommeldatei und Protokoll wie dort). **(b) Windows (Vorschlag des Assistenten, noch nicht bestätigt):** `winsound` entfällt für GRAFIK. Der Strom wird mit der Windows-Schnittstelle **`winmm` (`waveOut…`) über `ctypes`** geöffnet; das ist Teil von Python, braucht keine zusätzliche Software und kennt gleichzeitig mehrere Puffer. Das Skript mischt die Klänge selbst zu Blöcken (44,1 kHz, mono, 16 bit) und reicht sie in einem Ring aus vier Puffern zu je 10 ms an die Schnittstelle (höchstens 40 ms Verzögerung, innerhalb der Grenze 50 ms aus Nr. 12). Unter Linux ist die Senke ein Abspielprogramm mit Roh-Audio über die Standardeingabe (`paplay`, `pw-cat` oder `aplay`), dasselbe Mischen. **(c) Vorbehalte:** Windows ist weder übersetzt noch getestet; ein Windows-Tester **kommt noch** (Antwort 16.10.2026, F-18). Das Mischen in Python würde den Interpreter belasten (GIL); deshalb ist das Mischen **gleich im C-Modul** vorgesehen (Nr. 14). Fehlt `winmm` oder schlägt das Öffnen fehl, gilt Nr. 11 (Abbruch mit Code 16). | 03 (5 Nr. 13), 05 (F-17) |
| 16.10.2026 | **Mischer im C-Modul, statische Bibliotheken, Umwandlung MP3 → WAV** *(Review F-17 und F-18, Dialog, 16.10.2026, Entwurf 58)*: **(a) Windows-Tester:** Er „kommt noch“ (Antwort des Projektinhabers); bis dahin bleibt der Windows-Zweig ungetestet. **(b) Das Mischen kommt gleich in ein C-Modul** (Antwort „wenn möglich, gleich C-Modul vorsehen“), nicht erst nach einer Messung. Anforderungen: Das Modul `tonmisch` enthält Mischer (Dauerschleifen mit Pegel 0 oder voll, Einzelklänge, Ausgabe in Blöcken zu 10 ms), Ringpuffer und die **Senke** (Linux: Abspielprogramm mit Roh-Audio über eine Röhre, vom Modul gestartet; Windows: `winmm`/`waveOut…`). Es läuft in **einem eigenen C-Thread**, sodass weder die GIL noch das Python-Tempo den Ton stören. Die Schnittstelle zu Python bleibt schmal: Klangdaten übergeben, Ereignis auslösen, Pegel je Kanal setzen, Öffnen, Schließen, Ausfall melden (→ Nr. 13a). **(c) Statische Bibliotheken** (Wunsch „static libraries“): Das Modul wird wie die Trommel als **statische Bibliothek** gebaut (`libtonmisch.a`, unter MSVC `tonmisch.lib`) und **fest in das Python-Erweiterungsmodul eingebunden**, möglichst **zusammen mit der Trommel in einer einzigen Datei** (`.so` bzw. `.pyd`); es wird keine zusätzliche Bibliothek zur Laufzeit nachgeladen. Der Testrahmen unter Linux wird mit `-static` gebunden. Grenze (Standardannahme): Das Erweiterungsmodul selbst ist eine ladbare Datei; die Systembibliotheken (C-Laufzeit, unter Windows `winmm.dll`, die es nur als DLL gibt) bleiben dynamisch. **(d) Klangdaten:** Python liest die WAV-Dateien (Standardbibliothek `wave`) und übergibt die Rohdaten; das C-Modul kennt kein Dateiformat (Standardannahme, nicht gefragt). **(e) MP3 → WAV, einmalig umgewandelt** (Antwort „ja, einmal mundgerecht umwandeln“): Die fünf Aufnahmen liegen jetzt als WAV (44,1 kHz, mono, 16 bit; Stereo zu Mono gemittelt, unverändert im Pegel) in `ton/toene_rechner_stanzer/` vor: `rechner_grundgeraeusch.wav` (5,94 s), `netz_ein_fade_in.wav` (11,29 s), `netz_aus_fade_out.wav` (1,95 s), `ls_motor.wav` (4,96 s), `ls_dauerstanzen.wav` (18,06 s). Die MP3 bleiben als Quelle in `ton/aufnahmen/`; zur Laufzeit wird nichts umgewandelt, ein MP3-Decoder ist nicht nötig. Die Längen weichen um bis zu 0,05 s von den MP3-Angaben ab (Decoderverzögerung); bei `fade_in` ist 11,3 s weiter ausreichend. Die WAV sind nur gemessen, **nicht angehört**. | 03 (5 Nr. 14), 02 (4.5), 05 (F-17, F-18) |
| 16.10.2026 | **Stanzertöne: Dauerstanzen, Einzelzeichen, Aufnahmen** *(Review F-17, Dialog, 16.10.2026, Entwurf 59; Entscheidung dem Assistenten überlassen, daher nicht ausdrücklich bestätigt)*: **Grundsatz (Hinweis des Projektinhabers):** Die Einzeltöne sind **viel länger als die Stanzzeit eines Zeichens** (20 ms bei 50 Zeichen/s) und passen nur näherungsweise. Der Stanzerton wird deshalb **nicht je Zeichen, sondern nach Zustand** gespielt; ein Ton je Zeichen würde sich überlagern. **(a) Zustände und Schwelle:** *Aus*: kein Ton. *Motor*: `ls_motor.wav` als Schleife (Einsatz und Ende nach Entwurf 52 und 53: bei LS immer, sonst bis 5 s nach dem letzten Zeichen). *Dauerstanzen*: `ls_dauerstanzen.wav` als Schleife, sobald **zwei aufeinanderfolgende Zeichen höchstens 40 ms Abstand** haben; Ende, wenn **60 ms** lang kein Zeichen kommt; dann zurück zu *Motor*. Die Zahlen 40 ms und 60 ms sind Standardannahmen (Stanzer 50 Zeichen/s = 20 ms Abstand; Schwelle = zwei Zeichenzeiten, Ende = drei) und mit der Hörprüfung zu überprüfen. **(b) Einzelzeichen:** Es gibt **keinen Einzelschritt-Ton** (D-8 entschieden: nicht gebraucht, es liegt auch keine Aufnahme vor); ein einzelnes oder langsam folgendes Zeichen hört man nur als Motor. **(c) Motor und Dauerstanzen:** Eine Messung der Aufnahmen (16.10.2026) ist nicht eindeutig: Das Motorgeräusch hat über 5 kHz fast nichts (81 dB gegen 146 dB bei Dauerstanzen) und unter 200 Hz mehr (135 dB gegen 124 dB); die Feinspektren unter 1 kHz stimmen mäßig überein (Korrelation 0,64). **Standardannahme (D-9):** `ls_dauerstanzen.wav` enthält den Motor schon; während *Dauerstanzen* wird der Motor-Pegel daher auf 0 gesetzt (Überblendung 50 ms), beim Zurückschalten umgekehrt. Falls die Hörprüfung (Nr. 8) das Gegenteil zeigt, laufen beide gleichzeitig; das ist nur eine Konstante im C-Modul. **(d) Umsetzung:** über die Tore des Mischers (Nr. 12 und 14), im C-Modul; die Schwellenzeiten liegen als Konstanten dort. **Berichtigt durch Nr. 21 (Entwurf 66): Schwelle, Ende, Motor und Dauerstanzen.** | 03 (5 Nr. 15), 05 (F-17) |
| 16.10.2026 | **Echo über K0 mit Ton** *(Review F-17, Dialog, 16.10.2026, Entwurf 60)*: Das **Echo von Eingaben über K0** bekommt **denselben Ton** wie jede andere Ausgabe auf das Schreibwerk (Antwort „ja“ auf den Vorschlag). Begründung: Das Schreibwerk schreibt dort tatsächlich; die Gleichheit von TEST und GRAFIK (F-04) betrifft Ergebnisse, nicht den Ton. Es gelten Nr. 12 (Verzögerung), der Selektor SW und `--STUMM` unverändert. Standardannahme (nicht gefragt): Der Aufruf gehört an dieselbe Stelle wie bei der Ausgabe (`sw_schreibe`), sofern das Echo dort durchläuft; die Prüfung des Echo-Pfades im Interpreter steht beim Einbau noch aus. **Hinfällig seit 16.10.2026 (Entwurf 88): Das Echo gibt es in GRAFIK nicht** („Tastatureingaben sind nirgendwo zu sehen“); folglich auch kein Ton dafür. | 03 (5 Nr. 16), 05 (F-17) |
| 16.10.2026 | **Tabulator, Schreibposition und rechter Anschlag** *(Review F-17, Dialog, 16.10.2026, Entwurf 61; Festlegung des Projektinhabers)*: **(a) Tabulatorstopp alle 12 Zeichen** (eingetragen, hardwareseitig). Gibt der Rechner ein TAB aus, geht die Schreibposition auf den **nächsten Stopp** (12, 24, 36 …). Beispiele des Projektinhabers: nach `<wrzl>Alle Vö` (7 Zeichen) macht TAB **5 Leerschritte**; `<Tab>12<Tab>` macht beim zweiten TAB **10 Leerschritte** (Position 14 → 24). **(b) Ton:** Es gibt **nur noch einen TAB-Ton**, gleich für jeden Tabulatorweg, **400 ms lang** (etwa drei normale Zeichen). Damit entfällt die Wahl kurz oder lang und der Aufrufer braucht keinen Tabulatorweg (Beschreibung §16 und D-Punkt zu TAB erledigt). Die Datei `ton/sw_toene/tab_400.wav` ist aus `tab_lang.wav` (325 ms) durch tonhöhentreue Dehnung auf 400,0 ms gemacht (letzte 10 ms ausgeblendet); nur gemessen, **nicht angehört**. `tab_kurz.wav` und `tab_lang.wav` bleiben als Quelle liegen, werden aber nicht mehr gespielt; der Parameter `tab_lang` von `sw_ton()` entfällt beim Einbau. **(c) Rechter Anschlag:** Wird **Position 130 überschritten, wird keine Bewegung der Schreibposition mehr ausgeführt**; das gilt **auch für normale Zeichen**. **(d) Annahmen des Assistenten, **vom Projektinhaber bestätigt am 16.10.2026 (Entwurf 62)**:** Position = Spalte 0 bis 130 seit Zeilenanfang; WRZL und WR setzen sie auf 0. Ein TAB, dessen Stopp hinter 130 läge (ab Position 120), bewegt die Position **bis 130** und nicht weiter. Das Zeichen hinter dem Anschlag wird **angeschlagen (Ton läuft, TAB 400 ms, Zeichen 120 ms)** und **im Fenster auf Position 130 überdruckt** (ersetzt dort das letzte Zeichen), es entsteht **kein Zeilenumbruch** mehr (bisher `wrap='char'` bei 130 Spalten). Die Schreibwerkzeit eines TAB ist **400 ms** (Wartezeit = Tonlänge, wie bei `sw_ton()` heute). **(e) Geltungsbereich (**bestätigt 16.10.2026, Entwurf 62: nur im SW-Fenster**):** Die Regel gilt für die **Darstellung im SW-Fenster in GRAFIK**. Die Schreibwerk-Datei (`m.sw_datei`) und die Terminalausgabe behalten das Zeichen unverändert (TAB bleibt ein TAB); die Vergleichsdateien in `Test-Ergebnisvergleiche/` (zwei enthalten TAB: `bsp_5_15_lochband_druck…`) und damit die Gleichheit von TEST und GRAFIK (F-04) bleiben unberührt. Das Fenster rechnet die Position selbst mit. | 03 (5 Nr. 17), 01 (SW-Fenster), 05 (F-17) |
| 16.10.2026 | **Aufrufstelle des Lesers** *(Review F-17, Dialog, 16.10.2026, Entwurf 63)*: `ls_ton()` wird **bei jedem Zeichen aufgerufen, das der Leser K1 oder K2 tatsächlich an den Rechner liefert** (Antwort „dein Vorschlag passt“). Der Projektinhaber bestätigt, dass der Interpreter dort **genau ein Zeichen je Zugriff** liefert; das erledigt die Prüfung, die beim Einbau offen war. Kein Aufruf bei Zeichen von Tastatur oder K0. Im Modus TEST kein Ton. Das Tempo bleibt bei **130 Zeichen/s**; Einzelschritt, Dauergeräusch und Auslaufen richten sich wie bisher nach dem Abstand der Zeichen (Schwelle 100 ms, noch im echten Lauf zu prüfen). Annahme des Assistenten (nicht gefragt): Im Tonstrom (Nr. 12 und 14) ist der Einzelschritt ein Einzelklang, das Dauergeräusch eine Schleife mit Tor und das Auslaufen ein Einzelklang (`ls_ende.wav`). | 03 (5 Nr. 18), 05 (F-17) |
| 16.10.2026 | **Netz aus und `fade_out`** *(Review F-17 und F-02, Dialog, 16.10.2026, Entwurf 64)*: **`fade_out` (2 s) wird nur beim normalen Ausschalten mit dem Klick auf den Netzschalter gespielt** (Antwort „ja“ auf den Vorschlag); danach endet das Skript mit **Code 0**. Bei **Strg+C, X und Schließen des Fensters** (Code 8) hören **alle Töne sofort auf**: Tore zu, Tonstrom zu, **kein `fade_out`**. Beendet der Tonstrom dabei selbst den Prozess nicht, gilt Nr. 13 nicht als Ausfall (das Schließen ist gewollt). Damit ist D-5 erledigt. | 03 (5 Nr. 19), 05 (F-02, F-17) |
| 16.10.2026 | **Wiedereinschalten** *(Review F-17 und F-02, Dialog, 16.10.2026, Entwurf 65)*: **„Wieder einschalten“ heißt, das Skript neu zu starten** (Antwort „ja“ auf den Vorschlag). Es beginnt wieder mit „Rechner aus“ und wartet auf den Klick auf den Netzschalter. Die Register sind danach weg, die Trommeldatei bleibt erhalten. Damit ist D-1 erledigt; im Skript gibt es kein Wiedereinschalten nach dem Ausschalten. | 03 (5 Nr. 20), 05 (F-02, F-17) |
| 16.10.2026 | **Stanzerton, Berichtigung durch den Projektinhaber** *(Review F-17, Dialog, 16.10.2026, Entwurf 66; ersetzt Nr. 15 (a) und (c))*: **(a) Dauerstanzen beginnt mit dem zweiten Zeichen, das weniger als 50 ms nach seinem Vorgänger ausgegeben wird, und läuft, solange diese Bedingung erhalten bleibt** (ersetzt die Schwelle 40 ms). **(b) Ende von Dauerstanzen** (Annahme des Assistenten): Sobald 50 ms nach dem letzten Zeichen kein weiteres kommt, gilt die Bedingung nicht mehr; der Ton wird vom Zeitgeber beendet, nicht erst beim nächsten Zeichen. Er fällt dann auf das Motorgeräusch zurück (ersetzt die 60 ms). **(c) Abschalten:** Kommt **nach 5 Sekunden kein neues Zeichen**, wird der Ton abgeschaltet (der Projektinhaber schrieb „5?“; übernommen als 5 s, wie in Entwurf 52 und 53). **(d) Motor und Dauerstanzen sind das gleiche Geräusch:** Es gibt **einen** Stanzergeräusch-Zustand und nie zwei Geräusche gleichzeitig; während Dauerstanzen läuft, ist der Motor nicht zusätzlich zu hören (D-9 entschieden, die Messung der Aufnahmen ist damit gegenstandslos). **(e) LS gedrückt:** Der **Motor läuft dauernd**; das ist die **dominierende Bedingung**: Das Geräusch wird nie abgeschaltet, auch nicht nach 5 s. Auslegung des Assistenten (nicht gefragt): Auch bei gedrücktem LS wählt die Bedingung (a) weiter zwischen `ls_dauerstanzen.wav` und `ls_motor.wav`. Umsetzung unverändert über die Tore des Mischers (Nr. 12 und 14); 50 ms und 5 s sind Konstanten im C-Modul. | 03 (5 Nr. 21), 05 (F-17) |
| 16.10.2026 | **Hörprüfung** *(Review F-17, Dialog, 16.10.2026, Entwurf 66)*: Vorschlag des Assistenten, vom Projektinhaber **nicht ausdrücklich bestätigt**, aber mit Korrekturen zu zwei Punkten der Liste beantwortet und deshalb so weitergeführt (bei Widerspruch ändern): Die Hörprüfung ist eine **Abnahme nach dem Einbau**, vom Projektinhaber am Rechner, unter Linux und später unter Windows; sie ist **kein Hindernis für die Freigabe zum Neuprogrammieren**. Danach werden als Konstanten angepasst: die 50 ms und 5 s des Stanzers, die 100 ms Schwelle des Lesers, der Klang von `tab_400.wav` und der Übergang von `fade_in` in die Grundgeräusch-Schleife. Nicht mehr Gegenstand der Hörprüfung: Motor und Dauerstanzen (Nr. 21 (d)). | 03 (5 Nr. 22), 05 (F-17) |
| 16.10.2026 | **LS gedrückt und Abhören der Aufnahmen** *(Review F-17, Dialog, 16.10.2026, Entwurf 67; berichtigt die Auslegung in Nr. 21 (e))*: **Bei gedrücktem LS wird immer nur `ls_motor.wav` gespielt**; die 50-ms-Bedingung wählt dann nicht mehr zwischen den Aufnahmen, `ls_dauerstanzen.wav` wird bei gedrücktem LS nie gespielt. Der Projektinhaber hat **die Geräusche abgehört**; sie **scheinen in Ordnung zu sein**. Laufzeiten und Schwellen (50 ms, 5 s, 100 ms des Lesers) kann er **akustisch nicht stoppen**; sie bleiben Konstanten, die nach dem Einbau (Nr. 22) nachgestellt werden. Nicht ausdrücklich gesagt, welche Aufnahmen gemeint sind; `tab_400.wav` (neu in Entwurf 61) gilt daher weiter als nicht bestätigt. | 03 (5 Nr. 23), 05 (F-17) |
| 16.10.2026 | **Zielsysteme und Python-Version** *(Review F-18, Dialog, 16.10.2026, Entwurf 66)*: **macOS entfällt** (Antwort des Projektinhabers); Zielsysteme sind **Linux und Windows**; die macOS-Zweige im Code (`pbcopy`, `afplay`) werden im Neuprogrammieren nicht berücksichtigt. **Python-Mindestversion: 3.8 oder neuer** (passt zur Limited API des Erweiterungsmoduls). Die Tk-Version ist nicht festgelegt (Standardannahme: die mit Python gelieferte). **Auslieferung des C-Moduls: entschieden, siehe Eintrag Entwurf 67.** | 05 (F-18) |
| 16.10.2026 | **Auslieferung des C-Moduls** *(Review F-18, Dialog, 16.10.2026, Entwurf 67; schließt Dokument 02 §8 Nr. 3)*: **Das Paket liefert die fertig übersetzten Dateien mit**; der Anwender braucht weder Compiler noch Python-Entwicklungsdateien (Antwort „so soll es sein“). **Die Dateien sind `-static` gelinkt** (Wunsch des Projektinhabers). Festlegungen des Assistenten dazu (nicht gefragt): (1) **Eine Datei je System** (Linux, Windows), die Trommel und Tonmischer (Dokument 03 §5 Nr. 14) enthält; Limited API, daher **unabhängig von der Python-Version ab 3.8**. (2) **Statisch** heißt: eigene Quellen, `libtrommel.a`, `libtonmisch.a`, unter Linux `libgcc`, unter Windows die C-Laufzeit (`/MT` bzw. MinGW `-static`) werden in die Datei gebunden. **Technische Grenze:** Unter Linux bleibt `glibc` dynamisch (ein Python-Erweiterungsmodul ist selbst eine ladbare Datei), unter Windows `winmm.dll`. Die Linux-Datei wird auf einem **älteren System** gebaut, damit sie auf neueren läuft. (3) **Architektur x86-64** (Standardannahme, nicht gefragt). (4) **Die Windows-Datei wird erst mitgeliefert, wenn der Windows-Tester sie geprüft hat** („kommt noch“); der Quelltext mit Makefile und `build_msvc.bat` bleibt im Paket zum Nachbauen, ist aber keine Voraussetzung. (5) Nicht ladbares Modul: weiter Fehlermeldung und **Code 16** ohne Rückfall (Entscheidung 14./15.10.2026). | 02 (8 Nr. 3), 05 (F-18) |
| 16.10.2026 | **Hintergrund-Thread statt Hintergrundprozess** *(Review F-19, Dialog, 16.10.2026, Entwurf 68)*: Die Drehung der Trommel (und der Tonmischer, Dokument 03 §5 Nr. 14) laufen als **Hintergrund-Thread, ein C-Thread im Erweiterungsmodul, im selben Prozess** wie der Interpreter; **kein eigener Betriebssystem-Prozess** (Antwort „ja einverstanden“). Der Begriff „Hintergrundprozess“ wird in den Dokumenten 00 (Verzeichnis) und 02 durch „Hintergrund-Thread“ ersetzt; frühere Registerzeilen vom 13. und 15.10.2026 bleiben als Geschichte unverändert und gelten in diesem Sinn. Begründung: passt zu den statisch gelinkten Dateien und zu Strg+C; ein Prozess brächte nur Aufwand für den Datenaustausch. | 02, 03 (5 Nr. 14), 05 (F-19) |
| 16.10.2026 | **Klick- und Tastenbedienung des Pults (Review F-15, Dialog, 16.10.2026, Entwurf 69)**: **Auslösung beim Drücken der Maustaste.** **Klick-Tasten** (B, +, 1, 3, 5, 7, 9, ·, :, IS, IB, G, Ü, D, −, 0, 2, 4, 6, 8, „,“, ZR, WM, ST): 0,4 s hell, dann normal. **Wippen H–R und T–SW:** einfacher Klick rastet die Taste ein und löst die andere, immer genau eine eingerastet, kein Aufleuchten, kein Umschalt. **E und M:** Klick 0,4 s, gehaltene Maustaste = gedrückt, **Umschalt+Klick = Halter** (zweiter Umschalt+Klick löst, E und M gleichzeitig möglich); Umschalt wirkt **nur** bei E und M. **Gesperrte Taste:** ein Klick bewirkt nichts (kein Aufleuchten, kein Ton, keine Weitergabe); beim Überfahren ändern sich Taste, Mauszeiger und Hinweistext nicht. **Touchscreen wird nicht unterstützt.** Fokusverlust: gehaltene Maustaste wird losgelassen, Rastungen bleiben, 0,4-s-Timer laufen aus. *Zweiter Klick innerhalb der 0,4 s zählt als neuer Tastendruck und startet die Zeit neu: Vorschlag des Assistenten, nicht ausdrücklich bestätigt.* Dokument 01 §1.7, Dokument 05 F-15. |
| 16.10.2026 | **Computertastatur für die Eingabetasten (Review F-15, Dialog, 16.10.2026, Entwurf 69; ändert die Aufgabenteilung in Dokument 01 §1.6)**: Die Tasten `B + 1 3 5 7 9 · :` und `D − 0 2 4 6 8 , ZR` sind auch über die **gleichnamigen Tasten der Computertastatur** bedienbar, alle anderen Pult-Tasten nur mit der Maus. Zuordnung: Ziffern, + − , : wie auf der Computertastatur; „·“ = Punkt „.“; B und D = b und d (Groß/Klein gleich); ZR = Leertaste; Ziffernblock wie Hauptreihe. Wirkung wie ein Mausklick (Auslösung beim Drücken, 0,4 s hell), kein Wiederholen bei gehaltener Taste, dieselben Sperren, mehrere Tasten gleichzeitig mit je eigenem Timer. Die Computertastatur wirkt nur, wenn das **Bedienpult-Fenster den Fokus hat und der Rechnerzustand Eingaben zulässt**. |
| 16.10.2026 | **Fokus des Bedienpult-Fensters (Review F-16, Teilantwort, Dialog, 16.10.2026, Entwurf 69)**: Das Pult erhält den Fokus nach dem Programmstart und im laufenden Programm, wenn keine Eingaben im SW-Fenster anliegen (dort hat das SW-Fenster Vorrang); der Fokus verbleibt beim Pult. Wird er von Hand woandershin gesetzt, ist am Pult keine Eingabe möglich (weder Maus noch Computertastatur). Ein **Mausklick auf das Pult** bringt den Fokus zurück und **löst keine Taste aus**; für die Mausbedienung ist ein weiterer Klick nötig; die Computertastatur wirkt danach sofort, sofern der Rechnerzustand Eingaben zulässt. Eine Eingabe im SW-Fenster ist immer nur **ein Zeichen**, daher gibt es keine angefangene Eingabe beim Fokuswechsel. |
| 16.10.2026 | **Rollensperre für T–SW (Review F-15 (b), Dialog, entschieden 16.10.2026, Entwurf 71):** Das Seitenabbild der Originaldokumentation „die Tasten E, M, G, Ü und der Schalter T-SW lassen sich nur bei Stellung H betätigen“ ist maßgebend; alles Abweichende wird angepasst. T-SW ist bei Stellung R gesperrt (Klick ohne Wirkung) und nur bei Stellung H bedienbar. **Ersetzt** den Eintrag vom Entwurf 49 („T ↔ SW unterliegt nicht der Rollensperre“) und die Aussage zur Interruptfähigkeit des Umschalters T ↔ SW (Entwurf 48) | 01 (1.8 Nr. 20, 3.5, 7 Nr. 7 und 15), 05 (F-06, F-15), Pult-Doku 0.03-008 |
| 16.10.2026 | **Zeichenabbildung im SW-Fenster (Review F-16, Dialog, entschieden 16.10.2026, Entwurf 72):** Ein- und ausgegeben werden können nur die Zeichen des R300-Codes; die Umschalttasten der Computertastatur gelten ganz normal (sie bestimmen das getippte Zeichen), die C-8205-Zeichen `Um. KB`/`Um. GB` werden selbständig im Zusammenhang mit dem Zeichen gehandhabt (Zeichenlage wird mitgeführt, das passende Umschaltzeichen geht dem Zeichen voraus, das Zeichen bleibt vorgemerkt und wird beim nächsten Eingabe-Halt geliefert, ohne erneutes Tippen). **[Überholt seit 18.10.2026 (Dok. 09 U-10, Checkpoint 42): Es gibt keine Vormerkung. Das Fenster sendet die zwei Eingaben im echten Tastenabstand; jede wird nur angenommen, wenn im Moment der Eingabe ein `011` aktiv ist, sonst ist sie blockiert (S3-11, S3-13, S3-18). Wortlaut bleibt zur Nachvollziehbarkeit stehen.]** Weitere Einzelheiten (Sondertasten, stiller Verwurf nicht angenommener Zeichen, Vormerkung, Fokus bei verweigerter Fokusübernahme) hat der Projektinhaber dem Entwickler überlassen, **Standardannahmen, zu erproben** | 01 (1.7), 05 (F-16) |
| 18.10.2026 | **Zeichenlage bei der Eingabe am SW (Festlegung des Projektinhabers, GRAFIK G3-004):** Für die Eingabe am SW zählt nur die Zeichenlage des SW selbst (Vorzustand), nie die des Rechners; die Umschalttasten der Computertastatur werden nicht gesondert ausgewertet, das Fenster erkennt die Lage am Zeichen. Ein Umschaltzeichen geht nur bei Abweichung vom Vorzustand an den Rechner (dann zwei Eingabezeichen: Umschaltzeichen, Zeichen). Nach dem Einschalten ist der Vorzustand unbestimmt, das erste Zeichen setzt ihn. Ändert 01 (1.7 Nr. 2) und 05 (F-16); Test `testscripte/grafik_sw_pult_test.py` (Tasten des Bedienpults) | 01 (1.7), 05 (F-16) |
| 16.10.2026 | **Review F-02 (Netzablauf, Schritt 2):** Der Projektinhaber bezeichnet die Fragen zu F-02 als bereits geklärt („das ist alles schon geklärt“); keine neue Entscheidung. Es gelten die eingetragenen Festlegungen (13.10., 15.10., 16.10.); wo die Dokumente nichts festlegen, gelten vorläufig die Standardannahmen in Dokument 05 (F-02), nicht gesondert bestätigt | 05 (F-02), 01 (5, 7), 03 (5) |
| 16.10.2026 | **Startbelegung der Trommel in GRAFIK pflegen (Review F-03, Schritt 3):** Den Zustand der Trommeldatei vor einem GRAFIK-Lauf pflegt der **Projektinhaber selbst**; das Paket legt weder eine Vorlage `Trommelvorlagen/MP.txt` noch ein Zurücksetz-Skript an. Ein Schutz gegen Doppelstart bleibt nach der Entscheidung vom 15.10. („nicht vorgesehen“); eine Warnung bei nicht lauffähiger Trommel gibt es nicht (Standardannahme zu „Trommel so wie sie ist“, nicht gesondert gefragt) | 02 (6, 8 Nr. 10), 05 (F-03) |
| 16.10.2026 | **Gleichwertigkeit TEST und GRAFIK (Review F-04, Schritt 4):** Bei gleichem Programm müssen TEST und GRAFIK **dieselben Ergebnisse** liefern (Registerinhalte, Ausgaben). Ausnahmen nur die Zeiten (echte Trommel in GRAFIK) und die Befehlsentnahme nach X-Abbruch (`Überblick_und_Gesamtaufbau.md`, 4.1); sonstige Abweichungen gelten als Fehler des GRAFIK-Zweigs. **Prüfweg nicht entschieden** (nur von Hand abnehmen oder Einspielmodus für Pult-Klicks): Der Projektinhaber antwortete „beide TEST und GRAFIK müssen die gleichen Ergebnisse liefern“ und wählte keinen der beiden Wege; vorläufig Handabnahme (Standardannahme) | 00 (3.6), 04 (4), 05 (F-04) |
| 16.10.2026 | **Lampenbild ruhig** *(Durchgang O-5, Dialog, 16.10.2026, Entwurf 84)*: Wortlaut des Projektinhabers: „Lass die Lampen so leuchten, dass das Bild ruhig ist.“ Im Dauerlauf R sollen die Lampen also **nicht mit jeder Momentaufnahme springen oder flackern**. Das ergänzt die Festlegung „höchstens alle 40 ms den letzten Zustand“ (Dokument 01 §6.2); der 40-ms-Takt bleibt, er betrifft nur die Anzeige. Bei Halt und nach E-Schritt gilt weiter sofort der genaue Stand. **Wie** das Bild beruhigt wird, ist dem Entwickler überlassen. **Standardannahme (nicht gefragt, nicht bestätigt, jederzeit zu ändern):** Mittelung statt Momentaufnahme; eine Lampe leuchtet, wenn sie im Fenster der letzten 40 ms überwiegend an war (Schwellen 60 % an, 40 % aus, dazwischen bleibt der bisherige Zustand); nur die beiden vorhandenen Grafiken (hell, dunkel), keine dritte Grafik; die Zwischenabtastung ist zeitgesteuert und bremst die Befehle nicht. Abnahme: Handabnahme am laufenden Fenster, Dauerlauf R, Bild ruhig. | 01 (1.5, 6.2, 7 Nr. 8), 05 |
| 16.10.2026 | **Trommel: vier Punkte aus Dokument 02 §8** *(Durchgang O-7, Dialog, 16.10.2026, Entwurf 84)*: **(1)** Gesperrte Schreibzugriffe verbrauchen ihre Wartezeit (Vorschlag, nicht widersprochen). **(2)** Die Beobachtungsvariable `trommel_aktuelle_sektornummer` bleibt lockfrei (Vorschlag, nicht widersprochen). **(3)** Es gibt **keinen Schalter für eine feste Startlage**; nach dem Einschalten liegt die Trommel beliebig, wie am echten Gerät (Vorschlag, nicht widersprochen); `trommel_einschalten_start` bleibt nur für Testrahmen. **(4) Kein aktives Warten** (Spin). Antwort des Projektinhabers: „kein aktives Warten, alle 20 µs prüfen reicht“ (zuerst als „20 ms“ gelesen; gemeint sind **Mikrosekunden**, berichtigt am 16.10.2026). Der Hintergrund-Thread schläft immer. Solange ein Auftrag ansteht, prüft er die Uhr in Abständen von **höchstens 20 µs**; ein Tickbeginn darf also bis etwa 20 µs spät erkannt werden (eine Wortzeit sind 104 µs). Die Tickzahl und damit die Wartezeit in Wortzeiten (0 bis 31) bleiben exakt, weil der Takt eine Funktion der Uhr ist und übersprungene Ticks nachgeholt werden (Dokument 02 §4.3). Ohne anstehenden Auftrag ändert sich nichts. **Folgen:** Linux: der Zweig spinnt nicht, `clock_nanosleep` bleibt; die in Dokument 02 §5.1 gemessene mittlere Aufwachverspätung von 25 µs liegt knapp über dem Wert und berührt die Tickzahl nicht. Windows: Das aktive Warten entfällt; ein Schlafen in 20-µs-Schritten ist dort nicht zu erwarten (Zeitgeberraster im Millisekundenbereich, der Code setzt `timeBeginPeriod(1)`), der Thread prüft so oft, wie das System es zulässt; die Echtzeit-Dauer eines Zugriffs kann dadurch länger werden, die Wartezeit in Wortzeiten nicht. **Ungetestet.** Der Code (`plattform.h`, Windows-Zweig, Schalter `req_wartet`) ist **noch nicht angepasst**. | 02 (4.4, 5.3, 6, 8), 05 |
| 16.10.2026 | **Windows: Compiler MinGW-w64** *(Durchgang O-8, Dialog, 16.10.2026, Entwurf 85; schließt Dokument 02 §8 Nr. 6, soweit es den Compiler betrifft)*: Vorschlag war Visual Studio (MSVC) für die ausgelieferte Windows-Datei; Antwort des Projektinhabers: „ja, aber ich habe nur MinGW-w64 installiert“. **Entschieden: Windows wird mit MinGW-w64 gebaut** (`mingw32-make`, Erweiterungsmodul mit MinGW-w64, ausgelieferte Datei `-static`). Das ist auch der Compiler, mit dem das Projekt den Assembler unter Windows baut (`projekt/Assembler/make_c82ass.bat`). `build_msvc.bat` bleibt unverändert im Paket, ist aber **nicht der vorgesehene Weg** und nicht Teil der Auslieferung. Die übrigen Punkte des Vorschlags sind mit „ja“ übernommen: **der Windows-Tester baut und testet selbst** und meldet das Ergebnis zurück (er „kommt noch“, Entwurf 58); hier gibt es keinen Windows-Compiler. **Folgen, aus den Bauskripten gelesen (nicht gebaut, nicht getestet):** (a) `setup.py` und das Makefile setzen **kein `-static`**, obwohl die Auslieferung statisch gelinkt sein soll (Entwurf 67); anzupassen. (b) Mit nur MinGW-w64 muss der Compiler beim Bau des Erweiterungsmoduls ausdrücklich gewählt werden (`python setup.py build_ext --inplace --compiler=mingw32`), weil setuptools unter Windows sonst MSVC sucht (nach meiner Kenntnis von setuptools, zu prüfen). (c) **Risiko für „eine Datei für alle Python ab 3.8“ (Entwurf 67):** Die Zeile `#pragma comment(lib, "python3.lib")` in `Python.h`, die bei Limited API gegen die versionsunabhängige Bibliothek bindet, gilt nur für MSVC; unter MinGW-w64 wird das Modul voraussichtlich gegen die versionsgebundene Bibliothek (`python3xx`) gelinkt, die Datei gälte dann nur für die Python-Version, mit der gebaut wurde. Vermutung, beim ersten Bau zu prüfen (Linkziel `python3.dll` anstreben). (d) Hier war kein MinGW-w64-Compiler vorhanden und ließ sich nicht beschaffen; der Windows-Zweig bleibt **ungetestet** (Dokument 02 §5.3). | 02 (5.3, 6, 8, 9), 00 (3.2), 05 |
| 16.10.2026 | **Bahnsperrenschalter: nicht anzeigen, Schalterdatei** *(Durchgang O-9, Dialog, 16.10.2026, Entwurf 86; schließt Dokument 01 §7 Nr. 11)*: **(1)** Die rückseitigen Bahnsperrenschalter erscheinen **gar nicht** im Pult-Fenster, keine Zusatzleiste neben dem Foto. **(2)** Sie werden über `--BASP` des GRAFIK-Interpreters gesetzt und beim Hochfahren der Trommel an das C-Modul übermittelt. **(3)** Neue Aufgaben des C-Moduls: übermittelte Stellungen in einer **Datei neben der Trommel speichern**; werden keine übermittelt, die Stellung **aus dieser Datei entnehmen**; existiert die Datei noch nicht, mit **`000000` anlegen** und `000000` übernehmen. Ersetzt den Standard `000000` ohne Angabe (15.10.2026) und die Aussage „nie eine Konfigurationsdatei“ in `bahnsperre.h`. Dateiname, Format und Fehlerfall als Standardannahmen in Dokument 02 §6, **bestätigt 16.10.2026 (Entwurf 87, „ja, alles ok“)** | 01 (3.4, 7), 02 (3, 6), 04, 05 (O-9) |
| 16.10.2026 | **Töne: Standardannahmen bestätigt, Echo entfällt** *(Durchgang O-10, Dialog, 16.10.2026, Entwurf 88)*: Die Annahmen zu Dokument 03 §5 Nr. 12 bis 14, 17, 21 und 22 sind bestätigt (Einzelheiten Dokument 03 §5 Nr. 24). **Das Echo der Eingaben gibt es in GRAFIK nicht** („Tastatureingaben sind nirgendwo zu sehen“): kein dunkelgelbes Echo im SW-Fenster, kein Ton dafür; Nr. 16 hinfällig. **[überholt am 18.10.2026, Entwurf 104: das SW-Fenster zeigt jedes angenommene Zeichen selbst an, Dok. 09 S3-04 neu]** | 03 (5 Nr. 16, 24), 01 (1.6), 05 (O-10) |
| 18.10.2026 | **SW: Eingabe wird angezeigt, Sperre bei K0 weg** *(Dialog, 18.10.2026, Entwurf 105)*: „Wenn im SW ein Zeichen eingegeben wird, dann muss es dargestellt werden, nur mit dem 011-Befehl.“ („JA, NUR DAS IST RICHTIG.“) **Ersetzt** „ohne Echo“ (Entwurf 88). Ist der Kanal K0 da, wird eingegeben und angezeigt; ist er weg, ist die Taste blockiert (keine Eingabe, keine Anzeige); **es gibt keine wartenden Zeichen** und **kein Echo** beim C 8205; eine Schreibposition wird durch eine Eingabe oder eine Ausgabe belegt und rückt weiter; „Programmende“ als eigene Regel entfällt. **Zeichen in der anderen Lage (07:56):** Die Tastatur sendet zwei Signale (Umschalten, Zeichen, etwa 0,1 s Abstand); der Rechner bekommt zwei Eingaben und durchläuft zwei `011`; ist für die zweite kein `011` aktiv, ist sie blockiert (bei korrektem Eingabeprogramm kommt das nicht vor). Kein Warten, keine Vormerkung. | 09 (S3-04, S3-13, S3-18, §7, §10), 05 (F-48 bis F-51) |
| 16.10.2026 | **Klick und SW-Eingabe: Standardannahmen bestätigt** *(Durchgang O-11, Dialog, 16.10.2026, Entwurf 89, „alles bestätigt“)*: F-15 Nr. 1 (zweiter Klick innerhalb 0,4 s = neuer Tastendruck, Timer neu) und F-16 Nr. 3 bis 6 (Sondertasten, stiller Verwurf nicht angenommener Zeichen, Vormerkung, Fokus mit Titel „Eingabe erwartet“) | 05 (F-15, F-16, O-11), 01 (1.6, 1.7) |
| 16.10.2026 | **Pflege (Durchgang O-12, Dialog, 16.10.2026, Entwurf 90):** `node.js`-Satz in `projekt/Assembler/Dokumentation/C8205_Assembler_Dokumentation.md` **entfernen** (zuerst nur die `.md`, am 16.10.2026 auf Anweisung auch in der maßgeblichen `.odt`, Entwurf 91); **PDF werden nicht geändert**; keine Anforderungs-IDs („mach was du willst“: Register und Teildokumente bleiben); Überschrift und Punkt 3 in §3.6 bereinigt; Aufnahmelänge des Grundgeräuschs 6,0 s (Schleife, endlos) | 00 (3.6, 7), 03, 05 (O-12) |
| 16.10.2026 | **Vorgehen beim Neuprogrammieren: fünf Stufen** *(Durchgang O-13, Dialog, 16.10.2026, Entwurf 93, „so wollen wir vorgehen“)*: Stufe 1 Kern und Trommel (ohne Fenster, ohne Ton), Stufe 2 Pult-Fenster, Stufe 3 SW-Fenster, Stufe 4 Töne, Stufe 5 Umschaltung `--MODUS` und Aufräumen; Paket und Abnahme nach jeder Stufe; bis Stufe 5 eigenes Startskript für GRAFIK, TEST unberührt. Freigabe für den Beginn von Stufe 1 noch nicht ausdrücklich erteilt *(Stand 18.10.2026, Entwurf 120: Stufen 1, 2 und 3 abgenommen)* | 04 (6), 05 (O-13) |
| 17.10.2026 | **`LOCHSTREIFENKORB` in jedem Leser-Ordner** *(Dialog, 17.10.2026, Entwurf 94; zu Stufe 1)*: In **jedem Leser-Ordner** gibt es einen Unterordner `LOCHSTREIFENKORB`, **durchgehend in Großbuchstaben** (bestätigt schon 16.10.2026, Entwurf 35: gelesene Dateien wandern dorthin). **Leere Korb-Ordner werden nicht mit ins Paket gelegt**; der Leser legt sie bei Bedarf selbst an (so ist es im Programm). Eine gewöhnliche **Datei** namens `LOCHSTREIFENKORB` im Leserordner: **kann bleiben** wie bisher (wird beim Suchen wie ein Lochstreifen behandelt, beim Verschieben Fehlermeldung); keine Änderung | 07 (3a) |
| 17.10.2026 | **Tastenzeit 0,25 s** *(Test des Projektinhabers, 17.10.2026, Entwurf 96; ändert 15./16.10.2026)*: Alle Tasten mit Aufleuchten (Klick-Tasten, E, M, G, Ü, ST, Eingabetasten) zeigen die gedrückte Grafik **0,25 s** statt 0,4 s; weiterhin einstellbar. Dokument 01 §1.7, Dokument 06 angepasst; die älteren Zeilen dieses Registers mit „0,4 s“ gelten dadurch nicht mehr | 01 (1.7), 06 |
| 17.10.2026 | **Kanaltasten K0 bis K3 rasten ein, immer genau eine** *(Test des Projektinhabers, 17.10.2026, Entwurf 96; ersetzt Entwurf 76 und 77)*: Radio-Verhalten, auch bei Stellung R; Start: K0 eingerastet (vorher: keine Kanaltaste rastet). Dokument 01 (§1.3, §1.7, §1.8 Nr. 3), Dokument 06 angepasst | 01 (1.3, 1.7, 1.8), 06 |
| 17.10.2026 | **Töne des Rechners schon in Stufe 2** *(Test des Projektinhabers, 17.10.2026, Entwurf 96; zieht Teile von Stufe 4 vor)*: `fade_in` beim Einschalten (B rot), Grundgeräusch als Schleife ab B grün, `fade_out` beim Ausschalten, alles aus bei X und Strg+C; `--STUMM` ohne Ton. Schreibwerk-, Leser- und Stanzertöne bleiben Stufe 4. Nicht hörbar geprüft | 03, 04 (6), 08 |
| 17.10.2026 | **Eingabetasten bei Stellung R** *(bestätigt 17.10.2026, Entwurf 96)*: Die Eingabetasten sind nicht mechanisch gesperrt, sondern nur elektronisch verriegelt: Sie lassen sich klicken, **wenn der Rechner gerade auf eine K0-Eingabe wartet**, sonst nicht. Ändert die Zeile „Rollensperre und Entriegelung“ (15.10.2026, „R verriegelt gleichzeitig die Eingabetasten“) und Dokument 01 §3.5 | 01 (3.5) |
| 17.10.2026 | **Thread-Regel im Pult-Betrieb (Fehlerbehebung, Entwurf 96):** Pult-Tasten werden im Rechner-Thread ausgeführt, nie im Fenster-Thread (E im Eingabe-Halt blockierte das Fenster); Strg+C zweimal beendet sofort | 08 |
| 17.10.2026 | **Hardware-Check-Fenster `--HWCHECK`** *(Dialog, 17.10.2026, Entwurf 97)*: zweites, verschiebbares Fenster in Mindestgröße mit BZ, BR (AR-Teil und OR), AC und <<AR>> (Speicherinhalt an der Adresse in AR), alles oktal, AR/AC/<<AR>> in Vierergruppen; bleibt aufgeblendet, solange der Grafik-Interpreter läuft (nicht schließbar); ohne Rückwirkung auf den Rechner. Standardannahmen in Dokument 01 §1.9 Nr. 5, nicht bestätigt | 01 (1.9), 08 |
| 17.10.2026 | **HW-Check-Fenster um Spurnummer und Sektornummer erweitert** *(Dialog, 17.10.2026, Entwurf 98)*: neue Zeile „Spur Sektor“ zwischen BR und AC (Adresse im Speicheradressregister AR; Spur = AR ÷ 32, Sektor = AR mod 32, oktal 3 und 2 Stellen); jetzt fünf Zeilen. Auslegung Dokument 01 §1.9 Nr. 5 (f), nicht bestätigt | 01 (1.9), 08 |
| 17.10.2026 | **Wirkung von E und M+ E im Halt** *(Dialog, 17.10.2026, Entwurf 99; **berichtigt 18.10.2026**)*: Erste Fassung („jedes E erhöht BZ um 1, unabhängig vom Trommelinhalt“) **gestrichen**. Es gilt, **wie im Interpreter programmiert** (0.03-015, GRAFIK G2-012): E ohne M führt den Befehl aus (Niederdrücken `E+` = Phase IV und I, Loslassen `E-` = Phase II und III); unter M erhöht das Niederdrücken BZ und AR um 1 (AR := BZ), AC-Adressfeld = BZ+1, Lampenreihe AR zeigt AR; Loslassen unter M ohne Wirkung. Dokument 01 §1.10 neu gefasst | 01 (1.10), 06 (M-35), 08 |
| 17.10.2026 | **HW-Check-Fenster: Vierergruppen von links** *(Test des Projektinhabers, 17.10.2026, Entwurf 99; ersetzt „von rechts“ aus Entwurf 97)*: AC und <<AR>> (11 Stellen) werden als **4 + 4 + 3** gruppiert, z. B. `2206 0635 124`, Null als `0000 0000 000` (vorher `220 6063 5124`, `000 0000 0000`). Platzhalter bei nicht lesbarem Speicher bleibt `---- ---- ---`. Dokument 01 §1.9 Nr. 5 (a) berichtigt | 01 (1.9), 08 |
<!-- REGISTER-ENDE -->

## Anhang B Übersetzungstabelle alt → neu

### B.1 Dokumente

| Altdokument / Gegenstand | Ziel (Abschnitt) |
|---|---|
| 00 Hauptdokument | §2 Register → Anhang A der GRAFIK_Beschreibung; §3.1 bis §3.5 → Beschreibung §9, Bestandsdokumente; §3.6 → Beschreibung §1; §4 offene Entscheidungen → Offene Punkte; §6 Änderungsverzeichnis → entfällt (Entwurfsverlauf, siehe S6-09) |
| 01 Pult-Fenster | → Beschreibung §3, §8, §9; Offenes → §10 |
| 02 Trommel | → Beschreibung §7; Testergebnisse → Prüfverfahren §7 |
| 03 Ton | → Beschreibung §6; Bezug zu `ton/SW_Ton_Beschreibung.md` |
| 04 Prüfbericht Module | Befunde zur Modulaufteilung → Beschreibung („Aufbau der GRAFIK-Module“, Kurzfassung in §1 oder eigener Abschnitt, Entscheidung O6-4); Rest entfällt |
| 05 Review (F-01 bis F-23 und folgende) | Entscheidungen stehen im Register; **offene** Befunde → Offene Punkte; Rest entfällt |
| 06 Mausbedienung | → Beschreibung §4 (M-15 bis M-35 mit Nummern) |
| 07 bis 09 Stufen 1 bis 3 | Anforderungen und Ergebnisse → Beschreibung; Abnahmekriterien und echte Läufe → Prüfverfahren §8; Handliste Dok. 09 §9 → Prüfverfahren §7 |
| 10 Stufe 4 | Anforderungen S4-xx → Beschreibung §6; Abnahme, Hörprüfung, B-2 → Prüfverfahren §7, §8, §9 |
| 11 Stufe 5 | S5-xx → Beschreibung §1, §2; A5-x → Prüfverfahren §8; A5-8 → §9 |
| 12 (dieses) | nach Abschluss von Stufe 6 entfällt es mit den übrigen (Ergebnis steht im Prüfverfahren) |
| `CHECKPOINT_Stufe2.md`, `CHECKPOINT_Stufe3.md` | **Triage** (S6-04): „NICHT geprüft“-Abschnitte und Warnungen prüfen; durch spätere Abnahme erledigte entfallen, offene und Warnhinweise → Offene Punkte bzw. Hinweise |
| `CHECKPOINT_G5-001` bis `G5-010` | Offene Punkte und „Nicht geprüft“ → Offene Punkte; sonst entfallen (Verlauf steht in Dokument 00) |
| `AENDERUNG_…0_03-015.md`, `…0_03-016.md` | Inhalt → `C8205-Versionierung.md` (S6-03); **erst danach löschen** |
| `HWCHECK_HW-003.md` | Ursachen und Behebung → Beschreibung §8 (kurz) |
| `ton/SW_Ton_Beschreibung.md` | **bleibt** (Teil B bis D); Teil A bekommt den Hinweis, dass die Anforderungen in die GRAFIK_Beschreibung §6 übernommen sind; Verweise auf Dok. 01 bis 03 umstellen |
| `Pult_Tastentest_GRAFIK.md` | wird Prüfverfahren §5; die Datei entfällt danach, die Verweise werden umgestellt |

### B.2 Kennungsfamilien

Gezählt per Textsuche in Dok. 00 bis 12, `CHECKPOINT_*`, `AENDERUNG_*`, `HWCHECK_HW-003.md`, `ton/SW_Ton_Beschreibung.md`, `Pult_Tastentest_GRAFIK.md`. „Erwähnungen“ sind Fundstellen, nicht verschiedene Nummern. Die Spalte „Zielabschnitt“ ist ein **Vorschlag** und wird beim Schreiben je Nummer bestätigt (Familien mit unsicherer Bedeutung sind so vermerkt). Dokument-/Abschnittsnummern der Ziele: Beschreibung §n, Prüfverfahren §n.

| Familie | Bedeutung | Bereich | Erwähnungen | Fundstellen (Auswahl, Anzahl) | Zielabschnitt (Vorschlag) |
|---|---|---|---|---|---|
| F- | Review-Befunde (Dok. 05) und Entscheidungsdatei; **F-15 und F-16 doppelt belegt** (Review-Befunde und Entscheidungsdatei F-15 bis F-33), im Register unterscheidbar nur über Datum und Text | F-01 bis F-65 | 683 | Dok. 00 (281), Dok. 05 (171), CP Stufe3 (85), Dok. 09 (60), Dok. 01 (27), Dok. 03 (24) | Entschiedenes: Register (Anhang A) und das jeweilige Sachthema in §1 bis §9; Offenes: §10. In B.1 nur als Bereich F-01 bis F-65 geführt, Feinzuordnung beim Schreiben |
| M- | Mausbedienung (Dok. 06, M-15 bis M-35 und weitere) | M-15 bis M-35 | 77 | Dok. 06 (51), Dok. 00 (8), Dok. 12 (6), Dok. 01 (3), Dok. 05 (3), CP Stufe2 (2) | Beschreibung §4 |
| S3- | Anforderungen Stufe 3 (Dok. 09: SW-Fenster, K0-Eingabe) | S3-01 bis S3-18 | 311 | Dok. 09 (136), CP Stufe3 (81), Dok. 00 (51), Dok. 05 (18), Dok. 10 (13), Dok. 01 (10) | Beschreibung §5; Handlisten und Abnahme: Prüfverfahren §7 und §8 |
| S4- | Anforderungen Stufe 4 (Dok. 10: Töne) | S4-01 bis S4-19 | 124 | Dok. 10 (86), Dok. 00 (15), CP Stufe3 (15), Dok. 12 (3), SW_Ton (2), Dok. 05 (1) | Beschreibung §6; Abnahme und Hörprüfung: Prüfverfahren §7 bis §9 |
| S5- | Anforderungen Stufe 5 (Dok. 11: Betriebsmodi, Start) | S5-01 bis S5-12 | 39 | Dok. 11 (27), CP G5-004 (6), Dok. 00 (3), Dok. 12 (2), CP G5-010 (1) | Beschreibung §1 und §2 |
| S6- | Anforderungen Stufe 6 (Dok. 12, dieses Vorhaben) | S6-01 bis S6-12 | 56 | Dok. 12 (40), Dok. 00 (8), CP G6-001 (4), CP G6-002 (2), CP G6-003 (2) | entfällt mit Dok. 12; Ergebnis im Prüfverfahren §8 |
| O4- | Offene Fragen Stufe 4 (Dok. 10) | O4-01 bis O4-18 | 168 | Dok. 10 (67), Dok. 05 (40), CP Stufe3 (32), Dok. 00 (19), Dok. 03 (5), Dok. 04 (4) | entschiedene: Register und §6; offene: §10 |
| O5- | Offene Fragen Stufe 5 (Dok. 11) | O5-01 bis O5-05 | 33 | Dok. 11 (9), Dok. 00 (6), CP G5-005 (5), CP G5-004 (4), CP G5-006 (4), Dok. 10 (1) | entschiedene: Register und §1/§2; offene (O5-3 Windows): Prüfverfahren §9 |
| O6- | Offene Fragen Stufe 6 (Dok. 12) | O6-01 bis O6-07 | 50 | Dok. 12 (14), Dok. 00 (12), CP G6-002 (11), CP G6-001 (7), CP G6-003 (6) | entfallen mit Dok. 12; Entscheidungen sind in den Zieldokumenten umgesetzt |
| U- | in Dok. 09 und 10 (z. B. U-9, U-10, U-11 neben S3-14 und Z-1); genaue Bedeutung beim Schreiben je Fundstelle klären | U-01 bis U-12 | 243 | CP Stufe3 (94), Dok. 09 (76), Dok. 00 (38), Dok. 05 (16), Dok. 10 (7), Dok. 03 (5) | Beschreibung §5 (Dok. 09) bzw. §6 (Dok. 10); Handprüfung: Prüfverfahren §7 |
| B- | Befunde (Dok. 09, 10, 11, Checkpoints); **B-2 = Windows-Bau tonmisch** | B-01 bis B-09 | 174 | Dok. 09 (52), Dok. 10 (33), CP Stufe3 (33), Dok. 00 (18), Dok. 05 (8), CP G5-007 (8) | Prüfverfahren §10 (Bekannte Befunde); B-2: Prüfverfahren §9 |
| A- | Abnahmekriterien (A-1 bis A-8; Dok. 09) | A-01 bis A-08 | 79 | Dok. 09 (35), CP Stufe3 (25), Dok. 00 (18), Dok. 05 (1) | Prüfverfahren §8 |
| A5- | Abnahmekriterien Stufe 5 (Dok. 11); **A5-8 = Windows** | A5-01 bis A5-08 | 100 | Dok. 11 (20), CP G5-010 (14), CP G5-009 (13), Dok. 00 (11), CP G5-008 (9), Dok. 12 (7) | Prüfverfahren §8; A5-8: §9 |
| A6- | Abnahmekriterien Stufe 6 (Dok. 12) | A6-01 bis A6-08 | 27 | Dok. 12 (23), Dok. 00 (2), CP G6-001 (2) | Dok. 12 entfällt; Ergebnis im Prüfverfahren §8 |
| G1- | Änderungskennung (Verlauf Dok. 00 §6), zur Stufe 1; Bedeutung des Buchstaben-Zahlen-Schemas beim Schreiben bestätigen | G1-02 bis G1-02 | 2 | Dok. 07 (1), CP Stufe2 (1) | Versionierung (Zählung der GRAFIK-Module, S6-03/S6-09) |
| G2- | Änderungskennung (Verlauf Dok. 00 §6), z. B. G2-003 `ton/`, G2-011/-012 E und M | G2-02 bis G2-12 | 38 | CP Stufe2 (18), Dok. 01 (5), AENDERUNG 0.03-015 (4), Dok. 00 (2), Dok. 06 (2), Dok. 10 (2) | Versionierung; Offenes aus CHECKPOINT_Stufe2: §10 (Triage S6-04) |
| G3- | Änderungskennung (Verlauf Dok. 00 §6), z. B. G3-004 Zeichenlage SW | G3-01 bis G3-08 | 72 | CP Stufe3 (38), Dok. 09 (18), Dok. 00 (9), AENDERUNG 0.03-016 (4), Dok. 05 (2), Dok. 10 (1) | Versionierung; Offenes aus CHECKPOINT_Stufe3: §10 (Triage S6-04) |
| G4- | Änderungskennung (Verlauf Dok. 00 §6), z. B. G4-005, G4-007 | G4-01 bis G4-19 | 52 | Dok. 10 (37), Dok. 09 (5), Dok. 00 (4), CP Stufe3 (2), Dok. 01 (1), Dok. 05 (1) | Versionierung; Offenes: §10 |
| G5- | Änderungskennung Stufe 5 (nicht zu verwechseln mit den Dateien `CHECKPOINT_G5-001` bis `-010`) | G5-01 bis G5-10 | 59 | Dok. 11 (17), Dok. 00 (8), Dok. 12 (7), Dok. 10 (5), Dok. 04 (3), CP G5-004 (3) | Versionierung; Offenes: §10 (Triage S6-04) |
| G6- | Stufe 6 (Dateien `CHECKPOINT_G6-001` bis `-004`; Dok. 12 nennt „Checkpoint G6-nnn“) | G6-01 bis G6-04 | 15 | Dok. 12 (5), Dok. 00 (4), CP G6-003 (3), CP G6-002 (2), CP G6-001 (1) | entfallen nach Abschluss; Meilenstein in der Versionierung |
| SWTK- | Tk-Testläufe des SW-Fensters (Tk-Testskripte) | SWTK-01 bis SWTK-04 | 46 | Dok. 09 (23), CP Stufe3 (15), Dok. 00 (4), Dok. 05 (4) | Prüfverfahren §3 (Testskripte) und §7 |
| Z- | Rückfragen in Dok. 09 (Z-1, Z-2; Z-1 am 07:56 beantwortet, betrifft Vormerkung) | Z-01 bis Z-02 | 33 | Dok. 09 (12), CP Stufe3 (12), Dok. 00 (7), Dok. 05 (2) | Beschreibung §5; Prüfverfahren §10 |
| VM- | Änderungskennung zur Vormerkung (VM-001, Stufe 3) | VM-01 bis VM-03 | 45 | CP Stufe3 (19), Dok. 09 (18), Dok. 05 (5), Dok. 00 (3) | Beschreibung §5 |
| RLA- | Testlauf-Kennung (RLA-001/-002; RLA-002 weist den Gravis als `[BEKANNT]` aus) | RLA-01 bis RLA-02 | 12 | Dok. 09 (6), CP Stufe3 (5), Dok. 00 (1) | Prüfverfahren §6 (R300-Eingabe) |
| DL- | Änderungskennung (DL-003) | DL-01 bis DL-03 | 8 | CP Stufe3 (4), CP Stufe2 (2), Dok. 00 (1), Dok. 09 (1) | Beschreibung §2 (Schalter), Prüfverfahren §3 |
| HZ- | Änderungskennung zur Haltzeit (HZ-001/-002, `grafik_haltzeit.py`) | HZ-01 bis HZ-03 | 5 | Dok. 10 (5) | Beschreibung §8.3 (Haltzeit; Verweis in §6.5) |
| FL- | Änderungskennung zur Fensterlage (FL-001, `grafik_fensterlage.py`) | FL-01 bis FL-01 | 3 | Dok. 00 (1), Dok. 05 (1), Dok. 10 (1) | Beschreibung §3 |
| HW- | Änderungskennung zum Hardware-Check (HW-003) | HW-01 bis HW-04 | 20 | Dok. 12 (5), Dok. 00 (3), AENDERUNG 0.03-015 (3), Dok. 08 (2), CP Stufe2 (2), CP Stufe3 (2) | Beschreibung §8 |
| E- | E-1 bis E-4 (Dok. 05/09: E unter M) und E-001 (Änderung) | E-01 bis E-04 | 13 | CP Stufe3 (8), Dok. 00 (2), Dok. 09 (2), Dok. 05 (1) | Beschreibung §3; Versionierung 0.03-015 |
| D- | Entscheidungspunkte Ton (D-8, D-9, D-13; Dok. 03, SW_Ton) | D-01 bis D-13 | 65 | Dok. 00 (20), SW_Ton (19), Dok. 03 (18), Dok. 05 (8) | Beschreibung §6 und `ton/SW_Ton_Beschreibung.md` (bleibt) |
| O- | O-1 bis O-12 der ersten Pakete (Dok. 00 bis 03, 05, 09) | O-01 bis O-13 | 79 | Dok. 00 (35), Dok. 05 (18), Dok. 02 (13), Dok. 09 (5), Dok. 01 (4), CP Stufe3 (3) | entschiedene: Register; offene: §10 |
| SW- | SW-Kennungen (SW_Ton) | SW-01 bis SW-07 | 14 | SW_Ton (14) | `ton/SW_Ton_Beschreibung.md` (bleibt) |
| LS- | Lochstreifen/Leser-Töne (SW_Ton) | LS-01 bis LS-05 | 11 | SW_Ton (11) | `ton/SW_Ton_Beschreibung.md` (bleibt) |
| ALL- | Sammelkennung (SW_Ton) | ALL-01 bis ALL-03 | 6 | SW_Ton (6) | `ton/SW_Ton_Beschreibung.md` (bleibt) |
| PTK- | Pult-Tastentest (nur in CHECKPOINT_Stufe3 erwähnt) | PTK-01 bis PTK-01 | 3 | C8205-Interpreter-Pult_Ta (2), CP Stufe3 (1) | Prüfverfahren §5 |

Nicht aufgenommen (Treffer ohne Kennungscharakter, z. B. Normen, Zeichen, Teilenummern): BIS, C, RE, UTF.

### B.3 Verweise im Code und in Dokumenten (später umzustellen)

**Code** (Kommentare und Docstrings; Zählung per Textsuche, die Zahlen weichen von Dok. 12 §2 ab, weil dort ein weiteres Muster mitgezählt wurde: hier 58 Treffer in 22 Dateien):

| Datei | Treffer | Maßnahme |
|---|---|---|
| `c-module/python/c8205_ton_methoden.h` | 1 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `c-module/tonmisch.c` | 1 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `c-module/tonmisch.h` | 1 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `c8205_grafik.py` | 8 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_geraete.py` | 2 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_geraeteton.py` | 2 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_k0.py` | 2 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_pult.py` | 10 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_pult_fenster.py` | 2 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_rechnerton.py` | 1 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_schreibwerk.py` | 2 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_sw.py` | 7 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_sw_fenster.py` | 5 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_ton.py` | 1 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_tonmisch.py` | 2 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_tonmisch_c.py` | 1 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `grafik-interpreter-module/grafik_trommel.py` | 2 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `testscripte/grafik_checkpoint5_tests.py` | 1 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `testscripte/grafik_gleichwertigkeit.py` | 1 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `testscripte/grafik_sw_pult_test.py` | 2 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `testscripte/grafik_sw_vormerkung_s3_13.py` | 2 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |
| `testscripte/r300_eingabe_log_auswerten.py` | 2 | auf neue Abschnitte umstellen (S6-07, nur Kommentare) |

**Dokumente außerhalb der Anforderungspakete:**

| Datei | Treffer | Maßnahme |
|---|---|---|
| `README.md` | 2 | Verweise umstellen (S6-07/S6-08) |
| `README.en.md` | 2 | Verweise umstellen (S6-07/S6-08) |
| `markdown-dateien/C8205-Interpreter-Python_Interpreter.md` | 1 | Verweise umstellen (S6-07/S6-08) |
| `markdown-dateien/C8205-Interpreter-Bedienpult_mit_Schaltern.md` | 1 | Verweise umstellen (S6-07/S6-08) |
| `markdown-dateien/C8205-Projektstruktur.md` | 5 | Verweise umstellen (S6-07/S6-08) |
| `markdown-dateien/C8205-Interpreter-Pult_Tastentest_GRAFIK.md` | 2 | Verweise umstellen (S6-07/S6-08) |
| `markdown-dateien/C8205-Interpreter-Lochstreifenleser.md` | 1 | Verweise umstellen (S6-07/S6-08) |
| `ton/SW_Ton_Beschreibung.md` | 15 | Verweise umstellen (S6-07/S6-08) |
