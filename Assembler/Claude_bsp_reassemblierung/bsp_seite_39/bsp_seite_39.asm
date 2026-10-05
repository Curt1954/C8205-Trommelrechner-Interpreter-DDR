; bsp_seite_39.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_seite_39.test
; #DOK-0001 Summieren eines Vektors
; #SPEI-0001 2020-2021
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                000     beginn
                equ     02000
adr_a:          da      a                        ; Adrese der ersten Komponente Vektor
adr_b:          da      b                        ; Adresse der letzten Komponente Vektor
beginn:         241     zelle_s                  ; s:=0
                211     adr_a
schleife:       240     zelle_i                  ; i:=a
                251     0
                210     zelle_s                  ; summe := summe + Speicher[i]
                240     zelle_s                  ; s:=summe
                211     zelle_i
                210     adr_1                    ; i:=i+1
                330     adr_b
                140     schleife
                211     zelle_s                  ; AC:=Summe
halt:           164     00001                    ; DEBUG Nr. 0001 aktivieren
                020     0                        ; halt
adr_1:          dw      01000                    ; eine Adreßeinheit
                equ     02022
a:              dw      0144
                dw      0145
                dw      0310
b:              dw      067
                end
zelle_i:        abs     02020
zelle_s:        abs     02021

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=2017 AC=00000000710 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=1
;
; 2020: 00002025000
; 2021: 00000000710
;
;
