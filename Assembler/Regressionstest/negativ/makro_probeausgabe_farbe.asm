; makro_probeausgabe_farbe: mit --probeausgabe und Farbe ist die Zeile des Probelaufs gruen (ESC-Zeichen nur vom Aufrufer, die Debugdatei des Probelaufs ist farblos)
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
