; makro_zellen_end: end im Block setzt den Befehlszaehler
        start
M1:     MACRO
        dw      $CALC(zellen(a,b))
        MEND
        M1
a:      dw      1
        end
b:      dw      0
