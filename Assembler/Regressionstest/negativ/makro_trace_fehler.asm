        start
; makro_trace_fehler: schlaegt eine Anweisung fehl, gibt es fuer sie keine Spurzeile; die Fehlermeldung steht nach den
; Spurzeilen des Aufrufs, die Zeilen dahinter werden weiter gespurt, die Spur endet mit dem Aufruf (Doku 4.24), rc 16
F1:     MACRO
        $TRACE ON
        $SET a 1
        $INC unbekannt 1
        $SET a 3
        dw 1
        MEND
NACH:   MACRO
        $SET b 7
        dw 7
        MEND
        F1
        NACH
        end
