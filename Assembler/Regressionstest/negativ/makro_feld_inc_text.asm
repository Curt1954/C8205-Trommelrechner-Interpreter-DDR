        start
M1:     MACRO
        $DIM q 4
        $SET q(1) "ab"
        $INC q(1)
        dw 1
        MEND
        M1
        end
