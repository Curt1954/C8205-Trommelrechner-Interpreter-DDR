        start
; makro_dump: $DUMP gibt den Stand von Variablen und Feldern aus (Doku 4.24, Beispiel STAND)
STAND:  MACRO
        $SET zahl 12
        $DIM q 4
        $SET q(2) 9
        $SET t "abc"
        $LOCAL zahl i
        $SET zahl 5
        $SET i 3
        $DUMP
        $DUMP q(2) x
        $NOTE zahl=$V(zahl) i=$V(i) q2=$V(q(2))
        $DUMP i q(1+1) ; Kommentar hinter den Zielen
        dw $V(zahl)
        MEND
        STAND
        end
