; makro_hex_calch_breite17: $CALCH17(1): die Breite liegt ausserhalb von 1 bis 16
        start
M1:     MACRO
        dw      $CALCH17(1)
        MEND
        M1
        end
