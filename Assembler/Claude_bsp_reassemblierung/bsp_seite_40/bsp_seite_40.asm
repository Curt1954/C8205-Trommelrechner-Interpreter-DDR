; bsp_seite_40.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_seite_40.test
; #DOK-0001  Summieren eines Vektors Beispiel 2 von Seite 40
; #SPEI-0001 0000-0000
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
                210     lesebef
schleife:       240     beliebig                 ; Lesebefehl
                330     adr_b
                equ     02010
                210     zelle_s                  ; summe := summe + speicher
                240     zelle_s
                150     halt
                211     beliebig                 ; Lesebefehl
                210     adr_1                    ; Lesebefehl Adresse erhöhen
                000     schleife
halt:           164     00001                    ; DEBUG Nr. 0001 aktivieren
                020     0                        ; halt
adr_1:          dw      01000                    ; eine Adreßeinheit
                equ     02022
lesebef:        dw      0211
a:              dw      0144
                dw      0145
                dw      0310
b:              dw      067


                end
beliebig:       abs     02007
zelle_s:        abs     02021

; Tastenfolge:
; H G R
;
; Prüfungen:
;
; BZ=2020 AC=00000000710 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=1
;
