# Python-Interpreter für den C 8205 (`c8205_interp.py`)

Version: 0.03-014

Stand: 14.10.2026 (Sollwerte der Referenzläufe in 13.5 auf den aktuellen Stand gebracht; Aufrufparameter `--BASP` für die Bahnsperrenschalter, nur der Parameter; zuvor 13.10.2026: Testmarke `#TROMMEL=LEER` / `#TROMMEL=MP`; zuvor 10.10.2026: Fenster „SW Ausgabe“ bleibt immer offen, Kopieren mit der Maus, Schalter `--zwischenablage`; zuvor 09.10.2026: Versionsnummer, Schalter `--version`; zuvor 08.10.2026: Trommel als persistente Datei, Schalter `--trommel`; zuvor 04.10.2026: Geräte-Zeilen in der Testdatei auch für Leser und Stanzer). Diese Datei beschreibt den Python-Interpreter, seine Bedienung und alles, was zur Erzeugung
einer menschenzentrierten Bedienungsanleitung (PDF) erforderlich ist. Die Regeln des Rechners selbst stehen
**nicht** hier, sondern in den übrigen Regelwerk-Dateien; hier wird nur auf sie verwiesen (Abschnitt 12).

## Inhaltsverzeichnis

1. Zweck und Einordnung
2. Aufbau des Interpreters
3. Voraussetzungen und Installation
4. Schnellstart
5. Aufruf und Schalter
6. Die Testdatei
7. Die Tastenfolge
8. Geräte und Kanäle (Ein-/Ausgabe)
9. Ausgaben, Protokoll und Endzustand
10. Fehlermeldungen und Abhilfe
11. Abweichungen, Erweiterungen und offene Punkte
12. Bezug zu den Regelwerk-Dateien
13. Beispiele
14. Vorgaben für die PDF-Bedienungsanleitung

---

## 1. Zweck und Einordnung

Der Interpreter führt Programme des Rechners C 8205 **interpretativ** aus: Er läuft den Knotengraphen des
Befehlsablaufs (Phasen I bis IV) ab und bildet Register, Flags, Trommelspeicher und Peripherie nach. Alle
Zeiten (Wortzeit, Wartezeit auf die Trommel) sind 0; die Trommeldrehung wird nicht nachgebildet. Die Trommel
selbst ist eine **persistente Textdatei** (`virtuelle_Geraete/Trommel/trommel.txt`, Abschnitt 8.5): Ihr Inhalt
bleibt über Tests und Aufrufe hinweg erhalten.

Er dient dazu,
- Testprogramme des C 8205 nachvollziehbar durchzurechnen (Protokoll Knoten für Knoten),
- das Verhalten des Regelwerks zu prüfen,
- Ein-/Ausgabe (Schreibwerk, Lochbandleser, Stanzer, Pult-Tastatur) an einem Terminal zu erproben.


Grundsatz (aus der Datei `C8205-Interpreter-Durchführung_eines_Tests.md`): Der Graph wird wortlautgetreu
abgelaufen. Unklares wird als **Stub** gemeldet (Abbruch mit Meldung) und nie stillschweigend „repariert“.

## 2. Aufbau des Interpreters

Der Interpreter wird **nicht** aus den Regelwerk-Dateien erzeugt, sondern liest sie zur Laufzeit:

| Baustein | Herkunft | Inhalt |
|---|---|---|
| Knotengraph | `C8205-Interpreter-Eingänge_der_Knoten.md` (im Verzeichnis `--mdverz`) | Knoten, Typen, Ein-/Ausgänge, Verzweigungen |
| Variablentabelle T2 | `C8205-Interpreter-Beschreibung_der_Knoten.md` (im Verzeichnis `--mdverz`) | Bedeutung der ANWEISUNG-nnn |
| Funktionen je ANWEISUNG | handgeschrieben in `c8205_interp.py` (`a001`, `a021`, `t002` …) | Wirkung auf Register, Flags, Speicher |
| Kodetabelle (Tabelle 1) | **in das Skript eingebettet** (`TABELLE1`), erzeugt aus `C8205-Interpreter-Kodetabellen.md`, Abschnitt 1.4 | Zeichen, Lochbilder, Ein-/Ausgabe-Adressen |
| Geräte | handgeschrieben (`Leser`, `Stanzer`, `K0Quelle`, `sw_schreibe`) | Peripherie |
| Trommel | Klasse `Trommel` in `c8205_interp.py`; Datei `virtuelle_Geraete/Trommel/trommel.txt` (Schalter `--trommel`) | Speicher: 4096 Zellen, jeder Lese- und Schreibzugriff eines Befehls läuft über die Klasse (Abschnitt 8.5) |

Die Funktionen tragen die Nummer der ANWEISUNG (`a` = Anweisung, `t` = Test). Ändert sich der Graph oder T2, muss
nur das Skript angepasst werden, wenn eine ANWEISUNG neu ist oder anders wirkt. Fehlt zu einer ANWEISUNG eine
Funktion, meldet der Interpreter einen Stub.

Ablauf eines Aufrufs: **Trommeldatei prüfen und laden** (einmal, vor dem ersten Test; Abschnitt 8.5) und dann für jede
Testdatei: Testdatei einlesen → **formale Prüfung** → Zeilen der Testdatei auf die Trommel schreiben (sie überlagern den
Trommelinhalt) → Tastenfolge auswerten (Ausgangszustand der Register und Flags) → Knotengraph ab Konnektor B ablaufen →
Ergebnis ausgeben. Register und Flags beginnen bei jedem Test neu, die Trommel nicht.

## 3. Voraussetzungen und Installation

- **Python 3** (nur Standardbibliothek, nichts zu installieren). Die Terminal-Eingabe auf Kanal K0
  (Standardfall ohne `--k0`, Abschnitt 8.4) funktioniert plattformübergreifend: unter Linux/macOS über
  das Modul `termios`, unter Windows über das Modul `msvcrt` (beide Standardbibliothek, die Auswahl
  erfolgt automatisch anhand des laufenden Betriebssystems).
- **Verzeichnis `markdown-dateien/` neben `c8205_interp.py`** (Vorgabe für `--mdverz`, Abschnitt 5.1):
  enthält `C8205-Interpreter-Eingänge_der_Knoten.md` und `C8205-Interpreter-Beschreibung_der_Knoten.md`.
- **Trommeldatei `virtuelle_Geraete/Trommel/trommel.txt` neben `c8205_interp.py`** (Vorgabe für `--trommel`, Abschnitt 5.1): genau
  4096 Zeilen, les- und beschreibbar. Der Interpreter legt sie nie selbst an. Eine leere Trommel erzeugt
  `python3 testscripte/erzeuge_leere_trommel.py` (Abschnitt 8.5).
- Optional der Wrapper `c8205_interpreter.sh` (Linux/macOS) bzw. `c8205_interpreter.bat` (Windows, Abschnitt 5.2), der
  ebenfalls im Ordner des Skripts liegen muss, weil er `python3 c8205_interp.py` relativ aufruft.
- Ein Terminal mit ANSI-Farben (für Gelb und Rot; ohne Terminal oder mit gesetztem `NO_COLOR` erscheint reiner Text).
- **Nur für `--SW-TERMINAL`:** `tkinter` (Linux: `sudo apt install python3-tk`; Windows/macOS im Python-Installer von python.org enthalten) und eine grafische Oberfläche. Zum Kopieren aus dem Fenster unter Linux optional `xsel`/`xclip` (X11) bzw. `wl-clipboard` (Wayland); unter Windows ist nichts nachzuinstallieren (Win32-API über `ctypes`).

Der Dateiname der Eingänge-Datei enthält ein „ä“. Findet der Interpreter sie nicht, kann das Verzeichnis mit
`--mdverz VERZ` angegeben werden.

## 4. Schnellstart

Einmalig (und immer, wenn eine leere Trommel gebraucht wird, Abschnitt 8.5) die Trommeldatei erzeugen:

```
python3 testscripte/erzeuge_leere_trommel.py
```

Dann den Test starten:

```
python3 c8205_interp.py --MODUS=TEST Tests/0015-030.txt
```

Das führt den Test aus, gibt die Zeichen der Ausgabebefehle auf dem Terminal aus (dunkelgelb) und zeigt die
Endzeile (`Ende: …`). Mit Wrapper und Protokolldatei:

```
./c8205_interpreter.sh 0015-030.txt        # schreibt Test-Protokolle/0015-030.log
```

Erwartet wird für den Test `0015-030` die Ausgabe `Jahr 1972` (Abschnitt 13.1).

## 5. Aufruf und Schalter

### 5.1 Kommandozeile

```
python3 c8205_interp.py --MODUS=TEST [--mdverz VERZ] [--trommel PFAD] [--out VERZ|DATEI.log]
        [--leser1 PFAD] [--leser2 PFAD] [--stanzer1 PFAD] [--sw-ausgabe PFAD]
        [--k0 datei=PFAD] [--knotentest] [--NO-TERMOUT] [--SW-TERMINAL] [--zwischenablage auto|tk|system]
        [--pruefe-stanzer1 DATEI] [--pruefe-sw-ausgabe DATEI] [--BASP abcdef]  TEST.txt [TEST2.txt ...]
python3 c8205_interp.py --version
```

| Schalter | Wirkung | Vorgabe |
|---|---|---|
| `TEST.txt` | Testdatei(en) (Abschnitt 6). Ist der Pfad nicht vorhanden, wird der Dateiname unterhalb des aktuellen Ordners und des Skript-Ordners gesucht (Groß-/Kleinschreibung egal). Bei mehreren Treffern werden sie aufgelistet und der Test startet nicht. | – |
| `--MODUS TEST\|GRAFIK` | Betriebsart (auch `--modus`, `--MODUS=X`; Groß-/Kleinschreibung gleich; der letzte Wert gewinnt). **Ohne Angabe startet GRAFIK** (Pult- und SW-Fenster). Testläufe mit Testdatei brauchen `--MODUS=TEST`; eine Testdatei im Modus GRAFIK wird ignoriert und mit Hinweis auf `stderr` gemeldet. Unbekannter Wert: Rückkehrcode 2. `--version` und `--help` gelten in jedem Modus. Die Wrapper (Abschnitt 5.2) setzen `--MODUS=TEST`. | `GRAFIK` |
| `--mdverz VERZ` | Verzeichnis mit den beiden Regelwerk-Dateien `C8205-Interpreter-Eingänge_der_Knoten.md` (Knotengraph) und `C8205-Interpreter-Beschreibung_der_Knoten.md` (Variablentabelle T2); fehlt eine der beiden darin, bricht der Start mit Fehlermeldung ab. Ersetzt die früheren getrennten Schalter `--graph`/`--t2`. | `markdown-dateien/` neben dem Skript |
| `--trommel PFAD` | Trommeldatei, der persistente Speicher des Interpreters: 4096 Zeilen `aaaa: ttttttttttt` (Abschnitt 8.5). Sie wird einmal vor dem ersten Test formal geprüft und zum Lesen und Schreiben geöffnet; fehlt sie oder ist sie fehlerhaft, startet kein Test (Rückkehrcode 16). Der Schalter gilt für den ganzen Aufruf und ist **nur auf der Kommandozeile** möglich, nicht als Zeile der Testdatei. | `virtuelle_Geraete/Trommel/trommel.txt` neben dem Skript |
| `--out …` | Mit Dateiendung (z. B. `Protokolle/t1.log`): Protokoll genau in diese Datei (Ordner werden angelegt; nur mit **einem** Test). Ohne Endung: Ordner, Protokoll dann in `ORDNER/<Testname>/protokoll.txt`. | `Test-Protokolle/` im Skript-Ordner |
| `--leser1 PFAD`, `--leser2 PFAD` | Lochstreifen (Datei oder Verzeichnis) für Leser 1 (Kanal K1) bzw. 2 (K2); alternativ als Zeile `--leser1 PFAD` bzw. `--leser2 PFAD` in der Testdatei (Abschnitt 6, der Schalter hat Vorrang) | nicht angegeben → keine Eingabe auf K1/K2 möglich |
| `--stanzer1 PFAD` | Ausgabedatei/-verzeichnis des Stanzers 1 (Kanal K1); alternativ als Zeile `--stanzer1 PFAD` in der Testdatei (Abschnitt 6, der Schalter hat Vorrang) | nicht angegeben → keine Ausgabe auf K1 möglich (auch nicht am Terminal) |
| `--sw-ausgabe PFAD` | Ausgabedatei/-verzeichnis für die Schreibwerk-Ausgabe (Kanal K2, Abschnitt 8.1); alternativ als Zeile `--sw-ausgabe PFAD` in der Testdatei (Abschnitt 6, der Schalter hat Vorrang) | nicht angegeben → Ausgabe geht stattdessen ans Terminal (dunkelgelb) |
| `--SW-TERMINAL` | Öffnet neben dem Terminal ein Textfenster **„SW Ausgabe“** (nur Text, 130 Zeichen × 36 Zeilen, verschiebbar, Vorgabe rechts unten auf dem Desktop) und gibt jede Schreibwerk-Ausgabe (Kanal K2) **zusätzlich** dort aus, **gleichgültig ob `--sw-ausgabe` gesetzt ist**; außerdem erscheint jede angenommene Eingabe über K0 (T oder SW) als **Echo in Dunkelgelb** (Abschnitt 8.4); die Wirkung von `--sw-ausgabe` bleibt unverändert (Datei, ohne den Schalter Terminal, Abschnitt 8.1). Das Fenster bleibt auch nach dem Ende aller Tests des Aufrufs **immer offen**, bis es mit Klick auf X geschlossen wird. Der Text lässt sich mit der Maus markieren und kopieren (Abschnitt 8.1). Das Fenster läuft als eigener Prozess und braucht `tkinter` und eine grafische Oberfläche; fehlt eines davon, erscheint eine Warnung und der Test läuft ohne Fenster. Der Schalter wird bei der Durchführung des Tests ausgewertet (Durchführung eines Tests, 6.3.1). **Nur Kommandozeile:** als Zeile in der Testdatei ist er ein Formfehler (Abschnitt 6, Rückkehrcode 16) | nicht angegeben → AUS (kein Fenster) |
| `--zwischenablage auto\|tk\|system` | Kopierverfahren des Fensters „SW Ausgabe“ (nur mit `--SW-TERMINAL`, Abschnitt 8.1): `auto` legt den Text zuerst über ein Systemprogramm in die Zwischenablage (Windows: Win32-API; Linux: `wl-copy` unter Wayland, `xsel`, sonst `xclip` unter X11; macOS: `pbcopy`; WSL zusätzlich `clip.exe`) und nur bei Misserfolg über Tk; `tk` benutzt nur die Tk-Zwischenablage; `system` nur Systemprogramm bzw. Win32-API. Gedacht für Umgebungen mit eigenem Zwischenablage-Abgleich (z. B. virtuelle Maschinen), in denen sich die Verfahren unterschiedlich verhalten | `auto` |
| `--k0 datei=PFAD` | Eingabequelle für Kanal K0 (T und SW gleichermaßen): Verzeichnis mit Eingabedatei(en); alternativ als Zeile `--k0 datei=PFAD` in der Testdatei (Abschnitt 6, der Schalter hat Vorrang) | nicht angegeben → Eingabe vom Terminal (interaktiv) |
| `--pruefe-stanzer1 DATEI` | Dateiprüfung (Durchführung eines Tests, Abschnitt 3b), alternativ als Zeile `--pruefe-stanzer1 DATEI` im Abschnitt `Prüfungen:` der Testdatei (der Schalter hat Vorrang): vergleicht die über `--stanzer1` erzeugte Datei mit der Soll-Datei `DATEI` (diff). Ein Name ohne Ordner liegt neben der Testdatei (`Tests/`). Soll- oder Ist-Datei fehlt oder Inhalt verschieden → Prüfung falsch (`Test falsch`, Rückkehrcode 6). Setzt `--stanzer1` voraus; nur mit **einer** Testdatei. | nicht angegeben → keine Dateiprüfung |
| `--pruefe-sw-ausgabe DATEI` | wie `--pruefe-stanzer1` (auch als Zeile im Abschnitt `Prüfungen:`), aber für die über `--sw-ausgabe` erzeugte Schreibwerk-Datei (`sw-ausgabe.txt`); setzt `--sw-ausgabe` voraus | nicht angegeben → keine Dateiprüfung |
| `--BASP abcdef` (auch `--BASP=abcdef` und `--basp`) | Bahnsperrenschalter der Magnettrommel (`C8205-Interpreter-Magnettrommel.md`, Abschnitt „Bahnsperrenschalter“): sechs Ziffern `0`/`1` (1 = EIN) für a = Hauptschalter (0001), b bis f = Zusatzschalter 0040, 0100, 0200, 0400, 1000; Vorgabe `000000` (alle AUS, keine Sperre). Beispiel: `--BASP=111000`. Der Interpreter prüft den Wert (jede andere Eingabe wird mit einer Fehlermeldung und Rückkehrcode 2 abgelehnt) und speichert ihn; bei einem Wert ungleich `000000` nennt er den Parameter auf dem Bildschirm und im Protokollkopf. **Die Wirkung (Schreibsperre der Trommel) ist noch nicht umgesetzt.** Nur auf der Kommandozeile, nicht als Zeile in der Testdatei. |
| `--knotentest` | Nimmt die Zeilen der durchlaufenen Knoten (`Kxxx KON/PHA/ANW/TST …`) ins Knotenprotokoll auf (Bildschirm bei STUFE=1, Protokolldatei bei STUFE=2). Ohne den Schalter entfallen diese Zeilen; erhalten bleiben die `BR=`-Zeilen (vor Knoten 2 und 7), die Diagnose sowie Fehler- und Stub-Meldungen. Der Schalter ändert weder den Ablauf noch die `Knoten:`-Zahl der Endzeile. | aus (false) |
| `--NO-TERMOUT` | Unterdrückt alle Ausgaben des Interpreters selbst am Terminal (Kopfzeile, Diagnose, Knotenzeilen, Endzeile, sonstige Meldungen); Ausnahmen: die vom C8205-Programm selbst über Ein-/Ausgabebefehle erzeugten Zeichen (z. B. SW-Ausgabe ohne `--sw-ausgabe`) sowie Meldungen bei fehlgeschlagener Vorab-Prüfung (Abschnitt 5 der Datei `C8205-Interpreter-Durchführung_eines_Tests.md`) bleiben sichtbar, da der Test dann ohnehin abbricht; dasselbe gilt für die Meldung zu einer fehlenden oder fehlerhaften Trommeldatei (Abschnitt 8.5). | aus (false) |
| `--version` | Gibt die Versionsnummer des Interpreters (Form `y.xx-zzz`, Regeln: `C8205-Versionierung.md`) aus und beendet das Programm mit Rückkehrcode 0, ohne einen Test auszuführen; eine Testdatei ist dazu nicht anzugeben. Zur Abfrage direkt `python3` aufrufen; die Wrapper (Abschnitt 5.2) sind für Testläufe gedacht | – |

