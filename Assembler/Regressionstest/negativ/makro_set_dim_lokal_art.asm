; makro_set_dim_lokal_art: mit ;#MAKROLOKAL=1 darf ein durch $SET angelegter lokaler Name nicht danach mit $DIM zum Feld werden
;#MAKROLOKAL=1
        start
G9:     MACRO
        $SET a 1
        $DIM a 3
        MEND
        G9
        end
