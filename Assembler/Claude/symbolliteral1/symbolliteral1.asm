; symbolliteral1.asm - Symbol-Literal !<symbolname> (Anforderungen_Symbolliteral.md, ab c82ass 1.03-005)
; Zwei Arbeitszellen hilf und hilf2 entstehen aus !hilf und !hilf2 (hilf zweimal benutzt = eine Zelle). Ohne Sprungbereich bleiben sie
; als "hilf dbn 1" und "hilf2 dbn 1" hinter end (Reihenfolge des ersten Auftretens).
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
wert:           dw      017              ; Zelle 0001
wert2:          dw      05               ; Zelle 0002
erg:            dw      0                ; Zelle 0003
erg2:           dw      0                ; Zelle 0004
haupt:          211     wert2            ; Zelle 0005: AC := 5
                240     !hilf            ; Zelle 0006: (hilf) := 5
                211     wert             ; Zelle 0007: AC := 017
                240     !hilf2           ; Zelle 0010: (hilf2) := 017
                211     !hilf            ; Zelle 0011: AC := (hilf) = 5
                240     erg              ; Zelle 0012: (erg) := 5
                211     !hilf2           ; Zelle 0013: AC := (hilf2) = 017
                240     erg2             ; Zelle 0014: (erg2) := 017
                164     0001             ; Zelle 0015: Diagnoseausgabe (nur im Test)
                020     0                ; Zelle 0016: Halt
ende:           end

; Sollwerte von Hand hergeleitet: hilf liegt auf 0017, hilf2 auf 0020; Halt auf 0016, BZ danach 0017.
;#PRUEFE-START
; BZ=0017 AC=00000000017 US=1
; 0003: 00000000005   # erg
; 0004: 00000000017   # erg2
; 0017: 00000000005   # hilf
; 0020: 00000000017   # hilf2
;#PRUEFE-ENDE
