; dt_text_lauf2.asm - dtm mit \...\-Text und Literal in einer equ10-Luecke: der Optimierer laeuft Pass 2 ein zweites Mal (bis c82ass 1.02-002 ging der Text dabei verloren)
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
t1:             dtm     \12\             ; Zellen 0001 bis 0003: Umschaltzeichen KB, Ziffer 1, Ziffer 2
                equ10   *                ; auf 0010 aufrunden: Luecke 0004 bis 0007, dort legt der Assembler das Literal ab
haupt:          211     #5               ; Zelle 0010: AC := Literal 5 (Zelle 0004)
                240     erg              ; Zelle 0011: (erg) := AC
                020     0                ; Zelle 0012: Halt
erg:            dw      0                ; Zelle 0013: Ergebnis
ende:           end

; Sollwerte von Hand hergeleitet: dtm 1 setzt das Umschaltzeichen $inkb (Ausgabeadresse 1170), Ziffer 1 hat 0010, Ziffer 2 hat 0020 (Wort 0000 <Adresse> 030).
; Halt auf Zelle 0012, BZ = 0013; das Literal 5 liegt auf Zelle 0004, der AC enthaelt 5.
;#PRUEFE-START
; BZ=0013 AC=00000000005 US=1
; 0001: 00001170030   # dtm: Umschaltzeichen KB
; 0002: 00000010030   # dtm: Ziffer 1
; 0003: 00000020030   # dtm: Ziffer 2
; 0004: 00000000005   # Literal 5 in der Luecke
; 0013: 00000000005   # erg
;#PRUEFE-ENDE
