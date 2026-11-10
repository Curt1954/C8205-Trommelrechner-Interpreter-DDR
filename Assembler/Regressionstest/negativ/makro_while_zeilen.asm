; makro_while_zeilen: eine Schleife, die mehr Zeilen erzeugt, als der Assembler zulaesst, endet mit einem Fehler
        start
W6:     MACRO
        $SET i 0
        $WHILE $V(i) < 4000
        dw 1
        dw 2
        $INC i
        $ENDWHILE
        MEND
        W6
        end
