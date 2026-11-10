; opt1.asm - Optimierer (Doku Abschnitt 5): zwei Literale und eine dw-Zeile wandern in den Sprungbereich von equ40 *
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          211     #5           ; Zelle 0001: AC := 5 (Literal l0001, wandert nach 0006)
                210     #7           ; Zelle 0002: AC := AC + 7 (Literal l0002, wandert nach 0007)
                240     erg          ; Zelle 0003: (erg) := AC
                164     0001         ; Zelle 0004: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0005: Halt
                equ40   *            ; Zaehler springt von 0006 auf 0040, Sprungbereich 0006 bis 0037 ist frei
                dw      3            ; Zelle 0040: Fueller ohne Marke, nie verlegbar (dw unmittelbar hinter equ40)
erg:            dw      0            ; ohne Optimierer Zelle 0041; mit Optimierer Zelle 0010 (erg wird nur als Adressteil benutzt)
ende:           end

; Sollwerte von Hand: 5 + 7 = 12 dezimal = 014 oktal; erg liegt nach dem Verlegen auf Zelle 0010; Halt auf 0005.
;#PRUEFE-START
; BZ=0006 AC=00000000014 US=1
; 0010: 00000000014   # erg
;#PRUEFE-ENDE
