; makro_local_rept: eine lokale Variable in der Anzahl von $REPT gibt es noch nicht ($REPT wird vor $LOCAL aufgeloest)
        start
L8:     MACRO
        $LOCAL n
        $SET n 2
        $REPT $V(n)
        dw 1
        $ENDREPT
        MEND
        L8
        end
