** PDF-Gestaltungsrichtlinie (Wurzeldokument für alle PDF-Ausgaben) **

Version: 0.95-002

Dieses Dokument legt fest, nach welchen Konventionen die .md-Quelldateien dieses Projekts als
menschenlesbare PDFs ausgegeben werden. Ziel: jede künftige PDF-Ausgabe (Knotengraph, Einzelbefehlsliste,
Kodetabellen/Tabelle 1, ggf. weitere) soll ohne erneute Design-Entscheidung nach demselben Muster
entstehen. Bei Änderungen an dieser Richtlinie: Abschnitt 9 (Änderungsprotokoll) fortschreiben, nicht
stillschweigend überschreiben.


## 1. Seitenformat und Ränder

- Seitengröße: A4 Hochformat (595,28 × 841,89 pt) als Standard. Querformat nur, wenn eine Tabelle in
  Hochformat nicht sinnvoll spaltenweise umbrechbar ist (Einzelfallentscheidung, hier vermerken).
- Rand: 30 pt (≈ 10,6 mm) auf allen vier Seiten als Basis.
- Kopfzeilenbereich: zusätzlich 26 pt oberhalb des Inhalts reserviert.
- Fußzeilenbereich: zusätzlich 14 pt unterhalb des Inhalts reserviert.

## 2. Schrift

- Schriftfamilie: DejaVu Sans / DejaVu Sans Bold / DejaVu Sans Mono (aus `/usr/share/fonts/truetype/dejavu/`,
  einbetten und als Font registrieren). Entscheidung 2026-10-02: Alle Dokumente verwenden einheitlich DejaVu; der
  Basisfont Helvetica stellt Unicode-Notation (Hoch-/Tiefzahlen, ⟨⟩, ∧ ∨, ≤ ≥, →) nicht dar.
  **Ausnahme Knotengraph:** Die Kacheln bleiben bei Helvetica / Helvetica-Bold (PDF-Basisfont), weil Helvetica schmaler
  setzt und die Platzverhältnisse dort knapp sind; der Knotengraph wird nicht umgestellt. Die ASCII-Schreibweise z12
  statt z₁₂ gilt weiter für selbst erzeugte Beschriftungen in Diagrammen.
- Richtgrößen:
  - Deckblatt: Titel 26 pt fett, Untertitel 12 pt (weitere Größen: Abschnitt 4.2)
  - Seitentitel auf Referenzseiten (z. B. „Kurzcodes A-nnn“): 16 pt fett
  - Abschnittsüberschriften: 12 pt fett
  - Fließtext / Hinweise: 9–10 pt
  - Tabellen-/Referenzzeilen: 8,5 pt (nicht kleiner, sonst nicht mehr gut lesbar im Druck)
  - Kopfzeile Inhaltsseite: 11 pt fett (Titel) + 8 pt (Legende/Unterzeile)
  - Fußzeile: 7,5 pt
- Unicode-Hochzahlen/-Tiefzahlen (₀₁₂₃…, ⁰¹²³…) in Diagrammen mit Helvetica (Knotengraph) NICHT verwenden (der
  Basisfont stellt sie als Kästchen dar). Stattdessen ASCII-Schreibweise wie z12, z30 oder reportlab-Tags (<sub>/<super>).

## 3. Kopf- und Fußzeile jeder Inhaltsseite

- Gilt ab Seite 2. Das Deckblatt (Seite 1) hat weder Kopf- noch Fußzeile noch Seitenzahl (Abschnitt 4.1), zählt aber
  bei „Seite X / Y“ als Seite 1.
- Kopfzeile links: „C 8205 – “ und Titel des Dokuments (wie auf dem Deckblatt) + bei mehrseitigen/gekachelten
  Inhalten die Position, z. B. "Blatt 3/12 (Zeile 2/6, Spalte 1/2)".
- Kopfzeile, zweite Zeile: kompakte Legende der verwendeten Farben/Symbole (siehe Abschnitt 5), sofern
  auf der Seite relevant – Wiederholung auf jeder Seite, damit Einzelblätter für sich verständlich bleiben.
- Fußzeile links: Kurzhinweis, falls Kacheln überlappen ("Kacheln überlappen sich ca. 7 mm …").
- Fußzeile rechts: "Seite X / Y" (absolute Seitenzahl im Gesamt-PDF, nicht nur innerhalb eines Abschnitts).
- Lage, Schrift und Farben der Kopf- und Fußzeile sowie alle übrigen Elemente der Folgeseiten: Abschnitt 3a.

## 3a. Folgeseiten (alle Seiten ab Seite 2)

Dieser Abschnitt legt fest, wie die Seiten hinter dem Deckblatt aussehen, damit PDFs aus verschiedenen Skripten gleich
wirken. Maßstab sind die Bausteine in `pdflib.py` (Stand 2026-10-11), soweit sie hier aufgeführt sind; wo ein Skript davon
abweicht, ist das ein Mangel des Skripts, nicht der Richtlinie (Liste: 3a.7). Für Diagramme und Kacheln gelten zusätzlich
die Abschnitte 5 und 6. Alle Maße in pt, Farben wie in 4.1: Tinte #1F2937, Grau #6B7280, Linie #D1D5DB, Fläche #F3F4F6,
Dunkel #374151.


### 3a.1 Kopf- und Fußzeile: Lage, Schrift, Inhalt

Was in den Zeilen steht, regelt Abschnitt 3; hier stehen Lage und Schrift. Lagen sind vom Seitenrand gemessen.

| Element | Lage | Schrift und Farbe |
|---|---|---|
| Kopfzeile, Zeile 1 | Grundlinie 38 pt vom oberen Seitenrand | 11 pt Sans Bold, Tinte |
| Kopfzeile, Zeile 2 | Grundlinie 50 pt vom oberen Seitenrand | 8 pt Sans, Grau |
| Kopflinie | 54,5 pt vom oberen Seitenrand, Breite 0,5 pt, volle Satzbreite | Linie |
| Inhaltsbereich (Satzspiegel) | 56 pt vom oberen bis 44 pt vom unteren Seitenrand, Breite 535,3 pt | – |
| Fußlinie | 41 pt vom unteren Seitenrand, Breite 0,5 pt, volle Satzbreite | Linie |
| Fußzeile links und rechts | Grundlinie 28 pt vom unteren Seitenrand | 7,5 pt Sans, Grau |

- **Zeile 1 links:** „C 8205 – “ und Titel des Deckblatts (4.6); bei Kachel-PDFs folgt die Position, z. B. „Blatt 3/12 (Zeile 2/6,
  Spalte 1/2)“.
