; makro_adr_keine_konvergenz: Das Makro waehlt die lange Form (2 Woerter), wenn der Abstand hoechstens 6 ist: der Abstand wechselt 7, 6, 7, 6 ...
WEIT:   MACRO 2
        $IF $CALC(abstand($1,$2)) <= 6
        dw      021
        dw      022
        $ELSE
        dw      011
        $ENDIF
        MEND
        start
anf:    dw      0
        WEIT    anf ende
        db      4
ende:   dw      9
        end
