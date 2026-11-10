; fk_ausgabe.asm  --  Projekt_Festkomma: gebrochene Festkommazahl (dwf-Format) zur Basis 10 ausgeben (fk_ausgabe) und einlesen (fk_eingabe)
; STAND 08.11.2026: fk_ausgabe und fk_eingabe in einer Datei, gemeinsame Zeichentabelle, analog zu gk_ausgabe.asm (Projekt_Gleitkomma). Siehe Datei aufgabe.
; Die UP selbst stehen seit 08.11.2026 als Makro FK_AUSGABE in Assembler/Sourcecode/c82ass.makros (Parameter = Anfangswert der Stellenzahl, immer beide UP und die Tabelle, nur einmal erzeugt). Diese Datei ist das Testprogramm dazu:
; sie ruft FK_AUSGABE auf und enthaelt das Testhauptprogramm. Der erzeugte Code ist mit dem frueheren Quelltext Zelle fuer Zelle gleich (Vergleich .obj).
;
; PARAMETER (Festlegung 031 bis 033, Rangfolge 2): Jedes der beiden UP hat einen eigenen Parameterblock mit einer Parameterzelle: die Zahl der Dezimalstellen hinter dem Komma
;   (ganze Zahl 0 bis 9, nicht geprueft). Aufbau je UP: erste Zelle 000 *+2 (Sprung ueber den Parameter), dann die Parameterzelle (fk_as bei fk_ausgabe, fk_es bei fk_eingabe), dann der Code.
;   Der Aufrufer schreibt die Stellenzahl VOR dem Aufruf in die Parameterzelle des UP (240 fk_as bzw. 240 fk_es); sie bleibt erhalten, bis er sie aendert, und wird nie veraendert.
;   Nicht Register R1 (die beiden UP rufen mit prdig ein eigenes UP auf). Die Zahl selbst geht im AC hinein (fk_ausgabe) bzw. heraus (fk_eingabe, Festlegung 032); das Rueckkehrwort
;   legt der Aufrufer wie bei gk nach fk_rueck bzw. fk_rueck_ein (kein 025, weil dabei der AC mit dem Rueckkehrwort ueberschrieben wuerde und die Zahl nicht mehr im AC stuende).
;   Das Komma gehoert nur zur Ein-/Ausgabe: im Maschinenwort steht eine ganze Zahl (Wort = x * 2^32), nur ihre Deutung als Bruch ist vereinbart.
;
; ===== UP fk_ausgabe: <AC> als gebrochene Festkommazahl zur Basis 10 auf dem angewaehlten Kanal (Schreibwerk) ausgeben, gibt nichts zurueck.
; ANNAHMEN (offen, bitte bestaetigen): B1 Zahlformat wie dwf (Doku 3.3.20): Komma zwischen z0 und z1, Wort = x * 2^32, negativ im Zweierkomplement (33 Bit),
;   Bereich -1 bis 1 - 2^-32.
;   B2 Druckbild [+|-]g,ddd (Dezimalkomma) mit fk_as Nachkommastellen, g = ganzer Teil, normal 0; bei 0 Stellen ohne Komma. Die Zahl -1 (Wort 040000000000) erscheint als -1,000.
;   Die Ausgabe wird auf fk_as Stellen gerundet (halb aufwaerts im Betrag); rundet der Betrag auf 1, so erscheint +1,000 bzw. -1,000.
;   B3 Das UP druckt nur KB-Zeichen, erwartet KB, laesst KB. B4 Aufruf ohne 025: Aufrufer legt das Rueckkehrwort nach fk_rueck,
;   laedt die Zahl in den AC, Sprung 000 fk_ausgabe. B5 Das UP zerstoert AC und eigene Zellen und die Arbeitsspur 7640 bis 7677.
;   B6 Die 9. Stelle kann in seltenen Faellen um 1 vom exakt gerundeten Wert abweichen (Multiplikation mit Rundung, Fehler hoechstens 1 Einheit von N).
; VERFAHREN: Betrag und Vorzeichen (die Zahl -1 gesondert, ihr Betrag 2^32 passt nicht in 32 Bit). N = |z| * 10^9 / 2^32 als ganze Zahl 0 bis 10^9 (9 Stellen):
;   Betrag (32-Bit-Bruch) mal 4 * 10^9 (Bruch, Multiplikation 6.1.1, 4 * 10^9 passt als Zahl in 32 Bit) ergibt 4 N, dann 2 nach rechts mit Rundung.
;   Rundung auf fk_as = k < 9: N := N + 5 * 10^(8-k).
;   Ist N >= 10^9, dann ganzer Teil 1 und N = N - 10^9. Die ersten k Ziffern durch Subtraktion der Zehnerpotenzen 10^8 bis 10^0.
;
; ===== UP fk_eingabe: liest eine Zahl vom angewaehlten Eingabekanal (K0, Schreibwerk/Tastatur) und gibt sie als dwf-Zahl im <AC> zurueck.
; Aufruf (wie B4): Aufrufer waehlt den Eingabekanal an, legt das Rueckkehrwort nach fk_rueck_ein, Sprung 000 fk_eingabe; Ergebnis im AC.
; ANNAHMEN (offen, bitte bestaetigen): C1 Eingabeform [+|-] Ziffern [, Ziffern] und ein Punkt als Eingabeende, z. B. -0,16. ; das Komma trennt die Nachkommastellen;
;   Leertaste (ZR), Zeilenschaltung (WRZL), Umschaltzeichen, Tabulator und der Buchstabe e werden uebergangen (C2: KB/GB wird nicht nachgefuehrt, Festlegung 030 offen).
;   C3 Es zaehlen die ersten fk_es Nachkommastellen; die naechste Stelle entscheidet ueber die Rundung (5 bis 9 auf, 0 bis 4 ab, Betrag; weitere Stellen werden verworfen).
;   Rundet der Betrag auf 1 oder mehr, so ist das Ergebnis +-(1 - 2^-32) (groesster darstellbarer Betrag). C4 Ist der ganzzahlige Teil ungleich 0, so ist das Ergebnis
;   das Wort -1 (040000000000), unabhaengig von Vorzeichen und Nachkommastellen: nur -1 ist als ganze Zahl darstellbar, +1 und alles ab 1 nicht (wie bei dwf, das 1 ablehnt).
;   C5 Keine Pruefung der Eingabe (Festlegung 005 sinngemaess): ein Zeichen, das nicht in der Tabelle vorgesehen ist, liefert einen Zellenwert und wirkt wie eine Ziffer.
;   C6 Das Ergebnis weicht um hoechstens 1 Einheit der letzten Binaerstelle (2^-32) vom gerundeten dwf-Wert ab (Multiplikation mit gerundeter Konstante).
;   C7 Das UP zerstoert AC, eigene Zellen und die Arbeitsspur 7640 bis 7677.
; VERFAHREN: Ziffern hinter dem Komma als ganze Zahl N (bis k = fk_es Stellen), dazu die naechste Stelle zum Runden (ab 5: N + 1), auf 9 Stellen mit Zehnern aufgefuellt; 4 N (kleiner 2^32) mal q = 2^61/10^9 (Bruch,
;   Multiplikation 6.1.1) ergibt F/2, F = Wort des Betrags = N * 2^32 / 10^9; ein Schritt nach links; Vorzeichen durch Negieren.
; Zeichentabelle tab (0100-Grenze, 64 Zellen, Festlegung 014): in den Zellen unbelegter Zeichen liegen die Zeichen-Ausgabebefehle zif,
;   die Zehnerpotenzen pw0 und alle Arbeitszellen beider UP (Eingabe und Ausgabe laufen nie gleichzeitig, sie teilen sich die Arbeitszellen).
; Zellenverwendung: nn = N, dcnt = Phase (0 vor dem Komma, 1 hinter dem Komma) bzw. Ziffernzaehler, pwv = Vorzeichenmerker bzw. Zehnerpotenz, kz = Zahl der Nachkommastellen,
;   ip = Summe der Ziffern des ganzzahligen Teils, rd = erste verworfene Ziffer (-1: keine), tmp = Ziffer, zabs = Wort bzw. Betrag, dg = Ziffer * 01000, pwi = Zeiger auf die Zehnerpotenz.
; Speicher: ohne Testhauptprogramm (im Routinebetrieb nur der Aufruf FK_AUSGABE) beginnt fk_ausgabe bei 0000, dann fk_eingabe (je mit Parameterblock), Literale in der Luecke vor tab, Zeichentabelle tab.
; Das Testhauptprogramm liegt relativ ab 02000 (hinter den UP). Ein BIS-Objektprogramm laedt nie nach 0000 bis 0377 und beschreibt keine Zelle von 0000 bis 01777;
; die Lage bestimmt der Lader mit der Leitadresse (zum Beispiel 2000: UP ab 2000, Hauptprogramm ab 4000).
;
; Testfaelle: Das Hauptprogramm liest Zahlen ein (K0, Datei Test-virtuelleGeraete/T-SW-Eingabe/fk_ausgabe.txt, jede Zahl mit Punkt beendet) und gibt jede mit fk_ausgabe aus,
;     danach vier Zahlen mit 3 Stellen und acht Worte mit je eigener Stellenzahl.
;     Erster Teil mit 9 Stellen.
;     Eingabe -0,16.  -> -0,160000000      Eingabe 0,5.   -> +0,500000000      Eingabe +0,75.  -> +0,750000000      Eingabe -0,5.        -> -0,500000000
;     Eingabe 0,1.    -> +0,100000000      Eingabe -0,1.  -> -0,100000000      Eingabe 0,999999999. -> +0,999999999  Eingabe 0,000000001. -> +0,000000001
;     Eingabe 0.      -> +0,000000000      Eingabe -1.    -> -1,000000000      Eingabe 0,123456789. -> +0,123456789  Eingabe 0,3333.        -> +0,333300000
;     Eingabe 0,0000000001234. -> +0,000000000 (10. Stelle 1: abgerundet)
;     Eingabe -0,000000001.    -> -0,000000001; Eingabe 0,9999999999. -> +1,000000000 (rundet auf 1: groesster Betrag, gedruckt als 1)
;     Zweiter Teil mit 3 Stellen: 0,12345. -> +0,123   0,1235. -> +0,124   -0,9996. -> -1,000   0,0004. -> +0,000
;     Dritter Teil: Worte unmittelbar, je mit eigener Stellenzahl (Tabelle tbl): (9, 037777777777) -> +1,000000000   (9, 040000000001) -> -1,000000000   (0, 037777777777) -> +1
;     (0, 020000000000) -> +1   (0, 010000000000) -> +0   (2, 0,1) -> +0,10   (1, -0,1) -> -0,1   (5, 0,5) -> +0,50000
;
;#TROMMEL=LEER
;#PROT STUFE=2
;#BZ=1777
;#TASTENFOLGE H SW=1 M+ E M- R
; Test: Befehlszaehler 1777 (#BZ), Tastenfolge H SW=1 M+ E M- R (E zaehlt 1 dazu: Start bei 02000); Schalter SW=1 noetig fuer die K0-Eingabe von WRZL.
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/fk_ausgabe.txt
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/fk_ausgabe
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/fk_ausgabe-sw-ausgabe.txt
                start                ; Zaehlung beginnt bei 0000 (relativ): die UP ab 0000, das Testhauptprogramm ab 02000
                FK_AUSGABE 9         ; UP fk_ausgabe, fk_eingabe und Zeichentabelle aus c82ass.makros (nur einmal erzeugt), relativ ab 0000

; ===== TESTHAUPTPROGRAMM, relativ ab 02000 (Zahl lesen, mit fk_eingabe wandeln, mit fk_ausgabe drucken). Fuer den Routinebetrieb den Abschnitt bis
; 'ENDE TESTHAUPTPROGRAMM' entfernen (der Makroaufruf FK_AUSGABE bleibt). Die UP liegen relativ ab 0000, die Lage bestimmt der Lader (Leitadresse, durch 0100 teilbar).
; Teil 1: 15 Zahlen mit 9 Stellen; Teil 2: 4 Zahlen mit 3 Stellen; Teil 3: Tabelle tbl mit Paaren (Stellenzahl, Wort), nur Ausgabe.
                equ     02000        ; relative Adresse 02000
haupt:          ANWAHL  K2           ; Kanal 2 = Schreibwerk
                KB                   ; Schreibwerk auf Kleinbuchstaben (KB) schalten
                WRZL                 ; Zeilenschaltung, danach ist K0 (Eingabe) angewaehlt
lese:           211     kk           ; Stellenzahl (Teil 1: 9, Teil 2: 3)
                240     fk_es        ; Parameter von fk_eingabe
                211     rwe          ; Rueckkehrwort der Eingabe
                240     fk_rueck_ein ; in die Rueckkehrzelle von fk_eingabe
                000     fk_eingabe   ; Zahl einlesen, Ergebnis im AC
nache:          240     zw           ; fk-Zahl merken
                211     kk           ; Stellenzahl
                240     fk_as        ; Parameter von fk_ausgabe
                ANWAHL  K2           ; Kanal 2 = Schreibwerk
                KB                   ; Schreibwerk auf Kleinbuchstaben (KB) schalten
                211     rwa          ; Rueckkehrwort der Ausgabe
                240     fk_rueck     ; in die Rueckkehrzelle von fk_ausgabe
                211     zw           ; fk-Zahl in den AC
                000     fk_ausgabe   ; Zahl ausgeben
nacha:          WRZL                 ; Zeilenschaltung, danach ist K0 (Eingabe) angewaehlt
                211     zn           ; Zaehler
                220     #1           ; - 1
                240     zn           ; merken
                050     lese         ; noch nicht fertig: naechste Zahl
                211     ph           ; Teil 1 oder Teil 2 fertig: Teil
                330     #0           ; Teil 1?
                170     teil2        ; ja: Teil 2 vorbereiten
                000     teil3        ; nein: Teil 3
teil2:          211     #1           ; Teil 2
                240     ph           ; merken
                211     #3           ; 3 Stellen
                240     kk           ; fuer Teil 2 merken
                211     #3           ; 4 Zahlen
                240     zn           ; Zaehler
                000     lese         ; lesen
teil3:          211     @tbl         ; Zeiger auf die Tabelle
                240     tp           ; merken
dl:             211     tp           ; Tabellenzeiger
                251     0            ; AC := Stellenzahl
                240     fk_as        ; Parameter von fk_ausgabe
                211     tp           ; Zeiger
                210     #01000       ; naechstes Wort
                240     tp           ; merken
                251     0            ; AC := Wort
                240     zw           ; merken
                211     tp           ; Zeiger
                210     #01000       ; naechstes Paar
                240     tp           ; merken
                ANWAHL  K2           ; Kanal 2 = Schreibwerk
                KB                   ; Schreibwerk auf Kleinbuchstaben (KB) schalten
                211     rwa3         ; Rueckkehrwort der Ausgabe
                240     fk_rueck     ; in die Rueckkehrzelle von fk_ausgabe
                211     zw           ; Wort in den AC
                000     fk_ausgabe   ; Zahl ausgeben
nach3:          WRZL                 ; Zeilenschaltung
                211     tz           ; Zaehler
                220     #1           ; - 1
                240     tz           ; merken
                050     dl           ; noch nicht fertig: naechstes Paar
                020     0            ; Halt
rwe:            da      nache        ; Rueckkehrwort der Eingabe
rwa:            da      nacha        ; Rueckkehrwort der Ausgabe
rwa3:           da      nach3        ; Rueckkehrwort der Ausgabe (Teil 3)
kk:             dw      9            ; Stellenzahl fuer Teil 1 und 2
zw:             db      1            ; gelesene fk-Zahl
zn:             dw      14           ; Zaehler: 15 Zahlen
ph:             dw      0            ; Teil: 0 Teil 1, 1 Teil 2
tp:             db      1            ; Zeiger auf die Tabelle tbl
tz:             dw      7            ; Zaehler: 8 Paare
tbl:            dw      9            ; Paar 1: Stellenzahl 9
                dw      037777777777 ; Wort 1 - 2^-32
                dw      9            ; Paar 2: Stellenzahl 9
                dw      040000000001 ; Wort -1 + 2^-32
                dw      0            ; Paar 3: Stellenzahl 0
                dw      037777777777 ; Wort 1 - 2^-32
                dw      0            ; Paar 4: Stellenzahl 0
                dw      020000000000 ; Wort 0,5
                dw      0            ; Paar 5: Stellenzahl 0
                dw      010000000000 ; Wort 0,25
                dw      2            ; Paar 6: Stellenzahl 2
                dw      03146314632  ; Wort 0,1
                dw      1            ; Paar 7: Stellenzahl 1
                dw      074631463146 ; Wort -0,1
                dw      5            ; Paar 8: Stellenzahl 5
                dw      020000000000 ; Wort 0,5
; ===== ENDE TESTHAUPTPROGRAMM
ende:           end                  ; Ende
sp7640:         abs     07640        ; Arbeitsspur (nur Bezug)
