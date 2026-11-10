; makro_global_nach_set: mit ;#MAKROLOKAL=1 ist ein durch $SET lokal angelegter Name nicht mehr mit $GLOBAL vereinbar
;#MAKROLOKAL=1
        start
G4:     MACRO
        $SET a 1
        $GLOBAL a
        MEND
        G4
        end
