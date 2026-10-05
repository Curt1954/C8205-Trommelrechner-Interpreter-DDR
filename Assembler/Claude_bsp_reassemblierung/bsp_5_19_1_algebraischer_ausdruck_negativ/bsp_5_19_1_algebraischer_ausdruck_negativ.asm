; bsp_5_19_1_algebraischer_ausdruck_negativ.asm  -  symbolisches Assemblerprogramm zu Testdatei
;   bsp_5_19_1_algebraischer_ausdruck_negativ.txt
; #DOK-0001 Zeitoptimale Programmierung, algebraischer Ausdruck (Programmieranleitung 5.19.1, Aufgabe wie 5.5): a=3, b=7, c=5, negatives
;   Ergebnis x=-25 (Zweierkomplement)
; #DOK-0001 Programm 5.19.1 wie im Buch (Zellen 3003, 3006-3011, 3031-3032); Operanden a=<3000>, b=<3001>, c=<3002>; Befehlsfolge: 2a, 2a-b,
;   2(2a-b-c), 2(2(2a-b-c)+a), -b
; #DOK-0001 erwartet <AC> = 77777777747 (oktal), x = 10a - 5b - 4c
; #SPEI-0001 3000-3002
; #SPEI-0001 3031-3034
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3003                    ; Sprung zum Programmanfang der Aufgabe
; Operanden
                equ     03000
d3000:          dw      03                       ; a
d3001:          dw      07                       ; b
d3002:          dw      05                       ; c
; Programm 5.19.1 (zeitoptimal)
m3003:          000     m3006                    ; 3006 000 ; Sprung zum Programmstart
                equ     03006
m3006:          215     d3000                    ; 3000 215 ; <AC>:=2a
                220     d3001                    ; 3001 220 ; <AC>:=2a-b
                224     d3002                    ; 3002 224 ; <AC>:=2(2a-b-c)
                000     m3031                    ; 3031 000 ; Sprung
                equ     03031
m3031:          214     d3000                    ; 3000 214 ; <AC>:=2(2(2a-b-c)+a)
                220     d3001                    ; 3001 220 ; <AC>:=x
; Programmende (im Buch ohne Inhalt), hier mit Debug und Stopp
                164     00001                    ; DEBUG Nr. 0001
                020     0                        ; unbedingter Stopp

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3035 AC=77777777747 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3000: 00000000003
; 3001: 00000000007
; 3002: 00000000005
; 3031: 00003000214
; 3032: 00003001220
;
