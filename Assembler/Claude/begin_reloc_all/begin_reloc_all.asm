; begin_reloc_all.asm - begin RELOC-ALL: Bloecke mit und ohne equ100 (Assemblerdokumentation 3.3.12 und 5.4, ab c82ass 1.03-011)
; Block A: RELOC-ALL mit equ100 (Gruppe 1, wie RELOC-EQU), 3 Zellen, aufgerundet auf 0100, Anfang 07500, Luecke 07503 bis 07577.
; Block B: RELOC-ALL ohne equ (Gruppe 4), 5 Zellen, Marke blkB auf der begin-Zeile; kommt in die Luecke von A.
; Block C: RELOC-ALL FILL ohne equ, 2 Zellen (FILL ohne Wirkung, weil keine Ausrichtung); kommt hinter B in dieselbe Luecke.
; Block D: RELOC-ALL ohne equ, 0100 Zellen, passt nicht in die Luecke (075 Zellen); kommt dicht unter A.
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
erg:            dw      0                ; Zelle 0001: Ergebnis
haupt:          211     a1               ; Zelle 0002: AC := (a1), Block A
                210     b1               ; Zelle 0003: AC := AC + (b1), Block B
                210     blkB             ; Zelle 0004: AC := AC + (blkB), Marke auf der begin-Zeile von B (= b1)
                210     c1               ; Zelle 0005: AC := AC + (c1), Block C
                210     d1               ; Zelle 0006: AC := AC + (d1), Block D
                240     erg              ; Zelle 0007: (erg) := AC
                020     0                ; Zelle 0010: Halt
                begin   RELOC-ALL        ; Block A: Gruppe 1
blkA:           equ100  *                ; erste Anweisung: Gruppe 1
a1:             dw      1                ; erste Zelle von Block A
                db      2                ; Rest: zusammen 3 Zellen
                bend                     ; Ende Block A
blkB:           begin   RELOC-ALL        ; Block B: keine equ-Zeile, Gruppe 4
b1:             dw      2                ; erste Zelle von Block B
                db      4                ; Rest: zusammen 5 Zellen
                bend                     ; Ende Block B
                begin   RELOC-ALL FILL   ; Block C: Gruppe 4, FILL ohne Wirkung
c1:             dw      4                ; erste Zelle von Block C
                db      1                ; zusammen 2 Zellen
                bend                     ; Ende Block C
                begin   RELOC-ALL        ; Block D: Gruppe 4, 0100 Zellen
d1:             dw      8                ; erste Zelle von Block D
                db      077              ; zusammen 0100 Zellen
                bend                     ; Ende Block D
ende:           end

; Sollwerte von Hand hergeleitet: A bei 07500 (07600 - 0100), Luecke 07503 bis 07577 (075 Zellen). Gruppe 4 groesster Block zuerst:
; D (0100) passt nicht in die Luecke und liegt dicht unter A: 07500 - 0100 = 07400. B (5) kommt an den Anfang der Luecke: 07503.
; C (2) folgt: 07510. Summe a1 + b1 + blkB + c1 + d1 = 1 + 2 + 2 + 4 + 8 = 17 dezimal = 021 oktal. Halt auf 0010, BZ = 0011.
;#PRUEFE-START
; BZ=0011 AC=00000000021 US=1
; 0001: 00000000021   # erg
; 7500: 00000000001   # a1, Anfang Block A
; 7503: 00000000002   # b1, Anfang Block B (in der Luecke von A)
; 7510: 00000000004   # c1, Anfang Block C (hinter B)
; 7400: 00000000010   # d1, Anfang Block D (unter A)
;#PRUEFE-ENDE
