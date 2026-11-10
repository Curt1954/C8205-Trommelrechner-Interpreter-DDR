; makroadr.asm - adr und abstand im Makro-Praeprozessor (Assemblerdokumentation 4.23, c82ass ab 1.01-018)
; ABST: ein Wort mit abstand(von,bis); ADRW: ein Wort mit adr(marke); ZWEI: Makro, das zwei Woerter erzeugt (Marken aus Makros zaehlen mit)
ABST:           MACRO 2
                dw      $CALC(abstand($1,$2))       ; Abstand der beiden Marken
                MEND
ADRW:           MACRO 1
                dw      $CALC(adr($1))              ; Adresse der Marke
                MEND
ZWEI:           MACRO 0
                dw      1                           ; erstes Wort des Makros
                dw      2                           ; zweites Wort des Makros
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                ABST    tab_a tab_e  ; Zelle 0001: abstand(tab_a,tab_e) = 8
                ADRW    tab_e        ; Zelle 0002: adr(tab_e) = 13 = 015 (Vorwaertsbezug)
haupt:          164     0001         ; Zelle 0003: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0004: Halt
tab_a:          db      5            ; Zellen 0005 bis 0011 (fuenf Zellen)
                ZWEI                 ; Zellen 0012 und 0013 (dezimal 10 und 11)
                dw      3            ; Zelle 0014 (dezimal 12)
tab_e:          dw      4            ; Zelle 0015 (dezimal 13)
                ADRW    haupt        ; Zelle 0016 (dezimal 14): adr(haupt) = 3
ende:           end

; Sollwerte von Hand hergeleitet. Dezimale Adressen: 0 Sprung, 1 ABST, 2 ADRW, 3 haupt, 4 Halt, 5 bis 9 tab_a (db 5), 10 und 11 ZWEI, 12 dw 3, 13 tab_e, 14 ADRW.
; abstand(tab_a,tab_e) = 13 - 5 = 8 = 010 oktal; adr(tab_e) = 13 = 015 oktal; adr(haupt) = 3. Halt auf Zelle 0004, also BZ = 0005.
; Zwei Probelaeufe: Lauf 1 ohne Tabelle, Lauf 2 liefert dieselben Adressen.
;#PRUEFE-START
; BZ=0005 US=1
; 0001: 00000000010   # ABST tab_a tab_e
; 0002: 00000000015   # ADRW tab_e
; 0012: 00000000001   # ZWEI, erstes Wort (oktal 12 = dezimal 10)
; 0013: 00000000002   # ZWEI, zweites Wort
; 0014: 00000000003   # dw 3
; 0015: 00000000004   # tab_e
; 0016: 00000000003   # ADRW haupt
;#PRUEFE-ENDE
