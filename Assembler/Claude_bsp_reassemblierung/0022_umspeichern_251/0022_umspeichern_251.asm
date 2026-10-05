; 0022_umspeichern_251.asm  -  symbolisches Assemblerprogramm zu Testdatei 0022_umspeichern_251.txt
; #DOK-0022 Test Umspeichern mit R-Befehl
; #SPEI-0022 4000-4020
; #SPEI-0022 6000-6020
; #SPEI-1022 3706-3723
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
m0000:          000     m3700                    ; Sprung nach 3700
                equ     03700
m3700:          241     m3723                    ; i:=0
m3701:          210     m3720                    ; Aufbau Transportbefehl nach 60xx
                240     m3706                    ; Aufbau Transportbefehl nach 60xx
                220     m3721                    ; Aufbau Löschbefehl 40xx
                240     m3707                    ; Aufbau Löschbefehl 40xx
                dw      0251                     ; R-Befehl <AC>==4000+i umgestellt auf "40xx in den AC lesen"
m3706:          000     m0000                    ; beliebig
m3707:          000     m0000                    ; beliebig
                164     01022                    ; Leerbefehl und Debug

                211     m3723                    ; <Ac>==0000 i 000
                210     m3722                    ; <Ac>==0000 i+1 000
                240     m3723                    ; i := i + 1 speichern
                330     d6000                    ; Rest-Feld Größe
                140     m3701                    ; Sprung bei i < Restfelsgröße

                164     00022                    ; Leerbefehl und Debug
                020     0                        ; Stop

m3720:          240     d6000                    ; Konstante für befehlsaufbau
m3721:          777     d1777                    ; Konstante für befehlsaufbau
m3722:          000     m0001                    ; 1 Adreßeinheit
m3723:          000     m0000                    ; beliebig

; Beginn Datenbereich
                equ     04000
                dw      017000
                dw      01
                dw      02
                dw      04
                dw      010
                dw      011
                dw      012
                dw      014
                dw      020
                dw      021
                dw      022
                dw      024
                dw      030
                dw      031
                dw      032
                dw      034
                dw      040
                equ     06000
d6000:          dw      020000                   ; Restfeldgröße in Adreßeinheiten

                end
m0001:          abs     01
d1777:          abs     01777

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3720 AC=00000020000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=1
;
; 4000: 00000000000
; 4001: 00000000000
; 4002: 00000000000
; 4003: 00000000000
; 4004: 00000000000
; 4005: 00000000000
; 4006: 00000000000
; 4007: 00000000000
; 4010: 00000000000
; 4011: 00000000000
; 4012: 00000000000
; 4013: 00000000000
; 4014: 00000000000
; 4015: 00000000000
; 4016: 00000000000
; 4017: 00000000000
; 4020: 00000000040
; 6000: 00000017000
; 6001: 00000000001
; 6002: 00000000002
; 6003: 00000000004
; 6004: 00000000010
; 6005: 00000000011
; 6006: 00000000012
; 6007: 00000000014
; 6010: 00000000020
; 6011: 00000000021
; 6012: 00000000022
; 6013: 00000000024
; 6014: 00000000030
; 6015: 00000000031
; 6016: 00000000032
; 6017: 00000000034
; 6020: 00000000000
;
;
