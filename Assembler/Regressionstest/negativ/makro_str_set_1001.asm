; makro_str_set_1001: ein $SET-Text mit 1001 Zeichen ist ein Fehler (hoechstens 1000, ab c82ass 1.01-015)
        start
M1:     MACRO
        $SET a "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        $SET b "$V(a)$V(a)$V(a)$V(a)$V(a)"
        $SET t "$V(b)$V(b)x"
        MEND
        M1
        end
