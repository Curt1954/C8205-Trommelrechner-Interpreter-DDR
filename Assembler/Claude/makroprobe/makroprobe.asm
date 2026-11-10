; makroprobe.asm - $PROBE im Makro-Praeprozessor (Assemblerdokumentation 4.23, c82ass ab 1.01-020)
; $PROBE ist 1 in einem Probelauf fuer adr/abstand (Lauf 1 rechnet dort mit dem Abstand 0) und bei --pass0, sonst 0.
; CHK: verlangt einen Abstand von mindestens 1, prueft das aber nur im eigentlichen Lauf; ohne $PROBE = 0 bricht
;      Probelauf 1 mit $ERROR ab (Abstand 0), siehe Negativtest makro_adr_probelauf_fehler
; PW: ein Wort mit dem Wert von $PROBE; WAHL: je ein Wort, aber je nach $PROBE ein anderer Wert (gleiche Zellenzahl);
; SUMME: $PROBE in $CALC
CHK:            MACRO 2
                $IF $PROBE = 0
                $IF $CALC(abstand($1,$2)) < 1
                $ERROR Abstand kleiner 1
                $ENDIF
                $ENDIF
                dw      $CALC(abstand($1,$2))       ; Abstand der beiden Marken
                MEND
PW:             MACRO 0
                dw      $PROBE                      ; im eigentlichen Lauf 0
                MEND
WAHL:           MACRO 0
                $IF $PROBE = 1
                dw      111                         ; nur im Probelauf
                $ELSE
                dw      222                         ; im eigentlichen Lauf (oktal 336)
                $ENDIF
                MEND
SUMME:          MACRO 0
                dw      $CALC($PROBE+5)             ; im eigentlichen Lauf 5
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
a:              dw      0            ; Zelle 0001
                CHK     a b          ; Zelle 0002: abstand(a,b) = 3 - 1 = 2
b:              dw      9            ; Zelle 0003
haupt:          020     0            ; Zelle 0004: Halt
                PW                   ; Zelle 0005: 0
                WAHL                 ; Zelle 0006: 222 = oktal 336
                SUMME                ; Zelle 0007: 5
ende:           end

; Sollwerte von Hand hergeleitet. Dezimale Adressen: 0 Sprung, 1 a, 2 CHK, 3 b, 4 Halt, 5 PW, 6 WAHL, 7 SUMME.
; abstand(a,b) = 3 - 1 = 2. Halt auf Zelle 0004, also BZ = 0005. Im eigentlichen Lauf ist $PROBE gleich 0:
; PW = 0, WAHL = 222 dezimal = 336 oktal, SUMME = 0 + 5 = 5. Zwei Probelaeufe (Lauf 1 ohne Tabelle, Lauf 2 gleiche Adressen).
;#PRUEFE-START
; BZ=0005 US=1
; 0002: 00000000002   # CHK a b
; 0003: 00000000011   # b: dw 9
; 0005: 00000000000   # PW
; 0006: 00000000336   # WAHL
; 0007: 00000000005   # SUMME
;#PRUEFE-ENDE
