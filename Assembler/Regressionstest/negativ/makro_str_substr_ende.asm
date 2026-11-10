; makro_str_substr_ende: $SUBSTR mit einem Ende hinter dem Textende ist ein Fehler
        start
M1:     MACRO
        $SUBSTR z "abc" 2 3
        MEND
        M1
        end
