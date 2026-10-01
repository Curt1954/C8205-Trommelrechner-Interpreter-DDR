# Kodetabellen

Die Zeichenkode-Tabellen des C 8205: Lochstreifenkode (Tabelle 1),
R 300-Lochkartenkode (Tabelle 2) und Fernschreibkode CCITT-2 (Tabelle 3).

## Inhaltsverzeichnis

- [1 Tabelle 1 — Lochstreifenkode](#1-tabelle-1--lochstreifenkode)
 - [1.1 Spalten und Bedeutung](#11-spalten-und-bedeutung)
 - [1.2 Verwendung durch Leser und Stanzer](#12-verwendung-durch-leser-und-stanzer)
 - [1.3 Lochbilder und Konsistenzprüfung](#13-lochbilder-und-konsistenzprüfung)
 - [1.4 Die Tabelle](#14-die-tabelle)
 - [1.5 Sprung-Umstellung](#15-sprung-umstellung)
 - [1.6 Sonderzeilen und Zeichen ohne ASCII-Wert](#16-sonderzeilen-und-zeichen-ohne-ascii-wert)
 - [1.7 Auffälligkeiten](#17-auffälligkeiten)
- [2 R 300-Kode und weitere Kodes](#2-r-300-kode-und-weitere-kodes)
 - [2.1 Spalten und Bedeutung (abgeleitet)](#21-spalten-und-bedeutung-abgeleitet)
 - [2.2 Abgleich mit Tabelle 1](#22-abgleich-mit-tabelle-1)
 - [2.3 Die Tabelle](#23-die-tabelle)
 - [2.4 Bezug zum Bedienungspult und offene Punkte](#24-bezug-zum-bedienungspult-und-offene-punkte)
 - [2.5 Abgleich mit der Lochkarten-Grafik](#25-abgleich-mit-der-lochkarten-grafik-q6)
- [3 FS-Kode (CCITT-2)](#3-fs-kode-ccitt-2)
 - [3.1 Spalten und Bedeutung](#31-spalten-und-bedeutung)
 - [3.2 Die Tabelle](#32-die-tabelle)
 - [3.3 Bezug zu Tabelle 1/2 und offene Punkte](#33-bezug-zu-tabelle-12-und-offene-punkte)
- [4 Gemeinsame Bezüge der Tabellen](#4-gemeinsame-bezüge-der-tabellen)
- [Änderungsprotokoll (Kodetabellen)](#änderungsprotokoll-kodetabellen)

---

## 1 Tabelle 1 — Lochstreifenkode

*Quellen der Quelle/der Quelle. Die Tabelle betrifft Lochstreifenleser UND
Lochstreifenstanzer sowie die Befehlsdefinition (Spalte
"Sprung-Umstellung").*

### 1.1 Spalten und Bedeutung

**Spalten der Original-Tabelle (in Originalreihenfolge):** Klbuch —
BCD (zu Klbuch) — Gbuch — BCD (zu Gbuch) — Lochspuren **w v u p 8 Tr 4 2
1** — Eingabe Adresse — Sprung-Umstellung — Ausgabe-Adresse C8205 oktal
— Ascii GB — Ascii KB.

**Bedeutung der Spalten:**

| Spalte | Bedeutung |
|---|---|
| Klbuch / Gbuch | Klbuch = Kleinbuchstaben, Gbuch = Großbuchstaben (Zeichenlagen). Im Rechner haben Groß- und Kleinbuchstaben keinen unterschiedlichen Kode, sondern werden durch einen Zusatzkode unterschieden. Wie ein gelesenes Zeichen intern im Speicher kodiert wird, hängt davon ab, ob zeicheneingabe-übergreifend VORHER ein Zeichen Klbuch oder Gbuch gelesen wurde |
| BCD | Lochkartenkode (Zonen-/Ziffernlochungen, z. B. 11^6^8) |
| Eingabe Adresse | interne Kodenummer des Rechners, eigentlich ein Alias dafür (oktal) |
| Sprung-Umstellung | technische Fähigkeit des Rechenwerks: bei Lochstreifeneingabe wird der Eingabewert in eine gültige Darstellung im Rechnerspeicher umgerechnet. Wird bei der **Definition der Befehle** gebraucht, nicht für die Definition des Lesers an sich |
| Ausgabe-Adresse C8205 oktal | vier Oktalstellen; die letzte ("x") ist beliebig und wird ignoriert. Die ersten drei Stellen entsprechen dem Bitmuster des Lochbilds (s. 1.3) |
| Ascii GB / Ascii KB | Kodewert (dezimal) des Zeichens in Gbuch bzw. Klbuch. Werte wie 465 sind Kodes aus der Zeit vor ASCII, die real existierten und 1967 technisch so dargestellt wurden |

### 1.2 Verwendung durch Leser und Stanzer

**Verwendung der Tabelle:** Die Tabelle wird vom Leser
und vom Stanzer referiert.

- **Leser:** maßgebend ist die Spalte "Eingabe Adresse". Sie ist ein Wert
 des Lesers, der ihn sendet; der Rechner muss ihn interpretieren.
- **Stanzer:** maßgebend ist die Spalte "Ausgabe-Adresse". Sie ist ein
 Wert des Rechners, der ihn sendet; die Stanzer-Elektronik muss ihn
 interpretieren.

### 1.3 Lochbilder und Konsistenzprüfung

**Lochbilder:** Die gestanzten Spuren jeder Zeile sind
der Quelle entnommen (Punkte maschinell ausgelesen und den Spalten
w v u p 8 Tr 4 2 1 zugeordnet, alle 52 Zeilen). Sie stimmen in allen 52
Zeilen exakt mit dem Bitmuster der Spalte "Ausgabe-Adresse" überein
(dort als Oktalzahl, letztes "x" s. 1.7). Daraus folgt die Regel:

| Spur | 1 | 2 | 4 | 8 | p | u | v | w |
|---|---|---|---|---|---|---|---|---|
| Bitwert in Ausgabe-Adresse | 1 | 2 | 4 | 10₈ | 20₈ | 40₈ | 100₈ | 200₈ |

Die Spalte **Tr** kommt in der Ausgabe-Adresse nicht vor und ist in
keiner Zeile mit einem Punkt besetzt (auch nicht bei "Transport"). Sie ist die Transportlochung und trägt
keine Information (s. Lochstreifenleser, A4).

**Konsistenzprüfung (maschinell, alle 52 Zeilen):**
- In 51 von 52 Zeilen ist die Anzahl der Lochungen **ungerade** (Parität
 ungerade; **p** ergänzt die Datenspuren zu ungerader Zahl). Ausnahme:
 "Irrung Zeichen" (8 Lochungen, gerade) — s. 1.7.
- Die Spalte "Eingabe Adresse" ergibt sich in 51 Zeilen aus den Spuren 1,
 2, 4, 8, u, v (u = 20₈, v = 40₈ im 6-Bit-Wert; p und w bleiben
 unberücksichtigt). Ausnahme: "Irrung Zeichen" — liefert dieses
 Zeichen KEINE Eingabeadresse (Zeile 50, s. 1.6/1.7).
- Alle Werte der Spalte "Eingabe Adresse" sind eindeutig, alle Werte der
 Spalte "Ausgabe-Adresse" ebenfalls.
- Ascii-Werte stimmen für alle Einzelzeichen mit dem Zeichen der jeweiligen
 Spalte überein (nach den Korrekturen der Zeile 20, s. u.); Ausnahme:
 Zeile 48 (Wert 465, Kode aus der Zeit vor ASCII).

### 1.4 Die Tabelle

*Lesehilfe: Spalte "Lochbild" = gestanzte Spuren der Zeile (Reihenfolge
w v u p 8 4 2 1), "—" = im
Original leer. Die Spalten "Eingabe-Adresse" und "Ausgabe-Adresse" sind
oktal (letzteres mit dem "x" der Quelle = beliebige, ignorierte Stelle).
"Ascii GB/KB" sind dezimal. † = gegenüber der Vorlage
korrigiert (bei Zeile 50: Eingabe Adresse "56" der Vorlage ist falsch,
das Zeichen liefert keine Eingabeadresse; bei den Zeilen 24, 36, 37, 49:
Spalte "Sprung-Umstellung" gegenüber einer früheren Fassung dieses
Dokuments korrigiert, s. 1.5). "(Relikt)" = Zusatz dieses
Dokuments für Zeile 52, s. 1.6.*

| Nr. | Klbuch | BCD (Kl) | Gbuch | BCD (G) | Lochbild | Eingabe Adresse | Sprung-Umstellung | Ausgabe-Adresse | Ascii GB | Ascii KB |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 1 | < | 11^6^8 | 1 | 1 | nein | 001x | 60 | 49 |
| 2 | 2 | 2 | " | 12^7^8 | 2 | 2 | nein | 002x | 34 | 50 |
| 3 | 3 | 3 | ≈ | 11^2^8 | p 2 1 | 3 | nein | 023x | 0 | 51 |
| 4 | 4 | 4 | [ | 0^7^8 | 4 | 4 | nein | 004x | 91 | 52 |
| 5 | 5 | 5 | > | 0^6^8 | p 4 1 | 5 | nein | 025x | 62 | 53 |
| 6 | 6 | 6 | ' | 12^11^0 | p 4 2 | 6 | nein | 026x | 39 | 54 |
| 7 | 7 | 7 | ≋ | 0^2^8 | 4 2 1 | 7 | nein | 007x | 0 | 55 |
| 8 | 8 | 8 | ~ | 12^2^8 | 8 | 10 | nein | 010x | 126 | 56 |
| 9 | 9 | 9 | ] | 7^8 | p 8 1 | 11 | nein | 031x | 93 | 57 |
| 10 | 0 | 0 | # | 3^8 | p | 0 | nein | 020x | 35 | 48 |
| 11 | % | 0^4^8 | \* | 11^4^8 | v u p 8 4 | 74 | nein | 174x | 42 | 37 |
| 12 | Tabulator | — | Tabulator | — | v u 8 4 1 | 75 | ja | 155x | 9 | 9 |
| 13 | q | — | Q | 11^8 | v p 8 | 50 | nein | 130x | 81 | 113 |
| 14 | w | — | W | 0^6 | v u p 4 2 | 66 | nein | 166x | 87 | 119 |
| 15 | e | — | E | 12^5 | u 4 1 | 25 | nein | 045x | 69 | 101 |
| 16 | r | — | R | 11^9 † | v 8 1 | 51 | nein | 111x | 82 | 114 |
| 17 | t | — | T | 0^3 | v u p 2 1 | 63 | nein | 163x | 84 | 116 |
| 18 | z | — | Z | 0^9 | v u p 8 1 | 71 | nein | 171x | 90 | 122 |
| 19 | u | — | U | 0^4 | v u 4 | 64 | nein | 144x | 85 | 117 |
| 20 | i † | — | I | 12^9 | u 8 1 | 31 | nein | 051x | 73 | 105 |
| 21 | o | — | O | 11^6 | v 4 2 | 46 | nein | 106x | 79 | 111 |
| 22 | p | — | P | 11^7 | v p 4 2 1 | 47 | nein | 127x | 80 | 112 |
| 23 | : | 5^8 | ( | 4^8 | 8 4 1 | 15 | ja | 015x | 40 | 58 |
| 24 | + | 12^0 | = | 11^5^8 | u | 20 | ja† | 040x | 61 | 43 |
| 25 | Um. KB | — | Um. KB | — | v 8 4 2 1 | 57 | ja | 117x | 0 | 0 |
| 26 | Um. GB | — | Um. GB | — | u 8 4 2 1 | 37 | ja | 057x | 0 | 0 |
| 27 | a | — | A | 12^1 | u p 1 | 21 | nein | 061x | 65 | 97 |
| 28 | s | — | S | 0^2 | v u 2 | 62 | nein | 142x | 83 | 115 |
| 29 | d | — | D | 12^4 | u p 4 | 24 | nein | 064x | 68 | 100 |
| 30 | f | — | F | 12^6 | u 4 2 | 26 | nein | 046x | 70 | 102 |
| 31 | g | — | G | 12^7 | u p 4 2 1 | 27 | nein | 067x | 71 | 103 |
| 32 | h | — | H | 12^8 | u p 8 | 30 | nein | 070x | 72 | 104 |
| 33 | j | — | J | 11^1 | v p 1 | 41 | nein | 121x | 74 | 106 |
| 34 | k | — | K | 11^2 | v p 2 | 42 | nein | 122x | 75 | 107 |
| 35 | l | 4^8 | L | 11^3 | v 2 1 | 43 | nein | 103x | 76 | 108 |
| 36 | \` | — | ; | 12^4^8 | v u p | 60 | nein† | 160x | 59 | 96 |
| 37 | / | 0^1 | ) | 11^3^8 | v u 1 | 61 | ja† | 141x | 41 | 47 |
| 38 | SatzMarke | — | WRZL | — | w u p 8 2 | 32 | ja | 272x | 10 | 10 |
| 39 | y | — | Y | 0^8 | v u 8 | 70 | nein | 150x | 89 | 121 |
| 40 | x | — | X | 0^7 | v u 4 2 1 | 67 | nein | 147x | 88 | 120 |
| 41 | c | — | C | 12^3 | u 2 1 | 23 | nein | 043x | 67 | 99 |
| 42 | v | — | V | 0^5 | v u p 4 1 | 65 | nein | 165x | 86 | 118 |
| 43 | b | — | B | 12^2 | u p 2 | 22 | nein | 062x | 66 | 98 |
| 44 | n | — | N | 11^5 | v 4 1 | 45 | nein | 105x | 78 | 110 |
| 45 | m | — | M | 11^4 | v p 4 | 44 | nein | 124x | 77 | 109 |
| 46 | , | 0^3^8 | ? | 11^7^8 | v u 8 2 1 | 73 | ja | 153x | 63 | 44 |
| 47 | . | 3^8 | ! | 12^5^8 | u p 8 2 1 | 33 | ja | 073x | 33 | 46 |
| 48 | - | 11^0 | △ | 0^5^8 | v | 40 | ja | 100x | 465 | 45 |
| 49 | Leertaste | 8^2 | ZR | — | p 8 2 | 12 | nein† | 032x | 32 | 32 |
| 50 | Irrung Zeichen | — | Irrung Zeichen | — | w v u p 8 4 2 1 | — † | nein | 377x | 0 | 0 |
| 51 | Irrung Satz | — | Irrung Satz | — | 8 4 2 | 16 | ja | 016x | 0 | 0 |
| 52 | Transport (Relikt) | — | Transport (Relikt) | — | v u p 8 4 2 1 | 77 | nein | 177x | 0 | 0 |

*(Zeilennummer "Nr." nur zur Referenz in diesem Dokument, nicht Teil der
Original-Tabelle.)*

### 1.5 Sprung-Umstellung

**Zeilen mit Sprung-Umstellung = ja (11), gemäß Originalquelle
(Kodetabelle_1.pdf) — geklärt:** Tabulator, ":", "+/=", Um. KB, Um. GB,
"/ )", SatzMarke, ",", ".", "-", Irrung Satz.

Gegenüber einer früheren Fassung dieses Dokuments wurden vier Werte
korrigiert (in 1.4 mit † markiert): "+/=" (Nr. 24, Adresse 20) und
"/ )" (Nr. 37, Adresse 61) waren fälschlich "nein", sind laut Quelle
"ja"; "`" (Nr. 36, Adresse 60) und Leertaste (Nr. 49, Adresse 12) waren
fälschlich "ja", sind laut Quelle "nein". Damit ist Leertaste NICHT in
der Liste enthalten (im Unterschied zur vorherigen Fassung), "+/=" und
"/ )" dagegen schon.

Ein zwischenzeitlich diskutierter Formelansatz (logischer Ausdruck über
die acht Datenspuren, aus einer Originalabbildung übertragen) wurde
verworfen: Mehrere Terme ließen sich trotz wiederholter Prüfung am
Original nicht widerspruchsfrei mit der jetzt gesicherten Tabelle 1 in
Einklang bringen. Maßgeblich ist stattdessen ausschließlich die Spalte
"Sprung-Umstellung" der Tabelle 1 wie oben in 1.4 wiedergegeben.

Die Bedeutung (s. 1.1) gehört zur Befehlsdefinition; der Bezug zur
Bemerkung bei Eingabebefehl 2. Art (Befehlsliste, B=1/A=1: "wenn keine
Umstellung in Sprungbefehl…") liegt nahe, ist aber nicht ausdrücklich
bestätigt. **offen**

### 1.6 Sonderzeilen und Zeichen ohne ASCII-Wert

**

- **Zeichen ohne ASCII-Wert (Ascii = 0):** "≈", "≋", "Um. KB", "Um. GB",
 "Irrung Zeichen", "Irrung Satz", "Transport". Das sind Zeichen, die die
 ASCII-Definition nicht kennt, die aber in der Vorläufer-Rechentechnik
 jener Zeit real existierten. **Ausgabe über den Stanzer:** Alle
 Zeichen der Spalte "Ausgabe-Adresse C8205 oktal" sind ausgebbar, alle
 anderen nicht. (Über Lochkarte, BCD-Kode, war Ausgabe möglich;
 Lochkarten werden hier nicht betrachtet, s. Lochstreifenleser, Geltungsbereich.)
- **"Irrung Zeichen" und "Irrung Satz":** stammen aus der Zeit der
 Lochstreifenverarbeitung ohne Rechner. Ein einmal gestanztes Zeichen
 lässt sich nicht rückgängig machen. War das Stanzen falsch, wurde
 "Irrung Zeichen" nachgesetzt, um die vorhergehende Lochung unschädlich
 zu machen; analog "Irrung Satz". Die Daten auf Lochstreifen waren
 satzweise organisiert (logische Einheit, nichts Leserspezifisches: der
 Leser liest immer nur ein Zeichen). Mit "Irrung Satz" konnten viele
 Lochungen auf einmal als falsch gekennzeichnet werden.
- **"Irrung Zeichen" beim Lesen:** Alle 8 Spuren gelocht, also gerade
 Anzahl Bits und damit kein gültiges Zeichen — Absicht: So erkennt der
 Leser ohne Lesen und Interpretieren, dass es kein Zeichen ist. Das
 Zeichen liefert **keine** Eingabeadresse (die 56 der Vorlage ist falsch)
 und wird als Irrung des unmittelbar davor gelochten Zeichens
 interpretiert. **Der Rechner benutzt keine Irrung-Zeichen**: Sie
 werden gebraucht, wenn der Mensch Daten auf Lochstreifen erfasst, denn
 irren tut nur der Mensch. Der Rechner könnte die Zeichen ausgeben, wenn
 das im Programm so programmiert ist; eine Automatik gibt es nicht. Beim
 Lesen von "Irrung Zeichen" liegt ein Gerätefehler vor: FE leuchtet und
 der Rechner stoppt (Lochstreifenleser A2).
- **"Transport" (Zeile 52):** Relikt aus noch früheren Zeiten, nie
 benutzt. Der tatsächliche Transport heißt "Transport Vorspann" und hat
 keine Datenlochung, nur die kleine Transportlochung (Lochstreifenleser A1).

### 1.7 Auffälligkeiten

*Feststellungen; Korrekturen nur, soweit bestätigt.*

**Geklärt:**

1. **Zeile 20:** Klbuch = "i" (die Vorlage zeigt "I"; Ascii KB 105 = "i").
 In der Tabelle korrigiert (†).
2. **R (Zeile 16):** BCD = 11^9 (die Vorlage zeigt 11^7, doppelt mit "P").
 In der Tabelle korrigiert (†).
3. **Zeile 48 ("-" / "△"):** Ascii GB = 465 ist kein Fehler, sondern ein
 Kode aus der Zeit vor ASCII (1967 real so dargestellt). Unverändert.
4. **"x"** hinter der Ausgabe-Adresse: beliebige Stelle, wird ignoriert.
5. **Ascii = 0:** Zeichen, die ASCII nicht kennt (1.6).
6. **"Irrung Zeichen":** gerade Parität ist Absicht; die Eingabe Adresse
 56 der Vorlage ist falsch, das Zeichen liefert keine Eingabeadresse
 (Zeile 50, †).
7. **Spur Tr:** Transportlochung ohne Information, daher in keiner
 Zeile besetzt (Lochstreifenleser A1).
8. **Zeile 52 "Transport":** Relikt, nie benutzt (1.6).

**Feststellung:**

9. **Spur w:** nur bei "SatzMarke" und "Irrung Zeichen" besetzt (alle
 anderen Zeilen benutzen höchstens 7 Spuren).

---

## 2 R 300-Kode und weitere Kodes

*Quelle der Quelle: „Tabelle 2 – R300 Lochkartenkode" ( am 20.09.2026 als
Grafik und danach als Text eingebracht). Die Zeilen haben folgendes Format:
`"Lochbild", Lage, Ausgabe-Adresse, Eingabe-Adresse, 'Zeichen', // Kommentar`.
Die Tabelle in 2.3 gibt die Textfassung des Autors wieder (63 Zeilen; die
Zeilennummer „Nr." gehört nicht zur Vorlage). Die
Spaltenbedeutungen in 2.1 sind **abgeleitet** (Abgleich mit Tabelle 1, 2.2) und
noch nicht eigens bestätigt.*

### 2.1 Spalten und Bedeutung (abgeleitet)

| Spalte (Reihenfolge der Vorlage) | Bedeutung |
|---|---|
| Lochbild | 12 Zeichen „0"/„1" für die Zeilen der Lochkarte in der Reihenfolge **12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9** (1 = gelocht). Entspricht der Spalte „BCD" in Tabelle 1 (z. B. „<" = 11-6-8 = `010000001010`). |
| Lage | Zeichenlage: **1** = Klbuch (Kleinbuchstaben-Lage), **0** = Gbuch (Großbuchstaben-Lage), **x** = in beiden Lagen gleich (Buchstaben und Leerzeichen). Ziffern sind 1, ihre Sonderzeichen 0. |
| Ausgabe-Adresse | 12-Bit-Wert als Oktalzahl mit führender 0 (Schreibweise der Vorlage): `0010` = 010₈ entspricht der Ausgabe-Adresse „001x" aus Tabelle 1 mit x = 0. |
| Eingabe-Adresse | Oktalzahl mit führender 0 (Schreibweise der Vorlage) der internen Kodenummer (`010` = 10₈ = „Eingabe Adresse" 10 aus Tabelle 1). |
| Zeichen, Kommentar | Zeichen und Kommentar der Vorlage („Leer", „Dreieck"; sonst das Zeichen selbst). „\|" steht für das Zeichen der Klbuch-Zeile „l" (Tabelle 1, Nr. 35), „@" für „△", „(Leer)" für die Leertaste bzw. ZR. Das Zeichen „'" (Nr. 16) steht in der Textfassung als `"'"`. |

### 2.2 Abgleich mit Tabelle 1

*Maschineller Abgleich aller 63 Zeilen von Tabelle 2 mit den Zeilen von
Tabelle 1 (Zuordnung über das Zeichen; letzte Spalte der Tabelle in 2.3).*

- **Ausgabe-Adresse und Eingabe-Adresse** stimmen in allen 63 Zeilen mit
 Tabelle 1 überein; die Lage passt in allen 63 Zeilen zur Zuordnung
 Klbuch/Gbuch bzw. Buchstabe.
- **Lochbild:** 60 von 63 Zeilen stimmen mit der Spalte „BCD" von Tabelle 1
 überein. **Drei Abweichungen — geklärt: Fehler der
 Vorlage, Tabelle 2 an Tabelle 1 angeglichen** (Korrektur in 2.3
 eingetragen, †† markiert die drei angeglichenen Zeilen; ursprüngliche
 Vorlage-Werte hier dokumentiert):
 1. „[" (Nr. 14): Vorlage `001000000100` = 0-7; jetzt wie Tabelle 1:
 0-7-8 (`001000000110`). Die Vorlage hatte damit dasselbe Lochbild
 wie „X".
 2. „R" (Nr. 26): Vorlage `010000000100` = 11-7; jetzt wie Tabelle 1:
 11-9 (`010000000001`; Tabelle 1 hatte diese Zeile bereits selbst
 korrigiert, †; Vorlage 11-7 doppelt mit „P"). Die Vorlage hatte
 damit dasselbe Lochbild wie „P" (Nr. 32) — dieselbe
 Vorlage-Verwechslung, die in Tabelle 1 bereits korrigiert war.
 3. „." (Nr. 60): Vorlage `000010000010` = 2-8; jetzt wie Tabelle 1:
 3-8 (`000001000010`). Die Vorlage hatte damit dasselbe Lochbild wie
 die Leertaste (Nr. 61, Lage x).
 Maßgeblich für den Vergleich war Tabelle 1 mit den
 nachgereichten korrigierten Spalten: „[" 0-7-8, „R" 11-9, „." 3-8. Die
 Musterkarte (der Quelle, anderer Rechner, 2.5) stimmt bei „[" und „R" damit
 überein; bei „." weicht sie ab, was für die Klärung nicht maßgeblich
 war (2.5 entsprechend aktualisiert).
- **Nachgereichte korrigierte Spalten von Tabelle 1:**
 Die Werte der Spalten BCD (Kl) und BCD (G) stimmen in allen Zeilen mit
 Tabelle 1 in 1.4 überein. Einziger Unterschied: In der Zeile 20 steht in der
 Nachreichung Klbuch „I", in 1.4 „i" († Korrektur, 1.7 Punkt 1); 1.4 bleibt
 unverändert. **offen** (gilt „i"?).
- **Gleiche Lochbilder in Tabelle 1 (dokumentiert, kein Fehler der
 Transkription):** „#" und „." (3-8) sowie „(" und „l" (4-8); sie werden durch
 die Lage unterschieden. In Tabelle 2 bleibt nur das Paar „(" / „|" bestehen
 (Nr. 33 und 46, Lage 0 bzw. 1).
- **Zeilen von Tabelle 1 ohne Lochkartenkode** (Spalte BCD „—" in beiden
 Zeichenlagen) kommen in Tabelle 2 nicht vor: Tabulator, Um. KB, Um. GB,
 SatzMarke/WRZL, Irrung Zeichen, Irrung Satz, Transport. Das Klbuch-Zeichen
 „`" (Nr. 36) hat ebenfalls keine eigene Zeile (nur das Gbuch-Zeichen „;").
 Buchstaben erscheinen einmal (als Großbuchstabe, Lage x).

### 2.3 Die Tabelle

*Spalten wie in der Vorlage (Lochbild, Lage, Ausgabe-Adresse, Eingabe-Adresse,
Zeichen, Kommentar), dazu zur Lesbarkeit „Zeilen" (Kartenzeilen des Lochbilds,
abgeleitet) und „Tab. 1" (Nr. der zugehörigen Zeile in Tabelle 1, abgeleitet).
Alle Adressen sind oktal. †† = Lochbild an Tabelle 1
angeglichen (Vorlage wich ab; 2.2).*

| Nr. | Lochbild | Zeilen | Lage | Ausgabe-Adresse | Eingabe-Adresse | Zeichen | Kommentar | Tab. 1 |
|---|---|---|---|---|---|---|---|---|
| 1 | `000100000000` | 1 | 1 | 0010 | 01 | 1 | | 1 |
| 2 | `000010000000` | 2 | 1 | 0020 | 02 | 2 | | 2 |
| 3 | `000001000000` | 3 | 1 | 0230 | 03 | 3 | | 3 |
| 4 | `000000100000` | 4 | 1 | 0040 | 04 | 4 | | 4 |
| 5 | `000000010000` | 5 | 1 | 0250 | 05 | 5 | | 5 |
| 6 | `000000001000` | 6 | 1 | 0260 | 06 | 6 | | 6 |
| 7 | `000000000100` | 7 | 1 | 0070 | 07 | 7 | | 7 |
| 8 | `000000000010` | 8 | 1 | 0100 | 010 | 8 | | 8 |
| 9 | `000000000001` | 9 | 1 | 0310 | 011 | 9 | | 9 |
| 10 | `001000000000` | 0 | 1 | 0200 | 00 | 0 | | 10 |
| 11 | `010000001010` | 11-6-8 | 0 | 0010 | 01 | < | | 1 |
| 12 | `100000000110` | 12-7-8 | 0 | 0020 | 02 | " | | 2 |
| 13 | `010010000010` | 11-2-8 | 0 | 0230 | 03 | ≈ | | 3 |
| 14 | `001000000110` | 0-7-8 †† | 0 | 0040 | 04 | [ | | 4 |
| 15 | `001000001010` | 0-6-8 | 0 | 0250 | 05 | > | | 5 |
| 16 | `111000000000` | 12-11-0 | 0 | 0260 | 06 | ' | | 6 |
| 17 | `001010000010` | 0-2-8 | 0 | 0070 | 07 | ≋ | | 7 |
| 18 | `100010000010` | 12-2-8 | 0 | 0100 | 010 | ~ | | 8 |
| 19 | `000000000110` | 7-8 | 0 | 0310 | 011 | ] | | 9 |
| 20 | `000001000010` | 3-8 | 0 | 0200 | 00 | # | | 10 |
| 21 | `010000100010` | 11-4-8 | 0 | 01740 | 074 | * | | 11 |
| 22 | `001000100010` | 0-4-8 | 1 | 01740 | 074 | % | | 11 |
| 23 | `010000000010` | 11-8 | x | 01300 | 050 | Q | | 13 |
| 24 | `001000001000` | 0-6 | x | 01660 | 066 | W | | 14 |
| 25 | `100000010000` | 12-5 | x | 0450 | 025 | E | | 15 |
| 26 | `010000000001` | 11-9 †† | x | 01110 | 051 | R | | 16 |
| 27 | `001001000000` | 0-3 | x | 01630 | 063 | T | | 17 |
| 28 | `001000000001` | 0-9 | x | 01710 | 071 | Z | | 18 |
| 29 | `001000100000` | 0-4 | x | 01440 | 064 | U | | 19 |
| 30 | `100000000001` | 12-9 | x | 0510 | 031 | I | | 20 |
| 31 | `010000001000` | 11-6 | x | 01060 | 046 | O | | 21 |
| 32 | `010000000100` | 11-7 | x | 01270 | 047 | P | | 22 |
| 33 | `000000100010` | 4-8 | 0 | 0150 | 015 | ( | | 23 |
| 34 | `010000010010` | 11-5-8 | 0 | 0400 | 020 | = | | 24 |
| 35 | `000000010010` | 5-8 | 1 | 0150 | 015 | : | | 23 |
| 36 | `101000000000` | 12-0 | 1 | 0400 | 020 | + | | 24 |
| 37 | `100100000000` | 12-1 | x | 0610 | 021 | A | | 27 |
| 38 | `001010000000` | 0-2 | x | 01420 | 062 | S | | 28 |
| 39 | `100000100000` | 12-4 | x | 0640 | 024 | D | | 29 |
| 40 | `100000001000` | 12-6 | x | 0460 | 026 | F | | 30 |
| 41 | `100000000100` | 12-7 | x | 0670 | 027 | G | | 31 |
| 42 | `100000000010` | 12-8 | x | 0700 | 030 | H | | 32 |
| 43 | `010100000000` | 11-1 | x | 01210 | 041 | J | | 33 |
| 44 | `010010000000` | 11-2 | x | 01220 | 042 | K | | 34 |
| 45 | `010001000000` | 11-3 | x | 01030 | 043 | L | | 35 |
| 46 | `000000100010` | 4-8 | 1 | 01030 | 043 | \| | | 35 |
| 47 | `100000100010` | 12-4-8 | 0 | 01600 | 060 | ; | | 36 |
| 48 | `010001000010` | 11-3-8 | 0 | 01410 | 061 | ) | | 37 |
| 49 | `001100000000` | 0-1 | 1 | 01410 | 061 | / | | 37 |
| 50 | `001000000010` | 0-8 | x | 01500 | 070 | Y | | 39 |
| 51 | `001000000100` | 0-7 | x | 01470 | 067 | X | | 40 |
| 52 | `100001000000` | 12-3 | x | 0430 | 023 | C | | 41 |
| 53 | `001000010000` | 0-5 | x | 01650 | 065 | V | | 42 |
| 54 | `100010000000` | 12-2 | x | 0620 | 022 | B | | 43 |
| 55 | `010000010000` | 11-5 | x | 01050 | 045 | N | | 44 |
| 56 | `010000100000` | 11-4 | x | 01240 | 044 | M | | 45 |
| 57 | `010000000110` | 11-7-8 | 0 | 01530 | 073 | ? | | 46 |
| 58 | `001001000010` | 0-3-8 | 1 | 01530 | 073 | , | | 46 |
| 59 | `100000010010` | 12-5-8 | 0 | 0730 | 033 | ! | | 47 |
| 60 | `000001000010` | 3-8 †† | 1 | 0730 | 033 | . | | 47 |
| 61 | `000010000010` | 2-8 | x | 0320 | 012 | (Leer) | Leer | 49 |
| 62 | `011000000000` | 11-0 | 1 | 01000 | 040 | - | | 48 |
| 63 | `001000010010` | 0-5-8 | 0 | 01000 | 040 | @ | Dreieck | 48 |

### 2.4 Bezug zum Bedienungspult und offene Punkte

- **Pult-Tastatur** (soll später in der Datei "C8205-Interpreter-Bedienpult_mit_Schaltern.md" stehen): Beim Anschlagen einer
 Eingabetaste wird die dem Zeichen zugeordnete Eingabeverschlüsselung gemäß dem
 FS- bzw. R 300-Kode disjunktiv mit dem Inhalt des Adressenregisters verknüpft
 (Bedienungsanleitung 2.2.2). **Offen:** Welche Spalte von Tabelle 2 ist diese
 Verschlüsselung — die 12-Bit-Ausgabe-Adresse (gleiche Breite wie AR) oder die
 Eingabe-Adresse?
- **Pult-Zeichentasten** (0–9, +, −, „,", „.", „:", B, D, ZR, WM, IS, IB):
 0–9, +, −, „,", „.", „:", B und D haben eine Zeile in Tabelle 2; ZR entspricht
 der Zeile „Leer". **Bedeutung der Abkürzungen — geklärt:**
 ZR = Zwischenraum (= Leerzeichen, s. o.); WM = Wortmarke; IS = Irrung Satz
 (entspricht der bereits erfassten Zeile „Irrung Satz", Tabelle 1 Nr. 51);
 IB = Irrung Block. **Weiterhin offen:** Für „Wortmarke" (WM) und „Irrung
 Block" (IB) gibt es bislang KEINE Zeile in Tabelle 1 oder Tabelle 2 — anders
 als bei „Irrung Satz" (IS) ist noch unklar, ob es sich um eigene, bisher
 nicht erfasste Lochstreifen-Zeichen handelt oder um andere Bezeichnungen für
 bereits vorhandene Zeilen (z. B. „Irrung Zeichen"/„Transport"). Original:
 IB und WM sind im Fernschreibkode (FS/CCITT-2) wirkungslos — s. Abschnitt 3.
- **Schreibwerk:** R 300 ist der einzige verdrahtete Kode (soll später in der Datei "C8205-Interpreter-Bedienpult_mit_Schaltern.md" stehen).
- **FS-Kode (CCITT-2):** nicht eingegangen, noch nicht erfasst.

### 2.5 Abgleich mit der Lochkarten-Grafik

*Die Grafik zeigt eine Musterlochkarte **eines anderen Rechners** mit 80 Spaltenplätzen; die Zeilen der Karte
sind (von oben) 12, 11, 0, 1 … 9, gelochte Stellen sind schwarze Blöcke. Ausgelesen
wurde die Lochung jeder Spalte maschinell (Muster in der Reihenfolge 12, 11, 0,
1 … 9 wie in 2.1); die Zuordnung der Zeichen folgt dem Aufdruck über den
Spalten und dem Abgleich mit Tabelle 1. Alle Werte **abgeleitet**, nicht
eigens bestätigt. Die Karte ist nur eine Vergleichsquelle ("minimale
Differenzen bei darstellbaren Sonderzeichen").*

**Ausgelesene Karte (64 belegte Spalten; Spaltenplatz 1–80, dazwischen leer):**

- **Ziffern** (Plätze 1–10): „0" bis „9" jeweils nur die eigene Ziffernzeile
 (0 → Zeile 0, 1 → Zeile 1, …, 9 → Zeile 9).
- **A–I** (Plätze 13–21): 12-1 … 12-9. **J–R** (Plätze 24–32): 11-1 … 11-9.
 **S–Z** (Plätze 35–42): 0-2 … 0-9.
- **Sonderzeichen** (Plätze 45–80):

| Platz | Zeichen (Aufdruck / Zuordnung) | Lochbild (12 Bit) | Zeilen |
|---|---|---|---|
| 45 | # | `000001000010` | 3-8 |
| 46 | ( | `000000100010` | 4-8 |
| 47 | : | `000000010010` | 5-8 |
| 48 | ▼ (Aufdruck) | `000000001010` | 6-8 |
| 49 | ] | `000000000110` | 7-8 |
| 52 | + | `101000000000` | 12-0 |
| 53 | . | `100001000010` | 12-3-8 |
| 54 | ; | `100000100010` | 12-4-8 |
| 55 | ! | `100000010010` | 12-5-8 |
| 56 | ▼ (Aufdruck) | `100000001010` | 12-6-8 |
| 57 | " | `100000000110` | 12-7-8 |
| 60 | - | `011000000000` | 11-0 |
| 61 | ) | `010001000010` | 11-3-8 |
| 62 | * | `010000100010` | 11-4-8 |
| 63 | = | `010000010010` | 11-5-8 |
| 64 | < (Aufdruck unklar) | `010000001010` | 11-6-8 |
| 65 | ? | `010000000110` | 11-7-8 |
| 68 | ' | `111000000000` | 12-11-0 |
| 69 | / | `001100000000` | 0-1 |
| 70 | , | `001001000010` | 0-3-8 |
| 71 | % | `001000100010` | 0-4-8 |
| 72 | △ | `001000010010` | 0-5-8 |
| 73 | > (Aufdruck unklar) | `001000001010` | 0-6-8 |
| 74 | [ | `001000000110` | 0-7-8 |
| 77 | ¤ (Leer) | `000010000010` | 2-8 |
| 78 | ~ | `100010000010` | 12-2-8 |
| 79 | ≈ | `010010000010` | 11-2-8 |
| 80 | ≋ | `001010000010` | 0-2-8 |

**Ergebnis des Abgleichs:**

- **Tabelle 2 (Vorlage, vor der Angleichung in 2.2/2.3):** 60 von 63 Zeilen
 stimmten mit der Karte überein. Abweichend waren dieselben drei Zeilen wie
 in 2.2: „[" (Vorlage: 0-7, Karte: 0-7-8), „R" (Vorlage: 11-7, Karte: 11-9),
 „." (Vorlage: 2-8, Karte: 12-3-8).
- **Tabelle 1 (korrigierte Spalten):** stimmt mit der Karte in allen Zeichen
 überein, außer bei „.": Tabelle 1 hat 3-8 (= Lochbild von „#", durch die
 Lage unterschieden), die Karte hat 12-3-8.
- **Bewertung — geklärt:** Für „[" und „R" stützt die
 Karte die Werte von Tabelle 1 (0-7-8 bzw. 11-9), an die Tabelle 2
 entsprechend angeglichen wurde (2.2/2.3, ††). Bei „." ist die Karte
 (12-3-8) für den R 300 nicht maßgeblich, da sie zu einem anderen Rechner
 gehört; Tabelle 2 wurde stattdessen an Tabelle 1 (3-8) angeglichen.
- **Unterschiede zwischen Karte und Tabellen bei Sonderzeichen — geklärt
 (20.09.2026: in Ordnung, minimale Differenzen bei darstellbaren
 Sonderzeichen):** Die Karte hat zwei Spalten mit dem Aufdruck „▼" (Platz 48:
 6-8, Platz 56: 12-6-8) ohne Gegenstück in Tabelle 1 und 2. Sie hat keine Zeichen
 für Tabulator, Um. KB, Um. GB, SatzMarke/WRZL, Irrung Zeichen, Irrung Satz und
 Transport (kein Lochkartenkode, vgl. 2.2) und keine Kleinbuchstaben (Lage x wie in
 Tabelle 2).

## 3 FS-Kode (CCITT-2)

*Quelle der Quelle: Grafik „CCITT 2-Kode" ( am 20.09.2026 hochgeladen).
Der FS-Kode (Fernschreibkode) ist neben Tabelle 1 (Lochstreifenkode) und
Tabelle 2 (R 300-Lochkartenkode) der dritte an der Pult-Tastatur wählbare
Kode (soll später in der Datei "C8205-Interpreter-Bedienpult_mit_Schaltern.md" stehen: Taste T, „Kode der Pult-Tastatur: R 300 bzw.
CCITT-2"; A7 Punkt 1).*

### 3.1 Spalten und Bedeutung

| Spalte (Reihenfolge der Vorlage) | Bedeutung |
|---|---|
| Zeichen BU | Zeichen in der Buchstaben-Ebene ("Buchstabenumschaltung") |
| Zeichen ZI | Zeichen in der Ziffern-Ebene ("Ziffernumschaltung") |
| Adresse | interne Kodenummer/Adresse des Rechners für dieses Zeichen (oktal, 3 Stellen + beliebige/ignorierte 4. Stelle „x" — Format wie „Ausgabe-Adresse C8205 oktal" in Tabelle 1, s. 1.1) |
| Kanal 54.321 | physisches 5-Kanal-Punktmuster des Fernschreiblochstreifens (Kanäle 5, 4, 3, 2, 1); analog zu den Lochspuren in Tabelle 1 |

**BU/ZI als Abkürzungen:** BU = Buchstaben(-umschaltung),
ZI = Ziffern(-umschaltung) — dieselbe Bedeutung wie die gleichnamigen
Sonderzeilen am Tabellenende (s. 3.2).

### 3.2 Die Tabelle

*Lesehilfe: "—" = im Original leer (kein Zeichen in dieser Ebene). Die
fünf Sonderzeilen am Ende (WR, ZV, BU, ZI, ZR) haben kein eigenes
Buchstaben-/Ziffern-Zeichen, sondern sind Steuerfunktionen — daher nur
eine Bezeichnung, unter der ZI-Spalte eingerückt wie in der Vorlage. Das
Punktmuster der Spalte „Kanal 54.321" ist in der Vorlage vorhanden, wird
hier aber (noch) nicht bitgenau je Zeile wiedergegeben (3.3).*

| Nr. | Zeichen BU | Zeichen ZI | Adresse |
|---|---|---|---|
| 1 | (—) | (—) | 000x |
| 2 | A | − | 030x |
| 3 | B | ? | 023x |
| 4 | C | : | 016x |
| 5 | D | (—) | 022x |
| 6 | E | 3 | 020x |
| 7 | F | (—) | 026x |
| 8 | G | (—) | 013x |
| 9 | H | (—) | 005x |
| 10 | I | 8 | 014x |
| 11 | J | (—) | 032x |
| 12 | K | ( | 036x |
| 13 | L | ) | 011x |
| 14 | M | . | 007x |
| 15 | N | , | 006x |
| 16 | O | 9 | 003x |
| 17 | P | 0 | 015x |
| 18 | Q | 1 | 035x |
| 19 | R | 4 | 012x |
| 20 | S | ' | 024x |
| 21 | T | 5 | 001x |
| 22 | U | 7 | 034x |
| 23 | V | = | 017x |
| 24 | W | 2 | 031x |
| 25 | X | / | 027x |
| 26 | Y | 6 | 025x |
| 27 | Z | + | 021x |
| 28 | — (Steuerfunktion) | WR | 002x |
| 29 | — (Steuerfunktion) | ZV | 010x |
| 30 | — (Steuerfunktion) | BU | 037x |
| 31 | — (Steuerfunktion) | ZI | 033x |
| 32 | — (Steuerfunktion) | ZR | 004x |

*Alle Zeichen/Adressen:. Die
Zeilennummer „Nr." ist nur Referenz dieses Dokuments, nicht Teil der
Vorlage.*

### 3.3 Bezug zu Tabelle 1/2 und offene Punkte

**Bedeutung der Sonderzeilen — geklärt:**

| Kürzel | Bedeutung |
|---|---|
| ZR | Zwischenraum (= Leerzeichen) |
| WM | Wortmarke *(kommt in dieser FS-Tabelle nicht als eigene Zeile vor — s. u.)* |
| IS | Irrung Satz |
| IB | Irrung Block |
| WR | Wagenrücklauf (Carriage Return) |
| ZV | Zeilenvorschub (Line Feed) |

**Bezug zur künftigen Datei "C8205-Interpreter-Bedienpult_mit_Schaltern.md" (Bedeutung von B, D, ZR, WM, IS, IB):**
Mit obiger Klärung sind ZR, WM, IS, IB bedeutungsmäßig geklärt. **Weiterhin
offen:** Bedeutung der Pult-Tasten B und D (kommen weder in Tabelle 1/2
noch — als Sonderzeichen — in dieser FS-Tabelle vor; ggf. eigene, hier noch
nicht erfasste Zeichen).

**WM ("Wortmarke") — jetzt geklärt: identisch mit Tabulator (TAB).**
Laut Autor ist WM identisch mit dem Code für TAB: Eingabe-Adresse **075**
(oktal, Quellnotation "0075"), Sprung-Umstellung = **ja** — das entspricht
exakt der bereits vorhandenen Zeile "Tabulator" (Tabelle 1, Nr. 12,
Eingabe Adresse 75, Sprung-Umstellung ja, Ausgabe-Adresse 155x). Eine
eigene Tabellenzeile für WM ist damit nicht nötig; WM verweist auf Nr. 12.
Diese Klärung ersetzt die frühere (jetzt widerlegte) Bedienpult-Angabe
"WM identisch mit dem Code für '.'".

**IB ("Irrung Block") — Eingabe-Adresse geklärt:** Laut vom Autor
nachgereichtem Original-Tabellenausschnitt hat IB die Eingabe-Adresse
**036 (oktal, Quellnotation "0036")**; die Spalte Sprung-Umstellung ist
dabei mit "\*" markiert = **ja** (Umstellung auf Sprung, analog zu den in
1.5 mit "ja" geführten Zeilen von Tabelle 1). Damit ist dieser Punkt geklärt. Eine eigene
Ausgabe-Adresse für IB ist damit noch nicht belegt — falls benötigt, bleibt
das ein gesonderter, hier noch offener Punkt.

**IS ("Irrung Satz") — Bezug zu Tabelle 1:** Tabelle 1 (Abschnitt 1.4) hat
bereits eine Zeile "Irrung Satz" (Nr. 51, Eingabe-Adresse 16, Ausgabe-Adresse
016x). Ob diese Zeile mit dem hier über IS erreichten FS-Zeichen identisch
ist (naheliegend, aber nicht ausdrücklich für den FS-Kode
bestätigt), bleibt **offen**.

**Punktmuster "Kanal 54.321":** Aus der Vorlage noch nicht bitgenau je
Zeile in eine Tabellenspalte übertragen — anders als bei Tabelle 1
(1.3, dort inkl. Konsistenzprüfung gegen die Ausgabe-Adresse) fehlt hier
noch der maschinelle Abgleich Punktmuster ↔ Adresse. **offen.**

## 4 Gemeinsame Bezüge der Tabellen

*Größtenteils noch nicht erfasst.* Es gibt neben Tabelle 1 den
R 300-Kode (Tabelle 2, Abschnitt 2) und dem jetzt erfassten FS-Kode
(Tabelle 3, Abschnitt 3) sicher auch weitere gemeinsame Bezüge in der
Beschreibung; diese werden hier gesammelt, sobald sie auftreten. Verwandte
Zusammenhänge (Zeichenlage Klbuch/Gbuch, Umschaltzeichen) stehen zunächst im
Unterdokument Lochstreifenleser, A4.

---

