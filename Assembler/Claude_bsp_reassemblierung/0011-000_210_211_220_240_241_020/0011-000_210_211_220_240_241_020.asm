; 0011-000_210_211_220_240_241_020.asm  -  symbolisches Assemblerprogramm zu Testdatei 0011-000_210_211_220_240_241_020.txt
; #DOK-0011 Test Unbedingter Sprung, Ladebefehl und Addition Subtraktion und Speicherbefehl
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                000     m3000
                equ     03000
m3000:          211     d3014
                220     d3015
                220     d3015
                210     d3016
                220     d3017
                240     d3020
                241     d3021
                164     00011
                020     0
; Beginn Datenbereich
                equ     03014
d3014:          dw      0100
d3015:          dw      0200
d3016:          dw      0300
d3017:          dw      010
d3020:          dw      020
d3021:          dw      030

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3011 AC=00000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
;
