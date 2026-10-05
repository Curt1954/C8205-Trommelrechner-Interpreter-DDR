; bsp_5_16_umspeichern_vektor.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_16_umspeichern_vektor.txt
; #DOK-0001 Umspeichern eines Vektors (Programmieranleitung 5.16), Programm wie im Buch ab Zelle 3000, Parameter a°=4034, n°=6 Komponenten,
;   b°=4106
; #DOK-0001 Quellvektor 4034-4041 (Spurgrenze 4037/4040 wird überschritten), Zielvektor 4106-4113; erwartet: alle sechs Komponenten ab 4106
;   kopiert, <3006>=n°, <3016>=(b+5) 240
; #SPEI-0001 3000-3026
; #SPEI-0001 4034-4041
; #SPEI-0001 4106-4113
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

; Programm 5.16 (Programmanfang in Zelle 3000, wie im Buch; Start über 0000)
m0000:          000     m3000                    ; Sprung zum Programmanfang
                equ     03000
m3000:          000     m3007                    ; 3007 000 ; Programmanfang
; Parameter
m3001:          000     d4034                    ; a° = Adresse der ersten Komponente des gespeicherten Vektors
m3002:          000     m0006                    ; n° = Dimension des Vektors (6 Adresseneinheiten)
m3003:          000     m4106                    ; b° = Adresse der ersten Komponente des umgespeicherten Vektors
; Konstanten
m3004:          000     m0001                    ; 0001 000 ; Adresseneinheit
d3005:          dw      0240                     ; 0000 240 ; Speicherbefehl
; Arbeitszelle
m3006:          000     m0000                    ; i (wird zur Laufzeit gesetzt)
m3007:          241     m3006                    ; 3006 241 ; i:=0
m3010:          210     m3003                    ; 3003 210 ; <AC>:=(b+i)°
                210     d3005                    ; 3005 210 ; <AC>:=(b+i) 240
                240     m3016                    ; 3016 240 ; <3016>:=(b+i) 240
                211     m3006                    ; 3006 211 ; <AC>:=i°
                210     m3001                    ; 3001 210 ; <AC>:=(a+i)°
                dw      0251                     ; 0000 251 ; <AC>:=a(i+1)
m3016:          000     m0000                    ; (b+i) 240 ; <b+i>:=a(i+1) (wird zur Laufzeit gesetzt)
                211     m3006                    ; 3006 211 ; <AC>:=i°
                210     m3004                    ; 3004 210 ; <AC>:=(i+1)°
                240     m3006                    ; 3006 240 ; i:=i+1
                330     m3002                    ; 3002 330 ; Vergleicher 3, falls i=n
                170     m3025                    ; 3025 170 ; Prüfen, ob i=n
                000     m3010                    ; 3010 000 ; Schleife
; Programmende (im Buch 0000 020; hier mit Debug-Befehl davor)
m3025:          164     00001                    ; DEBUG Nr. 0001
                020     0                        ; Programmende, unbedingter Stopp
; Quellvektor
                equ     04034
d4034:          dw      070000000101             ; a1
                dw      012345670202             ; a2
                dw      0303                     ; a3
                dw      077777777777             ; a4
                dw      0505                     ; a5 (hinter der Spurgrenze)
                dw      050505050606             ; a6

                end
m0001:          abs     01
m0006:          abs     06
m4106:          abs     04106

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3027 AC=00000006000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=1 V2=1
; 3006: 00000006000
; 3016: 00004113240
; 4034: 70000000101
; 4035: 12345670202
; 4036: 00000000303
; 4037: 77777777777
; 4040: 00000000505
; 4041: 50505050606
; 4106: 70000000101
; 4107: 12345670202
; 4110: 00000000303
; 4111: 77777777777
; 4112: 00000000505
; 4113: 50505050606
;
