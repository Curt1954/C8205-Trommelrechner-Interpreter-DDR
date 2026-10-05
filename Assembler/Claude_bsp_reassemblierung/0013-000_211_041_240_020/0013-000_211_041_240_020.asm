; 0013-000_211_041_240_020.asm  -  symbolisches Assemblerprogramm zu Testdatei 0013-000_211_041_240_020.txt
; #DOK-0014 Test Unbedingter Sprung, Ladebefehl und Addition Positiv-Sprung mit Löschen und Speicherbefehl
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                000     m5000
                equ     05000
m5000:          211     d5006
                240     d5007
m5002:          041     m5002
                164     00014
                020     0
; Beginn Datenbereich
                equ     05006
d5006:          dw      0100
d5007:          dw      0200

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=5005 AC=00000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
;
