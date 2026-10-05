; bsp_5_7_teilwoerter.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_7_teilwoerter.txt
; #DOK-0001 Trennung des Maschinenwortes in Teilwoerter (Programmieranleitung 5.7)
; #SPEI-0001 3000-3004
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3005                    ; Sprung zum Programmanfang
                equ     03000
d3000:          dw      052526317434             ; (A;B;C) mit A=2525 B=1463 C=3434 (je 11 Bit, oktal)
                equ     03004
d3004:          dw      077760000000             ; Konstante 7776 0000 000
m3005:          211     d3000                    ; <AC>:=(A;B;C) ; Programmanfang
                240     d3001                    ; <3001>:=(A;B;C)
                644     d7721                    ; 11malige Linksverschiebung, <AC>:=(B;C;0) ; Arbeitsspur 7700-7777 (Inhalt 0)
                240     d3002                    ; <3002>:=(B;C;0)
                644     d7721                    ; 11malige Linksverschiebung, <AC>:=(C;0;0)
                240     d3003                    ; <3003>:=(C;0;0)
                211     d3004                    ; <AC>:=7776 0000 000
                250     d3001                    ; <3001>:=(A;B;C) UND 7776 0000 000 = (A;0;0)
                250     d3002                    ; <3002>:=(B;C;0) UND 7776 0000 000 = (B;0;0)
                164     00001                    ; DEBUG Nr. 0001
                020     0                        ; Halt

                end
d3001:          abs     03001
d3002:          abs     03002
d3003:          abs     03003
d7721:          abs     07721

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3020 AC=77760000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3000: 52526317434
; 3001: 52520000000
; 3002: 31460000000
; 3003: 70700000000
; 3004: 77760000000
;