- **Zeile 2:** genau eine Zeile, höchstens ca. 120 Zeichen. Bei redaktionellen PDFs die wichtigste Schreibweise oder Legende
  des Dokuments; bei Wortlaut-PDFs „Quelle: <Dateiname> · im Wortlaut der Quelle“; bei Kachel-PDFs auf den Kachelseiten die
  grafische Legende der Kantenfarben (Abschnitt 5), auf den Vorspannseiten der Seitentyp („Lesehinweise“, „Referenzseiten
  Kurzcodes A-nnn“).
- **Fußzeile links:** „C8205-Interpreter-Projekt · Stand TT.MM.JJJJ“; der Stand ist der des Deckblatts. Bei Kachel-PDFs steht
  auf den Kachelseiten stattdessen der Überlappungshinweis (Abschnitt 3). **Rechts:** „Seite X / Y“.
- **Farben:** Text in Tinte oder Grau, Linien in Linienfarbe; kein reines Schwarz und keine anderen Grautöne (ausgenommen
  der Inhalt von Diagrammen, dort gilt Abschnitt 5).


### 3a.2 Textelemente

Alle Texte in Tinte, sofern nicht anders vermerkt; Schrift DejaVu Sans, Code DejaVu Sans Mono (Abschnitt 2).

| Element | Schrift | Größe / Zeilenabstand | Abstand davor / danach |
|---|---|---|---|
| Fließtext | Sans | 9,2 / 12,6 pt | – / 4,5 pt |
| Aufzählung, Nummerierung | Sans, wie Fließtext | 9,2 / 12,6 pt; Einzug 11 pt (Nummerierung 15 pt) | – / 2,5 pt |
| Überschrift Ebene 1 | Sans Bold | 12 / 15 pt | 11 / 5 pt |
| Überschrift Ebene 2 | Sans Bold | 10 / 13 pt | 7 / 3,5 pt |
| Überschrift Ebene 3 (nur Wortlaut-PDFs) | Sans Bold | 9,2 / 12 pt | 5 / – |
| Tabellentext | Sans | 8,5 / 10,8 pt | – |
| Codeblock | Sans Mono | 7,4 / 9 pt | – / 6 pt |
| Bildunterschrift | Sans, Grau | 8 / 10,4 pt | 2 / 7 pt |
| Inhaltsverzeichnis Ebene 1 | Sans Bold | 9 / 11 pt | 2,4 / – |
| Inhaltsverzeichnis Ebene 2 | Sans | 8,4 / 9,8 pt; Einzug 14 pt | – |

Absätze lassen keine einzelne Zeile am Seitenende (Waise) oder am Seitenanfang (Witwe) stehen.


### 3a.3 Tabellen

Alle Tabellen haben denselben Stil:

- **Kopfzeile:** 8,5 pt Sans Bold, weiß auf Dunkel; sie wiederholt sich auf jeder Folgeseite der Tabelle.
- **Zellen:** 8,5 pt Tinte; Innenabstand 4,5 pt seitlich und 3 pt oben und unten.
- **Linien:** Zeilenlinie 0,4 pt und Rahmen 0,5 pt in Linienfarbe. **Kein Zebramuster und kein Gitter.**
- **Umbruch:** Die letzte Zeile steht nie allein auf der Folgeseite; Tabellen bis 10 Zeilen und 190 pt Höhe bleiben auf einer Seite.
- **Farbige Zellfüllungen** gibt es nur, wenn ihre Bedeutung in den Lesehinweisen erklärt ist (Beispiel: In der Knotentabelle
  kennzeichnet die Zeilenfarbe den Knotentyp). Zebrastreifen tragen keine Bedeutung und entfallen, damit Farbe in den
  Tabellen immer etwas bedeutet.


### 3a.4 Hinweis- und Achtung-Kästen

Ein Kasten hat links einen Balken (3,2 pt breit) und eine getönte Fläche; Innenabstand 7 pt links, 6 pt rechts, 4,5 pt oben und
unten, danach 6 pt Abstand. Text 8,8 / 11,8 pt; er beginnt mit dem Stichwort in Fettschrift.

| Kasten | Balken | Fläche | Bedeutung |
|---|---|---|---|
| Hinweis | Blau #2563EB | #EAF1FF | nützliche Ergänzung, die das Verständnis erleichtert |
| Achtung | Orange #D97706 | #FFF3E0 | Stelle, an der man sich leicht irrt oder an der Hardware und Interpreter abweichen |

Blau und Orange sind für diese beiden Kästen reserviert (Ergänzung zu Abschnitt 5); in Text, Linien und Tabellenköpfen kommen
sie nicht vor. Das Deckblatt hat keine solchen Kästen (4.1).


### 3a.5 Codeblöcke

Sans Mono 7,4 / 9 pt auf Fläche, links ein Balken in Grau (3,2 pt); Innenabstand 10 pt links, 5 pt rechts, 4 pt oben und unten. Zu
lange Zeilen werden vorab umbrochen, Fortsetzungszeilen sind um vier Zeichen eingerückt. Blöcke bis 12 Zeilen bleiben zusammen
und mit dem einleitenden Absatz, wenn dieser mit „:“ endet. Längere Blöcke werden nur an Leerzeilen oder spätestens nach 40
Zeilen getrennt, mit mindestens 6 Zeilen oben und 4 Zeilen unten.


### 3a.6 Seitenumbrüche

- **Überschriften** stehen nie allein am Seitenende. Dafür muss unter ihnen Platz bleiben: bei redaktionellen PDFs 120 pt (Ebene 1)
  und 85 pt (Ebene 2), bei Wortlaut-PDFs 60, 48 und 40 pt (Ebene 1, 2, 3), weil dort viele kurze Abschnitte folgen.
- **Kapitel beginnen nicht grundsätzlich auf einer neuen Seite.** Die Teile eines Dokuments (Lesehinweise, Inhaltsverzeichnis,
  Referenzseiten, Inhalt) beginnen dagegen immer auf einer neuen Seite (4.4). Dokumente, deren Kapitel eigenständige
  Tabellen sind, dürfen jedes Kapitel auf einer neuen Seite beginnen (Beispiel: Knotentabellen).
- **Abbildung und Bildunterschrift** bleiben zusammen.


### 3a.7 Bekannte Abweichungen der Skripte (Stand 2026-10-14)

Bis zur Anpassung der Skripte weichen sie wie folgt von Abschnitt 3a und 4 ab. Der Eintrag wird gestrichen, sobald das
Skript angepasst ist.

