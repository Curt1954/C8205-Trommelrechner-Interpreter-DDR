; makrolokal_while.asm - Test von ;#MAKROLOKAL=1 im Rumpf von $WHILE: eine implizit angelegte lokale Variable bleibt ueber die Durchlaeufe erhalten (Assemblerdokumentation 4.31, 4.19)
;#DOK-0001 Test Schalter MAKROLOKAL und $WHILE: $SET legt c im ersten Durchlauf an, $INC zaehlt weiter; $LOCAL im Rumpf beginnt dagegen jedes Mal neu
;#PROT STUFE=2
;#MAKROLOKAL=1
; ZAEHLEN: $1 Durchlaeufe; c entsteht im ersten Durchlauf mit 10 und wird in jedem weiteren um 1 erhoeht
ZAEHLEN:        MACRO 1
                $SET i 1
                $WHILE $V(i) <= $1
                $IF $V(i) = 1
                $SET c 10               ; legt c lokal an (nur im ersten Durchlauf)
                $ELSE
                $INC c                  ; c ist aus dem ersten Durchlauf noch da
                $ENDIF
                $INC i
                $ENDWHILE
                dw      $V(c)           ; 10 + ($1 - 1)
                MEND
; MITLOKAL: $LOCAL im Rumpf vereinbart c in jedem Durchlauf neu mit 0 (4.19), am Ende steht c deshalb auf 1
MITLOKAL:       MACRO 1
                $SET i 1
                $WHILE $V(i) <= $1
                $LOCAL c
                $INC c
                $INC i
                $ENDWHILE
                dw      $V(c)           ; 1
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                ZAEHLEN 4            ; Zelle 0001: 13
                ZAEHLEN 1            ; Zelle 0002: 10
                MITLOKAL 4           ; Zelle 0003: 1
haupt:          164     0001         ; Zelle 0004: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0005: Halt
ende:           end

; Sollwerte von Hand hergeleitet: ZAEHLEN 4 = 10 + 3 = 13 dezimal = 015 oktal; ZAEHLEN 1 = 10 dezimal = 012 oktal; MITLOKAL = 1.
; Halt auf Zelle 5, BZ danach 0006.
;#PRUEFE-START
; BZ=0006 US=1
; 0001: 00000000015   # ZAEHLEN 4 = 13
; 0002: 00000000012   # ZAEHLEN 1 = 10
; 0003: 00000000001   # MITLOKAL: c beginnt in jedem Durchlauf neu
;#PRUEFE-ENDE
