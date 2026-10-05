; sp-027_bedingter_Sprung.asm  -  symbolisches Assemblerprogramm zu Testdatei sp-027_bedingter_Sprung.txt
; #DOK-0001 Bedingter Sprung mit Rueckkehrabsicht, SP=1, ungerader BZ, R=2 und R=3
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                065     m0010
                020     0
                equ     010
m0010:          064     m0020
                equ     020
m0020:          066     m0030
                equ     030
m0030:          020     0
                equ     03000
d3000:          dw      05

                end

; Tastenfolge:
; SP=1 H G R
;
; Prüfungen:
; BZ=0031 AC=00000033000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
;
