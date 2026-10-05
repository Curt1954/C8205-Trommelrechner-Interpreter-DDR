; 0012-000_211_050_001_240_020.asm  -  symbolisches Assemblerprogramm zu Testdatei 0012-000_211_050_001_240_020.txt
; #DOK-0012 Test Unbedingter Sprung, Ladebefehl und Addition Positiv-Sprung und Speicherbefehl
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                000     m5000
                equ     05000
m5000:          211     d5006
                050     m5003
                001     m5003
m5003:          240     d5007
                164     00012
                020     0
; Beginn Datenbereich
d5006:          dw      0100
d5007:          dw      0200

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=5006 AC=00000000100 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
