# CHECKPOINT 25.10.2026 - Pult C8205Z und Zusatztrommeln

## Kurzstand (hier anfangen)
1. Pult-Zeichnung (Z-Ausführung, 30+4 Lampen) ruht: SVG/PNG und nummerierte Fassung (158 Elemente, elemente.csv) liegen bei; Beschriftungen ab Lampe L18, Ziffernblock und Zusatztasten sind Platzhalter bzw. geraten. Warten auf Fotos aus der Technischen Sammlung Dresden (Hinweise zum Fotografieren im Verlauf gegeben).
2. Das Zip-Pult des Simulators (pult/, 1148x860) ist das Standardpult; die Z-Zeichnung ist davon unabhängig. Assembler und Simulatorcode wurden NICHT geändert.
3. Aktuelles Thema: Arbeitsweise der 4 Zusatztrommeln (nur C8205Z). GÜLTIG ist Schritt 9 (Berichtigung): Block = 8 physisch aufeinanderfolgende HT-Sektoren ab Position 0/8/16/24 (logisch 00/10/20/30), HT-Zeit je Block höchstens 4,16 ms, Spur mit Doppelpuffer höchstens 84,2 ms, ZT je Block ein Umlauf (20 ms); Faktor ZT/HT = 6. ÜBERHOLT sind die HT-Zahlen und die Blockdefinition aus Schritt 6 bis 8.
4. Nächster Schritt: Zeitmodell/Spezifikation der ZT (Anwahl 5100..5400 030, Adreßtransport aaaa 032, Ausgabe bbbb 401, Eingabe bbbb 461, je 8 Worte, zwei alternierende Puffer; Parameter g = ZT-Mindestabstand, Vorgabe offen). Vorlage: c-module/trommel.c (Wortzeit 104 us), Magnettrommel.md, Anhang A.
5. Offene Fragen an den Inhaber: Zuordnung 5100..5400 zu T1..T4; g festlegen; Schritt-Tabellen 6 bis 8 verwerfen oder löschen; Bedeutung der Matrix links am Z-Pult.

---

# aufgabe – Bedienpult-Grafik (Stand 25.10.2026)

## Erledigt
- Pult als SVG nachgezeichnet (gen.py -> bedienpult.svg, viewBox 1024x461), PNG 1024 und 2048.
- Tasten sind je <g class="key" id="key-..."> mit .face (für späteren Klick-Effekt: Klasse .down verschiebt 2px).
- Lampen: <g class="lamp" id="lamp-XX">, Klasse .on schaltet an; H ist .red.
- LEDs: id ar-led0..11, ur-led0..7, ur-led-red.

## Schritt 2: Nummerierung
- Nummerierte Variante erzeugt (python3 gen.py --num): bedienpult_nummeriert.svg, PNG 2048/3072, elemente.csv (158 Elemente).
- Nr. 1-30 Lampen oben, 31-34 T-Lampen, 35-46 AR-LEDs, 47-54 UR-LEDs, 55 rote LED, 56 Schlüsselschalter,
  57-86 Matrix links, 87-101 orange Tasten, 102-107 graue Tasten oben, 108-131 Reihen 2/3, 132-141 OR-Block, 142-158 Ziffernblock.
- Nächster Schritt: Beschreibungen des Nutzers pro Nr. in elemente.csv (Spalte 5) einarbeiten.

## Offen / zu prüfen
- CLAUDE.md-Zip lag nicht bei den Uploads -> Konventionen/Stand nicht berücksichtigt; Zip bitte erneut hochladen.
- Lampenbeschriftung ab Lampe 18 (L18..L30) auf dem Foto unleserlich -> Platzhalter.
- Ziffernblock rechts (hex C..0) und breite Taste darunter: Beschriftung geraten.
- Reihe 2, Gruppe 3: linke Taste unbeschriftet, "A","F" geraten; Gruppenüberschrift "UR" geraten.
- Orange/graue Datentasten oben unbeschriftet (so im Foto).
- Assembler unberührt (keine Versionsdateien nötig).

