        start
; makro_trace_aus: $TRACE OFF in einem aufgerufenen Makro schaltet die Spur insgesamt aus, auch fuer den Rest des
; aufrufenden Makros (Doku 4.24); die Zeile des Aufrufs steht noch in der Spur, Rueckgabecode 0
INNEN:  MACRO
        $TRACE OFF
        $SET z 1
        dw 1
        MEND
AUSSEN: MACRO
        $TRACE ON
        $SET a 1
        INNEN
        $SET a 2
        dw 2
        MEND
        AUSSEN
        end