- **`erzeuge_knoten_pdfs.py`, nur das Knotengraph-PDF** (die Knotentabellen erzeugt seit der Anpassung der eingebettete
  Baustein `erzeuge_knotentabellen_pdf.py` mit Deckblatt und Erzeugungsdatum nach Abschnitt 3a und 4): kein Deckblatt nach
  Abschnitt 4; der Stand wird aus den Datumsangaben der Quelltexte abgeleitet, nicht als Erzeugungsdatum gesetzt.
- **`pdflib.py`:** `Doc` trägt Titel „C 8205 – Testhandbuch“ und Betreff „Testhandbuch“ fest (nur für das Testhandbuch
  richtig; das Rechnerbeschreibungs-Skript und `md2pdf.py` überschreiben beides).
- **`erzeuge_knoten_pdfs.py`, Knotengraph-PDF:** zeichnet mit eigenem Code und führt Schriften, Maße und Farben selbst (der
  eingebettete Baustein `pdflib.py` wird für die Knotentabellen verwendet); Text in reinem Schwarz und #555555 statt Tinte und Grau; Fußzeile mit Grundlinie 31 statt 28 pt; Überschrift Ebene 2 mit 11 statt 10 pt;
  Tabellen mit Gitter und hellgrauem Kopf (#D9D9D9); Kopfzeile auch auf Seite 1; Titel „C8205 Knotengraph“ statt
  „C 8205 – Knotengraph“.


## 4. Deckblatt und Referenzseiten

Jedes PDF nach dieser Richtlinie beginnt mit einem **Deckblatt** auf Seite 1. Es ist für alle PDFs gleich aufgebaut; es
unterscheiden sich nur die Texte und einzelne Zeilen des Angabenblocks (4.2, 4.3, 4.6). Festlegung vom 2026-10-11. Sie
ersetzt den früheren Seitenanfang aus Titel, Fließtext, Legenden und Inhaltsverzeichnis. Das Deckblatt sagt, **was** das
Dokument ist, **worauf** es beruht und **wie aktuell** es ist; wie man es **liest**, steht ab Seite 2 (4.4).


### 4.1 Grundsätze

- **Eine Seite, nur das Wesentliche.** Das Deckblatt zeigt, wo das Dokument im Projekt steht (Zone A), wie es heißt und
  was es ist (B), worauf es beruht und wie aktuell es ist (D, E). Legenden, Schreibweisen, Lesehinweise und das
  Inhaltsverzeichnis stehen nicht auf dem Deckblatt.
- **Keine Kopf- und Fußzeile, keine Seitenzahl** auf dem Deckblatt; Abschnitt 3 gilt erst ab Seite 2. Das Deckblatt zählt
  aber als Seite 1: Die nächste Seite trägt „Seite 2 / Y“, Y = Gesamtzahl einschließlich Deckblatt.
- **Nur Grautöne** der Palette der Inhaltsseiten: Tinte #1F2937, Grau #6B7280, Linie #D1D5DB, Fläche #F3F4F6, Dunkel
  #374151. Grün, Rot, Blau und Orange (Abschnitt 5 und 3a.4) kommen auf dem Deckblatt nicht vor: Ihre
  festen Bedeutungen sollen nicht verwässert werden, und das Blatt bleibt im Schwarzweißdruck unverändert.
- **Keine Bilder, Logos oder Flächen bis an den Seitenrand** (übliche Drucker drucken nicht randlos). Gliedern nur durch
  Linien, Abstände und Schriftgrößen.
- **Linksbündig an einem gemeinsamen Spaltenrand**; nichts ist zentriert.
- **Schrift** DejaVu Sans / Sans Bold / Sans Mono (Abschnitt 2). Die Ausnahme „Knotengraph bleibt bei Helvetica“ gilt nur
  für die Kacheln, nicht für das Deckblatt.


### 4.2 Aufbau und Maße

Das Deckblatt hat einen größeren Rand als die Inhaltsseiten (Abschnitt 1): **20 mm = 56,7 pt** auf allen vier Seiten,
Spaltenbreite 481,9 pt. Die Zonen A bis C hängen am oberen Rand, D bis F am unteren; die freie Fläche dazwischen wächst
und schrumpft mit dem Text, keine Zone rückt nach.

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│ C 8205 · Simulation eines DDR-Kleinrechners …          [ INTERPRETER ] │   ← Zone A
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                        │
│                                                                        │
│                                                                        │
│ HANDBUCH                                                               │   ← Zone B
│ Testhandbuch                                                           │
│ Wie ein Test aufgebaut ist, wie er abläuft und                         │
│ wie man sein Ergebnis liest                                            │
│                                                                        │
│ Kurzbeschreibung (nur wenn der Untertitel nicht genügt)                │   ← Zone C
│                                                                        │
│                                                                        │
│                                                                        │
│ ────────────────────────────────────────────────────────────────────── │
│ Quelle      C8205-Interpreter-Durchführung_eines_Tests.md     0.03-009 │   ← Zone D
│ ────────────────────────────────────────────────────────────────────── │
│ Stand       11.10.2026                                                 │
│ ────────────────────────────────────────────────────────────────────── │
│ Umfang      58 Seiten, A4 hoch                                         │
│ ────────────────────────────────────────────────────────────────────── │
│                                                                        │
│ ┃ Maßgeblich bleibt die Quelldatei. Dieses PDF wird nicht              │   ← Zone E
│ ┃ automatisch nachgeführt: Es ist aktuell, solange …                   │
│                                                                        │
│                                                                        │
│ ────────────────────────────────────────────────────────────────────── │
│ C8205-Interpreter-Projekt                    C8205-Testhandbuch_A4.pdf │   ← Zone F
└────────────────────────────────────────────────────────────────────────┘
```

| Zone | Inhalt | Lage | Schrift und Linien |
|---|---|---|---|
| A Kennung | links: „C 8205 · Simulation eines DDR-Kleinrechners von 1968“ (Titel der README); rechts: Bereichsetikett; darunter Linie über die Spaltenbreite | Oberkante 56,7 pt vom oberen Rand; Linie 22 pt darunter | Text 9 pt Grau; Etikett 8 pt fett, weiß auf Dunkel #374151, Großbuchstaben, Rechteck mit 2 pt Rundung, Innenabstand 6 pt seitlich und 3 pt oben/unten; Linie 2 pt Dunkel |
| B Titelblock | Dokumentart (Überzeile), Titel, Untertitel | Oberkante der Überzeile bei 27 % der Seitenhöhe (ca. 227 pt vom oberen Rand); Überzeile → Titel 8 pt, Titel → Untertitel 10 pt | Überzeile 9 pt fett Grau, Großbuchstaben, Zeichenabstand 1 pt; Titel 26 pt fett Tinte, Zeilenabstand 31 pt; Untertitel 12 pt Grau, Zeilenabstand 16 pt |
| C Kurzbeschreibung | 2 bis 4 Sätze, **nur wenn der Untertitel nicht genügt**; höchstens 6 Zeilen (ca. 500 Zeichen) | 24 pt unter dem Untertitel | 10 pt Tinte, Zeilenabstand 14 pt |
| D Angabenblock | Tabelle „Quelle(n), Stand, Umfang …“ (Zeilen s. u.) | Unterkante 14 pt über Zone E | 8,5 pt, Zeilenabstand 11 pt, je 4 pt Abstand oben und unten; Bezeichner Grau, Werte Tinte, Dateinamen und Skriptnamen in Sans Mono 8 pt; Bezeichnerspalte 90 pt breit; Linie 0,5 pt #D1D5DB über jeder Zeile und unter der letzten |
| E Aktualitätshinweis | immer derselbe Text (4.3) | Unterkante 24 pt über der Linie von Zone F | 8,5 pt Tinte, Zeilenabstand 11,5 pt; Fläche #F3F4F6, Innenabstand 8 pt, Balken links 3 pt Dunkel |
| F Fuß | links: „C8205-Interpreter-Projekt“ (wie in der Fußzeile der Inhaltsseiten); rechts: Dateiname des PDFs | Grundlinie 56,7 pt vom unteren Rand; Linie 12 pt darüber | 7,5 pt Grau (wie Fußzeile, Abschnitt 3); Dateiname in Sans Mono; Linie 0,5 pt #D1D5DB |

Zeilen des Angabenblocks (Zone D), feste Reihenfolge; Zeilen ohne Inhalt entfallen:

| Zeile | Inhalt |
|---|---|
| Quelle / Quellen | Dateiname der .md-Quelle ohne Pfad, **rechtsbündig die Version `y.xx-zzz` der Quelle** zum Zeitpunkt der Erzeugung. Mehrere Quellen: je eine Zeile, in der Reihenfolge von Abschnitt 8. Der Bezeichner steht nur in der ersten Zeile |
| Stand | Datum der Erzeugung des PDFs, `TT.MM.JJJJ` (gleicher Wert wie „Stand“ in der Fußzeile der Inhaltsseiten) |
| Umfang | „N Seiten, A4 hoch“, einschließlich Deckblatt |
| Erzeugt mit | nur bei PDFs aus einem Skript: Skriptname, z. B. `erzeuge_rechnerbeschreibung_pdf.py` |
| Layoutraster | nur bei Kachel-PDFs: „Z Zeile(n) × S Spalte(n) = Z·S A4-Seiten, Skalierung X %“ |


### 4.3 Texte und Wertevorrat

- **Titel:** der Name, unter dem das Dokument in Abschnitt 8 und in der Dokumentenlandkarte des Projektüberblicks genannt
  wird; ohne Vorsatz „C 8205 –“ (steht in Zone A) und ohne Klammerzusatz der Quelle (z. B. „(Wurzeldokument für …)“).
  Er wird **nicht aus der ersten Zeile der .md-Datei abgeleitet**: Die Titelzeilen der Quellen sind uneinheitlich
  (`** X **`, `# X`, `# ** X **`, `### X ###`) und nennen nicht immer den PDF-Titel (die Quelle „Knotendefinition“ ergibt
  das PDF „Knotengraph“). Titel, Untertitel, Art und Bereich stehen deshalb fest in 4.6.
