; Abdruck numerischer Texte vom Lochband im R300 Code.
;#; LEITADRESSE 02
               start
start:         dt       \0123456789 \
;               dz       $zr
               000      eingabe
               ANWAHL   LSL2     
eingabe:       011      start ;Ab start liegen die Druckbefehle
               240      druckbefehl
               000      druckbefehl
               dz       +
druckbefehl:   dw       0
               000      eingabe
               equ      032
               WRZL
               000      eingabe
               equ      040
               dz       -
               000      eingabe
               equ      073
               dz       ,
               000      eingabe
               dz       $tab
               000      eingabe
               end

