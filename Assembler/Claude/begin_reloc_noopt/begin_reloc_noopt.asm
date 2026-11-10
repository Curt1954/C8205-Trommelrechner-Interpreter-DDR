; begin_reloc_noopt.asm - dasselbe Programm wie begin_reloc, aber mit --no-opt: keine Blockverschiebung, keine Literalverlegung
; Die Option steht in der Marker-Zeile unten; asm_und_test.sh liest sie (im Regressionstest ohne Wirkung: dort laeuft das Programm mit Optimierer).
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

; Sollwerte von Hand hergeleitet (ohne Optimierer bleiben die Bloecke an ihrer Quelltextstelle, equ100 und equ40 rufen die Grenze auf):
; Vorderteil 0000 bis 0013; A: equ100 -> 0100, 0150 Zellen bis 0247; B: naechste 0100-Grenze nach 0250 ist 0300, 040 Zellen bis 0337;
; C: equ40, 0340 ist 040-Grenze, 020 Zellen bis 0357; D: naechste 040-Grenze nach 0360 ist 0400, 050 Zellen bis 0447; Literale dahinter 0450 bis 0452.
; Summe wie in begin_reloc: 5 + 6 + 7 + 011 + 022 + 033 + 044 = 0154.
;#ASMOPTIONEN --no-opt
;#PRUEFE-START
; BZ=0014 AC=00000000154 US=1
; 0001: 00000000154   # erg
; 0100: 00000000011   # a1
; 0300: 00000000022   # b1
; 0340: 00000000033   # c1
; 0400: 00000000044   # d1
; 0450: 00000000005   # Literal 5
; 0451: 00000000006   # Literal 6
; 0452: 00000000007   # Literal 7
;#PRUEFE-ENDE
