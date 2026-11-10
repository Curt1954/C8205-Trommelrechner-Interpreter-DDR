; makro_hex_hex_gross: 0x8000000000000000 (2^63) liegt ausserhalb des Zahlenbereichs
        start
M1:     MACRO
        dw      $CALC(0x8000000000000000)
        MEND
        M1
        end
