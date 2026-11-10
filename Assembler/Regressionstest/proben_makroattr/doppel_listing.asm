; doppel_listing.asm - Annahme 2: mehrere Zeilen mit derselben Marke; der Assembler meldet doppelte Symbole (rc 16), gelesen wird nur das Listing (vergleich_listing.py)
FRAGE_ART:      MACRO 1
                dw      $CALC(art($1))
                MEND
FRAGE_ZELLEN:   MACRO 1
                dw      $CALC(zellen($1))
                MEND
                start
                FRAGE_ART d1            ; E=1
                FRAGE_ART d2            ; E=2
                FRAGE_ART d3            ; E=2
                FRAGE_ZELLEN d3         ; E=4
                FRAGE_ART d4            ; E=4
                FRAGE_ART d5            ; E=3
                020     0
ende:           end
d1:             equ     *
d1:             abs     7
d2:             equ     5
d2:             abs     6
d3:             db      4
d3:             equ     5
d4:             db      4
d4:             equ     *
d5:             equ     *
d5:             db      4
