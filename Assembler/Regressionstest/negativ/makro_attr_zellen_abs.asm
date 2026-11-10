; makro_attr_zellen_abs: zellen auf einer abs-Zeile: ein Wert belegt keine Zelle
        start
M1:     MACRO
        dw      $CALC(zellen(x))
        MEND
        M1
        end
x:      abs     3
