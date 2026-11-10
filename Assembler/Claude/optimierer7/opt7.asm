; opt7.asm - Optimierer (Doku Abschnitt 5.1, 5.2): Programm ohne end; ein Literal fuellt den Sprungbereich, die uebrigen stehen am Programmende
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          211     #1           ; Zelle 0001: AC := 1 (Literal l0001, wandert nach 0007)
                210     #2           ; Zelle 0002: AC := AC + 2 (Literal l0002, Programmende 0011)
                210     #3           ; Zelle 0003: AC := AC + 3 (Literal l0003, Programmende 0012)
                210     #4           ; Zelle 0004: AC := AC + 4 (Literal l0004, Programmende 0013)
                164     0001         ; Zelle 0005: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0006: Halt
                equ10   *            ; Zaehler springt von 0007 auf 0010, Sprungbereich nur 0007 (eine Zelle)
                dw      9            ; Zelle 0010: Fueller; kein end im Quelltext

; Sollwerte von Hand: 1+2+3+4 = 10 dezimal = 012 oktal; l0001 auf 0007 (einzige freie Zelle), l0002 bis l0004 hinter dem Fueller auf 0011, 0012, 0013; Halt auf 0006, BZ danach 0007.
;#PRUEFE-START
; BZ=0007 AC=00000000012 US=1
; 0007: 00000000001   # l0001
; 0011: 00000000002   # l0002
; 0012: 00000000003   # l0003
; 0013: 00000000004   # l0004
;#PRUEFE-ENDE
