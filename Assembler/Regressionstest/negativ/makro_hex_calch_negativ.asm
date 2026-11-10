; makro_hex_calch_negativ: $CALCH(0-5) mit negativem Ergebnis ist hexadezimal nicht darstellbar
        start
M1:     MACRO
        dw      $CALCH(0-5)
        MEND
        M1
        end
