; makro_hex_hex_leer: 0x ohne Ziffern ist keine Zahl
        start
M1:     MACRO
        dw      $CALC(0x)
        MEND
        M1
        end
