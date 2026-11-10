; makro_str_begrenzer: ein aufgeloester Text mit dem eigenen Begrenzungszeichen ist ein Fehler
        start
M1:     MACRO
        $SET a 'a"b'
        $UPPER z "$V(a)"
        MEND
        M1
        end
