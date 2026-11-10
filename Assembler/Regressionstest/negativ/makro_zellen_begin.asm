; makro_zellen_begin: begin im Block setzt den Befehlszaehler
        start
M1:     MACRO
        dw      $CALC(zellen(a,b))
        MEND
        M1
a:      dw      1
        begin   020
b:      dw      0
        end
