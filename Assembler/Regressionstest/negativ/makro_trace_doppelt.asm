        start
; makro_trace_doppelt: $TRACE ON bei eingeschalteter und $TRACE OFF bei ausgeschalteter Spur bleiben ohne Wirkung
; (Doku 4.24); der innere Aufruf bleibt eingerueckt, die Spur des aeusseren geht nach dem Aufruf weiter, Rueckgabecode 0
INNEN:  MACRO
        $TRACE ON
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
LEER:   MACRO
        $TRACE OFF
        $SET b 3
        dw 3
        MEND
        AUSSEN
        LEER
        end