- **Titellänge:** höchstens zwei Zeilen bei 26 pt (ca. 30 Zeichen je Zeile). Ist der Titel länger, 22 pt; passt er auch
  dann nicht in zwei Zeilen, den Titel kürzen und die Langform in den Untertitel setzen.
- **Untertitel:** ein Satzfragment ohne Schlusspunkt, höchstens zwei Zeilen (ca. 70 Zeichen je Zeile), sagt in einem Atemzug,
  was das Dokument enthält. Er wiederholt den Titel nicht.
- **Dokumentart** (Überzeile, genau ein Wert):

| Wert | Bedeutung |
|---|---|
| ÜBERBLICK | Einstieg und Einordnung für Leser, die das Projekt nicht kennen |
| BESCHREIBUNG | erklärt Aufbau und Wirkungsweise (Rechner, Teilprojekt) |
| REFERENZ | zum Nachschlagen: Tabellen, Listen, Wortlaut von Regelwerksdateien |
| HANDBUCH | Anleitung zum Tun: bedienen, testen |
| DIAGRAMM | Graph oder Ablaufplan |
| RICHTLINIE | Wurzeldokument mit Regeln (Versionierung, Projektstruktur, PDF-Gestaltung) |

- **Bereich** (Etikett rechts oben, genau ein Wert; angelehnt an die drei Teilprojekte aus Überblick_und_Gesamtaufbau und
  Projektstruktur, ergänzt um GESAMTPROJEKT und RECHNER UND REGELWERK für Dokumente, die keinem Teilprojekt allein gehören):

| Wert | Bedeutung |
|---|---|
| GESAMTPROJEKT | gilt für alle Teilprojekte: Überblick, Einstieg, Wurzeldokumente |
| RECHNER UND REGELWERK | der simulierte C 8205 selbst: Aufbau, Befehle, Kodes, Knotenautomat, Bedienpult |
| INTERPRETER | Python-Interpreter, Tests, Lochstreifen-Hilfsprogramme |
| ASSEMBLER | Assembler c82ass |
| BIS | Bausteininterpretationssystem |

- **Kurzbeschreibung (Zone C):** Bei PDFs, die eine Quelle im Wortlaut wiedergeben (Abschnitt 6a), genügt der Standardsatz:
  „Dieses PDF gibt die Quelle im Wortlaut wieder; Listen, Tabellen und Codeblöcke entsprechen der Quelle, weich
  umbrochene Zeilen sind zu Absätzen zusammengeführt.“ Bei redaktionellen PDFs steht hier der bisherige erste Absatz
  des Titelblocks (Zweck, Leserkreis, Abgrenzung), auf die Zeilenzahl gekürzt.
- **Version und Stand:** Die Version wird beim Erzeugen aus der Zeile `Version: y.xx-zzz` der Quelldatei gelesen (bei den
  beiden Knoten-Dateien `# Version: …`; Muster: `C8205-Versionierung.md`, Abschnitt 6), nicht von Hand eingetragen.
  **Fehlt die Zeile, bricht die Erzeugung mit einer Fehlermeldung ab**; es wird kein Platzhalter gedruckt. Der Stand ist
  das Erzeugungsdatum, nicht das Datum der Quelle.
