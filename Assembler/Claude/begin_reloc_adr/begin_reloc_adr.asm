; begin_reloc_adr.asm - adr und abstand ueber einen verschobenen Block (Probelaeufe sehen die verschobenen Adressen). Assemblerdokumentation 4.23, 5.4.
ABST:           MACRO   2                ; Abstand zweier Marken als Wort ablegen
                dw      $CALC(abstand($1,$2)) ; Abstand
                MEND                     ; Ende
ADRW:           MACRO   1                ; Adresse einer Marke als Wort ablegen
                dw      $CALC(adr($1))   ; Adresse
                MEND                     ; Ende
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          020     0                ; Zelle 0001: Halt
                begin   RELOC-EQU        ; Block: 5 Zellen, aufgerundet 0100, Anfang 07500
blk:            equ100  *                ; Gruppe 1
b1:             dw      1                ; erste Zelle, 07500
                db      3                ; 07501 bis 07503
b2:             dw      2                ; 07504
                bend                     ; Ende
                ABST    b1 b2            ; Zelle 0002: Abstand b1 bis b2 = 4
                ADRW    b2               ; Zelle 0003: Adresse von b2 = 07504
ende:           end

; Sollwerte von Hand hergeleitet: Block 5 Zellen, aufgerundet 0100, Anfang 07600 - 0100 = 07500; b2 liegt vier Zellen hinter b1 (07504).
; Abstand 4, Adresse 07504. Halt auf 0001, BZ = 0002.
;#PRUEFE-START
; BZ=0002 US=1
; 0002: 00000000004   # abstand(b1,b2)
; 0003: 00000007504   # adr(b2)
; 7500: 00000000001   # b1
; 7504: 00000000002   # b2
;#PRUEFE-ENDE
