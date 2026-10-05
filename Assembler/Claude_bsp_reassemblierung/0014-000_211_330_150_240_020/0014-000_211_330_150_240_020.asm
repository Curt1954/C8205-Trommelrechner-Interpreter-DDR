; 0014-000_211_330_150_240_020.asm  -  symbolisches Assemblerprogramm zu Testdatei 0014-000_211_330_150_240_020.txt
; #DOK-0014 Test Unbedingter Sprung, Ladebefehl und Vergleicher setzen und Vergleichersprung und Speicherbefehl
; #SPEI-0014 7773-7776
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                000     m3000
                equ     03000
m3000:          211     d7773
                330     d7776
                150     m3004
                211     d7776
m3004:          330     d7774
                150     m3007
                211     d7774
m3007:          240     d7773
                164     00014
                020     0
; Beginn Datenbereich
                equ     07773
d7773:          dw      020000000100
d7774:          dw      0200
                dw      0
d7776:          dw      011111111111

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3012 AC=20000000100 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=1
;
; 7773: 20000000100
; 7774: 00000000200
; 7775: 00000000000
; 7776: 11111111111
;
;
;
