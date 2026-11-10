; opsymalias.asm - mehrere Namen fuer denselben Code (OPSYM O-12): .LD, .A1 und .A2 sind alle 211
;#PROT STUFE=2
;#OPSYM=alias.opsym
                start                ; Zaehlung beginnt bei 0000
                .JMP    haupt        ; Zelle 0000: Sprung zum Hauptprogramm
a:              dw      5            ; Zelle 0001: Konstante 5
b:              dw      3            ; Zelle 0002: Konstante 3
erg:            dw      0            ; Zelle 0003: Ergebnis
haupt:          .LD     a            ; Zelle 0004: AC := 5
                .A1     a            ; Zelle 0005: AC := 5 (Laden mit Loeschen, keine Addition)
                .A2     b            ; Zelle 0006: AC := 3
                .STO    erg          ; Zelle 0007: erg := 3
                .STOP   0            ; Zelle 0010: Halt
ende:           end

; Sollwerte von Hand hergeleitet: Laden mit Loeschen ersetzt den AC, also AC = 3 = erg; Halt auf 0010, BZ=0011.
;#PRUEFE-START
; BZ=0011 AC=00000000003 US=1
; 0003: 00000000003   # erg
;#PRUEFE-ENDE
