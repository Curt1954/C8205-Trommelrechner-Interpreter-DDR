;makrobinaer.asm - Test der Binaerfunktionen des Makroprozessors: $CALCB, $CALCBn, 0b-Zahlen im Rechenausdruck, $VALB (Assemblerdokumentation 4.27)
;#DOK-0001 Test $CALCB und $CALCBn (Ausgabe), 0b-Zahl im Ausdruck (Eingabe), $VALB (Text nach Zahl), Rundreise, $VAL unveraendert
;#PROT STUFE=2
; BINAUS: $CALCB gibt Binaerziffern ohne Praefix aus; dwb liest sie dual, das Wort ist die Zahl (Zellen 1 bis 7)
BINAUS:         MACRO
                dwb     $CALCB(10)              ; 10 = 1010 binaer = 012 oktal
                dwb     $CALCB(0)               ; 0 ergibt die Ziffer 0
                dwb     $CALCB8(5)              ; mit Breite 8: 00000101 = 5
                dwb     $CALCB33(5)             ; Breite 33 (ein ganzes Wort) = 5
                dwb     $CALCB33(8589934591)    ; 2^33-1: 33 Einsen = 77777777777 oktal
                dwb     $CALCB1(1)              ; Breite 1: Ziffer 1
                dwb     $CALCB(2+3*4)           ; 14 = 1110 binaer = 016 oktal
                MEND
; BINLIT: 0b-Zahlen im Rechenausdruck (Zellen 8 bis 14)
BINLIT:         MACRO
                dw      $CALC(0b11111111)       ; 255 = 0377
                dw      $CALC(0B101*2)          ; grosses B, 5*2 = 10 = 012
                dw      $CALC(0b1<<20)          ; 2^20 = 04000000
                dw      $CALC(0b101|010)        ; 5 ODER 010 (oktal 8) = 13 = 015
                dwb     $CALCB(0b11+0b101)      ; 3+5 = 8 = 1000 binaer = 010
                dw      $CALC(0b0000101)        ; fuehrende Nullen zaehlen nicht: 5
                dw      $CALC(-0b101+100)       ; -5 + 100 = 95 = 0137
                MEND
; BINVAL: $VALB liest einen Text dual (Zellen 15 bis 21)
BINVAL:         MACRO
                $VALB n "101"
                dw      $V(n)                   ; 101 dual = 5
                $VALB n "00101"
                dw      $V(n)                   ; fuehrende Nullen: 5
                $VALB n "-101"
                dw      $CALC($V(n)+100)        ; -5 + 100 = 95 = 0137
                $VALB n "0"
                dw      $V(n)                   ; 0
                $VALB n "1"
                dw      $V(n)                   ; 1
                $VALB n "111111111111111111111111111111111111111111111111111111111111111"
                dw      $CALC($V(n)>>54)        ; 63 Einsen = 2^63-1, durch 2^54 geteilt = 511 = 0777
                $VAL d "101"
                dw      $V(d)                   ; $VAL liest unveraendert dezimal: 101 = 0145
                MEND
; BINRUND: Rundreise Zahl, Binaertext, Zahl; Schleife 0 bis 100; groesste Zahl (Zellen 22 bis 28)
BINRUND:        MACRO
                $SET n 1234
                $SET t "$CALCB($V(n))"          ; 10011010010
                dw      $V(#t)                  ; 11 Zeichen = 013
                $VALB r "$V(t)"
                dw      $V(r)                   ; 1234 = 02322
                $SET t "$CALCB16($V(n))"        ; 0000010011010010
                dw      $V(#t)                  ; 16 Zeichen = 020
                $VALB r "$V(t)"
                dw      $V(r)                   ; 1234 = 02322
                $SET ok 0
                $SET n 0
                $WHILE $V(n) <= 100
                $SET t "$CALCB($V(n))"
                $VALB r "$V(t)"
                $IF $V(r) = $V(n)
                $INC ok
                $ENDIF
                $SET t "$CALCB33($V(n))"
                $VALB r "$V(t)"
                $IF $V(r) = $V(n)
                $INC ok
                $ENDIF
                $INC n
                $ENDWHILE
                dw      $V(ok)                  ; 101 Werte, je zwei Pruefungen: 202 = 0312
                $SET g 9223372036854775807
                $SET t "$CALCB($V(g))"          ; 63 Einsen
                dw      $V(#t)                  ; 63 Zeichen = 077
                $VALB r "$V(t)"
                $SET d $CALC($V(r)-$V(g))
                dw      $V(d)                   ; gleiche Zahl zurueck: Unterschied 0
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                BINAUS               ; Zellen 1 bis 7
                BINLIT               ; Zellen 8 bis 14
                BINVAL               ; Zellen 15 bis 21
                BINRUND              ; Zellen 22 bis 28
haupt:          164     0001         ; Zelle 29: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 30: Halt
ende:           end
; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal); haupt = Zelle 29 (oktal 0035), Halt in Zelle 30, BZ danach 0037.
;#PRUEFE-START
; BZ=0037 US=1
; 0001: 00000000012   # BINAUS: $CALCB(10)
; 0002: 00000000000   # BINAUS: $CALCB(0)
; 0003: 00000000005   # BINAUS: $CALCB8(5)
; 0004: 00000000005   # BINAUS: $CALCB33(5)
; 0005: 77777777777   # BINAUS: $CALCB33(2^33-1)
; 0006: 00000000001   # BINAUS: $CALCB1(1)
; 0007: 00000000016   # BINAUS: $CALCB(2+3*4)
; 0010: 00000000377   # BINLIT: 0b11111111
; 0011: 00000000012   # BINLIT: 0B101*2
; 0012: 00004000000   # BINLIT: 0b1<<20
; 0013: 00000000015   # BINLIT: 0b101|010
; 0014: 00000000010   # BINLIT: $CALCB(0b11+0b101)
; 0015: 00000000005   # BINLIT: 0b0000101
; 0016: 00000000137   # BINLIT: -0b101+100
; 0017: 00000000005   # BINVAL: 101
; 0020: 00000000005   # BINVAL: 00101
; 0021: 00000000137   # BINVAL: -101 + 100
; 0022: 00000000000   # BINVAL: 0
; 0023: 00000000001   # BINVAL: 1
; 0024: 00000000777   # BINVAL: 63 Einsen durch 2^54
; 0025: 00000000145   # BINVAL: $VAL 101 dezimal
; 0026: 00000000013   # BINRUND: Text hat 11 Zeichen
; 0027: 00000002322   # BINRUND: 1234 zurueck
; 0030: 00000000020   # BINRUND: Breite 16
; 0031: 00000002322   # BINRUND: 1234 zurueck (feste Breite)
; 0032: 00000000312   # BINRUND: 202 gelungene Rundreisen
; 0033: 00000000077   # BINRUND: 2^63-1 hat 63 Zeichen
; 0034: 00000000000   # BINRUND: Unterschied 0
;#PRUEFE-ENDE
