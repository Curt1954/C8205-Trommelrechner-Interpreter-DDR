; makro_adr_abstand_ein: abstand mit nur einem Namen: das zweite Argument fehlt
        start
M:      MACRO
        dw      $CALC(abstand(a))
        MEND
        M
a:      dw      1
        end
