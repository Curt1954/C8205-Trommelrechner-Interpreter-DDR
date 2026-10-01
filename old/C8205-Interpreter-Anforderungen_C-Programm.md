# Anforderungen für die automatische Erzeugung des C-Programms "Knotenautomat C 8205"

Stand: 27.09.2026 (SW-Ausgabe/KB-GB-Logik korrigiert: falsche SW-Wartebedingung entfernt, eigener
Ausgabe-Zustand `zs_sw_zeichenlage` ergänzt; zuvor: ANWEISUNG-008/009/017/031 an geändertes Regelwerk
angepasst; s. Abschnitt 15). Dieses Dokument sammelt alles, was ein Generator (und der
zugehörige handgeschriebene C-Code) wissen muss, um aus dem Regelwerk ein lauffähiges C-Programm zu
erzeugen. Es wiederholt das Regelwerk nicht, sondern verweist darauf und ergänzt, was für C
festzulegen ist.


**Statuskennzeichnung jeder Aussage:**

- **[F]** Festlegung: steht im Regelwerk oder ist vom Autor ausdrücklich vorgegeben.
- **[V]** Vorschlag: aus dem Regelwerk abgeleitet oder für C notwendig ergänzt; vom Autor zu bestätigen.
  Bis zur Bestätigung gilt der Vorschlag als Vorgabe für die Erzeugung.
- **[O]** offen: Das Regelwerk legt es nicht fest. Der Generator erzeugt dafür einen Stub, der beim
  Erreichen mit "ANWEISUNG-nnn nicht definiert (O-n)" ins Protokoll schreibt und den Lauf anhält
  (Regel "laut scheitern", s. 2.5). Die Nummern O-1 … O-5 verweisen auf Abschnitt 15.

---

## 1 Quellen (Regelwerk)

| Datei | Rolle für die Erzeugung |
|---|---|
| C8205-Interpreter-Eingänge_der_Knoten.md | Knotengraph: 78 Knoten, Eingänge, Typen, Texte, Ausgänge. Hauptquelle des Generators |
| C8205-Interpreter-Beschreibung_der_Knoten.md | Variablentabelle T2: Bedeutung und Behandlungsart jeder ANWEISUNG-nnn |
| C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md | Register, Flags, Wortformat, Feldaufteilung, Zahlensysteme |
| C8205-Interpreter-Befehlsliste-Zwischenstand.md | Befehlsdekodierung (B, A, Z) und Einzelbefehlsübersicht (Code → Wirkung) |
| C8205-Interpreter-Kodetabellen.md | Tabelle 1 (Lochstreifenkode) für Leser, Stanzer und Tastatur K0 |
| C8205-Interpreter-Magnettrommel.md | Trommelorganisation, Interleaving, Wortzeit, Bahnsperrenschalter |
| C8205-Interpreter-Bedienpult_mit_Schaltern.md | Tasten, Schalter, Kanalanwahl, typische Tastenfolgen |
| C8205-Interpreter-Lochstreifenleser.md | Leser 303 und Stanzer: Ablauf von Ein-/Ausgabe, Fehlerverhalten |
| C8205-Interpreter-Durchführung_eines_Tests.md | Trommeldatei, Tastenfolge, Testmarken (`#DOK`, `#SPEI`, `#SPUR`, `#PROT STUFE=n`), Ein-/Ausgabedateien, Protokollierungsstufen |
| C8205-Interpreter-Überblick_und_Gesamtaufbau.md | Vier Phasen, Wartezeiten, Leistungswerte |
| trommel.c/h, bahnsperre.c/h, unterbrechung.c/h | fixierte, vom Autor gelieferte C-Module (verbindlich, byte-identisch zu übernehmen, s. Abschnitt 4.0 und 4.4) |

---

## 2 Ziel und Betriebsarten

**2.1 Ziel [F].** Ein C-Programm (Arbeitsname `c8205`), das einen Test ausführt: Trommeldatei und
Tastenfolge definieren den Ausgangszustand; danach läuft der Knotenautomat ab Konnektor B (bzw. dem in
12.5 bestimmten Startpunkt), bis der Rechner in den Halt-Zustand übergeht. Dabei entstehen Protokoll und
Ausgabedateien.

**2.2 Zeitmodus (Programmschalter `--zeit`) [F/V].**

- `interpretativ` (Standard): alle Zeiten sind 0. ANWEISUNG-003 gilt als immer erfüllt, ANWEISUNG-004 hat
  keine Wirkung (T2, 004; Durchführung eines Tests, 1).