> **Hinweis – Fenster „SW Ausgabe“ (`--SW-TERMINAL`):** Das Fenster bleibt **immer offen**, auch nach dem Ende des Tests und unabhängig von der Mausposition, bis Sie es mit Klick auf X schließen. Es läuft als eigener Prozess; jeder Aufruf öffnet ein neues Fenster. Text im Fenster lässt sich mit der Maus markieren und kopieren: sofort beim Loslassen der Maustaste, mit Strg+C oder Strg+Einfg oder über das Kontextmenü (rechte Maustaste). Das gilt unter Linux und unter Windows (Abschnitt 8.1).

Die langen Bezeichnungen `--lochbandleser1`, `--lochbandleser2` und `--lochbandstanzer1` sind gleichwertig.
Für `--leser1`/`--leser2`/`--stanzer1` gilt: Ein **nicht angegebenes** Gerät ist kein Fehler, solange das
Programm es nicht benutzt. Benutzt es das Programm doch, erscheint eine **rote Fehlermeldung** und der
Test endet (Abschnitt 10). **Ausnahme:** Kanal K0 (Eingabe, Abschnitt 8.4) und die Schreibwerk-Ausgabe
(Kanal K2, Abschnitt 8.1) haben funktionierende Vorgaben ohne eigenes Flag (Terminal-Eingabe bzw.
Terminal-Ausgabe) und erzeugen daher auch ohne `--k0`/`--sw-ausgabe` keinen Fehler.

**Version abfragen:** `--version` braucht keine Testdatei und führt keinen Test aus. Es gibt die Versionsnummer aus und
endet mit Rückkehrcode 0:

```
$ python3 c8205_interp.py --version
c8205_interp.py 0.03-001
```

Die Nummer hat die Form `y.xx-zzz` (Hauptversion, Unterversion, Build); Aufbau und Regeln stehen in
`C8205-Versionierung.md`. Die Wrapper (Abschnitt 5.2) sind für Testläufe gedacht (Testdatei als erstes Argument); die Version wird
direkt mit `python3` abgefragt. Die Nummer ist fassungsabhängig und kein fester Sollwert.

### 5.2 Wrapper `c8205_interpreter.sh` / `c8205_interpreter.bat`

```
./c8205_interpreter.sh TESTDATEI [SCHALTER ...]          # Linux/macOS
c8205_interpreter.bat  TESTDATEI [SCHALTER ...]          # Windows
```

Kern des Linux-Wrappers:

```sh
file="$1"
if [ -z "$file" ]; then
    echo "Test-Datei fehlt."
    exit 1
fi
shift
# Dateiname ohne Pfad, Endung durch .log ersetzen
prot_file="$(basename "$file")"
prot_file="${prot_file%.*}.log"
python3 c8205_interp.py --MODUS=TEST --mdverz ./markdown-dateien --out "Test-Protokolle/$prot_file" "$file" "$@"
```

Der Wrapper nimmt als **erstes Argument die Testdatei**, legt das Protokoll nach `Test-Protokolle/<Testname>.log`
und reicht **alle weiteren Argumente unverändert an den Interpreter weiter**. Damit sind alle Schalter aus
Abschnitt 5.1 über den Wrapper verfügbar, z. B.:

```
./c8205_interpreter.sh Tests/x.txt --leser1 virtuelle_Geraete/Leser1
./c8205_interpreter.sh Tests/x.txt --leser1 band5.txt --knotentest
```

Regeln:

- Die Testdatei steht **immer an erster Stelle**, die Schalter folgen danach. Ohne Testdatei meldet der Wrapper
  „Test-Datei fehlt.“ und endet mit Code 1.
- Die Vorgaben des Wrappers (`--mdverz ./markdown-dateien`, `--out Test-Protokolle/<Testname>.log`) stehen vor den
  weitergereichten Schaltern. Wird ein Schalter doppelt angegeben, gilt der zuletzt genannte; ein eigenes `--out`
  oder `--mdverz` überschreibt also die Vorgabe des Wrappers.
- Der Rückkehrcode des Interpreters wird vom Wrapper unverändert weitergegeben.
- Schalter mit eigenem Wertargument (`--out`, `--stanzer1`, `--sw-ausgabe`, `--pruefe-stanzer1`, `--pruefe-sw-ausgabe` u. a.) erkennt der
  Linux-Wrapper; der Wert gilt nie als Testdatei. Beispiel:
  `./c8205_interpreter.sh --NO-TERMOUT --stanzer1 virtuelle_Geraete/Stanzer1/ x.test --pruefe-stanzer1 x-stanzer-ausgabe.txt`
- **Windows (`.bat`):** Werte mit Gleichheitszeichen müssen in Anführungszeichen stehen, weil die Eingabeaufforderung
  `=` als Trennzeichen behandelt: `c8205_interpreter.bat Tests\x.txt --k0 "datei=band\k0"`. Pfade mit Leerzeichen
  ebenfalls in Anführungszeichen setzen.
- Es wird weiterhin **eine** Testdatei je Aufruf verarbeitet (das Protokoll heißt nach dieser Datei).
- **Trommel:** Der Wrapper übergibt `--trommel` nicht; es gilt die Vorgabe `virtuelle_Geraete/Trommel/trommel.txt` neben dem Skript
  (unabhängig vom aktuellen Ordner). Eine andere Trommeldatei steht wie jeder weitere Schalter hinter der Testdatei:
  `./c8205_interpreter.sh Tests/x.txt --trommel andere/trommel.txt`. Der Wrapper setzt die Trommel **nicht** zurück; jeder Aufruf
  beginnt mit dem Trommelstand, den der vorige Lauf hinterlassen hat (Abschnitt 8.5).

### 5.3 Betriebsart GRAFIK (Stufe 6)

**GRAFIK:** `c8205_interp.py` hat zwei Betriebsarten, gewählt mit `--MODUS=TEST` oder `--MODUS=GRAFIK`. **Ohne Angabe startet GRAFIK**; die Testläufe dieses Dokuments (Abschnitte 6 bis 13) brauchen daher `--MODUS=TEST`. Ein unbekannter Modus liefert eine Fehlermeldung und den Rückkehrcode 2. GRAFIK arbeitet mit Bedienpult-Fenster, Schreibwerk-Fenster, Tönen und echter Trommel; Start, Schalter und das Verhalten der TEST-Schalter in GRAFIK (wirkungslos, aber ohne Fehler) stehen in `C8205-Interpreter-GRAFIK_Beschreibung.md`, Abschnitte 1 und 2. Prüfung: `C8205-Interpreter-GRAFIK_Pruefverfahren.md`.

## 6. Die Testdatei

Eine Testdatei besteht aus zwei Teilen, eingeleitet durch die Zeilen `Trommeldatei:` und `Tastenfolge:`; als dritter, **optionaler** Teil kann ein Abschnitt `Prüfungen:` folgen (Ergebnisprüfung, s. unten).

**Abschnitt `Trommeldatei:`** der Testdatei (Trommelabschnitt: die Zellen, die vor dem Test auf die persistente Trommel geschrieben werden; **nicht genannte Zellen behalten ihren bisherigen Inhalt**, Abschnitt 8.5):

```
Adresse: Wert [# Bemerkung]        Adresse = 4 Oktalstellen, Wert = 11 Oktalstellen
```

Ein Wert besteht aus 4 Oktalstellen „beliebig“ und 7 Stellen Befehl (4 Adresse + 3 Operation), z. B.
`00004500030` = Adresse `4500`, Operation `030`. Leerzeilen und Zeilen mit `#` werden übergangen.

**Achtung (die Trommel bleibt zwischen den Tests erhalten):** Ein Test, der sich auf Zellen verlässt, die er in `Trommeldatei:` nicht selbst nennt, erbt deren Inhalt von den vorigen Läufen. Das gilt auch für `Prüfungen:` mit Sollwert 0 auf einer nicht belegten Zelle. Entweder die Zellen ausdrücklich nennen (auch `aaaa: 00000000000`) oder vor dem Lauf eine leere Trommel erzeugen (Abschnitt 8.5).

**Testmarken** (nur für die Testdurchführung, ohne Entsprechung in der Hardware):

| Marke | Wirkung |
|---|---|
| `#DOK-xxxx Text` | Kommentar zum Test (`xxxx` oktal). Beim Befehl 164 („Leerbefehl“) mit der Adresse `xxxx` wird der Text als Diagnose auf dem Bildschirm ausgegeben, unabhängig von der Protokollstufe. Es folgt keine automatische Zustandszeile. Mehrfach zulässig. |
| `#SPEI-xxxx ssss-eeee` | Speicherbereich, der beim Befehl 164 mit der Adresse `xxxx` ausgegeben wird. Unabhängig von `#DOK`, auch einzeln und mehrfach zulässig; `ssss ≤ eeee`. |
| `#SPUR-xxxx aaaa` | Ganze Spur (Bahn) mit der Adresse `aaaa`, ausgegeben beim Befehl 164 mit der Adresse `xxxx` (Abschnitt 13.6). Unabhängig von `#DOK`, auch einzeln und mehrfach zulässig. |
| `#PROT STUFE=n` | Protokollstufe des Tests (höchstens einmal): 0 = kein Knotenprotokoll, 1 = Knotenzeilen auf dem Bildschirm, 2 = Knotenzeilen nur in der Protokolldatei. Fehlt die Marke, gilt 1. |
| `#AC=ooooooooooo` | Anfangswert des Akkumulators, 11 Oktalziffern (Ergänzung 08.10.2026; höchstens einmal). Wird vor der Tastenfolge gesetzt. Fehlt die Marke, startet der AC mit 0. |
| `#BZ=oooo` | Anfangswert des Befehlszählers, 4 Oktalziffern (Ergänzung 08.10.2026; höchstens einmal). Wird vor der ersten Taste und vor jedem Befehl gesetzt (Anfangszustand); eine danach abgearbeitete Taste `G` setzt BZ nicht (sie stellt BR auf 0000 000); BZ := 0 entsteht erst durch die Ausführung dieses Sprungs (`R` oder `E` ohne `M`). Fehlt die Marke, startet BZ mit 0. |
| `#INTERRUPT H <Tasten>` | Unterbricht den sequentiellen Programmlauf (BZ := BZ+1) nach dem Befehl der davorstehenden Zeile und bedient die angegebene Tastenfolge (Ergänzung 08.10.2026; nur ZWISCHEN zwei Befehlszeilen, höchstens einmal je Befehlszeile, mehrfach in der Datei zulässig). Erste Taste `H`; endet die Folge mit `R` oder `ST`, läuft das Programm weiter, sonst endet der Test im Halt. Einzelheiten: `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2d. |
| `#TROMMEL=LEER` / `#TROMMEL=MP` | Setzt die Trommel VOR dem Test neu (Ergänzung 13.10.2026): `LEER` = alle 4096 Zellen 0; `MP` = Abbild des Minimalprogramms aus `virtuelle_Geraete/Trommelvorlagen/MP.txt` (Format wie die Trommeldatei; fehlt die Vorlage, startet der Test nicht, Rückkehrcode 16). Danach überlagern die Zeilen von `Trommeldatei:`. Höchstens einmal; nicht im Abschnitt `Prüfungen:`; ohne die Marke bleibt die Trommel unverändert. Steht sie im ersten Test des Aufrufs und fehlt die Trommeldatei oder ist sie fehlerhaft, wird diese neu angelegt (Abschnitt 8.5; Durchführung, Abschnitt 2g). |
| `#STARTE n` | Makro für die Tastenfolge `H G M+ E … E M- R` (n Anschläge `E`, Ansprung des Speicherplatzes n; Ergänzung 09.10.2026). `n`: Oktalzahl mit 1 bis 4 Ziffern, nicht leer; höchstens einmal; ersetzt die Tastenfolge (daneben keine Tasten). Einzelheiten: `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2e. |

Beide Marken `#AC=` und `#BZ=` stehen im Abschnitt `Trommeldatei:` (vor der Tastenfolge), sind voneinander unabhängig und einzeln oder zusammen zulässig. Ein ungültiger Wert (falsche Stellenzahl, Ziffer 8 oder 9, leerer Wert) oder eine doppelte Marke ist ein Fehler der formalen Prüfung (Rückkehrcode 16, der Test startet nicht). Einzelheiten und Beispiel: `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2.

