; bsp_5_11_pos.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_11_pos.txt
; #DOK-0001 Angabe des Vorzeichens einer Zahl (Programmieranleitung 5.11), x = +5
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe
; #SPEI-0001 3000-3000
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3001                    ; Sprung zum Programmanfang
                equ     03000
d3000:          dw      05                       ; x
m3001:          030     04500                    ; Anwahl der Schreibmaschine
                030     01170                    ; Umschaltung auf KB
                211     d3000                    ; <AC>:=x
                040     m3007                    ; Negativsprung nach 3007, falls x<0
                030     01270                    ; Druck "p"
                000     m3010                    ; Sprung zum Stop
m3007:          030     01050                    ; Druck "n"
m3010:          020     0                        ; unbedingter Stop

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3011 AC=00000000005 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3000: 00000000005
; --pruefe-sw-ausgabe bsp_5_11_pos-sw-ausgabe.txt
;
