; sinusfunktion_zeichnen.asm  --  Projekt_Gleitkomma: Hauptprogramm, zeichnet eine volle Sinusperiode y = sin(2*pi*x) fuer x = 0 bis 1 mit dem Zeichen * auf dem Schreibwerk (SW, Kanal K2).
; Stand 08.11.2026. Das Programm wird vom BIS als Objektcode (.obj, Eingabe mit Kennzeichen, Hauptleitadresse + Ladeadresse) geladen und ist ueber seine Zelle 0000 (Sprung) startbar.
;
; Massstab (Vorgabe des Inhabers): das ganze Bild ist 15 Zeilen hoch (sonst wird es unfoermig), x = 1 entspricht 25 Spalten. Ausgegeben werden die Spalten j = 0 bis 25 (x = j/25, also 26 Spalten;
;   Winkel 2*pi*x im Bogenmass, keine Gradumrechnung noetig: gk_sin rechnet im Bogenmass) und die Zeilen r = 14 bis 0 (y = (r - 7)/7: oben y = +1, Zeile 7 ist die x-Achse y = 0, unten y = -1).
;   In Spalte j steht ein * in der Zeile r = n_j = 7 + (ganze Zahl nahe 7 * sin(2*pi*j/25), gerundet auf die naechste ganze Zahl); alle anderen Stellen bleiben Leerzeichen.
;   Jede Zeile hat 26 Zeichen und endet mit einer Zeilenschaltung. Vor dem Bild stehen zwei Zeilenschaltungen (Abstand zur Ausgabe des BIS beim Laden).
;
; VERFAHREN: Teil 1 rechnet die 26 Zeilenzahlen n_j mit dem UP gk_sin (Makro GK_SIN, Format dwg): x := 0; je Spalte  n_j := ((7 * sin(x)) + (2^25 + 7)) und 017  (die Addition rundet 7 sin(x)
;   auf eine ganze Zahl; weil die Summe zwischen 2^25 und 2^26 bleibt, ist die Mantisse des Ergebnisses 2^25 + 7 + n, die unteren vier Bit sind 7 + n mit n von -7 bis 7, also 0 bis 14;
;   Verfahren wie in gk_sin, der Offset 7 macht die Zeilenzahl auch fuer negative Werte nichtnegativ); danach x := x + 2*pi/25 (gk_add; der Summenfehler ueber 25 Schritte liegt bei 2E-6,
;   die Rundungsgrenzen sind mindestens 0,07 Zeileneinheiten entfernt). n_j kommen in die Tabelle tab (26 Zellen).
;   Teil 2 gibt zwei Zeilenschaltungen und dann die Zeilen r = 14 bis 0 aus: je Zeile Anwahl K2, Um. GB, fuer jede Spalte ein * (n_j = r) oder ein Leerzeichen, Um. KB, Zeilenschaltung (WRZL waehlt danach K0).
;
; Parameter, Rueckgabe: keine. Aufrufe der Rechen-UP: gk_sin ueber den Parameterblock gks_x; gk_mul und gk_add ueber R1 (7773) und R2 (7776), Ergebnis im AC (Festlegungen 031 bis 033).
; Zerstoert: R1, R2, die Arbeitsspur 7640 bis 7677 (gk_add, gk_mul, gk_sin), die eigenen Zellen. Verwendete Maschinenmittel: Kanal K2 (Schreibwerk); das KB/GB-Merkmal (030): das Programm beginnt
;   und endet jede Zeile im Zustand KB, mitten in der Zeile steht es auf GB; es ruft keine E/A-UP auf, ein Merkmal in einer Zelle ist deshalb nicht noetig.
; Speicher: GK_SIN (mit gk_add, gk_sub, gk_mul, gk_sin und gk_cos) 0636 Zellen ab 0001, dahinter das Hauptprogramm; Gesamtgroesse siehe Listing (.dmp). Empfehlung nach 001: Ladeadresse auf eine 040-Grenze,
;   kleinste Startzelle 0500 (0040 bis 0377 belegt das BIS-Minimalprogramm, 0400 bis 0477 sind seine Anschlusszellen), groesste so, dass das Programm vor 07540 endet; alle Spruenge relativ.
; ANNAHMEN (bitte bestaetigen): (a) Eine volle Periode y = sin(2*pi*x), x = 0 bis 1 einschliesslich (26 Spalten), das ganze Bild 15 Zeilen hoch (y = +1 bis y = -1, 7 Zeilen je Einheit, Achse auf Zeile 7).
;   (b) Rundung auf die naechste ganze Zeile. (c) Ohne Achsen und Beschriftung, nur *. (d) Der Test laeuft ab Zelle 0000 auf leerer Trommel; das Laden ueber das BIS ist nicht getestet,
;   der Assembler erzeugt dafuer die Objektdatei.
;
; Test: Tastenfolge H G R (Start bei Zelle 0000), Trommel leer, Schreibwerk-Ausgabe gegen Test-Ergebnisvergleiche/sinusfunktion_zeichnen-sw-ausgabe.txt.
;#TROMMEL=LEER
;#PROT STUFE=2
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/sinusfunktion_zeichnen

