; begin_reloc_g2.asm - nur Gruppe 2 (equ40) mit FILL: ein Block mit 3 Zellen wird auf 040 Zellen aufgerundet und nach 07540 verschoben,
; das Literal 9 kommt in die Luecke hinter dem Blockende (07543). Assemblerdokumentation 5.4, Anforderungsdatei Abschnitt 4 und 5.
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
erg:            dw      0                ; Zelle 0001: Ergebnis
haupt:          211     #9               ; Zelle 0002: AC := 9 (Literal)
                210     x1               ; Zelle 0003: AC := AC + (x1), Block X
                240     erg              ; Zelle 0004: (erg) := AC
                020     0                ; Zelle 0005: Halt
                begin   RELOC-EQU FILL   ; Block X: Gruppe 2, mit Luecke fuer Literale
blkX:           equ40   *                ; erste Anweisung: Gruppe 2
x1:             dw      5                ; erste Zelle von Block X
                db      2                ; Rest: zusammen 3 Zellen
                bend                     ; Ende Block X
ende:           end

; Sollwerte von Hand hergeleitet: Block X belegt 3 Zellen, aufgerundet auf 040; der Anfang ist 07600 - 040 = 07540 (keine Gruppe 1 davor).
; Das Blockende liegt bei 07543, dahinter folgt die Luecke bis 07577; dort steht das Literal 9 auf 07543. Summe 9 + 5 = 14 dezimal = 016 oktal.
; Halt auf 0005, BZ = 0006.
;#PRUEFE-START
; BZ=0006 AC=00000000016 US=1
; 0001: 00000000016   # erg
; 7540: 00000000005   # x1, Anfang Block X
; 7543: 00000000011   # Literal 9 in der Luecke
; 7544: 00000000000   # Luecke bleibt leer
;#PRUEFE-ENDE
