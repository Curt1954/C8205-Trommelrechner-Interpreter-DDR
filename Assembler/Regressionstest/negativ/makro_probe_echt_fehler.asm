; makro_probe_echt_fehler: die Pruefung mit $PROBE = 0 gilt im eigentlichen Lauf; abstand(b,a) ist -2, $ERROR kommt aus dem
; eigentlichen Lauf und nicht aus einem Probelauf (Doku 4.23)
CHK:    MACRO 2
        $IF $PROBE = 0
        $IF $CALC(abstand($1,$2)) < 1
        $ERROR Abstand kleiner 1
        $ENDIF
        $ENDIF
        dw      $CALC(abstand($1,$2))
        MEND
        start
a:      dw      0
        CHK     b a
b:      dw      9
        end
