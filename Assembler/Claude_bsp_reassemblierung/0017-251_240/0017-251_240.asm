; 0017-251_240.asm  -  symbolisches Assemblerprogramm zu Testdatei 0017-251_240.txt
; #DOK-0017 Test R-fehl und Speichern
; #SPEI-0017 3716-3717
; #SPEI-0017 7774-7774
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                000     m3710
                equ     03710
m3710:          251     d3717
                240     d7774
                164     00017
                020     0
; Beginn Datenbereich
                equ     03716
                dw      03717211
d3717:          dw      0110011001
                end
d7774:          abs     07774

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3714 AC=00110011001 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
; 3716: 00003717211
; 3717: 00110011001
; 7774: 00110011001
;
;
;
