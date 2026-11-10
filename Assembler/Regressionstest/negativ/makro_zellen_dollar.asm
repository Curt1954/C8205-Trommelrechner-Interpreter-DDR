; makro_zellen_dollar: $-Zeile im Block: die Zellenzahl steht erst nach ihrer Auswertung fest
        start
M1:     MACRO
        dw      $CALC(zellen(a,b))
        MEND
        M1
a:      dw      1
$SET    n 2
b:      dw      0
        end
