; makro_probe_wortgrenze: nur das ganze Wort $PROBE wird ersetzt; $PROBEX, $PROBE1 und $PROBE_ bleiben stehen (Doku 4.23)
G:      MACRO 0
        $NOTE x=$PROBEX y=$PROBE1 z=$PROBE_ w=$PROBE
        dw      0
        MEND
        start
        G
        end
