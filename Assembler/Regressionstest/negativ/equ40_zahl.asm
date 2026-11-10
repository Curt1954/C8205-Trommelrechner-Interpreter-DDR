; equ40_zahl.asm - Negativtest: equ40 mit Zahl als Operand ist unzulaessig (Doku 3.3.8, 5.1), erlaubt ist nur equ40 *
                start                ; Zaehlung beginnt bei 0000
                020     0            ; Zelle 0000: Halt
                equ40   0200         ; Fehler: Operand muss * sein
                dw      9            ; Zelle 0200: Fueller
                end
