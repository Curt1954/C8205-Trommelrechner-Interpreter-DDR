; makro_zellen_db_ausdruck: db mit einem Ausdruck im Block: die Zahlenpruefung von db meldet
        start
M1:     MACRO
        dw      $CALC(zellen(a,b))
        MEND
        M1
a:      dw      1
        db      3+1
b:      dw      0
        end
