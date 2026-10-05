; bsp_seite_42_025_stanzer.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_seite_42_025_stanzer.test
; #DOK-0001  Unterprogrammtechnik,  Sprung mit Rückkehrabsicht, 025
; #SPEI-0001 2012-2027
; #SPEI-0002 2012-2016
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     beginn
                equ     02000
beginn:         030     04600                    ; 4600 oder K1 oder LSL1 oder LSS1
                211     z_a
                240     up+1
                025     up
                211     z_b
                240     up+1
                025     up
                211     z_c
                240     up+1
                025     up
halt:           164     00001                    ; DEBUG Nr. 0001 aktivieren
                020     0                        ; halt
z_a:            dto     A
z_b:            dto     B
z_c:            dto     C
up:             240     zum_rs
                equ     02022
nix:            dw      0777

                end
zum_rs:         abs     02021

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=2014 AC=00002012000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
; 2012: 00000001164
; 2013: 00000000020
; 2014: 00000610030
; 2015: 00000620030
; 2016: 00000430030
; 2017: 00002021240
; 2020: 00000430030
; 2021: 00002012000
; 2022: 00000000777
;
; --pruefe-stanzer1 bsp_seite_42_025_stanzer-stanzer-ausgabe.txt
;
;
