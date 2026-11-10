; makro_binaer_calcb_negativ: $CALCB(-5) mit negativem Ergebnis ist binaer nicht darstellbar
        start
M1:     MACRO
        dw      $CALCB(0-5)
        MEND
        M1
        end