- `echt`: Die Trommeldrehung wird über das Modul `trommel` nachgebildet (T2, 004: "im C-Simulator muss die
  sektorweise Drehung nachgebildet werden"). Die Wartezeit entsteht ausschließlich in den Warteschleifen der
  Knoten 5/6, 26/27, 57/64 und 47/60.

**2.3 K0-Eingabequelle (Programmschalter `--k0`) [F].** `--k0 tastatur` (Host-Tastatur) oder
`--k0 datei=PFAD` (Textdatei). Beide Quellen liefern pro Eingabebefehl genau ein Zeichen (s. 11.6). Die
Vorgabe "beides, umschaltbar" stammt vom Autor.

**2.4 Generierter und handgeschriebener Code [V].** Der Generator (ein Skript, Sprache offen, Vorschlag
Python 3) liest die Regelwerk-Dateien und erzeugt reines C (C11 mit POSIX, `-D_POSIX_C_SOURCE=200809L`,
`-pthread`). Generierte Dateien tragen im Kopf den Vermerk "GENERIERT, nicht von Hand ändern". Sie
enthalten keine Logik, die im Regelwerk nicht steht.

**2.5 Regel "laut scheitern" [V].** Für jede ANWEISUNG, deren Definition [O] ist oder deren T2-Eintrag Behandlungsart
`V` trägt, erzeugt der Generator einen Stub. Ein Stub darf niemals stillschweigend "nichts tun". Er
gibt den Namen stets auf dem Bildschirm aus (unabhängig von `#PROT STUFE=n`, 12.2a/13.0 — wie die
Diagnoseausgabe bei Befehl 164, 13.1, ist ein Fehlerabbruch keine gewöhnliche Protokollzeile des
Knotenautomaten-Durchlaufs und wird deshalb nicht durch die Protokollierungsstufe unterdrückt) und
hält den Lauf mit Halt-Grund `NICHT_DEFINIERT` an.

---

## 3 Modulübersicht

| Modul | Status | Aufgabe |
|---|---|---|
| `trommel.c/h` | fixiert (s. 4.4) | Trommelspeicher, Drehung, Sektornummer, Lesen/Schreiben |
| `bahnsperre.c/h` | fixiert (s. 4.4) | Bahnsperrenschalter, Schreibschutz |
| `unterbrechung.c/h` | fixiert (s. 4.4) | Strg+C-Konvention (`abbruch_angefordert`) |
| `rechner.c/h` | neu, von Hand | Register, Flags, Zusatzzustand, Feldzugriffe (Abschnitte 5–7) |
| `kodetab.c/h` | generiert | Tabelle 1 aus Kodetabellen 1.4 (11.2) |
| `optab.c/h` | generiert | Code (B-A-Z) → Befehlsgruppe aus der Einzelbefehlsübersicht (10.3) |
| `knoten_gen.c/h` | generiert | Knotenautomat (Abschnitt 8) |
| `anweisungen.c/h` | von Hand (Stubs generiert) | je eine Funktion pro ANWEISUNG-nnn (Abschnitt 9) |
| `befehle.c/h` | von Hand | Grundoperationen für ANWEISUNG-021/022 (Abschnitt 10) |
| `bedienpult.c/h` | von Hand | Tastenfolge, Schalter, Ausgangszustand (Abschnitt 12) |
| `testlader.c/h` | von Hand | Trommeldatei, Testmarken (inkl. `#PROT`), Gültigkeitsprüfung (12.1–12.2a, 12.6) |
| `peripherie.c/h` | von Hand | Leser 1/2, Stanzer, SW-Ausgabe, K0-Eingabe (Abschnitt 11) |
| `protokoll.c/h` | von Hand | Protokolldatei und Bildschirm (Abschnitt 13) |
| `main.c` | von Hand | Programmschalter, Ablaufsteuerung, Aufräumen (Abschnitt 14) |

---

## 4 Regeln der vorhandenen Module (bindend)

**4.0 Grundsatz "unverändert benutzt" [F].** Die drei Module `trommel.c/h`, `bahnsperre.c/h` und
`unterbrechung.c/h` liegen als vom Autor fertiggestellte, geprüfte Dateien vor (Fassung s. 4.4). Sie
werden bei jeder Erzeugung eines C-Programms byte-identisch, ohne jede inhaltliche Änderung
übernommen und lediglich unverändert mitübersetzt/mitgelinkt:

- Der Generator erzeugt für diese drei Module keinerlei Code und schreibt sie nicht neu; er verweist in
  generiertem Code (z. B. `knoten_gen.c`, `optab.c`) nur auf ihre in 4.4 genannten Header-Deklarationen.
- Handgeschriebener Code (`rechner.c`, `bedienpult.c`, `testlader.c`, `peripherie.c`, `protokoll.c`,
  `main.c`) darf diese drei Module ausschließlich über die in `trommel.h`, `bahnsperre.h` und
  `unterbrechung.h` deklarierte Schnittstelle benutzen (aufrufen), niemals ihre `.c`-Dateien kopieren,
  patchen oder ihre Logik nachbilden.
- Stellt sich bei der Erzeugung oder beim Test heraus, dass eine dieser drei Dateien fachlich nicht zum
  übrigen Regelwerk passt (s. Beispiel in 4.1, Bekannte Abweichung), wird das hier im Anforderungsdokument
  vermerkt (Abschnitt 15) — die Datei selbst wird dadurch NICHT geändert, solange der Autor keine neue
  Fassung liefert. Jede vom Autor gelieferte Neufassung ersetzt die in 4.4 genannte Prüfsumme vollständig;
  bis dahin gilt ausschließlich die dort festgehaltene Fassung als verbindlich.

**4.1 trommel [F].**

- Adresse = 12 Bit (`Bahn<<5 | Sektor`), `trommel_sektor()` und `trommel_bahn()` sind bitweise.
- Die Koinzidenzprüfung gehört NICHT ins Modul. Der Aufrufer vergleicht
  `trommel_aktuelle_sektornummer` selbst (T2, 003).
- `trommel_lesen()` und `trommel_schreiben()` bearbeiten eine Zelle als `uint64_t` (33 Bit, 11 Oktalziffern).
- `trommel_schreiben()` liefert `TROMMEL_SCHREIBEN_GESPERRT`, wenn die Bahn gesperrt ist. Der Automat
  ignoriert den Rückgabewert im Befehlsablauf (Bahnsperre beeinflusst den Befehlsablauf nicht). Das
  Protokoll vermerkt den Fall als Hinweiszeile.
- Trommeldatei des Moduls: 4096 Zeilen `oooo wwwwwwwwwww`. Sie wird pro Lauf vom Testlader erzeugt (12.1).
- **Korrektur (Stand 26.09.2026, s. O-7 in Abschnitt 15) [F]:** In einer früheren Lieferfassung startete
  der Hintergrundthread `drum_hintergrundprozess()` seinen internen `index` unabhängig vom in
  `trommel_einschalten()` zufällig gezogenen Startwert immer bei 0; dadurch lief die Sektorfolge ab dem
  ersten Tick (< 1 Wortzeit) immer bei `PERM[1]` weiter, unabhängig vom zufällig gezogenen Startsektor.
  Das ist behoben: `trommel_einschalten()` hält den beim Ziehen des Zufallswerts verwendeten PERM-Index in
  der modulweiten Variablen `drum_start_index` fest (gesetzt VOR `pthread_create()`, also ohne
  Datenwettlauf), und `drum_hintergrundprozess()` initialisiert seinen `index` daraus statt mit einer
  festen 0. Die Sektorfolge setzt sich damit ab dem ersten Tick lückenlos an der zufällig gezogenen Stelle
  fort. Verifiziert durch Testlauf (`drum_start_index`-Wert vor dem ersten Tick vs. `PERM`-Nachfolgewert
  nach dem ersten Tick, für mehrere Läufe reproduziert).

**4.1a Polling-Intervall der Koinzidenzprüfung [V].** Die Koinzidenzprüfung (ANWEISUNG-003) liegt
außerhalb des Moduls `trommel` beim Aufrufer (s. 4.1). Im Modus `echt` MUSS diese Prüfung **gedrosselt
per `nanosleep()` alle 20 µs** erfolgen, nicht als ungedrosselter Busy-Spin:

```c
struct timespec poll = { .tv_sec = 0, .tv_nsec = 20000L }; /* 20 µs */
while (trommel_aktuelle_sektornummer != trommel_sektor(reg_AR) && !abbruch_angefordert) {
    nanosleep(&poll, NULL);
}
```

Begründung: `trommel_aktuelle_sektornummer` ändert sich alle 104 µs (`TICK_NS`, s. `trommel.c`); ein
Busy-Spin läse die Variable dagegen ungebremst zehntausendfach pro Wortzeit und bindet dabei einen
CPU-Kern vollständig (Lastspitze, unnötige Wärmeentwicklung) ohne jeden Korrektheitsgewinn gegenüber
gedrosseltem Polling. 20 µs wurden gewählt, weil sie sicher unter der 104-µs-Standzeit eines
Sektorwerts liegen (Faktor ≈5) und damit praktisch ausschließen, dass ein Koinzidenz-Fenster durch
Scheduler-Jitter übersprungen wird; `nanosleep()` garantiert dabei nur ein *Mindest*-Schlafintervall,
kein exaktes (OS-Scheduler-Jitter möglich). Ein einzelnes verpasstes Fenster wäre unkritisch (nächste
Koinzidenz nach spätestens einer vollen Trommelumdrehung), aber unerwünscht häufig, daher der
Sicherheitsfaktor ≈5. Betrifft ausschließlich die aufrufende Seite (`anweisungen.c`, ANWEISUNG-003);
`trommel.c/h` selbst bleibt unverändert (4.0).

**4.2 bahnsperre [F].** Die sechs Schalterstellungen kommen ausschließlich von außen über
`bahnsperre_setzen()`. Im Programm geschieht das über die Schalterdatei (12.4). Es gibt keine
Konfigurationsdatei im Sinne des Moduls.

**4.3 unterbrechung [F].**

- `unterbrechung_einrichten()` wird einmal zu Programmbeginn aufgerufen.
- JEDE wartende Schleife prüft zusätzlich zu ihrer Abbruchbedingung `abbruch_angefordert`. Das betrifft:
  - die Schleifen 5↔6, 26↔27, 57↔64 und die Wartezeiten in 47 und 60,
  - die zentrale Schleife des Knotenautomaten (bei jedem Knoten; sonst würde im Modus `interpretativ` eine
    Endlosschleife des Anwenderprogramms Strg+C nie sehen),
  - das Warten auf Eingabe (Leser ohne Streifen, K0),
- Bei Abbruch: Protokoll abschließen, `trommel_ausschalten()`, Dateien schließen, Terminal zurücksetzen (11.6),
  Ausstieg mit Exit-Code 130. `sigaction()` wird bewusst OHNE `SA_RESTART` eingerichtet, damit
  unterbrochene wartende Systemaufrufe (z. B. beim Lesen von K0) mit `EINTR` zurückkehren, statt automatisch
  neu zu starten (s. Kommentar in `unterbrechung.c`).

**4.4 Fixierte Fassung der drei Module (Dateikennung) [F].** Stand 26.09.2026, nach Korrektur des
Startindex-Fehlers in `trommel.c` (s. 4.1) vom Autor als Upload geliefert. Nur diese exakten Dateien
(SHA-256, vollständig, über den unveränderten Dateiinhalt) gelten als
verbindlich im Sinne von 4.0; jede automatisierte oder manuelle Erzeugung des C-Programms MUSS diese
Prüfsummen vor dem Build gegenprüfen und bei Abweichung abbrechen, statt stillschweigend mit einer anderen
Fassung weiterzumachen:

| Datei | Zeilen | SHA-256 |
|---|---|---|
| `trommel.h` | 49 | `c104ce3b8a316694b4fe21de8ddd3171f1e32db6c8e8a0fc836f6490723545e8` |
| `trommel.c` | 124 | `ca51d4dd8064d3e096f501b79ece31758126e2c0a5277cb2207a0eaa8b35cc07` |
| `bahnsperre.h` | 51 | `af5d86e8ac11e1d52c0983eefa6b886757d8af09668a611a8613cf8b2b88ce00` |
| `bahnsperre.c` | 40 | `80344cd84c2151a5938451d160a1be9d8efda88e11e6ee78e6f3c007aa1bb31d` |
| `unterbrechung.h` | 25 | `7328e632613fbfa7b0bf24dee4c3fc2a59963752df7947e2ceba0d247d93242d` |
| `unterbrechung.c` | 23 | `20a819fe64d3107079c7b2d59894362050997065f7108730897107a2d42c462e` |

`main.c` (bzw. der Build-Prozess, s. 14.1/14.2) bindet diese sechs Dateien unverändert ein (Compile &
Link der `.c`-Dateien, `#include` der `.h`-Dateien); es gibt keinen Bearbeitungsschritt des Generators, der
sie durchläuft. Die beiden mitgelieferten Wegwerf-Rahmenprozesse `testframe.c` (mit `unterbrechung`) und
`testframe_trommel.c` (ohne `unterbrechung`, ältere Fassung ohne Strg+C-Behandlung) sind keine Bestandteile
des zu erzeugenden `c8205`-Programms, sondern nur Testnachweise für das Zusammenspiel der Module; sie
werden vom Generator nicht übernommen.

---

## 5 Zahlen und Datentypen

**5.1 Wortbreite [F].** Speicherzellen und der AC werden IMMER als `uint64_t` geführt. Maske
`#define MASK33 0x1FFFFFFFFULL`. Nach jeder Anweisung, die ein 33-Bit-Wort verändert, wird mit `MASK33`
maskiert.

**5.2 Bitabbildung [F/V].** z₀ ist das linke (höchstwertige) Bit, z₃₂ das rechte. Es gilt
`z_i = Bit (32 − i)` des `uint64_t`. Makros: `Z(w,i) = (w >> (32 - (i))) & 1`.

**5.3 Zahlensysteme [F].** Original-Zahlen (Befehle, Register, Speicher) sind oktal, außer ausdrücklich dual
oder dezimal. Ein-/Ausgabe: Adressen `%04o`, Worte `%011llo`. Referenznummern (Knoten, ANWEISUNG-nnn) sind
dezimal.

**5.3a C-Literale [V].** Oktale Konstanten im Quelltext mit führender 0 (`015`, `0400`). Vorsicht bei
Bezeichnern wie `ANWEISUNG-008`: nicht als oktale Zahl lesen.

**5.4 Vorzeichenbehandlung [F/V].**

- Dualzahlen sind Festkomma, Komma zwischen z₀ und z₁, z₀ = Vorzeichen, negative Zahlen als Zweierkomplement
  über 33 Bit (Datenstruktur, Dualzahlen).
- Das Vorzeichenbit z₀ liegt in `uint64_t` bei Bit 32, mitten im Wort. C-Vergleiche (`< 0`, `<`, `>`) und
  der C-Vorzeichentest dürfen auf 33-Bit-Werten deshalb NIE direkt benutzt werden; die Bits 33–63 sind
  "abgeschnitten" und müssen immer 0 sein. Vorzeichenbehaftete Auswertung (Vergleich, Test AC<0,
  Addition/Subtraktion, bedingte Befehle) läuft ausschließlich über die Regeln in 5.6.
- Vorzeichenbit für "AC<0": z₀ (Bit 32); bei R=1 gilt z₃₂ (Bit 0) (Befehlsliste 4.1.6).

**5.5 Wertebereiche [F].** BZ und AR sind 12 Bit (Rechnung modulo 4096), OR 9 Bit, Sektor 5 Bit, Bahn 7 Bit.

**5.6 33-Bit-Arithmetik in `uint64_t` [F/V].** Das Datenformat ist Zweierkomplement über 33 Bit (die Angabe
z = Σ zᵢ·2⁻ⁱ ist derselbe Wert, skaliert mit 2⁻³²). Weil C nur 64-Bit-Zweierkomplement kennt, gelten in
`rechner.c` (Makros/Inline-Funktionen, sonst nirgends) folgende Regeln:

- **Invariante:** Jeder Wert eines 33-Bit-Worts (AC, Speicherzelle, Zwischenwerte) erfüllt
  `(w & ~MASK33) == 0`. Im Debug-Übersetzungslauf wird das an jeder Schnittstelle mit `assert` geprüft.
- **Vorzeichentest:** `#define NEG33(w) (((w) >> 32) & 1)`. Nie `(int64_t)w < 0`.
- **Vorzeichenerweiterung** (nur für Vergleiche und Zahlenwert-Auswertung), ohne implementierungsabhängiges
  Verhalten:
  ```c
  static inline int64_t sext33(uint64_t w) {          /* w bereits maskiert */
      return NEG33(w) ? -(int64_t)((~w + 1) & MASK33) : (int64_t)w;
  }
  ```
  Vergleiche (Vergleicher V1/V2, Tests "AC<0", "AC≥0", Vorzeichenbefehl, bedingte Addition/Subtraktion)
  benutzen `sext33()` beider Seiten. Ein Vergleich der rohen `uint64_t`-Werte ist falsch, weil negative
  Zahlen dann größer als alle positiven wären.
- **Addition/Subtraktion:** `r = (a ± b) & MASK33`. Überlauf (Zahlenbereich 33 Bit überschritten) bei Addition:
  `((a ^ r) & (b ^ r) & SIGN33) != 0`; bei Subtraktion (a − b):
  `((a ^ b) & (a ^ r) & SIGN33) != 0` mit `SIGN33 = 1ULL << 32`. Der Umgang mit `fl_FUE` steht in 10.6.
- **Negation** (bedingte Add./Sub., R-Befehl mit −): `(~x + 1) & MASK33`. Das entspricht der Originalregel
  "alle Bits vor dem niedrigstwertigen 1-Bit negieren".
- **Bitweise Operationen:** Bei `~AC` (Konjunktion mit negiertem AC) gilt `(~ac) & MASK33`, sonst stehen
  die Bits 33–63 auf 1.
- **Verschiebungen:** R=1 (Rechtsverschiebung, z₀ := 0) ist logisch: `ac >> 1` (Bit 32 wird 0, weil Bit 33 ff.
  schon 0 sind). R=2: `(ac << 1) & MASK33`. R=3: `((ac << 1) & MASK33) | NEG33(ac)`.
- **Laden aus der Trommel:** `trommel_lesen()` liefert höchstens 11 Oktalziffern, also ≤ 2³³−1; die Invariante
  ist damit automatisch erfüllt. Für `trommel_schreiben()` ist sie Voraussetzung.
- **Vorzeichenlose Sicht:** Bei vorzeichenlosen Zahlen ist z₀ das höchstwertige Bit; diese Sicht wird nur für
  bitweise Operationen und Transport gebraucht und benötigt keine Erweiterung.

---

## 6 Register, Flags und Zusatzzustand

**6.1 Register [F].**

| C-Name | Breite | Bedeutung |
|---|---|---|
| `reg_AC` | 33 (`uint64_t`) | Akkumulator |
| `reg_BZ` | 12 | Befehlszähler |
| `reg_AR` | 12 | Adreßregister (Zellenwähler; zugleich Adreßteil a des BR) |
| `reg_OR` | 9 | Operationsregister, identisch mit BAZ |
| BR | 21 | Befehlsregister = AR‖OR (kein eigener Speicher, nur Sicht) |

V1 und V2 sind Flags (Vergleicher). Namensbereiche sind getrennt (Datenstruktur, Namensbereiche):
Flags erhalten das Präfix `fl_`, Register `reg_`, Befehlsfelder `feld_`. Das vermeidet Kollisionen wie
Flag A und Feld A.

**6.2 Flags [F].** `fl_E, fl_A, fl_T, fl_SW, fl_K1, fl_K2, fl_K3, fl_FE, fl_FUE (FÜ), fl_BS, fl_US, fl_V1,
fl_V2, fl_H, fl_SP`. T und SW sind alternativ (nie beide 1). K0 hat kein eigenes Flag, sondern T bzw. SW.
`fl_H` (Halt/Rechnen, Schalter H-R) und `fl_SP` (Schalter SP) sind inzwischen in die Flagtabelle der
Datei "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md" aufgenommen worden (O-3, geklärt) und damit reguläre Flags wie alle anderen. Schalter
und Flag desselben Namens sind dieselbe Sache (Datenstruktur, Erläuterung zu BS). Der Schalter LS hat für
die Nachbildung keine Bedeutung (Bedienpult) und wird nicht geführt.

**Korrektur (Stand 27.09.2026):** Frühere Fassungen dieses Dokuments nannten hier ANWEISUNG-009 und -031
als Abfragestellen von `fl_SP`. Nach der aktuellen Fassung von T2 (Beschreibung der Knoten) fragt
ANWEISUNG-031 tatsächlich den Schalter **BS** ab (nicht SP, s. 9.4), und ANWEISUNG-009 testet AC-Vorzeichen,
Vergleicher V1/V2 und `fl_FUE` (ebenfalls s. 9.4) — beide fragen SP nicht (mehr) ab. Im derzeitigen
Regelwerk wird `fl_SP` von keiner ANWEISUNG-nnn ausgewertet; der Flag bleibt trotzdem Teil der
Flagtabelle (Datenstruktur, Bedienpult: Schalter SP), da er dort unabhängig vom Knotenautomaten definiert
ist. Sollte sich das als Lücke im Regelwerk herausstellen, ist das kein Fehler dieses Dokuments, sondern
Sache des Regelwerks selbst.

**6.3 Zusatzzustand des Automaten (im Regelwerk nicht als Register benannt) [V].**

| C-Name | Bedeutung |
|---|---|
| `zs_phase` | zuletzt betretene Phase I–IV (gesetzt an den Phasenzuordnungsknoten) |
| `zs_adr` | Adreßteil ADR des in Phase II entnommenen Befehlswortes (Puffer, siehe 005/007) |
| `zs_x_merker` | Merker "X-Abbruch aufgetreten" (T2, 002); wird an Knoten 78 (ANWEISUNG-044) gesetzt und beim Auswerten an Knoten 4 (Test 002) gelöscht (Verbrauch bei Konsum) |
| `zs_sektorzaehler` | Zahl der in Phase IV bearbeiteten Sektoren (T2, 040) |
| `zs_vgl_ac`, `zs_vgl_v` | AC und Vergleichsgröße v, festgehalten für ANWEISUNG-037 (10.2) |
| `zs_zeichenlage` | KB/GB der EINGABE, Start KB, geändert durch gelesenes Um. KB/Um. GB (11.7) |
| `zs_sw_zeichenlage` | KB/GB der SW-AUSGABE, zufällig beim Einschalten gesetzt, geändert durch Ausgabe-Adresse 117x/057x (11.5) |
| `zs_halt_grund` | Halt-Ursache (Endknoten-Nr., `US`, `BS`, `FE`, `NICHT_DEFINIERT`, `ABBRUCH`, `EINGABE_ENDE`) |
| `zs_kanal` | aktuell angewählter Kanal 0–3 (abgeleitet aus fl_T/fl_SW/fl_K1–K3) |

---

## 7 Befehlswort und Feldzugriff [F]

Das Maschinenwort hat 33 Bit. z₀–z₁₁ sind "beliebig", z₁₂–z₃₂ der Maschinenbefehl (21 Bit).

| Feld | Bits | C-Ausdruck (Wort `w`) |
|---|---|---|
| Adresse ADR (a) | z₁₂–z₂₃ | `(w >> 9) & 0xFFF` |
| Spur/Bahn | z₁₂–z₁₈ | `(ADR >> 5) & 0x7F` (= `trommel_bahn`) |
| Sektor | z₁₉–z₂₃ | `ADR & 0x1F` (= `trommel_sektor`) |
| Operation OP (BAZ, OR) | z₂₄–z₃₂ | `w & 0x1FF` |
| B (Befehlstyp) | z₂₄–z₂₆ | `(OP >> 6) & 7` |
| A (Operationsart) | z₂₇–z₂₉ | `(OP >> 3) & 7` |
| Z (Operationszusatz) | z₃₀–z₃₂ | `OP & 7` |
| R (Resultatbehandlung) | z₃₀–z₃₁ | `(OP >> 1) & 3` |
| L (Löschbit) | z₃₂ | `OP & 1` |
| z₃₀ (Hilfsausdruck in T2) | z₃₀ | `(OP >> 2) & 1` (= 1 für Z ≥ 4) |

Der Code `BAZ` wird als dreistellige Oktalzahl B-A-Z gelesen (Beispiel 164 = B 1, A 6, Z 4).
Anwahl: `z₁₂ = 1` ⇔ `ADR & 04000`.

---

## 8 Knotentabelle → Automat (Generator)

**8.1 Eingabeformat [F].** Datei "C8205-Interpreter-Eingänge_der_Knoten.md". Kommentarzeilen beginnen mit `#`. Datenzeile:

`Knotennummer; Eingänge; Typ; Text; Ausgänge`

- Eingänge: Liste von Ganzzahlen, getrennt durch Leerzeichen; `-` = kein Eingang.
- Typ: `Konnektor`, `Phasenzuordnung`, `Anweisung`, `Test`.
- Text: Klartext oder `$ANWEISUNG-nnn` (aufgelöst über T2). `&&` trennt gleichzeitige Anweisungen.
- Ausgänge: Anweisung/Phasenzuordnung `Ziel(Eingang)`; Test `Ziel(Eingang falsch) | Ziel(Eingang wahr)`;
  `---` = Endknoten ohne Ausgang.

**8.2 Parser [V].** Feldtrennung an `;` (Text und Ausgangsfeld dürfen keine `;` enthalten; bei Konnektoren
ist das Ausgangsfeld u. U. ein Kommentar wie "verbindet mit Konnektor 4 in Knoten 54" und wird nicht als
Ausgang gelesen). Ausgang-Muster: `(\d+)\((\d+)(?: (falsch|wahr))?\)`.

**8.3 Konnektoren [F].**

- Konnektoren mit gleichem Namen (Text) sind verbunden, auch wenn Ein- oder Ausgang fehlt. Der Text
  "verbindet mit …" ist nur Kommentar.
- Konnektor `B` ist extern: Eintritt in den Ablauf von außen (Knoten 1), kein Gegenstück in der Tabelle.
- Auflösung im Generator: Genau ein Knoten je Konnektorname trägt einen Ausgang (Fortsetzung). Ein Zielknoten
  ohne Ausgang wird durch einen Sprung zu diesem Knoten ersetzt. Konnektorgruppen (Stand heute):
  `1` = {7 (Fortsetzung → 6), 63}, `2` = {29 (→ 57), 51}, `3` = {72 (→ 26), 52}, `4` = {54 (→ 55), 41, 53}.
  Mehr als ein Fortsetzungsknoten je Gruppe ist ein Generatorfehler.
- Mehrfachverbindungen sind zulässig, ohne Änderung der Ein-/Ausgangszahl.

**8.4 Validierung vor der Erzeugung [V].** Der Generator bricht ab, wenn eine Prüfung fehlschlägt. Alle
Prüfungen sind auf dem Stand vom 28.09.2026 bestanden (78 Knoten, s. **Korrektur 28.09.2026** unten):

1. Jeder Ausgang zeigt auf einen existierenden Knoten.
2. Der Zieleingang ist beim Zielknoten deklariert.
3. Jeder deklarierte Eingang hat genau eine Quelle (Ausnahme: Konnektoren).
4. Jeder Test hat genau zwei Ausgänge (falsch, wahr).
5. Jeder Knoten ist ab Knoten 1 (unter Beachtung der Konnektoren) erreichbar.
6. Jede `$ANWEISUNG-nnn` ist in T2 definiert. T2-Einträge dürfen nur indirekt referenziert sein
   (ANWEISUNG-040/-041/-042 über -024).
7. Jede ANWEISUNG-nnn kommt nur in einer Rolle vor (Test oder Anweisung). Das ist heute erfüllt.

**Korrektur 28.09.2026:** Der Graph wurde um sechs Knoten (73–78) erweitert, um den X-Abbruch der
verkürzten Gruppen-/Wiederholungsbefehle (B=5, B=7) mit der Befehlsliste (4.1.6) in Einklang zu bringen.
Bisher brach der Automat bei negativem AC (ANWEISUNG-042) sofort ab (Knoten 35), ohne die zugehörige
Zelle zu Ende zu bearbeiten; ein am Autor durchgeführter Test (`0021-544`) hat gezeigt, dass die Zelle,
bei der AC negativ wird, noch vollständig verarbeitet (insbesondere gespeichert) werden muss. Ablauf jetzt:
An Knoten 35 wird nur noch die normale Abbruchbedingung (ANWEISUNG-024 = 040 ODER 041) geprüft. Ist sie
falsch, prüft Knoten 73 die X-Bedingung (ANWEISUNG-042). Ist auch sie falsch, geht es wie bisher zu Knoten 32
(nächste Zelle). Ist sie wahr, wird genau eine weitere Zelle mit Operation und Resultatbehandlung bearbeitet
(Knoten 74–76: nächster Sektor, Operation, Resultatbehandlung), an Knoten 77 nochmals die normale
Abbruchbedingung geprüft (Vorrang, wie bisher an Knoten 35) und andernfalls an Knoten 78 (ANWEISUNG-044) der
Merker "X-Abbruch aufgetreten" gesetzt, bevor der Automat abbricht. ANWEISUNG-024 wurde entsprechend auf die
normale Abbruchbedingung allein reduziert (Test an Knoten 35 UND 77); ANWEISUNG-042 wird jetzt ausschließlich
an Knoten 73 getestet; das Setzen des Merkers wandert von ANWEISUNG-024 in die neue ANWEISUNG-044.


**8.5 Erzeugter Code [V].** Ein Automat als Zustandsmaschine:

```c
typedef enum { HALT_ENDKNOTEN, HALT_ABBRUCH, HALT_FEHLER } automat_ergebnis_t;
automat_ergebnis_t automat_lauf(int startknoten);
```

- Eine Schleife `for (;;) { if (abbruch_angefordert) ...; prot_knoten(k); switch (k) { case 1: ... } }`.
- Je Knoten ein `case` mit Kommentar (Typ, Text, T2-Kurztext).
- Anweisung: `anw_nnn(); k = ZIEL; eing = ZIELEINGANG;` (jeder Sprung merkt sich den Zieleingang)
- Test: `k = test_nnn() ? WAHR_ZIEL : FALSCH_ZIEL;`
- Phasenzuordnung: `zs_phase = P; prot_phase(P); k = ZIEL;`
- Endknoten (`---`): `anw_030(k, eing); zs_halt_grund = Knoten-Nr.; return HALT_ENDKNOTEN;` (`eing` ist der Eingang, über den der Knoten betreten wurde; Knoten 45 hat zwei Eingänge mit verschiedenem Halt-Grund). Alle fünf Endknoten (30/45/46/58/66) tragen im Graph den Text `$ANWEISUNG-030`.
- Konnektor: erzeugt keinen eigenen Code, die Sprünge gehen direkt auf die Fortsetzung.
- Eingangsnummern haben keine Laufzeitbedeutung (sie ordnen nur die Kanten). Mehrfacheingänge sind normale
  Sprungziele.

**8.6 Phasen [F].** Die Phasenzuordnungsknoten sind 2 (Beginn Phase I), 8 (II), 15 (III), 31/61/67 (IV). Eine
Phase dauert im Modus `echt` eine Wortzeit (104 µs) (Überblick, Abschnitt 4). Zwischen Phase III und IV
liegt die Koinzidenz-Wartezeit (Knoten 26 und 57).

**8.7 Haltepunkte im Graph [F].** Für E-Einzelschritt und Halt (12.5) werden zwei Prüfpunkte benötigt:
HP2 = Eintritt in Knoten 8 (vor Phase II) und HP3 = Eintritt in Knoten 19 (Ende der Phase-III-Arbeit
15–18: Adreßaufstellung und Löschbit; danach beginnt die Entschlüsselung). Geklärt (O-1): HP3 ist der
eigentliche Halt-Punkt für den Schalter H — der Automat hält immer erst nach vollständiger Bearbeitung
des aktuellen Befehls, also nach der nächsten erreichten Phase III; R hebt diesen Halt auf, die Schleife
läuft ab HP3 weiter. HP2 ist kein eigener Haltepunkt des Graphen (Knoten 8 ist der reguläre
Phasenzuordnungsknoten "Beginn Phase II", s. 8.6), sondern wird nur zusätzlich für die feinere
Schrittweite der Taste E gebraucht.

**8.8 Hooks [V].** Der Generator fügt an festen Stellen Aufrufe ein: `prot_knoten(k)` beim Betreten jedes
Knotens (Ziel abhängig von `#PROT STUFE=n`, s. 13.0), `debug_hook_nach_022()` nach den Knoten mit
ANWEISUNG-022 (33, 62, 70), stets auf den Bildschirm und zusätzlich in die Protokolldatei bei `STUFE=2`
(13.1).

---

## 9 Variablentabelle T2 → Anweisungsfunktionen

**9.1 Parser [V].** Eine T2-Zeile lautet `ANWEISUNG-nnn; Beschreibung; Behandlungsart`. Die Behandlungsart
ist das erste Feld, das (nach `;`) genau `ARW`, `AH`, `ZST` oder `V` lautet — alle vier Werte laut
Kopfkommentar der Variablentabelle T2, nicht nur die ersten drei. Kommentare (`# …`) hinter dem Feld oder innerhalb der Beschreibung
werden ignoriert (ANWEISUNG-018 hat den Kommentar in der Beschreibung). Die heute definierten 42
Einträge: 38 ARW, 3 AH, 1 ZST (ANWEISUNG-030), 0 V. **Korrektur (Stand 27.09.2026):** ANWEISUNG-009 ist in
der aktuellen T2-Fassung als `ARW` geführt, nicht mehr als `AH`; frühere Fassungen dieses Dokuments zählten
sie versehentlich zu den AH-Einträgen (dadurch vormals fälschlich "37 ARW, 4 AH").

**9.2 Behandlungsarten [F].**

- `ARW`: Rechenwerk-Operation, direkt als C-Anweisung formulierbar.
- `AH`: durch Hardware ausgeführt (003, 004, 031); wird gegen Modulzustand bzw. Flags abgebildet.
  (**Korrektur 27.09.2026:** ANWEISUNG-009 gehört nach aktueller T2-Fassung nicht mehr hierher, s. 9.4.)
- `ZST`: End-Zustand, den der Knotenautomat erreicht (T2-Kopfkommentar); im Regelwerk bislang nur
  ANWEISUNG-030 ("unbedingter Stopp-Befehl", s. 9.4). Wird nicht als gewöhnliche `anw_nnn()`-Funktion
  übersetzt, sondern über den Endknoten-Mechanismus in 8.5 als `anw_030(knoten, eingang)` abgebildet
  (s. 9.4, Nr. 030) — `ZST` besagt hier nur, dass mit ihr der Automatenlauf endet, nicht, dass sie
  anders generiert würde als eine `ARW`-Anweisung.
- `V`: allgemein, braucht Detailklärung → Stub (2.5).

**9.3 Funktionsschema [V].** `int test_nnn(void)` für Tests, `void anw_nnn(void)` für Anweisungen. `&&` in
Beschreibungen bedeutet gleichzeitig: Alle rechten Seiten werden mit den Altwerten ausgewertet.
Klammerung: Wo T2 "ODER"/"UND" ohne Klammern mischt (008, 040, 041, 042), gilt die im Kommentar bzw.
Kontext erkennbare Klammerung (siehe Tabelle).

**9.4 Definition je ANWEISUNG.** `B`, `A`, `Z`, `L`, `z30` stehen für die Felder aus Abschnitt 7 des Inhalts
von `reg_OR`.

| Nr. | Rolle | C-Umsetzung | Status |
|---|---|---|---|
| 001 | Anw | `t_ar=AR; t_bz=BZ; AR=t_bz; BZ=(t_ar+1)&0xFFF;` (gleichzeitig). In Phase I (Knoten 3) ist der BZ-Wert unbrauchbar, wird aber in Phase II immer überschrieben (Knoten 11 bzw. 37) | F/V |
| 002 | Test | `int r = zs_x_merker; zs_x_merker = 0; return r;` (Löschen des Merkers beim Auswerten) | F |
| 003 | Test (AH) | `echt`: Polling-Intervall 20 µs statt ungedrosseltem Busy-Spin (CPU-Entlastung, s. 4.1a): `struct timespec poll={0,20000L}; while (trommel_aktuelle_sektornummer != trommel_sektor(reg_AR) && !abbruch_angefordert) nanosleep(&poll, NULL);` liefert danach `trommel_aktuelle_sektornummer == trommel_sektor(reg_AR)`; `interpretativ`: 1 | F/V |
| 004 | Anw (AH) | `echt`: warten, bis sich `trommel_aktuelle_sektornummer` ändert (= eine Wortzeit), mit Prüfung auf `abbruch_angefordert`; `interpretativ`: keine Wirkung. Die Verdrahtung (zurück zum Test bzw. Neustart Phase I) ergibt sich allein aus dem Graph | F/V |
| 005 | Anw | Befehlsentnahme: `w = trommel_lesen(reg_AR)`; `reg_OR = w & 0x1FF`; `zs_adr = (w>>9) & 0xFFF`. Die Entnahme steht nirgends als eigener Knoten und wird hier ergänzt | V |
| 006 | Test | `(B!=0 && B!=1) && (A==5 \|\| A==7) && L==1` | F |
| 007 | Anw | `reg_BZ = zs_adr` | F |
| 008 | Test | `(B<=1) && (A==4 \|\| A==5 \|\| A==7)` (**Korrektur 27.09.2026:** T2 wurde geändert; frühere Fassung dieser Zeile lautete `(B==0\|\|B==1) && A==6 && z30`, das entspricht nicht mehr dem aktuellen Regelwerk) | F |
| 009 | Test | `(B==0 && A==4 && ac_negativ()) \|\| (B==0 && A==5 && !ac_negativ()) \|\| (B==1 && A==4 && (fl_V1 \|\| (fl_V1 && fl_V2))) \|\| (B==1 && A==5 && (fl_V2 \|\| (fl_V1 && fl_V2))) \|\| (B==0 && A==7 && fl_FUE) \|\| (B==1 && A==7 && (fl_V1 && fl_V2))` — Klauseln je B/A-Kombination: B=0 (bedingter Stopp) prüft AC-Vorzeichen bzw. `fl_FUE`, B=1 (bedingter Sprung mit Rückkehrabsicht) prüft die Vergleicher V1/V2 (V3 := `fl_V1 && fl_V2`, Datenstruktur). `V1 ODER V3` bzw. `V2 ODER V3` sind wörtlich aus T2 übernommen, obwohl `V1 ODER V3` wegen V3⇒V1 logisch auf `V1` reduzierbar wäre (Vereinfachung vom Autor zu bestätigen). **Korrektur 27.09.2026:** ANWEISUNG-009 ist in T2 jetzt `ARW` (nicht mehr `AH`) und testet nicht mehr `fl_SP`; frühere Fassung dieser Zeile war veraltet | F/V |
| 010 | Anw | `A := 2`: `reg_OR = (reg_OR & ~070) \| 020` | F |
| 011 | Test | `L == 1` | F |
| 012 | Anw | `reg_AC = 0` | F |
| 013 | Test | `(B<=1) && A==2 && z30` (Sprung mit Rückkehrabsicht, auch nach Umstellung durch 010; die B-Bedingung schließt Einzelbefehle wie die Subtraktion aus). | F |
| 014 | Test | `(B<=1) && A==2 && !z30` (Unbedingter Stop 1. Art; an Knoten 42 gebraucht, um innerhalb der Weiche von Test 043 zwischen A=2- und A=6-Fall zu unterscheiden) | F |
| 015 | Test | `(B<=1) && A==1` | F |
| 016 | Test | `(B<=1) && A==3` | F |
| 017 | Anw | Ausgabe-Halt-Befehl 03Z (A=3): keine eigenständige Wirkung über ANWEISUNG-028 hinaus (T2-Wortlaut), d. h. AC wird ausschließlich der Löschanweisung (L) unterworfen, sonst keine Wirkung auf AC; höchstens Herauslösung der drei informationstragenden Triaden a1,a2,a3 aus dem Adreßteil (ADR hier als Datencode, nicht als Speicheradresse; a4 ungenutzt). **Korrektur 27.09.2026:** T2 nennt jetzt drei Triaden a1,a2,a3 (vormals in dieser Zeile fälschlich nur a1,a2 mit "a3,a4 ungenutzt"); außerdem lief die Beschreibung "nur Vorbereitung für 028" der tatsächlichen Knotenreihenfolge zuwider — Knoten 39 (ANWEISUNG-028) wird laut Graph VOR Knoten 23 (ANWEISUNG-017) durchlaufen, 017 kann also nicht "Vorbereitung für" 028 sein, sondern ist (wie T2 sagt) wirkungslos über das durch 028 bereits Festgelegte hinaus. Eine etwaige Z≥4-Umstellung (wie bei A=2, s. 013) ist hier ohne Wirkung, weil ihre Bedingung nur in Phase II auswertbar wäre; Phase IV entfällt für diesen Befehl (Organisationsbefehl, s. Knoten 22 → 2(5): Rücksprung direkt zu Phase I), daher auch keine Resultatbehandlung | F |
| 018 | Test | `(B<=1) && (A==0 \|\| A==4 \|\| A==5 \|\| A==7)` (Kontext: A=1,2,3 und A=6/z30 sind vorher ausgeschieden) | F |
| 019 | Test | `B == 3` | F |
| 020 | Test | `fl_FUE` | F |
| 021 | Anw | Ausführung gemäß BAZ. T2 verweist ausdrücklich auf die Befehlsliste (Abschnitt 4.3 und "Einzelbefehlsübersicht") als alleinige Quelle der Einzelformeln, s. Abschnitt 10 | F |
| 022 | Anw | Resultatbehandlung, s. Abschnitt 10 | F/O |
| 023 | Test | `B >= 4` | F |
| 024 | Test | `return t040() \|\| t041();` (an den Knoten 35 und 77; reine Prüfung der normalen Abbruchbedingung. Die X-Bedingung wird gesondert an Knoten 73 getestet, s. **Korrektur 28.09.2026** und Knoten 042/044) | F |
| 025 | Anw | `reg_AR = (reg_AR & ~0x1F) \| ((reg_AR + 015) & 037)` (nächster Sektor in physischer Folge; die Bahn bleibt) | F |
| 026 | Anw | `reg_BZ = ((reg_AC >> 9) \| zs_adr) & 0xFFF` (AC-Bits z₁₂–z₂₃ ODER Adreßteil a = a1a2a3a4; Ergebnis nach BZ) | F |
| 027 | Anw | Umstellung R-Befehl: `reg_OR &= ~(1u<<5)` (z₂₇:=0, B und Z bleiben unverändert; A: 5(101)→1(001) Addition, 7(111)→3(011) bedingte Add./Sub.). AC ist zu diesem Zeitpunkt noch ungelöscht; da L=1 (aus Z=1/5/7) weiterhin gilt, löscht die folgende Phase III AC auf 0, sodass Phase IV Addition bzw. bedingte Add./Sub. mit 0 ausführt (⟨AC⟩:=⟨BZ⟩ bzw. ⟨AC⟩:=−⟨BZ⟩, BZ = kombinierte Adresse aus Knoten 37) | F |
| 028 | Anw | Ausgabe-Halt-Befehl 03Z (B=0/1, A=3): Fallunterscheidung nach a1 (erste Oktalziffer von a): a1≥4 = Anwahlbefehl (`reg_AR & 04000`), a1≤3 = Ausgabebefehl. Kanalzuordnung bei Anwahl zusätzlich über a2 ∈ {7,6,5,4} = K0/K1/K2/K3, bereits vollständig durch die Anwahlverschlüsselung der Kanalauswahltasten definiert (4700/4600/4500/4400 030). Ausführung s. 11.1/11.2 | F |
| 029 | Anw | Nur die AC-Bits z₁₂–z₂₃ werden geändert, alle übrigen Bits des AC bleiben unverändert: `feld = (reg_AC >> 9) & 0xFFF;` (Bits herausschneiden) `hilf = reg_BZ;` (BZ in Hilfsspeicher kopieren, BZ selbst bleibt unverändert) `hilf >>= 1;` (12-Bit-Hilfswert um 1 Bit nach rechts, oberstes Bit wird 0, niedrigstes fällt weg) `feld \|= hilf;` `reg_AC = (reg_AC & ~(0xFFFULL << 9)) \| ((uint64_t)feld << 9);` (Ergebnis zurück in z₁₂–z₂₃) | F |
| 030 | Anw (ZST) | Text an allen fünf Endknoten (30/45/46/58/66) gleichlautend ("unbedingter Stopp-Befehl wird ausgeführt, kein Ausgang, Flag US=1 setzen"), tatsächlicher Halt-Grund aber abhängig vom Knoten/Eingang, über den 030 erreicht wird: 30, 46, 58, 66 (jeweils über die wahr-Seite von Test 020 "Überlauf vorhanden?" erreicht) → `fl_FUE` (ist dort bereits 1; der T2-Wortlaut "Flag US=1 setzen" gilt hier NICHT wörtlich); 45 über Eingang 1 (aus Knoten 42, Test 014 wahr = unbedingter Stopp) → `fl_US := 1`; 45 über Eingang 2 (aus Knoten 43, Test 031 wahr = bedingter Stopp mit gesetztem Schalter BS) → `fl_BS := 1`. Der Generator übergibt der Funktion den Eingang, über den der Endknoten betreten wurde: `anw_030(knoten, eingang)` | F/V |
| 031 | Test (AH) | `fl_BS` (Test, ob Schalter BS gesetzt, an Knoten 43 auf dem bedingter-Stopp-Ast, s. 030). **Korrektur 27.09.2026:** frühere Fassung dieser Zeile nannte `fl_SP` mit dem Zusatz "BS gehört nicht hierher" — das war nach der aktuellen T2-Fassung falsch: 031 fragt gerade BS ab, nicht SP (der bereits in 030 richtig vermerkte Zusammenhang "Test 031 wahr = bedingter Stopp mit gesetztem Schalter BS" war von diesem Fehler nicht betroffen) | F |
| 032 | Anw | Ausführen der Eingabe: `fl_E=1`; Zeichen holen (11.3/11.6); bei Fehler `fl_FE=1`, Halt; sonst `reg_AR \|= eingabeadresse`; `fl_E=0` | V |
| 033 | Anw | Umstellung nach der Eingabe (032), abhängig von Tabelle 1, Spalte "Sprung-Umstellung", für das eingelesene Zeichen: **ja** → `A := 0` (Z und B bleiben) = Unbedingter Sprung (B=0) bzw. Unbedingter Sprung 2. Art (B=1); **nein** → `B := B+2` (0→2 Einzelbefehl, 1→3 markierter Einzelbefehl), A bleibt 1 (Z bleibt) = Festkomma-Addition ("Lesebefehl"), d. h. AC (zuvor durch Z=1 gelöscht) wird um die in 032 gebildete Adresse (Zeichencode ∨ a) addiert. Beispiel Befehlsliste: a01Z → 211 (Lesebefehl) oder 001 (Unbedingter Sprung) | F |
| 034 | Test | `B == 3` | F |
| 035 | Anw | `fl_V1 = fl_V2 = 1`; zusätzlich `zs_vgl_ac = reg_AC`, `zs_vgl_v = (A<=3) ? trommel_lesen(reg_AR) : 0` | F/V |
| 036 | Test | `(B<=1) && A==0` | F |
| 037 | Anw | Vergleicher korrigieren, s. 10.2 | F/V |
| 038 | Test | `B == 2` | F |
| 040 | Test | `(B>=4) && zs_sektorzaehler == 32` | F/V |
| 041 | Test | `(B==6 \|\| B==7) && (zs_start_sektor != 0) && trommel_sektor(reg_AR) == 023`. Sonderfall: War der Startsektor der Gruppe (Sektor von AR beim Betreten von "Beginn Phase IV") 0, wird diese Bedingung nicht ausgewertet (immer falsch); der Befehl verhält sich dann wie ein Gruppenbefehl, d. h. nur 040 (nach 32 Sektoren) beendet ihn (Befehlsliste 4.1.7) | F |
| 042 | Test | `(B==5 \|\| B==7) && ac_negativ()`; Vorzeichen R-abhängig: bei R≠1 (R=0,2,3) ist z₀ das Vorzeichen, bei R=1 (Rechtsverschiebung) ist z₃₂ das Vorzeichen, weil Vr (R=1) z₀ auf 0 zwingt (Befehlsliste 4.1.6, 4.2.1a). Getestet an Knoten 73, also NACH Operation und Resultatbehandlung der soeben bearbeiteten Zelle, s. **Korrektur 28.09.2026** | F |
| 044 | Anw | `zs_x_merker = 1;` (Knoten 78: der Abbruch erfolgte durch die X-Bedingung 042, nicht durch die normale Abbruchbedingung 024, s. **Korrektur 28.09.2026**) | F |
| 043 | Test | `((B<=1) && A==2 && !z30) \|\| ((B<=1) && A==6 && !z30)` (Weiche an Knoten 20 zwischen dem "Stop"-Ast (A=2 oder A=6, jeweils Z<4) und dem übrigen Organisationsbefehl-Pfad; die Unterscheidung A=2 vs. A=6 — unbedingter Stop vs. bedingter Stop — erfolgt erst nachgelagert an Knoten 42/43 über die Tests 014 und 031. **Korrektur beim Vollabgleich vom 26.09.2026:** Diese Zeile fehlte bisher vollständig in der Tabelle, obwohl Knoten 20 sie referenziert) | F |

`zs_sektorzaehler` wird an den Knoten "Beginn Phase IV" (31, 61, 67) auf 0 gesetzt und nach jeder Ausführung
von 021 um 1 erhöht [V].

---

## 10 Befehlsausführung (ANWEISUNG-021 und -022)

**10.1 Trennung [F].** ANWEISUNG-021 führt die Operation auf EINER Zelle (Zellenwähler AR) aus; die
Wiederholung bei Gruppen- und Wiederholungsbefehlen (B=4…7) steckt im Graph (Knoten 32–36). Die
Wirkung jedes Codes steht in der Befehlsliste (Abschnitt 4.3 und Einzelbefehlsübersicht) und ist dort
normativ. Sie wird in `befehle.c` als rund 20 Grundoperationen umgesetzt, ausgewählt über `optab`.

**10.2 Vergleicher (B=3) [F/V].** V1/V2 werden am Ende der Phase III beide gesetzt (035). Der Vergleich
bezieht sich auf den AC nach Phase III und auf v = ⟨a⟩ (A ≤ 3) bzw. v = 0 (A ≥ 4) VOR der Operation.
Deshalb liegen `zs_vgl_ac` und `zs_vgl_v` schon nach 035 fest, obwohl 037 im Graph nach 021 steht.
Wirkung von 037 (vorzeichenbehaftet über 33 Bit): AC < v → V1=1, V2=0; AC > v → V1=0, V2=1;
AC = v → beide bleiben 1. Bei markierten Einzelbefehlen mit Löschanweisung ist der AC zum Vergleichszeitpunkt 0.

**10.3 Tabelle `optab` [V].** Der Generator liest die "Einzelbefehlsübersicht" der Befehlsliste (Spalten
Nr., Code(s), Beschreibung; Codes dreistellig oktal B-A-Z) und erzeugt `optab[512]` mit Gruppen-Nummer und
Beschreibung. Prüfungen: kein Code doppelt; nicht belegte Codes bleiben als "nicht definiert" markiert.
Ausführung eines nicht definierten Codes: Stub-Regel (2.5). Da T2 (ANWEISUNG-021) die Befehlsliste als
alleinige Quelle der Einzelformeln erklärt und Änderungen dort "automatisch hier" wirken sollen, wird `optab`
bei jeder Erzeugung neu aus der Befehlsliste gebildet. Der Generator prüft dabei, dass jeder Gruppe eine
implementierte Grundoperation in `befehle.c` zugeordnet ist, und meldet neue oder geänderte Gruppen (Zeilen-Hash
der Übersicht), damit keine Änderung unbemerkt ohne Umsetzung bleibt.

**10.4 Grundoperationen (Auswahl, normativ in der Befehlsliste) [F].**

- Konjunktion im AC, Addition, Subtraktion, bedingte Addition/Subtraktion (auch Variante Z=2,3),
  Transport (`trommel_schreiben`, Rückgabe GESPERRT wird ignoriert), Konjunktion im Speicher (auch mit
  negiertem AC), Vorzeichenbefehl (bedingte Speicherlöschung), R-Operation (nach 027 in Addition bzw.
  bedingte Add./Sub. umgestellt).
- Sprungbefehle wirken über den Graph (BZ/AR-Belegung, Rückkehradresse per 029), nicht in 021.
- Leer-Befehl (B=1, A=6, Z≥4): keine Operation, die befohlene AC-Löschung wird ausgeführt.

**10.5 Resultatbehandlung (022) [F].** Nach 021, bezogen auf den AC (Befehlsliste 4.2.1):

- R=0: unverändert.
- R=1: Rechtsverschiebung um 1 Bit, z₀ wird 0 (`AC >>= 1`).
- R=2: Linksverschiebung um 1 Bit, z₃₂ wird 0 (`AC = (AC<<1) & MASK33`).
- R=3: zyklische Linksverschiebung (`AC = ((AC<<1) & MASK33) | z₀_alt`).

Das Löschbit L wirkt in Phase III (Knoten 17/18), nicht hier.

**10.6 Überlauf [F].** `fl_FUE` hält den Überlauf der zuletzt ausgeführten überlaufbestimmenden Operation. Wird ein Überlauf erkannt, wird `fl_FUE := 1` gesetzt. Jede weitere überlaufbestimmende Operation bestimmt den Überlauf neu: `fl_FUE := 0`, wenn kein Überlauf auftritt, sonst wieder 1. Andere Operationen lassen `fl_FUE` unverändert; die Taste G löscht es.

Überlaufbestimmend sind Addition, Subtraktion, bedingte Addition/Subtraktion und R-Befehl, und zwar nur als Einzelbefehl (B=2) oder markierter Einzelbefehl (B=3) ohne Resultatbehandlung (R=0) (Originaltext: "Der Überlauf wird nur bei ... ausgewertet"). Gruppen- und Wiederholungsbefehle (B=4–7) bestimmen keinen Überlauf. R≠0 bedeutet Verschiebung; eine Verschiebung erzeugt keinen Überlauf und bestimmt ihn auch nicht neu, `fl_FUE` bleibt dann unverändert. Bei Addition und Subtraktion wird der Überlauf nach 5.6 aus den Vorzeichenbits bestimmt.
Ausgewertet wird `fl_FUE` durch ANWEISUNG-020 (Knoten 28, 44, 55, 65), durch den Überlauf-Sprung (A=7) und
(**Korrektur 27.09.2026**, s. 9.4) durch ANWEISUNG-009 (Knoten 13, Fall B=0/A=7).

---

## 11 Peripherie

**11.1 Kanalanwahl (028, Anwahlbefehl) [F/V].** Ein Anwahlbefehl ist ein Ausgabe-Halt-Befehl 03Z mit a1≥4 (erste Oktalziffer von a). Bei den vier Kanaltasten-Codes 4700 = K0, 4600 = K1, 4500 = K2, 4400 = K3 (Bedienpult, Kanaltabelle; a2 = 7,6,5,4, a3=a4=0) wird das gewählte Kanalflag 1, die Flags der anderen drei Kanäle 0; K0 setzt zusätzlich T bzw. SW je nach Schalter SW. Die Adresse ist dabei nur eine Kode-Zahl zur Kennzeichnung des Kanals, keine reale Speicheradresse: Der Inhalt der Zelle 4700/4600/4500/4400 wird durch die Ausführung weder verändert noch mit AC verknüpft (Befehlsliste, Kanaltabelle). Kanal K3 ist am C 8205 "frei" (kein Gerät zugeordnet); die Anwahl selbst ist trotzdem gültig, nur bleibt sie ohne I/O-Wirkung. Für die Fallunterscheidung Anwahl/Ausgabe zählt nach Originaltext ausschließlich z₁₂ (a1); die Triaden a3 und a4 werden dabei nicht ausgewertet. Bei a1<4 (Ausgabebefehl) ist a2 ohne besondere Bedeutung, es ist reguläre Zeichenausgabe (11.2). Bei a1≥4 (Anwahlbefehl) ist nur a2 ∈ {4,5,6,7} definiert (Kanalwahl K0–K3); a2 < 4 ist nicht definiert und für spätere Erweiterungen vorgesehen (Autorangabe) — Behandlung wie ein nicht definierter Code (Stub-Regel 2.5).

**11.2 Ausgabebefehl (028, `a & 04000 == 0`) [F/V].**

- Ausgabeadresse a (oktal) → Lochbild `(a >> 3) & 0xFF` (die ersten drei Oktalstellen; die vierte "x" wird
  ignoriert). Ausgebbar sind nur Zeichen, deren Ausgabe-Adresse in Tabelle 1 vorkommt; sonst keine Ausgabe,
  Hinweiszeile im Protokoll.
- `fl_A = 1` während der Ausgabe, danach 0.
- Ziel je Kanal: K1 → Stanzer (11.4), K2 → SW-Ausgabe (11.5, unabhängig vom Schalter SW: K2 gibt immer auf die Schreibmaschine aus). K0 gibt es nur für Eingabe (11.6); der Schalter SW ist nur bei K0 überhaupt relevant (T/SW-Unterscheidung der Eingabe) und hat für die Ausgabe keine Bedeutung. K3 → keine Ausgabe.

**11.3 Leser 1 und 2 (K1, K2) [F].**

- Je Leser ein eigenes Unterverzeichnis mit Textdateien = nacheinander eingelegte Lochstreifen. Verzeichnis
  je Leser über `--leser1 DIR`, `--leser2 DIR`; Dateien in Namensreihenfolge.
- Dateiformat: eine Zeile je Lochungszeile, acht Zeichen `0`/`1` für w v u p 8 4 2 1 (Tr nicht
  dargestellt); Leerzeilen sind Transportlochungen (Vorspann) und werden überlesen.
- Pro Eingabebefehl genau eine Zeile. Ist die Datei zu Ende, wird die nächste Datei des Verzeichnisses
  geöffnet; eine nicht verbrauchte Datei bleibt geladen und wird beim nächsten Befehl fortgesetzt.
- Gerade Anzahl gelochter Spuren (auch "Irrung Zeichen") = Gerätefehler: `fl_FE = 1`, Halt.
- Eingabeadresse = `(lb & 0x0F) | ((lb >> 1) & 0x30)` (Spuren 1,2,4,8,u,v; p und w unberücksichtigt) und muss
  mit der Spalte "Eingabe Adresse" der Tabelle 1 übereinstimmen (Konsistenzprüfung im Generator).
- Kein Streifen mehr (oder eine Leseanforderung, bevor überhaupt ein Streifen eingelegt wurde): Der
  virtuelle Leser wartet unendlich, `fl_E` bleibt gesetzt (kein Fehler) — entspricht exakt dem realen
  Rechnerverhalten (Lochstreifenleser A5), keine eigene Festlegung des C-Programms. Diese Wartesituation
  wird bei jeder neuen Leseanforderung, der kein Streifen zur Verfügung steht, mit einem Protokolleintrag
  (Debug-Ausschrift) quittiert — unabhängig von der folgenden Einstellung. Der zusätzliche Programmschalter
  `--leser-ende halt|warten` ist eine reine Test-/Debug-Hilfe für Interpreter und C-Programm, keine
  Hardwareeigenschaft: `halt` beendet den Lauf zusätzlich mit Halt-Grund `EINGABE_ENDE` (für automatische
  Tests); Standard ist `warten` (entspricht dem realen, unendlichen Warten des Rechners). (O-5, geklärt)
- Am Ende der Interpretation werden alle angebrochenen Streifen beider Leser beendet, ohne Wiederverwendung
  über Läufe hinaus.

**11.4 Stanzer (K1) [F].** Ausgabe nach `stanzer-ausgabe.txt`: eine Zeile je Zeichen, acht Zeichen `0`/`1`
für w v u p 8 4 2 1 (Tr nicht dargestellt). Die Datei wird nur angelegt, wenn tatsächlich gestanzt wird,
und dann fortgeführt (anhängen). Keine Wartebedingung.

**11.5 SW-Ausgabe [F].** Ausgabe nach `sw-ausgabe.txt`, nur angelegt bei tatsächlicher Ausgabe,
anhängend, zeichenweise. Die Ausgabe erfolgt unabhängig von der Stellung des Schalters/Flags SW
(11.2) — keine Wartebedingung. Zeichenabbildung: Zeile der Tabelle 1 über die Ausgabe-Adresse; Text =
Spalte "Ascii" der aktuellen SW-Ausgabe-Zeichenlage `zs_sw_zeichenlage` (KB/GB, s. u., NICHT die
eingabeseitige `zs_zeichenlage` aus 11.7); Zeilen mit Ascii 0 (Um. KB, Um. GB u. a.) werden als
`<Name>` geschrieben. Das Zeichen WRZL (Tabelle-1-Zeile 38, Ausgabe-Adresse 272x) beendet die Zeile
(Zeilenvorschub); mehrere WRZL hintereinander ergeben Leerzeilen.

**11.5a SW-Ausgabe-Zeichenlage `zs_sw_zeichenlage` [F].** Eigener, von `zs_zeichenlage` (Eingabe, 11.7)
unabhängiger Zustand des Schreibwerks als Ausgabegerät: KB und GB sind alternativ. Beim
Netz-Einschalten (analog zum zufällig gezogenen Trommel-Startsektor, 4.4) wird `zs_sw_zeichenlage`
zufällig auf KB oder GB gesetzt (Ausgangszustand, 12.1/14.2). Er wird ausschließlich durch die
**Ausgabe** eines Zeichens mit passender Ausgabe-Adresse geändert: 117x → KB, 057x → GB (x = beliebige
Oktalziffer, don't-care). Eingaben (auch von Um. KB/Um. GB) haben auf `zs_sw_zeichenlage` keine
Wirkung.

**11.6 K0-Eingabe (Tastatur/Schreibwerk) [F].** Bewusst anders als beim Leser (11.3, O-5 geklärt):
Bei `--k0 tastatur` sieht der Bediener am Eingabekursor unmittelbar, dass eine Eingabe erwartet wird,
ein Debug-Hinweis wäre überflüssig. Bei `--k0 datei=PFAD` bedeutet Dateiende, dass der Testablauf selbst
zu Ende ist — Warten wäre dort sinnlos, daher sofortiger Halt mit `EINGABE_ENDE` statt "warten". Voraussetzung: Kanal K0 angewählt und `fl_T` oder
`fl_SW` gesetzt (Durchführung eines Tests, 6.1). Pro Eingabebefehl wird genau ein Zeichen geholt.

- `--k0 tastatur`: Terminal im Rohmodus (`termios`, `ICANON` und `ECHO` aus, `ISIG` an), damit jeder Tastendruck
  ein Zeichen liefert und Strg+C weiter wirkt. Das Lesen ist blockierend und wird durch SIGINT (ohne
  `SA_RESTART`) mit `EINTR` unterbrochen; danach `abbruch_angefordert` prüfen. Das Terminal wird bei jedem
  Ausstieg (auch Abbruch) zurückgesetzt. Ist stdin kein Terminal, wird byteweise gelesen.
- `--k0 datei=PFAD`: Textdatei, ein Zeichen je Zeile (das Zeichen selbst oder ein Name wie `ZR`, `WM`,
  `IS`, `IB`, `TAB`, `WRZL`); Zeilen mit `#` sind Kommentar. Dateiende: Halt mit `EINGABE_ENDE`.
- Umsetzung Zeichen → Eingabeadresse über Tabelle 1: Host-Zeichen wird über die Spalten "Ascii KB"/"Ascii GB"
  gefunden; die Spalte "Eingabe Adresse" liefert die Verschlüsselung, die wie bei den Tasten disjunktiv mit
  dem Adreßregister verknüpft wird. ZR = Leerzeichen (Tabelle 1, Zeile 49); TAB = Tabulator (Zeile 12);
  WM = TAB "Tabulator" (Wortmarke identisch mit Tabulator, s. Kodetabellen 3.3 — ersetzt die frühere
  Zuordnung zu "."; Tabelle 1, Zeile 12, Eingabe Adresse 75); IS = "Irrung Satz" (Tabelle 1, Zeile 51, Eingabe Adresse 16); WRZL = SatzMarke (Zeile 38, Eingabe
  Adresse 32); **IB** = "Irrung Block", Eingabe-Adresse **036** (oktal; nachgereichter Original-Tabellenauszug,
  Kodetabellen 3.3), Sprung-Umstellung = ja (O-6, geklärt).
- Der Automat wartet nur auf Zeichen; `fl_E` bleibt währenddessen 1.

**11.7 Zeichenlage (Eingabe) [F].** Zustand `zs_zeichenlage`, Start KB, rechnerweit für alle Leser. Ein
gelesenes Um. KB/Um. GB (Tabelle 1, Zeilen 25/26) ändert ihn. Auf die Eingabeadresse hat
`zs_zeichenlage` KEINE Wirkung: Um. KB und Um. GB sind für die Eingabe "normale Zeichen" und werden wie
jedes andere Zeichen regulär über ihre feste Spalte "Eingabe Adresse" verschlüsselt und disjunktiv mit
AR verknüpft (11.6). `zs_zeichenlage` hat auf die SW-Ausgabe KEINE Wirkung — dafür gilt die eigene,
unabhängige `zs_sw_zeichenlage` (11.5a). Bei der Ausgabe gibt der Rechner Umschaltzeichen nur aus, wenn
das Programm es vorsieht (keine Automatik).

**11.8 Tabelle 1 → `kodetab` [F/V].** Der Generator liest Abschnitt 1.4 der Kodetabellen (Spalten: Nr.,
Klbuch, BCD, Gbuch, BCD, Lochbild, Eingabe Adresse, Sprung-Umstellung, Ausgabe-Adresse, Ascii GB, Ascii KB)
und erzeugt ein C-Array (52 Zeilen). Konsistenzprüfungen im Generator: ungerade Parität in 51 von 52 Zeilen
(Ausnahme "Irrung Zeichen"); Eingabeadresse gleich der Formel aus 11.3; Eindeutigkeit von Eingabe- und
Ausgabe-Adresse; Lochbild gleich den ersten drei Oktalstellen der Ausgabe-Adresse. Zeile 50 (Irrung Zeichen)
hat keine Eingabeadresse, Zeile 52 (Transport) ist ein Relikt und wird nicht benutzt. 5-Kanal-Streifen
(Fernschreibkode) werden nicht unterstützt (gestrichen).

---

## 12 Bedienpult und Testdefinition

**12.1 Trommeldatei des Tests [F].** Zeilenformat `Adresse: Wert [# Bemerkung]`, Adresse 4 Oktalstellen,
Wert 11 Oktalstellen, Leerzeilen erlaubt, Kommentarzeilen mit `#`. Die Datei ist nur ein Ausschnitt der
Trommel. Der Testlader erzeugt daraus die 4096-Zeilen-Datei des Moduls `trommel`. Nicht genannte Zellen
sind für den Testzweck ohne Bedeutung; der Testlader belegt sie beim Aufbau der vollständigen
4096-Zeilen-Datei mit `00000000000` (O-2, geklärt). Kommt dieselbe Adresse mehrfach mit demselben Wert
vor, ist das unschädlich; kommt sie mehrfach mit unterschiedlichem Wert vor, ist die Trommeldatei
widersprüchlich und der Test ungültig (Durchführung eines Tests, 5.; s. 12.6).

**12.2 Testmarken `#DOK`/`#SPEI`/`#SPUR` [F].** `#DOK-xxxx <Text>` (xxxx oktal; dieselbe Nummer darf mehrfach vorkommen, alle zugehörigen Texte werden in Dateireihenfolge ausgegeben) und je DOK
höchstens einmal `#SPEI-xxxx ssss-eeee` (Speicherbereich). Beide sind Testhilfen ohne Entsprechung in
der Hardware. Gefordert ist eine gültige Spanne `ssss<=eeee`; das ist eine reine formale Prüfung der
Testvoraussetzungen vor Start (12.6), keine inhaltliche Bedeutung (O-4, geklärt).

**12.2b Testmarke `#SPUR-xxxx aaaa` [F, Ergänzung 29.09.2026].** Wie `#SPEI-xxxx`, aber ohne Bezug auf
eine Adressspanne: Ausgegeben werden alle 32 Zellen der Spur (Bahn), in der die Oktaladresse `aaaa`
liegt (`spur = aaaa & ~0x1F`), und zwar in der physischen Zugriffsreihenfolge der Trommel
(`PHYS_LOG`-Tabelle, s. Magnettrommel-Datei, Abschnitt Speichernumerierung/Interleiving; Adresse je
physischer Position p: `spur | PHYS_LOG[p]`). Darf wie `#SPEI-xxxx` mehrfach mit derselben Nummer
vorkommen; die Ausgaben erscheinen nach allen `#SPEI-xxxx`-Ausgaben derselben Nummer, in Dateireihenfolge.

**12.2a Protokollierungsstufe `#PROT STUFE=n` [F].** Test-weite Testmarke (nicht an eine Adresse
gebunden, anders als `#DOK`/`#SPEI`), `n ∈ {0,1,2}`, höchstens einmal je Trommeldatei zulässig. Fehlt
sie, gilt `STUFE=1` als Standardwert (Durchführung eines Tests, 2.). Sie steuert ausschließlich, ob und
wohin der Durchlauf durch den Knotenautomaten protokolliert wird (Abschnitt 13); auf die
Diagnoseausgabe bei Befehl 164 (13.1) hat sie nur teilweise Einfluss (dort zusätzlich zur stets
erfolgenden Bildschirmausgabe). Wie `#DOK`/`#SPEI` eine reine Testhilfe des Interpreters/C-Programms
ohne Entsprechung in der physischen Elektronik des C 8205.

**12.3 Tastenfolge-Datei [V].** Eine Zeile oder Leerzeichen-getrennte Token; `#` beginnt einen Kommentar.

| Token | Bedeutung und Wirkung (Bedienpult, Durchführung eines Tests) |
|---|---|
| `H` / `R` | Schalter H-R: `fl_H := 1` bzw. `fl_H := 0`; beim Schalten von H auf R zusätzlich `fl_US := 0` |
| `G` | nur bei H: alle Flags außer H, T, BS und SP := 0 (BS, SP sind eingerastete Schalter, G löst sie nicht); `AR := 0`, `OR := 0` (BR = 0000 000); K0 anwählen (T := 1, bzw. SW := 1 wenn Schalter SW gedrückt); BZ und AC unverändert. danach `fl_US := 1` (wird durch ST oder H→R wieder gelöscht) |
| `M+` / `M-` | M gedrückt halten / loslassen: `OR := OR ∨ 025` (Sprung mit Rückkehrabsicht), solange gehalten; bei `M-` entfällt der Beitrag von 025 (übrige OR-Anteile bleiben), wenn unter M mindestens ein `E` betätigt wurde. M hat nur die Stellungen gedrückt/losgelassen und muss in der Tastenfolge losgelassen werden (12.6) |
| `M` | Antippen, gleichbedeutend mit `M+` und sofort `M-` (Fall 4): `OR := OR ∨ 025`; kein E unter M, daher bleibt BR = ⟨AR⟩ 025 aufgestellt (Start bei Knoten 19, 12.5) |
| `E` | Einzelschritt (Tipp), nur bei `fl_H = 1` wirksam: Phase IV und Phase I, dann Phase II und III, dann Halt (HP3, Knoten 19); ohne M vollständig über den Knotengraphen. Unter gehaltenem M entfällt die Befehlsentnahme (Phase II); Wirkung: `BZ := BZ+1`, `AR := BZ`, `AC := (BZ+1)` im Adressfeld (Beispiel B nach 4×E: `AC = 00000005000`), anschließend steht der Automat vor Phase II — geklärt (O-1): sinnvoll, da bei gehaltenem M jedes E nur die Adresse weitererhöht, ein Zwischenstopp vor dem Loslassen wäre wirkungslos |
| `Ü` | nur bei `fl_H = 1` wirksam (sonst keine Wirkung): `AR := 7777`, `OR := OR ∨ 240` (Transport); BR ist damit aufgestellt und noch nicht ausgeführt (Start bei Knoten 19, s. 12.5) |
| `ST` | nicht an H gebunden, aber elektronisch verriegelt: nur bei `fl_US = 1` oder `fl_BS = 1` wirksam (sonst keine Wirkung): `OR := OR ∨ 240`, AR unverändert; dabei `fl_US := 0`; BR ist damit aufgestellt und noch nicht ausgeführt (Start bei Knoten 19, 12.5). `fl_US` steht in einer Tastenfolge nach `G` (12.3) |
| `SW=1` / `SW=0` | Schalter SW gedrückt (Flag SW, T := 0) bzw. gelöst (T := 1, SW := 0) |
| `SP=1/0`, `BS=1/0` | Selektorschalter, einrastend: `=1` (gedrückt) setzt das gleichnamige Flag auf 1, `=0` (gelöst) auf 0; sonst keine Wirkung. `G` ändert diese Flags nicht; nicht an H gebunden |
| `K0` … `K3` | Kanaltasten: gewähltes Flag := 1, andere := 0 (K0: T oder SW je Schalter SW) |

Eine Tastenfolge wird bis zur Wirkung der dadurch aufgestellten Instruktion vorausinterpretiert. Sie muss den
Ausgangszustand vor Eintritt in den Automaten vollständig definieren, sonst startet der Test nicht (12.6).
Die Eingabetasten (0…9, +, − usw.) sind nicht Teil der Tastenfolge, sie werden als K0-Eingabe (11.6) bedient.

**12.4 Schalterdatei [V].** Optionale Kopfzeile in der Tastenfolge oder eigene Datei: `BAHNSPERRE: e 40 100 200
400 1000` mit Werten 0/1 (Reihenfolge wie `bahnsperre_setzen()`), sowie Anfangsstellungen von SW, SP, BS.
Nicht genannte Schalter stehen auf 0.

**12.5 Startpunkte und Halt [F].** (O-1, geklärt: der Fall "BR aufgestellt und noch nicht ausgeführt"
entspricht genau der Situation, in der H den Automaten an HP3/Knoten 19 angehalten hat, s. 8.7 — R setzt
die Schleife dort einfach fort.)

- Nach `R`: Ist keine Instruktion in BR aufgestellt (Beispiele A und B: Ansprung 0000 bzw. n über G/M/E),
  startet der Automat bei Konnektor B (Knoten 1) mit dem in BZ stehenden Wert.
- Ist BR aufgestellt und noch nicht ausgeführt (Ü, ST, M ohne E unter M, sowie nach E ohne M: "Fälle 2 bis 5" der Tastenfolgen),
  startet der Automat bei Knoten 19 (BR ausführen, Phase-III-Arbeit gilt als erledigt).
- Endet die Tastenfolge ohne `R`, bleibt der Rechner im Halt: ohne `E` keine Ausführung, mit `E`
  Einzelschritt bis HP3 (8.7). Das Ergebnis eines solchen Tests ist der Zustand nach dem letzten Schritt
  (Fall 5: `H G Ü E`).
- Nach `E` ohne M steht der Automat an HP3 (BR aufgestellt); folgt danach `R`, startet er bei Knoten 19.
- Halt-Ursachen: Endknoten, US/BS (laut Stopp-Befehl), `fl_FE`, Abbruch, Stub.

**12.6 Gültigkeitsprüfung vor dem Start [F].** Der Test startet nur, wenn alles gilt: Zeilenformat der
Trommeldatei; keine Adresse mehrfach mit widersprüchlichem Wert belegt (12.1); 
`#SPEI-xxxx` nur zu vorhandenem DOK und mit gültiger Spanne; `#SPUR-xxxx` nur zu vorhandenem DOK;
`#PROT STUFE=n` höchstens einmal vorhanden
und `n ∈ {0,1,2}` (12.2a); Tastenfolge ergibt einen vollständig definierten Ausgangszustand. Ungültig sind
insbesondere: `M-` ohne vorheriges `M+`, zweites `M+` bei gedrücktem M,
`R` oder Tastenfolgenende bei noch gedrücktem M, unbekannte Token, Ende weder mit `R` noch im Halt (H gesetzt).
`Ü` und `E` bei `fl_H = 0` sind gültig, aber ohne Wirkung. Sonst
Meldung auf `stderr` und Exit-Code 1; da bei einem Startfehler der Automat gar nicht erst anläuft,
entsteht unabhängig von `#PROT STUFE=n` keine Protokolldatei (13.3) — die Fehlermeldung geht
ausschließlich auf `stderr`. (Die Quelle beschreibt für die interpretative/manuelle Testdurchführung an
dieser Stelle ein Zurückstellen bis zur Klärung mit dem Auftraggeber statt eines Programmabbruchs,
Durchführung eines Tests, 5.; das automatisierte C-Programm bildet denselben Grundsatz "keine
eigenmächtige Korrektur einer ungültigen Testdefinition" durch sofortigen, unkorrigierten Abbruch ab.)

---

## 13 Protokoll

**13.0 Grundprinzip [F].** Die Testmarke `#PROT STUFE=n` (12.2a) unterscheidet drei Protokollierungsstufen
für den Durchlauf durch den Knotenautomaten. Sie betrifft ausschließlich die Frage, OB und WOHIN
(Bildschirm oder Datei) die durchlaufenen Knoten protokolliert werden; sie betrifft NICHT die
Diagnoseausgabe bei Befehl 164 (13.1), die stufenunabhängig immer auf dem Bildschirm erscheint:

| STUFE | Knotenzustände auf dem Bildschirm (13.2) | Protokolldatei `protokoll.txt` (13.3) |
|---|---|---|
| 0 | nein | wird nicht angelegt |
| 1 (Standard) | ja | wird nicht angelegt |
| 2 | nein | wird angelegt, enthält die Knotenzustände |

**13.1 Diagnoseausgabe bei Befehl 164 [F].** Wird der Befehl 164 (oktal, Leerbefehl) mit einer Adresse a
ausgeführt, für die `#DOK-xxxx` mit xxxx = a existiert, dann wird NACH der regulären Abarbeitung
(Hook nach ANWEISUNG-022) unabhängig von `#PROT STUFE=n` STETS auf dem Bildschirm ausgegeben: die Marke
mit Text, `reg_BZ`, `reg_AC`, die Flags FE, FÜ, BS, US, E, A. Ist `#SPEI-xxxx ssss-eeee` definiert,
zusätzlich alle Zellen ssss…eeee als `Adresse: Wert` (oktal); ist zusätzlich `#SPUR-xxxx aaaa` definiert,
danach alle 32 Zellen von dessen Spur in physischer Zugriffsreihenfolge, ebenfalls als `Adresse: Wert`
(s. 12.2b). Bei `STUFE=2` wird dieselbe Ausgabe
zusätzlich in die Protokolldatei (13.3) geschrieben; bei `STUFE=0` und `STUFE=1` bleibt es bei der
Bildschirmausgabe, es entsteht keine zusätzliche Datei-Ausgabe. Danach läuft der Automat regulär weiter.

**Korrektur gegenüber der Fassung vom 24.09.2026:** Dort hieß es, die Diagnose gelte "nur für die
Datei, nicht für den Bildschirm" — das war schlicht falsch herum und ist mit der Definition der
Protokollierungsstufe in "C8205-Interpreter-Durchführung_eines_Tests.md" (Abschnitt 7.2: die Diagnose erscheint "unabhängig
von der ... Protokollierungsstufe stets zusätzlich auf dem Bildschirm") klargestellt: Die
Bildschirmausgabe ist der Regelfall, die Datei-Ausgabe bei `STUFE=2` die Ergänzung, nicht umgekehrt.

**13.2 Bildschirmausgabe der Knotenzustände (nur `STUFE=1`) [F].** Bei `STUFE=1` (Standard, falls
`#PROT` fehlt) werden die durchlaufenen Knoten zusätzlich zu 13.1 auf dem Bildschirm ausgegeben, knapp,
eine Zeile je Knoten (Zeilenformat s. 13.4). Bei `STUFE=0` und `STUFE=2` entfällt diese
Bildschirmausgabe vollständig (bei `STUFE=2`, weil dieselbe Information stattdessen in die
Protokolldatei geschrieben wird, s. 13.3; bei `STUFE=0`, weil sie ganz entfällt).

**13.3 Protokolldatei `protokoll.txt` (nur `STUFE=2`) [F].** Nur bei `STUFE=2` wird je Test genau eine
Datei angelegt; bei `STUFE=0` und `STUFE=1` entsteht keine Protokolldatei. Inhalt in zeitlicher
Reihenfolge: (1) Ausgangsbedingungen: übernommene Trommeldatei und Tastenfolge mit Wirkung auf
Register/Flags; (2) die durchlaufenen Knoten in Reihenfolge (an Stelle der Bildschirmausgabe aus 13.2);
(3) die Diagnoseausgaben nach 13.1, soweit während des Laufs ausgelöst. Das Protokoll wird, sofern
angelegt, am Testende bereitgestellt (Ausgabeverzeichnis, 14).

**13.4 Zeilenformat der Knotenzeile [V].** Beispiel: `K011 ANW 007 BZ=0000 AR=0000 AC=00000000000`.
Format: Knoten, Typ, Text bzw. ANWEISUNG-Nr., gefolgt von einer festen Auswahl der Register (oktal).
Gilt unverändert für beide Ziele, je nach Stufe: Bildschirm bei `STUFE=1` (13.2), Protokolldatei bei
`STUFE=2` (13.3).

---

## 14 Programmaufruf und Ausgaben

**14.1 Aufruf [V].**

```
c8205 --trommel TEST.txt --tasten TASTEN.txt [--zeit interpretativ|echt]
      [--k0 tastatur|datei=PFAD] [--leser1 DIR] [--leser2 DIR] [--leser-ende warten|halt]
      [--ausgabe DIR]
```

Die Trommeldatei des Moduls entsteht im Ausgabeverzeichnis (Standard `./out`), ebenso `protokoll.txt`
(nur bei `#PROT STUFE=2`, s. 13.3), `sw-ausgabe.txt` (falls Ausgabe) und `stanzer-ausgabe.txt` (falls
gestanzt). Bei `#PROT STUFE=0` oder `STUFE=1` entsteht keine `protokoll.txt`.

**14.2 Ablauf [V].** (1) `unterbrechung_einrichten()`; (2) Testdefinition lesen und prüfen (12.6);
(3) `trommel_einschalten()`; Bahnsperre und Schalter setzen; `zs_sw_zeichenlage` zufällig auf KB/GB
setzen (11.5a); Ausgangszustand aus der Tastenfolge bilden; (4)
`automat_lauf(startknoten)`; (5) Aufräumen und Bereitstellen der Ausgaben.

**14.3 Exit-Codes [V].** 0 normaler Halt; 1 ungültige Testdefinition/Fehler; 2 Halt durch Stub
(`NICHT_DEFINIERT`); 130 Abbruch durch Strg+C.

---

## 15 Offene Punkte (Klärungsbedarf, blockieren nur den jeweils betroffenen Teil)

Alle ursprünglich fünf offenen Punkte (O-1 bis O-5) sind geklärt (Stand 25.09.2026). Zur Erinnerung, mit
Verweis auf die jetzt maßgeblichen Stellen:

- **O-1 Haltepunkte und Startpunkte** (8.7, 12.5, 12.3/Taste E) — geklärt.
- **O-2 Vorbelegung nicht genannter Trommelzellen** (12.1) — geklärt.
- **O-3 Flagtabelle H/SP** (6.2, Datei "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md") — geklärt.
- **O-4 SPEI-Spanne** (12.2) — geklärt.
- **O-5 Leser-Ende und K0-Datei-Ende** (11.3, 11.6) — geklärt.

Bei der Klärung wurden außerdem mehrere inkonsistente inline-Tags korrigiert, die auf ältere
Nummerierungen dieses Abschnitts zurückgingen (u. a. fälschlich O-3 statt O-1 bei 8.7/12.5/12.3, O-4 statt
O-2 bei 12.1, ein verwaister Verweis O-1 bei der Anwahlbefehl-Fallunterscheidung in der Befehlsliste, sowie
ein in Abschnitt 15 nie geführtes O-6 bei 12.2).

**Nachtrag Stand 26.09.2026 (Vormittag):** Kein neuer offener Punkt, aber eine Korrektur bereits als
[F] geführter Aussagen: Das Regelwerk ("C8205-Interpreter-Durchführung_eines_Tests.md") hat inzwischen die Testmarke
`#PROT STUFE=n` definiert (12.2a) und damit klargestellt, dass die Diagnoseausgabe bei Befehl 164
stets auf dem Bildschirm erscheint und nur bei `STUFE=2` zusätzlich in die Protokolldatei geschrieben
wird — genau umgekehrt zur bisherigen Formulierung in Abschnitt 13. Siehe die dortige
Korrektur-Anmerkung (13.1).

**Nachtrag Stand 26.09.2026 (ergänzter Vollabgleich):** Ein neuer offener Punkt, bislang nur
unnumeriert in 11.6 erwähnt. Die Bezeichnung "O-6" ist frei (der einzige frühere Gebrauch war der oben
in der vorigen Erinnerung genannte verwaiste, nie tatsächlich in diesem Abschnitt geführte Verweis bei
12.2 und bezeichnete nichts Eigenständiges) und wird hier bewusst für einen neuen, tatsächlich noch
offenen Punkt vergeben — nicht zu verwechseln mit jenem Alt-Verweis:

- **O-6 Eingabeadresse des Zeichens "IB" (Irrung Block)** — geklärt (Nachtrag 27.09.2026): Eingabe-Adresse
  036 (oktal), Sprung-Umstellung = ja, laut vom Autor nachgereichtem Original-Tabellenauszug (Kodetabellen
  3.3). Die Eingabeadresse für IB wird jetzt wie bei den anderen Sonderzeichen regulär eingesetzt (11.6)
  statt eines Stubs.

**Nachtrag Stand 26.09.2026 (Module fixiert, Korrektur trommel.c):** Die drei Module `trommel`,
`bahnsperre` und `unterbrechung` liegen als vom Autor gelieferte, fixierte Dateien vor (4.0/4.4) und
werden nicht mehr vom Generator behandelt. Dabei kam ein Punkt zur Sprache und wurde noch am selben Tag
geklärt:

- **O-7 Sektor-Startlage von `trommel.c` nach dem ersten Tick** — geklärt. Der frühere „Korrekturbedarf"
  (Hintergrundthread startete `index` bei 0 statt synchron zum in `trommel_einschalten()` zufällig
  gezogenen Startwert) wurde in einer ersten Fassung der fixierten Datei zunächst als nicht mehr zu
  behebende, akzeptierte Eigenschaft geführt. Das war nicht akzeptabel: Der Autor hat `trommel.c`
  daraufhin korrigiert (s. 4.1) — der Hintergrundthread übernimmt den Startindex jetzt über die
  modulweite Variable `drum_start_index` von `trommel_einschalten()`, sodass die Sektorfolge ab dem
  ersten Tick lückenlos am zufällig gezogenen Startsektor fortsetzt. Die in 4.4 hinterlegte Prüfsumme
  von `trommel.c` wurde entsprechend aktualisiert.

**Nachtrag Stand 27.09.2026 (Regelwerk-Änderung an T2, Knoten 12/13/43):** Die Datei "C8205-Interpreter-Beschreibung_der_Knoten.md" (T2) wurde seit dem letzten Vollabgleich geändert. Betroffen sind die Definitionen von
ANWEISUNG-008, -009 und -031 sowie eine Detailangabe bei ANWEISUNG-017; alle vier Zeilen in 9.4 (und die
Zähl-/Verweisstellen in 6.2, 9.1, 9.2, 10.6) wurden entsprechend korrigiert:

- ANWEISUNG-008 testet jetzt `(B<=1) && (A==4 || A==5 || A==7)` statt (vormals) `A==6 && z30`.
- ANWEISUNG-009 ist jetzt `ARW` (nicht `AH`) und testet AC-Vorzeichen/Vergleicher/Überlauf je nach
  B/A-Kombination, statt (vormals) den Schalter `fl_SP` abzufragen.
- ANWEISUNG-031 fragt `fl_BS` ab, nicht `fl_SP` (die vorige Fassung dieses Dokuments hatte hier
  fälschlich SP genannt, obwohl der zugehörige Endknoten-Eintrag 030 bereits korrekt von BS ausging).
- ANWEISUNG-017 löst laut T2 drei Triaden a1,a2,a3 heraus (nicht zwei).

**O-8 Tragfähigkeit der A=6-Kontextkommentare bei ANWEISUNG-010/013/018/043** — offen. Die T2-Kommentare zu
ANWEISUNG-013 ("Sprung mit Rückkehrabsicht ... nach Umstellung durch ANWEISUNG-010 aus A=6") und zu
ANWEISUNG-018 ("A=6+z₃₀=1 ... Knoten 12–14") beschreiben Knoten 12–14 weiterhin so, als prüften diese den
Sonderfall A=6 (bedingter Sprung mit Rückkehrabsicht) mit dem Schalter SP. Das war die Rolle der
FRÜHEREN Fassung von ANWEISUNG-008/009 (s. o.), nicht die der jetzigen (A=4/5/7, AC/Vergleicher/Überlauf).
Ob diese Kommentare im Regelwerk selbst nur noch nicht nachgezogen wurden, oder ob ANWEISUNG-010 (T2:
"interne Umstellung auf A=0") in Wahrheit weiterhin für A=6 zuständig ist und an anderer, hier noch nicht
identifizierter Stelle geprüft wird, ist ungeklärt. Ebenso ungeklärt: ob die Wahl `A := 2` (statt des
T2-Wortlauts "A=0") in ANWEISUNG-010 (s. 9.4) unter der neuen Bedeutung von 008/009 noch zutrifft. Bis zur
Klärung durch den Autor bleiben ANWEISUNG-010, -013, -018 und -043 unverändert (ihr eigener Wortlaut
widerspricht der aktuellen T2-Fassung nicht direkt, nur die Konsistenz mit 008/009 ist fraglich); es wird
kein Generator-Stub benötigt, da alle vier weiterhin `F`/`F/V` gemäß ihrem eigenen T2-Eintrag sind.

**Nachtrag Stand 27.09.2026 (SW-Ausgabe/KB-GB-Logik korrigiert):** Zwei Punkte zur Schreibwerk-Ausgabe
wurden vom Autor richtiggestellt:

- Die bisherige Aussage in 11.5, die SW-Ausgabe warte auf Schalter/Flag SW = 1, war falsch und
  widersprach bereits 11.2 ("K2 → SW-Ausgabe, unabhängig vom Schalter SW"). Entfernt.
- Neu eingeführt: ein von der eingabeseitigen Zeichenlage (`zs_zeichenlage`, 11.7) unabhängiger
  Ausgabe-Zustand `zs_sw_zeichenlage` (11.5a) — beim Einschalten zufällig auf KB/GB gesetzt, geändert
  durch Ausgabe der Adressen 117x (KB) bzw. 057x (GB). Bestimmt jetzt die Ascii-Spaltenwahl in 11.5
  statt der bisher (fälschlich) dafür verwendeten `zs_zeichenlage`.

**Nachtrag Stand 27.09.2026 (WM-Definition korrigiert):** WM ("Wortmarke") ist laut Autor identisch mit
TAB (Tabulator), Eingabe-Adresse 075 oktal, Sprung-Umstellung = ja (Tabelle 1, Zeile 12) — nicht wie
zuvor angenommen identisch mit ".". 11.6 und die Datei "C8205-Interpreter-Bedienpult_mit_Schaltern.md" entsprechend korrigiert.

---

## 16 Abnahmetests

1. **Generatorprüfung:** Alle Validierungen aus 8.4 und 11.8 bestehen; Anzahl Knoten = 72, Anweisungen = 42.
2. **Beispiel A** (Tastenfolge `H G R`, Trommeldatei aus "C8205-Interpreter-Durchführung_eines_Tests.md", 2): Der Automat startet
   mit dem Befehl auf Adresse 0000. Ohne `#PROT`-Marke (Standard `STUFE=1`) erscheinen die durchlaufenen
   Knoten auf dem Bildschirm; es entsteht keine `protokoll.txt`.
3. **Beispiel B** (Ansprung 0004 über `H G M+ E E E E M- R`): Der erste entnommene Befehl liegt auf Adresse 0004. Vor dem Start bei Konnektor B gilt `AC = 00000005000`.
4. **Strg+C:** In jeder Warteschleife (echt: 5/6; K0-Eingabe; Leser ohne Streifen) beendet Strg+C den Lauf
   kontrolliert mit Exit-Code 130 und geschlossenen Dateien.
5. **Zeitmodus:** Derselbe Test liefert in `interpretativ` und `echt` gleiche Register-/Flagendzustände.
6. **Bahnsperre:** Ein Transportbefehl auf eine gesperrte Bahn ändert die Zelle nicht, der Ablauf läuft weiter.
7. **Debug:** Ein Test mit 164 und `#DOK`/`#SPEI` zeigt genau die Diagnose nach 13.1 auf dem Bildschirm —
   unabhängig davon, ob `#PROT` gesetzt ist. Nur bei zusätzlichem `#PROT STUFE=2` erscheint dieselbe
   Diagnose außerdem in `protokoll.txt`.
8. **Bedingte Sprünge:** Ein Test mit Negativ-Sprung (AC<0 erfüllt und nicht erfüllt) springt bzw. läuft weiter wie in der Befehlsliste beschrieben.
9. **Protokollierungsstufen:** Derselbe Test, einmal mit `#PROT STUFE=0`, einmal mit `STUFE=1` und einmal
   mit `STUFE=2` gefahren: Bei `STUFE=0` erscheinen weder Knotenzustände auf dem Bildschirm noch entsteht
   eine `protokoll.txt`; bei `STUFE=1` erscheinen die Knotenzustände auf dem Bildschirm, es entsteht keine
   Datei; bei `STUFE=2` entsteht eine `protokoll.txt` mit den Knotenzuständen, ohne dass diese auf dem
   Bildschirm erscheinen. In allen drei Fällen bleiben Register-/Flagendzustände identisch — die Stufe
   beeinflusst ausschließlich die Protokollierung, nicht die Ausführung.
10. **Widersprüchliche Trommeldatei:** Eine Trommeldatei, die dieselbe Adresse zweimal mit
    unterschiedlichem Wert definiert, führt zu Exit-Code 1 vor Testbeginn (12.6), ohne dass der Automat
    anläuft.
11. **Ü (Fall 3/5):** `H Ü R` führt BR = `7777 240` aus (Start bei Knoten 19); `H G Ü E` endet im Halt an HP3 mit
    `AR`/`OR`/`BZ` gemäß Phase II und III des Befehls aus Zelle ⟨BZ⟩; `Ü` ohne vorheriges `H` ändert AR/OR nicht.
12. **M:** `H G M R` (Fall 4, M = `M+ M-`) führt BR = `0000 025` aus (Start bei Knoten 19). `H G M- R` und
    `H G M+ E R` (M nicht losgelassen) führen zu Exit-Code 1 vor Testbeginn; `H G M+ E E E E M- R` (Beispiel B)
    ist gültig.
13. **E allein:** `H G E E` führt zwei Einzelschritte über den Knotengraphen aus und endet im Halt (H bleibt 1).
14. **ST:** `H G Ü ST R` führt BR = `7777 240` aus (Start bei Knoten 19), US ist danach 0; `H ST R` (ohne `G`, US=0)
    ändert BR nicht (ST ohne Wirkung), der Lauf beginnt bei Konnektor B.