; makro_zellen_zweiter_name: der zweite Symbolname fehlt
        start
M1:     MACRO
        dw      $CALC(zellen(a,))
        MEND
        M1
a:      dw      1
b:      dw      0
        end
