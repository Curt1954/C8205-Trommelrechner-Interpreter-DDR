; sp-028_bedingter_Sprung_SP0.asm  -  symbolisches Assemblerprogramm zu Testdatei sp-028_bedingter_Sprung_SP0.txt
; #DOK-0001 Bedingter Sprung mit Rueckkehrabsicht bei SP=0 (nicht genommen): keine Verschiebung, Loeschung nach L
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                065     m0010
                211     d3000
                067     m0010
                211     d3000
                064     m0010
                066     m0010
                020     0
                equ     03000
d3000:          dw      040000000005

                end
m0010:          abs     010

; Tastenfolge:
; SP=0 H G R
;
; Prüfungen:
; BZ=0010 AC=40000000005 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
