; asm_0001_bsp_5_16.asm  -  symbolisches Assemblerprogramm zu Testdatei asm_0001_bsp_5_16.txt
; #DOK-0001 Test eines mit Assembler assemblierten Programmes
; #SPEI-0001 2027-2033
; #SPEI-0001 2100-2104
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start


                000     go
                equ     02000
go:             000     beginn
aqv:            da      qvektor                  ; Adrese der ersten Komponente Quellvektor
dqv:            dw      05000                    ; Dimension von qvektor gezählz in Adreßeinheiten
azv:            da      d2100                    ; Adresse der ersten Komponente Zielvektor
adreinheit:     dw      01000                    ; Adresseinheit
spbef:          dw      0240                     ; Speicherbefehl
                equ     02007
beginn:         241     i                        ; I:=0
schleife:       210     azv                      ; ac:=(azv+i)
                210     spbef                    ; ac:=(azv+i)240
                240     genbef                   ; Arbeitszelle genbef:= (qzv+i) 240
                211     i                        ; ac:=<i>
                210     aqv                      ; ac:=qvektor+i
                251     0                        ; ac:=<qvektor+i>
                equ     02017
                211     i                        ; ac:=<i>
                210     adreinheit               ; ac:=i+1
                240     i                        ; i:=ac
                330     dqv                      ; vergleicher 3, falls i == <dqv>
                170     halt                     ; sprung bei gleich
                000     schleife
halt:           164     00001                    ; DEBUG Nr. 0023 aktivieren
                020     0                        ; halt
qvektor:        dw      01
                dw      02
                dw      03
                dw      04
                dw      05

                end
i:              abs     02006
genbef:         abs     02016
d2100:          abs     02100

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=2027 AC=00000005000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=1 V2=1
;
; 2027: 00000000001
; 2030: 00000000002
; 2031: 00000000003
; 2032: 00000000004
; 2033: 00000000005
; 2100: 00000000001
; 2101: 00000000002
; 2102: 00000000003
; 2103: 00000000004
; 2104: 00000000005
;
;
