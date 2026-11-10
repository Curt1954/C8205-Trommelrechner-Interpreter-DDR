        start
; makro_dump_leer: ohne Variablen und Felder steht "(keine Variablen)" unter der Kopfzeile (Doku 4.24)
LEER:   MACRO
        $DUMP
        dw 1
        MEND
        LEER
        end
