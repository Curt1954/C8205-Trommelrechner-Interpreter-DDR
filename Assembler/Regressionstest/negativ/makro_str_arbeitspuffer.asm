; makro_str_arbeitspuffer: ein Argument mit mehr als 4095 Zeichen nach dem Aufloesen von $V(..) passt nicht in den Arbeitspuffer (5 mal 900 = 4500)
        start
M1:     MACRO
        $SET a "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        $SET b "$V(a)$V(a)$V(a)"
        $SET c "$V(b)$V(b)$V(b)"
        $UPPER z "$V(c)$V(c)$V(c)$V(c)$V(c)"
        MEND
        M1
        end