- **Aktualitätshinweis (Zone E), Wortlaut fest:** „Maßgeblich bleibt die Quelldatei. Dieses PDF wird nicht automatisch
  nachgeführt: Es ist aktuell, solange die Version oben mit der Versionszeile der Quelldatei übereinstimmt.“ Bei mehreren
  Quellen: „Maßgeblich bleiben die Quelldateien … solange die Versionen oben mit den Versionszeilen der Quelldateien
  übereinstimmen.“ Damit ist der in `C8205-Versionierung.md`, Abschnitt 8, offene Punkt „Nummer der Quelldatei auf das
  Deckblatt“ entschieden: **ja**.


### 4.4 Seite 2 und folgende

- Seite 2 beginnt mit den **Lesehinweisen**, soweit das Dokument welche hat: Schreibweisen, Legende der Farben und Symbole
  (Abschnitt 5), Lesereihenfolge, Abgrenzung, Verweise auf verwandte PDFs; Hinweis- und Achtung-Kästen dürfen hier stehen.
  Es folgt das **Inhaltsverzeichnis** (Gliederungsebenen 1 bis 2), wenn das Dokument eine Gliederung hat. Passen beide
  nicht auf eine Seite, steht das Inhaltsverzeichnis auf Seite 3.
- Hat ein Dokument weder Lesehinweise noch Gliederung, beginnt der Inhalt auf Seite 2.
- Der eigentliche Inhalt beginnt immer auf einer neuen Seite.
- Die Kopf- und Fußzeilen nach Abschnitt 3 beginnen auf Seite 2.


### 4.5 Referenzseiten, Leerseite und Doppelseitenansicht

- Falls im Inhalt Kurzcodes verwendet werden (z. B. A-nnn für ANWEISUNG-nnn), folgt nach den Lesehinweisen eine eigene
  Referenzseite (ggf. mehrseitig) mit Kurzcode → Volltext, bevor der eigentliche Inhalt beginnt.
- **Kachel-PDFs:** Die erste Kachelseite hat eine **gerade Seitenzahl**. Endet der vorangehende Teil auf einer geraden
  Seite, wird eine Leerseite (mit dem Vermerk „Leerseite – damit die Kachelseiten paarweise nebeneinander stehen“)
  eingefügt, sonst nicht. Grund: In der Doppelseitenansicht mit einzelnem Deckblatt (Seite 1 rechts, danach 2|3, 4|5, …)
  stehen Spalte 1 links und Spalte 2 rechts nebeneinander.
- Für Kachel-PDFs wird die Anzeigevoreinstellung „zwei Seiten, ungerade rechts“ gesetzt (PDF-Katalogeintrag `PageLayout` =
  `TwoPageRight`), damit der Leser die Doppelseitenansicht nicht erst einstellen muss.

**Seitenfolge Knotengraph (Kachel-PDF)**

| Seite | Inhalt | Kopfzeile, Zeile 2 |
|---|---|---|
| 1 | Deckblatt (4.2) mit der zusätzlichen Zeile „Layoutraster“ | keine Kopf- und Fußzeile |
| 2 | Lesehinweise: Lesereihenfolge, Kurzcodes A-nnn, Konnektoren, gleichzeitige Anweisungen (&&), Knoten- und Symboltypen, Kanten und Farben | „Lesehinweise“ |
| 3 bis k | Referenzseiten „Kurzcodes A-nnn“: Tabelle Kurzcode, Volltext, Art; die Tabellenkopfzeile wiederholt sich | „Referenzseiten Kurzcodes A-nnn“ |
| k+1, nur wenn k gerade | Leerseite mit dem Vermerk „Leerseite – damit die Kachelseiten paarweise nebeneinander stehen“ (Grau, kursiv, mittig) | keine Kopfzeile; Fußzeile nur mit „Seite X / Y“ |
| ab der ersten Kachelseite | Kachelseiten Blatt 1 bis N, zeilenweise, links nach rechts, oben nach unten | grafische Legende der Kantenfarben |

- Es gibt **kein Inhaltsverzeichnis** (keine Gliederung, 4.4). Die erste Kachelseite ist Seite k+1, wenn k ungerade ist, sonst
  k+2; die Gesamtseitenzahl ist (Nummer der ersten Kachelseite − 1) + Z · S.
- **Beispiel:** Raster 3 Zeilen × 2 Spalten = 6 Kachelseiten. Enden die Referenzseiten auf Seite 5 (k = 5), beginnt die erste
  Kachelseite auf Seite 6, ohne Leerseite; insgesamt 11 Seiten. Enden sie auf Seite 4 (k = 4), steht auf Seite 5 die
  Leerseite, die erste Kachelseite ist wieder Seite 6, insgesamt 11 Seiten.
- **Kachelgeometrie** nach Abschnitt 6: Überlappung 20 pt, feste Spaltenzahl, Skalierung nicht unter ca. 85 bis 90 %. Jede Kachel
  wird auf den Satzspiegel (535,3 × 741,9 pt) beschnitten, damit nichts in Kopf- oder Fußzeile ragt. Kopfzeile Zeile 1:
  „C 8205 – Knotengraph  Blatt n/N (Zeile i/Z, Spalte j/S)“; Fußzeile links: der Überlappungshinweis.
- **Knotentabellen** (nicht gekachelt, aus demselben Skript): Deckblatt, dessen Kurzbeschreibung (Zone C) den Umfang nennt (Zahl
  der Knoten und der Einträge der Variablentabelle T2); Seite 2 mit Lesehinweisen (Lesart, Legende der Zeilenfarben und
  Arten) und Inhaltsverzeichnis; danach beginnen Knotentabelle, Variablentabelle T2 und „Lesart, Konventionen und
  Ergänzungen der Quellen“ je auf einer neuen Seite (3a.6).


### 4.6 Deckblattdaten je PDF

Titel, Untertitel, Art und Bereich der bisherigen PDFs (Quellen: Abschnitt 8). Bei neuen PDFs wird hier eine Zeile
ergänzt, bevor das PDF erzeugt wird.

