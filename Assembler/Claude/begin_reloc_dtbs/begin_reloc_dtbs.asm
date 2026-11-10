; begin_reloc_dtbs.asm - verschobener RELOC-EQU-Block mit dtm \...\-Text und Literal in der FILL-Luecke (zweiter Pass-2-Lauf des Optimierers, Assemblerdokumentation 5.4)
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
                begin   RELOC-EQU FILL   ; Block (Gruppe 1): kommt dicht unter 07600, Literale duerfen in die Luecke dahinter
                equ100  *                ; Rasterung 0100
bl:             dtm     \12\             ; drei Zellen: Umschaltzeichen KB, Ziffer 1, Ziffer 2
                bend                     ; Ende des Blocks: 3 Zellen 07500 bis 07502, Luecke ab 07503
erg:            dw      0                ; Zelle 0001: Ergebnis
haupt:          211     #5               ; Zelle 0002: AC := Literal 5 (der Assembler legt es in die Luecke des Blocks)
                240     erg              ; Zelle 0003: (erg) := AC
                020     0                ; Zelle 0004: Halt
ende:           end

; Sollwerte von Hand hergeleitet: dtm 1 setzt das Umschaltzeichen $inkb (Ausgabeadresse 1170), Ziffer 1 hat 0010, Ziffer 2 hat 0020 (Wort 0000 <Adresse> 030).
; Halt auf Zelle 0004, BZ = 0005; das Literal 5 liegt auf 07503, der AC enthaelt 5 und erg ebenfalls.
;#PRUEFE-START
; BZ=0005 AC=00000000005 US=1
; 0001: 00000000005   # erg
; 7500: 00001170030   # dtm: Umschaltzeichen KB
; 7501: 00000010030   # dtm: Ziffer 1
; 7502: 00000020030   # dtm: Ziffer 2
; 7503: 00000000005   # Literal 5 in der Luecke
;#PRUEFE-ENDE
