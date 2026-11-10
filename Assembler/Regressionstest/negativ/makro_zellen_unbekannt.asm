; makro_zellen_unbekannt: unbekannter Operationscode im Block
        start
M1:     MACRO
        dw      $CALC(zellen(a,b))
        MEND
        M1
a:      dw      1
        FOO     3
b:      dw      0
        end
