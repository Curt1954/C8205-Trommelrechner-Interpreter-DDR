; makro_zellen_gleich: von und bis sind dieselbe Marke
        start
M1:     MACRO
        dw      $CALC(zellen(a,a))
        MEND
        M1
a:      dw      1
b:      dw      0
        end
