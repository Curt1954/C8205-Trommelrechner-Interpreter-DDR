; 0024-Ueberlauf_Halt.asm  -  symbolisches Assemblerprogramm zu Testdatei 0024-Ueberlauf_Halt.txt
; #DOK-0002 Test Halt wegen Ueberlauf: nach einem Ueberlauf folgt kein Ueberlaufsprung, nur FUE ist gesetzt (weder US noch BS)
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                210     d3001
                210     d3001
                020     0
; Beginn Datenbereich
                equ     03000
d3000:          dw      037777777777
d3001:          dw      01

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=0003 AC=40000000000 AR=3001 FE=0 FUE=1 BS=0 US=0 E=0 A=0 V1=0 V2=0
; 3000: 37777777777
; 3001: 00000000001
;
;
