; makrovarif.asm - Test von $V(name) in den Bedingungen von $IF und $ELIF (Assemblerdokumentation 4.7)
;#DOK-0001 Test von $V in $IF/$ELIF: Zaehler ueber mehrere Makroaufrufe, Vergleich mit Zahl und mit $CALC
;#PROT STUFE=2
ZINIT:          MACRO
                $SET n 0
                MEND
; ZAEHL: erhoeht die Variable n um 1 und erzeugt je nach Stand ein Wort 1 (n < 3), 2 (n = 3) oder 3 (n > 3), dann n*2 mit $CALC
ZAEHL:          MACRO
                $INC n
                $IF $V(n) < 3
                dw      1               ; Zaehler kleiner 3
                $ELIF $V(n) = 3
                dw      2               ; Zaehler gleich 3
                $ELSE
                dw      3               ; Zaehler groesser 3
                $ENDIF
                $IF $CALC($V(n)*2) > 6
                dw      077             ; doppelter Zaehler groesser 6
                $ENDIF
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                ZINIT                ; n := 0 (erzeugt keinen Code)
                ZAEHL                ; n=1: Zelle 0001 = 1
                ZAEHL                ; n=2: Zelle 0002 = 1
                ZAEHL                ; n=3: Zelle 0003 = 2
                ZAEHL                ; n=4: Zelle 0004 = 3, Zelle 0005 = 077
                ZAEHL                ; n=5: Zelle 0006 = 3, Zelle 0007 = 077
haupt:          164     0001         ; Zelle 0008: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0009: Halt
ende:           end

; Sollwerte von Hand hergeleitet: n=1,2 -> 1; n=3 -> 2; n=4,5 -> 3 und wegen 2n > 6 zusaetzlich 077. Halt auf 0011 (oktal), BZ danach 0012.
;#PRUEFE-START
; BZ=0012 US=1
; 0001: 00000000001   # n=1
; 0002: 00000000001   # n=2
; 0003: 00000000002   # n=3
; 0004: 00000000003   # n=4
; 0005: 00000000077   # 2*4=8 > 6
; 0006: 00000000003   # n=5
; 0007: 00000000077   # 2*5=10 > 6
;#PRUEFE-ENDE
