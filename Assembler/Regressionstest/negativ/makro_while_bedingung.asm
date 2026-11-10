; makro_while_bedingung: eine unvollstaendige Bedingung in $WHILE ist ein Fehler
        start
W7:     MACRO
        $SET i 0
        $WHILE $V(i) <
        dw 1
        $ENDWHILE
        MEND
        W7
        end
