; makro_adr_zwei_namen: adr nimmt genau einen Namen
        start
M:      MACRO
        dw      $CALC(adr(a,b))
        MEND
        M
a:      dw      1
b:      dw      2
        end
