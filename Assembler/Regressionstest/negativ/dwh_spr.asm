        start 0
        000     daten        ; Sprung auf ein dwh-Wort mit Wert ungleich 0: Warnung SPR
        000     platz        ; Sprung auf dwh 0: Platzhalter, keine Warnung
daten:  dwh     1F
platz:  dwh     0
        end
