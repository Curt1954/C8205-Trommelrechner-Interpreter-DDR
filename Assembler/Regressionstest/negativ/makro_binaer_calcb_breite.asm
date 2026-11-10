; makro_binaer_calcb_breite: $CALCB4(16) braucht fuenf Binaerziffern, mehr als die Breite 4
        start
M1:     MACRO
        dw      $CALCB4(16)
        MEND
        M1
        end
