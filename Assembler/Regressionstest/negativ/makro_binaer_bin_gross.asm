; makro_binaer_bin_gross: 0b mit 64 Einsen liegt ausserhalb des Zahlenbereichs
        start
M1:     MACRO
        dw      $CALC(0b1111111111111111111111111111111111111111111111111111111111111111)
        MEND
        M1
        end
