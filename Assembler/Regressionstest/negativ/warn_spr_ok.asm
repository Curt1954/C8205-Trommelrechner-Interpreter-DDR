; Zulaessige Sprungziele: Befehl, db-/dbn-/dw-0-Platzhalter, dz und dt (erzeugen Ausgabebefehle)
; und ein Sprungbefehl, den ein Speicherbefehl ueberschreibt (Adresskonstante in Befehlsform).
        start 0
        000     a
        000     b
        000     c
        000     d
        000     e
        000     f
        000     g
        240     param
a:      020     0
b:      db      1
c:      dbn     1
d:      dw      0
e:      dz      $zr
f:      dt      \AB\
g:      020     0
param:  000     wert
wert:   dw      7
        end