**Geräte-Zeilen `--leser1`, `--leser2`, `--stanzer1`, `--sw-ausgabe` und `--k0` (Ergänzung 03.10.2026, erweitert 04.10.2026).** Diese Schalter dürfen auch als eigene Zeile in der Testdatei stehen
(Abschnitt 2b der Datei `C8205-Interpreter-Durchführung_eines_Tests.md`), damit der Test seine Ein-/Ausgabequelle selbst mitbringt:

```
--leser1 PFAD                Lochstreifen für Leser 1 (K1): Datei oder Verzeichnis
--leser2 PFAD                Lochstreifen für Leser 2 (K2): Datei oder Verzeichnis
--stanzer1 PFAD              Ausgabedatei bzw. -verzeichnis des Stanzers 1 (K1)
--sw-ausgabe PFAD            Schreibwerk-Ausgabe (K2) in die Datei sw-ausgabe.txt dieses Verzeichnisses
--k0 datei=PFAD              K0-Eingabe (T und SW) aus Datei bzw. Verzeichnis
```

- Die Zeile darf an jeder Stelle der Testdatei stehen (üblich: bei den Testmarken im Abschnitt `Trommeldatei:`); je Schalter **höchstens einmal**.
  Nach dem Schalternamen folgt der Wert wie auf der Kommandozeile (bei `--k0` mit `datei=`); ein Kommentar `# …` am Zeilenende ist zulässig.
- **Die Kommandozeile hat Vorrang:** Ist derselbe Schalter dort angegeben, gilt der Wert der Kommandozeile, die Zeile der Testdatei wird übergangen.
- Ein **relativer Pfad** gilt wie auf der Kommandozeile, also vom aktuellen Verzeichnis aus (nicht vom Ordner der Testdatei).
- **`--SW-TERMINAL` ist keine Geräte-Zeile:** Der Schalter (Abschnitt 5.1, 8.1) darf nur auf der Kommandozeile stehen. Eine Zeile `--SW-TERMINAL` in der Testdatei
  ist ein Formfehler der Vorab-Prüfung; der Test startet nicht (Rückkehrcode 16).
- Formfehler (Zeile ohne Wert, Schalter doppelt, `--k0` ohne `datei=`) und ein nicht vorhandener `--k0`-Pfad lassen den Test nicht starten (Rückkehrcode 16).
- Zeigt `--leser1`/`--leser2` in der Testdatei auf ein Verzeichnis, erscheint ein Hinweis: alle Dateien darin werden als Lochstreifen gelesen (8.2); für einen Test ist eine einzelne Datei sicherer.

**Ergebnisprüfung (`Prüfungen:`, optional).** Nach der Tastenfolge kann ein dritter Abschnitt `Prüfungen:` stehen. Er legt Soll-Werte
für den Endzustand fest; der Interpreter vergleicht sie nach dem Lauf mit den erreichten Werten und meldet `Test wahr` oder `Test falsch`.
Maßgeblich ist Abschnitt 3a der Datei `C8205-Interpreter-Durchführung_eines_Tests.md`; hier die Kurzfassung:

- **Höchstens eine Register-/Flag-Zeile** mit Zuweisungen `SCHLÜSSEL=WERT`, durch Leerzeichen getrennt, in beliebiger Reihenfolge, jeder Schlüssel höchstens einmal.
  Zulässig sind `BZ`, `AC`, `AR` und die Flags `FE`, `FUE` (für FÜ), `BS`, `US`, `E`, `A`, `V1`, `V2`. `BZ=` und `AR=` haben 4 Oktalstellen,
  `AC=` 11 Oktalstellen, ein Flag genau eine Stelle `0` oder `1`.
- **Beliebig viele Speicherprüfzeilen** `aaaa: wwwwwwwwwww` (4 + 11 Oktalstellen), danach, je Zeile eine Trommeladresse mit ihrem Sollwert; dieselbe Adresse nicht mit widersprüchlichem Wert.
- **Dateiprüfungen** (Abschnitt 3b der Testbeschreibung): Zeilen `--pruefe-stanzer1 DATEI` und `--pruefe-sw-ausgabe DATEI`, je höchstens einmal, an beliebiger Stelle des Abschnitts. `DATEI` ist die Soll-Datei (ohne Ordnerangabe: neben der Testdatei); sie wird mit der über `--stanzer1` bzw. `--sw-ausgabe` erzeugten Datei verglichen. Fehlt eine Datei oder ist der Inhalt verschieden, ist die Prüfung falsch. Setzt den jeweiligen Geräteschalter voraus.
- **Test wahr** nur, wenn alle angegebenen Einzelprüfungen übereinstimmen; sonst **Test falsch**. Ein leerer Abschnitt gilt als fehlender Abschnitt.
- Endet der Test nicht ordnungsgemäß (Stub, Laufzeitfehler), entfällt die Prüfung (Vermerk „nicht durchgeführt“) und der Test gilt nicht automatisch als falsch.
- Die Ausgabe steht immer auf dem Bildschirm, unabhängig von `#PROT STUFE` (Abschnitt 9); der Rückkehrcode folgt dem Ergebnis (Abschnitt 9).

```
Prüfungen:
BZ=0003 AC=00000000045 AR=0003 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
0000: 00003000211
3000: 00000000100
```

**Formale Prüfung.** Vor dem Start wird geprüft: Zeilenformat, keine Adresse mit widersprüchlichem Wert,
`#SPEI` mit gültiger Spanne (`#SPEI`/`#SPUR` brauchen kein `#DOK`), gültige `#PROT`-Stufe, gültige Marken `#AC=` (11 Oktalziffern) und `#BZ=` (4 Oktalziffern), je höchstens einmal, gültige `#INTERRUPT`-Zeilen (`Durchführung_eines_Tests.md`, Abschnitt 2d), gültiges `#STARTE` (Abschnitt 2e), vorhandene Tastenfolge, ein gültiger `Prüfungen:`-Abschnitt
(unbekannter oder doppelter Schlüssel, falsche Stellenzahl, Flag-Wert nicht 0/1, Speicherprüfzeile im falschen Format oder mit widersprüchlichem Sollwert)
sowie die angegebenen Geräte-Pfade (`--leser1`, `--leser2`, `--k0 datei=`, auch wenn sie als Zeile der Testdatei stehen): ein fehlender Pfad lässt den Test nicht starten. Bei einer Unstimmigkeit startet
der Test **nicht** und wird nicht eigenmächtig korrigiert.
Die Trommeldatei wird nicht je Test, sondern einmal vor dem ersten Test des Aufrufs geprüft (Abschnitt 8.5).

## 7. Die Tastenfolge

Die Tastenfolge (Zeile(n) hinter `Tastenfolge:`, Tokens durch Leerzeichen getrennt) legt den Ausgangszustand
vor Konnektor B fest. Sie **endet mit `R`** (dann ist `H` am Ende gelöst) **oder im Halt** (`H` bleibt gesetzt, z. B. `H G Ü E`); beides
ist definiert. Endet sie weder mit `R` noch im Halt, gilt sie als nicht definiert und der Test startet nicht.

Definition der Token: Dokument `C8205-Interpreter-Bedienpult_mit_Schaltern.md`, Abschnitt „Tastenfolge-Token“. Die Tabelle gibt
die Umsetzung im Interpreter wieder.

