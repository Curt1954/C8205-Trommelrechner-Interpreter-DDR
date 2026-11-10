; makro_hex_dw_praefix: 0xFF im Operanden von dw (ausserhalb eines Rechenausdrucks) ist ungueltig; richtig: dw $CALC(0xFF)
        start
M1:     MACRO
        dw      0xFF
        MEND
        M1
        end
