; Test --pass0: $NOTE im Quelltext und im Makro, $WARN; nur Pass 0, Ausgabe auf STDOUT, ohne Kopfmeldungen
        $SET n 5
        macro hinweis
        $NOTE im Makro Wert $V(n)
        mend
        start
        $NOTE Stand n = $V(n)
        hinweis
        $WARN Warnung n = $V(n)
        dw 1
        end
