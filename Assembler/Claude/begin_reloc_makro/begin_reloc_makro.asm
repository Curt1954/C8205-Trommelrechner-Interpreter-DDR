; begin_reloc_makro.asm - ein Makro erzeugt den Block (begin RELOC-EQU, lokale Marke tab%) und greift danach auf ihn zu. Assemblerdokumentation 4.3, 5.4.
TAB:            MACRO   0                ; Block mit 16 Zellen und ein Zugriff darauf
                begin   RELOC-EQU        ; Block verschieben
tab%:           equ100  *                ; Gruppe 1, lokale Marke
                dw      7                ; erste Zelle
                db      017              ; Rest, zusammen 020 Zellen
                bend                     ; Ende
                210     tab%             ; AC := AC + (tab%), Befehl im Vorderteil
                MEND                     ; Ende
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
erg:            dw      0                ; Zelle 0001: Ergebnis
haupt:          211     erg              ; Zelle 0002: AC := (erg) = 0
                TAB                      ; Zelle 0003: AC := AC + 7
                240     erg              ; Zelle 0004: (erg) := AC
                020     0                ; Zelle 0005: Halt
ende:           end

; Sollwerte von Hand hergeleitet: Block 020 Zellen, aufgerundet 0100, Anfang 07500; AC = 0 + 7 = 7. Halt auf 0005, BZ = 0006.
;#PRUEFE-START
; BZ=0006 AC=00000000007 US=1
; 0001: 00000000007   # erg
; 7500: 00000000007   # erste Zelle des Blocks
;#PRUEFE-ENDE
