; quelltext_while_label: im normalen Quelltext (ohne Makro) ist ein Label name% im Rumpf von $WHILE ein Fehler (lokale Labels gibt es nur im Makro)
        start
        $SET i 0
        $WHILE $V(i) < 2
schleife%: dw 1
        $INC i
        $ENDWHILE
        end
