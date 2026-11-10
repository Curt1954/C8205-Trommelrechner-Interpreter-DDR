
;makrohex.asm - Test der Hexadezimalfunktionen: dwh, $CALCH, $CALCHn, 0x-Zahlen im Rechenausdruck, $VALH (Assemblerdokumentation 3.3.19a und 4.28)
;#DOK-0001 Test dwh (1 bis 8 Hexziffern), $CALCH und $CALCHn (Ausgabe), 0x-Zahl im Ausdruck (Eingabe), $VALH (Text nach Zahl), Rundreise, $VAL unveraendert
;#PROT STUFE=2
; HEXAUS: $CALCH gibt Hexziffern (Grossbuchstaben) ohne Praefix aus; dwh liest sie, das Wort ist die Zahl (Zellen 1 bis 7)
HEXAUS:         MACRO
                dwh     $CALCH(255)             ; 255 = FF = 0377 oktal
                dwh     $CALCH(0)               ; 0 ergibt die Ziffer 0
                dwh     $CALCH8(255)            ; mit Breite 8: 000000FF = 0377
                dwh     $CALCH8(4294967295)     ; 2^32-1: FFFFFFFF = 37777777777 oktal
                dwh     $CALCH1(10)             ; Breite 1: Ziffer A = 012
                dwh     $CALCH(2+3*4)           ; 14 = E = 016 oktal
                dwh     $CALCH(48879)           ; BEEF = 0137357 oktal
                MEND
; HEXLIT: 0x-Zahlen im Rechenausdruck (Zellen 8 bis 16)
HEXLIT:         MACRO
                dw      $CALC(0xFF)             ; 255 = 0377
                dw      $CALC(0XaB*2)           ; grosses X, Kleinbuchstaben: 171*2 = 342 = 0526
                dw      $CALC(0x1<<20)          ; 2^20 = 04000000
                dw      $CALC(0x5|010)          ; 5 ODER 010 (oktal 8) = 13 = 015
                dwh     $CALCH(0xFF+0x1)        ; 255+1 = 256 = 100 hexadezimal = 0400
                dw      $CALC(0x0000AB)         ; fuehrende Nullen zaehlen nicht: 171 = 0253
                dw      $CALC(-0xA+100)         ; -10 + 100 = 90 = 0132
                dw      $CALC(0xb+0b1)          ; 0xb ist 11 (b als Hexziffer), 0b1 ist 1: 12 = 014
                dw      $CALC(0x1E+3)           ; E ist Hexziffer, kein Exponent: 30+3 = 33 = 041
                MEND
; HEXVAL: $VALH liest einen Text hexadezimal (Zellen 17 bis 25)
HEXVAL:         MACRO
                $VALH n "FF"
                dw      $V(n)                   ; FF hexadezimal = 255 = 0377
                $VALH n "ff"
                dw      $V(n)                   ; Kleinbuchstaben: 255
                $VALH n "00FF"
                dw      $V(n)                   ; fuehrende Nullen: 255
                $VALH n "-A"
                dw      $CALC($V(n)+100)        ; -10 + 100 = 90 = 0132
                $VALH n "0"
                dw      $V(n)                   ; 0
                $VALH n "1"
                dw      $V(n)                   ; 1
                $VALH n "7FFFFFFFFFFFFFFF"
                dw      $CALC($V(n)>>54)        ; 2^63-1 durch 2^54 geteilt = 511 = 0777
                $VAL d "101"
                dw      $V(d)                   ; $VAL liest unveraendert dezimal: 101 = 0145
                $VALH n "10"
                dw      $V(n)                   ; 10 hexadezimal = 16 = 020
                MEND
