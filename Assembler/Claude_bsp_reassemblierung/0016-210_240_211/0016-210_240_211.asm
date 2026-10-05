; 0016-210_240_211.asm  -  symbolisches Assemblerprogramm zu Testdatei 0016-210_240_211.txt
; #DOK-0016 Test Ladebefehl und Addition
; #SPEI-0016 7774-7774
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                000     m3710
                equ     03710
m3710:          210     d3716
                240     d3712
d3712:          dw      01010101010
                240     d7774
                164     00016
                020     0
; Beginn Datenbereich
d3716:          dw      03717211
                dw      0110011001
                end
d7774:          abs     07774

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3716 AC=00110011001 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 7774: 00110011001
;
;
