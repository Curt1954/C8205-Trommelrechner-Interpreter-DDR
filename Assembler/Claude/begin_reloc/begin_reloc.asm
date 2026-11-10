; begin_reloc.asm - Blockverschiebung mit begin RELOC-EQU [FILL] (Anforderungsdatei Abschnitt 5, Assemblerdokumentation 5.4)
; Vier Bloecke A (FILL, 0150 Zellen), B (040), C (020), D (050); A, B Gruppe 1 (equ100), C, D Gruppe 2 (equ40).
; Der vordere Code addiert die drei Literale 5, 6, 7 und je die erste Zelle der vier Bloecke und speichert die Summe in erg.
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
erg:            dw      0                ; Zelle 0001: Ergebnis (initialisiert)
haupt:          211     #5               ; Zelle 0002: AC := 5 (Literal)
                210     #6               ; Zelle 0003: AC := AC + 6 (Literal)
                210     #7               ; Zelle 0004: AC := AC + 7 (Literal)
                210     a1               ; Zelle 0005: AC := AC + (a1), Block A
                210     b1               ; Zelle 0006: AC := AC + (b1), Block B
                210     c1               ; Zelle 0007: AC := AC + (c1), Block C
                210     d1               ; Zelle 0010: AC := AC + (d1), Block D
                240     erg              ; Zelle 0011: (erg) := AC speichern
                164     0001             ; Zelle 0012: Diagnoseausgabe (nur im Test)
                020     0                ; Zelle 0013: Halt
                begin   RELOC-EQU FILL   ; Block A: wird nach 07400 verschoben, Luecke 07550 bis 07577 fuer Literale
blkA:           equ100  *                ; erste Anweisung: Gruppe 1
a1:             dw      011              ; erste Zelle von Block A
                db      0147             ; Rest von Block A: 0147 Zellen, zusammen 0150
                bend                     ; Ende Block A
                begin   RELOC-EQU        ; Block B ohne FILL: nach 07300
blkB:           equ100  *                ; Gruppe 1
b1:             dw      022              ; erste Zelle von Block B
                db      037              ; Rest von Block B, zusammen 040 Zellen
                bend                     ; Ende Block B
                begin   RELOC-EQU        ; Block C ohne FILL: nach 07240
blkC:           equ40   *                ; Gruppe 2
c1:             dw      033              ; erste Zelle von Block C
                db      017              ; Rest von Block C, zusammen 020 Zellen
                bend                     ; Ende Block C
                begin   RELOC-EQU        ; Block D ohne FILL: nach 07140
blkD:           equ40   *                ; Gruppe 2
d1:             dw      044              ; erste Zelle von Block D
                db      047              ; Rest von Block D, zusammen 050 Zellen
                bend                     ; Ende Block D
ende:           end

; Sollwerte von Hand hergeleitet (Anforderungsdatei Abschnitt 5): Anfaenge A 07400, B 07300, C 07240, D 07140 (07600 - 0200, - 0100, - 040, - 0100).
; Summe 5 + 6 + 7 + 011 + 022 + 033 + 044 = 18 + 9 + 18 + 27 + 36 = 108 dezimal = 0154 oktal. Halt auf 0013, BZ = 0014.
; Literale l0001 bis l0003 (5, 6, 7) liegen in der Luecke von A: 07550, 07551, 07552; die Zelle 07553 bleibt leer.
;#PRUEFE-START
; BZ=0014 AC=00000000154 US=1
; 0001: 00000000154   # erg
; 7400: 00000000011   # a1, Anfang Block A
; 7300: 00000000022   # b1, Anfang Block B
; 7240: 00000000033   # c1, Anfang Block C
; 7140: 00000000044   # d1, Anfang Block D
; 7550: 00000000005   # Literal 5 in der Luecke von A
; 7551: 00000000006   # Literal 6
; 7552: 00000000007   # Literal 7
; 7553: 00000000000   # Luecke bleibt leer
;#PRUEFE-ENDE
