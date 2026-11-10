        start
M1: MACRO
        $SPEC   CLASS=KX
        $BLOCK  hilf
hz:     dw 5
        $ENDBLOCK
        020 0
        MEND
M2: MACRO
        $SPEC   CLASS=KX
        $BLOCK  hilf
hz:     dw 5
        $ENDBLOCK
        020 1
        MEND
        M1
        M2
        M2
        020 0
        end
