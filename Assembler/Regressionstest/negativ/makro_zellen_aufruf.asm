; makro_zellen_aufruf: Makroaufruf im Block: die Zellenzahl steht erst nach dem Aufloesen fest
        start
M2:     MACRO
        dw      1
        MEND
M1:     MACRO
        dw      $CALC(zellen(a,b))
        MEND
        M1
a:      dw      1
        M2
b:      dw      0
        end
