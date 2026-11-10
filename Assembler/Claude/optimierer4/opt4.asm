; opt4.asm - Optimierer (Doku Abschnitt 5.2): steht ein Literalsymbol im Quelltext (l0002-l0001), wird nichts umgeordnet
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          211     #5           ; Zelle 0001: AC := 5 (Literal l0001)
                210     #7           ; Zelle 0002: AC := AC + 7 (Literal l0002)
                240     erg          ; Zelle 0003: (erg) := AC
                164     0001         ; Zelle 0004: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0005: Halt
                equ40   *            ; Zaehler springt von 0006 auf 0040
                dw      3            ; Zelle 0040: Fueller
erg:            dw      0            ; Zelle 0041: bleibt, weil Literalsymbol im Quelltext
diff:           dw      l0002-l0001  ; Zelle 0042: Literalsymbol im Quelltext (Abstand 1)
ende:           end

; Sollwerte von Hand: 5+7 = 12 = 014 oktal; erg bleibt auf 0041; Literale hinter end: l0001 auf 0043 (5), l0002 auf 0044 (7); diff = 1.
;#PRUEFE-START
; BZ=0006 AC=00000000014 US=1
; 0041: 00000000014   # erg
; 0043: 00000000005   # Literal 5
; 0044: 00000000007   # Literal 7
;#PRUEFE-ENDE
