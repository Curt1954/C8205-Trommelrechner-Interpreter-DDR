        start
R5:     MACRO
        $REPT 2
ML0001%: 000 ML0001%
        $ENDREPT
        000 ML0002%
ML0002%: 000 0
        MEND
        R5
        end
