; makro_str_set_selbst: $SET a "$V(a)" mit nicht gesetztem a ist ein Fehler (nicht endlos)
        start
M1:     MACRO
        $SET a "$V(a)"
        MEND
        M1
        end