| PDF | Titel | Untertitel | Art | Bereich |
|---|---|---|---|---|
| `C8205-Projektueberblick_A4.pdf` | Projektüberblick | Was das Projekt ist, wie es aufgebaut ist und wie die Dokumente zusammenhängen | ÜBERBLICK | GESAMTPROJEKT |
| `C8205-Einstieg_fuer_Neueinsteiger_A4.pdf` | Einstieg für Neueinsteiger | Was das Projekt enthält, in welcher Reihenfolge man liest und wo man bei einer Frage weiterliest | ÜBERBLICK | GESAMTPROJEKT |
| `C8205-Rechnerbeschreibung_A4.pdf` | Rechnerbeschreibung | Aufbau, Register, Maschinenwort, Zahlendarstellung, Magnettrommel und Befehlszyklus des Cellatron C 8205 | BESCHREIBUNG | RECHNER UND REGELWERK |
| `C8205-Bedienpult_und_Peripherie_A4.pdf` | Bedienpult und Peripherie | Tasten, Schalter, Lampen, Kanäle, Lochstreifenleser, -stanzer und Schreibwerk | BESCHREIBUNG | RECHNER UND REGELWERK |
| `C8205-Bedienungsanleitung_Interpreter_A4.pdf` | Bedienungsanleitung Python-Interpreter | Aufruf, Schalter und Geräte von c8205_interp.py | HANDBUCH | INTERPRETER |
| `C8205-Testhandbuch_A4.pdf` | Testhandbuch | Wie ein Test aufgebaut ist, wie er abläuft und wie man sein Ergebnis liest | HANDBUCH | INTERPRETER |
| `C8205-Durchfuehrung_eines_Tests_A4.pdf` | Durchführung eines Tests | Das Testformat im Wortlaut der Quelle: Trommeldatei, Tastenfolge, Prüfungen, Geräte, Protokoll | REFERENZ | INTERPRETER |
| `C8205-GRAFIK_Beschreibung_A4.pdf` | GRAFIK-Interpreter: Beschreibung | Zweck, Fenster, Geräte, Töne, Aufruf und Grenzen des GRAFIK-Modus im Wortlaut der Quelle | BESCHREIBUNG | INTERPRETER |
| `C8205-GRAFIK_Pruefverfahren_A4.pdf` | GRAFIK-Interpreter: Prüfverfahren | Wie man prüft, dass der GRAFIK-Interpreter das Soll der Beschreibung erfüllt: Läufe, Tests, Abnahme | HANDBUCH | INTERPRETER |
| `C8205-Lochstreifen-Hilfsprogramme_A4.pdf` | Lochstreifen-Hilfsprogramme | Anzeige, Eingabe und Umwandlung virtueller Lochstreifen: Format, Aufruf, Zwischenablage und Installation | HANDBUCH | INTERPRETER |
| `C8205-Knotengraph_A4.pdf` | Knotengraph | Ablaufplan der Befehlsverarbeitung (Phasen I bis IV) als Knoten- und Testgraph | DIAGRAMM | RECHNER UND REGELWERK |
| `C8205-Knotentabellen_A4.pdf` | Knotentabellen | Knotentabelle und Variablentabelle T2 im Wortlaut der Quellen | REFERENZ | RECHNER UND REGELWERK |
| `C8205-Einzelbefehlsliste_A4.pdf` | Einzelbefehlsliste | Generische Befehlsbeschreibung und vollständige Übersicht der Einzelbefehle | REFERENZ | RECHNER UND REGELWERK |
| `C8205-Kodetabellen_A4.pdf` | Kodetabellen | Zeichenkodetabelle des C 8205: R-300-Lochstreifenkode (Tabelle 1) | REFERENZ | RECHNER UND REGELWERK |
| `C8205-BIS_A4.pdf` | Bausteininterpretationssystem | Bausteine, Kleines Eingabeprogramm (KEP) und Minimalprogramm | BESCHREIBUNG | BIS |
| `C8205-Assemblerdokumentation_A4.pdf` | Assemblerdokumentation | Cross-Assembler c82ass: Installation, Sprachdefinition, Anweisungen, Makros und Prüfbericht | BESCHREIBUNG | ASSEMBLER |
| `C8205-Projektstruktur_A4.pdf` | Projektstruktur | Verzeichnisse, Skripte und erzeugte Dateien des Gesamtprojekts: welcher Pfad wofür zuständig ist | RICHTLINIE | GESAMTPROJEKT |
| `C8205-PDF_Gestaltungsrichtlinie_A4.pdf` | PDF-Gestaltungsrichtlinie | Seitenformat, Folgeseiten, Deckblatt, Farben und Kachelung aller PDF-Ausgaben | RICHTLINIE | GESAMTPROJEKT |
| `C8205-Testuebersicht_A4.pdf` | Testübersicht | Alle Tests mit Inhalt, Geräte- und Vergleichsdateien und zugehörigem ASM-Quelltext | REFERENZ | INTERPRETER |
| `C8205-PDF_Gestaltungsrichtlinie_A4.pdf` | PDF-Gestaltungsrichtlinie | Seitenformat, Folgeseiten, Deckblatt, Farben und Kachelung aller PDF-Ausgaben | RICHTLINIE | GESAMTPROJEKT |

- Bei Kachel-PDFs (`Knotengraph`) steht zusätzlich die Zeile „Layoutraster“ im Angabenblock; Lesereihenfolge, Kurzcodes,
  Konnektoren und die Legenden der Knoten-, Symbol- und Kantentypen stehen auf Seite 2 (4.4).


### 4.7 Umsetzung (Hinweis, keine Gestaltungsvorgabe)

- Das Deckblatt wird von **einer gemeinsamen Funktion** in `pdflib.py` gezeichnet, direkt auf den Canvas (eigene
  Seitenvorlage ohne Kopf- und Fußzeile), nicht als Fließtext. `md2pdf.py`, `erzeuge_rechnerbeschreibung_pdf.py`,
  `build_testhandbuch.py` und `erzeuge_knoten_pdfs.py` rufen sie auf, damit das Deckblatt nicht je Skript nachgebaut wird.
- Die Gesamtseitenzahl für „Umfang“ stammt aus dem zweiten Durchlauf, wie die Angabe „Seite X / Y“.
- Welche Skripte noch von den Abschnitten 3a und 4 abweichen, steht in 3a.7.
- Die PDF-Dokumenteigenschaften übernehmen das Deckblatt: Titel = Deckblatt-Titel; Autor = „C8205-Interpreter-Projekt“
  (bisher uneinheitlich, auch „C 8205 Projekt“); Betreff = Dokumentart und Quelle(n) mit Version.


## 5. Farbcodierung (projektweit einheitlich, nicht nur für den Knotengraphen)

| Farbe/Stil | Bedeutung |
|---|---|
| Grün, durchgezogen | positiv / wahr / OK |
| Rot, gestrichelt | negativ / falsch / Fehler |
| Schwarz | neutraler Standardfluss, unbedingte Weiterschaltung |
| Grau, punktiert | indirekte Verbindung / Verweis (z. B. Konnektorsprung, Querverweis auf andere Tabelle) |
| Blau, Balken links (Kasten) | Hinweis: nützliche Ergänzung (3a.4) |
| Orange, Balken links (Kasten) | Achtung: Stelle, an der man sich leicht irrt oder Hardware und Interpreter abweichen (3a.4) |

