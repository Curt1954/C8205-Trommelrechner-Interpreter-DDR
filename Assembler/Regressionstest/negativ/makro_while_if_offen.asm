; makro_while_if_offen: $ENDWHILE, solange ein $IF in der Schleife noch offen ist, ist ein Fehler
        start
W5:     MACRO
        $SET i 0
        $WHILE $V(i) < 2
        $IF $V(i) = 0
        dw 1
        $ENDWHILE
        $ENDIF
        MEND
        W5
        end
