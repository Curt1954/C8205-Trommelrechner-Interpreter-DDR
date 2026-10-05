; sp-029_Sprung_B1.asm  -  symbolisches Assemblerprogramm zu Testdatei sp-029_Sprung_B1.txt
; #DOK-0001 Sprung mit Rueckkehrabsicht 2. Art (B=1: 125, 124, 126), ungerader BZ, R=2 und R=3
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                125     m0010
                020     0
                equ     010
m0010:          124     m0020
                equ     020
m0020:          126     m0030
                equ     030
m0030:          211     d3000
                126     m0040
                equ     040
m0040:          020     0
                equ     03000
d3000:          dw      040000000005

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=0041 AC=00000032013 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
;