Formen (für Graphen/Ablaufpläne):

| Form | Bedeutung |
|---|---|
| Ellipse | Konnektor / Verweis, kein eigener Ablaufschritt |
| Parallelogramm | Phasenübergang / Abschnittsmarke |
| Rechteck | Anweisung / Aktion |
| Raute | Test / Verzweigung |
| Rechteck, doppelt umrandet | Endzustand |

## 6. Große Inhalte: feste Kachelung statt automatischer Optimierung

Bewährtes Vorgehen (aus dem Knotengraphen übernommen), wenn ein Inhalt nicht auf eine A4-Seite passt:

1. Feste Spaltenanzahl wählen (z. B. 2), NICHT die von Graphviz/Layout-Tool automatisch optimierte
   Kachelanzahl verwenden – letztere führt zu unübersichtlich vielen, teils fast leeren Seiten.
2. Die Gesamtbreite des Originalinhalts auf exakt diese Spaltenzahl herunterskalieren (Skalierungsfaktor
   = (Spalten × Kachelbreite − Überlappung) / Originalbreite). Schrift bleibt dadurch bei einer moderaten
   Verkleinerung (Richtwert: nicht unter ca. 85–90 % der Originalgröße) noch gut lesbar.
3. Zeilenanzahl ergibt sich aus der (skalierten) Gesamthöhe und der Kachelhöhe.
4. Überlappung zwischen Nachbarkacheln: ca. 20 pt (≈ 7 mm), damit Linien/Kanten über Seitengrenzen
   hinweg optisch weiterverfolgt werden können.
5. Keine eingebettete Mini-Übersichtskarte pro Seite (unnötig groß in der Dateigröße, fehleranfällig bei
   der Rechteck-Koordinatenberechnung). Stattdessen genügt die Zeile/Spalte-Angabe in der Kopfzeile in
   Verbindung mit der festen, vorhersagbaren Lesereihenfolge (zeilenweise, links→rechts, oben→unten).

## 6a. Fließtext-/Tabellendokumente (Befehlsliste, Kodetabellen, ...)

Für reine Text-/Tabellendokumente (kein Diagramm, keine Kachelung nach Abschnitt 6) gilt zusätzlich (die Schrift ist
nach Abschnitt 2 ohnehin DejaVu Sans):

- **Schrift:** Enthält die Quelle Unicode-Sonderzeichen aus der Mathematik/Notation (Hoch-/Tiefzahlen
  z. B. z₃₀, Winkelklammern ⟨AC⟩, Logikzeichen ∧ ∨, Vergleichszeichen ≤ ≥ ≠, Pfeile →), reicht der
  PDF-Basisfont Helvetica NICHT aus (fehlende Glyphen erscheinen als Kästchen). Stattdessen DejaVu Sans
  (Regular/Bold/Oblique/BoldOblique) aus `/usr/share/fonts/truetype/dejavu/` einbetten und als Font
  registrieren. Die in Abschnitt 2 genannte ASCII-Ersatzschreibweise (z12 statt z₁₂) bleibt die
  bevorzugte Lösung für selbst erzeugte Beschriftungen (Diagramme, Legenden); bei der Übernahme von
  Fließtext aus einer .md-Quelle ist der Unicode-Font der pragmatischere Weg, da Hunderte Einzelstellen
  sonst manuell übersetzt werden müssten.
