; makro_hex_calch_breite: $CALCH2(256) braucht drei Hexadezimalziffern, mehr als die Breite 2
        start
M1:     MACRO
        dw      $CALCH2(256)
        MEND
        M1
        end
