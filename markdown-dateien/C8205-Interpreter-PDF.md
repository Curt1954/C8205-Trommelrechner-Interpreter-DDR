** PDF-Gestaltungsrichtlinie (Wurzeldokument für alle PDF-Ausgaben) **

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
  - Haupttitel Deckblatt: 16 pt fett
  - Abschnittsüberschriften: 12 pt fett
  - Fließtext / Hinweise: 9–10 pt
  - Tabellen-/Referenzzeilen: 8,5 pt (nicht kleiner, sonst nicht mehr gut lesbar im Druck)
  - Kopfzeile Inhaltsseite: 11 pt fett (Titel) + 8 pt (Legende/Unterzeile)
  - Fußzeile: 7,5 pt
- Unicode-Hochzahlen/-Tiefzahlen (₀₁₂₃…, ⁰¹²³…) in Diagrammen mit Helvetica (Knotengraph) NICHT verwenden (der
  Basisfont stellt sie als Kästchen dar). Stattdessen ASCII-Schreibweise wie z12, z30 oder reportlab-Tags (<sub>/<super>).

## 3. Kopf- und Fußzeile jeder Inhaltsseite

- Kopfzeile links: Kurztitel des Dokuments + bei mehrseitigen/gekachelten Inhalten die Position, z. B.
  "Blatt 3/12 (Zeile 2/6, Spalte 1/2)".
- Kopfzeile, zweite Zeile: kompakte Legende der verwendeten Farben/Symbole (siehe Abschnitt 5), sofern
  auf der Seite relevant – Wiederholung auf jeder Seite, damit Einzelblätter für sich verständlich bleiben.
- Fußzeile links: Kurzhinweis, falls Kacheln überlappen ("Kacheln überlappen sich ca. 7 mm …").
- Fußzeile rechts: "Seite X / Y" (absolute Seitenzahl im Gesamt-PDF, nicht nur innerhalb eines Abschnitts).

## 4. Deckblatt und Referenzseiten

- Erste Seite: Titel, Kurzbeschreibung (Quelldatei(en), Umfang), Layoutraster ("N Zeile(n) × M Spalten =
  N·M A4-Seiten, Skalierung X %"), Lesereihenfolge-Hinweis, Legende Knoten-/Symboltypen, Legende Kanten/
  Farben, sonstige Hinweise.
- Falls im Inhalt Kurzcodes verwendet werden (z. B. A-nnn für ANWEISUNG-nnn), folgt eine eigene
  Referenzseite (ggf. mehrseitig) mit Kurzcode → Volltext, bevor der eigentliche Inhalt beginnt.
- Nach der letzten Referenzseite: eine Leerseite einfügen, damit die nachfolgenden Kachelseiten ab der
  ersten Doppelseiten-Ansicht paarweise (Spalte 1 links / Spalte 2 rechts einer Zeile) sichtbar sind.

## 5. Farbcodierung (projektweit einheitlich, nicht nur für den Knotengraphen)

| Farbe/Stil | Bedeutung |
|---|---|
| Grün, durchgezogen | positiv / wahr / OK |
| Rot, gestrichelt | negativ / falsch / Fehler |
| Schwarz | neutraler Standardfluss, unbedingte Weiterschaltung |
| Grau, punktiert | indirekte Verbindung / Verweis (z. B. Konnektorsprung, Querverweis auf andere Tabelle) |

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
entfällt er). Bisher:

- `C8205-Knotengraph_A4.pdf` (Quellen: C8205-Interpreter-Eingänge_der_Knoten.md und
  C8205-Interpreter-Beschreibung_der_Knoten.md)
- `C8205-Knotentabellen_A4.pdf` (Quellen: dieselben beiden Dateien; Knotentabelle, Variablentabelle T2 und die
  Kommentare der Quellen im Wortlaut, ergänzt den Knotengraph um die Tabellenform)
- `C8205-Einzelbefehlsliste_A4.pdf` (Quelle: C8205-Interpreter-Befehlsliste.md)
- `C8205-Kodetabellen_A4.pdf` (Quelle: C8205-Interpreter-Kodetabellen.md)
- `C8205-Projektueberblick_A4.pdf` (Quelle: C8205-Interpreter-Projektueberblick.md)
- `C8205-Rechnerbeschreibung_A4.pdf`, `C8205-Bedienpult_und_Peripherie_A4.pdf`,
  `C8205-Bedienungsanleitung_Interpreter_A4.pdf`, `C8205-Testhandbuch_A4.pdf` (redaktionell)
- `C8205_Assembler_Dokumentation.pdf` (Export aus der .odt mit LibreOffice, nicht nach dieser Richtlinie;
  Ausnahme vom Namensmuster, da der Name der Quelle übernommen wird)

## 9. Änderungsprotokoll

Neueste Änderung zuerst. Einträge vom 2026-10-02 sind aus den Entscheidungsvermerken in Abschnitt 2 und 8 übernommen
(das Protokoll war bis dahin leer).

| Datum | Änderung | Abschnitt |
|---|---|---|
| 2026-10-05 | `C8205-Knotentabellen_A4.pdf` in die Liste der PDFs aufgenommen (Quellen angegeben); bei `C8205-Knotengraph_A4.pdf` ebenfalls die Quellen ergänzt. | 8 |
| 2026-10-05 | Verweis in der Einleitung berichtigt: Das Änderungsprotokoll ist Abschnitt 9 (stand fälschlich als Abschnitt 8, das ist die Dateibenennung). | Einleitung |
| 2026-10-05 | Änderungsprotokoll angelegt und mit den bisher nur im Text vermerkten Entscheidungen gefüllt. | 9 |
| 2026-10-02 | Schrift: einheitlich DejaVu Sans / Bold / Mono für alle Dokumente; Ausnahme Knotengraph (Kacheln bleiben Helvetica). Grund: Helvetica stellt die Unicode-Notation nicht dar. | 2, 6a |
| 2026-10-02 | Dateinamen: Suffix `_A4` bei allen A4-PDFs, auch bei einfachen Text-/Tabellendokumenten ohne Kachelung. | 8 |

