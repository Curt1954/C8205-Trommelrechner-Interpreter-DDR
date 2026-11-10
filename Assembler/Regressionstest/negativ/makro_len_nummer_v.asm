; makro_len_nummer_v: $LEN($V(i)) mit einer Nummer ueber der Zahl der uebergebenen Parameter ist ein Fehler (ab c82ass 1.01-015 ist $V in $LEN erlaubt)
        start
M1:     MACRO 3
        $SET i 5
        dw $LEN($V(i))
        MEND
        M1 7 11 13
        end
