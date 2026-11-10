; makro_zellen_leerraum: Leerraum hinter dem Komma in zellen(a, b): eigene Meldung (ab c82ass 1.01-013; vorher irrefuehrend "Der zweite Symbolname fehlt")
        start
M1:     MACRO
        dw      $CALC(zellen(a, b))
        MEND
        M1
a:      dw      1
b:      dw      0
        end
