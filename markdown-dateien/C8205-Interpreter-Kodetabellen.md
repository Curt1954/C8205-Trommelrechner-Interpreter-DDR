# Kodetabellen

Version: 0.95-001

Die Zeichenkode-Tabellen des C 8205: R 300-Lochstreifenkode (Tabelle 1) und externer R 300-Code (Tabelle 2).

## Inhaltsverzeichnis

- [1 Tabelle 1 — Lochstreifenkode (R 300)](#1-tabelle-1--lochstreifenkode-r-300)
 - [1.1 Spalten und Bedeutung](#11-spalten-und-bedeutung)
 - [1.2 Verwendung durch Leser und Stanzer](#12-verwendung-durch-leser-und-stanzer)
 - [1.3 Lochbilder und Konsistenzprüfung](#13-lochbilder-und-konsistenzprüfung)
 - [1.4 Die Tabelle](#14-die-tabelle)
 - [1.5 Sprung-Umstellung](#15-sprung-umstellung)
 - [1.6 Sonderzeilen und Zeichen ohne ASCII-Wert](#16-sonderzeilen-und-zeichen-ohne-ascii-wert)
 - [1.7 Auffälligkeiten](#17-auffälligkeiten)
 - [1.8 Verprobung mit dem kleinen Eingabeprogramm (KEP)](#18-verprobung-mit-dem-kleinen-eingabeprogramm-kep)
- [2 Tabelle 2 — Externer R 300-Code für C 8205](#2-tabelle-2--externer-r-300-code-für-c-8205)
 - [2.1 Geltungsbereich und Spalten](#21-geltungsbereich-und-spalten)
 - [2.2 Die Tabelle](#22-die-tabelle)
 - [2.3 Abgleich mit Tabelle 1](#23-abgleich-mit-tabelle-1)
- [3 Bezüge zu anderen Dokumenten](#3-bezüge-zu-anderen-dokumenten)

---

## 1 Tabelle 1 — Lochstreifenkode (R 300)

*Quelle: Originaltabelle „Tabelle 1" (Kodetabelle_1.pdf). Die Tabelle betrifft Lochstreifenleser UND
Lochstreifenstanzer sowie die Befehlsdefinition (Spalte
"Sprung-Umstellung").*

### 1.1 Spalten und Bedeutung

**Spalten der Original-Tabelle (in Originalreihenfolge):** Klbuch —
BCD (zu Klbuch) — Gbuch — BCD (zu Gbuch) — Lochspuren **w v u p 8 Tr 4 2 1** — Eingabe Adresse — Sprung-Umstellung — Ausgabe-Adresse C8205 oktal
— Ascii GB — Ascii KB.

**Bedeutung der Spalten:**

| Spalte | Bedeutung |
|---|---|
| Klbuch / Gbuch | Klbuch = Kleinbuchstaben, Gbuch = Großbuchstaben (Zeichenlagen). Im Rechner haben Groß- und Kleinbuchstaben keinen unterschiedlichen Kode, sondern werden durch einen Zusatzkode unterschieden. Wie ein gelesenes Zeichen intern im Speicher kodiert wird, hängt davon ab, ob zeicheneingabe-übergreifend VORHER ein Zeichen Klbuch oder Gbuch gelesen wurde |
| WRZL / ZWR | Gbuch-Bezeichnungen: WRZL = Wagenrücklauf mit Zeilenschaltung (entspricht dem heutigen CR, bei SatzMarke); ZWR = Zwischenraum (Leertaste). Die Bezeichnung ZWR steht so im KEP (Programmieranleitung 5.18) und in Anlage 1 |
| BCD | Lochkartenkode (Zonen-/Ziffernlochungen, z. B. 11^6^8) |
| Eingabe Adresse | interne Kodenummer des Rechners, eigentlich ein Alias dafür (oktal) |
| Sprung-Umstellung | technische Fähigkeit des Rechenwerks: bei Lochstreifeneingabe wird der Eingabewert in eine gültige Darstellung im Rechnerspeicher umgerechnet. Wird bei der **Definition der Befehle** gebraucht, nicht für die Definition des Lesers an sich. Wirkung laut KEP-Verprobung (1.8): Bei Umstellung wird der Eingabebefehl wie ein unbedingter Sprung auf die Zelle (Adreßteil ∨ Eingabe Adresse) ausgeführt |
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
- **Schreibwerk (Ausgabe):** Hier wertet die Schreibmaschinenverdrahtung nur sechs der acht Bits der Ausgabe-Adresse aus,
  nämlich die Spuren v u 8 4 2 1 (z₁₄, z₁₅, z₁₇–z₂₀); w (z₁₃) und p (z₁₆) bleiben unberücksichtigt (Originaldokumentation 4.3.2.5).
  Das Zeichen ergibt sich daher wie bei der Eingabe aus diesen sechs Bits (die Spalte "Eingabe Adresse" ist in allen Zeilen
  mit Eingabeadresse eindeutig).

### 1.3 Lochbilder und Konsistenzprüfung

**Lochbilder:** Die gestanzten Spuren jeder Zeile sind
der Quelle entnommen (Punkte maschinell ausgelesen und den Spalten
w v u p 8 Tr 4 2 1 zugeordnet, alle 55 Zeilen; ZV, BM und WR nach den Ergänzungen). Sie stimmen in allen 55
Zeilen exakt mit dem Bitmuster der Spalte "Ausgabe-Adresse" überein
(dort als Oktalzahl, letztes "x" s. 1.7). Daraus folgt die Regel:

| Spur | 1 | 2 | 4 | 8 | p | u | v | w |
|---|---|---|---|---|---|---|---|---|
| Bitwert in Ausgabe-Adresse | 1 | 2 | 4 | 10₈ | 20₈ | 40₈ | 100₈ | 200₈ |

Die Spalte **Tr** kommt in der Ausgabe-Adresse nicht vor und ist in
keiner Zeile mit einem Punkt besetzt (auch nicht bei "Transport"). Sie ist die Transportlochung und trägt
keine Information (s. Lochstreifenleser, A4).

**Konsistenzprüfung (maschinell, alle 55 Zeilen):**
- In 54 von 55 Zeilen ist die Anzahl der Lochungen **ungerade** (Parität
 ungerade; **p** ergänzt die Datenspuren zu ungerader Zahl). Ausnahme:
 "Irrung Zeichen" (8 Lochungen, gerade); es wird bei der Eingabe von der Paritätsprüfung ausgeschlossen
 und übersprungen (s. 1.6/1.7).
- Die Spalte "Eingabe Adresse" ergibt sich in 54 Zeilen aus den Spuren 1,
 2, 4, 8, u, v (u = 20₈, v = 40₈ im 6-Bit-Wert; p und w bleiben
 unberücksichtigt). Ausnahme: "Irrung Zeichen" — Tabelle 1 nennt hier 56 (Zeile 50), die Regel ergäbe 77.
 Beim Lesen vom Lochband wird das Zeichen übersprungen und seine Eingabeadresse nicht ins Adreßregister übernommen (s. 1.6/1.7).
- Die Werte der Spalte "Eingabe Adresse" sind eindeutig mit **einer Ausnahme**: "ZV" (Zeile 52) und "BM" (Zeile 53) haben beide die Eingabeadresse 72.
 Sie unterscheiden sich im Lochbild (ZV: Spur p, BM: Spur w) und in der Sprung-Umstellung (ZV nein, BM ja); die Eingabeadresse allein bestimmt
 bei diesen beiden Zeichen also nicht, ob ein Eingabebefehl springt. Alle Werte der Spalte "Ausgabe-Adresse" sind eindeutig.
- Ascii-Werte stimmen für alle Einzelzeichen mit dem Zeichen der jeweiligen
 Spalte überein; Ausnahme:
 Zeile 48 (Wert 465, Kode aus der Zeit vor ASCII).

### 1.4 Die Tabelle

*Lesehilfe: Spalte "Lochbild" = gestanzte Spuren der Zeile (Reihenfolge
w v u p 8 4 2 1), "—" = im
Original leer. Die Spalten "Eingabe-Adresse" und "Ausgabe-Adresse" sind
oktal (letzteres mit dem "x" der Quelle = beliebige, ignorierte Stelle).
"Ascii GB/KB" sind dezimal. "(Relikt)" = Zusatz dieses
Dokuments für Zeile 54, s. 1.6.*

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
| 16 | r | — | R | 11^9 | v 8 1 | 51 | nein | 111x | 82 | 114 |
| 17 | t | — | T | 0^3 | v u p 2 1 | 63 | nein | 163x | 84 | 116 |
| 18 | z | — | Z | 0^9 | v u p 8 1 | 71 | nein | 171x | 90 | 122 |
| 19 | u | — | U | 0^4 | v u 4 | 64 | nein | 144x | 85 | 117 |
| 20 | i | — | I | 12^9 | u 8 1 | 31 | nein | 051x | 73 | 105 |
| 21 | o | — | O | 11^6 | v 4 2 | 46 | nein | 106x | 79 | 111 |
| 22 | p | — | P | 11^7 | v p 4 2 1 | 47 | nein | 127x | 80 | 112 |
| 23 | : | 5^8 | ( | 4^8 | 8 4 1 | 15 | ja | 015x | 40 | 58 |
| 24 | + | 12^0 | = | 11^5^8 | u | 20 | nein | 040x | 61 | 43 |
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
| 36 | \` | — | ; | 12^4^8 | v u p | 60 | ja | 160x | 59 | 96 |
| 37 | / | 0^1 | ) | 11^3^8 | v u 1 | 61 | nein | 141x | 41 | 47 |
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
| 49 | Leertaste | 8^2 | ZWR | — | p 8 2 | 12 | ja | 032x | 32 | 32 |
| 50 | Irrung Zeichen | — | Irrung Zeichen | — | w v u p 8 4 2 1 | 56 | nein | 377x | 0 | 0 |
| 51 | Irrung Satz | — | Irrung Satz | — | 8 4 2 | 16 | ja | 016x | 0 | 0 |
| 52 | ZV | — | ZV | — | v u p 8 2 | 72 | nein | 172x | 0 | 0 |
| 53 | BM | — | BM | — | w v u 8 2 | 72 | ja | 352x | 0 | 0 |
| 54 | Transport (Relikt) | — | Transport (Relikt) | — | v u p 8 4 2 1 | 77 | nein | 177x | 0 | 0 |
| 55 | WR | — | WR | — | v 8 2 | 52 | nein | 112x | 13 | 13 |

*(Zeilennummer "Nr." nur zur Referenz in diesem Dokument, nicht Teil der
Original-Tabelle. Die Zeilen 52 und 53 (ZV, BM) hat der Projektinhaber am 11.10.2026 ergänzt; die Zeile "Transport" war bis dahin Zeile 52 und ist jetzt Zeile 54. Die Zeile 55 (WR, Wagenrücklauf ohne Zeilenschaltung; Klbuch und Gbuch gleich) wurde am 12.10.2026 vom Projektinhaber ergänzt (Eingabe Adresse 52 = 101010 mit Prüfbit p an Stelle 4 von links: 1001010 = 112 oktal; Sprung-Umstellung nein; Ascii-Wert 13 noch zu bestätigen).
Abkürzungen: ZV Zeilenvorschub, BM Blockmarke, WRZL Wagenrücklauf und Zeilenschaltung (entspricht CR), ZR Zwischenraum (auch Leertaste).)*

### 1.5 Sprung-Umstellung

**Zeilen mit Sprung-Umstellung = ja (12):** Tabulator, ":", Um. KB, Um. GB,
Zeichenpaar zu Eingabe Adresse 60 (Zeile 36), SatzMarke, ",", ".", "-", Irrung Satz, Leertaste/ZWR, BM. (ZV hat dieselbe Eingabeadresse wie BM, aber keine Sprung-Umstellung.)

**Korrekturen 12.10.2026 (Projektinhaber):** Eingabe Adresse 60 (Zeile 36) hat Sprung-Umstellung, Eingabe Adresse 61 (Zeile 37) hat keine; vorher stand es umgekehrt. Eingabe Adresse 20 ("+" / "=", Zeile 24) hat keine Sprung-Umstellung; vorher stand "ja". Bestätigt: Eingabe Adresse 12 und 15 haben Sprung-Umstellung.

**Herkunft:** Die Spalte ist der Originaltabelle „Tabelle 1" entnommen.

Die Spalte "Sprung-Umstellung" ist hier nur als Eigenschaft des Zeichens
wiedergegeben; ihre Bedeutung (s. 1.1) gehört zur Befehlsdefinition und wird
dort beschrieben.

### 1.6 Sonderzeilen und Zeichen ohne ASCII-Wert

- **Zeichen ohne ASCII-Wert (Ascii = 0):** "≈", "≋", "Um. KB", "Um. GB",
 "Irrung Zeichen", "Irrung Satz", "ZV", "BM", "Transport". Das sind Zeichen, die die
 ASCII-Definition nicht kennt, die aber in der Vorläufer-Rechentechnik
 jener Zeit real existierten. **Ausgabe über den Stanzer:** Alle
 Zeichen der Spalte "Ausgabe-Adresse C8205 oktal" sind ausgebbar, alle
 anderen nicht. **Ausgabe über das Schreibwerk:** Es zählen nur die sechs Bits v u 8 4 2 1 (s. 1.2); darstellbar sind nur Zeichen,
 die auf der Schreibwerktastatur vorhanden sind.
- **"Irrung Zeichen" und "Irrung Satz":** stammen aus der Zeit der
 Lochstreifenverarbeitung ohne Rechner. Ein einmal gestanztes Zeichen
 lässt sich nicht rückgängig machen. War das Stanzen falsch, wurde
 "Irrung Zeichen" nachgesetzt, um die vorhergehende Lochung unschädlich
 zu machen; analog "Irrung Satz". Die Daten auf Lochstreifen waren
 satzweise organisiert (logische Einheit, nichts Leserspezifisches: der
 Leser liest immer nur ein Zeichen). Mit "Irrung Satz" konnten viele
 Lochungen auf einmal als falsch gekennzeichnet werden.
- **"Irrung Zeichen" beim Lesen (Originaldokumentation 4.3.2.2, Abb. 16):** Alle 8
  Spuren gelocht, also gerade Anzahl Bits und damit kein gültiges Zeichen — Absicht: So erkennt der
  Leser ohne Lesen und Interpretieren, dass es kein Zeichen ist. Tabelle 1 nennt als Eingabe Adresse 56.
  Bei der Lochbandeingabe unterliegt es einer
  Sonderbehandlung: Es wird von der Paritätsprüfung ausgeschlossen, **nicht** ins Adreßregister
  übernommen und übersprungen; die Eingabe geht mit dem nächsten Zeichen des Lochbands weiter. Es
  entsteht also **kein** Fehler: weder FE noch Stopp. Eine Rücknahme des davor gelesenen Zeichens
  beschreibt das Original nicht. Bei Tastatur- und Schreibwerkeingabe entfällt dieses Sonderzeichen.
  **Der Rechner benutzt keine Irrung-Zeichen**: Sie werden gebraucht, wenn der Mensch Daten auf
  Lochstreifen erfasst, denn irren tut nur der Mensch. Der Rechner könnte die Zeichen ausgeben, wenn
  das im Programm so programmiert ist; eine Automatik gibt es nicht. Ein Gerätefehler (FE leuchtet,
  der Rechner stoppt) liegt nur bei einer anderen Zeile mit gerader Lochzahl vor
  (Lochstreifenleser A0 und A4).
- **"ZV" und "BM" (Zeilen 52 und 53):** Zeilenvorschub und Blockmarke (Ergänzung des Projektinhabers vom 11.10.2026). Beide haben die Eingabeadresse 72 und unterscheiden sich
  im Lochbild (ZV v u p 8 2, BM w v u 8 2) und in der Sprung-Umstellung (ZV nein, BM ja). Ein Eingabebefehl springt also bei BM, bei ZV nicht; ein ZV wirkt wie jedes
  Zeichen ohne Sprung-Umstellung (die Tabellenzelle wird als Datum gelesen). Nach den "Bemerkungen zur Eingabe" (BIS-2.2.1a) ist ein ZV zwischen zwei Zahlen im 8-Kanal-Code
  anschließend mit ZR zu löschen. BM ist im R 300-Code Schlusszeichen (BIS-2.2.9). Das Schreibwerk gibt weder ZV noch BM aus; der Stanzer gibt beide aus.
- **"Transport" (Zeile 54):** Relikt aus noch früheren Zeiten, nie
 benutzt. Der tatsächliche Transport heißt "Transport Vorspann" und hat
 keine Datenlochung, nur die kleine Transportlochung (Lochstreifenleser A4). Bei der Eingabe wird das
 Transportloch im Vorspann überlesen; ein Transportloch außerhalb des Vorspanns unterliegt dagegen der
 Paritätsprüfung (Originaldokumentation 4.3.2.2).

### 1.7 Auffälligkeiten

*Feststellungen.*

**Geklärt:**

1. **Zeile 48 ("-" / "△"):** Ascii GB = 465 ist kein Fehler, sondern ein
 Kode aus der Zeit vor ASCII (1967 real so dargestellt).
2. **"x"** hinter der Ausgabe-Adresse: beliebige Stelle, wird ignoriert.
3. **Ascii = 0:** Zeichen, die ASCII nicht kennt (1.6).
4. **"Irrung Zeichen":** gerade Parität ist Absicht; Tabelle 1 nennt als Eingabe Adresse 56
 (Zeile 50). Bei der Lochbandeingabe wird es von der Paritätsprüfung ausgeschlossen, nicht ins
 Adreßregister übernommen und übersprungen; es löst weder FE noch Stopp aus (1.6, Originaldokumentation 4.3.2.2, Abb. 16).
5. **Spur Tr:** Transportlochung ohne Information, daher in keiner
 Zeile besetzt (Lochstreifenleser A4).
6. **Zeile 54 "Transport":** Relikt, nie benutzt (1.6).

**Feststellung:**

7. **Spur w:** nur bei "SatzMarke", "Irrung Zeichen" und "BM" besetzt (alle
 anderen Zeilen benutzen höchstens 7 Spuren).

**Geklärt (Ergänzung 11.10.2026):**

8. **ZV und BM (Zeilen 52 und 53):** Beide Zeichen fehlten bis dahin in Tabelle 1. Der Projektinhaber hat sie ergänzt: gleiche Eingabeadresse 72, aber ZV ohne und BM mit
 Sprung-Umstellung (1.3, 1.6). Das Lochbild unterscheidet sie (ZV Spur p, BM Spur w). Im Minimalprogramm sind die Eingabetabellenzellen von 072 null: In der
 Kennzeicheneingabe führen beide Zeichen zum Sprung nach 0000 (BM springt, ZV liest eine 0 und fällt in die Fehlerprüfung); in der Adresseneingabe springt BM nach 0000,
 während ZV wie die Ziffer 0 zählt (anschließend mit ZR zu löschen, BIS-2.2.1a). In der Programmstück-Eingabe ist BM neben ":" Schlusszeichen.

### 1.8 Verprobung mit dem kleinen Eingabeprogramm (KEP)

*Quelle: Programmieranleitung 5.18 „Kleines Eingabeprogramm" mit Abb. 27; Befehlsliste (Einzelbefehlsübersicht).*

Das KEP liest im R 300-Code mit dem Eingabe-Halt (`0020 010`, Zelle 0030). Operationsteil 010 = B 0, A 1, Z 0 =
Eingabe-Halt 1. Art ohne Löschen, ohne Resultatbehandlung (Befehlsliste). Angesprochen wird die Zelle
**Adreßteil ∨ Eingabe Adresse** (Abb. 17: ODER in den sechs niedrigsten Bits). Das KEP lässt nur die Zeichen
0, 1, ":", "." und ZWR zu.

| Zeichen | Eingabe Adresse | Zelle (0020 ∨ Adr.) | Inhalt | Wirkung im KEP | Sprung-Umstellung muss | Tabelle 1 |
|---|---|---|---|---|---|---|
| 0 | 0000 | 0020 | 0000 0000 000 | Konstante „0" | nein | nein ✓ |
| 1 | 0001 | 0021 | 4000 0000 000 | Konstante „1" | nein | nein ✓ |
| ZWR | 0012 | 0032 | 0030 001 | unbedingter Sprung nach 0030, Löschen: ⟨Ac⟩ := 0 | **ja** | ja ✓ |
| : | 0015 | 0035 | 0016 000 | Sprung nach 0016 (Leitbefehl speichern) | ja | ja ✓ |
| . | 0033 | 0033 | 7723 000 | Sprung zum Leitbefehl 7723 | ja | ja ✓ |

**Begründung:** Zellen 0020/0021 enthalten Zahlen (Konstanten), die zu ⟨Ac⟩ addiert werden sollen (Abb. 27:
V(⟨Ac⟩ + 4000 0000 000)). Die Zellen 0032, 0033, 0035 enthalten Befehle, die ausgeführt werden müssen; als Zahl
addiert wäre `0030 001` sinnlos und die Eingabeschleife würde nicht erreicht.

**Gegenprobe der KEP-Befehle gegen die Befehlsliste (BAZ):** 0031 `0030 006` = Sprung, Z 6 = zyklische
Linksverschiebung ohne Löschen (V_zl) ✓; 0032/0017 `0030 001` = Sprung mit Löschen ✓; 0014 `7723 211` =
Festkomma-Addition mit Löschen ✓; 0015 `0025 210` = Festkomma-Addition ✓; 0016 `7723 240` = Transportbefehl ✓.
Alle stimmen mit den Kommentaren des Listings überein.

**Ergebnis:** Alle fünf Zeilen stimmen mit der Tabelle überein.

---

## 2 Tabelle 2 — Externer R 300-Code für C 8205

*Quelle: Originaltabelle "Externer R300-Code für C 8205" (Tabelle_2_externer_R300-Code.png), vom Projektinhaber am 12.10.2026
zur Aufnahme in die Kodetabellen vorgegeben.*

### 2.1 Geltungsbereich und Spalten

Tabelle 2 gibt den **externen R 300-Code** vollständig wieder, auch dort, wo der C 8205 das Zeichen nicht unterstützt. Sie enthält
Zeichen, die nur die Lochstreifentechnik der Org-Automaten auswerten kann; sie bleiben trotzdem in der Tabelle.
Was der C 8205 aus Tabelle 2 tatsächlich verarbeitet, steht in Tabelle 1 (Abschnitt 1).

**Spalten der Original-Tabelle (in Originalreihenfolge):** Lochung — Eingabeverschl. — S — Zeichen KB / GB — Ausgabeverschl.
(die Spalte L der Vorlage entfällt auf Vorgabe des Projektinhabers).

| Spalte | Bedeutung |
|---|---|
| Lochung | gestanzte Spuren der Zeile. Die Vorlage zeichnet die Spuren von links nach rechts in der Reihenfolge 1 2 4 Tr 8 p u v w; hier steht die Reihenfolge von Tabelle 1 (w v u p 8 4 2 1, die Spur Tr nie gelocht und nicht dargestellt, s. 1.3). Die Spuren sind dem Bild der Vorlage maschinell entnommen und stimmen in allen Zeilen mit der Ausgabeverschlüsselung überein |
| Eingabeverschl. | Eingabe Adresse (oktal, 4 Stellen), entspricht der Spalte "Eingabe Adresse" von Tabelle 1; sie ergibt sich aus den Spuren 1, 2, 4, 8, u, v (1.3) |
| Sprung-Umstellung | Kennzeichen S der Vorlage = Sprung-Umstellung, wie in Tabelle 1 (1.5): ja = in der Vorlage mit S gekennzeichnet, nein = ohne S. Bei Eingabe 0077 ist das S der Vorlage laut Projektinhaber falsch; hier steht nein |
| Zeichen KB / GB | Zeichen in Kleinbuchstaben- und Großbuchstabenlage. Steht in der Vorlage ein Name mittig über beide Spalten, gilt er für beide Lagen; er steht hier in der Spalte "Zeichen KB und GB" |
| Ausgabeverschl. | Ausgabe-Adresse (oktal, drei Stellen und das beliebige "x"), entspricht der Spalte "Ausgabe-Adresse" von Tabelle 1 |
| Tab. 1 Nr. | Zusatz dieses Dokuments: Nummer der Zeile in Tabelle 1 mit derselben Ausgabe-Adresse; "—" = Zeichen kommt in Tabelle 1 nicht vor |

### 2.2 Die Tabelle

*Lesehilfe: Spalte "Lochbild" = gestanzte Spuren (Reihenfolge w v u p 8 4 2 1). Die Zeilennummer "Nr." ist nur
eine Referenz dieses Dokuments und nicht Teil der Vorlage. Die Bezeichnungen sind unverändert aus der Vorlage übernommen
(ZR Zwischenraum, ZL Zeilenschaltung (= ZV in Tabelle 1), WR Wagenrücklauf ohne Zeilenschaltung, IS Irrung Satz, Sm SatzMarke, Bm Blockmarke).*

| Nr. | Lochbild | Eingabeverschl. | Sprung-Umstellung | KB | GB | Zeichen KB und GB | Ausgabeverschl. | Tab. 1 Nr. |
|---|---|---|---|---|---|---|---|---|
| 1 | p | 0000 | nein | 0 | # | — | 020x | 10 |
| 2 | 1 | 0001 | nein | 1 | < | — | 001x | 1 |
| 3 | 2 | 0002 | nein | 2 | " | — | 002x | 2 |
| 4 | p 2 1 | 0003 | nein | 3 | ≈ | — | 023x | 3 |
| 5 | 4 | 0004 | nein | 4 | [ | — | 004x | 4 |
| 6 | p 4 1 | 0005 | nein | 5 | > | — | 025x | 5 |
| 7 | p 4 2 | 0006 | nein | 6 | ' | — | 026x | 6 |
| 8 | 4 2 1 | 0007 | nein | 7 | ≋ | — | 007x | 7 |
| 9 | 8 | 0010 | nein | 8 | ~ | — | 010x | 8 |
| 10 | p 8 1 | 0011 | nein | 9 | ] | — | 031x | 9 |
| 11 | p 8 2 | 0012 | ja | — | — | ZR | 032x | 49 |
| 12 | 8 2 1 | 0013 | nein | — | — | Leserstopp | 013x | — |
| 13 | p 8 4 | 0014 | nein | $ | £ | NS | 034x | — |
| 14 | 8 4 1 | 0015 | ja | : | ( | — | 015x | 23 |
| 15 | 8 4 2 | 0016 | ja | — | — | IS | 016x | 51 |
| 16 | p 8 4 2 1 | 0017 | nein | — | — | ⇑ | 037x | — |
| 17 | u | 0020 | nein | + | = | — | 040x | 24 |
| 18 | u p 1 | 0021 | nein | a | A | — | 061x | 27 |
| 19 | u p 2 | 0022 | nein | b | B | — | 062x | 43 |
| 20 | u 2 1 | 0023 | nein | c | C | — | 043x | 41 |
| 21 | u p 4 | 0024 | nein | d | D | — | 064x | 29 |
| 22 | u 4 1 | 0025 | nein | e | E | — | 045x | 15 |
| 23 | u 4 2 | 0026 | nein | f | F | — | 046x | 30 |
| 24 | u p 4 2 1 | 0027 | nein | g | G | — | 067x | 31 |
| 25 | u p 8 | 0030 | nein | h | H | — | 070x | 32 |
| 26 | u 8 1 | 0031 | nein | i | I | — | 051x | 20 |
| 27 | u 8 2 | 0032 | ja | — | — | (WRZL) | 052x | — |
| 28 | u p 8 2 1 | 0033 | ja | . | ! | — | 073x | 47 |
| 29 | u 8 4 | 0034 | nein | — | — | WS | 054x | — |
| 30 | u p 8 4 1 | 0035 | ja | — | — | SPE | 075x | — |
| 31 | u p 8 4 2 | 0036 | ja | — | — | IB | 076x | — |
| 32 | u 8 4 2 1 | 0037 | ja | — | — | GB | 057x | 26 |
| 33 | v | 0040 | ja | - | △ | — | 100x | 48 |
| 34 | v p 1 | 0041 | nein | j | J | — | 121x | 33 |
| 35 | v p 2 | 0042 | nein | k | K | — | 122x | 34 |
| 36 | v 2 1 | 0043 | nein | l | L | — | 103x | 35 |
| 37 | v p 4 | 0044 | nein | m | M | — | 124x | 45 |
| 38 | v 4 1 | 0045 | nein | n | N | — | 105x | 44 |
| 39 | v 4 2 | 0046 | nein | o | O | — | 106x | 21 |
| 40 | v p 4 2 1 | 0047 | nein | p | P | — | 127x | 22 |
| 41 | v p 8 | 0050 | nein | q | Q | — | 130x | 13 |
| 42 | v 8 1 | 0051 | nein | r | R | — | 111x | 16 |
| 43 | v 8 2 | 0052 | nein | — | — | WR | 112x | 55 |
| 44 | v p 8 2 1 | 0053 | ja | — | — | SP | 133x | — |
| 45 | v 8 4 | 0054 | nein | — | — | Lo 1 | 114x | — |
| 46 | v p 8 4 1 | 0055 | ja | — | — | Lo A | 135x | — |
| 47 | v p 8 4 2 | 0056 | nein | — | — | ⇓ | 136x | — |
| 48 | v 8 4 2 1 | 0057 | ja | — | — | KB | 117x | 25 |
| 49 | v u p | 0060 | ja | \` | ; | — | 160x | 36 |
| 50 | v u 1 | 0061 | nein | / | ) | — | 141x | 37 |
| 51 | v u 2 | 0062 | nein | s | S | — | 142x | 28 |
| 52 | v u p 2 1 | 0063 | nein | t | T | — | 163x | 17 |
| 53 | v u 4 | 0064 | nein | u | U | — | 144x | 19 |
| 54 | v u p 4 1 | 0065 | nein | v | V | — | 165x | 42 |
| 55 | v u p 4 2 | 0066 | nein | w | W | — | 166x | 14 |
| 56 | v u 4 2 1 | 0067 | nein | x | X | — | 147x | 40 |
| 57 | v u 8 | 0070 | nein | y | Y | — | 150x | 39 |
| 58 | v u p 8 1 | 0071 | nein | z | Z | — | 171x | 18 |
| 59 | v u p 8 2 | 0072 | nein | — | — | ZL | 172x | 52 |
| 60 | v u 8 2 1 | 0073 | ja | , | ? | — | 153x | 46 |
| 61 | v u p 8 4 | 0074 | nein | % | \* | — | 174x | 11 |
| 62 | v u 8 4 1 | 0075 | ja | — | — | Tab / WM | 155x | 12 |
| 63 | v u 8 4 2 | 0076 | nein | — | — | Lo 2 | 156x | — |
| 64 | v u p 8 4 2 1 | 0077 | nein | — | — | — | 177x | 54 |
| 65 | w u p 8 2 | 0032 | ja | — | — | WRZL / Sm | 272x | 38 |
| 66 | w v u 8 2 | 0072 | ja | — | — | Bm | 352x | 53 |
| 67 | w v u p 8 4 2 1 | — | nein | — | — | Irrung | 377x | 50 |

*(Die Zeichen "⇑" (Nr. 16) und "⇓" (Nr. 47) sind Pfeilsymbole der Vorlage. Die leere Zeile der Vorlage zwischen 0077 und der letzten Gruppe
ist nicht übernommen. Bei "Irrung" (Nr. 67) ist in der Vorlage keine Eingabeverschlüsselung angegeben.)*

### 2.3 Abgleich mit Tabelle 1

Alle 55 Zeilen von Tabelle 1 kommen in Tabelle 2 vor (Zuordnung über die Ausgabe-Adresse, Spalte "Tab. 1 Nr."). Tabelle 2 enthält darüber
hinaus 12 Zeichen, die Tabelle 1 nicht kennt (Spalte "Tab. 1 Nr." = "—").

**Übereinstimmung der in beiden Tabellen enthaltenen Zeichen:** Klbuch, Gbuch, Eingabe Adresse und Ausgabe-Adresse stimmen in allen Zeilen überein,
ebenso die Sprung-Umstellung. Die gestanzten Spuren stimmen in allen 67 Zeilen mit der Ausgabeverschlüsselung überein;
die Anzahl der Lochungen ist ungerade, Ausnahme "Irrung" (wie in Tabelle 1, 1.3).

| Zeichen | Tabelle 1 | Tabelle 2 |
|---|---|---|
| Irrung Zeichen | Eingabe Adresse 56 (bleibt so) | Eingabeverschl. "—" (keine Eingabeadresse); 0056 ist in Tabelle 2 "⇓" |

**Sprung-Umstellung:** Tabelle 1 und Tabelle 2 stimmen in allen 55 gemeinsamen Zeichen überein. Dafür hat der Projektinhaber am 12.10.2026
Tabelle 1 bei Eingabe 20 (jetzt nein), 60 (jetzt ja) und 61 (jetzt nein) korrigiert und in Tabelle 2 das S der Vorlage bei Eingabe 0077 verworfen
(Transport: nein). Eingabe 12 und 15 sind in beiden Tabellen Sprung (ja).

---

## 3 Bezüge zu anderen Dokumenten

Zusammenhänge zur Tabelle 1 (Zeichenlage Klbuch/Gbuch, Umschaltzeichen) stehen im
Dokument Lochstreifenleser, A4. Zum Eingabe-Halt (Operation 010/110) s. Befehlsliste; zur Verprobung der Spalte "Sprung-Umstellung" s. 1.8 (KEP).

