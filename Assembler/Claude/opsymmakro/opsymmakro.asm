; opsymmakro.asm - Makro ADD und markierter Name .ADD im selben Quelltext (OPSYM O-02: getrennte Namensraeume)
;#PROT STUFE=2
ADD:            MACRO 0
                .ADD    b            ; Makrorumpf mit markiertem Namen: AC := AC + (b)
                MEND
                start                ; Zaehlung beginnt bei 0000
                .JMP    haupt        ; Zelle 0000: Sprung zum Hauptprogramm
a:              dw      5            ; Zelle 0001: Konstante 5
b:              dw      3            ; Zelle 0002: Konstante 3
erg:            dw      0            ; Zelle 0003: Ergebnis
haupt:          .LD     a            ; Zelle 0004: AC := 5
                ADD                  ; Zelle 0005: Makroaufruf ADD, Rumpf .ADD b: AC := 8
                .ADD    b            ; Zelle 0006: direkter markierter Name: AC := 11
                .STO    erg          ; Zelle 0007: erg := 11 (013 oktal)
                .STOP   0            ; Zelle 0010: Halt
ende:           end

; Sollwerte von Hand hergeleitet: 5 + 3 + 3 = 11 dezimal = 013 oktal; Halt auf 0010, BZ=0011.
;#PRUEFE-START
; BZ=0011 AC=00000000013 US=1
; 0003: 00000000013   # erg
;#PRUEFE-ENDE
