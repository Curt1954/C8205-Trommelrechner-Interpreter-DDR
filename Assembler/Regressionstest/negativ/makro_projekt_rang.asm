; Rangfolge der Makros: Quelltext, ;#MACRODATEI1 bis 9, c82ass.makros
;#MACRODATEI1=makro_projekt_rang_1.macro
;#MACRODATEI2=makro_projekt_rang_2.macro
VIER:   MACRO
        dw 06
        MEND
        start
a:      ZWEI                ; aus Datei 1: dw 02
b:      DREI                ; aus Datei 2: dw 04
c:      KB                  ; Datei 1 ersetzt c82ass.makros: dw 077
d:      VIER                ; Quelltext ersetzt Datei 2: dw 06
        020 0
        end
