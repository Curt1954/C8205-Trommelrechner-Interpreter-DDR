; makro_probe_zellenzahl: Z erzeugt im Probelauf zwei Zellen, im eigentlichen Lauf eine; die Adresse von b aendert sich,
; die Pruefung nach Pass 2 meldet den Adressfehler (Doku 4.23: die Zellenzahl darf nicht von $PROBE abhaengen)
AB:     MACRO 2
        dw      $CALC(abstand($1,$2))
        MEND
Z:      MACRO 0
        $IF $PROBE = 1
        dw      1
        dw      2
        $ELSE
        dw      3
        $ENDIF
        MEND
        start
a:      dw      0
        Z
b:      dw      0
        AB      a b
        end