## Schritt 3 (Zip ausgewertet)
- CLAUDE.md, aufgabe und Bedienpult-Doku gelesen (C8205-Interpreter-Bedienpult_mit_Schaltern.md, pult/pult_manifest.json im Gesamt-Zip).
- Befund: Die Doku beschreibt das Standardpult (15 große Lampen E A T SW K1 K2 K3 FE FÜ BS US R H B N, Reihen AR 12, OR 9, V1/V2; Tasten K0-K3, SP, BS, LS, SW, H R E M G Ü ST, Zeicheneingabe). Das Foto zeigt eine andere Ausführung (30 + 4 Lampen, Matrix T4..T1/1..1000, Tasten UW S2 S1, AR/HS/SWI/SWII, K0..K7?). Dafür gibt es im Zip keine Beschreibung.
- elemente.csv: neue Spalte "Vorschlag aus Doku" für 14 gesicherte Elemente (H, R, A, E, OR-Block).
- Offen: Beschriftung/Bedeutung der Z-Zusatzelemente; Rückfrage an Inhaber (Originalunterlage zum Z-Pult?).
- Das Pult im Simulator (pult/, 1148x860) ist das Standardpult; die SVG-Nachzeichnung ist eine Z-Ausführung -> klären, welches Pult der Simulator zeigen soll.

## Schritt 4: Zusatztrommeln (Angaben des Inhabers)
- C8205Z hat neben der Haupttrommel 4 Zusatztrommeln (je 4096 Worte, 128 Spuren x 32 Sektoren, 3000 U/min, 20 ms/Umdrehung, 0,625 ms/Wort). Anwahl 5100..5400 030 (Zuordnung zu T1-T4 nicht ermittelbar), Zusatzadresse aaaa 032, Ausgabe bbbb 401, Eingabe bbbb 461, je 8 Worte geometrisch.
- Hypothese Pult: Lampen T4..T1 (Nr. 31-34) = Zusatztrommel 1-4; Matrix links (Nr. 57-86, Spalten T4..T1, Gewichte 1/2/4/10 und 40..1000 oktal) gehört vermutlich zu den Trommeln (Adress-/Bahnwahl oder Sperre) - ungeprüft, Foto aus Dresden klärt es.
- Rückfrage: "0,525 ms" (Elektronik/Gruppenbefehl) vs. "0,625 ms" (Zusatztrommel je Wort) - Tippfehler oder zwei verschiedene Werte?
- Geprüft: beide Sektorfolgen sind Permutationen von 00..37; die Zusatzfolge ist die spaltenweise Lesung der Haupttrommelfolge (4 Zeilen x 8).

## Schritt 5: Zusatztrommel-Arbeitsweise (Rekonstruktion, nur Analyse, kein Code)
- Pult-Zeichnung ruht (Inhaber, 25.10.2026); Thema jetzt: Zusammenspiel Haupttrommel/Zusatztrommel (ZT).
- Nachgerechnet (Doku Magnettrommel, c-module/trommel.c: Wortzeit 104 us): Haupttrommel Umlauf 3,328 ms, logischer Schritt +5 Positionen = 0,52 ms, 8 Worte = 4,16 ms. ZT: 20 ms/Umlauf = 6,01 x Haupttrommel, 0,625 ms/Sektor.
- Befund: ZT-Folge, jede 4. Position gelesen (zt[k::4]), ergibt exakt die vier physischen Achtergruppen der Haupttrommel. Beziehung: Haupttrommel-Position q = 8*(p mod 4) + p div 4.
- Zeit je Spur (4 Blöcke zu 8): mit Doppelpuffer 4*20 + 4,16 = 84,2 ms (Angabe 85 ms stimmt), ohne Überlappung 96,6 ms.
- Offen (Inhaber): (1) Faktor 4 oder 6 zwischen den Trommeln (Rechnung: 6); (2) überträgt ein E/A-Befehl 8 Worte (1 Block) oder 32 (ganze Spur); (3) 0,525 vs 0,625 ms (Rechnung: 0,52 = Haupttrommel-Wortschritt, 0,625 = ZT-Sektor, beide stimmen).

## Schritt 6: Entscheidungen und Befund Blockdefinition
- Entschieden (Inhaber): ein E/A-Befehl überträgt 8 Worte (Block), nicht die Spur (Kosten, Pufferbits 8x33). Faktor ZT/HT = 6 (Rechenfehler "4" berichtigt).
- Korrektur: 32 Worte logisch auf der HT = 160 Slots = 5,0 Umdrehungen (16,64 ms), nicht 4.
- Befund: HT-Zeit je Block hängt von der Blockdefinition ab: 8 logisch aufeinanderfolgende Worte (xx00-xx07) = 40 Slots = 4,16 ms; physische Achtergruppe (Positionen 0-7, = jede 4. ZT-Position) = 132 Slots = 13,73 ms. Spur: 84,2 ms bzw. 93,7 ms mit Doppelpuffer.
- Offen: Blockdefinition (logisch xx00-07 oder physische Gruppe) und daraus die ZT-Nummerierung.

