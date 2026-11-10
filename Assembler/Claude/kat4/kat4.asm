; kat4.asm - Test von kat4 (komprimierter Text, 4 Zeichen je Wort, z0 am letzten Wort) und begin/bend
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
t1:             kat4    ab12         ; Zelle 0001: genau ein volles Wort
t2:             kat4    abcde        ; Zellen 0002 und 0003: volles Wort, dann Rest mit z0
t3:             kat4    \a b\        ; Zelle 0004: drei Zeichen mit Leerzeichen, links aufgefuellt
haupt:          020     0            ; Zelle 0005: Halt
                begin                ; Beginn eines Blocks (kein Speicher, kein Code)
d1:             dw      07           ; Zelle 0006: Konstante
d2:             dw      010          ; Zelle 0007: Konstante
                bend                 ; Ende des Blocks
ende:           end

; Sollwerte von Hand aus der Kodetabelle hergeleitet (Ausgabeadresse >> 3, 8 Bit je Zeichen, erstes Zeichen rechts, z0 = 040000000000).
; a = 0610 -> 061, b = 0620 -> 062, c = 0430 -> 043, d = 0640 -> 064, e = 0450 -> 045, 1 = 0010 -> 001, 2 = 0020 -> 002, Leerzeichen = 0320 -> 032.
;#PRUEFE-START
; BZ=0006
; 0001: 40200231061   # t1
; 0002: 06410631061   # t2 (a b c d)
; 0003: 40000000045   # t2 (e, z0)
; 0004: 40014415061   # t3
; 0006: 00000000007   # d1
; 0007: 00000000010   # d2
;#PRUEFE-ENDE
