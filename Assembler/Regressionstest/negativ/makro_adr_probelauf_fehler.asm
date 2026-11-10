; makro_adr_probelauf_fehler: Probelauf 1 rechnet mit dem Abstand 0: $ERROR beendet den Probelauf, der Fehler wird wiedergegeben
CHK:    MACRO 2
        $IF $CALC(abstand($1,$2)) = 0
        $ERROR Abstand ist null
        $ENDIF
        dw      $CALC(abstand($1,$2))
        MEND
        start
a:      dw      0
        CHK     a b
b:      dw      9
        end
