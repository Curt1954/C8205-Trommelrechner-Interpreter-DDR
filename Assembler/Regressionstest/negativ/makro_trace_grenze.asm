        start
; makro_trace_grenze: je Lauf hoechstens 10000 Spurzeilen, gezaehlt ueber alle Aufrufe; danach einmal ein Hinweis,
; der Lauf geht ohne Fehler weiter (Doku 4.24). Vier Aufrufe zu je 3000 gespurten Zeilen, Rueckgabecode 0
Z:      MACRO
        $TRACE ON
        $SET n 0
        $REPT 2999
        $INC n
        $ENDREPT
        MEND
        Z
        Z
        Z
        Z
        dw 5
        end
