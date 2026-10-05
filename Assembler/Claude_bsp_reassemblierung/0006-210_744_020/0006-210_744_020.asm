; 0006-210_744_020.asm  -  symbolisches Assemblerprogramm zu Testdatei 0006-210_744_020.txt
; #DOK-0006 Test Ladebefehl und X-Gruppen-Speicherbefehl und Linksverschiebung
; #DOK-0006 So ein Befehl bringt eigentlich nichts, besser alle 32 Zellen durchlaufen, und dann logisch begrenzen
; #DOK-0006 da hat man für jeden logische Speichernummer einen korrekt verschobenen Wert.
; #SPEI-0006 4000-4037
; #SPUR-0006 4000
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                744     d4001
                equ     03
                020     0
; Folgebefehl nach dem X-Abbruch: liegt im zeitlich faelligen Sektor der Spur 0000 (nicht in b+1), danach b+2 = 0003
                equ     021
                164     00006                    ; 164 Leerbefehl (Diagnose)
; Beginn Datenbereich
                equ     03000
d3000:          dw      01000000
                dw      045

                end
d4001:          abs     04001

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=0004 AC=00000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 4000: 00000000000
; 4015: 00000000000
; 4032: 00000000000
; 4007: 00000000000
; 4024: 00000000000
; 4001: 00001000000
; 4016: 00002000000
; 4033: 00004000000
; 4010: 00010000000
; 4025: 00020000000
; 4002: 00040000000
; 4017: 00100000000
; 4034: 00200000000
; 4011: 00400000000
; 4026: 01000000000
; 4003: 02000000000
; 4020: 04000000000
; 4035: 10000000000
; 4012: 20000000000
; 4027: 40000000000
; 4004: 00000000000
; 4021: 00000000000
; 4036: 00000000000
; 4013: 00000000000
; 4030: 00000000000
; 4005: 00000000000
; 4022: 00000000000
; 4037: 00000000000
; 4014: 00000000000
; 4031: 00000000000
; 4006: 00000000000
; 4023: 00000000000
;
;
