; makrosymbol3.asm - Test: von Makros und von $REPT im Quelltext erzeugte abs-Symbole in $CALC (Assemblerdokumentation 4.18, c82ass ab 1.01-011);
;                    der Quelltext hat $-Zeilen: Pass 0 wertet ihn vorab aus (4.1) und loest die Makroaufrufe dabei an Ort und Stelle auf
;#DOK-0001 Test: sq0=10 und sq1=20 aus $REPT im Quelltext, GROESSE erzeugt gr=$1*2, die Makros N1 bis N3 lesen sie in $CALC, $IF und $REPT
;#PROT STUFE=2
GROESSE:        MACRO   1
gr:             abs     $CALC($1*2)                 ; Zahlensymbol, Wert = Parameter*2
                MEND
N1:             MACRO
                dw      $CALC(sq0+sq1)              ; 10+20 = 30
                dw      $CALC(gr+1)                 ; 14+1 = 15
                MEND
N2:             MACRO
                $IF     $CALC(gr) > 10
                dw      1                           ; gr = 14 > 10: wahr
                $ELSE
                dw      0
                $ENDIF
                MEND
N3:             MACRO
                $REPT   gr/7                        ; 14/7 = 2 Durchlaeufe
                dw      $CALC($Z1+sq1)              ; 20, 21
                $ENDREPT
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                $REPT   2
sq$Z1:          abs     $CALC(($Z1+1)*10)           ; sq0 = 10, sq1 = 20 (vom Quelltext erzeugt)
                $ENDREPT
                GROESSE 7            ; erzeugt gr = 14 (keine Zelle)
                N1                   ; Zellen 0001 und 0002
                N2                   ; Zelle 0003
                N3                   ; Zellen 0004 und 0005
haupt:          020     0            ; Zelle 0006: Halt
ende:           end

; Sollwerte von Hand hergeleitet; Halt auf 0006, BZ danach 0007.
; 10+20=30=036; 14+1=15=017; 14>10 -> 1; $Z1+20: 20=024, 21=025.
;#PRUEFE-START
; BZ=0007 US=1
; 0001: 00000000036   # sq0+sq1 = 30
; 0002: 00000000017   # gr+1 = 15
; 0003: 00000000001   # $IF gr>10: wahr
; 0004: 00000000024   # $REPT gr/7, Durchlauf 0: 20
; 0005: 00000000025   # Durchlauf 1: 21
;#PRUEFE-ENDE