GKOP:           MACRO   2                ; Rechen-UP aufrufen: AC (erster Operand) nach R1, zweiter Operand nach R2, 025 UP; Ergebnis im AC
                .STO    r1               ; erster Operand (AC) nach R1
                .LD     $2               ; zweiter Operand
                .STO    r2               ; nach R2
                025     $1               ; gk_mul oder gk_add: AC := Ergebnis
                MEND                     ; Ende

                start                    ; Zaehlung beginnt bei 0000 (relativ)
                .JMP    haupt            ; Zelle 0000: Sprung zum Hauptprogramm
                GK_SIN                   ; Makro GK_SIN (c82ass.makros): gk_add, gk_sub, gk_mul und gk_sin, jeder Teil nur einmal erzeugt

r1:             abs     07773            ; Register R1 (nur Bezug)
r2:             abs     07776            ; Register R2 (nur Bezug)
d15:            dwg     7                ; Konstante 7 (dwg): 7 Zeilen je Einheit von y
d25:            dwg     33554439         ; Konstante 2^25 + 7 (dwg): rundet die Summe auf eine ganze Zahl, Offset 7 haelt sie nichtnegativ
dh:             dwg     0.25132741228718 ; Spaltenabstand 2*pi/25 (dwg, Bogenmass)
xz:             db      1                ; aktuelles x (dwg)
tz:             db      1                ; Zeiger auf die aktuelle Tabellenzelle (Adresswort)
nt:             db      1                ; Zwischenspeicher n_j
zr:             db      1                ; aktuelle Zeile r (ganze Zahl, 14 bis 0)
tab:            db      26               ; n_j fuer j = 0 bis 25 (Zeilenzahl der Spalte j)
tabend:         db      1                ; Ende der Tabelle (nur als Vergleichsadresse, Zelle ohne Inhalt)

; ===== Teil 1: n_j = 7 + Rundung(7 * sin(2*pi*j/25)) fuer j = 0 bis 25
haupt:          .STOC   xz               ; x := 0 (dwg 0 ist das Wort 0), AC := 0
                .LD     @tab             ; Zeiger auf tab[0]
                .STO    tz               ; merken
t1:             .LD     xz               ; AC := x
                .STO    gks_x            ; Parameter von gk_sin
                025     gk_sin           ; AC := sin(x)
                GKOP    gk_mul d15       ; AC := 7 * sin(x)
                GKOP    gk_add d25       ; AC := 7 sin(x) + 2^25 + 7 (rundet auf eine ganze Zahl)
                .AND    #017             ; untere vier Bit: n_j = 7 + n (0 bis 14)
                .STO    nt               ; n_j merken
                .LD     tz               ; Zeiger auf tab[j]
                .ADD    #0240            ; + Speicherbefehl
                .STO    sp               ; Befehl 240 tab[j] auf die naechste Zelle legen
                .LD     nt               ; n_j
sp:             db      1                ; Laufzeit: 240 tab[j]
                .LD     xz               ; AC := x
                GKOP    gk_add dh        ; AC := x + 2*pi/25
                .STO    xz               ; neues x
                ZEIGER_NAECHST tz        ; naechste Tabellenzelle
                .SUB    @tabend          ; Zeiger - Ende der Tabelle
                .JNEG   t1               ; kleiner (negativ): naechste Spalte

