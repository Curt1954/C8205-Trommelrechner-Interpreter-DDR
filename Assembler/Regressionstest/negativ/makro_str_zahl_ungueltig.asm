; makro_str_zahl_ungueltig: ein Zahlenargument, das kein Rechenausdruck ist, ist ein Fehler
        start
M1:     MACRO
        $SUBSTR z "abc" a+
        MEND
        M1
        end
