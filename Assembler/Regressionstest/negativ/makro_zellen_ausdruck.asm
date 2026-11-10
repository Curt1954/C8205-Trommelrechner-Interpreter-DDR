; makro_zellen_ausdruck: ein Ausdruck statt eines Symbolnamens ist ein Fehler
        start
M1:     MACRO
        dw      $CALC(zellen(a,b+1))
        MEND
        M1
a:      dw      1
b:      dw      0
        end
