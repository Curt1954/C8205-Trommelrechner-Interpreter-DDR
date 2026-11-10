        start
; makro_dump_feld: Felder mit mehr als 16 Elementen erscheinen in Zeilen zu je 16 Elementen (Doku 4.24)
FELD:   MACRO
        $DIM q 40
        $SET q(3) 7
        $SET q(39) 5
        $DIM r 33
        $SET r(32) 4
        $DUMP
        dw 1
        MEND
        FELD
        end
