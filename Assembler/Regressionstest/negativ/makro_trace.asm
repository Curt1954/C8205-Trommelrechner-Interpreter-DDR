        start
; makro_trace: $TRACE ON gibt die Ablaufspur auf STDERR aus (Doku 4.24, Beispiel SUMME), Rueckgabecode 0
SUMME:  MACRO 1
        $TRACE ON
        $LOCAL i s
        $SET i 1
        $WHILE $V(i) <= $1
        $INC s $V(i)
        $INC i
        $ENDWHILE
        dw $V(s)                  ; Summe 1 bis $1
        MEND
        SUMME 2
        end
