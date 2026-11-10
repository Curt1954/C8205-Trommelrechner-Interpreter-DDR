        start
; makro_trace_rest: Fehler in $TRACE (Doku 4.24), Rueckgabecode 16
T1:     MACRO
        $TRACE ON extra
        dw 1
        MEND
        T1
        end
