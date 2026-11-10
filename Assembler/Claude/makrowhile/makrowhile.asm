; makrowhile.asm - Test von $WHILE ... $ENDWHILE und $EXIT (Assemblerdokumentation 4.19)
;#DOK-0001 Test Schleife mit Abbruchbedingung ($WHILE) und vorzeitigem Verlassen des Makros ($EXIT)
;#PROT STUFE=2
; QUADRATE: erzeugt die Quadrate 1, 4, 9, ... solange sie hoechstens $1 sind (Zahl der Durchlaeufe steht erst im Lauf fest)
QUADRATE:       MACRO 1
                $SET i 1
                $WHILE $CALC($V(i)*$V(i)) <= $1
                dw      $CALC($V(i)*$V(i))      ; Quadrat des Zaehlers i
                $INC i
                $ENDWHILE
                MEND
; FINDE: zaehlt k von 0 an, erzeugt k; bei k = 3 erzeugt es 077 und verlaesst das Makro mit $EXIT mitten in der Schleife
FINDE:          MACRO
                $SET k 0
                $WHILE $V(k) < 10
                $IF $V(k) = 3
                dw      077                     ; Fundstelle
                $EXIT
                $ENDIF
                dw      $V(k)                   ; Zaehler k
                $INC k
                $ENDWHILE
                dw      070                     ; wird nach $EXIT nicht erzeugt
                MEND
; DREIECK: zwei geschachtelte Schleifen, die innere hat als Grenze den Zaehler der aeusseren; erzeugt 11, 21 22, 31 32 33 (dezimal)
DREIECK:        MACRO
                $SET a 1
                $WHILE $V(a) <= 3
                $SET b 1
                $WHILE $V(b) <= $V(a)
                dw      $CALC($V(a)*10+$V(b))   ; Zehner a, Einer b
                $INC b
                $ENDWHILE
                $INC a
                $ENDWHILE
                MEND
; LEER: Die Bedingung ist von Anfang an falsch, der Rumpf entfaellt (erzeugt keinen Code)
LEER:           MACRO
                $SET z 5
                $WHILE $V(z) < 3
                dw      077                     ; wird nie erzeugt
                $ENDWHILE
                MEND
; FRUEH: $EXIT nur im erzeugten Zweig; bei $1 = 0 endet das Makro nach dem ersten Wort, sonst erzeugt es zwei Worte
FRUEH:          MACRO 1
                dw      1                       ; immer
                $IF $1 = 0
                $EXIT
                $ENDIF
                dw      2                       ; nur bei $1 ungleich 0
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                QUADRATE 30          ; Zellen 1 bis 5: 1, 4, 9, 16, 25
                FINDE                ; Zellen 6 bis 9: 0, 1, 2, 077
                DREIECK              ; Zellen 10 bis 15: 11, 21, 22, 31, 32, 33
                LEER                 ; kein Code
                FRUEH 0              ; Zelle 16: 1
                FRUEH 1              ; Zellen 17 und 18: 1, 2
haupt:          164     0001         ; Zelle 19: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 20: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen oktal): Quadrate 1,4,9,16,25 = oktal 1,4,11,20,31.
; FINDE: k=0,1,2 erzeugen 0,1,2, bei k=3 077, dann $EXIT. DREIECK: 11=013, 21=025, 22=026, 31=037, 32=040, 33=041 (oktal).
; FRUEH 0 erzeugt 1; FRUEH 1 erzeugt 1 und 2. Halt auf Zelle 20 dezimal = 0024 (oktal), BZ danach 0025.
;#PRUEFE-START
; BZ=0025 US=1
; 0001: 00000000001   # 1*1
; 0002: 00000000004   # 2*2
; 0003: 00000000011   # 3*3 = 9
; 0004: 00000000020   # 4*4 = 16
; 0005: 00000000031   # 5*5 = 25
; 0006: 00000000000   # k=0
; 0007: 00000000001   # k=1
; 0010: 00000000002   # k=2
; 0011: 00000000077   # k=3: Fundstelle, danach $EXIT
; 0012: 00000000013   # 11
; 0013: 00000000025   # 21
; 0014: 00000000026   # 22
; 0015: 00000000037   # 31
; 0016: 00000000040   # 32
; 0017: 00000000041   # 33
; 0020: 00000000001   # FRUEH 0
; 0021: 00000000001   # FRUEH 1, erstes Wort
; 0022: 00000000002   # FRUEH 1, zweites Wort
;#PRUEFE-ENDE
