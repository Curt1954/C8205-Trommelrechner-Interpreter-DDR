; sp-026_Sprung_zyklisch.asm  -  symbolisches Assemblerprogramm zu Testdatei sp-026_Sprung_zyklisch.txt
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                026     m0010
                020     0
                equ     010
m0010:          020     0
                equ     03000
d3000:          dw      040000000005

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=0011 AC=00000002013 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
