; makro_adr_fehlt: adr einer Marke, die es nicht gibt: Fehler mit dem Namen (Doku 4.23)
        start
M:      MACRO
        dw      $CALC(adr(gibtsnicht))
        MEND
        M
a:      dw      1
        end
