; bsp_6_1_1_multiplikation_festkomma.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_6_1_1_multiplikation_festkomma.txt
; #DOK-0001 Zahlwort Festkomma vorn: Multiplikation positiver Zahlen (Programmieranleitung 6.1.1), Zahlenbeispiel des Buches a=0,110101
;   b=0,111001 (dual, auf 33 Bit erweitert)
; #DOK-0001 Programm wie im Buch ab Zelle 3000; a=<3007>, b=<3010>, Arbeitsspur 7700; 7700 440 Transport auf alle Zellen, 7700 472
;   Teilprodukte, 7700 412 Summierung; das exakte Produkt ist 0,101111001101 (dual)
; #DOK-0001 erwartet <AC> = a*b = 27464000000 (oktal), Teilprodukte b(i)*a in den 32 Zellen der Arbeitsspur 7700
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
d3007:          dw      032400000000             ; a
d3010:          dw      034400000000             ; b
d3011:          dw      020000000000             ; Konstante 2000 0000 000 (= 2^-1)

                end
d7700:          abs     07700

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3007 AC=27464000000 AR=3000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3007: 32400000000
; 3010: 34400000000
; 3011: 20000000000
; 7700: 00000000000
; 7715: 00000000000
; 7732: 00000000000
; 7707: 00000000000
; 7724: 00000000000
; 7701: 00000000000
; 7716: 00000000000
; 7733: 00000000000
; 7710: 00000000000
; 7725: 00000000000
; 7702: 00000000000
; 7717: 00000000000
; 7734: 00000000000
; 7711: 00000000000
; 7726: 00000000000
; 7703: 00000000000
; 7720: 00000000000
; 7735: 00000000000
; 7712: 00000000000
; 7727: 00000000000
; 7704: 00000000000
; 7721: 00000000000
; 7736: 00000000000
; 7713: 00000000000
; 7730: 00000000000
; 7705: 00000000000
; 7722: 32400000000
; 7737: 00000000000
; 7714: 00000000000
; 7731: 32400000000
; 7706: 32400000000
; 7723: 32400000000
;