- **Absätze zusammenführen, nicht zeilenweise setzen:** Die Quelldateien sind im Fließtext weich
  umgebrochen (mehrere kurze Zeilen ohne Leerzeile = EIN Absatz/Listenpunkt). Der Konverter muss
  zusammenhängende Zeilen (auch über Zeilenumbrüche hinweg) zu einem Absatz/Listenpunkt
  zusammenfügen, bevor daraus ein PDF-Paragraph wird — sonst entstehen unnötige Zeilenumbrüche und
  mehrzeilige Inline-Formatierungen (**fett**/*kursiv* über Zeilengrenzen) werden nicht erkannt.
- **Lochbild-/Bitmuster-Spalten:** als Kreisgrafik statt Text/Zahlen darstellen (● = gelocht/gesetzt,
  ○ = nicht gelocht/nicht gesetzt), in der von der Quelle vorgegebenen Spurreihenfolge; Spaltenkopf um
  die Reihenfolge ergänzen (z. B. "Lochbild (w v u p 8 4 2 1)"). Bewährt sich für jede Bit-für-Bit-
  Spalte, nicht nur Lochstreifen.
- **Tabellenspaltenbreite:** proportional zur mittleren Zeicheninhaltslänge je Spalte verteilen, mit
  Mindestbreite (~30 pt bei 8,5 pt Schrift), sonst brechen kurze Spalten (Nr., einzelne Codes) mitten
  im Inhalt um. Kommagetrennte Listen ohne Leerzeichen ("0,1,2,3") vor dem Rendern mit Leerzeichen nach
  jedem Komma versehen, sonst kein Umbruchpunkt vorhanden.
- **Abbildungen:** Eine Zeile `![Bildunterschrift](abbildungen/Datei.png)` (Pfad relativ zur .md-Datei) setzt `md2pdf.py`
  als Abbildung mit Bildunterschrift (`pdflib.bild`): linksbündig, Bildunterschrift nach 3a.2, Abbildung und Bildunterschrift
  zusammen (3a.6). Folgt unmittelbar ein Absatz, der nur aus einer kursiven Zeile `*Abbildung N: ...*` besteht (so zeigt
  GitHub ihn unter dem Bild), ist er die Bildunterschrift; sonst gilt der Text in den eckigen Klammern. Die Druckgröße ergibt
  sich aus der Pixelzahl und der im PNG gespeicherten Auflösung (dpi), begrenzt auf die Satzspiegelbreite und 340 pt Höhe;
  ohne Angabe gelten 72 dpi. Fehlt die Bilddatei, bricht die Erzeugung ab. Selbst gezeichnete Abbildungen
  (`PDF/pdf-layout-scripte/zeichne_abbildungen.py`) verwenden die Farben von 3a/4 und werden 1:1 gesetzt, ihre Schrift ist deshalb mindestens
  etwa 6 pt groß.

## 7. Werkzeuge

- Graphviz (`dot`) für Diagramme/Graphen (Ausgabe zunächst als einseitiges Vektor-PDF in Originalgröße,
  keine Skalierung/Kachelung durch Graphviz selbst).
- reportlab für Text-, Tabellen- und Referenzseiten sowie für die Kopf-/Fußzeilen-Overlays der Kachelseiten.
- pypdf (`Transformation`, `merge_transformed_page`) zum Skalieren, Verschieben und Zusammenführen.
- pdftoppm (poppler) nur für die visuelle Kontrolle während der Erstellung – wird NICHT in das finale PDF
  eingebettet (Dateigröße).

## 8. Dateibenennung

Muster: `C8205-<Inhalt>_A4.pdf`, Bindestrich-getrennt, `_A4`-Suffix bei allen A4-PDFs, auch bei einfachen
Text-/Tabellendokumenten ohne Kachelung (Praxis seit 2026-10-02; nur bei Dokumenten in einem anderen Format
entfällt er). Bisher (die Reihenfolge mehrerer Quellen ist die Reihenfolge auf dem Deckblatt, Abschnitt 4.2):

- `C8205-Knotengraph_A4.pdf` (Quellen: C8205-Interpreter-Eingänge_der_Knoten.md und
  C8205-Interpreter-Beschreibung_der_Knoten.md)
- `C8205-Knotentabellen_A4.pdf` (Quellen: dieselben beiden Dateien; Knotentabelle, Variablentabelle T2 und die
  Kommentare der Quellen im Wortlaut, ergänzt den Knotengraph um die Tabellenform)
- `C8205-Einzelbefehlsliste_A4.pdf` (Quelle: C8205-Interpreter-Befehlsliste.md)
- `C8205-Kodetabellen_A4.pdf` (Quelle: C8205-Interpreter-Kodetabellen.md)
- `C8205-Projektueberblick_A4.pdf` (Quelle: C8205-Interpreter-Projektueberblick.md)
- `C8205-Einstieg_fuer_Neueinsteiger_A4.pdf` (Quelle: C8205-Einstieg_fuer_Neueinsteiger.md; Wortlaut nach Abschnitt 6a, erzeugt mit
  `PDF/pdf-layout-scripte/erzeuge_einstieg_pdf.py`, das `md2pdf.py` aufruft)
- `C8205-BIS_A4.pdf` (Quelle: C8205-Interpreter-BIS.md; Fließtext und Tabellen nach Abschnitt 6a, ohne Kachelung)
- `C8205-Durchfuehrung_eines_Tests_A4.pdf` (Quelle: C8205-Interpreter-Durchführung_eines_Tests.md; Wortlaut nach
  Abschnitt 6a, erzeugt mit `PDF/pdf-layout-scripte/erzeuge_durchfuehrung_pdf.py`, das `md2pdf.py` aufruft)
- `C8205-GRAFIK_Beschreibung_A4.pdf` (Quelle: C8205-Interpreter-GRAFIK_Beschreibung.md; Wortlaut nach
  Abschnitt 6a, erzeugt mit `PDF/pdf-layout-scripte/erzeuge_grafik_beschreibung_pdf.py`, das `md2pdf.py` aufruft)
- `C8205-GRAFIK_Pruefverfahren_A4.pdf` (Quelle: C8205-Interpreter-GRAFIK_Pruefverfahren.md; Wortlaut nach
  Abschnitt 6a, erzeugt mit `PDF/pdf-layout-scripte/erzeuge_grafik_pruefverfahren_pdf.py`, das `md2pdf.py` aufruft)
- `C8205-Lochstreifen-Hilfsprogramme_A4.pdf` (Quelle: C8205-Interpreter-Lochstreifen-Hilfsprogramme.md; Wortlaut nach Abschnitt 6a,
  erzeugt mit `PDF/pdf-layout-scripte/erzeuge_lochstreifen_hilfsprogramme_pdf.py`, das `md2pdf.py` aufruft)
- `C8205-Rechnerbeschreibung_A4.pdf` (redaktionell; erzeugt mit `PDF/pdf-layout-scripte/erzeuge_rechnerbeschreibung_pdf.py`, Bausteine aus `pdflib.py`; Stand 08.10.2026)
- `C8205-Bedienpult_und_Peripherie_A4.pdf` (redaktionell; Quellen: C8205-Interpreter-Bedienpult_mit_Schaltern.md und
  C8205-Interpreter-Lochstreifenleser.md; ergänzend herangezogen, aber nicht auf dem Deckblatt:
  Datenstruktur_und_Verarbeitungseinheiten.md und Kodetabellen.md; erzeugt mit
  `PDF/pdf-layout-scripte/erzeuge_bedienpult_peripherie_pdf.py`, Bausteine aus `pdflib.py`)
- `C8205-Bedienungsanleitung_Interpreter_A4.pdf` (redaktionell; Quellen: C8205-Interpreter-Python_Interpreter.md und
  C8205-Interpreter-Durchführung_eines_Tests.md)
- `C8205-Testhandbuch_A4.pdf` (redaktionell; Quelle: C8205-Interpreter-Durchführung_eines_Tests.md)
- `C8205-Assemblerdokumentation_A4.pdf` (Quelle: C8205_Assembler_Dokumentation.md; Wortlaut nach Abschnitt 6a, erzeugt
  mit `PDF/pdf-layout-scripte/md2pdf.py`; liegt in `Assembler/Dokumentation/` neben der .odt und der .md)
- `C8205-Projektstruktur_A4.pdf` (Quelle: C8205-Projektstruktur.md; Wortlaut nach Abschnitt 6a, erzeugt mit
  `PDF/pdf-layout-scripte/erzeuge_projektstruktur_pdf.py`, das `md2pdf.py` aufruft)
- `C8205-PDF_Gestaltungsrichtlinie_A4.pdf` (Quelle: C8205-Interpreter-PDF.md, diese Datei; Wortlaut nach Abschnitt 6a, erzeugt
  mit `PDF/pdf-layout-scripte/md2pdf.py`)
- `C8205-Testuebersicht_A4.pdf` (Quelle: `CSV/test_tabelle.md`, von `CSV/test_tabelle.py` aus `Tests/` und `Assembler/` erzeugt; Tabelle nach
  Abschnitt 3a.3, erzeugt mit `CSV/pdf-layout-scripte/erzeuge_testuebersicht_pdf.py`, das weder `md2pdf.py` noch `pdflib` braucht; liegt in `CSV/`)

## 9. Änderungsprotokoll

Neueste Änderung zuerst. Erledigte Einträge werden gestrichen; zurzeit gibt es keine offenen Einträge.

| Datum | Änderung | Abschnitt |
|---|---|---|

