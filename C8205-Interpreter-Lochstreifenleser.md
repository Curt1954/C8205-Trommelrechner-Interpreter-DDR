# Lochstreifenleser

Hardwarebeschreibung des Lochstreifenlesers 303 am Rechner C 8205.

Die Zeichenkode-Tabellen (Zeichenkode des Lochbands) stehen in der Datei
"C8205-Interpreter-Kodetabellen.md", Abschnitt 1; dorthin wird an
den entsprechenden Stellen verwiesen. Die vollständige Kanaltabelle (K0–K3)
und die Bedienelemente sollen später in einer eigenen Datei zum Bedienpult
stehen; bis dahin steht hier nur, was zum Verständnis des Lesers nötig ist.


## Inhaltsverzeichnis

- [A0 Überblick](#a0-überblick)
- [A3 Geschwindigkeit](#a3-geschwindigkeit)
- [A4 Lochbandkode (Tabelle 1)](#a4-lochbandkode-tabelle-1)
- [A5 Anschluss an den Rechner](#a5-anschluss-an-den-rechner)
- [A6 Namenskollisionen](#a6-namenskollisionen)

---

## A0 Überblick

| Merkmal | Angabe |
|---|---|
| Bezeichnung | Lochbandleser 303. "Lochband" und "Lochstreifen" sind Synonyme; in diesem Dokument "Lochstreifenleser" (Kürzel LL) bzw. "Leser" |
| Hersteller | Secura-Werke |
| Vorgänger | Leser 301 (der 303 war dessen Nachfolger) |
| Bandbreite | normalerweise 8-spurige Lochbänder |
| Bauform | mit Gehäuse als Auftischgerät ODER gehäuselos zum Einbau in die Gerätefrontblende |
| Einsatz | u. a. am Computer "Cellatron C8205" sowie an Papierverarbeitungsmaschinen |
| Ausführung "Doppel-Lochbandleser 303" | Am Rechner hängt Leser 1 an Kanal K1 und Leser 2 an Kanal K2; s. A5 |

Zusammenhang mit dem Flag FE (Definition siehe Datei "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md"): FE ("Fehler bei Eingabe") ist ein logischer
Fehler — ein Fehler in den einzugebenden Daten; er kann bei Ausgabe nicht
auftreten. Alle anderen Fehler bei Ein- und Ausgabe sind physische Fehler
(Fehler der Geräteelektronik) und werden nicht in Flags des Rechners
abgebildet. Eine Zeile mit gerader Zahl gelochter Spuren (kein gültiges
Zeichen, s. A4; z. B. "Irrung Zeichen") ist ein solcher logischer Fehler in
den Daten: Flag FE wird gesetzt und der Rechner stoppt. Ausgenommen sind
Zeilen ohne Datenlochung (Vorspann), die der Leser überliest (s. A4).

## A3 Geschwindigkeit

130 Zeichen/s. Der Leser ist der Standardleser des C 8205 (mechanisch,
Metallbürsten).


## A4 Lochbandkode (Tabelle 1)

Die Tabelle 1 selbst (52 Zeilen mit Lochbildern), die Spaltenbedeutungen,
die Konsistenzprüfung, die Sonderzeilen und die Auffälligkeiten stehen in
der Datei "C8205-Interpreter-Kodetabellen.md", Abschnitt 1. Die
E/A-Befehle gehören sowohl zum Rechner als auch zum Leser bzw. Stanzer;
ihre Wirkung im Rahmen des Befehlsablaufs wird hier nicht behandelt.

**Kurzfassung (Details in den Kodetabellen):**

- **Spuren:** w v u p 8 Tr 4 2 1. Tr ist die Transportlochung ohne
  Information; die acht Datenspuren haben folgende Bitwerte im Lochbild:

| Spur | 1 | 2 | 4 | 8 | p | u | v | w |
|---|---|---|---|---|---|---|---|---|
| Bitwert | 1 | 2 | 4 | 10₈ | 20₈ | 40₈ | 100₈ | 200₈ |

- **Parität:** Alle gültigen Zeichen haben eine ungerade Zahl gelochter
  Datenspuren (p ergänzt). Eine Zeile mit gerader Zahl gelochter Spuren ist
  kein gültiges Zeichen und beim Lesen ein Gerätefehler (Flag FE wird
  gesetzt, der Rechner stoppt). Das gilt auch für "Irrung Zeichen" (alle 8
  Spuren). Zeilen ohne Datenlochung (Vorspann) überliest der Leser.
- **Leser:** maßgebend ist die Spalte "Eingabe Adresse" — ein Wert des
  Lesers, der ihn sendet; der Rechner muss ihn interpretieren.
  **Stanzer:** maßgebend ist die Spalte "Ausgabe-Adresse" — ein Wert des
  Rechners, der ihn sendet; die Stanzer-Elektronik muss ihn interpretieren.
  Über den Stanzer sind alle Zeichen der Spalte "Ausgabe-Adresse" ausgebbar,
  alle anderen nicht.
- **"Irrung Zeichen"/"Irrung Satz":** Der Rechner benutzt sie nicht; sie
  dienen der menschlichen Datenerfassung auf Lochstreifen.
- **Sprung-Umstellung:** gehört zur Befehlsdefinition, nicht zur
  Leserdefinition.

**Zeichenlage und Umschaltzeichen:**

- Um. KB / Um. GB bedeuten "Umschalten KB" bzw. "Umschalten GB".
- Die Zeichenlage Klbuch/Gbuch existiert physisch nur am Schreibwerk (SW):
  je nachdem, ob der Umschalter der Schreibmaschine eingerastet ist oder
  nicht; von dort kommt sie auch.
- Der Rechner steht nach dem Einschalten auf KB und merkt sich die
  Zeichenlage übergreifend, d. h. alle Leser werden damit beurteilt — es
  sei denn (und das ist die Regel), über den Leser kommt explizit ein
  Umschaltzeichen. Da immer nur ein Kanal gleichzeitig aktiv sein kann,
  entsteht kein Problem.
- Zeicheneingabe über das SW: Dazu muss K0 angewählt sein (durch Taste oder
  Befehl) und der Schalter SW gedrückt sein. Wird an der Schreibmaschine
  die Umschalttaste KB oder GB gedrückt, bekommt der Rechner auch das als
  Zeichen zugestellt. Eingabe von Umschaltzeichen erfolgt nur, wenn der
  schreibende Mensch es vorsieht; es gibt keine Automatik.
- Bei der Ausgabe durch den Rechner werden Umschaltzeichen nur ausgegeben,
  wenn das Programm es vorsieht; es gibt keine Automatik.
- "Irrung Zeichen" und "Irrung Satz" sind in beiden Zeichenlagen gleich.

## A5 Anschluss an den Rechner

**Kanäle und Geräte:** Die vollständige Kanaltabelle (K0–K3, manuelle
Anwahl, programmierte Anwahlverschlüsselung, alle angeschlossenen Geräte)
soll später in einer eigenen Datei zum Bedienpult stehen; hier nur die für
den Leser nötigen Fakten: Leser 1 hängt an Kanal K1, Leser 2 an Kanal K2,
Stanzer 1 hängt an Kanal K1. Kanal K3 ist beim C 8205 "frei" (kein Gerät
zugeordnet). K0 ist Tastatur- bzw. Schreibwerk-Eingabe (kein
Lochstreifenleser).

**Ablauf einer Zeicheneingabe:**

1. Im Rechenwerk des C 8205 wird ein Eingabebefehl ausgeführt
   ("Eingabe-Halt", Oberbegriff für zwei Eingabebefehlsarten, deren
   Unterschied hier nicht relevant ist).
2. Er veranlasst den Leser, dessen Kanal angewählt ist (Kx mit x ≠ 0), eine
   Position (Lochungszeile) vom Lochstreifen zu lesen, sofern einer
   eingelegt ist. Während dieses Vorgangs ist das Flag E gesetzt (Definition
   siehe Datei "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md": "=1, wenn ein
   Eingabebefehl aufgestellt ist").
3. Ist kein Lochstreifen eingelegt, wartet der Leser unendlich; der Rechner
   bleibt mit gesetztem Flag E stehen (kein Fehler).
4. Ist ein Lochstreifen eingelegt, werden die Lochungen gemäß Tabelle 1
   (Kodetabellen, Abschnitt 1) gelesen und in eine Eingabeadresse
   umgerechnet; diese ist ein Wert des Lesers, der ihn sendet (s. A4).
5. Die Eingabeadresse wird an das Rechenwerk übergeben, das mit ihrer Hilfe
   den Eingabebefehl abschließt (das Wie wird hier nicht erklärt, es
   gehört zur Befehlsdefinition).
6. Damit ist die Zeicheneingabe abgeschlossen; Flag E wird gelöscht, und
   der nächste Befehl kann verarbeitet werden.

Wie das Zeichen intern im Speicher kodiert wird, hängt davon ab, ob
zeicheneingabe-übergreifend VORHER ein Zeichen Klbuch oder Gbuch gelesen
wurde (Zeichenlage rechnerweit, Anfang KB, s. A4).

**Bedienung am Leser: Streifen einlegen und Streifenende**

- Der Lochstreifen kann schon eingelegt werden, wenn der Rechner noch gar
  keine Eingabe anfordert. Er bleibt dann einfach stehen und wartet, bis
  das der Fall ist.
- Fordert der Rechner eine Eingabe an, und ist kein Streifen eingelegt,
  bleibt der Rechner mit gesetztem Flag E stehen; das ist kein Fehler. Wird
  der Streifen dann eingelegt, beginnt die Eingabe sofort;
  Transportlochungen (Zeilen ohne Datenlochung) werden überlesen.
- Der Streifen wird so lange transportiert, wie Eingabebefehle vorliegen,
  bis er aus dem Leser herausfällt. Liegen keine Eingabebefehle vor, bleibt
  der Streifen mittendrin stehen.


## A6 Namenskollisionen

Es werden Namensgleichheiten dokumentiert, nicht aufgelöst.

- **Spurbezeichnungen w, v, u, p** (Kopf der Lochspuren) kollidieren mit
  den gleichlautenden Zeichen w, v, u, p in Tabelle 1 (Klbuch) — andere
  Domäne (Lochspur vs. Zeichen).
- **Spuren 1, 2, 4, 8** kollidieren mit den Ziffern 1, 2, 4, 8 der Tabelle
  und mit den BCD-Zahlen (Stanzzonen 0, 11, 12 und Ziffernwerte).
- **Tr** (Spalte) — keine bekannte Kollision; zur Bedeutung s. A4
  (Transportlochung ohne Information).
- **"Leser 1"/"Leser 2"** (Kanalnamen) vs. "Doppel-Lochbandleser": Für die
  Leserdefinition ohne Belang; am Rechner Leser 1 an K1, Leser 2 an K2
  (s. A5).
- **"Transport":** Tabellenzeile "Transport" (Relikt, nie benutzt),
  "Transport Vorspann" (tatsächlicher Transport ohne Datenlochung), Spur
  Tr (Transportlochung) und der Transportmechanismus des Lesers
  (Reibrad/Zahnrad) sind verschiedene Dinge mit demselben Wortstamm.
- **"E":** Flag E ("=1, wenn ein Eingabebefehl aufgestellt ist", Datei
  "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md") — hier nur als Verweis in A5
  benutzt — und die gleichnamige Taste "E" (Einzelschritt) am Bedienpult
  sind getrennte Namensdomänen (Flag vs. Taste); für den Leser ist
  ausschließlich das Flag E relevant.


---

# Lochstreifenstanzer

Hardwarebeschreibung des Lochstreifenstanzers am Rechner C 8205.


## B0 Überblick

| Merkmal | Angabe |
|---|---|
| Bezeichnung | Lochbandstanzer Cellatron C8021 (Kürzel LS, Kürzel-Kollision mit Schalter "LS", s. B6) |
| Bauform | Einbaugerät |
| Anzahl am Rechner | max. 1 Stanzer |

## B3 Geschwindigkeit

50 Zeichen/s ("maximale Stanzgeschwindigkeit"). Damit dauert ein Zeichen
20 ms.

## B4 Kode

8-Kanal-Code (Tabelle 1 / R300-Kode), Paritätslochung im 5. Bit (Spur p,
Bitwert 20₈ = 2⁴). Der Stanzer erzeugt die Lochungen in den Spuren
w v u p 8 Tr 4 2 1 (w höchstwertig), gemäß Spalte "Ausgabe-Adresse C8205
oktal" der Kodetabellen (Abschnitt 1). Ausgebbar sind ausschließlich die
dort enthaltenen Zeichen.

## B5 Anschluss an den Rechner / Ablauf einer Zeichenausgabe

**Kanal:** K1 (gemeinsam mit Leser 1). Nur ein Stanzer vorhanden, anders
als bei den zwei Lesern.

**Ablauf (analog A5 beim Leser, jedoch Flag A statt E):**

1. Ausgabebefehl im Rechenwerk ausgeführt ("Ausgabe-Halt").
2. Kanal K1 muss angewählt sein; während des Vorgangs ist Flag A gesetzt
   (Definition Datei "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten-mod4.md": "=1,
   wenn ein Ausgabebefehl aufgestellt ist").
3. Ist kein Streifen eingelegt bzw. zu Ende, wartet der Stanzer unendlich;
   Flag A bleibt gesetzt (kein Fehler) — analog zum Leser.
4. Ist ein Streifen eingelegt, wird die Lochung gemäß Tabelle 1 (Spalte
   Ausgabe-Adresse) für das auszugebende Zeichen gestanzt.
5. Danach wird Flag A gelöscht, der nächste Befehl kann verarbeitet
   werden.

**Motorsteuerung:** Der Stanzermotor läuft nicht dauerhaft, sondern läuft
automatisch an, sobald ein Zeichen ausgegeben werden soll, und schaltet
nach einer Abschaltverzögerung automatisch wieder ab, wenn keine weiteren
Zeichen folgen (Wert der Verzögerung soll später in der Datei "C8205-Interpreter-Bedienpult_mit_Schaltern.md"
stehen). Bei kleinen Ausgabelücken würde das zu ständigem Ein-/Ausschalten
führen; dem wirkt der Schalter "LS" entgegen (eingerastet: Motor läuft
dauerhaft weiter) — Details sollen später in der Datei "C8205-Interpreter-Bedienpult_mit_Schaltern.md" stehen,
hier nur referenziert.

**Vorspann:** Ein Vorspann von ca. 5 cm sollte gestanzt werden, damit der
fertige Lochstreifen gut in einen Leser eingelegt werden kann.

**Fehlerbehandlung:** Wie oben (A0) festgehalten, ist FE ein rein
logischer Eingabefehler und kann bei Ausgabe nicht auftreten; physische
Fehler der Stanzer-Elektronik werden nicht in Flags abgebildet.

## B6 Namenskollisionen

Gelten analog zum Leser (s. A6: Spurbezeichnungen w/v/u/p, Ziffernspuren
1/2/4/8, "Transport"). Zusätzlich: Kürzel "LS" für den Stanzer selbst
(Bezeichnung, s. B0) kollidiert mit dem gleichnamigen Bedienpult-Schalter
"LS" (Motor-Dauerlauf, s. B5) — Bezeichnung vs. Schalter, getrennte
Namensdomänen.


---

# Schreibwerk (Ausgabe)

Hardwarebeschreibung der Schreibwerk-Ausgabe am Rechner C 8205. Die
Schreibwerk-**Eingabe** (Tastatur-/SW-Zeicheneingabe über Kanal K0) ist in
A5 beschrieben; hier geht es ausschließlich um die Ausgabeseite.

## C0 Überblick

| Merkmal | Angabe |
|---|---|
| Bezeichnung | Schreibwerk (SW), für alphanumerische Ein- und Ausgabe |
| Geschwindigkeit | max. 10 Zeichen/s |
| Kanal (Ausgabe) | K2 (gemeinsam mit Leser 2 für die Eingabe) |

## C1 Kanal und Sperrwirkung des Schalters "SW"/"T-SW"

Die Ausgabe über Kanal K2 ist **unabhängig** von der Stellung des
Schalters "SW"/"T-SW" jederzeit möglich; dieser Schalter wirkt sich
ausschließlich auf die Eingabeseite von Kanal K0 aus (s. Datei "C8205-Interpreter-Bedienpult_mit_Schaltern.md",
Abschnitt "Schalter LS und Stellung SW").

## C2 KB/GB-Gedächtnis bei der Ausgabe

Bei der **Eingabe** sind die Tasten "Umschaltung KB" (Kleinbuchstabe) und
"Umschaltung GB" (Großbuchstabe) ganz normale Zeichen wie jedes andere
(s. A4).

Bei der **Ausgabe** dagegen besitzt das Schreibwerk für diese Umschaltung
ein Gedächtnis: KB und GB sind zueinander alternativ (genau ein Zustand
ist jeweils aktiv).

- Beim **Netz-Einschalten** des Rechners C8205 wird dieser Zustand (KB
  ODER GB) — auch für den Interpreter
  — **zufällig** gesetzt.
- Die Ausgabe über K2 verwendet die jeweils **vorhandene** (aktuelle)
  KB/GB-Stellung, um das auszugebende Zeichen als Klein- oder
  Großbuchstabe darzustellen.
- Der KB/GB-Zustand wird durch die Ausgabe eines Zeichens mit
  entsprechender Ausgabe-Adresse gemäß Tabelle 1 (Kodetabellen,
  Abschnitt 1) umgeschaltet:
  - Ausgabe-Adresse **117x** (oktal) → KB einschalten
  - Ausgabe-Adresse **057x** (oktal) → GB einschalten

  Dabei steht **x** für eine beliebige Oktalziffer (0–7), also don't-care
  an dieser Stelle.

## C3 Offene Punkte

- Der detaillierte Ablauf einer Zeichenausgabe über das Schreibwerk
  (analog A5 beim Leser bzw. B5 beim Stanzer: welcher Befehl genau
  auslöst, welches Flag währenddessen gesetzt ist, Fehlerbehandlung) ist
  noch nicht dokumentiert.
