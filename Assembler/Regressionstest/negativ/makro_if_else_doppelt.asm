        start
E1:     MACRO 1
        $IF $1 = 1
        dw 1
        $ELSE
        dw 2
        $ELSE
        dw 3
        $ENDIF
        MEND
        E1 1
        end
