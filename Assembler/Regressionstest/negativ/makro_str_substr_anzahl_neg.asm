; makro_str_substr_anzahl_neg: $SUBSTR mit Anzahl kleiner als 0 ist ein Fehler (Anzahl 0 ist erlaubt, ab c82ass 1.01-015)
        start
M1:     MACRO
        $SUBSTR z "abc" 1 -1
        MEND
        M1
        end
