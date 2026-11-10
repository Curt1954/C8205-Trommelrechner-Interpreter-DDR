; opt3.asm - Optimierer (Doku Abschnitt 5.4): dw-Zeile in einem begin-bend-Block wird nicht verlegt, das Literal schon
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          211     #5           ; Zelle 0001: AC := 5 (Literal, wandert nach 0005)
                240     erg          ; Zelle 0002: (erg) := AC
                164     0001         ; Zelle 0003: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0004: Halt
                equ40   *            ; Zaehler springt von 0005 auf 0040
                dw      3            ; Zelle 0040: Fueller
                begin                ; Beginn des Blocks: nichts darin wird verlegt
erg:            dw      0            ; Zelle 0041: bleibt, weil im Block
                bend                 ; Ende des Blocks
ende:           end

; Sollwerte von Hand: AC = 5; Literal auf 0005; erg bleibt auf 0041; Halt auf 0004, BZ danach 0005.
;#PRUEFE-START
; BZ=0005 AC=00000000005 US=1
; 0005: 00000000005   # Literal
; 0041: 00000000005   # erg
;#PRUEFE-ENDE
