; opsymdatei.asm - Namensdatei per ;#OPSYM=<Pfad> (OPSYM O-04), Projektnamen neben Standardnamen
;#PROT STUFE=2
;#OPSYM=namen.opsym
                start                ; Zaehlung beginnt bei 0000
                .JMP    haupt        ; Zelle 0000: Sprung zum Hauptprogramm
a:              dw      5            ; Zelle 0001: Konstante 5
b:              dw      3            ; Zelle 0002: Konstante 3
erg:            dw      0            ; Zelle 0003: Ergebnis
haupt:          .HOLE   a            ; Zelle 0004: Projektname: AC := 5
                .ADD    b            ; Zelle 0005: Standardname: AC := 8
                .SPEI   erg          ; Zelle 0006: Projektname: erg := 8
                .STOP   0            ; Zelle 0007: Halt
ende:           end

; Sollwerte von Hand hergeleitet: 5 + 3 = 8 dezimal = 010 oktal; Halt auf 0007, BZ=0010.
;#PRUEFE-START
; BZ=0010 AC=00000000010 US=1
; 0003: 00000000010   # erg
;#PRUEFE-ENDE
