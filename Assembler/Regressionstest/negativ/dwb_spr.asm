        start 0
        000     daten        ; Sprung auf ein dwb-Wort mit Wert ungleich 0: Warnung SPR
        000     platz        ; Sprung auf dwb 0: Platzhalter, keine Warnung
daten:  dwb     101
platz:  dwb     0
        end
