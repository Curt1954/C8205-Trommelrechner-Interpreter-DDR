; makro_endwhile_ohne_while: $ENDWHILE ohne $WHILE ist ein Fehler
        start
W2:     MACRO
        dw 1
        $ENDWHILE
        MEND
        W2
        end
