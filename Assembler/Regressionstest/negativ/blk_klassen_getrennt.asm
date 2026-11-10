        start
M1: MACRO
        $SPEC   CLASS=KX
        $BLOCK  a
x1:     dw 5
        $ENDBLOCK
        MEND
M2: MACRO
        $SPEC   CLASS=KY
        $BLOCK  a
x2:     dw 6
        $ENDBLOCK
        MEND
        M1
        M2
        020 0
        end
