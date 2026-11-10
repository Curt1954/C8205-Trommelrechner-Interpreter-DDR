        start
S7: MACRO a w=9
        $PR(w) 1 2
        dw $a
        MEND
        S7 1
        end
