; makro_global_klammer: $GLOBAL mit Anzahl in Klammern (wie $LOCAL name(n)) ist ein Fehler, ein Feld legt $DIM an
        start
G2:     MACRO
        $GLOBAL q(3)
        MEND
        G2
        end
