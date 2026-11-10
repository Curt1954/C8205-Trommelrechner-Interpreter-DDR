        start 0
        000     daten        ; Sprung auf ein dwg-Wort mit Wert ungleich 0: Warnung SPR
        000     platz        ; Sprung auf dwg -0: Wort 0, Platzhalter, keine Warnung
daten:  dwg     16
platz:  dwg     -0
        end
