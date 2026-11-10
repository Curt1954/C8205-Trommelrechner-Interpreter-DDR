; makro_adr_pass0: mit --pass0 liefern adr und abstand den Wert 0 ohne Meldung, ohne Probelaeufe (auch fuer eine Marke, die es nicht gibt)
M:      MACRO 2
        dw      $CALC(abstand($1,$2)+adr($1))
        MEND
        start
a:      dw      0
        M       a gibtsnicht
        end