| Token (Groß-/Kleinschreibung egal) | Wirkung |
|---|---|
| `H` | Schalter H-R auf „H“: Flag H := 1 |
| `G` | Generallöschen: alle Flags außer H, T, SP := 0 (auch BS), danach US := 1; AR := 0000, OR := 000 (BR = 0000 000, unbedingter Sprung nach 0000); BZ und AC bleiben unverändert (Originaldokumentation). *Hinweis (Berichtigung 09.10.2026):* G setzt BZ nicht. Durch den aufgestellten BR 0000 000 kommt es zum Sprung nach 0000, wenn kein `M+ E … E M-` folgt; erst dessen Ausführung (`R` oder `E` ohne `M`) setzt BZ := 0000. Bis dahin bleibt BZ erhalten, auch ein mit `#BZ=` vorgegebener Wert. Kanal K0 angewählt (T := 1, bei gedrücktem SW: SW := 1) |
| `M+`, `M-drücken`, `M-gedrückt-halten` (Schreibweisen mit `drueck…` oder `halt…`) | M gedrückt halten: OR := OR ODER 025 |
| `M-`, `M-loslassen` | M loslassen: der Beitrag 025 im OR entfällt (übrige Anteile, z. B. von Ü, bleiben) |
| `M` | Antippen = `M+` und sofort `M-` (Fall 4): OR := OR ODER 025, BR bleibt aufgestellt. `R` startet bei Konnektor 4 (Knoten 54), wenn BR ein Sprung mit Rückkehrabsicht (025, 027, 125, 127) ist: Phase III gilt als abgelaufen, nur Resultatbehandlung (Ergänzung 04.10.2026, Originaldokumentation 4.3.2.3). Sonst startet `R` bei Knoten 19 |
| `E` (mit gehaltenem M) | BZ := BZ + 1, AR := BZ, AC := (BZ+1) im Adressfeld (Beispiel B nach 4×E: `00000005000`); Befehlsentnahme gesperrt, Automat steht danach vor Phase II |
| `E` (ohne M) | nur bei H: Einzelschritt über den Knotengraphen ab Knoten 19 (nach `M` mit Sprung mit Rückkehrabsicht ab Knoten 54; Phase IV, I bzw. II, III), Halt vor erneutem Eintritt in Knoten 19 |
| `SP=1` (auch `SP+`) | Schalter SP gedrückt/eingerastet: Flag SP := 1 |
| `BS=1` (auch `BS+`) | Schalter BS gedrückt/eingerastet: nur die Schalterstellung BS; das Flag BS wird davon nicht gesetzt (es wird erst 1, wenn ein bedingter Stopp wirksam wird) |
| `SP=0` (auch `SP-`) | Schalter SP gelöst: Flag SP := 0. `G` löst die Schalter nicht (mechanisch eingerastet) |
| `BS=0` (auch `BS-`) | Schalter BS gelöst: nur die Schalterstellung BS; das Flag BS wird davon nicht geändert. `G` löst den Schalter nicht, löscht aber das Flag BS |
| `ST` | nicht an H gebunden, nur bei US oder BS wirksam (sonst keine Wirkung): OR := OR ODER 240, AR unverändert, US := 0; BR aufgestellt, `R` startet bei Knoten 19. Nach einem Stop-Befehl ist das die Operation 26Z, nach `G` die Operation 240 |
| `Ü` (`UE`) | nur bei H: AR := 7777, OR := OR ODER 240 (BR aufgestellt); ohne H keine Wirkung |
| `SW=1`, `SW+`, `SW-drücken` | Schalter SW gedrückt: Flag SW := 1, T := 0 |
| `SW=0`, `SW-`, `SW-loslassen` | Schalter SW gelöst: Flag SW := 0, T := 1 |
| `K0`, `K1`, `K2`, `K3` | Kanalauswahltaste (rastend): Flag des gewählten Kanals := 1, Flags der anderen drei := 0 (bei `K0` zusätzlich T oder SW je nach Schalter SW, analog zu `G`); seit Interpreter 0.03-016 gilt auch für den Anwahlbefehl K0 die dauerhafte Schalterstellung SW (`m.sw_schalter`) im Moment der Anwahl, siehe `C8205-Versionierung.md` (Abschnitt 10.2); ein im Testprogramm nachfolgend ausgeführter Anwahlbefehl übersteuert diese Einstellung zur Laufzeit (s. Datei `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 6.0) |
| `R` | Schalter H-R auf „R“: Flag H := 0, US := 0; Interpretation beginnt bei Konnektor B (bei aufgestelltem BR bei Knoten 19, nach `M` mit Sprung mit Rückkehrabsicht bei Knoten 54) |

`SW` muss **vor** `G` gesetzt werden, weil `G` daraus T oder SW für K0 ableitet.
Typisches Muster „Sprung nach Speicherplatz n“: `H G M-drücken E … E M-loslassen R` (n mal `E`).

Nach `Ü`, `ST` oder `E` (ohne M) ist BR aufgestellt: folgt `R`, beginnt der Ablauf bei Knoten 19 statt bei Konnektor B.
Nach `M` (ohne E) mit einem Sprung mit Rückkehrabsicht in BR beginnt er bei Knoten 54 (Ergänzung 04.10.2026): Der Interpreter stellt die Operation
beim Eintritt auf A=0 um (wie Knoten 40) und führt nur Überlauftest, Resultatbehandlung und Phase II aus, nicht die Sprungoperation `⟨AC⟩ := Vr⟨BZ⟩ ∨ ⟨AC⟩`.
Ungültig (der Test startet nicht): `M-` ohne `M+`, `M+` bei gedrücktem M, `R` oder Ende bei gedrücktem M.

Die Kanaltasten `K0`–`K3` sind definiert (s. Token-Tabelle oben) und im Interpreter umgesetzt. Die Eingabetasten (0…9, `+` usw.) gehören nicht in die Tastenfolge, sie
werden als K0-Eingabe bedient (Abschnitt 8.4).

## 8. Geräte und Kanäle (Ein-/Ausgabe)

Ein Kanal wird durch einen **Anwahlbefehl** ausgewählt, der im Testprogramm steht:

| Anwahlbefehl | Kanal | Eingabe | Ausgabe |
|---|---|---|---|
| `4700 030` | K0 | Pult-Tastatur (T) oder Schreibwerk (SW) | keine |
| `4600 030` | K1 | Lochbandleser 1 | Lochbandstanzer 1 |
| `4500 030` | K2 | Lochbandleser 2 | Schreibwerk (Terminal) |
| `4400 030` | K3 | frei | frei |

Ein Ausgabe-Halt-Befehl (`a 030`) mit `a1 ≤ 3` gibt das Zeichen aus, dessen Ausgabe-Adresse (erste drei
Oktalstellen von `a`, Tabelle 1) zur Adresse passt. Während der Ausgabe ist Flag A = 1. Beim Stanzer (K1) zählen alle acht Bits z₁₃–z₂₀,
beim Schreibwerk (K2) nur z₁₄, z₁₅ und z₁₇–z₂₀ (Spuren v u 8 4 2 1; z₁₃ = w und z₁₆ = p werden ignoriert, Original 4.3.2.5).
Ist für den Ausgabe-Halt kein Ausgabegerät angewählt (K0, K3 oder keine Anwahl), stoppt der Rechner nach dem Original mit gesetztem Flag A (Lampe A);
der Interpreter meldet das als **Stub**, das Flag A bleibt dabei 1 (Endzeile `A=1`). Dasselbe gilt für eine nicht existierende Anwahl (`a1 ≥ 4`, `a2 < 4`). Der Überlauf wird nach Ausgabe-Halt und Anwahl getestet (Knoten 80, Halt wegen Überlauf Knoten 81).
Die Pufferung der Ausgabe (1-Zeichen-Puffer) wird nicht zeitlich nachgebildet (Wartezeit=0).

### 8.1 Schreibwerk-Ausgabe (K2)

> **Hinweis – Fenster „SW Ausgabe“ (`--SW-TERMINAL`):** Das Fenster bleibt **immer offen**, auch nach dem Ende des Tests und unabhängig von der Mausposition, bis Sie es mit Klick auf X schließen. Es läuft als eigener Prozess; jeder Aufruf öffnet ein neues Fenster. Text im Fenster lässt sich mit der Maus markieren und kopieren: sofort beim Loslassen der Maustaste, mit Strg+C oder Strg+Einfg oder über das Kontextmenü (rechte Maustaste). Das gilt unter Linux und unter Windows (Abschnitt 8.1).

- Schreibwerk-Ausgabe erfolgt immer über Kanal K2; die Stellung des Schalters SW hat darauf keinen
  Einfluss (der Schalter SW betrifft ausschließlich die Eingabeseite, Kanal K0, Abschnitt 8.4).
- **Ohne `--sw-ausgabe`** (Vorgabe): Jedes Zeichen erscheint **sofort** auf dem Terminal, in
  **Dunkelgelb** (ANSI 33).
- **Mit `--sw-ausgabe PFAD`**: Jedes Zeichen geht stattdessen in die Datei "sw-ausgabe.txt" in diesem
  Verzeichnis (angelegt nur bei tatsächlicher Ausgabe, fortgeführt/angehängt bei mehreren Ausgaben;
  `WRZL` schließt die aktuelle Zeile ab). In diesem Fall erscheint nichts mehr am Terminal. Die Datei
  wird am Testende zum Download bereitgestellt — das ist nur beim Claude-Interpreter erforderlich, der
  Python-Interpreter legt sie ohnehin direkt im angegebenen Verzeichnis ab. Bei jedem Test wird die
  Datei beim ersten Ausgabezeichen neu angelegt und danach nur noch fortgeführt.
- **Mit `--SW-TERMINAL`** (Ergänzung 10.10.2026): Jedes Zeichen erscheint **zusätzlich** in einem Textfenster „SW Ausgabe“ (nur Text, 130 × 36 Zeichen, verschiebbar,
  Vorgabe rechts unten auf dem Desktop), gleichgültig ob `--sw-ausgabe` gesetzt ist; Datei bzw. Terminal bleiben wie oben beschrieben. Zusätzlich zeigt das Fenster jede Eingabe über K0 als Echo in Dunkelgelb (Abschnitt 8.4). Das Fenster
  bleibt auch am Ende des Aufrufs **immer offen**, bis es mit Klick auf X geschlossen wird (es läuft als eigener Prozess und überlebt den Interpreter und sein Terminal; unter
  Linux in einer eigenen Sitzung, unter Windows ohne Konsolenfenster). Voraussetzung sind `tkinter` (Linux: Paket
  `python3-tk`) und eine grafische Oberfläche, sonst gibt es eine Warnung und der Test läuft ohne Fenster. Den Schalter gibt es nur auf der Kommandozeile, nicht als
  Zeile in der Testdatei.
- **Markieren und Kopieren im Fenster `--SW-TERMINAL`** (wie in den Lochstreifen-Hilfsprogrammen, `C8205-Interpreter-Lochstreifen-Hilfsprogramme.md`, Abschnitt 3.3): Der Text im Fenster lässt sich mit der Maus markieren (auch Doppel- und Dreifachklick).
  Kopiert wird sofort beim **Loslassen der Maustaste**, mit **Strg+C**, **Strg+Umschalt+C** oder **Strg+Einfg** (auch wenn der Tastaturfokus nicht im Textfeld liegt) und über das **Kontextmenü**
  (rechte Maustaste; auf macOS auch mittlere Taste bzw. Strg+Klick) mit „Kopieren“ und „Alles markieren“. Strg+A markiert den gesamten Text. Jedes erfolgreiche Kopieren meldet sich kurz in der Titelleiste
  („kopiert (N Zeichen, Verfahren)“), ein Fehlschlag mit „Kopieren fehlgeschlagen“. Derselbe Text wird innerhalb von 5 Sekunden nicht erneut in die Zwischenablage gelegt. Unter Windows werden Strg+C, Strg+A und Strg+Einfg
  zusätzlich über den Tastenkode erkannt (auch bei nicht-lateinischem Tastaturlayout); AltGr-Zeichen gelten nicht als Strg-Befehl. Das Verfahren wählt `--zwischenablage` (Abschnitt 5.1, Vorgabe `auto`): Windows über die
  Win32-API (`CF_UNICODETEXT`, bis zu 20 Versuche im Abstand von 50 ms), Linux/macOS/WSL zuerst über ein Systemprogramm, das die Zwischenablage dauerhaft übernimmt (Wayland `wl-copy`, X11 `xsel`, sonst `xclip`,
  macOS `pbcopy`, WSL `clip.exe`; Auswahl bei jedem Kopieren nach `WAYLAND_DISPLAY`/`XDG_SESSION_TYPE`/`DISPLAY` und den installierten Programmen, fehlende werden übersprungen); die Tk-Zwischenablage ist der Rückfall.
  Die Programme sind optional (Linux: `sudo apt install xsel xclip` bzw. `wl-clipboard`); in virtuellen Maschinen entscheidet das Gast-Zusatzprogramm, wie der Text zum Host kommt.
- Die Zeichenlage KB/GB des Schreibwerks wird beim Start **zufällig** gesetzt. `Um. KB` (Ausgabe-Adresse `117x`)
  und `Um. GB` (`057x`) stellen sie um; sie wirken, geben aber selbst **nichts** aus.
  Ohne Umschaltzeichen im Programm ist die Groß-/Kleinschreibung also zufällig.
- Zeichen ohne sichtbare Darstellung erscheinen als `<Name>` (z. B. `<Irrung Zeichen>`); `SatzMarke` (`272x`) ist ein Zeilenumbruch.
- Das Schreibwerk wertet nur die sechs Bits z₁₄, z₁₅, z₁₇–z₂₀ der Ausgabe-Adresse aus; ein anderes p- oder w-Bit ändert das Zeichen nicht.
- Ist die Ausgabe-Adresse kein darstellbares Zeichen (nicht in Tabelle 1), erscheint nichts (Hinweis im Protokoll).
- Bei `STUFE=1` erscheinen die Knotenzeilen (mit `--knotentest`) erst nach dem Lauf; die Schreibwerk-Ausgabe steht davor.

### 8.2 Lochbandleser (K1, K2)

`--leser1` / `--leser2` nehmen eine **Datei** (ein Streifen) oder einen **Ordner** (Streifen in Namensreihenfolge).
Pro Eingabebefehl wird **eine Zeile** gelesen: acht Zeichen `0`/`1` für die Spuren `w v u p 8 4 2 1`
(Transportspur nicht dargestellt). Leerzeilen sind Vorspann und werden übergangen.

- **Ungerade** Zahl gelochter Spuren = gültig; **gerade** = Fehler bei Eingabe: FE := 1, der Lauf hält. Ausnahme „Irrung Zeichen“ (`11111111`, alle 8 Spuren): keine Paritätsprüfung, nicht ins Adressregister übernommen, übersprungen; der Eingabebefehl wartet auf das nächste Zeichen (Originaldokumentation 4.3.2.2, Abb. 16; Ergänzung 04.10.2026). Leerzeilen (Vorspann) werden übergangen. Ein Transportloch außerhalb des Vorspanns ist im Streifenformat nicht definiert und nicht umgesetzt.
- Die Eingabeadresse ist `(Lochbild & 0x0F) | ((Lochbild >> 1) & 0x30)` und muss in Tabelle 1 vorkommen.
- Sie wird mit dem Adressregister ODER-verknüpft. Danach wird der Befehl umgestellt: bei **Sprung-Umstellung „ja“**
  (z. B. `:`, `.`, `,`, Tabulator, `Um. KB`, `Um. GB`) zu einem unbedingten Sprung an die Adresse `a ODER Eingabeadresse`,
  bei „nein“ (z. B. Ziffern, Buchstaben) zu einem Lesebefehl, der den **Inhalt der Zelle** `a ODER Eingabeadresse` zum AC addiert (nicht die Eingabeadresse selbst; wie im Kleinen Eingabeprogramm, Kodetabellen 1.8).
- Ist der Streifen (die aktuell geladene Datei) zu Ende und liegt im `--leserX`-Verzeichnis keine weitere
  Datei vor, wartet der Interpreter still (ohne Meldung) auf das Erscheinen einer neuen Datei, statt zu
  halten — wie beim realen Leser (s. Datei `C8205-Interpreter-Lochstreifenleser.md`, Abschnitt A5).
  Existiert der angegebene Pfad gar nicht, wird dies bei der formalen Vorab-Prüfung als
  Fehler gemeldet, der Test startet dann nicht (Rückkehrcode 16). Das stille Warten lässt sich nur durch
  eine neue Datei im Verzeichnis oder mit Strg+C beenden (Rückkehrcode 8).

### 8.3 Lochbandstanzer (K1)

`--stanzer1 PFAD` ist die Ausgabedatei (bei einem Ordner: `stanzer-ausgabe.txt` darin). Je gestanztem Zeichen
entsteht eine Zeile mit acht Zeichen `0`/`1` für `w v u p 8 4 2 1`. Die Datei wird beim ersten gestanzten
Zeichen eines Laufs **neu angelegt** (nicht angehängt) und nur angelegt, wenn wirklich gestanzt wird. Fehlt
`--stanzer1`, kann keine Ausgabe auf K1 erfolgen — anders als bei der Schreibwerk-Ausgabe (8.1) gibt es
hier **keinen** Terminal-Ausweg; wird K1 trotzdem benutzt, erscheint die rote Fehlermeldung aus Abschnitt
10 und der Test endet.

### 8.4 Pult-Tastatur und Schreibwerk-Eingabe (K0)

**Standardfall (kein Flag nötig):** Der Interpreter liest einen Tastendruck je Eingabebefehl vom Terminal
(ohne Echo, ohne Enter, Strg+C wirkt) — für T und SW gleichermaßen.

**Flag `--k0 datei=PFAD`:** Statt vom Terminal werden die Eingaben für K0 (T und SW gleichermaßen) aus
einer Textdatei bzw. einem Verzeichnis entnommen; je Zeile ein Zeichen oder Name (`ZR`, `WM`, `IS`, `IB`,
`TAB`, `WRZL` oder Namen aus Tabelle 1; Zeilen mit `#` sind Kommentar). `PFAD` kann mehrere Dateien
enthalten, die in alphanumerischer Reihenfolge verarbeitet werden (analog zu den Lochstreifenlesern,
Abschnitt 8.2). Ist eine Datei zu Ende und liegt keine weitere bereits vor, wartet der Interpreter still
(ohne Meldung) auf das Erscheinen einer neuen Datei, statt zu halten; existiert der angegebene Pfad gar
nicht, wird dies bei der formalen Vorab-Prüfung als Fehler gemeldet und der Test nicht gestartet.
Nur bei Terminal-Eingabe ohne weitere Zeichen (z. B. geschlossenes stdin) endet der Lauf mit `EINGABE_ENDE`.
Der frühere Schalter `--k0 tastatur` entfällt; ohne `--k0` wird vom Terminal gelesen.

*(Plattformhinweis: Unter Linux/macOS wird `termios`/`tty` verwendet, unter Windows `msvcrt.getch()` – beide
liefern das Zeichen sofort und ohne Bildschirm-Echo. Unter Windows ist `msvcrt.getch()` bekannt dafür, dass es
Strg+C in Ausnahmefällen als normales Zeichen statt als Abbruchsignal liefern kann; im Zweifel hilft Strg+Pause
oder das Schließen des Konsolenfensters.)*

Was eingegeben werden darf, hängt vom Schalter SW ab:

| Zustand | Eingebbar |
|---|---|
| SW nicht gedrückt (Flag T, Pult-Tastatur) | **nur** `0`–`9`, `+`, `-`, `,`, `.`, `:`, `ZR`, `WM`, `IS`, `IB` (19 Codes). `B` und `D` haben keinen Code und sind nicht eingebbar. |
| SW gedrückt (Flag SW, Schreibwerk) | **alle** Zeichen der Tabelle 1 |

Ein nicht erlaubtes Zeichen wird bei `datei=` mit roter Meldung abgelehnt (Test endet); im Standardfall
(Terminal) wird der Tastendruck ignoriert und auf die nächste gültige Taste gewartet.
Zeichen werden über die Spalten „Ascii KB“/„Ascii GB“ gefunden; die Eingabe-Zeichenlage (Start KB, geändert durch
gelesenes `Um. KB`/`Um. GB`) bestimmt, welche Spalte zuerst durchsucht wird. Auf die Eingabeadresse hat sie keinen Einfluss.

**Echo im Fenster `--SW-TERMINAL`** (Ergänzung 10.10.2026): Ist der Schalter angegeben (Abschnitt 5.1, 8.1), erscheint jedes **angenommene** K0-Zeichen
(Pult-Tastatur T oder Schreibwerk SW; vom Terminal oder aus `--k0 datei=PFAD`) zusätzlich als **Echo in Dunkelgelb** im Fenster „SW Ausgabe“; die Ausgaben des
Rechners stehen dort in der Standardfarbe, so lassen sich Eingabe und Ausgabe unterscheiden. Das Echo zeigt das Zeichen wie das Schreibwerk (Namen ohne
Zeichen als `<Name>`), in der gerade gültigen Zeichenlage KB/GB. Nicht angenommene Zeichen (z. B. an T nicht eingebbar) und die Eingaben der Lochbandleser (K1, K2)
erscheinen nicht. Ohne den Schalter gibt es kein Echo; der Standardfall bleibt „ohne Echo“. 

> **Hinweis (18.10.2026, Entwurf 111, U-8):** Dieser Abschnitt beschreibt das Echo des **Python-Interpreters im Modus TEST** (`--SW-TERMINAL`, Terminal-Eingabe) und gilt dort weiter. Im Modus **GRAFIK** gibt es kein Echo des Rechners über K0 (der C 8205 hat keines); das SW-Fenster zeigt dort **jedes angenommene Zeichen selbst** an, auf derselben Schreibposition wie die Ausgabe, in der Standardfarbe (Anforderungsdokument 09, S3-04). Umschaltzeichen, blockierte und nicht angenommene Zeichen erscheinen nicht.

### 8.5 Die Trommel (persistente Datei, Änderung 07.10.2026)

Die Trommel ist **keine Datei je Test**, sondern eine dauerhafte Textdatei (Vorgabe `virtuelle_Geraete/Trommel/trommel.txt`, Schalter `--trommel`).
Sie hält ihren Inhalt über Tests und Aufrufe hinweg. Der Abschnitt `Trommeldatei:` einer Testdatei (Abschnitt 6) ist davon zu unterscheiden:
Er nennt nur die Zellen, die der Test vor dem Start auf die Trommel schreibt.

- **Format:** genau 4096 Zeilen `aaaa: ttttttttttt` (Adresse 4 Oktalstellen, ein Doppelpunkt, ein Leerzeichen, Wert 11 Oktalstellen, Zeilenende LF),
  in aufsteigender logischer Adresse `0000` bis `7777`, jede Adresse genau einmal. Keine Kommentar- und keine Leerzeilen. Jede Zeile ist 18 Byte lang;
  der Interpreter schreibt eine Zelle an die Byteposition Adresse × 18. Die Reihenfolge der Datei ist die logische, nicht die physische Reihenfolge
  der Sektoren (Interleaving: `C8205-Interpreter-Magnettrommel.md`).
- **Prüfung vor dem ersten Test:** Die Datei muss vorhanden und lesbar sein, genau 4096 Zeilen im obigen Format haben und die Adressen lückenlos aufsteigend
  führen; sie muss sich zum Schreiben öffnen lassen. Sonst meldet der Interpreter `FEHLER: Trommeldatei "…" ist formal fehlerhaft - Test(s) starten nicht:`
  mit den Einzelfehlern (höchstens 50, danach die Zahl der weiteren) bzw. `… kann nicht geoeffnet werden: …` und endet mit Rückkehrcode 16. Es läuft dann **kein**
  Test des Aufrufs. Die Meldung erscheint auch mit `--NO-TERMOUT`.
- **Beginn eines Tests:** Der Interpreter schreibt die `Adresse: Wert`-Zeilen des Abschnitts `Trommeldatei:` auf die Trommel (nach der formalen Prüfung der
  Testdatei, vor der Tastenfolge). Sie überlagern die vorhandenen Werte. **Zellen, die der Test nicht nennt, behalten ihren bisherigen Inhalt.**
  Register, Flags und Geräte beginnen dagegen bei jedem Test neu (AC usw. = 0, Ausgangszustand durch die Tastenfolge).
- **Während des Tests:** Jeder Schreibzugriff eines Befehls ändert die Zelle im Arbeitsspeicher des Interpreters und die zugehörige Zeile der Datei.
  Gelesen wird aus dem Arbeitsspeicher; die Datei wird einmal beim Start eingelesen. Der Interpreter ruft kein ausdrückliches `flush` auf: Eine geschriebene Zelle
  gelangt beim nächsten Schreibzugriff in die Datei, die zuletzt geschriebene spätestens beim Schließen am Ende des Aufrufs; auch nach Abbruch mit Strg+C wird die Datei noch geschlossen.
  Bei hartem Abbruch des Prozesses (z. B. `kill`) kann die zuletzt geschriebene Zelle in der Datei fehlen.
- **Nach dem Test:** Der Endzustand der Trommel bleibt stehen und ist der Anfangszustand des nächsten Tests, auch wenn ein Aufruf mehrere Testdateien nacheinander
  abarbeitet. Dasselbe gilt für `#SPEI`, `#SPUR` und die Speicherprüfzeilen in `Prüfungen:`: Sie lesen den aktuellen Trommelstand, auch mit Resten früherer Tests.
- **Leere Trommel erzeugen und zurücksetzen:** `python3 testscripte/erzeuge_leere_trommel.py [--aus PFAD]` schreibt alle 4096 Zeilen mit `00000000000` (Vorgabe: `virtuelle_Geraete/Trommel/trommel.txt`
  neben dem Skript; fehlende Ordner werden angelegt; eine vorhandene Datei wird ohne Rückfrage überschrieben). Der Interpreter setzt die Trommel von sich aus **nie** zurück und legt die
  Datei **nie** an. Einzige Ausnahme ist die Testmarke `#TROMMEL=LEER` bzw. `#TROMMEL=MP` (nächster Punkt).
- **Testmarke `#TROMMEL=LEER` / `#TROMMEL=MP` (Ergänzung 13.10.2026):** Vor dem Test wird die Trommel komplett neu gesetzt und die Datei vollständig neu geschrieben: `LEER` = alle Zellen 0, `MP` = Abbild aus `virtuelle_Geraete/Trommelvorlagen/MP.txt`. Danach überlagern die Zeilen des Abschnitts `Trommeldatei:` (Reihenfolge zwingend). Fehlt die Marke, bleibt die Trommel unverändert. Steht die Marke im **ersten** Test eines Aufrufs und fehlt die Trommeldatei oder ist sie formal fehlerhaft, legt der Interpreter sie neu an (alle Zellen 0, fehlende Ordner werden angelegt) und meldet das in einer Hinweiszeile, statt mit Rückkehrcode 16 zu enden. Bildschirm: `Trommel: vor dem Test geleert (#TROMMEL=LEER)`; Protokoll: Zeile bei den Ausgangsbedingungen. Der bisherige Inhalt geht ohne Rückfrage verloren; für Tests, die einen Arbeitsstand nicht zerstören dürfen, eine eigene Datei mit `--trommel` verwenden. Einzelheiten: `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2g.
- **Folge für Tests und Sollwerte:** Ein Lauf ist nur dann unabhängig von seiner Vorgeschichte, wenn der Test alle Zellen, die er liest oder prüft, selbst nennt oder wenn vorher eine leere Trommel
  erzeugt wird. Beispiel: Der Test `bsp_seite_42_025-sw-ausgabe` erwartet in `Prüfungen:` die Zellen `2024` bis `2027` mit Wert 0, belegt sie aber nicht selbst. Auf leerer Trommel ist er
  `Test wahr`; läuft er nach `bsp_seite_40` (das `2024` bis `2026` mit Daten belegt), ist er `Test falsch`. Für Regressionsläufe (13.5) und für den Vergleich mit dem Claude-Interpreter
  gilt daher: Python-Lauf auf leerer Trommel; der Claude-Interpreter hat keine Trommeldatei und nimmt für nicht genannte Zellen 0 an
  (`C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2c).
