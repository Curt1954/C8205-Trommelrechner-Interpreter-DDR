; asm_0008_bedsprung_sp0.asm  -  symbolisches Assemblerprogramm zu Testdatei asm_0008_bedsprung_sp0.txt
; #DOK-0001 Test 065 (bedingter Sprung mit Rückkehrabsicht), SP nicht gesetzt: kein Sprung, AC=0, erg=0
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                000     haupt
erg:            dw      0
eins:           dw      01
                equ     04
haupt:          065     up                       ; Aufruf nur, wenn SP gesetzt
                020     0                        ; Halt
up:             240     rueck                    ; Rücksprungwort sichern
                211     eins
                240     erg                      ; erg := 1
                000     rueck

                end
rueck:          abs     03

; Tastenfolge:
; H G SP=0 R
;
; Prüfungen:
; BZ=0006 AC=00000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0001: 00000000000
; 0003: 00000000000
;