; HEXRUND: Rundreise Zahl, Hextext, Zahl; Schleife 0 bis 100; groesste Zahl; Grossbuchstaben (Zellen 26 bis 33)
HEXRUND:        MACRO
                $SET n 1234
                $SET t "$CALCH($V(n))"          ; 4D2
                dw      $V(#t)                  ; 3 Zeichen = 03
                $VALH r "$V(t)"
                dw      $V(r)                   ; 1234 = 02322
                $SET t "$CALCH8($V(n))"         ; 000004D2
                dw      $V(#t)                  ; 8 Zeichen = 010
                $VALH r "$V(t)"
                dw      $V(r)                   ; 1234 = 02322
                $SET ok 0
                $SET n 0
                $WHILE $V(n) <= 100
                $SET t "$CALCH($V(n))"
                $VALH r "$V(t)"
                $IF $V(r) = $V(n)
                $INC ok
                $ENDIF
                $SET t "$CALCH8($V(n))"
                $VALH r "$V(t)"
                $IF $V(r) = $V(n)
                $INC ok
                $ENDIF
                $INC n
                $ENDWHILE
                dw      $V(ok)                  ; 101 Werte, je zwei Pruefungen: 202 = 0312
                $SET g 9223372036854775807
                $SET t "$CALCH($V(g))"          ; 7FFFFFFFFFFFFFFF
                dw      $V(#t)                  ; 16 Zeichen = 020
                $VALH r "$V(t)"
                $SET d $CALC($V(r)-$V(g))
                dw      $V(d)                   ; gleiche Zahl zurueck: Unterschied 0
                $SET t "$CALCH(171)"            ; AB, nicht ab
                $ORD c "$V(t)" 1
                dw      $V(c)                   ; Code des ersten Zeichens: A = 65 = 0101
                MEND
; HEXDWH: dwh mit festem Operanden (Zellen 34 bis 43)
HEXDWH:         MACRO
                dwh     0                       ; Wort 0
                dwh     1                       ; Wort 1
                dwh     00000001                ; 8 Stellen, fuehrende Nullen: Wort 1
                dwh     7FFFFFFF                ; 2^31-1 = 17777777777 oktal
                dwh     80000000                ; 2^31 = 20000000000 oktal
                dwh     abcdef01                ; Kleinbuchstaben: 25363367401 oktal
                dwh     DEADBEEF                ; Grossbuchstaben: 33653337357 oktal
hx1:            da      cafe                    ; Vorwaertsverweis auf ein Symbol, dessen Name nur aus Hexziffern besteht (spaetes Symbol)
cafe:           dw      0                       ; die Zelle, auf die hx1 zeigt
                dwh     cafe                    ; hier ist cafe eine Hexzahl und kein Symbol: 0xCAFE = 0145376 oktal
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                HEXAUS               ; Zellen 1 bis 7
                HEXLIT               ; Zellen 8 bis 16
                HEXVAL               ; Zellen 17 bis 25
                HEXRUND              ; Zellen 26 bis 33
                HEXDWH               ; Zellen 34 bis 43
haupt:          164     0001         ; Zelle 44: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 45: Halt
ende:           end
; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal); haupt = Zelle 44 (oktal 0054), Halt in Zelle 45, BZ danach 0056.
;#PRUEFE-START
; BZ=0056 US=1
; 0001: 00000000377   # HEXAUS: $CALCH(255) = FF
; 0002: 00000000000   # HEXAUS: $CALCH(0)
; 0003: 00000000377   # HEXAUS: $CALCH8(255) = 000000FF
; 0004: 37777777777   # HEXAUS: $CALCH8(2^32-1) = FFFFFFFF
; 0005: 00000000012   # HEXAUS: $CALCH1(10) = A
; 0006: 00000000016   # HEXAUS: $CALCH(2+3*4) = E
; 0007: 00000137357   # HEXAUS: $CALCH(48879) = BEEF
; 0010: 00000000377   # HEXLIT: 0xFF
; 0011: 00000000526   # HEXLIT: 0XaB*2
; 0012: 00004000000   # HEXLIT: 0x1<<20
; 0013: 00000000015   # HEXLIT: 0x5|010
; 0014: 00000000400   # HEXLIT: $CALCH(0xFF+0x1) = 100
; 0015: 00000000253   # HEXLIT: 0x0000AB
; 0016: 00000000132   # HEXLIT: -0xA+100
; 0017: 00000000014   # HEXLIT: 0xb+0b1
; 0020: 00000000041   # HEXLIT: 0x1E+3
; 0021: 00000000377   # HEXVAL: FF
; 0022: 00000000377   # HEXVAL: ff
; 0023: 00000000377   # HEXVAL: 00FF
; 0024: 00000000132   # HEXVAL: -A + 100
; 0025: 00000000000   # HEXVAL: 0
; 0026: 00000000001   # HEXVAL: 1
; 0027: 00000000777   # HEXVAL: 7FFFFFFFFFFFFFFF durch 2^54
; 0030: 00000000145   # HEXVAL: $VAL 101 dezimal
; 0031: 00000000020   # HEXVAL: 10 hexadezimal = 16
; 0032: 00000000003   # HEXRUND: Text hat 3 Zeichen
; 0033: 00000002322   # HEXRUND: 1234 zurueck
; 0034: 00000000010   # HEXRUND: Breite 8
; 0035: 00000002322   # HEXRUND: 1234 zurueck (feste Breite)
; 0036: 00000000312   # HEXRUND: 202 gelungene Rundreisen
; 0037: 00000000020   # HEXRUND: 2^63-1 hat 16 Zeichen
; 0040: 00000000000   # HEXRUND: Unterschied 0
; 0041: 00000000101   # HEXRUND: Grossbuchstabe A = 65
; 0042: 00000000000   # HEXDWH: dwh 0
; 0043: 00000000001   # HEXDWH: dwh 1
; 0044: 00000000001   # HEXDWH: dwh 00000001
; 0045: 17777777777   # HEXDWH: dwh 7FFFFFFF
; 0046: 20000000000   # HEXDWH: dwh 80000000
; 0047: 25363367401   # HEXDWH: dwh abcdef01
; 0050: 33653337357   # HEXDWH: dwh DEADBEEF
; 0052: 00000000000   # HEXDWH: cafe: dw 0
; 0053: 00000145376   # HEXDWH: dwh cafe = 0xCAFE
;#PRUEFE-ENDE
