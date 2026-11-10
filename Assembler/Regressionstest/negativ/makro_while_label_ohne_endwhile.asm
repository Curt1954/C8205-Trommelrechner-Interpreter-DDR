; makro_while_label_ohne_endwhile: fehlendes $ENDWHILE bei einem Label im Rumpf: nur diese eine Meldung, kein Folgefehler durch ein stehengebliebenes %
        start
W5:     MACRO
        $SET i 0
        $WHILE $V(i) < 2
schl%:  dw 1
        $INC i
        MEND
        W5
        end