- **Zeilenende:** Die Datei muss LF-Zeilenenden haben (siehe offene Punkte, Abschnitt 11).

## 9. Ausgaben, Protokoll und Endzustand

**Bildschirm** (je Test): Kopfzeile `=== Test <Name> (#PROT STUFE=n) ===`, gefolgt von Schreibwerk-Zeichen,
Diagnose (`-- Diagnose --`, `#DOK-…`, `#SPEI-…`, `#SPUR-…` bei Befehl 164), bei STUFE=1 (und `--knotentest`) den Knotenzeilen bzw. `BR=`-Zeilen und am Ende der
**Endzeile**:

```
Ende: <Grund> | Knoten: n | BZ=… AC=… AR=… | FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
```

Die Registerwerte sind oktal (BZ, AR vierstellig, AC elfstellig). Flags: FE Fehler bei Eingabe, FUE Überlauf,
BS bedingter Stopp, US unbedingter Stopp, E/A Ein-/Ausgabebefehl aufgestellt, V1/V2 Vergleicher.

**Endgründe** (Auswahl):

| Endgrund | Bedeutung |
|---|---|
| Unbedingter Stop (US:=1) | Programm hat ordnungsgemäß gehalten |
| Bedingter Stop (BS:=1) | bedingter Stopp-Befehl bei eingerastetem Schalter BS (Knoten 79) |
| Halt wegen Überlauf (FÜ bereits 1) | Überlauf-Halt (Knoten 46, 58, 66); weder US noch BS gesetzt, nur FÜ |
| Fehler bei Eingabe (FE) | gerade Zahl von Lochungen |
| EINGABE_ENDE | Terminal-Eingabe (K0) ohne weitere Zeichen, z. B. stdin geschlossen; bei Leser und `--k0 datei=` gibt es kein Ende, sondern stilles Warten (8.2, 8.4) |
| Gerät nicht nutzbar | Gerät nicht angegeben oder Datei/Zeichen ungültig (rote Meldung); gilt nicht für K0 (Terminal-Vorgabe) oder K2-Schreibwerk-Ausgabe (Terminal-Vorgabe) |
| STUB bei Knoten n | Regelwerk unvollständig (Kanal K3 ist dagegen der definierte Fall „nicht benutzt“, s. Abschnitt 11) |
| Tastenfolge nicht gültig/definiert | Test startete nicht |

**Diagnose (Befehl 164).** Der Leerbefehl wird zuerst abgearbeitet; erst danach erscheint die Diagnose. Die Leer-Befehle 164 und 166
sind laut Befehlsliste (Nr. 66) „Leer-Operation ohne Löschen“, also **ohne Resultatbehandlung**: das Z-Feld erzeugt
hier **keine Verschiebung** (Korrektur 29.09.2026). Die Adresse des Befehls (`a`) wählt die zugehörigen `#DOK`-Texte (alle, in Dateireihenfolge), die `#SPEI`-Bereiche und die
`#SPUR`-Spuren; jede Speicherzelle steht als Zeile `aaaa: wwwwwwwwwww` unter der jeweiligen Markenzeile. Die Marken sind
voneinander unabhängig: passt nur ein `#SPEI` oder nur ein `#SPUR` zur Adresse, wird nur dieses ausgegeben. Eine
automatische Zustandszeile (`BZ=… AC=… FE=…`) nach `#DOK` gibt es nicht (Änderung 29.09.2026); passt keine Marke, entfällt die Diagnose ganz.
Vor der Ausgabe je `#SPEI`- bzw. `#SPUR`-Marke steht die auslösende Testmarke selbst als Zeile (z. B. `#SPEI-0023 4000-4005`,
`#SPUR-0023 4000`), damit im Protokoll erkennbar ist, wozu die folgenden Speicherzeilen gehören.

**Ergebnisprüfung** (nur, wenn die Testdatei einen Abschnitt `Prüfungen:` enthält, Abschnitt 6): Nach der Endzeile steht auf dem Bildschirm, unabhängig von
`#PROT STUFE`, die Zeile `Ergebnisprüfung:`, darunter je Einzelprüfung eine Zeile `SCHLÜSSEL: soll=… ist=… OK` bzw. `… FEHLER` (Register und Flags, dann Speicherzellen in
Adressreihenfolge) und zuletzt `Test wahr` oder `Test falsch`. Endete der Test nicht ordnungsgemäß, steht stattdessen
`Ergebnisprüfung: nicht durchgeführt (Test nicht ordnungsgemäß beendet)`. Bei `#PROT STUFE=2` wird dasselbe als Abschnitt `== 3. Ergebnisprüfung ==` ans Ende der Protokolldatei geschrieben.

**Dateiprüfungen** (`--pruefe-stanzer1`, `--pruefe-sw-ausgabe`, als Schalter, Abschnitt 5.1, oder als Zeile im Abschnitt `Prüfungen:`, Abschnitt 6): Sie erscheinen im selben Block `Ergebnisprüfung:` hinter den Einzelprüfungen des
Abschnitts `Prüfungen:`, je Prüfung eine Zeile `Stanzer 1: soll=<Soll-Datei> ist=<Ist-Datei> OK` bzw. `Schreibwerk: … FEHLER (<Grund>)`. Grund ist `Soll-Datei fehlt`,
`Ist-Datei fehlt, vom Lauf nicht angelegt` oder `Inhalt verschieden, diff:`; im letzten Fall folgt der Unterschied im Format `diff -u` (Soll gegen Ist, höchstens 100 Zeilen).
Eine Ist-Datei gilt nur, wenn **dieser** Lauf sie angelegt hat; eine übrig gebliebene Datei eines früheren Laufs zählt nicht. `Test wahr` gilt nur, wenn alle Einzelprüfungen
**und** alle Dateiprüfungen wahr sind; der Rückkehrcode folgt dem Gesamtergebnis (0 oder 6). Mit `--NO-TERMOUT` entfällt die Bildschirmausgabe; das Ergebnis steht dann bei `#PROT STUFE=2` in der Protokolldatei und im Rückkehrcode.

**Protokolldatei** (nur bei `#PROT STUFE=2`): Abschnitte `== 1. Ausgangsbedingungen ==` (die vom Test auf die Trommel geschriebenen Zeilen, nicht der ganze Trommelinhalt,
Tastenfolge mit Wirkung je Taste), `== 2. Zustände des Knotenautomaten ==`, `== Ende ==` und, falls vorhanden, `== 3. Ergebnisprüfung ==`.
Knotenzeilen erscheinen nur bei Aufruf mit `--knotentest`. Eine Knotenzeile hat die Form
`K009 ANW 005 BZ=0001 AR=0001 AC=00000000000`; Tests tragen zusätzlich `-> wahr` oder `-> falsch`.
Die Zeile `BR=aaaa ooo` mit dem Befehlsregister (Adressteil und Operationsteil des zuletzt geladenen Befehls) steht
**vor Knoten 2** (Beginn Phase I) und **vor Knoten 7** (Sprung über Konnektor 1 aus Knoten 63; Knoten 7 selbst wird als
Konnektor übersprungen, die Zeile steht unmittelbar nach der Zeile von Knoten 63). Sie steht auch ohne `--knotentest`
im Protokoll. Beispiel: `  BR=3000 211  (vor Knoten 002)  BZ=0001 AC=00000000000 FÜ=0 V1=0 V2=0 V3=0`. Am Zeilenende stehen der
Befehlszähler `<BZ>` (vierstellig oktal), der Akkumulator `<AC>` (elfstellig oktal), das Überlauf-Flag FÜ und die Vergleicher V1, V2 sowie der Pseudovergleicher V3
(V3=1 genau dann, wenn V1=1 und V2=1) zum jeweiligen Zeitpunkt. Die frühere Zeile „nach Knoten 009“ entfällt. Bei STUFE=0 oder 1
entsteht keine Protokolldatei; bei angegebenem `--out` erscheint dann ein Hinweis.

