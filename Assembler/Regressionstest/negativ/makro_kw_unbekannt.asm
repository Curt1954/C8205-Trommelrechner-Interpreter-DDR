        start
SCHIEBE: MACRO ziel anzahl=1 richtung=LI
        dw $ziel
        dw $anzahl
        MEND
        SCHIEBE 1 foo=2
        end
