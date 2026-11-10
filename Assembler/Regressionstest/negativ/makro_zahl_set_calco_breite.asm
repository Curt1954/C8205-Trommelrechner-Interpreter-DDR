; makro_zahl_set_calco_breite: $CALCO2 mit mehr als zwei Ziffern (512 = 01000) im Text von $SET ist ein Fehler (Z-03)
        start
M1:     MACRO
        $SET n 512
        $SET t "x$CALCO2($V(n))"
        MEND
        M1
        end
