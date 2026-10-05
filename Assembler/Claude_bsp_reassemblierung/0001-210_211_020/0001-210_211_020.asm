; 0001-210_211_020.asm  -  symbolisches Assemblerprogramm zu Testdatei 0001-210_211_020.txt
; #DOK-0001 Test Ladebefehl und Addition
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                210     d3001
                164     00001
                020     0
; Beginn Datenbereich
                equ     03000
d3000:          dw      0100
d3001:          dw      045

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=0004 AC=00000000145 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0000: 00003000211
; 3000: 00000000100
; 3001: 00000000045
;
;
