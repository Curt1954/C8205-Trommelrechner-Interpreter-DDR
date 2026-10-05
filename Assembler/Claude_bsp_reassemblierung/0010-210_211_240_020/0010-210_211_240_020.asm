; 0010-210_211_240_020.asm  -  symbolisches Assemblerprogramm zu Testdatei 0010-210_211_240_020.txt
; #DOK-0010 Test Unbedingter Sprung, Ladebefehl und Addition und Speicherbefehl
; #SPEI-0010 3777-4001
; #SPEI-0010 5001-5002
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                000     m3000
                equ     03000
m3000:          211     d3777
                240     d5000
                211     d4000
                240     d5001
                211     d4001
                240     d5002
                164     00010
                020     0
; Beginn Datenbereich
                equ     03777
d3777:          dw      0100
d4000:          dw      0200
d4001:          dw      0300
                equ     05000
d5000:          dw      010
d5001:          dw      020
d5002:          dw      030

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
;
; BZ=3010 AC=00000000300 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
; 3777: 00000000100
; 4000: 00000000200
; 4001: 00000000300
; 5000: 00000000100
; 5001: 00000000200
; 5002: 00000000300
;
;
