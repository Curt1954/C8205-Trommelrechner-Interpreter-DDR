** Magnettrommel (Speicher) **

Der gesamte Speicher liegt magnetisch auf einer Trommel, organisiert in Zellen (Maschinenworten).


## Speicherorganisation

Die Trommel hat 128 Spuren (auch Bahnen genannt) mit je 32 Sektoren. Speicherkapazität gesamt:
128 × 32 = 4096 Maschinenworte à 33 Bit. Eine 12-Bit-Adresse gliedert sich in Bahn-Nr. (7 Bit) und
Sektor-Nr. (5 Bit) – die genaue Bit-Aufteilung im Maschinenwort ist in der Datei "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md"
(Abschnitt Register/Felder, Feld "Adresse": Spur z₁₂–z₁₈, Sektor z₁₉–z₂₃) beschrieben.
(zahlenangaben dezimal)

## Speichernumerierung / Interleaving

Die logische (Adressierungs-)Reihenfolge der Sektoren einer Spur entspricht NICHT der physisch-
räumlichen Abfolge auf der Trommel. Durch die Drehung der Trommel ergibt sich zwar grundsätzlich eine
physische und zeitliche Abfolge der Sektoren, doch die Leseelektronik konnte aus Leistungsgründen nicht
jeden physisch aufeinanderfolgenden Sektor unmittelbar nacheinander lesen, sondern jeweils nur jeden
6. physisch aufeinanderfolgenden Sektor (gezählt einschließlich des gerade gelesenen, also 5 Positionen
weiter; vier Sektoren werden übersprungen, s. Tabelle). Die logische Sektoradresse wird entsprechend dieser technisch
bedingten Zugriffsreihenfolge vergeben. Aus diesem physisch bedingten Aufbau resultiert (mindestens
teilweise) auch das Zustandekommen von Wartezeit.

Vollständige physische Zugriffsreihenfolge (alle 32 Sektoradressen, oktal, jede genau einmal, danach
Wiederholung bei der nächsten Trommelumdrehung):

| Position (physisch) | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 |
|---|---|---|---|---|---|---|---|---|
| logische Sektoradresse | 00 | 15 | 32 | 07 | 24 | 01 | 16 | 33 |

| Position (physisch) | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|---|---|
| logische Sektoradresse | 10 | 25 | 02 | 17 | 34 | 11 | 26 | 03 |

| Position (physisch) | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 |
|---|---|---|---|---|---|---|---|---|
| logische Sektoradresse | 20 | 35 | 12 | 27 | 04 | 21 | 36 | 13 |

| Position (physisch) | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 |
|---|---|---|---|---|---|---|---|---|
| logische Sektoradresse | 30 | 05 | 22 | 37 | 14 | 31 | 06 | 23 |

(alle Angaben oktal)

Schreitet man in dieser Reihenfolge von einer logischen Adresse L zur logisch nächsten L+1 fort, beträgt
der Abstand zwischen ihren beiden Positionen durchgehend +05 (oktal). Umgekehrt entspricht der Schritt
von einer physischen Position zur unmittelbar benachbarten physischen Position durchgehend +15 (oktal)
in der logischen Adresse. Beide Schrittweiten sind zueinander invers modulo 40 (oktal)
(05 · 15 ≡ 01 mod 40, oktal) – eine konsistente Kehrwert-Beziehung, keine zwei unabhängigen Fakten.

Eine Wortzeit – die Zeit, die vergeht, bis der nächste Sektor unter dem Lese-/Schreibkopf ansteht –
beträgt 104 µs.

**Bahnwahl:** Jede Bahn wird über eine eigene, bahnspezifische Elektronik ausgewählt; die dafür nötige
minimale Schaltzeit ist für alle Bahnen gleich und wegen ihrer Kleinheit vernachlässigbar (= 0 gesetzt).
Ein Bahnwechsel kostet daher – anders als ein Sektor-Zugriff innerhalb derselben Bahn – keine
zusätzliche Wartezeit; ausschlaggebend für die Zugriffszeit ist ausschließlich die Sektorposition
innerhalb der (beliebig) gewählten Bahn.