**Rückkehrcode:** Der Interpreter liefert dem Betriebssystem einen Rückkehrcode, der sich stets
auf **genau einen** Test bezieht — auch wenn in einem Aufruf mehrere Testdateien abgearbeitet werden
(Abschnitt 5.1): maßgeblich ist der zuletzt bearbeitete Test; eine Gesamtauswertung über mehrere Tests hinweg ist ggf. von einem übergeordneten
Skript (z. B. `c8205_interpreter.sh`/`.bat`) selbst vorzunehmen.

| Code | Bedeutung |
|---|---|
| 0 | keine Vorab-Prüfungs-Fehler; `Prüfungen:`-Abschnitt und/oder Dateiprüfung definiert und Ergebnis `Test wahr` |
| 4 | keine Vorab-Prüfungs-Fehler; weder `Prüfungen:`-Abschnitt noch Dateiprüfung (`--pruefe-…`) angegeben |
| 6 | keine Vorab-Prüfungs-Fehler; Prüfung definiert, aber Ergebnis `Test falsch` (auch: Soll- oder Ist-Datei fehlt, Dateiinhalt verschieden) |
| 8 | sonstige Laufzeitfehler (Stub, Gerät nicht nutzbar, Abbruch mit Strg+C) |
| 16 | Vorab-Prüfungs-Fehler (u. a. fehlender Geräte-Pfad, `--pruefe-stanzer1`/`--pruefe-sw-ausgabe` ohne `--stanzer1`/`--sw-ausgabe`, ungültige Tastenfolge, ungültiger `Prüfungen:`-Abschnitt, ungültige Testmarke `#TROMMEL` oder fehlende Trommelvorlage (`MP`), Testdatei nicht gefunden oder nicht eindeutig; ebenso eine fehlende oder formal fehlerhafte Trommeldatei, dann startet im ganzen Aufruf kein Test) |
| 2 | ungültiger Aufruf (unbekannter oder falsch angegebener Schalter, fehlende Regelwerk-Dateien, `--out` mit Dateiendung bei mehreren Tests); der Interpreter startet keinen Test |

## 10. Fehlermeldungen und Abhilfe

Fehler zu Geräten erscheinen **in Rot** auf dem Terminal (Standardfehlerausgabe, nur mit Terminal gefärbt):

| Meldung | Ursache | Abhilfe |
|---|---|---|
| `Knotengraph nicht gefunden: …` | `C8205-Interpreter-Eingänge_der_Knoten.md` nicht im `--mdverz`-Verzeichnis | `--mdverz` korrekt angeben oder Datei dorthin legen |
| `Knotenbeschreibung nicht gefunden: …` | `C8205-Interpreter-Beschreibung_der_Knoten.md` nicht im `--mdverz`-Verzeichnis | `--mdverz` korrekt angeben oder Datei dorthin legen |
| `FEHLER: Trommeldatei "…" ist formal fehlerhaft - Test(s) starten nicht:` mit Zeilen wie `Trommeldatei nicht gefunden: …`, `Trommeldatei hat n Zeilen; erwartet werden genau 4096 …`, `Zeile n: ungueltiges Format …`, `Zeile n: Adresse aaaa erwartet, gefunden bbbb.` | Trommeldatei fehlt, hat nicht genau 4096 Zeilen, eine Zeile hat das falsche Format oder die Adressen sind nicht lückenlos aufsteigend | `--trommel` bzw. Pfad prüfen; leere Trommel mit `python3 testscripte/erzeuge_leere_trommel.py` neu erzeugen (Abschnitt 8.5); Rückkehrcode 16, es startet kein Test |
| `FEHLER: Trommeldatei "…" kann nicht geoeffnet werden: …` | Datei lässt sich nicht zum Schreiben öffnen (Rechte, schreibgeschützt) | Schreibrechte prüfen; Rückkehrcode 16 |
| `Eingabe von Lochbandleser n (Kanal Kn) angefordert, aber --lesern nicht angegeben.` | Programm liest von K1/K2, Schalter fehlt | `--leser1`/`--leser2` angeben |
| `Ausgabe auf Lochbandstanzer 1 (Kanal K1) angefordert, aber --stanzer1 nicht angegeben.` | Programm stanzt, Schalter fehlt | `--stanzer1` angeben |
| `Lochbandleser n: Lochstreifen-Pfad nicht gefunden: …` | Pfad falsch | Pfad prüfen |
| `K0: Eingabe-Pfad nicht gefunden: …` | bei `--k0 datei=PFAD` (Schalter oder Zeile der Testdatei) angegebener Pfad existiert nicht | Pfad prüfen (formale Vorab-Prüfung; der Test startet nicht, Rückkehrcode 16) |
| Das Fenster „SW Ausgabe“ bleibt nach dem Test offen | gewollt: das Fenster schließt sich nie von selbst | mit Klick auf X schließen (jeder Aufruf mit `--SW-TERMINAL` öffnet ein eigenes Fenster) |
| Titelleiste des Fensters „SW Ausgabe“ zeigt `Kopieren fehlgeschlagen` | kein Kopierverfahren hat funktioniert (Linux: weder `wl-copy`/`xsel`/`xclip` noch Tk-Zwischenablage erreichbar; Windows: Zwischenablage von einem anderen Programm gesperrt) | `--zwischenablage system` bzw. `tk` versuchen; unter Linux `xsel`, `xclip` oder `wl-clipboard` installieren; in virtuellen Maschinen das Gast-Zusatzprogramm prüfen |
| `WARNUNG: --SW-TERMINAL: kein Ausgabefenster moeglich: …` | `tkinter` fehlt oder es gibt keine grafische Oberfläche (unter Linux `DISPLAY` nicht gesetzt) | `python3-tk` installieren bzw. in einer grafischen Sitzung starten; der Test läuft trotzdem, nur ohne Fenster |
| `Zeile n: --SW-TERMINAL ist nur als Kommandozeilenschalter zulaessig, nicht in der Testdatei` | Der Schalter steht als Zeile in der Testdatei | Zeile entfernen; `--SW-TERMINAL` beim Aufruf angeben (Rückkehrcode 16) |
| `Zeile n: --leser1/--leser2/--stanzer1/--sw-ausgabe/--k0 …` (ohne Wert, mehrfach angegeben, `--k0` ohne `datei=`) | Formfehler einer Geräte-Zeile der Testdatei | Zeile korrigieren (Abschnitt 6; Rückkehrcode 16) |
| `--pruefe-stanzer1 ohne --stanzer1: …` / `--pruefe-sw-ausgabe ohne --sw-ausgabe: …` | Dateiprüfung ohne das zugehörige Gerät, es gäbe keine Ist-Datei | passenden Geräteschalter ergänzen (formale Vorab-Prüfung; Rückkehrcode 16) |
| `--pruefe-stanzer1/--pruefe-sw-ausgabe sind nur mit genau einer Testdatei zulässig` | Dateiprüfung mit mehreren Testdateien | Tests einzeln starten (ungültiger Aufruf, Rückkehrcode 2) |
| `Lochstreifen …: ungültige Zeile …` | Zeile ist nicht acht Zeichen aus `0`/`1` | Streifendatei korrigieren |
| `K0-Eingabe: '…' ist an der Pult-Tastatur (T) nicht eingebbar …` | Zeichen an T nicht erlaubt | `SW=1` vor `G` in die Tastenfolge oder anderes Zeichen |
| `K0-Datei nicht lesbar: …` | Datei fehlt | Pfad prüfen |
| `Testdatei nicht gefunden: …` | Name weder als Pfad noch unterhalb der Suchordner vorhanden | Pfad prüfen, Schreibweise, aktuellen Ordner beachten (wird mit angezeigt) |
| `Testdatei … nicht eindeutig gefunden` | mehrere Dateien gleichen Namens | vollständigen Pfad angeben |
| `--out mit Dateiendung … ist nur mit genau einer Testdatei zulässig` | `--out x.log` mit mehreren Tests | Ordner ohne Endung verwenden oder Tests einzeln starten |
| `Tastenfolge nicht gültig/definiert` | Token unbekannt, weder `R` noch Halt am Ende, M nicht losgelassen, nicht implementierte Taste | Abschnitt 7 |
| `STUB bei Knoten n: …` | vom Programm benutzte Funktion noch nicht umgesetzt | Abschnitt 11 |

## 11. Abweichungen, Erweiterungen und offene Punkte

**Erweiterungen gegenüber dem Regelwerk** (nur für den Interpreter, ohne Entsprechung in der Hardware):
- Testmarken `#DOK`, `#SPEI`, `#PROT STUFE`.
- Testzeile `#STARTE n` (Ergänzung 09.10.2026): Makro für `H G M+ E … E M- R` (`Durchführung_eines_Tests.md`, Abschnitt 2e); der Parser setzt daraus die Tastenfolge zusammen, der Ablauf ist der der ausgeschriebenen Tasten. Protokoll (Ergänzung 08.10.2026): Der Abschnitt „Ausgangsbedingungen“ zeigt Folgen von mindestens vier `E` unter M gekürzt (erste zwei Zeilen, Sammelzeile, letzte Zeile; Funktion `_starte_kompakt`); ausgeschriebene Tastenfolgen bleiben vollständig.
- Testzeile `#INTERRUPT H <Tasten>` (Ergänzung 08.10.2026): Unterbrechung des Programmlaufs zwischen zwei Befehlen mit weiterer Tastenfolge (`Durchführung_eines_Tests.md`, Abschnitt 2d). Knotentabelle unverändert; der Interpreter prüft in der Hauptschleife beim Eintritt in Knoten 2 (Phase I), ob nach dem vorigen Befehl BZ = Adresse+1 gilt.
- Testmarken `#AC=` und `#BZ=` (Ergänzung 08.10.2026): Anfangswerte von Akkumulator und Befehlszähler. Sie gelten als Anfangszustand vor der ersten Taste; die Taste `G` setzt BZ und AC nicht (BZ := 0 erst durch den von G aufgestellten Sprung nach 0000, wenn `R` oder `E` ihn ausführt). Ohne die Marken ändert sich nichts. Im Protokoll (Abschnitt `== 1. Ausgangsbedingungen ==`) stehen die Marken und eine Zeile `Anfangswerte: …`.
- Schalter `--trommel` und die Trommel als persistente Datei (Änderung 07.10.2026, Abschnitt 8.5), Hilfsskript `testscripte/erzeuge_leere_trommel.py`.
- Schalter `--leser1/2`, `--stanzer1`, `--sw-ausgabe`, `--k0`; das Regelwerk (Durchführung eines Tests, 6.2) beschreibt für Leser
  Verzeichnisse, der Interpreter nimmt auch eine einzelne Datei.
- `--out` mit Dateiendung als direkte Protokolldatei; Suche der Testdatei über den Namen.
- Wrapper `c8205_interpreter.sh`/`.bat` reichen zusätzliche Schalter an den Interpreter durch (Ergänzung 02.10.2026, Abschnitt 5.2).
- Token `SW=1`/`SW=0` in der Tastenfolge.
- Geräte-Zeilen `--leser1 PFAD`, `--leser2 PFAD`, `--stanzer1 PFAD`, `--sw-ausgabe PFAD` und `--k0 datei=PFAD` in der Testdatei (Ergänzung 03.10.2026, für Leser und Stanzer 04.10.2026, Durchführung eines Tests, Abschnitt 2b); die Kommandozeile hat Vorrang.
- Dateiprüfungen `--pruefe-stanzer1 DATEI` und `--pruefe-sw-ausgabe DATEI`, als Zeile im Abschnitt `Prüfungen:` der Testdatei oder als Schalter (Ergänzung 03.10.2026, Durchführung eines Tests, Abschnitt 3b). Dabei gilt ein
  Stanzer-Pfad mit Schrägstrich am Ende (noch nicht vorhandenes Verzeichnis) als Verzeichnis; vorher scheiterte der Lauf mit einem Python-Fehler.
- Schalter `--SW-TERMINAL` (Ergänzung 10.10.2026, Durchführung eines Tests, 6.3.1): Textfenster „SW Ausgabe“ zusätzlich zur Ausgabe nach 8.1; Vorgabe aus; nur Kommandozeile, nicht in der Testdatei.
- Schalter `--knotentest` (Ergänzung 29.09.2026): Knotenzeilen im Protokoll nur auf Wunsch; Vorgabe aus. Der Wrapper
  `c8205_interpreter.sh`/`.bat` ruft ohne diesen Schalter auf; für Knotenzeilen in der `.log`-Datei wird er beim Aufruf
  angehängt: `./c8205_interpreter.sh Tests/x.txt --knotentest`.

**Auslegung, wo das Regelwerk offen lässt:**
- `B` und `D` (Pult-Tasten) haben keinen Code und sind an T nicht eingebbar.
- `WM` = Tabulator (Eingabe-Adresse 075), `IB` = Eingabe-Adresse 036 (Auslegung des Interpreters).
- Tabellenzeile 52 („Transport“, Relikt) wird nicht benutzt.

**Auslegung A=3/Z=2 (Ergänzung 29.09.2026, korrigiert 05.10.2026):** Die Codes `232`, `332`, `432`, `532`, `632`, `732` („bedingte Addition ohne Löschen, mit Rechtsverschiebung“) werden nach Befehlsliste 4.3 (A=3, Z=2,3) ausgeführt: z₃₂ ist das **niederwertigste Bit des AC**, nicht das Löschbit (L ist bei Z=2 immer 0). Ist z₃₂(AC)=1, wird `<a>` zum AC addiert (`<AC> := <AC> + <a>`, mod 2³³; ein Übertrag aus Bit 33 wird gemerkt), anderenfalls bleibt der AC unverändert. Die anschließende Rechtsverschiebung leistet die Resultatbehandlung (ANWEISUNG-022); dabei wird der gemerkte Übertrag als z₀ eingesetzt (Summe zweier positiver Zahlen < 2, Produktaufbau der Multiplikation, Programmieranleitung 6.1.2). Die frühere Fassung (nur Rechtsverschiebung, nie Addition, weil z₃₂ als Löschbit gelesen wurde) ließ die verkürzte Multiplikation 6.1.2 (`7700 432`) mit AC=0 enden und ist damit überholt. Bei `332` wird der Vergleicher wie bei allen markierten Befehlen gesetzt und korrigiert. Damit gibt es für die 512 Operationscodes keinen Stub mehr; K3 wird in dieser Ausbaustufe nicht benutzt (s. unten), Ein-/Ausgabebefehle brauchen die passenden Geräteschalter.

