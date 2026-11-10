; makro_p_nummer_v: $P($V(i)) mit einer Nummer ueber der Zahl der uebergebenen Parameter ist ein Fehler (ab c82ass 1.01-015 ist $V in $P erlaubt)
        start
M1:     MACRO 3
        $SET i 5
        dw $P($V(i))
        MEND
        M1 7 11 13
        end
