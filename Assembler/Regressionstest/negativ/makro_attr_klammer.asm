; makro_attr_klammer: hoechstens ein Klammerpaar um den Namen (Annahme 6): def(((tab))) ist ein Fehler
        start
M1:     MACRO
        dw      $CALC(def(((tab))))
        MEND
        M1
        end
tab:    abs     1
