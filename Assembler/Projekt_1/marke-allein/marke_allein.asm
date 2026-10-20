; Test: Marke allein auf einer Zeile (ohne Operation)
; Die Marke belegt keinen Speicher und erhaelt die Adresse der naechsten Zeile,
; die Speicher belegt. Erwartet: a1 = b1 = 0001, c1 = 0002, daten = d1 = 0003, ende = 0005
               start
               000   a1         ; Sprung nach a1 (= b1)
a1:                             ; Marke allein
b1:            011   01000      ; Befehl mit Marke
c1:            020   0
daten:         ; Marke allein mit Kommentar
d1:            dw    0123
               000   daten      ; Sprung nach daten (= d1)
ende:          end
