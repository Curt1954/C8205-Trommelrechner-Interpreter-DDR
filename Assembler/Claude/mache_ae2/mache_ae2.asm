; mache_ae2.asm - Test von MACHE_ADRESSEINHEIT2 ohne eigene Nullspur (nur Arbeitsspur 7640 über SCHIEBE_LI)
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
w1:             dw      5            ; Zelle 0001: Wert 5
w2:             dw      3            ; Zelle 0002: Wert 3
w3:             dw      07           ; Zelle 0003: Wert 7
e1:             dw      0            ; Zelle 0004: Ergebnis 1
e2:             dw      0            ; Zelle 0005: Ergebnis 2
e3:             dw      0            ; Zelle 0006: Ergebnis 3
haupt:          MACHE_ADRESSEINHEIT2 w1 e1 9 ; 5 mal 2^9 (Adresseinheit 01000)
                MACHE_ADRESSEINHEIT2 w2 e2 1 ; 3 mal 2
                MACHE_ADRESSEINHEIT2 w3 e3 3 ; 7 mal 8
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
ende:           end

; Sollwerte von Hand hergeleitet: 5 * 512 = 2560 = 05000 oktal; 3 * 2 = 06; 7 * 8 = 070 oktal.
; Das Hauptprogramm steht ab 0007 (3 Makros zu je 3 Zellen bis 0017), 164 auf 0020, Halt auf 0021, BZ = 0022; AC = letzter Wert 070.
;#PRUEFE-START
; BZ=0022 AC=00000000070 US=1
; 0004: 00000005000   # e1
; 0005: 00000000006   # e2
; 0006: 00000000070   # e3
;#PRUEFE-ENDE
