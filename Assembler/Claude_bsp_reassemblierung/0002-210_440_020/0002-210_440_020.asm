; 0002-210_440_020.asm  -  symbolisches Assemblerprogramm zu Testdatei 0002-210_440_020.txt
; #DOK-0002 Test Ladebefehl und Wiederholungs-Speicherbefehl
; #SPEI-0002 4000-4037
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                440     d4001
                164     00002
                020     0
; Beginn Datenbereich
                equ     03000
d3000:          dw      0100
                dw      045

                end
d4001:          abs     04001

; Tastenfolge:
; H G R
;
; Prüfungen:
;
; 4000: 00000000100
; 4001: 00000000100
; 4002: 00000000100
; 4003: 00000000100
; 4004: 00000000100
; 4005: 00000000100
; 4006: 00000000100
; 4007: 00000000100
; 4010: 00000000100
; 4011: 00000000100
; 4012: 00000000100
; 4013: 00000000100
; 4014: 00000000100
; 4015: 00000000100
; 4016: 00000000100
; 4017: 00000000100
; 4020: 00000000100
; 4021: 00000000100
; 4022: 00000000100
; 4023: 00000000100
; 4024: 00000000100
; 4025: 00000000100
; 4026: 00000000100
; 4027: 00000000100
; 4030: 00000000100
; 4031: 00000000100
; 4032: 00000000100
; 4033: 00000000100
; 4034: 00000000100
; 4035: 00000000100
; 4036: 00000000100
; 4037: 00000000100
; BZ=0004 AC=00000000100 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
;
