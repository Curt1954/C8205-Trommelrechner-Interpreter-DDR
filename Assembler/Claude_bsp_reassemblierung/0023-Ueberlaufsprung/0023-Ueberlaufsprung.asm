; 0023-Ueberlaufsprung.asm  -  symbolisches Assemblerprogramm zu Testdatei 0023-Ueberlaufsprung.txt
; #DOK-0002 Test Ueberlaufsprung 070 bei vorhandenem Ueberlauf: Sprung nach 0010 und Ueberlauf wird geloescht
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                210     d3001
                070     m0010
                020     0
; Sprungziel
                equ     010
m0010:          020     0
; Beginn Datenbereich
                equ     03000
d3000:          dw      037777777777
d3001:          dw      01

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=0011 AC=40000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0010: 00000000020
; 3000: 37777777777
; 3001: 00000000001
;
;
