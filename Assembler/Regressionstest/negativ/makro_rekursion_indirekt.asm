; makro_rekursion_indirekt: A ruft B, B ruft A -> Fehler mit Aufrufkette (frueher erst Abbruch bei "Zu viele Zeilen")
        start
A1:     MACRO
        B1
        MEND
B1:     MACRO
        A1
        MEND
        A1
        040 ziel
ziel:   dw 1
