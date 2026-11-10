        start
; makro_trace_schachtel: verschachtelter Aufruf, Einrueckung um zwei Leerzeichen, 'ruft' vor der Spur des Aufgerufenen,
; die Spur endet am Ende des Aufrufs, der sie eingeschaltet hat (Doku 4.24), Rueckgabecode 0
INNEN:  MACRO 1
        $SET z $1
        dw $1
        MEND
AUSSEN: MACRO 1
        $TRACE ON
        $SET a $1
        INNEN $1
        $INC a
        MEND
NACH:   MACRO
        $SET b 7
        dw 7
        MEND
        AUSSEN 4
        NACH
        end
