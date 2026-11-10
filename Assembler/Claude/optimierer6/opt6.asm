; opt6.asm - Optimierer (Doku Abschnitt 5.1, 5.2): Sprungbereich einer spa-Anweisung, zwei Literale wandern hinein
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          211     #1           ; Zelle 0001: AC := 1 (Literal l0001, wandert nach 0005)
                210     #2           ; Zelle 0002: AC := AC + 2 (Literal l0002, wandert nach 0006)
                164     0001         ; Zelle 0003: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0004: Halt
                spa     020          ; Zaehler springt von 0005 auf 0020, Sprungbereich 0005 bis 0017 (13 Zellen)
                dw      9            ; Zelle 0020: Fueller
                end

; Sollwerte von Hand: 1+2 = 3; l0001 auf 0005, l0002 auf 0006 (Reihenfolge der Literaltabelle, aufsteigende Adresse); Halt auf 0004, BZ danach 0005.
;#PRUEFE-START
; BZ=0005 AC=00000000003 US=1
; 0005: 00000000001   # l0001
; 0006: 00000000002   # l0002
; 0020: 00000000011   # Fueller dw 9 (oktal 011)
;#PRUEFE-ENDE