**Auslegung des Interpreters (bewusst wortlautgetreu nach dem Knotengraphen, nicht nach vereinfachenden Beschreibungen):**
- ANWEISUNG-001 wird in Knoten 3 (Phase I) **und** Knoten 16 (Phase III) jeweils vollständig angewendet
  (`<AR>:=<BZ>` und gleichzeitig `<BZ>:=<AR>+1` mit dem Altwert). Der dabei in Phase I entstehende BZ-Zwischenwert wird
  in Knoten 11 überschrieben, bevor ihn ein Knoten liest; die Phasentabelle der Überblicksdatei ist nur eine Vergröberung.
- Die Resultatbehandlung (ANWEISUNG-022, Z-Feld) wird bei jedem Befehl angewendet, **außer** bei den Leer-Befehlen (B=1, A=6, Z≥4; z. B. 164, 166): diese laufen ohne Resultatbehandlung, auch ohne Verschiebung (Korrektur 29.09.2026).
- Bei den verkürzten Gruppen-/Wiederholungsbefehlen (B=5, 7) ist das Vorzeichenbit R-abhängig: bei R≠1 gilt z₀,
  bei R=1 gilt z₃₂ (ANWEISUNG-042). Der Test wird **nach** ANWEISUNG-022 der jeweiligen Zelle ausgewertet (Beispiele 13.4).
- ANWEISUNG-010 setzt nach T2 die interne Umstellung der Operation: A=4, 5, 7 → A=0 (sonst würde ein genommener Sprung wie ein Stopp enden); B=0/A=6/z₃₀=1 (bedingter Sprung mit Rückkehrabsicht, SP gesetzt) → A=2 (Ergänzung 02.10.2026; in `c8205_interp.py` umgesetzt für ANWEISUNG-008, -009, -010 und -018).
- ANWEISUNG-029 stellt nach dem Sichern der Rückkehradresse die Operation auf A=0 (unbedingter Sprung) um, wie in ANWEISUNG-013 beschrieben (Ergänzung 02.10.2026). Vorher blieb das Sprungziel bei Sprüngen mit Rückkehrabsicht (024 bis 027, 124 bis 127) ungenutzt, weil Phase I danach die Folgeadresse BZ holte.
- Stopp-Zustände (Ergänzung 02.10.2026): ANWEISUNG-030 (Knoten 45) setzt nur US. Der bedingte Stopp bei gesetztem Schalter BS läuft über den neuen Knoten 79 mit ANWEISUNG-045 (Flag BS:=1). Der Halt wegen Überlauf (Knoten 46, 58, 66) verwendet die neue ANWEISUNG-046 und setzt weder US noch BS; angezeigt wird nur FÜ. Vorher war das in `c8205_interp.py` über `came_from` innerhalb von ANWEISUNG-030 unterschieden, in der Knotentabelle aber nicht abgebildet.
- Ausgabe-Halt (Ergänzung 04.10.2026, Abgleich mit der Originaldokumentation 4.3.2.5): neue Knoten 80 (Test ANWEISUNG-020, Überlauf vorhanden) und 81 (Halt wegen Überlauf, ANWEISUNG-046) hinter Knoten 23, vorher führte Knoten 23 direkt zu Phase I. Schreibwerk-Ausgabe über sechs Bits, Stub bei fehlendem Ausgabegerät (Abschnitt 8).
- Lochbandeingabe (Ergänzung 04.10.2026, Abgleich mit der Originaldokumentation 4.3.2.2, Abb. 16): „Irrung Zeichen“ wird übersprungen (kein FE, kein Stopp, nicht ins AR); vorher löste es FE und Halt aus. Abschnitt 8.2. Tests `lb-001`, `lb-002`, `lb-003` mit den Streifendateien `lb-001_…`, `lb-002_…`, `lb-003_…` in `virtuelle_Geraete/Leser1/` (Aufruf z. B. `--leser1 virtuelle_Geraete/Leser1/lb-001_irrung_zeichen_dann_1.txt`).
- Eingabe-Lesebefehl (Ergänzung 04.10.2026 (2), Abgleich mit dem Kleinen Eingabeprogramm, Kodetabellen 1.8): Bei Ziffern und Buchstaben addiert der umgestellte Lesebefehl den **Inhalt der Zelle** `a ODER Eingabeadresse` zum AC, nicht die Eingabeadresse. Abschnitte 8.2 und 13.2 angepasst. Die Tests `lb-001` und `lb-002` enthalten dafür die Konstante `0001: 00000000001` (Sollwert AC=…1 bleibt).
- Tasten nach Stopp (Ergänzung 04.10.2026 (3), Abgleich mit der Originaldokumentation 4.3.2.3, Abb. 19): Nach `M` (ohne E) beginnt der Ablauf bei einem Sprung mit Rückkehrabsicht in BR nicht mehr bei Knoten 19, sondern bei Knoten 54. Vorher lief über Knoten 40 die Sprungoperation `⟨AC⟩ := Vr⟨BZ⟩ ∨ ⟨AC⟩` ab, obwohl Phase III schon abgelaufen ist (Original: nur Resultatbehandlung). Bedienpult-Dokument, Abschnitt „Fortsetzung nach einem Stopp“, beschreibt `ST`, `Ü` (Operation 26Z nach einem Stop-Befehl) und `M`. Tests `tk-001` bis `tk-008` (Tastenkombinationen, Wirkung auf BZ und AC).

**Offene Punkte:**
- **Protokollkopf zur Trommel:** Der Interpreter schreibt in den Abschnitt `== 1. Ausgangsbedingungen ==` der Protokolldatei noch die Überschrift „Trommeldatei (uebernommen, Ausschnitt; nicht genannte Zellen = 0)“. Das stimmt seit der persistenten Trommel nicht mehr: Nicht genannte Zellen behalten ihren Inhalt. Die Zeilen darunter (die vom Test geschriebenen Zellen) sind richtig. Die Überschrift im Interpreter ist anzupassen (Abschnitt 8.5).
- **Zeilenende der Trommeldatei:** Der Interpreter rechnet die Position einer Zelle als Adresse × 18 (LF). Eine Datei mit CRLF-Zeilenenden besteht die formale Prüfung, wird aber beim ersten Schreiben beschädigt; der nächste Lauf meldet sie dann als formal fehlerhaft (unter Linux mit einer künstlich in CRLF umgewandelten Datei nachgestellt, unter Windows nicht erprobt). Betroffen wäre auch eine unter Windows im Textmodus erzeugte Datei (`testscripte/erzeuge_leere_trommel.py` öffnet im Textmodus) und eine durch Git umgewandelte. Bis zur Behebung: Trommeldatei nur mit LF-Zeilenenden führen.
- Ein Transportloch außerhalb des Vorspanns (Original: unterliegt der Paritätsprüfung) ist im Streifenformat nicht darstellbar und nicht umgesetzt; die Auslegung steht noch aus.
- **Bahnsperrenschalter (`--BASP`, Ergänzung 14.10.2026):** Der Aufrufparameter ist vorhanden (Abschnitt 5.1), seine Wirkung nicht: Schreibzugriffe des Rechners auf gesperrte Bahnen werden noch nicht unterdrückt (Regel: `C8205-Interpreter-Magnettrommel.md`, Abschnitt „Bahnsperrenschalter“).

**Festlegung Kanal K3 (29.09.2026):** Kanal K3 (Anwahl `4400 030`, kein Gerät) wird vom C 8205 in dieser Ausbaustufe **nie benutzt** (Festlegung des Autors).
Ein Programm, das auf K3 ein- oder ausgibt, liegt außerhalb des definierten Betriebs. Der Interpreter meldet dies mit einem Stub, das ist kein Fehler des Interpreters und kein offener Punkt. Seit 04.10.2026 gilt das auch für den Ausgabe-Halt auf K0 und ohne Anwahl (vorher blieb die Ausgabe auf K0/K3 stillschweigend aus).

## 12. Bezug zu den Regelwerk-Dateien

| Thema | Datei |
|---|---|
| Überblick, Phasen, Leistungsdaten | `C8205-Interpreter-Überblick_und_Gesamtaufbau.md` |
| Flags, Register, Maschinenwort | `C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md` |
| Trommel, Sektoren, Bahnsperre | `C8205-Interpreter-Magnettrommel.md` |
| Trommeldatei des Interpreters (Format, Persistenz, Zurücksetzen) | Abschnitt 8.5 dieser Datei; Sicht der Tests: `C8205-Interpreter-Durchführung_eines_Tests.md`, Abschnitt 2c |
| Tasten, Schalter, Kanäle, Funktionsabläufe | `C8205-Interpreter-Bedienpult_mit_Schaltern.md` |
| Leser, Stanzer, Schreibwerk (Hardware) | `C8205-Interpreter-Lochstreifenleser.md` |
| Zeichenkodes, Tabelle 1 | `C8205-Interpreter-Kodetabellen.md` |
| Befehle und Formeln | `C8205-Interpreter-Befehlsliste.md` |
| Knotengraph / Variablentabelle T2 | `C8205-Interpreter-Eingänge_der_Knoten.md`, `C8205-Interpreter-Beschreibung_der_Knoten.md` |
| Testdurchführung, Testdatei, Protokoll | `C8205-Interpreter-Durchführung_eines_Tests.md` |
| Cache der BAZ-Wirkungen (wird vom Python-Interpreter nicht gelesen) | `baz-wirkungstabelle.md` |

## 13. Beispiele

### 13.1 Ausgabe auf dem Schreibwerk (Test `0015-030`)

```
Trommeldatei:
#DOK-0015 Test Ausgabebefehl
#PROT STUFE=2
0001: 00007240000
7240: 00004500030
7241: 00002720030
7242: 00000570030
7243: 00001210030
7244: 00001170030
7245: 00000610030
7246: 00000700030
7247: 00001110030
7250: 00000320030
7251: 00000010030
7252: 00000310030
7253: 00000070030
7254: 00000020030
7255: 00000015164
7256: 00000000020

Tastenfolge:
H G M-drücken E M-loslassen R
```

Ablauf: Die Tastenfolge springt (Muster „Sprung nach n“, n = 1) auf Adresse 0001, dort steht ein Sprung nach 7240.
Das Programm wählt K2 an (`4500 030`), gibt `SatzMarke` (Zeilenumbruch), `Um. GB`, `J`, `Um. KB`, `a`, `h`, `r`,
Leerzeichen, `1`, `9`, `7`, `2` aus und ruft den Leerbefehl 164 (Diagnose) auf.

```
$ ./c8205_interpreter.sh 0015-030.txt
=== Test 0015-030 (#PROT STUFE=2) ===

Jahr 1972
-- Diagnose --
#DOK-0015 Test Ausgabebefehl
Ende: Unbedingter Stop (US:=1) | Knoten: 308 | BZ=7257 AC=00000002000 AR=0000 | FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
Protokolldatei: Test-Protokolle/0015-030.log
```

Die Zeile `Jahr 1972` erscheint in Dunkelgelb. Die Leerzeile davor ist der Zeilenumbruch des Programms.
Der `Knoten:`-Wert kann je nach Fassung des Graphen abweichen und ist kein fester Sollwert.
Der AC `…2000` stammt von der Taste `E` unter gehaltenem `M` (AC := BZ+1 im Adressfeld, Abschnitt 7); das Programm lädt keinen Wert, und der Leerbefehl 164 ändert den AC nicht.

**Variante mit Ausgabefenster (`--SW-TERMINAL`):**

> **Hinweis – Fenster „SW Ausgabe“ (`--SW-TERMINAL`):** Das Fenster bleibt **immer offen**, auch nach dem Ende des Tests und unabhängig von der Mausposition, bis Sie es mit Klick auf X schließen. Es läuft als eigener Prozess; jeder Aufruf öffnet ein neues Fenster. Text im Fenster lässt sich mit der Maus markieren und kopieren: sofort beim Loslassen der Maustaste, mit Strg+C oder Strg+Einfg oder über das Kontextmenü (rechte Maustaste). Das gilt unter Linux und unter Windows (Abschnitt 8.1).

Starten Sie den Test:

```
$ python3 c8205_interp.py --MODUS=TEST --SW-TERMINAL Tests/0015-030.txt
```

Im Fenster „SW Ausgabe“ steht `Jahr 1972`. Das Terminal zeigt wie zuvor die Zeilen des Interpreters (ohne `--sw-ausgabe` auch die Dunkelgelb-Ausgabe). Mit `--sw-ausgabe virtuelle_Geraete/SW-Ausgabe` geht dieselbe Ausgabe zusätzlich in die Datei `sw-ausgabe.txt`.

### 13.2 Ziffer vom Lochstreifen lesen

Programm: `0000: 00004600030` (K1 anwählen), `0001: 00000000011` (Eingabe-Halt mit Löschen), `0002: 00000000020` (Stopp),
dazu die Konstante `0005: 00000000042`.
Streifendatei `band5.txt` mit den Zeilen `` (leer) und `00010101` (die Ziffer 5: Spuren p, 4, 1).
Aufruf: `python3 c8205_interp.py --MODUS=TEST --leser1 band5.txt test.txt`. Ergebnis: Stopp bei BZ=0003 mit AC=…42. Die Eingabeadresse 05 wird mit dem
Adreßteil 0000 des Eingabe-Halts zur Adresse 0005 verknüpft; der AC erhält den **Inhalt** der Zelle 0005 (nicht die Zahl 5). Ist Zelle 0005 nicht
belegt, ist AC=0.
Enthält der Streifen vor der Ziffer die Zeile `11111111` („Irrung Zeichen“), ist das Ergebnis dasselbe; die Zeile wird übersprungen.

Mit dem Zeichen `:` (Zeile `00001101`) und Eingabe-Halt `0001: 00000000010` springt das Programm nach 0015.

### 13.3 Zeichen stanzen

