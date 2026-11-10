        start
; makro_note: $NOTE gibt einen Text auf STDERR aus (Doku 4.24); Rueckgabecode 0, keine Warnung
SUMME:  MACRO 1
        $LOCAL i s
        $DIM q 4
        $SET q(3) 9
        $SET i 1
        $WHILE $V(i) <= $1
        $INC s $V(i)
        $NOTE i=$V(i) s=$V(s) q3=$V(q(3))
        $INC i
        $ENDWHILE
        dw $V(s)
        MEND
RAND:   MACRO 1
        $NOTE ; Semikolon gehoert zum Text, $1 ist ersetzt
        $NOTE
        $IF $1 = 0
        $NOTE nur bei Null
        $ENDIF
        $IF $1 = 1
        $NOTE nur bei Eins
        $ENDIF
        $REPT 2
        $NOTE rept $Z1 calc $CALC(7*6)
        $ENDREPT
        $EXIT
        $NOTE nach EXIT
        dw 99
        MEND
AUSSEN: MACRO
        RAND 1
        $NOTE aussen fertig
        MEND
LANG:   MACRO 1
        $NOTE $1$1
        dw 1
        MEND
        SUMME 3
        AUSSEN
        $NOTE ausserhalb des Makros
        LANG "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        end
