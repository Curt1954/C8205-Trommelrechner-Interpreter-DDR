; sp-025_024_Sprung.asm  -  symbolisches Assemblerprogramm zu Testdatei sp-025_024_Sprung.txt
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                025     m0010
                020     0
                equ     010
m0010:          024     m0020
                equ     020
m0020:          020     0
                equ     03000
d3000:          dw      05
                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=0021 AC=00000015000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
