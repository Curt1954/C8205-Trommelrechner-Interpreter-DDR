; makro_attr_kette_stern: eine Kette, die in equ * endet, hat keinen festen Zahlenwert
        start
M1:     MACRO
        dw      $CALC(kb1)
        MEND
        M1
        end
kb0:    equ     *
kb1:    equ     kb0