## Schritt 7: Blockdefinition geklärt
- Entschieden (Inhaber): Block = 8 aufeinanderfolgende Adressen, nur ab Anfangsadressen mit letzter Oktalziffer 0 (xx00, xx10, xx20, xx30). Grund: Befehl hat 12 Bit Adresse (aaaa) + BAZ; ZT-Adresse 9 wirksame Bit; sonst keine eindeutige Zuordnung HT<->ZT.
- Folge: HT-Zeit je Block 4,16 ms, Spur mit Doppelpuffer 84,2 ms (Variante "physische Gruppe" 93,7 ms entfällt).
- Gerechnet: mit der ZT-Nummerierung des Inhabers liegen die 8 Worte eines Blocks in einem Bogen von 16,25 bis 16,9 ms (<20 ms), mit HT-Nummerierung 17,5 ms; kleinster Abstand zweier Worte 2 Sektoren (1,25 ms). "Nur jede 4. Zelle" ist daher zeitlich nicht erzwungen (0,625 ms Sektor > 0,52 ms Zyklus).
- Offen: Ist "ZT nur jede 4. Zelle" gesicherte Angabe oder Annahme? Danach Zeitmodell (Anwahl 5k00 030, aaaa 032, bbb0 401/461, 2 Puffer).

## Schritt 8: ZT-Mindestabstand g als Parameter
- "ZT nur jede 4. Zelle" ist Überlegung des Inhabers, keine gesicherte Angabe. Modellparameter g = Mindestabstand zweier ZT-Zugriffe in Sektoren (0,625 ms je Sektor); Vorgabe offen (HT-Elektronik: 0,52 ms Zyklus -> g=1).
- Blockzeit (8 Worte, aligniert xxx0-xxx7) in Umläufen: Liste des Inhabers g<=2: 16,2-16,9 ms, g=3: 19,4-31,9 ms, g=4: 33,1 ms (>1 Umlauf, also unverträglich mit g=4); HT-Nummerierung g<=2: 17,5 ms, g>=3: 22,5 ms; transponiert (Position p=4i+k, Wort i, Block k): 18,1 ms für g=1..4.
- Folgerung: Soll g=4 gelten, muss die ZT-Nummerierung "transponiert" sein (die 8 Worte eines Blocks genau 4 Sektoren auseinander); die Liste des Inhabers passt dann nicht. Bei g<=2 ist sie die schnellste.
- Offen: g festlegen (Entscheidung Inhaber) und Nummerierung; dann Zeitmodell.

## Schritt 9: BERICHTIGUNG (Hinweis Inhaber: G/GX/W/WX greifen mit einer Umdrehung auf alle Zellen zu)
- Befehlsliste 4.1.5: Gruppenbefehl durchläuft Phase IV für alle 32 Zellen der Spur "in der Reihenfolge ihrer geometrischen Anordnung" = aufeinanderfolgende physische Sektoren, je 104 us, ein Umlauf 3,33 ms. Mein Ansatz "Mindestabstand 5 Positionen" gilt nur für getrennte Einzelbefehle (Befehlsfolge), nicht für G/GX/W/WX und damit nicht für den ZT-Transfer.
- Damit entfallen: "32 Worte = 5 Umdrehungen", "physische Gruppe = 13,7 ms / Spur 93,7 ms" und die Festlegung Block = xxx0-xxx7 aus Schritt 7. Die Tabellen der Schritte 6 bis 8 (HT-Zeit) sind überholt.
- Richtig: Block = 8 physisch aufeinanderfolgende HT-Sektoren, Start nur auf Position 0, 8, 16, 24 = logische Sektoren 00, 10, 20, 30 (Haupttrommel-Folge: Positionen 0/8/16/24). Das erklärt "Anfangsadressen xx00, xx10, xx20, xx30" und die Identität "jede 4. ZT-Position = eine HT-Achtergruppe".
- HT-Zeit je Block: 8 x 104 us = 0,83 ms Übertragung + Wartezeit auf den Gruppenanfang 0..3,33 ms, also höchstens 40 Wortzeiten = 4,16 ms (= die 4,2 ms des Inhabers, als Höchstwert). Spur mit Doppelpuffer höchstens 4 x 20 + 4,16 = 84,2 ms, im Mittel rund 82,5 ms.
- ZT je Block: Positionen p = k (mod 4), 8 Zellen im Abstand 4 Sektoren = ein Umlauf (rund 18 bis 20 ms inkl. Anlaufwartezeit).
- Offen: g (ZT-Mindestabstand) bleibt Parameter; Puffer bleibt sinnvoll (ZT-Zellen kommen alle 2,5 ms, HT-Zielsektoren aber 0,104 ms auseinander: erst sammeln, dann in 0,83 ms schreiben).
