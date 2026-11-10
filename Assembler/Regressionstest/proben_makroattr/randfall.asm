; randfall.asm - Randfaelle der Annahmen 1 und 2 (Ketten, Namenslaenge 32, Parameter als Ausdruck); lauffaehig, Pruefung mit vergleich.py (Doku 4.23)
;#PROT STUFE=2
FRAGE_ART:      MACRO 1
                dw      $CALC(art($1))
                MEND
FRAGE_DEF:      MACRO 1
                dw      $CALC(def($1))
                MEND
FRAGE_ZELLEN:   MACRO 1
                dw      $CALC(zellen($1))
                MEND
WERT:           MACRO 1
                dw      $CALC($1)
                MEND
DOPPELT:        MACRO 1
                dw      $CALC(2*$1)
                MEND
                start
                000     haupt
                FRAGE_ART ka0                           ; E=1
                FRAGE_ART ka1                           ; E=2
                FRAGE_ART ka14                          ; E=2
                FRAGE_ART ka15                          ; E=2
                FRAGE_ART ka16                          ; E=3
                FRAGE_ART ka17                          ; E=3
                FRAGE_DEF ka17                          ; E=1
                WERT ka15                               ; E=3
                WERT ka1                                ; E=3
                FRAGE_ART kb0                           ; E=3
                FRAGE_ART kb1                           ; E=3
                FRAGE_ART kb2                           ; E=3
                FRAGE_DEF kb2                           ; E=1
                FRAGE_ART nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn; E=2
                FRAGE_DEF nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn; E=1
                WERT nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn   ; E=5
                FRAGE_ZELLEN nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnd; E=3
                FRAGE_ART nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnd; E=4
                DOPPELT art(a_equ)+1                    ; E=6
                DOPPELT 2*3                             ; E=12
                DOPPELT zellen(a_db)+art(a_abs)         ; E=12
                WERT art(a_abs)+art(a_equ)*10           ; E=21
haupt:          164     0001
                020     0
a_db:           db      5
ende:           end
ka0:            abs     3
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
kb0:            equ     *
kb1:            equ     kb0
kb2:            equ     kb1
nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn:  equ     5
nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnd:  db      3
a_abs:          abs     5
a_equ:          equ     07640
