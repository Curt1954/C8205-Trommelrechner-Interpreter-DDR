; betrag.asm  -  symbolisches Assemblerprogramm zu Testdatei betrag.test
; #DOK-0001 Test betrag: z = -|a+b| + |-b+c| + |-c+d| mit a=5 b=3 c=7 d=2, erwartet z=1
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
; Beginn Programmbefehle und Daten (unverändert aus betrag.test)
                000     haupt
a:              dw      05
b:              dw      03
c:              dw      07
d:              dw      02
                equ     012
haupt:          211     a                        ; |a+b|
                240     px
                211     b
                240     py
                025     betrag                   ; Sprung mit Rückkehrabsicht
                221     res                      ; ac := -|a+b|
                240     z
                221     b                        ; |-b+c|: x = c, y = -b
                240     py
                211     c
                240     px
                025     betrag
                211     z
                210     res                      ; z := z + |-b+c|
                240     z
                221     c                        ; |-c+d|: x = d, y = -c
                240     py
                211     d
                240     px
                025     betrag
                211     z
                210     res                      ; z := z + |-c+d|
                240     z
                020     0                        ; Halt, Ergebnis in z
betrag:         240     rueck                    ; Rücksprungwort aus AC sichern
                211     px
                210     py                       ; ac := x+y
                240     res
                050     rueck                    ; Positivsprung: x+y >= 0, also fertig
                221     res                      ; sonst ac := 0 - res
                240     res
                000     rueck

                end
z:              abs     05
px:             abs     06
py:             abs     07
res:            abs     010
rueck:          abs     011

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=0042 AC=00000000001 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0001: 00000000005
; 0002: 00000000003
; 0003: 00000000007
; 0004: 00000000002
; 0005: 00000000001
; 0006: 00000000002
; 0007: 77777777771
; 0010: 00000000005
; 0011: 00000036000
;
