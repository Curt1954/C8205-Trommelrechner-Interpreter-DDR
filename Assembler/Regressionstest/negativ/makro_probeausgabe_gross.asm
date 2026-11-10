; makro_probeausgabe_gross: --PROBEAUSGABE (Gross-/Kleinschreibung egal) wirkt wie --probeausgabe
CHK:    MACRO 2
        $TRACE ON
        $NOTE chk probe=$PROBE abstand=$CALC(abstand($1,$2))
        $SET x 5
        $DUMP
        dw      $CALC(abstand($1,$2))
        MEND
        start
a:      dw      0
        CHK     a b
b:      dw      9
        end
