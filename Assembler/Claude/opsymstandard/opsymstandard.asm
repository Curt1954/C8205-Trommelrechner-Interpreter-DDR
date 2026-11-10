; opsymstandard.asm - Standardnamen fuer Operationscodes (OPSYM), im Quelltext mit Punkt geschrieben
                start                ; Zaehlung beginnt bei 0000
                .JMP    haupt        ; Zelle 0000: Sprung zum Hauptprogramm
a:              dw      5            ; Zelle 0001: Konstante 5
b:              dw      3            ; Zelle 0002: Konstante 3
erg:            dw      0            ; Zelle 0003: Ergebnis 1
erg2:           dw      0            ; Zelle 0004: Ergebnis 2
haupt:          .LD     a            ; AC := 5
                .ADD    b            ; AC := 8
                .SUB    a            ; AC := 3
                .STO    erg          ; erg := 3
                .LD     a            ; AC := 5
                .AND    b            ; AC := 5 und 3 = 1
                .STO    erg2         ; erg2 := 1
                .NOP    0001         ; Diagnoseausgabe (nur im Test)
                .STOP   0            ; Halt
ende:           end                  ; 

; Sollwerte von Hand hergeleitet: 5+3-5 = 3 in erg; 5 UND 3 = 1 im AC und in erg2; Halt auf 0015, BZ=0016.
;#PRUEFE-START
; BZ=0016 AC=00000000001 US=1
; 0003: 00000000003   # erg
; 0004: 00000000001   # erg2
;#PRUEFE-ENDE
