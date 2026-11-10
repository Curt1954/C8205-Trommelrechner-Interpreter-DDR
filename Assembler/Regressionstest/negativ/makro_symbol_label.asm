        start
G:      MACRO
x:      abs ziel+1
        MEND
N:      MACRO
        dw $CALC(x+1)
        MEND
        G
        N
ziel:   020 0
        end
