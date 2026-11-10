        start
S8: MACRO a w=1
        $PR(w) 1 2
        dw $a
        MEND
        S8 1 w=5
        end
