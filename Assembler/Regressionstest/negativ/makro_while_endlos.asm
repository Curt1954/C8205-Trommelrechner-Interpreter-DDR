; makro_while_endlos: eine Bedingung, die immer wahr bleibt, endet nach 4096 Durchlaeufen mit einem Fehler (keine Endlosschleife)
        start
W3:     MACRO
        $SET i 0
        $WHILE $V(i) >= 0
        $INC i
        $ENDWHILE
        MEND
        W3
        end
