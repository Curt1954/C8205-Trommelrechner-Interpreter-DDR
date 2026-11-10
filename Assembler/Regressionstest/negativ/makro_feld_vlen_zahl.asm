        start
M1:     MACRO
        $DIM q 4
        $SET q(1) 5
        dw $V(#q(1))
        MEND
        M1
        end
