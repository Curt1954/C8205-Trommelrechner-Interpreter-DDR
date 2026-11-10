; makro_zahl_str_calc: Division durch 0 im $CALC eines Textarguments von $STRCMP (nach dem Aufloesen von $V) ist ein Fehler der Funktion (Z-02, Z-03)
        start
M1:     MACRO
        $SET z 0
        $STRCMP r "$CALC(1/$V(z))" "x"
        MEND
        M1
        end
