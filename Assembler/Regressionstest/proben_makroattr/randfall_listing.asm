; randfall_listing.asm - Randfaelle der Annahmen 1 und 2 mit Zyklus, equ/abs ohne Operand: der Assembler lehnt das Programm ab (rc 16), gelesen wird nur das Listing (vergleich_listing.py)
;#PROT STUFE=2
FRAGE_ART:      MACRO 1
                dw      $CALC(art($1))              ; Art des Symbols
                MEND
FRAGE_DEF:      MACRO 1
                dw      $CALC(def($1))              ; 1, wenn das Symbol vorhanden ist
                MEND
FRAGE_ZELLEN:   MACRO 1
                dw      $CALC(zellen($1))           ; Zellenzahl
                MEND
WERT:           MACRO 1
                dw      $CALC($1)                   ; Wert des Ausdrucks
                MEND
DOPPELT:        MACRO 1
                dw      $CALC(2*$1)                 ; Parameter wird eingeklammert eingesetzt
                MEND
                start
                000     haupt
                FRAGE_ART za            ; E=3
                FRAGE_ART zb            ; E=3
                FRAGE_ART zs            ; E=3
                FRAGE_DEF za            ; E=1
                FRAGE_DEF zs            ; E=1
                FRAGE_ART ka0           ; E=1
                FRAGE_ART ka1           ; E=2
                FRAGE_ART ka14          ; E=2
                FRAGE_ART ka15          ; E=2
                FRAGE_ART ka16          ; E=3
                FRAGE_ART ka17          ; E=3
                FRAGE_DEF ka17          ; E=1
                WERT ka15               ; E=3
                FRAGE_ART kb1           ; E=3
                FRAGE_ART kb2           ; E=3
                FRAGE_ART eo            ; E=3
                FRAGE_DEF eo            ; E=1
                FRAGE_ART ao            ; E=3
                FRAGE_ART nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn; E=2
                FRAGE_DEF nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn; E=1
                FRAGE_ZELLEN nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnd; E=3
                DOPPELT art(a_equ)+1    ; E=6
                DOPPELT 2*3             ; E=12
haupt:          164     0001
                020     0
ende:           end
za:             equ     zb              ; Zyklus mit zwei Symbolen
zb:             equ     za
zs:             equ     zs              ; Selbstverweis
ka0:            abs     3               ; Kette A: ka0 abs, ka1..ka17 je equ auf den Vorgaenger
ka1:            equ     ka0
ka2:            equ     ka1
ka3:            equ     ka2
ka4:            equ     ka3
ka5:            equ     ka4
ka6:            equ     ka5
ka7:            equ     ka6
ka8:            equ     ka7
ka9:            equ     ka8
ka10:           equ     ka9
ka11:           equ     ka10
ka12:           equ     ka11
ka13:           equ     ka12
ka14:           equ     ka13
ka15:           equ     ka14
ka16:           equ     ka15
ka17:           equ     ka16
kb0:            equ     *               ; Kette B endet in einer Adresse
kb1:            equ     kb0
kb2:            equ     kb1
eo:             equ                     ; equ ohne Operand
ao:             abs                     ; abs ohne Operand
nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn:  equ     5                       ; Name mit 32 Zeichen
nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnd:  db      3                       ; Name mit 32 Zeichen auf db
a_abs:          abs     5
a_equ:          equ     07640
