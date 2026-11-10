        start
M1: MACRO
        $SPEC   CLASS=KX
        $BLOCK  a
x1:     dw 5
        $ENDBLOCK
        MEND
M2: MACRO
        $SPEC   CLASS=KX
        $BLOCK  b
x1:     dw 5
        $ENDBLOCK
        MEND
        M1
        M2
        end
