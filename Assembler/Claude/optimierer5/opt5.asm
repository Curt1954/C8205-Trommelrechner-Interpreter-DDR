; opt5.asm - Optimierer (Doku Abschnitt 5.1, 5.2): zwei Sprungbereiche (equ10 * und equ40 *), drei Literale verteilen sich darauf
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          211     #1           ; Zelle 0001: AC := 1 (Literal l0001, wandert nach 0006)
                210     #2           ; Zelle 0002: AC := AC + 2 (Literal l0002, wandert nach 0007)
                210     #3           ; Zelle 0003: AC := AC + 3 (Literal l0003, wandert nach 0011)
                164     0001         ; Zelle 0004: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0005: Halt
                equ10   *            ; Zaehler springt von 0006 auf 0010, Sprungbereich 0006 bis 0007 (zwei Zellen)
                dw      9            ; Zelle 0010: Fueller
                equ40   *            ; Zaehler springt von 0011 auf 0040, Sprungbereich 0011 bis 0037
                dw      9            ; Zelle 0040: Fueller
                end

; Sollwerte von Hand: 1+2+3 = 6; l0001 auf 0006, l0002 auf 0007 (erster Bereich voll), l0003 auf 0011 (zweiter Bereich); Halt auf 0005, BZ danach 0006.
;#PRUEFE-START
; BZ=0006 AC=00000000006 US=1
; 0006: 00000000001   # l0001
; 0007: 00000000002   # l0002
; 0011: 00000000003   # l0003
;#PRUEFE-ENDE