; ===== Teil 2: zwei Zeilenschaltungen, dann die Zeilen r = 14 bis 0 ausgeben
                ANWAHL  K2               ; Schreibwerk anwaehlen
                dz      $wrzl            ; erste Zeilenschaltung (Abstand zur BIS-Ausgabe)
                WRZL                     ; zweite Zeilenschaltung, danach K0
                .LD     #14              ; erste Zeile: y = +1
                .STO    zr               ; Zeilenzaehler
t2:             ANWAHL  K2               ; Schreibwerk anwaehlen (WRZL hat K0 angewaehlt)
                dz      $ingb            ; Um. GB: das * ist ein Zeichen im Zustand GB
                .LD     @tab             ; Zeiger auf tab[0]
                .STO    tz               ; merken
t3:             .LD     tz               ; Zeiger auf n_j
                .LDR    0                ; AC := n_j
                .CMP    zr               ; n_j mit der Zeile vergleichen
                .JVG3   stern            ; gleich: Stern
                dto     \ \              ; sonst Leerzeichen
                .JMP    weit             ; weiter zur naechsten Spalte
stern:          dto     *                ; Stern
weit:           ZEIGER_NAECHST tz        ; naechste Spalte
                .SUB    @tabend          ; Zeiger - Ende der Tabelle
                .JNEG   t3               ; kleiner (negativ): naechste Spalte
                dz      $inkb            ; Um. KB: Zeilenende wieder im Zustand KB
                WRZL                     ; Zeilenschaltung, danach K0
                .LD     zr               ; AC := Zeile
                .SUB    #1               ; naechste Zeile (darunter)
                .STO    zr               ; merken
                .JPOS   t2               ; Zeile >= 0: weiter
                .STOP   0                ; Halt: Zeichnung fertig
ende:           end                      ; Ende

; Sollwerte von Hand hergeleitet (n_j = 7 + floor(7*sin(2*pi*j/25) + 0,5) mit exakter Mathematik, nicht aus dem Lauf): Halt auf Zelle 0776, BZ = 0777; die Tabelle tab liegt auf 0646 bis 0677 (n_j in Zelle 0646 + j).
; Die Zeilenzahlen n_j: 7 9 10 12 13 14 14 14 13 12 11 10 8 6 4 3 2 1 0 0 0 1 2 4 5 7. Die Schreibwerk-Ausgabe: zwei Leerzeilen, dann 15 Zeilen zu 26 Zeichen (Zeile r von 14 bis 0), Sollwert in der genannten Datei.
;#PRUEFE-START
; BZ=0777 US=1
; 0646: 00000000007   # tab[0]: n = 7
; 0647: 00000000011   # tab[1]: n = 9
; 0650: 00000000012   # tab[2]: n = 10
; 0651: 00000000014   # tab[3]: n = 12
; 0652: 00000000015   # tab[4]: n = 13
; 0653: 00000000016   # tab[5]: n = 14
; 0654: 00000000016   # tab[6]: n = 14
; 0655: 00000000016   # tab[7]: n = 14
; 0656: 00000000015   # tab[8]: n = 13
; 0657: 00000000014   # tab[9]: n = 12
; 0660: 00000000013   # tab[10]: n = 11
; 0661: 00000000012   # tab[11]: n = 10
; 0662: 00000000010   # tab[12]: n = 8
; 0663: 00000000006   # tab[13]: n = 6
; 0664: 00000000004   # tab[14]: n = 4
; 0665: 00000000003   # tab[15]: n = 3
; 0666: 00000000002   # tab[16]: n = 2
; 0667: 00000000001   # tab[17]: n = 1
; 0670: 00000000000   # tab[18]: n = 0
; 0671: 00000000000   # tab[19]: n = 0
; 0672: 00000000000   # tab[20]: n = 0
; 0673: 00000000001   # tab[21]: n = 1
; 0674: 00000000002   # tab[22]: n = 2
; 0675: 00000000004   # tab[23]: n = 4
; 0676: 00000000005   # tab[24]: n = 5
; 0677: 00000000007   # tab[25]: n = 7
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/sinusfunktion_zeichnen-sw-ausgabe.txt
;#PRUEFE-ENDE
