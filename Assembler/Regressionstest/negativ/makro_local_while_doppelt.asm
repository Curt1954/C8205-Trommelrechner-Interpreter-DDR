; makro_local_while_doppelt: ein Name zweimal in einer $LOCAL-Zeile im Rumpf von $WHILE bleibt ein Fehler
        start
L10:    MACRO
        $SET k 0
        $WHILE $V(k) < 2
        $LOCAL a a
        $INC k
        $ENDWHILE
        MEND
        L10
        end
