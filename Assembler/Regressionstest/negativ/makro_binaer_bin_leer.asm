; makro_binaer_bin_leer: 0b ohne Ziffern ist keine Zahl
        start
M1:     MACRO
        dw      $CALC(0b)
        MEND
        M1
        end
