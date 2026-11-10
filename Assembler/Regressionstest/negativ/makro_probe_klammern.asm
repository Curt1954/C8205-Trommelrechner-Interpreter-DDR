; makro_probe_klammern: $PROBE steht ohne Klammern und ohne Argument; $PROBE() ist ein Fehler (Doku 4.23)
K:      MACRO 0
        dw      $PROBE()
        MEND
        start
        K
        end
