        start
; makro_trace_zweige: Spurzeilen der Zweige $IF, $ELIF, $ELSE, der Zeichenkettenfunktionen, von $LOCAL (mit Feld), $DIM,
; $EXIT und einer erzeugten Zeile mit Marke (Doku 4.24); Sollwerte von Hand hergeleitet, Rueckgabecode 0
ZWEIG:  MACRO 1
        $TRACE ON
        $LOCAL w t u s f(3)
        $SET f(1) 5
        $SET t "ab"
        $IF $1 = 1
        $SET w 10
        $ELIF $1 = 2
        $SET w 20
        $ELSE
        $SET w 30
        $ENDIF
        $UPPER u "$V(t)"
        $SUBSTR s "hallo" 2 3
marke%: dw $V(w)         ; Wort
        $EXIT
        dw 99
        MEND
FELD:   MACRO
        $TRACE ON
        $DIM g 2
        MEND
        ZWEIG 1
        ZWEIG 2
        ZWEIG 3
        FELD
        end
