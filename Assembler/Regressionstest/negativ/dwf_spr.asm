        start 0
        000     daten        ; Sprung auf ein dwf-Wort mit Wert ungleich 0: Warnung SPR
        000     platz        ; Sprung auf dwf 0.0: Wort 0, Platzhalter, keine Warnung
daten:  dwf     0.5
platz:  dwf     0.0
        end
