; makro_str_index_leer: $INDEX mit leerem Suchtext ist ein Fehler
        start
M1:     MACRO
        $INDEX p "abc" ""
        MEND
        M1
        end