**Grund für die Zugriffszeit-Problematik:** Anders als bei einem Rechner mit wahlfreiem, gleichmäßig
schnellem Zugriff (RAM) ist die Zugriffszeit beim Trommelrechner variabel und potenziell lang: Eine
Zelle ist unter dem Lese-/Schreibkopf nicht kontinuierlich zugreifbar, sondern nur diskret – direkt nach
einem Zugriff erst wieder bei der logisch folgenden Zelle, die physisch 5 Positionen weiter liegt (der 6.
Sektor, einschließlich des gelesenen gezählt). Liegen Programm bzw. Daten so im Speicher
verteilt, dass der jeweils logisch nächste benötigte Zugriff genau auf diese Distanz fällt, ist
der Zugriff zeitoptimal (keine zusätzliche Wartezeit). Andernfalls muss unter Umständen eine volle
Trommelumdrehung abgewartet werden, bis die gewünschte Zelle wieder zugreifbar ist.

**Zeitoptimale Folgeadresse je Befehlsart:** Für die drei Befehlsarten Einzelbefehl, Gruppenbefehl und
Sprung berechnet sich, ausgehend von der aktuell eingestellten Speicheradresse A, die Adresse der Zelle,
auf die frühestens ohne zusätzliche Wartezeit zugegriffen werden kann:

| Befehlsart | Formel(n) (oktal, mod 40) |
|---|---|
| Einzelbefehl | A+32; A+07 |
| Gruppenbefehl | A+32; A+07; A+24 |
| Sprung | A+24 |

Das sind Formeln als Programmier-/Layout-Hilfe zur Vermeidung unnötiger Wartezeiten, keine Eigenschaft
der Befehlsausführung selbst.


## Bahnsperrenschalter

Schützt innerhalb der Spuren 0000 bis 1740 (oktal) bestimmte, auswählbare Gruppen von Bahnen gegen
irrtümliches Überschreiben. Der Befehlsablauf wird dadurch nicht beeinflusst – reine
Schreibschutz-Funktion, keine Auswirkung auf die Befehlsverarbeitung selbst. Die Schalter befinden
sich physisch an der Rückseite der Tastatur-Anzeige-Einheit; für die Testdefinition gehören sie zum Bedienpult
(Bezeichnungen `BSP_0001` … `BSP_1000`, s. Dokument "C8205-Interpreter-Bedienpult_mit_Schaltern.md"). Im
Grundzustand sind alle sechs AUS, es besteht keine Sperre.

Sechs Einzelschalter, jeder mit seiner oktalen Kennzeichnung, die angibt, welchen Adreßbereich/-kanal er
sperren kann: 0001, 0040, 0100, 0200, 0400, 1000. Der erste dieser sechs (Kennzeichnung 0001) trägt als
einziger keine Zahl, sondern die für ihn wie für alle anderen geltende Doppelbezeichnung "EIN–AUS"; die
übrigen fünf sind EIN/AUS-Schalter mit ihrer Zahl als Beschriftung. Der Schalter 0001 ist der Hauptschalter; die
Schalter 0040 bis 1000 heißen Zusatzschalter. Der EIN–AUS-Schalter wirkt unabhängig
von den fünf anderen: in Stellung "EIN" ist (mindestens) Spur 0000 gegen Überschreiben gesichert; in
Stellung "AUS" sind alle Spuren offen – unabhängig davon, wie die fünf anderen Schalter stehen.

Bei Hauptschalter EIN gilt eine Bahn B (Bahn-Nr. als Ganzzahl, 0 = Spur 0000, 1 = Spur 0040, …,
37 oktal = Spur 1740) genau dann als gesperrt, wenn B eine (einschließlich leere) Bit-Teilmenge der
eingeschalteten Zusatzschalter ist – wobei 40 (oktal) → Bit0, 100 (oktal) → Bit1, 200 (oktal) → Bit2,
400 (oktal) → Bit3, 1000 (oktal) → Bit4 der Bahn-Nr. entspricht. Spur 0000 (leere Teilmenge) ist damit
bei Hauptschalter EIN immer gesperrt, unabhängig von den fünf Zusatzschaltern. Folge: Bahnen ab Spur
2000 (oktal) (Bahn-Nr. ≥ 32) sind über diese Schalter grundsätzlich nie sperrbar (die Regel deckt nur
5 Bit = 32 Bahnen ab).
