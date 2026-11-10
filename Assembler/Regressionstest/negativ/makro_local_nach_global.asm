; makro_local_nach_global: $LOCAL fuer einen mit $GLOBAL vereinbarten Namen ist ein Fehler (mit und ohne Schalter gleich; hier ohne)
        start
G6:     MACRO
        $GLOBAL a
        $LOCAL a
        MEND
        G6
        end
