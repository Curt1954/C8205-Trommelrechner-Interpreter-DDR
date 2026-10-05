; bsp_5_19_2_teilwoerter.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_19_2_teilwoerter.txt
; #DOK-0001 Zeitoptimale Programmierung, Trennung des Maschinenwortes in Teilwoerter (Programmieranleitung 5.19.2, Aufgabe wie 5.7)
; #DOK-0001 (A;B;C) mit A=2525 B=1463 C=3434 (je 11 Bit, oktal) in 3000; zwei 22malige zyklische Linksverschiebungen (W-Befehl 7702 646,
;   Sektor 02 bis 23); erwartet <3001>=(A;0;0), <3002>=(B;0;0), <3003>=(C;0;0)
; #SPEI-0001 3000-3004
; #SPEI-0001 3047-3051
; #SPEI-0001 7702-7702
; #SPEI-0001 7723-7723
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3005                    ; Sprung zum Programmanfang der Aufgabe
                equ     03000
d3000:          dw      052526317434             ; (A;B;C) mit A=2525 B=1463 C=3434 (je 11 Bit, oktal)
                equ     03004
d3004:          dw      077760000000             ; Konstante 7776 0000 000
m3005:          000     m3006                    ; 3006 000 ; Programmanfang
m3006:          211     d3000                    ; 3000 211 ; <AC>:=(A;B;C)
                240     d3001                    ; 3001 240 ; <3001>:=(A;B;C)
                646     d7702                    ; 7702 646 ; 22malige zyklische Linksverschiebung, <AC>:=(C;A;B)
                240     d3003                    ; 3003 240 ; <3003>:=(C;A;B)
                000     m3032                    ; 3032 000 ; Sprung
                equ     03032
m3032:          646     d7702                    ; 7702 646 ; 22malige zyklische Linksverschiebung, <AC>:=(B;C;A)
                240     d3002                    ; 3002 240 ; <3002>:=(B;C;A)
                000     m3035                    ; 3035 000 ; Sprung
m3035:          211     d3004                    ; 3004 211 ; <AC>:=7776 0000 000
                000     m3047                    ; 3047 000 ; Sprung
                equ     03047
m3047:          250     d3001                    ; 3001 250 ; <3001>:=(A;B;C) UND 7776 0000 000 = (A;0;0)
                250     d3002                    ; 3002 250 ; <3002>:=(B;C;A) UND 7776 0000 000 = (B;0;0)
                250     d3003                    ; 3003 250 ; <3003>:=(C;A;B) UND 7776 0000 000 = (C;0;0)
; Programmende (im Buch ohne Inhalt), hier mit Debug und Stopp
                164     00001                    ; DEBUG Nr. 0001
                020     0                        ; unbedingter Stopp

                end
d3001:          abs     03001
d3002:          abs     03002
d3003:          abs     03003
d7702:          abs     07702

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3054 AC=77760000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3000: 52526317434
; 3001: 52520000000
; 3002: 31460000000
; 3003: 70700000000
; 3004: 77760000000
; 7702: 70712525463
; 7723: 54637071252
;
