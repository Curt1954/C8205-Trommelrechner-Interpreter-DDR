; 0004-210_544_020.asm  -  symbolisches Assemblerprogramm zu Testdatei 0004-210_544_020.txt
; #DOK-0004 Test Ladebefehl und X-Wiederholung-Speicherbefehl und Linksverschiebung
; #DOK-0004 So ein Befehl bringt eigentlich nichts, besser alle 32 Zellen durchlaufen, und dann logisch begrenzen
; #DOK-0004 da hat man für jeden logische Speichernummer einen korrekt verschobenen Wert.
; #SPEI-0004 4000-4037
; #SPUR-0004 4000
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                211     d3000
                544     d4001
                equ     03
                020     0
; Folgebefehl nach dem X-Abbruch: liegt im zeitlich faelligen Sektor der Spur 0000 (nicht in b+1), danach b+2 = 0003
                equ     015
                164     00004                    ; 164 Leerbefehl (Diagnose)
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
; BZ=0004 AC=00000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
; 4000: 00000000000
; 4001: 00000000100
; 4002: 00000004000
; 4003: 00000200000
; 4004: 00010000000
; 4005: 00400000000
; 4006: 20000000000
; 4007: 00000000000
; 4010: 00000001000
; 4011: 00000040000
; 4012: 00002000000
; 4013: 00100000000
; 4014: 04000000000
; 4015: 00000000000
; 4016: 00000000200
; 4017: 00000010000
; 4020: 00000400000
; 4021: 00020000000
; 4022: 01000000000
; 4023: 40000000000
; 4024: 00000000000
; 4025: 00000002000
; 4026: 00000100000
; 4027: 00004000000
; 4030: 00200000000
; 4031: 10000000000
; 4032: 00000000000
; 4033: 00000000400
; 4034: 00000020000
; 4035: 00001000000
; 4036: 00040000000
; 4037: 02000000000
;
;
;
