; makro_attr_zellen_aufruf: zellen auf einer Marke auf einem Makroaufruf: die Zellenzahl steht erst nach dem Aufloesen fest
        start
M2:     MACRO
        dw      1
        MEND
M1:     MACRO
        dw      $CALC(zellen(x))
        MEND
        M1
        end
x:      M2
