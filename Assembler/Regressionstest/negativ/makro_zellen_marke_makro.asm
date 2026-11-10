; makro_zellen_marke_makro: die Marke bis hat ein Makro erzeugt und steht nicht im Quelltext
        start
M2:     MACRO
erz:    abs     5
        MEND
M1:     MACRO
        dw      $CALC(zellen(a,erz))
        MEND
a:      dw      1
        M2
        M1
        end
