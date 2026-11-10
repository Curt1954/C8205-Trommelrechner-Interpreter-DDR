; makro_attr_zellen_db_operand: zellen auf db mit einem Operanden, der keine Zahl ist (Regeln von 3.3.1)
        start
M1:     MACRO
        dw      $CALC(zellen(tab))
        MEND
        M1
        end
tab:    db      3+1
