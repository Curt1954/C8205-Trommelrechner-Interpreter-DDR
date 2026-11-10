; makro_probeausgabe_aus: ohne --probeausgabe bleiben $NOTE, $TRACE und $DUMP der Probelaeufe unsichtbar, nur der eigentliche Lauf zeigt sie (Doku 4.24)
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
