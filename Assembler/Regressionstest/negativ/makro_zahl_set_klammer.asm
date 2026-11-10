; makro_zahl_set_klammer: die Klammer fehlt erst nach dem Aufloesen von $V (c = "(1"): Fehler des $SET (Z-03); fehlt sie schon im Quelltext, meldet wie bisher die Zeilenpruefung
        start
M1:     MACRO
        $SET c "(1"
        $SET t "$CALC($V(c)+2)"
        MEND
        M1
        end
