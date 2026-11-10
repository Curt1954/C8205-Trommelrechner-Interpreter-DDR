; makro_while_label: ein lokales Label aus dem Rumpf von $WHILE gilt nur im Rumpf; ein Sprung dahinter findet es nicht
        start
W4:     MACRO
        $SET i 0
        $WHILE $V(i) < 2
inn%:   dw 1
        $INC i
        $ENDWHILE
        000 inn%
        MEND
        W4
        end
