        start
; $V(...) im Text von $WARN wird ersetzt (ab c82ass 1.01-005, Doku 4.5 und 4.24); ohne $V( bleibt der Text wie bisher
W1:     MACRO 1
        $SET n $1
        $WARN n=$V(n) und $CALC($V(n)*2)
        $WARN ohne Variable $1 und $CALC(2+3)
        dw $V(n)
        MEND
        W1 7
        end
