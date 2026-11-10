; makro_dim_lokal_anzahl: mit ;#MAKROLOKAL=1 ist ein zweites $DIM desselben lokalen Namens mit anderer Anzahl ein Fehler
;#MAKROLOKAL=1
        start
G8:     MACRO
        $DIM a 3
        $DIM a 4
        MEND
        G8
        end
