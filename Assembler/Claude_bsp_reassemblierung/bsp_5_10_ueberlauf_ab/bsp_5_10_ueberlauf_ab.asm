; bsp_5_10_ueberlauf_ab.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_10_ueberlauf_ab.txt
; #DOK-0001 Addition mit Zahlenbereichsueberschreitung (Programmieranleitung 5.10), a=37777777777 (groesste positive Zahl) b=1, Ueberlauf
;   bei a+b
; #SPEI-0001 3000-3003
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

m0000:          000     m3005                    ; Sprung zum Programmanfang
                equ     03000
d3000:          dw      037777777777             ; a
d3001:          dw      01                       ; b
d3002:          dw      03                       ; c
m3003:          000     m0000                    ; Ergebniszelle (a+b+c bzw. 4000 0000 000 bei Ueberlauf)
d3004:          dw      040000000000             ; Konstante 4000 0000 000
m3005:          211     d3000                    ; <AC>:=a
                210     d3001                    ; <AC>:=a+b
                070     m3013                    ; Ueberlaufsprung
                210     d3002                    ; <AC>:=a+b+c
                070     m3013                    ; Ueberlaufsprung
                000     m3014                    ; Sprung zum Speichern
m3013:          211     d3004                    ; <AC>:=4000 0000 000
m3014:          240     m3003                    ; <3003>:=<AC>
                164     00001                    ; DEBUG Nr. 0001
                020     0                        ; unbedingter Stop

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3017 AC=40000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3000: 37777777777
; 3001: 00000000001
; 3002: 00000000003
; 3003: 40000000000
;
