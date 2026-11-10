; makro_str_feldindex_aussen: ein Feldindex ausserhalb des Feldes ist ein Fehler
        start
M1:     MACRO
        $DIM f 3
        $UPPER f(4) "x"
        MEND
        M1
        end
