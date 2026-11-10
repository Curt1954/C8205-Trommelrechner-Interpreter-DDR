; opsymzeile.asm - Name im Quelltext mit  NAME: opsym <code>  (OPSYM O-13); ein Label gleichen Namens bleibt ein Symbol (O-28)
;#PROT STUFE=2
                start                ; Zaehlung beginnt bei 0000
HOL:            opsym   211          ; Name HOL fuer den Code 211 (kein Symbol, keine Adresse)
SPE:            opsym   240          ; Name SPE fuer den Code 240
                .JMP    haupt        ; Zelle 0000: Sprung zum Hauptprogramm
hol:            dw      7            ; Zelle 0001: Label hol (Symbol) neben dem Namen .HOL
erg:            dw      0            ; Zelle 0002: Ergebnis
haupt:          .HOL    hol          ; Zelle 0003: AC := 7
                .SPE    erg          ; Zelle 0004: erg := 7
                .STOP   0            ; Zelle 0005: Halt
ende:           end

; Sollwerte von Hand hergeleitet: AC und erg = 7; Halt auf 0005, BZ=0006.
;#PRUEFE-START
; BZ=0006 AC=00000000007 US=1
; 0002: 00000000007   # erg
;#PRUEFE-ENDE
