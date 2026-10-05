; bsp_6_1_1_multiplikation_festkomma_dicht.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_6_1_1_multiplikation_festkomma_dicht.txt
; #DOK-0001 Zahlwort Festkomma vorn: Multiplikation positiver Zahlen (Programmieranleitung 6.1.1), a und b mit voller Stellenzahl
; #DOK-0001 Programm wie im Buch ab Zelle 3000; a=<3007>, b=<3010>, Arbeitsspur 7700; das Ergebnis weicht durch die Rundung um weniger als
;   eine Einheit der letzten Stelle vom exakten Produkt ab
; #DOK-0001 erwartet <AC> = a*b = 25761027732 (oktal), Teilprodukte b(i)*a in den 32 Zellen der Arbeitsspur 7700
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3000                    ; Sprung zum Programmanfang der Aufgabe (Programm beginnt in Zelle 3000)
; Programm 6.1.1; Arbeitsspur 7700 (die Zellen der Spur werden vom Gruppenbefehl beschrieben)
                equ     03000
m3000:          211     d3007                    ; 3007 211 ; <AC>:=a
                440     d7700                    ; 7700 440 ; Transport von a auf alle Zellen einer Spur
                211     d3010                    ; 3010 211 ; <AC>:=b
                472     d7700                    ; 7700 472 ; Bildung der Teilprodukte P(i)=b(i)*a für i=32,...,1
                211     d3011                    ; 3011 211 ; <AC>:=2^-1 (Rundung des Resultats)
                412     d7700                    ; 7700 412 ; <AC>:=a*b, Summierung der Teilprodukte
                020     03000                    ; 3000 020 ; unbedingter Stopp
d3007:          dw      027351646213             ; a
d3010:          dw      035762104535             ; b
d3011:          dw      020000000000             ; Konstante 2000 0000 000 (= 2^-1)

                end
d7700:          abs     07700

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3007 AC=25761027732 AR=3000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3007: 27351646213
; 3010: 35762104535
; 3011: 20000000000
; 7700: 27351646213
; 7715: 00000000000
; 7732: 27351646213
; 7707: 27351646213
; 7724: 27351646213
; 7701: 00000000000
; 7716: 27351646213
; 7733: 00000000000
; 7710: 27351646213
; 7725: 00000000000
; 7702: 00000000000
; 7717: 27351646213
; 7734: 00000000000
; 7711: 00000000000
; 7726: 00000000000
; 7703: 27351646213
; 7720: 00000000000
; 7735: 00000000000
; 7712: 00000000000
; 7727: 27351646213
; 7704: 00000000000
; 7721: 00000000000
; 7736: 27351646213
; 7713: 27351646213
; 7730: 27351646213
; 7705: 27351646213
; 7722: 27351646213
; 7737: 27351646213
; 7714: 00000000000
; 7731: 27351646213
; 7706: 27351646213
; 7723: 27351646213
;