Programm: `0000: 00004600030` (K1 anwählen), `0001: 00000250030` (Ausgabe der Ziffer 5, Ausgabe-Adresse `025x`),
`0002: 00000730030` (Ausgabe des Punktes, `073x`), `0003: 00000000020` (Stopp).
Aufruf mit `--stanzer1 out/band.txt` erzeugt eine Datei mit den Zeilen `00010101` und `00111011`.
Ohne `--stanzer1` endet derselbe Test mit der roten Fehlermeldung aus Abschnitt 10.
Mit der Zeile `--pruefe-stanzer1 soll.txt` im Abschnitt `Prüfungen:` der Testdatei (oder dem gleichnamigen Schalter; Datei neben der Testdatei) wird die erzeugte Datei zusätzlich mit `soll.txt` verglichen:
gleicher Inhalt → `Test wahr` (Rückkehrcode 0); abweichender Inhalt, fehlende Soll-Datei oder fehlende Ist-Datei → `Test falsch` (Rückkehrcode 6).

### 13.4 Vorzeichenbit und X-Abbruch (synthetische Tests, Stand 28.09.2026)

Alle Tests haben `#PROT STUFE=0` und enden mit der Diagnose des Befehls 164 (`#SPEI-… 4000-4037`).

**`s1-R1`** – verkürzter Gruppen-Transport mit Rechtsverschiebung (R=1, Code `542`), AC startet mit `…006`:

```
0000: 00003000211          # AC := <3000>
0001: 00004001542          # GX-Transport nach 4001, Z=2 (R=1, ohne Löschen)
0002: 00000020164          # Leerbefehl, Diagnose #DOK-0020
0003: 00000000020
3000: 00000000006
```

Ergebnis: **zwei** Zellen werden geschrieben, `4001: 00000000006` (Ladewert unverschoben, vor der Verschiebung noch positiv)
und `4016: 00000000003` (die Zelle, bei der AC durch die Rechtsverschiebung negativ wird: z₀ ist bei R=1 stets 0, entscheidend
ist z₃₂, hier 1 nach der ersten Verschiebung). Bei z₀ als Vorzeichen würden alle 32 Zellen geschrieben.

**`s2-R2`** – Linksverschiebung (R=2, Code `544`) und AC = `…003`: z₀ entscheidet. Es werden alle 32 Zellen geschrieben;
die letzte (`4037`) enthält `00060000000` – die durch die Verschiebung negativ gewordene, aber noch abgespeicherte 32. Zelle.

**`s3-neg`** – Sonderfall: AC ist bereits **vor** der ersten Zelle negativ (`3000: 40000000000`, GX-Transport R=2). Auch hier
wird die erste Zelle (`4001`) noch vollständig bearbeitet und mit dem negativen Wert beschrieben, erst danach bricht der Lauf ab.

### 13.5 Referenzläufe (Sollwerte für Regressionsläufe)

Alle Tests: Tastenfolge `H G R`, Ende „Unbedingter Stop (US:=1)“, FE=0, FÜ=0, BS=0. Die Knotenzahl ist fassungsabhängig. Die Sollwerte gelten für einen Lauf auf leerer Trommel (Abschnitt 8.5).

| Test | Inhalt | Ergebnis |
|---|---|---|
| `0004` | Ladebefehl, GX-Transport, Linksverschiebung | 27 Zellen ≠ 0; AC am Ende `0`; BZ=0004 |
| `0005` | Gruppen-Transport (`640`), Startsektor 01 bis Sektor 23 | 27 Zellen ≠ 0; AC `…100`; BZ=0004 |
| `0006`, `0007` | WX-/GX-Transport mit Linksverschiebung | je 15 Zellen ≠ 0; AC `0`; BZ=0004 |
| `0010` | Laden, Addieren, Speichern; zwei `#SPEI`-Bereiche | AC `…300`; BZ=3010; 5 Speicherzeilen in der Diagnose |
| `0011` | Subtraktion, `241` löscht AC vor dem Transport | AC `0`; `3020`=`77777777770`, `3021`=`0`; BZ=3011 |
| `0012` | Positiv-Sprung genommen, Befehl `5002` übersprungen | AC `…100`; BZ=5006 |
| `0021` | Ladebefehl, WX-Transport mit Linksverschiebung, X-Abbruch (Autor-Test) | 3 Zellen ≠ 0: `4001`=`10000000000`, `4016`=`20000000000`, `4033`=`40000000000` (letztere jetzt korrekt gespeichert); AC `0`; BZ=0004 |
| `ac-001`, `bz-001`, `acbz-001`, `acbz-002` | Anfangswerte `#AC=`/`#BZ=` (08.10.2026); Tastenfolge `H G R` bzw. (`acbz-002`) `H M-gedrückt-halten E M-loslassen R`; Sollwerte stehen im Abschnitt `Prüfungen:` der Tests | Test wahr (rc 0); Ende wie vor: Unbedingter Stop |
| `st-001` bis `st-004` | `#STARTE` (09.10.2026): `#STARTE 4`, Gegenprobe mit ausgeschriebener Tastenfolge, `#STARTE 12` (oktal), `st-004`: `#STARTE 1000` mit Schreibwerk-Ausgabe aufs Terminal und `#INTERRUPT H G M+ E M- R`; Sollwerte im Abschnitt `Prüfungen:` | Test wahr (rc 0); `st-001` = `st-002`: BZ=0007 AC `…145`; `st-003`: BZ=0014 AC `…100`; `st-004`: Terminal `XYxy`, BZ=1011 AC `00001006000` |
| `int-001` bis `int-006` | `#INTERRUPT` (08.10.2026): Fortsetzung `H R`, Ende ohne `R`, `H G Ü E` (Transport nach 7777), `H G ST`, Sprung übersprungen, zwei Zeilen; Sollwerte im Abschnitt `Prüfungen:` bzw. im Protokoll | `int-001`, `int-004`: AC=145, BZ=0003 (Stopp); `int-002`: Halt, BZ=0001, AC=100; `int-003`: `7777`=100, Test wahr |
| `0014` | Sprung, Laden, Vergleichersetzen, Vergleichersprung 2 (zweimal genommen), Transport, Leerbefehl | Diagnose (`#SPEI-0014 7773-7776`): `7773`=`11111111111`, `7774`=`00000000200`, `7775`=`0`, `7776`=`11111111111`; Ende: BZ=3012 AC=`11111111111` V1=0 V2=1; 228 Knoten |

### 13.6 Neue Testmarke `#SPUR-xxxx aaaa` (Ergänzung 29.09.2026)

Analog zu `#SPEI-xxxx ssss-eeee`, aber statt einer Adressspanne wird die **ganze Spur (Bahn)** ausgegeben,
in der `aaaa` liegt — alle 32 Zellen, in der physischen Zugriffsreihenfolge der Trommel (nicht in
aufsteigender logischer Adresse). Erscheint in der Diagnose nach allen `#SPEI-xxxx`-Ausgaben derselben
Adresse und ist von `#DOK` unabhängig; vor den 32 Zellen steht die Marke `#SPUR-xxxx aaaa` als Kopfzeile. Beispiel `s4-spur` (13.5): `#SPUR-0023 4000` gibt beginnend mit `4000` alle 32 Zellen der
Spur `40xx` in physischer Reihenfolge aus (`4000, 4015, 4032, 4007, 4024, 4001, 4016, 4033, …, 4023`).

## 14. Vorgaben für die PDF-Bedienungsanleitung

Dieser Abschnitt legt fest, was für die Erzeugung einer **menschenzentrierten** Bedienungsanleitung (PDF)
erforderlich ist. Die Anleitung erklärt die **Bedienung des Interpreters**, nicht den Rechner C 8205; den Rechner
nur so weit, wie die Bedienung ihn braucht.

### 14.1 Zielgruppe und Ton

- **Leser:** Personen, die Testprogramme für den C 8205 schreiben und durchrechnen, ohne den Aufbau des Interpreters zu kennen.
  Kenntnis von Oktalzahlen und Grundbegriffen des Rechners (Register, Flags) wird nicht vorausgesetzt; Begriffe werden im Glossar erklärt.
- **Sprache:** Deutsch, knapp, in der Handlungsform („Starten Sie …“ oder Imperativ, einheitlich). Ein Satz, eine Handlung.
- **Terminologie einheitlich:** „Lochstreifenleser“ (Kürzel Leser), „Lochstreifenstanzer“ (Stanzer), „Schreibwerk“ (SW), „Testdatei“,
  „Tastenfolge“, „Trommeldatei“ (die persistente Datei `trommel.txt`; der Abschnitt `Trommeldatei:` einer Testdatei heißt in der Anleitung „Trommelabschnitt“). Kanäle immer als K0 bis K3.

### 14.2 Gliederung

| Kapitel der Anleitung | Inhalt | Quelle in dieser Datei |
|---|---|---|
| 1 Zu dieser Anleitung | Zweck, Zielgruppe, Symbole, Stand | 1, 14.1 |
| 2 Erste Schritte | Voraussetzungen, Ordner, Trommeldatei erzeugen, erster Lauf | 3, 4, 8.5 |
| 3 Tests schreiben | Aufbau der Testdatei, Marken, Tastenfolge, Trommel zwischen den Tests | 6, 7, 8.5 |
| 4 Interpreter starten | Aufruf, Schalter, Wrapper, Suche der Testdatei | 5 |
| 5 Ein- und Ausgabe | Kanäle, Schreibwerk, Leser, Stanzer, Tastatur | 8 |
| 6 Ergebnisse lesen | Bildschirm, Endzeile, Protokoll | 9 |
| 7 Wenn etwas schiefgeht | Fehlermeldungen mit Abhilfe | 10 |
| 8 Beispiele Schritt für Schritt | drei Beispiele mit Ausgaben | 13 |
| 9 Kurzreferenz | eine Seite: alle Schalter, Tokens, Kanäle | 5, 7, 8 |
| Anhang | Glossar, Grenzen des Interpreters, Verweise auf das Regelwerk | 11, 12 |

### 14.3 Pflichtinhalte und Gestaltung

- **Jede Handlung mit Beispiel:** Jeder Schalter und jedes Token erscheint mindestens einmal in einem lauffähigen Beispiel.
- **Echte Ausgaben:** Terminalausgaben werden aus tatsächlichen Läufen übernommen, nicht von Hand geschrieben. Feste Werte
  (Knotennummern) nur mit Vermerk, dass sie fassungsabhängig sind.
- **Farben erklären und nicht allein tragen lassen:** Dunkelgelb = Ausgabe des Rechners (Schreibwerk), Rot = Fehlermeldung.
  In Schwarz-Weiß-Druck muss die Bedeutung aus dem Text hervorgehen (z. B. Prefix „Fehler:“ bzw. Kennzeichnung im Beispiel).
- **Hinweis- und Warnkästen:** „Hinweis“ für Nützliches, „Achtung“ für Stellen, an denen Tests scheitern (z. B. `SW=1` vor `G`,
  Tastenfolge endet mit `R`, Zufalls-Zeichenlage KB/GB).
- **Hinweis zum Fenster `--SW-TERMINAL`:** Der Hinweiskasten aus Abschnitt 8.1 (Fenster bleibt immer offen bis X; Text mit der Maus markieren und kopieren) steht abgesetzt an den vier Stellen: im Kapitel „Interpreter starten“ beim Schalter, im Kapitel „Ein- und Ausgabe“ beim Schreibwerk, im Beispiel des Kapitels 8 und in der Kurzreferenz. Ein Hinweis, den Mauszeiger vor dem Aufruf in eine Bildschirmecke zu stellen, entfällt (überholt seit Interpreter-Version 0.03-007); der Schalter `--zwischenablage` gehört in die Schalterübersicht, die Zeile „Kopieren fehlgeschlagen“ ins Fehlerverzeichnis.
- **Codeblöcke** in Festbreitenschrift, Terminalausgaben von Eingaben unterscheidbar (Eingaben nach `$`).
- **Tabellen** für Schalter, Tokens, Kanäle, Fehlermeldungen (Vorlage: Abschnitte 5, 7, 8, 10).
- **Fehlerverzeichnis** alphabetisch oder nach Meldungstext auffindbar; jede Meldung mit Ursache und Abhilfe.
- **Glossar:** Akkumulator (AC), Befehlszähler (BZ), Adressregister (AR), Operationsregister (OR), Flag, Trommel, Trommeldatei (persistente Trommel), Sektor, Bahn,
  Oktal, Knoten, Konnektor, Phase I bis IV, Stub, Testmarke, Zeichenlage KB/GB, Kanal K0 bis K3, T/SW, Sprung-Umstellung.
- **Layout:** A4, Seitenzahlen, Inhaltsverzeichnis mit Seitenverweisen, Kopfzeile mit Titel und Stand, Kapitel beginnen auf neuer Seite.
  Die Kurzreferenz passt auf **eine** Seite und ist einzeln druckbar.
- **Stand und Version:** Datum und Versionsnummer des Interpreters (Ausgabe von `python3 c8205_interp.py --version`, Form `y.xx-zzz`) auf der
  Titelseite; die Anleitung gilt für die dort genannte Version.

### 14.4 Erzeugung

1. **Quelle:** Die Anleitung wird aus dieser Datei (Abschnitte 1 bis 13) abgeleitet, nicht kopiert; Fachtexte zum Rechner werden
   nur verlinkt oder als Glossareintrag verkürzt. Der Abschnitt 14 selbst gehört nicht in die Anleitung.
2. **Beispiele neu erzeugen:** Vor jeder Ausgabe alle Beispiele des Kapitels 8 mit dem aktuellen `c8205_interp.py` ausführen und die
   Ausgabe übernehmen (Farben in Screenshots oder farbigen Codeblöcken sichtbar machen).
3. **Werkzeug:** Die Anleitung entsteht mit reportlab aus `PDF-Erzeugung/build_anleitung.py` (Bausteine in `pdflib.py`, Schrift DejaVu Sans);
   der Text steht im Skript und wird von Hand aus dieser Datei nachgezogen, die Beispiele stammen aus echten Läufen (`runex.py`). Ablauf: `C8205-PDF-Erzeugung.md`.
   Der Zeichensatz muss `ä ö ü ß`, Oktalzahlen und die Symbole `→ ≤ ≥ …` darstellen.
4. **Abnahmeprüfung** vor Veröffentlichung:
   - jeder Schalter aus `python3 c8205_interp.py --help` kommt in der Anleitung vor,
   - jede Fehlermeldung aus Abschnitt 10 ist im Fehlerverzeichnis,
   - jedes Beispiel wurde mit der genannten Fassung ausgeführt,
   - Verweise auf Dateinamen entsprechen den tatsächlichen Namen (Präfix `C8205-Interpreter-`),
   - Glossar, Inhaltsverzeichnis und Kurzreferenz sind vollständig.

### 14.5 Pflege

Ändert sich der Interpreter (neuer Schalter, neues Token, neue Meldung, umgesetzter offener Punkt), sind in dieser Datei die Abschnitte
5 bis 11 und die Beispiele in 13 zu aktualisieren und die Anleitung neu zu erzeugen. Gelöste Punkte aus Abschnitt 11 werden dort
gestrichen und in 5 bis 9 beschrieben.
