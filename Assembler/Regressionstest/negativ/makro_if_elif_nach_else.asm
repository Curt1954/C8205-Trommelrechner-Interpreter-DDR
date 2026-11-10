        start
E2:     MACRO 1
        $IF $1 = 1
        dw 1
        $ELSE
        dw 2
        $ELIF $1 = 2
        dw 3
        $ENDIF
        MEND
        E2 1
        end
