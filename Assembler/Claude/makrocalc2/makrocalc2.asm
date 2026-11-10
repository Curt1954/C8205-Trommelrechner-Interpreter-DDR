; makrocalc2.asm - Test der erweiterten Rechenausdruecke: min(a,b), max(a,b), Vergleiche < > <= >= == !=, $CALCOn(...) (oktal, feste Breite)
;                 und der 64-Bit-Vergleich in $IF (Assemblerdokumentation 4.2)
;#DOK-0001 Test von min, max, Vergleichsoperatoren (Ergebnis 1 oder 0), $CALCO4 und $IF mit Zahlen ueber 32 Bit
;#PROT STUFE=2
MX:             MACRO 2
                dw      $CALC(min($1,$2))    ; Minimum
                dw      $CALC(max($1,$2))    ; Maximum
                dw      $CALC($1<$2)         ; kleiner
                dw      $CALC($1>=$2)        ; groesser oder gleich
                dw      $CALC($1==$2)        ; gleich
                dw      $CALC($1!=$2)        ; ungleich
                dw      $CALCO4($1*8)        ; oktal mit vier Ziffern (Wert 8 mal $1)
                MEND
MX2:            MACRO 1
                $IF $1 > 2999999999
                dw      1                    ; groesser als 2999999999 (ueber 32 Bit)
                $ELSE
                dw      0                    ; nicht groesser
                $ENDIF
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                MX      3 5          ; Zellen 0001 bis 0007
                MX      7 7          ; Zellen 0010 bis 0016
                MX2     3000000000   ; Zelle 0017
                MX2     5            ; Zelle 0020
haupt:          164     0001         ; Zelle 0021: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0022: Halt
ende:           end

; Sollwerte von Hand hergeleitet; Halt auf 0022, BZ danach 0023.
;#PRUEFE-START
; BZ=0023 US=1
; 0001: 00000000003   # min(3,5) = 3
; 0002: 00000000005   # max(3,5) = 5
; 0003: 00000000001   # 3<5 = 1
; 0004: 00000000000   # 3>=5 = 0
; 0005: 00000000000   # 3==5 = 0
; 0006: 00000000001   # 3!=5 = 1
; 0007: 00000000030   # $CALCO4(3*8) = 00030 = 24
; 0010: 00000000007   # min(7,7) = 7
; 0011: 00000000007   # max(7,7) = 7
; 0012: 00000000000   # 7<7 = 0
; 0013: 00000000001   # 7>=7 = 1
; 0014: 00000000001   # 7==7 = 1
; 0015: 00000000000   # 7!=7 = 0
; 0016: 00000000070   # $CALCO4(7*8) = 00070 = 56
; 0017: 00000000001   # $IF 3000000000 > 2999999999 (64 Bit): wahr
; 0020: 00000000000   # $IF 5 > 2999999999: falsch
;#PRUEFE-ENDE
