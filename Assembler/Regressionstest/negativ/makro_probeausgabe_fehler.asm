; makro_probeausgabe_fehler: schlaegt ein Probelauf fehl, steht seine Debugausgabe (mit --probeausgabe) vor der Fehlermeldung und nicht noch einmal im .adrlog-Auszug
CHK:    MACRO 2
        $NOTE vor dem Fehler abstand=$CALC(abstand($1,$2))
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
