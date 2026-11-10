        start
; makro_dump_name: Fehler in $DUMP (Doku 4.24), Rueckgabecode 16, keine Ausgabe des Standes
D1:     MACRO
        $DIM q 4
        $SET e 1
        $DUMP q 1abc
        dw 1
        MEND
        D1
        end
