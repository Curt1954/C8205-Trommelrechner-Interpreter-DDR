; makro_zahl_set_calco_negativ: $CALCO mit negativem Ergebnis im Text von $SET ist ein Fehler (Z-03)
        start
M1:     MACRO
        $SET n 5
        $SET t "$CALCO(3-$V(n))"
        MEND
        M1
        end
